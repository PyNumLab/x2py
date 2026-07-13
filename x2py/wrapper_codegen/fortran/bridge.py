"""Direct recursive Fortran bridge generation from shared wrapper plans."""

from __future__ import annotations

from x2py.semantics.ownership import AssignmentMode, CodegenAction, NativeBarrierAction
from x2py.semantics.wrapper_policy import (
    ArgumentHandoffMode,
    BridgeDataAction,
    ModuleGetterAction,
    OptionalMode,
)
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
    DatatypeFamily,
    FunctionPlan,
    ModulePlan,
    ModuleVariablePlan,
    NamespacePlan,
    NativeCallSlotPlan,
    ResultPlan,
)
from x2py.wrapper_codegen.primitive_scalar_types import PrimitiveScalarTypeRegistry
from x2py.wrapper_codegen.visitor import ClassVisitor


class FortranBridgeGenerator(ClassVisitor):
    """Recursively lower bridge plan views directly into Fortran nodes."""

    def require_supported(self, plan: ModulePlan) -> None:
        """Reject unsupported Fortran ABI actions and scalar types."""
        for function in self._functions(plan):
            self._require_function_supported(function)
        for variable in self._variables(plan):
            self._require_variable_supported(variable)

    def _require_function_supported(self, function: FunctionPlan) -> None:
        """Reject unsupported actions in one planned bridge procedure."""
        if self._has_optional_arguments(function) and any(
            slot.source_kind == "literal" for slot in function.native_call_slots
        ):
            raise ValueError(f"{function.owner_path!r} mixes optional scalar arguments with hidden literals")
        for argument in function.arguments:
            self._require_argument_supported(argument)
        for slot in function.native_call_slots:
            self._require_native_result_supported(function, slot)

    def _require_argument_supported(self, argument: ArgumentTransferPlan) -> None:
        """Reject one unsupported native argument action."""
        supported = {
            NativeBarrierAction.PASS_VALUE,
            NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS,
            NativeBarrierAction.PASS_RAW_ADDRESS,
            NativeBarrierAction.PASS_STORAGE_ADDRESS,
        }
        if argument.bridge.native_action not in supported:
            raise ValueError(
                f"Unsupported Fortran argument action for {argument.owner_path!r}: {argument.bridge.native_action!r}"
            )
        if (
            argument.bridge.native_action is NativeBarrierAction.PASS_RAW_ADDRESS
            and argument.bridge.handoff_mode is not ArgumentHandoffMode.OPAQUE_ADDRESS
        ):
            raise ValueError(f"Unsupported Fortran raw-address handoff for {argument.owner_path!r}")
        if argument.bridge.data_action is BridgeDataAction.BLOCKED:
            raise ValueError(f"Blocked Fortran bridge data action for {argument.owner_path!r}")
        PrimitiveScalarTypeRegistry.type_for(argument.semantic_type_name)

    def _require_native_result_supported(self, function: FunctionPlan, slot: NativeCallSlotPlan) -> None:
        """Reject one unsupported native result output."""
        if slot.source_kind != "result":
            return
        if slot.datatype_family is DatatypeFamily.STRING:
            self._require_string_result_supported(function, slot)
            return
        if slot.semantic_type_name is None:
            raise ValueError(f"Missing Fortran result datatype for {slot.owner_path!r}")
        PrimitiveScalarTypeRegistry.type_for(slot.semantic_type_name)

    def _require_string_result_supported(self, function: FunctionPlan, slot: NativeCallSlotPlan) -> None:
        """Require one fixed-length status-message result."""
        policy = function.binding.status_error
        if policy is None:
            raise ValueError(f"Unsupported Fortran string output for {slot.owner_path!r}")
        if policy.message_role != slot.symbolic_role:
            raise ValueError(f"Unsupported Fortran string output for {slot.owner_path!r}")
        if slot.character_length is None:
            raise ValueError(f"Unsupported Fortran string output for {slot.owner_path!r}")
        if slot.bridge_data_action is not BridgeDataAction.COPY_REPRESENTATION:
            raise ValueError(f"Unsupported Fortran string bridge data action for {slot.owner_path!r}")

    def _require_variable_supported(self, variable: ModuleVariablePlan) -> None:
        """Reject unsupported actions in one planned module variable."""
        if variable.bridge.native_assignment not in {
            AssignmentMode.NONE,
            AssignmentMode.VALUE_COPY,
        }:
            raise ValueError(
                f"Unsupported Fortran module setter assignment for {variable.owner_path!r}: "
                f"{variable.bridge.native_assignment!r}"
            )
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
            interfaces=(*self._external_interfaces(plan), *self._allocator_interfaces(plan)),
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
        result_name, result_type = self._lower_result(plan)
        parameters = tuple(
            parameter
            for argument in sorted(plan.arguments, key=lambda item: item.bridge.abi_position)
            for parameter in self.visit(argument)
        )
        parameters = (*parameters, *self._native_output_parameters(plan))
        bridge_name = self._bridge_function_name(plan)
        is_subroutine = plan.bridge.native_is_subroutine
        return FortranFunction(
            name=bridge_name,
            parameters=parameters,
            result_name=result_name,
            result_type=result_type,
            bind_name=bridge_name,
            declarations=(
                *self._optional_declarations(plan),
                *self._opaque_address_declarations(plan),
                *self._native_output_declarations(plan),
            ),
            body=(
                *self._descriptor_initializers(plan),
                *self._opaque_address_initializers(plan),
                *self._function_body(plan, result_name),
                *self._native_output_finalizers(plan),
            ),
            is_subroutine=is_subroutine,
        )

    def _lower_result(
        self,
        plan: FunctionPlan,
    ) -> tuple[str | None, str | None]:
        """Dispatch one completed bridge result action explicitly."""
        result = self._direct_result(plan)
        if result is None:
            return self._lower_result_none(plan)
        action = result.bridge.codegen_action
        match action:
            case CodegenAction.DIRECT_VALUE:
                return self._lower_result_direct_value(plan, result)
        raise ValueError(f"Unsupported Fortran result action for {plan.owner_path!r}: {action!r}")

    def _lower_result_none(
        self,
        _plan: FunctionPlan,
    ) -> tuple[str | None, str | None]:
        """Return the procedure shape of a native subroutine with no projection."""
        return None, None

    def _lower_result_direct_value(
        self,
        plan: FunctionPlan,
        result: ResultPlan,
    ) -> tuple[str | None, str | None]:
        """Return the procedure shape of a direct native function result."""
        return "result", self._bridge_result_type(plan, result)

    def _visit_ModuleVariablePlan(self, plan: ModuleVariablePlan) -> tuple[FortranFunction, ...]:
        """Lower bridge-owned getter and setter actions into procedures."""
        return (
            *self._lower_module_getter(plan),
            *self._lower_module_setter(plan),
        )

    def _lower_module_getter(self, plan: ModuleVariablePlan) -> tuple[FortranFunction, ...]:
        """Dispatch one completed bridge getter action explicitly."""
        action = plan.bridge.getter_action
        match action:
            case ModuleGetterAction.CONSTANT_VALUE:
                return self._lower_module_getter_constant_value(plan)
            case ModuleGetterAction.DIRECT_VALUE:
                return self._lower_module_getter_direct_value(plan)
            case ModuleGetterAction.NULLABLE_SNAPSHOT:
                return self._lower_module_getter_nullable_snapshot(plan)
        raise ValueError(f"Unsupported Fortran module getter action for {plan.owner_path!r}: {action!r}")

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

    def _lower_module_setter(self, plan: ModuleVariablePlan) -> tuple[FortranFunction, ...]:
        """Dispatch one completed native assignment action explicitly."""
        action = plan.bridge.native_assignment
        match action:
            case AssignmentMode.NONE:
                return self._lower_module_setter_none(plan)
            case AssignmentMode.VALUE_COPY:
                return self._lower_module_setter_value_copy(plan)
        raise ValueError(f"Unsupported Fortran module setter assignment for {plan.owner_path!r}: {action!r}")

    def _lower_module_setter_none(self, _plan: ModuleVariablePlan) -> tuple[FortranFunction, ...]:
        """Return no native setter when the bridge assignment is omitted."""
        return ()

    def _lower_module_setter_value_copy(self, plan: ModuleVariablePlan) -> tuple[FortranFunction, ...]:
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

    def _visit_ArgumentTransferPlan(self, plan: ArgumentTransferPlan) -> tuple[FortranParameter, ...]:
        """Lower one argument through the completed optional-mode action."""
        return self._lower_argument(plan)

    def _lower_argument(self, plan: ArgumentTransferPlan) -> tuple[FortranParameter, ...]:
        """Dispatch one completed bridge optional mode explicitly."""
        mode = plan.bridge.optional_mode
        match mode:
            case OptionalMode.REQUIRED:
                return self._lower_argument_required(plan)
            case OptionalMode.NULLABLE_VALUE:
                return self._lower_argument_nullable_value(plan)
            case OptionalMode.DESCRIPTOR:
                return self._lower_argument_descriptor(plan)
        raise ValueError(f"Unsupported Fortran argument optional mode for {plan.owner_path!r}: {mode!r}")

    def _lower_argument_required(self, plan: ArgumentTransferPlan) -> tuple[FortranParameter, ...]:
        """Dispatch one required bridge parameter from its completed ABI shape."""
        mode = plan.bridge.handoff_mode
        match mode:
            case ArgumentHandoffMode.VALUE:
                return self._lower_argument_required_value(plan)
            case ArgumentHandoffMode.TYPED_REFERENCE:
                return self._lower_argument_required_typed_reference(plan)
            case ArgumentHandoffMode.OPAQUE_ADDRESS:
                return self._lower_argument_required_opaque_address(plan)
        raise ValueError(f"Unsupported Fortran argument handoff for {plan.owner_path!r}: {mode!r}")

    def _lower_argument_required_value(self, plan: ArgumentTransferPlan) -> tuple[FortranParameter, ...]:
        """Return one interoperable scalar value parameter."""
        return (self._parameter(plan, ("value",)),)

    def _lower_argument_required_typed_reference(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[FortranParameter, ...]:
        """Return one ordinary interoperable scalar reference parameter."""
        return (self._parameter(plan, ()),)

    def _lower_argument_required_opaque_address(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[FortranParameter, ...]:
        """Return one C pointer value for caller-owned scalar storage."""
        name = plan.bridge.native_name.lower()
        return (FortranParameter(f"bound_{name}", "type(c_ptr)", ("value",)),)

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
        expressions.update(self._hidden_native_result_entries(plan))
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

    def _hidden_native_result_entries(
        self,
        plan: FunctionPlan,
    ) -> tuple[tuple[int, CodeExpression], ...]:
        """Return all mechanically lowered hidden-result native entries."""
        entries = []
        for slot in plan.native_call_slots:
            if slot.source_kind != "result":
                continue
            expression = self._native_output_value_name(slot)
            if self._has_optional_arguments(plan):
                expression = f"{slot.native_name}={expression}"
            entries.append((slot.native_position, CodeExpression(expression)))
        return tuple(entries)

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
        """Dispatch only the bridge data action completed before lowering."""
        action = plan.bridge.data_action
        match action:
            case BridgeDataAction.ASSOCIATE_VIEW:
                return self._prepare_present_associated_view(plan)
            case BridgeDataAction.COPY_REPRESENTATION:
                return self._prepare_present_representation_copy(plan)
        raise ValueError(f"Unsupported present bridge data action for {plan.owner_path!r}: {action!r}")

    def _prepare_present_associated_view(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[FortranPointerAssignment | FortranCall | FortranIf, ...]:
        """Associate a non-owning native view without copying payload data."""
        name = plan.bridge.native_name.lower()
        if plan.bridge.optional_mode is OptionalMode.NULLABLE_VALUE:
            return (
                FortranCall(
                    "c_f_pointer",
                    (CodeExpression(f"bound_{name}"), CodeExpression(name)),
                ),
            )
        if plan.bridge.optional_mode is not OptionalMode.DESCRIPTOR:
            raise ValueError(f"Associated-view preparation requires an optional argument: {plan.owner_path!r}")
        if plan.native_call_slot.value_kind != "pointer":
            raise ValueError(f"Associated descriptor view requires pointer policy: {plan.owner_path!r}")
        return (
            self._descriptor_input_pointer_call(name),
            FortranIf(
                CodeExpression(f"associated({name}_input)"),
                body=(FortranPointerAssignment(f"{name}_descriptor", CodeExpression(f"{name}_input")),),
            ),
        )

    def _prepare_present_representation_copy(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[FortranCall | FortranIf, ...]:
        """Copy only when completed policy requires a different native representation."""
        if plan.bridge.optional_mode is not OptionalMode.DESCRIPTOR:
            raise ValueError(f"Representation copy requires descriptor policy: {plan.owner_path!r}")
        if plan.native_call_slot.value_kind != "allocatable":
            raise ValueError(f"Representation copy requires allocatable policy: {plan.owner_path!r}")
        name = plan.bridge.native_name.lower()
        return (
            self._descriptor_input_pointer_call(name),
            FortranIf(
                CodeExpression(f"associated({name}_input)"),
                body=(FortranAssignment(f"{name}_descriptor", CodeExpression(f"{name}_input")),),
            ),
        )

    def _descriptor_input_pointer_call(self, name: str) -> FortranCall:
        """Associate one binding value with a typed descriptor-input view."""
        return FortranCall(
            "c_f_pointer",
            (CodeExpression(f"bound_{name}"), CodeExpression(f"{name}_input")),
        )

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

    def _opaque_address_declarations(self, plan: FunctionPlan) -> tuple[FortranDeclaration, ...]:
        """Return typed pointer locals for required opaque scalar addresses."""
        return tuple(
            FortranDeclaration(
                argument.bridge.native_name.lower(),
                PrimitiveScalarTypeRegistry.type_for(argument.semantic_type_name).fortran_spelling,
                ("pointer",),
            )
            for argument in plan.arguments
            if (
                argument.bridge.optional_mode is OptionalMode.REQUIRED
                and argument.bridge.handoff_mode is ArgumentHandoffMode.OPAQUE_ADDRESS
                and argument.bridge.data_action is BridgeDataAction.ASSOCIATE_VIEW
            )
        )

    def _opaque_address_initializers(self, plan: FunctionPlan) -> tuple[FortranCall, ...]:
        """Associate typed scalar locals with caller-provided C addresses."""
        return tuple(
            FortranCall(
                "c_f_pointer",
                (
                    CodeExpression(f"bound_{argument.bridge.native_name.lower()}"),
                    CodeExpression(argument.bridge.native_name.lower()),
                ),
            )
            for argument in plan.arguments
            if (
                argument.bridge.optional_mode is OptionalMode.REQUIRED
                and argument.bridge.handoff_mode is ArgumentHandoffMode.OPAQUE_ADDRESS
                and argument.bridge.data_action is BridgeDataAction.ASSOCIATE_VIEW
            )
        )

    def _descriptor_initializers(self, plan: FunctionPlan) -> tuple[FortranCall, ...]:
        return tuple(
            FortranCall("nullify", (CodeExpression(f"{argument.bridge.native_name.lower()}_descriptor"),))
            for argument in plan.arguments
            if (
                argument.bridge.optional_mode is OptionalMode.DESCRIPTOR
                and argument.native_call_slot.value_kind == "pointer"
            )
        )

    def _native_output_parameters(self, plan: FunctionPlan) -> tuple[FortranParameter, ...]:
        """Return bridge ABI parameters for every typed native result slot."""
        parameters = []
        for slot in sorted(plan.native_call_slots, key=lambda item: item.native_position):
            if slot.source_kind != "result":
                continue
            if slot.datatype_family is DatatypeFamily.STRING:
                parameters.append(FortranParameter(slot.native_name.lower(), "type(c_ptr)"))
                continue
            if slot.semantic_type_name is None:
                raise ValueError(f"Missing native output datatype for {slot.owner_path!r}")
            scalar_type = PrimitiveScalarTypeRegistry.type_for(slot.semantic_type_name)
            parameters.append(FortranParameter(slot.native_name.lower(), scalar_type.fortran_spelling))
        return tuple(parameters)

    def _native_output_declarations(self, plan: FunctionPlan) -> tuple[FortranDeclaration, ...]:
        """Dispatch helper-local output storage from completed bridge data actions."""
        declarations = []
        for slot in plan.native_call_slots:
            if slot.source_kind != "result":
                continue
            if slot.bridge_data_action is BridgeDataAction.DIRECT_TRANSFER:
                continue
            if slot.bridge_data_action is BridgeDataAction.COPY_REPRESENTATION:
                declarations.extend(self._representation_copy_output_declarations(slot))
                continue
            raise ValueError(
                f"Unsupported native-output bridge data action for {slot.owner_path!r}: {slot.bridge_data_action!r}"
            )
        return tuple(declarations)

    def _representation_copy_output_declarations(
        self,
        slot: NativeCallSlotPlan,
    ) -> tuple[FortranDeclaration, ...]:
        """Declare storage only for one justified representation-copy output."""
        if slot.datatype_family is not DatatypeFamily.STRING:
            raise ValueError(f"Unsupported representation-copy output for {slot.owner_path!r}")
        length = self._string_output_length(slot)
        value_name = self._native_output_value_name(slot)
        return (
            FortranDeclaration(value_name, f"character(kind=c_char, len={length})"),
            FortranDeclaration(
                f"{slot.native_name.lower()}_copy",
                "character(kind=c_char)",
                ("pointer", "dimension(:)"),
            ),
        )

    def _native_output_finalizers(
        self,
        plan: FunctionPlan,
    ) -> tuple[FortranAssignment | FortranIf, ...]:
        """Dispatch output finalization from completed bridge data actions."""
        nodes = []
        for slot in plan.native_call_slots:
            if slot.source_kind != "result" or slot.bridge_data_action is BridgeDataAction.DIRECT_TRANSFER:
                continue
            if slot.bridge_data_action is BridgeDataAction.COPY_REPRESENTATION:
                nodes.extend(self._lower_native_output_representation_copy(slot))
                continue
            raise ValueError(
                f"Unsupported native-output bridge data action for {slot.owner_path!r}: {slot.bridge_data_action!r}"
            )
        return tuple(nodes)

    def _lower_native_output_representation_copy(
        self,
        slot: NativeCallSlotPlan,
    ) -> tuple[FortranAssignment | FortranIf, ...]:
        """Copy one native output only through the explicit policy permission."""
        if slot.datatype_family is not DatatypeFamily.STRING:
            raise ValueError(f"Unsupported representation-copy output for {slot.owner_path!r}")
        name = slot.native_name.lower()
        value_name = self._native_output_value_name(slot)
        copy_name = f"{name}_copy"
        length = self._string_output_length(slot)
        c_length = length + 1
        return (
            FortranAssignment(name, CodeExpression(f"c_malloc({c_length}_c_size_t)")),
            FortranIf(
                CodeExpression(f"c_associated({name})"),
                body=(
                    FortranCall(
                        "c_f_pointer",
                        (CodeExpression(name), CodeExpression(copy_name), CodeExpression(f"[{c_length}]")),
                    ),
                    FortranAssignment(
                        f"{copy_name}(1:{length})",
                        CodeExpression(f"transfer({value_name}, {copy_name}(1:{length}))"),
                    ),
                    FortranAssignment(f"{copy_name}({c_length})", CodeExpression("c_null_char")),
                ),
            ),
        )

    def _native_output_value_name(self, slot: NativeCallSlotPlan) -> str:
        """Return the native-call expression selected for one output slot."""
        name = slot.native_name.lower()
        return f"{name}_value" if slot.datatype_family is DatatypeFamily.STRING else name

    def _string_output_length(self, slot: NativeCallSlotPlan) -> int:
        if slot.character_length is None or slot.character_length <= 0:
            raise ValueError(f"String output {slot.owner_path!r} is missing a fixed character length")
        return slot.character_length

    def _bridge_result_type(self, plan: FunctionPlan, result: ResultPlan | None = None) -> str:
        result = result or self._direct_result(plan)
        if result is None:
            raise ValueError(f"{plan.owner_path!r} native function has no result plan")
        return PrimitiveScalarTypeRegistry.type_for(result.semantic_type_name).fortran_spelling

    def _direct_result(self, plan: FunctionPlan) -> ResultPlan | None:
        """Return the sole direct result used by the Fortran function ABI."""
        return next((result for result in plan.results if result.source_kind == "direct_return"), None)

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
            if function.bridge.external
        )
        return (FortranInterface(procedures),) if procedures else ()

    def _allocator_interfaces(self, plan: ModulePlan) -> tuple[FortranInterface, ...]:
        """Return the allocator interface required by detached bridge copies."""
        needs_snapshot = any(
            variable.bridge.getter_action is ModuleGetterAction.NULLABLE_SNAPSHOT for variable in self._variables(plan)
        )
        needs_string_output = any(
            slot.datatype_family is DatatypeFamily.STRING
            for function in self._functions(plan)
            for slot in function.native_call_slots
            if slot.source_kind == "result"
        )
        if not needs_snapshot and not needs_string_output:
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
        direct_result = self._direct_result(plan)
        result_type = self._bridge_result_type(plan, direct_result) if result_name is not None else None
        if result_type is not None and direct_result is not None:
            imports = tuple(dict.fromkeys((*imports, self._iso_symbol(direct_result.semantic_type_name))))
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

    def _iso_symbol(self, semantic_type_name: str) -> str:
        symbols = {
            "Bool": "c_bool",
            "Int8": "c_int8_t",
            "Int16": "c_int16_t",
            "Int32": "c_int32_t",
            "Int64": "c_int64_t",
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
            "c_char",
            "c_double",
            "c_double_complex",
            "c_f_pointer",
            "c_float",
            "c_float_complex",
            "c_int8_t",
            "c_int16_t",
            "c_int",
            "c_int32_t",
            "c_int64_t",
            "c_null_char",
            "c_ptr",
            "c_null_ptr",
            "c_size_t",
        )
