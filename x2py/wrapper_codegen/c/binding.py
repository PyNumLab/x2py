"""Direct recursive C binding generation from shared wrapper plans."""

from __future__ import annotations

from dataclasses import dataclass

from x2py.semantics.ownership import (
    CodegenAction,
    NativeBarrierAction,
    PythonBarrierAction,
    SetterAction,
)
from x2py.semantics.wrapper_policy import (
    ModuleGetterAction,
    OptionalMode,
    WritebackPhase,
)
from x2py.wrapper_codegen.nodes import (
    CDeclaration,
    CExpressionStatement,
    CFunction,
    CFunctionPrototype,
    CHeader,
    CIf,
    CInclude,
    CMacroDefinition,
    CMethodDefEntry,
    CMethodDefTable,
    CModule,
    CModuleDef,
    CModulePropertyEntry,
    CModulePropertySupport,
    CParameter,
    CReturn,
    CodeExpression,
)
from x2py.wrapper_codegen.plan import (
    ArgumentTransferPlan,
    DatatypeFamily,
    FunctionPlan,
    LifecycleActionPlan,
    ModulePlan,
    ModuleVariablePlan,
    NamespacePlan,
    ResultPlan,
)
from x2py.wrapper_codegen.primitive_scalar_types import PrimitiveScalarTypeRegistry
from x2py.wrapper_codegen.visitor import ClassVisitor


@dataclass
class _CArgumentNames:
    object_name: str
    value_name: str
    nullable_name: str
    present_name: str


@dataclass
class _CFunctionContext:
    arguments: dict[str, _CArgumentNames]
    result_name: str | None
    python_result_name: str | None


class CBindingGenerator(ClassVisitor):
    """Recursively lower binding plan views directly into C syntax nodes."""

    def require_supported(self, plan: ModulePlan) -> None:
        """Reject unsupported C ABI actions and scalar types."""
        for function in self._functions(plan):
            for argument in function.arguments:
                if argument.binding.python_action is not PythonBarrierAction.SCALAR_VALUE:
                    raise ValueError(
                        f"Unsupported C argument action for {argument.owner_path!r}: {argument.binding.python_action!r}"
                    )
                PrimitiveScalarTypeRegistry.type_for(argument.semantic_type_name)
            if function.result is not None:
                PrimitiveScalarTypeRegistry.type_for(function.result.semantic_type_name)
            for action in function.writeback_actions:
                if action.phase is not WritebackPhase.COPY_OUT or action.binding is None:
                    continue
                PrimitiveScalarTypeRegistry.type_for(action.binding.semantic_type_name)
        for variable in self._variables(plan):
            PrimitiveScalarTypeRegistry.type_for(variable.semantic_type_name)

    def _visit_ModulePlan(self, plan: ModulePlan) -> tuple[CModule, CHeader]:
        """Return a complete C module and header from one shared plan."""
        functions = tuple(function for namespace in plan.namespaces for function in self.visit(namespace))
        needs_runtime = self.requires_runtime_support(plan)
        needs_free = self._module_needs_snapshot_allocator(plan)
        c_module = CModule(
            name=f"{plan.binding.owner_path}_wrapper",
            defines=self._module_defines(needs_runtime),
            includes=self._module_includes(plan, needs_runtime, needs_free),
            declarations=self._module_declarations(plan),
            functions=(
                *self._module_allocator_functions(needs_free),
                *functions,
                self._module_init(plan, needs_runtime),
            ),
        )
        c_header = CHeader(
            guard=f"{plan.binding.owner_path.upper()}_WRAPPER_H",
            includes=(CInclude("Python.h"),),
            prototypes=tuple(self._binding_prototype(function) for function in self._functions(plan)),
        )
        return c_module, c_header

    def _visit_NamespacePlan(self, plan: NamespacePlan) -> tuple[CFunction, ...]:
        """Return binding functions directly owned by one Python namespace."""
        return (
            *(self.visit(function) for function in plan.functions),
            *(function for variable in plan.variables for function in self.visit(variable)),
        )

    def requires_runtime_support(self, plan: ModulePlan) -> bool:
        """Return whether module lowering consumes NumPy/runtime helpers."""
        return bool(tuple(self._variables(plan))) or any(
            function.arguments or function.result is not None for function in self._functions(plan)
        )

    def _module_needs_snapshot_allocator(self, plan: ModulePlan) -> bool:
        """Return whether nullable module snapshots need the shared allocator."""
        return any(
            variable.binding.getter_action is ModuleGetterAction.NULLABLE_SNAPSHOT for variable in self._variables(plan)
        )

    def _module_defines(self, needs_runtime: bool) -> tuple[CMacroDefinition, ...]:
        """Return compile-time definitions selected by assembled module needs."""
        if not needs_runtime:
            return ()
        return (CMacroDefinition("PY_ARRAY_UNIQUE_SYMBOL", "CWRAPPER_ARRAY_API"),)

    def _module_includes(
        self,
        plan: ModulePlan,
        needs_runtime: bool,
        needs_free: bool,
    ) -> tuple[CInclude, ...]:
        """Return dependency-closed includes for one assembled C module."""
        return (
            CInclude("Python.h"),
            CInclude("stdint.h"),
            CInclude("stdbool.h"),
            CInclude("complex.h"),
            *((CInclude("stdlib.h"),) if needs_free else ()),
            *self._module_runtime_includes(needs_runtime),
            CInclude(f"{plan.binding.owner_path}_wrapper.h", system=False),
        )

    def _module_runtime_includes(self, required: bool) -> tuple[CInclude, ...]:
        """Return NumPy/runtime includes when generated nodes consume them."""
        if not required:
            return ()
        return (
            CInclude("x2py_runtime/numpy_version.h", system=False),
            CInclude("numpy/arrayobject.h"),
            CInclude("x2py_runtime/python_runtime.h", system=False),
        )

    def _module_declarations(
        self,
        plan: ModulePlan,
    ) -> tuple[
        CDeclaration | CFunctionPrototype | CMethodDefTable | CModuleDef | CModulePropertySupport,
        ...,
    ]:
        """Return ordered bridge, helper, table, and module declarations."""
        property_support = tuple(
            support
            for namespace in plan.namespaces
            if (support := self._module_property_support(plan, namespace)) is not None
        )
        return (
            *(self._bridge_prototype(function) for function in self._functions(plan)),
            *(
                prototype
                for variable in self._variables(plan)
                for prototype in self._module_variable_bridge_prototypes(variable)
            ),
            *(
                prototype
                for variable in self._variables(plan)
                for prototype in self._module_variable_helper_prototypes(variable)
            ),
            *(self._method_table(plan, namespace) for namespace in plan.namespaces),
            *(self._module_def(plan, namespace) for namespace in plan.namespaces),
            *property_support,
        )

    def _module_allocator_functions(self, required: bool) -> tuple[CFunction, ...]:
        """Return the snapshot allocator exported to the Fortran bridge."""
        if not required:
            return ()
        return (
            CFunction(
                "x2py_malloc",
                "void *",
                parameters=(CParameter("size", "size_t"),),
                body=(
                    CDeclaration(
                        "fail_alloc",
                        "const char *",
                        CodeExpression('getenv("X2PY_WRAPPER_FAIL_ALLOC")'),
                    ),
                    CIf(
                        CodeExpression("fail_alloc != NULL && fail_alloc[0] != '\\0' && fail_alloc[0] != '0'"),
                        body=(CReturn(CodeExpression("NULL")),),
                    ),
                    CReturn(CodeExpression("malloc(size == 0 ? 1 : size)")),
                ),
            ),
        )

    def _visit_ModuleVariablePlan(self, plan: ModuleVariablePlan) -> tuple[CFunction, ...]:
        """Lower binding-owned getter and setter actions into C functions."""
        return (
            *self._lower_module_getter(plan),
            *self._lower_module_setter(plan),
        )

    def _lower_module_getter(self, plan: ModuleVariablePlan) -> tuple[CFunction, ...]:
        """Dispatch one completed Python getter action explicitly."""
        action = plan.binding.getter_action
        match action:
            case ModuleGetterAction.CONSTANT_VALUE:
                return self._lower_module_getter_constant_value(plan)
            case ModuleGetterAction.DIRECT_VALUE:
                return self._lower_module_getter_direct_value(plan)
            case ModuleGetterAction.NULLABLE_SNAPSHOT:
                return self._lower_module_getter_nullable_snapshot(plan)
        raise ValueError(f"Unsupported C module getter action for {plan.owner_path!r}: {action!r}")

    def _lower_module_getter_constant_value(self, _plan: ModuleVariablePlan) -> tuple[CFunction, ...]:
        """Constants are materialized in the module dictionary at initialization."""
        return ()

    def _lower_module_getter_direct_value(self, plan: ModuleVariablePlan) -> tuple[CFunction, ...]:
        """Return a copied Python scalar from one native getter call."""
        scalar_type = PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name)
        return (
            CFunction(
                self._module_getter_name(plan),
                "PyObject *",
                storage="static",
                body=(
                    CDeclaration(
                        "value",
                        scalar_type.c_spelling,
                        CodeExpression(f"{self._module_bridge_getter_name(plan)}()"),
                    ),
                    CDeclaration(
                        "result",
                        "PyObject *",
                        CodeExpression(f"{scalar_type.python_module_result_converter}(&value)"),
                    ),
                    CReturn(CodeExpression("result")),
                ),
            ),
        )

    def _lower_module_getter_nullable_snapshot(self, plan: ModuleVariablePlan) -> tuple[CFunction, ...]:
        """Return None or a detached Python copy from a nullable native snapshot."""
        scalar_type = PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name)
        return (
            CFunction(
                self._module_getter_name(plan),
                "PyObject *",
                storage="static",
                body=(
                    CDeclaration(
                        "data",
                        "void *",
                        CodeExpression(f"{self._module_bridge_getter_name(plan)}()"),
                    ),
                    CIf(
                        CodeExpression("data == NULL"),
                        body=(CExpressionStatement(CodeExpression("Py_RETURN_NONE")),),
                    ),
                    CDeclaration(
                        "value",
                        scalar_type.c_spelling,
                        CodeExpression(f"*({scalar_type.c_spelling} *)data"),
                    ),
                    CDeclaration(
                        "result",
                        "PyObject *",
                        CodeExpression(f"{scalar_type.python_module_result_converter}(&value)"),
                    ),
                    CExpressionStatement(CodeExpression("free(data)")),
                    CReturn(CodeExpression("result")),
                ),
            ),
        )

    def _lower_module_setter(self, plan: ModuleVariablePlan) -> tuple[CFunction, ...]:
        """Dispatch one completed Python setter action explicitly."""
        action = plan.binding.setter_action
        match action:
            case SetterAction.WRITE_THROUGH:
                return self._lower_module_setter_write_through(plan)
            case SetterAction.REJECT_REPLACEMENT:
                return self._lower_module_setter_reject_replacement(plan)
            case SetterAction.OMIT:
                return self._lower_module_setter_omit(plan)
        raise ValueError(f"Unsupported C module setter action for {plan.owner_path!r}: {action!r}")

    def _lower_module_setter_write_through(self, plan: ModuleVariablePlan) -> tuple[CFunction, ...]:
        """Return a Python-to-native scalar write-through helper."""
        scalar_type = PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name)
        return (
            CFunction(
                self._module_setter_name(plan),
                "int",
                parameters=(CParameter("value_obj", "PyObject *"),),
                storage="static",
                body=(
                    self._module_setter_type_check(plan, scalar_type),
                    CDeclaration(
                        "value",
                        scalar_type.c_spelling,
                        CodeExpression(f"{scalar_type.python_input_converter}(value_obj)"),
                    ),
                    CExpressionStatement(CodeExpression("if (PyErr_Occurred()) return -1")),
                    CExpressionStatement(CodeExpression(f"{self._module_bridge_setter_name(plan)}(value)")),
                    CReturn(CodeExpression("0")),
                ),
            ),
        )

    def _lower_module_setter_reject_replacement(self, _plan: ModuleVariablePlan) -> tuple[CFunction, ...]:
        """Read-only descriptor rejection is emitted by module attribute routing."""
        return ()

    def _lower_module_setter_omit(self, _plan: ModuleVariablePlan) -> tuple[CFunction, ...]:
        """Constants use ordinary Python module-dictionary rebinding."""
        return ()

    def _module_setter_type_check(self, plan, scalar_type) -> CExpressionStatement:
        return CExpressionStatement(
            CodeExpression(
                f"if (!{scalar_type.python_input_check.format(object_name='value_obj')}) {{ "
                f'PyErr_Format(PyExc_TypeError, "Expected an argument of type '
                f"{scalar_type.python_type_name} for module variable {plan.binding.python_names[0]}. "
                "Received <class '%s'>\", Py_TYPE(value_obj)->tp_name); return -1; }"
            )
        )

    def _visit_FunctionPlan(self, plan: FunctionPlan) -> CFunction:
        """Recursively assemble one complete CPython binding function."""
        context = self._function_context(plan)
        argument_nodes = tuple(
            node
            for argument in sorted(plan.arguments, key=lambda item: item.python_position)
            for node in self.visit(argument, context=context)
        )
        output_nodes = self._output_nodes(plan, context)
        return CFunction(
            name=self._binding_function_name(plan),
            return_type="PyObject *",
            parameters=self._binding_parameters(),
            storage="static",
            body=(
                self._keyword_declaration(plan),
                *(node for node in argument_nodes if isinstance(node, CDeclaration)),
                *(self._result_declaration(plan, context)),
                self._parse_statement(plan, context),
                *(node for node in argument_nodes if not isinstance(node, CDeclaration)),
                *output_nodes,
            ),
        )

    def _visit_ArgumentTransferPlan(
        self,
        plan: ArgumentTransferPlan,
        *,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf, ...]:
        """Lower one input through its completed optional mode."""
        return self._lower_argument(plan, context)

    def _lower_argument(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf, ...]:
        """Dispatch one completed binding optional mode explicitly."""
        mode = plan.binding.optional_mode
        match mode:
            case OptionalMode.REQUIRED:
                return self._lower_argument_required(plan, context)
            case OptionalMode.NULLABLE_VALUE:
                return self._lower_argument_nullable_value(plan, context)
            case OptionalMode.DESCRIPTOR:
                return self._lower_argument_descriptor(plan, context)
        raise ValueError(f"Unsupported C argument optional mode for {plan.owner_path!r}: {mode!r}")

    def _lower_argument_required(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement, ...]:
        """Return declarations and conversion statements for one scalar input."""
        scalar_type = PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name)
        if scalar_type.python_input_converter is None or scalar_type.python_input_check is None:
            raise ValueError(f"Unsupported scalar input type {plan.semantic_type_name!r}")
        names = context.arguments[plan.owner_path]
        return (
            CDeclaration(names.object_name, "PyObject *"),
            CDeclaration(names.value_name, scalar_type.c_spelling),
            CExpressionStatement(
                CodeExpression(
                    f"if (!{scalar_type.python_input_check.format(object_name=names.object_name)}) {{ "
                    f'PyErr_Format(PyExc_TypeError, "Expected an argument of type '
                    f"{scalar_type.python_type_name} for argument {plan.binding.python_name}. "
                    f"Received <class '%s'>\", Py_TYPE({names.object_name})->tp_name); return NULL; }}"
                )
            ),
            CExpressionStatement(
                CodeExpression(f"{names.value_name} = {scalar_type.python_input_converter}({names.object_name})")
            ),
            CExpressionStatement(CodeExpression("if (PyErr_Occurred()) return NULL")),
        )

    def _lower_argument_nullable_value(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf, ...]:
        """Return omitted-or-value conversion nodes for an optional scalar."""
        scalar_type = PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name)
        names = context.arguments[plan.owner_path]
        return (
            CDeclaration(names.object_name, "PyObject *", CodeExpression("Py_None")),
            CDeclaration(names.value_name, scalar_type.c_spelling),
            CDeclaration(names.nullable_name, "void *", CodeExpression("NULL")),
            CIf(
                CodeExpression(f"{names.object_name} != Py_None"),
                body=(
                    self._type_check_statement(plan, names.object_name, scalar_type),
                    self._conversion_statement(names, scalar_type),
                    CExpressionStatement(CodeExpression("if (PyErr_Occurred()) return NULL")),
                    CExpressionStatement(CodeExpression(f"{names.nullable_name} = &{names.value_name}")),
                ),
            ),
        )

    def _lower_argument_descriptor(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf, ...]:
        """Return distinct omitted, explicit-none, and concrete descriptor states."""
        scalar_type = PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name)
        names = context.arguments[plan.owner_path]
        return (
            CDeclaration(names.object_name, "PyObject *", CodeExpression("NULL")),
            CDeclaration(names.value_name, scalar_type.c_spelling),
            CDeclaration(names.nullable_name, "void *", CodeExpression("NULL")),
            CDeclaration(names.present_name, "void *", CodeExpression("NULL")),
            CIf(
                CodeExpression(f"{names.object_name} != NULL"),
                body=(CExpressionStatement(CodeExpression(f"{names.present_name} = &{names.value_name}")),),
            ),
            CIf(
                CodeExpression(f"({names.object_name} != NULL) && ({names.object_name} != Py_None)"),
                body=(
                    self._type_check_statement(plan, names.object_name, scalar_type),
                    self._conversion_statement(names, scalar_type),
                    CExpressionStatement(CodeExpression("if (PyErr_Occurred()) return NULL")),
                    CExpressionStatement(CodeExpression(f"{names.nullable_name} = &{names.value_name}")),
                ),
            ),
        )

    def _type_check_statement(self, plan, object_name, scalar_type) -> CExpressionStatement:
        """Return one scalar type check with the established error surface."""
        return CExpressionStatement(
            CodeExpression(
                f"if (!{scalar_type.python_input_check.format(object_name=object_name)}) {{ "
                f'PyErr_Format(PyExc_TypeError, "Expected an argument of type '
                f"{scalar_type.python_type_name} for argument {plan.binding.python_name}. "
                f"Received <class '%s'>\", Py_TYPE({object_name})->tp_name); return NULL; }}"
            )
        )

    def _conversion_statement(self, names: _CArgumentNames, scalar_type) -> CExpressionStatement:
        """Return one Python-to-native scalar conversion statement."""
        return CExpressionStatement(
            CodeExpression(f"{names.value_name} = {scalar_type.python_input_converter}({names.object_name})")
        )

    def _visit_ResultPlan(
        self,
        plan: ResultPlan,
        *,
        function: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[CExpressionStatement | CDeclaration | CReturn, ...]:
        """Lower one result through its completed binding action."""
        return self._lower_result(plan, function, context)

    def _lower_result(
        self,
        plan: ResultPlan,
        function: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[CExpressionStatement | CDeclaration | CReturn, ...]:
        """Dispatch one completed binding result action explicitly."""
        action = plan.binding.codegen_action
        match action:
            case CodegenAction.DIRECT_VALUE:
                return self._lower_result_direct_value(plan, function, context)
            case CodegenAction.HIDDEN_OUTPUT:
                return self._lower_result_hidden_output(plan, function, context)
        raise ValueError(f"Unsupported C result action for {plan.owner_path!r}: {action!r}")

    def _lower_result_direct_value(
        self,
        plan: ResultPlan,
        function: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[CExpressionStatement | CDeclaration | CReturn, ...]:
        return self._lower_result_value(plan, function, context)

    def _lower_result_hidden_output(
        self,
        plan: ResultPlan,
        function: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[CExpressionStatement | CDeclaration | CReturn, ...]:
        return self._lower_result_value(plan, function, context)

    def _lower_result_value(
        self,
        plan: ResultPlan,
        function: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[CExpressionStatement | CDeclaration | CReturn, ...]:
        """Return the bridge call and Python scalar result projection."""
        scalar_type = PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name)
        if (
            scalar_type.python_result_converter is None
            or context.result_name is None
            or context.python_result_name is None
        ):
            raise ValueError(f"Unsupported scalar result type {plan.semantic_type_name!r}")
        call = self._bridge_call(function, context)
        call_statement = (
            CExpressionStatement(CodeExpression(f"{context.result_name} = {call}"))
            if plan.source_kind == "direct_return"
            else CExpressionStatement(CodeExpression(call))
        )
        return (
            call_statement,
            CDeclaration(
                context.python_result_name,
                "PyObject *",
                CodeExpression(f"{scalar_type.python_result_converter}(&{context.result_name})"),
            ),
            CExpressionStatement(CodeExpression(f"if ({context.python_result_name} == NULL) return NULL")),
            CReturn(CodeExpression(context.python_result_name)),
        )

    def _output_nodes(
        self,
        plan: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[CExpressionStatement | CDeclaration | CReturn, ...]:
        """Return the native call and completed Python output projection."""
        if plan.result is not None:
            return self.visit(plan.result, function=plan, context=context)
        if plan.writeback_actions:
            return self._writeback_nodes(plan, context)
        return (
            CExpressionStatement(CodeExpression(self._bridge_call(plan, context))),
            CExpressionStatement(CodeExpression("Py_RETURN_NONE")),
        )

    def _writeback_nodes(
        self,
        plan: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[CExpressionStatement | CDeclaration | CReturn, ...]:
        """Return scalar replacement conversion after the native call."""
        ordered = sorted(
            (
                action
                for action in plan.writeback_actions
                if action.phase is WritebackPhase.COPY_OUT and action.binding is not None
            ),
            key=lambda item: item.binding.result_position,
        )
        if len(ordered) != 1:
            raise ValueError(f"{plan.owner_path!r} requires exactly one scalar writeback result")
        action = ordered[0]
        return self._lower_writeback(plan, action, context)

    def _lower_writeback(
        self,
        plan: FunctionPlan,
        action: LifecycleActionPlan,
        context: _CFunctionContext,
    ) -> tuple[CExpressionStatement | CDeclaration | CReturn, ...]:
        """Dispatch one completed binding writeback action explicitly."""
        codegen_action = action.binding.codegen_action
        match codegen_action:
            case CodegenAction.COPY_IN_OUT:
                return self._lower_writeback_copy_in_out(plan, action, context)
            case CodegenAction.IN_PLACE_ARGUMENT:
                return self._lower_writeback_in_place_argument(plan, action, context)
        raise ValueError(f"Unsupported C writeback action for {action.owner_path!r}: {codegen_action!r}")

    def _lower_writeback_copy_in_out(
        self,
        plan: FunctionPlan,
        action: LifecycleActionPlan,
        context: _CFunctionContext,
    ) -> tuple[CExpressionStatement | CDeclaration | CReturn, ...]:
        return self._lower_writeback_value(plan, action, context)

    def _lower_writeback_in_place_argument(
        self,
        plan: FunctionPlan,
        action: LifecycleActionPlan,
        context: _CFunctionContext,
    ) -> tuple[CExpressionStatement | CDeclaration | CReturn, ...]:
        return self._lower_writeback_value(plan, action, context)

    def _lower_writeback_value(
        self,
        plan: FunctionPlan,
        action: LifecycleActionPlan,
        context: _CFunctionContext,
    ) -> tuple[CExpressionStatement | CDeclaration | CReturn, ...]:
        """Return one Python scalar replacement from mutated bridge storage."""
        source = self._argument_for_role(plan, action.source_role)
        names = context.arguments[source.owner_path]
        scalar_type = PrimitiveScalarTypeRegistry.type_for(action.binding.semantic_type_name)
        python_result_name = context.python_result_name or "result_obj"
        return (
            CExpressionStatement(CodeExpression(self._bridge_call(plan, context))),
            CDeclaration(
                python_result_name,
                "PyObject *",
                CodeExpression(f"{scalar_type.python_result_converter}(&{names.value_name})"),
            ),
            CExpressionStatement(CodeExpression(f"if ({python_result_name} == NULL) return NULL")),
            CReturn(CodeExpression(python_result_name)),
        )

    def _argument_for_role(self, plan: FunctionPlan, role: str) -> ArgumentTransferPlan:
        """Return the argument that produced one validated lifecycle role."""
        for argument in plan.arguments:
            if argument.binding.handoff_role == role:
                return argument
        raise ValueError(f"{plan.owner_path!r} has no argument for lifecycle role {role!r}")

    def _function_context(self, plan: FunctionPlan) -> _CFunctionContext:
        arguments = {
            argument.owner_path: _CArgumentNames(
                f"{argument.binding.python_name.lower()}_obj",
                argument.binding.python_name.lower(),
                f"{argument.binding.python_name.lower()}_nullable",
                f"{argument.binding.python_name.lower()}_present",
            )
            for argument in plan.arguments
        }
        if plan.result is None:
            python_result = "result_obj" if plan.writeback_actions else None
            return _CFunctionContext(arguments, None, python_result)
        base = plan.result.bridge.native_name.lower() if plan.result.source_kind == "hidden_output" else "result"
        return _CFunctionContext(arguments, base, "result_obj")

    def _keyword_declaration(self, plan: FunctionPlan) -> CDeclaration:
        keywords = ", ".join(
            f'"{argument.binding.python_name}"'
            for argument in sorted(plan.arguments, key=lambda item: item.python_position)
        )
        entries = f"{keywords}, NULL" if keywords else "NULL"
        return CDeclaration("kwlist[]", "static char *", CodeExpression(f"{{{entries}}}"))

    def _parse_statement(self, plan: FunctionPlan, context: _CFunctionContext) -> CExpressionStatement:
        arguments = sorted(plan.arguments, key=lambda item: item.python_position)
        required = [item for item in arguments if item.binding.optional_mode is OptionalMode.REQUIRED]
        optional = [item for item in arguments if item.binding.optional_mode is not OptionalMode.REQUIRED]
        units = "O" * len(required) + ("|" if optional else "") + "O" * len(optional)
        targets = ", ".join(f"&{context.arguments[item.owner_path].object_name}" for item in arguments)
        suffix = f", {targets}" if targets else ""
        return CExpressionStatement(
            CodeExpression(f'if (!PyArg_ParseTupleAndKeywords(args, kwargs, "{units}", kwlist{suffix})) return NULL')
        )

    def _result_declaration(
        self,
        plan: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration, ...]:
        if plan.result is None or context.result_name is None:
            return ()
        scalar_type = PrimitiveScalarTypeRegistry.type_for(plan.result.semantic_type_name)
        return (CDeclaration(context.result_name, scalar_type.c_spelling),)

    def _bridge_call(self, plan: FunctionPlan, context: _CFunctionContext) -> str:
        arguments = []
        for argument in sorted(plan.arguments, key=lambda item: item.bridge.abi_position):
            names = context.arguments[argument.owner_path]
            value = self._bridge_call_argument(argument, names)
            arguments.append(value)
            if argument.bridge.optional_mode is OptionalMode.DESCRIPTOR:
                arguments.append(names.present_name)
        if plan.result is not None and plan.result.source_kind == "hidden_output":
            arguments.append(f"&{context.result_name}")
        return f"{self._bridge_function_name(plan)}({', '.join(arguments)})"

    def _bridge_call_argument(self, plan: ArgumentTransferPlan, names: _CArgumentNames) -> str:
        """Return one binding-to-bridge C argument expression."""
        if plan.bridge.optional_mode is not OptionalMode.REQUIRED:
            return names.nullable_name
        if plan.bridge.native_action is not NativeBarrierAction.PASS_VALUE:
            return f"&{names.value_name}"
        return names.value_name

    def _bridge_prototype(self, plan: FunctionPlan) -> CFunctionPrototype:
        return_type = "void"
        if plan.result is not None and plan.result.source_kind == "direct_return":
            return_type = PrimitiveScalarTypeRegistry.type_for(plan.result.semantic_type_name).c_spelling
        parameters = []
        for argument in sorted(plan.arguments, key=lambda item: item.bridge.abi_position):
            if argument.bridge.optional_mode is OptionalMode.REQUIRED:
                scalar_type = PrimitiveScalarTypeRegistry.type_for(argument.semantic_type_name).c_spelling
                if argument.bridge.native_action is not NativeBarrierAction.PASS_VALUE:
                    scalar_type = f"{scalar_type} *"
            else:
                scalar_type = "void *"
            parameters.append(CParameter(argument.bridge.native_name.lower(), scalar_type))
            if argument.bridge.optional_mode is OptionalMode.DESCRIPTOR:
                parameters.append(CParameter(f"{argument.bridge.native_name.lower()}_present", "void *"))
        if plan.result is not None and plan.result.source_kind == "hidden_output":
            scalar_type = PrimitiveScalarTypeRegistry.type_for(plan.result.semantic_type_name).c_spelling
            parameters.append(CParameter(plan.result.bridge.native_name.lower(), f"{scalar_type} *"))
        return CFunctionPrototype(self._bridge_function_name(plan), return_type, tuple(parameters))

    def _module_variable_bridge_prototypes(
        self,
        plan: ModuleVariablePlan,
    ) -> tuple[CFunctionPrototype, ...]:
        """Return getter/setter ABI declarations selected by the variable plan."""
        prototypes = []
        if plan.bridge.getter_role is not None:
            return_type = (
                "void *"
                if plan.binding.getter_action is ModuleGetterAction.NULLABLE_SNAPSHOT
                else PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name).c_spelling
            )
            prototypes.append(CFunctionPrototype(self._module_bridge_getter_name(plan), return_type))
        if plan.bridge.setter_role is not None:
            scalar_type = PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name).c_spelling
            prototypes.append(
                CFunctionPrototype(
                    self._module_bridge_setter_name(plan),
                    "void",
                    (CParameter("value", scalar_type),),
                )
            )
        return tuple(prototypes)

    def _module_variable_helper_prototypes(
        self,
        plan: ModuleVariablePlan,
    ) -> tuple[CFunctionPrototype, ...]:
        """Declare C helpers before the generated module-type routing code."""
        if plan.binding.getter_action is ModuleGetterAction.CONSTANT_VALUE:
            return ()
        prototypes = [CFunctionPrototype(self._module_getter_name(plan), "PyObject *", storage="static")]
        if plan.binding.setter_action is SetterAction.WRITE_THROUGH:
            prototypes.append(
                CFunctionPrototype(
                    self._module_setter_name(plan),
                    "int",
                    (CParameter("value_obj", "PyObject *"),),
                    "static",
                )
            )
        return tuple(prototypes)

    def _module_property_support(
        self,
        module: ModulePlan,
        namespace: NamespacePlan,
    ) -> CModulePropertySupport | None:
        """Return dynamic module-attribute routing for non-constant variables."""
        entries = tuple(
            CModulePropertyEntry(
                python_name=python_name,
                getter_name=self._module_getter_name(variable),
                setter_name=(
                    self._module_setter_name(variable)
                    if variable.binding.setter_action is SetterAction.WRITE_THROUGH
                    else None
                ),
                reject_replacement=(variable.binding.setter_action is SetterAction.REJECT_REPLACEMENT),
            )
            for variable in namespace.variables
            if variable.binding.getter_action is not ModuleGetterAction.CONSTANT_VALUE
            for python_name in variable.binding.python_names
        )
        if not entries:
            return None
        namespace_symbol = self._namespace_symbol(namespace)
        return CModulePropertySupport(
            name=f"{module.binding.owner_path}_{namespace_symbol}_module_property_setup",
            module_name=self._namespace_module_name(module, namespace),
            entries=entries,
        )

    def _binding_prototype(self, plan: FunctionPlan) -> CFunctionPrototype:
        return CFunctionPrototype(
            self._binding_function_name(plan),
            "PyObject *",
            self._binding_parameters(),
            "static",
        )

    def _method_table(self, module: ModulePlan, namespace: NamespacePlan) -> CMethodDefTable:
        return CMethodDefTable(
            f"{module.binding.owner_path}_{self._namespace_symbol(namespace)}_methods",
            tuple(
                CMethodDefEntry(
                    function.binding.python_name, self._binding_function_name(function), "METH_VARARGS | METH_KEYWORDS"
                )
                for function in namespace.functions
            ),
        )

    def _module_def(self, module: ModulePlan, namespace: NamespacePlan) -> CModuleDef:
        owner = module.binding.owner_path
        symbol = self._namespace_symbol(namespace)
        python_name = self._namespace_module_name(module, namespace)
        return CModuleDef(
            f"{owner}_{symbol}_module",
            python_name,
            f"{python_name} generated wrapper",
            f"{owner}_{symbol}_methods",
        )

    def _module_init(self, plan: ModulePlan, needs_runtime: bool) -> CFunction:
        module_name = plan.binding.owner_path
        root_namespace = self._namespace(plan, ())
        return CFunction(
            f"PyInit_{module_name}",
            "PyMODINIT_FUNC",
            body=(
                *((CExpressionStatement(CodeExpression("import_array()")),) if needs_runtime else ()),
                CDeclaration(
                    "mod",
                    "PyObject *",
                    CodeExpression(f"PyModule_Create(&{module_name}_{self._namespace_symbol(root_namespace)}_module)"),
                ),
                CExpressionStatement(CodeExpression("if (mod == NULL) return NULL")),
                *self._namespace_configuration_nodes(plan, root_namespace, "mod"),
                *(
                    node
                    for namespace in self._ordered_child_namespaces(plan)
                    for node in self._child_namespace_nodes(plan, namespace)
                ),
                CReturn(CodeExpression("mod")),
            ),
        )

    def _ordered_child_namespaces(self, plan: ModulePlan) -> tuple[NamespacePlan, ...]:
        """Return parents before descendants regardless of editable tuple order."""
        return tuple(
            sorted(
                (namespace for namespace in plan.namespaces if namespace.python_path),
                key=lambda namespace: (len(namespace.python_path), namespace.python_path),
            )
        )

    def _child_namespace_nodes(
        self,
        module: ModulePlan,
        namespace: NamespacePlan,
    ) -> tuple[CDeclaration | CExpressionStatement, ...]:
        """Create, attach, and configure one child Python module."""
        object_name = self._namespace_object_name(namespace)
        parent = self._namespace_object_name(self._namespace(module, namespace.python_path[:-1]))
        definition = f"{module.binding.owner_path}_{self._namespace_symbol(namespace)}_module"
        local_name = namespace.python_path[-1]
        return (
            CDeclaration(object_name, "PyObject *", CodeExpression(f"PyModule_Create(&{definition})")),
            CExpressionStatement(CodeExpression(f"if ({object_name} == NULL) {{ Py_DECREF(mod); return NULL; }}")),
            CExpressionStatement(
                CodeExpression(
                    f'if (PyModule_AddObject({parent}, "{local_name}", {object_name}) < 0) '
                    f"{{ Py_DECREF({object_name}); Py_DECREF(mod); return NULL; }}"
                )
            ),
            *self._namespace_configuration_nodes(module, namespace, object_name),
        )

    def _namespace_configuration_nodes(
        self,
        module: ModulePlan,
        namespace: NamespacePlan,
        object_name: str,
    ) -> tuple[CDeclaration | CExpressionStatement, ...]:
        """Initialize properties, native state, and constants in one namespace."""
        property_support = self._module_property_support(module, namespace)
        property_nodes = (
            (
                CExpressionStatement(
                    CodeExpression(
                        f"if ({property_support.name}({object_name}) < 0) {{ Py_DECREF(mod); return NULL; }}"
                    )
                ),
            )
            if property_support is not None
            else ()
        )
        return (
            *property_nodes,
            *self._module_initializer_nodes(namespace),
            *self._module_constant_nodes(namespace, object_name),
        )

    def _module_initializer_nodes(self, namespace: NamespacePlan) -> tuple[CExpressionStatement, ...]:
        """Return import-time native assignments selected by completed policy."""
        return tuple(
            CExpressionStatement(
                CodeExpression(
                    f"{self._module_bridge_setter_name(variable)}("
                    f"{self._module_literal(variable, variable.binding.initializer)})"
                )
            )
            for variable in namespace.variables
            if variable.binding.initializer is not None
        )

    def _module_constant_nodes(
        self,
        namespace: NamespacePlan,
        module_object: str,
    ) -> tuple[CDeclaration | CExpressionStatement, ...]:
        """Materialize scalar constants in the ordinary module dictionary."""
        nodes = []
        index = 0
        for variable in namespace.variables:
            if variable.binding.getter_action is not ModuleGetterAction.CONSTANT_VALUE:
                continue
            scalar_type = PrimitiveScalarTypeRegistry.type_for(variable.semantic_type_name)
            for python_name in variable.binding.python_names:
                value_name = f"constant_{variable.symbol_name}_value_{index}"
                object_name = f"constant_{variable.symbol_name}_object_{index}"
                nodes.extend(
                    (
                        CDeclaration(
                            value_name,
                            scalar_type.c_spelling,
                            CodeExpression(self._module_literal(variable, variable.binding.constant_value)),
                        ),
                        CDeclaration(
                            object_name,
                            "PyObject *",
                            CodeExpression(f"{scalar_type.python_module_result_converter}(&{value_name})"),
                        ),
                        CExpressionStatement(
                            CodeExpression(f"if ({object_name} == NULL) {{ Py_DECREF(mod); return NULL; }}")
                        ),
                        CExpressionStatement(
                            CodeExpression(
                                f'if (PyModule_AddObject({module_object}, "{python_name}", {object_name}) < 0) '
                                f"{{ Py_DECREF({object_name}); Py_DECREF(mod); return NULL; }}"
                            )
                        ),
                    )
                )
                index += 1
        return tuple(nodes)

    def _module_literal(self, plan: ModuleVariablePlan, value: object) -> str:
        """Dispatch one completed datatype family to its C literal spelling."""
        family = plan.datatype_family
        match family:
            case DatatypeFamily.BOOL:
                return self._lower_module_literal_bool(value)
            case DatatypeFamily.INTEGER:
                return self._lower_module_literal_integer(value)
            case DatatypeFamily.REAL:
                return self._lower_module_literal_real(value)
            case DatatypeFamily.COMPLEX:
                return self._lower_module_literal_complex(value)
        raise ValueError(f"Unsupported C module literal family for {plan.owner_path!r}: {family!r}")

    def _lower_module_literal_bool(self, value: object) -> str:
        return "true" if value else "false"

    def _lower_module_literal_integer(self, value: object) -> str:
        return str(value)

    def _lower_module_literal_real(self, value: object) -> str:
        return repr(value)

    def _lower_module_literal_complex(self, value: object) -> str:
        number = complex(value)
        return f"({number.real!r} + {number.imag!r} * I)"

    def _binding_parameters(self) -> tuple[CParameter, ...]:
        return (
            CParameter("self", "PyObject *"),
            CParameter("args", "PyObject *"),
            CParameter("kwargs", "PyObject *"),
        )

    def _binding_function_name(self, plan: FunctionPlan) -> str:
        return f"wrap_{plan.symbol_name}"

    def _bridge_function_name(self, plan: FunctionPlan) -> str:
        return f"bind_c_{plan.symbol_name}"

    def _module_getter_name(self, plan: ModuleVariablePlan) -> str:
        return f"module_get_{plan.symbol_name}"

    def _module_setter_name(self, plan: ModuleVariablePlan) -> str:
        return f"module_set_{plan.symbol_name}"

    def _module_bridge_getter_name(self, plan: ModuleVariablePlan) -> str:
        return f"bind_c_get_{plan.symbol_name}"

    def _module_bridge_setter_name(self, plan: ModuleVariablePlan) -> str:
        return f"bind_c_set_{plan.symbol_name}"

    def _functions(self, plan: ModulePlan) -> tuple[FunctionPlan, ...]:
        return tuple(function for namespace in plan.namespaces for function in namespace.functions)

    def _variables(self, plan: ModulePlan) -> tuple[ModuleVariablePlan, ...]:
        return tuple(variable for namespace in plan.namespaces for variable in namespace.variables)

    def _namespace(self, plan: ModulePlan, python_path: tuple[str, ...]) -> NamespacePlan:
        for namespace in plan.namespaces:
            if namespace.python_path == python_path:
                return namespace
        raise ValueError(f"{plan.owner_path!r} has no namespace {python_path!r}")

    def _namespace_symbol(self, plan: NamespacePlan) -> str:
        return "_".join(plan.python_path).casefold() if plan.python_path else "root"

    def _namespace_object_name(self, plan: NamespacePlan) -> str:
        return f"namespace_{self._namespace_symbol(plan)}" if plan.python_path else "mod"

    def _namespace_module_name(self, module: ModulePlan, namespace: NamespacePlan) -> str:
        return ".".join((module.binding.owner_path, *namespace.python_path))
