"""Support analysis for wrapper-plan generation units."""

from __future__ import annotations

from x2py.semantics import models
from x2py.semantics.ownership import ObjectKind, PythonBarrierAction
from x2py.semantics.wrapper_policy import (
    CallbackABIKind,
    CallbackResultAction,
    ClassConstructorKind,
    ClassMethodKind,
    ClassSurfacePolicy,
    DerivedTypePolicy,
    DerivedNativeHandoff,
    FunctionWrapperPolicy,
    ModuleObjectAccessMechanism,
    ModuleVariablePolicy,
    NativeArrayDescriptorKind,
    NativeArrayHandleKind,
    NativeDescriptorHandoffABI,
)
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
            *(
                self.visit(function)
                for function in module.functions
                if function.visibility == "public" and self._is_module_function_export(function)
            ),
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

    @staticmethod
    def _is_module_function_export(function: models.SemanticFunction) -> bool:
        """Read the completed decision that hides type-bound root targets."""
        policy = function.metadata.get(models.RESOLVED_FUNCTION_WRAPPER_POLICY_METADATA)
        return not isinstance(policy, FunctionWrapperPolicy) or policy.module_export

    def _visit_SemanticVariable(self, variable: models.SemanticVariable) -> WrapperPlanSupportReport:
        """Return module-variable lane support from completed policy."""
        policy = variable.metadata.get(models.RESOLVED_MODULE_VARIABLE_POLICY_METADATA)
        if not isinstance(policy, ModuleVariablePolicy):
            blocker = WrapperPlanSupportBlocker(
                owner_path=variable.name,
                reason="missing completed module-variable policy",
            )
            return WrapperPlanSupportReport(owner_path=variable.name, blockers=(blocker,))
        return self._module_variable_support_report(policy)

    def _module_variable_support_report(self, policy: ModuleVariablePolicy) -> WrapperPlanSupportReport:
        """Classify one completed module-variable policy without backend inference."""
        blockers = list(policy.blockers)
        if policy.supported and policy.rank > 0 and policy.native_array_handle is None:
            blockers.append("rank-positive module array snapshots are not implemented by wrapper-plan lowering")
        return WrapperPlanSupportReport(
            owner_path=policy.owner_path,
            covered_lanes=self._module_variable_lanes(policy, blockers),
            blockers=tuple(WrapperPlanSupportBlocker(policy.owner_path, reason) for reason in blockers),
        )

    @staticmethod
    def _module_variable_lanes(policy: ModuleVariablePolicy, blockers: list[str]) -> tuple[str, ...]:
        """Return the completed scalar or descriptor module-variable lane."""
        if not policy.supported or blockers:
            return ()
        if policy.derived is not None:
            lane = {
                ModuleObjectAccessMechanism.DIRECT_ADDRESS: "aliased-derived-module-objects",
                ModuleObjectAccessMechanism.MEMBER_PROXY: "plain-derived-module-proxies",
                ModuleObjectAccessMechanism.VALUE_COPY: "derived-module-constant-values",
            }[policy.derived.access]
            return (lane,)
        if policy.native_array_handle is None:
            return ("scalar-module-variables",)
        return (f"{policy.native_array_handle.descriptor_kind.value}-module-handles",)

    def _visit_SemanticFunction(self, function: models.SemanticFunction) -> WrapperPlanSupportReport:
        """Return a stable support report for one semantic function."""
        policy = function.metadata.get(models.RESOLVED_FUNCTION_WRAPPER_POLICY_METADATA)
        if not isinstance(policy, FunctionWrapperPolicy):
            blocker = WrapperPlanSupportBlocker(
                owner_path=function.name,
                reason="missing completed function wrapper policy",
            )
            return WrapperPlanSupportReport(owner_path=function.name, blockers=(blocker,))
        blockers = (*(WrapperPlanSupportBlocker(policy.owner_path, reason) for reason in policy.blockers),)
        return WrapperPlanSupportReport(
            owner_path=policy.owner_path,
            covered_lanes=() if blockers else self._function_lanes(policy),
            blockers=blockers,
        )

    def _module_blockers(self, module: models.SemanticModule) -> tuple[WrapperPlanSupportBlocker, ...]:
        """Return blockers for module-level owners outside completed lanes."""
        blockers = []
        blockers.extend(self._class_orchestration_blockers(module))
        blockers.extend(self._owner_blockers(module.name, "overload sets", module.overload_sets))
        return tuple(blockers)

    def _class_orchestration_blockers(
        self,
        module: models.SemanticModule,
    ) -> tuple[WrapperPlanSupportBlocker, ...]:
        """Require completed class and method policy without backend inference."""
        blockers = []
        for semantic_class in self._semantic_classes(module.classes):
            policy = semantic_class.metadata.get(models.RESOLVED_DERIVED_TYPE_POLICY_METADATA)
            if not isinstance(policy, DerivedTypePolicy):
                blockers.append(
                    WrapperPlanSupportBlocker(
                        owner_path=f"{module.name}.{semantic_class.name}",
                        reason="missing completed derived-type policy",
                    )
                )
            elif policy.blockers:
                blockers.extend(WrapperPlanSupportBlocker(policy.owner_path, reason) for reason in policy.blockers)
            surface = semantic_class.metadata.get(models.RESOLVED_CLASS_SURFACE_POLICY_METADATA)
            if not isinstance(surface, ClassSurfacePolicy):
                blockers.append(
                    WrapperPlanSupportBlocker(
                        owner_path=f"{module.name}.{semantic_class.name}",
                        reason="missing completed class-surface policy",
                    )
                )
                continue
            blockers.extend(WrapperPlanSupportBlocker(surface.owner_path, reason) for reason in surface.blockers)
            blockers.extend(self._class_function_blockers(semantic_class))
        return tuple(blockers)

    @staticmethod
    def _semantic_classes(classes: list[models.SemanticClass]):
        """Yield classes in stable base-before-nested declaration order."""
        for semantic_class in classes:
            yield semantic_class
            yield from WrapperPlanSupportAnalyzer._semantic_classes(semantic_class.classes)

    @staticmethod
    def _class_function_blockers(
        semantic_class: models.SemanticClass,
    ) -> tuple[WrapperPlanSupportBlocker, ...]:
        """Return completed method/candidate blockers owned by one class."""
        functions = (
            *(method for method in semantic_class.methods if method.name != "__init__"),
            *(procedure for overload in semantic_class.overload_sets for procedure in overload.procedures),
        )
        blockers = []
        for function in functions:
            policy = function.metadata.get(models.RESOLVED_FUNCTION_WRAPPER_POLICY_METADATA)
            if not isinstance(policy, FunctionWrapperPolicy):
                blockers.append(
                    WrapperPlanSupportBlocker(
                        owner_path=f"{semantic_class.name}.{function.name}",
                        reason="missing completed class function policy",
                    )
                )
            else:
                blockers.extend(WrapperPlanSupportBlocker(policy.owner_path, reason) for reason in policy.blockers)
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
            *self._callback_argument_lanes(policy),
            *self._scalar_argument_lanes(policy),
            *self._string_argument_lanes(policy),
            *self._array_argument_lanes(policy),
            *self._derived_argument_lanes(policy),
        )

    @staticmethod
    def _callback_argument_lanes(policy: FunctionWrapperPolicy) -> tuple[str, ...]:
        """Classify callback runtime and typed transfer evidence explicitly."""
        callbacks = tuple(argument.callback for argument in policy.arguments if argument.callback is not None)
        if not callbacks:
            return ()
        transfers = tuple(
            transfer
            for callback in callbacks
            for transfer in (
                *callback.arguments,
                *((callback.result.transfer,) if callback.result.transfer is not None else ()),
            )
        )
        lanes = [
            "immediate-callbacks",
            "callback-context-runtime",
            "callback-same-thread-reentry",
            "callback-fatal-errors",
            *WrapperPlanSupportAnalyzer._callback_transfer_lanes({transfer.abi for transfer in transfers}),
        ]
        if any(callback.result.action is not CallbackResultAction.RETURN_VOID for callback in callbacks):
            lanes.append("callback-results")
        return tuple(lanes)

    @staticmethod
    def _callback_transfer_lanes(abis: set[CallbackABIKind]) -> tuple[str, ...]:
        """Map callback ABI kinds to their independently verified rollout lanes."""
        by_abi = (
            (CallbackABIKind.VALUE, "callback-scalar-values"),
            (CallbackABIKind.REFERENCE, "callback-scalar-storage"),
            (CallbackABIKind.DATA_AND_LENGTH, "callback-fixed-strings"),
            (CallbackABIKind.DATA_AND_SHAPE, "callback-arrays"),
            (CallbackABIKind.DERIVED_ADDRESS, "callback-derived-values"),
        )
        return tuple(lane for abi, lane in by_abi if abi in abis)

    def _output_lanes(self, policy: FunctionWrapperPolicy) -> tuple[str, ...]:
        """Return result and writeback lanes selected by completed output policy."""
        lanes = [
            *self._scalar_output_lanes(policy),
            *self._string_output_lanes(policy),
            *self._array_output_lanes(policy),
            *self._derived_output_lanes(policy),
        ]
        if not policy.results and not policy.writeback_actions:
            lanes.append("void-calls")
        return tuple(lanes)

    def _derived_argument_lanes(self, policy: FunctionWrapperPolicy) -> tuple[str, ...]:
        """Return scalar-derived wrapper handoff lanes."""
        arguments = tuple(
            argument
            for argument in policy.arguments
            if argument.callback is None and argument.ownership.kind is ObjectKind.DERIVED_TYPE
        )
        lanes = []
        if arguments:
            lanes.append("derived-wrapper-inputs")
        optional, mutable, typed_value, polymorphic = self._derived_argument_facts(arguments)
        if optional:
            lanes.append("optional-derived-inputs")
        if mutable:
            lanes.append("in-place-derived-inputs")
        if typed_value:
            lanes.append("typed-derived-value-inputs")
        if polymorphic:
            lanes.append("scalar-polymorphic-inputs")
        return tuple(lanes)

    @staticmethod
    def _derived_argument_facts(arguments: tuple) -> tuple[bool, bool, bool, bool]:
        """Collect the four independent scalar-derived rollout facts in one pass."""
        optional = mutable = typed_value = polymorphic = False
        for argument in arguments:
            optional |= argument.optional
            mutable |= argument.ownership.mutates_native
            typed_value |= bool(
                argument.derived is not None and argument.derived.native_handoff is DerivedNativeHandoff.TYPED_VALUE
            )
            polymorphic |= argument.polymorphic is not None
        return optional, mutable, typed_value, polymorphic

    def _derived_output_lanes(self, policy: FunctionWrapperPolicy) -> tuple[str, ...]:
        """Return wrapper-owned derived result source lanes."""
        results = tuple(result for result in policy.results if result.ownership.kind is ObjectKind.DERIVED_TYPE)
        return self._result_source_lanes(results, prefix="derived")

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
        ordinary = tuple(result for result in results if result.scalar_descriptor is None)
        lanes.extend(self._result_source_lanes(ordinary, prefix="scalar"))
        if any(result.scalar_descriptor is not None for result in results):
            lanes.append("scalar-descriptor-results")
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
        fixed = tuple(result for result in results if result.scalar_descriptor is None)
        lanes.extend(self._result_source_lanes(fixed, prefix="fixed-string"))
        if any(result.scalar_descriptor is not None for result in results):
            lanes.append("deferred-string-descriptor-results")
        return tuple(lanes)

    # Ordinary-array lane classification.
    def _array_argument_lanes(self, policy: FunctionWrapperPolicy) -> tuple[str, ...]:
        """Return ordinary-array buffer, address, and optional lanes."""
        arguments = tuple(
            argument for argument in policy.arguments if argument.ownership.kind is ObjectKind.NUMPY_ARRAY
        )
        handles = tuple(argument.native_array_handle for argument in arguments if argument.native_array_handle)
        candidates = (
            (self._has_array_action(arguments, PythonBarrierAction.ARRAY_STORAGE), "array-buffer-inputs"),
            (self._has_native_array_actual(arguments), "array-native-handle-actuals"),
            (self._has_excluded_native_array_actual(arguments), "array-handle-actuals-excluded"),
            (self._has_array_representation_copy(arguments), "array-copy-to-fortran"),
            (self._has_array_action(arguments, PythonBarrierAction.RAW_ADDRESS), "array-raw-address-inputs"),
            (self._has_optional_array(arguments), "array-optional-inputs"),
            (
                self._has_descriptor_kind(handles, NativeArrayDescriptorKind.ALLOCATABLE),
                "allocatable-descriptor-inputs",
            ),
            (
                self._has_descriptor_kind(handles, NativeArrayDescriptorKind.POINTER),
                "pointer-descriptor-inputs",
            ),
            (self._has_optional_native_handle(handles), "optional-native-array-handles"),
            (self._has_projected_native_handle(handles), "projected-native-array-handles"),
        )
        return tuple(lane for covered, lane in candidates if covered)

    def _has_array_action(self, arguments: tuple, action: PythonBarrierAction) -> bool:
        """Return whether one array argument uses the selected Python action."""
        return any(argument.python_barrier_action is action for argument in arguments)

    def _has_native_array_actual(self, arguments: tuple) -> bool:
        """Return whether ordinary arrays accept runtime handle actuals."""
        return any(argument.native_array_actual is not None for argument in arguments)

    def _has_excluded_native_array_actual(self, arguments: tuple) -> bool:
        """Keep ordinary arrays with an unimplemented handle source on legacy."""
        return any(
            argument.python_barrier_action is PythonBarrierAction.ARRAY_STORAGE
            and argument.native_array_actual is None
            and not argument.transformations
            for argument in arguments
        )

    @staticmethod
    def _has_array_representation_copy(arguments: tuple) -> bool:
        """Return whether binding-owned NumPy representation conversion is planned."""
        return any(argument.transformations for argument in arguments)

    def _has_optional_array(self, arguments: tuple) -> bool:
        """Return whether one ordinary or descriptor array is optional."""
        return any(argument.optional for argument in arguments)

    def _has_descriptor_kind(self, handles: tuple, descriptor_kind: NativeArrayDescriptorKind) -> bool:
        """Return whether one argument handle has the selected descriptor kind."""
        return any(handle.descriptor_kind is descriptor_kind for handle in handles)

    def _has_optional_native_handle(self, handles: tuple) -> bool:
        """Return whether omission is distinct from a present empty descriptor."""
        return any(handle.optional_absent for handle in handles)

    def _has_projected_native_handle(self, handles: tuple) -> bool:
        """Return whether mutation stays attached to caller descriptor storage."""
        return any(handle.handoff.abi is NativeDescriptorHandoffABI.DIRECT_STANDARD_DESCRIPTOR for handle in handles)

    def _array_output_lanes(self, policy: FunctionWrapperPolicy) -> tuple[str, ...]:
        """Return ordinary-array writeback and result-source lanes."""
        results = tuple(result for result in policy.results if result.ownership.kind is ObjectKind.NUMPY_ARRAY)
        owned_handles = tuple(
            result.native_array_handle
            for result in results
            if result.native_array_handle is not None
            and result.native_array_handle.handle_kind is NativeArrayHandleKind.OWNED_RESULT_DESCRIPTOR
        )
        candidates = (
            (self._has_array_writeback(policy), "array-writebacks"),
            *tuple((True, lane) for lane in self._result_source_lanes(results, prefix="array")),
            (self._has_owned_result_source(results, owned_handles, "direct_return"), "owned-allocatable-results"),
            (
                self._has_owned_result_source(results, owned_handles, "hidden_output"),
                "owned-allocatable-hidden-outputs",
            ),
            (bool(results and len(policy.results) > 1), "array-multiple-results"),
        )
        return tuple(lane for covered, lane in candidates if covered)

    def _has_array_writeback(self, policy: FunctionWrapperPolicy) -> bool:
        """Return whether one lifecycle action projects ordinary array identity."""
        return any(action.object_kind is ObjectKind.NUMPY_ARRAY for action in policy.writeback_actions)

    def _has_owned_result_source(self, results: tuple, handles: tuple, source_kind: str) -> bool:
        """Return whether wrapper-owned descriptor storage has one result source."""
        return any(result.source_kind == source_kind and result.native_array_handle in handles for result in results)

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
        lanes.extend(self._derived_type_lanes(module))
        lanes.extend(self._class_surface_lanes(module))
        lanes.extend(self._class_function_lanes(module))
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

    def _class_surface_lanes(self, module: models.SemanticModule) -> tuple[str, ...]:
        """Return completed public class orchestration lanes."""
        policies = tuple(
            semantic_class.metadata.get(models.RESOLVED_CLASS_SURFACE_POLICY_METADATA)
            for semantic_class in self._semantic_classes(module.classes)
        )
        surfaces = tuple(policy for policy in policies if isinstance(policy, ClassSurfacePolicy))
        facts = self._class_surface_facts(surfaces)
        candidates = (
            (bool(surfaces), "class-registration"),
            (ClassConstructorKind.DEFAULT_FIELDS in facts, "default-class-constructors"),
            (ClassConstructorKind.BOUND_PROCEDURE in facts, "bound-class-constructors"),
            (ClassConstructorKind.OVERLOAD_SET in facts, "overloaded-class-constructors"),
            (ClassMethodKind.INSTANCE in facts, "instance-methods"),
            (ClassMethodKind.STATIC in facts, "static-methods"),
            ("overloads" in facts, "class-overloads"),
            ("inheritance" in facts, "class-inheritance"),
            (self._class_has_finalizers(module), "class-finalizers"),
        )
        return tuple(lane for covered, lane in candidates if covered)

    @staticmethod
    def _class_surface_facts(surfaces: tuple[ClassSurfacePolicy, ...]) -> set[object]:
        """Collect constructor, method, overload, and inheritance facts once."""
        facts: set[object] = set()
        for surface in surfaces:
            facts.add(surface.constructor.kind)
            facts.update(method.kind for method in surface.methods)
            if surface.overloads:
                facts.add("overloads")
            if surface.base_identities:
                facts.add("inheritance")
        return facts

    def _class_has_finalizers(self, module: models.SemanticModule) -> bool:
        """Return whether any planned class owns a native finalizer."""
        for semantic_class in self._semantic_classes(module.classes):
            policy = semantic_class.metadata.get(models.RESOLVED_DERIVED_TYPE_POLICY_METADATA)
            if isinstance(policy, DerivedTypePolicy) and policy.finalizers:
                return True
        return False

    def _class_function_lanes(self, module: models.SemanticModule) -> tuple[str, ...]:
        """Reuse ordinary transfer lanes for every concrete class callable."""
        lanes = []
        for semantic_class in self._semantic_classes(module.classes):
            functions = (
                *(method for method in semantic_class.methods if method.name != "__init__"),
                *(procedure for overload in semantic_class.overload_sets for procedure in overload.procedures),
            )
            for function in functions:
                policy = function.metadata.get(models.RESOLVED_FUNCTION_WRAPPER_POLICY_METADATA)
                if not isinstance(policy, FunctionWrapperPolicy):
                    continue
                for lane in self._function_lanes(policy):
                    if lane not in lanes:
                        lanes.append(lane)
        return tuple(lanes)

    def _derived_type_lanes(self, module: models.SemanticModule) -> tuple[str, ...]:
        """Return public derived field families from completed class policy."""
        fields = self._derived_fields(module)
        families = {field.object_kind for field in fields}
        lanes = [
            lane
            for family, lane in (
                (ObjectKind.SCALAR, "derived-scalar-fields"),
                (ObjectKind.STRING, "derived-string-fields"),
                (ObjectKind.DERIVED_TYPE, "derived-borrowed-field-owners"),
            )
            if family in families
        ]
        if self._has_ordinary_derived_array_field(fields):
            lanes.append("derived-array-fields")
        if any(field.native_array_handle is not None for field in fields):
            lanes.append("derived-native-handle-fields")
        return tuple(lanes)

    @staticmethod
    def _derived_fields(module: models.SemanticModule):
        """Return completed public field policies without reconstructing them."""
        policies = tuple(
            semantic_class.metadata.get(models.RESOLVED_DERIVED_TYPE_POLICY_METADATA)
            for semantic_class in module.classes
        )
        return tuple(field for policy in policies if isinstance(policy, DerivedTypePolicy) for field in policy.fields)

    @staticmethod
    def _has_ordinary_derived_array_field(fields: tuple) -> bool:
        """Return whether one non-handle array field uses the live-view lane."""
        return any(
            field.object_kind is ObjectKind.NUMPY_ARRAY and field.native_array_handle is None for field in fields
        )

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
