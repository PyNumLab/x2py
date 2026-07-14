"""Hierarchical wrapper-plan construction from completed semantic policy."""

from __future__ import annotations

from collections import Counter, defaultdict

from x2py.semantics import models
from x2py.semantics.wrapper_policy import (
    ArgumentHandoffMode,
    ArrayHandoffPolicy,
    ModuleGetterAction,
    ModuleVariablePolicy,
    OptionalMode,
    ArgumentPolicy,
    FunctionWrapperPolicy,
    LifecyclePolicy,
    NativeArrayDescriptorKind,
    NativeCallSlotPolicy,
    NativeArrayActualPolicy,
    NativeArrayHandleWrapperPolicy,
    NativeDescriptorHandoffABI,
    NativeDescriptorHandoffPolicy,
    NativeStatusErrorPolicy,
    ResultPolicy,
    ScalarDescriptorResultPolicy,
    TransformationPolicy,
    WritebackPhase,
    completed_module_variable_policy,
    completed_function_wrapper_policy,
)
from x2py.semantics.wrapper_exports import PythonExportPolicy
from x2py.semantics.ownership import NativeBarrierAction, SetterAction
from x2py.wrapper_codegen.plan import (
    ArrayHandoffPlan,
    ArgumentTransferPlan,
    BindingArgumentPlan,
    BindingFunctionPlan,
    BindingLifecyclePlan,
    BindingModulePlan,
    BindingModuleVariablePlan,
    BindingResultPlan,
    BindingStatusErrorPlan,
    BridgeArgumentPlan,
    BridgeFunctionPlan,
    BridgeLifecyclePlan,
    BridgeModulePlan,
    BridgeModuleVariablePlan,
    BridgeResultPlan,
    DatatypeFamily,
    FunctionPlan,
    LifecycleActionPlan,
    ModulePlan,
    ModuleVariablePlan,
    NamespacePlan,
    NativeCallSlotPlan,
    NativeArrayActualPlan,
    NativeArrayHandlePlan,
    NativeDescriptorHandoffPlan,
    ResultPlan,
    ScalarDescriptorResultPlan,
    TransformationPlan,
)
from x2py.wrapper_codegen.support import WrapperPlanSupportAnalyzer
from x2py.wrapper_codegen.visitor import ClassVisitor


_DATATYPE_FAMILIES = {
    "Bool": DatatypeFamily.BOOL,
    "Int8": DatatypeFamily.INTEGER,
    "Int16": DatatypeFamily.INTEGER,
    "Int32": DatatypeFamily.INTEGER,
    "Int64": DatatypeFamily.INTEGER,
    "Float32": DatatypeFamily.REAL,
    "Float64": DatatypeFamily.REAL,
    "Complex64": DatatypeFamily.COMPLEX,
    "Complex128": DatatypeFamily.COMPLEX,
    "String": DatatypeFamily.STRING,
}

_DOCUMENTATION_SCALAR_TYPES = {
    "Bool": "bool",
    "Int8": "int8",
    "Int16": "int16",
    "Int32": "int32",
    "Int64": "int64",
    "Float32": "float32",
    "Float64": "float64",
    "Complex64": "complex64",
    "Complex128": "complex128",
    "String": "str",
}


class WrapperPlanner(ClassVisitor):
    """Project completed semantic policies into one editable shared plan."""

    def __init__(self, *, support_analyzer: WrapperPlanSupportAnalyzer | None = None):
        """Create a planner with an optional support analyzer."""
        super().__init__()
        self.support_analyzer = support_analyzer or WrapperPlanSupportAnalyzer()

    def build(self, module: models.SemanticModule) -> ModulePlan:
        """Mechanically project one editable wrapper plan."""
        return self.visit(module)

    def _visit_SemanticModule(self, module: models.SemanticModule) -> ModulePlan:
        """Return one module plan after whole-unit support analysis."""
        report = self.support_analyzer.analyze(module)
        if not report.supported:
            raise ValueError(self._support_error(module.name, report.blockers))
        functions = self._functions_by_namespace(module)
        variables = self._variables_by_namespace(module)
        self._complete_generated_symbols(functions, variables)
        namespace_paths = self._namespace_paths((*functions, *variables))
        namespaces = tuple(
            NamespacePlan(
                owner_path=self._namespace_owner_path(module.name, path),
                python_path=path,
                functions=tuple(functions[path]),
                variables=tuple(variables[path]),
            )
            for path in namespace_paths
        )
        return ModulePlan(
            owner_path=module.name,
            binding=BindingModulePlan(module.name),
            bridge=BridgeModulePlan(module.name),
            namespaces=namespaces,
            required_headers=self._required_headers(namespaces),
        )

    def _functions_by_namespace(self, module: models.SemanticModule) -> dict[tuple[str, ...], list[FunctionPlan]]:
        """Group exported function plans by completed Python namespace."""
        functions = defaultdict(list)
        for function in module.functions:
            if function.visibility != "public":
                continue
            policy = completed_function_wrapper_policy(function)
            for export in policy.python_exports:
                functions[export.namespace].append(self._function_plan(policy, export, module.name))
        return functions

    def _variables_by_namespace(
        self,
        module: models.SemanticModule,
    ) -> dict[tuple[str, ...], list[ModuleVariablePlan]]:
        """Group exported module-variable plans by completed Python namespace."""
        variables = defaultdict(list)
        for variable in module.variables:
            if variable.visibility != "public":
                continue
            policy = completed_module_variable_policy(variable)
            exports_by_namespace = defaultdict(list)
            for export in policy.python_exports:
                exports_by_namespace[export.namespace].append(export.name)
            for namespace, python_names in exports_by_namespace.items():
                variables[namespace].append(
                    self._module_variable_plan(policy, namespace, tuple(python_names), module.name)
                )
        return variables

    def _complete_generated_symbols(
        self,
        functions: dict[tuple[str, ...], list[FunctionPlan]],
        variables: dict[tuple[str, ...], list[ModuleVariablePlan]],
    ) -> None:
        """Keep unique symbols short and qualify only colliding local names."""
        entries = (*self._planned_items(functions), *self._planned_items(variables))
        counts = Counter(item.symbol_name.casefold() for _namespace, item in entries)
        for namespace, item in entries:
            if counts[item.symbol_name.casefold()] > 1:
                item.symbol_name = self._symbol_name(namespace, item.symbol_name)

    def _planned_items(self, grouped: dict[tuple[str, ...], list]) -> tuple[tuple[tuple[str, ...], object], ...]:
        """Flatten namespace groups while retaining each item's namespace."""
        return tuple((namespace, item) for namespace, items in grouped.items() for item in items)

    def _module_variable_plan(
        self,
        policy: ModuleVariablePolicy,
        namespace: tuple[str, ...],
        python_names: tuple[str, ...],
        module_name: str,
    ) -> ModuleVariablePlan:
        getter_role = (
            None if policy.getter_action is ModuleGetterAction.CONSTANT_VALUE else f"{policy.owner_path}:getter"
        )
        setter_role = f"{policy.owner_path}:setter" if policy.setter_action is SetterAction.WRITE_THROUGH else None
        return ModuleVariablePlan(
            owner_path=self._export_owner_path(module_name, namespace, python_names[0]),
            symbol_name=policy.native_name.casefold(),
            semantic_type_name=policy.semantic_type_name,
            datatype_family=self._datatype_family(policy.semantic_type_name),
            binding=BindingModuleVariablePlan(
                python_names=python_names,
                getter_action=policy.getter_action,
                setter_action=policy.setter_action,
                initializer=policy.initializer,
                constant_value=policy.constant_value,
            ),
            bridge=BridgeModuleVariablePlan(
                native_name=policy.native_name,
                native_module=policy.native_module,
                getter_action=policy.getter_action,
                native_assignment=policy.native_assignment,
                descriptor_kind=policy.descriptor_kind,
                getter_role=getter_role,
                setter_role=setter_role,
            ),
            native_array_handle=self._native_array_handle_plan(policy.native_array_handle, policy.owner_path),
        )

    def _function_plan(
        self,
        policy: FunctionWrapperPolicy,
        export: PythonExportPolicy,
        module_name: str,
    ) -> FunctionPlan:
        """Return one exported function plan from completed policy."""
        native_call_slots = tuple(
            self._native_slot_plan(slot, self._native_slot_role(slot, policy.results))
            for slot in policy.native_call_slots
        )
        arguments = self._argument_plans(policy, native_call_slots)
        results = self._result_plans(policy, native_call_slots)
        return FunctionPlan(
            owner_path=self._export_owner_path(module_name, export.namespace, export.name),
            symbol_name=export.name.casefold(),
            binding=BindingFunctionPlan(
                python_name=export.name,
                docstring=self._function_docstring(export.name, arguments, results),
                hold_gil=policy.hold_gil,
                status_error=self._status_error_plan(policy.status_error, native_call_slots),
            ),
            bridge=BridgeFunctionPlan(
                policy.native_name,
                policy.external,
                policy.native_module,
                policy.native_is_subroutine,
            ),
            arguments=arguments,
            results=results,
            native_call_slots=native_call_slots,
            available_roles=self._available_roles(arguments, results, native_call_slots),
            writeback_actions=tuple(self.visit(action) for action in policy.writeback_actions),
            cleanup_actions=tuple(self.visit(action) for action in policy.cleanup_actions),
            release_actions=tuple(self.visit(action) for action in policy.release_actions),
        )

    # Stable Python function documentation from completed transfer plans.
    def _function_docstring(
        self,
        python_name: str,
        arguments: tuple[ArgumentTransferPlan, ...],
        results: tuple[ResultPlan, ...],
    ) -> str:
        """Describe the Python boundary without asking a backend to infer policy."""
        visible_arguments = tuple(argument for argument in arguments if argument.python_visible)
        documented_outputs = self._documented_outputs(arguments, results)
        parameter_names = ", ".join(argument.binding.python_name for argument in visible_arguments)
        result_summary = self._result_documentation_summary(documented_outputs)
        lines = (
            f"{python_name}({parameter_names}) -> {result_summary}",
            *self._parameter_documentation_section(visible_arguments),
            *self._return_documentation_section(documented_outputs, arguments),
            "",
            "Raises",
            "------",
            "TypeError",
            "    If an argument violates its completed dtype, rank, shape, layout, or handle contract.",
        )
        return "\n".join(lines)

    def _parameter_documentation_section(
        self,
        arguments: tuple[ArgumentTransferPlan, ...],
    ) -> tuple[str, ...]:
        """Return the parameter section for visible completed transfers."""
        if not arguments:
            return ()
        body = tuple(line for argument in arguments for line in self._argument_documentation_lines(argument))
        return ("", "Parameters", "----------", *body)

    def _return_documentation_section(
        self,
        outputs: tuple[ArgumentTransferPlan | ResultPlan, ...],
        arguments: tuple[ArgumentTransferPlan, ...],
    ) -> tuple[str, ...]:
        """Return the result section for ordered result transfers."""
        body = tuple(
            line
            for output in outputs
            for line in (
                self._projected_argument_documentation_lines(output)
                if isinstance(output, ArgumentTransferPlan)
                else self._result_documentation_lines(output, arguments)
            )
        )
        return ("", "Returns", "-------", *(body or ("None",)))

    def _argument_documentation_lines(self, argument: ArgumentTransferPlan) -> tuple[str, ...]:
        """Render one argument solely from its completed transfer facts."""
        optional = argument.binding.optional_mode is not OptionalMode.REQUIRED or (
            argument.nullable and argument.native_array_handle is None
        )
        type_name = self._transfer_documentation_type(argument, nullable=optional, signature=False)
        lines = [f"{argument.binding.python_name} : {type_name}"]
        lines.extend(self._array_documentation_lines(argument.array))
        lines.extend(self._argument_handle_documentation_lines(argument))
        lines.extend(self._argument_optional_documentation_lines(argument, optional=optional))
        lines.extend(("    Mutates: yes",) if argument.mutates_native else ())
        return tuple(lines)

    def _projected_argument_documentation_lines(
        self,
        argument: ArgumentTransferPlan,
    ) -> tuple[str, ...]:
        """Render one identity/replacement output owned by an argument transfer."""
        nullable = argument.binding.optional_mode is not OptionalMode.REQUIRED
        type_name = self._transfer_documentation_type(argument, nullable=nullable, signature=False)
        lines = [f"{argument.binding.python_name} : {type_name}"]
        lines.extend(self._array_documentation_lines(argument.array))
        lines.extend(self._argument_handle_documentation_lines(argument))
        return tuple(lines)

    @staticmethod
    def _argument_handle_documentation_lines(argument: ArgumentTransferPlan) -> tuple[str, ...]:
        """Describe persistent descriptor ownership when one is planned."""
        if argument.native_array_handle is None:
            return ()
        return (f"    Descriptor ownership: {argument.native_array_handle.descriptor_ownership.value}",)

    @staticmethod
    def _argument_optional_documentation_lines(
        argument: ArgumentTransferPlan,
        *,
        optional: bool,
    ) -> tuple[str, ...]:
        """Describe omission and present-null semantics selected by policy."""
        if argument.binding.optional_mode is OptionalMode.DESCRIPTOR:
            return (
                "    Omit to make the native optional dummy absent.",
                "    Pass None for a present unallocated or unassociated descriptor.",
            )
        if argument.binding.optional_mode is OptionalMode.REQUIRED_DESCRIPTOR:
            return ("    Pass None for an unallocated or unassociated required descriptor.",)
        if optional:
            return ("    May be omitted or passed as None.",)
        return ()

    def _result_documentation_lines(
        self,
        result: ResultPlan,
        arguments: tuple[ArgumentTransferPlan, ...],
    ) -> tuple[str, ...]:
        """Render one result from its owning result plan and projection index."""
        name = self._result_documentation_name(result, arguments)
        type_name = self._transfer_documentation_type(result, nullable=result.nullable, signature=False)
        lines = [f"{name} : {type_name}"]
        lines.extend(self._array_documentation_lines(result.array))
        if result.native_array_handle is not None:
            handle = result.native_array_handle
            lines.append(f"    Descriptor ownership: {handle.descriptor_ownership.value}")
            state = "Unallocated" if handle.descriptor_kind is NativeArrayDescriptorKind.ALLOCATABLE else "Unassociated"
            lines.append(f"    {state} state remains inside the returned handle.")
        return tuple(lines)

    def _result_documentation_summary(
        self,
        outputs: tuple[ArgumentTransferPlan | ResultPlan, ...],
    ) -> str:
        """Return the stable signature spelling for ordered Python results."""
        types = tuple(
            self._transfer_documentation_type(
                output,
                nullable=(
                    output.binding.optional_mode is not OptionalMode.REQUIRED
                    if isinstance(output, ArgumentTransferPlan)
                    else output.nullable
                ),
                signature=True,
            )
            for output in outputs
        )
        if not types:
            return "None"
        if len(types) == 1:
            return types[0]
        return f"tuple[{', '.join(types)}]"

    @staticmethod
    def _documented_outputs(
        arguments: tuple[ArgumentTransferPlan, ...],
        results: tuple[ResultPlan, ...],
    ) -> tuple[ArgumentTransferPlan | ResultPlan, ...]:
        """Merge result transfers with argument-owned projected outputs by position."""
        by_position = dict(WrapperPlanner._projected_documented_outputs(arguments))
        by_position.update((result.result_position, result) for result in results)
        return tuple(by_position[position] for position in sorted(by_position))

    @staticmethod
    def _projected_documented_outputs(
        arguments: tuple[ArgumentTransferPlan, ...],
    ) -> tuple[tuple[int, ArgumentTransferPlan], ...]:
        """Return projected argument outputs with concrete result positions."""
        return tuple(
            (argument.result_position, argument)
            for argument in arguments
            if argument.projects_result and argument.result_position is not None
        )

    def _transfer_documentation_type(self, transfer, *, nullable: bool, signature: bool) -> str:
        """Map one completed transfer representation to its Python documentation type."""
        type_name = self._transfer_base_documentation_type(transfer)
        return self._nullable_documentation_type(type_name, nullable=nullable, signature=signature)

    def _transfer_base_documentation_type(self, transfer) -> str:
        """Map a completed representation to its non-null Python type."""
        scalar_type = _DOCUMENTATION_SCALAR_TYPES[transfer.semantic_type_name]
        if transfer.native_array_handle is not None:
            return self._native_handle_documentation_type(transfer, scalar_type)
        if transfer.array is not None:
            element_type = "bytes" if transfer.datatype_family is DatatypeFamily.STRING else scalar_type
            return f"ndarray[{element_type}]"
        return scalar_type

    @staticmethod
    def _native_handle_documentation_type(transfer, scalar_type: str) -> str:
        """Spell one allocatable or pointer array handle type."""
        prefix = (
            "AllocatableArray"
            if transfer.native_array_handle.descriptor_kind is NativeArrayDescriptorKind.ALLOCATABLE
            else "PointerArray"
        )
        return f"{prefix}[{scalar_type}]"

    @staticmethod
    def _nullable_documentation_type(type_name: str, *, nullable: bool, signature: bool) -> str:
        """Add signature or section nullability spelling when selected."""
        if not nullable:
            return type_name
        return f"{type_name} | None" if signature else f"{type_name} or None"

    @staticmethod
    def _array_documentation_lines(array: ArrayHandoffPlan | None) -> tuple[str, ...]:
        """Describe rank and layout already selected in one array handoff plan."""
        if array is None:
            return ()
        if array.rank is None:
            return ("    Rank: 1..15", "    Layout: F-contiguous")
        lines = [f"    Rank: {array.rank}"]
        if array.rank > 1:
            layout = "C-contiguous" if array.order == "ORDER_C" else "F-contiguous"
            lines.append(f"    Layout: {layout}")
        return tuple(lines)

    @staticmethod
    def _result_documentation_name(
        result: ResultPlan,
        arguments: tuple[ArgumentTransferPlan, ...],
    ) -> str:
        """Name a projected result through its owning argument when available."""
        projected = next(
            (argument for argument in arguments if argument.result_position == result.result_position),
            None,
        )
        if projected is not None:
            return projected.binding.python_name
        return result.bridge.native_name or "result"

    def _argument_plans(
        self,
        policy: FunctionWrapperPolicy,
        native_call_slots: tuple[NativeCallSlotPlan, ...],
    ) -> tuple[ArgumentTransferPlan, ...]:
        """Return declared transfers sharing the function's native-slot records."""
        return tuple(
            self.visit(
                argument,
                native_slot=self._planned_native_slot(native_call_slots, argument.owner_path),
            )
            for argument in policy.arguments
        )

    def _result_plans(
        self,
        policy: FunctionWrapperPolicy,
        native_call_slots: tuple[NativeCallSlotPlan, ...],
    ) -> tuple[ResultPlan, ...]:
        """Return ordered result consumers sharing completed native slots."""
        return tuple(
            self.visit(
                result,
                native_slot=self._result_native_slot(result, native_call_slots),
            )
            for result in sorted(policy.results, key=lambda item: item.result_position)
        )

    # Shared argument, result, and lifecycle transfer planning.
    def _visit_ArgumentPolicy(
        self,
        policy: ArgumentPolicy,
        *,
        native_slot: NativeCallSlotPlan,
    ) -> ArgumentTransferPlan:
        """Return one transfer whose backend views share one handoff role."""
        role = self._value_role(policy.owner_path)
        native_array_handle = native_slot.native_array_handle
        length_role = self._argument_length_role(policy)
        return ArgumentTransferPlan(
            owner_path=policy.owner_path,
            python_position=policy.python_position,
            native_position=policy.native_position,
            semantic_type_name=policy.semantic_type_name,
            datatype_family=self._datatype_family(policy.semantic_type_name),
            character_length=policy.character_length,
            object_kind=policy.ownership.kind,
            ownership_owner=policy.ownership.owner,
            transfer_mode=policy.ownership.transfer,
            destruction_policy=policy.ownership.destruction,
            storage_mode=policy.storage_mode,
            boundary_storage_mode=policy.boundary_storage_mode,
            nullable=policy.nullable,
            mutates_native=policy.ownership.mutates_native,
            projects_result=policy.projects_result,
            python_visible=policy.python_visible,
            result_position=policy.result_position,
            array=native_slot.array,
            native_array_actual=self._native_array_actual_plan(policy.native_array_actual),
            native_array_handle=native_array_handle,
            binding=self._binding_argument_plan(policy, role, length_role),
            bridge=self._bridge_argument_plan(policy, native_slot, native_array_handle, role, length_role),
            native_call_slot=native_slot,
            transformations=tuple(self.visit(item) for item in policy.transformations),
        )

    @staticmethod
    def _argument_length_role(policy: ArgumentPolicy) -> str | None:
        """Return the character length role selected by completed handoff policy."""
        if policy.handoff_mode is ArgumentHandoffMode.CHARACTER_BUFFER:
            return f"{policy.owner_path}:length"
        return None

    @staticmethod
    def _binding_argument_plan(
        policy: ArgumentPolicy,
        role: str,
        length_role: str | None,
    ) -> BindingArgumentPlan:
        """Project the binding-facing view without revisiting semantic decisions."""
        return BindingArgumentPlan(
            python_name=policy.python_name,
            python_action=policy.python_barrier_action,
            codegen_action=policy.codegen_action,
            handoff_role=role,
            optional_mode=policy.optional_mode,
            nullable=policy.nullable,
            writable=policy.writable,
            descriptor_boundary=policy.descriptor_boundary,
            length_handoff_role=length_role,
        )

    def _bridge_argument_plan(
        self,
        policy: ArgumentPolicy,
        native_slot: NativeCallSlotPlan,
        native_array_handle: NativeArrayHandlePlan | None,
        role: str,
        length_role: str | None,
    ) -> BridgeArgumentPlan:
        """Project the bridge-facing view without revisiting semantic decisions."""
        return BridgeArgumentPlan(
            native_name=policy.native_name,
            native_action=policy.native_barrier_action,
            codegen_action=policy.codegen_action,
            handoff_mode=policy.handoff_mode,
            data_action=policy.bridge_data_action,
            copy_reason=policy.bridge_copy_reason,
            abi_position=native_slot.native_position,
            handoff_role=role,
            optional_mode=policy.optional_mode,
            presence_role=self._argument_presence_role(policy, native_array_handle),
            length_handoff_role=length_role,
            descriptor_output_role=self._required_descriptor_output_role(policy, "descriptor-output"),
            descriptor_output_presence_role=self._required_descriptor_output_role(
                policy,
                "descriptor-output-present",
            ),
        )

    @staticmethod
    def _argument_presence_role(
        policy: ArgumentPolicy,
        native_array_handle: NativeArrayHandlePlan | None,
    ) -> str | None:
        """Return the explicit optional or descriptor presence handoff role."""
        if native_array_handle is not None:
            return native_array_handle.handoff.presence_role
        if policy.optional_mode is OptionalMode.DESCRIPTOR:
            return f"{policy.owner_path}:present"
        return None

    @staticmethod
    def _required_descriptor_output_role(policy: ArgumentPolicy, suffix: str) -> str | None:
        """Return one required-descriptor copyout role when projection owns it."""
        if policy.optional_mode is OptionalMode.REQUIRED_DESCRIPTOR and policy.projects_result:
            return f"{policy.owner_path}:{suffix}"
        return None

    def _visit_TransformationPolicy(self, policy: TransformationPolicy) -> TransformationPlan:
        """Mechanically retain one completed transformation owner and phase."""
        return TransformationPlan(
            phase=policy.phase,
            layer=policy.layer,
            action=policy.action,
            source_representation=policy.source_representation,
            target_representation=policy.target_representation,
            reason=policy.reason,
        )

    def _visit_LifecyclePolicy(
        self,
        policy: LifecyclePolicy,
    ) -> LifecycleActionPlan:
        """Return one transfer-owned action for function-wide ordering."""
        family = self._datatype_family(policy.semantic_type_name)
        binding = None
        bridge = None
        if policy.phase is WritebackPhase.NATIVE_MUTATION:
            bridge = BridgeLifecyclePlan(source_role=policy.source_role)
        else:
            binding = BindingLifecyclePlan(
                source_role=policy.source_role,
                codegen_action=policy.codegen_action,
                semantic_type_name=policy.semantic_type_name,
                datatype_family=family,
                result_position=policy.result_position,
                python_result_role=(
                    f"{policy.owner_path}:python-result" if policy.phase is WritebackPhase.COPY_OUT else None
                ),
            )
        return LifecycleActionPlan(
            owner_path=policy.owner_path,
            phase=policy.phase,
            source_role=policy.source_role,
            codegen_action=policy.codegen_action,
            semantic_type_name=policy.semantic_type_name,
            datatype_family=family,
            object_kind=policy.object_kind,
            result_position=policy.result_position,
            binding=binding,
            bridge=bridge,
        )

    def _visit_ResultPolicy(
        self,
        policy: ResultPolicy,
        *,
        native_slot: NativeCallSlotPlan | None,
    ) -> ResultPlan:
        """Return one result with binding consumer and bridge producer views."""
        native_role = f"{policy.owner_path}:native-result"
        if policy.source_kind == "hidden_output" and native_slot is None:
            raise ValueError(f"{policy.owner_path!r} hidden result requires its completed native-call slot")
        array = self._result_array_plan(policy, native_slot)
        native_array_handle = self._result_native_array_handle_plan(policy, native_slot, array)
        return ResultPlan(
            owner_path=policy.owner_path,
            semantic_type_name=policy.semantic_type_name,
            datatype_family=self._datatype_family(policy.semantic_type_name),
            source_kind=policy.source_kind,
            result_position=policy.result_position,
            character_length=policy.character_length,
            object_kind=policy.ownership.kind,
            ownership_owner=policy.ownership.owner,
            transfer_mode=policy.ownership.transfer,
            destruction_policy=policy.ownership.destruction,
            storage_mode=policy.storage_mode,
            boundary_storage_mode=policy.boundary_storage_mode,
            nullable=policy.ownership.nullable,
            array=array,
            native_array_handle=native_array_handle,
            binding=BindingResultPlan(
                policy.codegen_action,
                policy.python_barrier_action,
                f"{policy.owner_path}:python-result",
            ),
            bridge=BridgeResultPlan(
                policy.codegen_action,
                policy.native_barrier_action,
                policy.bridge_data_action,
                policy.bridge_copy_reason,
                native_role,
                policy.native_name,
                policy.native_position,
            ),
            native_call_slot=native_slot,
            scalar_descriptor=self._result_scalar_descriptor_plan(policy, native_slot),
            transformations=tuple(self.visit(item) for item in policy.transformations),
        )

    def _result_array_plan(
        self,
        policy: ResultPolicy,
        native_slot: NativeCallSlotPlan | None,
    ) -> ArrayHandoffPlan | None:
        """Reuse a hidden slot array or project one direct result array."""
        if native_slot is not None:
            return native_slot.array
        return self._array_plan(
            policy.array,
            policy.owner_path,
            include_buffer_roles=policy.native_array_handle is None,
        )

    def _result_native_array_handle_plan(
        self,
        policy: ResultPolicy,
        native_slot: NativeCallSlotPlan | None,
        array: ArrayHandoffPlan | None,
    ) -> NativeArrayHandlePlan | None:
        """Reuse a hidden slot handle or project one direct result handle."""
        if native_slot is not None:
            return native_slot.native_array_handle
        return self._native_array_handle_plan(policy.native_array_handle, policy.owner_path, array=array)

    def _result_scalar_descriptor_plan(
        self,
        policy: ResultPolicy,
        native_slot: NativeCallSlotPlan | None,
    ) -> ScalarDescriptorResultPlan | None:
        """Reuse exact hidden descriptor state or project one direct result."""
        if native_slot is not None:
            return native_slot.scalar_descriptor
        return self._scalar_descriptor_result_plan(policy.scalar_descriptor, policy.owner_path)

    def _native_slot_plan(self, slot: NativeCallSlotPolicy, role: str) -> NativeCallSlotPlan:
        """Return one shared ABI slot without selecting backend behavior."""
        array = self._array_plan(
            slot.array,
            slot.owner_path,
            include_buffer_roles=slot.native_barrier_action is NativeBarrierAction.PASS_ARRAY_BUFFER,
        )
        return NativeCallSlotPlan(
            owner_path=slot.owner_path,
            native_position=slot.native_position,
            source_kind=slot.source_kind,
            python_position=slot.python_position,
            python_name=slot.python_name,
            native_name=slot.native_name,
            value_kind=slot.value_kind,
            symbolic_role=role,
            native_action=slot.native_barrier_action,
            codegen_action=slot.codegen_action,
            bridge_data_action=slot.bridge_data_action,
            bridge_copy_reason=slot.bridge_copy_reason,
            object_kind=slot.object_kind,
            literal_type=slot.literal_type,
            literal_value=slot.literal_value,
            result_position=slot.result_position,
            semantic_type_name=slot.semantic_type_name,
            datatype_family=(self._datatype_family(slot.semantic_type_name) if slot.semantic_type_name else None),
            character_length=slot.character_length,
            array=array,
            native_array_handle=self._native_array_handle_plan(slot.native_array_handle, slot.owner_path, array=array),
            scalar_descriptor=self._scalar_descriptor_result_plan(slot.scalar_descriptor, slot.owner_path),
        )

    # Rank-zero scalar/string descriptor result planning.
    def _scalar_descriptor_result_plan(
        self,
        policy: ScalarDescriptorResultPolicy | None,
        owner_path: str,
    ) -> ScalarDescriptorResultPlan | None:
        """Mechanically project one nullable rank-zero descriptor result."""
        if policy is None:
            return None
        return ScalarDescriptorResultPlan(
            descriptor_kind=policy.descriptor_kind,
            runtime_length=policy.runtime_length,
            nullable=policy.nullable,
            copy_reason=policy.copy_reason,
            release_owner=policy.release_owner,
            presence_role=f"{owner_path}:present",
        )

    # Native-array-handle planning.
    def _native_array_actual_plan(self, policy: NativeArrayActualPolicy | None) -> NativeArrayActualPlan | None:
        """Mechanically project completed ordinary-array accepted sources."""
        if policy is None:
            return None
        return NativeArrayActualPlan(
            accepted_sources=policy.accepted_sources,
            dtype=policy.dtype,
            rank=policy.rank,
            shape=policy.shape,
            order=policy.order,
            writable=policy.writable,
            require_native_byte_order=policy.require_native_byte_order,
            require_aligned=policy.require_aligned,
            require_contiguous=policy.require_contiguous,
        )

    def _native_array_handle_plan(
        self,
        policy: NativeArrayHandleWrapperPolicy | None,
        owner_path: str,
        *,
        array: ArrayHandoffPlan | None = None,
    ) -> NativeArrayHandlePlan | None:
        """Project one typed handle policy and its subordinate descriptor roles."""
        if policy is None:
            return None
        array_plan = array or self._array_plan(policy.array, owner_path, include_buffer_roles=False)
        if array_plan is None:
            raise ValueError(f"Native array handle {owner_path!r} is missing its array data facet")
        return NativeArrayHandlePlan(
            descriptor_kind=policy.descriptor_kind,
            handle_kind=policy.handle_kind,
            origin=policy.origin,
            owner=policy.owner,
            owner_retention=policy.owner_retention,
            descriptor_ownership=policy.descriptor_ownership,
            borrowed=policy.borrowed,
            getter_behavior=policy.getter_behavior,
            setter_action=policy.setter_action,
            native_assignment=policy.native_assignment,
            output_projection=policy.output_projection,
            release=policy.release,
            target_lifetime=policy.target_lifetime,
            destroy_behavior=policy.destroy_behavior,
            extraction_action=policy.extraction_action,
            descriptor_interop=policy.descriptor_interop,
            nullable=policy.nullable,
            optional_absent=policy.optional_absent,
            storage_mode=policy.storage_mode,
            operations=policy.operations,
            required_headers=policy.required_headers,
            array=array_plan,
            handoff=self._native_descriptor_handoff_plan(policy.handoff, owner_path, policy.operations),
        )

    def _native_descriptor_handoff_plan(
        self,
        policy: NativeDescriptorHandoffPolicy,
        owner_path: str,
        operations,
    ) -> NativeDescriptorHandoffPlan:
        """Name descriptor facts once for binding, bridge, and lifecycle consumers."""
        fact_packed = policy.abi is NativeDescriptorHandoffABI.FACT_PACKED_CALL_LOCAL
        return NativeDescriptorHandoffPlan(
            abi=policy.abi,
            descriptor_pointer_role=self._native_descriptor_pointer_role(policy, owner_path),
            base_addr_role=self._native_descriptor_fact_role(owner_path, "base-addr", fact_packed),
            elem_len_role=self._native_descriptor_fact_role(owner_path, "elem-len", fact_packed),
            rank_role=self._native_descriptor_fact_role(owner_path, "descriptor-rank", fact_packed),
            lower_bound_roles=self._native_descriptor_axis_roles(owner_path, policy.rank, "lower-bound", fact_packed),
            extent_roles=self._native_descriptor_axis_roles(owner_path, policy.rank, "descriptor-extent", fact_packed),
            stride_multiplier_roles=self._native_descriptor_axis_roles(
                owner_path, policy.rank, "stride-multiplier", fact_packed
            ),
            presence_role=self._native_descriptor_presence_role(policy, owner_path),
            owner_storage_role=self._native_descriptor_owner_role(policy, owner_path),
            operation_roles=tuple((operation, f"{owner_path}:operation:{operation.value}") for operation in operations),
        )

    def _native_descriptor_pointer_role(
        self,
        policy: NativeDescriptorHandoffPolicy,
        owner_path: str,
    ) -> str | None:
        """Name call-local or direct descriptor storage when one crosses the ABI."""
        if policy.abi is NativeDescriptorHandoffABI.OWNED_RESULT_STORAGE:
            return None
        return f"{owner_path}:descriptor"

    def _native_descriptor_fact_role(self, owner_path: str, label: str, enabled: bool) -> str | None:
        """Name one fact-packed scalar descriptor field."""
        return f"{owner_path}:{label}" if enabled else None

    def _native_descriptor_presence_role(
        self,
        policy: NativeDescriptorHandoffPolicy,
        owner_path: str,
    ) -> str | None:
        """Name optional descriptor presence separately from allocation state."""
        return f"{owner_path}:descriptor-present" if policy.optional_presence else None

    def _native_descriptor_owner_role(
        self,
        policy: NativeDescriptorHandoffPolicy,
        owner_path: str,
    ) -> str | None:
        """Name persistent wrapper-owned descriptor storage."""
        if policy.abi is NativeDescriptorHandoffABI.OWNED_RESULT_STORAGE:
            return f"{owner_path}:owner-storage"
        return None

    def _native_descriptor_axis_roles(
        self,
        owner_path: str,
        rank: int,
        label: str,
        enabled: bool,
    ) -> tuple[str, ...]:
        """Name one standard-descriptor field role per declared axis."""
        if not enabled:
            return ()
        return tuple(f"{owner_path}:{label}:{axis}" for axis in range(rank))

    # Ordinary-array buffer and raw-address planning.
    def _array_plan(
        self,
        policy: ArrayHandoffPolicy | None,
        owner_path: str,
        *,
        include_buffer_roles: bool = True,
    ) -> ArrayHandoffPlan | None:
        """Mechanically add only the ABI roles selected by completed transport."""
        if policy is None:
            return None
        abi_rank, runtime_rank_role, itemsize_role = self._array_transport_roles(
            policy,
            owner_path,
            include_buffer_roles,
        )
        return ArrayHandoffPlan(
            rank=policy.rank,
            shape=policy.shape,
            axes=policy.axes,
            order=policy.order,
            native_order=policy.native_order,
            contiguous=policy.contiguous,
            itemsize=policy.itemsize,
            category=policy.category,
            data_role=self._value_role(owner_path),
            extent_roles=tuple(f"{owner_path}:extent:{axis}" for axis in range(abi_rank)),
            extent_reference_roles=self._array_extent_reference_roles(owner_path, policy.extent_references),
            upper_bound_roles=self._array_layout_roles(owner_path, abi_rank, policy.contiguous, "upper-bound"),
            stride_roles=self._array_layout_roles(owner_path, abi_rank, policy.contiguous, "stride"),
            runtime_rank_role=runtime_rank_role,
            itemsize_role=itemsize_role,
        )

    def _array_transport_roles(
        self,
        policy: ArrayHandoffPolicy,
        owner_path: str,
        include_buffer_roles: bool,
    ) -> tuple[int, str | None, str | None]:
        """Return packed-buffer roles or the raw-address empty role set."""
        if not include_buffer_roles:
            return 0, None, None
        return (
            self._array_abi_rank(policy),
            self._array_runtime_rank_role(policy, owner_path),
            self._array_itemsize_role(policy, owner_path),
        )

    def _array_abi_rank(self, policy: ArrayHandoffPolicy) -> int:
        """Return the concrete ABI field count for fixed or assumed rank."""
        return 15 if policy.rank is None else policy.rank

    def _array_runtime_rank_role(self, policy: ArrayHandoffPolicy, owner_path: str) -> str | None:
        """Name the runtime-rank role only for assumed-rank arrays."""
        return f"{owner_path}:rank" if policy.rank is None else None

    def _array_itemsize_role(self, policy: ArrayHandoffPolicy, owner_path: str) -> str | None:
        """Name the itemsize role only for fixed-width character arrays."""
        return f"{owner_path}:itemsize" if policy.itemsize is not None else None

    def _array_layout_roles(
        self,
        owner_path: str,
        rank: int,
        contiguous: bool | None,
        label: str,
    ) -> tuple[str, ...]:
        """Name one ABI role per axis only for stride-aware layouts."""
        if contiguous is not False:
            return ()
        return tuple(f"{owner_path}:{label}:{axis}" for axis in range(rank))

    def _array_extent_reference_roles(
        self,
        owner_path: str,
        references: tuple[tuple[str, ...], ...],
    ) -> tuple[tuple[str, ...], ...]:
        """Resolve completed extent names to existing argument handoff roles."""
        function_path = owner_path.rsplit(".", 1)[0]
        return tuple(tuple(f"{function_path}.{name}:value" for name in axis) for axis in references)

    def _status_error_plan(
        self,
        policy: NativeStatusErrorPolicy | None,
        native_call_slots: tuple[NativeCallSlotPlan, ...],
    ) -> BindingStatusErrorPlan | None:
        """Project one completed native-status decision into binding roles."""
        if policy is None:
            return None
        roles = {slot.owner_path: slot.symbolic_role for slot in native_call_slots}
        try:
            status_role = roles[policy.status.owner_path]
            message_role = roles[policy.message.owner_path] if policy.message is not None else None
        except KeyError as error:
            raise ValueError(f"Completed native status output {error.args[0]!r} has no native-call slot") from None
        return BindingStatusErrorPlan(
            status_role=status_role,
            message_role=message_role,
            success=policy.success,
            exception_kind=policy.exception_kind,
        )

    def _planned_native_slot(
        self,
        native_call_slots: tuple[NativeCallSlotPlan, ...],
        owner_path: str,
    ) -> NativeCallSlotPlan:
        """Return the one shared editable native-call slot for an owner."""
        for slot in native_call_slots:
            if slot.owner_path == owner_path:
                return slot
        raise ValueError(f"{owner_path!r} is missing a completed native-call slot")

    def _result_native_slot(
        self,
        result_policy: ResultPolicy,
        native_call_slots: tuple[NativeCallSlotPlan, ...],
    ) -> NativeCallSlotPlan | None:
        """Return the completed slot for one hidden result, if any."""
        if result_policy.source_kind != "hidden_output":
            return None
        return self._planned_native_slot(native_call_slots, result_policy.owner_path)

    def _available_roles(
        self,
        arguments: tuple[ArgumentTransferPlan, ...],
        results: tuple[ResultPlan, ...],
        native_call_slots: tuple[NativeCallSlotPlan, ...],
    ) -> tuple[str, ...]:
        """Return symbolic roles available after the native call."""
        roles = [argument.binding.handoff_role for argument in arguments]
        roles.extend(
            role
            for argument in arguments
            for role in (
                argument.bridge.descriptor_output_role,
                argument.bridge.descriptor_output_presence_role,
            )
            if role is not None
        )
        roles.extend(self._native_result_roles(native_call_slots))
        roles.extend(self._direct_result_roles(results))
        return tuple(dict.fromkeys(roles))

    def _required_headers(self, namespaces: tuple[NamespacePlan, ...]) -> tuple[str, ...]:
        """Return the union of headers selected by completed handle plans."""
        handles = tuple(
            handle
            for namespace in namespaces
            for handle in self._namespace_native_array_handles(namespace)
            if handle is not None
        )
        return self._native_array_headers(handles)

    def _native_array_headers(self, handles: tuple[NativeArrayHandlePlan, ...]) -> tuple[str, ...]:
        """Deduplicate planned handle headers in encounter order."""
        return tuple(dict.fromkeys(header for handle in handles for header in handle.required_headers))

    def _namespace_native_array_handles(
        self,
        namespace: NamespacePlan,
    ) -> tuple[NativeArrayHandlePlan | None, ...]:
        """Return argument, result, and module handle plans for one namespace."""
        return (
            *(handle for function in namespace.functions for handle in self._function_native_array_handles(function)),
            *(variable.native_array_handle for variable in namespace.variables),
        )

    def _function_native_array_handles(
        self,
        function: FunctionPlan,
    ) -> tuple[NativeArrayHandlePlan | None, ...]:
        """Return datatype-varying handle owners for one function."""
        return (
            *(argument.native_array_handle for argument in function.arguments),
            *(result.native_array_handle for result in function.results),
        )

    def _native_result_roles(self, native_call_slots: tuple[NativeCallSlotPlan, ...]) -> tuple[str, ...]:
        """Return every role produced through a native result slot."""
        return tuple(slot.symbolic_role for slot in native_call_slots if slot.source_kind == "result")

    def _direct_result_roles(self, results: tuple[ResultPlan, ...]) -> tuple[str, ...]:
        """Return direct-return roles produced by the bridge function result."""
        return tuple(result.bridge.native_result_role for result in results if result.source_kind == "direct_return")

    def _datatype_family(self, semantic_type_name: str) -> DatatypeFamily:
        """Copy the backend-relevant family of one supported semantic type."""
        try:
            return _DATATYPE_FAMILIES[semantic_type_name]
        except KeyError:
            raise ValueError(f"Unsupported first-lane scalar type {semantic_type_name!r}") from None

    def _support_error(self, owner_path: str, blockers: object) -> str:
        """Return a compact unsupported-generation-unit error."""
        details = "; ".join(f"{item.owner_path}: {item.reason}" for item in blockers)
        return f"Unsupported wrapper-plan generation unit {owner_path!r}: {details}"

    def _namespace_paths(self, declared_paths: tuple[tuple[str, ...], ...]) -> tuple[tuple[str, ...], ...]:
        """Return root plus every declared namespace and required ancestor."""
        paths = {()}
        for path in declared_paths:
            paths.update(path[:depth] for depth in range(1, len(path) + 1))
        return tuple(sorted(paths, key=lambda item: (len(item), item)))

    def _namespace_owner_path(self, module_name: str, namespace: tuple[str, ...]) -> str:
        return ".".join((module_name, *namespace)) if namespace else module_name

    def _export_owner_path(
        self,
        module_name: str,
        namespace: tuple[str, ...],
        python_name: str,
    ) -> str:
        return ".".join((module_name, *namespace, python_name))

    def _symbol_name(self, namespace: tuple[str, ...], local_name: str) -> str:
        """Return the readable generated symbol stem implied by one export path."""
        return "_".join((*namespace, local_name)).casefold()

    def _value_role(self, owner_path: str) -> str:
        """Return the symbolic value role for one transfer owner."""
        return f"{owner_path}:value"

    def _native_slot_role(
        self,
        native_slot: NativeCallSlotPolicy,
        results: tuple[ResultPolicy, ...],
    ) -> str:
        """Return the symbolic role for one native-call slot."""
        if native_slot.source_kind == "literal":
            return f"{native_slot.owner_path}:literal"
        public_result = self._public_result_for_slot(native_slot, results)
        if public_result is not None:
            return f"{public_result.owner_path}:native-result"
        if native_slot.source_kind == "result":
            return f"{native_slot.owner_path}:native-result"
        return self._value_role(native_slot.owner_path)

    def _public_result_for_slot(
        self,
        native_slot: NativeCallSlotPolicy,
        results: tuple[ResultPolicy, ...],
    ) -> ResultPolicy | None:
        """Return the Python-visible hidden result carried by one native slot."""
        if native_slot.source_kind != "result":
            return None
        return next(
            (
                result
                for result in results
                if result.source_kind == "hidden_output" and result.owner_path == native_slot.owner_path
            ),
            None,
        )
