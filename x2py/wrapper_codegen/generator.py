"""Public direct-generation boundary for editable wrapper plans."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from x2py.pipeline.wrapper_artifacts import (
    GeneratedSourceFile,
    GeneratedWrapperArtifacts,
    RenderedGeneratedWrapperArtifacts,
)
from x2py.semantics.ownership import (
    AssignmentMode,
    CodegenAction,
    DestructionPolicy,
    NativeBarrierAction,
    ObjectKind,
    OwnershipOwner,
    PythonBarrierAction,
    SetterAction,
    StorageMode,
    TransferMode,
)
from x2py.semantics.wrapper_policy import (
    ArgumentHandoffMode,
    BridgeDataAction,
    FIXED_STRING_RESULT_COPY_REASON,
    NATIVE_ARRAY_POINTER_C_DESCRIPTOR_HEADER,
    OWNED_NATIVE_ARRAY_HANDLE_COPY_REASON,
    ORDINARY_ARRAY_RESULT_COPY_REASON,
    ModuleGetterAction,
    NativeArrayDescriptorInterop,
    NativeArrayDescriptorKind,
    NativeArrayDescriptorOwnership,
    NativeArrayDestroyBehavior,
    NativeArrayHandleKind,
    NativeArrayHandleOrigin,
    NativeArrayOperation,
    NativeArrayOutputProjection,
    NativeArrayOwnerRetention,
    NativeArrayRelease,
    NativeArraySourceKind,
    NativeDescriptorHandoffABI,
    OptionalMode,
    PythonExceptionKind,
    RAW_STRING_ADDRESS_COPY_REASON,
    SCALAR_DESCRIPTOR_RESULT_COPY_REASON,
    STRING_INPUT_COPY_REASON,
    STRING_REPLACEMENT_COPY_REASON,
    STRING_STORAGE_COPY_REASON,
    TransformationAction,
    TransformationLayer,
    WritebackPhase,
)
from x2py.wrapper_codegen.c.binding import CBindingGenerator
from x2py.wrapper_codegen.fortran.bridge import FortranBridgeGenerator
from x2py.wrapper_codegen.plan import (
    ArgumentTransferPlan,
    DatatypeFamily,
    FunctionPlan,
    LifecycleActionPlan,
    ModulePlan,
    ModuleVariablePlan,
    NativeArrayHandlePlan,
    NativeCallSlotPlan,
    NamespacePlan,
    ResultPlan,
    WrapperPlanDiagnostic,
)
from x2py.wrapper_codegen.source_printers import CSourcePrinter, FortranSourcePrinter


class WrapperCodeGenerator:
    """Freeze, validate, directly lower, and print one wrapper plan."""

    def __init__(
        self,
        *,
        c_generator: CBindingGenerator | None = None,
        fortran_generator: FortranBridgeGenerator | None = None,
        c_printer: CSourcePrinter | None = None,
        fortran_printer: FortranSourcePrinter | None = None,
    ):
        self._c_generator = c_generator or CBindingGenerator()
        self._fortran_generator = fortran_generator or FortranBridgeGenerator()
        self._c_printer = c_printer or CSourcePrinter()
        self._fortran_printer = fortran_printer or FortranSourcePrinter()

    def generate(self, plan: ModulePlan) -> RenderedGeneratedWrapperArtifacts:
        """Consume exactly one editable plan and return rendered artifacts."""
        plan.freeze()
        self._validate_plan(plan)
        self._c_generator.require_supported(plan)
        self._fortran_generator.require_supported(plan)
        c_module, c_header = self._c_generator.visit(plan)
        fortran_module = self._fortran_generator.visit(plan)
        return self._rendered_artifacts(
            plan.owner_path,
            self._c_printer.doprint(c_module),
            self._c_printer.doprint(c_header),
            self._fortran_printer.doprint(fortran_module),
            runtime_support_keys=(("python_runtime",) if self._c_generator.requires_runtime_support(plan) else ()),
            required_headers=plan.required_headers,
        )

    def _validate_plan(self, plan: ModulePlan) -> None:
        """Reject complete-plan inconsistencies in the final frozen plan."""
        diagnostics = self._plan_diagnostics(plan)
        if diagnostics:
            raise ValueError(self._diagnostic_summary(diagnostics))

    def _plan_diagnostics(self, plan: ModulePlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return binding/bridge graph diagnostics before backend preflight."""
        diagnostics = []
        if plan.binding.owner_path != plan.owner_path:
            diagnostics.append(self._diagnostic(plan.owner_path, "binding-module-owner", plan.binding.owner_path))
        if plan.bridge.owner_path != plan.owner_path:
            diagnostics.append(self._diagnostic(plan.owner_path, "bridge-module-owner", plan.bridge.owner_path))
        diagnostics.extend(self._namespace_tree_diagnostics(plan))
        for namespace in plan.namespaces:
            diagnostics.extend(self._namespace_diagnostics(namespace))
            for function in namespace.functions:
                diagnostics.extend(self._function_diagnostics(function))
            for variable in namespace.variables:
                diagnostics.extend(self._module_variable_diagnostics(variable))
        diagnostics.extend(self._generated_symbol_diagnostics(plan))
        diagnostics.extend(self._required_header_diagnostics(plan))
        return tuple(diagnostics)

    def _required_header_diagnostics(self, plan: ModulePlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Require module headers to equal the completed handle-plan union."""
        handles = tuple(
            handle
            for namespace in plan.namespaces
            for handle in self._namespace_native_array_handles(namespace)
            if handle is not None
        )
        expected = self._native_array_required_headers(handles)
        if plan.required_headers == expected:
            return ()
        return (self._diagnostic(plan.owner_path, "inconsistent-required-headers", plan.required_headers),)

    def _namespace_native_array_handles(
        self,
        namespace: NamespacePlan,
    ) -> tuple[NativeArrayHandlePlan | None, ...]:
        """Return every datatype-varying native handle in one namespace."""
        return (
            *(argument.native_array_handle for function in namespace.functions for argument in function.arguments),
            *(result.native_array_handle for function in namespace.functions for result in function.results),
            *(variable.native_array_handle for variable in namespace.variables),
        )

    def _native_array_required_headers(self, handles: tuple[NativeArrayHandlePlan, ...]) -> tuple[str, ...]:
        """Return stable deduplicated headers selected by handle plans."""
        return tuple(dict.fromkeys(header for handle in handles for header in handle.required_headers))

    def _namespace_tree_diagnostics(self, plan: ModulePlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return root, ancestor, owner, and duplicate-path diagnostics."""
        paths = [namespace.python_path for namespace in plan.namespaces]
        counts = Counter(paths)
        diagnostics = []
        if () not in counts:
            diagnostics.append(self._diagnostic(plan.owner_path, "missing-root-namespace", ()))
        diagnostics.extend(
            self._diagnostic(plan.owner_path, "duplicate-namespace-path", path)
            for path, occurrences in counts.items()
            if occurrences > 1
        )
        path_set = set(paths)
        for namespace in plan.namespaces:
            diagnostics.extend(self._namespace_path_diagnostics(plan, namespace, path_set))
        return tuple(diagnostics)

    def _namespace_path_diagnostics(
        self,
        module: ModulePlan,
        namespace: NamespacePlan,
        paths: set[tuple[str, ...]],
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return owner, parent, and identifier diagnostics for one path."""
        diagnostics = []
        expected_owner = ".".join((module.owner_path, *namespace.python_path))
        if namespace.owner_path != expected_owner:
            diagnostics.append(self._diagnostic(namespace.owner_path, "inconsistent-namespace-owner", expected_owner))
        if namespace.python_path and namespace.python_path[:-1] not in paths:
            diagnostics.append(
                self._diagnostic(namespace.owner_path, "missing-parent-namespace", namespace.python_path[:-1])
            )
        diagnostics.extend(
            self._diagnostic(namespace.owner_path, "invalid-namespace-name", part)
            for part in namespace.python_path
            if not part.isidentifier()
        )
        return tuple(diagnostics)

    def _namespace_diagnostics(self, plan: NamespacePlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Reject ambiguous Python exports within one namespace."""
        return (*self._python_export_name_diagnostics(plan), *self._export_owner_diagnostics(plan))

    def _python_export_name_diagnostics(self, plan: NamespacePlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return duplicate local export-name diagnostics."""
        names = [function.binding.python_name for function in plan.functions]
        names.extend(name for variable in plan.variables for name in variable.binding.python_names)
        return tuple(
            self._diagnostic(plan.owner_path, "duplicate-python-export", name)
            for name, count in Counter(names).items()
            if count > 1
        )

    def _export_owner_diagnostics(self, plan: NamespacePlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return exported child-owner diagnostics."""
        diagnostics = []
        for function in plan.functions:
            expected_owner = f"{plan.owner_path}.{function.binding.python_name}"
            if function.owner_path != expected_owner:
                diagnostics.append(
                    self._diagnostic(function.owner_path, "inconsistent-function-export-owner", expected_owner)
                )
        for variable in plan.variables:
            if not variable.binding.python_names:
                continue
            expected_owner = f"{plan.owner_path}.{variable.binding.python_names[0]}"
            if variable.owner_path != expected_owner:
                diagnostics.append(
                    self._diagnostic(variable.owner_path, "inconsistent-variable-export-owner", expected_owner)
                )
        return tuple(diagnostics)

    def _generated_symbol_diagnostics(self, plan: ModulePlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Reject missing or colliding C/Fortran symbol stems before lowering."""
        owners_by_symbol: dict[str, list[str]] = {}
        diagnostics = list(self._namespace_symbol_diagnostics(plan))
        for namespace in plan.namespaces:
            for item in (*namespace.functions, *namespace.variables):
                if not item.symbol_name or not item.symbol_name.isidentifier():
                    diagnostics.append(self._diagnostic(item.owner_path, "invalid-generated-symbol", item.symbol_name))
                    continue
                owners_by_symbol.setdefault(item.symbol_name.casefold(), []).append(item.owner_path)
        diagnostics.extend(
            self._diagnostic(plan.owner_path, "duplicate-generated-symbol", f"{symbol}:{','.join(owners)}")
            for symbol, owners in owners_by_symbol.items()
            if len(owners) > 1
        )
        return tuple(diagnostics)

    def _namespace_symbol_diagnostics(self, plan: ModulePlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Reject namespace paths that collapse to one generated C symbol."""
        owners_by_symbol: dict[str, list[str]] = {}
        for namespace in plan.namespaces:
            symbol = "_".join(namespace.python_path).casefold() if namespace.python_path else "root"
            owners_by_symbol.setdefault(symbol, []).append(namespace.owner_path)
        return tuple(
            self._diagnostic(plan.owner_path, "duplicate-generated-namespace-symbol", f"{symbol}:{','.join(owners)}")
            for symbol, owners in owners_by_symbol.items()
            if len(owners) > 1
        )

    def _module_variable_diagnostics(
        self,
        plan: ModuleVariablePlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return getter, setter, and initialization consistency diagnostics."""
        diagnostics = []
        if plan.binding.getter_action is not plan.bridge.getter_action:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-module-getter-action", plan.binding.getter_action)
            )
        if not plan.binding.python_names:
            diagnostics.append(self._diagnostic(plan.owner_path, "missing-module-python-name", plan.owner_path))
        diagnostics.extend(self._module_getter_diagnostics(plan))
        diagnostics.extend(self._module_setter_diagnostics(plan))
        if plan.binding.initializer is not None and plan.binding.setter_action is not SetterAction.WRITE_THROUGH:
            diagnostics.append(self._diagnostic(plan.owner_path, "initializer-without-native-setter", plan.owner_path))
        return tuple(diagnostics)

    def _module_getter_diagnostics(self, plan: ModuleVariablePlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return module getter handoff diagnostics."""
        action = plan.binding.getter_action
        if action is ModuleGetterAction.NATIVE_ARRAY_HANDLE:
            return self._module_native_array_handle_diagnostics(plan)
        if action is ModuleGetterAction.CONSTANT_VALUE:
            diagnostics = []
            if plan.bridge.getter_role is not None:
                diagnostics.append(
                    self._diagnostic(plan.owner_path, "constant-has-bridge-getter", plan.bridge.getter_role)
                )
            if plan.binding.constant_value is None:
                diagnostics.append(self._diagnostic(plan.owner_path, "missing-module-constant-value", plan.owner_path))
            return tuple(diagnostics)
        if plan.bridge.getter_role is None:
            return (self._diagnostic(plan.owner_path, "missing-module-getter-role", action.value),)
        if action is ModuleGetterAction.NULLABLE_SNAPSHOT and plan.bridge.descriptor_kind not in {
            "allocatable",
            "pointer",
        }:
            return (self._diagnostic(plan.owner_path, "missing-module-descriptor-kind", action.value),)
        return ()

    def _module_native_array_handle_diagnostics(
        self,
        plan: ModuleVariablePlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate one stable borrowed module descriptor handle."""
        handle = plan.native_array_handle
        if handle is None:
            return (self._diagnostic(plan.owner_path, "missing-module-native-array-handle", None),)
        expected = (
            ("kind", handle.handle_kind, NativeArrayHandleKind.BORROWED_MODULE_DESCRIPTOR),
            ("origin", handle.origin, NativeArrayHandleOrigin.MODULE_VARIABLE),
            ("owner-retention", handle.owner_retention, NativeArrayOwnerRetention.NATIVE_MODULE),
            ("descriptor-ownership", handle.descriptor_ownership, NativeArrayDescriptorOwnership.BORROWED),
            ("output-projection", handle.output_projection, NativeArrayOutputProjection.NONE),
            ("release", handle.release, NativeArrayRelease.NATIVE_OWNER),
            ("destroy", handle.destroy_behavior, NativeArrayDestroyBehavior.NONE),
        )
        diagnostics = [
            self._diagnostic(plan.owner_path, f"invalid-module-handle-{name}", actual.value)
            for name, actual, required in expected
            if actual is not required
        ]
        if not handle.borrowed:
            diagnostics.append(self._diagnostic(plan.owner_path, "module-handle-not-borrowed", handle.borrowed))
        if plan.binding.setter_action is not SetterAction.REJECT_REPLACEMENT:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "module-handle-replacement-not-rejected", plan.binding.setter_action)
            )
        diagnostics.extend(self._native_array_handle_shape_diagnostics(plan.owner_path, handle))
        diagnostics.extend(self._native_descriptor_handoff_diagnostics(plan.owner_path, handle, None))
        return tuple(diagnostics)

    def _module_setter_diagnostics(self, plan: ModuleVariablePlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return module setter exposure and native-assignment diagnostics."""
        if plan.native_array_handle is not None:
            return self._module_handle_setter_diagnostics(plan)
        if plan.binding.setter_action is SetterAction.WRITE_THROUGH:
            return self._module_write_through_setter_diagnostics(plan)
        return self._module_nonwriting_setter_diagnostics(plan)

    def _module_handle_setter_diagnostics(self, plan: ModuleVariablePlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate stable module-handle replacement policy."""
        handle = plan.native_array_handle
        if handle is None:
            return ()
        diagnostics = []
        if plan.binding.setter_action is not handle.setter_action:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-module-handle-setter", plan.binding.setter_action)
            )
        if plan.bridge.native_assignment is not handle.native_assignment:
            diagnostics.append(
                self._diagnostic(
                    plan.owner_path,
                    "inconsistent-module-handle-assignment",
                    plan.bridge.native_assignment,
                )
            )
        if plan.bridge.setter_role is not None:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "module-handle-has-replacement-role", plan.bridge.setter_role)
            )
        return tuple(diagnostics)

    def _module_write_through_setter_diagnostics(
        self,
        plan: ModuleVariablePlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate one scalar module write-through setter."""
        diagnostics = []
        if plan.bridge.native_assignment is not AssignmentMode.VALUE_COPY:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-module-native-assignment", plan.bridge.native_assignment)
            )
        if plan.bridge.setter_role is None:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "missing-module-setter-role", plan.binding.setter_action.value)
            )
        return tuple(diagnostics)

    def _module_nonwriting_setter_diagnostics(
        self,
        plan: ModuleVariablePlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate an omitted or replacement-rejecting module setter."""
        diagnostics = []
        if plan.bridge.native_assignment is not AssignmentMode.NONE:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-module-native-assignment", plan.bridge.native_assignment)
            )
        if plan.bridge.setter_role is not None:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "setter-role-without-write-through", plan.bridge.setter_role)
            )
        diagnostics.extend(self._module_nonwriting_action_diagnostics(plan))
        return tuple(diagnostics)

    def _module_nonwriting_action_diagnostics(
        self,
        plan: ModuleVariablePlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate descriptor rejection and constant omission choices."""
        action = plan.binding.setter_action
        if action is SetterAction.REJECT_REPLACEMENT and plan.bridge.descriptor_kind not in {
            "allocatable",
            "pointer",
        }:
            return (self._diagnostic(plan.owner_path, "rejected-module-setter-without-descriptor", action.value),)
        if action is SetterAction.OMIT and plan.binding.getter_action is not ModuleGetterAction.CONSTANT_VALUE:
            return (self._diagnostic(plan.owner_path, "omitted-nonconstant-module-setter", action.value),)
        return ()

    def _function_diagnostics(self, plan: FunctionPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return ordering, handoff, result, and lifecycle diagnostics."""
        diagnostics = [
            *self._sequence_diagnostics(
                plan.owner_path,
                "python",
                tuple(argument.python_position for argument in plan.arguments),
                len(plan.arguments),
            ),
            *self._sequence_diagnostics(
                plan.owner_path,
                "native",
                tuple(slot.native_position for slot in plan.native_call_slots),
                len(plan.native_call_slots),
            ),
            *self._duplicate_role_diagnostics(plan),
            *self._available_role_diagnostics(plan),
            *self._function_output_diagnostics(plan),
            *self._string_result_aggregation_diagnostics(plan),
            *self._status_error_diagnostics(plan),
        ]
        slots = {slot.native_position: slot for slot in plan.native_call_slots}
        for slot in plan.native_call_slots:
            diagnostics.extend(self._native_slot_diagnostics(slot))
        for argument in plan.arguments:
            diagnostics.extend(self._argument_diagnostics(argument, slots, plan.available_roles))
        for result in plan.results:
            diagnostics.extend(self._result_diagnostics(result, slots, plan.available_roles))
        for action in (*plan.writeback_actions, *plan.cleanup_actions, *plan.release_actions):
            diagnostics.extend(self._lifecycle_diagnostics(action, plan.available_roles))
        diagnostics.extend(self._writeback_phase_diagnostics(plan))
        diagnostics.extend(self._string_writeback_diagnostics(plan))
        return tuple(diagnostics)

    def _argument_diagnostics(
        self,
        plan: ArgumentTransferPlan,
        function_slots: dict[int, NativeCallSlotPlan],
        available_roles: tuple[str, ...],
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return binding-to-bridge handoff and slot diagnostics."""
        diagnostics = [
            *self._argument_policy_consistency_diagnostics(plan),
            *self._argument_slot_consistency_diagnostics(plan, function_slots),
            *self._optional_argument_diagnostics(plan),
            *self._argument_family_diagnostics(plan, available_roles),
            *self._argument_transformation_diagnostics(plan),
            *self._argument_data_action_diagnostics(plan),
            *self._bridge_data_diagnostics(
                plan.owner_path,
                plan.bridge.data_action,
                plan.bridge.copy_reason,
            ),
        ]
        return tuple(diagnostics)

    # Layer-owned representation transformation validation.
    def _argument_transformation_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate layer ownership and lifecycle for explicit representation copies."""
        if plan.array is None or plan.array.native_order == plan.array.order:
            return (
                (self._diagnostic(plan.owner_path, "unexpected-transformations", plan.transformations),)
                if plan.transformations
                else ()
            )
        representation = self._array_representation_transformation_diagnostics(plan)
        if representation:
            return representation
        return (
            *self._transformation_phase_diagnostics(plan),
            *(
                diagnostic
                for transformation in plan.transformations
                for diagnostic in self._one_transformation_diagnostics(plan, transformation)
            ),
        )

    def _array_representation_transformation_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate whether an argument requires the supported representation pair."""
        array = plan.array
        if array is None:
            return (self._diagnostic(plan.owner_path, "missing-transformation-array", None),)
        if array.order != "ORDER_C" or array.native_order != "ORDER_F":
            return (
                self._diagnostic(
                    plan.owner_path,
                    "unsupported-array-representation-transform",
                    f"{array.order}:{array.native_order}",
                ),
            )
        return ()

    def _transformation_phase_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Require the lifecycle phases implied by completed ownership."""
        expected_phases = []
        if plan.binding.codegen_action is not CodegenAction.IDENTITY_OUTPUT:
            expected_phases.append(WritebackPhase.COPY_IN)
        if plan.mutates_native:
            expected_phases.append(WritebackPhase.COPY_OUT)
        expected_phases.append(WritebackPhase.CLEANUP)
        if tuple(item.phase for item in plan.transformations) == tuple(expected_phases):
            return ()
        return (
            self._diagnostic(
                plan.owner_path,
                "invalid-transformation-phases",
                tuple(item.phase.value for item in plan.transformations),
            ),
        )

    def _one_transformation_diagnostics(
        self,
        plan: ArgumentTransferPlan,
        transformation,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate one transformation's layer and action vocabulary."""
        diagnostics = []
        if transformation.layer is not TransformationLayer.BINDING:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-transformation-layer", transformation.layer.value)
            )
        expected_action = (
            TransformationAction.RELEASE_TEMPORARY
            if transformation.phase is WritebackPhase.CLEANUP
            else TransformationAction.COPY_ARRAY_REPRESENTATION
        )
        if transformation.action is not expected_action:
            diagnostics.append(
                self._diagnostic(
                    plan.owner_path,
                    "invalid-transformation-action",
                    transformation.action.value,
                )
            )
        return tuple(diagnostics)

    def _argument_family_diagnostics(
        self,
        plan: ArgumentTransferPlan,
        available_roles: tuple[str, ...],
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Dispatch one argument from its completed object-kind decision."""
        match plan.object_kind:
            case ObjectKind.SCALAR:
                diagnostics = list(self._scalar_boundary_diagnostics(plan))
                if plan.array is not None:
                    diagnostics.append(self._diagnostic(plan.owner_path, "unexpected-scalar-array-handoff", None))
                if plan.datatype_family is DatatypeFamily.STRING:
                    diagnostics.append(
                        self._diagnostic(
                            plan.owner_path,
                            "invalid-scalar-datatype-family",
                            plan.datatype_family.value,
                        )
                    )
                return tuple(diagnostics)
            case ObjectKind.STRING:
                diagnostics = list(self._string_boundary_diagnostics(plan))
                if plan.array is not None:
                    diagnostics.append(self._diagnostic(plan.owner_path, "unexpected-string-array-handoff", None))
                return tuple(diagnostics)
            case ObjectKind.NUMPY_ARRAY:
                return (
                    *self._array_boundary_diagnostics(plan),
                    *self._array_extent_reference_diagnostics(plan, available_roles),
                )
            case _:
                return (
                    self._diagnostic(
                        plan.owner_path,
                        "unsupported-argument-object-kind",
                        plan.object_kind.value,
                    ),
                )

    def _array_extent_reference_diagnostics(
        self,
        plan: ArgumentTransferPlan,
        available_roles: tuple[str, ...],
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Require every planned extent dependency to name a function role."""
        if plan.array is None:
            return ()
        return tuple(
            self._diagnostic(plan.owner_path, "unavailable-array-extent-reference", role)
            for axis_roles in plan.array.extent_reference_roles
            for role in axis_roles
            if role not in available_roles
        )

    def _argument_policy_consistency_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return cross-view role and completed-action diagnostics."""
        diagnostics = []
        role = plan.binding.handoff_role
        if plan.bridge.handoff_role != role:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-bridge-handoff", role))
        if plan.native_call_slot.symbolic_role != role:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-native-handoff", role))
        if plan.bridge.length_handoff_role != plan.binding.length_handoff_role:
            diagnostics.append(
                self._diagnostic(
                    plan.owner_path,
                    "inconsistent-length-handoff",
                    plan.binding.length_handoff_role,
                )
            )
        if plan.bridge.native_action is not plan.native_call_slot.native_action:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-native-action", plan.bridge.native_action.value)
            )
        if plan.bridge.data_action is not plan.native_call_slot.bridge_data_action:
            diagnostics.append(
                self._diagnostic(
                    plan.owner_path,
                    "inconsistent-bridge-data-action",
                    plan.native_call_slot.bridge_data_action.value,
                )
            )
        if plan.array is not plan.native_call_slot.array:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-array-handoff", plan.array))
        if plan.native_array_handle is not plan.native_call_slot.native_array_handle:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-native-array-handle", plan.native_array_handle)
            )
        diagnostics.extend(self._argument_completed_fact_diagnostics(plan))
        if plan.bridge.copy_reason != plan.native_call_slot.bridge_copy_reason:
            diagnostics.append(
                self._diagnostic(
                    plan.owner_path,
                    "inconsistent-bridge-copy-reason",
                    plan.native_call_slot.bridge_copy_reason,
                )
            )
        return tuple(diagnostics)

    def _argument_completed_fact_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return projected action, length, mutability, and nullability drift."""
        diagnostics = []
        if plan.binding.codegen_action is not plan.bridge.codegen_action:
            diagnostics.append(
                self._diagnostic(
                    plan.owner_path, "inconsistent-argument-codegen-action", plan.bridge.codegen_action.value
                )
            )
        if plan.binding.codegen_action is not plan.native_call_slot.codegen_action:
            diagnostics.append(
                self._diagnostic(
                    plan.owner_path,
                    "inconsistent-native-slot-codegen-action",
                    plan.native_call_slot.codegen_action.value,
                )
            )
        if plan.character_length != plan.native_call_slot.character_length:
            diagnostics.append(
                self._diagnostic(
                    plan.owner_path,
                    "inconsistent-argument-character-length",
                    plan.native_call_slot.character_length,
                )
            )
        if plan.binding.writable != plan.mutates_native:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-argument-mutability", plan.binding.writable)
            )
        if plan.binding.nullable != plan.nullable:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-argument-nullability", plan.binding.nullable)
            )
        if plan.native_call_slot.object_kind is not plan.object_kind:
            diagnostics.append(
                self._diagnostic(
                    plan.owner_path,
                    "inconsistent-argument-object-kind",
                    plan.native_call_slot.object_kind,
                )
            )
        return tuple(diagnostics)

    def _argument_slot_consistency_diagnostics(
        self,
        plan: ArgumentTransferPlan,
        function_slots: dict[int, NativeCallSlotPlan],
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return argument position and native-slot graph diagnostics."""
        diagnostics = []
        if plan.bridge.abi_position != plan.native_position:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-bridge-position", plan.native_position))
        if plan.native_call_slot.native_position != plan.native_position:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-native-position", plan.native_position))
        if plan.native_call_slot.python_position != plan.python_position:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-python-position", plan.python_position))
        if function_slots.get(plan.native_position) is not plan.native_call_slot:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-function-native-slot", plan.native_position)
            )
        if plan.native_call_slot.source_kind not in {"implicit", "projection"}:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-argument-native-slot", plan.native_call_slot.source_kind)
            )
        return tuple(diagnostics)

    def _argument_data_action_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Require the completed data action to match the selected scalar path."""
        expected = self._expected_argument_data_action(plan)
        if plan.bridge.data_action is expected:
            return ()
        return (
            self._diagnostic(
                plan.owner_path,
                "invalid-bridge-data-action",
                f"{plan.bridge.data_action.value}:{expected.value}",
            ),
        )

    def _expected_argument_data_action(self, plan: ArgumentTransferPlan) -> BridgeDataAction:
        """Return the data action implied by completed orthogonal selectors."""
        mode = plan.bridge.handoff_mode
        if mode is ArgumentHandoffMode.NATIVE_DESCRIPTOR:
            return self._expected_native_descriptor_data_action(plan)
        if mode is ArgumentHandoffMode.ARRAY_BUFFER:
            return BridgeDataAction.ASSOCIATE_VIEW
        if mode is ArgumentHandoffMode.CHARACTER_BUFFER:
            return BridgeDataAction.COPY_REPRESENTATION
        if plan.object_kind is ObjectKind.STRING and mode is ArgumentHandoffMode.OPAQUE_ADDRESS:
            return BridgeDataAction.COPY_REPRESENTATION
        if plan.bridge.optional_mode in {OptionalMode.REQUIRED_DESCRIPTOR, OptionalMode.DESCRIPTOR}:
            return self._expected_optional_descriptor_data_action(plan)
        if plan.bridge.optional_mode is OptionalMode.NULLABLE_VALUE or mode is ArgumentHandoffMode.OPAQUE_ADDRESS:
            return BridgeDataAction.ASSOCIATE_VIEW
        return BridgeDataAction.DIRECT_TRANSFER

    def _expected_native_descriptor_data_action(self, plan: ArgumentTransferPlan) -> BridgeDataAction:
        """Distinguish call-local facts from persistent projected descriptors."""
        handle = plan.native_array_handle
        if handle is not None and handle.handoff.abi is NativeDescriptorHandoffABI.DIRECT_STANDARD_DESCRIPTOR:
            return BridgeDataAction.DIRECT_TRANSFER
        return BridgeDataAction.ASSOCIATE_VIEW

    def _expected_optional_descriptor_data_action(self, plan: ArgumentTransferPlan) -> BridgeDataAction:
        """Return the scalar optional descriptor view/copy selection."""
        if plan.native_call_slot.value_kind == "allocatable":
            return BridgeDataAction.COPY_REPRESENTATION
        return BridgeDataAction.ASSOCIATE_VIEW

    # Scalar argument validation.
    def _scalar_boundary_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return completed Python/native scalar boundary consistency diagnostics."""
        action = plan.binding.python_action
        if action not in {
            PythonBarrierAction.SCALAR_VALUE,
            PythonBarrierAction.SCALAR_STORAGE,
            PythonBarrierAction.RAW_ADDRESS,
        }:
            return (self._diagnostic(plan.owner_path, "invalid-scalar-python-action", action.value),)
        expected = {
            PythonBarrierAction.SCALAR_STORAGE: NativeBarrierAction.PASS_STORAGE_ADDRESS,
            PythonBarrierAction.RAW_ADDRESS: NativeBarrierAction.PASS_RAW_ADDRESS,
        }.get(action)
        if expected is None:
            if plan.bridge.handoff_mode is ArgumentHandoffMode.OPAQUE_ADDRESS:
                return (self._diagnostic(plan.owner_path, "unexpected-opaque-address-handoff", action.value),)
            return ()
        diagnostics = []
        if plan.bridge.native_action is not expected:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-scalar-address-action", plan.bridge.native_action.value)
            )
        if plan.bridge.handoff_mode is not ArgumentHandoffMode.OPAQUE_ADDRESS:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-scalar-address-handoff", plan.bridge.handoff_mode.value)
            )
        if plan.bridge.data_action is not BridgeDataAction.ASSOCIATE_VIEW:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-scalar-address-data-action", plan.bridge.data_action.value)
            )
        if plan.binding.optional_mode is not OptionalMode.REQUIRED:
            diagnostics.append(self._diagnostic(plan.owner_path, "optional-scalar-address-boundary", action.value))
        return tuple(diagnostics)

    # Ordinary-array argument validation.
    def _array_boundary_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate one ordinary-array transfer selected by object kind."""
        array = plan.array
        if array is None:
            return (self._diagnostic(plan.owner_path, "missing-array-handoff", None),)
        if plan.native_array_handle is not None:
            return self._native_array_handle_argument_diagnostics(plan)
        diagnostics = [
            *self._array_ownership_diagnostics(plan),
            *self._array_action_diagnostics(plan),
            *self._array_scope_diagnostics(plan),
            *self._array_shape_diagnostics(plan),
            *self._native_array_actual_diagnostics(plan),
        ]
        return tuple(diagnostics)

    # Native-array-handle argument validation.
    def _native_array_handle_argument_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate one typed descriptor handle and its shared native slot."""
        handle = plan.native_array_handle
        if handle is None:
            return ()
        diagnostics = [
            *self._native_array_handle_argument_action_diagnostics(plan, handle),
            *self._native_array_handle_argument_ownership_diagnostics(plan, handle),
            *self._native_array_handle_shape_diagnostics(plan.owner_path, handle),
            *self._native_descriptor_handoff_diagnostics(plan.owner_path, handle, plan),
        ]
        if plan.array is not handle.array:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-handle-array-facet", plan.array))
        if plan.native_array_actual is not None:
            diagnostics.append(self._diagnostic(plan.owner_path, "descriptor-has-array-actual-policy", None))
        return tuple(diagnostics)

    def _native_array_handle_argument_action_diagnostics(
        self,
        plan: ArgumentTransferPlan,
        handle: NativeArrayHandlePlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate the shared action vocabulary for descriptor inputs."""
        diagnostics = []
        expected = (
            ("python-action", plan.binding.python_action, PythonBarrierAction.WRAPPER_INSTANCE),
            ("native-action", plan.bridge.native_action, NativeBarrierAction.PASS_NATIVE_DESCRIPTOR),
            ("handoff-mode", plan.bridge.handoff_mode, ArgumentHandoffMode.NATIVE_DESCRIPTOR),
        )
        diagnostics.extend(
            self._diagnostic(plan.owner_path, f"invalid-handle-{name}", actual.value)
            for name, actual, required in expected
            if actual is not required
        )
        projected = handle.handoff.abi is NativeDescriptorHandoffABI.DIRECT_STANDARD_DESCRIPTOR
        expected_codegen = CodegenAction.IN_PLACE_ARGUMENT if projected else CodegenAction.CALL_LOCAL_INPUT
        if plan.binding.codegen_action is not expected_codegen:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-handle-codegen-action", plan.binding.codegen_action.value)
            )
        return tuple(diagnostics)

    def _native_array_handle_argument_ownership_diagnostics(
        self,
        plan: ArgumentTransferPlan,
        handle: NativeArrayHandlePlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate caller ownership and absence semantics for descriptor inputs."""
        diagnostics = []
        if plan.ownership_owner is not OwnershipOwner.CALLER or handle.owner is not OwnershipOwner.CALLER:
            diagnostics.append(self._diagnostic(plan.owner_path, "invalid-handle-argument-owner", plan.ownership_owner))
        if plan.transfer_mode not in {TransferMode.CALL_LOCAL, TransferMode.IN_PLACE}:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-handle-argument-transfer", plan.transfer_mode.value)
            )
        expected_destruction = (
            DestructionPolicy.CALLER
            if handle.handoff.abi is NativeDescriptorHandoffABI.DIRECT_STANDARD_DESCRIPTOR
            else DestructionPolicy.NONE
        )
        if plan.destruction_policy is not expected_destruction:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-handle-argument-destruction", plan.destruction_policy.value)
            )
        expected_optional = OptionalMode.DESCRIPTOR if handle.optional_absent else OptionalMode.REQUIRED
        if plan.binding.optional_mode is not expected_optional:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-handle-presence-mode", plan.binding.optional_mode.value)
            )
        return tuple(diagnostics)

    def _array_ownership_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate caller-owned ordinary-array lifetime facts."""
        diagnostics = []
        expected = (
            ("object-kind", plan.object_kind, ObjectKind.NUMPY_ARRAY),
            ("owner", plan.ownership_owner, OwnershipOwner.CALLER),
            ("storage", plan.storage_mode, StorageMode.STACK),
            ("boundary-storage", plan.boundary_storage_mode, StorageMode.STACK),
        )
        diagnostics.extend(
            self._diagnostic(plan.owner_path, f"invalid-array-{name}", actual.value)
            for name, actual, required in expected
            if actual is not required
        )
        expected_transfer = TransferMode.IN_PLACE if plan.mutates_native else TransferMode.CALL_LOCAL
        expected_destruction = DestructionPolicy.CALLER if plan.mutates_native else DestructionPolicy.NONE
        if plan.transfer_mode is not expected_transfer:
            diagnostics.append(self._diagnostic(plan.owner_path, "invalid-array-transfer", plan.transfer_mode.value))
        if plan.destruction_policy is not expected_destruction:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-array-destruction", plan.destruction_policy.value)
            )
        return tuple(diagnostics)

    def _native_array_actual_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate accepted native-handle sources on the ordinary buffer ABI."""
        actual = plan.native_array_actual
        if actual is None:
            return ()
        array = plan.array
        expected_sources = (
            NativeArraySourceKind.NDARRAY,
            NativeArraySourceKind.ALLOCATABLE_HANDLE,
            NativeArraySourceKind.POINTER_HANDLE,
        )
        diagnostics = [
            *self._native_array_actual_source_diagnostics(plan, expected_sources),
            *self._native_array_actual_shape_diagnostics(plan),
            *self._native_array_actual_validation_diagnostics(plan),
        ]
        expected_order = None if array is None or array.rank == 1 else ("C" if array.order == "ORDER_C" else "F")
        if actual.order != expected_order:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-array-actual-order", actual.order))
        if plan.bridge.handoff_mode is not ArgumentHandoffMode.ARRAY_BUFFER:
            diagnostics.append(self._diagnostic(plan.owner_path, "array-actual-not-buffer-handoff", None))
        return tuple(diagnostics)

    def _native_array_actual_source_diagnostics(
        self,
        plan: ArgumentTransferPlan,
        expected_sources: tuple[NativeArraySourceKind, ...],
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate the explicit ndarray/handle accepted-source set."""
        actual = plan.native_array_actual
        if actual is None or actual.accepted_sources == expected_sources:
            return ()
        return (self._diagnostic(plan.owner_path, "invalid-array-actual-sources", actual.accepted_sources),)

    def _native_array_actual_shape_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate handle-actual rank and shape against the shared array facet."""
        actual = plan.native_array_actual
        array = plan.array
        if actual is None or (array is not None and actual.rank == array.rank and actual.shape == array.shape):
            return ()
        return (self._diagnostic(plan.owner_path, "inconsistent-array-actual-shape", actual.shape),)

    def _native_array_actual_validation_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate writeability, native byte order, and alignment flags."""
        actual = plan.native_array_actual
        if actual is None:
            return ()
        diagnostics = []
        if actual.writable != plan.binding.writable:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-array-actual-writeability", actual.writable)
            )
        if not actual.require_native_byte_order or not actual.require_aligned or not actual.require_contiguous:
            diagnostics.append(self._diagnostic(plan.owner_path, "incomplete-array-actual-validation", None))
        return tuple(diagnostics)

    def _native_array_handle_shape_diagnostics(
        self,
        owner_path: str,
        handle: NativeArrayHandlePlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate one concrete descriptor data facet."""
        diagnostics = [
            *self._native_array_handle_rank_diagnostics(owner_path, handle),
            *self._native_array_handle_buffer_role_diagnostics(owner_path, handle),
            *self._native_array_handle_header_diagnostics(owner_path, handle),
        ]
        if (
            handle.descriptor_kind is NativeArrayDescriptorKind.POINTER
            and handle.handle_kind is NativeArrayHandleKind.OWNED_RESULT_DESCRIPTOR
        ):
            diagnostics.append(self._diagnostic(owner_path, "pointer-result-without-stable-owner", None))
        return tuple(diagnostics)

    def _native_array_handle_rank_diagnostics(
        self,
        owner_path: str,
        handle: NativeArrayHandlePlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate concrete descriptor rank, shape, and axes."""
        array = handle.array
        if array.rank is None or not 1 <= array.rank <= 15:
            return (self._diagnostic(owner_path, "invalid-native-array-handle-rank", array.rank),)
        if len(array.shape) != array.rank or len(array.axes) != array.rank:
            return (self._diagnostic(owner_path, "inconsistent-native-array-handle-shape", array.shape),)
        return ()

    def _native_array_handle_buffer_role_diagnostics(
        self,
        owner_path: str,
        handle: NativeArrayHandlePlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Reject ordinary array-buffer ABI roles on a descriptor facet."""
        array = handle.array
        packed_roles = (
            *array.extent_roles,
            *array.upper_bound_roles,
            *array.stride_roles,
            array.runtime_rank_role,
            array.itemsize_role,
        )
        if any(role is not None for role in packed_roles):
            return (self._diagnostic(owner_path, "descriptor-has-array-buffer-roles", None),)
        return ()

    def _native_array_handle_header_diagnostics(
        self,
        owner_path: str,
        handle: NativeArrayHandlePlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate the build header selected by completed descriptor interop."""
        needs_cfi = handle.descriptor_interop is not NativeArrayDescriptorInterop.NONE or handle.handle_kind in {
            NativeArrayHandleKind.ARGUMENT_DESCRIPTOR,
            NativeArrayHandleKind.OPTIONAL_ABSENT_HANDLE,
            NativeArrayHandleKind.OWNED_RESULT_DESCRIPTOR,
        }
        expected_headers = (NATIVE_ARRAY_POINTER_C_DESCRIPTOR_HEADER,) if needs_cfi else ()
        if handle.required_headers == expected_headers:
            return ()
        return (self._diagnostic(owner_path, "incomplete-native-array-build-requirements", handle.required_headers),)

    def _native_descriptor_handoff_diagnostics(
        self,
        owner_path: str,
        handle: NativeArrayHandlePlan,
        argument: ArgumentTransferPlan | None,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate descriptor ABI roles without reconstructing its policy."""
        handoff = handle.handoff
        rank = handle.array.rank
        diagnostics = []
        if rank is None:
            return (self._diagnostic(owner_path, "missing-native-descriptor-rank", None),)
        expected_counts = (
            len(handoff.lower_bound_roles),
            len(handoff.extent_roles),
            len(handoff.stride_multiplier_roles),
        )
        diagnostics.extend(self._native_descriptor_abi_diagnostics(owner_path, handle, expected_counts))
        diagnostics.extend(self._native_descriptor_presence_diagnostics(owner_path, handle, argument))
        diagnostics.extend(self._native_array_operation_diagnostics(owner_path, handle))
        return tuple(diagnostics)

    def _native_descriptor_abi_diagnostics(
        self,
        owner_path: str,
        handle: NativeArrayHandlePlan,
        expected_counts: tuple[int, int, int],
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Dispatch exact role validation by typed descriptor ABI."""
        handlers = {
            NativeDescriptorHandoffABI.FACT_PACKED_CALL_LOCAL: self._fact_packed_descriptor_diagnostics,
            NativeDescriptorHandoffABI.DIRECT_STANDARD_DESCRIPTOR: self._direct_descriptor_diagnostics,
            NativeDescriptorHandoffABI.OWNED_RESULT_STORAGE: self._owned_descriptor_diagnostics,
        }
        try:
            handler = handlers[handle.handoff.abi]
        except KeyError:
            return (self._diagnostic(owner_path, "unknown-native-descriptor-handoff", handle.handoff.abi),)
        return handler(owner_path, handle, expected_counts)

    def _fact_packed_descriptor_diagnostics(
        self,
        owner_path: str,
        handle: NativeArrayHandlePlan,
        expected_counts: tuple[int, int, int],
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate every call-local descriptor fact role."""
        handoff = handle.handoff
        diagnostics = []
        expected_rank = handle.array.rank
        if expected_counts != (expected_rank, expected_rank, expected_rank):
            diagnostics.append(
                self._diagnostic(owner_path, "inconsistent-native-descriptor-axis-roles", expected_counts)
            )
        if None in {
            handoff.descriptor_pointer_role,
            handoff.base_addr_role,
            handoff.elem_len_role,
            handoff.rank_role,
        }:
            diagnostics.append(self._diagnostic(owner_path, "missing-native-descriptor-fact-role", None))
        if handoff.owner_storage_role is not None:
            diagnostics.append(self._diagnostic(owner_path, "fact-packed-has-owner-storage", None))
        return tuple(diagnostics)

    def _direct_descriptor_diagnostics(
        self,
        owner_path: str,
        handle: NativeArrayHandlePlan,
        expected_counts: tuple[int, int, int],
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate one persistent projected standard-descriptor pointer."""
        diagnostics = []
        if handle.handoff.descriptor_pointer_role is None or any(expected_counts):
            diagnostics.append(self._diagnostic(owner_path, "invalid-direct-native-descriptor-roles", None))
        if handle.output_projection is not NativeArrayOutputProjection.PROJECTED_HANDLE:
            diagnostics.append(self._diagnostic(owner_path, "direct-descriptor-without-projection", None))
        return tuple(diagnostics)

    def _owned_descriptor_diagnostics(
        self,
        owner_path: str,
        handle: NativeArrayHandlePlan,
        expected_counts: tuple[int, int, int],
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate persistent wrapper-owned result descriptor storage roles."""
        handoff = handle.handoff
        invalid = handoff.owner_storage_role is None or handoff.descriptor_pointer_role is not None
        if invalid or any(expected_counts):
            return (self._diagnostic(owner_path, "invalid-owned-native-descriptor-roles", None),)
        return ()

    def _native_descriptor_presence_diagnostics(
        self,
        owner_path: str,
        handle: NativeArrayHandlePlan,
        argument: ArgumentTransferPlan | None,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Keep Python absence distinct from descriptor allocation state."""
        presence = handle.handoff.presence_role
        if handle.optional_absent != (presence is not None):
            return (self._diagnostic(owner_path, "inconsistent-native-descriptor-presence", presence),)
        if argument is None:
            return ()
        if handle.optional_absent and argument.bridge.presence_role != presence:
            return (self._diagnostic(owner_path, "inconsistent-native-descriptor-presence-role", presence),)
        if not handle.optional_absent and argument.bridge.presence_role is not None:
            return (self._diagnostic(owner_path, "required-native-descriptor-has-presence", None),)
        return ()

    def _native_array_operation_diagnostics(
        self,
        owner_path: str,
        handle: NativeArrayHandlePlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Require every handle to expose its common runtime operations exactly once."""
        operations = handle.operations
        required = {NativeArrayOperation.SHAPE, NativeArrayOperation.ARRAY_ACTUAL, NativeArrayOperation.DESCRIPTOR}
        diagnostics = []
        if len(set(operations)) != len(operations) or not required.issubset(operations):
            diagnostics.append(self._diagnostic(owner_path, "incomplete-native-array-operations", operations))
        roles = handle.handoff.operation_roles
        if tuple(operation for operation, _role in roles) != operations or any(not role for _operation, role in roles):
            diagnostics.append(self._diagnostic(owner_path, "inconsistent-native-array-operation-roles", roles))
        if handle.destroy_behavior is NativeArrayDestroyBehavior.HANDLE_FINALIZER:
            if NativeArrayOperation.DESTROY not in operations:
                diagnostics.append(self._diagnostic(owner_path, "missing-native-array-destroy-operation", None))
        elif NativeArrayOperation.DESTROY in operations:
            diagnostics.append(self._diagnostic(owner_path, "borrowed-native-array-has-destroy-operation", None))
        return tuple(diagnostics)

    def _array_action_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Dispatch completed buffer or raw-address array actions."""
        action = plan.binding.python_action
        if action is PythonBarrierAction.ARRAY_STORAGE:
            return self._array_buffer_action_diagnostics(plan)
        if action is PythonBarrierAction.RAW_ADDRESS:
            return self._raw_array_action_diagnostics(plan)
        return (self._diagnostic(plan.owner_path, "invalid-array-python-action", action.value),)

    def _array_buffer_action_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate completed NumPy-buffer binding and bridge actions."""
        diagnostics = []
        if plan.bridge.native_action is not NativeBarrierAction.PASS_ARRAY_BUFFER:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-array-native-action", plan.bridge.native_action.value)
            )
        if plan.bridge.handoff_mode is not ArgumentHandoffMode.ARRAY_BUFFER:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-array-handoff-mode", plan.bridge.handoff_mode.value)
            )
        if plan.bridge.data_action is not BridgeDataAction.ASSOCIATE_VIEW:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-array-data-action", plan.bridge.data_action.value)
            )
        if plan.binding.codegen_action not in {
            CodegenAction.CALL_LOCAL_INPUT,
            CodegenAction.IN_PLACE_ARGUMENT,
            CodegenAction.IDENTITY_OUTPUT,
        }:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-array-codegen-action", plan.binding.codegen_action.value)
            )
        return tuple(diagnostics)

    def _raw_array_action_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate one raw array address through the shared action vocabulary."""
        diagnostics = []
        if plan.bridge.native_action is not NativeBarrierAction.PASS_RAW_ADDRESS:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-raw-array-native-action", plan.bridge.native_action.value)
            )
        if plan.bridge.handoff_mode is not ArgumentHandoffMode.OPAQUE_ADDRESS:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-raw-array-handoff-mode", plan.bridge.handoff_mode.value)
            )
        if plan.bridge.data_action is not BridgeDataAction.ASSOCIATE_VIEW:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-raw-array-data-action", plan.bridge.data_action.value)
            )
        if plan.binding.codegen_action not in {CodegenAction.CALL_LOCAL_INPUT, CodegenAction.IN_PLACE_ARGUMENT}:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-raw-array-codegen-action", plan.binding.codegen_action.value)
            )
        return tuple(diagnostics)

    def _array_scope_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Keep array buffers and raw addresses on their completed scopes."""
        if plan.binding.python_action is PythonBarrierAction.RAW_ADDRESS:
            return self._raw_array_scope_diagnostics(plan)
        diagnostics = []
        if plan.binding.optional_mode not in {OptionalMode.REQUIRED, OptionalMode.NULLABLE_VALUE}:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-array-optional-mode", plan.binding.optional_mode.value)
            )
        if plan.binding.descriptor_boundary:
            diagnostics.append(self._diagnostic(plan.owner_path, "descriptor-backed-ordinary-array", plan.nullable))
        if plan.nullable and plan.binding.optional_mode is OptionalMode.REQUIRED:
            diagnostics.append(self._diagnostic(plan.owner_path, "nullable-required-ordinary-array", True))
        if plan.projects_result and plan.result_position is None:
            diagnostics.append(self._diagnostic(plan.owner_path, "missing-array-result-position", None))
        return tuple(diagnostics)

    def _raw_array_scope_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Require one non-optional, non-projecting raw array address."""
        diagnostics = []
        if plan.binding.optional_mode is not OptionalMode.REQUIRED:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "optional-raw-array-address", plan.binding.optional_mode.value)
            )
        if plan.nullable or plan.binding.descriptor_boundary:
            diagnostics.append(self._diagnostic(plan.owner_path, "descriptor-backed-raw-array", plan.nullable))
        if plan.projects_result or plan.result_position is not None:
            diagnostics.append(self._diagnostic(plan.owner_path, "projected-raw-array-address", plan.result_position))
        return tuple(diagnostics)

    def _array_shape_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Dispatch buffer or raw-pointee shape and ABI-role validation."""
        array = plan.array
        if array is None:
            return ()
        if plan.binding.python_action is PythonBarrierAction.RAW_ADDRESS:
            return self._raw_array_shape_diagnostics(plan)
        diagnostics = []
        if array.rank is None:
            diagnostics.extend(self._assumed_rank_array_diagnostics(plan))
        else:
            diagnostics.extend(self._concrete_rank_array_diagnostics(plan))
        diagnostics.extend(self._array_layout_role_diagnostics(plan))
        diagnostics.extend(self._array_handoff_role_diagnostics(plan))
        diagnostics.extend(self._array_itemsize_diagnostics(plan))
        return tuple(diagnostics)

    def _raw_array_shape_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate concrete dense pointee facts without packed buffer roles."""
        return (
            *self._raw_array_rank_diagnostics(plan),
            *self._raw_array_layout_diagnostics(plan),
            *self._raw_array_buffer_role_diagnostics(plan),
            *self._array_handoff_role_diagnostics(plan),
            *self._raw_array_itemsize_diagnostics(plan),
        )

    def _raw_array_rank_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Require one concrete supported raw-pointee rank and shape."""
        array = plan.array
        if array is None:
            return ()
        if array.rank is None or not 1 <= array.rank <= 15:
            return (self._diagnostic(plan.owner_path, "invalid-raw-array-rank", array.rank),)
        if len(array.shape) != array.rank or len(array.axes) != array.rank:
            return (self._diagnostic(plan.owner_path, "inconsistent-raw-array-rank", array.rank),)
        return ()

    def _raw_array_layout_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Require the completed dense raw-address category and orientation."""
        array = plan.array
        if array is None:
            return ()
        diagnostics = []
        if array.category != "raw_address":
            diagnostics.append(self._diagnostic(plan.owner_path, "invalid-raw-array-category", array.category))
        if array.order not in {None, "ORDER_F", "ORDER_C"}:
            diagnostics.append(self._diagnostic(plan.owner_path, "invalid-raw-array-order", array.order))
        if array.contiguous is not True or any(axis != "dense" for axis in array.axes):
            diagnostics.append(self._diagnostic(plan.owner_path, "invalid-raw-array-layout", array.axes))
        return tuple(diagnostics)

    def _raw_array_buffer_role_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Forbid NumPy-buffer ABI roles on an opaque raw address."""
        array = plan.array
        if array is None:
            return ()
        buffer_roles = (
            *array.extent_roles,
            *array.upper_bound_roles,
            *array.stride_roles,
            array.runtime_rank_role,
            array.itemsize_role,
        )
        if any(role is not None for role in buffer_roles):
            return (self._diagnostic(plan.owner_path, "unexpected-raw-array-buffer-roles", None),)
        return ()

    def _raw_array_itemsize_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Require fixed itemsize only for raw character-array pointees."""
        array = plan.array
        if array is None:
            return ()
        if plan.datatype_family is DatatypeFamily.STRING:
            if array.itemsize is None or array.itemsize <= 0:
                return (self._diagnostic(plan.owner_path, "invalid-raw-character-array-itemsize", None),)
            return ()
        if array.itemsize is not None:
            return (self._diagnostic(plan.owner_path, "unexpected-raw-array-itemsize", array.itemsize),)
        return ()

    def _array_handoff_role_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate ordinary-array data, extent, and shape-reference roles."""
        array = plan.array
        if array is None:
            return ()
        diagnostics = []
        if array.data_role != plan.binding.handoff_role:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-array-data-role", array.data_role))
        if any(not role for role in array.extent_roles):
            diagnostics.append(self._diagnostic(plan.owner_path, "missing-array-extent-role", array.extent_roles))
        if len(array.extent_reference_roles) != len(array.shape):
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-array-extent-reference-count", array.extent_reference_roles)
            )
        return tuple(diagnostics)

    def _array_itemsize_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate fixed-width character itemsize fields only on character arrays."""
        array = plan.array
        if array is None:
            return ()
        if plan.datatype_family is DatatypeFamily.STRING:
            if array.itemsize is None or array.itemsize <= 0 or array.itemsize_role is None:
                return (self._diagnostic(plan.owner_path, "invalid-array-itemsize", array.itemsize),)
            return ()
        if array.itemsize is not None or array.itemsize_role is not None:
            return (self._diagnostic(plan.owner_path, "unexpected-array-itemsize", array.itemsize),)
        return ()

    def _concrete_rank_array_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate fixed-rank shape and layout facts."""
        array = plan.array
        if array is None or array.rank is None:
            return ()
        diagnostics = []
        if not 1 <= array.rank <= 15:
            diagnostics.append(self._diagnostic(plan.owner_path, "invalid-array-rank", array.rank))
        if len(array.shape) != array.rank or len(array.axes) != array.rank:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-array-rank", array.rank))
        if len(array.extent_roles) != array.rank or array.runtime_rank_role is not None:
            diagnostics.append(self._diagnostic(plan.owner_path, "invalid-array-rank-roles", array.extent_roles))
        return tuple(diagnostics)

    def _assumed_rank_array_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate the one-through-fifteen runtime-rank ABI."""
        array = plan.array
        if array is None or array.rank is not None:
            return ()
        diagnostics = []
        if array.category != "assumed_rank" or array.shape != ("...",):
            diagnostics.append(self._diagnostic(plan.owner_path, "invalid-assumed-rank-array", array.shape))
        if len(array.extent_roles) != 15 or array.runtime_rank_role is None:
            diagnostics.append(self._diagnostic(plan.owner_path, "invalid-assumed-rank-roles", array.extent_roles))
        return tuple(diagnostics)

    def _array_layout_role_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate dense versus stride-aware ABI fields."""
        array = plan.array
        if array is None:
            return ()
        return (
            *self._array_order_diagnostics(plan),
            *self._array_axis_mode_diagnostics(plan),
            *self._array_stride_role_diagnostics(plan),
        )

    def _array_order_diagnostics(self, plan: ArgumentTransferPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate the completed ordinary-array order marker."""
        array = plan.array
        if array is None:
            return ()
        diagnostics = []
        if array.order not in {None, "ORDER_F", "ORDER_C"}:
            diagnostics.append(self._diagnostic(plan.owner_path, "invalid-array-order", array.order))
        if array.native_order not in {None, "ORDER_F", "ORDER_C"}:
            diagnostics.append(self._diagnostic(plan.owner_path, "invalid-native-array-order", array.native_order))
        return tuple(diagnostics)

    def _array_axis_mode_diagnostics(self, plan: ArgumentTransferPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate dense versus stride-aware axis markers."""
        array = plan.array
        if array is None:
            return ()
        if array.order not in {None, "ORDER_F", "ORDER_C"}:
            return ()
        if array.contiguous not in {True, False}:
            return (self._diagnostic(plan.owner_path, "invalid-array-contiguity", array.contiguous),)
        if array.contiguous is True and any(axis != "dense" for axis in array.axes):
            return (self._diagnostic(plan.owner_path, "invalid-array-axis-modes", array.axes),)
        if array.contiguous is False and "strided" not in array.axes:
            return (self._diagnostic(plan.owner_path, "invalid-array-axis-modes", array.axes),)
        return ()

    def _array_stride_role_diagnostics(self, plan: ArgumentTransferPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate stride metadata presence or absence from completed contiguity."""
        array = plan.array
        if array is None:
            return ()
        if array.contiguous is False:
            return (
                *self._required_array_stride_role_diagnostics(plan),
                *self._array_stride_role_count_diagnostics(plan),
            )
        if array.upper_bound_roles or array.stride_roles:
            return (self._diagnostic(plan.owner_path, "unexpected-dense-array-stride-roles", None),)
        return ()

    def _required_array_stride_role_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Require positive-stride metadata and a Fortran-oriented layout."""
        array = plan.array
        if array is not None and (array.order == "ORDER_C" or not array.upper_bound_roles or not array.stride_roles):
            return (self._diagnostic(plan.owner_path, "invalid-strided-array-layout", array.order),)
        return ()

    def _array_stride_role_count_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Require one upper bound and element stride per array extent."""
        array = plan.array
        if array is None:
            return ()
        diagnostics = []
        if len(array.upper_bound_roles) != len(array.extent_roles):
            diagnostics.append(self._diagnostic(plan.owner_path, "invalid-array-upper-bound-roles", None))
        if len(array.stride_roles) != len(array.extent_roles):
            diagnostics.append(self._diagnostic(plan.owner_path, "invalid-array-stride-roles", None))
        return tuple(diagnostics)

    # String argument validation.
    def _string_boundary_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Dispatch completed string-value, storage, or raw-address validation."""
        if plan.datatype_family is not DatatypeFamily.STRING:
            return (
                self._diagnostic(
                    plan.owner_path,
                    "invalid-string-datatype-family",
                    plan.datatype_family.value,
                ),
            )
        action = plan.binding.python_action
        if action is PythonBarrierAction.STRING_VALUE:
            return (*self._string_value_action_diagnostics(plan), *self._string_length_diagnostics(plan))
        if action is PythonBarrierAction.STRING_STORAGE:
            return self._string_address_diagnostics(
                plan,
                native_action=NativeBarrierAction.PASS_STORAGE_ADDRESS,
                storage_mode=StorageMode.ALIAS,
                copy_reason=STRING_STORAGE_COPY_REASON,
                label="storage",
            )
        if action is PythonBarrierAction.RAW_ADDRESS:
            return self._string_address_diagnostics(
                plan,
                native_action=NativeBarrierAction.PASS_RAW_ADDRESS,
                storage_mode=StorageMode.STACK,
                copy_reason=RAW_STRING_ADDRESS_COPY_REASON,
                label="raw-address",
            )
        return (self._diagnostic(plan.owner_path, "invalid-string-python-action", action.value),)

    def _string_value_action_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return action, handoff, and presence diagnostics for one string input."""
        diagnostics = []
        if plan.binding.python_action is not PythonBarrierAction.STRING_VALUE:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-string-python-action", plan.binding.python_action.value)
            )
        if plan.bridge.native_action is not NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-string-native-action", plan.bridge.native_action.value)
            )
        if plan.bridge.handoff_mode is not ArgumentHandoffMode.CHARACTER_BUFFER:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-string-handoff", plan.bridge.handoff_mode.value)
            )
        if plan.bridge.data_action is not BridgeDataAction.COPY_REPRESENTATION:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-string-data-action", plan.bridge.data_action.value)
            )
        if plan.binding.optional_mode not in {OptionalMode.REQUIRED, OptionalMode.NULLABLE_VALUE}:
            diagnostics.append(
                self._diagnostic(
                    plan.owner_path,
                    "invalid-string-optional-mode",
                    plan.binding.optional_mode.value,
                )
            )
        diagnostics.extend(self._string_codegen_diagnostics(plan))
        return tuple(diagnostics)

    def _string_address_diagnostics(
        self,
        plan: ArgumentTransferPlan,
        *,
        native_action: NativeBarrierAction,
        storage_mode: StorageMode,
        copy_reason: str,
        label: str,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate one fixed string storage/raw address plan."""
        diagnostics = list(
            self._string_address_ownership_diagnostics(
                plan,
                storage_mode=storage_mode,
                label=label,
            )
        )
        if plan.bridge.native_action is not native_action:
            diagnostics.append(
                self._diagnostic(
                    plan.owner_path, f"invalid-string-{label}-native-action", plan.bridge.native_action.value
                )
            )
        if plan.bridge.handoff_mode is not ArgumentHandoffMode.OPAQUE_ADDRESS:
            diagnostics.append(
                self._diagnostic(plan.owner_path, f"invalid-string-{label}-handoff", plan.bridge.handoff_mode.value)
            )
        if plan.bridge.data_action is not BridgeDataAction.COPY_REPRESENTATION:
            diagnostics.append(
                self._diagnostic(plan.owner_path, f"invalid-string-{label}-data-action", plan.bridge.data_action.value)
            )
        if plan.bridge.copy_reason != copy_reason:
            diagnostics.append(
                self._diagnostic(plan.owner_path, f"invalid-string-{label}-copy-reason", plan.bridge.copy_reason)
            )
        diagnostics.extend(self._string_address_length_diagnostics(plan, label))
        return tuple(diagnostics)

    def _string_address_ownership_diagnostics(
        self,
        plan: ArgumentTransferPlan,
        *,
        storage_mode: StorageMode,
        label: str,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate completed caller-owned in-place string address facts."""
        expected = (
            ("object-kind", plan.object_kind, ObjectKind.STRING),
            ("owner", plan.ownership_owner, OwnershipOwner.CALLER),
            ("transfer", plan.transfer_mode, TransferMode.IN_PLACE),
            ("destruction", plan.destruction_policy, DestructionPolicy.CALLER),
            ("storage", plan.storage_mode, storage_mode),
            ("boundary-storage", plan.boundary_storage_mode, storage_mode),
        )
        diagnostics = [
            self._diagnostic(plan.owner_path, f"invalid-string-{label}-{name}", actual.value)
            for name, actual, required in expected
            if actual is not required
        ]
        if plan.binding.codegen_action is not CodegenAction.IN_PLACE_ARGUMENT:
            diagnostics.append(
                self._diagnostic(plan.owner_path, f"invalid-string-{label}-action", plan.binding.codegen_action.value)
            )
        if not plan.mutates_native:
            diagnostics.append(self._diagnostic(plan.owner_path, f"string-{label}-without-mutation", False))
        if plan.projects_result:
            diagnostics.append(
                self._diagnostic(plan.owner_path, f"string-{label}-projects-result", plan.result_position)
            )
        if plan.nullable or plan.binding.optional_mode is not OptionalMode.REQUIRED:
            diagnostics.append(
                self._diagnostic(plan.owner_path, f"optional-string-{label}", plan.binding.optional_mode.value)
            )
        return tuple(diagnostics)

    def _string_address_length_diagnostics(
        self,
        plan: ArgumentTransferPlan,
        label: str,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Require one fixed plan length and prohibit a runtime length ABI role."""
        diagnostics = []
        if plan.character_length is None or plan.character_length <= 0:
            diagnostics.append(
                self._diagnostic(plan.owner_path, f"invalid-string-{label}-length", plan.character_length)
            )
        if plan.binding.length_handoff_role is not None:
            diagnostics.append(
                self._diagnostic(
                    plan.owner_path,
                    f"unexpected-string-{label}-length-handoff",
                    plan.binding.length_handoff_role,
                )
            )
        return tuple(diagnostics)

    def _string_codegen_diagnostics(self, plan: ArgumentTransferPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return string action, copy-reason, and replacement diagnostics."""
        diagnostics = []
        action = plan.binding.codegen_action
        if action not in {CodegenAction.CALL_LOCAL_INPUT, CodegenAction.COPY_IN_OUT}:
            diagnostics.append(self._diagnostic(plan.owner_path, "invalid-string-codegen-action", action.value))
        expected_reason = (
            STRING_REPLACEMENT_COPY_REASON if action is CodegenAction.COPY_IN_OUT else STRING_INPUT_COPY_REASON
        )
        if plan.bridge.copy_reason != expected_reason:
            diagnostics.append(self._diagnostic(plan.owner_path, "invalid-string-copy-reason", plan.bridge.copy_reason))
        if action is CodegenAction.COPY_IN_OUT:
            diagnostics.extend(self._string_replacement_diagnostics(plan))
        elif plan.projects_result:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "call-local-string-projects-result", plan.result_position)
            )
        return tuple(diagnostics)

    def _string_replacement_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate completed ownership and projection for one string replacement."""
        expected = (
            ("object-kind", plan.object_kind, ObjectKind.STRING),
            ("owner", plan.ownership_owner, OwnershipOwner.PYTHON),
            ("transfer", plan.transfer_mode, TransferMode.COPY_RETURN),
            ("destruction", plan.destruction_policy, DestructionPolicy.PYTHON_REFCOUNT),
            ("storage", plan.storage_mode, StorageMode.STACK),
            ("boundary-storage", plan.boundary_storage_mode, StorageMode.STACK),
        )
        diagnostics = [
            self._diagnostic(plan.owner_path, f"invalid-string-replacement-{name}", actual.value)
            for name, actual, required in expected
            if actual is not required
        ]
        if not plan.mutates_native:
            diagnostics.append(self._diagnostic(plan.owner_path, "string-replacement-without-mutation", False))
        if not plan.projects_result or plan.result_position is None:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "string-replacement-without-result", plan.result_position)
            )
        if plan.nullable and plan.binding.optional_mode is OptionalMode.REQUIRED:
            diagnostics.append(self._diagnostic(plan.owner_path, "nullable-string-replacement", True))
        return tuple(diagnostics)

    def _string_length_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return payload-length handoff and fixed-length diagnostics."""
        diagnostics = []
        length_role = plan.binding.length_handoff_role
        if length_role is None:
            diagnostics.append(self._diagnostic(plan.owner_path, "missing-string-length-handoff", None))
        if plan.native_call_slot.character_length is not None and plan.native_call_slot.character_length <= 0:
            diagnostics.append(
                self._diagnostic(
                    plan.owner_path,
                    "invalid-string-character-length",
                    plan.native_call_slot.character_length,
                )
            )
        if plan.character_length is not None and plan.character_length <= 0:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-argument-character-length", plan.character_length)
            )
        return tuple(diagnostics)

    def _optional_argument_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return presence-mode and descriptor handoff diagnostics."""
        return (
            *self._optional_presence_diagnostics(plan),
            *self._optional_native_diagnostics(plan),
            *self._descriptor_output_role_diagnostics(plan),
        )

    def _descriptor_output_role_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Require copy-out roles exactly for projected required descriptors."""
        roles = (plan.bridge.descriptor_output_role, plan.bridge.descriptor_output_presence_role)
        expected = plan.binding.optional_mode is OptionalMode.REQUIRED_DESCRIPTOR and plan.projects_result
        if expected and any(role is None for role in roles):
            return (self._diagnostic(plan.owner_path, "missing-required-descriptor-output-role", roles),)
        if not expected and any(role is not None for role in roles):
            return (self._diagnostic(plan.owner_path, "unexpected-descriptor-output-role", roles),)
        return ()

    def _optional_presence_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return cross-view presence and descriptor diagnostics."""
        diagnostics = []
        mode = plan.binding.optional_mode
        if plan.bridge.optional_mode is not mode:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-optional-mode", mode.value))
        if plan.native_array_handle is not None:
            if not plan.binding.descriptor_boundary:
                diagnostics.append(self._diagnostic(plan.owner_path, "missing-native-descriptor-boundary", mode.value))
            expected_presence = plan.native_array_handle.handoff.presence_role
            if plan.bridge.presence_role != expected_presence:
                diagnostics.append(
                    self._diagnostic(plan.owner_path, "inconsistent-native-descriptor-presence-role", expected_presence)
                )
            return tuple(diagnostics)
        descriptor_mode = mode in {OptionalMode.REQUIRED_DESCRIPTOR, OptionalMode.DESCRIPTOR}
        if plan.binding.descriptor_boundary != descriptor_mode:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-descriptor-boundary", mode.value))
        if mode is OptionalMode.DESCRIPTOR and plan.bridge.presence_role is None:
            diagnostics.append(self._diagnostic(plan.owner_path, "missing-descriptor-presence-role", mode.value))
        if mode is not OptionalMode.DESCRIPTOR and plan.bridge.presence_role is not None:
            diagnostics.append(self._diagnostic(plan.owner_path, "unexpected-descriptor-presence-role", mode.value))
        return tuple(diagnostics)

    def _optional_native_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return optional native-action and descriptor-kind diagnostics."""
        diagnostics = []
        mode = plan.binding.optional_mode
        descriptor_mode = mode in {OptionalMode.REQUIRED_DESCRIPTOR, OptionalMode.DESCRIPTOR}
        if mode is not OptionalMode.REQUIRED and plan.bridge.native_action not in {
            NativeBarrierAction.PASS_VALUE,
            NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS,
            NativeBarrierAction.PASS_STORAGE_ADDRESS,
            NativeBarrierAction.PASS_ARRAY_BUFFER,
            NativeBarrierAction.PASS_NATIVE_DESCRIPTOR,
        }:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-optional-native-action", plan.bridge.native_action.value)
            )
        if descriptor_mode and plan.native_call_slot.value_kind not in {"allocatable", "pointer"}:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-descriptor-value-kind", plan.native_call_slot.value_kind)
            )
        return tuple(diagnostics)

    def _result_diagnostics(
        self,
        plan: ResultPlan,
        function_slots: dict[int, NativeCallSlotPlan],
        available_roles: tuple[str, ...],
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return direct or hidden result producer/consumer diagnostics."""
        diagnostics = list(self._result_role_diagnostics(plan, available_roles))
        diagnostics.extend(
            self._bridge_data_diagnostics(
                plan.owner_path,
                plan.bridge.data_action,
                plan.bridge.copy_reason,
            )
        )
        if plan.bridge.codegen_action is not plan.binding.codegen_action:
            diagnostics.append(
                self._diagnostic(
                    plan.owner_path,
                    "inconsistent-result-codegen-action",
                    plan.bridge.codegen_action,
                )
            )
        if plan.source_kind == "direct_return":
            diagnostics.extend(self._direct_result_diagnostics(plan))
        elif plan.source_kind == "hidden_output":
            diagnostics.extend(self._hidden_result_diagnostics(plan, function_slots))
        else:
            diagnostics.append(self._diagnostic(plan.owner_path, "unknown-result-source", plan.source_kind))
        diagnostics.extend(self._result_family_diagnostics(plan))
        return tuple(diagnostics)

    def _result_family_diagnostics(self, plan: ResultPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Dispatch one result from its completed object-kind decision."""
        if plan.scalar_descriptor is not None:
            return self._scalar_descriptor_result_diagnostics(plan)
        match plan.object_kind:
            case ObjectKind.SCALAR:
                diagnostics = list(self._nonstring_result_length_diagnostics(plan))
                if plan.array is not None:
                    diagnostics.append(self._diagnostic(plan.owner_path, "unexpected-scalar-result-array", None))
                if plan.datatype_family is DatatypeFamily.STRING:
                    diagnostics.append(
                        self._diagnostic(
                            plan.owner_path,
                            "invalid-scalar-result-datatype-family",
                            plan.datatype_family.value,
                        )
                    )
                return tuple(diagnostics)
            case ObjectKind.STRING:
                if plan.array is not None:
                    return (self._diagnostic(plan.owner_path, "unexpected-string-result-array", None),)
                return self._string_result_diagnostics(plan)
            case ObjectKind.NUMPY_ARRAY:
                return self._array_result_diagnostics(plan)
            case _:
                return (
                    self._diagnostic(
                        plan.owner_path,
                        "unsupported-result-object-kind",
                        plan.object_kind.value,
                    ),
                )

    # Rank-zero scalar/string descriptor result validation.
    def _scalar_descriptor_result_diagnostics(self, plan: ResultPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate one nullable rank-zero descriptor copy contract."""
        descriptor = plan.scalar_descriptor
        if descriptor is None:
            return ()
        return (
            *self._scalar_descriptor_family_diagnostics(plan),
            *self._scalar_descriptor_ownership_diagnostics(plan),
            *self._scalar_descriptor_copy_diagnostics(plan),
            *self._scalar_descriptor_source_diagnostics(plan),
        )

    def _scalar_descriptor_family_diagnostics(
        self,
        plan: ResultPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate scalar/string family and runtime-length selection."""
        descriptor = plan.scalar_descriptor
        if descriptor is None:
            return ()
        diagnostics = []
        if plan.object_kind not in {ObjectKind.SCALAR, ObjectKind.STRING}:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-scalar-descriptor-object-kind", plan.object_kind)
            )
        if plan.array is not None or plan.native_array_handle is not None:
            diagnostics.append(self._diagnostic(plan.owner_path, "scalar-descriptor-has-array-policy", None))
        if descriptor.runtime_length != (plan.object_kind is ObjectKind.STRING):
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-scalar-descriptor-runtime-length", descriptor.runtime_length)
            )
        if descriptor.runtime_length and plan.character_length is not None:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "fixed-length-scalar-descriptor-result", plan.character_length)
            )
        return tuple(diagnostics)

    def _scalar_descriptor_ownership_diagnostics(
        self,
        plan: ResultPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate nullability, Python release, and presence role."""
        descriptor = plan.scalar_descriptor
        if descriptor is None:
            return ()
        diagnostics = []
        if not descriptor.nullable or not plan.nullable:
            diagnostics.append(self._diagnostic(plan.owner_path, "nonnullable-scalar-descriptor-result", None))
        if descriptor.release_owner is not OwnershipOwner.PYTHON:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-scalar-descriptor-release-owner", descriptor.release_owner)
            )
        if descriptor.presence_role != f"{plan.owner_path}:present":
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-scalar-descriptor-presence-role", descriptor.presence_role)
            )
        return tuple(diagnostics)

    def _scalar_descriptor_copy_diagnostics(
        self,
        plan: ResultPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate the one explicit representation-copy reason and action."""
        descriptor = plan.scalar_descriptor
        if descriptor is None:
            return ()
        diagnostics = []
        if descriptor.copy_reason != SCALAR_DESCRIPTOR_RESULT_COPY_REASON:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-scalar-descriptor-copy-reason", descriptor.copy_reason)
            )
        if plan.bridge.data_action is not BridgeDataAction.COPY_REPRESENTATION:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-scalar-descriptor-data-action", plan.bridge.data_action)
            )
        if plan.bridge.copy_reason != descriptor.copy_reason:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-scalar-descriptor-copy-reason", plan.bridge.copy_reason)
            )
        return tuple(diagnostics)

    def _scalar_descriptor_source_diagnostics(
        self,
        plan: ResultPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate exact hidden-slot sharing or direct-result independence."""
        descriptor = plan.scalar_descriptor
        if descriptor is None:
            return ()
        if plan.source_kind == "hidden_output":
            if plan.native_call_slot is None or plan.native_call_slot.scalar_descriptor is not descriptor:
                return (self._diagnostic(plan.owner_path, "inconsistent-scalar-descriptor-native-slot", None),)
        elif plan.native_call_slot is not None:
            return (self._diagnostic(plan.owner_path, "direct-scalar-descriptor-has-slot", None),)
        return ()

    # Fixed-string result validation.
    def _string_result_aggregation_diagnostics(
        self,
        plan: FunctionPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Keep fixed string allocation cleanup single-result in Phase 5B."""
        if any(result.object_kind is ObjectKind.STRING for result in plan.results) and len(plan.results) != 1:
            return (self._diagnostic(plan.owner_path, "mixed-string-result-aggregation", len(plan.results)),)
        return ()

    def _string_result_diagnostics(self, plan: ResultPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate the fixed string result contract before either backend."""
        if plan.datatype_family is not DatatypeFamily.STRING:
            return (
                self._diagnostic(
                    plan.owner_path,
                    "invalid-string-result-datatype-family",
                    plan.datatype_family.value,
                ),
            )
        diagnostics = []
        if plan.character_length is None or plan.character_length <= 0:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-result-character-length", plan.character_length)
            )
        diagnostics.extend(self._string_result_ownership_diagnostics(plan))
        if plan.binding.python_action is not PythonBarrierAction.NONE:
            diagnostics.append(
                self._diagnostic(
                    plan.owner_path, "invalid-string-result-python-action", plan.binding.python_action.value
                )
            )
        if plan.bridge.data_action is not BridgeDataAction.COPY_REPRESENTATION:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-string-result-data-action", plan.bridge.data_action.value)
            )
        if plan.bridge.copy_reason != FIXED_STRING_RESULT_COPY_REASON:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-string-result-copy-reason", plan.bridge.copy_reason)
            )
        if plan.source_kind == "direct_return":
            diagnostics.extend(self._direct_string_result_diagnostics(plan))
        elif plan.source_kind == "hidden_output":
            diagnostics.extend(self._hidden_string_result_diagnostics(plan))
        return tuple(diagnostics)

    def _string_result_ownership_diagnostics(self, plan: ResultPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate completed fixed-string ownership projected into the plan."""
        expected = (
            ("object-kind", plan.object_kind, ObjectKind.STRING),
            ("owner", plan.ownership_owner, OwnershipOwner.PYTHON),
            ("transfer", plan.transfer_mode, TransferMode.COPY_RETURN),
            ("destruction", plan.destruction_policy, DestructionPolicy.PYTHON_REFCOUNT),
            ("storage", plan.storage_mode, StorageMode.STACK),
            ("boundary-storage", plan.boundary_storage_mode, StorageMode.STACK),
        )
        diagnostics = [
            self._diagnostic(plan.owner_path, f"invalid-string-result-{name}", actual.value)
            for name, actual, required in expected
            if actual is not required
        ]
        if plan.nullable and plan.source_kind != "hidden_output":
            diagnostics.append(self._diagnostic(plan.owner_path, "nullable-fixed-string-result", plan.nullable))
        return tuple(diagnostics)

    def _nonstring_result_length_diagnostics(self, plan: ResultPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        if plan.character_length is None:
            return ()
        return (
            self._diagnostic(
                plan.owner_path,
                "nonstring-result-character-length",
                plan.character_length,
            ),
        )

    def _direct_string_result_diagnostics(self, plan: ResultPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        diagnostics = []
        if plan.binding.codegen_action is not CodegenAction.COPY_OUT:
            diagnostics.append(
                self._diagnostic(
                    plan.owner_path,
                    "invalid-direct-string-result-action",
                    plan.binding.codegen_action.value,
                )
            )
        if plan.bridge.native_action is not NativeBarrierAction.NONE:
            diagnostics.append(
                self._diagnostic(
                    plan.owner_path,
                    "invalid-direct-string-native-action",
                    plan.bridge.native_action.value,
                )
            )
        return tuple(diagnostics)

    def _hidden_string_result_diagnostics(self, plan: ResultPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        diagnostics = []
        if plan.binding.codegen_action is not CodegenAction.COPY_OUT:
            diagnostics.append(
                self._diagnostic(
                    plan.owner_path,
                    "invalid-hidden-string-result-action",
                    plan.binding.codegen_action.value,
                )
            )
        if plan.bridge.native_action is not NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS:
            diagnostics.append(
                self._diagnostic(
                    plan.owner_path,
                    "invalid-hidden-string-native-action",
                    plan.bridge.native_action.value,
                )
            )
        return tuple(diagnostics)

    def _result_role_diagnostics(
        self,
        plan: ResultPlan,
        available_roles: tuple[str, ...],
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        if plan.bridge.native_result_role not in available_roles:
            return (self._diagnostic(plan.owner_path, "unavailable-result-role", plan.bridge.native_result_role),)
        return ()

    def _direct_result_diagnostics(self, plan: ResultPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        diagnostics = []
        if plan.native_call_slot is not None or plan.bridge.abi_position is not None:
            diagnostics.append(self._diagnostic(plan.owner_path, "direct-result-has-native-slot", plan.source_kind))
        expected_data_action = (
            BridgeDataAction.COPY_REPRESENTATION
            if plan.object_kind in {ObjectKind.STRING, ObjectKind.NUMPY_ARRAY} or plan.scalar_descriptor is not None
            else BridgeDataAction.DIRECT_TRANSFER
        )
        if plan.bridge.data_action is not expected_data_action:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-direct-result-data-action", plan.bridge.data_action.value)
            )
        return tuple(diagnostics)

    def _hidden_result_diagnostics(
        self,
        plan: ResultPlan,
        function_slots: dict[int, NativeCallSlotPlan],
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        if plan.native_call_slot is None or plan.bridge.abi_position is None:
            return (self._diagnostic(plan.owner_path, "missing-result-native-slot", plan.bridge.native_name),)
        slot = plan.native_call_slot
        diagnostics = [
            *self._hidden_result_shape_diagnostics(plan, slot),
            *self._hidden_result_policy_consistency_diagnostics(plan, slot),
        ]
        if function_slots.get(slot.native_position) is not slot:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-function-result-slot", slot.native_position)
            )
        return tuple(diagnostics)

    def _hidden_result_shape_diagnostics(
        self,
        plan: ResultPlan,
        slot: NativeCallSlotPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return hidden-result native-slot shape diagnostics."""
        diagnostics = []
        if slot.source_kind != "result":
            diagnostics.append(self._diagnostic(plan.owner_path, "invalid-result-native-slot", slot.source_kind))
        if slot.native_position != plan.bridge.abi_position:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-result-native-position", slot.native_position)
            )
        if slot.result_position != plan.result_position:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-result-position", slot.result_position))
        if slot.symbolic_role != plan.bridge.native_result_role:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-result-role", slot.symbolic_role))
        return tuple(diagnostics)

    def _hidden_result_policy_consistency_diagnostics(
        self,
        plan: ResultPlan,
        slot: NativeCallSlotPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return hidden-result completed-action consistency diagnostics."""
        diagnostics = []
        if slot.native_action is not plan.bridge.native_action:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-result-native-action", slot.native_action.value)
            )
        if slot.codegen_action is not plan.bridge.codegen_action:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-result-slot-codegen-action", slot.codegen_action.value)
            )
        if slot.bridge_data_action is not plan.bridge.data_action:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-result-data-action", slot.bridge_data_action.value)
            )
        if slot.bridge_copy_reason != plan.bridge.copy_reason:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-result-copy-reason", slot.bridge_copy_reason)
            )
        if slot.character_length != plan.character_length:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-result-character-length", slot.character_length)
            )
        if slot.array is not plan.array:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-result-array-handoff", slot.array))
        if slot.native_array_handle is not plan.native_array_handle:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-result-native-array-handle", slot.native_array_handle)
            )
        if slot.scalar_descriptor is not plan.scalar_descriptor:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-result-scalar-descriptor", slot.scalar_descriptor)
            )
        if slot.object_kind is not plan.object_kind:
            diagnostics.append(
                self._diagnostic(
                    plan.owner_path,
                    "inconsistent-result-object-kind",
                    slot.object_kind,
                )
            )
        return tuple(diagnostics)

    # Ordinary-array result validation.
    def _array_result_diagnostics(self, plan: ResultPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate one fixed-shape ordinary array producer and copy consumer."""
        if plan.native_array_handle is not None:
            return self._native_array_handle_result_diagnostics(plan)
        array = plan.array
        if array is None:
            return (self._diagnostic(plan.owner_path, "missing-array-result-handoff", None),)
        diagnostics = [
            *self._array_result_ownership_diagnostics(plan),
            *self._array_result_shape_diagnostics(plan),
            *self._array_result_itemsize_diagnostics(plan),
            *self._array_result_copy_diagnostics(plan),
        ]
        if plan.nullable:
            diagnostics.append(self._diagnostic(plan.owner_path, "nullable-ordinary-array-result", plan.nullable))
        diagnostics.extend(self._array_result_source_diagnostics(plan))
        return tuple(diagnostics)

    # Native-array-handle result validation.
    def _native_array_handle_result_diagnostics(self, plan: ResultPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate one wrapper-owned allocatable descriptor result."""
        handle = plan.native_array_handle
        if handle is None:
            return ()
        return (
            *self._native_array_handle_shape_diagnostics(plan.owner_path, handle),
            *self._native_descriptor_handoff_diagnostics(plan.owner_path, handle, None),
            *self._native_array_result_ownership_diagnostics(plan),
            *self._native_array_result_handle_diagnostics(plan),
            *self._native_array_result_copy_diagnostics(plan),
        )

    def _native_array_result_ownership_diagnostics(
        self,
        plan: ResultPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate wrapper ownership, storage, and public result actions."""
        expected = (
            ("owner", plan.ownership_owner, OwnershipOwner.WRAPPER),
            ("transfer", plan.transfer_mode, TransferMode.WRAPPER_INSTANCE),
            ("destruction", plan.destruction_policy, DestructionPolicy.WRAPPER_DEALLOC),
            ("storage", plan.storage_mode, StorageMode.HEAP),
            ("boundary-storage", plan.boundary_storage_mode, StorageMode.ALIAS),
            ("codegen-action", plan.binding.codegen_action, CodegenAction.WRAPPER_INSTANCE),
            ("python-action", plan.binding.python_action, PythonBarrierAction.NONE),
        )
        return tuple(
            self._diagnostic(plan.owner_path, f"invalid-native-array-result-{name}", actual.value)
            for name, actual, required in expected
            if actual is not required
        )

    def _native_array_result_handle_diagnostics(
        self,
        plan: ResultPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate owned allocatable handle identity and release policy."""
        handle = plan.native_array_handle
        if handle is None:
            return ()
        diagnostics = []
        if handle.handle_kind is not NativeArrayHandleKind.OWNED_RESULT_DESCRIPTOR:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-native-array-result-kind", handle.handle_kind)
            )
        if handle.descriptor_kind is not NativeArrayDescriptorKind.ALLOCATABLE:
            diagnostics.append(self._diagnostic(plan.owner_path, "unsupported-pointer-array-result", None))
        if handle.descriptor_ownership is not NativeArrayDescriptorOwnership.OWNED or handle.borrowed:
            diagnostics.append(self._diagnostic(plan.owner_path, "invalid-native-array-result-ownership", None))
        if handle.release is not NativeArrayRelease.WRAPPER_DEALLOC:
            diagnostics.append(self._diagnostic(plan.owner_path, "missing-native-array-result-release", None))
        if plan.array is not handle.array:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-native-array-result-facet", plan.array))
        return tuple(diagnostics)

    def _native_array_result_copy_diagnostics(
        self,
        plan: ResultPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate the ownership-transfer representation copy action."""
        diagnostics = []
        if plan.bridge.data_action is not BridgeDataAction.COPY_REPRESENTATION:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-native-array-result-data-action", plan.bridge.data_action)
            )
        if plan.bridge.copy_reason != OWNED_NATIVE_ARRAY_HANDLE_COPY_REASON:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-native-array-result-copy-reason", plan.bridge.copy_reason)
            )
        return tuple(diagnostics)

    def _array_result_ownership_diagnostics(self, plan: ResultPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate ordinary array result ownership and storage decisions."""
        expected = (
            ("object-kind", plan.object_kind, ObjectKind.NUMPY_ARRAY),
            ("owner", plan.ownership_owner, OwnershipOwner.PYTHON),
            ("transfer", plan.transfer_mode, TransferMode.COPY_RETURN),
            ("destruction", plan.destruction_policy, DestructionPolicy.PYTHON_REFCOUNT),
            ("storage", plan.storage_mode, StorageMode.STACK),
            ("boundary-storage", plan.boundary_storage_mode, StorageMode.STACK),
        )
        return tuple(
            self._diagnostic(plan.owner_path, f"invalid-array-result-{name}", actual.value)
            for name, actual, required in expected
            if actual is not required
        )

    def _array_result_itemsize_diagnostics(self, plan: ResultPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate fixed-width character itemsize only inside the array family."""
        array = plan.array
        if array is None:
            return ()
        if plan.datatype_family is DatatypeFamily.STRING:
            if (
                array.itemsize is None
                or array.itemsize <= 0
                or array.itemsize_role is None
                or plan.character_length != array.itemsize
            ):
                return (self._diagnostic(plan.owner_path, "invalid-array-result-itemsize", array.itemsize),)
            return ()
        if array.itemsize is not None or array.itemsize_role is not None or plan.character_length is not None:
            return (self._diagnostic(plan.owner_path, "unexpected-array-result-itemsize", array.itemsize),)
        return ()

    def _array_result_shape_diagnostics(self, plan: ResultPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate a fully resolved fixed-rank ordinary array result shape."""
        return (
            *self._array_result_rank_diagnostics(plan),
            *self._array_result_shape_count_diagnostics(plan),
            *self._array_result_extent_diagnostics(plan),
            *self._array_result_order_diagnostics(plan),
        )

    def _array_result_rank_diagnostics(self, plan: ResultPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Require a supported concrete ordinary array result rank."""
        array = plan.array
        if array is not None and (array.rank is None or not 1 <= array.rank <= 15):
            return (self._diagnostic(plan.owner_path, "invalid-array-result-rank", array.rank),)
        return ()

    def _array_result_shape_count_diagnostics(self, plan: ResultPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Require one shape and extent role per result axis."""
        array = plan.array
        if (
            array is not None
            and array.rank is not None
            and (len(array.shape) != array.rank or len(array.extent_roles) != array.rank)
        ):
            return (self._diagnostic(plan.owner_path, "inconsistent-array-result-shape", array.shape),)
        return ()

    def _array_result_extent_diagnostics(self, plan: ResultPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Reject unresolved ordinary array result extent spellings."""
        array = plan.array
        if array is not None and any(shape in {":", "::Strided", "...", "Flat"} for shape in array.shape):
            return (self._diagnostic(plan.owner_path, "unresolved-array-result-shape", array.shape),)
        return ()

    def _array_result_order_diagnostics(self, plan: ResultPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Reject multidimensional C-oriented native result copies."""
        array = plan.array
        if array is not None and array.order == "ORDER_C" and array.rank is not None and array.rank > 1:
            return (self._diagnostic(plan.owner_path, "invalid-array-result-order", array.order),)
        return ()

    def _array_result_copy_diagnostics(self, plan: ResultPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate the explicit ordinary array representation-copy decision."""
        diagnostics = []
        if plan.bridge.data_action is not BridgeDataAction.COPY_REPRESENTATION:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-array-result-data-action", plan.bridge.data_action.value)
            )
        if plan.bridge.copy_reason != ORDINARY_ARRAY_RESULT_COPY_REASON:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-array-result-copy-reason", plan.bridge.copy_reason)
            )
        return tuple(diagnostics)

    def _array_result_source_diagnostics(self, plan: ResultPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate direct versus hidden ordinary array producer actions."""
        if plan.source_kind == "direct_return":
            expected_action = CodegenAction.COPY_OUT
            expected_native = NativeBarrierAction.NONE
        else:
            expected_action = CodegenAction.COPY_OUT
            expected_native = NativeBarrierAction.PASS_ARRAY_BUFFER
        diagnostics = []
        if plan.binding.codegen_action is not expected_action:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-array-result-action", plan.binding.codegen_action.value)
            )
        if plan.bridge.native_action is not expected_native:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-array-result-native-action", plan.bridge.native_action.value)
            )
        return tuple(diagnostics)

    def _native_slot_diagnostics(self, plan: NativeCallSlotPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return hidden literal and hidden result slot diagnostics."""
        diagnostics = list(
            self._bridge_data_diagnostics(
                plan.owner_path,
                plan.bridge_data_action,
                plan.bridge_copy_reason,
            )
        )
        if plan.source_kind not in {"implicit", "projection", "literal", "result"}:
            diagnostics.append(self._diagnostic(plan.owner_path, "unknown-native-slot-source", plan.source_kind))
        if plan.source_kind == "literal":
            diagnostics.extend(self._literal_slot_diagnostics(plan))
        elif plan.object_kind is None:
            diagnostics.append(self._diagnostic(plan.owner_path, "missing-native-slot-object-kind", None))
        if plan.source_kind == "result":
            diagnostics.extend(self._result_slot_diagnostics(plan))
        return tuple(diagnostics)

    def _bridge_data_diagnostics(
        self,
        owner_path: str,
        action: BridgeDataAction,
        copy_reason: str | None,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Reject uncompleted or unjustified bridge-side data movement."""
        if action is BridgeDataAction.BLOCKED:
            return (self._diagnostic(owner_path, "blocked-bridge-data-action", action.value),)
        if action is BridgeDataAction.COPY_REPRESENTATION:
            if not copy_reason or not copy_reason.strip():
                return (self._diagnostic(owner_path, "missing-bridge-copy-reason", action.value),)
            return ()
        if copy_reason is not None:
            return (self._diagnostic(owner_path, "unexpected-bridge-copy-reason", action.value),)
        return ()

    def _literal_slot_diagnostics(self, plan: NativeCallSlotPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return diagnostics for one hidden literal slot."""
        diagnostics = []
        if plan.literal_type is None:
            diagnostics.append(self._diagnostic(plan.owner_path, "missing-literal-type", plan.native_position))
        if plan.literal_value is None:
            diagnostics.append(self._diagnostic(plan.owner_path, "missing-literal-value", plan.native_position))
        if plan.python_position is not None:
            diagnostics.append(self._diagnostic(plan.owner_path, "literal-python-position", plan.python_position))
        if plan.object_kind is not None:
            diagnostics.append(self._diagnostic(plan.owner_path, "literal-object-kind", plan.object_kind.value))
        if plan.bridge_data_action is not BridgeDataAction.DIRECT_TRANSFER:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-literal-data-action", plan.bridge_data_action.value)
            )
        return tuple(diagnostics)

    def _result_slot_diagnostics(self, plan: NativeCallSlotPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return diagnostics for one native result slot."""
        return (
            *self._result_slot_identity_diagnostics(plan),
            *self._result_slot_string_diagnostics(plan),
            *self._result_slot_data_action_diagnostics(plan),
        )

    def _result_slot_identity_diagnostics(
        self,
        plan: NativeCallSlotPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate result/native positions and datatype identity."""
        diagnostics = []
        if plan.result_position is None:
            diagnostics.append(self._diagnostic(plan.owner_path, "missing-result-position", plan.native_position))
        if plan.python_position is not None:
            diagnostics.append(self._diagnostic(plan.owner_path, "result-python-position", plan.python_position))
        if plan.semantic_type_name is None or plan.datatype_family is None:
            diagnostics.append(self._diagnostic(plan.owner_path, "missing-result-datatype", plan.native_position))
        return tuple(diagnostics)

    def _result_slot_string_diagnostics(
        self,
        plan: NativeCallSlotPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Require fixed string length unless runtime descriptor length is planned."""
        if plan.object_kind is ObjectKind.STRING and plan.character_length is None and plan.scalar_descriptor is None:
            return (self._diagnostic(plan.owner_path, "missing-result-character-length", plan.native_position),)
        return ()

    def _result_slot_data_action_diagnostics(
        self,
        plan: NativeCallSlotPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate direct versus representation-copy native output action."""
        expected = (
            BridgeDataAction.COPY_REPRESENTATION
            if plan.object_kind in {ObjectKind.STRING, ObjectKind.NUMPY_ARRAY} or plan.scalar_descriptor is not None
            else BridgeDataAction.DIRECT_TRANSFER
        )
        if plan.bridge_data_action is not expected:
            return (
                self._diagnostic(
                    plan.owner_path,
                    "invalid-result-data-action",
                    f"{plan.bridge_data_action.value}:{expected.value}",
                ),
            )
        return ()

    def _lifecycle_diagnostics(
        self,
        plan: LifecycleActionPlan,
        available_roles: tuple[str, ...],
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return lifecycle source-role and backend-owner diagnostics."""
        phase_name = plan.phase.value if isinstance(plan.phase, WritebackPhase) else str(plan.phase)
        diagnostics = [*self._lifecycle_role_diagnostics(plan, available_roles, phase_name)]
        diagnostics.extend(self._lifecycle_owner_diagnostics(plan, phase_name))
        if plan.binding is not None:
            diagnostics.extend(self._binding_lifecycle_diagnostics(plan, phase_name))
        if plan.bridge is not None and plan.bridge.source_role != plan.source_role:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-lifecycle-role", phase_name))
        return tuple(diagnostics)

    def _lifecycle_role_diagnostics(
        self,
        plan: LifecycleActionPlan,
        available_roles: tuple[str, ...],
        phase_name: str,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return lifecycle phase and source-handoff diagnostics."""
        diagnostics = []
        if plan.source_role not in available_roles:
            diagnostics.append(self._diagnostic(plan.owner_path, f"unavailable-{phase_name}-role", plan.source_role))
        if not isinstance(plan.phase, WritebackPhase):
            diagnostics.append(self._diagnostic(plan.owner_path, "unknown-writeback-phase", phase_name))
        return tuple(diagnostics)

    def _lifecycle_owner_diagnostics(
        self,
        plan: LifecycleActionPlan,
        phase_name: str,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return binding-versus-bridge lifecycle ownership diagnostics."""
        diagnostics = []
        if (plan.binding is None) == (plan.bridge is None):
            diagnostics.append(self._diagnostic(plan.owner_path, "lifecycle-backend-owner", phase_name))
        expected_bridge_owner = plan.phase is WritebackPhase.NATIVE_MUTATION
        if expected_bridge_owner != (plan.bridge is not None):
            diagnostics.append(self._diagnostic(plan.owner_path, "invalid-writeback-phase-owner", phase_name))
        return tuple(diagnostics)

    def _binding_lifecycle_diagnostics(
        self,
        plan: LifecycleActionPlan,
        phase_name: str,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return binding-owned writeback action and target diagnostics."""
        diagnostics = []
        binding = plan.binding
        if binding.source_role != plan.source_role:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-lifecycle-role", phase_name))
        diagnostics.extend(self._binding_lifecycle_fact_diagnostics(plan, phase_name))
        if binding.codegen_action not in {CodegenAction.COPY_IN_OUT, CodegenAction.IN_PLACE_ARGUMENT}:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-writeback-action", binding.codegen_action.value)
            )
        if plan.phase is WritebackPhase.COPY_OUT and not binding.python_result_role:
            diagnostics.append(self._diagnostic(plan.owner_path, "missing-python-writeback-target", phase_name))
        if plan.phase is not WritebackPhase.COPY_OUT and binding.python_result_role is not None:
            diagnostics.append(self._diagnostic(plan.owner_path, "unexpected-python-writeback-target", phase_name))
        return tuple(diagnostics)

    def _binding_lifecycle_fact_diagnostics(
        self,
        plan: LifecycleActionPlan,
        phase_name: str,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return shared-versus-binding lifecycle fact drift."""
        diagnostics = []
        binding = plan.binding
        if binding.codegen_action is not plan.codegen_action:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-lifecycle-action", phase_name))
        if binding.semantic_type_name != plan.semantic_type_name:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-lifecycle-type", phase_name))
        if binding.datatype_family is not plan.datatype_family:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-lifecycle-family", phase_name))
        if binding.result_position != plan.result_position:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-lifecycle-position", phase_name))
        return tuple(diagnostics)

    # String lifecycle validation.
    def _string_writeback_diagnostics(self, plan: FunctionPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate the complete string replacement lifecycle and exclusions."""
        replacements = tuple(
            argument
            for argument in plan.arguments
            if argument.object_kind is ObjectKind.STRING
            and argument.binding.codegen_action is CodegenAction.COPY_IN_OUT
        )
        diagnostics = []
        if replacements and plan.binding.status_error is not None:
            diagnostics.append(self._diagnostic(plan.owner_path, "string-writeback-with-status-error", plan.owner_path))
        for argument in replacements:
            diagnostics.extend(self._one_string_writeback_diagnostics(plan, argument))
        return tuple(diagnostics)

    def _one_string_writeback_diagnostics(
        self,
        plan: FunctionPlan,
        argument: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return lifecycle coverage and fact drift for one replacement."""
        actions = tuple(
            action for action in plan.writeback_actions if action.source_role == argument.binding.handoff_role
        )
        diagnostics = []
        if {action.phase for action in actions} != set(WritebackPhase):
            diagnostics.append(
                self._diagnostic(plan.owner_path, "incomplete-string-writeback-lifecycle", argument.owner_path)
            )
        for action in actions:
            diagnostics.extend(self._one_string_writeback_action_diagnostics(plan, argument, action))
        return tuple(diagnostics)

    def _one_string_writeback_action_diagnostics(
        self,
        plan: FunctionPlan,
        argument: ArgumentTransferPlan,
        action: LifecycleActionPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return one lifecycle action's string replacement consistency."""
        if (
            action.codegen_action is CodegenAction.COPY_IN_OUT
            and action.object_kind is ObjectKind.STRING
            and action.semantic_type_name == "String"
            and action.datatype_family is DatatypeFamily.STRING
            and action.result_position == argument.result_position
        ):
            return ()
        return (self._diagnostic(plan.owner_path, "inconsistent-string-writeback-lifecycle", action.phase.value),)

    def _writeback_phase_diagnostics(self, plan: FunctionPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Require one complete ordered phase set for every writeback handoff."""
        diagnostics = []
        grouped: dict[str, list[LifecycleActionPlan]] = {}
        for action in plan.writeback_actions:
            grouped.setdefault(action.source_role, []).append(action)
        for source_role, actions in grouped.items():
            expected = (
                {WritebackPhase.COPY_OUT}
                if all(action.object_kind is ObjectKind.NUMPY_ARRAY for action in actions)
                else set(WritebackPhase)
            )
            phases = [action.phase for action in actions]
            counts = Counter(phases)
            for phase, occurrences in counts.items():
                if occurrences > 1:
                    diagnostics.append(self._diagnostic(plan.owner_path, "duplicate-writeback-phase", phase))
            for phase in sorted(expected - set(phases), key=lambda item: item.value):
                diagnostics.append(
                    self._diagnostic(plan.owner_path, "missing-writeback-phase", f"{source_role}:{phase.value}")
                )
        return tuple(diagnostics)

    def _function_output_diagnostics(self, plan: FunctionPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return output projection and native callable-kind diagnostics."""
        diagnostics = [*self._mixed_output_diagnostics(plan)]
        diagnostics.extend(self._binding_result_diagnostics(plan))
        diagnostics.extend(self._writeback_result_diagnostics(plan))
        diagnostics.extend(self._native_callable_kind_diagnostics(plan))
        diagnostics.extend(self._unclaimed_result_diagnostics(plan))
        return tuple(diagnostics)

    def _mixed_output_diagnostics(self, plan: FunctionPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Reject simultaneous public result and writeback projections."""
        if plan.results and plan.writeback_actions:
            return (self._diagnostic(plan.owner_path, "mixed-result-and-writeback", plan.owner_path),)
        return ()

    def _binding_result_diagnostics(self, plan: FunctionPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate ordered consumers and the sole direct native result."""
        diagnostics = list(
            self._sequence_diagnostics(
                plan.owner_path,
                "binding-result",
                tuple(result.result_position for result in plan.results),
                len(plan.results),
            )
        )
        direct_results = tuple(result for result in plan.results if result.source_kind == "direct_return")
        if len(direct_results) > 1:
            diagnostics.append(self._diagnostic(plan.owner_path, "multiple-direct-results", len(direct_results)))
        return tuple(diagnostics)

    def _writeback_result_diagnostics(self, plan: FunctionPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate contiguous Python result positions for copy-out actions."""
        result_positions = tuple(
            action.binding.result_position
            for action in plan.writeback_actions
            if action.phase is WritebackPhase.COPY_OUT and action.binding is not None
        )
        return self._sequence_diagnostics(
            plan.owner_path,
            "writeback-result",
            result_positions,
            len(result_positions),
        )

    def _native_callable_kind_diagnostics(self, plan: FunctionPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Require callable kind to agree with the public result representation."""
        requires_subroutine = not any(result.source_kind == "direct_return" for result in plan.results)
        if plan.bridge.native_is_subroutine != requires_subroutine:
            return (self._diagnostic(plan.owner_path, "inconsistent-native-callable-kind", requires_subroutine),)
        return ()

    def _unclaimed_result_diagnostics(self, plan: FunctionPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Require exactly one binding or status consumer per native output."""
        claimed_roles = self._claimed_result_roles(plan)
        diagnostics = []
        for slot in plan.native_call_slots:
            if slot.source_kind != "result":
                continue
            claim_count = claimed_roles[slot.symbolic_role]
            if claim_count == 0:
                diagnostics.append(self._diagnostic(plan.owner_path, "unclaimed-native-result", slot.symbolic_role))
            elif claim_count > 1:
                diagnostics.append(
                    self._diagnostic(plan.owner_path, "multiple-native-result-consumers", slot.symbolic_role)
                )
        return tuple(diagnostics)

    def _claimed_result_roles(self, plan: FunctionPlan) -> Counter[str]:
        """Return public and status-policy consumers of native result slots."""
        roles = Counter(
            result.bridge.native_result_role for result in plan.results if result.source_kind == "hidden_output"
        )
        if plan.binding.status_error is not None:
            roles[plan.binding.status_error.status_role] += 1
            if plan.binding.status_error.message_role is not None:
                roles[plan.binding.status_error.message_role] += 1
        return roles

    def _status_error_diagnostics(self, plan: FunctionPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate completed status/message roles before either backend emits."""
        policy = plan.binding.status_error
        if policy is None:
            return ()
        result_slots = {slot.symbolic_role: slot for slot in plan.native_call_slots if slot.source_kind == "result"}
        diagnostics = [*self._status_role_diagnostics(plan, result_slots)]
        diagnostics.extend(self._message_role_diagnostics(plan, result_slots))
        diagnostics.extend(self._status_policy_diagnostics(plan))
        return tuple(diagnostics)

    def _status_role_diagnostics(
        self,
        plan: FunctionPlan,
        result_slots: dict[str, NativeCallSlotPlan],
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate the completed integer status role."""
        policy = plan.binding.status_error
        status = result_slots.get(policy.status_role)
        if status is None:
            return (self._diagnostic(plan.owner_path, "missing-status-result-role", policy.status_role),)
        if status.object_kind is not ObjectKind.SCALAR or status.datatype_family is not DatatypeFamily.INTEGER:
            return (self._diagnostic(plan.owner_path, "incompatible-status-result-role", policy.status_role),)
        if status.semantic_type_name != "Int32":
            return (self._diagnostic(plan.owner_path, "incompatible-status-result-role", policy.status_role),)
        return ()

    def _message_role_diagnostics(
        self,
        plan: FunctionPlan,
        result_slots: dict[str, NativeCallSlotPlan],
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate the optional fixed-length status message role."""
        policy = plan.binding.status_error
        if policy.message_role is None:
            return ()
        message = result_slots.get(policy.message_role)
        if message is None:
            return (self._diagnostic(plan.owner_path, "missing-message-result-role", policy.message_role),)
        if message.object_kind is not ObjectKind.STRING or message.datatype_family is not DatatypeFamily.STRING:
            return (self._diagnostic(plan.owner_path, "incompatible-message-result-role", policy.message_role),)
        if message.character_length is None:
            return (self._diagnostic(plan.owner_path, "incompatible-message-result-role", policy.message_role),)
        return ()

    def _status_policy_diagnostics(self, plan: FunctionPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Validate cross-role and exception facts for status handling."""
        policy = plan.binding.status_error
        diagnostics = []
        if policy.message_role == policy.status_role:
            diagnostics.append(self._diagnostic(plan.owner_path, "duplicate-status-message-role", policy.status_role))
        if policy.exception_kind is not PythonExceptionKind.RUNTIME_ERROR:
            diagnostics.append(self._diagnostic(plan.owner_path, "unsupported-status-exception", policy.exception_kind))
        return tuple(diagnostics)

    def _sequence_diagnostics(
        self,
        owner_path: str,
        label: str,
        positions: tuple[int, ...],
        count: int,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return contiguous-position coverage diagnostics."""
        diagnostics = []
        counts = Counter(positions)
        for position, occurrences in sorted(counts.items()):
            if occurrences > 1:
                diagnostics.append(self._diagnostic(owner_path, f"duplicate-{label}-position", position))
        expected = set(range(count))
        actual = set(positions)
        for position in sorted(expected - actual):
            diagnostics.append(self._diagnostic(owner_path, f"missing-{label}-position", position))
        for position in sorted(actual - expected):
            code = f"negative-{label}-position" if position < 0 else f"out-of-range-{label}-position"
            diagnostics.append(self._diagnostic(owner_path, code, position))
        return tuple(diagnostics)

    def _duplicate_role_diagnostics(self, plan: FunctionPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return duplicate symbolic producer/consumer role diagnostics."""
        roles = [argument.binding.handoff_role for argument in plan.arguments]
        roles.extend(slot.symbolic_role for slot in plan.native_call_slots if slot.source_kind == "literal")
        roles.extend(slot.symbolic_role for slot in plan.native_call_slots if slot.source_kind == "result")
        roles.extend(
            result.bridge.native_result_role for result in plan.results if result.source_kind == "direct_return"
        )
        return tuple(
            self._diagnostic(plan.owner_path, "duplicate-symbolic-role", role)
            for role, count in Counter(roles).items()
            if count > 1
        )

    def _available_role_diagnostics(self, plan: FunctionPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Require the advertised roles to match argument and result producers."""
        expected = [argument.binding.handoff_role for argument in plan.arguments]
        expected.extend(
            role
            for argument in plan.arguments
            for role in (
                argument.bridge.descriptor_output_role,
                argument.bridge.descriptor_output_presence_role,
            )
            if role is not None
        )
        expected.extend(slot.symbolic_role for slot in plan.native_call_slots if slot.source_kind == "result")
        expected.extend(
            result.bridge.native_result_role for result in plan.results if result.source_kind == "direct_return"
        )
        if Counter(plan.available_roles) != Counter(expected):
            return (self._diagnostic(plan.owner_path, "inconsistent-available-roles", plan.available_roles),)
        return ()

    def _diagnostic(self, owner_path: str, code: str, detail: object) -> WrapperPlanDiagnostic:
        return WrapperPlanDiagnostic(owner_path, code, str(detail))

    def _diagnostic_summary(self, diagnostics: tuple[WrapperPlanDiagnostic, ...]) -> str:
        details = "; ".join(f"{item.owner_path}:{item.code}:{item.message}" for item in diagnostics)
        return f"Invalid edited wrapper plan before generation: {details}"

    def _rendered_artifacts(
        self,
        module_name: str,
        c_source: str,
        c_header: str,
        fortran_source: str,
        runtime_support_keys: tuple[str, ...],
        required_headers: tuple[str, ...],
    ) -> RenderedGeneratedWrapperArtifacts:
        artifacts = GeneratedWrapperArtifacts(
            module_name=module_name,
            bridge_sources=(Path(f"bind_c_{module_name}_wrapper.f90"),),
            binding_sources=(Path(f"{module_name}_wrapper.c"),),
            header_files=(Path(f"{module_name}_wrapper.h"),),
            runtime_support_keys=runtime_support_keys,
            required_headers=required_headers,
        )
        return RenderedGeneratedWrapperArtifacts(
            artifacts=artifacts,
            extension_init_name=f"PyInit_{module_name}",
            sources=(
                GeneratedSourceFile(artifacts.bridge_sources[0], fortran_source),
                GeneratedSourceFile(artifacts.binding_sources[0], c_source),
                GeneratedSourceFile(artifacts.header_files[0], c_header),
            ),
        )
