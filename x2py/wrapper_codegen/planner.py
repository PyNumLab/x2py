"""Hierarchical wrapper-plan construction from completed semantic policy."""

from __future__ import annotations

from typing import ClassVar

from x2py.semantics import models
from x2py.semantics.ownership import CodegenAction, NativeBarrierAction, PythonBarrierAction
from x2py.semantics.scalar_wrapper_policy import (
    ScalarWrapperArgumentPolicy,
    ScalarWrapperFunctionPolicy,
    ScalarWrapperNativeCallSlotPolicy,
    ScalarWrapperResultPolicy,
    completed_scalar_wrapper_policy,
)
from x2py.wrapper_codegen.plan import (
    ActionHandlerPlan,
    ArgumentTransferPlan,
    BindingHandoffPlan,
    BridgeAbiPlan,
    BridgeAbiSlotPlan,
    FunctionPlan,
    HandlerRegistryPlan,
    ModulePlan,
    NativeCallSlotPlan,
    ResultPlan,
)
from x2py.wrapper_codegen.support import WrapperPlanSupportAnalyzer
from x2py.wrapper_codegen.visitor import ClassVisitor


class WrapperPlanner(ClassVisitor):
    """Build route-neutral wrapper plans from completed semantic policies."""

    PYTHON_ACTION_REGISTRY: ClassVar[dict[PythonBarrierAction, str]] = {
        PythonBarrierAction.SCALAR_VALUE: "_handle_python_scalar_value",
    }
    NATIVE_ACTION_REGISTRY: ClassVar[dict[NativeBarrierAction, str]] = {
        NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS: "_handle_native_call_local_address",
        NativeBarrierAction.PASS_VALUE: "_handle_native_value",
    }
    RESULT_ACTION_REGISTRY: ClassVar[dict[CodegenAction, str]] = {
        CodegenAction.DIRECT_VALUE: "_handle_direct_scalar_result",
    }

    def __init__(self, *, support_analyzer: WrapperPlanSupportAnalyzer | None = None):
        """Create a planner with an optional support analyzer."""
        super().__init__()
        self.support_analyzer = support_analyzer or WrapperPlanSupportAnalyzer()

    def _visit_SemanticModule(self, module: models.SemanticModule) -> ModulePlan:
        """Return one module plan after whole-unit support analysis."""
        report = self.support_analyzer.visit(module)
        if not report.supported:
            raise ValueError(self._support_error(module.name, report.blockers))
        return ModulePlan(
            owner_path=module.name,
            functions=tuple(self.visit(function) for function in module.functions),
            handler_registry=self._handler_registry(),
        )

    def _visit_SemanticFunction(self, function: models.SemanticFunction) -> FunctionPlan:
        """Return one function plan from completed scalar wrapper policy."""
        policy = completed_scalar_wrapper_policy(function)
        arguments = tuple(
            self.visit(argument, native_slot=self._native_slot(policy, argument)) for argument in policy.arguments
        )
        result = self.visit(policy.result) if policy.result is not None else None
        return FunctionPlan(
            owner_path=policy.owner_path,
            python_name=policy.python_name,
            native_name=policy.native_name,
            external=policy.external,
            bind_target=policy.bind_target,
            arguments=arguments,
            result=result,
            bridge_abi=BridgeAbiPlan(policy.owner_path, tuple(argument.bridge_abi_slot for argument in arguments)),
            available_roles=self._available_roles(arguments, result),
        )

    def _visit_ScalarWrapperArgumentPolicy(
        self,
        policy: ScalarWrapperArgumentPolicy,
        *,
        native_slot: ScalarWrapperNativeCallSlotPolicy,
    ) -> ArgumentTransferPlan:
        """Return one argument transfer plan from completed scalar policy."""
        role = self._value_role(policy.owner_path)
        binding_handoff = self._binding_handoff(policy, role)
        bridge_slot = self._bridge_slot(policy, native_slot, role)
        return ArgumentTransferPlan(
            owner_path=policy.owner_path,
            python_name=policy.python_name,
            native_name=policy.native_name,
            python_position=policy.python_position,
            native_position=policy.native_position,
            semantic_type_name=policy.semantic_type_name,
            python_action=policy.python_barrier_action,
            native_action=policy.native_barrier_action,
            codegen_action=policy.codegen_action,
            binding_handoff=binding_handoff,
            bridge_abi_slot=bridge_slot,
            native_call_slot=self._native_slot_plan(native_slot, role),
        )

    def _visit_ScalarWrapperResultPolicy(self, policy: ScalarWrapperResultPolicy) -> ResultPlan:
        """Return one result plan from completed scalar result policy."""
        return ResultPlan(
            owner_path=policy.owner_path,
            semantic_type_name=policy.semantic_type_name,
            codegen_action=policy.codegen_action,
            python_action=policy.python_barrier_action,
            native_action=policy.native_barrier_action,
            native_result_role=f"{policy.owner_path}:native-result",
            python_result_role=f"{policy.owner_path}:python-result",
            handler_name=self.RESULT_ACTION_REGISTRY[policy.codegen_action],
        )

    def _binding_handoff(self, policy: ScalarWrapperArgumentPolicy, role: str) -> BindingHandoffPlan:
        """Return the binding-to-bridge handoff for one transfer."""
        return BindingHandoffPlan(
            owner_path=policy.owner_path,
            produced_role=role,
            consumed_role=role,
            python_action=policy.python_barrier_action,
            handler_name=self.PYTHON_ACTION_REGISTRY[policy.python_barrier_action],
        )

    def _bridge_slot(
        self,
        policy: ScalarWrapperArgumentPolicy,
        native_slot: ScalarWrapperNativeCallSlotPolicy,
        role: str,
    ) -> BridgeAbiSlotPlan:
        """Return the bridge ABI slot for one transfer."""
        return BridgeAbiSlotPlan(
            owner_path=policy.owner_path,
            index=native_slot.native_position,
            symbolic_role=role,
            native_action=policy.native_barrier_action,
            handler_name=self.NATIVE_ACTION_REGISTRY[policy.native_barrier_action],
        )

    def _native_slot_plan(self, native_slot: ScalarWrapperNativeCallSlotPolicy, role: str) -> NativeCallSlotPlan:
        """Return the native-call slot for one transfer."""
        return NativeCallSlotPlan(
            owner_path=native_slot.owner_path,
            native_position=native_slot.native_position,
            source_kind=native_slot.source_kind,
            python_position=native_slot.python_position,
            python_name=native_slot.python_name,
            native_name=native_slot.native_name,
            value_kind=native_slot.value_kind,
            symbolic_role=role,
            native_action=native_slot.native_barrier_action,
            codegen_action=native_slot.codegen_action,
        )

    def _handler_registry(self) -> HandlerRegistryPlan:
        """Return the class-owned completed action registry as plan data."""
        return HandlerRegistryPlan(
            python_action_handlers=self._handler_refs(self.PYTHON_ACTION_REGISTRY),
            native_action_handlers=self._handler_refs(self.NATIVE_ACTION_REGISTRY),
            result_action_handlers=self._handler_refs(self.RESULT_ACTION_REGISTRY),
        )

    def _native_slot(
        self,
        function_policy: ScalarWrapperFunctionPolicy,
        argument_policy: ScalarWrapperArgumentPolicy,
    ) -> ScalarWrapperNativeCallSlotPolicy:
        """Return the completed native-call slot for one argument policy."""
        for slot in function_policy.native_call_slots:
            if slot.owner_path == argument_policy.owner_path:
                return slot
        raise ValueError(f"{argument_policy.owner_path!r} is missing a completed native-call slot")

    def _available_roles(
        self,
        arguments: tuple[ArgumentTransferPlan, ...],
        result: ResultPlan | None,
    ) -> tuple[str, ...]:
        """Return symbolic values available after the native call."""
        roles = [argument.binding_handoff.produced_role for argument in arguments]
        if result is not None:
            roles.append(result.native_result_role)
        return tuple(roles)

    def _handler_refs(self, registry: dict[object, str]) -> tuple[ActionHandlerPlan, ...]:
        """Return handler registry entries as deterministic plan records."""
        return tuple(ActionHandlerPlan(action=action, handler_name=handler) for action, handler in registry.items())

    def _support_error(self, owner_path: str, blockers: object) -> str:
        """Return a compact unsupported-generation-unit error."""
        details = "; ".join(f"{item.owner_path}: {item.reason}" for item in blockers)
        return f"Unsupported wrapper-plan generation unit {owner_path!r}: {details}"

    def _value_role(self, owner_path: str) -> str:
        """Return the symbolic value role for one transfer owner."""
        return f"{owner_path}:value"

    def _handle_python_scalar_value(self, plan: object) -> object:
        """Registry target for scalar Python argument values."""
        return plan

    def _handle_native_call_local_address(self, plan: object) -> object:
        """Registry target for scalar call-local address native slots."""
        return plan

    def _handle_native_value(self, plan: object) -> object:
        """Registry target for scalar by-value native slots."""
        return plan

    def _handle_direct_scalar_result(self, plan: object) -> object:
        """Registry target for scalar direct-value results."""
        return plan
