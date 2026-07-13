"""Direct recursive Fortran bridge generation from shared wrapper plans."""

from __future__ import annotations

import re

from x2py.semantics.ownership import (
    AssignmentMode,
    CodegenAction,
    NativeBarrierAction,
    ObjectKind,
    PythonBarrierAction,
)
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
    FortranCase,
    FortranDeclaration,
    FortranFunction,
    FortranIf,
    FortranInterface,
    FortranInterfaceProcedure,
    FortranModule,
    FortranParameter,
    FortranPointerAssignment,
    FortranSelectCase,
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
        for result in function.results:
            match result.object_kind:
                case ObjectKind.SCALAR:
                    PrimitiveScalarTypeRegistry.type_for(result.semantic_type_name)
                case ObjectKind.STRING:
                    self._require_string_plan_result_supported(result)
                case ObjectKind.NUMPY_ARRAY:
                    self._require_array_plan_result_supported(result)
                case _:
                    raise ValueError(
                        f"Unsupported Fortran result object kind for {result.owner_path!r}: {result.object_kind!r}"
                    )
        for slot in function.native_call_slots:
            self._require_native_result_supported(function, slot)

    def _require_argument_supported(self, argument: ArgumentTransferPlan) -> None:
        """Reject one unsupported native argument action."""
        supported = {
            NativeBarrierAction.PASS_VALUE,
            NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS,
            NativeBarrierAction.PASS_RAW_ADDRESS,
            NativeBarrierAction.PASS_STORAGE_ADDRESS,
            NativeBarrierAction.PASS_ARRAY_BUFFER,
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
        match argument.object_kind:
            case ObjectKind.SCALAR:
                self._require_scalar_argument_supported(argument)
            case ObjectKind.STRING:
                self._require_string_argument_supported(argument)
            case ObjectKind.NUMPY_ARRAY:
                self._require_array_argument_supported(argument)
            case _:
                raise ValueError(
                    f"Unsupported Fortran argument object kind for {argument.owner_path!r}: {argument.object_kind!r}"
                )

    def _require_native_result_supported(self, function: FunctionPlan, slot: NativeCallSlotPlan) -> None:
        """Dispatch one native result output to its family support check."""
        if slot.source_kind != "result":
            return
        match slot.object_kind:
            case ObjectKind.SCALAR:
                self._require_scalar_native_result_supported(slot)
            case ObjectKind.STRING:
                self._require_string_result_supported(function, slot)
            case ObjectKind.NUMPY_ARRAY:
                self._require_array_result_supported(function, slot)
            case _:
                raise ValueError(
                    f"Unsupported Fortran native result object kind for {slot.owner_path!r}: {slot.object_kind!r}"
                )

    # Scalar support checks.
    def _require_scalar_argument_supported(self, argument: ArgumentTransferPlan) -> None:
        """Require one first-lane primitive scalar argument type."""
        PrimitiveScalarTypeRegistry.type_for(argument.semantic_type_name)

    def _require_scalar_native_result_supported(self, slot: NativeCallSlotPlan) -> None:
        """Require one first-lane primitive scalar native result type."""
        if slot.semantic_type_name is None:
            raise ValueError(f"Missing Fortran result datatype for {slot.owner_path!r}")
        PrimitiveScalarTypeRegistry.type_for(slot.semantic_type_name)

    # Ordinary-array support checks.
    def _require_array_argument_supported(self, argument: ArgumentTransferPlan) -> None:
        """Require one completed ordinary array view."""
        array = argument.array
        if array is None or (array.rank is not None and not 1 <= array.rank <= 15):
            raise ValueError(f"Unsupported Fortran array rank for {argument.owner_path!r}")
        if array.contiguous not in {True, False}:
            raise ValueError(f"Unsupported Fortran array layout for {argument.owner_path!r}")
        if argument.bridge.handoff_mode is not ArgumentHandoffMode.ARRAY_BUFFER:
            raise ValueError(f"Unsupported Fortran array handoff for {argument.owner_path!r}")
        if argument.bridge.data_action is not BridgeDataAction.ASSOCIATE_VIEW:
            raise ValueError(f"Unsupported Fortran array data action for {argument.owner_path!r}")
        if argument.datatype_family is not DatatypeFamily.STRING:
            PrimitiveScalarTypeRegistry.type_for(argument.semantic_type_name)

    def _require_array_plan_result_supported(self, result: ResultPlan) -> None:
        """Require one fixed-shape ordinary array copy result."""
        array = result.array
        if array is None or array.rank is None or not 1 <= array.rank <= 15:
            raise ValueError(f"Unsupported Fortran array result rank for {result.owner_path!r}")
        if array.order == "ORDER_C" and array.rank > 1:
            raise ValueError(f"Unsupported Fortran array result order for {result.owner_path!r}")
        if result.bridge.data_action is not BridgeDataAction.COPY_REPRESENTATION:
            raise ValueError(f"Unsupported Fortran array result data action for {result.owner_path!r}")
        if result.datatype_family is DatatypeFamily.STRING:
            if array.itemsize is None or array.itemsize <= 0:
                raise ValueError(f"Unsupported Fortran character array result for {result.owner_path!r}")
            return
        PrimitiveScalarTypeRegistry.type_for(result.semantic_type_name)

    def _require_array_result_supported(self, function: FunctionPlan, slot: NativeCallSlotPlan) -> None:
        """Require one hidden fixed-shape ordinary array copy result."""
        self._require_array_result_shape_supported(slot)
        self._require_array_result_action_supported(slot)
        self._require_array_result_type_supported(function, slot)

    def _require_array_result_shape_supported(self, slot: NativeCallSlotPlan) -> None:
        """Require one fixed-rank non-C-oriented array result shape."""
        array = slot.array
        if array is None or array.rank is None or not 1 <= array.rank <= 15:
            raise ValueError(f"Unsupported Fortran array output rank for {slot.owner_path!r}")
        if array.order == "ORDER_C" and array.rank > 1:
            raise ValueError(f"Unsupported Fortran array output order for {slot.owner_path!r}")

    def _require_array_result_action_supported(self, slot: NativeCallSlotPlan) -> None:
        """Require the completed ordinary-array representation-copy action."""
        if slot.bridge_data_action is not BridgeDataAction.COPY_REPRESENTATION:
            raise ValueError(f"Unsupported Fortran array output data action for {slot.owner_path!r}")

    def _require_array_result_type_supported(self, function: FunctionPlan, slot: NativeCallSlotPlan) -> None:
        """Require one primitive non-character result owned by the function plan."""
        if not any(result.native_call_slot is slot for result in function.results):
            raise ValueError(f"Unsupported Fortran array output for {slot.owner_path!r}")
        if slot.datatype_family is DatatypeFamily.STRING:
            if slot.array is None or slot.array.itemsize is None or slot.array.itemsize <= 0:
                raise ValueError(f"Unsupported Fortran character array output for {slot.owner_path!r}")
            return
        if slot.semantic_type_name is None:
            raise ValueError(f"Missing Fortran array output datatype for {slot.owner_path!r}")
        PrimitiveScalarTypeRegistry.type_for(slot.semantic_type_name)

    # String support checks.
    def _require_string_argument_supported(self, argument: ArgumentTransferPlan) -> None:
        """Require a completed string value, storage, or raw-address contract."""
        if argument.bridge.data_action is not BridgeDataAction.COPY_REPRESENTATION:
            raise ValueError(f"Unsupported Fortran string data action for {argument.owner_path!r}")
        action = argument.binding.python_action
        if action is PythonBarrierAction.STRING_VALUE:
            self._require_string_value_argument_supported(argument)
            return
        if action not in {PythonBarrierAction.STRING_STORAGE, PythonBarrierAction.RAW_ADDRESS}:
            raise ValueError(f"Unsupported Fortran string boundary for {argument.owner_path!r}: {action!r}")
        self._require_string_address_argument_supported(argument)

    def _require_string_value_argument_supported(self, argument: ArgumentTransferPlan) -> None:
        """Require one character-buffer value handoff."""
        if argument.bridge.native_action is not NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS:
            raise ValueError(f"Unsupported Fortran string action for {argument.owner_path!r}")
        if argument.bridge.handoff_mode is not ArgumentHandoffMode.CHARACTER_BUFFER:
            raise ValueError(f"Unsupported Fortran string handoff for {argument.owner_path!r}")
        if argument.bridge.codegen_action not in {CodegenAction.CALL_LOCAL_INPUT, CodegenAction.COPY_IN_OUT}:
            raise ValueError(f"Unsupported Fortran string codegen action for {argument.owner_path!r}")

    def _require_string_address_argument_supported(self, argument: ArgumentTransferPlan) -> None:
        """Require one fixed storage/raw-address handoff."""
        if argument.bridge.handoff_mode is not ArgumentHandoffMode.OPAQUE_ADDRESS:
            raise ValueError(f"Unsupported Fortran string address handoff for {argument.owner_path!r}")
        if argument.bridge.codegen_action is not CodegenAction.IN_PLACE_ARGUMENT:
            raise ValueError(f"Unsupported Fortran string address action for {argument.owner_path!r}")
        if argument.character_length is None or argument.character_length <= 0:
            raise ValueError(f"Unsupported Fortran string address length for {argument.owner_path!r}")

    def _require_string_result_supported(self, function: FunctionPlan, slot: NativeCallSlotPlan) -> None:
        """Require one fixed string result slot or status-message slot."""
        if slot.character_length is None or slot.character_length <= 0:
            raise ValueError(f"Unsupported Fortran string output for {slot.owner_path!r}")
        if slot.bridge_data_action is not BridgeDataAction.COPY_REPRESENTATION:
            raise ValueError(f"Unsupported Fortran string bridge data action for {slot.owner_path!r}")
        policy = function.binding.status_error
        if policy is not None and policy.message_role == slot.symbolic_role:
            return
        if any(result.native_call_slot is slot for result in function.results):
            return
        raise ValueError(f"Unsupported Fortran string output for {slot.owner_path!r}")

    def _require_string_plan_result_supported(self, result: ResultPlan) -> None:
        """Require one fixed string result with a justified representation copy."""
        if result.character_length is None or result.character_length <= 0:
            raise ValueError(f"Unsupported Fortran string result for {result.owner_path!r}")
        if result.bridge.data_action is not BridgeDataAction.COPY_REPRESENTATION:
            raise ValueError(f"Unsupported Fortran string result data action for {result.owner_path!r}")

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
                *self._array_declarations(plan),
                *self._string_value_declarations(plan),
                *self._string_address_declarations(plan),
                *self._direct_result_declarations(plan),
                *self._native_output_declarations(plan),
            ),
            body=(
                *self._descriptor_initializers(plan),
                *self._opaque_address_initializers(plan),
                *self._array_initializers(plan),
                *self._string_value_initializers(plan),
                *self._string_address_initializers(plan),
                *self._function_body(plan, result_name),
                *self._string_value_finalizers(plan),
                *self._string_address_finalizers(plan),
                *self._direct_result_finalizers(plan),
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
        match result.object_kind:
            case ObjectKind.NUMPY_ARRAY if action is CodegenAction.COPY_OUT:
                return self._lower_result_array_copy(plan, result)
            case ObjectKind.STRING if action is CodegenAction.COPY_OUT:
                return self._lower_result_fixed_string(plan, result)
            case ObjectKind.SCALAR if action is CodegenAction.DIRECT_VALUE:
                return self._lower_result_direct_value(plan, result)
            case _:
                raise ValueError(
                    f"Unsupported Fortran result selection for {plan.owner_path!r}: {result.object_kind!r}:{action!r}"
                )

    # String result lowering.
    def _lower_result_fixed_string(
        self,
        _plan: FunctionPlan,
        _result: ResultPlan,
    ) -> tuple[str | None, str | None]:
        """Return the C-pointer bridge shape for one copied fixed string."""
        return "result", "type(c_ptr)"

    # Ordinary-array result lowering.
    def _lower_result_array_copy(
        self,
        _plan: FunctionPlan,
        _result: ResultPlan,
    ) -> tuple[str | None, str | None]:
        """Return the C-pointer bridge shape for one copied ordinary array."""
        return "result", "type(c_ptr)"

    def _lower_result_none(
        self,
        _plan: FunctionPlan,
    ) -> tuple[str | None, str | None]:
        """Return the procedure shape of a native subroutine with no projection."""
        return None, None

    # Scalar result lowering.
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
        if plan.object_kind is ObjectKind.NUMPY_ARRAY:
            if mode not in {OptionalMode.REQUIRED, OptionalMode.NULLABLE_VALUE}:
                raise ValueError(f"Unsupported Fortran array presence mode for {plan.owner_path!r}: {mode!r}")
            return self._lower_argument_array_buffer(plan)
        if plan.object_kind is ObjectKind.STRING and plan.bridge.handoff_mode is ArgumentHandoffMode.CHARACTER_BUFFER:
            if mode not in {OptionalMode.REQUIRED, OptionalMode.NULLABLE_VALUE}:
                raise ValueError(f"Unsupported Fortran string presence mode for {plan.owner_path!r}: {mode!r}")
            return self._lower_argument_string_value(plan)
        if plan.object_kind not in {ObjectKind.SCALAR, ObjectKind.STRING}:
            raise ValueError(f"Unsupported Fortran argument object kind for {plan.owner_path!r}: {plan.object_kind!r}")
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
            case ArgumentHandoffMode.CHARACTER_BUFFER:
                return self._lower_argument_string_value(plan)
        raise ValueError(f"Unsupported Fortran argument handoff for {plan.owner_path!r}: {mode!r}")

    # Scalar argument lowering.
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

    # String argument lowering.
    def _lower_argument_string_value(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[FortranParameter, ...]:
        """Receive one C UTF-8 payload address and its runtime byte length."""
        name = plan.bridge.native_name.lower()
        return (
            FortranParameter(f"bound_{name}", "type(c_ptr)", ("value",)),
            FortranParameter(f"{name}_length", "integer(c_int64_t)", ("value",)),
        )

    # Ordinary-array argument lowering.
    def _lower_argument_array_buffer(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[FortranParameter, ...]:
        """Receive exactly the ordinary-array ABI fields named by the plan."""
        array = plan.array
        if array is None:
            raise ValueError(f"Array argument {plan.owner_path!r} has no handoff spec")
        name = plan.bridge.native_name.lower()
        return (
            FortranParameter(f"bound_{name}", "type(c_ptr)", ("value",)),
            *(
                (FortranParameter(f"{name}_rank", "integer(c_int64_t)", ("value",)),)
                if array.runtime_rank_role is not None
                else ()
            ),
            *(
                (FortranParameter(f"{name}_itemsize", "integer(c_int64_t)", ("value",)),)
                if array.itemsize_role is not None
                else ()
            ),
            *(
                FortranParameter(f"{name}_extent_{axis}", "integer(c_int64_t)", ("value",))
                for axis in range(len(array.extent_roles))
            ),
            *(
                FortranParameter(f"{name}_upper_bound_{axis}", "integer(c_int64_t)", ("value",))
                for axis in range(len(array.upper_bound_roles))
            ),
            *(
                FortranParameter(f"{name}_stride_{axis}", "integer(c_int64_t)", ("value",))
                for axis in range(len(array.stride_roles))
            ),
        )

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
    ) -> tuple[FortranAssignment | FortranCall | FortranIf | FortranSelectCase, ...]:
        result_name = self._native_direct_result_name(plan, result_name)
        assumed_rank = tuple(
            argument
            for argument in sorted(plan.arguments, key=lambda item: item.bridge.abi_position)
            if argument.array is not None and argument.array.rank is None
        )
        if assumed_rank:
            return (self._assumed_rank_call_tree(plan, assumed_rank, 0, {}, result_name),)
        optional = tuple(
            argument
            for argument in sorted(plan.arguments, key=lambda item: item.bridge.abi_position)
            if argument.bridge.optional_mode is not OptionalMode.REQUIRED
        )
        if not optional:
            return (self._native_invocation(plan, frozenset(), result_name, {}),)
        return (self._optional_call_tree(plan, optional, 0, frozenset(), result_name, {}),)

    def _optional_call_tree(
        self,
        plan: FunctionPlan,
        optional: tuple[ArgumentTransferPlan, ...],
        index: int,
        present: frozenset[str],
        result_name: str | None,
        replacements: dict[str, str],
    ) -> FortranAssignment | FortranCall | FortranIf:
        """Return an exhaustive native-call tree for optional presence states."""
        if index == len(optional):
            return self._native_invocation(plan, present, result_name, replacements)
        argument = optional[index]
        present_roles = present | {argument.owner_path}
        return FortranIf(
            condition=CodeExpression(self._presence_condition(argument)),
            body=(
                *self._present_preparation(argument),
                self._optional_call_tree(plan, optional, index + 1, present_roles, result_name, replacements),
            ),
            else_body=(self._optional_call_tree(plan, optional, index + 1, present, result_name, replacements),),
        )

    def _native_invocation(
        self,
        plan: FunctionPlan,
        present: frozenset[str],
        result_name: str | None,
        replacements: dict[str, str],
    ) -> FortranAssignment | FortranCall:
        arguments = self._native_arguments(plan, present, replacements)
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
        replacements: dict[str, str],
    ) -> tuple[CodeExpression, ...]:
        expressions = dict(self._visible_native_argument_entries(plan, present, replacements))
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
        replacements: dict[str, str],
    ) -> tuple[tuple[int, CodeExpression], ...]:
        """Return native-position entries for present Python arguments."""
        entries = []
        has_optional = self._has_optional_arguments(plan)
        for argument in plan.arguments:
            if argument.bridge.optional_mode is not OptionalMode.REQUIRED and argument.owner_path not in present:
                continue
            expression = replacements.get(argument.owner_path, self._native_argument_expression(argument))
            if has_optional:
                expression = f"{argument.bridge.native_name}={expression}"
            entries.append((argument.native_call_slot.native_position, CodeExpression(expression)))
        return tuple(entries)

    def _assumed_rank_call_tree(
        self,
        plan: FunctionPlan,
        arguments: tuple[ArgumentTransferPlan, ...],
        index: int,
        replacements: dict[str, str],
        result_name: str | None,
    ) -> FortranAssignment | FortranCall | FortranIf | FortranSelectCase:
        """Dispatch each runtime-rank array through explicit one-to-fifteen branches."""
        if index == len(arguments):
            optional = tuple(
                argument
                for argument in sorted(plan.arguments, key=lambda item: item.bridge.abi_position)
                if argument.bridge.optional_mode is not OptionalMode.REQUIRED
            )
            if optional:
                return self._optional_call_tree(plan, optional, 0, frozenset(), result_name, replacements)
            return self._native_invocation(plan, frozenset(), result_name, replacements)
        argument = arguments[index]
        name = argument.bridge.native_name.lower()
        cases = []
        for rank in range(1, 16):
            rank_name = f"{name}_rank_{rank}"
            replacements[argument.owner_path] = rank_name
            nested = self._assumed_rank_call_tree(plan, arguments, index + 1, replacements, result_name)
            del replacements[argument.owner_path]
            cases.append(
                FortranCase(
                    rank,
                    (
                        self._assumed_rank_pointer_initializer(argument, rank, rank_name),
                        nested,
                    ),
                )
            )
        cases.append(FortranCase(None, ()))
        return FortranSelectCase(CodeExpression(f"{name}_rank"), tuple(cases))

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
        if plan.bridge.handoff_mode is ArgumentHandoffMode.ARRAY_BUFFER:
            return self._array_native_argument_expression(plan)
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
        if plan.bridge.handoff_mode is ArgumentHandoffMode.ARRAY_BUFFER:
            return (self._array_pointer_initializer(plan),)
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
    ) -> tuple[FortranCall | FortranAssignment | FortranIf, ...]:
        """Copy only when completed policy requires a different native representation."""
        if plan.bridge.handoff_mode is ArgumentHandoffMode.CHARACTER_BUFFER:
            return self._string_value_initializer_nodes(plan)
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
            if argument.bridge.handoff_mode is ArgumentHandoffMode.CHARACTER_BUFFER:
                continue
            if argument.bridge.handoff_mode is ArgumentHandoffMode.ARRAY_BUFFER:
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
                and argument.object_kind is ObjectKind.SCALAR
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
                and argument.object_kind is ObjectKind.SCALAR
            )
        )

    # Ordinary-array bridge storage.
    def _array_declarations(self, plan: FunctionPlan) -> tuple[FortranDeclaration, ...]:
        """Declare typed pointer views for ordinary array buffers."""
        declarations = []
        for argument in plan.arguments:
            if argument.bridge.handoff_mode is not ArgumentHandoffMode.ARRAY_BUFFER:
                continue
            array = argument.array
            if array is None:
                raise ValueError(f"Array argument {argument.owner_path!r} is missing its handoff")
            if array.rank is None:
                declarations.extend(self._assumed_rank_array_declarations(argument))
                continue
            declarations.append(
                FortranDeclaration(
                    self._array_pointer_name(argument),
                    self._array_element_fortran_type(argument),
                    ("pointer", self._array_dimension_attribute(array.rank)),
                )
            )
        return tuple(declarations)

    def _array_initializers(self, plan: FunctionPlan) -> tuple[FortranCall, ...]:
        """Associate each completed ordinary array data/extent handoff."""
        initializers = []
        for argument in plan.arguments:
            if argument.bridge.handoff_mode is not ArgumentHandoffMode.ARRAY_BUFFER:
                continue
            if argument.bridge.optional_mode is not OptionalMode.REQUIRED:
                continue
            if argument.array is not None and argument.array.rank is None:
                continue
            initializers.append(self._array_pointer_initializer(argument))
        return tuple(initializers)

    def _array_pointer_initializer(self, argument: ArgumentTransferPlan) -> FortranCall:
        """Associate one fixed-rank array pointer using planned base extents."""
        array = argument.array
        if array is None or array.rank is None:
            raise ValueError(f"Array argument {argument.owner_path!r} requires a concrete rank")
        name = argument.bridge.native_name.lower()
        extents = [f"{name}_extent_{axis}" for axis in range(array.rank)]
        if array.order == "ORDER_C":
            extents.reverse()
        return FortranCall(
            "c_f_pointer",
            (
                CodeExpression(f"bound_{name}"),
                CodeExpression(self._array_pointer_name(argument)),
                CodeExpression(f"[{', '.join(extents)}]"),
            ),
        )

    def _assumed_rank_array_declarations(
        self,
        argument: ArgumentTransferPlan,
    ) -> tuple[FortranDeclaration, ...]:
        """Declare one readable typed pointer local for every supported runtime rank."""
        name = argument.bridge.native_name.lower()
        element_type = self._array_element_fortran_type(argument)
        return tuple(
            FortranDeclaration(
                f"{name}_rank_{rank}",
                element_type,
                ("pointer", self._array_dimension_attribute(rank)),
            )
            for rank in range(1, 16)
        )

    def _assumed_rank_pointer_initializer(
        self,
        argument: ArgumentTransferPlan,
        rank: int,
        pointer_name: str,
    ) -> FortranCall:
        """Associate one runtime-rank branch with its planned extent prefix."""
        name = argument.bridge.native_name.lower()
        extents = ", ".join(f"{name}_extent_{axis}" for axis in range(rank))
        return FortranCall(
            "c_f_pointer",
            (
                CodeExpression(f"bound_{name}"),
                CodeExpression(pointer_name),
                CodeExpression(f"[{extents}]"),
            ),
        )

    def _array_pointer_name(self, argument: ArgumentTransferPlan) -> str:
        """Name the bridge pointer, separating strided base storage visibly."""
        name = argument.bridge.native_name.lower()
        return f"{name}_base" if argument.array is not None and argument.array.contiguous is False else name

    def _array_native_argument_expression(self, argument: ArgumentTransferPlan) -> str:
        """Pass a dense pointer or the explicitly planned positive-stride slice."""
        array = argument.array
        if array is None:
            raise ValueError(f"Array argument {argument.owner_path!r} has no handoff spec")
        name = argument.bridge.native_name.lower()
        if array.rank is None:
            return name
        pointer_name = self._array_pointer_name(argument)
        if array.contiguous is not False:
            return pointer_name
        slices = (f"1:{name}_upper_bound_{axis} + 1:{name}_stride_{axis}" for axis in range(array.rank))
        return f"{pointer_name}({', '.join(slices)})"

    def _array_element_fortran_type(self, argument: ArgumentTransferPlan) -> str:
        """Return the completed primitive or fixed-width character element type."""
        array = argument.array
        if argument.datatype_family is DatatypeFamily.STRING:
            if array is None or array.itemsize is None or array.itemsize <= 0:
                raise ValueError(f"Character array {argument.owner_path!r} has no fixed itemsize")
            return f"character(kind=c_char, len={array.itemsize})"
        return PrimitiveScalarTypeRegistry.type_for(argument.semantic_type_name).fortran_spelling

    def _array_dimension_attribute(self, rank: int) -> str:
        """Spell one explicit-rank deferred-shape pointer attribute."""
        return f"dimension({', '.join(':' for _ in range(rank))})"

    # String address bridge storage.
    def _string_address_declarations(self, plan: FunctionPlan) -> tuple[FortranDeclaration, ...]:
        """Declare fixed helper-local character storage for address boundaries."""
        declarations = []
        for argument in self._string_address_arguments(plan):
            name = argument.bridge.native_name.lower()
            length = self._string_address_length(argument)
            declarations.extend(
                (
                    FortranDeclaration(
                        f"{name}_bytes",
                        "character(kind=c_char)",
                        ("pointer", "dimension(:)"),
                    ),
                    FortranDeclaration(name, f"character(kind=c_char, len={length})"),
                )
            )
        return tuple(declarations)

    def _string_address_initializers(
        self,
        plan: FunctionPlan,
    ) -> tuple[FortranCall | FortranAssignment, ...]:
        """Associate fixed-width bytes and materialize native character locals."""
        nodes = []
        for argument in self._string_address_arguments(plan):
            name = argument.bridge.native_name.lower()
            length = self._string_address_length(argument)
            nodes.extend(
                (
                    FortranCall(
                        "c_f_pointer",
                        (
                            CodeExpression(f"bound_{name}"),
                            CodeExpression(f"{name}_bytes"),
                            CodeExpression(f"[{length}]"),
                        ),
                    ),
                    FortranAssignment(name, CodeExpression(f"transfer({name}_bytes, {name})")),
                )
            )
        return tuple(nodes)

    def _string_address_finalizers(self, plan: FunctionPlan) -> tuple[FortranAssignment, ...]:
        """Copy every mutated fixed character byte back to caller storage."""
        nodes = []
        for argument in self._string_address_arguments(plan):
            if not argument.mutates_native:
                continue
            name = argument.bridge.native_name.lower()
            length = self._string_address_length(argument)
            nodes.append(
                FortranAssignment(
                    f"{name}_bytes(1:{length})",
                    CodeExpression(f"transfer({name}, {name}_bytes(1:{length}))"),
                )
            )
        return tuple(nodes)

    def _string_address_arguments(self, plan: FunctionPlan) -> tuple[ArgumentTransferPlan, ...]:
        """Return address-shaped strings selected by completed plan facts."""
        return tuple(
            argument
            for argument in plan.arguments
            if argument.object_kind is ObjectKind.STRING
            and argument.bridge.handoff_mode is ArgumentHandoffMode.OPAQUE_ADDRESS
            and argument.bridge.data_action is BridgeDataAction.COPY_REPRESENTATION
        )

    def _string_address_length(self, plan: ArgumentTransferPlan) -> int:
        """Return the fixed extent already completed in the shared plan."""
        if plan.character_length is None or plan.character_length <= 0:
            raise ValueError(f"String address {plan.owner_path!r} is missing a fixed character length")
        return plan.character_length

    # String value bridge storage.
    def _string_value_declarations(self, plan: FunctionPlan) -> tuple[FortranDeclaration, ...]:
        """Return bridge-local character storage for string-value inputs."""
        declarations = []
        for argument in plan.arguments:
            if argument.bridge.handoff_mode is not ArgumentHandoffMode.CHARACTER_BUFFER:
                continue
            name = argument.bridge.native_name.lower()
            declarations.extend(
                (
                    FortranDeclaration(
                        f"{name}_bytes",
                        "character(kind=c_char)",
                        ("pointer", "dimension(:)"),
                    ),
                    FortranDeclaration(name, f"character(kind=c_char, len={name}_length)"),
                )
            )
        return tuple(declarations)

    def _string_value_initializers(
        self,
        plan: FunctionPlan,
    ) -> tuple[FortranCall | FortranAssignment, ...]:
        """Associate and copy C bytes only for completed representation-copy inputs."""
        nodes = []
        for argument in plan.arguments:
            if argument.bridge.handoff_mode is not ArgumentHandoffMode.CHARACTER_BUFFER:
                continue
            if argument.bridge.optional_mode is not OptionalMode.REQUIRED:
                continue
            if argument.bridge.data_action is not BridgeDataAction.COPY_REPRESENTATION:
                raise ValueError(f"String input {argument.owner_path!r} is missing representation-copy policy")
            nodes.extend(self._string_value_initializer_nodes(argument))
        return tuple(nodes)

    def _string_value_initializer_nodes(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[FortranCall | FortranAssignment, ...]:
        """Associate and materialize one present string payload."""
        name = plan.bridge.native_name.lower()
        extent = f"{name}_length + 1" if plan.bridge.codegen_action is CodegenAction.COPY_IN_OUT else f"{name}_length"
        source = (
            f"{name}_bytes(1:{name}_length)"
            if plan.bridge.codegen_action is CodegenAction.COPY_IN_OUT
            else f"{name}_bytes"
        )
        return (
            FortranCall(
                "c_f_pointer",
                (
                    CodeExpression(f"bound_{name}"),
                    CodeExpression(f"{name}_bytes"),
                    CodeExpression(f"[{extent}]"),
                ),
            ),
            FortranAssignment(name, CodeExpression(f"transfer({source}, {name})")),
        )

    def _string_value_finalizers(
        self,
        plan: FunctionPlan,
    ) -> tuple[FortranAssignment | FortranIf, ...]:
        """Dispatch completed post-call string copyback actions."""
        nodes = []
        for argument in plan.arguments:
            if argument.bridge.handoff_mode is not ArgumentHandoffMode.CHARACTER_BUFFER:
                continue
            action = argument.bridge.codegen_action
            if action is CodegenAction.CALL_LOCAL_INPUT:
                continue
            if action is CodegenAction.COPY_IN_OUT:
                copyback = self._lower_argument_string_copyback(argument)
                if argument.bridge.optional_mode is OptionalMode.NULLABLE_VALUE:
                    name = argument.bridge.native_name.lower()
                    nodes.append(FortranIf(CodeExpression(f"c_associated(bound_{name})"), body=copyback))
                else:
                    nodes.extend(copyback)
                continue
            raise ValueError(f"Unsupported Fortran string finalizer for {argument.owner_path!r}: {action!r}")
        return tuple(nodes)

    def _lower_argument_string_copyback(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[FortranAssignment, ...]:
        """Copy one complete native character value back to binding storage."""
        name = plan.bridge.native_name.lower()
        return (
            FortranAssignment(
                f"{name}_bytes(1:{name}_length)",
                CodeExpression(f"transfer({name}, {name}_bytes(1:{name}_length))"),
            ),
            FortranAssignment(f"{name}_bytes({name}_length + 1)", CodeExpression("c_null_char")),
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
            if slot.object_kind in {ObjectKind.STRING, ObjectKind.NUMPY_ARRAY}:
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
                declarations.extend(self._representation_copy_output_declarations(plan, slot))
                continue
            raise ValueError(
                f"Unsupported native-output bridge data action for {slot.owner_path!r}: {slot.bridge_data_action!r}"
            )
        return tuple(declarations)

    def _direct_result_declarations(self, plan: FunctionPlan) -> tuple[FortranDeclaration, ...]:
        """Declare helper-local native storage for one copied direct result."""
        result = self._direct_result(plan)
        if result is None:
            return ()
        if result.object_kind is ObjectKind.NUMPY_ARRAY:
            return self._direct_array_result_declarations(plan, result)
        if result.object_kind is not ObjectKind.STRING:
            return ()
        length = self._string_result_length(result)
        return (
            FortranDeclaration("result_value", f"character(kind=c_char, len={length})"),
            FortranDeclaration(
                "result_copy",
                "character(kind=c_char)",
                ("pointer", "dimension(:)"),
            ),
        )

    # Ordinary-array result storage.
    def _direct_array_result_declarations(
        self,
        plan: FunctionPlan,
        result: ResultPlan,
    ) -> tuple[FortranDeclaration, ...]:
        """Declare typed native and contiguous-copy storage for one array result."""
        shape = self._array_result_shape(plan, result)
        element_type = self._array_result_element_type(result)
        copy_type = "character(kind=c_char)" if result.datatype_family is DatatypeFamily.STRING else element_type
        return (
            FortranDeclaration("result_value", element_type, (f"dimension({', '.join(shape)})",)),
            FortranDeclaration("result_copy", copy_type, ("pointer", "dimension(:)")),
        )

    def _direct_result_finalizers(
        self,
        plan: FunctionPlan,
    ) -> tuple[FortranAssignment | FortranIf, ...]:
        """Copy one direct result into bridge-owned C storage."""
        result = self._direct_result(plan)
        if result is None:
            return ()
        if result.object_kind is ObjectKind.NUMPY_ARRAY:
            if result.array is None:
                raise ValueError(f"Array result {result.owner_path!r} has no shape plan")
            return self._fixed_array_copy_nodes(
                result.array.order,
                result.array.rank,
                itemsize=self._array_result_itemsize(result),
                target_name="result",
                value_name="result_value",
                copy_name="result_copy",
            )
        if result.object_kind is not ObjectKind.STRING:
            return ()
        return self._fixed_string_copy_nodes(
            length=self._string_result_length(result),
            target_name="result",
            value_name="result_value",
            copy_name="result_copy",
        )

    def _representation_copy_output_declarations(
        self,
        plan: FunctionPlan,
        slot: NativeCallSlotPlan,
    ) -> tuple[FortranDeclaration, ...]:
        """Declare storage only for one justified representation-copy output."""
        if slot.object_kind is ObjectKind.NUMPY_ARRAY:
            return self._array_copy_output_declarations(plan, slot)
        if slot.object_kind is not ObjectKind.STRING:
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

    def _array_copy_output_declarations(
        self,
        plan: FunctionPlan,
        slot: NativeCallSlotPlan,
    ) -> tuple[FortranDeclaration, ...]:
        """Declare typed native and contiguous-copy storage for one hidden array."""
        shape = self._array_output_shape(plan, slot)
        if slot.semantic_type_name is None:
            raise ValueError(f"Missing array output datatype for {slot.owner_path!r}")
        element_type = self._array_result_element_type(slot)
        copy_type = "character(kind=c_char)" if slot.datatype_family is DatatypeFamily.STRING else element_type
        name = slot.native_name.lower()
        return (
            FortranDeclaration(f"{name}_value", element_type, (f"dimension({', '.join(shape)})",)),
            FortranDeclaration(f"{name}_copy", copy_type, ("pointer", "dimension(:)")),
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
                nodes.extend(self._lower_native_output_representation_copy(plan, slot))
                continue
            raise ValueError(
                f"Unsupported native-output bridge data action for {slot.owner_path!r}: {slot.bridge_data_action!r}"
            )
        return tuple(nodes)

    def _lower_native_output_representation_copy(
        self,
        plan: FunctionPlan,
        slot: NativeCallSlotPlan,
    ) -> tuple[FortranAssignment | FortranIf, ...]:
        """Copy one native output only through the explicit policy permission."""
        if slot.object_kind is ObjectKind.NUMPY_ARRAY:
            if slot.array is None:
                raise ValueError(f"Array output {slot.owner_path!r} has no shape plan")
            name = slot.native_name.lower()
            return self._fixed_array_copy_nodes(
                slot.array.order,
                slot.array.rank,
                itemsize=self._array_result_itemsize(slot),
                target_name=name,
                value_name=f"{name}_value",
                copy_name=f"{name}_copy",
            )
        if slot.object_kind is not ObjectKind.STRING:
            raise ValueError(f"Unsupported representation-copy output for {slot.owner_path!r}")
        name = slot.native_name.lower()
        value_name = self._native_output_value_name(slot)
        copy_name = f"{name}_copy"
        length = self._string_output_length(slot)
        return self._fixed_string_copy_nodes(
            length=length,
            target_name=name,
            value_name=value_name,
            copy_name=copy_name,
        )

    def _fixed_array_copy_nodes(
        self,
        order: str | None,
        rank: int | None,
        *,
        itemsize: int | None,
        target_name: str,
        value_name: str,
        copy_name: str,
    ) -> tuple[FortranAssignment | FortranIf, ...]:
        """Allocate and fill one detached contiguous ordinary-array copy."""
        if rank is None or rank <= 0:
            raise ValueError(f"Array copy {value_name!r} requires a fixed positive rank")
        if order == "ORDER_C" and rank > 1:
            raise ValueError(f"Array copy {value_name!r} requires Fortran element order")
        if itemsize is not None:
            return self._fixed_character_array_copy_nodes(
                itemsize,
                target_name=target_name,
                value_name=value_name,
                copy_name=copy_name,
            )
        return (
            FortranAssignment(
                target_name,
                CodeExpression(f"c_malloc(max(1_c_size_t, c_sizeof({value_name})))"),
            ),
            FortranIf(
                CodeExpression(f"c_associated({target_name})"),
                body=(
                    FortranCall(
                        "c_f_pointer",
                        (
                            CodeExpression(target_name),
                            CodeExpression(copy_name),
                            CodeExpression(f"[size({value_name})]"),
                        ),
                    ),
                    FortranAssignment(
                        copy_name,
                        CodeExpression(f"reshape({value_name}, [size({value_name})])"),
                    ),
                ),
            ),
        )

    def _fixed_character_array_copy_nodes(
        self,
        itemsize: int,
        *,
        target_name: str,
        value_name: str,
        copy_name: str,
    ) -> tuple[FortranAssignment | FortranIf, ...]:
        """Allocate and copy one fixed-width character array as raw bytes."""
        if itemsize <= 0:
            raise ValueError(f"Character array copy {value_name!r} requires a fixed positive itemsize")
        byte_count = f"{itemsize} * size({value_name})"
        return (
            FortranAssignment(
                target_name,
                CodeExpression(f"c_malloc(max(1_c_size_t, {itemsize}_c_size_t * size({value_name}, kind=c_size_t)))"),
            ),
            FortranIf(
                CodeExpression(f"c_associated({target_name})"),
                body=(
                    FortranCall(
                        "c_f_pointer",
                        (
                            CodeExpression(target_name),
                            CodeExpression(copy_name),
                            CodeExpression(f"[{byte_count}]"),
                        ),
                    ),
                    FortranAssignment(
                        copy_name,
                        CodeExpression(f"transfer({value_name}, {copy_name}, {byte_count})"),
                    ),
                ),
            ),
        )

    def _array_result_element_type(self, plan: ResultPlan | NativeCallSlotPlan) -> str:
        """Return the completed numeric or fixed-width character element type."""
        if plan.datatype_family is DatatypeFamily.STRING:
            itemsize = self._array_result_itemsize(plan)
            if itemsize is None:
                raise ValueError(f"Character array result {plan.owner_path!r} has no itemsize")
            return f"character(kind=c_char, len={itemsize})"
        if plan.semantic_type_name is None:
            raise ValueError(f"Array result {plan.owner_path!r} has no element type")
        return PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name).fortran_spelling

    def _array_result_itemsize(self, plan: ResultPlan | NativeCallSlotPlan) -> int | None:
        """Return a character-array itemsize after object-kind dispatch."""
        if plan.datatype_family is not DatatypeFamily.STRING:
            return None
        if plan.array is None or plan.array.itemsize is None or plan.array.itemsize <= 0:
            raise ValueError(f"Character array result {plan.owner_path!r} has no fixed itemsize")
        return plan.array.itemsize

    # String result storage.
    def _fixed_string_copy_nodes(
        self,
        *,
        length: int,
        target_name: str,
        value_name: str,
        copy_name: str,
    ) -> tuple[FortranAssignment | FortranIf, ...]:
        """Allocate and fill one justified NUL-terminated fixed string copy."""
        c_length = length + 1
        return (
            FortranAssignment(target_name, CodeExpression(f"c_malloc({c_length}_c_size_t)")),
            FortranIf(
                CodeExpression(f"c_associated({target_name})"),
                body=(
                    FortranCall(
                        "c_f_pointer",
                        (
                            CodeExpression(target_name),
                            CodeExpression(copy_name),
                            CodeExpression(f"[{c_length}]"),
                        ),
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
        return f"{name}_value" if slot.object_kind in {ObjectKind.STRING, ObjectKind.NUMPY_ARRAY} else name

    def _string_output_length(self, slot: NativeCallSlotPlan) -> int:
        if slot.character_length is None or slot.character_length <= 0:
            raise ValueError(f"String output {slot.owner_path!r} is missing a fixed character length")
        return slot.character_length

    def _string_result_length(self, result: ResultPlan) -> int:
        if result.character_length is None or result.character_length <= 0:
            raise ValueError(f"String result {result.owner_path!r} is missing a fixed character length")
        return result.character_length

    def _native_direct_result_name(self, plan: FunctionPlan, result_name: str | None) -> str | None:
        result = self._direct_result(plan)
        if result is not None and result.object_kind in {ObjectKind.STRING, ObjectKind.NUMPY_ARRAY}:
            return "result_value"
        return result_name

    def _bridge_result_type(self, plan: FunctionPlan, result: ResultPlan | None = None) -> str:
        result = result or self._direct_result(plan)
        if result is None:
            raise ValueError(f"{plan.owner_path!r} native function has no result plan")
        if result.object_kind in {ObjectKind.STRING, ObjectKind.NUMPY_ARRAY}:
            return "type(c_ptr)"
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
        if not self._needs_allocator_interface(plan):
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

    def _needs_allocator_interface(self, plan: ModulePlan) -> bool:
        """Return whether module snapshots or function copies allocate storage."""
        return self._needs_snapshot_allocator(plan) or self._needs_function_copy_allocator(plan)

    def _needs_snapshot_allocator(self, plan: ModulePlan) -> bool:
        """Return whether a module-variable getter produces a detached snapshot."""
        return any(
            variable.bridge.getter_action is ModuleGetterAction.NULLABLE_SNAPSHOT for variable in self._variables(plan)
        )

    def _needs_function_copy_allocator(self, plan: ModulePlan) -> bool:
        """Return whether any function copies an array or string result."""
        return any(self._function_needs_copy_allocator(function) for function in self._functions(plan))

    def _function_needs_copy_allocator(self, function: FunctionPlan) -> bool:
        """Return whether one function owns a result-copy allocation."""
        return self._result_plans_need_allocator(function) or self._native_result_slots_need_allocator(function)

    def _result_plans_need_allocator(self, function: FunctionPlan) -> bool:
        """Return whether one Python result is an array or string copy."""
        return any(result.object_kind in {ObjectKind.STRING, ObjectKind.NUMPY_ARRAY} for result in function.results)

    def _native_result_slots_need_allocator(self, function: FunctionPlan) -> bool:
        """Return whether one hidden native result is an array or string copy."""
        return any(
            slot.object_kind in {ObjectKind.STRING, ObjectKind.NUMPY_ARRAY}
            for slot in function.native_call_slots
            if slot.source_kind == "result"
        )

    def _external_interface_procedure(self, plan: FunctionPlan) -> FortranInterfaceProcedure:
        parameters = tuple(
            self._external_interface_parameter(argument)
            for argument in sorted(plan.arguments, key=lambda item: item.native_position)
        )
        imports = tuple(dict.fromkeys(self._iso_symbol(argument.semantic_type_name) for argument in plan.arguments))
        result_name = None if plan.bridge.native_is_subroutine else "native_result"
        direct_result = self._direct_result(plan)
        result_type = self._native_result_type(plan, direct_result) if result_name is not None else None
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

    def _native_result_type(self, plan: FunctionPlan, result: ResultPlan | None) -> str:
        """Return the native procedure result type inside an external interface."""
        if result is None:
            raise ValueError("External native function is missing its direct result plan")
        if result.object_kind is ObjectKind.NUMPY_ARRAY:
            shape = self._array_result_shape(plan, result)
            return f"{self._array_result_element_type(result)}, dimension({', '.join(shape)})"
        if result.object_kind is ObjectKind.STRING:
            return f"character(kind=c_char, len={self._string_result_length(result)})"
        return PrimitiveScalarTypeRegistry.type_for(result.semantic_type_name).fortran_spelling

    def _external_interface_parameter(self, argument: ArgumentTransferPlan) -> FortranParameter:
        """Return the native external dummy declaration for one planned argument."""
        attributes = ("optional",) if argument.bridge.optional_mode is not OptionalMode.REQUIRED else ()
        if argument.object_kind is ObjectKind.NUMPY_ARRAY:
            array = argument.array
            if array is None:
                raise ValueError(f"Array argument {argument.owner_path!r} has no shape plan")
            element_type = self._array_element_fortran_type(argument)
            dimension = ".." if array.rank is None else ", ".join(":" for _ in range(array.rank))
            return FortranParameter(
                argument.bridge.native_name.lower(),
                element_type,
                (*attributes, f"dimension({dimension})"),
            )
        if argument.object_kind is ObjectKind.STRING:
            length = argument.native_call_slot.character_length
            length_text = "*" if length is None else str(length)
            return FortranParameter(
                argument.bridge.native_name.lower(),
                f"character(kind=c_char, len={length_text})",
                attributes,
            )
        return FortranParameter(
            argument.bridge.native_name.lower(),
            PrimitiveScalarTypeRegistry.type_for(argument.semantic_type_name).fortran_spelling,
            attributes,
        )

    # Ordinary-array result-shape lowering.
    def _array_result_shape(self, plan: FunctionPlan, result: ResultPlan) -> tuple[str, ...]:
        """Lower one result shape through the plan's native scalar roles."""
        if result.array is None:
            raise ValueError(f"Array result {result.owner_path!r} has no shape plan")
        return self._array_result_shape_from_roles(result.array, plan.arguments)

    def _array_output_shape(self, plan: FunctionPlan, slot: NativeCallSlotPlan) -> tuple[str, ...]:
        """Lower one hidden-output shape through the plan's native scalar roles."""
        if slot.array is None:
            raise ValueError(f"Array output {slot.owner_path!r} has no shape plan")
        return self._array_result_shape_from_roles(slot.array, plan.arguments)

    def _array_result_shape_from_roles(self, array, arguments) -> tuple[str, ...]:
        """Replace validated shape references with their native dummy names."""
        lowered_shape = []
        role_names = {argument.binding.handoff_role: argument.bridge.native_name.lower() for argument in arguments}
        for axis, expression in enumerate(array.shape):
            lowered = expression
            for role in array.extent_reference_roles[axis]:
                native_name = role_names.get(role)
                if native_name is None:
                    reference_name = role.rsplit(".", 1)[-1].split(":", 1)[0]
                    native_name = reference_name
                reference_name = role.rsplit(".", 1)[-1].split(":", 1)[0]
                lowered = re.sub(rf"\b{re.escape(reference_name)}\b", native_name, lowered)
            lowered_shape.append(lowered)
        return tuple(lowered_shape)

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
            "String": "c_char",
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
            "c_sizeof",
        )
