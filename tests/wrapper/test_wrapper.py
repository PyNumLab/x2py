import gc
import importlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest

from tests.wrapper.fmath_cases import fmath_cases


SCALAR_LEGACY_SOURCE = Path(__file__).with_name("fmath.f")
ARRAY_LEGACY_SOURCE = Path(__file__).with_name("fmath_arrays.f")
SCALAR_F90_SOURCE = Path(__file__).with_name("fmath_f90.f90")
ARRAY_F90_SOURCE = Path(__file__).with_name("fmath_arrays_f90.f90")
STRING_LEGACY_SOURCE = Path(__file__).with_name("fstrings.f")
STRING_F90_SOURCE = Path(__file__).with_name("fstrings_f90.f90")
CLASS_F90_SOURCE = Path(__file__).with_name("fclasses_f90.f90")
OVERLOAD_F90_SOURCE = Path(__file__).with_name("foverloads_f90.f90")
OVERLOAD_FIXED_SOURCE = Path(__file__).with_name("foverloads_fixed.f")
OPERATOR_F90_SOURCE = Path(__file__).with_name("foperators_f90.f90")
ALLOCATABLE_VIEW_F90_SOURCE = Path(__file__).with_name("fallocatable_views_f90.f90")
OUTPUTS_F90_SOURCE = Path(__file__).with_name("foutputs_f90.f90")


def _assert_fmath_examples(module):
    cases = fmath_cases()
    missing = sorted(name for name, _, _ in cases if not hasattr(module, name))
    assert missing == []

    for name, args, expected in cases:
        actual = getattr(module, name)(*args)
        if isinstance(expected, bool):
            assert bool(actual) is expected, name
        elif isinstance(expected, int):
            assert actual == expected, name
        else:
            np.testing.assert_allclose(actual, expected, rtol=1e-6, atol=1e-6, err_msg=name)


def _build_and_import(source_template: Path, workdir: Path, expected_generated_sources: set[str]):
    source = workdir / source_template.name
    module_name = source_template.stem
    shutil.copyfile(source_template, source)

    cmd = [
        sys.executable,
        "-m",
        "x2py",
        str(source),
        "--out-dir",
        str(workdir),
        "--json",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)

    shared_library = Path(payload["shared_library"])
    assert shared_library.exists()
    assert Path(payload["output_dir"]) == workdir
    assert shared_library.parent == workdir
    assert {Path(path).name for path in payload["generated_sources"]} == expected_generated_sources
    generated_files = [Path(path) for path in payload["generated_files"]]
    assert any(path.name == "python_runtime.c" and path.parent.name == "x2py_runtime" for path in generated_files)

    sys.modules.pop(module_name, None)
    sys.path.insert(0, str(workdir))
    try:
        return importlib.import_module(module_name)
    finally:
        sys.path.remove(str(workdir))


def _normalized_fortran_source(source: Path):
    return " ".join(source.read_text().replace("&", "").split())


def _result_dtype(expected):
    if isinstance(expected, bool):
        return np.dtype(np.bool_)
    if isinstance(expected, int):
        return np.dtype(np.int32)
    return np.asarray(expected).dtype


def _array_argument(value, size: int, *, strided: bool):
    dtype = np.asarray(value).dtype
    if strided:
        storage = np.zeros(2 * size, dtype=dtype)
        array = storage[::2]
    else:
        array = np.zeros(size, dtype=dtype)
    array[:] = value
    return array


def _array_result(expected, size: int, *, strided: bool):
    dtype = _result_dtype(expected)
    if strided:
        storage = np.zeros(2 * size, dtype=dtype)
        return storage[1::2]
    return np.zeros(size, dtype=dtype)


def _assert_array_result(function_name, result, expected, size):
    expected_array = np.full(size, expected, dtype=result.dtype)
    if result.dtype == np.dtype(np.bool_):
        np.testing.assert_array_equal(result, expected_array, err_msg=function_name)
    else:
        np.testing.assert_allclose(
            result,
            expected_array,
            rtol=1e-6,
            atol=1e-6,
            err_msg=function_name,
        )


def _assert_fmath_array_examples(module, *, suffix="", strided=False):
    cases = fmath_cases()
    missing = sorted(f"{name}{suffix}" for name, _, _ in cases if not hasattr(module, f"{name}{suffix}"))
    assert missing == []

    size = 4
    for function_name, scalar_args, expected in cases:
        wrapped_name = f"{function_name}{suffix}"
        array_args = [_array_argument(scalar_arg, size, strided=strided) for scalar_arg in scalar_args]
        result = _array_result(expected, size, strided=strided)

        getattr(module, wrapped_name)(np.int32(size), *array_args, result)

        _assert_array_result(wrapped_name, result, expected, size)


def _assert_array_rejects_strided_views(module, function_name):
    size = 4
    values = _array_argument(np.float32(2.0), size, strided=True)
    result = _array_result(np.float32(4.0), size, strided=True)

    with pytest.raises(TypeError, match="contiguous"):
        getattr(module, function_name)(np.int32(size), values, result)


def _assert_legacy_string_examples(module):
    assert module.CHAR_CODE_DEFAULT("A") == ord("A")
    assert module.CHAR_CODE_STAR1(np.str_("B")) == ord("B")
    assert module.STRING_LEN_STAR8("short") == 5
    assert module.STRING_LEN_STAR8("too-long-value") == 8
    assert module.STRING_LEN_ASSUMED("variable length") == 15
    assert module.STRING_LEN_ENTITY("python") == 6
    assert module.CHAR_RESULT_DEFAULT() == "L"
    assert module.STRING_RESULT_STAR8() == "LEGACY!!"
    assert module.STRING_RESULT_PADDED() == "PAD     "
    assert module.STRING_RESULT_DECLARED() == "STRING"


def _assert_modern_string_examples(module):
    assert module.char_code_default("A") == ord("A")
    assert module.char_code_len1(np.str_("B")) == ord("B")
    assert module.char_code_kind1("C") == ord("C")
    assert module.char_code_c_char("D") == ord("D")
    assert module.string_len_fixed("short") == 5
    assert module.string_len_fixed("too-long-value") == 8
    assert module.string_len_assumed("variable length") == 15
    assert module.string_len_c_char("c-char") == 6
    assert module.char_result_default() == "M"
    assert module.char_result_c_char() == "C"
    assert module.string_result_fixed() == "MODERN!!"
    assert module.string_result_padded() == "PAD     "
    assert module.string_result_c_char() == "C-CHAR!!"
    assert module.string_result_deferred("dynamic") == "dynamic-deferred"
    assert module.string_result_deferred("café") == "café-deferred"


def _assert_modern_class_examples(module):
    assert hasattr(module, "vector")
    value = module.vector()
    value.x = np.float64(3.0)
    value.y = np.float64(4.0)

    assert value.magnitude() == np.float64(5.0)
    value.scale(np.float64(2.0))
    assert value.x == np.float64(6.0)
    assert value.y == np.float64(8.0)
    assert value.magnitude() == np.float64(10.0)
    value.shift(np.float64(1.5), np.float64(-2.0))
    assert value.x == np.float64(7.5)
    assert value.y == np.float64(6.0)

    assert hasattr(module, "vector_store")
    store = module.vector_store()
    assert store.values is None
    assert store.matrix is None

    with pytest.raises(AttributeError, match="reallocate"):
        store.values = np.array([9.0], dtype=np.float64)

    store.allocate_values(np.int64(3))
    store.values[:] = np.array([1.0, 2.0, 3.0], dtype=np.float64)
    np.testing.assert_allclose(store.values, np.array([1.0, 2.0, 3.0]))

    store.set_values(np.array([4.0, 5.0], dtype=np.float64))
    np.testing.assert_allclose(store.values, np.array([4.0, 5.0]))

    matrix = np.asfortranarray(np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], dtype=np.float64))
    store.allocate_matrix(np.int64(2), np.int64(3))
    store.matrix[:, :] = matrix
    np.testing.assert_allclose(store.matrix, matrix)
    assert store.matrix.flags.f_contiguous

    replacement = np.asfortranarray(matrix * 2.0)
    store.set_matrix(replacement)
    np.testing.assert_allclose(store.matrix, replacement)
    assert store.matrix.flags.f_contiguous

    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        store.set_matrix(np.array(replacement, order="C"))

    made = module.vector_store.make(np.int64(4), np.float64(1.5))
    np.testing.assert_allclose(made.values, np.full(4, 1.5, dtype=np.float64))


def test_fortran_wrapper_pipeline_builds_importable_extension(tmp_path: Path):
    module = _build_and_import(
        SCALAR_LEGACY_SOURCE,
        tmp_path,
        {
            "bind_c_fmath_wrapper.f90",
            "fmath_wrapper.c",
            "fmath_wrapper.h",
        },
    )

    _assert_fmath_examples(module)


def test_f90_wrapper_pipeline_builds_importable_extension(tmp_path: Path):
    module = _build_and_import(
        SCALAR_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fmath_f90_wrapper.f90",
            "fmath_f90_wrapper.c",
            "fmath_f90_wrapper.h",
        },
    )

    _assert_fmath_examples(module)


def test_fortran_array_wrapper_pipeline_matches_fmath_results_with_contiguous_arrays(tmp_path: Path):
    module = _build_and_import(
        ARRAY_LEGACY_SOURCE,
        tmp_path,
        {
            "bind_c_fmath_arrays_wrapper.f90",
            "fmath_arrays_wrapper.c",
            "fmath_arrays_wrapper.h",
        },
    )

    _assert_fmath_array_examples(module, strided=False)
    _assert_array_rejects_strided_views(module, "SQUARE_R4")


def test_f90_array_wrapper_distinguishes_contiguous_and_strided_contracts(tmp_path: Path):
    module = _build_and_import(
        ARRAY_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fmath_arrays_f90_wrapper.f90",
            "fmath_arrays_f90_wrapper.c",
            "fmath_arrays_f90_wrapper.h",
        },
    )

    _assert_fmath_array_examples(module, suffix="_CONTIGUOUS", strided=False)
    _assert_array_rejects_strided_views(module, "SQUARE_R4_CONTIGUOUS")
    _assert_fmath_array_examples(module, suffix="_STRIDED", strided=True)


def test_legacy_fortran_character_arguments_and_results(tmp_path: Path):
    module = _build_and_import(
        STRING_LEGACY_SOURCE,
        tmp_path,
        {
            "bind_c_fstrings_wrapper.f90",
            "fstrings_wrapper.c",
            "fstrings_wrapper.h",
        },
    )

    bind_c_source = _normalized_fortran_source(tmp_path / "bind_c_fstrings_wrapper.f90")
    assert "C_fixed = transfer(C_0001, C_fixed)" in bind_c_source
    assert "C = transfer(C_0001, C) C_fixed = C" not in bind_c_source
    assert (
        "CHAR_RESULT_DEFAULT_ptr = transfer(CHAR_RESULT_DEFAULT_0001, CHAR_RESULT_DEFAULT_ptr, CHAR_RESULT_DEFAULT_len)"
    ) in bind_c_source
    assert "do Dummy_" not in bind_c_source

    _assert_legacy_string_examples(module)


def test_modern_fortran_character_arguments_and_results(tmp_path: Path):
    module = _build_and_import(
        STRING_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fstrings_f90_wrapper.f90",
            "fstrings_f90_wrapper.c",
            "fstrings_f90_wrapper.h",
        },
    )

    _assert_modern_string_examples(module)


def test_modern_fortran_derived_type_exposes_class_and_type_bound_methods(tmp_path: Path):
    module = _build_and_import(
        CLASS_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fclasses_f90_wrapper.f90",
            "fclasses_f90_wrapper.c",
            "fclasses_f90_wrapper.h",
        },
    )

    _assert_modern_class_examples(module)


def test_fortran_generic_interfaces_dispatch_in_generated_c_extension(tmp_path: Path):
    module = _build_and_import(
        OVERLOAD_F90_SOURCE,
        tmp_path,
        {
            "bind_c_foverloads_f90_wrapper.f90",
            "foverloads_f90_wrapper.c",
            "foverloads_f90_wrapper.h",
        },
    )

    assert module.convert(np.int32(4)) == np.int32(14)
    assert module.convert(np.float64(4.0)) == np.float64(4.5)
    assert module.convert(np.complex128(2.0 + 3.0j)) == np.complex128(3.0 + 2.0j)
    assert module.summarize(np.float64(2.5)) == np.float64(2.5)
    assert module.summarize(np.array([1.0, 2.0, 3.0], dtype=np.float64)) == np.float64(6.0)

    value = module.accumulator()
    value.add(np.int32(2))
    value.add(np.float64(0.5))
    assert value.total == np.float64(2.5)
    assert module.inspect(value) == np.float64(2.5)

    sample = module.sample()
    sample.value = np.float64(7.25)
    assert module.inspect(sample) == np.float64(7.25)

    with pytest.raises(TypeError):
        module.convert("not numeric")
    with pytest.raises(TypeError):
        value.add(np.complex128(1.0 + 0.0j))


def test_fixed_form_fortran_generic_interface_dispatches_in_generated_c_extension(tmp_path: Path):
    module = _build_and_import(
        OVERLOAD_FIXED_SOURCE,
        tmp_path,
        {
            "bind_c_foverloads_fixed_wrapper.f90",
            "foverloads_fixed_wrapper.c",
            "foverloads_fixed_wrapper.h",
        },
    )

    assert module.convert(np.int32(2)) == np.int32(22)
    assert module.convert(np.float64(2.0)) == np.float64(2.25)
    with pytest.raises(TypeError):
        module.convert(np.complex128(2.0 + 0.0j))


def test_fortran_defined_operators_and_assignment_dispatch_in_generated_c_extension(tmp_path: Path):
    module = _build_and_import(
        OPERATOR_F90_SOURCE,
        tmp_path,
        {
            "bind_c_foperators_f90_wrapper.f90",
            "foperators_f90_wrapper.c",
            "foperators_f90_wrapper.h",
        },
    )

    def vector(value):
        result = module.vector()
        result.value = np.float64(value)
        return result

    def offset(value):
        result = module.offset()
        result.value = np.float64(value)
        return result

    left = vector(5.0)
    right = vector(2.0)

    assert module.convert(np.int32(2)) == np.int32(12)
    assert module.convert(np.float64(2.0)) == np.float64(2.5)
    assert (left + right).value == np.float64(7.0)
    assert (left + np.int32(3)).value == np.float64(8.0)
    assert (left + np.float64(0.5)).value == np.float64(5.5)
    assert (np.float64(1.5) + left).value == np.float64(106.5)
    assert (left + np.array([1.0, 2.0], dtype=np.float64)).value == np.float64(8.0)
    assert (left + offset(4.0)).value == np.float64(9.0)
    temporary_result = vector(1.0) + vector(2.0)
    gc.collect()
    assert temporary_result.value == np.float64(3.0)
    assert (+left).value == np.float64(5.0)
    assert (left - np.float64(1.5)).value == np.float64(3.5)
    assert (np.float64(9.0) - left).value == np.float64(4.0)
    assert (-left).value == np.float64(-5.0)
    assert (left * np.float64(2.0)).value == np.float64(10.0)
    assert (left / np.float64(2.0)).value == np.float64(2.5)
    assert (left ** np.int32(2)).value == np.float64(25.0)
    with pytest.raises(TypeError, match="modulus is not supported"):
        pow(left, np.int32(2), np.int32(3))

    assert left == vector(5.0)
    assert left != right
    assert right < left
    assert left < np.float64(6.0)
    assert np.float64(1.0) < left
    assert right <= left
    assert left > right
    assert left >= right
    assert bool(left & right) is True
    assert bool(vector(0.0) | right) is True
    assert bool(~vector(0.0)) is True
    assert left == offset(1.0)
    assert left != np.int32(0)
    assert left.operator_dot(right) == np.float64(10.0)
    assert left.r_operator_shift(np.float64(2.0)).value == np.float64(207.0)

    assigned = vector(1.0)
    assigned_identity = id(assigned)
    assert assigned.assign(np.int32(7)) is None
    assert id(assigned) == assigned_identity
    assert assigned.value == np.float64(7.0)
    assert assigned.assign(np.float64(3.5)) is None
    assert assigned.value == np.float64(3.5)
    assert assigned.assign(assigned) is None
    assert assigned.value == np.float64(3.5)

    counter = module.counter()
    counter.value = np.int32(4)
    assert (counter + np.int32(3)).value == np.int32(7)

    with pytest.raises(TypeError):
        left + np.complex128(1.0 + 0.0j)
    with pytest.raises(TypeError):
        assigned.assign(np.complex128(1.0 + 0.0j))


def test_allocatable_module_and_derived_type_arrays_are_borrowed_views(tmp_path: Path):
    module = _build_and_import(
        ALLOCATABLE_VIEW_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fallocatable_views_f90_wrapper.f90",
            "fallocatable_views_f90_wrapper.c",
            "fallocatable_views_f90_wrapper.h",
        },
    )

    assert "Functions" in module.__doc__
    assert "build_values" in module.__doc__
    assert "buffer" in module.__doc__
    assert "build_values(n) -> ndarray[float64] | None" in module.build_values.__doc__
    assert "n : int32" in module.build_values.__doc__
    assert "Intent: in" in module.build_values.__doc__
    assert "values : ndarray[float64] or None" in module.build_values.__doc__
    assert "Rank: 1" in module.build_values.__doc__
    assert "Ownership: Python-owned" in module.build_values.__doc__
    assert "Returns None when unallocated." in module.build_values.__doc__
    assert "TypeError" in module.build_values.__doc__
    assert "Rank: 2" in module.build_matrix.__doc__
    assert "Layout: F-contiguous" in module.build_matrix.__doc__
    assert "get_module_values() -> ndarray[float64] | None" in module.get_module_values.__doc__
    assert "Ownership: Native-owned" in module.get_module_values.__doc__
    assert "zero-copy view of native Fortran memory" in module.get_module_values.__doc__
    assert "Fields" in module.buffer.__doc__
    assert "values : ndarray[float64] or None" in module.buffer.__doc__
    assert "Ownership: Native-owned" in module.buffer.values.__doc__

    assert module.get_module_values() is None
    module.allocate_module_values(np.int32(3))
    module_values = module.get_module_values()
    np.testing.assert_allclose(module_values, np.array([1.0, 2.0, 3.0], dtype=np.float64))

    module_values[0] = np.float64(10.0)
    assert module.module_values_sum() == np.float64(15.0)
    module.scale_module_values(np.float64(2.0))
    np.testing.assert_allclose(module_values, np.array([20.0, 4.0, 6.0], dtype=np.float64))

    module.deallocate_module_values()
    assert module.get_module_values() is None

    built_values = module.build_values(np.int32(4))
    np.testing.assert_allclose(built_values, np.array([2.0, 4.0, 6.0, 8.0], dtype=np.float64))
    built_values[0] = np.float64(-1.0)
    np.testing.assert_allclose(built_values, np.array([-1.0, 4.0, 6.0, 8.0], dtype=np.float64))
    assert module.build_values(np.int32(0)) is None

    built_matrix = module.build_matrix(np.int32(2), np.int32(2))
    np.testing.assert_allclose(
        built_matrix,
        np.array([[11.0, 21.0], [12.0, 22.0]], dtype=np.float64),
    )
    assert module.build_matrix(np.int32(0), np.int32(2)) is None

    made_values = module.make_values(np.int32(3))
    np.testing.assert_allclose(made_values, np.array([3.0, 6.0, 9.0], dtype=np.float64))
    assert module.make_values(np.int32(0)) is None

    made_matrix = module.make_matrix(np.int32(2), np.int32(2))
    np.testing.assert_allclose(
        made_matrix,
        np.array([[111.0, 121.0], [112.0, 122.0]], dtype=np.float64),
    )
    assert module.make_matrix(np.int32(2), np.int32(0)) is None

    values = module.buffer()
    assert values.values is None
    values.allocate_values(np.int32(3))
    field_view = values.values
    assert field_view.base is values
    np.testing.assert_allclose(field_view, np.array([1.0, 2.0, 3.0], dtype=np.float64))

    field_view[1] = np.float64(8.0)
    assert values.values_sum() == np.float64(12.0)
    values.scale_values(np.float64(0.5))
    np.testing.assert_allclose(field_view, np.array([0.5, 4.0, 1.5], dtype=np.float64))

    with pytest.raises(AttributeError, match="Can't reallocate memory"):
        values.values = np.array([1.0, 2.0], dtype=np.float64)

    retained_view = values.values
    del values
    gc.collect()
    np.testing.assert_allclose(retained_view, np.array([0.5, 4.0, 1.5], dtype=np.float64))

    owner = retained_view.base
    owner.deallocate_values()
    assert owner.values is None


def test_output_arguments_and_multiple_results_follow_python_projection_rules(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    module = _build_and_import(
        OUTPUTS_F90_SOURCE,
        tmp_path,
        {
            "bind_c_foutputs_f90_wrapper.f90",
            "foutputs_f90_wrapper.c",
            "foutputs_f90_wrapper.h",
        },
    )

    assert "scalar_status(n) -> int32" in module.scalar_status.__doc__
    assert "status : int32" in module.scalar_status.__doc__
    assert "fill_vector(n, values) -> ndarray[float64]" in module.fill_vector.__doc__
    assert "Intent: out" in module.fill_vector.__doc__
    assert "Initial contents are ignored." in module.fill_vector.__doc__
    assert "Ownership: Python-owned" in module.fill_vector.__doc__
    assert "Allocatable array outputs are copied into Python-owned NumPy arrays." in module.build_alloc.__doc__
    assert "copy adds overhead" in module.build_alloc.__doc__
    assert "make_label() -> str" in module.make_label.__doc__
    assert "make_point(scale) -> output_point" in module.make_point.__doc__

    assert module.scalar_status(np.int32(5)) == np.int32(15)

    vector = np.empty(4, dtype=np.float64)
    returned_vector = module.fill_vector(np.int32(4), vector)
    assert returned_vector is vector
    np.testing.assert_allclose(vector, np.array([2.0, 4.0, 6.0, 8.0], dtype=np.float64))

    matrix = np.empty((2, 3), dtype=np.float64, order="F")
    returned_matrix = module.fill_matrix(np.int32(2), np.int32(3), matrix)
    assert returned_matrix is matrix
    np.testing.assert_allclose(
        matrix,
        np.array([[11.0, 21.0, 31.0], [12.0, 22.0, 32.0]], dtype=np.float64),
    )

    allocated = module.build_alloc(np.int32(3))
    np.testing.assert_allclose(allocated, np.array([3.0, 6.0, 9.0], dtype=np.float64))
    assert allocated.base is not None
    assert module.build_alloc(np.int32(0)) is None

    assert module.with_scalar(np.int32(4)) == (np.int32(8), np.int32(7))

    mixed_vector = np.empty(3, dtype=np.float64)
    mixed_result = module.mixed_outputs(np.int32(3), mixed_vector)
    assert mixed_result[0] == np.float64(3.5)
    assert mixed_result[1] is mixed_vector
    assert mixed_result[2] == np.int32(23)
    np.testing.assert_allclose(mixed_result[1], np.array([101.0, 102.0, 103.0], dtype=np.float64))
    np.testing.assert_allclose(mixed_result[3], np.array([201.0, 202.0, 203.0], dtype=np.float64))

    inout_values = np.array([1.0, 2.0], dtype=np.float64)
    assert module.increment(inout_values) is None
    np.testing.assert_allclose(inout_values, np.array([2.0, 3.0], dtype=np.float64))
    assert module.increment_with_status(inout_values) == np.int32(2)
    np.testing.assert_allclose(inout_values, np.array([4.0, 5.0], dtype=np.float64))

    assert module.make_label() == "RESULT!!"

    point = module.make_point(np.int32(6))
    assert isinstance(point, module.output_point)
    assert point.x == np.float64(6.25)
    assert point.tag == np.int32(46)

    with pytest.raises(TypeError):
        module.scalar_status(np.int32(1), np.int32(0))
    with pytest.raises(TypeError):
        module.build_alloc(np.int32(2), np.empty(2, dtype=np.float64))
    with pytest.raises(TypeError):
        module.fill_vector(np.int32(4), np.empty(4, dtype=np.float32))
    with pytest.raises(TypeError):
        module.fill_vector(np.int32(4), np.empty((4, 1), dtype=np.float64))
    with pytest.raises(TypeError):
        module.fill_vector(np.int32(4), np.empty(3, dtype=np.float64))
    with pytest.raises(TypeError):
        module.fill_matrix(np.int32(2), np.int32(3), np.empty((2, 3), dtype=np.float64, order="C"))

    monkeypatch.setenv("X2PY_WRAPPER_FAIL_ALLOC", "1")
    with pytest.raises(MemoryError, match="copy-return output array"):
        module.build_alloc(np.int32(3))


def test_fortran_wrapper_default_places_extension_beside_source(tmp_path: Path):
    source = tmp_path / SCALAR_LEGACY_SOURCE.name
    shutil.copyfile(SCALAR_LEGACY_SOURCE, source)

    cmd = [sys.executable, "-m", "x2py", str(source), "--json"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)

    build_dir = tmp_path / "__x2py__"
    shared_library = Path(payload["shared_library"])
    assert shared_library.parent == tmp_path
    assert shared_library.exists()
    assert Path(payload["output_dir"]) == build_dir
    assert (build_dir / "bind_c_fmath_wrapper.f90").exists()
    assert not list(tmp_path.glob("*_wrapper.c"))


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        module = _build_and_import(
            SCALAR_LEGACY_SOURCE,
            Path(tmp),
            {
                "bind_c_fmath_wrapper.f90",
                "fmath_wrapper.c",
                "fmath_wrapper.h",
            },
        )
        _assert_fmath_examples(module)
    print("TEST PASSING!!")
