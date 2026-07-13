"""Support analysis for wrapper-plan generation units."""

from __future__ import annotations

from x2py.semantics import models
from x2py.semantics.wrapper_policy import (
    ModuleVariablePolicy,
    FunctionWrapperPolicy,
)
from x2py.semantics.ownership import PythonBarrierAction
from x2py.wrapper_codegen.plan import WrapperPlanSupportBlocker, WrapperPlanSupportReport
from x2py.wrapper_codegen.visitor import ClassVisitor


class WrapperPlanSupportAnalyzer(ClassVisitor):
    """Report whole-generation-unit eligibility without selecting a route."""

    def analyze(self, module: models.SemanticModule) -> WrapperPlanSupportReport:
        """Analyze one policy-completed generation unit for plan support."""
        return self.visit(module)

    def _visit_SemanticModule(self, module: models.SemanticModule) -> WrapperPlanSupportReport:
        """Return a stable support report for a semantic module."""
        child_reports = (
            *(self.visit(function) for function in module.functions if function.visibility == "public"),
            *(self.visit(variable) for variable in module.variables if variable.visibility == "public"),
        )
        blockers = [
            *self._module_blockers(module),
            *(blocker for report in child_reports for blocker in report.blockers),
        ]
        return WrapperPlanSupportReport(
            owner_path=module.name,
            covered_lanes=self._module_lanes(module, child_reports),
            blockers=tuple(blockers),
        )

    def _visit_SemanticVariable(self, variable: models.SemanticVariable) -> WrapperPlanSupportReport:
        """Return module-variable lane support from completed policy."""
        policy = variable.metadata.get(models.RESOLVED_MODULE_VARIABLE_POLICY_METADATA)
        if not isinstance(policy, ModuleVariablePolicy):
            blocker = WrapperPlanSupportBlocker(
                owner_path=variable.name,
                reason="missing completed module-variable policy",
            )
            return WrapperPlanSupportReport(owner_path=variable.name, blockers=(blocker,))
        lanes = ("scalar-module-variables",) if policy.supported else ()
        return WrapperPlanSupportReport(
            owner_path=policy.owner_path,
            covered_lanes=lanes,
            blockers=tuple(WrapperPlanSupportBlocker(policy.owner_path, reason) for reason in policy.blockers),
        )

    def _visit_SemanticFunction(self, function: models.SemanticFunction) -> WrapperPlanSupportReport:
        """Return a stable support report for one semantic function."""
        policy = function.metadata.get(models.RESOLVED_FUNCTION_WRAPPER_POLICY_METADATA)
        if not isinstance(policy, FunctionWrapperPolicy):
            blocker = WrapperPlanSupportBlocker(
                owner_path=function.name,
                reason="missing completed function wrapper policy",
            )
            return WrapperPlanSupportReport(owner_path=function.name, blockers=(blocker,))
        return WrapperPlanSupportReport(
            owner_path=policy.owner_path,
            covered_lanes=self._function_lanes(policy),
            blockers=tuple(WrapperPlanSupportBlocker(policy.owner_path, reason) for reason in policy.blockers),
        )

    def _module_blockers(self, module: models.SemanticModule) -> tuple[WrapperPlanSupportBlocker, ...]:
        """Return blockers for module-level owners outside completed lanes."""
        blockers = []
        blockers.extend(self._owner_blockers(module.name, "classes", module.classes))
        blockers.extend(self._owner_blockers(module.name, "overload sets", module.overload_sets))
        return tuple(blockers)

    def _covered_lanes(self, reports: tuple[WrapperPlanSupportReport, ...]) -> tuple[str, ...]:
        """Return stable supported-lane labels for one generation unit."""
        lanes = []
        for report in reports:
            for lane in report.covered_lanes:
                if lane not in lanes:
                    lanes.append(lane)
        return tuple(lanes)

    def _function_lanes(self, policy: FunctionWrapperPolicy) -> tuple[str, ...]:
        """Return completed first-lane coverage for one supported function."""
        if policy.blockers:
            return ()
        runtime_lanes = ["native-call-runtime"]
        if policy.status_error is not None:
            runtime_lanes.append("native-status-errors")
        return (*self._argument_lanes(policy), *self._output_lanes(policy), *runtime_lanes)

    def _argument_lanes(self, policy: FunctionWrapperPolicy) -> tuple[str, ...]:
        """Return input-related lanes selected by completed arguments."""
        actions = {argument.python_barrier_action for argument in policy.arguments}
        lanes = []
        if PythonBarrierAction.SCALAR_VALUE in actions:
            lanes.append("scalar-inputs")
        if PythonBarrierAction.SCALAR_STORAGE in actions:
            lanes.append("scalar-storage-inputs")
        if PythonBarrierAction.RAW_ADDRESS in actions:
            lanes.append("scalar-raw-address-inputs")
        if any(argument.optional for argument in policy.arguments):
            lanes.append("scalar-optional-inputs")
        if any(argument.descriptor_boundary for argument in policy.arguments):
            lanes.append("scalar-descriptor-inputs")
        return tuple(lanes)

    def _output_lanes(self, policy: FunctionWrapperPolicy) -> tuple[str, ...]:
        """Return result and writeback lanes selected by completed output policy."""
        lanes = []
        if policy.writeback_actions:
            lanes.append("scalar-writebacks")
        result_lane = "scalar-direct-results"
        if policy.result is not None and policy.result.source_kind == "hidden_output":
            result_lane = "scalar-hidden-outputs"
        if policy.result is not None:
            lanes.append(result_lane)
        if policy.result is None and not policy.writeback_actions:
            lanes.append("void-calls")
        return tuple(lanes)

    def _module_lanes(
        self,
        module: models.SemanticModule,
        reports: tuple[WrapperPlanSupportReport, ...],
    ) -> tuple[str, ...]:
        """Return child lanes plus explicit Python namespace coverage."""
        lanes = list(self._covered_lanes(reports))
        policies = (
            *(
                function.metadata.get(models.RESOLVED_FUNCTION_WRAPPER_POLICY_METADATA)
                for function in module.functions
                if function.visibility == "public"
            ),
            *(
                variable.metadata.get(models.RESOLVED_MODULE_VARIABLE_POLICY_METADATA)
                for variable in module.variables
                if variable.visibility == "public"
            ),
        )
        if any(
            any(export.namespace for export in policy.python_exports)
            for policy in policies
            if isinstance(policy, (FunctionWrapperPolicy, ModuleVariablePolicy))
        ):
            lanes.append("python-namespaces")
        return tuple(lanes)

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
                reason=f"{owner_kind} are outside the completed wrapper-plan lanes",
            )
            for owner in owners
        )
