"""Hierarchical wrapper-plan construction from completed semantic policy."""

from __future__ import annotations

from collections import Counter, defaultdict

from x2py.semantics import models
from x2py.semantics.wrapper_policy import (
    ModuleGetterAction,
    ModuleVariablePolicy,
    ArgumentPolicy,
    FunctionWrapperPolicy,
    LifecyclePolicy,
    NativeCallSlotPolicy,
    ResultPolicy,
    WritebackPhase,
    completed_module_variable_policy,
    completed_function_wrapper_policy,
)
from x2py.semantics.wrapper_exports import PythonExportPolicy
from x2py.semantics.ownership import SetterAction
from x2py.wrapper_codegen.plan import (
    ArgumentTransferPlan,
    BindingArgumentPlan,
    BindingFunctionPlan,
    BindingLifecyclePlan,
    BindingModulePlan,
    BindingModuleVariablePlan,
    BindingResultPlan,
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
    "Int32": DatatypeFamily.INTEGER,
    "Float32": DatatypeFamily.REAL,
    "Float64": DatatypeFamily.REAL,
    "Complex64": DatatypeFamily.COMPLEX,
    "Complex128": DatatypeFamily.COMPLEX,
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
        arguments = self._argument_plans(policy)
        result = self._result_plan(policy)
        return FunctionPlan(
            owner_path=self._export_owner_path(module_name, export.namespace, export.name),
            symbol_name=export.name.casefold(),
            binding=BindingFunctionPlan(export.name, policy.hold_gil),
            bridge=BridgeFunctionPlan(
                policy.native_name,
                policy.external,
                policy.native_module,
                policy.native_is_subroutine,
            ),
            arguments=arguments,
            result=result,
            native_call_slots=tuple(
                self._native_slot_plan(slot, self._native_slot_role(slot, result)) for slot in policy.native_call_slots
            ),
            available_roles=self._available_roles(arguments, result),
            writeback_actions=tuple(self.visit(action) for action in policy.writeback_actions),
            cleanup_actions=tuple(self.visit(action) for action in policy.cleanup_actions),
            release_actions=tuple(self.visit(action) for action in policy.release_actions),
        )

    def _argument_plans(self, policy: FunctionWrapperPolicy) -> tuple[ArgumentTransferPlan, ...]:
        """Return declared transfers wired to completed native slots."""
        return tuple(
            self.visit(argument, native_slot=self._native_slot(policy, argument)) for argument in policy.arguments
        )

    def _result_plan(self, policy: FunctionWrapperPolicy) -> ResultPlan | None:
        """Return one completed result plan when the function has a result."""
        if policy.result is None:
            return None
        return self.visit(policy.result, native_slot=self._result_native_slot(policy))

    def _visit_ArgumentPolicy(
        self,
        policy: ArgumentPolicy,
        *,
        native_slot: NativeCallSlotPolicy,
    ) -> ArgumentTransferPlan:
        """Return one transfer whose backend views share one handoff role."""
        role = self._value_role(policy.owner_path)
        return ArgumentTransferPlan(
            owner_path=policy.owner_path,
            python_position=policy.python_position,
            native_position=policy.native_position,
            semantic_type_name=policy.semantic_type_name,
            datatype_family=self._datatype_family(policy.semantic_type_name),
            binding=BindingArgumentPlan(
                policy.python_name,
                policy.python_barrier_action,
                role,
                policy.optional_mode,
                policy.nullable,
                policy.descriptor_boundary,
            ),
            bridge=BridgeArgumentPlan(
                policy.native_name,
                policy.native_barrier_action,
                native_slot.native_position,
                role,
                policy.optional_mode,
                f"{policy.owner_path}:present" if policy.descriptor_boundary else None,
            ),
            native_call_slot=self._native_slot_plan(native_slot, role),
        )

    def _visit_LifecyclePolicy(
        self,
        policy: LifecyclePolicy,
    ) -> LifecycleActionPlan:
        """Return one binding-owned writeback plan."""
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
            binding=binding,
            bridge=bridge,
        )

    def _visit_ResultPolicy(
        self,
        policy: ResultPolicy,
        *,
        native_slot: NativeCallSlotPolicy | None,
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
            binding=BindingResultPlan(
                policy.codegen_action,
                policy.python_barrier_action,
                f"{policy.owner_path}:python-result",
            ),
            bridge=BridgeResultPlan(
                policy.codegen_action,
                policy.native_barrier_action,
                native_role,
                policy.native_name,
                policy.native_position,
            ),
            native_call_slot=self._native_slot_plan(native_slot, native_role) if native_slot is not None else None,
        )

    def _native_slot_plan(self, slot: NativeCallSlotPolicy, role: str) -> NativeCallSlotPlan:
        """Return one native-call slot without selecting backend behavior."""
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
            literal_type=slot.literal_type,
            literal_value=slot.literal_value,
            result_position=slot.result_position,
        )

    def _native_slot(
        self,
        function_policy: FunctionWrapperPolicy,
        argument_policy: ArgumentPolicy,
    ) -> NativeCallSlotPolicy:
        """Return the completed native-call slot for one argument policy."""
        for slot in function_policy.native_call_slots:
            if slot.owner_path == argument_policy.owner_path:
                return slot
        raise ValueError(f"{argument_policy.owner_path!r} is missing a completed native-call slot")

    def _result_native_slot(
        self,
        function_policy: FunctionWrapperPolicy,
    ) -> NativeCallSlotPolicy | None:
        """Return the completed slot for one hidden result, if any."""
        if function_policy.result is None or function_policy.result.source_kind != "hidden_output":
            return None
        for slot in function_policy.native_call_slots:
            if slot.owner_path == function_policy.result.owner_path:
                return slot
        raise ValueError(f"{function_policy.result.owner_path!r} is missing a completed native-call result slot")

    def _available_roles(
        self,
        arguments: tuple[ArgumentTransferPlan, ...],
        result: ResultPlan | None,
    ) -> tuple[str, ...]:
        """Return symbolic roles available after the native call."""
        roles = [argument.binding.handoff_role for argument in arguments]
        if result is not None:
            roles.append(result.bridge.native_result_role)
        return tuple(roles)

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
        result: ResultPlan | None,
    ) -> str:
        """Return the symbolic role for one native-call slot."""
        if native_slot.source_kind == "literal":
            return f"{native_slot.owner_path}:literal"
        if native_slot.source_kind == "result":
            if result is None or result.native_call_slot is None:
                raise ValueError(f"{native_slot.owner_path!r} result slot has no result plan")
            return result.bridge.native_result_role
        return self._value_role(native_slot.owner_path)
