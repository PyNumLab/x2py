import pytest

from x2py.codegen.bind_c import BindCArrayType, BindCPointer
from x2py.codegen.models.core import Add, Declare, IndexedElement, Slice, Variable
from x2py.codegen.models.datatypes import (
    Literal,
    NumpyBoolType,
    NumpyFloat32Type,
    NumpyFloat64Type,
    NumpyInt32Type,
    NumpyInt64Type,
    NumpyNDArrayType,
    Cast,
    StringType,
    cast_to,
    convert_to_literal,
)
from x2py.codegen.printers.ccode import CCodePrinter
from x2py.codegen.printers.fcode import FCodePrinter
from x2py.codegen.scope import Scope


def test_literal_stores_value_and_datatype_without_specialized_subclasses():
    integer = Literal(7, NumpyInt64Type())
    boolean = Literal(False, NumpyBoolType())
    string = Literal("value", StringType())

    assert integer.python_value == 7
    assert integer.dtype is NumpyInt64Type()
    assert integer.shape is None
    assert boolean.python_value is False
    assert string.python_value == "value"
    assert string.shape == (None,)


def test_raw_array_uses_array_attributes_and_variable_storage():
    array_type = NumpyNDArrayType.get_new(NumpyInt64Type(), 1, None, raw=True)
    variable = Variable(array_type, "shape", shape=(4,), memory_handling="stack")

    assert array_type.raw is True
    assert variable.is_raw_array
    assert variable.on_stack
    assert CCodePrinter("test.c", verbose=0)._print(Declare(variable)) == ("int64_t shape[4];\n")


def test_cast_to_uses_shared_cast_concept_with_requested_datatype():
    source = Variable(NumpyFloat64Type(), "value")
    cast = cast_to(source, NumpyInt32Type())

    assert type(cast) is Cast
    assert cast.dtype is NumpyInt32Type()


def test_bind_c_array_type_describes_packed_strided_layout():
    array_type = BindCArrayType.get_new(2, has_strides=True)

    assert array_type is BindCArrayType.get_new(2, has_strides=True)
    assert array_type.array_rank == 2
    assert array_type.rank == 1
    assert array_type.container_rank == 1
    assert array_type.has_strides is True
    assert len(array_type) == 7
    assert isinstance(array_type[0], BindCPointer)
    assert all(isinstance(field, NumpyInt64Type) for field in array_type[1:])
    assert array_type.shape_is_compatible((Literal(7, NumpyInt64Type()),))
    assert not array_type.shape_is_compatible((convert_to_literal(4),))


def test_bind_c_array_type_without_strides_contains_pointer_and_shape():
    array_type = BindCArrayType.get_new(3, has_strides=False)

    assert array_type.array_rank == 3
    assert array_type.has_strides is False
    assert len(array_type) == 4
    assert array_type.shape_is_compatible((convert_to_literal(4),))


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
    packed = Variable(array_type, "packed", shape=(convert_to_literal(4),))
    fields = [Variable(array_type[i], f"field_{i}") for i in range(len(array_type))]

    for i, field in enumerate(fields):
        scope.insert_symbolic_alias(IndexedElement(packed, i), field)

    assert scope.collect_all_tuple_elements(packed) == fields


def test_fortran_printer_prints_array_slice_with_inclusive_stop():
    array_type = NumpyNDArrayType.get_new(NumpyFloat32Type(), 1, None)
    array = Variable(array_type, "values", shape=(convert_to_literal(8),))
    stop = Variable(NumpyInt64Type(), "upper")
    stride = Variable(NumpyInt64Type(), "stride")
    element = IndexedElement(
        array,
        Slice(
            convert_to_literal(1),
            Add(stop, convert_to_literal(1)),
            stride,
        ),
    )

    printer = FCodePrinter("test.f90", verbose=0)
    printer.set_scope(Scope(name="f", scope_type="function"))
    printer.print_kind = lambda expr: "i32"
    assert printer._print(element) == ("values(1_i32:upper + 1_i32 - 1_i32:stride)")
