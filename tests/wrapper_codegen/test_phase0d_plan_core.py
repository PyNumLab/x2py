"""Phase 0D tests for route-neutral wrapper-plan core records."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from x2py.pipeline.pyi import pyi_file_to_semantic_module
from x2py.semantics.ownership import CodegenAction, NativeBarrierAction, PythonBarrierAction
from x2py.semantics.policy_completion import complete_semantic_policies
from x2py.wrapper_codegen import (
    ArgumentTransferPlan,
    FunctionPlan,
    LifecycleActionPlan,
    ModulePlan,
    WrapperPlanRenderer,
    WrapperPlanSupportAnalyzer,
    WrapperPlanValidator,
    WrapperPlanner,
)

from tests._shared.ownership_policy_support import parse_pyi_text


FMATH_CONTRACT = Path("tests/wrapper/fortran/scalars/contracts/fmath/__init__.pyi")


def _fmath_plan() -> ModulePlan:
    module = pyi_file_to_semantic_module(FMATH_CONTRACT, module_name="fmath")
    complete_semantic_policies(module)
    return WrapperPlanner().visit(module)


def _function(plan: ModulePlan, owner_path: str = "fmath.add_r8") -> FunctionPlan:
    return next(function for function in plan.functions if function.owner_path == owner_path)


def _replace_function(plan: ModulePlan, function: FunctionPlan) -> ModulePlan:
    functions = tuple(function if item.owner_path == function.owner_path else item for item in plan.functions)
    return replace(plan, functions=functions)


def _replace_argument(function: FunctionPlan, argument: ArgumentTransferPlan) -> FunctionPlan:
    arguments = tuple(argument if item.owner_path == argument.owner_path else item for item in function.arguments)
    slots = tuple(item.bridge_abi_slot for item in arguments if item.bridge_abi_slot is not None)
    return replace(function, arguments=arguments, bridge_abi=replace(function.bridge_abi, slots=slots))


def _with_first_argument(plan: ModulePlan, argument: ArgumentTransferPlan) -> ModulePlan:
    return _replace_function(plan, _replace_argument(_function(plan), argument))


def _drop_primary_handlers(plan: ModulePlan) -> ModulePlan:
    registry = replace(plan.handler_registry, python_action_handlers=())
    return replace(plan, handler_registry=registry)


def _drop_secondary_handlers(plan: ModulePlan) -> ModulePlan:
    registry = replace(plan.handler_registry, native_action_handlers=())
    return replace(plan, handler_registry=registry)


def _drop_bridge_slot(plan: ModulePlan) -> ModulePlan:
    argument = replace(_function(plan).arguments[0], bridge_abi_slot=None)
    return _with_first_argument(plan, argument)


def _drop_native_slot(plan: ModulePlan) -> ModulePlan:
    argument = replace(_function(plan).arguments[0], native_call_slot=None)
    return _with_first_argument(plan, argument)


def _break_handoff_role(plan: ModulePlan) -> ModulePlan:
    argument = _function(plan).arguments[0]
    handoff = replace(argument.binding_handoff, consumed_role="fmath.add_r8.X:other")
    return _with_first_argument(plan, replace(argument, binding_handoff=handoff))


def _duplicate_symbolic_role(plan: ModulePlan) -> ModulePlan:
    function = _function(plan)
    first, second = function.arguments
    role = first.binding_handoff.produced_role
    handoff = replace(second.binding_handoff, produced_role=role, consumed_role=role)
    bridge = replace(second.bridge_abi_slot, symbolic_role=role)
    native = replace(second.native_call_slot, symbolic_role=role)
    updated = replace(second, binding_handoff=handoff, bridge_abi_slot=bridge, native_call_slot=native)
    return _replace_function(plan, _replace_argument(function, updated))


def _remove_result_role(plan: ModulePlan) -> ModulePlan:
    function = _function(plan)
    roles = tuple(role for role in function.available_roles if role != function.result.native_result_role)
    return _replace_function(plan, replace(function, available_roles=roles))


def _add_unavailable_writeback(plan: ModulePlan) -> ModulePlan:
    function = _function(plan)
    action = LifecycleActionPlan(
        owner_path="fmath.add_r8.X",
        phase="writeback",
        source_role="missing:role",
        handler_name="_handle_writeback",
    )
    return _replace_function(plan, replace(function, writeback_actions=(action,)))


def test_fmath_policy_projects_to_plan_and_deterministic_rendering():
    plan = _fmath_plan()
    add_r8 = _function(plan)

    assert WrapperPlanValidator().visit(plan) == ()
    assert len(plan.functions) == 85
    assert add_r8.python_name == "add_r8"
    assert add_r8.native_name == "ADD_R8"
    assert add_r8.external is True
    assert add_r8.bind_target == "ADD_R8"
    assert [argument.owner_path for argument in add_r8.arguments] == ["fmath.add_r8.X", "fmath.add_r8.Y"]
    assert [argument.python_action for argument in add_r8.arguments] == [
        PythonBarrierAction.SCALAR_VALUE,
        PythonBarrierAction.SCALAR_VALUE,
    ]
    assert [argument.native_action for argument in add_r8.arguments] == [
        NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS,
        NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS,
    ]
    assert [slot.index for slot in add_r8.bridge_abi.slots] == [0, 1]
    assert [
        (argument.native_call_slot.native_position, argument.native_call_slot.value_kind)
        for argument in add_r8.arguments
    ] == [
        (0, "addr"),
        (1, "addr"),
    ]
    assert add_r8.result is not None
    assert add_r8.result.codegen_action is CodegenAction.DIRECT_VALUE

    first = add_r8.arguments[0]
    assert first.binding_handoff.produced_role == "fmath.add_r8.X:value"
    assert first.binding_handoff.consumed_role == "fmath.add_r8.X:value"
    assert first.bridge_abi_slot.symbolic_role == "fmath.add_r8.X:value"
    assert first.native_call_slot.symbolic_role == "fmath.add_r8.X:value"
    assert first.native_call_slot.source_kind == "projection"
    assert first.native_call_slot.value_kind == "addr"

    rendered = WrapperPlanRenderer().visit(plan)
    assert "function fmath.add_r8 python=add_r8 native=ADD_R8" in rendered
    assert "python:scalar_value->_handle_python_scalar_value" in rendered
    assert "native:pass_call_local_address->_handle_native_call_local_address" in rendered
    assert "native_slot=0:addr:fmath.add_r8.X:value" in rendered
    assert "lifecycle=none" in rendered


def test_support_analyzer_reports_unsupported_generation_units_without_route_selection():
    module = parse_pyi_text(
        """
def sum_values(values: Float64[:]) -> Float64: ...
""",
        module_name="array_argument",
    )
    complete_semantic_policies(module)

    report = WrapperPlanSupportAnalyzer().visit(module)

    assert report.supported is False
    assert report.blockers[0].owner_path == "array_argument.sum_values"
    assert "not a first-lane primitive scalar" in report.blockers[0].reason
    with pytest.raises(ValueError, match="Unsupported wrapper-plan generation unit"):
        WrapperPlanner().visit(module)


def test_planner_fails_on_missing_policy_before_deriving_defaults():
    module = parse_pyi_text(
        """
def add(x: Float64, y: Float64) -> Float64: ...
""",
        module_name="missing_policy",
    )

    with pytest.raises(ValueError, match="missing completed scalar wrapper policy"):
        WrapperPlanner().visit(module)


@pytest.mark.parametrize(
    ("mutate", "expected_code"),
    [
        (_drop_primary_handlers, "unknown-primary-handler"),
        (_drop_secondary_handlers, "unknown-secondary-handler"),
        (_drop_bridge_slot, "missing-bridge-abi-slot"),
        (_drop_native_slot, "missing-native-call-slot"),
        (_break_handoff_role, "inconsistent-binding-handoff"),
        (_duplicate_symbolic_role, "duplicate-symbolic-role"),
        (_remove_result_role, "unavailable-result-role"),
        (_add_unavailable_writeback, "unavailable-writeback-role"),
    ],
)
def test_validator_reports_invariant_categories_before_backend_emission(mutate, expected_code):
    invalid = mutate(_fmath_plan())

    diagnostics = WrapperPlanValidator().visit(invalid)

    assert expected_code in {diagnostic.code for diagnostic in diagnostics}
