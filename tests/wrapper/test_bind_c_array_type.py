import importlib
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from tests.wrapper.fmath_cases import fmath_cases
from x2py.codegen.bind_c import BindCArrayType, BindCPointer
from x2py.codegen.models.core import Add, IndexedElement, Slice, Variable
from x2py.codegen.models.datatypes import LiteralInteger, PythonNativeInt
from x2py.codegen.models.datatypes import NumpyFloat32Type, NumpyNDArrayType
from x2py.codegen.printers.fcode import FCodePrinter
from x2py.codegen.scope import Scope


def test_bind_c_array_type_describes_packed_strided_layout():
    array_type = BindCArrayType.get_new(2, has_strides=True)

    assert array_type is BindCArrayType.get_new(2, has_strides=True)
    assert array_type.array_rank == 2
    assert array_type.rank == 1
    assert array_type.container_rank == 1
    assert array_type.has_strides is True
    assert len(array_type) == 7
    assert isinstance(array_type[0], BindCPointer)
    assert all(isinstance(field, PythonNativeInt) for field in array_type[1:])
    assert array_type.shape_is_compatible((LiteralInteger(7),))
    assert not array_type.shape_is_compatible((LiteralInteger(4),))


def test_bind_c_array_type_without_strides_contains_pointer_and_shape():
    array_type = BindCArrayType.get_new(3, has_strides=False)

    assert array_type.array_rank == 3
    assert array_type.has_strides is False
    assert len(array_type) == 4
    assert array_type.shape_is_compatible((LiteralInteger(4),))


@pytest.mark.parametrize(
    ("rank", "has_strides", "error"),
    [
        (0, True, ValueError),
        (1.5, True, TypeError),
        (1, 1, TypeError),
    ],
)
def test_bind_c_array_type_rejects_invalid_parameters(rank, has_strides, error):
    with pytest.raises(error):
        BindCArrayType.get_new(rank, has_strides)


def test_scope_expands_bind_c_array_to_registered_fields():
    scope = Scope(name="f", scope_type="function")
    array_type = BindCArrayType.get_new(1, has_strides=True)
    packed = Variable(array_type, "packed", shape=(LiteralInteger(4),))
    fields = [
        Variable(array_type[i], f"field_{i}")
        for i in range(len(array_type))
    ]

    for i, field in enumerate(fields):
        scope.insert_symbolic_alias(IndexedElement(packed, i), field)

    assert scope.collect_all_tuple_elements(packed) == fields


def test_fortran_printer_prints_array_slice_with_inclusive_stop():
    array_type = NumpyNDArrayType.get_new(NumpyFloat32Type(), 1, None)
    array = Variable(array_type, "values", shape=(LiteralInteger(8),))
    stop = Variable(PythonNativeInt(), "upper")
    stride = Variable(PythonNativeInt(), "stride")
    element = IndexedElement(
        array,
        Slice(
            LiteralInteger(1),
            Add(stop, LiteralInteger(1)),
            stride,
        ),
    )

    printer = FCodePrinter("test.f90", verbose=0)
    printer.set_scope(Scope(name="f", scope_type="function"))
    printer.print_kind = lambda expr: "i32"
    assert printer._print(element) == (
        "values(1_i32:upper + 1_i32 - 1_i32:stride)"
    )


def test_array_wrapper_builds_all_precisions_and_handles_strided_views(tmp_path):
    source = tmp_path / "fmath_arrays.f"
    repository_source = Path(__file__).with_name("fmath_arrays.f")
    shutil.copyfile(repository_source, source)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(source),
            "--wrap",
            "--out-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    sys.modules.pop("fmath_arrays", None)
    sys.path.insert(0, str(tmp_path))
    try:
        module = importlib.import_module("fmath_arrays")
    finally:
        sys.path.remove(str(tmp_path))

    cases = fmath_cases()
    missing = sorted(name for name, _, _ in cases if not hasattr(module, name))
    assert missing == []

    size = 4
    for function_name, scalar_args, expected in cases:
        array_args = []
        for scalar_arg in scalar_args:
            input_storage = np.zeros(2 * size, dtype=np.asarray(scalar_arg).dtype)
            array_arg = input_storage[::2]
            array_arg[:] = scalar_arg
            array_args.append(array_arg)

        if isinstance(expected, bool):
            result_dtype = np.bool_
        elif isinstance(expected, int):
            result_dtype = np.int32
        else:
            result_dtype = np.asarray(expected).dtype
        result_storage = np.zeros(2 * size, dtype=result_dtype)
        result = result_storage[1::2]

        getattr(module, function_name)(np.int32(size), *array_args, result)

        expected_array = np.full(size, expected, dtype=result_dtype)
        if result_dtype == np.dtype(np.bool_):
            np.testing.assert_array_equal(result, expected_array, err_msg=function_name)
        else:
            np.testing.assert_allclose(
                result,
                expected_array,
                rtol=1e-6,
                atol=1e-6,
                err_msg=function_name,
            )
