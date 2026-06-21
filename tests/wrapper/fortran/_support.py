import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from tests.wrapper.fortran.fmath_cases import fmath_cases


def _assert_fmath_examples(module):
    cases = fmath_cases()
    missing = sorted(name.lower() for name, _, _ in cases if not hasattr(module, name.lower()))
    assert missing == []

    for name, args, expected in cases:
        public_name = name.lower()
        actual = getattr(module, public_name)(*args)
        if isinstance(expected, bool):
            assert bool(actual) is expected, public_name
        elif isinstance(expected, int):
            assert actual == expected, public_name
        else:
            np.testing.assert_allclose(actual, expected, rtol=1e-6, atol=1e-6, err_msg=public_name)


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


def _build_text_and_import(source_text: str, filename: str, workdir: Path, expected_generated_sources: set[str]):
    source = workdir / filename
    source.write_text(source_text, encoding="utf-8")
    module_name = source.stem

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
    assert {Path(path).name for path in payload["generated_sources"]} == expected_generated_sources

    sys.modules.pop(module_name, None)
    sys.path.insert(0, str(workdir))
    try:
        return importlib.import_module(module_name)
    finally:
        sys.path.remove(str(workdir))


def _build_sources_and_import(source_texts: list[tuple[str, str]], workdir: Path):
    sources = []
    for filename, source_text in source_texts:
        source = workdir / filename
        source.write_text(source_text, encoding="utf-8")
        sources.append(source)

    cmd = [
        sys.executable,
        "-m",
        "x2py",
        *(str(source) for source in sources),
        "--wrap",
        "--out-dir",
        str(workdir),
        "--json",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)
    module_name = payload["module_name"]

    assert payload["sources"] == [str(source) for source in sources]
    assert payload["compiled"] is True
    assert payload["build_makefile"] is None
    assert Path(payload["shared_library"]).exists()
    for source in sources:
        assert any(Path(path).name == f"{source.stem}.o" for path in payload["generated_files"])

    sys.modules.pop(module_name, None)
    sys.path.insert(0, str(workdir))
    try:
        return importlib.import_module(module_name), payload
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
    missing = sorted(
        f"{name}{suffix}".lower() for name, _, _ in cases if not hasattr(module, f"{name}{suffix}".lower())
    )
    assert missing == []

    size = 4
    for function_name, scalar_args, expected in cases:
        wrapped_name = f"{function_name}{suffix}".lower()
        array_args = [_array_argument(scalar_arg, size, strided=strided) for scalar_arg in scalar_args]
        result = _array_result(expected, size, strided=strided)

        getattr(module, wrapped_name)(np.int32(size), *array_args, result)

        _assert_array_result(wrapped_name, result, expected, size)


def _assert_array_rejects_strided_views(module, function_name):
    size = 4
    values = _array_argument(np.float32(2.0), size, strided=True)
    result = _array_result(np.float32(4.0), size, strided=True)

    with pytest.raises(TypeError, match="contiguous"):
        getattr(module, function_name.lower())(np.int32(size), values, result)


def _assert_legacy_string_examples(module):
    assert module.char_code_default("A") == ord("A")
    assert module.char_code_star1(np.str_("B")) == ord("B")
    assert module.string_len_star8("short") == 5
    assert module.string_len_star8("too-long-value") == 8
    assert module.string_len_assumed("variable length") == 15
    assert module.string_len_entity("python") == 6
    assert module.char_result_default() == "L"
    assert module.string_result_star8() == "LEGACY!!"
    assert module.string_result_padded() == "PAD     "
    assert module.string_result_declared() == "STRING"


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
