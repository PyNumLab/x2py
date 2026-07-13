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
    NativeBarrierAction,
    SetterAction,
)
from x2py.semantics.wrapper_policy import (
    ModuleGetterAction,
    OptionalMode,
    WritebackPhase,
)
from x2py.wrapper_codegen.c.binding import CBindingGenerator
from x2py.wrapper_codegen.fortran.bridge import FortranBridgeGenerator
from x2py.wrapper_codegen.plan import (
    ArgumentTransferPlan,
    FunctionPlan,
    LifecycleActionPlan,
    ModulePlan,
    ModuleVariablePlan,
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
        )

    def _validate_plan(self, plan: ModulePlan) -> None:
        """Reject structural inconsistencies in the final frozen plan."""
        diagnostics = self._plan_diagnostics(plan)
        if diagnostics:
            raise ValueError(self._diagnostic_summary(diagnostics))

    def _plan_diagnostics(self, plan: ModulePlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return module and descendant diagnostics before lowering starts."""
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
        return tuple(diagnostics)

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

    def _module_setter_diagnostics(self, plan: ModuleVariablePlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return module setter exposure and native-assignment diagnostics."""
        action = plan.binding.setter_action
        assignment = plan.bridge.native_assignment
        role = plan.bridge.setter_role
        if action is SetterAction.WRITE_THROUGH:
            diagnostics = []
            if assignment is not AssignmentMode.VALUE_COPY:
                diagnostics.append(self._diagnostic(plan.owner_path, "invalid-module-native-assignment", assignment))
            if role is None:
                diagnostics.append(self._diagnostic(plan.owner_path, "missing-module-setter-role", action.value))
            return tuple(diagnostics)
        if role is not None:
            return (self._diagnostic(plan.owner_path, "setter-role-without-write-through", role),)
        if action is SetterAction.REJECT_REPLACEMENT and plan.bridge.descriptor_kind is None:
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
            *self._function_output_diagnostics(plan),
        ]
        slots = {slot.native_position: slot for slot in plan.native_call_slots}
        for slot in plan.native_call_slots:
            diagnostics.extend(self._native_slot_diagnostics(slot))
        for argument in plan.arguments:
            diagnostics.extend(self._argument_diagnostics(argument, slots))
        if plan.result is not None:
            diagnostics.extend(self._result_diagnostics(plan.result, slots, plan.available_roles))
        for action in (*plan.writeback_actions, *plan.cleanup_actions, *plan.release_actions):
            diagnostics.extend(self._lifecycle_diagnostics(action, plan.available_roles))
        diagnostics.extend(self._writeback_phase_diagnostics(plan))
        return tuple(diagnostics)

    def _argument_diagnostics(
        self,
        plan: ArgumentTransferPlan,
        function_slots: dict[int, NativeCallSlotPlan],
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return binding-to-bridge handoff and slot diagnostics."""
        diagnostics = []
        role = plan.binding.handoff_role
        if plan.bridge.handoff_role != role:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-bridge-handoff", role))
        if plan.native_call_slot.symbolic_role != role:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-native-handoff", role))
        if plan.bridge.native_action is not plan.native_call_slot.native_action:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-native-action", plan.bridge.native_action.value)
            )
        if plan.bridge.abi_position != plan.native_position:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-bridge-position", plan.native_position))
        if plan.native_call_slot.native_position != plan.native_position:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-native-position", plan.native_position))
        if plan.native_call_slot.python_position != plan.python_position:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-python-position", plan.python_position))
        if function_slots.get(plan.native_position) != plan.native_call_slot:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-function-native-slot", plan.native_position)
            )
        diagnostics.extend(self._optional_argument_diagnostics(plan))
        return tuple(diagnostics)

    def _optional_argument_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return presence-mode and descriptor handoff diagnostics."""
        return (
            *self._optional_presence_diagnostics(plan),
            *self._optional_native_diagnostics(plan),
        )

    def _optional_presence_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return cross-view presence and descriptor diagnostics."""
        diagnostics = []
        mode = plan.binding.optional_mode
        if plan.bridge.optional_mode is not mode:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-optional-mode", mode.value))
        descriptor_mode = mode is OptionalMode.DESCRIPTOR
        if plan.binding.descriptor_boundary != descriptor_mode:
            diagnostics.append(self._diagnostic(plan.owner_path, "inconsistent-descriptor-boundary", mode.value))
        if descriptor_mode and plan.bridge.presence_role is None:
            diagnostics.append(self._diagnostic(plan.owner_path, "missing-descriptor-presence-role", mode.value))
        if not descriptor_mode and plan.bridge.presence_role is not None:
            diagnostics.append(self._diagnostic(plan.owner_path, "unexpected-descriptor-presence-role", mode.value))
        return tuple(diagnostics)

    def _optional_native_diagnostics(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return optional native-action and descriptor-kind diagnostics."""
        diagnostics = []
        mode = plan.binding.optional_mode
        descriptor_mode = mode is OptionalMode.DESCRIPTOR
        if mode is not OptionalMode.REQUIRED and plan.bridge.native_action not in {
            NativeBarrierAction.PASS_VALUE,
            NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS,
            NativeBarrierAction.PASS_STORAGE_ADDRESS,
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
        if plan.native_call_slot is not None or plan.bridge.abi_position is not None:
            return (self._diagnostic(plan.owner_path, "direct-result-has-native-slot", plan.source_kind),)
        return ()

    def _hidden_result_diagnostics(
        self,
        plan: ResultPlan,
        function_slots: dict[int, NativeCallSlotPlan],
    ) -> tuple[WrapperPlanDiagnostic, ...]:
        diagnostics = []
        if plan.native_call_slot is None or plan.bridge.abi_position is None:
            return (self._diagnostic(plan.owner_path, "missing-result-native-slot", plan.bridge.native_name),)
        slot = plan.native_call_slot
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
        if function_slots.get(slot.native_position) != slot:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-function-result-slot", slot.native_position)
            )
        return tuple(diagnostics)

    def _native_slot_diagnostics(self, plan: NativeCallSlotPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Return hidden literal and hidden result slot diagnostics."""
        diagnostics = []
        if plan.source_kind == "literal":
            if plan.literal_type is None:
                diagnostics.append(self._diagnostic(plan.owner_path, "missing-literal-type", plan.native_position))
            if plan.literal_value is None:
                diagnostics.append(self._diagnostic(plan.owner_path, "missing-literal-value", plan.native_position))
            if plan.python_position is not None:
                diagnostics.append(self._diagnostic(plan.owner_path, "literal-python-position", plan.python_position))
        if plan.source_kind == "result":
            if plan.result_position is None:
                diagnostics.append(self._diagnostic(plan.owner_path, "missing-result-position", plan.native_position))
            if plan.python_position is not None:
                diagnostics.append(self._diagnostic(plan.owner_path, "result-python-position", plan.python_position))
        return tuple(diagnostics)

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
        if binding.codegen_action not in {CodegenAction.COPY_IN_OUT, CodegenAction.IN_PLACE_ARGUMENT}:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "invalid-writeback-action", binding.codegen_action.value)
            )
        if plan.phase is WritebackPhase.COPY_OUT and not binding.python_result_role:
            diagnostics.append(self._diagnostic(plan.owner_path, "missing-python-writeback-target", phase_name))
        if plan.phase is not WritebackPhase.COPY_OUT and binding.python_result_role is not None:
            diagnostics.append(self._diagnostic(plan.owner_path, "unexpected-python-writeback-target", phase_name))
        return tuple(diagnostics)

    def _writeback_phase_diagnostics(self, plan: FunctionPlan) -> tuple[WrapperPlanDiagnostic, ...]:
        """Require one complete ordered phase set for every writeback handoff."""
        diagnostics = []
        grouped: dict[str, list[LifecycleActionPlan]] = {}
        for action in plan.writeback_actions:
            grouped.setdefault(action.source_role, []).append(action)
        expected = set(WritebackPhase)
        for source_role, actions in grouped.items():
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
        diagnostics = []
        if plan.result is not None and plan.writeback_actions:
            diagnostics.append(self._diagnostic(plan.owner_path, "mixed-result-and-writeback", plan.owner_path))
        result_positions = tuple(
            action.binding.result_position
            for action in plan.writeback_actions
            if action.phase is WritebackPhase.COPY_OUT and action.binding is not None
        )
        diagnostics.extend(
            self._sequence_diagnostics(plan.owner_path, "writeback-result", result_positions, len(result_positions))
        )
        requires_subroutine = plan.result is None or plan.result.source_kind == "hidden_output"
        if plan.bridge.native_is_subroutine != requires_subroutine:
            diagnostics.append(
                self._diagnostic(plan.owner_path, "inconsistent-native-callable-kind", requires_subroutine)
            )
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
        if plan.result is not None:
            roles.append(plan.result.bridge.native_result_role)
        return tuple(
            self._diagnostic(plan.owner_path, "duplicate-symbolic-role", role)
            for role, count in Counter(roles).items()
            if count > 1
        )

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
    ) -> RenderedGeneratedWrapperArtifacts:
        artifacts = GeneratedWrapperArtifacts(
            module_name=module_name,
            bridge_sources=(Path(f"bind_c_{module_name}_wrapper.f90"),),
            binding_sources=(Path(f"{module_name}_wrapper.c"),),
            header_files=(Path(f"{module_name}_wrapper.h"),),
            runtime_support_keys=runtime_support_keys,
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
