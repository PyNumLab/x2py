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
    NativeArrayDescriptorKind,
    NativeArrayExtractionAction,
    NativeArrayOperation,
    NativeDescriptorHandoffABI,
    OptionalMode,
    TransformationLayer,
)
from x2py.wrapper_codegen.nodes import (
    CodeExpression,
    FortranAllocate,
    FortranAssignment,
    FortranCall,
    FortranCase,
    FortranDeclaration,
    FortranDeallocate,
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
    ArrayHandoffPlan,
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
        self._require_optional_literal_combination_supported(function)
        for argument in function.arguments:
            self._require_argument_supported(argument)
        for result in function.results:
            self._require_plan_result_supported(result)
        for slot in function.native_call_slots:
            self._require_native_result_supported(function, slot)

    def _require_optional_literal_combination_supported(self, function: FunctionPlan) -> None:
        """Reject the one unsupported optional/literal native call combination."""
        if self._has_optional_arguments(function) and any(
            slot.source_kind == "literal" for slot in function.native_call_slots
        ):
            raise ValueError(f"{function.owner_path!r} mixes optional scalar arguments with hidden literals")

    def _require_plan_result_supported(self, result: ResultPlan) -> None:
        """Dispatch one binding-visible result by completed object kind."""
        if result.scalar_descriptor is not None:
            self._require_scalar_descriptor_plan_result_supported(result)
            return
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

    def _require_argument_supported(self, argument: ArgumentTransferPlan) -> None:
        """Reject one unsupported native argument action."""
        if any(item.layer is TransformationLayer.BRIDGE for item in argument.transformations):
            raise ValueError(f"Unsupported bridge transformation for {argument.owner_path!r}")
        supported = {
            NativeBarrierAction.PASS_VALUE,
            NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS,
            NativeBarrierAction.PASS_RAW_ADDRESS,
            NativeBarrierAction.PASS_STORAGE_ADDRESS,
            NativeBarrierAction.PASS_ARRAY_BUFFER,
            NativeBarrierAction.PASS_NATIVE_DESCRIPTOR,
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
        if slot.scalar_descriptor is not None:
            self._require_scalar_descriptor_native_result_supported(function, slot)
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

    def _require_scalar_descriptor_native_result_supported(
        self,
        function: FunctionPlan,
        slot: NativeCallSlotPlan,
    ) -> None:
        """Require one nullable rank-zero descriptor output slot."""
        if not any(result.native_call_slot is slot for result in function.results):
            raise ValueError(f"Unclaimed Fortran scalar descriptor output for {slot.owner_path!r}")
        self._require_scalar_descriptor_copy_supported(slot, label="output")

    def _require_scalar_descriptor_plan_result_supported(self, result: ResultPlan) -> None:
        """Require one nullable rank-zero descriptor result copy."""
        self._require_scalar_descriptor_copy_supported(result, label="result")

    def _require_scalar_descriptor_copy_supported(
        self,
        result: ResultPlan | NativeCallSlotPlan,
        *,
        label: str,
    ) -> None:
        """Require the shared scalar/string nullable descriptor copy shape."""
        descriptor = result.scalar_descriptor
        if descriptor is None or not descriptor.nullable:
            raise ValueError(f"Unsupported Fortran scalar descriptor {label} for {result.owner_path!r}")
        data_action = result.bridge.data_action if isinstance(result, ResultPlan) else result.bridge_data_action
        if data_action is not BridgeDataAction.COPY_REPRESENTATION:
            raise ValueError(f"Unsupported Fortran scalar descriptor action for {result.owner_path!r}")
        if result.object_kind is ObjectKind.STRING:
            if not descriptor.runtime_length:
                raise ValueError(f"Missing Fortran runtime string length for {result.owner_path!r}")
            return
        if result.object_kind is not ObjectKind.SCALAR or descriptor.runtime_length:
            raise ValueError(f"Unsupported Fortran scalar descriptor family for {result.owner_path!r}")
        if result.datatype_family is not DatatypeFamily.STRING:
            PrimitiveScalarTypeRegistry.type_for(result.semantic_type_name)

    # Ordinary-array and native-array-handle support checks.
    def _require_array_argument_supported(self, argument: ArgumentTransferPlan) -> None:
        """Dispatch one completed array buffer or raw-address view."""
        if argument.native_array_handle is not None:
            self._require_native_array_handle_argument_supported(argument)
            return
        if argument.binding.python_action is PythonBarrierAction.RAW_ADDRESS:
            self._require_raw_array_argument_supported(argument)
            return
        self._require_array_buffer_argument_supported(argument)

    def _require_native_array_handle_argument_supported(self, argument: ArgumentTransferPlan) -> None:
        """Require one typed standard-descriptor bridge argument."""
        handle = argument.native_array_handle
        if handle is None or handle.array.rank is None:
            raise ValueError(f"Unsupported Fortran native array handle for {argument.owner_path!r}")
        if argument.bridge.handoff_mode is not ArgumentHandoffMode.NATIVE_DESCRIPTOR:
            raise ValueError(f"Unsupported Fortran native descriptor handoff for {argument.owner_path!r}")
        if handle.handoff.abi not in {
            NativeDescriptorHandoffABI.FACT_PACKED_CALL_LOCAL,
            NativeDescriptorHandoffABI.DIRECT_STANDARD_DESCRIPTOR,
        }:
            raise ValueError(f"Unsupported Fortran native descriptor ABI for {argument.owner_path!r}")
        if argument.datatype_family is not DatatypeFamily.STRING:
            PrimitiveScalarTypeRegistry.type_for(argument.semantic_type_name)

    def _require_array_buffer_argument_supported(self, argument: ArgumentTransferPlan) -> None:
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

    def _require_raw_array_argument_supported(self, argument: ArgumentTransferPlan) -> None:
        """Require one opaque address with a concrete dense pointee view."""
        self._require_raw_array_shape_supported(argument)
        self._require_raw_array_actions_supported(argument)
        self._require_raw_array_element_supported(argument)

    def _require_raw_array_shape_supported(self, argument: ArgumentTransferPlan) -> None:
        """Require concrete dense raw-pointee shape facts."""
        array = argument.array
        if array is None or array.rank is None or not 1 <= array.rank <= 15:
            raise ValueError(f"Unsupported Fortran raw array rank for {argument.owner_path!r}")
        if array.contiguous is not True or array.category != "raw_address":
            raise ValueError(f"Unsupported Fortran raw array layout for {argument.owner_path!r}")

    def _require_raw_array_actions_supported(self, argument: ArgumentTransferPlan) -> None:
        """Require the opaque non-copying raw-address action pair."""
        if argument.bridge.handoff_mode is not ArgumentHandoffMode.OPAQUE_ADDRESS:
            raise ValueError(f"Unsupported Fortran raw array handoff for {argument.owner_path!r}")
        if argument.bridge.data_action is not BridgeDataAction.ASSOCIATE_VIEW:
            raise ValueError(f"Unsupported Fortran raw array data action for {argument.owner_path!r}")

    def _require_raw_array_element_supported(self, argument: ArgumentTransferPlan) -> None:
        """Require one supported primitive or fixed-character pointee element."""
        array = argument.array
        if argument.datatype_family is DatatypeFamily.STRING:
            if array is None or array.itemsize is None or array.itemsize <= 0:
                raise ValueError(f"Unsupported Fortran raw character array for {argument.owner_path!r}")
            return
        PrimitiveScalarTypeRegistry.type_for(argument.semantic_type_name)

    def _require_array_plan_result_supported(self, result: ResultPlan) -> None:
        """Require one fixed-shape ordinary array copy result."""
        if self._is_owned_native_array_result(result):
            self._require_owned_native_array_result_supported(result)
            return
        self._require_array_plan_result_shape_supported(result)
        self._require_array_plan_result_action_supported(result)
        self._require_array_plan_result_type_supported(result)

    def _require_array_plan_result_shape_supported(self, result: ResultPlan) -> None:
        """Require one fixed-rank non-C-oriented direct result shape."""
        array = result.array
        if array is None or array.rank is None or not 1 <= array.rank <= 15:
            raise ValueError(f"Unsupported Fortran array result rank for {result.owner_path!r}")
        if array.native_order == "ORDER_C" and array.rank > 1:
            raise ValueError(f"Unsupported Fortran array result order for {result.owner_path!r}")

    def _require_array_plan_result_action_supported(self, result: ResultPlan) -> None:
        """Require the explicit representation-copy action for one direct array."""
        if result.bridge.data_action is not BridgeDataAction.COPY_REPRESENTATION:
            raise ValueError(f"Unsupported Fortran array result data action for {result.owner_path!r}")

    def _require_array_plan_result_type_supported(self, result: ResultPlan) -> None:
        """Require one supported primitive or fixed-character result element."""
        array = result.array
        if result.datatype_family is DatatypeFamily.STRING:
            if array is None or array.itemsize is None or array.itemsize <= 0:
                raise ValueError(f"Unsupported Fortran character array result for {result.owner_path!r}")
            return
        PrimitiveScalarTypeRegistry.type_for(result.semantic_type_name)

    def _require_array_result_supported(self, function: FunctionPlan, slot: NativeCallSlotPlan) -> None:
        """Require one hidden fixed-shape ordinary array copy result."""
        if self._is_owned_native_array_slot(slot):
            result = next((item for item in function.results if item.native_call_slot is slot), None)
            if result is None:
                raise ValueError(f"Unclaimed Fortran native array handle output for {slot.owner_path!r}")
            self._require_owned_native_array_result_supported(result)
            return
        self._require_array_result_shape_supported(slot)
        self._require_array_result_action_supported(slot)
        self._require_array_result_type_supported(function, slot)

    def _require_owned_native_array_result_supported(self, result: ResultPlan) -> None:
        """Require one wrapper-owned allocatable standard descriptor result."""
        handle = result.native_array_handle
        if (
            handle is None
            or handle.descriptor_kind is not NativeArrayDescriptorKind.ALLOCATABLE
            or handle.handoff.abi is not NativeDescriptorHandoffABI.OWNED_RESULT_STORAGE
            or handle.array.rank is None
        ):
            raise ValueError(f"Unsupported Fortran owned native array result for {result.owner_path!r}")
        if result.datatype_family is not DatatypeFamily.STRING:
            PrimitiveScalarTypeRegistry.type_for(result.semantic_type_name)

    def _require_array_result_shape_supported(self, slot: NativeCallSlotPlan) -> None:
        """Require one fixed-rank non-C-oriented array result shape."""
        array = slot.array
        if array is None or array.rank is None or not 1 <= array.rank <= 15:
            raise ValueError(f"Unsupported Fortran array output rank for {slot.owner_path!r}")
        if array.native_order == "ORDER_C" and array.rank > 1:
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
        if variable.binding.getter_action is ModuleGetterAction.NATIVE_ARRAY_HANDLE:
            handle = variable.native_array_handle
            if handle is None or handle.array.rank is None:
                raise ValueError(f"Unsupported Fortran module handle for {variable.owner_path!r}")
            if variable.datatype_family is not DatatypeFamily.STRING:
                PrimitiveScalarTypeRegistry.type_for(variable.semantic_type_name)
            return
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
            *(
                procedure
                for function in plan.functions
                for procedure in (
                    self.visit(function),
                    *self._scalar_descriptor_result_collectors(function),
                )
            ),
            *(procedure for variable in plan.variables for procedure in self.visit(variable)),
        )

    def _visit_FunctionPlan(self, plan: FunctionPlan) -> FortranFunction:
        """Recursively assemble one complete bridge procedure."""
        result_name, result_type = self._lower_result(plan)
        owned_direct_result = self._owned_direct_result(plan)
        parameters = tuple(
            parameter
            for argument in sorted(plan.arguments, key=lambda item: item.bridge.abi_position)
            for parameter in self.visit(argument)
        )
        parameters = (
            *parameters,
            *self._native_output_parameters(plan),
            *self._owned_direct_result_parameters(owned_direct_result),
            *self._scalar_descriptor_direct_result_parameters(plan),
        )
        bridge_name = self._bridge_function_name(plan)
        is_subroutine = plan.bridge.native_is_subroutine or owned_direct_result is not None
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
                *self._raw_array_address_declarations(plan),
                *self._string_value_declarations(plan),
                *self._string_address_declarations(plan),
                *self._direct_result_declarations(plan),
                *self._native_output_declarations(plan),
            ),
            body=(
                *self._descriptor_initializers(plan),
                *self._required_descriptor_initializers(plan),
                *self._opaque_address_initializers(plan),
                *self._array_initializers(plan),
                *self._raw_array_address_initializers(plan),
                *self._string_value_initializers(plan),
                *self._string_address_initializers(plan),
                *self._function_body(plan, result_name),
                *self._required_descriptor_finalizers(plan),
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
        if result.scalar_descriptor is not None:
            return self._lower_result_scalar_descriptor(plan, result)
        if self._is_owned_native_array_result(result):
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

    # Nullable rank-zero descriptor result lowering.
    def _lower_result_scalar_descriptor(
        self,
        _plan: FunctionPlan,
        _result: ResultPlan,
    ) -> tuple[str | None, str | None]:
        """Return the detached-copy C-pointer bridge shape."""
        return "result", "type(c_ptr)"

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

    def _owned_direct_result_parameters(
        self,
        result: ResultPlan | None,
    ) -> tuple[FortranParameter, ...]:
        """Expose persistent binding-owned descriptor storage as one output dummy."""
        if result is None:
            return ()
        handle = result.native_array_handle
        if handle is None or handle.array.rank is None:
            raise ValueError(f"Owned result {result.owner_path!r} has no descriptor rank")
        if self._is_owned_deferred_character_result(result):
            return (
                FortranParameter("result", "type(c_ptr)"),
                FortranParameter("result_itemsize", "integer(c_int64_t)"),
                *(FortranParameter(f"result_extent_{axis}", "integer(c_int64_t)") for axis in range(handle.array.rank)),
            )
        dimension = self._array_dimension_attribute(handle.array.rank)
        return (
            FortranParameter(
                "result",
                self._array_result_element_type(result),
                ("allocatable", dimension, "intent(out)"),
            ),
        )

    def _scalar_descriptor_direct_result_parameters(
        self,
        plan: FunctionPlan,
    ) -> tuple[FortranParameter, ...]:
        """Expose runtime metadata associated with a direct descriptor result."""
        result = self._direct_result(plan)
        if result is None or result.scalar_descriptor is None:
            return ()
        parameters = [FortranParameter("result_present", "integer(c_int)")]
        if result.scalar_descriptor.runtime_length:
            parameters.append(FortranParameter("result_length", "integer(c_int64_t)"))
        return tuple(parameters)

    def _visit_ModuleVariablePlan(self, plan: ModuleVariablePlan) -> tuple[FortranFunction, ...]:
        """Lower bridge-owned getter and setter actions into procedures."""
        if plan.binding.getter_action is ModuleGetterAction.NATIVE_ARRAY_HANDLE:
            return self._lower_module_native_array_operations(plan)
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

    # Borrowed module native-array-handle operations.
    def _lower_module_native_array_operations(
        self,
        plan: ModuleVariablePlan,
    ) -> tuple[FortranFunction, ...]:
        """Lower every planned module-handle operation into a named bridge procedure."""
        handle = plan.native_array_handle
        if handle is None:
            raise ValueError(f"Module handle {plan.owner_path!r} has no operation plan")
        procedures = []
        for operation in handle.operations:
            procedure = self._lower_module_native_array_operation(plan, operation)
            if procedure is not None:
                procedures.append(procedure)
        return tuple(procedures)

    def _lower_module_native_array_operation(
        self,
        plan: ModuleVariablePlan,
        operation: NativeArrayOperation,
    ) -> FortranFunction | None:
        """Dispatch one operation using only the completed typed operation selector."""
        if operation in {
            NativeArrayOperation.NATIVE_BYTE_ORDER,
            NativeArrayOperation.ALIGNED,
            NativeArrayOperation.WRITEABLE,
            NativeArrayOperation.LAYOUT,
        }:
            return None
        if operation is NativeArrayOperation.TO_NUMPY:
            return self._lower_module_native_array_extraction(plan)
        return self._lower_module_native_array_bridge_operation(plan, operation)

    def _lower_module_native_array_extraction(
        self,
        plan: ModuleVariablePlan,
    ) -> FortranFunction | None:
        """Lower a detached snapshot only when completed extraction policy owns it."""
        handle = plan.native_array_handle
        if handle is None:
            raise ValueError(f"Module handle {plan.owner_path!r} has no operation plan")
        if handle.extraction_action is not NativeArrayExtractionAction.READ_ONLY_DETACHED_COPY:
            return None
        return self._module_native_array_snapshot_operation(plan)

    def _lower_module_native_array_bridge_operation(
        self,
        plan: ModuleVariablePlan,
        operation: NativeArrayOperation,
    ) -> FortranFunction:
        """Lower one operation selected to cross the native bridge."""
        if operation in {
            NativeArrayOperation.ALLOCATED,
            NativeArrayOperation.ASSOCIATED,
            NativeArrayOperation.CONTIGUOUS,
        }:
            return self._module_native_array_state_operation(plan, operation)
        if operation is NativeArrayOperation.ELEMENT_LENGTH:
            return self._module_native_array_element_length_operation(plan)
        if operation is NativeArrayOperation.ARRAY_ACTUAL:
            return self._module_native_array_actual_operation(plan)
        if operation is NativeArrayOperation.SHAPE:
            return self._module_native_array_shape_operation(plan)
        if operation is NativeArrayOperation.DESCRIPTOR:
            return self._module_native_array_descriptor_operation(plan)
        if operation in {NativeArrayOperation.ALLOCATE, NativeArrayOperation.RESIZE}:
            return self._module_native_array_shape_mutation_operation(plan, operation)
        if operation is NativeArrayOperation.DEALLOCATE:
            return self._module_native_array_deallocate_operation(plan)
        if operation is NativeArrayOperation.NULLIFY:
            return self._module_native_array_nullify_operation(plan)
        raise ValueError(f"Unsupported module native array operation for {plan.owner_path!r}: {operation!r}")

    def _module_native_array_state_operation(self, plan: ModuleVariablePlan, operation) -> FortranFunction:
        """Return allocated, associated, or contiguous state."""
        native = self._native_variable_name(plan)
        if operation is NativeArrayOperation.ALLOCATED:
            expression = f"allocated({native})"
        elif operation is NativeArrayOperation.ASSOCIATED:
            expression = f"associated({native})"
        else:
            presence = self._module_native_array_presence_expression(plan)
            expression = f".not. ({presence}) .or. is_contiguous({native})"
        name = self._module_native_array_operation_name(plan, operation)
        return FortranFunction(
            name=name,
            result_name="result",
            result_type="logical(c_bool)",
            bind_name=name,
            body=(FortranAssignment("result", CodeExpression(expression)),),
        )

    def _module_native_array_actual_operation(self, plan: ModuleVariablePlan) -> FortranFunction:
        """Return current module-array data storage without changing ownership."""
        name = self._module_native_array_operation_name(plan, NativeArrayOperation.ARRAY_ACTUAL)
        native = self._native_variable_name(plan)
        handle = plan.native_array_handle
        if handle is not None and handle.extraction_action is NativeArrayExtractionAction.READ_ONLY_DETACHED_COPY:
            return FortranFunction(
                name=name,
                result_name="result",
                result_type="type(c_ptr)",
                bind_name=name,
                body=(FortranAssignment("result", CodeExpression("c_null_ptr")),),
            )
        return FortranFunction(
            name=name,
            result_name="result",
            result_type="type(c_ptr)",
            bind_name=name,
            body=(
                FortranIf(
                    CodeExpression(self._module_native_array_presence_expression(plan)),
                    body=(FortranAssignment("result", CodeExpression(f"c_loc({native})")),),
                    else_body=(FortranAssignment("result", CodeExpression("c_null_ptr")),),
                ),
            ),
        )

    def _module_native_array_snapshot_operation(self, plan: ModuleVariablePlan) -> FortranFunction:
        """Copy one non-addressable module allocatable into bridge-owned storage."""
        handle = plan.native_array_handle
        if handle is None or handle.array.rank is None:
            raise ValueError(f"Module snapshot {plan.owner_path!r} has no rank")
        if plan.datatype_family is DatatypeFamily.STRING:
            raise ValueError(f"Deferred character module snapshot {plan.owner_path!r} is not implemented")
        name = self._module_native_array_operation_name(plan, NativeArrayOperation.TO_NUMPY)
        native = self._native_variable_name(plan)
        copy_nodes = (
            FortranAssignment(
                "result",
                CodeExpression(f"c_malloc(max(1_c_size_t, c_sizeof(element) * size({native}, kind=c_size_t)))"),
            ),
            FortranIf(
                CodeExpression("c_associated(result)"),
                body=(
                    FortranCall(
                        "c_f_pointer",
                        (CodeExpression("result"), CodeExpression("copy"), CodeExpression(f"[size({native})]")),
                    ),
                    FortranAssignment("copy", CodeExpression(f"reshape({native}, [size({native})])")),
                ),
            ),
        )
        return FortranFunction(
            name=name,
            result_name="result",
            result_type="type(c_ptr)",
            bind_name=name,
            declarations=(
                FortranDeclaration(
                    "copy",
                    self._module_native_array_element_type(plan),
                    ("pointer", "dimension(:)"),
                ),
                FortranDeclaration("element", self._module_native_array_element_type(plan)),
            ),
            body=(
                FortranIf(
                    CodeExpression(self._module_native_array_presence_expression(plan)),
                    body=copy_nodes,
                    else_body=(FortranAssignment("result", CodeExpression("c_null_ptr")),),
                ),
            ),
        )

    def _module_native_array_element_length_operation(self, plan: ModuleVariablePlan) -> FortranFunction:
        """Return the runtime character element width or zero when absent."""
        name = self._module_native_array_operation_name(plan, NativeArrayOperation.ELEMENT_LENGTH)
        native = self._native_variable_name(plan)
        return FortranFunction(
            name=name,
            result_name="result",
            result_type="integer(c_int64_t)",
            bind_name=name,
            body=(
                FortranIf(
                    CodeExpression(self._module_native_array_presence_expression(plan)),
                    body=(FortranAssignment("result", CodeExpression(f"len({native}, kind=c_int64_t)")),),
                    else_body=(FortranAssignment("result", CodeExpression("0_c_int64_t")),),
                ),
            ),
        )

    def _module_native_array_shape_operation(self, plan: ModuleVariablePlan) -> FortranFunction:
        """Return current extents, preserving absent descriptor state as zeroes."""
        handle = plan.native_array_handle
        if handle is None or handle.array.rank is None:
            raise ValueError(f"Module handle {plan.owner_path!r} has no shape rank")
        parameters = tuple(
            FortranParameter(f"extent_{axis}", "integer(c_int64_t)") for axis in range(handle.array.rank)
        )
        native = self._native_variable_name(plan)
        present = tuple(
            FortranAssignment(f"extent_{axis}", CodeExpression(f"size({native}, {axis + 1}, kind=c_int64_t)"))
            for axis in range(handle.array.rank)
        )
        absent = tuple(
            FortranAssignment(f"extent_{axis}", CodeExpression("0_c_int64_t")) for axis in range(handle.array.rank)
        )
        name = self._module_native_array_operation_name(plan, NativeArrayOperation.SHAPE)
        return FortranFunction(
            name=name,
            parameters=parameters,
            bind_name=name,
            body=(
                FortranIf(
                    CodeExpression(self._module_native_array_presence_expression(plan)),
                    body=present,
                    else_body=absent,
                ),
            ),
            is_subroutine=True,
        )

    def _module_native_array_descriptor_operation(self, plan: ModuleVariablePlan) -> FortranFunction | None:
        """Associate a call-local standard descriptor with one pointer module variable."""
        handle = plan.native_array_handle
        if handle is None or handle.descriptor_kind is not NativeArrayDescriptorKind.POINTER:
            return None
        if handle.array.rank is None:
            raise ValueError(f"Pointer module handle {plan.owner_path!r} has no descriptor rank")
        name = self._module_native_array_operation_name(plan, NativeArrayOperation.DESCRIPTOR)
        native = self._native_variable_name(plan)
        return FortranFunction(
            name=name,
            parameters=(
                FortranParameter(
                    "descriptor",
                    self._module_native_array_element_type(plan),
                    ("pointer", self._array_dimension_attribute(handle.array.rank), "intent(out)"),
                ),
            ),
            bind_name=name,
            body=(
                FortranIf(
                    CodeExpression(f"associated({native})"),
                    body=(FortranPointerAssignment("descriptor", CodeExpression(native)),),
                    else_body=(FortranPointerAssignment("descriptor", CodeExpression("null()")),),
                ),
            ),
            is_subroutine=True,
        )

    def _module_native_array_shape_mutation_operation(self, plan: ModuleVariablePlan, operation) -> FortranFunction:
        """Allocate or resize one module descriptor through completed permissions."""
        handle = plan.native_array_handle
        if handle is None or handle.array.rank is None:
            raise ValueError(f"Module handle {plan.owner_path!r} has no mutation rank")
        parameters = tuple(
            FortranParameter(f"extent_{axis}", "integer(c_int64_t)", ("value",)) for axis in range(handle.array.rank)
        )
        extents = tuple(CodeExpression(f"extent_{axis}") for axis in range(handle.array.rank))
        native = self._native_variable_name(plan)
        body = (
            FortranIf(
                CodeExpression(self._module_native_array_presence_expression(plan)),
                body=(FortranDeallocate(native),),
            ),
            FortranAllocate(native, extents),
        )
        name = self._module_native_array_operation_name(plan, operation)
        return FortranFunction(
            name=name,
            parameters=parameters,
            bind_name=name,
            body=body,
            is_subroutine=True,
        )

    def _module_native_array_deallocate_operation(self, plan: ModuleVariablePlan) -> FortranFunction:
        """Deallocate one policy-authorized module descriptor payload."""
        name = self._module_native_array_operation_name(plan, NativeArrayOperation.DEALLOCATE)
        native = self._native_variable_name(plan)
        return FortranFunction(
            name=name,
            bind_name=name,
            body=(
                FortranIf(
                    CodeExpression(self._module_native_array_presence_expression(plan)),
                    body=(FortranDeallocate(native),),
                ),
            ),
            is_subroutine=True,
        )

    def _module_native_array_nullify_operation(self, plan: ModuleVariablePlan) -> FortranFunction:
        """Nullify one policy-authorized module pointer association."""
        name = self._module_native_array_operation_name(plan, NativeArrayOperation.NULLIFY)
        return FortranFunction(
            name=name,
            bind_name=name,
            body=(FortranPointerAssignment(self._native_variable_name(plan), CodeExpression("null()")),),
            is_subroutine=True,
        )

    def _module_native_array_presence_expression(self, plan: ModuleVariablePlan) -> str:
        handle = plan.native_array_handle
        if handle is None:
            raise ValueError(f"Module handle {plan.owner_path!r} has no descriptor kind")
        intrinsic = "allocated" if handle.descriptor_kind is NativeArrayDescriptorKind.ALLOCATABLE else "associated"
        return f"{intrinsic}({self._native_variable_name(plan)})"

    def _module_native_array_element_type(self, plan: ModuleVariablePlan) -> str:
        """Return one numeric or deferred-character module-array element type."""
        if plan.datatype_family is DatatypeFamily.STRING:
            return "character(kind=c_char, len=:)"
        return PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name).fortran_spelling

    def _module_native_array_operation_name(self, plan: ModuleVariablePlan, operation) -> str:
        """Return the C-visible operation name derived from plan ownership."""
        return f"bind_c_{plan.symbol_name}_{operation.value}"

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
            return self._lower_array_argument(plan, mode)
        if plan.object_kind is ObjectKind.STRING and plan.bridge.handoff_mode is ArgumentHandoffMode.CHARACTER_BUFFER:
            if mode not in {OptionalMode.REQUIRED, OptionalMode.NULLABLE_VALUE}:
                raise ValueError(f"Unsupported Fortran string presence mode for {plan.owner_path!r}: {mode!r}")
            return self._lower_argument_string_value(plan)
        if plan.object_kind not in {ObjectKind.SCALAR, ObjectKind.STRING}:
            raise ValueError(f"Unsupported Fortran argument object kind for {plan.owner_path!r}: {plan.object_kind!r}")
        match mode:
            case OptionalMode.REQUIRED:
                return self._lower_argument_required(plan)
            case OptionalMode.REQUIRED_DESCRIPTOR:
                return self._lower_argument_required_descriptor(plan)
            case OptionalMode.NULLABLE_VALUE:
                return self._lower_argument_nullable_value(plan)
            case OptionalMode.DESCRIPTOR:
                return self._lower_argument_descriptor(plan)
        raise ValueError(f"Unsupported Fortran argument optional mode for {plan.owner_path!r}: {mode!r}")

    def _lower_argument_required_descriptor(self, plan: ArgumentTransferPlan) -> tuple[FortranParameter, ...]:
        """Receive one required Python argument as a nullable descriptor payload."""
        name = plan.bridge.native_name.lower()
        parameters = [FortranParameter(f"bound_{name}", "type(c_ptr)", ("value",))]
        if plan.bridge.descriptor_output_role is not None:
            parameters.extend(
                (
                    FortranParameter(f"bound_{name}_output", "type(c_ptr)", ("value",)),
                    FortranParameter(f"bound_{name}_output_present", "integer(c_int)", ("intent(out)",)),
                )
            )
        return tuple(parameters)

    def _lower_array_argument(
        self,
        plan: ArgumentTransferPlan,
        mode: OptionalMode,
    ) -> tuple[FortranParameter, ...]:
        """Dispatch one array parameter from its completed handoff mode."""
        if plan.bridge.handoff_mode is ArgumentHandoffMode.NATIVE_DESCRIPTOR:
            if mode not in {OptionalMode.REQUIRED, OptionalMode.DESCRIPTOR}:
                raise ValueError(f"Unsupported Fortran descriptor presence mode for {plan.owner_path!r}: {mode!r}")
            return self._lower_argument_native_array_descriptor(plan)
        if mode not in {OptionalMode.REQUIRED, OptionalMode.NULLABLE_VALUE}:
            raise ValueError(f"Unsupported Fortran array presence mode for {plan.owner_path!r}: {mode!r}")
        if plan.bridge.handoff_mode is ArgumentHandoffMode.ARRAY_BUFFER:
            return self._lower_argument_array_buffer(plan)
        if mode is OptionalMode.REQUIRED and plan.bridge.handoff_mode is ArgumentHandoffMode.OPAQUE_ADDRESS:
            return self._lower_argument_required_opaque_address(plan)
        raise ValueError(f"Unsupported Fortran array handoff for {plan.owner_path!r}: {plan.bridge.handoff_mode!r}")

    # Native-array-handle bridge parameters.
    def _lower_argument_native_array_descriptor(
        self,
        plan: ArgumentTransferPlan,
    ) -> tuple[FortranParameter, ...]:
        """Receive one standard descriptor as a typed allocatable/pointer dummy."""
        handle = plan.native_array_handle
        if handle is None or handle.array.rank is None:
            raise ValueError(f"Native descriptor {plan.owner_path!r} has no concrete rank")
        name = plan.bridge.native_name.lower()
        attribute = "allocatable" if handle.descriptor_kind is NativeArrayDescriptorKind.ALLOCATABLE else "pointer"
        parameters = [
            FortranParameter(
                name,
                self._native_array_argument_element_type(plan),
                (attribute, self._array_dimension_attribute(handle.array.rank)),
            )
        ]
        if plan.bridge.optional_mode is OptionalMode.DESCRIPTOR:
            parameters.append(FortranParameter(f"bound_{name}_present", "type(c_ptr)", ("value",)))
        return tuple(parameters)

    def _native_array_argument_element_type(self, plan: ArgumentTransferPlan) -> str:
        """Return one numeric or deferred-character descriptor dummy type."""
        if plan.datatype_family is DatatypeFamily.STRING:
            return "character(kind=c_char, len=:)"
        return PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name).fortran_spelling

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
        """Return one C pointer value for caller-owned opaque storage."""
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
            if argument.bridge.optional_mode in {OptionalMode.NULLABLE_VALUE, OptionalMode.DESCRIPTOR}
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
        direct_result = self._direct_result(plan)
        if self._is_allocatable_scalar_descriptor_result(direct_result):
            return FortranCall(
                self._scalar_descriptor_result_collector_name(plan),
                (CodeExpression(expression), CodeExpression(result_name)),
            )
        if (
            direct_result is not None
            and direct_result.scalar_descriptor is not None
            and direct_result.scalar_descriptor.descriptor_kind is NativeArrayDescriptorKind.POINTER
        ):
            return FortranPointerAssignment(result_name, CodeExpression(expression))
        return FortranAssignment(result_name, CodeExpression(expression))

    # Nullable rank-zero allocatable result collection.
    def _scalar_descriptor_result_collectors(
        self,
        plan: FunctionPlan,
    ) -> tuple[FortranFunction, ...]:
        """Preserve an unallocated direct scalar result before copy-out."""
        result = self._direct_result(plan)
        if not self._is_allocatable_scalar_descriptor_result(result):
            return ()
        element_type = (
            "character(kind=c_char, len=:)"
            if result.object_kind is ObjectKind.STRING
            else PrimitiveScalarTypeRegistry.type_for(result.semantic_type_name).fortran_spelling
        )
        return (
            FortranFunction(
                name=self._scalar_descriptor_result_collector_name(plan),
                parameters=(
                    FortranParameter("value", element_type, ("allocatable", "intent(in)")),
                    FortranParameter("target", element_type, ("allocatable", "intent(out)")),
                ),
                body=(
                    FortranIf(
                        CodeExpression("allocated(value)"),
                        body=(FortranAssignment("target", CodeExpression("value")),),
                    ),
                ),
                is_subroutine=True,
            ),
        )

    def _scalar_descriptor_result_collector_name(self, plan: FunctionPlan) -> str:
        """Return the stable helper name for one rank-zero allocatable result."""
        return f"x2py_collect_{plan.symbol_name}_scalar_descriptor_result"

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
            if (
                argument.bridge.optional_mode in {OptionalMode.NULLABLE_VALUE, OptionalMode.DESCRIPTOR}
                and argument.owner_path not in present
            ):
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
                if argument.bridge.optional_mode in {OptionalMode.NULLABLE_VALUE, OptionalMode.DESCRIPTOR}
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
        if plan.bridge.handoff_mode is ArgumentHandoffMode.NATIVE_DESCRIPTOR:
            return name
        if plan.bridge.optional_mode in {OptionalMode.REQUIRED_DESCRIPTOR, OptionalMode.DESCRIPTOR}:
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
        if plan.bridge.handoff_mode is ArgumentHandoffMode.NATIVE_DESCRIPTOR:
            return ()
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
        if plan.bridge.handoff_mode is ArgumentHandoffMode.NATIVE_DESCRIPTOR:
            return ()
        if plan.bridge.handoff_mode is ArgumentHandoffMode.ARRAY_BUFFER:
            return (self._array_pointer_initializer(plan),)
        if plan.bridge.optional_mode is OptionalMode.NULLABLE_VALUE:
            return (
                FortranCall(
                    "c_f_pointer",
                    (CodeExpression(f"bound_{name}"), CodeExpression(name)),
                ),
            )
        if plan.bridge.optional_mode not in {OptionalMode.REQUIRED_DESCRIPTOR, OptionalMode.DESCRIPTOR}:
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
        if plan.bridge.optional_mode not in {OptionalMode.REQUIRED_DESCRIPTOR, OptionalMode.DESCRIPTOR}:
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
            if argument.bridge.handoff_mode is ArgumentHandoffMode.NATIVE_DESCRIPTOR:
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
            if mode is OptionalMode.REQUIRED_DESCRIPTOR and argument.bridge.descriptor_output_role is not None:
                declarations.append(FortranDeclaration(f"{name}_output", scalar_type.fortran_spelling, ("pointer",)))
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

    def _raw_array_address_declarations(self, plan: FunctionPlan) -> tuple[FortranDeclaration, ...]:
        """Declare typed non-owning views for caller-supplied raw array addresses."""
        return tuple(
            FortranDeclaration(
                self._array_pointer_name(argument),
                self._array_element_fortran_type(argument),
                ("pointer", self._array_dimension_attribute(argument.array.rank)),
            )
            for argument in self._raw_array_address_arguments(plan)
            if argument.array is not None and argument.array.rank is not None
        )

    def _raw_array_address_initializers(self, plan: FunctionPlan) -> tuple[FortranCall, ...]:
        """Associate raw addresses with typed views using only planned shape facts."""
        return tuple(
            self._raw_array_pointer_initializer(plan, argument) for argument in self._raw_array_address_arguments(plan)
        )

    def _raw_array_pointer_initializer(
        self,
        plan: FunctionPlan,
        argument: ArgumentTransferPlan,
    ) -> FortranCall:
        """Associate one raw address with its completed pointee rank and orientation."""
        array = argument.array
        if array is None or array.rank is None:
            raise ValueError(f"Raw array address {argument.owner_path!r} requires a concrete rank")
        shape = list(self._array_shape_from_roles(array, plan.arguments))
        if array.native_order == "ORDER_C":
            shape.reverse()
        name = argument.bridge.native_name.lower()
        return FortranCall(
            "c_f_pointer",
            (
                CodeExpression(f"bound_{name}"),
                CodeExpression(self._array_pointer_name(argument)),
                CodeExpression(f"[{', '.join(shape)}]"),
            ),
        )

    def _raw_array_address_arguments(self, plan: FunctionPlan) -> tuple[ArgumentTransferPlan, ...]:
        """Return raw array address arguments selected by completed actions."""
        return tuple(
            argument
            for argument in plan.arguments
            if argument.object_kind is ObjectKind.NUMPY_ARRAY
            and argument.binding.python_action is PythonBarrierAction.RAW_ADDRESS
            and argument.bridge.native_action is NativeBarrierAction.PASS_RAW_ADDRESS
            and argument.bridge.handoff_mode is ArgumentHandoffMode.OPAQUE_ADDRESS
            and argument.bridge.data_action is BridgeDataAction.ASSOCIATE_VIEW
        )

    def _array_pointer_initializer(self, argument: ArgumentTransferPlan) -> FortranCall:
        """Associate one fixed-rank array pointer using planned base extents."""
        array = argument.array
        if array is None or array.rank is None:
            raise ValueError(f"Array argument {argument.owner_path!r} requires a concrete rank")
        name = argument.bridge.native_name.lower()
        extents = [f"{name}_extent_{axis}" for axis in range(array.rank)]
        if array.native_order == "ORDER_C":
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

    def _descriptor_initializers(self, plan: FunctionPlan) -> tuple[FortranPointerAssignment, ...]:
        return tuple(
            FortranPointerAssignment(
                f"{argument.bridge.native_name.lower()}_descriptor",
                CodeExpression("null()"),
            )
            for argument in plan.arguments
            if (
                argument.bridge.optional_mode in {OptionalMode.REQUIRED_DESCRIPTOR, OptionalMode.DESCRIPTOR}
                and argument.bridge.handoff_mode is not ArgumentHandoffMode.NATIVE_DESCRIPTOR
                and argument.native_call_slot.value_kind == "pointer"
            )
        )

    def _required_descriptor_initializers(
        self,
        plan: FunctionPlan,
    ) -> tuple[FortranAssignment | FortranPointerAssignment | FortranCall | FortranIf, ...]:
        """Prepare descriptor storage for required nullable descriptor values."""
        return tuple(
            node
            for argument in plan.arguments
            if argument.bridge.optional_mode is OptionalMode.REQUIRED_DESCRIPTOR
            for node in self._present_preparation(argument)
        )

    def _required_descriptor_finalizers(
        self,
        plan: FunctionPlan,
    ) -> tuple[FortranIf, ...]:
        """Copy final descriptor values and states into binding-owned output slots."""
        return tuple(
            self._required_descriptor_finalizer(argument)
            for argument in plan.arguments
            if argument.bridge.optional_mode is OptionalMode.REQUIRED_DESCRIPTOR
            and argument.bridge.descriptor_output_role is not None
        )

    def _required_descriptor_finalizer(self, argument: ArgumentTransferPlan) -> FortranIf:
        """Lower one planned required-descriptor copy-out ABI."""
        name = argument.bridge.native_name.lower()
        inquiry = "associated" if argument.native_call_slot.value_kind == "pointer" else "allocated"
        return FortranIf(
            CodeExpression(f"{inquiry}({name}_descriptor)"),
            body=(
                FortranAssignment(f"bound_{name}_output_present", CodeExpression("1")),
                FortranCall(
                    "c_f_pointer",
                    (CodeExpression(f"bound_{name}_output"), CodeExpression(f"{name}_output")),
                ),
                FortranAssignment(f"{name}_output", CodeExpression(f"{name}_descriptor")),
            ),
            else_body=(FortranAssignment(f"bound_{name}_output_present", CodeExpression("0")),),
        )

    def _native_output_parameters(self, plan: FunctionPlan) -> tuple[FortranParameter, ...]:
        """Return bridge ABI parameters for every typed native result slot."""
        parameters = []
        for slot in sorted(plan.native_call_slots, key=lambda item: item.native_position):
            if slot.source_kind != "result":
                continue
            parameters.extend(self._native_output_parameters_for_slot(slot))
        return tuple(parameters)

    def _native_output_parameters_for_slot(self, slot: NativeCallSlotPlan) -> tuple[FortranParameter, ...]:
        """Lower one completed result-slot kind into bridge ABI parameters."""
        if slot.scalar_descriptor is not None:
            return self._scalar_descriptor_output_parameters(slot)
        if self._is_owned_native_array_slot(slot):
            return self._owned_native_array_output_parameters(slot)
        if slot.object_kind in {ObjectKind.STRING, ObjectKind.NUMPY_ARRAY}:
            return (FortranParameter(slot.native_name.lower(), "type(c_ptr)"),)
        if slot.semantic_type_name is None:
            raise ValueError(f"Missing native output datatype for {slot.owner_path!r}")
        scalar_type = PrimitiveScalarTypeRegistry.type_for(slot.semantic_type_name)
        return (FortranParameter(slot.native_name.lower(), scalar_type.fortran_spelling),)

    def _scalar_descriptor_output_parameters(self, slot: NativeCallSlotPlan) -> tuple[FortranParameter, ...]:
        """Lower one completed rank-zero descriptor result ABI."""
        descriptor = slot.scalar_descriptor
        if descriptor is None:
            raise ValueError(f"Scalar output {slot.owner_path!r} has no descriptor plan")
        name = slot.native_name.lower()
        parameters = [
            FortranParameter(name, "type(c_ptr)"),
            FortranParameter(f"{name}_present", "integer(c_int)"),
        ]
        if descriptor.runtime_length:
            parameters.append(FortranParameter(f"{name}_length", "integer(c_int64_t)"))
        return tuple(parameters)

    def _owned_native_array_output_parameters(self, slot: NativeCallSlotPlan) -> tuple[FortranParameter, ...]:
        """Lower one completed owned rank-positive descriptor result ABI."""
        handle = slot.native_array_handle
        if handle is None or handle.array.rank is None:
            raise ValueError(f"Owned output {slot.owner_path!r} has no descriptor rank")
        name = slot.native_name.lower()
        if self._is_owned_deferred_character_slot(slot):
            return (
                FortranParameter(name, "type(c_ptr)"),
                FortranParameter(f"{name}_itemsize", "integer(c_int64_t)"),
                *(FortranParameter(f"{name}_extent_{axis}", "integer(c_int64_t)") for axis in range(handle.array.rank)),
            )
        return (
            FortranParameter(
                name,
                self._array_result_element_type(slot),
                ("allocatable", self._array_dimension_attribute(handle.array.rank), "intent(out)"),
            ),
        )

    def _native_output_declarations(self, plan: FunctionPlan) -> tuple[FortranDeclaration, ...]:
        """Dispatch helper-local output storage from completed bridge data actions."""
        declarations = []
        for slot in plan.native_call_slots:
            if slot.source_kind != "result":
                continue
            if slot.scalar_descriptor is not None:
                declarations.extend(self._scalar_descriptor_output_declarations(slot))
                continue
            if self._is_owned_native_array_slot(slot):
                handle = slot.native_array_handle
                if handle is None or handle.array.rank is None:
                    raise ValueError(f"Owned output {slot.owner_path!r} has no descriptor rank")
                declarations.append(
                    FortranDeclaration(
                        f"{slot.native_name.lower()}_value",
                        self._array_result_element_type(slot),
                        ("allocatable", self._array_dimension_attribute(handle.array.rank)),
                    )
                )
                if self._is_owned_deferred_character_slot(slot):
                    declarations.append(
                        FortranDeclaration(
                            f"{slot.native_name.lower()}_copy",
                            "character(kind=c_char)",
                            ("pointer", "dimension(:)"),
                        )
                    )
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
        """Declare backend-local storage selected by direct-result lowering."""
        result = self._direct_result(plan)
        if result is None:
            return ()
        if result.scalar_descriptor is not None:
            return self._scalar_descriptor_copy_declarations(result, "result")
        if self._is_owned_native_array_result(result):
            handle = result.native_array_handle
            if handle is None or handle.array.rank is None:
                raise ValueError(f"Owned result {result.owner_path!r} has no descriptor rank")
            declarations = [
                FortranDeclaration(
                    "result_value",
                    self._array_result_element_type(result),
                    ("allocatable", self._array_dimension_attribute(handle.array.rank)),
                ),
            ]
            if self._is_owned_deferred_character_result(result):
                declarations.append(
                    FortranDeclaration(
                        "result_copy",
                        "character(kind=c_char)",
                        ("pointer", "dimension(:)"),
                    )
                )
            return tuple(declarations)
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

    def _scalar_descriptor_output_declarations(
        self,
        slot: NativeCallSlotPlan,
    ) -> tuple[FortranDeclaration, ...]:
        """Declare native and detached-copy storage for one hidden descriptor scalar."""
        return self._scalar_descriptor_copy_declarations(slot, slot.native_name.lower())

    def _scalar_descriptor_copy_declarations(
        self,
        result: ResultPlan | NativeCallSlotPlan,
        name: str,
    ) -> tuple[FortranDeclaration, ...]:
        """Declare helper-local storage selected by a scalar descriptor plan."""
        descriptor = result.scalar_descriptor
        if descriptor is None:
            return ()
        attribute = "allocatable" if descriptor.descriptor_kind is NativeArrayDescriptorKind.ALLOCATABLE else "pointer"
        value_name = f"{name}_value"
        copy_name = f"{name}_copy"
        if result.object_kind is ObjectKind.STRING:
            return (
                FortranDeclaration(value_name, "character(kind=c_char, len=:)", (attribute,)),
                FortranDeclaration(copy_name, "character(kind=c_char)", ("pointer", "dimension(:)")),
            )
        scalar_type = PrimitiveScalarTypeRegistry.type_for(result.semantic_type_name)
        return (
            FortranDeclaration(value_name, scalar_type.fortran_spelling, (attribute,)),
            FortranDeclaration(copy_name, scalar_type.fortran_spelling, ("pointer",)),
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
    ) -> tuple[FortranAssignment | FortranCall | FortranIf, ...]:
        """Finalize one direct result into its selected bridge representation."""
        result = self._direct_result(plan)
        if result is None:
            return ()
        if result.scalar_descriptor is not None:
            return self._scalar_descriptor_copy_nodes(result, "result")
        if self._is_owned_native_array_result(result):
            if self._is_owned_deferred_character_result(result):
                return self._owned_deferred_character_copy_nodes(result, "result", "result_value", "result_copy")
            return (
                FortranCall(
                    "move_alloc",
                    (CodeExpression("result_value"), CodeExpression("result")),
                ),
            )
        if result.object_kind is ObjectKind.NUMPY_ARRAY:
            if result.array is None:
                raise ValueError(f"Array result {result.owner_path!r} has no shape plan")
            return self._fixed_array_copy_nodes(
                result.array.native_order,
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
            if slot.scalar_descriptor is not None:
                nodes.extend(self._scalar_descriptor_copy_nodes(slot, slot.native_name.lower()))
                continue
            if self._is_owned_native_array_slot(slot):
                name = slot.native_name.lower()
                if self._is_owned_deferred_character_slot(slot):
                    nodes.extend(
                        self._owned_deferred_character_copy_nodes(
                            slot,
                            name,
                            f"{name}_value",
                            f"{name}_copy",
                        )
                    )
                    continue
                nodes.append(
                    FortranIf(
                        CodeExpression(f"allocated({name}_value)"),
                        body=(FortranAssignment(name, CodeExpression(f"{name}_value")),),
                    )
                )
                continue
            if slot.bridge_data_action is BridgeDataAction.COPY_REPRESENTATION:
                nodes.extend(self._lower_native_output_representation_copy(plan, slot))
                continue
            raise ValueError(
                f"Unsupported native-output bridge data action for {slot.owner_path!r}: {slot.bridge_data_action!r}"
            )
        return tuple(nodes)

    def _scalar_descriptor_copy_nodes(
        self,
        result: ResultPlan | NativeCallSlotPlan,
        name: str,
    ) -> tuple[FortranAssignment | FortranIf, ...]:
        """Copy one present scalar descriptor payload into C-owned storage."""
        descriptor = result.scalar_descriptor
        if descriptor is None:
            return ()
        value_name = f"{name}_value"
        copy_name = f"{name}_copy"
        present = "allocated" if descriptor.descriptor_kind is NativeArrayDescriptorKind.ALLOCATABLE else "associated"
        initializers: list[FortranAssignment | FortranIf] = [
            FortranAssignment(name, CodeExpression("c_null_ptr")),
            FortranAssignment(f"{name}_present", CodeExpression("0_c_int")),
        ]
        if descriptor.runtime_length:
            initializers.append(FortranAssignment(f"{name}_length", CodeExpression("0_c_int64_t")))
            copy_body: tuple[FortranAssignment | FortranCall | FortranIf, ...] = (
                FortranAssignment(f"{name}_length", CodeExpression(f"len({value_name}, kind=c_int64_t)")),
                FortranAssignment(
                    name,
                    CodeExpression(f"c_malloc(max(1_c_size_t, int({name}_length, c_size_t)))"),
                ),
                FortranIf(
                    CodeExpression(f"c_associated({name})"),
                    body=(
                        FortranCall(
                            "c_f_pointer",
                            (
                                CodeExpression(name),
                                CodeExpression(copy_name),
                                CodeExpression(f"[{name}_length]"),
                            ),
                        ),
                        FortranIf(
                            CodeExpression(f"{name}_length > 0_c_int64_t"),
                            body=(
                                FortranAssignment(
                                    f"{copy_name}(1:{name}_length)",
                                    CodeExpression(f"transfer({value_name}, {copy_name}(1:{name}_length))"),
                                ),
                            ),
                        ),
                    ),
                ),
            )
        else:
            copy_body = (
                FortranAssignment(
                    name,
                    CodeExpression(f"c_malloc(max(1_c_size_t, c_sizeof({value_name})))"),
                ),
                FortranIf(
                    CodeExpression(f"c_associated({name})"),
                    body=(
                        FortranCall("c_f_pointer", (CodeExpression(name), CodeExpression(copy_name))),
                        FortranAssignment(copy_name, CodeExpression(value_name)),
                    ),
                ),
            )
        initializers.append(
            FortranIf(
                CodeExpression(f"{present}({value_name})"),
                body=(FortranAssignment(f"{name}_present", CodeExpression("1_c_int")), *copy_body),
            )
        )
        return tuple(initializers)

    # Deferred-character native-array-handle result copying.
    def _owned_deferred_character_copy_nodes(
        self,
        result: ResultPlan | NativeCallSlotPlan,
        target_name: str,
        value_name: str,
        copy_name: str,
    ) -> tuple[FortranAssignment | FortranIf, ...]:
        """Copy a runtime-width character array before persistent CFI materialization."""
        handle = result.native_array_handle
        if handle is None or handle.array.rank is None:
            raise ValueError(f"Deferred character result {result.owner_path!r} has no descriptor rank")
        rank = handle.array.rank
        itemsize = f"{target_name}_itemsize"
        extents = tuple(f"{target_name}_extent_{axis}" for axis in range(rank))
        byte_count = " * ".join((itemsize, *extents))
        present_body: list[FortranAssignment | FortranCall | FortranIf] = [
            FortranAssignment(itemsize, CodeExpression(f"len({value_name}, kind=c_int64_t)")),
            *(
                FortranAssignment(
                    extent,
                    CodeExpression(f"size({value_name}, {axis + 1}, kind=c_int64_t)"),
                )
                for axis, extent in enumerate(extents)
            ),
            FortranAssignment(
                target_name,
                CodeExpression(f"c_malloc(max(1_c_size_t, int({byte_count}, c_size_t)))"),
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
                    FortranIf(
                        CodeExpression(f"{byte_count} > 0_c_int64_t"),
                        body=(
                            FortranAssignment(
                                copy_name,
                                CodeExpression(f"transfer({value_name}, {copy_name}, {byte_count})"),
                            ),
                        ),
                    ),
                ),
            ),
        ]
        return (
            FortranAssignment(target_name, CodeExpression("c_null_ptr")),
            FortranAssignment(itemsize, CodeExpression("0_c_int64_t")),
            *(FortranAssignment(extent, CodeExpression("0_c_int64_t")) for extent in extents),
            FortranIf(CodeExpression(f"allocated({value_name})"), body=tuple(present_body)),
        )

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
                slot.array.native_order,
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
        """Return the completed numeric, fixed, or deferred character element type."""
        if plan.datatype_family is DatatypeFamily.STRING:
            if plan.native_array_handle is not None and plan.array is not None and plan.array.itemsize is None:
                return "character(kind=c_char, len=:)"
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
        if slot.scalar_descriptor is not None:
            return f"{name}_value"
        if self._is_owned_native_array_slot(slot):
            return f"{name}_value"
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
        if result is not None and result.scalar_descriptor is not None:
            return "result_value"
        if result is not None and self._is_owned_native_array_result(result):
            return "result_value"
        if result is not None and result.object_kind in {ObjectKind.STRING, ObjectKind.NUMPY_ARRAY}:
            return "result_value"
        return result_name

    def _bridge_result_type(self, plan: FunctionPlan, result: ResultPlan | None = None) -> str:
        result = result or self._direct_result(plan)
        if result is None:
            raise ValueError(f"{plan.owner_path!r} native function has no result plan")
        if result.scalar_descriptor is not None:
            return "type(c_ptr)"
        if result.object_kind in {ObjectKind.STRING, ObjectKind.NUMPY_ARRAY}:
            return "type(c_ptr)"
        return PrimitiveScalarTypeRegistry.type_for(result.semantic_type_name).fortran_spelling

    def _direct_result(self, plan: FunctionPlan) -> ResultPlan | None:
        """Return the sole direct result used by the Fortran function ABI."""
        return next((result for result in plan.results if result.source_kind == "direct_return"), None)

    def _owned_direct_result(self, plan: FunctionPlan) -> ResultPlan | None:
        """Return the direct result that uses persistent descriptor output storage."""
        result = self._direct_result(plan)
        return result if result is not None and self._is_owned_native_array_result(result) else None

    @staticmethod
    def _is_allocatable_scalar_descriptor_result(result: ResultPlan | None) -> bool:
        """Return whether a direct rank-zero result must preserve unallocated state."""
        return (
            result is not None
            and result.scalar_descriptor is not None
            and result.scalar_descriptor.descriptor_kind is NativeArrayDescriptorKind.ALLOCATABLE
        )

    @staticmethod
    def _is_owned_native_array_result(result: ResultPlan) -> bool:
        """Return whether one result owns persistent standard-descriptor storage."""
        handle = result.native_array_handle
        return handle is not None and handle.handoff.abi is NativeDescriptorHandoffABI.OWNED_RESULT_STORAGE

    @staticmethod
    def _is_owned_native_array_slot(slot: NativeCallSlotPlan) -> bool:
        """Return whether one hidden slot shares persistent descriptor storage."""
        handle = slot.native_array_handle
        return handle is not None and handle.handoff.abi is NativeDescriptorHandoffABI.OWNED_RESULT_STORAGE

    @classmethod
    def _is_owned_deferred_character_result(cls, result: ResultPlan) -> bool:
        """Return whether owner storage needs a runtime-width copy ABI."""
        return cls._is_owned_native_array_result(result) and result.datatype_family is DatatypeFamily.STRING

    @classmethod
    def _is_owned_deferred_character_slot(cls, slot: NativeCallSlotPlan) -> bool:
        """Return whether a hidden owner slot needs a runtime-width copy ABI."""
        return cls._is_owned_native_array_slot(slot) and slot.datatype_family is DatatypeFamily.STRING

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
            variable.bridge.getter_action is ModuleGetterAction.NULLABLE_SNAPSHOT
            or (
                variable.native_array_handle is not None
                and variable.native_array_handle.extraction_action
                is NativeArrayExtractionAction.READ_ONLY_DETACHED_COPY
            )
            for variable in self._variables(plan)
        )

    def _needs_function_copy_allocator(self, plan: ModulePlan) -> bool:
        """Return whether any function copies an array or string result."""
        return any(self._function_needs_copy_allocator(function) for function in self._functions(plan))

    def _function_needs_copy_allocator(self, function: FunctionPlan) -> bool:
        """Return whether one function owns a result-copy allocation."""
        return self._result_plans_need_allocator(function) or self._native_result_slots_need_allocator(function)

    def _result_plans_need_allocator(self, function: FunctionPlan) -> bool:
        """Return whether one Python result is an array or string copy."""
        return any(
            result.scalar_descriptor is not None or result.object_kind in {ObjectKind.STRING, ObjectKind.NUMPY_ARRAY}
            for result in function.results
        )

    def _native_result_slots_need_allocator(self, function: FunctionPlan) -> bool:
        """Return whether one hidden native result is an array or string copy."""
        return any(
            slot.scalar_descriptor is not None or slot.object_kind in {ObjectKind.STRING, ObjectKind.NUMPY_ARRAY}
            for slot in function.native_call_slots
            if slot.source_kind == "result"
        )

    def _external_interface_procedure(self, plan: FunctionPlan) -> FortranInterfaceProcedure:
        parameters = tuple(
            self._external_interface_parameter(plan, argument)
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
        if result.scalar_descriptor is not None:
            attribute = (
                "allocatable"
                if result.scalar_descriptor.descriptor_kind is NativeArrayDescriptorKind.ALLOCATABLE
                else "pointer"
            )
            if result.object_kind is ObjectKind.STRING:
                return f"character(kind=c_char, len=:), {attribute}"
            scalar_type = PrimitiveScalarTypeRegistry.type_for(result.semantic_type_name)
            return f"{scalar_type.fortran_spelling}, {attribute}"
        if result.object_kind is ObjectKind.NUMPY_ARRAY:
            shape = self._array_result_shape(plan, result)
            return f"{self._array_result_element_type(result)}, dimension({', '.join(shape)})"
        if result.object_kind is ObjectKind.STRING:
            return f"character(kind=c_char, len={self._string_result_length(result)})"
        return PrimitiveScalarTypeRegistry.type_for(result.semantic_type_name).fortran_spelling

    def _external_interface_parameter(
        self,
        plan: FunctionPlan,
        argument: ArgumentTransferPlan,
    ) -> FortranParameter:
        """Return the native external dummy declaration for one planned argument."""
        attributes = (
            ("optional",)
            if argument.bridge.optional_mode in {OptionalMode.NULLABLE_VALUE, OptionalMode.DESCRIPTOR}
            else ()
        )
        if argument.object_kind is ObjectKind.NUMPY_ARRAY:
            array = argument.array
            if array is None:
                raise ValueError(f"Array argument {argument.owner_path!r} has no shape plan")
            element_type = self._array_element_fortran_type(argument)
            dimension = self._external_array_dimension(plan, argument)
            if argument.native_array_handle is not None:
                descriptor_attribute = (
                    "allocatable"
                    if argument.native_array_handle.descriptor_kind is NativeArrayDescriptorKind.ALLOCATABLE
                    else "pointer"
                )
                attributes = (*attributes, descriptor_attribute)
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

    def _external_array_dimension(self, plan: FunctionPlan, argument: ArgumentTransferPlan) -> str:
        """Lower the completed native dummy shape without changing its ABI category."""
        array = argument.array
        if array is None:
            raise ValueError(f"Array argument {argument.owner_path!r} has no shape plan")
        return self._external_array_dimension_from_plan(array, plan)

    def _external_array_dimension_from_plan(self, array: ArrayHandoffPlan, plan: FunctionPlan) -> str:
        """Render rank/category facts already selected in one array plan."""
        if array.rank is None:
            return ".."
        if array.category in {"assumed_shape", "deferred_shape"}:
            return ", ".join(":" for _ in range(array.rank))
        shape = list(self._array_shape_from_roles(array, plan.arguments))
        if array.native_order == "ORDER_C":
            shape.reverse()
        if array.category != "assumed_size":
            return ", ".join(shape)
        return self._external_assumed_size_dimension(array, shape)

    @staticmethod
    def _external_assumed_size_dimension(array: ArrayHandoffPlan, shape: list[str]) -> str:
        """Use a legal assumed-size spelling while retaining plan rank elsewhere."""
        if array.native_order == "ORDER_C" or any(item == ":" for item in shape[:-1]):
            return "*"
        shape[-1] = "*"
        return ", ".join(shape)

    # Ordinary-array result-shape lowering.
    def _array_result_shape(self, plan: FunctionPlan, result: ResultPlan) -> tuple[str, ...]:
        """Lower one result shape through the plan's native scalar roles."""
        if result.array is None:
            raise ValueError(f"Array result {result.owner_path!r} has no shape plan")
        return self._array_shape_from_roles(result.array, plan.arguments)

    def _array_output_shape(self, plan: FunctionPlan, slot: NativeCallSlotPlan) -> tuple[str, ...]:
        """Lower one hidden-output shape through the plan's native scalar roles."""
        if slot.array is None:
            raise ValueError(f"Array output {slot.owner_path!r} has no shape plan")
        return self._array_shape_from_roles(slot.array, plan.arguments)

    def _array_shape_from_roles(self, array, arguments) -> tuple[str, ...]:
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
        return any(
            argument.bridge.optional_mode in {OptionalMode.NULLABLE_VALUE, OptionalMode.DESCRIPTOR}
            for argument in plan.arguments
        )

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
            "c_loc",
            "c_null_char",
            "c_ptr",
            "c_null_ptr",
            "c_size_t",
            "c_sizeof",
        )
