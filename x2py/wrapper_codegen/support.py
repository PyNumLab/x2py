"""Support analysis for wrapper-plan generation units."""

from __future__ import annotations

from x2py.semantics import models
from x2py.semantics.ownership import ObjectKind, PythonBarrierAction
from x2py.semantics.wrapper_policy import FunctionWrapperPolicy, ModuleVariablePolicy
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
        capability_blockers = self._function_capability_blockers(function, policy)
        blockers = (
            *capability_blockers,
            *(WrapperPlanSupportBlocker(policy.owner_path, reason) for reason in policy.blockers),
        )
        return WrapperPlanSupportReport(
            owner_path=policy.owner_path,
            covered_lanes=() if blockers else self._function_lanes(policy),
            blockers=blockers,
        )

    def _function_capability_blockers(
        self,
        function: models.SemanticFunction,
        policy: FunctionWrapperPolicy,
    ) -> tuple[WrapperPlanSupportBlocker, ...]:
        """Keep source ABI optimizations on legacy until direct lowering owns them."""
        if not function.metadata.get("fortran_bind_c"):
            return ()
        return (
            WrapperPlanSupportBlocker(
                owner_path=policy.owner_path,
                reason="existing bind(C) direct-symbol calls are not implemented by wrapper-plan lowering",
            ),
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
        return (
            *self._scalar_argument_lanes(policy),
            *self._string_argument_lanes(policy),
            *self._array_argument_lanes(policy),
        )

    def _output_lanes(self, policy: FunctionWrapperPolicy) -> tuple[str, ...]:
        """Return result and writeback lanes selected by completed output policy."""
        lanes = [
            *self._scalar_output_lanes(policy),
            *self._string_output_lanes(policy),
            *self._array_output_lanes(policy),
        ]
        if not policy.results and not policy.writeback_actions:
            lanes.append("void-calls")
        return tuple(lanes)

    # Scalar lane classification.
    def _scalar_argument_lanes(self, policy: FunctionWrapperPolicy) -> tuple[str, ...]:
        """Return scalar input, address, optional, and descriptor lanes."""
        arguments = tuple(argument for argument in policy.arguments if argument.ownership.kind is ObjectKind.SCALAR)
        actions = {argument.python_barrier_action for argument in arguments}
        lanes = []
        if PythonBarrierAction.SCALAR_VALUE in actions:
            lanes.append("scalar-inputs")
        if PythonBarrierAction.SCALAR_STORAGE in actions:
            lanes.append("scalar-storage-inputs")
        if self._has_scalar_raw_address(policy):
            lanes.append("scalar-raw-address-inputs")
        if self._has_scalar_optional(policy):
            lanes.append("scalar-optional-inputs")
        if any(argument.descriptor_boundary for argument in arguments):
            lanes.append("scalar-descriptor-inputs")
        return tuple(lanes)

    def _has_scalar_raw_address(self, policy: FunctionWrapperPolicy) -> bool:
        """Return whether one scalar argument crosses as a raw address."""
        return any(
            argument.ownership.kind is ObjectKind.SCALAR
            and argument.python_barrier_action is PythonBarrierAction.RAW_ADDRESS
            for argument in policy.arguments
        )

    def _has_scalar_optional(self, policy: FunctionWrapperPolicy) -> bool:
        """Return whether one non-string scalar argument is optional."""
        return any(argument.optional and argument.ownership.kind is ObjectKind.SCALAR for argument in policy.arguments)

    def _scalar_output_lanes(self, policy: FunctionWrapperPolicy) -> tuple[str, ...]:
        """Return scalar writeback and result-source lanes."""
        lanes = []
        if any(action.object_kind is ObjectKind.SCALAR for action in policy.writeback_actions):
            lanes.append("scalar-writebacks")
        results = tuple(result for result in policy.results if result.ownership.kind is ObjectKind.SCALAR)
        lanes.extend(self._result_source_lanes(results, prefix="scalar"))
        if len(results) > 1:
            lanes.append("scalar-multiple-results")
        return tuple(lanes)

    # String lane classification.
    def _string_argument_lanes(self, policy: FunctionWrapperPolicy) -> tuple[str, ...]:
        """Return scalar-string input, address, and optional lanes."""
        actions = {
            argument.python_barrier_action
            for argument in policy.arguments
            if argument.ownership.kind is ObjectKind.STRING
        }
        lanes = []
        if PythonBarrierAction.STRING_STORAGE in actions:
            lanes.append("string-storage-inputs")
        if PythonBarrierAction.STRING_VALUE in actions:
            lanes.append("string-value-inputs")
        if self._has_string_raw_address(policy):
            lanes.append("string-raw-address-inputs")
        if self._has_string_optional(policy):
            lanes.append("string-optional-inputs")
        return tuple(lanes)

    def _has_string_raw_address(self, policy: FunctionWrapperPolicy) -> bool:
        """Return whether one scalar string crosses as a raw address."""
        return any(
            argument.ownership.kind is ObjectKind.STRING
            and argument.python_barrier_action is PythonBarrierAction.RAW_ADDRESS
            for argument in policy.arguments
        )

    def _has_string_optional(self, policy: FunctionWrapperPolicy) -> bool:
        """Return whether one scalar string argument is optional."""
        return any(argument.optional and argument.ownership.kind is ObjectKind.STRING for argument in policy.arguments)

    def _string_output_lanes(self, policy: FunctionWrapperPolicy) -> tuple[str, ...]:
        """Return scalar-string writeback and result-source lanes."""
        lanes = []
        if any(action.object_kind is ObjectKind.STRING for action in policy.writeback_actions):
            lanes.append("string-writebacks")
        results = tuple(result for result in policy.results if result.ownership.kind is ObjectKind.STRING)
        lanes.extend(self._result_source_lanes(results, prefix="fixed-string"))
        return tuple(lanes)

    # Ordinary-array lane classification.
    def _array_argument_lanes(self, policy: FunctionWrapperPolicy) -> tuple[str, ...]:
        """Return ordinary-array buffer, address, and optional lanes."""
        arguments = tuple(
            argument for argument in policy.arguments if argument.ownership.kind is ObjectKind.NUMPY_ARRAY
        )
        lanes = []
        if any(argument.python_barrier_action is PythonBarrierAction.ARRAY_STORAGE for argument in arguments):
            lanes.append("array-buffer-inputs")
        if any(argument.python_barrier_action is PythonBarrierAction.RAW_ADDRESS for argument in arguments):
            lanes.append("array-raw-address-inputs")
        if any(argument.optional for argument in arguments):
            lanes.append("array-optional-inputs")
        return tuple(lanes)

    def _array_output_lanes(self, policy: FunctionWrapperPolicy) -> tuple[str, ...]:
        """Return ordinary-array writeback and result-source lanes."""
        lanes = []
        if any(action.object_kind is ObjectKind.NUMPY_ARRAY for action in policy.writeback_actions):
            lanes.append("array-writebacks")
        results = tuple(result for result in policy.results if result.ownership.kind is ObjectKind.NUMPY_ARRAY)
        lanes.extend(self._result_source_lanes(results, prefix="array"))
        if results and len(policy.results) > 1:
            lanes.append("array-multiple-results")
        return tuple(lanes)

    def _result_source_lanes(self, results: tuple, *, prefix: str) -> tuple[str, ...]:
        """Return direct and hidden lane labels for one result family."""
        source_kinds = {result.source_kind for result in results}
        lanes = []
        if "direct_return" in source_kinds:
            lanes.append(f"{prefix}-direct-results")
        if "hidden_output" in source_kinds:
            lanes.append(f"{prefix}-hidden-outputs")
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
