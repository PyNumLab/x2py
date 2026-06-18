from pathlib import Path

import pytest

from x2py import parse_fortran_file
from x2py.codegen.models.core import ClassDef, FunctionOverloadSet
from x2py.codegen.models.datatypes import (
    CustomDataType,
    NIL,
    NumpyFloat64Type,
    NumpyInt64Type,
    NumpyNDArrayType,
)
from x2py.codegen.scope import Scope
from x2py.semantics.fortran2ir import fortran_module_to_semantic_module
from x2py.semantics.ir2ast import semantic_ir_to_codegen_ast


FORTRAN_CLASS_SOURCE = Path(__file__).parents[1] / "wrapper" / "fclasses_f90.f90"
FORTRAN_OPERATOR_SOURCE = Path(__file__).parents[1] / "wrapper" / "foperators_f90.f90"


def test_modern_fortran_derived_type_and_type_bound_methods_become_codegen_class():
    parsed = parse_fortran_file(
        FORTRAN_CLASS_SOURCE.read_text(),
        filename=str(FORTRAN_CLASS_SOURCE),
    )
    semantic_module = fortran_module_to_semantic_module(parsed)
    semantic_vector = next(cls for cls in semantic_module.classes if cls.name == "vector")
    semantic_shift = next(method for method in semantic_vector.methods if method.name == "shift")
    assert semantic_shift.passed_object_name == "owner"
    assert semantic_shift.passed_object_position == 1
    assert semantic_shift.binding_attributes == ("pass(owner)",)

    scope = Scope(name=semantic_module.name, scope_type="module")
    codegen_module = semantic_ir_to_codegen_ast(semantic_module, scope)

    assert [str(cls.name) for cls in codegen_module.classes] == [
        "vector",
        "vector_store",
    ]
    vector, vector_store = codegen_module.classes
    assert isinstance(vector, ClassDef)
    assert str(vector.name) == "vector"
    assert isinstance(vector.class_type, CustomDataType)
    assert vector.class_type.name == "vector"

    assert [str(attribute.name) for attribute in vector.attributes] == ["x", "y"]
    assert all(attribute.class_type is NumpyFloat64Type() for attribute in vector.attributes)

    assert [str(method.name) for method in vector.methods] == ["scale", "shift_vector", "magnitude"]
    scale = vector.methods_as_dict["scale"]
    self_arg = scale.arguments[0]
    assert self_arg.bound_argument
    assert self_arg.var.class_type is vector.class_type
    assert self_arg.var.cls_base is vector

    shift = vector.methods_as_dict["shift"]
    assert vector.scope.get_python_name(shift.name) == "shift"
    assert [str(argument.name) for argument in shift.arguments] == ["owner", "dx", "dy"]
    assert shift.arguments[0].bound_argument
    assert shift.arguments[0].bound_argument_position == 1
    assert shift.arguments[0].var.cls_base is vector

    magnitude = vector.methods_as_dict["magnitude"]
    assert magnitude.arguments[0].bound_argument
    assert magnitude.results.var.class_type is NumpyFloat64Type()

    assert isinstance(vector_store, ClassDef)
    assert isinstance(vector_store.class_type, CustomDataType)
    assert vector_store.class_type.name == "vector_store"
    assert [str(attribute.name) for attribute in vector_store.attributes] == [
        "values",
        "matrix",
    ]
    values, matrix = vector_store.attributes
    assert isinstance(values.class_type, NumpyNDArrayType)
    assert values.class_type.element_type is NumpyFloat64Type()
    assert values.memory_handling == "heap"
    assert isinstance(matrix.class_type, NumpyNDArrayType)
    assert matrix.class_type.element_type is NumpyFloat64Type()
    assert matrix.class_type.rank == 2
    assert matrix.class_type.order == "F"
    assert matrix.memory_handling == "heap"

    assert [vector_store.scope.get_python_name(method.name) for method in vector_store.methods] == [
        "allocate_values",
        "set_values",
        "allocate_matrix",
        "set_matrix",
        "make",
    ]
    allocate_values = vector_store.methods_as_dict["allocate_values"]
    assert allocate_values.arguments[0].bound_argument
    assert allocate_values.arguments[0].var.class_type is vector_store.class_type
    assert allocate_values.arguments[1].var.class_type is NumpyInt64Type()

    set_values = vector_store.methods_as_dict["set_values"]
    assert set_values.arguments[0].bound_argument
    assert isinstance(set_values.arguments[1].var.class_type, NumpyNDArrayType)

    set_matrix = vector_store.methods_as_dict["set_matrix"]
    assert set_matrix.arguments[0].bound_argument
    assert isinstance(set_matrix.arguments[1].var.class_type, NumpyNDArrayType)
    assert set_matrix.arguments[1].var.class_type.rank == 2
    assert set_matrix.arguments[1].var.class_type.order == "F"

    make = vector_store.methods_as_dict["make"]
    assert str(make.name) == "make_vector_store"
    assert not make.arguments[0].bound_argument
    assert make.arguments[0].var.class_type is NumpyInt64Type()
    assert make.arguments[1].var.class_type is NumpyFloat64Type()
    assert make.results.var.class_type is vector_store.class_type


def test_generic_interfaces_become_module_and_class_function_overload_sets():
    source = """
module generic_mod
  interface convert
    module procedure convert_integer, convert_real
  end interface convert
  type :: box
  contains
    procedure :: set_integer
    procedure :: set_real
    generic :: set => set_integer, set_real
  end type box
contains
  integer function convert_integer(value)
    integer :: value
    convert_integer = value
  end function convert_integer
  real function convert_real(value)
    real :: value
    convert_real = value
  end function convert_real
  subroutine set_integer(self, value)
    class(box) :: self
    integer :: value
  end subroutine set_integer
  subroutine set_real(self, value)
    class(box) :: self
    real :: value
  end subroutine set_real
end module generic_mod
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(source))
    codegen_module = semantic_ir_to_codegen_ast(
        semantic_module,
        Scope(name=semantic_module.name, scope_type="module"),
    )

    assert len(codegen_module.overload_sets) == 1
    assert isinstance(codegen_module.overload_sets[0], FunctionOverloadSet)
    assert codegen_module.overload_sets[0].name == "convert"
    assert [str(func.name) for func in codegen_module.overload_sets[0].functions] == [
        "convert_integer_0001",
        "convert_real_0001",
    ]
    assert len(codegen_module.classes[0].overload_sets) == 1
    assert codegen_module.classes[0].overload_sets[0].name == "set"


def test_indistinguishable_generic_overloads_raise_generation_error():
    source = """
module generic_mod
  interface convert
    module procedure convert_first, convert_second
  end interface convert
contains
  integer function convert_first(value)
    integer :: value
    convert_first = value
  end function convert_first
  integer function convert_second(value)
    integer :: value
    convert_second = value
  end function convert_second
end module generic_mod
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(source))
    with pytest.raises(ValueError, match="indistinguishable overload"):
        semantic_ir_to_codegen_ast(
            semantic_module,
            Scope(name=semantic_module.name, scope_type="module"),
        )


def test_unresolved_generic_target_raises_before_codegen():
    source = """
module generic_mod
  interface convert
    module procedure missing
  end interface convert
end module generic_mod
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(source))
    with pytest.raises(ValueError, match="missing specific procedure.*missing"):
        semantic_ir_to_codegen_ast(
            semantic_module,
            Scope(name=semantic_module.name, scope_type="module"),
        )


def test_allocatable_module_array_without_target_raises_before_codegen():
    source = """
module alloc_mod
  real(8), allocatable :: values(:)
end module alloc_mod
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(source))

    with pytest.raises(ValueError, match="allocatable array without the Fortran target attribute"):
        semantic_ir_to_codegen_ast(
            semantic_module,
            Scope(name=semantic_module.name, scope_type="module"),
        )


def test_allocatable_result_and_output_lower_for_copy_return_codegen():
    source = """
module alloc_mod
contains
  subroutine fill(values)
    real(8), allocatable, intent(out) :: values(:)
  end subroutine fill
  function make_values() result(values)
    real(8), allocatable :: values(:)
  end function make_values
end module alloc_mod
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(source))
    codegen_module = semantic_ir_to_codegen_ast(
        semantic_module,
        Scope(name=semantic_module.name, scope_type="module"),
    )

    fill = next(function for function in codegen_module.funcs if str(function.name) == "fill")
    values = fill.arguments[0].var
    assert values.intent == "out"
    assert values.memory_handling == "heap"
    assert isinstance(values.class_type, NumpyNDArrayType)
    assert values.class_type.rank == 1

    make_values = next(function for function in codegen_module.funcs if str(function.name) == "make_values")
    result = make_values.results.var
    assert result.intent == "out"
    assert result.memory_handling == "heap"
    assert isinstance(result.class_type, NumpyNDArrayType)
    assert result.class_type.rank == 1


def test_allocatable_inout_raises_before_codegen():
    inout_source = """
module alloc_mod
contains
  subroutine replace(values)
    real(8), allocatable, intent(inout) :: values(:)
  end subroutine replace
end module alloc_mod
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(inout_source))

    with pytest.raises(ValueError, match="allocatable inout argument 'values'"):
        semantic_ir_to_codegen_ast(
            semantic_module,
            Scope(name=semantic_module.name, scope_type="module"),
        )


@pytest.mark.parametrize("intent", ["out", "inout"])
def test_pointer_output_arguments_raise_before_codegen_without_policy(intent):
    source = f"""
module pointer_mod
contains
  subroutine attach(values)
    real(8), pointer, intent({intent}) :: values(:)
  end subroutine attach
end module pointer_mod
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(source))

    with pytest.raises(ValueError, match=rf"pointer {intent} argument 'values'"):
        semantic_ir_to_codegen_ast(
            semantic_module,
            Scope(name=semantic_module.name, scope_type="module"),
        )


def test_multiple_allocatable_copy_returns_lower_before_codegen():
    multiple_source = """
module alloc_mod
contains
  subroutine make_pair(left, right)
    real(8), allocatable, intent(out) :: left(:)
    real(8), allocatable, intent(out) :: right(:)
  end subroutine make_pair
end module alloc_mod
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(multiple_source))

    codegen_module = semantic_ir_to_codegen_ast(
        semantic_module,
        Scope(name=semantic_module.name, scope_type="module"),
    )

    make_pair = next(function for function in codegen_module.funcs if str(function.name) == "make_pair")
    assert [argument.var.intent for argument in make_pair.arguments] == ["out", "out"]
    assert all(argument.var.memory_handling == "heap" for argument in make_pair.arguments)


def test_optional_arguments_preserve_status_and_python_defaults_in_codegen_ast():
    source = """
module optional_mod
contains
  subroutine step(tol, dt, values, status)
    real(8), intent(in), optional :: tol
    integer, intent(in) :: dt
    real(8), intent(inout), optional :: values(:)
    integer, intent(out) :: status
  end subroutine step
end module optional_mod
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(source))

    codegen_module = semantic_ir_to_codegen_ast(
        semantic_module,
        Scope(name=semantic_module.name, scope_type="module"),
    )

    step = next(function for function in codegen_module.funcs if str(function.name) == "step")
    assert [str(argument.name) for argument in step.arguments] == ["dt", "status", "tol", "values"]
    assert [argument.var.is_optional for argument in step.arguments] == [False, False, True, True]
    assert [argument.has_default for argument in step.arguments] == [False, False, True, True]
    assert step.arguments[2].value is NIL
    assert step.arguments[3].value is NIL


def test_defined_operators_and_assignment_become_named_codegen_overload_sets():
    semantic_module = fortran_module_to_semantic_module(
        parse_fortran_file(
            FORTRAN_OPERATOR_SOURCE.read_text(),
            filename=str(FORTRAN_OPERATOR_SOURCE),
        )
    )
    codegen_module = semantic_ir_to_codegen_ast(
        semantic_module,
        Scope(name=semantic_module.name, scope_type="module"),
    )
    vector = next(cls for cls in codegen_module.classes if str(cls.name) == "vector")
    overload_sets = {item.name: item for item in vector.overload_sets}

    assert overload_sets["__add__"].native_name == "operator(+)"
    assert overload_sets["__sub__"].native_name == "operator(-)"
    assert set(overload_sets["__eq__"].native_names) == {"operator(==)", "operator(.eqv.)"}
    assert overload_sets["operator_dot"].native_name == "operator(.dot.)"
    assert overload_sets["assign"].native_name == "assignment(=)"
    assert overload_sets["assign"].functions[0].arguments[0].bound_argument
    reflected = next(
        function for function in overload_sets["__add__"].functions if "add_real_vector" in str(function.name)
    )
    assert not reflected.arguments[0].bound_argument


def test_indistinguishable_defined_operator_overloads_raise_generation_error():
    source = """
module ambiguous_operator
  type :: box
    integer :: value
  end type box
  interface operator(+)
    module procedure add_first, add_second
  end interface operator(+)
contains
  type(box) function add_first(left, right)
    type(box), intent(in) :: left
    integer, intent(in) :: right
  end function add_first
  type(box) function add_second(left, right)
    type(box), intent(in) :: left
    integer, intent(in) :: right
  end function add_second
end module ambiguous_operator
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(source))

    with pytest.raises(ValueError, match="indistinguishable overload"):
        semantic_ir_to_codegen_ast(
            semantic_module,
            Scope(name=semantic_module.name, scope_type="module"),
        )
