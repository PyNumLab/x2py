"""Support analysis for wrapper-plan generation units."""

from __future__ import annotations

from x2py.semantics import models
from x2py.semantics.scalar_wrapper_policy import ScalarWrapperFunctionPolicy
from x2py.wrapper_codegen.plan import WrapperPlanSupportBlocker, WrapperPlanSupportReport
from x2py.wrapper_codegen.visitor import ClassVisitor


class WrapperPlanSupportAnalyzer(ClassVisitor):
    """Report whole-generation-unit eligibility without selecting a route."""

    def _visit_SemanticModule(self, module: models.SemanticModule) -> WrapperPlanSupportReport:
        """Return a stable support report for a semantic module."""
        blockers = [
            *self._module_blockers(module),
            *self._child_blockers(module),
        ]
        return WrapperPlanSupportReport(owner_path=module.name, blockers=tuple(blockers))

    def _visit_SemanticFunction(self, function: models.SemanticFunction) -> WrapperPlanSupportReport:
        """Return a stable support report for one semantic function."""
        policy = function.metadata.get(models.RESOLVED_SCALAR_WRAPPER_POLICY_METADATA)
        if not isinstance(policy, ScalarWrapperFunctionPolicy):
            blocker = WrapperPlanSupportBlocker(
                owner_path=function.name,
                reason="missing completed scalar wrapper policy",
            )
            return WrapperPlanSupportReport(owner_path=function.name, blockers=(blocker,))
        return WrapperPlanSupportReport(
            owner_path=policy.owner_path,
            blockers=tuple(WrapperPlanSupportBlocker(policy.owner_path, reason) for reason in policy.blockers),
        )

    def _module_blockers(self, module: models.SemanticModule) -> tuple[WrapperPlanSupportBlocker, ...]:
        """Return blockers for module-level owners outside the first scalar lane."""
        blockers = []
        blockers.extend(self._owner_blockers(module.name, "variables", module.variables))
        blockers.extend(self._owner_blockers(module.name, "classes", module.classes))
        blockers.extend(self._owner_blockers(module.name, "overload sets", module.overload_sets))
        return tuple(blockers)

    def _child_blockers(self, module: models.SemanticModule) -> tuple[WrapperPlanSupportBlocker, ...]:
        """Return blockers reported by supported child visitor methods."""
        blockers = []
        for function in module.functions:
            blockers.extend(self.visit(function).blockers)
        return tuple(blockers)

    def _owner_blockers(
        self,
        module_name: str,
        owner_kind: str,
        owners: list[object],
    ) -> tuple[WrapperPlanSupportBlocker, ...]:
        """Return one blocker for each unsupported module child owner."""
        return tuple(
            WrapperPlanSupportBlocker(
                owner_path=f"{module_name}.{getattr(owner, 'name', owner_kind)}",
                reason=f"{owner_kind} are outside the first scalar wrapper-plan lane",
            )
            for owner in owners
        )
