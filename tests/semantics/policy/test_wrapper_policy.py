from pathlib import Path

import pytest

from tests.wrapper.fortran._support import wrapper_source
from x2py.fortran_parser.parser import parse_fortran_project
from x2py.pipeline.build import _apply_source_python_exports, _fortran_source_for_pipeline, _merge_wrapper_modules
from x2py.pipeline.preprocessing import PreprocessingConfig
from x2py.pipeline.pyi import pyi_file_to_semantic_module
from x2py.semantics.fortran2ir import fortran_project_to_semantic_modules
from x2py.semantics.models import (
    RESOLVED_FUNCTION_WRAPPER_POLICY_METADATA,
    RESOLVED_MODULE_VARIABLE_POLICY_METADATA,
    RESOLVED_OWNERSHIP_POLICY_METADATA,
    RESOLVED_RUNTIME_STATUS_ERROR_POLICY_METADATA,
    SemanticFunction,
    SemanticType,
)
from x2py.semantics.ownership import (
    AssignmentMode,
    CodegenAction,
    NativeBarrierAction,
    ObjectKind,
    PythonBarrierAction,
    StorageMode,
    SetterAction,
)
from x2py.semantics.policy_completion import complete_semantic_policies
from x2py.semantics.wrapper_policy import (
    BridgeDataAction,
    FunctionWrapperPolicy,
    ModuleGetterAction,
    ModuleVariablePolicy,
    NativeStatusErrorPolicy,
    OptionalMode,
    PythonExceptionKind,
    WritebackPhase,
    completed_function_wrapper_policy,
)

from tests._shared.ownership_policy_support import parse_pyi_text


FMATH_CONTRACT = Path("tests/wrapper/fortran/scalars/contracts/fmath/__init__.pyi")


def _source_semantic_module(filename: str, *, module_name: str):
    source = wrapper_source(filename)
    parsed = parse_fortran_project({str(source): _fortran_source_for_pipeline(source, PreprocessingConfig())})
    modules = fortran_project_to_semantic_modules(parsed)
    _apply_source_python_exports(modules)
    module = _merge_wrapper_modules(modules, name=module_name)
    complete_semantic_policies(module)
    return module


def test_fmath_fixture_gets_completed_function_wrapper_policy():
    module = pyi_file_to_semantic_module(FMATH_CONTRACT, module_name="fmath")

    complete_semantic_policies(module)

    policies = [function.metadata[RESOLVED_FUNCTION_WRAPPER_POLICY_METADATA] for function in module.functions]
    assert policies
    assert all(isinstance(policy, FunctionWrapperPolicy) for policy in policies)
    assert all(policy.supported for policy in policies)
    assert all(policy.blockers == () for policy in policies)
    assert all(policy.writeback_actions == () for policy in policies)
    assert all(policy.cleanup_actions == () for policy in policies)
    assert all(policy.release_actions == () for policy in policies)


def test_optional_scalar_policy_completes_nullable_value_presence_before_planning():
    module = pyi_file_to_semantic_module(
        Path("tests/wrapper/fortran/function_calls/contracts/foptional_fixed/__init__.pyi"),
        module_name="foptional_fixed",
    )
    complete_semantic_policies(module)

    policy = completed_function_wrapper_policy(module.functions[0])

    assert policy.supported is True
    assert [argument.optional_mode for argument in policy.arguments] == [
        OptionalMode.REQUIRED,
        OptionalMode.NULLABLE_VALUE,
    ]
    assert policy.native_module is None
    assert policy.native_is_subroutine is False


def test_optional_descriptor_policy_completes_three_state_boundary_before_planning():
    module = parse_pyi_text(
        """
@native_call([Allocatable(Arg(0))])
def alloc_state(value: Annotated[Float64, Immutable] | None = ...) -> Int32: ...
""",
        module_name="scalar_optional_descriptors",
    )
    complete_semantic_policies(module)

    policy = completed_function_wrapper_policy(module.functions[0])
    value = policy.arguments[0]

    assert policy.supported is True
    assert value.optional_mode is OptionalMode.DESCRIPTOR
    assert value.bridge_data_action is BridgeDataAction.COPY_REPRESENTATION
    assert value.bridge_copy_reason == "materialize owned Fortran allocatable scalar storage from the binding value"
    assert value.nullable is True
    assert value.descriptor_boundary is True
    assert policy.native_module == "scalar_optional_descriptors"


def test_scalar_copy_in_out_policy_completes_writeback_before_planning():
    module = parse_pyi_text(
        'def bump(value: Annotated[Int32, Immutable]) -> Returns["value", Int32]: ...',
        module_name="scalar_writeback",
    )
    complete_semantic_policies(module)

    policy = completed_function_wrapper_policy(module.functions[0])

    assert policy.supported is True
    assert policy.results == ()
    assert policy.native_is_subroutine is True
    assert tuple(action.phase for action in policy.writeback_actions) == tuple(WritebackPhase)
    assert {action.source_role for action in policy.writeback_actions} == {"scalar_writeback.bump.value:value"}
    assert {action.result_position for action in policy.writeback_actions} == {0}


def test_native_call_policy_maps_visible_positions_when_hidden_output_precedes_input():
    module = parse_pyi_text(
        """
@native_call([Return("status", 0), Addr(Arg(0))])
def mapped_status(base: Int32) -> Int32: ...
""",
        module_name="scalar_native_order",
    )
    complete_semantic_policies(module)

    policy = completed_function_wrapper_policy(module.functions[0])

    assert [(argument.name, argument.python_position, argument.native_position) for argument in policy.arguments] == [
        ("base", 0, 1)
    ]
    assert [(slot.owner_path, slot.source_kind, slot.native_position) for slot in policy.native_call_slots] == [
        ("scalar_native_order.mapped_status.status", "result", 0),
        ("scalar_native_order.mapped_status.base", "projection", 1),
    ]


def test_multiple_scalar_result_policy_completes_order_and_hidden_address_before_planning():
    module = parse_pyi_text(
        """
@native_call([Addr(Arg(0)), Return("status", 1)])
def with_scalar(n: Int32) -> tuple[Int32, Int32]: ...
""",
        module_name="multiple_scalar_results",
    )
    complete_semantic_policies(module)

    policy = completed_function_wrapper_policy(module.functions[0])

    assert policy.supported is True
    assert [(result.source_kind, result.result_position) for result in policy.results] == [
        ("direct_return", 0),
        ("hidden_output", 1),
    ]
    hidden = policy.results[1]
    assert hidden.native_barrier_action is NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS
    assert policy.native_call_slots[1].owner_path == hidden.owner_path
    assert policy.native_call_slots[1].result_position == hidden.result_position
    assert policy.native_call_slots[1].native_barrier_action is hidden.native_barrier_action


def test_hidden_scalar_descriptor_result_keeps_descriptor_policy_instead_of_plain_address_storage():
    module = parse_pyi_text(
        """
@native_call([Allocatable(Return("value", 0))])
def create_allocatable() -> Float64 | None: ...
""",
        module_name="descriptor_result",
    )
    function = module.functions[0]
    result_argument = function.arguments[0]

    complete_semantic_policies(module)

    decision = result_argument.metadata[RESOLVED_OWNERSHIP_POLICY_METADATA]
    assert function.projection[0].value_kind == "allocatable"
    assert result_argument.semantic_type.storage is None
    assert decision.descriptor_boundary is True
    assert decision.native_barrier_action is NativeBarrierAction.PASS_VALUE


def test_source_fmath_scalar_policy_accepts_storage_address_native_action():
    module = _source_semantic_module("fmath.f", module_name="fmath")
    function = next(item for item in module.functions if item.name == "ADD_R8")
    policies = [item.metadata[RESOLVED_FUNCTION_WRAPPER_POLICY_METADATA] for item in module.functions]

    policy = function.metadata[RESOLVED_FUNCTION_WRAPPER_POLICY_METADATA]

    assert isinstance(policy, FunctionWrapperPolicy)
    assert policy.supported is True
    assert policy.blockers == ()
    assert [(export.namespace, export.name) for export in policy.python_exports] == [((), "add_r8")]
    assert policy.native_name == "ADD_R8"
    assert policy.external is True
    assert [argument.name for argument in policy.arguments] == ["X", "Y"]
    assert [argument.codegen_action for argument in policy.arguments] == [
        CodegenAction.IN_PLACE_ARGUMENT,
        CodegenAction.IN_PLACE_ARGUMENT,
    ]
    assert [argument.python_barrier_action for argument in policy.arguments] == [
        PythonBarrierAction.SCALAR_VALUE,
        PythonBarrierAction.SCALAR_VALUE,
    ]
    assert [argument.native_barrier_action for argument in policy.arguments] == [
        NativeBarrierAction.PASS_STORAGE_ADDRESS,
        NativeBarrierAction.PASS_STORAGE_ADDRESS,
    ]
    assert [argument.storage_mode for argument in policy.arguments] == [StorageMode.STACK, StorageMode.STACK]
    assert all(policy.writeback_actions == () for policy in policies)
    assert all(policy.cleanup_actions == () for policy in policies)
    assert all(policy.release_actions == () for policy in policies)
    assert [
        (slot.source_kind, slot.value_kind, slot.native_barrier_action, slot.codegen_action)
        for slot in policy.native_call_slots
    ] == [
        (
            "projection",
            "arg",
            NativeBarrierAction.PASS_STORAGE_ADDRESS,
            CodegenAction.IN_PLACE_ARGUMENT,
        ),
        (
            "projection",
            "arg",
            NativeBarrierAction.PASS_STORAGE_ADDRESS,
            CodegenAction.IN_PLACE_ARGUMENT,
        ),
    ]


def test_source_export_policy_resolves_names_inside_each_namespace():
    module = _source_semantic_module("fnaming_f90.f90", module_name="fnaming_f90")
    policies = {
        function.name: function.metadata[RESOLVED_FUNCTION_WRAPPER_POLICY_METADATA]
        for function in module.functions
        if function.visibility == "public"
    }

    assert [(export.namespace, export.name) for export in policies["lambda"].python_exports] == [
        (("fnaming_f90",), "lambda_")
    ]
    assert [(export.namespace, export.name) for export in policies["lambda_"].python_exports] == [
        (("fnaming_f90",), "lambda__2")
    ]
    assert all(
        function.metadata[RESOLVED_FUNCTION_WRAPPER_POLICY_METADATA].python_exports == ()
        for function in module.functions
        if function.visibility == "private"
    )


def test_fmath_scalar_policy_records_address_projected_call_slots():
    module = pyi_file_to_semantic_module(FMATH_CONTRACT, module_name="fmath")
    complete_semantic_policies(module)
    function = next(item for item in module.functions if item.name == "add_r8")

    policy = completed_function_wrapper_policy(function)

    assert policy.owner_path == "fmath.add_r8"
    assert [(export.namespace, export.name) for export in policy.python_exports] == [((), "add_r8")]
    assert policy.native_name == "ADD_R8"
    assert policy.external is True

    assert [argument.name for argument in policy.arguments] == ["X", "Y"]
    assert [argument.python_position for argument in policy.arguments] == [0, 1]
    assert [argument.native_position for argument in policy.arguments] == [0, 1]
    for argument in policy.arguments:
        assert argument.semantic_type_name == "Float64"
        assert argument.rank == 0
        assert argument.optional is False
        assert argument.ownership.kind is ObjectKind.SCALAR
        assert argument.codegen_action is CodegenAction.CALL_LOCAL_INPUT
        assert argument.python_barrier_action is PythonBarrierAction.SCALAR_VALUE
        assert argument.native_barrier_action is NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS
        assert argument.storage_mode is StorageMode.ALIAS
        assert argument.boundary_storage_mode is StorageMode.ALIAS
        assert argument.projects_result is False
        assert argument.python_visible is True

    assert [(slot.native_position, slot.python_position) for slot in policy.native_call_slots] == [
        (0, 0),
        (1, 1),
    ]
    assert [slot.source_kind for slot in policy.native_call_slots] == ["projection", "projection"]
    assert [slot.value_kind for slot in policy.native_call_slots] == ["addr", "addr"]
    assert [slot.native_name for slot in policy.native_call_slots] == ["X", "Y"]
    assert all(
        slot.native_barrier_action is NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS for slot in policy.native_call_slots
    )

    assert len(policy.results) == 1
    result = policy.results[0]
    assert result.owner_path == "fmath.add_r8.return"
    assert result.semantic_type_name == "Float64"
    assert result.rank == 0
    assert result.ownership.kind is ObjectKind.SCALAR
    assert result.codegen_action is CodegenAction.DIRECT_VALUE
    assert result.python_barrier_action is PythonBarrierAction.NONE
    assert result.native_barrier_action is NativeBarrierAction.NONE
    assert result.storage_mode is StorageMode.STACK
    assert result.boundary_storage_mode is StorageMode.STACK


def test_wrapper_policy_records_runtime_and_native_order_metadata():
    module = parse_pyi_text(
        """
@hold_gil
@bind("SWAP_ARGS")
@external
@native_call([Addr(Arg(1)), Addr(Arg(0))])
def swap_args(x: Float64, y: Float64) -> Float64: ...
""",
        module_name="runtime_policy",
    )
    complete_semantic_policies(module)

    policy = completed_function_wrapper_policy(module.functions[0])

    assert policy.hold_gil is True
    assert policy.external is True
    assert [argument.python_position for argument in policy.arguments] == [0, 1]
    assert [argument.native_position for argument in policy.arguments] == [1, 0]
    assert [(slot.native_position, slot.python_position, slot.value_kind) for slot in policy.native_call_slots] == [
        (0, 1, "addr"),
        (1, 0, "addr"),
    ]


def test_runtime_status_policy_is_completed_before_wrapper_planning():
    module = parse_pyi_text(
        """
@raises(status="status", message="message", success=0)
@native_call([Addr(Arg(0)), Return("status", 0), Return("message", 1)])
def solve(value: Int32) -> tuple[Int32, String[32]]: ...
""",
        module_name="runtime_status",
    )

    complete_semantic_policies(module)

    function = module.functions[0]
    status_error = function.metadata[RESOLVED_RUNTIME_STATUS_ERROR_POLICY_METADATA]
    policy = completed_function_wrapper_policy(function)
    assert isinstance(status_error, NativeStatusErrorPolicy)
    assert policy.status_error is status_error
    assert status_error.success == 0
    assert status_error.exception_kind is PythonExceptionKind.RUNTIME_ERROR
    assert status_error.status.owner_path == "runtime_status.solve.status"
    assert status_error.status.native_position == 1
    assert status_error.status.semantic_type_name == "Int32"
    assert status_error.message is not None
    assert status_error.message.owner_path == "runtime_status.solve.message"
    assert status_error.message.native_position == 2
    assert status_error.message.semantic_type_name == "String"
    assert status_error.message.character_length == 32
    assert policy.results == ()
    assert [slot.semantic_type_name for slot in policy.native_call_slots] == ["Int32", "Int32", "String"]
    assert [slot.character_length for slot in policy.native_call_slots] == [None, None, 32]


def test_wrapper_policy_records_implicit_native_order():
    module = parse_pyi_text(
        """
def add(x: Float64, y: Float64) -> Float64: ...
""",
        module_name="implicit_order",
    )
    complete_semantic_policies(module)

    policy = completed_function_wrapper_policy(module.functions[0])

    assert policy.hold_gil is False
    assert [argument.native_position for argument in policy.arguments] == [0, 1]
    assert [(slot.source_kind, slot.native_position, slot.python_position) for slot in policy.native_call_slots] == [
        ("implicit", 0, 0),
        ("implicit", 1, 1),
    ]


def test_scalar_module_variable_policy_completes_access_and_storage_before_planning():
    module = parse_pyi_text(
        """
limit: Final[Int32] = 12
counter: Int32 = 3
target_scale: Annotated[Float64, Aliased]
optional_scale: Allocatable[Float64]
selected_scale: Pointer[Float64]
""",
        module_name="scalar_state",
    )
    complete_semantic_policies(module)

    policies = {
        variable.name: variable.metadata[RESOLVED_MODULE_VARIABLE_POLICY_METADATA] for variable in module.variables
    }

    assert all(isinstance(policy, ModuleVariablePolicy) for policy in policies.values())
    assert all(policy.supported for policy in policies.values())
    assert policies["limit"].getter_action is ModuleGetterAction.CONSTANT_VALUE
    assert policies["limit"].setter_action is SetterAction.OMIT
    assert policies["limit"].native_assignment is AssignmentMode.NONE
    assert policies["limit"].constant_value == 12
    assert policies["counter"].getter_action is ModuleGetterAction.DIRECT_VALUE
    assert policies["counter"].setter_action is SetterAction.WRITE_THROUGH
    assert policies["counter"].native_assignment is AssignmentMode.VALUE_COPY
    assert policies["counter"].initializer == 3
    assert policies["target_scale"].getter_action is ModuleGetterAction.DIRECT_VALUE
    assert policies["target_scale"].setter_action is SetterAction.WRITE_THROUGH
    assert policies["target_scale"].native_assignment is AssignmentMode.VALUE_COPY
    assert policies["optional_scale"].getter_action is ModuleGetterAction.NULLABLE_SNAPSHOT
    assert policies["optional_scale"].descriptor_kind == "allocatable"
    assert policies["optional_scale"].setter_action is SetterAction.REJECT_REPLACEMENT
    assert policies["optional_scale"].native_assignment is AssignmentMode.NONE
    assert policies["selected_scale"].getter_action is ModuleGetterAction.NULLABLE_SNAPSHOT
    assert policies["selected_scale"].descriptor_kind == "pointer"
    assert policies["selected_scale"].setter_action is SetterAction.REJECT_REPLACEMENT
    assert policies["selected_scale"].native_assignment is AssignmentMode.NONE


def test_wrapper_policy_records_primitive_hidden_literals():
    module = parse_pyi_text(
        """
@native_call([Arg(0), Int32(1), Float64(0.5), Bool(False)])
def scale(x: Float64) -> Float64: ...
""",
        module_name="hidden_literals",
    )
    complete_semantic_policies(module)

    policy = completed_function_wrapper_policy(module.functions[0])

    assert [argument.native_position for argument in policy.arguments] == [0]
    assert [
        (
            slot.owner_path,
            slot.native_position,
            slot.source_kind,
            slot.python_position,
            slot.value_kind,
            slot.literal_type,
            slot.literal_value,
            slot.native_barrier_action,
            slot.codegen_action,
        )
        for slot in policy.native_call_slots
    ] == [
        (
            "hidden_literals.scale.x",
            0,
            "projection",
            0,
            "arg",
            None,
            None,
            NativeBarrierAction.PASS_VALUE,
            CodegenAction.CALL_LOCAL_INPUT,
        ),
        (
            "hidden_literals.scale.native_slot_1",
            1,
            "literal",
            None,
            "literal",
            "Int32",
            1,
            NativeBarrierAction.PASS_VALUE,
            CodegenAction.DIRECT_VALUE,
        ),
        (
            "hidden_literals.scale.native_slot_2",
            2,
            "literal",
            None,
            "literal",
            "Float64",
            0.5,
            NativeBarrierAction.PASS_VALUE,
            CodegenAction.DIRECT_VALUE,
        ),
        (
            "hidden_literals.scale.native_slot_3",
            3,
            "literal",
            None,
            "literal",
            "Bool",
            False,
            NativeBarrierAction.PASS_VALUE,
            CodegenAction.DIRECT_VALUE,
        ),
    ]


def test_wrapper_policy_blocks_non_primitive_hidden_literals():
    module = parse_pyi_text(
        """
@native_call([Arg(0), String[1]("N")])
def tagged(x: Float64) -> Float64: ...
""",
        module_name="hidden_string_literal",
    )
    complete_semantic_policies(module)
    policy = module.functions[0].metadata[RESOLVED_FUNCTION_WRAPPER_POLICY_METADATA]

    assert policy.supported is False
    assert "native-call literal slot 1 uses unsupported first-lane literal type 'String[1]'" in policy.blockers


def test_wrapper_policy_blocks_non_primitive_arguments_before_planning():
    module = parse_pyi_text(
        """
def sum_values(values: Float64[:]) -> Float64: ...
""",
        module_name="array_argument",
    )
    complete_semantic_policies(module)
    function = module.functions[0]
    policy = function.metadata[RESOLVED_FUNCTION_WRAPPER_POLICY_METADATA]

    assert isinstance(policy, FunctionWrapperPolicy)
    assert policy.supported is False
    assert "argument 'values' is not a first-lane primitive scalar" in policy.blockers
    assert "argument 'values' has no completed bridge data action" in policy.blockers
    assert policy.arguments[0].bridge_data_action is BridgeDataAction.BLOCKED

    with pytest.raises(ValueError, match="blocked wrapper policy"):
        completed_function_wrapper_policy(function)


def test_wrapper_policy_keeps_string_arguments_blocked_until_bridge_data_action_is_completed():
    module = parse_pyi_text(
        "def consume(value: String) -> None: ...",
        module_name="string_argument",
    )
    complete_semantic_policies(module)
    policy = module.functions[0].metadata[RESOLVED_FUNCTION_WRAPPER_POLICY_METADATA]

    assert policy.supported is False
    assert "argument 'value' has no completed bridge data action" in policy.blockers
    assert policy.arguments[0].bridge_data_action is BridgeDataAction.BLOCKED


def test_missing_wrapper_policy_fails_before_planning():
    function = SemanticFunction(
        name="add",
        arguments=[],
        return_type=SemanticType(name="Float64", dtype="Float64"),
    )

    with pytest.raises(ValueError, match="missing completed wrapper policy"):
        completed_function_wrapper_policy(function)
