"""Direct recursive C binding generation from shared wrapper plans."""

from __future__ import annotations

from dataclasses import dataclass
import re

from x2py.semantics.ownership import (
    CodegenAction,
    ObjectKind,
    PythonBarrierAction,
    SetterAction,
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
    PythonExceptionKind,
    TransformationAction,
    TransformationLayer,
    WritebackPhase,
)
from x2py.wrapper_codegen.nodes import (
    CAllowThreadsBegin,
    CAllowThreadsEnd,
    CComment,
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
    NativeCallSlotPlan,
    ResultPlan,
)
from x2py.wrapper_codegen.primitive_scalar_types import PrimitiveScalarTypeRegistry
from x2py.wrapper_codegen.visitor import ClassVisitor


@dataclass
class _CArgumentNames:
    object_name: str
    value_name: str
    length_name: str
    nullable_name: str
    present_name: str
    extent_names: tuple[str, ...]
    upper_bound_names: tuple[str, ...]
    stride_names: tuple[str, ...]
    runtime_rank_name: str
    itemsize_name: str


@dataclass
class _CFunctionContext:
    arguments: dict[str, _CArgumentNames]
    native_outputs: dict[str, str]
    result_name: str | None
    python_result_name: str | None
    python_results: dict[str, str]
    role_values: dict[str, str]


class CBindingGenerator(ClassVisitor):
    """Recursively lower binding plan views directly into C syntax nodes."""

    def require_supported(self, plan: ModulePlan) -> None:
        """Reject unsupported C ABI actions and scalar types."""
        for function in self._functions(plan):
            self._require_function_supported(function)
        for variable in self._variables(plan):
            self._require_variable_supported(variable)

    def _require_variable_supported(self, variable: ModuleVariablePlan) -> None:
        """Dispatch one module variable from its completed getter action."""
        if variable.binding.getter_action is ModuleGetterAction.NATIVE_ARRAY_HANDLE:
            handle = variable.native_array_handle
            if handle is None or handle.array.rank is None:
                raise ValueError(f"Unsupported C module handle for {variable.owner_path!r}")
            if variable.datatype_family is not DatatypeFamily.STRING:
                PrimitiveScalarTypeRegistry.type_for(variable.semantic_type_name)
            return
        PrimitiveScalarTypeRegistry.type_for(variable.semantic_type_name)

    def _require_function_supported(self, function: FunctionPlan) -> None:
        """Reject unsupported actions and types for one binding function."""
        for argument in function.arguments:
            self._require_argument_supported(argument)
        for result in function.results:
            if result.scalar_descriptor is not None:
                self._require_scalar_descriptor_binding_result_supported(result)
                continue
            match result.object_kind:
                case ObjectKind.SCALAR:
                    PrimitiveScalarTypeRegistry.type_for(result.semantic_type_name)
                case ObjectKind.STRING:
                    self._require_string_binding_result_supported(result)
                case ObjectKind.NUMPY_ARRAY:
                    self._require_array_binding_result_supported(result)
                case _:
                    raise ValueError(
                        f"Unsupported C result object kind for {result.owner_path!r}: {result.object_kind!r}"
                    )
        for slot in function.native_call_slots:
            self._require_native_result_supported(function, slot)
        for action in function.writeback_actions:
            self._require_writeback_supported(action)

    def _require_argument_supported(self, argument: ArgumentTransferPlan) -> None:
        """Reject one unsupported Python argument conversion."""
        self._require_argument_transformations_supported(argument)
        if argument.binding.python_action not in {
            PythonBarrierAction.SCALAR_VALUE,
            PythonBarrierAction.SCALAR_STORAGE,
            PythonBarrierAction.STRING_STORAGE,
            PythonBarrierAction.STRING_VALUE,
            PythonBarrierAction.RAW_ADDRESS,
            PythonBarrierAction.ARRAY_STORAGE,
            PythonBarrierAction.WRAPPER_INSTANCE,
        }:
            raise ValueError(
                f"Unsupported C argument action for {argument.owner_path!r}: {argument.binding.python_action!r}"
            )
        if (
            argument.binding.python_action
            in {
                PythonBarrierAction.SCALAR_STORAGE,
                PythonBarrierAction.STRING_STORAGE,
                PythonBarrierAction.RAW_ADDRESS,
            }
            and argument.bridge.handoff_mode is not ArgumentHandoffMode.OPAQUE_ADDRESS
        ):
            raise ValueError(f"Unsupported C address handoff for {argument.owner_path!r}")
        match argument.object_kind:
            case ObjectKind.SCALAR:
                self._require_scalar_argument_supported(argument)
            case ObjectKind.STRING:
                self._require_string_argument_supported(argument)
            case ObjectKind.NUMPY_ARRAY:
                self._require_array_argument_supported(argument)
            case _:
                raise ValueError(
                    f"Unsupported C argument object kind for {argument.owner_path!r}: {argument.object_kind!r}"
                )

    @staticmethod
    def _require_argument_transformations_supported(argument: ArgumentTransferPlan) -> None:
        """Accept only binding-owned array representation actions in this backend."""
        for transformation in argument.transformations:
            if transformation.layer is not TransformationLayer.BINDING:
                raise ValueError(
                    f"C binding cannot lower {transformation.layer.value} transformation for {argument.owner_path!r}"
                )
            if transformation.action not in {
                TransformationAction.COPY_ARRAY_REPRESENTATION,
                TransformationAction.RELEASE_TEMPORARY,
            }:
                raise ValueError(
                    f"Unsupported C binding transformation for {argument.owner_path!r}: {transformation.action.value}"
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
                    f"Unsupported C native result object kind for {slot.owner_path!r}: {slot.object_kind!r}"
                )

    # Scalar support checks.
    def _require_scalar_argument_supported(self, argument: ArgumentTransferPlan) -> None:
        """Require one first-lane primitive scalar argument type."""
        PrimitiveScalarTypeRegistry.type_for(argument.semantic_type_name)

    def _require_scalar_native_result_supported(self, slot: NativeCallSlotPlan) -> None:
        """Require one first-lane primitive scalar native result type."""
        if slot.semantic_type_name is None:
            raise ValueError(f"Missing C result datatype for {slot.owner_path!r}")
        PrimitiveScalarTypeRegistry.type_for(slot.semantic_type_name)

    def _require_scalar_descriptor_native_result_supported(
        self,
        function: FunctionPlan,
        slot: NativeCallSlotPlan,
    ) -> None:
        """Require one nullable rank-zero descriptor output slot."""
        if slot.bridge_data_action is not BridgeDataAction.COPY_REPRESENTATION:
            raise ValueError(f"Unsupported C scalar descriptor action for {slot.owner_path!r}")
        if not any(result.native_call_slot is slot for result in function.results):
            raise ValueError(f"Unclaimed C scalar descriptor output for {slot.owner_path!r}")
        if slot.object_kind is ObjectKind.STRING:
            if not slot.scalar_descriptor.runtime_length:
                raise ValueError(f"Missing C runtime string length for {slot.owner_path!r}")
            return
        if slot.object_kind is not ObjectKind.SCALAR or slot.scalar_descriptor.runtime_length:
            raise ValueError(f"Unsupported C scalar descriptor family for {slot.owner_path!r}")
        if slot.semantic_type_name is None:
            raise ValueError(f"Missing C scalar descriptor datatype for {slot.owner_path!r}")
        PrimitiveScalarTypeRegistry.type_for(slot.semantic_type_name)

    def _require_scalar_descriptor_binding_result_supported(self, result: ResultPlan) -> None:
        """Require one nullable rank-zero descriptor Python result."""
        descriptor = result.scalar_descriptor
        if descriptor is None or not descriptor.nullable:
            raise ValueError(f"Unsupported C scalar descriptor result for {result.owner_path!r}")
        if result.bridge.data_action is not BridgeDataAction.COPY_REPRESENTATION:
            raise ValueError(f"Unsupported C scalar descriptor copy for {result.owner_path!r}")
        if result.object_kind is ObjectKind.STRING:
            if not descriptor.runtime_length:
                raise ValueError(f"Missing C runtime string length for {result.owner_path!r}")
            return
        if result.object_kind is not ObjectKind.SCALAR or descriptor.runtime_length:
            raise ValueError(f"Unsupported C scalar descriptor family for {result.owner_path!r}")
        PrimitiveScalarTypeRegistry.type_for(result.semantic_type_name)

    # Ordinary-array and native-array-handle support checks.
    def _require_array_argument_supported(self, argument: ArgumentTransferPlan) -> None:
        """Dispatch one completed array buffer or raw-address handoff."""
        if argument.native_array_handle is not None:
            self._require_native_array_handle_argument_supported(argument)
            return
        if argument.binding.python_action is PythonBarrierAction.RAW_ADDRESS:
            self._require_raw_array_argument_supported(argument)
            return
        self._require_array_buffer_argument_supported(argument)

    def _require_native_array_handle_argument_supported(self, argument: ArgumentTransferPlan) -> None:
        """Require one typed standard-descriptor argument handoff."""
        handle = argument.native_array_handle
        if handle is None or handle.array.rank is None:
            raise ValueError(f"Unsupported C native array handle for {argument.owner_path!r}")
        if argument.bridge.handoff_mode is not ArgumentHandoffMode.NATIVE_DESCRIPTOR:
            raise ValueError(f"Unsupported C native descriptor handoff for {argument.owner_path!r}")
        if handle.handoff.abi not in {
            NativeDescriptorHandoffABI.FACT_PACKED_CALL_LOCAL,
            NativeDescriptorHandoffABI.DIRECT_STANDARD_DESCRIPTOR,
        }:
            raise ValueError(f"Unsupported C native descriptor ABI for {argument.owner_path!r}")
        if self._native_array_cfi_type(argument) is None:
            raise ValueError(f"Missing CFI element type for {argument.owner_path!r}")

    def _require_array_buffer_argument_supported(self, argument: ArgumentTransferPlan) -> None:
        """Require one completed ordinary array-buffer handoff."""
        array = argument.array
        if array is None or (array.rank is not None and not 1 <= array.rank <= 15):
            raise ValueError(f"Unsupported C array rank for {argument.owner_path!r}")
        if array.contiguous not in {True, False}:
            raise ValueError(f"Unsupported C array layout for {argument.owner_path!r}")
        if argument.bridge.handoff_mode is not ArgumentHandoffMode.ARRAY_BUFFER:
            raise ValueError(f"Unsupported C array handoff for {argument.owner_path!r}")
        if argument.bridge.data_action is not BridgeDataAction.ASSOCIATE_VIEW:
            raise ValueError(f"Unsupported C array data action for {argument.owner_path!r}")
        if argument.datatype_family is not DatatypeFamily.STRING:
            PrimitiveScalarTypeRegistry.type_for(argument.semantic_type_name)

    def _require_raw_array_argument_supported(self, argument: ArgumentTransferPlan) -> None:
        """Require one completed opaque address with concrete pointee layout."""
        self._require_raw_array_shape_supported(argument)
        self._require_raw_array_actions_supported(argument)
        self._require_array_element_supported(argument)

    def _require_raw_array_shape_supported(self, argument: ArgumentTransferPlan) -> None:
        """Require concrete dense raw-pointee shape facts."""
        array = argument.array
        if array is None or array.rank is None or not 1 <= array.rank <= 15:
            raise ValueError(f"Unsupported C raw array rank for {argument.owner_path!r}")
        if array.contiguous is not True or array.category != "raw_address":
            raise ValueError(f"Unsupported C raw array layout for {argument.owner_path!r}")

    def _require_raw_array_actions_supported(self, argument: ArgumentTransferPlan) -> None:
        """Require the opaque non-copying raw-address action pair."""
        if argument.bridge.handoff_mode is not ArgumentHandoffMode.OPAQUE_ADDRESS:
            raise ValueError(f"Unsupported C raw array handoff for {argument.owner_path!r}")
        if argument.bridge.data_action is not BridgeDataAction.ASSOCIATE_VIEW:
            raise ValueError(f"Unsupported C raw array data action for {argument.owner_path!r}")

    def _require_array_element_supported(self, argument: ArgumentTransferPlan) -> None:
        """Require one supported primitive or fixed-character array element."""
        array = argument.array
        if argument.datatype_family is DatatypeFamily.STRING:
            if array is None or array.itemsize is None or array.itemsize <= 0:
                raise ValueError(f"Unsupported C raw character array for {argument.owner_path!r}")
            return
        PrimitiveScalarTypeRegistry.type_for(argument.semantic_type_name)

    def _require_array_binding_result_supported(self, result: ResultPlan) -> None:
        """Require one fixed-shape ordinary array result consumer."""
        if result.native_array_handle is not None:
            self._require_owned_native_array_result_supported(result)
            return
        if result.array is None or result.array.rank is None:
            raise ValueError(f"Unsupported C array result for {result.owner_path!r}")
        if result.bridge.data_action is not BridgeDataAction.COPY_REPRESENTATION:
            raise ValueError(f"Unsupported C array result data action for {result.owner_path!r}")
        if result.datatype_family is DatatypeFamily.STRING:
            if result.array.itemsize is None or result.array.itemsize <= 0:
                raise ValueError(f"Unsupported C character array result for {result.owner_path!r}")
            return
        PrimitiveScalarTypeRegistry.type_for(result.semantic_type_name)

    def _require_owned_native_array_result_supported(self, result: ResultPlan) -> None:
        """Require one wrapper-owned allocatable result descriptor."""
        handle = result.native_array_handle
        if (
            handle is None
            or handle.descriptor_kind is not NativeArrayDescriptorKind.ALLOCATABLE
            or handle.handoff.abi is not NativeDescriptorHandoffABI.OWNED_RESULT_STORAGE
            or handle.array.rank is None
        ):
            raise ValueError(f"Unsupported C owned native array result for {result.owner_path!r}")
        if self._native_array_cfi_type(result) is None:
            raise ValueError(f"Missing CFI result element type for {result.owner_path!r}")

    def _require_array_result_supported(self, function: FunctionPlan, slot: NativeCallSlotPlan) -> None:
        """Require one hidden fixed-shape array output slot."""
        if slot.native_array_handle is not None:
            self._require_owned_native_array_slot_supported(function, slot)
            return
        self._require_ordinary_array_result_slot_supported(function, slot)

    def _require_owned_native_array_slot_supported(
        self,
        function: FunctionPlan,
        slot: NativeCallSlotPlan,
    ) -> None:
        """Require one hidden wrapper-owned descriptor result slot."""
        result = next((item for item in function.results if item.native_call_slot is slot), None)
        if result is None:
            raise ValueError(f"Unclaimed C native array handle output for {slot.owner_path!r}")
        self._require_owned_native_array_result_supported(result)

    def _require_ordinary_array_result_slot_supported(
        self,
        function: FunctionPlan,
        slot: NativeCallSlotPlan,
    ) -> None:
        """Require one hidden fixed-shape ordinary-array output slot."""
        if slot.array is None or slot.array.rank is None:
            raise ValueError(f"Unsupported C array output for {slot.owner_path!r}")
        if slot.bridge_data_action is not BridgeDataAction.COPY_REPRESENTATION:
            raise ValueError(f"Unsupported C array output data action for {slot.owner_path!r}")
        if not any(result.native_call_slot is slot for result in function.results):
            raise ValueError(f"Unclaimed C array output for {slot.owner_path!r}")
        if slot.datatype_family is DatatypeFamily.STRING:
            if slot.array.itemsize is None or slot.array.itemsize <= 0:
                raise ValueError(f"Unsupported C character array output for {slot.owner_path!r}")
            return
        if slot.semantic_type_name is None:
            raise ValueError(f"Missing C array output datatype for {slot.owner_path!r}")
        PrimitiveScalarTypeRegistry.type_for(slot.semantic_type_name)

    # String support checks.
    def _require_string_argument_supported(self, argument: ArgumentTransferPlan) -> None:
        """Require a completed string value, storage, or raw-address action."""
        if argument.datatype_family is not DatatypeFamily.STRING:
            raise ValueError(f"Unsupported C string datatype for {argument.owner_path!r}")
        if argument.bridge.data_action is not BridgeDataAction.COPY_REPRESENTATION:
            raise ValueError(f"Unsupported C string data action for {argument.owner_path!r}")
        action = argument.binding.python_action
        if action is PythonBarrierAction.STRING_VALUE:
            self._require_string_value_argument_supported(argument)
            return
        if action not in {PythonBarrierAction.STRING_STORAGE, PythonBarrierAction.RAW_ADDRESS}:
            raise ValueError(f"Unsupported C string boundary for {argument.owner_path!r}: {action!r}")
        self._require_string_address_argument_supported(argument)

    def _require_string_value_argument_supported(self, argument: ArgumentTransferPlan) -> None:
        """Require one character-buffer value handoff."""
        if argument.bridge.handoff_mode is not ArgumentHandoffMode.CHARACTER_BUFFER:
            raise ValueError(f"Unsupported C string handoff for {argument.owner_path!r}")
        if argument.binding.codegen_action not in {CodegenAction.CALL_LOCAL_INPUT, CodegenAction.COPY_IN_OUT}:
            raise ValueError(f"Unsupported C string codegen action for {argument.owner_path!r}")

    def _require_string_address_argument_supported(self, argument: ArgumentTransferPlan) -> None:
        """Require one fixed storage/raw-address handoff."""
        if argument.bridge.handoff_mode is not ArgumentHandoffMode.OPAQUE_ADDRESS:
            raise ValueError(f"Unsupported C string address handoff for {argument.owner_path!r}")
        if argument.binding.codegen_action is not CodegenAction.IN_PLACE_ARGUMENT:
            raise ValueError(f"Unsupported C string address action for {argument.owner_path!r}")
        if argument.character_length is None or argument.character_length <= 0:
            raise ValueError(f"Unsupported C string address length for {argument.owner_path!r}")

    def _require_string_result_supported(self, function: FunctionPlan, slot: NativeCallSlotPlan) -> None:
        """Require one fixed string result slot or status-message slot."""
        if slot.character_length is None or slot.character_length <= 0:
            raise ValueError(f"Unsupported C string output for {slot.owner_path!r}")
        if slot.bridge_data_action is not BridgeDataAction.COPY_REPRESENTATION:
            raise ValueError(f"Unsupported C string bridge data action for {slot.owner_path!r}")
        policy = function.binding.status_error
        if policy is not None and policy.message_role == slot.symbolic_role:
            return
        if any(result.native_call_slot is slot for result in function.results):
            return
        raise ValueError(f"Unsupported C string output for {slot.owner_path!r}")

    def _require_string_binding_result_supported(self, result: ResultPlan) -> None:
        """Require one fixed string result consumer with a justified bridge copy."""
        if result.character_length is None or result.character_length <= 0:
            raise ValueError(f"Unsupported C string result for {result.owner_path!r}")
        if result.bridge.data_action is not BridgeDataAction.COPY_REPRESENTATION:
            raise ValueError(f"Unsupported C string result data action for {result.owner_path!r}")

    def _require_writeback_supported(self, action: LifecycleActionPlan) -> None:
        """Require one object-kind-specific binding copy-out action."""
        if action.phase is not WritebackPhase.COPY_OUT:
            return
        if action.binding is None:
            return
        if action.object_kind is ObjectKind.NUMPY_ARRAY:
            if action.binding.codegen_action is not CodegenAction.IN_PLACE_ARGUMENT:
                raise ValueError(f"Unsupported C array writeback for {action.owner_path!r}")
            return
        if action.binding.datatype_family is DatatypeFamily.STRING:
            if action.binding.codegen_action is not CodegenAction.COPY_IN_OUT:
                raise ValueError(f"Unsupported C string writeback for {action.owner_path!r}")
            return
        PrimitiveScalarTypeRegistry.type_for(action.binding.semantic_type_name)

    def _visit_ModulePlan(self, plan: ModulePlan) -> tuple[CModule, CHeader]:
        """Return a complete C module and header from one shared plan."""
        functions = tuple(function for namespace in plan.namespaces for function in self.visit(namespace))
        needs_runtime = self.requires_runtime_support(plan)
        needs_free = self._module_needs_allocator(plan)
        c_module = CModule(
            name=f"{plan.binding.owner_path}_wrapper",
            defines=self._module_defines(needs_runtime),
            includes=self._module_includes(plan, needs_runtime, needs_free),
            declarations=self._module_declarations(plan),
            functions=(
                *self._module_allocator_functions(needs_free),
                *self._native_array_operation_functions(plan),
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
            function.arguments or function.results for function in self._functions(plan)
        )

    def _module_needs_allocator(self, plan: ModulePlan) -> bool:
        """Return whether emitted bridge-owned copies need the shared allocator."""
        return any(
            variable.binding.getter_action is ModuleGetterAction.NULLABLE_SNAPSHOT
            or (
                variable.native_array_handle is not None
                and variable.native_array_handle.extraction_action
                is NativeArrayExtractionAction.READ_ONLY_DETACHED_COPY
            )
            for variable in self._variables(plan)
        ) or any(self._function_needs_allocator(function) for function in self._functions(plan))

    def _function_needs_allocator(self, function: FunctionPlan) -> bool:
        """Return whether one binding/bridge function owns allocated string storage."""
        return (
            any(
                result.scalar_descriptor is not None
                or result.object_kind in {ObjectKind.STRING, ObjectKind.NUMPY_ARRAY}
                for result in function.results
            )
            or any(
                argument.object_kind is ObjectKind.STRING
                and argument.binding.codegen_action is CodegenAction.COPY_IN_OUT
                for argument in function.arguments
            )
            or any(
                slot.scalar_descriptor is not None or slot.object_kind in {ObjectKind.STRING, ObjectKind.NUMPY_ARRAY}
                for slot in function.native_call_slots
                if slot.source_kind == "result"
            )
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
            *((CInclude("string.h"),) if self._module_uses_memory_copy(plan) else ()),
            *((CInclude("stdlib.h"),) if needs_free else ()),
            *(CInclude(header) for header in plan.required_headers),
            *self._module_runtime_includes(needs_runtime),
            CInclude(f"{plan.binding.owner_path}_wrapper.h", system=False),
        )

    def _module_uses_string_values(self, plan: ModulePlan) -> bool:
        """Return whether binding conversion needs C string helpers."""
        return any(
            argument.binding.python_action is PythonBarrierAction.STRING_VALUE
            for function in self._functions(plan)
            for argument in function.arguments
        )

    def _module_uses_memory_copy(self, plan: ModulePlan) -> bool:
        """Return whether binding conversion emits string or array byte copies."""
        return self._module_uses_string_values(plan) or any(
            result.object_kind is ObjectKind.NUMPY_ARRAY
            for function in self._functions(plan)
            for result in function.results
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
        CComment | CDeclaration | CFunctionPrototype | CMethodDefTable | CModuleDef | CModulePropertySupport,
        ...,
    ]:
        """Return ordered bridge, helper, table, and module declarations."""
        property_support = tuple(
            support
            for namespace in plan.namespaces
            if (support := self._module_property_support(plan, namespace)) is not None
        )
        return (
            *self._module_contract_comments(plan),
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
            *self._native_array_operation_declarations(plan),
            *(self._method_table(plan, namespace) for namespace in plan.namespaces),
            *(self._module_def(plan, namespace) for namespace in plan.namespaces),
            *property_support,
        )

    def _module_contract_comments(self, plan: ModulePlan) -> tuple[CComment, ...]:
        """Emit maintainer-visible ownership notes selected by module-handle policy."""
        if not any(
            variable.native_array_handle is not None
            and variable.native_array_handle.extraction_action is NativeArrayExtractionAction.READ_ONLY_DETACHED_COPY
            for variable in self._variables(plan)
        ):
            return ()
        return (
            CComment("Plain allocatable module arrays without Aliased are copied into Python-owned NumPy arrays."),
            CComment("Returned module snapshots are read-only and detached from later native changes."),
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

    # Owned native-array-handle operation tables.
    def _native_array_operation_declarations(
        self,
        plan: ModulePlan,
    ) -> tuple[CFunctionPrototype | CDeclaration, ...]:
        """Declare private operation wrappers and their callable definitions."""
        declarations = []
        for variable in self._module_native_array_variables(plan):
            declarations.extend(
                (
                    CDeclaration(
                        self._module_native_array_cache_name(variable),
                        "static PyObject *",
                        CodeExpression("NULL"),
                    ),
                    CDeclaration(
                        self._module_native_array_owner_name(variable),
                        "static PyObject *",
                        CodeExpression("NULL"),
                    ),
                )
            )
            if variable.native_array_handle is None:
                continue
            for operation in variable.native_array_handle.operations:
                name = self._module_native_array_operation_name(variable, operation)
                declarations.extend(
                    (
                        CFunctionPrototype(
                            name,
                            "PyObject *",
                            (CParameter("self", "PyObject *"), CParameter("args", "PyObject *")),
                            storage="static",
                        ),
                        CDeclaration(
                            self._module_native_array_operation_def_name(variable, operation),
                            "static PyMethodDef",
                            CodeExpression(f'{{"{name}", (PyCFunction){name}, METH_VARARGS, ""}}'),
                        ),
                    )
                )
        for function, result in self._owned_native_array_results(plan):
            for operation in result.native_array_handle.operations:
                name = self._owned_native_array_operation_name(function, result, operation)
                declarations.extend(
                    (
                        CFunctionPrototype(
                            name,
                            "PyObject *",
                            (CParameter("self", "PyObject *"), CParameter("args", "PyObject *")),
                            storage="static",
                        ),
                        CDeclaration(
                            self._owned_native_array_operation_def_name(function, result, operation),
                            "static PyMethodDef",
                            CodeExpression(f'{{"{name}", (PyCFunction){name}, METH_VARARGS, ""}}'),
                        ),
                    )
                )
        return tuple(declarations)

    def _native_array_operation_functions(self, plan: ModulePlan) -> tuple[CFunction, ...]:
        """Lower every planned owned-descriptor operation into a named C method."""
        return (
            *(
                self._module_native_array_operation_function(variable, operation)
                for variable in self._module_native_array_variables(plan)
                if variable.native_array_handle is not None
                for operation in variable.native_array_handle.operations
            ),
            *(
                self._owned_native_array_operation_function(function, result, operation)
                for function, result in self._owned_native_array_results(plan)
                for operation in result.native_array_handle.operations
            ),
        )

    def _module_native_array_variables(self, plan: ModulePlan) -> tuple[ModuleVariablePlan, ...]:
        """Return borrowed module-handle plans in stable namespace order."""
        return tuple(
            variable
            for variable in self._variables(plan)
            if variable.binding.getter_action is ModuleGetterAction.NATIVE_ARRAY_HANDLE
        )

    # Borrowed module native-array-handle operations.
    def _module_native_array_operation_function(
        self,
        variable: ModuleVariablePlan,
        operation: NativeArrayOperation,
    ) -> CFunction:
        """Lower one planned borrowed-module operation into a private callable."""
        return CFunction(
            self._module_native_array_operation_name(variable, operation),
            "PyObject *",
            parameters=(CParameter("self", "PyObject *"), CParameter("args", "PyObject *")),
            storage="static",
            body=self._module_native_array_operation_body(variable, operation),
        )

    def _module_native_array_operation_body(
        self,
        variable: ModuleVariablePlan,
        operation: NativeArrayOperation,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf | CReturn, ...]:
        """Dispatch one module operation without rediscovering semantic policy."""
        if operation in {
            NativeArrayOperation.NATIVE_BYTE_ORDER,
            NativeArrayOperation.ALIGNED,
            NativeArrayOperation.WRITEABLE,
            NativeArrayOperation.LAYOUT,
        }:
            return self._module_native_array_metadata_body(operation)
        if operation in {
            NativeArrayOperation.ALLOCATED,
            NativeArrayOperation.ASSOCIATED,
            NativeArrayOperation.CONTIGUOUS,
            NativeArrayOperation.ELEMENT_LENGTH,
            NativeArrayOperation.ARRAY_ACTUAL,
        }:
            return self._module_native_array_query_body(variable, operation)
        return self._module_native_array_data_operation_body(variable, operation)

    @staticmethod
    def _module_native_array_metadata_body(
        operation: NativeArrayOperation,
    ) -> tuple[CReturn, ...]:
        """Return binding-known metadata that requires no bridge call."""
        if operation is NativeArrayOperation.LAYOUT:
            return (CReturn(CodeExpression('PyUnicode_FromString("F")')),)
        return (CReturn(CodeExpression("PyBool_FromLong(1)")),)

    def _module_native_array_query_body(
        self,
        variable: ModuleVariablePlan,
        operation: NativeArrayOperation,
    ) -> tuple[CReturn, ...]:
        """Return one scalar fact queried from the native bridge."""
        call = f"{self._module_native_array_bridge_operation_name(variable, operation)}()"
        if operation in {
            NativeArrayOperation.ALLOCATED,
            NativeArrayOperation.ASSOCIATED,
            NativeArrayOperation.CONTIGUOUS,
        }:
            expression = f"PyBool_FromLong({call})"
        elif operation is NativeArrayOperation.ELEMENT_LENGTH:
            expression = f"PyLong_FromLongLong((long long){call})"
        else:
            expression = f"PyLong_FromVoidPtr({call})"
        return (CReturn(CodeExpression(expression)),)

    def _module_native_array_data_operation_body(
        self,
        variable: ModuleVariablePlan,
        operation: NativeArrayOperation,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf | CReturn, ...]:
        """Lower shape, extraction, descriptor, and mutation operations."""
        if operation is NativeArrayOperation.SHAPE:
            return self._module_native_array_shape_body(variable)
        if operation is NativeArrayOperation.TO_NUMPY:
            handle = variable.native_array_handle
            if handle is not None and handle.extraction_action is NativeArrayExtractionAction.READ_ONLY_DETACHED_COPY:
                return self._module_native_array_snapshot_body(variable)
            return self._module_native_array_descriptor_body(variable)
        if operation is NativeArrayOperation.DESCRIPTOR:
            return self._module_native_array_descriptor_body(variable)
        if operation in {NativeArrayOperation.ALLOCATE, NativeArrayOperation.RESIZE}:
            return self._module_native_array_shape_mutation_body(variable, operation)
        if operation in {
            NativeArrayOperation.DEALLOCATE,
            NativeArrayOperation.NULLIFY,
        }:
            return (
                CExpressionStatement(
                    CodeExpression(f"{self._module_native_array_bridge_operation_name(variable, operation)}()")
                ),
                CExpressionStatement(CodeExpression("Py_RETURN_NONE")),
            )
        raise ValueError(f"Unsupported module native array operation for {variable.owner_path!r}: {operation!r}")

    def _module_native_array_shape_body(
        self,
        variable: ModuleVariablePlan,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf | CReturn, ...]:
        """Return current module-array extents as one Python tuple."""
        handle = variable.native_array_handle
        if handle is None or handle.array.rank is None:
            raise ValueError(f"Module handle {variable.owner_path!r} has no rank")
        rank = handle.array.rank
        extents = tuple(f"extent_{axis}" for axis in range(rank))
        return (
            *(CDeclaration(name, "int64_t", CodeExpression("0")) for name in extents),
            CExpressionStatement(
                CodeExpression(
                    f"{self._module_native_array_bridge_operation_name(variable, NativeArrayOperation.SHAPE)}("
                    f"{', '.join(f'&{name}' for name in extents)})"
                )
            ),
            CDeclaration("shape", "PyObject *", CodeExpression(f"PyTuple_New({rank})")),
            CIf(CodeExpression("shape == NULL"), body=(CReturn(CodeExpression("NULL")),)),
            *(
                CExpressionStatement(
                    CodeExpression(f"PyTuple_SET_ITEM(shape, {axis}, PyLong_FromLongLong((long long){name}))")
                )
                for axis, name in enumerate(extents)
            ),
            CExpressionStatement(CodeExpression("if (PyErr_Occurred()) { Py_DECREF(shape); return NULL; }")),
            CReturn(CodeExpression("shape")),
        )

    def _module_native_array_descriptor_body(
        self,
        variable: ModuleVariablePlan,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf | CReturn, ...]:
        """Return standard descriptor facts for module extraction and handoff."""
        handle = variable.native_array_handle
        if handle is None or handle.array.rank is None:
            raise ValueError(f"Module handle {variable.owner_path!r} has no descriptor rank")
        if handle.descriptor_kind is NativeArrayDescriptorKind.POINTER:
            return self._module_pointer_descriptor_body(variable)
        return self._module_contiguous_descriptor_body(variable)

    def _module_native_array_snapshot_body(
        self,
        variable: ModuleVariablePlan,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf | CReturn, ...]:
        """Adopt a bridge-owned detached snapshot long enough for runtime copying."""
        handle = variable.native_array_handle
        if handle is None or handle.array.rank is None:
            raise ValueError(f"Module snapshot {variable.owner_path!r} has no rank")
        if variable.datatype_family is DatatypeFamily.STRING:
            raise ValueError(f"Deferred character module snapshot {variable.owner_path!r} is not implemented")
        rank = handle.array.rank
        extents = tuple(f"extent_{axis}" for axis in range(rank))
        dims = "snapshot_dims"
        data = "snapshot_data"
        array = "snapshot_array"
        base = "snapshot_base"
        scalar_type = PrimitiveScalarTypeRegistry.type_for(variable.semantic_type_name)
        if scalar_type.numpy_type_macro is None:
            raise ValueError(f"Module snapshot {variable.owner_path!r} has no NumPy type")
        return (
            CDeclaration(
                data,
                "void *",
                CodeExpression(
                    f"{self._module_native_array_bridge_operation_name(variable, NativeArrayOperation.TO_NUMPY)}()"
                ),
            ),
            CIf(
                CodeExpression(f"{data} == NULL"),
                body=(
                    CExpressionStatement(CodeExpression("Py_INCREF(Py_None)")),
                    CReturn(CodeExpression("Py_None")),
                ),
            ),
            *(CDeclaration(name, "int64_t", CodeExpression("0")) for name in extents),
            CExpressionStatement(
                CodeExpression(
                    f"{self._module_native_array_bridge_operation_name(variable, NativeArrayOperation.SHAPE)}("
                    f"{', '.join(f'&{name}' for name in extents)})"
                )
            ),
            CDeclaration(
                f"{dims}[]",
                "npy_intp",
                CodeExpression(f"{{{', '.join(extents)}}}"),
            ),
            CDeclaration(
                array,
                "PyObject *",
                CodeExpression(
                    f"(PyObject *)PyArray_New(&PyArray_Type, {rank}, {dims}, {scalar_type.numpy_type_macro}, "
                    f"NULL, {data}, 0, NPY_ARRAY_F_CONTIGUOUS | NPY_ARRAY_WRITEABLE, NULL)"
                ),
            ),
            CIf(
                CodeExpression(f"{array} == NULL"),
                body=(
                    CExpressionStatement(CodeExpression(f"free({data})")),
                    CReturn(CodeExpression("NULL")),
                ),
            ),
            *self._capsule_base_attachment_nodes(array, base, data),
            CReturn(CodeExpression(array)),
        )

    def _module_contiguous_descriptor_body(
        self,
        variable: ModuleVariablePlan,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf | CReturn, ...]:
        """Build allocatable descriptor facts from native data and extents."""
        handle = variable.native_array_handle
        if handle is None or handle.array.rank is None:
            raise ValueError(f"Module handle {variable.owner_path!r} has no descriptor rank")
        rank = handle.array.rank
        scalar_type = (
            None
            if variable.datatype_family is DatatypeFamily.STRING
            else PrimitiveScalarTypeRegistry.type_for(variable.semantic_type_name)
        )
        extents = tuple(f"extent_{axis}" for axis in range(rank))
        elem_len = (
            f"{self._module_native_array_bridge_operation_name(variable, NativeArrayOperation.ELEMENT_LENGTH)}()"
            if variable.datatype_family is DatatypeFamily.STRING
            else f"sizeof({scalar_type.c_spelling})"
        )
        nodes: list[CDeclaration | CExpressionStatement | CIf | CReturn] = [
            CDeclaration(
                "base_addr",
                "void *",
                CodeExpression(
                    f"{self._module_native_array_bridge_operation_name(variable, NativeArrayOperation.ARRAY_ACTUAL)}()"
                ),
            ),
            *(CDeclaration(name, "int64_t", CodeExpression("0")) for name in extents),
            CExpressionStatement(
                CodeExpression(
                    f"{self._module_native_array_bridge_operation_name(variable, NativeArrayOperation.SHAPE)}("
                    f"{', '.join(f'&{name}' for name in extents)})"
                )
            ),
            CDeclaration("dimensions", "PyObject *", CodeExpression(f"PyList_New({rank})")),
            CIf(CodeExpression("dimensions == NULL"), body=(CReturn(CodeExpression("NULL")),)),
            CDeclaration("stride", "int64_t", CodeExpression(elem_len)),
        ]
        for axis, extent in enumerate(extents):
            nodes.extend(
                (
                    CDeclaration(
                        f"dimension_{axis}",
                        "PyObject *",
                        CodeExpression(
                            f'Py_BuildValue("{{sL,sL,sL}}", "lower_bound", (long long)0, '
                            f'"extent", (long long){extent}, "sm", (long long)stride)'
                        ),
                    ),
                    CIf(
                        CodeExpression(f"dimension_{axis} == NULL"),
                        body=(
                            CExpressionStatement(CodeExpression("Py_DECREF(dimensions)")),
                            CReturn(CodeExpression("NULL")),
                        ),
                    ),
                    CExpressionStatement(CodeExpression(f"PyList_SET_ITEM(dimensions, {axis}, dimension_{axis})")),
                    CExpressionStatement(CodeExpression(f"stride *= ({extent} > 0 ? {extent} : 1)")),
                )
            )
        nodes.extend(self._descriptor_record_return_nodes("base_addr", elem_len, rank))
        return tuple(nodes)

    def _module_pointer_descriptor_body(
        self,
        variable: ModuleVariablePlan,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf | CReturn, ...]:
        """Decode a call-local standard pointer descriptor without copying data."""
        handle = variable.native_array_handle
        if handle is None or handle.array.rank is None:
            raise ValueError(f"Pointer module handle {variable.owner_path!r} has no descriptor rank")
        cfi_type = self._module_native_array_cfi_type(variable)
        if cfi_type is None:
            raise ValueError(f"Pointer module handle {variable.owner_path!r} has no CFI type")
        rank = handle.array.rank
        elem_len = self._module_native_array_elem_size(variable)
        return (
            CDeclaration("descriptor_storage", f"CFI_CDESC_T({rank})"),
            CDeclaration("descriptor", "CFI_cdesc_t *", CodeExpression("(CFI_cdesc_t *)&descriptor_storage")),
            CDeclaration("status", "int", CodeExpression("CFI_SUCCESS")),
            CExpressionStatement(
                CodeExpression(
                    f"status = CFI_establish(descriptor, NULL, CFI_attribute_pointer, "
                    f"{cfi_type}, {elem_len}, {rank}, NULL)"
                )
            ),
            CIf(
                CodeExpression("status != CFI_SUCCESS"),
                body=(
                    CExpressionStatement(
                        CodeExpression(
                            'PyErr_SetString(PyExc_RuntimeError, "failed to establish pointer descriptor reader")'
                        )
                    ),
                    CReturn(CodeExpression("NULL")),
                ),
            ),
            CExpressionStatement(
                CodeExpression(
                    f"{self._module_native_array_bridge_operation_name(variable, NativeArrayOperation.DESCRIPTOR)}"
                    "(descriptor)"
                )
            ),
            *self._native_array_descriptor_record_nodes(rank, "descriptor"),
        )

    def _descriptor_record_return_nodes(
        self,
        base_addr: str,
        elem_len: str,
        rank: int,
    ) -> tuple[CDeclaration | CExpressionStatement | CReturn, ...]:
        """Finish one standard descriptor mapping from existing dimensions."""
        return (
            CDeclaration(
                "descriptor_record",
                "PyObject *",
                CodeExpression(
                    f'Py_BuildValue("{{sK,sK,si,sO}}", "base_addr", '
                    f'(unsigned long long)(uintptr_t){base_addr}, "elem_len", '
                    f'(unsigned long long)({elem_len}), "rank", {rank}, "dim", dimensions)'
                ),
            ),
            CExpressionStatement(CodeExpression("Py_DECREF(dimensions)")),
            CReturn(CodeExpression("descriptor_record")),
        )

    def _module_native_array_shape_mutation_body(
        self,
        variable: ModuleVariablePlan,
        operation: NativeArrayOperation,
    ) -> tuple[CDeclaration | CExpressionStatement | CReturn, ...]:
        """Parse and forward one planned module allocation/resize shape."""
        handle = variable.native_array_handle
        if handle is None or handle.array.rank is None:
            raise ValueError(f"Module handle {variable.owner_path!r} has no mutation rank")
        rank = handle.array.rank
        objects = tuple(f"extent_{axis}_obj" for axis in range(rank))
        extents = tuple(f"extent_{axis}" for axis in range(rank))
        return (
            *(CDeclaration(name, "PyObject *") for name in objects),
            *(CDeclaration(name, "int64_t", CodeExpression("0")) for name in extents),
            CExpressionStatement(
                CodeExpression(
                    f'if (!PyArg_ParseTuple(args, "{"O" * rank}", '
                    f"{', '.join(f'&{name}' for name in objects)})) return NULL"
                )
            ),
            *(
                CExpressionStatement(
                    CodeExpression(f"{extent} = (int64_t)PyLong_AsLongLong({obj}); if (PyErr_Occurred()) return NULL")
                )
                for extent, obj in zip(extents, objects, strict=True)
            ),
            CExpressionStatement(
                CodeExpression(
                    f"{self._module_native_array_bridge_operation_name(variable, operation)}({', '.join(extents)})"
                )
            ),
            CExpressionStatement(CodeExpression("Py_RETURN_NONE")),
        )

    def _module_native_array_operation_name(
        self,
        variable: ModuleVariablePlan,
        operation: NativeArrayOperation,
    ) -> str:
        owner = re.sub(r"\W", "_", variable.owner_path).casefold()
        return f"x2py_module_{owner}_{operation.value}"

    def _module_native_array_operation_def_name(
        self,
        variable: ModuleVariablePlan,
        operation: NativeArrayOperation,
    ) -> str:
        return f"{self._module_native_array_operation_name(variable, operation)}_def"

    def _module_native_array_bridge_operation_name(
        self,
        variable: ModuleVariablePlan,
        operation: NativeArrayOperation,
    ) -> str:
        return f"bind_c_{variable.symbol_name}_{operation.value}"

    def _module_native_array_cache_name(self, variable: ModuleVariablePlan) -> str:
        owner = re.sub(r"\W", "_", variable.owner_path).casefold()
        return f"x2py_module_{owner}_handle"

    def _module_native_array_owner_name(self, variable: ModuleVariablePlan) -> str:
        owner = re.sub(r"\W", "_", variable.owner_path).casefold()
        return f"x2py_module_{owner}_owner"

    def _owned_native_array_results(self, plan: ModulePlan) -> tuple[tuple[FunctionPlan, ResultPlan], ...]:
        """Return wrapper-owned descriptor result plans in stable generation order."""
        return tuple(
            (function, result)
            for function in self._functions(plan)
            for result in function.results
            if result.native_array_handle is not None
            and result.native_array_handle.handoff.abi is NativeDescriptorHandoffABI.OWNED_RESULT_STORAGE
        )

    def _owned_native_array_operation_function(
        self,
        function: FunctionPlan,
        result: ResultPlan,
        operation: NativeArrayOperation,
    ) -> CFunction:
        """Dispatch one planned owned-descriptor runtime operation."""
        name = self._owned_native_array_operation_name(function, result, operation)
        body = self._owned_native_array_operation_body(result, operation)
        return CFunction(
            name,
            "PyObject *",
            parameters=(CParameter("self", "PyObject *"), CParameter("args", "PyObject *")),
            storage="static",
            body=body,
        )

    def _owned_native_array_operation_body(
        self,
        result: ResultPlan,
        operation: NativeArrayOperation,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf | CReturn, ...]:
        """Return one operation body over persistent CFI owner storage."""
        if operation is NativeArrayOperation.RESIZE:
            return self._owned_native_array_resize_body(result)
        handler = self._owned_native_array_operation_handler(operation)
        return (*self._owned_native_array_owner_nodes("owner"), *handler(result))

    def _owned_native_array_operation_handler(self, operation: NativeArrayOperation):
        """Return one directly named operation lowerer."""
        handlers = {
            NativeArrayOperation.SHAPE: self._owned_native_array_descriptor_record_body,
            NativeArrayOperation.TO_NUMPY: self._owned_native_array_descriptor_record_body,
            NativeArrayOperation.ELEMENT_LENGTH: self._owned_native_array_element_length_body,
            NativeArrayOperation.ARRAY_ACTUAL: self._owned_native_array_actual_body,
            NativeArrayOperation.DESCRIPTOR: self._owned_native_array_descriptor_body,
            NativeArrayOperation.ALLOCATED: self._owned_native_array_allocated_body,
            NativeArrayOperation.NATIVE_BYTE_ORDER: self._owned_native_array_true_body,
            NativeArrayOperation.ALIGNED: self._owned_native_array_true_body,
            NativeArrayOperation.WRITEABLE: self._owned_native_array_true_body,
            NativeArrayOperation.LAYOUT: self._owned_native_array_layout_body,
            NativeArrayOperation.DEALLOCATE: self._owned_native_array_deallocate_body,
            NativeArrayOperation.DESTROY: self._owned_native_array_destroy_body,
        }
        try:
            return handlers[operation]
        except KeyError:
            raise ValueError(f"Unsupported owned native array operation {operation.value!r}") from None

    def _owned_native_array_descriptor_record_body(
        self,
        result: ResultPlan,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf | CReturn, ...]:
        """Expose one owned descriptor record for shape or NumPy extraction."""
        handle = result.native_array_handle
        if handle is None or handle.array.rank is None:
            raise ValueError(f"Owned result {result.owner_path!r} has no descriptor rank")
        return self._native_array_descriptor_record_nodes(handle.array.rank, "owner_descriptor")

    def _owned_native_array_actual_body(self, _result: ResultPlan) -> tuple[CReturn, ...]:
        """Expose the current owned allocation data address."""
        return (CReturn(CodeExpression("PyLong_FromVoidPtr(owner_descriptor->base_addr)")),)

    def _owned_native_array_element_length_body(self, _result: ResultPlan) -> tuple[CReturn, ...]:
        """Expose the current deferred character element width."""
        return (CReturn(CodeExpression("PyLong_FromSize_t(owner_descriptor->elem_len)")),)

    def _owned_native_array_descriptor_body(self, _result: ResultPlan) -> tuple[CReturn, ...]:
        """Expose persistent standard-descriptor storage."""
        return (CReturn(CodeExpression("PyLong_FromVoidPtr(owner_descriptor)")),)

    def _owned_native_array_allocated_body(self, _result: ResultPlan) -> tuple[CReturn, ...]:
        """Report the current allocation state."""
        return (CReturn(CodeExpression("PyBool_FromLong(owner_descriptor->base_addr != NULL)")),)

    def _owned_native_array_true_body(self, _result: ResultPlan) -> tuple[CReturn, ...]:
        """Return one invariant true array capability."""
        return (CReturn(CodeExpression("PyBool_FromLong(1)")),)

    def _owned_native_array_layout_body(self, _result: ResultPlan) -> tuple[CReturn, ...]:
        """Return the planned Fortran layout marker."""
        return (CReturn(CodeExpression('PyUnicode_FromString("F")')),)

    def _owned_native_array_deallocate_body(
        self,
        _result: ResultPlan,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf | CReturn, ...]:
        """Deallocate payload while retaining owner storage."""
        return self._owned_native_array_deallocate_nodes(free_owner=False)

    def _owned_native_array_destroy_body(
        self,
        _result: ResultPlan,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf | CReturn, ...]:
        """Destroy payload and persistent owner storage."""
        return self._owned_native_array_deallocate_nodes(free_owner=True)

    def _owned_native_array_owner_nodes(
        self,
        prefix: str,
    ) -> tuple[CDeclaration | CExpressionStatement, ...]:
        """Decode the persistent descriptor owner passed by the runtime adapter."""
        return (
            CDeclaration(f"{prefix}_obj", "PyObject *"),
            CDeclaration(f"{prefix}_descriptor", "CFI_cdesc_t *", CodeExpression("NULL")),
            CExpressionStatement(CodeExpression(f'if (!PyArg_ParseTuple(args, "O", &{prefix}_obj)) return NULL')),
            CExpressionStatement(
                CodeExpression(f"{prefix}_descriptor = (CFI_cdesc_t *)PyLong_AsVoidPtr({prefix}_obj)")
            ),
            CExpressionStatement(
                CodeExpression(
                    f"if ({prefix}_descriptor == NULL) {{ if (!PyErr_Occurred()) "
                    'PyErr_SetString(PyExc_ReferenceError, "native array owner descriptor is NULL"); return NULL; }'
                )
            ),
        )

    def _native_array_descriptor_record_nodes(
        self,
        rank: int,
        descriptor_name: str,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf | CReturn, ...]:
        """Decode a standard C descriptor into the runtime's mapping protocol."""
        nodes: list[CDeclaration | CExpressionStatement | CIf | CReturn] = [
            CDeclaration("dimensions", "PyObject *", CodeExpression(f"PyList_New({rank})")),
            CIf(CodeExpression("dimensions == NULL"), body=(CReturn(CodeExpression("NULL")),)),
        ]
        for axis in range(rank):
            item = f"dimension_{axis}"
            nodes.extend(
                (
                    CDeclaration(
                        item,
                        "PyObject *",
                        CodeExpression(
                            f'Py_BuildValue("{{sL,sL,sL}}", "lower_bound", '
                            f'(long long){descriptor_name}->dim[{axis}].lower_bound, "extent", '
                            f'(long long){descriptor_name}->dim[{axis}].extent, "sm", '
                            f"(long long){descriptor_name}->dim[{axis}].sm)"
                        ),
                    ),
                    CIf(
                        CodeExpression(f"{item} == NULL"),
                        body=(
                            CExpressionStatement(CodeExpression("Py_DECREF(dimensions)")),
                            CReturn(CodeExpression("NULL")),
                        ),
                    ),
                    CExpressionStatement(CodeExpression(f"PyList_SET_ITEM(dimensions, {axis}, {item})")),
                )
            )
        nodes.extend(
            (
                CDeclaration(
                    "descriptor_record",
                    "PyObject *",
                    CodeExpression(
                        f'Py_BuildValue("{{sK,sK,si,sO}}", "base_addr", '
                        f'(unsigned long long)(uintptr_t){descriptor_name}->base_addr, "elem_len", '
                        f'(unsigned long long){descriptor_name}->elem_len, "rank", '
                        f'(int){descriptor_name}->rank, "dim", dimensions)'
                    ),
                ),
                CExpressionStatement(CodeExpression("Py_DECREF(dimensions)")),
                CReturn(CodeExpression("descriptor_record")),
            )
        )
        return tuple(nodes)

    def _owned_native_array_deallocate_nodes(
        self,
        *,
        free_owner: bool,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf | CReturn, ...]:
        """Release payload and optionally persistent descriptor storage."""
        nodes: list[CDeclaration | CExpressionStatement | CIf | CReturn] = [
            CDeclaration("status", "int", CodeExpression("CFI_SUCCESS")),
            CIf(
                CodeExpression("owner_descriptor->base_addr != NULL"),
                body=(
                    CExpressionStatement(CodeExpression("status = CFI_deallocate(owner_descriptor)")),
                    CIf(
                        CodeExpression("status != CFI_SUCCESS"),
                        body=(
                            *((CExpressionStatement(CodeExpression("free(owner_descriptor)")),) if free_owner else ()),
                            CExpressionStatement(
                                CodeExpression(
                                    'PyErr_SetString(PyExc_RuntimeError, "failed to deallocate owned native array")'
                                )
                            ),
                            CReturn(CodeExpression("NULL")),
                        ),
                    ),
                ),
            ),
        ]
        if free_owner:
            nodes.append(CExpressionStatement(CodeExpression("free(owner_descriptor)")))
        nodes.append(CExpressionStatement(CodeExpression("Py_RETURN_NONE")))
        return tuple(nodes)

    def _owned_native_array_resize_body(
        self,
        result: ResultPlan,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf | CReturn, ...]:
        """Replace owned allocatable payload with one validated requested shape."""
        handle = result.native_array_handle
        if handle is None or handle.array.rank is None:
            raise ValueError(f"Owned result {result.owner_path!r} has no resize rank")
        rank = handle.array.rank
        extent_objects = tuple(f"extent_{axis}_obj" for axis in range(rank))
        targets = ", ".join(f"&{name}" for name in ("owner_obj", *extent_objects))
        nodes: list[CDeclaration | CExpressionStatement | CIf | CReturn] = [
            CDeclaration("owner_obj", "PyObject *"),
            *(CDeclaration(name, "PyObject *") for name in extent_objects),
            CDeclaration("owner_descriptor", "CFI_cdesc_t *", CodeExpression("NULL")),
            CDeclaration(f"lower_bounds[{rank}]", "CFI_index_t"),
            CDeclaration(f"upper_bounds[{rank}]", "CFI_index_t"),
            CDeclaration("status", "int", CodeExpression("CFI_SUCCESS")),
            CExpressionStatement(
                CodeExpression(f'if (!PyArg_ParseTuple(args, "{"O" * (rank + 1)}", {targets})) return NULL')
            ),
            CExpressionStatement(CodeExpression("owner_descriptor = (CFI_cdesc_t *)PyLong_AsVoidPtr(owner_obj)")),
            CExpressionStatement(
                CodeExpression(
                    "if (owner_descriptor == NULL) { if (!PyErr_Occurred()) PyErr_SetString("
                    'PyExc_ReferenceError, "native array owner descriptor is NULL"); return NULL; }'
                )
            ),
        ]
        for axis, item in enumerate(extent_objects):
            nodes.extend(
                (
                    CExpressionStatement(
                        CodeExpression(f"upper_bounds[{axis}] = (CFI_index_t)PyLong_AsLongLong({item}) - 1")
                    ),
                    CExpressionStatement(CodeExpression("if (PyErr_Occurred()) return NULL")),
                    CExpressionStatement(CodeExpression(f"lower_bounds[{axis}] = 0")),
                )
            )
        nodes.extend(
            (
                CIf(
                    CodeExpression("owner_descriptor->base_addr != NULL"),
                    body=(
                        CExpressionStatement(CodeExpression("status = CFI_deallocate(owner_descriptor)")),
                        CExpressionStatement(
                            CodeExpression(
                                "if (status != CFI_SUCCESS) { PyErr_SetString(PyExc_RuntimeError, "
                                '"failed to release owned native array before resize"); return NULL; }'
                            )
                        ),
                    ),
                ),
                CExpressionStatement(
                    CodeExpression(
                        "status = CFI_allocate(owner_descriptor, lower_bounds, upper_bounds, "
                        "owner_descriptor->elem_len)"
                    )
                ),
                CExpressionStatement(
                    CodeExpression(
                        "if (status != CFI_SUCCESS) { PyErr_SetString(PyExc_RuntimeError, "
                        '"failed to resize owned native array"); return NULL; }'
                    )
                ),
                CExpressionStatement(CodeExpression("Py_RETURN_NONE")),
            )
        )
        return tuple(nodes)

    def _owned_native_array_operation_name(
        self,
        _function: FunctionPlan | None,
        result: ResultPlan,
        operation: NativeArrayOperation,
    ) -> str:
        """Return one stable private operation symbol."""
        owner = re.sub(r"\W", "_", result.owner_path).casefold()
        return f"x2py_owned_{owner}_{operation.value}"

    def _owned_native_array_operation_def_name(
        self,
        function: FunctionPlan | None,
        result: ResultPlan,
        operation: NativeArrayOperation,
    ) -> str:
        """Return the private PyMethodDef symbol for one operation."""
        return f"{self._owned_native_array_operation_name(function, result, operation)}_def"

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
            case ModuleGetterAction.NATIVE_ARRAY_HANDLE:
                return self._lower_module_getter_native_array_handle(plan)
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

    def _lower_module_getter_native_array_handle(self, plan: ModuleVariablePlan) -> tuple[CFunction, ...]:
        """Create one stable borrowed runtime handle from planned module operations."""
        handle = plan.native_array_handle
        if handle is None or handle.array.rank is None:
            raise ValueError(f"Module native array handle {plan.owner_path!r} is incomplete")
        cache = self._module_native_array_cache_name(plan)
        owner = self._module_native_array_owner_name(plan)
        prefix = f"{cache}_build"
        nodes: list[CDeclaration | CExpressionStatement | CIf | CReturn] = [
            CIf(
                CodeExpression(f"{cache} != NULL"),
                body=(
                    CExpressionStatement(CodeExpression(f"Py_INCREF({cache})")),
                    CReturn(CodeExpression(cache)),
                ),
            ),
            CDeclaration(f"{prefix}_ops", "PyObject *", CodeExpression("PyDict_New()")),
            CDeclaration(f"{prefix}_operation", "PyObject *", CodeExpression("NULL")),
            CDeclaration(f"{prefix}_runtime", "PyObject *", CodeExpression("NULL")),
            CDeclaration(f"{prefix}_helper", "PyObject *", CodeExpression("NULL")),
            CIf(CodeExpression(f"{prefix}_ops == NULL"), body=(CReturn(CodeExpression("NULL")),)),
        ]
        for operation in handle.operations:
            definition = self._module_native_array_operation_def_name(plan, operation)
            nodes.extend(
                (
                    CExpressionStatement(
                        CodeExpression(f"{prefix}_operation = PyCFunction_NewEx(&{definition}, NULL, NULL)")
                    ),
                    CIf(
                        CodeExpression(f"{prefix}_operation == NULL"),
                        body=(
                            CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_ops)")),
                            CReturn(CodeExpression("NULL")),
                        ),
                    ),
                    CIf(
                        CodeExpression(
                            f'PyDict_SetItemString({prefix}_ops, "{operation.value}", {prefix}_operation) < 0'
                        ),
                        body=(
                            CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_operation)")),
                            CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_ops)")),
                            CReturn(CodeExpression("NULL")),
                        ),
                    ),
                    CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_operation)")),
                )
            )
        nodes.extend(
            (
                CExpressionStatement(
                    CodeExpression(f'{prefix}_runtime = PyImport_ImportModule("x2py.runtime.handles")')
                ),
                CIf(
                    CodeExpression(f"{prefix}_runtime == NULL"),
                    body=(
                        CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_ops)")),
                        CReturn(CodeExpression("NULL")),
                    ),
                ),
                CExpressionStatement(
                    CodeExpression(
                        f"{prefix}_helper = PyObject_GetAttrString({prefix}_runtime, "
                        '"_native_array_handle_from_generated_ops")'
                    )
                ),
                CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_runtime)")),
                CIf(
                    CodeExpression(f"{prefix}_helper == NULL"),
                    body=(
                        CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_ops)")),
                        CReturn(CodeExpression("NULL")),
                    ),
                ),
                CExpressionStatement(
                    CodeExpression(
                        self._native_array_handle_factory_call(
                            helper=f"{prefix}_helper",
                            target=cache,
                            descriptor_kind=handle.descriptor_kind.value,
                            semantic_type_name=plan.semantic_type_name,
                            datatype_family=plan.datatype_family,
                            rank=handle.array.rank,
                            ops=f"{prefix}_ops",
                            owner=f"{owner} != NULL ? {owner} : Py_None",
                            descriptor_ownership="borrowed",
                            extraction_action=handle.extraction_action.value,
                        )
                    )
                ),
                CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_helper)")),
                CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_ops)")),
                CIf(CodeExpression(f"{cache} == NULL"), body=(CReturn(CodeExpression("NULL")),)),
                CExpressionStatement(CodeExpression(f"Py_INCREF({cache})")),
                CReturn(CodeExpression(cache)),
            )
        )
        return (
            CFunction(
                self._module_getter_name(plan),
                "PyObject *",
                storage="static",
                body=tuple(nodes),
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
            node for argument in self._binding_conversion_order(plan) for node in self.visit(argument, context=context)
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
                *self._direct_result_declaration(plan, context),
                *self._native_output_declarations(plan, context),
                self._parse_statement(plan, context),
                *(node for node in argument_nodes if not isinstance(node, CDeclaration)),
                *self._native_call_setup_nodes(plan, context),
                *output_nodes,
            ),
        )

    def _binding_conversion_order(self, plan: FunctionPlan) -> tuple[ArgumentTransferPlan, ...]:
        """Convert non-owning inputs before allocating the sole replacement buffer."""
        return tuple(
            sorted(
                plan.arguments,
                key=lambda argument: (
                    argument.binding.codegen_action is CodegenAction.COPY_IN_OUT,
                    argument.python_position,
                ),
            )
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
        if plan.native_array_handle is not None:
            return self._lower_argument_native_array_handle(plan, context)
        mode = plan.binding.optional_mode
        match mode:
            case OptionalMode.REQUIRED:
                return self._lower_argument_required(plan, context)
            case OptionalMode.REQUIRED_DESCRIPTOR:
                return self._lower_argument_required_descriptor(plan, context)
            case OptionalMode.NULLABLE_VALUE:
                return self._lower_argument_nullable_value(plan, context)
            case OptionalMode.DESCRIPTOR:
                return self._lower_argument_descriptor(plan, context)
        raise ValueError(f"Unsupported C argument optional mode for {plan.owner_path!r}: {mode!r}")

    def _lower_argument_required_descriptor(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CIf, ...]:
        """Require the Python argument while allowing an empty native descriptor state."""
        scalar_type = PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name)
        names = context.arguments[plan.owner_path]
        return (
            CDeclaration(names.object_name, "PyObject *"),
            CDeclaration(names.value_name, scalar_type.c_spelling),
            CDeclaration(names.nullable_name, "void *", CodeExpression("NULL")),
            *(
                (
                    CDeclaration(
                        self._descriptor_output_present_name(names),
                        "int",
                        CodeExpression("0"),
                    ),
                )
                if plan.bridge.descriptor_output_role is not None
                else ()
            ),
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

    def _lower_argument_required(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf, ...]:
        """Dispatch one required argument from its completed Python action."""
        action = plan.binding.python_action
        match action:
            case PythonBarrierAction.SCALAR_VALUE:
                return self._lower_argument_required_scalar_value(plan, context)
            case PythonBarrierAction.SCALAR_STORAGE:
                return self._lower_argument_required_scalar_storage(plan, context)
            case PythonBarrierAction.STRING_STORAGE:
                return self._lower_argument_required_string_storage(plan, context)
            case PythonBarrierAction.STRING_VALUE:
                return self._lower_argument_required_string_value(plan, context)
            case PythonBarrierAction.RAW_ADDRESS:
                return self._lower_argument_required_raw_address(plan, context)
            case PythonBarrierAction.ARRAY_STORAGE:
                return self._lower_argument_required_array_storage(plan, context)
        raise ValueError(f"Unsupported required C argument action for {plan.owner_path!r}: {action!r}")

    # Scalar argument lowering.
    def _lower_argument_required_scalar_value(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement, ...]:
        """Return declarations and conversion statements for one scalar value."""
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

    # String argument lowering.
    def _lower_argument_required_string_value(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf, ...]:
        """Dispatch one completed string input-storage action."""
        action = plan.binding.codegen_action
        if action is CodegenAction.CALL_LOCAL_INPUT:
            return self._lower_argument_required_string_input(plan, context)
        if action is CodegenAction.COPY_IN_OUT:
            return self._lower_argument_required_string_replacement(plan, context)
        raise ValueError(f"Unsupported required C string action for {plan.owner_path!r}: {action!r}")

    def _lower_argument_required_string_input(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement, ...]:
        """Validate and borrow one read-only UTF-8 payload for the call."""
        names = context.arguments[plan.owner_path]
        return (
            CDeclaration(names.object_name, "PyObject *"),
            CDeclaration(names.value_name, "const char *", CodeExpression("NULL")),
            CDeclaration(names.length_name, "Py_ssize_t", CodeExpression("0")),
            *self._required_string_validation_nodes(plan, names, names.value_name),
        )

    def _lower_argument_required_string_replacement(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf, ...]:
        """Allocate and populate one mutable string call buffer."""
        names = context.arguments[plan.owner_path]
        source_name = f"{names.value_name}_source"
        return (
            CDeclaration(names.object_name, "PyObject *"),
            CDeclaration(source_name, "const char *", CodeExpression("NULL")),
            CDeclaration(names.value_name, "char *", CodeExpression("NULL")),
            CDeclaration(names.length_name, "Py_ssize_t", CodeExpression("0")),
            *self._required_string_validation_nodes(plan, names, source_name),
            *self._string_replacement_allocation_nodes(plan, names, source_name),
        )

    def _string_replacement_allocation_nodes(
        self,
        plan: ArgumentTransferPlan,
        names: _CArgumentNames,
        source_name: str,
    ) -> tuple[CExpressionStatement | CIf, ...]:
        """Allocate and copy one validated mutable string payload."""
        return (
            CExpressionStatement(
                CodeExpression(f"{names.value_name} = (char *)x2py_malloc((size_t){names.length_name} + 1)")
            ),
            CIf(
                CodeExpression(f"{names.value_name} == NULL"),
                body=(
                    CExpressionStatement(
                        CodeExpression(
                            f'PyErr_SetString(PyExc_MemoryError, "Unable to allocate mutable string buffer '
                            f'for argument {plan.binding.python_name}.")'
                        )
                    ),
                    CReturn(CodeExpression("NULL")),
                ),
            ),
            CExpressionStatement(
                CodeExpression(f"memcpy({names.value_name}, {source_name}, (size_t){names.length_name})")
            ),
            CExpressionStatement(CodeExpression(f"{names.value_name}[{names.length_name}] = '\\0'")),
        )

    def _required_string_validation_nodes(
        self,
        plan: ArgumentTransferPlan,
        names: _CArgumentNames,
        payload_name: str,
    ) -> tuple[CExpressionStatement, ...]:
        """Return shared required-string type, UTF-8, NUL, and length checks."""
        nodes = [
            CExpressionStatement(
                CodeExpression(
                    f"if (!PyUnicode_Check({names.object_name})) {{ "
                    f'PyErr_Format(PyExc_TypeError, "Expected an argument of type str for argument '
                    f"{plan.binding.python_name}. Received <class '%s'>\", "
                    f"Py_TYPE({names.object_name})->tp_name); return NULL; }}"
                )
            ),
            CExpressionStatement(
                CodeExpression(f"{payload_name} = PyUnicode_AsUTF8AndSize({names.object_name}, &{names.length_name})")
            ),
            CExpressionStatement(CodeExpression(f"if ({payload_name} == NULL) return NULL")),
            CExpressionStatement(
                CodeExpression(
                    f"if ((Py_ssize_t)strlen({payload_name}) != {names.length_name}) {{ "
                    f'PyErr_SetString(PyExc_TypeError, "Argument {plan.binding.python_name} cannot contain '
                    'embedded NUL"); return NULL; }'
                )
            ),
        ]
        fixed_length = plan.character_length
        if fixed_length is not None:
            nodes.append(
                CExpressionStatement(
                    CodeExpression(
                        f"if ({names.length_name} != {fixed_length}) {{ "
                        f'PyErr_SetString(PyExc_TypeError, "Argument {plan.binding.python_name} must encode to '
                        f'exactly {fixed_length} bytes"); return NULL; }}'
                    )
                )
            )
        return tuple(nodes)

    # Ordinary-array argument lowering.
    def _lower_argument_required_array_storage(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement, ...]:
        """Validate and borrow one completed ordinary NumPy array buffer."""
        if plan.native_array_actual is not None:
            return self._lower_argument_required_array_actual(plan, context)
        array_plan = plan.array
        if array_plan is None:
            raise ValueError(f"Array argument {plan.owner_path!r} is missing its handoff")
        names = context.arguments[plan.owner_path]
        array = f"(PyArrayObject *){names.object_name}"
        nodes = [
            *self._ordinary_array_argument_declarations(plan, names),
            self._array_type_and_rank_check(plan, names, array),
            *self._array_access_checks(plan, array),
            *self._array_layout_checks(plan, array),
            *self._array_shape_checks(plan, context, array),
        ]
        nodes.extend(self._array_extraction_nodes(plan, names, array))
        return tuple(nodes)

    def _ordinary_array_argument_declarations(
        self,
        plan: ArgumentTransferPlan,
        names: _CArgumentNames,
    ) -> tuple[CDeclaration, ...]:
        """Declare backend-local storage named by one ordinary-array handoff."""
        array = plan.array
        if array is None:
            raise ValueError(f"Array argument {plan.owner_path!r} is missing its handoff")
        declarations = [
            CDeclaration(names.object_name, "PyObject *"),
            CDeclaration(names.value_name, "void *", CodeExpression("NULL")),
        ]
        if plan.transformations:
            declarations.append(
                CDeclaration(
                    self._array_transformation_temp_name(names),
                    "PyObject *",
                    CodeExpression("NULL"),
                )
            )
        declarations.extend(CDeclaration(name, "int64_t", CodeExpression("0")) for name in names.extent_names)
        if array.upper_bound_roles:
            declarations.extend(CDeclaration(name, "int64_t", CodeExpression("0")) for name in names.upper_bound_names)
        if array.stride_roles:
            declarations.extend(CDeclaration(name, "int64_t", CodeExpression("1")) for name in names.stride_names)
        if array.runtime_rank_role is not None:
            declarations.append(CDeclaration(names.runtime_rank_name, "int64_t", CodeExpression("0")))
        if array.itemsize_role is not None:
            declarations.append(CDeclaration(names.itemsize_name, "int64_t", CodeExpression("0")))
        return tuple(declarations)

    # Native-handle actuals reuse the ordinary array-buffer ABI.
    def _lower_argument_required_array_actual(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement, ...]:
        """Pack an ndarray or native handle through the shared runtime helper."""
        actual = plan.native_array_actual
        array = plan.array
        if actual is None or array is None:
            raise ValueError(f"Array actual {plan.owner_path!r} is missing its completed policy")
        names = context.arguments[plan.owner_path]
        prefix = names.value_name
        nodes: list[CDeclaration | CExpressionStatement] = [
            CDeclaration(names.object_name, "PyObject *"),
            CDeclaration(names.value_name, "void *", CodeExpression("NULL")),
            *(CDeclaration(name, "int64_t", CodeExpression("0")) for name in names.extent_names),
            CDeclaration(f"{prefix}_runtime", "PyObject *", CodeExpression("NULL")),
            CDeclaration(f"{prefix}_helper", "PyObject *", CodeExpression("NULL")),
            CDeclaration(f"{prefix}_shape", "PyObject *", CodeExpression("NULL")),
            CDeclaration(f"{prefix}_layout", "PyObject *", CodeExpression("NULL")),
            CDeclaration(f"{prefix}_packed", "PyObject *", CodeExpression("NULL")),
        ]
        nodes.extend(self._native_array_actual_call_nodes(plan, context, names))
        nodes.extend(self._native_array_actual_unpack_nodes(plan, names))
        return tuple(nodes)

    def _native_array_actual_call_nodes(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
        names: _CArgumentNames,
    ) -> tuple[CExpressionStatement, ...]:
        """Call the completed normal-array runtime packer."""
        actual = plan.native_array_actual
        if actual is None:
            return ()
        prefix = names.value_name
        nodes = [
            CExpressionStatement(CodeExpression(f'{prefix}_runtime = PyImport_ImportModule("x2py.runtime.handles")')),
            CExpressionStatement(CodeExpression(f"if ({prefix}_runtime == NULL) return NULL")),
            CExpressionStatement(
                CodeExpression(
                    f"{prefix}_helper = PyObject_GetAttrString({prefix}_runtime, "
                    '"_native_array_actual_argument_for_binding_positional")'
                )
            ),
            CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_runtime)")),
            CExpressionStatement(CodeExpression(f"if ({prefix}_helper == NULL) return NULL")),
            CExpressionStatement(CodeExpression(f"{prefix}_shape = PyTuple_New({actual.rank})")),
            CExpressionStatement(
                CodeExpression(f"if ({prefix}_shape == NULL) {{ Py_DECREF({prefix}_helper); return NULL; }}")
            ),
            *self._native_array_actual_shape_nodes(plan, context, names),
            *self._native_array_actual_layout_nodes(plan, names),
            CExpressionStatement(
                CodeExpression(
                    f'{prefix}_packed = PyObject_CallFunction({prefix}_helper, "OsiOOiiiiiii", '
                    f'{names.object_name}, "{actual.dtype}", {actual.rank}, {prefix}_shape, {prefix}_layout, '
                    f"{int(actual.writable)}, {int(actual.require_native_byte_order)}, {int(actual.require_aligned)}, "
                    f"0, 0, 0, {int(actual.require_contiguous)})"
                )
            ),
            CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_helper)")),
            CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_shape)")),
            CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_layout)")),
            CExpressionStatement(CodeExpression(f"if ({prefix}_packed == NULL) return NULL")),
        ]
        return tuple(nodes)

    def _native_array_actual_shape_nodes(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
        names: _CArgumentNames,
    ) -> tuple[CExpressionStatement, ...]:
        """Build the planned expected-shape tuple for runtime validation."""
        actual = plan.native_array_actual
        array = plan.array
        if actual is None or array is None:
            return ()
        prefix = names.value_name
        nodes = []
        for axis, expression in enumerate(actual.shape):
            if expression in {":", "::Strided", "Flat"}:
                nodes.append(CExpressionStatement(CodeExpression("Py_INCREF(Py_None)")))
                item = "Py_None"
            else:
                expected = self._array_extent_expression(array, axis, expression, context)
                item = f"PyLong_FromLongLong((long long)({expected}))"
            nodes.append(CExpressionStatement(CodeExpression(f"PyTuple_SET_ITEM({prefix}_shape, {axis}, {item})")))
            nodes.append(
                CExpressionStatement(
                    CodeExpression(
                        f"if (PyTuple_GET_ITEM({prefix}_shape, {axis}) == NULL) {{ "
                        f"Py_DECREF({prefix}_helper); Py_DECREF({prefix}_shape); return NULL; }}"
                    )
                )
            )
        return tuple(nodes)

    def _native_array_actual_layout_nodes(
        self,
        plan: ArgumentTransferPlan,
        names: _CArgumentNames,
    ) -> tuple[CExpressionStatement, ...]:
        """Materialize the planned runtime layout marker."""
        actual = plan.native_array_actual
        if actual is None:
            return ()
        prefix = names.value_name
        if actual.order is None:
            return (
                CExpressionStatement(CodeExpression(f"{prefix}_layout = Py_None")),
                CExpressionStatement(CodeExpression("Py_INCREF(Py_None)")),
            )
        return (
            CExpressionStatement(CodeExpression(f'{prefix}_layout = PyUnicode_FromString("{actual.order}")')),
            CExpressionStatement(
                CodeExpression(
                    f"if ({prefix}_layout == NULL) {{ Py_DECREF({prefix}_helper); "
                    f"Py_DECREF({prefix}_shape); return NULL; }}"
                )
            ),
        )

    def _native_array_actual_unpack_nodes(
        self,
        plan: ArgumentTransferPlan,
        names: _CArgumentNames,
    ) -> tuple[CExpressionStatement, ...]:
        """Unpack exactly the existing Phase 6 pointer/extent fields."""
        prefix = names.value_name
        nodes = [
            CExpressionStatement(
                CodeExpression(f"{names.value_name} = PyLong_AsVoidPtr(PyTuple_GetItem({prefix}_packed, 0))")
            ),
            CExpressionStatement(
                CodeExpression(
                    f"if ({names.value_name} == NULL && PyErr_Occurred()) {{ Py_DECREF({prefix}_packed); "
                    "return NULL; }"
                )
            ),
        ]
        for axis, extent_name in enumerate(names.extent_names):
            nodes.extend(
                (
                    CExpressionStatement(
                        CodeExpression(
                            f"{extent_name} = (int64_t)PyLong_AsLongLong(PyTuple_GetItem({prefix}_packed, {axis + 1}))"
                        )
                    ),
                    CExpressionStatement(
                        CodeExpression(f"if (PyErr_Occurred()) {{ Py_DECREF({prefix}_packed); return NULL; }}")
                    ),
                )
            )
        nodes.append(CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_packed)")))
        return tuple(nodes)

    def _array_type_and_rank_check(
        self,
        plan: ArgumentTransferPlan,
        names: _CArgumentNames,
        array: str,
    ) -> CExpressionStatement:
        """Require the exact NumPy element type and completed rank shape."""
        handoff = plan.array
        if handoff is None:
            raise ValueError(f"Array argument {plan.owner_path!r} is missing its handoff")
        if plan.datatype_family is DatatypeFamily.STRING:
            numpy_type = "NPY_STRING"
            python_type = f"numpy.bytes_[{handoff.itemsize}]"
        else:
            scalar_type = PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name)
            if scalar_type.numpy_type_macro is None:
                raise ValueError(f"Unsupported array element type {plan.semantic_type_name!r}")
            numpy_type = scalar_type.numpy_type_macro
            python_type = scalar_type.python_type_name
        rank_check = (
            f"PyArray_NDIM({array}) < 1 || PyArray_NDIM({array}) > 15"
            if handoff.rank is None
            else f"PyArray_NDIM({array}) != {handoff.rank}"
        )
        return CExpressionStatement(
            CodeExpression(
                f"if (!PyArray_Check({names.object_name}) || PyArray_TYPE({array}) != {numpy_type} || "
                f'{rank_check}) {{ PyErr_Format(PyExc_TypeError, "Expected a compatible numpy.ndarray of '
                f"type {python_type} for argument {plan.binding.python_name}. Received <class '%s'>\", "
                f"Py_TYPE({names.object_name})->tp_name); return NULL; }}"
            )
        )

    def _array_access_checks(
        self,
        plan: ArgumentTransferPlan,
        array: str,
    ) -> tuple[CExpressionStatement, ...]:
        """Require native byte order, alignment, and planned writeability."""
        checks = [
            CExpressionStatement(
                CodeExpression(
                    f"if (!PyArray_ISNOTSWAPPED({array})) {{ PyErr_SetString(PyExc_TypeError, "
                    f'"Argument {plan.binding.python_name} must use native byte order"); return NULL; }}'
                )
            ),
            CExpressionStatement(
                CodeExpression(
                    f"if (!PyArray_ISALIGNED({array})) {{ PyErr_SetString(PyExc_TypeError, "
                    f'"Argument {plan.binding.python_name} must be aligned"); return NULL; }}'
                )
            ),
        ]
        if plan.binding.writable:
            checks.append(
                CExpressionStatement(
                    CodeExpression(
                        f"if (!PyArray_ISWRITEABLE({array})) {{ PyErr_SetString(PyExc_TypeError, "
                        f'"Argument {plan.binding.python_name} must be writeable"); return NULL; }}'
                    )
                )
            )
        return tuple(checks)

    def _array_layout_checks(
        self,
        plan: ArgumentTransferPlan,
        array: str,
    ) -> tuple[CExpressionStatement, ...]:
        """Dispatch dense or positive-strided layout validation."""
        handoff = plan.array
        if handoff is None:
            return ()
        if handoff.contiguous is False:
            return self._positive_strided_array_checks(plan, array)
        if handoff.order == "ORDER_C":
            condition = f"!PyArray_IS_C_CONTIGUOUS({array})"
            expected_order = "C"
        elif handoff.order == "ORDER_F" or (handoff.rank is not None and handoff.rank > 1):
            condition = f"!PyArray_IS_F_CONTIGUOUS({array})"
            expected_order = "F"
        else:
            condition = f"!(PyArray_IS_C_CONTIGUOUS({array}) || PyArray_IS_F_CONTIGUOUS({array}))"
            expected_order = "C or F"
        return (
            CExpressionStatement(
                CodeExpression(
                    f"if ({condition}) {{ PyErr_SetString(PyExc_TypeError, "
                    f'"Argument {plan.binding.python_name} has incompatible layout; expected ordering '
                    f'({expected_order})"); return NULL; }}'
                )
            ),
        )

    def _positive_strided_array_checks(
        self,
        plan: ArgumentTransferPlan,
        array: str,
    ) -> tuple[CExpressionStatement, ...]:
        """Require positive non-overlapping Fortran-oriented element strides."""
        handoff = plan.array
        if handoff is None or handoff.rank is None:
            raise ValueError(f"Strided array {plan.owner_path!r} requires a concrete rank")
        checks = []
        for axis in range(handoff.rank):
            stride = f"PyArray_STRIDE({array}, {axis})"
            checks.append(
                CExpressionStatement(
                    CodeExpression(
                        f"if (({stride} % PyArray_ITEMSIZE({array})) != 0 || "
                        f"(PyArray_SIZE({array}) > 0 && PyArray_DIM({array}, {axis}) > 1 && {stride} <= 0)) {{ "
                        f'PyErr_SetString(PyExc_TypeError, "Argument {plan.binding.python_name} has incompatible '
                        f'layout; expected ordering (F)"); return NULL; }}'
                    )
                )
            )
            if axis:
                previous_stride = f"PyArray_STRIDE({array}, {axis - 1})"
                previous_extent = f"PyArray_DIM({array}, {axis - 1})"
                checks.append(
                    CExpressionStatement(
                        CodeExpression(
                            f"if (PyArray_SIZE({array}) > 0 && {previous_extent} > 0 && "
                            f"{stride} < {previous_stride} * {previous_extent}) {{ "
                            f'PyErr_SetString(PyExc_TypeError, "Argument {plan.binding.python_name} has incompatible '
                            f'layout; expected ordering (F)"); return NULL; }}'
                        )
                    )
                )
        return tuple(checks)

    def _array_shape_checks(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
        array: str,
    ) -> tuple[CExpressionStatement, ...]:
        """Validate every concrete declared extent against completed scalar roles."""
        handoff = plan.array
        if handoff is None or handoff.rank is None:
            return ()
        checks = []
        runtime_markers = {":", "::Strided", "Flat"}
        for axis, expression in enumerate(handoff.shape):
            if expression in runtime_markers:
                continue
            expected = self._array_extent_expression(handoff, axis, expression, context)
            checks.append(
                CExpressionStatement(
                    CodeExpression(
                        f"if (PyArray_DIM({array}, {axis}) != (npy_intp)({expected})) {{ "
                        f'PyErr_SetString(PyExc_TypeError, "Argument {plan.binding.python_name} has incompatible '
                        f'shape at axis {axis}"); return NULL; }}'
                    )
                )
            )
        return tuple(checks)

    def _array_extent_expression(
        self,
        handoff,
        axis: int,
        expression: str,
        context: _CFunctionContext,
    ) -> str:
        """Lower one validated extent expression through its planned role references."""
        lowered = expression
        for role in handoff.extent_reference_roles[axis]:
            try:
                value_name = context.role_values[role]
            except KeyError:
                raise ValueError(f"Array extent role {role!r} has no binding value") from None
            reference_name = role.rsplit(".", 1)[-1].split(":", 1)[0]
            lowered = re.sub(rf"\b{re.escape(reference_name)}\b", value_name, lowered)
        return lowered

    def _array_extraction_nodes(
        self,
        plan: ArgumentTransferPlan,
        names: _CArgumentNames,
        array: str,
    ) -> tuple[CExpressionStatement, ...]:
        """Extract only the ABI fields named by the editable handoff plan."""
        handoff = plan.array
        if handoff is None:
            return ()
        nodes = [CExpressionStatement(CodeExpression(f"{names.value_name} = PyArray_DATA({array})"))]
        if handoff.runtime_rank_role is not None:
            nodes.append(
                CExpressionStatement(CodeExpression(f"{names.runtime_rank_name} = (int64_t)PyArray_NDIM({array})"))
            )
        if handoff.itemsize_role is not None:
            nodes.extend(
                (
                    CExpressionStatement(CodeExpression(f"{names.itemsize_name} = (int64_t)PyArray_ITEMSIZE({array})")),
                    CExpressionStatement(
                        CodeExpression(
                            f"if ({names.itemsize_name} != {handoff.itemsize}) {{ PyErr_SetString(PyExc_TypeError, "
                            f'"Argument {plan.binding.python_name} must have NumPy bytes dtype itemsize '
                            f'{handoff.itemsize}"); return NULL; }}'
                        )
                    ),
                )
            )
        active_rank = 15 if handoff.rank is None else handoff.rank
        for axis in range(active_rank):
            guard = f"if (PyArray_NDIM({array}) > {axis}) " if handoff.rank is None else ""
            nodes.append(
                CExpressionStatement(
                    CodeExpression(f"{guard}{names.extent_names[axis]} = (int64_t)PyArray_DIM({array}, {axis})")
                )
            )
        if handoff.contiguous is False:
            nodes.extend(self._strided_array_extraction_nodes(handoff.rank, names, array))
        return tuple(nodes)

    def _strided_array_extraction_nodes(
        self,
        rank: int | None,
        names: _CArgumentNames,
        array: str,
    ) -> tuple[CExpressionStatement, ...]:
        """Compute bridge base extents, slice bounds, and relative strides."""
        if rank is None:
            raise ValueError("Assumed-rank strided arrays require a separate completed lane")
        nodes = []
        base_product = "1"
        for axis in range(rank):
            absolute_stride = f"(PyArray_STRIDE({array}, {axis}) / PyArray_ITEMSIZE({array}))"
            nodes.append(
                CExpressionStatement(
                    CodeExpression(
                        f"{names.stride_names[axis]} = PyArray_SIZE({array}) == 0 ? 1 : "
                        f"{absolute_stride} / ({base_product})"
                    )
                )
            )
            nodes.append(
                CExpressionStatement(
                    CodeExpression(
                        f"{names.upper_bound_names[axis]} = {names.extent_names[axis]} == 0 ? -1 : "
                        f"({names.extent_names[axis]} - 1) * {names.stride_names[axis]}"
                    )
                )
            )
            if axis + 1 < rank:
                next_stride = f"(PyArray_STRIDE({array}, {axis + 1}) / PyArray_ITEMSIZE({array}))"
                nodes.append(
                    CExpressionStatement(
                        CodeExpression(
                            f"{names.extent_names[axis]} = {next_stride} / ({base_product}); "
                            f"if ({names.extent_names[axis]} < 1) {names.extent_names[axis]} = 1"
                        )
                    )
                )
                base_product = f"({base_product}) * {names.extent_names[axis]}"
            else:
                nodes.append(
                    CExpressionStatement(
                        CodeExpression(f"{names.extent_names[axis]} = {names.upper_bound_names[axis]} + 1")
                    )
                )
        return tuple(nodes)

    # Scalar storage and address lowering.
    def _lower_argument_required_scalar_storage(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement, ...]:
        """Validate and borrow one rank-zero NumPy scalar data address."""
        scalar_type = PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name)
        if scalar_type.numpy_type_macro is None:
            raise ValueError(f"Unsupported scalar storage type {plan.semantic_type_name!r}")
        names = context.arguments[plan.owner_path]
        array = f"(PyArrayObject *){names.object_name}"
        expected = scalar_type.python_type_name
        nodes = [
            CDeclaration(names.object_name, "PyObject *"),
            CDeclaration(names.value_name, "void *", CodeExpression("NULL")),
            CExpressionStatement(
                CodeExpression(
                    f"if (!PyArray_Check({names.object_name}) || PyArray_TYPE({array}) != "
                    f"{scalar_type.numpy_type_macro} || PyArray_NDIM({array}) != 0) {{ "
                    f'PyErr_Format(PyExc_TypeError, "Expected a rank-zero numpy.ndarray of type '
                    f"{expected} for argument {plan.binding.python_name}. Received <class '%s'>\", "
                    f"Py_TYPE({names.object_name})->tp_name); return NULL; }}"
                )
            ),
            CExpressionStatement(
                CodeExpression(
                    f"if (!PyArray_ISNOTSWAPPED({array})) {{ "
                    f'PyErr_SetString(PyExc_TypeError, "Argument {plan.binding.python_name} must use native '
                    'byte order"); return NULL; }'
                )
            ),
            CExpressionStatement(
                CodeExpression(
                    f"if (!PyArray_ISALIGNED({array})) {{ "
                    f'PyErr_SetString(PyExc_TypeError, "Argument {plan.binding.python_name} must be aligned"); '
                    "return NULL; }"
                )
            ),
        ]
        if plan.binding.writable:
            nodes.append(
                CExpressionStatement(
                    CodeExpression(
                        f"if (!PyArray_ISWRITEABLE({array})) {{ "
                        f'PyErr_SetString(PyExc_TypeError, "Argument {plan.binding.python_name} must be writeable"); '
                        "return NULL; }"
                    )
                )
            )
        nodes.append(CExpressionStatement(CodeExpression(f"{names.value_name} = PyArray_DATA({array})")))
        return tuple(nodes)

    # String storage lowering.
    def _lower_argument_required_string_storage(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement, ...]:
        """Validate and borrow one rank-zero fixed-width NumPy bytes buffer."""
        if plan.character_length is None or plan.character_length <= 0:
            raise ValueError(f"String storage {plan.owner_path!r} is missing a fixed length")
        names = context.arguments[plan.owner_path]
        array = f"(PyArrayObject *){names.object_name}"
        length = plan.character_length
        return (
            CDeclaration(names.object_name, "PyObject *"),
            CDeclaration(names.value_name, "void *", CodeExpression("NULL")),
            CExpressionStatement(
                CodeExpression(
                    f"if (!PyArray_Check({names.object_name}) || PyArray_TYPE({array}) != NPY_STRING || "
                    f"PyArray_NDIM({array}) != 0) {{ "
                    f'PyErr_Format(PyExc_TypeError, "Expected a rank-zero numpy.ndarray with dtype S{length} '
                    f"for argument {plan.binding.python_name}. Received <class '%s'>\", "
                    f"Py_TYPE({names.object_name})->tp_name); return NULL; }}"
                )
            ),
            CExpressionStatement(
                CodeExpression(
                    f"if (PyArray_ITEMSIZE({array}) != {length}) {{ "
                    f'PyErr_SetString(PyExc_TypeError, "Argument {plan.binding.python_name} must use itemsize '
                    f'{length}"); return NULL; }}'
                )
            ),
            CExpressionStatement(
                CodeExpression(
                    f"if (!PyArray_ISNOTSWAPPED({array})) {{ "
                    f'PyErr_SetString(PyExc_TypeError, "Argument {plan.binding.python_name} must use native '
                    'byte order"); return NULL; }'
                )
            ),
            CExpressionStatement(
                CodeExpression(
                    f"if (!PyArray_ISALIGNED({array})) {{ "
                    f'PyErr_SetString(PyExc_TypeError, "Argument {plan.binding.python_name} must be aligned"); '
                    "return NULL; }"
                )
            ),
            CExpressionStatement(
                CodeExpression(
                    f"if (!PyArray_ISWRITEABLE({array})) {{ "
                    f'PyErr_SetString(PyExc_TypeError, "Argument {plan.binding.python_name} must be writeable"); '
                    "return NULL; }"
                )
            ),
            CExpressionStatement(CodeExpression(f"{names.value_name} = PyArray_DATA({array})")),
        )

    def _lower_argument_required_raw_address(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement, ...]:
        """Convert one Python integer into a caller-owned raw address."""
        names = context.arguments[plan.owner_path]
        return (
            CDeclaration(names.object_name, "PyObject *"),
            CDeclaration(names.value_name, "void *", CodeExpression("NULL")),
            CExpressionStatement(
                CodeExpression(
                    f"if (!PyLong_Check({names.object_name})) {{ "
                    f'PyErr_Format(PyExc_TypeError, "Expected an integer raw address for argument '
                    f"{plan.binding.python_name}. Received <class '%s'>\", "
                    f"Py_TYPE({names.object_name})->tp_name); return NULL; }}"
                )
            ),
            CExpressionStatement(CodeExpression(f"{names.value_name} = PyLong_AsVoidPtr({names.object_name})")),
            CExpressionStatement(CodeExpression(f"if ({names.value_name} == NULL && PyErr_Occurred()) return NULL")),
        )

    # Native-array-handle argument lowering.
    def _lower_argument_native_array_handle(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf, ...]:
        """Dispatch one descriptor handle from its planned standard ABI."""
        handle = plan.native_array_handle
        if handle is None:
            return ()
        if handle.handoff.abi is NativeDescriptorHandoffABI.FACT_PACKED_CALL_LOCAL:
            return self._lower_argument_native_array_facts(plan, context)
        if handle.handoff.abi is NativeDescriptorHandoffABI.DIRECT_STANDARD_DESCRIPTOR:
            return self._lower_argument_native_array_direct(plan, context)
        raise ValueError(f"Unsupported C native descriptor ABI for {plan.owner_path!r}: {handle.handoff.abi!r}")

    def _lower_argument_native_array_facts(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf, ...]:
        """Establish call-local CFI storage from validated descriptor facts."""
        handle = plan.native_array_handle
        if handle is None or handle.array.rank is None:
            raise ValueError(f"Native descriptor {plan.owner_path!r} has no concrete rank")
        names = context.arguments[plan.owner_path]
        rank = handle.array.rank
        prefix = names.value_name
        nodes: list[CDeclaration | CExpressionStatement | CIf] = [
            self._native_descriptor_object_declaration(plan, names),
            CDeclaration(f"{prefix}_storage", f"CFI_CDESC_T({rank})"),
            CDeclaration(names.value_name, "CFI_cdesc_t *", CodeExpression("NULL")),
            CDeclaration(f"{prefix}_base_addr", "void *", CodeExpression("NULL")),
            CDeclaration(f"{prefix}_elem_len", "size_t", CodeExpression("0")),
            CDeclaration(f"{prefix}_descriptor_rank", "CFI_rank_t", CodeExpression("0")),
            CDeclaration(f"{prefix}_cfi_extents[{rank}]", "CFI_index_t"),
            *(
                CDeclaration(f"{prefix}_{label}_{axis}", "CFI_index_t", CodeExpression("0"))
                for axis in range(rank)
                for label in ("lower_bound", "descriptor_extent", "stride_multiplier")
            ),
            CDeclaration(f"{prefix}_establish_status", "int", CodeExpression("CFI_SUCCESS")),
            *self._native_descriptor_helper_declarations(prefix),
            *(self._native_descriptor_presence_declarations(plan, names)),
        ]
        nodes.extend(
            self._native_descriptor_helper_call_nodes(
                plan,
                context,
                names,
                "_native_array_descriptor_argument_for_binding_positional",
            )
        )
        nodes.extend(self._native_descriptor_presence_unpack_nodes(plan, names, 3 + 3 * rank))
        nodes.extend(self._native_descriptor_fact_unpack_nodes(plan, names))
        nodes.append(CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_packed)")))
        return tuple(nodes)

    def _lower_argument_native_array_direct(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf, ...]:
        """Borrow one persistent runtime-owned standard descriptor pointer."""
        names = context.arguments[plan.owner_path]
        prefix = names.value_name
        nodes: list[CDeclaration | CExpressionStatement | CIf] = [
            self._native_descriptor_object_declaration(plan, names),
            CDeclaration(names.value_name, "CFI_cdesc_t *", CodeExpression("NULL")),
            *self._native_descriptor_helper_declarations(prefix),
            *(self._native_descriptor_presence_declarations(plan, names)),
        ]
        nodes.extend(
            self._native_descriptor_helper_call_nodes(
                plan,
                context,
                names,
                "_native_array_descriptor_handoff_for_binding_positional",
            )
        )
        nodes.extend(self._native_descriptor_presence_unpack_nodes(plan, names, 1))
        nodes.extend(self._native_descriptor_pointer_unpack_nodes(plan, names))
        nodes.append(CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_packed)")))
        return tuple(nodes)

    def _native_descriptor_object_declaration(
        self,
        plan: ArgumentTransferPlan,
        names: _CArgumentNames,
    ) -> CDeclaration:
        """Declare a required object or the optional-absence default."""
        initializer = CodeExpression("Py_None") if plan.binding.optional_mode is OptionalMode.DESCRIPTOR else None
        return CDeclaration(names.object_name, "PyObject *", initializer)

    def _native_descriptor_helper_declarations(self, prefix: str) -> tuple[CDeclaration, ...]:
        """Return binding-local Python objects used by one runtime helper call."""
        return tuple(
            CDeclaration(f"{prefix}_{suffix}", "PyObject *", CodeExpression("NULL"))
            for suffix in ("runtime", "helper", "shape", "packed", "item")
        )

    def _native_descriptor_presence_declarations(
        self,
        plan: ArgumentTransferPlan,
        names: _CArgumentNames,
    ) -> tuple[CDeclaration, ...]:
        """Declare a dedicated optional-presence token only when planned."""
        if plan.binding.optional_mode is not OptionalMode.DESCRIPTOR:
            return ()
        return (CDeclaration(names.present_name, "void *", CodeExpression("NULL")),)

    def _native_descriptor_helper_call_nodes(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
        names: _CArgumentNames,
        helper_name: str,
    ) -> tuple[CExpressionStatement, ...]:
        """Call one planned native-descriptor runtime packer."""
        handle = plan.native_array_handle
        if handle is None or handle.array.rank is None:
            return ()
        prefix = names.value_name
        dtype = self._native_array_dtype(plan)
        dtype_format = "O" if dtype is None else "s"
        dtype_argument = "Py_None" if dtype is None else f'"{dtype}"'
        nodes = [
            CExpressionStatement(CodeExpression(f'{prefix}_runtime = PyImport_ImportModule("x2py.runtime.handles")')),
            CExpressionStatement(CodeExpression(f"if ({prefix}_runtime == NULL) return NULL")),
            CExpressionStatement(
                CodeExpression(f'{prefix}_helper = PyObject_GetAttrString({prefix}_runtime, "{helper_name}")')
            ),
            CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_runtime)")),
            CExpressionStatement(CodeExpression(f"if ({prefix}_helper == NULL) return NULL")),
            CExpressionStatement(CodeExpression(f"{prefix}_shape = PyTuple_New({handle.array.rank})")),
            CExpressionStatement(
                CodeExpression(f"if ({prefix}_shape == NULL) {{ Py_DECREF({prefix}_helper); return NULL; }}")
            ),
            *self._native_descriptor_expected_shape_nodes(plan, context, names),
            CExpressionStatement(
                CodeExpression(
                    f'{prefix}_packed = PyObject_CallFunction({prefix}_helper, "Os{dtype_format}iOi", '
                    f'{names.object_name}, "{handle.descriptor_kind.value}", {dtype_argument}, '
                    f"{handle.array.rank}, {prefix}_shape, {int(handle.optional_absent)})"
                )
            ),
            CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_helper)")),
            CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_shape)")),
            CExpressionStatement(CodeExpression(f"if ({prefix}_packed == NULL) return NULL")),
        ]
        return tuple(nodes)

    def _native_descriptor_expected_shape_nodes(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
        names: _CArgumentNames,
    ) -> tuple[CExpressionStatement, ...]:
        """Materialize the descriptor's declared shape for runtime validation."""
        handle = plan.native_array_handle
        if handle is None:
            return ()
        prefix = names.value_name
        nodes = []
        for axis, expression in enumerate(handle.array.shape):
            if expression in {":", "::Strided", "Flat"}:
                nodes.append(CExpressionStatement(CodeExpression("Py_INCREF(Py_None)")))
                item = "Py_None"
            else:
                expected = self._array_extent_expression(handle.array, axis, expression, context)
                item = f"PyLong_FromLongLong((long long)({expected}))"
            nodes.extend(
                (
                    CExpressionStatement(CodeExpression(f"PyTuple_SET_ITEM({prefix}_shape, {axis}, {item})")),
                    CExpressionStatement(
                        CodeExpression(
                            f"if (PyTuple_GET_ITEM({prefix}_shape, {axis}) == NULL) {{ "
                            f"Py_DECREF({prefix}_helper); Py_DECREF({prefix}_shape); return NULL; }}"
                        )
                    ),
                )
            )
        return tuple(nodes)

    def _native_descriptor_presence_unpack_nodes(
        self,
        plan: ArgumentTransferPlan,
        names: _CArgumentNames,
        index: int,
    ) -> tuple[CExpressionStatement, ...]:
        """Decode the separate optional-presence token before descriptor fields."""
        if plan.binding.optional_mode is not OptionalMode.DESCRIPTOR:
            return ()
        prefix = names.value_name
        return (
            CExpressionStatement(CodeExpression(f"{prefix}_item = PyTuple_GetItem({prefix}_packed, {index})")),
            CExpressionStatement(
                CodeExpression(f"if ({prefix}_item == NULL) {{ Py_DECREF({prefix}_packed); return NULL; }}")
            ),
            CExpressionStatement(
                CodeExpression(f"if ({prefix}_item != Py_None) {names.present_name} = PyLong_AsVoidPtr({prefix}_item)")
            ),
            CExpressionStatement(
                CodeExpression(
                    f"if ({names.present_name} == NULL && PyErr_Occurred()) {{ "
                    f"Py_DECREF({prefix}_packed); return NULL; }}"
                )
            ),
        )

    def _native_descriptor_pointer_unpack_nodes(
        self,
        plan: ArgumentTransferPlan,
        names: _CArgumentNames,
    ) -> tuple[CExpressionStatement, ...]:
        """Decode one persistent standard-descriptor pointer."""
        prefix = names.value_name
        condition = "1" if plan.binding.optional_mode is OptionalMode.REQUIRED else f"{names.present_name} != NULL"
        return (
            CExpressionStatement(CodeExpression(f"{prefix}_item = PyTuple_GetItem({prefix}_packed, 0)")),
            CExpressionStatement(
                CodeExpression(f"if ({prefix}_item == NULL) {{ Py_DECREF({prefix}_packed); return NULL; }}")
            ),
            CExpressionStatement(
                CodeExpression(f"if ({condition}) {names.value_name} = (CFI_cdesc_t *)PyLong_AsVoidPtr({prefix}_item)")
            ),
            CExpressionStatement(
                CodeExpression(
                    f"if ({names.value_name} == NULL && PyErr_Occurred()) {{ "
                    f"Py_DECREF({prefix}_packed); return NULL; }}"
                )
            ),
        )

    def _native_descriptor_fact_unpack_nodes(
        self,
        plan: ArgumentTransferPlan,
        names: _CArgumentNames,
    ) -> tuple[CExpressionStatement | CIf, ...]:
        """Decode facts and establish a call-local standard descriptor."""
        handle = plan.native_array_handle
        if handle is None or handle.array.rank is None:
            return ()
        condition = CodeExpression(
            "1" if plan.binding.optional_mode is OptionalMode.REQUIRED else f"{names.present_name} != NULL"
        )
        return (CIf(condition, body=self._native_descriptor_fact_present_nodes(plan, names)),)

    def _native_descriptor_fact_present_nodes(
        self,
        plan: ArgumentTransferPlan,
        names: _CArgumentNames,
    ) -> tuple[CExpressionStatement, ...]:
        """Unpack one present fact tuple and initialize its CFI dimensions."""
        handle = plan.native_array_handle
        if handle is None or handle.array.rank is None:
            return ()
        prefix = names.value_name
        rank = handle.array.rank
        cfi_type = self._native_array_cfi_type(plan)
        if cfi_type is None:
            raise ValueError(f"Missing CFI type for {plan.owner_path!r}")
        attribute = (
            "CFI_attribute_allocatable"
            if handle.descriptor_kind is NativeArrayDescriptorKind.ALLOCATABLE
            else "CFI_attribute_pointer"
        )
        nodes = [
            *self._native_descriptor_integer_field_nodes(prefix, f"{prefix}_base_addr", 0, pointer=True),
            *self._native_descriptor_integer_field_nodes(prefix, f"{prefix}_elem_len", 1),
            *self._native_descriptor_integer_field_nodes(prefix, f"{prefix}_descriptor_rank", 2),
        ]
        for axis in range(rank):
            offset = 3 + 3 * axis
            nodes.extend(self._native_descriptor_integer_field_nodes(prefix, f"{prefix}_lower_bound_{axis}", offset))
            nodes.extend(
                self._native_descriptor_integer_field_nodes(prefix, f"{prefix}_descriptor_extent_{axis}", offset + 1)
            )
            nodes.extend(
                self._native_descriptor_integer_field_nodes(prefix, f"{prefix}_stride_multiplier_{axis}", offset + 2)
            )
        nodes.extend(
            (
                CExpressionStatement(
                    CodeExpression(
                        f"if ({prefix}_descriptor_rank != {rank}) {{ PyErr_Format(PyExc_ValueError, "
                        f'"native descriptor rank %lld does not match planned rank {rank} for argument '
                        f'{plan.binding.python_name}", (long long){prefix}_descriptor_rank); '
                        f"Py_DECREF({prefix}_packed); return NULL; }}"
                    )
                ),
                *(
                    CExpressionStatement(
                        CodeExpression(f"{prefix}_cfi_extents[{axis}] = {prefix}_descriptor_extent_{axis}")
                    )
                    for axis in range(rank)
                ),
                CExpressionStatement(
                    CodeExpression(
                        f"{prefix}_establish_status = CFI_establish((CFI_cdesc_t *)&{prefix}_storage, "
                        f"{prefix}_base_addr, {attribute}, {cfi_type}, "
                        f"{prefix}_elem_len, {rank}, {prefix}_cfi_extents)"
                    )
                ),
                CExpressionStatement(
                    CodeExpression(
                        f"if ({prefix}_establish_status != CFI_SUCCESS) {{ PyErr_Format(PyExc_RuntimeError, "
                        f'"Unable to establish native descriptor for argument {plan.binding.python_name}: %d", '
                        f"{prefix}_establish_status); Py_DECREF({prefix}_packed); return NULL; }}"
                    )
                ),
            )
        )
        for axis in range(rank):
            nodes.extend(
                (
                    CExpressionStatement(
                        CodeExpression(
                            f"((CFI_cdesc_t *)&{prefix}_storage)->dim[{axis}].lower_bound = {prefix}_lower_bound_{axis}"
                        )
                    ),
                    CExpressionStatement(
                        CodeExpression(
                            f"((CFI_cdesc_t *)&{prefix}_storage)->dim[{axis}].extent = "
                            f"{prefix}_descriptor_extent_{axis}"
                        )
                    ),
                    CExpressionStatement(
                        CodeExpression(
                            f"((CFI_cdesc_t *)&{prefix}_storage)->dim[{axis}].sm = {prefix}_stride_multiplier_{axis}"
                        )
                    ),
                )
            )
        nodes.append(CExpressionStatement(CodeExpression(f"{names.value_name} = (CFI_cdesc_t *)&{prefix}_storage")))
        return tuple(nodes)

    def _native_descriptor_integer_field_nodes(
        self,
        prefix: str,
        target: str,
        index: int,
        *,
        pointer: bool = False,
    ) -> tuple[CExpressionStatement, ...]:
        """Decode one validated tuple integer with local failure cleanup."""
        converter = "PyLong_AsVoidPtr" if pointer else "PyLong_AsLongLong"
        cast = "(void *)" if pointer else ""
        error = f"{target} == NULL && PyErr_Occurred()" if pointer else "PyErr_Occurred()"
        return (
            CExpressionStatement(CodeExpression(f"{prefix}_item = PyTuple_GetItem({prefix}_packed, {index})")),
            CExpressionStatement(
                CodeExpression(f"if ({prefix}_item == NULL) {{ Py_DECREF({prefix}_packed); return NULL; }}")
            ),
            CExpressionStatement(CodeExpression(f"{target} = {cast}{converter}({prefix}_item)")),
            CExpressionStatement(CodeExpression(f"if ({error}) {{ Py_DECREF({prefix}_packed); return NULL; }}")),
        )

    def _native_array_dtype(self, plan: ArgumentTransferPlan) -> str | None:
        """Return the NumPy dtype spelling already selected by primitive type."""
        return self._native_array_dtype_for_semantic_type(plan.semantic_type_name, plan.datatype_family)

    def _native_array_dtype_for_result(self, plan: ResultPlan) -> str | None:
        """Return the NumPy dtype spelling selected for one handle result."""
        return self._native_array_dtype_for_semantic_type(plan.semantic_type_name, plan.datatype_family)

    def _native_array_dtype_for_semantic_type(
        self,
        semantic_type_name: str,
        datatype_family: DatatypeFamily,
    ) -> str | None:
        """Translate one completed array element family to a runtime dtype."""
        if datatype_family is DatatypeFamily.STRING:
            return None
        scalar_type = PrimitiveScalarTypeRegistry.type_for(semantic_type_name)
        return {
            "NPY_BOOL": "bool",
            "NPY_INT8": "int8",
            "NPY_INT16": "int16",
            "NPY_INT32": "int32",
            "NPY_INT64": "int64",
            "NPY_FLOAT32": "float32",
            "NPY_FLOAT64": "float64",
            "NPY_COMPLEX64": "complex64",
            "NPY_COMPLEX128": "complex128",
        }[scalar_type.numpy_type_macro]

    def _native_array_cfi_type(self, plan: ArgumentTransferPlan | ResultPlan) -> str | None:
        """Return the standard-descriptor element type after array-family dispatch."""
        if plan.datatype_family is DatatypeFamily.STRING:
            return "CFI_type_char"
        return PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name).cfi_type_spelling

    def _module_native_array_cfi_type(self, plan: ModuleVariablePlan) -> str | None:
        """Return one module handle's standard-descriptor element type."""
        if plan.datatype_family is DatatypeFamily.STRING:
            return "CFI_type_char"
        return PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name).cfi_type_spelling

    def _module_native_array_elem_size(self, plan: ModuleVariablePlan) -> str:
        """Return the completed numeric size or runtime character element length."""
        if plan.datatype_family is DatatypeFamily.STRING:
            return f"{self._module_native_array_bridge_operation_name(plan, NativeArrayOperation.ELEMENT_LENGTH)}()"
        return f"sizeof({PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name).c_spelling})"

    def _native_array_handle_factory_call(
        self,
        *,
        helper: str,
        target: str,
        descriptor_kind: str,
        semantic_type_name: str,
        datatype_family: DatatypeFamily,
        rank: int,
        ops: str,
        owner: str,
        descriptor_ownership: str,
        extraction_action: str,
    ) -> str:
        """Call the runtime factory with a fixed dtype or deferred character dtype."""
        dtype = self._native_array_dtype_for_semantic_type(semantic_type_name, datatype_family)
        if dtype is None:
            return (
                f'{target} = PyObject_CallFunction({helper}, "sOiOOssO", "{descriptor_kind}", Py_None, '
                f'{rank}, {ops}, {owner}, "{descriptor_ownership}", "{extraction_action}", Py_None)'
            )
        return (
            f'{target} = PyObject_CallFunction({helper}, "ssiOOssO", "{descriptor_kind}", "{dtype}", '
            f'{rank}, {ops}, {owner}, "{descriptor_ownership}", "{extraction_action}", Py_None)'
        )

    def _lower_argument_nullable_value(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf, ...]:
        """Return omitted-or-value conversion nodes for an optional value."""
        if plan.object_kind is ObjectKind.NUMPY_ARRAY:
            return self._lower_argument_nullable_array_storage(plan, context)
        if plan.object_kind is ObjectKind.STRING:
            return self._lower_argument_nullable_string_value(plan, context)
        if plan.object_kind is not ObjectKind.SCALAR:
            raise ValueError(
                f"Unsupported optional C argument object kind for {plan.owner_path!r}: {plan.object_kind!r}"
            )
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

    # Optional ordinary-array lowering.
    def _lower_argument_nullable_array_storage(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CIf, ...]:
        """Preserve absent optional arrays or validate one present NumPy buffer."""
        names = context.arguments[plan.owner_path]
        required_nodes = self._lower_argument_required_array_storage(plan, context)
        declarations = tuple(node for node in required_nodes if isinstance(node, CDeclaration))
        body = tuple(node for node in required_nodes if not isinstance(node, CDeclaration))
        return (
            CDeclaration(names.object_name, "PyObject *", CodeExpression("Py_None")),
            *(node for node in declarations if node.name != names.object_name),
            CIf(CodeExpression(f"{names.object_name} != Py_None"), body=body),
        )

    # Optional string lowering.
    def _lower_argument_nullable_string_value(
        self,
        plan: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CIf, ...]:
        """Convert a concrete optional string or preserve its absent state."""
        names = context.arguments[plan.owner_path]
        declarations: tuple[CDeclaration, ...] = (
            CDeclaration(names.object_name, "PyObject *", CodeExpression("Py_None")),
            CDeclaration(names.length_name, "Py_ssize_t", CodeExpression("0")),
        )
        action = plan.binding.codegen_action
        if action is CodegenAction.CALL_LOCAL_INPUT:
            return (
                *declarations,
                CDeclaration(names.value_name, "const char *", CodeExpression("NULL")),
                CIf(
                    CodeExpression(f"{names.object_name} != Py_None"),
                    body=self._required_string_validation_nodes(plan, names, names.value_name),
                ),
            )
        if action is CodegenAction.COPY_IN_OUT:
            source_name = f"{names.value_name}_source"
            return (
                *declarations,
                CDeclaration(source_name, "const char *", CodeExpression("NULL")),
                CDeclaration(names.value_name, "char *", CodeExpression("NULL")),
                CIf(
                    CodeExpression(f"{names.object_name} != Py_None"),
                    body=(
                        *self._required_string_validation_nodes(plan, names, source_name),
                        *self._string_replacement_allocation_nodes(plan, names, source_name),
                    ),
                ),
            )
        raise ValueError(f"Unsupported optional C string action for {plan.owner_path!r}: {action!r}")

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
        context: _CFunctionContext,
        failure_cleanup: tuple[str, ...] = (),
    ) -> tuple[CExpressionStatement | CDeclaration | CIf, ...]:
        """Lower one result through its completed binding action."""
        return self._lower_result(plan, context, failure_cleanup)

    def _lower_result(
        self,
        plan: ResultPlan,
        context: _CFunctionContext,
        failure_cleanup: tuple[str, ...],
    ) -> tuple[CExpressionStatement | CDeclaration | CIf, ...]:
        """Dispatch one completed binding result action explicitly."""
        if plan.scalar_descriptor is not None:
            return self._lower_result_scalar_descriptor(plan, context, failure_cleanup)
        if plan.native_array_handle is not None:
            return self._lower_result_owned_native_array_handle(plan, context, failure_cleanup)
        match plan.object_kind:
            case ObjectKind.NUMPY_ARRAY:
                return self._lower_result_array_copy(plan, context, failure_cleanup)
            case ObjectKind.STRING:
                return self._lower_result_fixed_string(plan, context, failure_cleanup)
            case ObjectKind.SCALAR:
                if plan.binding.codegen_action is CodegenAction.DIRECT_VALUE:
                    return self._lower_result_direct_value(plan, context, failure_cleanup)
                raise ValueError(
                    f"Unsupported C scalar result action for {plan.owner_path!r}: {plan.binding.codegen_action!r}"
                )
            case _:
                raise ValueError(f"Unsupported C result object kind for {plan.owner_path!r}: {plan.object_kind!r}")

    # Nullable rank-zero descriptor result lowering.
    def _lower_result_scalar_descriptor(
        self,
        plan: ResultPlan,
        context: _CFunctionContext,
        failure_cleanup: tuple[str, ...],
    ) -> tuple[CDeclaration | CExpressionStatement | CIf, ...]:
        """Copy one nullable descriptor payload into a detached Python value."""
        native_name = self._result_native_name(plan, context)
        python_name = context.python_results.get(plan.owner_path)
        if python_name is None:
            raise ValueError(f"Scalar descriptor result {plan.owner_path!r} has no Python role")
        prior_cleanup = self._decref_names(failure_cleanup)
        if plan.object_kind is ObjectKind.STRING:
            conversion = CodeExpression(
                f'PyUnicode_DecodeUTF8((const char *){native_name}, (Py_ssize_t){native_name}_length, "strict")'
            )
        else:
            scalar_type = PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name)
            if scalar_type.python_result_converter is None:
                raise ValueError(f"Unsupported scalar descriptor type {plan.semantic_type_name!r}")
            conversion = CodeExpression(
                f"{scalar_type.python_result_converter}(({scalar_type.c_spelling} *){native_name})"
            )
        present_body: tuple[CDeclaration | CExpressionStatement | CIf, ...] = (
            CIf(
                CodeExpression(f"{native_name} == NULL"),
                body=(
                    *prior_cleanup,
                    CExpressionStatement(CodeExpression("PyErr_NoMemory()")),
                    CReturn(CodeExpression("NULL")),
                ),
            ),
            CExpressionStatement(CodeExpression(f"{python_name} = {conversion.text}")),
            CExpressionStatement(CodeExpression(f"free({native_name})")),
            CIf(
                CodeExpression(f"{python_name} == NULL"),
                body=(*prior_cleanup, CReturn(CodeExpression("NULL"))),
            ),
        )
        return (
            CDeclaration(python_name, "PyObject *", CodeExpression("NULL")),
            CIf(
                CodeExpression(f"!{native_name}_present"),
                body=(
                    CExpressionStatement(CodeExpression("Py_INCREF(Py_None)")),
                    CExpressionStatement(CodeExpression(f"{python_name} = Py_None")),
                ),
                else_body=present_body,
            ),
        )

    # Owned native-array-handle result lowering.
    def _lower_result_owned_native_array_handle(
        self,
        plan: ResultPlan,
        context: _CFunctionContext,
        failure_cleanup: tuple[str, ...],
    ) -> tuple[CDeclaration | CExpressionStatement | CIf, ...]:
        """Transfer persistent CFI owner storage into one runtime handle."""
        descriptor_name = self._owned_result_descriptor_name(plan, context)
        python_name = context.python_results.get(plan.owner_path)
        handle = plan.native_array_handle
        if python_name is None or handle is None or handle.array.rank is None:
            raise ValueError(f"Owned native array result {plan.owner_path!r} has no binding consumer")
        prefix = f"{descriptor_name}_handle"
        cleanup = self._owned_descriptor_failure_cleanup(descriptor_name)
        nodes: list[CDeclaration | CExpressionStatement | CIf] = [
            CDeclaration(f"{prefix}_runtime", "PyObject *", CodeExpression("NULL")),
            CDeclaration(f"{prefix}_helper", "PyObject *", CodeExpression("NULL")),
            CDeclaration(f"{prefix}_ops", "PyObject *", CodeExpression("NULL")),
            CDeclaration(f"{prefix}_owner", "PyObject *", CodeExpression("NULL")),
            CDeclaration(f"{prefix}_operation", "PyObject *", CodeExpression("NULL")),
            CDeclaration(python_name, "PyObject *", CodeExpression("NULL")),
            CExpressionStatement(CodeExpression(f"{prefix}_ops = PyDict_New()")),
            CIf(
                CodeExpression(f"{prefix}_ops == NULL"),
                body=(*cleanup, *self._decref_names(failure_cleanup), CReturn(CodeExpression("NULL"))),
            ),
        ]
        nodes.extend(self._owned_native_array_ops_dictionary_nodes(plan, prefix, cleanup, failure_cleanup))
        nodes.extend(
            (
                CExpressionStatement(CodeExpression(f"{prefix}_owner = PyLong_FromVoidPtr({descriptor_name})")),
                CIf(
                    CodeExpression(f"{prefix}_owner == NULL"),
                    body=(
                        CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_ops)")),
                        *cleanup,
                        *self._decref_names(failure_cleanup),
                        CReturn(CodeExpression("NULL")),
                    ),
                ),
                CExpressionStatement(
                    CodeExpression(f'{prefix}_runtime = PyImport_ImportModule("x2py.runtime.handles")')
                ),
                CIf(
                    CodeExpression(f"{prefix}_runtime == NULL"),
                    body=(
                        CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_owner)")),
                        CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_ops)")),
                        *cleanup,
                        *self._decref_names(failure_cleanup),
                        CReturn(CodeExpression("NULL")),
                    ),
                ),
                CExpressionStatement(
                    CodeExpression(
                        f"{prefix}_helper = PyObject_GetAttrString({prefix}_runtime, "
                        '"_native_array_handle_from_generated_ops")'
                    )
                ),
                CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_runtime)")),
                CIf(
                    CodeExpression(f"{prefix}_helper == NULL"),
                    body=(
                        CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_owner)")),
                        CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_ops)")),
                        *cleanup,
                        *self._decref_names(failure_cleanup),
                        CReturn(CodeExpression("NULL")),
                    ),
                ),
                CExpressionStatement(
                    CodeExpression(
                        self._native_array_handle_factory_call(
                            helper=f"{prefix}_helper",
                            target=python_name,
                            descriptor_kind=handle.descriptor_kind.value,
                            semantic_type_name=plan.semantic_type_name,
                            datatype_family=plan.datatype_family,
                            rank=handle.array.rank,
                            ops=f"{prefix}_ops",
                            owner=f"{prefix}_owner",
                            descriptor_ownership="owned",
                            extraction_action=handle.extraction_action.value,
                        )
                    )
                ),
                CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_helper)")),
                CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_owner)")),
                CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_ops)")),
                CIf(
                    CodeExpression(f"{python_name} == NULL"),
                    body=(*self._decref_names(failure_cleanup), CReturn(CodeExpression("NULL"))),
                ),
            )
        )
        return tuple(nodes)

    def _owned_native_array_ops_dictionary_nodes(
        self,
        result: ResultPlan,
        prefix: str,
        cleanup: tuple[CExpressionStatement | CIf, ...],
        failure_cleanup: tuple[str, ...],
    ) -> tuple[CExpressionStatement | CIf, ...]:
        """Populate a result handle's operation dictionary from planned roles."""
        handle = result.native_array_handle
        if handle is None:
            return ()
        nodes = []
        for operation in handle.operations:
            definition = self._owned_native_array_operation_def_name(None, result, operation)
            nodes.extend(
                (
                    CExpressionStatement(
                        CodeExpression(f"{prefix}_operation = PyCFunction_NewEx(&{definition}, NULL, NULL)")
                    ),
                    CIf(
                        CodeExpression(f"{prefix}_operation == NULL"),
                        body=(
                            CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_ops)")),
                            *cleanup,
                            *self._decref_names(failure_cleanup),
                            CReturn(CodeExpression("NULL")),
                        ),
                    ),
                    CIf(
                        CodeExpression(
                            f'PyDict_SetItemString({prefix}_ops, "{operation.value}", {prefix}_operation) < 0'
                        ),
                        body=(
                            CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_operation)")),
                            CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_ops)")),
                            *cleanup,
                            *self._decref_names(failure_cleanup),
                            CReturn(CodeExpression("NULL")),
                        ),
                    ),
                    CExpressionStatement(CodeExpression(f"Py_DECREF({prefix}_operation)")),
                )
            )
        return tuple(nodes)

    # Ordinary-array result lowering.
    def _lower_result_array_copy(
        self,
        plan: ResultPlan,
        context: _CFunctionContext,
        failure_cleanup: tuple[str, ...],
    ) -> tuple[CDeclaration | CExpressionStatement | CIf, ...]:
        """Transfer one bridge-owned fixed-shape buffer into a NumPy capsule owner."""
        handoff = plan.array
        native_name = self._result_native_name(plan, context)
        python_name = context.python_results.get(plan.owner_path)
        if handoff is None or handoff.rank is None or python_name is None:
            raise ValueError(f"Array result {plan.owner_path!r} has no fixed binding shape")
        dimensions = tuple(
            self._array_extent_expression(handoff, axis, expression, context)
            for axis, expression in enumerate(handoff.shape)
        )
        dims_name = f"{python_name}_dims"
        fortran_order = 0 if handoff.order == "ORDER_C" or handoff.rank == 1 else 1
        base_name = f"{python_name}_base"
        decrefs = tuple(CExpressionStatement(CodeExpression(f"Py_DECREF({name})")) for name in failure_cleanup)
        return (
            CIf(
                CodeExpression(f"{native_name} == NULL"),
                body=(
                    CExpressionStatement(
                        CodeExpression(
                            'PyErr_SetString(PyExc_MemoryError, "Unable to allocate copy-return output array.")'
                        )
                    ),
                    *decrefs,
                    CReturn(CodeExpression("NULL")),
                ),
            ),
            CDeclaration(f"{dims_name}[]", "npy_intp", CodeExpression(f"{{{', '.join(dimensions)}}}")),
            CDeclaration(
                python_name,
                "PyObject *",
                self._array_result_creation_expression(
                    plan,
                    handoff.rank,
                    dims_name,
                    fortran_order,
                    native_name,
                ),
            ),
            CIf(
                CodeExpression(f"{python_name} == NULL"),
                body=(
                    CExpressionStatement(CodeExpression(f"free({native_name})")),
                    *decrefs,
                    CReturn(CodeExpression("NULL")),
                ),
            ),
            *self._capsule_base_attachment_nodes(
                python_name,
                base_name,
                native_name,
                failure_cleanup=decrefs,
            ),
        )

    def _array_result_creation_expression(
        self,
        plan: ResultPlan,
        rank: int,
        dims_name: str,
        fortran_order: int,
        native_name: str,
    ) -> CodeExpression:
        """Construct a non-owning NumPy view before attaching its capsule owner."""
        flags = (
            "NPY_ARRAY_F_CONTIGUOUS | NPY_ARRAY_WRITEABLE"
            if fortran_order
            else "NPY_ARRAY_C_CONTIGUOUS | NPY_ARRAY_WRITEABLE"
        )
        if plan.datatype_family is DatatypeFamily.STRING:
            handoff = plan.array
            if handoff is None or handoff.itemsize is None or handoff.itemsize <= 0:
                raise ValueError(f"Character array result {plan.owner_path!r} has no fixed itemsize")
            return CodeExpression(
                f"(PyObject *)PyArray_New(&PyArray_Type, {rank}, {dims_name}, NPY_STRING, "
                f"NULL, {native_name}, {handoff.itemsize}, {flags}, NULL)"
            )
        scalar_type = PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name)
        if scalar_type.numpy_type_macro is None:
            raise ValueError(f"Unsupported array result type {plan.semantic_type_name!r}")
        return CodeExpression(
            f"(PyObject *)PyArray_New(&PyArray_Type, {rank}, {dims_name}, {scalar_type.numpy_type_macro}, "
            f"NULL, {native_name}, 0, {flags}, NULL)"
        )

    def _capsule_base_attachment_nodes(
        self,
        array_name: str,
        base_name: str,
        data_name: str,
        *,
        failure_cleanup: tuple[CExpressionStatement, ...] = (),
    ) -> tuple[CDeclaration | CIf, ...]:
        """Transfer one bridge-owned buffer to NumPy without double release."""
        return (
            CDeclaration(
                base_name,
                "PyObject *",
                CodeExpression(f"PyCapsule_New({data_name}, NULL, capsule_cleanup)"),
            ),
            CIf(
                CodeExpression(f"{base_name} == NULL"),
                body=(
                    CExpressionStatement(CodeExpression(f"Py_DECREF({array_name})")),
                    CExpressionStatement(CodeExpression(f"free({data_name})")),
                    *failure_cleanup,
                    CReturn(CodeExpression("NULL")),
                ),
            ),
            CIf(
                CodeExpression(f"PyArray_SetBaseObject((PyArrayObject *){array_name}, {base_name}) < 0"),
                body=(
                    # PyArray_SetBaseObject steals the capsule reference even on failure.
                    CExpressionStatement(CodeExpression(f"Py_DECREF({array_name})")),
                    *failure_cleanup,
                    CReturn(CodeExpression("NULL")),
                ),
            ),
        )

    # String result lowering.
    def _lower_result_fixed_string(
        self,
        plan: ResultPlan,
        context: _CFunctionContext,
        failure_cleanup: tuple[str, ...],
    ) -> tuple[CExpressionStatement | CDeclaration | CIf, ...]:
        """Consume one bridge-owned NUL-terminated fixed string copy."""
        native_name = self._result_native_name(plan, context)
        python_name = context.python_results.get(plan.owner_path)
        if python_name is None:
            raise ValueError(f"String result {plan.owner_path!r} has no Python result role")
        decrefs = tuple(CExpressionStatement(CodeExpression(f"Py_DECREF({name})")) for name in failure_cleanup)
        if plan.nullable:
            return (
                CDeclaration(python_name, "PyObject *", CodeExpression("NULL")),
                CIf(
                    CodeExpression(f"{native_name} == NULL"),
                    body=(
                        CExpressionStatement(CodeExpression(f"{python_name} = Py_None")),
                        CExpressionStatement(CodeExpression("Py_INCREF(Py_None)")),
                    ),
                    else_body=(
                        CExpressionStatement(
                            CodeExpression(f'{python_name} = Py_BuildValue("s", (const char *){native_name})')
                        ),
                        CExpressionStatement(CodeExpression(f"free({native_name})")),
                    ),
                ),
                CIf(
                    CodeExpression(f"{python_name} == NULL"),
                    body=(*decrefs, CReturn(CodeExpression("NULL"))),
                ),
            )
        return (
            CIf(
                CodeExpression(f"{native_name} == NULL"),
                body=(
                    CExpressionStatement(
                        CodeExpression(
                            'PyErr_SetString(PyExc_MemoryError, "Unable to allocate copy-return output string.")'
                        )
                    ),
                    *decrefs,
                    CReturn(CodeExpression("NULL")),
                ),
            ),
            CDeclaration(
                python_name,
                "PyObject *",
                CodeExpression(f'Py_BuildValue("s", (const char *){native_name})'),
            ),
            CExpressionStatement(CodeExpression(f"free({native_name})")),
            CIf(
                CodeExpression(f"{python_name} == NULL"),
                body=(*decrefs, CReturn(CodeExpression("NULL"))),
            ),
        )

    # Scalar result lowering.
    def _lower_result_direct_value(
        self,
        plan: ResultPlan,
        context: _CFunctionContext,
        failure_cleanup: tuple[str, ...],
    ) -> tuple[CExpressionStatement | CDeclaration | CIf, ...]:
        return self._lower_result_value(plan, context, failure_cleanup)

    def _lower_result_value(
        self,
        plan: ResultPlan,
        context: _CFunctionContext,
        failure_cleanup: tuple[str, ...],
    ) -> tuple[CExpressionStatement | CDeclaration | CIf, ...]:
        """Convert one native result into its binding-owned Python consumer."""
        scalar_type = PrimitiveScalarTypeRegistry.type_for(plan.semantic_type_name)
        native_name = self._result_native_name(plan, context)
        python_name = context.python_results.get(plan.owner_path)
        if scalar_type.python_result_converter is None or python_name is None:
            raise ValueError(f"Unsupported scalar result type {plan.semantic_type_name!r}")
        return (
            CDeclaration(
                python_name,
                "PyObject *",
                CodeExpression(f"{scalar_type.python_result_converter}(&{native_name})"),
            ),
            CIf(
                CodeExpression(f"{python_name} == NULL"),
                body=(
                    *(CExpressionStatement(CodeExpression(f"Py_DECREF({name})")) for name in failure_cleanup),
                    CReturn(CodeExpression("NULL")),
                ),
            ),
        )

    def _result_native_name(self, plan: ResultPlan, context: _CFunctionContext) -> str:
        """Return the validated C storage consumed by one result conversion."""
        if plan.source_kind == "direct_return":
            if context.result_name is None:
                raise ValueError(f"Direct result {plan.owner_path!r} has no C storage")
            return context.result_name
        try:
            return context.native_outputs[plan.bridge.native_result_role]
        except KeyError:
            raise ValueError(f"Hidden result {plan.owner_path!r} has no C output storage") from None

    def _output_nodes(
        self,
        plan: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[CExpressionStatement | CDeclaration | CReturn, ...]:
        """Return the native envelope, status projection, and Python result."""
        nodes = [
            *self._lower_native_call(plan, self._bridge_call_statement(plan, context)),
            *self._owned_deferred_character_materialization_nodes(plan, context),
            *self._binding_transformation_post_call_nodes(plan, context),
            *self._lower_status_error(plan, context),
        ]
        if plan.results:
            nodes.extend(self._binding_result_nodes(plan, context))
        elif plan.writeback_actions:
            nodes.extend(self._writeback_nodes(plan, context))
        else:
            nodes.append(CExpressionStatement(CodeExpression("Py_RETURN_NONE")))
        return tuple(nodes)

    # Deferred-character native-array-handle result materialization.
    def _owned_deferred_character_materialization_nodes(
        self,
        plan: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf, ...]:
        """Materialize copied runtime-width character outputs into persistent CFI owners."""
        nodes = []
        for result in sorted(plan.results, key=lambda item: item.result_position):
            if not self._is_owned_deferred_character_result(result):
                continue
            native_name = self._result_native_name(result, context)
            nodes.extend(self._one_owned_deferred_character_materialization(result, native_name))
        return tuple(nodes)

    def _one_owned_deferred_character_materialization(
        self,
        result: ResultPlan,
        native_name: str,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf, ...]:
        """Copy one bridge-owned character payload into its handle-owned descriptor."""
        handle = result.native_array_handle
        if handle is None or handle.array.rank is None:
            raise ValueError(f"Deferred character result {result.owner_path!r} has no descriptor rank")
        rank = handle.array.rank
        descriptor = f"{native_name}_owner_descriptor"
        status = f"{native_name}_owner_status"
        itemsize = f"{native_name}_itemsize"
        lower_bounds = f"{native_name}_lower_bounds"
        upper_bounds = f"{native_name}_upper_bounds"
        byte_count = " * ".join((itemsize, *(f"{native_name}_extent_{axis}" for axis in range(rank))))
        return (
            CExpressionStatement(CodeExpression(f"{descriptor} = (CFI_cdesc_t *)malloc(sizeof(CFI_CDESC_T({rank})))")),
            CIf(
                CodeExpression(f"{descriptor} == NULL"),
                body=(
                    CExpressionStatement(CodeExpression(f"free({native_name})")),
                    CExpressionStatement(CodeExpression("PyErr_NoMemory()")),
                    CReturn(CodeExpression("NULL")),
                ),
            ),
            CExpressionStatement(
                CodeExpression(
                    f"{status} = CFI_establish({descriptor}, NULL, CFI_attribute_allocatable, CFI_type_char, "
                    f"({itemsize} > 0 ? (size_t){itemsize} : (size_t)1), {rank}, NULL)"
                )
            ),
            CIf(
                CodeExpression(f"{status} != CFI_SUCCESS"),
                body=(
                    CExpressionStatement(CodeExpression(f"free({descriptor})")),
                    CExpressionStatement(CodeExpression(f"{descriptor} = NULL")),
                    CExpressionStatement(CodeExpression(f"free({native_name})")),
                    CExpressionStatement(
                        CodeExpression(
                            'PyErr_SetString(PyExc_RuntimeError, "failed to establish deferred character owner")'
                        )
                    ),
                    CReturn(CodeExpression("NULL")),
                ),
            ),
            CIf(
                CodeExpression(f"{native_name} != NULL"),
                body=(
                    CDeclaration(f"{lower_bounds}[{rank}]", "CFI_index_t"),
                    CDeclaration(f"{upper_bounds}[{rank}]", "CFI_index_t"),
                    *(CExpressionStatement(CodeExpression(f"{lower_bounds}[{axis}] = 0")) for axis in range(rank)),
                    *(
                        CExpressionStatement(
                            CodeExpression(f"{upper_bounds}[{axis}] = (CFI_index_t){native_name}_extent_{axis} - 1")
                        )
                        for axis in range(rank)
                    ),
                    CExpressionStatement(
                        CodeExpression(
                            f"{status} = CFI_allocate({descriptor}, {lower_bounds}, {upper_bounds}, (size_t){itemsize})"
                        )
                    ),
                    CIf(
                        CodeExpression(f"{status} != CFI_SUCCESS"),
                        body=(
                            CExpressionStatement(CodeExpression(f"free({descriptor})")),
                            CExpressionStatement(CodeExpression(f"{descriptor} = NULL")),
                            CExpressionStatement(CodeExpression(f"free({native_name})")),
                            CExpressionStatement(
                                CodeExpression(
                                    'PyErr_SetString(PyExc_RuntimeError, "failed to allocate deferred character owner")'
                                )
                            ),
                            CReturn(CodeExpression("NULL")),
                        ),
                    ),
                    CExpressionStatement(
                        CodeExpression(f"memcpy({descriptor}->base_addr, {native_name}, (size_t)({byte_count}))")
                    ),
                    CExpressionStatement(CodeExpression(f"free({native_name})")),
                    CExpressionStatement(CodeExpression(f"{native_name} = NULL")),
                ),
            ),
        )

    def _binding_result_nodes(
        self,
        plan: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[CExpressionStatement | CDeclaration | CIf | CReturn, ...]:
        """Convert ordered results and assemble a tuple only in the binding."""
        ordered = tuple(sorted(plan.results, key=lambda item: item.result_position))
        converted = []
        nodes = []
        for result in ordered:
            nodes.extend(self.visit(result, context=context, failure_cleanup=tuple(converted)))
            converted.append(context.python_results[result.owner_path])
        nodes.extend(self._python_result_aggregation_nodes(tuple(converted), context))
        return tuple(nodes)

    def _python_result_aggregation_nodes(
        self,
        converted: tuple[str, ...],
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf | CReturn, ...]:
        """Return one object directly or assemble ordered tuple ownership."""
        if len(converted) == 1:
            return (CReturn(CodeExpression(converted[0])),)
        aggregate = context.python_result_name
        if aggregate is None:
            raise ValueError("Multiple Python results have no aggregate binding role")
        return (
            CDeclaration(aggregate, "PyObject *", CodeExpression(f"PyTuple_New({len(converted)})")),
            CIf(
                CodeExpression(f"{aggregate} == NULL"),
                body=(
                    *(CExpressionStatement(CodeExpression(f"Py_DECREF({name})")) for name in converted),
                    CReturn(CodeExpression("NULL")),
                ),
            ),
            *(
                CExpressionStatement(CodeExpression(f"PyTuple_SET_ITEM({aggregate}, {position}, {name})"))
                for position, name in enumerate(converted)
            ),
            CReturn(CodeExpression(aggregate)),
        )

    def _bridge_call_statement(self, plan: FunctionPlan, context: _CFunctionContext) -> CExpressionStatement:
        """Return the mechanical bridge call selected by result storage."""
        call = self._bridge_call(plan, context)
        direct_result = self._direct_result(plan)
        expression = (
            f"{context.result_name} = {call}"
            if direct_result is not None and not self._is_owned_native_array_result(direct_result)
            else call
        )
        return CExpressionStatement(CodeExpression(expression))

    def _lower_native_call(
        self,
        plan: FunctionPlan,
        call: CExpressionStatement,
    ) -> tuple[CAllowThreadsBegin | CAllowThreadsEnd | CExpressionStatement, ...]:
        """Dispatch the completed GIL envelope to directly named methods."""
        if plan.binding.hold_gil:
            return self._lower_native_call_held(call)
        return self._lower_native_call_released(call)

    def _lower_native_call_held(self, call: CExpressionStatement) -> tuple[CExpressionStatement, ...]:
        """Emit one native bridge call while retaining the GIL."""
        return (call,)

    def _lower_native_call_released(
        self,
        call: CExpressionStatement,
    ) -> tuple[CAllowThreadsBegin | CExpressionStatement | CAllowThreadsEnd, ...]:
        """Release the GIL only for the native bridge call."""
        return (CAllowThreadsBegin(), call, CAllowThreadsEnd())

    def _lower_status_error(
        self,
        plan: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf | CReturn, ...]:
        """Dispatch one completed post-call Python exception action."""
        policy = plan.binding.status_error
        if policy is None:
            return ()
        if policy.exception_kind is PythonExceptionKind.RUNTIME_ERROR:
            return self._lower_status_error_runtime_error(plan, context)
        raise ValueError(f"Unsupported C status exception for {plan.owner_path!r}: {policy.exception_kind!r}")

    def _lower_status_error_runtime_error(
        self,
        plan: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf | CReturn, ...]:
        """Raise RuntimeError from completed status/message roles with the GIL held."""
        policy = plan.binding.status_error
        status_name = context.native_outputs[policy.status_role]
        condition = CodeExpression(f"{status_name} != {policy.success}")
        if policy.message_role is None:
            return (
                CIf(
                    condition,
                    body=(
                        CExpressionStatement(
                            CodeExpression(
                                f'PyErr_Format(PyExc_RuntimeError, "native call failed with status %d != {policy.success}", '
                                f"(int){status_name})"
                            )
                        ),
                        CReturn(CodeExpression("NULL")),
                    ),
                ),
            )
        message_name = context.native_outputs[policy.message_role]
        message_object = f"{message_name}_obj"
        return (
            CIf(
                CodeExpression(f"{message_name} == NULL"),
                body=(
                    CExpressionStatement(CodeExpression("PyErr_NoMemory()")),
                    CReturn(CodeExpression("NULL")),
                ),
            ),
            CDeclaration(
                message_object,
                "PyObject *",
                CodeExpression(f"PyUnicode_FromString((const char *){message_name})"),
            ),
            CExpressionStatement(CodeExpression(f"free({message_name})")),
            CIf(
                CodeExpression(f"{message_object} == NULL"),
                body=(CReturn(CodeExpression("NULL")),),
            ),
            CIf(
                condition,
                body=(
                    CExpressionStatement(CodeExpression(f"PyErr_SetObject(PyExc_RuntimeError, {message_object})")),
                    CExpressionStatement(CodeExpression(f"Py_DECREF({message_object})")),
                    CReturn(CodeExpression("NULL")),
                ),
            ),
            CExpressionStatement(CodeExpression(f"Py_DECREF({message_object})")),
        )

    def _writeback_nodes(
        self,
        plan: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[CExpressionStatement | CDeclaration | CReturn, ...]:
        """Return the sole replacement conversion after the native call."""
        ordered = sorted(
            (
                action
                for action in plan.writeback_actions
                if action.phase is WritebackPhase.COPY_OUT and action.binding is not None
            ),
            key=lambda item: item.binding.result_position,
        )
        if ordered and all(action.object_kind is ObjectKind.NUMPY_ARRAY for action in ordered):
            return self._array_identity_writeback_nodes(plan, tuple(ordered), context)
        if len(ordered) != 1:
            raise ValueError(f"{plan.owner_path!r} requires exactly one writeback result")
        action = ordered[0]
        return self._lower_writeback(plan, action, context)

    # Ordinary-array writeback lowering.
    def _array_identity_writeback_nodes(
        self,
        plan: FunctionPlan,
        actions: tuple[LifecycleActionPlan, ...],
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CExpressionStatement | CIf | CReturn, ...]:
        """Return original validated NumPy objects with owned references."""
        nodes = []
        converted = []
        for action in actions:
            source = self._argument_for_role(plan, action.source_role)
            names = context.arguments[source.owner_path]
            python_name = context.python_results[action.owner_path]
            nodes.extend(
                (
                    CDeclaration(python_name, "PyObject *", CodeExpression(names.object_name)),
                    CExpressionStatement(CodeExpression(f"Py_INCREF({python_name})")),
                )
            )
            converted.append(python_name)
        nodes.extend(self._python_result_aggregation_nodes(tuple(converted), context))
        return tuple(nodes)

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
        if action.binding.datatype_family is DatatypeFamily.STRING:
            return self._lower_writeback_string(plan, action, context)
        return self._lower_writeback_value(plan, action, context)

    # String writeback lowering.
    def _lower_writeback_string(
        self,
        plan: FunctionPlan,
        action: LifecycleActionPlan,
        context: _CFunctionContext,
    ) -> tuple[CExpressionStatement | CDeclaration | CIf | CReturn, ...]:
        """Dispatch string replacement conversion from completed presence mode."""
        source = self._argument_for_role(plan, action.source_role)
        if source.binding.optional_mode is OptionalMode.REQUIRED:
            return self._lower_writeback_required_string(source, context)
        if source.binding.optional_mode is OptionalMode.NULLABLE_VALUE:
            return self._lower_writeback_optional_string(source, context)
        raise ValueError(f"Unsupported string writeback presence mode for {source.owner_path!r}")

    def _lower_writeback_required_string(
        self,
        source: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CExpressionStatement | CDeclaration | CIf | CReturn, ...]:
        """Convert one required mutable buffer and release it exactly once."""
        names = context.arguments[source.owner_path]
        python_result_name = context.python_result_name or "result_obj"
        return (
            CDeclaration(
                python_result_name,
                "PyObject *",
                CodeExpression(f'Py_BuildValue("s", (const char *){names.value_name})'),
            ),
            CExpressionStatement(CodeExpression(f"free({names.value_name})")),
            CIf(
                CodeExpression(f"{python_result_name} == NULL"),
                body=(CReturn(CodeExpression("NULL")),),
            ),
            CReturn(CodeExpression(python_result_name)),
        )

    def _lower_writeback_optional_string(
        self,
        source: ArgumentTransferPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration | CIf | CReturn, ...]:
        """Return None for absence or convert and release one concrete replacement."""
        names = context.arguments[source.owner_path]
        python_result_name = context.python_result_name or "result_obj"
        return (
            CDeclaration(python_result_name, "PyObject *", CodeExpression("NULL")),
            CIf(
                CodeExpression(f"{names.value_name} == NULL"),
                body=(
                    CExpressionStatement(CodeExpression("Py_INCREF(Py_None)")),
                    CExpressionStatement(CodeExpression(f"{python_result_name} = Py_None")),
                ),
                else_body=(
                    CExpressionStatement(
                        CodeExpression(f'{python_result_name} = Py_BuildValue("s", (const char *){names.value_name})')
                    ),
                    CExpressionStatement(CodeExpression(f"free({names.value_name})")),
                    CIf(
                        CodeExpression(f"{python_result_name} == NULL"),
                        body=(CReturn(CodeExpression("NULL")),),
                    ),
                ),
            ),
            CReturn(CodeExpression(python_result_name)),
        )

    def _lower_writeback_in_place_argument(
        self,
        plan: FunctionPlan,
        action: LifecycleActionPlan,
        context: _CFunctionContext,
    ) -> tuple[CExpressionStatement | CDeclaration | CReturn, ...]:
        return self._lower_writeback_value(plan, action, context)

    # Scalar writeback lowering.
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
        if source.bridge.descriptor_output_presence_role is not None:
            return self._lower_descriptor_writeback_value(names, scalar_type, python_result_name)
        return (
            CDeclaration(
                python_result_name,
                "PyObject *",
                CodeExpression(f"{scalar_type.python_result_converter}(&{names.value_name})"),
            ),
            CExpressionStatement(CodeExpression(f"if ({python_result_name} == NULL) return NULL")),
            CReturn(CodeExpression(python_result_name)),
        )

    def _lower_descriptor_writeback_value(
        self,
        names: _CArgumentNames,
        scalar_type,
        python_result_name: str,
    ) -> tuple[CDeclaration | CIf | CReturn, ...]:
        """Return None or one copied scalar from a mutated required descriptor."""
        return (
            CDeclaration(python_result_name, "PyObject *", CodeExpression("NULL")),
            CIf(
                CodeExpression(f"!{self._descriptor_output_present_name(names)}"),
                body=(
                    CExpressionStatement(CodeExpression("Py_INCREF(Py_None)")),
                    CExpressionStatement(CodeExpression(f"{python_result_name} = Py_None")),
                ),
                else_body=(
                    CExpressionStatement(
                        CodeExpression(
                            f"{python_result_name} = {scalar_type.python_result_converter}(&{names.value_name})"
                        )
                    ),
                    CIf(
                        CodeExpression(f"{python_result_name} == NULL"),
                        body=(CReturn(CodeExpression("NULL")),),
                    ),
                ),
            ),
            CReturn(CodeExpression(python_result_name)),
        )

    @staticmethod
    def _descriptor_output_present_name(names: _CArgumentNames) -> str:
        """Name the binding-local final descriptor-state flag."""
        return f"{names.value_name}_descriptor_output_present"

    def _argument_for_role(self, plan: FunctionPlan, role: str) -> ArgumentTransferPlan:
        """Return the argument that produced one validated lifecycle role."""
        for argument in plan.arguments:
            if argument.binding.handoff_role == role:
                return argument
        raise ValueError(f"{plan.owner_path!r} has no argument for lifecycle role {role!r}")

    def _function_context(self, plan: FunctionPlan) -> _CFunctionContext:
        arguments = self._argument_contexts(plan)
        native_outputs = self._native_output_names(plan)
        output_owners = self._output_owners(plan)
        python_results = self._python_result_names(output_owners)
        python_result = self._python_result_name(plan)
        native_result = self._native_result_name(plan)
        role_values = self._argument_role_values(plan, arguments)
        return _CFunctionContext(
            arguments,
            native_outputs,
            native_result,
            python_result,
            python_results,
            role_values,
        )

    def _argument_contexts(self, plan: FunctionPlan) -> dict[str, _CArgumentNames]:
        """Name the binding locals for every Python argument."""
        return {argument.owner_path: self._argument_context_names(argument) for argument in plan.arguments}

    def _native_output_names(self, plan: FunctionPlan) -> dict[str, str]:
        """Name native hidden-output locals by their completed symbolic roles."""
        return {
            slot.symbolic_role: slot.native_name.lower()
            for slot in plan.native_call_slots
            if slot.source_kind == "result"
        }

    def _output_owners(self, plan: FunctionPlan) -> tuple[tuple[str, int], ...]:
        """Return ordered Python result owners from results or copy-out actions."""
        results = tuple(sorted(plan.results, key=lambda item: item.result_position))
        if results:
            return tuple((result.owner_path, result.result_position) for result in results)
        writebacks = self._ordered_output_writebacks(plan)
        return tuple((action.owner_path, action.binding.result_position) for action in writebacks)

    def _ordered_output_writebacks(self, plan: FunctionPlan) -> tuple[LifecycleActionPlan, ...]:
        """Return copy-out writebacks ordered by their completed result positions."""
        actions = (
            action
            for action in plan.writeback_actions
            if action.phase is WritebackPhase.COPY_OUT and action.binding is not None
        )
        return tuple(sorted(actions, key=lambda action: action.binding.result_position))

    def _python_result_names(self, output_owners: tuple[tuple[str, int], ...]) -> dict[str, str]:
        """Name one Python result local per ordered output owner."""
        single_output = len(output_owners) == 1
        return {
            owner_path: ("result_obj" if single_output else f"result_{position}_obj")
            for owner_path, position in output_owners
        }

    def _python_result_name(self, plan: FunctionPlan) -> str | None:
        """Return the aggregate Python result local only when output exists."""
        return "result_obj" if plan.results or plan.writeback_actions else None

    def _native_result_name(self, plan: FunctionPlan) -> str | None:
        """Return the direct native result local only for native functions."""
        return "result" if self._direct_result(plan) is not None else None

    def _argument_role_values(
        self,
        plan: FunctionPlan,
        arguments: dict[str, _CArgumentNames],
    ) -> dict[str, str]:
        """Map completed handoff roles to their binding value locals."""
        return {
            argument.binding.handoff_role: self._argument_role_value(
                argument,
                arguments[argument.owner_path].value_name,
            )
            for argument in plan.arguments
        }

    @staticmethod
    def _argument_role_value(argument: ArgumentTransferPlan, value_name: str) -> str:
        """Expose scalar-storage roles as values in dependent shape expressions."""
        if argument.binding.python_action is not PythonBarrierAction.SCALAR_STORAGE:
            return value_name
        scalar_type = PrimitiveScalarTypeRegistry.type_for(argument.semantic_type_name)
        return f"(*(({scalar_type.c_spelling} *){value_name}))"

    def _argument_context_names(self, argument: ArgumentTransferPlan) -> _CArgumentNames:
        """Name one argument's binding locals from its public Python name."""
        name = argument.binding.python_name.lower()
        rank = (
            15
            if argument.array is not None and argument.array.rank is None
            else (argument.array.rank if argument.array is not None else 0)
        )
        return _CArgumentNames(
            f"{name}_obj",
            name,
            f"{name}_length",
            f"{name}_nullable",
            f"{name}_present",
            tuple(f"{name}_extent_{axis}" for axis in range(rank)),
            tuple(f"{name}_upper_bound_{axis}" for axis in range(rank)),
            tuple(f"{name}_stride_{axis}" for axis in range(rank)),
            f"{name}_rank",
            f"{name}_itemsize",
        )

    def _keyword_declaration(self, plan: FunctionPlan) -> CDeclaration:
        keywords = ", ".join(
            f'"{argument.binding.python_name}"'
            for argument in sorted(plan.arguments, key=lambda item: item.python_position)
        )
        entries = f"{keywords}, NULL" if keywords else "NULL"
        return CDeclaration("kwlist[]", "static char *", CodeExpression(f"{{{entries}}}"))

    def _parse_statement(self, plan: FunctionPlan, context: _CFunctionContext) -> CExpressionStatement:
        arguments = sorted(plan.arguments, key=lambda item: item.python_position)
        required_modes = {OptionalMode.REQUIRED, OptionalMode.REQUIRED_DESCRIPTOR}
        required = [item for item in arguments if item.binding.optional_mode in required_modes]
        optional = [item for item in arguments if item.binding.optional_mode not in required_modes]
        units = "O" * len(required) + ("|" if optional else "") + "O" * len(optional)
        targets = ", ".join(f"&{context.arguments[item.owner_path].object_name}" for item in arguments)
        suffix = f", {targets}" if targets else ""
        return CExpressionStatement(
            CodeExpression(f'if (!PyArg_ParseTupleAndKeywords(args, kwargs, "{units}", kwlist{suffix})) return NULL')
        )

    def _direct_result_declaration(
        self,
        plan: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration, ...]:
        result = self._direct_result(plan)
        if result is None or context.result_name is None:
            return ()
        if result.scalar_descriptor is not None:
            declarations = [
                CDeclaration(context.result_name, "void *", CodeExpression("NULL")),
                CDeclaration(f"{context.result_name}_present", "int", CodeExpression("0")),
            ]
            if result.scalar_descriptor.runtime_length:
                declarations.append(CDeclaration(f"{context.result_name}_length", "int64_t", CodeExpression("0")))
            return tuple(declarations)
        if self._is_owned_native_array_result(result):
            if self._is_owned_deferred_character_result(result):
                rank = result.native_array_handle.array.rank
                return (
                    CDeclaration(context.result_name, "void *", CodeExpression("NULL")),
                    CDeclaration(f"{context.result_name}_itemsize", "int64_t", CodeExpression("0")),
                    *(
                        CDeclaration(f"{context.result_name}_extent_{axis}", "int64_t", CodeExpression("0"))
                        for axis in range(rank)
                    ),
                    CDeclaration(
                        f"{context.result_name}_owner_descriptor",
                        "CFI_cdesc_t *",
                        CodeExpression("NULL"),
                    ),
                    CDeclaration(
                        f"{context.result_name}_owner_status",
                        "int",
                        CodeExpression("CFI_SUCCESS"),
                    ),
                )
            return (
                CDeclaration(context.result_name, "CFI_cdesc_t *", CodeExpression("NULL")),
                CDeclaration(f"{context.result_name}_owner_status", "int", CodeExpression("CFI_SUCCESS")),
            )
        if result.object_kind in {ObjectKind.STRING, ObjectKind.NUMPY_ARRAY}:
            return (CDeclaration(context.result_name, "void *", CodeExpression("NULL")),)
        scalar_type = PrimitiveScalarTypeRegistry.type_for(result.semantic_type_name)
        return (CDeclaration(context.result_name, scalar_type.c_spelling),)

    def _native_output_declarations(
        self,
        plan: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[CDeclaration, ...]:
        """Declare bridge output storage from typed native result slots."""
        declarations = []
        for slot in sorted(plan.native_call_slots, key=lambda item: item.native_position):
            if slot.source_kind != "result":
                continue
            name = context.native_outputs[slot.symbolic_role]
            if slot.scalar_descriptor is not None:
                declarations.append(CDeclaration(name, "void *", CodeExpression("NULL")))
                declarations.append(CDeclaration(f"{name}_present", "int", CodeExpression("0")))
                if slot.scalar_descriptor.runtime_length:
                    declarations.append(CDeclaration(f"{name}_length", "int64_t", CodeExpression("0")))
                continue
            if self._is_owned_native_array_slot(slot):
                if self._is_owned_deferred_character_slot(slot):
                    rank = slot.native_array_handle.array.rank
                    declarations.extend(
                        (
                            CDeclaration(name, "void *", CodeExpression("NULL")),
                            CDeclaration(f"{name}_itemsize", "int64_t", CodeExpression("0")),
                            *(
                                CDeclaration(f"{name}_extent_{axis}", "int64_t", CodeExpression("0"))
                                for axis in range(rank)
                            ),
                            CDeclaration(
                                f"{name}_owner_descriptor",
                                "CFI_cdesc_t *",
                                CodeExpression("NULL"),
                            ),
                            CDeclaration(f"{name}_owner_status", "int", CodeExpression("CFI_SUCCESS")),
                        )
                    )
                    continue
                declarations.extend(
                    (
                        CDeclaration(name, "CFI_cdesc_t *", CodeExpression("NULL")),
                        CDeclaration(f"{name}_owner_status", "int", CodeExpression("CFI_SUCCESS")),
                    )
                )
                continue
            if slot.object_kind in {ObjectKind.STRING, ObjectKind.NUMPY_ARRAY}:
                declarations.append(CDeclaration(name, "void *", CodeExpression("NULL")))
                continue
            if slot.semantic_type_name is None:
                raise ValueError(f"Missing native result datatype for {slot.owner_path!r}")
            scalar_type = PrimitiveScalarTypeRegistry.type_for(slot.semantic_type_name)
            declarations.append(CDeclaration(name, scalar_type.c_spelling))
        return tuple(declarations)

    def _native_call_setup_nodes(
        self,
        plan: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[CExpressionStatement | CIf, ...]:
        """Allocate persistent standard-descriptor storage selected by result plans."""
        nodes = list(self._binding_transformation_setup_nodes(plan, context))
        initialized = []
        transformation_cleanup = self._binding_transformation_cleanup_nodes(plan, context)
        for result in sorted(plan.results, key=lambda item: item.result_position):
            if not self._is_owned_native_array_result(result):
                continue
            if self._is_owned_deferred_character_result(result):
                continue
            descriptor = self._result_native_name(result, context)
            handle = result.native_array_handle
            if handle is None or handle.array.rank is None:
                raise ValueError(f"Owned result {result.owner_path!r} is missing descriptor facts")
            cfi_type = self._native_array_cfi_type(result)
            if cfi_type is None:
                raise ValueError(f"Owned result {result.owner_path!r} is missing a CFI element type")
            elem_len = f"sizeof({PrimitiveScalarTypeRegistry.type_for(result.semantic_type_name).c_spelling})"
            cleanup = tuple(
                node for previous in reversed(initialized) for node in self._owned_descriptor_failure_cleanup(previous)
            )
            nodes.extend(
                (
                    CExpressionStatement(
                        CodeExpression(
                            f"{descriptor} = (CFI_cdesc_t *)malloc(sizeof(CFI_CDESC_T({handle.array.rank})))"
                        )
                    ),
                    CIf(
                        CodeExpression(f"{descriptor} == NULL"),
                        body=(
                            *transformation_cleanup,
                            *cleanup,
                            CExpressionStatement(CodeExpression("PyErr_NoMemory()")),
                            CReturn(CodeExpression("NULL")),
                        ),
                    ),
                    CExpressionStatement(
                        CodeExpression(
                            f"{descriptor}_owner_status = CFI_establish({descriptor}, NULL, "
                            f"CFI_attribute_allocatable, {cfi_type}, {elem_len}, {handle.array.rank}, NULL)"
                        )
                    ),
                    CIf(
                        CodeExpression(f"{descriptor}_owner_status != CFI_SUCCESS"),
                        body=(
                            CExpressionStatement(CodeExpression(f"free({descriptor})")),
                            CExpressionStatement(CodeExpression(f"{descriptor} = NULL")),
                            *transformation_cleanup,
                            *cleanup,
                            CExpressionStatement(
                                CodeExpression(
                                    'PyErr_SetString(PyExc_RuntimeError, "failed to establish owned native array '
                                    'descriptor storage")'
                                )
                            ),
                            CReturn(CodeExpression("NULL")),
                        ),
                    ),
                )
            )
            initialized.append(descriptor)
        return tuple(nodes)

    # Binding-owned representation transformations.
    def _binding_transformation_setup_nodes(
        self,
        plan: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[CExpressionStatement | CIf, ...]:
        """Create planned NumPy temporaries after every source argument is validated."""
        nodes = []
        initialized: list[str] = []
        for argument in plan.arguments:
            if not argument.transformations:
                continue
            names = context.arguments[argument.owner_path]
            temporary = self._array_transformation_temp_name(names)
            source = f"(PyArrayObject *){names.object_name}"
            copy_in = self._has_transformation_phase(argument, WritebackPhase.COPY_IN)
            expression = (
                f"PyArray_NewCopy({source}, NPY_FORTRANORDER)"
                if copy_in
                else f"PyArray_EMPTY(PyArray_NDIM({source}), PyArray_DIMS({source}), PyArray_TYPE({source}), 1)"
            )
            prior_cleanup = tuple(
                CExpressionStatement(CodeExpression(f"Py_DECREF({name})")) for name in reversed(initialized)
            )
            nodes.extend(
                (
                    CExpressionStatement(CodeExpression(f"{temporary} = {expression}")),
                    CIf(
                        CodeExpression(f"{temporary} == NULL"),
                        body=(*prior_cleanup, CReturn(CodeExpression("NULL"))),
                    ),
                    CExpressionStatement(
                        CodeExpression(f"{names.value_name} = PyArray_DATA((PyArrayObject *){temporary})")
                    ),
                )
            )
            initialized.append(temporary)
        return tuple(nodes)

    def _binding_transformation_post_call_nodes(
        self,
        plan: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[CExpressionStatement | CIf, ...]:
        """Perform planned copy-out actions, then release every binding temporary."""
        nodes = []
        cleanup = self._binding_transformation_cleanup_nodes(plan, context)
        for argument in plan.arguments:
            if not self._has_transformation_phase(argument, WritebackPhase.COPY_OUT):
                continue
            names = context.arguments[argument.owner_path]
            temporary = self._array_transformation_temp_name(names)
            nodes.append(
                CIf(
                    CodeExpression(
                        f"PyArray_CopyInto((PyArrayObject *){names.object_name}, (PyArrayObject *){temporary}) < 0"
                    ),
                    body=(*cleanup, CReturn(CodeExpression("NULL"))),
                )
            )
        nodes.extend(cleanup)
        return tuple(nodes)

    def _binding_transformation_cleanup_nodes(
        self,
        plan: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[CExpressionStatement, ...]:
        """Release every planned binding temporary exactly once."""
        return tuple(
            CExpressionStatement(
                CodeExpression(
                    f"Py_XDECREF({self._array_transformation_temp_name(context.arguments[item.owner_path])})"
                )
            )
            for item in reversed(plan.arguments)
            if self._has_transformation_phase(item, WritebackPhase.CLEANUP)
        )

    @staticmethod
    def _has_transformation_phase(argument: ArgumentTransferPlan, phase: WritebackPhase) -> bool:
        """Return whether one completed transfer owns an action in a lifecycle phase."""
        return any(transformation.phase is phase for transformation in argument.transformations)

    @staticmethod
    def _array_transformation_temp_name(names: _CArgumentNames) -> str:
        """Name the binding-owned NumPy representation temporary."""
        return f"{names.value_name}_representation"

    @staticmethod
    def _owned_descriptor_failure_cleanup(
        descriptor_name: str,
    ) -> tuple[CExpressionStatement, ...]:
        """Release unpublished owner storage without changing Python ownership."""
        return (
            CExpressionStatement(
                CodeExpression(
                    f"if ({descriptor_name} != NULL) {{ if ({descriptor_name}->base_addr != NULL) "
                    f"(void)CFI_deallocate({descriptor_name}); free({descriptor_name}); {descriptor_name} = NULL; }}"
                )
            ),
        )

    @staticmethod
    def _decref_names(names: tuple[str, ...]) -> tuple[CExpressionStatement, ...]:
        """Release already-created Python result objects on a later failure."""
        return tuple(CExpressionStatement(CodeExpression(f"Py_DECREF({name})")) for name in names)

    @staticmethod
    def _is_owned_native_array_result(result: ResultPlan) -> bool:
        """Return whether one result owns persistent standard-descriptor storage."""
        handle = result.native_array_handle
        return handle is not None and handle.handoff.abi is NativeDescriptorHandoffABI.OWNED_RESULT_STORAGE

    @staticmethod
    def _is_owned_native_array_slot(slot: NativeCallSlotPlan) -> bool:
        """Return whether one hidden slot shares owned descriptor storage."""
        handle = slot.native_array_handle
        return handle is not None and handle.handoff.abi is NativeDescriptorHandoffABI.OWNED_RESULT_STORAGE

    @classmethod
    def _is_owned_deferred_character_result(cls, result: ResultPlan) -> bool:
        """Return whether owner storage needs runtime character-width materialization."""
        return cls._is_owned_native_array_result(result) and result.datatype_family is DatatypeFamily.STRING

    @classmethod
    def _is_owned_deferred_character_slot(cls, slot: NativeCallSlotPlan) -> bool:
        """Return whether a hidden owner slot carries runtime-width characters."""
        return cls._is_owned_native_array_slot(slot) and slot.datatype_family is DatatypeFamily.STRING

    def _owned_result_descriptor_name(self, result: ResultPlan, context: _CFunctionContext) -> str:
        """Return persistent owner storage after any deferred-character materialization."""
        native_name = self._result_native_name(result, context)
        if self._is_owned_deferred_character_result(result):
            return f"{native_name}_owner_descriptor"
        return native_name

    def _bridge_call(self, plan: FunctionPlan, context: _CFunctionContext) -> str:
        arguments = [
            *self._bridge_visible_argument_values(plan, context),
            *self._bridge_hidden_result_values(plan, context),
            *self._bridge_direct_result_values(plan, context),
        ]
        return f"{self._bridge_function_name(plan)}({', '.join(arguments)})"

    def _bridge_visible_argument_values(
        self,
        plan: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[str, ...]:
        """Return ordered visible binding-to-bridge ABI values."""
        values = []
        for argument in sorted(plan.arguments, key=lambda item: item.bridge.abi_position):
            names = context.arguments[argument.owner_path]
            values.extend(self._bridge_call_arguments(argument, names))
            if argument.bridge.optional_mode is OptionalMode.DESCRIPTOR:
                values.append(names.present_name)
            if argument.bridge.descriptor_output_role is not None:
                values.extend((f"&{names.value_name}", f"&{self._descriptor_output_present_name(names)}"))
        return tuple(values)

    def _bridge_hidden_result_values(
        self,
        plan: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[str, ...]:
        """Return ordered hidden output ABI pointers."""
        values = []
        for slot in sorted(plan.native_call_slots, key=lambda item: item.native_position):
            if slot.source_kind != "result":
                continue
            name = context.native_outputs[slot.symbolic_role]
            values.extend(self._bridge_hidden_result_slot_values(slot, name))
        return tuple(values)

    def _bridge_hidden_result_slot_values(self, slot: NativeCallSlotPlan, name: str) -> tuple[str, ...]:
        """Return ABI pointers for one hidden output slot."""
        if self._is_owned_deferred_character_slot(slot):
            rank = slot.native_array_handle.array.rank
            return (
                f"&{name}",
                f"&{name}_itemsize",
                *(f"&{name}_extent_{axis}" for axis in range(rank)),
            )
        values = [name if self._is_owned_native_array_slot(slot) else f"&{name}"]
        if slot.scalar_descriptor is not None:
            values.append(f"&{name}_present")
            if slot.scalar_descriptor.runtime_length:
                values.append(f"&{name}_length")
        return tuple(values)

    def _bridge_direct_result_values(
        self,
        plan: FunctionPlan,
        context: _CFunctionContext,
    ) -> tuple[str, ...]:
        """Return helper ABI fields for one direct result."""
        result = self._direct_result(plan)
        if result is None:
            return ()
        if self._is_owned_native_array_result(result):
            if context.result_name is None:
                raise ValueError(f"Owned direct result {result.owner_path!r} has no C storage")
            if self._is_owned_deferred_character_result(result):
                rank = result.native_array_handle.array.rank
                return (
                    f"&{context.result_name}",
                    f"&{context.result_name}_itemsize",
                    *(f"&{context.result_name}_extent_{axis}" for axis in range(rank)),
                )
            return (context.result_name,)
        if result.scalar_descriptor is None:
            return ()
        values = [f"&{context.result_name}_present"]
        if result.scalar_descriptor.runtime_length:
            values.append(f"&{context.result_name}_length")
        return tuple(values)

    def _bridge_call_arguments(self, plan: ArgumentTransferPlan, names: _CArgumentNames) -> tuple[str, ...]:
        """Return one binding-to-bridge C handoff, including helper ABI fields."""
        if plan.bridge.handoff_mode is ArgumentHandoffMode.CHARACTER_BUFFER:
            return self._string_bridge_call_arguments(names)
        if plan.bridge.handoff_mode is ArgumentHandoffMode.ARRAY_BUFFER:
            return self._array_bridge_call_arguments(plan, names)
        if plan.bridge.handoff_mode is ArgumentHandoffMode.NATIVE_DESCRIPTOR:
            return (names.value_name,)
        return self._scalar_bridge_call_arguments(plan, names)

    # Scalar bridge call arguments.
    def _scalar_bridge_call_arguments(
        self,
        plan: ArgumentTransferPlan,
        names: _CArgumentNames,
    ) -> tuple[str, ...]:
        """Return one scalar value, storage, address, or optional handoff."""
        if plan.bridge.optional_mode is not OptionalMode.REQUIRED:
            return (names.nullable_name,)
        if plan.bridge.handoff_mode is ArgumentHandoffMode.OPAQUE_ADDRESS:
            return (names.value_name,)
        if plan.bridge.handoff_mode is ArgumentHandoffMode.TYPED_REFERENCE:
            return (f"&{names.value_name}",)
        return (names.value_name,)

    # String bridge call arguments.
    def _string_bridge_call_arguments(self, names: _CArgumentNames) -> tuple[str, ...]:
        """Return one scalar string pointer-and-length handoff."""
        return names.value_name, f"(int64_t){names.length_name}"

    # Ordinary-array bridge call arguments.
    def _array_bridge_call_arguments(
        self,
        plan: ArgumentTransferPlan,
        names: _CArgumentNames,
    ) -> tuple[str, ...]:
        """Return one completed ordinary-array C ABI field sequence."""
        handoff = plan.array
        if handoff is None:
            raise ValueError(f"Array argument {plan.owner_path!r} has no handoff spec")
        arguments = [names.value_name]
        if handoff.runtime_rank_role is not None:
            arguments.append(names.runtime_rank_name)
        if handoff.itemsize_role is not None:
            arguments.append(names.itemsize_name)
        arguments.extend(names.extent_names)
        arguments.extend(self._selected_array_axis_names(names.upper_bound_names, handoff.upper_bound_roles))
        arguments.extend(self._selected_array_axis_names(names.stride_names, handoff.stride_roles))
        return tuple(arguments)

    def _selected_array_axis_names(self, names: tuple[str, ...], roles: tuple[str, ...]) -> tuple[str, ...]:
        """Return array ABI local names only when the plan carries their roles."""
        return names if roles else ()

    def _bridge_prototype(self, plan: FunctionPlan) -> CFunctionPrototype:
        argument_parameters = tuple(
            parameter
            for argument in sorted(plan.arguments, key=lambda item: item.bridge.abi_position)
            for parameter in self._bridge_argument_parameters(argument)
        )
        result_parameters = tuple(
            parameter
            for slot in sorted(plan.native_call_slots, key=lambda item: item.native_position)
            for parameter in self._bridge_result_parameters(slot)
        )
        direct_result = self._direct_result(plan)
        direct_parameters = self._direct_bridge_result_parameters(direct_result)
        return CFunctionPrototype(
            self._bridge_function_name(plan),
            self._bridge_return_type(plan),
            (*argument_parameters, *result_parameters, *direct_parameters),
        )

    def _bridge_return_type(self, plan: FunctionPlan) -> str:
        """Return the direct bridge result type, or void for subroutines."""
        result = self._direct_result(plan)
        if result is None:
            return "void"
        if self._is_owned_native_array_result(result):
            return "void"
        if result.scalar_descriptor is not None:
            return "void *"
        if result.object_kind in {ObjectKind.STRING, ObjectKind.NUMPY_ARRAY}:
            return "void *"
        return PrimitiveScalarTypeRegistry.type_for(result.semantic_type_name).c_spelling

    def _direct_bridge_result_parameters(self, result: ResultPlan | None) -> tuple[CParameter, ...]:
        """Return helper ABI parameters associated with one direct result."""
        if result is None:
            return ()
        if self._is_owned_native_array_result(result):
            if self._is_owned_deferred_character_result(result):
                rank = result.native_array_handle.array.rank
                return (
                    CParameter("result", "void **"),
                    CParameter("result_itemsize", "int64_t *"),
                    *(CParameter(f"result_extent_{axis}", "int64_t *") for axis in range(rank)),
                )
            return (CParameter("result", "CFI_cdesc_t *"),)
        if result.scalar_descriptor is not None:
            parameters = [CParameter("result_present", "int *")]
            if result.scalar_descriptor.runtime_length:
                parameters.append(CParameter("result_length", "int64_t *"))
            return tuple(parameters)
        return ()

    def _direct_result(self, plan: FunctionPlan) -> ResultPlan | None:
        """Return the sole direct native function result, when present."""
        return next((result for result in plan.results if result.source_kind == "direct_return"), None)

    def _bridge_argument_parameters(self, argument: ArgumentTransferPlan) -> tuple[CParameter, ...]:
        """Return the bridge ABI parameters for one Python argument."""
        name = argument.bridge.native_name.lower()
        if argument.bridge.handoff_mode is ArgumentHandoffMode.CHARACTER_BUFFER:
            return self._string_bridge_argument_parameters(argument, name)
        if argument.bridge.handoff_mode is ArgumentHandoffMode.ARRAY_BUFFER:
            return self._array_bridge_argument_parameters(argument, name)
        if argument.bridge.handoff_mode is ArgumentHandoffMode.NATIVE_DESCRIPTOR:
            parameters = [CParameter(name, "CFI_cdesc_t *")]
            if argument.bridge.optional_mode is OptionalMode.DESCRIPTOR:
                parameters.append(CParameter(f"{name}_present", "void *"))
            return tuple(parameters)
        scalar_type = self._scalar_bridge_argument_type(argument)
        if argument.bridge.optional_mode is OptionalMode.DESCRIPTOR:
            return (CParameter(name, scalar_type), CParameter(f"{name}_present", "void *"))
        if argument.bridge.descriptor_output_role is not None:
            return (
                CParameter(name, scalar_type),
                CParameter(f"{name}_output", "void *"),
                CParameter(f"{name}_output_present", "int *"),
            )
        return (CParameter(name, scalar_type),)

    # Scalar bridge ABI parameters.
    def _scalar_bridge_argument_type(self, argument: ArgumentTransferPlan) -> str:
        """Return the C ABI type for one scalar bridge input."""
        if argument.bridge.optional_mode is not OptionalMode.REQUIRED:
            return "void *"
        if argument.bridge.handoff_mode is ArgumentHandoffMode.OPAQUE_ADDRESS:
            return "void *"
        scalar_type = PrimitiveScalarTypeRegistry.type_for(argument.semantic_type_name).c_spelling
        if argument.bridge.handoff_mode is ArgumentHandoffMode.TYPED_REFERENCE:
            return f"{scalar_type} *"
        return scalar_type

    # String bridge ABI parameters.
    def _string_bridge_argument_parameters(
        self,
        argument: ArgumentTransferPlan,
        name: str,
    ) -> tuple[CParameter, ...]:
        """Return one scalar string pointer-and-length ABI pair."""
        pointer_type = "char *" if argument.bridge.codegen_action is CodegenAction.COPY_IN_OUT else "const char *"
        return CParameter(name, pointer_type), CParameter(f"{name}_length", "int64_t")

    # Ordinary-array bridge ABI parameters.
    def _array_bridge_argument_parameters(
        self,
        argument: ArgumentTransferPlan,
        name: str,
    ) -> tuple[CParameter, ...]:
        """Return the completed ordinary-array bridge ABI parameters."""
        handoff = argument.array
        if handoff is None:
            raise ValueError(f"Array argument {argument.owner_path!r} has no handoff spec")
        parameters = [CParameter(name, "void *")]
        if handoff.runtime_rank_role is not None:
            parameters.append(CParameter(f"{name}_rank", "int64_t"))
        if handoff.itemsize_role is not None:
            parameters.append(CParameter(f"{name}_itemsize", "int64_t"))
        parameters.extend(self._array_bridge_axis_parameters(name, "extent", len(handoff.extent_roles)))
        parameters.extend(self._array_bridge_axis_parameters(name, "upper_bound", len(handoff.upper_bound_roles)))
        parameters.extend(self._array_bridge_axis_parameters(name, "stride", len(handoff.stride_roles)))
        return tuple(parameters)

    def _array_bridge_axis_parameters(self, name: str, label: str, count: int) -> tuple[CParameter, ...]:
        """Return one named int64 bridge parameter per ordinary-array axis."""
        return tuple(CParameter(f"{name}_{label}_{axis}", "int64_t") for axis in range(count))

    def _bridge_result_parameters(self, slot: NativeCallSlotPlan) -> tuple[CParameter, ...]:
        """Return the C ABI parameter for one native result slot."""
        if slot.source_kind != "result":
            return ()
        if slot.scalar_descriptor is not None:
            parameters = [
                CParameter(slot.native_name.lower(), "void **"),
                CParameter(f"{slot.native_name.lower()}_present", "int *"),
            ]
            if slot.scalar_descriptor.runtime_length:
                parameters.append(CParameter(f"{slot.native_name.lower()}_length", "int64_t *"))
            return tuple(parameters)
        if self._is_owned_native_array_slot(slot):
            if self._is_owned_deferred_character_slot(slot):
                rank = slot.native_array_handle.array.rank
                name = slot.native_name.lower()
                return (
                    CParameter(name, "void **"),
                    CParameter(f"{name}_itemsize", "int64_t *"),
                    *(CParameter(f"{name}_extent_{axis}", "int64_t *") for axis in range(rank)),
                )
            return (CParameter(slot.native_name.lower(), "CFI_cdesc_t *"),)
        if slot.object_kind in {ObjectKind.STRING, ObjectKind.NUMPY_ARRAY}:
            return (CParameter(slot.native_name.lower(), "void **"),)
        if slot.semantic_type_name is None:
            raise ValueError(f"Missing bridge result datatype for {slot.owner_path!r}")
        scalar_type = PrimitiveScalarTypeRegistry.type_for(slot.semantic_type_name).c_spelling
        return (CParameter(slot.native_name.lower(), f"{scalar_type} *"),)

    def _module_variable_bridge_prototypes(
        self,
        plan: ModuleVariablePlan,
    ) -> tuple[CFunctionPrototype, ...]:
        """Return getter/setter ABI declarations selected by the variable plan."""
        if plan.binding.getter_action is ModuleGetterAction.NATIVE_ARRAY_HANDLE:
            return self._module_native_array_bridge_prototypes(plan)
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

    def _module_native_array_bridge_prototypes(
        self,
        plan: ModuleVariablePlan,
    ) -> tuple[CFunctionPrototype, ...]:
        """Declare only bridge operations named by one borrowed handle plan."""
        handle = plan.native_array_handle
        if handle is None or handle.array.rank is None:
            raise ValueError(f"Module handle {plan.owner_path!r} has no operation plan")
        prototypes = []
        for operation in handle.operations:
            prototype = self._module_native_array_bridge_prototype(plan, operation)
            if prototype is not None:
                prototypes.append(prototype)
        return tuple(prototypes)

    def _module_native_array_bridge_prototype(
        self,
        plan: ModuleVariablePlan,
        operation: NativeArrayOperation,
    ) -> CFunctionPrototype | None:
        """Return the native bridge prototype selected by one operation."""
        if operation in {
            NativeArrayOperation.NATIVE_BYTE_ORDER,
            NativeArrayOperation.ALIGNED,
            NativeArrayOperation.WRITEABLE,
            NativeArrayOperation.LAYOUT,
        }:
            return None
        if operation is NativeArrayOperation.TO_NUMPY:
            return self._module_native_array_extraction_prototype(plan)
        return self._module_native_array_required_bridge_prototype(plan, operation)

    def _module_native_array_extraction_prototype(
        self,
        plan: ModuleVariablePlan,
    ) -> CFunctionPrototype | None:
        """Declare a bridge extraction only for a planned detached snapshot."""
        handle = plan.native_array_handle
        if handle is None:
            raise ValueError(f"Module handle {plan.owner_path!r} has no operation plan")
        if handle.extraction_action is not NativeArrayExtractionAction.READ_ONLY_DETACHED_COPY:
            return None
        name = self._module_native_array_bridge_operation_name(plan, NativeArrayOperation.TO_NUMPY)
        return CFunctionPrototype(name, "void *")

    def _module_native_array_required_bridge_prototype(
        self,
        plan: ModuleVariablePlan,
        operation: NativeArrayOperation,
    ) -> CFunctionPrototype:
        """Declare one operation that must cross the native bridge."""
        name = self._module_native_array_bridge_operation_name(plan, operation)
        if operation in {
            NativeArrayOperation.ALLOCATED,
            NativeArrayOperation.ASSOCIATED,
            NativeArrayOperation.CONTIGUOUS,
        }:
            return CFunctionPrototype(name, "bool")
        if operation is NativeArrayOperation.ELEMENT_LENGTH:
            return CFunctionPrototype(name, "int64_t")
        if operation is NativeArrayOperation.ARRAY_ACTUAL:
            return CFunctionPrototype(name, "void *")
        if operation is NativeArrayOperation.SHAPE:
            return self._module_native_array_shape_prototype(plan, name, pointer=True)
        if operation is NativeArrayOperation.DESCRIPTOR:
            return self._module_native_array_descriptor_prototype(plan, name)
        if operation in {NativeArrayOperation.ALLOCATE, NativeArrayOperation.RESIZE}:
            return self._module_native_array_shape_prototype(plan, name, pointer=False)
        if operation in {NativeArrayOperation.DEALLOCATE, NativeArrayOperation.NULLIFY}:
            return CFunctionPrototype(name, "void")
        raise ValueError(f"Unsupported module native array operation for {plan.owner_path!r}: {operation!r}")

    def _module_native_array_shape_prototype(
        self,
        plan: ModuleVariablePlan,
        name: str,
        *,
        pointer: bool,
    ) -> CFunctionPrototype:
        """Return one rank-specific shape query or mutation prototype."""
        handle = plan.native_array_handle
        if handle is None or handle.array.rank is None:
            raise ValueError(f"Module handle {plan.owner_path!r} has no rank")
        suffix = " *" if pointer else ""
        return CFunctionPrototype(
            name,
            "void",
            tuple(CParameter(f"extent_{axis}", f"int64_t{suffix}") for axis in range(handle.array.rank)),
        )

    def _module_native_array_descriptor_prototype(
        self,
        plan: ModuleVariablePlan,
        name: str,
    ) -> CFunctionPrototype | None:
        """Return the pointer-only standard-descriptor reader prototype."""
        handle = plan.native_array_handle
        if handle is None or handle.descriptor_kind is not NativeArrayDescriptorKind.POINTER:
            return None
        return CFunctionPrototype(name, "void", (CParameter("descriptor", "CFI_cdesc_t *"),))

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
                    function.binding.python_name,
                    self._binding_function_name(function),
                    "METH_VARARGS | METH_KEYWORDS",
                    function.binding.docstring,
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
            *self._module_native_array_owner_nodes(namespace, object_name),
            *self._module_initializer_nodes(namespace),
            *self._module_constant_nodes(namespace, object_name),
        )

    def _module_native_array_owner_nodes(
        self,
        namespace: NamespacePlan,
        module_object: str,
    ) -> tuple[CExpressionStatement, ...]:
        """Retain the owning Python module for every borrowed native handle."""
        nodes = []
        for variable in namespace.variables:
            if variable.binding.getter_action is not ModuleGetterAction.NATIVE_ARRAY_HANDLE:
                continue
            owner = self._module_native_array_owner_name(variable)
            nodes.extend(
                (
                    CExpressionStatement(CodeExpression(f"Py_INCREF({module_object})")),
                    CExpressionStatement(CodeExpression(f"{owner} = {module_object}")),
                )
            )
        return tuple(nodes)

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

    # Scalar module-literal lowering.
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
