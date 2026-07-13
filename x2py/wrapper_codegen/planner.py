"""Hierarchical wrapper-plan construction from completed semantic policy."""

from __future__ import annotations

from collections import Counter, defaultdict

from x2py.semantics import models
from x2py.semantics.wrapper_policy import (
    ArgumentHandoffMode,
    ArrayHandoffPolicy,
    ModuleGetterAction,
    ModuleVariablePolicy,
    ArgumentPolicy,
    FunctionWrapperPolicy,
    LifecyclePolicy,
    NativeCallSlotPolicy,
    NativeStatusErrorPolicy,
    ResultPolicy,
    WritebackPhase,
    completed_module_variable_policy,
    completed_function_wrapper_policy,
)
from x2py.semantics.wrapper_exports import PythonExportPolicy
from x2py.semantics.ownership import SetterAction
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
    ResultPlan,
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
        return ModulePlan(
            owner_path=module.name,
            binding=BindingModulePlan(module.name),
            bridge=BridgeModulePlan(module.name),
            namespaces=tuple(
                NamespacePlan(
                    owner_path=self._namespace_owner_path(module.name, path),
                    python_path=path,
                    functions=tuple(functions[path]),
                    variables=tuple(variables[path]),
                )
                for path in namespace_paths
            ),
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
                export.name,
                policy.hold_gil,
                self._status_error_plan(policy.status_error, native_call_slots),
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

    def _visit_ArgumentPolicy(
        self,
        policy: ArgumentPolicy,
        *,
        native_slot: NativeCallSlotPlan,
    ) -> ArgumentTransferPlan:
        """Return one transfer whose backend views share one handoff role."""
        role = self._value_role(policy.owner_path)
        length_role = (
            f"{policy.owner_path}:length" if policy.handoff_mode is ArgumentHandoffMode.CHARACTER_BUFFER else None
        )
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
            binding=BindingArgumentPlan(
                python_name=policy.python_name,
                python_action=policy.python_barrier_action,
                codegen_action=policy.codegen_action,
                handoff_role=role,
                optional_mode=policy.optional_mode,
                nullable=policy.nullable,
                writable=policy.writable,
                descriptor_boundary=policy.descriptor_boundary,
                length_handoff_role=length_role,
            ),
            bridge=BridgeArgumentPlan(
                native_name=policy.native_name,
                native_action=policy.native_barrier_action,
                codegen_action=policy.codegen_action,
                handoff_mode=policy.handoff_mode,
                data_action=policy.bridge_data_action,
                copy_reason=policy.bridge_copy_reason,
                abi_position=native_slot.native_position,
                handoff_role=role,
                optional_mode=policy.optional_mode,
                presence_role=f"{policy.owner_path}:present" if policy.descriptor_boundary else None,
                length_handoff_role=length_role,
            ),
            native_call_slot=native_slot,
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
            array=(native_slot.array if native_slot is not None else self._array_plan(policy.array, policy.owner_path)),
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
        )

    def _native_slot_plan(self, slot: NativeCallSlotPolicy, role: str) -> NativeCallSlotPlan:
        """Return one shared ABI slot without selecting backend behavior."""
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
            array=self._array_plan(slot.array, slot.owner_path),
        )

    # Ordinary-array planning.
    def _array_plan(
        self,
        policy: ArrayHandoffPolicy | None,
        owner_path: str,
    ) -> ArrayHandoffPlan | None:
        """Mechanically add ABI role names to completed array facts."""
        if policy is None:
            return None
        abi_rank = self._array_abi_rank(policy)
        return ArrayHandoffPlan(
            rank=policy.rank,
            shape=policy.shape,
            axes=policy.axes,
            order=policy.order,
            contiguous=policy.contiguous,
            itemsize=policy.itemsize,
            category=policy.category,
            data_role=self._value_role(owner_path),
            extent_roles=tuple(f"{owner_path}:extent:{axis}" for axis in range(abi_rank)),
            extent_reference_roles=self._array_extent_reference_roles(owner_path, policy.extent_references),
            upper_bound_roles=self._array_layout_roles(owner_path, abi_rank, policy.contiguous, "upper-bound"),
            stride_roles=self._array_layout_roles(owner_path, abi_rank, policy.contiguous, "stride"),
            runtime_rank_role=self._array_runtime_rank_role(policy, owner_path),
            itemsize_role=self._array_itemsize_role(policy, owner_path),
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
        roles.extend(self._native_result_roles(native_call_slots))
        roles.extend(self._direct_result_roles(results))
        return tuple(dict.fromkeys(roles))

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
