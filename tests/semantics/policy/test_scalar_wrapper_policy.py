from pathlib import Path

import pytest

from x2py.pipeline.pyi import pyi_file_to_semantic_module
from x2py.semantics.models import (
    RESOLVED_SCALAR_WRAPPER_POLICY_METADATA,
    SemanticFunction,
    SemanticType,
)
from x2py.semantics.ownership import (
    CodegenAction,
    NativeBarrierAction,
    ObjectKind,
    PythonBarrierAction,
    StorageMode,
)
from x2py.semantics.policy_completion import complete_semantic_policies
from x2py.semantics.scalar_wrapper_policy import (
    ScalarWrapperFunctionPolicy,
    completed_scalar_wrapper_policy,
)

from tests._shared.ownership_policy_support import parse_pyi_text


FMATH_CONTRACT = Path("tests/wrapper/fortran/scalars/contracts/fmath/__init__.pyi")


def test_fmath_fixture_gets_completed_scalar_wrapper_policy():
    module = pyi_file_to_semantic_module(FMATH_CONTRACT, module_name="fmath")

    complete_semantic_policies(module)

    policies = [function.metadata[RESOLVED_SCALAR_WRAPPER_POLICY_METADATA] for function in module.functions]
    assert policies
    assert all(isinstance(policy, ScalarWrapperFunctionPolicy) for policy in policies)
    assert all(policy.supported for policy in policies)
    assert all(policy.blockers == () for policy in policies)
    assert all(policy.writeback_actions == () for policy in policies)
    assert all(policy.cleanup_actions == () for policy in policies)
    assert all(policy.release_actions == () for policy in policies)


def test_fmath_scalar_policy_records_address_projected_call_slots():
    module = pyi_file_to_semantic_module(FMATH_CONTRACT, module_name="fmath")
    complete_semantic_policies(module)
    function = next(item for item in module.functions if item.name == "add_r8")

    policy = completed_scalar_wrapper_policy(function)

    assert policy.owner_path == "fmath.add_r8"
    assert policy.python_name == "add_r8"
    assert policy.native_name == "ADD_R8"
    assert policy.external is True
    assert policy.bind_target == "ADD_R8"

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

    assert policy.result is not None
    assert policy.result.owner_path == "fmath.add_r8.return"
    assert policy.result.semantic_type_name == "Float64"
    assert policy.result.rank == 0
    assert policy.result.ownership.kind is ObjectKind.SCALAR
    assert policy.result.codegen_action is CodegenAction.DIRECT_VALUE
    assert policy.result.python_barrier_action is PythonBarrierAction.NONE
    assert policy.result.native_barrier_action is NativeBarrierAction.NONE
    assert policy.result.storage_mode is StorageMode.STACK
    assert policy.result.boundary_storage_mode is StorageMode.STACK


def test_scalar_wrapper_policy_blocks_non_scalar_arguments_before_planning():
    module = parse_pyi_text(
        """
def sum_values(values: Float64[:]) -> Float64: ...
""",
        module_name="array_argument",
    )
    complete_semantic_policies(module)
    function = module.functions[0]
    policy = function.metadata[RESOLVED_SCALAR_WRAPPER_POLICY_METADATA]

    assert isinstance(policy, ScalarWrapperFunctionPolicy)
    assert policy.supported is False
    assert "argument 'values' is not a first-lane primitive scalar" in policy.blockers

    with pytest.raises(ValueError, match="blocked scalar wrapper policy"):
        completed_scalar_wrapper_policy(function)


def test_missing_scalar_wrapper_policy_fails_before_planning():
    function = SemanticFunction(
        name="add",
        arguments=[],
        return_type=SemanticType(name="Float64", dtype="Float64"),
    )

    with pytest.raises(ValueError, match="missing completed scalar wrapper policy"):
        completed_scalar_wrapper_policy(function)
