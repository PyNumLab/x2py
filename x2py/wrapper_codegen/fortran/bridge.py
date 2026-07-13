"""Direct recursive Fortran bridge generation from shared wrapper plans."""

from __future__ import annotations

from x2py.semantics.ownership import NativeBarrierAction
from x2py.semantics.wrapper_policy import ModuleGetterAction, OptionalMode
from x2py.wrapper_codegen.nodes import (
    CodeExpression,
    FortranAssignment,
    FortranCall,
    FortranDeclaration,
    FortranFunction,
    FortranIf,
    FortranInterface,
    FortranInterfaceProcedure,
    FortranModule,
    FortranParameter,
    FortranPointerAssignment,
    FortranUse,
)
from x2py.wrapper_codegen.plan import (
    ArgumentTransferPlan,
    FunctionPlan,
    ModulePlan,
    ModuleVariablePlan,
    NamespacePlan,
)
from x2py.wrapper_codegen.primitive_scalar_types import PrimitiveScalarTypeRegistry
from x2py.wrapper_codegen.visitor import ClassVisitor


class FortranBridgeGenerator(ClassVisitor):
    """Recursively lower bridge plan views directly into Fortran nodes."""

    def require_supported(self, plan: ModulePlan) -> None:
        """Reject actions without their directly named Fortran lowering method."""
        for function in self._functions(plan):
            self._require_function_supported(function)
        for variable in self._variables(plan):
            self._require_variable_supported(variable)

    def _require_function_supported(self, function: FunctionPlan) -> None:
        """Reject unsupported actions in one planned bridge procedure."""
        supported_native_actions = {
            NativeBarrierAction.PASS_VALUE,
            NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS,
            NativeBarrierAction.PASS_STORAGE_ADDRESS,
        }
        result_action = function.result.bridge.codegen_action if function.result is not None else "none"
        self._require_lowering_method("result", result_action, function.owner_path)
        if self._has_optional_arguments(function) and any(
            slot.source_kind == "literal" for slot in function.native_call_slots
        ):
            raise ValueError(f"{function.owner_path!r} mixes optional scalar arguments with hidden literals")
        for argument in function.arguments:
            if argument.bridge.native_action not in supported_native_actions:
                raise ValueError(
                    f"Unsupported Fortran argument action for {argument.owner_path!r}: "
                    f"{argument.bridge.native_action!r}"
                )
            self._require_lowering_method("argument", argument.bridge.optional_mode, argument.owner_path)
            PrimitiveScalarTypeRegistry.type_for(argument.semantic_type_name)

    def _require_variable_supported(self, variable: ModuleVariablePlan) -> None:
        """Reject unsupported actions in one planned module variable."""
        self._require_lowering_method("module_getter", variable.bridge.getter_action, variable.owner_path)
        self._require_lowering_method("module_setter", variable.binding.setter_action, variable.owner_path)
        if (
            variable.bridge.getter_action is ModuleGetterAction.NULLABLE_SNAPSHOT
            and variable.bridge.descriptor_kind not in {"allocatable", "pointer"}
        ):
            raise ValueError(
                f"Unsupported Fortran module getter descriptor for {variable.owner_path!r}: "
                f"{variable.bridge.descriptor_kind!r}"
            )
        PrimitiveScalarTypeRegistry.type_for(variable.semantic_type_name)

    def _visit_ModulePlan(self, plan: ModulePlan) -> FortranModule:
        """Return one complete Fortran bridge module."""
        return FortranModule(
            name=f"bind_c_{plan.bridge.owner_path}_wrapper",
            uses=(
                FortranUse("iso_c_binding", self._iso_c_symbols()),
                *self._native_module_uses(plan),
            ),
            interfaces=(*self._external_interfaces(plan), *self._module_snapshot_interfaces(plan)),
            procedures=tuple(procedure for namespace in plan.namespaces for procedure in self.visit(namespace)),
        )

    def _visit_NamespacePlan(self, plan: NamespacePlan) -> tuple[FortranFunction, ...]:
        """Return bridge procedures directly owned by one Python namespace."""
        return (
            *(self.visit(function) for function in plan.functions),
            *(procedure for variable in plan.variables for procedure in self.visit(variable)),
        )

    def _visit_FunctionPlan(self, plan: FunctionPlan) -> FortranFunction:
        """Recursively assemble one complete bridge procedure."""
        result_parameters, result_name, result_type = self._call_lowering(
            "result",
            plan.result.bridge.codegen_action if plan.result is not None else "none",
            plan,
        )
        parameters = tuple(
            parameter
            for argument in sorted(plan.arguments, key=lambda item: item.bridge.abi_position)
            for parameter in self.visit(argument)
        )
        parameters = (*parameters, *result_parameters)
        bridge_name = self._bridge_function_name(plan)
        is_subroutine = plan.bridge.native_is_subroutine
        return FortranFunction(
            name=bridge_name,
            parameters=parameters,
            result_name=result_name,
            result_type=result_type,
            bind_name=bridge_name,
            declarations=(*self._external_declarations(plan), *self._optional_declarations(plan)),
            body=(*self._descriptor_initializers(plan), *self._function_body(plan, result_name)),
            is_subroutine=is_subroutine,
        )

    def _lower_result_none(
        self,
        _plan: FunctionPlan,
    ) -> tuple[tuple[FortranParameter, ...], str | None, str | None]:
        """Return the procedure shape of a native subroutine with no projection."""
        return (), None, None

    def _lower_result_direct_value(
        self,
        plan: FunctionPlan,
    ) -> tuple[tuple[FortranParameter, ...], str | None, str | None]:
        """Return the procedure shape of a direct native function result."""
        return (), "result", self._bridge_result_type(plan)

    def _lower_result_hidden_output(
        self,
        plan: FunctionPlan,
    ) -> tuple[tuple[FortranParameter, ...], str | None, str | None]:
        """Return the procedure shape of a hidden native output parameter."""
        return self._hidden_result_parameters(plan), None, None

    def _visit_ModuleVariablePlan(self, plan: ModuleVariablePlan) -> tuple[FortranFunction, ...]:
        """Lower getter and setter actions through their visible naming rule."""
        getter = self._call_lowering("module_getter", plan.bridge.getter_action, plan)
        setter = self._call_lowering("module_setter", plan.binding.setter_action, plan)
        return (*getter, *setter)

    def _lower_module_getter_constant_value(self, _plan: ModuleVariablePlan) -> tuple[FortranFunction, ...]:
        """Constants are materialized directly by the Python binding."""
        return ()

    def _lower_module_getter_direct_value(self, plan: ModuleVariablePlan) -> tuple[FortranFunction, ...]:
        """Return one direct scalar module-variable getter."""
        scalar_type = PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name)
        name = self._module_bridge_getter_name(plan)
        return (
            FortranFunction(
                name=name,
                result_name="result",
                result_type=scalar_type.fortran_spelling,
                bind_name=name,
                body=(FortranAssignment("result", CodeExpression(self._native_variable_name(plan))),),
            ),
        )

    def _lower_module_getter_nullable_snapshot(
        self,
        plan: ModuleVariablePlan,
    ) -> tuple[FortranFunction, ...]:
        """Return a nullable detached snapshot through C-owned storage."""
        presence = "allocated" if plan.bridge.descriptor_kind == "allocatable" else "associated"
        return self._lower_nullable_module_getter(plan, f"{presence}({self._native_variable_name(plan)})")

    def _lower_nullable_module_getter(
        self,
        plan: ModuleVariablePlan,
        condition: str,
    ) -> tuple[FortranFunction, ...]:
        """Build the shared detached scalar snapshot bridge procedure."""
        scalar_type = PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name)
        name = self._module_bridge_getter_name(plan)
        return (
            FortranFunction(
                name=name,
                result_name="result",
                result_type="type(c_ptr)",
                bind_name=name,
                declarations=(
                    FortranDeclaration("copy", scalar_type.fortran_spelling, ("pointer",)),
                    FortranDeclaration("element", scalar_type.fortran_spelling),
                ),
                body=(
                    FortranIf(
                        CodeExpression(condition),
                        body=(
                            FortranAssignment(
                                "result",
                                CodeExpression("c_malloc(storage_size(element, kind=c_size_t))"),
                            ),
                            FortranIf(
                                CodeExpression("c_associated(result)"),
                                body=(
                                    FortranCall(
                                        "c_f_pointer",
                                        (CodeExpression("result"), CodeExpression("copy")),
                                    ),
                                    FortranAssignment("copy", CodeExpression(self._native_variable_name(plan))),
                                ),
                            ),
                        ),
                        else_body=(FortranAssignment("result", CodeExpression("c_null_ptr")),),
                    ),
                ),
            ),
        )

    def _lower_module_setter_write_through(self, plan: ModuleVariablePlan) -> tuple[FortranFunction, ...]:
        """Return one value-copy native module assignment."""
        scalar_type = PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name)
        name = self._module_bridge_setter_name(plan)
        return (
            FortranFunction(
                name=name,
                parameters=(FortranParameter("value", scalar_type.fortran_spelling, ("value",)),),
                bind_name=name,
                body=(FortranAssignment(self._native_variable_name(plan), CodeExpression("value")),),
                is_subroutine=True,
            ),
        )

    def _lower_module_setter_reject_replacement(self, _plan: ModuleVariablePlan) -> tuple[FortranFunction, ...]:
        """Rejected replacement has no native setter procedure."""
        return ()

    def _lower_module_setter_omit(self, _plan: ModuleVariablePlan) -> tuple[FortranFunction, ...]:
        """Constants have no native setter procedure."""
        return ()

    def _visit_ArgumentTransferPlan(self, plan: ArgumentTransferPlan) -> tuple[FortranParameter, ...]:
        """Lower one argument through the completed optional-mode action."""
        return self._call_lowering("argument", plan.bridge.optional_mode, plan)

    def _lower_argument_required(self, plan: ArgumentTransferPlan) -> tuple[FortranParameter, ...]:
        attributes = ("value",) if plan.bridge.native_action is NativeBarrierAction.PASS_VALUE else ()
        return (self._parameter(plan, attributes),)

    def _lower_argument_nullable_value(self, plan: ArgumentTransferPlan) -> tuple[FortranParameter, ...]:
        """Return one nullable C pointer parameter."""
        name = plan.bridge.native_name.lower()
        return (FortranParameter(f"bound_{name}", "type(c_ptr)", ("value",)),)

    def _lower_argument_descriptor(self, plan: ArgumentTransferPlan) -> tuple[FortranParameter, ...]:
        """Return nullable value and explicit presence pointer parameters."""
        name = plan.bridge.native_name.lower()
        return (
            FortranParameter(f"bound_{name}", "type(c_ptr)", ("value",)),
            FortranParameter(f"bound_{name}_present", "type(c_ptr)", ("value",)),
        )

    def _parameter(self, plan: ArgumentTransferPlan, attributes: tuple[str, ...]) -> FortranParameter:
        scalar_type = PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name)
        return FortranParameter(plan.bridge.native_name.lower(), scalar_type.fortran_spelling, attributes)

    def _function_body(
        self,
        plan: FunctionPlan,
        result_name: str | None,
    ) -> tuple[FortranAssignment | FortranCall | FortranIf, ...]:
        optional = tuple(
            argument
            for argument in sorted(plan.arguments, key=lambda item: item.bridge.abi_position)
            if argument.bridge.optional_mode is not OptionalMode.REQUIRED
        )
        if not optional:
            return (self._native_invocation(plan, frozenset(), result_name),)
        return (self._optional_call_tree(plan, optional, 0, frozenset(), result_name),)

    def _optional_call_tree(
        self,
        plan: FunctionPlan,
        optional: tuple[ArgumentTransferPlan, ...],
        index: int,
        present: frozenset[str],
        result_name: str | None,
    ) -> FortranAssignment | FortranCall | FortranIf:
        """Return an exhaustive native-call tree for optional presence states."""
        if index == len(optional):
            return self._native_invocation(plan, present, result_name)
        argument = optional[index]
        present_roles = present | {argument.owner_path}
        return FortranIf(
            condition=CodeExpression(self._presence_condition(argument)),
            body=(
                *self._present_preparation(argument),
                self._optional_call_tree(plan, optional, index + 1, present_roles, result_name),
            ),
            else_body=(self._optional_call_tree(plan, optional, index + 1, present, result_name),),
        )

    def _native_invocation(
        self,
        plan: FunctionPlan,
        present: frozenset[str],
        result_name: str | None,
    ) -> FortranAssignment | FortranCall:
        arguments = self._native_arguments(plan, present)
        native_name = self._native_function_name(plan)
        if plan.bridge.native_is_subroutine:
            return FortranCall(native_name, arguments)
        if result_name is None:
            raise ValueError(f"{plan.owner_path!r} native function is missing a bridge result")
        expression = f"{native_name}({', '.join(item.text for item in arguments)})"
        return FortranAssignment(result_name, CodeExpression(expression))

    def _native_arguments(
        self,
        plan: FunctionPlan,
        present: frozenset[str],
    ) -> tuple[CodeExpression, ...]:
        expressions = dict(self._visible_native_argument_entries(plan, present))
        expressions.update(
            (slot.native_position, CodeExpression(self._literal_expression(slot.literal_value)))
            for slot in plan.native_call_slots
            if slot.source_kind == "literal"
        )
        hidden_result = self._hidden_native_result_entry(plan)
        if hidden_result is not None:
            expressions[hidden_result[0]] = hidden_result[1]
        return tuple(
            expressions[slot.native_position]
            for slot in sorted(plan.native_call_slots, key=lambda item: item.native_position)
            if slot.native_position in expressions
        )

    def _visible_native_argument_entries(
        self,
        plan: FunctionPlan,
        present: frozenset[str],
    ) -> tuple[tuple[int, CodeExpression], ...]:
        """Return native-position entries for present Python arguments."""
        entries = []
        has_optional = self._has_optional_arguments(plan)
        for argument in plan.arguments:
            if argument.bridge.optional_mode is not OptionalMode.REQUIRED and argument.owner_path not in present:
                continue
            expression = self._native_argument_expression(argument)
            if has_optional:
                expression = f"{argument.bridge.native_name}={expression}"
            entries.append((argument.native_call_slot.native_position, CodeExpression(expression)))
        return tuple(entries)

    def _hidden_native_result_entry(
        self,
        plan: FunctionPlan,
    ) -> tuple[int, CodeExpression] | None:
        """Return one hidden-result native-position entry when present."""
        if plan.result is None or plan.result.source_kind != "hidden_output":
            return None
        expression = plan.result.bridge.native_name.lower()
        if self._has_optional_arguments(plan):
            expression = f"{plan.result.bridge.native_name}={expression}"
        return plan.result.bridge.abi_position, CodeExpression(expression)

    def _native_argument_expression(self, plan: ArgumentTransferPlan) -> str:
        name = plan.bridge.native_name.lower()
        if plan.bridge.optional_mode is OptionalMode.DESCRIPTOR:
            return f"{name}_descriptor"
        return name

    def _presence_condition(self, plan: ArgumentTransferPlan) -> str:
        name = plan.bridge.native_name.lower()
        suffix = "_present" if plan.bridge.optional_mode is OptionalMode.DESCRIPTOR else ""
        return f"c_associated(bound_{name}{suffix})"

    def _present_preparation(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[FortranAssignment | FortranPointerAssignment | FortranCall | FortranIf, ...]:
        name = plan.bridge.native_name.lower()
        pointer_call = FortranCall(
            "c_f_pointer",
            (CodeExpression(f"bound_{name}"), CodeExpression(f"{name}_input")),
        )
        if plan.bridge.optional_mode is OptionalMode.NULLABLE_VALUE:
            return (
                FortranCall(
                    "c_f_pointer",
                    (CodeExpression(f"bound_{name}"), CodeExpression(name)),
                ),
            )
        assignment = self._descriptor_assignment(plan, name)
        return (
            pointer_call,
            FortranIf(CodeExpression(f"associated({name}_input)"), body=(assignment,)),
        )

    def _descriptor_assignment(
        self,
        plan: ArgumentTransferPlan,
        name: str,
    ) -> FortranAssignment | FortranPointerAssignment:
        if plan.native_call_slot.value_kind == "pointer":
            return FortranPointerAssignment(f"{name}_descriptor", CodeExpression(f"{name}_input"))
        return FortranAssignment(f"{name}_descriptor", CodeExpression(f"{name}_input"))

    def _optional_declarations(self, plan: FunctionPlan) -> tuple[FortranDeclaration, ...]:
        declarations = []
        for argument in plan.arguments:
            mode = argument.bridge.optional_mode
            if mode is OptionalMode.REQUIRED:
                continue
            name = argument.bridge.native_name.lower()
            scalar_type = PrimitiveScalarTypeRegistry.type_for(argument.semantic_type_name)
            if mode is OptionalMode.NULLABLE_VALUE:
                declarations.append(FortranDeclaration(name, scalar_type.fortran_spelling, ("pointer",)))
                continue
            declarations.append(FortranDeclaration(f"{name}_input", scalar_type.fortran_spelling, ("pointer",)))
            descriptor_attribute = "pointer" if argument.native_call_slot.value_kind == "pointer" else "allocatable"
            declarations.append(
                FortranDeclaration(f"{name}_descriptor", scalar_type.fortran_spelling, (descriptor_attribute,))
            )
        return tuple(declarations)

    def _descriptor_initializers(self, plan: FunctionPlan) -> tuple[FortranCall, ...]:
        return tuple(
            FortranCall("nullify", (CodeExpression(f"{argument.bridge.native_name.lower()}_descriptor"),))
            for argument in plan.arguments
            if (
                argument.bridge.optional_mode is OptionalMode.DESCRIPTOR
                and argument.native_call_slot.value_kind == "pointer"
            )
        )

    def _hidden_result_parameters(self, plan: FunctionPlan) -> tuple[FortranParameter, ...]:
        if plan.result is None or plan.result.source_kind != "hidden_output":
            return ()
        scalar_type = PrimitiveScalarTypeRegistry.type_for(plan.result.semantic_type_name)
        return (FortranParameter(plan.result.bridge.native_name.lower(), scalar_type.fortran_spelling),)

    def _bridge_result_type(self, plan: FunctionPlan) -> str:
        if plan.result is None:
            raise ValueError(f"{plan.owner_path!r} native function has no result plan")
        return PrimitiveScalarTypeRegistry.type_for(plan.result.semantic_type_name).fortran_spelling

    def _external_declarations(self, plan: FunctionPlan) -> tuple[FortranDeclaration, ...]:
        if not plan.bridge.external or plan.result is None or self._has_optional_arguments(plan):
            return ()
        result_type = PrimitiveScalarTypeRegistry.type_for(plan.result.semantic_type_name).fortran_spelling
        return (FortranDeclaration(plan.bridge.native_name, result_type, ("external",)),)

    def _native_module_uses(self, plan: ModulePlan) -> tuple[FortranUse, ...]:
        modules: dict[str, list[str]] = {}
        for function in self._functions(plan):
            if function.bridge.native_module is not None:
                modules.setdefault(function.bridge.native_module, []).append(
                    f"{self._native_function_name(function)} => {function.bridge.native_name}"
                )
        for variable in self._variables(plan):
            if variable.bridge.getter_role is not None or variable.bridge.setter_role is not None:
                modules.setdefault(variable.bridge.native_module, []).append(
                    f"{self._native_variable_name(variable)} => {variable.bridge.native_name}"
                )
        return tuple(FortranUse(module, tuple(dict.fromkeys(names))) for module, names in modules.items())

    def _external_interfaces(self, plan: ModulePlan) -> tuple[FortranInterface, ...]:
        procedures = tuple(
            self._external_interface_procedure(function)
            for function in self._functions(plan)
            if function.bridge.external and self._has_optional_arguments(function)
        )
        return (FortranInterface(procedures),) if procedures else ()

    def _module_snapshot_interfaces(self, plan: ModulePlan) -> tuple[FortranInterface, ...]:
        """Return the allocator interface required by nullable module snapshots."""
        if not any(
            variable.bridge.getter_action is ModuleGetterAction.NULLABLE_SNAPSHOT for variable in self._variables(plan)
        ):
            return ()
        procedure = FortranInterfaceProcedure(
            name="c_malloc",
            imports=("c_ptr", "c_size_t"),
            parameters=(FortranParameter("size", "integer(c_size_t)", ("value",)),),
            result_name="ptr",
            result_type="type(c_ptr)",
            bind_name="x2py_malloc",
        )
        return (FortranInterface((procedure,)),)

    def _external_interface_procedure(self, plan: FunctionPlan) -> FortranInterfaceProcedure:
        parameters = tuple(
            FortranParameter(
                argument.bridge.native_name.lower(),
                PrimitiveScalarTypeRegistry.type_for(argument.semantic_type_name).fortran_spelling,
                ("optional",) if argument.bridge.optional_mode is not OptionalMode.REQUIRED else (),
            )
            for argument in sorted(plan.arguments, key=lambda item: item.native_position)
        )
        imports = tuple(dict.fromkeys(self._iso_symbol(argument.semantic_type_name) for argument in plan.arguments))
        result_name = None if plan.bridge.native_is_subroutine else "native_result"
        result_type = self._bridge_result_type(plan) if result_name is not None else None
        if result_type is not None and plan.result is not None:
            imports = tuple(dict.fromkeys((*imports, self._iso_symbol(plan.result.semantic_type_name))))
        return FortranInterfaceProcedure(
            name=plan.bridge.native_name,
            imports=imports,
            parameters=parameters,
            result_name=result_name,
            result_type=result_type,
            is_subroutine=plan.bridge.native_is_subroutine,
        )

    def _has_optional_arguments(self, plan: FunctionPlan) -> bool:
        return any(argument.bridge.optional_mode is not OptionalMode.REQUIRED for argument in plan.arguments)

    def _literal_expression(self, value: object) -> str:
        if isinstance(value, bool):
            return ".true." if value else ".false."
        if isinstance(value, complex):
            return f"({value.real}, {value.imag})"
        return str(value)

    def _bridge_function_name(self, plan: FunctionPlan) -> str:
        return f"bind_c_{plan.symbol_name}"

    def _module_bridge_getter_name(self, plan: ModuleVariablePlan) -> str:
        return f"bind_c_get_{plan.symbol_name}"

    def _module_bridge_setter_name(self, plan: ModuleVariablePlan) -> str:
        return f"bind_c_set_{plan.symbol_name}"

    def _native_function_name(self, plan: FunctionPlan) -> str:
        return plan.bridge.native_name if plan.bridge.external else f"native_{plan.symbol_name}"

    def _native_variable_name(self, plan: ModuleVariablePlan) -> str:
        return f"native_{plan.symbol_name}"

    def _functions(self, plan: ModulePlan) -> tuple[FunctionPlan, ...]:
        return tuple(function for namespace in plan.namespaces for function in namespace.functions)

    def _variables(self, plan: ModulePlan) -> tuple[ModuleVariablePlan, ...]:
        return tuple(variable for namespace in plan.namespaces for variable in namespace.variables)

    @staticmethod
    def lowering_method_name(subject: str, action: object) -> str:
        """Return the exact implementation method selected by one plan action."""
        value = getattr(action, "value", action)
        return f"_lower_{subject}_{value}"

    def _require_lowering_method(self, subject: str, action: object, owner_path: str) -> str:
        method_name = self.lowering_method_name(subject, action)
        if not callable(getattr(self, method_name, None)):
            raise ValueError(f"Unsupported Fortran lowering action for {owner_path!r}: {method_name}")
        return method_name

    def _call_lowering(self, subject: str, action: object, *args):
        method_name = self._require_lowering_method(subject, action, getattr(args[0], "owner_path", subject))
        return getattr(self, method_name)(*args)

    def _iso_symbol(self, semantic_type_name: str) -> str:
        symbols = {
            "Bool": "c_bool",
            "Int32": "c_int32_t",
            "Float32": "c_float",
            "Float64": "c_double",
            "Complex64": "c_float_complex",
            "Complex128": "c_double_complex",
        }
        return symbols[semantic_type_name]

    def _iso_c_symbols(self) -> tuple[str, ...]:
        return (
            "c_associated",
            "c_bool",
            "c_double",
            "c_double_complex",
            "c_f_pointer",
            "c_float",
            "c_float_complex",
            "c_int",
            "c_int32_t",
            "c_ptr",
            "c_null_ptr",
            "c_size_t",
        )
