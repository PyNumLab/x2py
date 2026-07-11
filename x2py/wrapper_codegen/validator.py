"""Validation for route-neutral wrapper plans before backend emission."""

from __future__ import annotations

from collections import Counter

from x2py.wrapper_codegen.plan import (
    ActionHandlerPlan,
    ArgumentTransferPlan,
    FunctionPlan,
    HandlerRegistryPlan,
    LifecycleActionPlan,
    ModulePlan,
    ResultPlan,
    WrapperPlanDiagnostic,
)
from x2py.wrapper_codegen.visitor import ClassVisitor


class WrapperPlanValidator(ClassVisitor):
    """Validate wrapper-plan invariants before node emission."""

    def _visit_ModulePlan(self, plan: ModulePlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return diagnostics for every function in a module plan."""
        diagnostics = []
        for function in plan.functions:
            diagnostics.extend(self.visit(function, handler_registry=plan.handler_registry))
        return tuple(diagnostics)

    def _visit_FunctionPlan(
        self,
        plan: FunctionPlan,
        *,
        handler_registry: HandlerRegistryPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return diagnostics for one function plan."""
        diagnostics = list(self._duplicate_role_diagnostics(plan))
        for argument in plan.arguments:
            diagnostics.extend(self.visit(argument, handler_registry=handler_registry))
        if plan.result is not None:
            diagnostics.extend(
                self.visit(plan.result, available_roles=plan.available_roles, handler_registry=handler_registry)
            )
        for action in self._lifecycle_actions(plan):
            diagnostics.extend(self.visit(action, available_roles=plan.available_roles))
        return tuple(diagnostics)

    def _visit_ArgumentTransferPlan(
        self,
        plan: ArgumentTransferPlan,
        *,
        handler_registry: HandlerRegistryPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return diagnostics for one argument transfer."""
        diagnostics = []
        diagnostics.extend(self._primary_handler_diagnostics(plan, handler_registry))
        diagnostics.extend(self._secondary_handler_diagnostics(plan, handler_registry))
        diagnostics.extend(self._missing_slot_diagnostics(plan))
        diagnostics.extend(self._handoff_diagnostics(plan))
        return tuple(diagnostics)

    def _visit_ResultPlan(
        self,
        plan: ResultPlan,
        *,
        available_roles: tuple[str, ...],
        handler_registry: HandlerRegistryPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return diagnostics for one result plan."""
        diagnostics = list(self._result_handler_diagnostics(plan, handler_registry))
        if plan.native_result_role not in available_roles:
            diagnostics.append(self._diagnostic(plan.owner_path, "unavailable-result-role", plan.native_result_role))
        return tuple(diagnostics)

    def _visit_LifecycleActionPlan(
        self,
        plan: LifecycleActionPlan,
        *,
        available_roles: tuple[str, ...],
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return diagnostics for one lifecycle action."""
        if plan.source_role in available_roles:
            return ()
        return (self._diagnostic(plan.owner_path, f"unavailable-{plan.phase}-role", plan.source_role),)

    def _primary_handler_diagnostics(
        self,
        plan: ArgumentTransferPlan,
        handler_registry: HandlerRegistryPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return diagnostics for missing Python action handlers."""
        handlers = self._handler_map(handler_registry.python_action_handlers)
        if plan.python_action in handlers:
            return ()
        return (self._diagnostic(plan.owner_path, "unknown-primary-handler", plan.python_action.value),)

    def _secondary_handler_diagnostics(
        self,
        plan: ArgumentTransferPlan,
        handler_registry: HandlerRegistryPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return diagnostics for missing native action handlers."""
        handlers = self._handler_map(handler_registry.native_action_handlers)
        if plan.native_action in handlers:
            return ()
        return (self._diagnostic(plan.owner_path, "unknown-secondary-handler", plan.native_action.value),)

    def _result_handler_diagnostics(
        self,
        plan: ResultPlan,
        handler_registry: HandlerRegistryPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return diagnostics for missing result handlers."""
        handlers = self._handler_map(handler_registry.result_action_handlers)
        if plan.codegen_action in handlers:
            return ()
        return (self._diagnostic(plan.owner_path, "unknown-result-handler", plan.codegen_action.value),)

    def _missing_slot_diagnostics(self, plan: ArgumentTransferPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return diagnostics for absent bridge or native slots."""
        diagnostics = []
        if plan.bridge_abi_slot is None:
            diagnostics.append(self._diagnostic(plan.owner_path, "missing-bridge-abi-slot", plan.native_name))
        if plan.native_call_slot is None:
            diagnostics.append(self._diagnostic(plan.owner_path, "missing-native-call-slot", plan.native_name))
        return tuple(diagnostics)

    def _handoff_diagnostics(self, plan: ArgumentTransferPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return diagnostics for inconsistent transfer roles and actions."""
        if plan.bridge_abi_slot is None or plan.native_call_slot is None:
            return ()
        diagnostics = []
        diagnostics.extend(self._handoff_role_diagnostics(plan))
        diagnostics.extend(self._slot_action_diagnostics(plan))
        return tuple(diagnostics)

    def _handoff_role_diagnostics(self, plan: ArgumentTransferPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return diagnostics for inconsistent symbolic handoff roles."""
        role = plan.binding_handoff.consumed_role
        diagnostics = []
        if plan.binding_handoff.produced_role != role:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-binding-handoff", role))
        if plan.bridge_abi_slot is not None and plan.bridge_abi_slot.symbolic_role != role:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-bridge-handoff", role))
        if plan.native_call_slot is not None and plan.native_call_slot.symbolic_role != role:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-native-handoff", role))
        return tuple(diagnostics)

    def _slot_action_diagnostics(self, plan: ArgumentTransferPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return diagnostics for inconsistent slot actions or positions."""
        diagnostics = []
        if plan.bridge_abi_slot.native_action is not plan.native_action:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-bridge-action", plan.native_action.value)
            )
        if plan.native_call_slot.native_action is not plan.native_action:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-native-action", plan.native_action.value)
            )
        if plan.bridge_abi_slot.index != plan.native_call_slot.native_position:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-native-position", plan.native_name))
        return tuple(diagnostics)

    def _duplicate_role_diagnostics(self, plan: FunctionPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return diagnostics for duplicate argument symbolic roles."""
        roles = [argument.binding_handoff.produced_role for argument in plan.arguments]
        duplicates = sorted(role for role, count in Counter(roles).items() if count > 1)
        return tuple(self._diagnostic(plan.owner_path, "duplicate-symbolic-role", role) for role in duplicates)

    def _lifecycle_actions(self, plan: FunctionPlan) -> tuple[LifecycleActionPlan, ...]:
        """Return lifecycle actions in execution order."""
        return plan.writeback_actions + plan.cleanup_actions + plan.release_actions

    def _handler_map(self, handlers: tuple[ActionHandlerPlan, ...]) -> dict[object, str]:
        """Return a lookup for configured handler names."""
        return {handler.action: handler.handler_name for handler in handlers if handler.handler_name}

    def _diagnostic(self, owner_path: str, code: str, detail: object) -> WrapperPlanDiagnostic:
        """Return one stable owner-path diagnostic."""
        return WrapperPlanDiagnostic(owner_path=owner_path, code=code, message=str(detail))
