from pathlib import Path

import pytest

from x2py import parse_fortran_file
from x2py.contracts import CONTRACT_SYMBOLS
from x2py.codegen.models.core import ClassDef, FunctionOverloadSet
from x2py.codegen.models.datatypes import (
    CharType,
    CustomDataType,
    NIL,
    NumpyFloat64Type,
    NumpyInt64Type,
    NumpyNDArrayType,
)
from x2py.codegen.scope import Scope
from x2py.ownership_policy import CodegenAction, SnapshotFieldAction
from x2py.semantics.fortran2ir import fortran_module_to_semantic_module
from x2py.semantics.ir2ast import semantic_ir_to_codegen_ast as _semantic_ir_to_codegen_ast
from x2py.semantics.models import SemanticModule
from x2py.semantics.policy_completion import complete_semantic_policies
from x2py.pyi_pipeline import pyi_text_to_semantic_module as _parse_pyi_text


WRAPPER_FORTRAN_DATA = Path(__file__).parents[1] / "data" / "fortran" / "wrapper"
FORTRAN_CLASS_SOURCE = WRAPPER_FORTRAN_DATA / "fclasses_f90.f90"
FORTRAN_OPERATOR_SOURCE = WRAPPER_FORTRAN_DATA / "foperators_f90.f90"
CONTRACT_IMPORT = f"from x2py.contracts import {', '.join(sorted(CONTRACT_SYMBOLS))}\n"


def parse_pyi_text(source: str, *args, **kwargs):
    if "x2py.contracts" in source:
        return _parse_pyi_text(source, *args, **kwargs)
    return _parse_pyi_text(f"{CONTRACT_IMPORT}{source}", *args, **kwargs)


def semantic_ir_to_codegen_ast(node, *args, **kwargs):
    if isinstance(node, SemanticModule):
        complete_semantic_policies(node)
    return _semantic_ir_to_codegen_ast(node, *args, **kwargs)


def test_ir_lowering_requires_completed_ownership_policy():
    module = parse_pyi_text(
        """
def scale(values: Float64[:]) -> None: ...
""",
        module_name="raw_policy",
    )

    with pytest.raises(ValueError, match="missing completed ownership policy"):
        _semantic_ir_to_codegen_ast(module, Scope(name=module.name, scope_type="module"))


def test_immutable_writable_arguments_lower_with_completed_copy_in_out_policy():
    module = parse_pyi_text(
        """
def normalize(
    values: Annotated[Float64[:], Immutable]
) -> Returns["values", Float64[:]]: ...
""",
        module_name="immutable_values",
    )

    lowered = semantic_ir_to_codegen_ast(module, Scope(name=module.name, scope_type="module"))
    values = lowered.funcs[0].arguments[0].var

    assert values.ownership_decision.codegen_action is CodegenAction.COPY_IN_OUT


def test_character_array_lowering_preserves_element_length_metadata():
    source = """
module char_array_mod
contains
  subroutine use_labels(labels)
    character(len=4), intent(in) :: labels(:)
  end subroutine use_labels
  subroutine replace_names(names)
    character(len=:), allocatable, intent(inout) :: names(:)
    if (allocated(names)) deallocate(names)
    allocate(character(len=5) :: names(2))
    names(1) = 'red'
    names(2) = 'blue'
  end subroutine replace_names
end module char_array_mod
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(source))
    lowered = semantic_ir_to_codegen_ast(
        semantic_module,
        Scope(name=semantic_module.name, scope_type="module"),
    )

    use_labels = next(func for func in lowered.funcs if func.name == "use_labels")
    labels = use_labels.arguments[0].var
    assert labels.dtype is CharType()
    assert labels.fortran_character_length.python_value == 4

    replace_names = next(func for func in lowered.funcs if func.name == "replace_names")
    names = replace_names.arguments[0].var
    assert names.dtype is CharType()
    assert names.fortran_character_length == ":"


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
    with pytest.raises(ValueError, match=r"missing specific procedure.*missing"):
        semantic_ir_to_codegen_ast(
            semantic_module,
            Scope(name=semantic_module.name, scope_type="module"),
        )


def test_allocatable_module_array_without_aliased_lowers_as_snapshot_copy():
    source = """
module alloc_mod
  real(8), allocatable :: values(:)
end module alloc_mod
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(source))

    codegen_module = semantic_ir_to_codegen_ast(
        semantic_module,
        Scope(name=semantic_module.name, scope_type="module"),
    )

    values = codegen_module.variables[0]
    assert values.ownership_decision.codegen_action is CodegenAction.SNAPSHOT_COPY
    assert values.getter_ownership_decision.codegen_action is CodegenAction.SNAPSHOT_COPY


def test_derived_snapshot_field_actions_are_completed_before_lowering():
    module = parse_pyi_text(
        """
class child:
    value: Int32

class box:
    scalar: Int32
    values: Annotated[Float64[:], Allocatable, Aliased]
    nested: child

current: box
""",
        module_name="snapshot_mod",
    )

    lowered = semantic_ir_to_codegen_ast(module, Scope(name=module.name, scope_type="module"))
    box = next(cls for cls in lowered.classes if str(cls.name) == "box")
    actions = {str(field.name): field.snapshot_field_action for field in box.attributes}

    assert actions == {
        "scalar": SnapshotFieldAction.SCALAR_COPY,
        "values": SnapshotFieldAction.ARRAY_COPY,
        "nested": SnapshotFieldAction.NESTED_SNAPSHOT,
    }


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
    assert values.memory_handling == "heap"
    assert isinstance(values.class_type, NumpyNDArrayType)
    assert values.class_type.rank == 1

    make_values = next(function for function in codegen_module.funcs if str(function.name) == "make_values")
    result = make_values.results.var
    assert result.memory_handling == "heap"
    assert isinstance(result.class_type, NumpyNDArrayType)
    assert result.class_type.rank == 1


def test_allocatable_inout_array_reaches_codegen_as_replacement_argument():
    inout_source = """
module alloc_mod
contains
  subroutine replace(values)
    real(8), allocatable, intent(inout) :: values(:)
  end subroutine replace
end module alloc_mod
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(inout_source))

    codegen_module = semantic_ir_to_codegen_ast(
        semantic_module,
        Scope(name=semantic_module.name, scope_type="module"),
    )

    replace = next(function for function in codegen_module.funcs if str(function.name) == "replace")
    values = replace.arguments[0].var
    assert values.memory_handling == "heap"
    assert isinstance(values.class_type, NumpyNDArrayType)
    assert values.class_type.rank == 1


def test_allocatable_scalar_derived_outputs_raise_before_codegen():
    source = """
module alloc_scalar_mod
  type :: item
    integer :: value
  end type item
contains
  subroutine replace(value)
    type(item), allocatable :: value
  end subroutine replace
end module alloc_scalar_mod
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(source))

    with pytest.raises(ValueError, match="writable allocatable scalar argument 'value'"):
        semantic_ir_to_codegen_ast(
            semantic_module,
            Scope(name=semantic_module.name, scope_type="module"),
        )


def test_bind_c_scalar_without_iso_c_kind_raises_before_codegen():
    source = """
module bad_bind_mod
contains
  integer function unsafe(n) bind(C) result(res)
    integer, value :: n
    res = n
  end function unsafe
end module bad_bind_mod
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(source))

    with pytest.raises(ValueError, match="bind\\(C\\) scalar argument 'n'"):
        semantic_ir_to_codegen_ast(
            semantic_module,
            Scope(name=semantic_module.name, scope_type="module"),
        )


@pytest.mark.parametrize("shape", ["", "(:)"])
def test_pointer_output_arguments_raise_before_codegen_without_policy(shape):
    source = f"""
module pointer_mod
contains
  subroutine attach(values)
    real(8), pointer :: values{shape}
  end subroutine attach
end module pointer_mod
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(source))

    with pytest.raises(ValueError, match="pointer argument 'values'"):
        semantic_ir_to_codegen_ast(
            semantic_module,
            Scope(name=semantic_module.name, scope_type="module"),
        )


def test_pointer_module_variables_raise_before_codegen_without_policy():
    source = """
module pointer_module_mod
  real(8), pointer :: values(:)
end module pointer_module_mod
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(source))

    with pytest.raises(ValueError, match="pointer array owner, lifetime, shape, and release policy are unknown"):
        semantic_ir_to_codegen_ast(
            semantic_module,
            Scope(name=semantic_module.name, scope_type="module"),
        )


def test_pointer_scalar_module_variable_raises_before_codegen_without_policy():
    source = """
module pointer_scalar_module_mod
  real(8), pointer :: value
end module pointer_scalar_module_mod
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(source))

    with pytest.raises(ValueError, match="pointer scalar module_variable owner, lifetime, and reassociation policy"):
        semantic_ir_to_codegen_ast(
            semantic_module,
            Scope(name=semantic_module.name, scope_type="module"),
        )


@pytest.mark.parametrize(
    ("source", "message"),
    [
        (
            """
module constructor_generic_mod
  type :: item
    integer :: value
  end type item
  interface item
    module procedure make_item
  end interface item
contains
  type(item) function make_item(value) result(instance)
    integer, intent(in) :: value
    instance%value = value
  end function make_item
end module constructor_generic_mod
""",
            "generic constructor interfaces are not mapped",
        ),
    ],
)
def test_unsupported_generic_constructor_raises_before_codegen(source, message):
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(source))

    with pytest.raises(ValueError, match=message):
        semantic_ir_to_codegen_ast(
            semantic_module,
            Scope(name=semantic_module.name, scope_type="module"),
        )


def test_bind_c_derived_value_uses_fortran_bridge_and_noninteroperable_type_is_rejected():
    interoperable_source = """
module bind_c_value_mod
  use iso_c_binding
  type, bind(C) :: point
    real(c_double) :: x
  end type point
contains
  subroutine consume(value) bind(C)
    type(point), value :: value
  end subroutine consume
end module bind_c_value_mod
"""
    noninteroperable_source = (
        interoperable_source.replace("type, bind(C) :: point", "type :: point")
        .replace("module bind_c_value_mod", "module bad_bind_c_value_mod")
        .replace("end module bind_c_value_mod", "end module bad_bind_c_value_mod")
    )

    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(interoperable_source))
    codegen_module = semantic_ir_to_codegen_ast(
        semantic_module,
        Scope(name=semantic_module.name, scope_type="module"),
    )
    argument = codegen_module.funcs[0].arguments[0].var

    assert isinstance(argument.class_type, CustomDataType)
    assert argument.passes_by_value is True

    bad_module = fortran_module_to_semantic_module(parse_fortran_file(noninteroperable_source))
    with pytest.raises(ValueError, match=r"by-value derived-type argument.*not declared bind\(C\)"):
        semantic_ir_to_codegen_ast(
            bad_module,
            Scope(name=bad_module.name, scope_type="module"),
        )


def test_scalar_polymorphic_input_arguments_become_dispatch_overload_sets():
    source = """
module polymorphic_codegen_mod
  type :: base
  end type base
  type, extends(base) :: child
  end type child
contains
  subroutine accept(value)
    class(base), intent(in) :: value
  end subroutine accept
end module polymorphic_codegen_mod
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(source))

    codegen_module = semantic_ir_to_codegen_ast(
        semantic_module,
        Scope(name=semantic_module.name, scope_type="module"),
    )

    assert codegen_module.funcs == ()
    assert len(codegen_module.overload_sets) == 1
    dispatch = codegen_module.overload_sets[0]
    assert isinstance(dispatch, FunctionOverloadSet)
    assert str(dispatch.name) == "accept"
    assert [func.arguments[0].var.class_type.name for func in dispatch.functions] == ["child", "base"]


def test_polymorphic_replacement_arguments_raise_before_codegen_without_policy():
    source = """
module polymorphic_codegen_mod
  type :: base
  end type base
contains
  subroutine replace(value)
    class(base) :: value
  end subroutine replace
end module polymorphic_codegen_mod
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(source))

    with pytest.raises(ValueError, match="polymorphic argument 'value'"):
        semantic_ir_to_codegen_ast(
            semantic_module,
            Scope(name=semantic_module.name, scope_type="module"),
        )


def test_non_default_lower_bound_extent_reaches_codegen_shape_validation():
    source = """
module lower_bound_mod
contains
  subroutine scale_lower(n, values)
    integer, intent(in) :: n
    real(8), intent(inout) :: values(0:n - 1)
  end subroutine scale_lower
end module lower_bound_mod
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(source))

    codegen_module = semantic_ir_to_codegen_ast(
        semantic_module,
        Scope(name=semantic_module.name, scope_type="module"),
    )

    scale_lower = next(function for function in codegen_module.funcs if str(function.name) == "scale_lower")
    values = scale_lower.arguments[1].var
    assert isinstance(values.class_type, NumpyNDArrayType)
    assert values.alloc_shape != (None,)
    assert "n" in repr(values.alloc_shape[0])


@pytest.mark.parametrize(
    ("source", "match"),
    [
        (
            """
module character_array_mod
contains
  subroutine inspect(labels)
    character(len=4), intent(in) :: labels(:)
  end subroutine inspect
end module character_array_mod
""",
            None,
        ),
        (
            """
module derived_array_mod
  type :: item
    integer :: value
  end type item
contains
  subroutine inspect(items)
    type(item), intent(in) :: items(:)
  end subroutine inspect
end module derived_array_mod
""",
            "array of derived type",
        ),
        (
            """
module high_rank_mod
contains
  subroutine inspect(values)
    real(8), intent(in) :: values(:, :, :, :, :, :, :, :, :, :, :, :, :, :, :, :)
  end subroutine inspect
end module high_rank_mod
""",
            "supports ranks 1 through 15",
        ),
    ],
)
def test_unsupported_remaining_array_contracts_raise_before_codegen(source, match):
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(source))

    if match is None:
        semantic_ir_to_codegen_ast(
            semantic_module,
            Scope(name=semantic_module.name, scope_type="module"),
        )
    else:
        with pytest.raises(ValueError, match=match):
            semantic_ir_to_codegen_ast(
                semantic_module,
                Scope(name=semantic_module.name, scope_type="module"),
            )


def test_assumed_rank_numeric_array_arguments_lower_with_dispatch_marker():
    source = """
module assumed_rank_mod
contains
  subroutine inspect(values)
    real(8), intent(in) :: values(..)
  end subroutine inspect
end module assumed_rank_mod
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_file(source))

    codegen_module = semantic_ir_to_codegen_ast(
        semantic_module,
        Scope(name=semantic_module.name, scope_type="module"),
    )

    inspect = next(function for function in codegen_module.funcs if str(function.name) == "inspect")
    values = inspect.arguments[0].var
    assert values.assumed_rank is True
    assert values.rank == 1
    assert values.alloc_shape == (None,)


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
