"""Deterministic text rendering for wrapper plans."""

from __future__ import annotations

from x2py.wrapper_codegen.plan import (
    ActionHandlerPlan,
    ArgumentTransferPlan,
    FunctionPlan,
    HandlerRegistryPlan,
    LifecycleActionPlan,
    ModulePlan,
    ResultPlan,
)
from x2py.wrapper_codegen.visitor import ClassVisitor


class WrapperPlanRenderer(ClassVisitor):
    """Render wrapper plans for maintainer diagnostics."""

    def _visit_ModulePlan(self, plan: ModulePlan) -> str:
        """Render one module plan."""
        lines = [f"module {plan.owner_path}", self.visit(plan.handler_registry)]
        lines.extend(self.visit(function) for function in plan.functions)
        return "\n".join(lines)

    def _visit_HandlerRegistryPlan(self, plan: HandlerRegistryPlan) -> str:
        """Render action handler registries."""
        lines = ["handlers:"]
        lines.extend(self._handler_lines("python", plan.python_action_handlers))
        lines.extend(self._handler_lines("native", plan.native_action_handlers))
        lines.extend(self._handler_lines("result", plan.result_action_handlers))
        return "\n".join(lines)

    def _visit_FunctionPlan(self, plan: FunctionPlan) -> str:
        """Render one function plan."""
        lines = [
            f"function {plan.owner_path} python={plan.python_name} native={plan.native_name}",
            f"  external={plan.external} bind={plan.bind_target}",
            f"  available_roles={','.join(plan.available_roles)}",
        ]
        lines.extend(f"  {self.visit(argument)}" for argument in plan.arguments)
        if plan.result is not None:
            lines.append(f"  {self.visit(plan.result)}")
        lines.extend(self._lifecycle_lines(plan))
        return "\n".join(lines)

    def _visit_ArgumentTransferPlan(self, plan: ArgumentTransferPlan) -> str:
        """Render one argument transfer."""
        return (
            f"arg {plan.owner_path} py={plan.python_action.value} "
            f"py_handler={plan.binding_handoff.handler_name} "
            f"handoff={plan.binding_handoff.produced_role}->{plan.binding_handoff.consumed_role} "
            f"bridge_slot={self._bridge_slot_label(plan)} native={plan.native_action.value} "
            f"native_handler={self._bridge_handler_label(plan)} native_slot={self._native_slot_label(plan)}"
        )

    def _visit_ResultPlan(self, plan: ResultPlan) -> str:
        """Render one result plan."""
        return (
            f"result {plan.owner_path} codegen={plan.codegen_action.value} "
            f"python={plan.python_action.value} native={plan.native_action.value} "
            f"handler={plan.handler_name} role={plan.native_result_role}->{plan.python_result_role}"
        )

    def _visit_LifecycleActionPlan(self, plan: LifecycleActionPlan) -> str:
        """Render one lifecycle action."""
        return f"{plan.phase} {plan.owner_path} source={plan.source_role} handler={plan.handler_name}"

    def _handler_lines(
        self,
        label: str,
        handlers: tuple[ActionHandlerPlan, ...],
    ) -> tuple[str, ...]:
        """Render one handler registry group."""
        return tuple(f"  {label}:{handler.action.value}->{handler.handler_name}" for handler in handlers)

    def _lifecycle_lines(self, plan: FunctionPlan) -> tuple[str, ...]:
        """Render lifecycle actions in execution order."""
        actions = plan.writeback_actions + plan.cleanup_actions + plan.release_actions
        if not actions:
            return ("  lifecycle=none",)
        return tuple(f"  {self.visit(action)}" for action in actions)

    def _bridge_slot_label(self, plan: ArgumentTransferPlan) -> str:
        """Return a printable bridge ABI slot label."""
        if plan.bridge_abi_slot is None:
            return "<missing>"
        return f"{plan.bridge_abi_slot.index}:{plan.bridge_abi_slot.symbolic_role}"

    def _bridge_handler_label(self, plan: ArgumentTransferPlan) -> str:
        """Return a printable native handler label."""
        if plan.bridge_abi_slot is None:
            return "<missing>"
        return plan.bridge_abi_slot.handler_name

    def _native_slot_label(self, plan: ArgumentTransferPlan) -> str:
        """Return a printable native-call slot label."""
        if plan.native_call_slot is None:
            return "<missing>"
        slot = plan.native_call_slot
        return f"{slot.native_position}:{slot.value_kind}:{slot.symbolic_role}"
