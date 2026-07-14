"""Phase 7 typed native-array handle and descriptor plan coverage."""

from __future__ import annotations

import pytest

from tests._shared.ownership_policy_support import parse_pyi_text
from x2py.semantics.ownership import CodegenAction, ObjectKind, PythonBarrierAction
from x2py.semantics.policy_completion import complete_semantic_policies
from x2py.semantics.wrapper_policy import (
    ArgumentHandoffMode,
    NativeArrayDescriptorKind,
    NativeArrayDescriptorOwnership,
    NativeArrayOperation,
    NativeArrayOutputProjection,
    NativeArraySourceKind,
    NativeDescriptorHandoffABI,
)
from x2py.wrapper_codegen import WrapperCodeGenerator, WrapperPlanner


def _phase7_plan():
    module = parse_pyi_text(
        """
from x2py.contracts import Addr, Allocatable, Arg, Float64, Int32, Pointer, Return, Returns, String, native_call

def normal(values: Float64[:]) -> Float64: ...
def alloc(values: Allocatable[Float64[:]]) -> Float64: ...
def pointer(values: Pointer[Float64[:]]) -> Float64: ...
def optional(values: Allocatable[Float64[:]] | None = ...) -> Float64: ...

@native_call([Arg(0), Addr(Arg(1))])
def replace(
    values: Allocatable[Float64[:]],
    mode: Int32,
) -> Returns["values", Allocatable[Float64[:]]]: ...

@native_call([Addr(Arg(0))])
def make(n: Int32) -> Allocatable[Float64[:]]: ...

@native_call([Arg(0)], result=Allocatable(Return(0)))
def deferred(text: String) -> String | None: ...

def make_names() -> Allocatable[String[:][:]]: ...

def replace_names(
    names: Allocatable[String[:][:]],
) -> Returns["names", Allocatable[String[:][:]]]: ...
""",
        module_name="phase7_handles",
    )
    complete_semantic_policies(module)
    return WrapperPlanner().build(module)


def _functions(plan):
    return {function.binding.python_name: function for function in plan.namespaces[0].functions}


def _module_handle_plan():
    module = parse_pyi_text(
        """
from x2py.contracts import Aliased, Allocatable, Annotated, Float64, Pointer, PointerAssociation, PointerPolicy, String

module_allocatable: Annotated[Allocatable[Float64[:]], Aliased]
module_names: Annotated[Allocatable[String[:][:]], Aliased]
module_pointer: Annotated[
    Pointer[Float64[:]],
    PointerAssociation("runtime"),
    PointerPolicy(
        nullable=True,
        transfer="call_local",
        target_owner="module",
        lifetime="module",
        deallocation="never",
        shape_source="pointer_bounds",
        contiguity="strided",
        reassociation="never",
        aliasing="borrowed",
        mutability="view",
    ),
]
""",
        module_name="phase7_module_handles",
    )
    complete_semantic_policies(module)
    return WrapperPlanner().build(module)


def test_phase7_keeps_datatype_specific_state_under_argument_and_result_plans():
    plan = _phase7_plan()
    functions = _functions(plan)

    normal = functions["normal"].arguments[0]
    assert normal.object_kind is ObjectKind.NUMPY_ARRAY
    assert normal.native_array_handle is None
    assert normal.native_array_actual is not None
    assert normal.native_array_actual.accepted_sources == (
        NativeArraySourceKind.NDARRAY,
        NativeArraySourceKind.ALLOCATABLE_HANDLE,
        NativeArraySourceKind.POINTER_HANDLE,
    )
    assert normal.native_array_actual.require_contiguous is True
    assert normal.bridge.handoff_mode is ArgumentHandoffMode.ARRAY_BUFFER
    assert normal.array is normal.native_call_slot.array

    alloc = functions["alloc"].arguments[0]
    pointer = functions["pointer"].arguments[0]
    for argument, descriptor_kind in (
        (alloc, NativeArrayDescriptorKind.ALLOCATABLE),
        (pointer, NativeArrayDescriptorKind.POINTER),
    ):
        handle = argument.native_array_handle
        assert handle is not None
        assert handle is argument.native_call_slot.native_array_handle
        assert handle.descriptor_kind is descriptor_kind
        assert handle.handoff.abi is NativeDescriptorHandoffABI.FACT_PACKED_CALL_LOCAL
        assert len(handle.handoff.extent_roles) == handle.array.rank == 1
        assert argument.binding.python_action is PythonBarrierAction.WRAPPER_INSTANCE
        assert argument.bridge.handoff_mode is ArgumentHandoffMode.NATIVE_DESCRIPTOR

    optional = functions["optional"].arguments[0]
    assert optional.native_array_handle is not None
    assert optional.native_array_handle.optional_absent is True
    assert optional.native_array_handle.handoff.presence_role == optional.bridge.presence_role
    assert alloc.native_array_handle is not None
    assert alloc.native_array_handle.handoff.presence_role is None

    replacement = functions["replace"].arguments[0]
    assert replacement.native_array_handle is not None
    assert replacement.native_array_handle.handoff.abi is NativeDescriptorHandoffABI.DIRECT_STANDARD_DESCRIPTOR
    assert replacement.native_array_handle.output_projection is NativeArrayOutputProjection.PROJECTED_HANDLE
    assert replacement.native_array_handle.handoff.extent_roles == ()
    assert replacement.binding.codegen_action is CodegenAction.IN_PLACE_ARGUMENT

    owned = functions["make"].results[0]
    assert owned.native_array_handle is not None
    assert owned.native_array_handle.handoff.abi is NativeDescriptorHandoffABI.OWNED_RESULT_STORAGE
    assert owned.native_array_handle.descriptor_ownership is NativeArrayDescriptorOwnership.OWNED
    assert owned.native_array_handle.handoff.owner_storage_role is not None
    assert NativeArrayOperation.DESTROY in owned.native_array_handle.operations

    deferred = functions["deferred"].results[0]
    assert deferred.native_array_handle is None
    assert deferred.scalar_descriptor is not None
    assert deferred.scalar_descriptor.runtime_length is True
    assert deferred.scalar_descriptor.presence_role == f"{deferred.owner_path}:present"

    names = functions["make_names"].results[0]
    assert names.native_array_handle is not None
    assert names.datatype_family.value == "string"
    assert names.array.itemsize is None
    assert NativeArrayOperation.ELEMENT_LENGTH in names.native_array_handle.operations
    assert NativeArrayOperation.RESIZE not in names.native_array_handle.operations

    replacement_names = functions["replace_names"].arguments[0]
    assert replacement_names.native_array_handle is not None
    assert replacement_names.native_array_handle.handoff.abi is NativeDescriptorHandoffABI.DIRECT_STANDARD_DESCRIPTOR
    assert NativeArrayOperation.ELEMENT_LENGTH in replacement_names.native_array_handle.operations
    assert plan.required_headers == ("ISO_Fortran_binding.h",)


def test_phase7_module_variables_own_borrowed_handle_plans_and_operation_sets():
    plan = _module_handle_plan()
    variables = {variable.symbol_name: variable for variable in plan.namespaces[0].variables}
    allocatable = variables["module_allocatable"].native_array_handle
    names = variables["module_names"].native_array_handle
    pointer = variables["module_pointer"].native_array_handle

    assert allocatable is not None
    assert names is not None
    assert pointer is not None
    assert allocatable.borrowed is names.borrowed is pointer.borrowed is True
    assert allocatable.descriptor_kind is NativeArrayDescriptorKind.ALLOCATABLE
    assert names.descriptor_kind is NativeArrayDescriptorKind.ALLOCATABLE
    assert pointer.descriptor_kind is NativeArrayDescriptorKind.POINTER
    assert NativeArrayOperation.DEALLOCATE in allocatable.operations
    assert NativeArrayOperation.RESIZE in allocatable.operations
    assert NativeArrayOperation.NULLIFY in pointer.operations
    assert NativeArrayOperation.CONTIGUOUS in pointer.operations
    assert NativeArrayOperation.DESTROY not in allocatable.operations
    assert NativeArrayOperation.ELEMENT_LENGTH in names.operations
    assert NativeArrayOperation.RESIZE not in names.operations
    assert NativeArrayOperation.DESTROY not in pointer.operations
    assert allocatable.required_headers == ()
    assert pointer.required_headers == ("ISO_Fortran_binding.h",)
    assert plan.required_headers == ("ISO_Fortran_binding.h",)


def test_phase7_deferred_character_module_handles_use_runtime_element_length():
    artifacts = WrapperCodeGenerator().generate(_module_handle_plan())
    c_source = next(source.text for source in artifacts.sources if source.path.suffix == ".c")
    bridge_source = next(source.text for source in artifacts.sources if source.path.suffix == ".f90")

    assert "bind_c_module_names_element_length()" in c_source
    assert '"elem_len", (unsigned long long)(bind_c_module_names_element_length())' in c_source
    assert "function bind_c_module_names_element_length() result(result)" in bridge_source
    assert "result = len(native_module_names, kind=c_int64_t)" in bridge_source


def test_phase7_generated_artifacts_follow_one_typed_action_vocabulary():
    artifacts = WrapperCodeGenerator().generate(_phase7_plan())
    c_source = next(source.text for source in artifacts.sources if source.path.suffix == ".c")
    bridge_source = next(source.text for source in artifacts.sources if source.path.suffix == ".f90")

    assert artifacts.artifacts.required_headers == ("ISO_Fortran_binding.h",)
    assert '"_native_array_actual_argument_for_binding_positional"' in c_source
    assert '"_native_array_descriptor_argument_for_binding_positional"' in c_source
    assert '"_native_array_descriptor_handoff_for_binding_positional"' in c_source
    assert '"_native_array_handle_from_generated_ops"' in c_source
    assert "CFI_CDESC_T(1)" in c_source
    assert "real(c_double), allocatable, dimension(:) :: values" in bridge_source
    assert "real(c_double), pointer, dimension(:) :: values" in bridge_source
    assert "x2py_collect_make_result" not in bridge_source
    assert "result_value = native_make(n)" in bridge_source
    assert "call move_alloc(result_value, result)" in bridge_source
    assert "x2py_collect_deferred_scalar_descriptor_result" in bridge_source
    assert "character(kind=c_char, len=:), allocatable :: result_value" in bridge_source
    assert "result_itemsize" in c_source
    assert "CFI_type_char" in c_source
    assert "character(kind=c_char, len=:), allocatable, dimension(:) :: names" in bridge_source


def test_phase7_numeric_owned_result_moves_once_into_persistent_descriptor():
    bridge_source = next(
        source.text
        for source in WrapperCodeGenerator().generate(_phase7_plan()).sources
        if source.path.suffix == ".f90"
    )
    start = bridge_source.index("subroutine bind_c_make(")
    end = bridge_source.index("end subroutine", start)
    procedure = bridge_source[start:end]

    assert "real(c_double), allocatable, dimension(:), intent(out) :: result" in procedure
    assert "real(c_double), allocatable, dimension(:) :: result_value" in procedure
    assert "result_value = native_make(n)" in procedure
    assert "call move_alloc(result_value, result)" in procedure
    assert "result = result_value" not in procedure
    assert "allocated(" not in procedure
    assert "x2py_collect" not in procedure


@pytest.mark.parametrize(
    ("edit", "diagnostic"),
    [
        ("required_presence", "inconsistent-native-descriptor-presence"),
        ("projected_facts", "invalid-direct-native-descriptor-roles"),
        ("owned_storage", "invalid-owned-native-descriptor-roles"),
        ("operation", "incomplete-native-array-operations"),
        ("header", "inconsistent-required-headers"),
    ],
)
def test_phase7_plan_edits_fail_central_validation(edit: str, diagnostic: str):
    plan = _phase7_plan()
    functions = _functions(plan)
    if edit == "required_presence":
        functions["alloc"].arguments[0].native_array_handle.handoff.presence_role = "edited:present"
    elif edit == "projected_facts":
        functions["replace"].arguments[0].native_array_handle.handoff.extent_roles = ("edited:extent",)
    elif edit == "owned_storage":
        functions["make"].results[0].native_array_handle.handoff.owner_storage_role = None
    elif edit == "operation":
        functions["pointer"].arguments[0].native_array_handle.operations = ()
    else:
        plan.required_headers = ()

    with pytest.raises(ValueError, match=diagnostic):
        WrapperCodeGenerator().generate(plan)
