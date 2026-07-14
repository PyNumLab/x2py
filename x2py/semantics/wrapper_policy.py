"""Completed wrapper policies for the currently supported generation lanes."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from enum import Enum
from typing import Any

from x2py.semantics import models
from x2py.semantics.metadata import ADDRESS_ROLE_METADATA, ADDRESS_ROLE_RAW
from x2py.semantics.native_array_handles import (
    NATIVE_ARRAY_POINTER_C_DESCRIPTOR_HEADER,
    NativeArrayHandlePolicy as CompletedNativeArrayHandlePolicy,
    native_array_descriptor_kind,
)
from x2py.semantics.wrapper_exports import PythonExportPolicy, completed_python_exports
from x2py.semantics.ownership import (
    AssignmentMode,
    CodegenAction,
    DestructionPolicy,
    NativeBarrierAction,
    ObjectKind,
    OwnershipDecision,
    OwnershipOwner,
    PythonBarrierAction,
    SetterAction,
    StorageMode,
    TransferMode,
)


_PLAN_PRIMITIVE_SCALAR_TYPES = frozenset(
    {
        "Bool",
        "Int8",
        "Int16",
        "Int32",
        "Int64",
        "Float32",
        "Float64",
        "Complex64",
        "Complex128",
    }
)

_NUMPY_DTYPE_NAMES = {
    "Bool": "bool",
    "Int8": "int8",
    "Int16": "int16",
    "Int32": "int32",
    "Int64": "int64",
    "Float32": "float32",
    "Float64": "float64",
    "Complex64": "complex64",
    "Complex128": "complex128",
}

FIXED_STRING_RESULT_COPY_REASON = "copy fixed-length Fortran character output into C-owned null-terminated storage"
ORDINARY_ARRAY_RESULT_COPY_REASON = "copy non-descriptor Fortran array output into C-owned contiguous storage"
OWNED_NATIVE_ARRAY_HANDLE_COPY_REASON = (
    "materialize native allocatable descriptor into persistent wrapper-owned CFI storage"
)
SCALAR_DESCRIPTOR_RESULT_COPY_REASON = (
    "copy a present rank-zero native descriptor value before releasing call-local descriptor storage"
)
STRING_INPUT_COPY_REASON = "materialize Fortran character storage from the binding UTF-8 byte buffer"
STRING_REPLACEMENT_COPY_REASON = (
    "materialize mutable Fortran character storage and copy post-call bytes back to binding storage"
)
STRING_STORAGE_COPY_REASON = (
    "materialize fixed-length Fortran character storage from caller-owned NumPy bytes and copy mutation back"
)
RAW_STRING_ADDRESS_COPY_REASON = (
    "materialize fixed-length Fortran character storage from a caller-supplied raw address and copy mutation back"
)


class OptionalMode(str, Enum):
    """Completed ABI behavior for one argument's presence states."""

    REQUIRED = "required"
    REQUIRED_DESCRIPTOR = "required_descriptor"
    NULLABLE_VALUE = "nullable_value"
    DESCRIPTOR = "descriptor"


class ArgumentHandoffMode(str, Enum):
    """Completed binding-to-bridge ABI shape for one argument."""

    VALUE = "value"
    TYPED_REFERENCE = "typed_reference"
    OPAQUE_ADDRESS = "opaque_address"
    CHARACTER_BUFFER = "character_buffer"
    ARRAY_BUFFER = "array_buffer"
    NATIVE_DESCRIPTOR = "native_descriptor"


class BridgeDataAction(str, Enum):
    """Completed bridge-side data movement for one boundary value."""

    DIRECT_TRANSFER = "direct_transfer"
    ASSOCIATE_VIEW = "associate_view"
    COPY_REPRESENTATION = "copy_representation"
    BLOCKED = "blocked"


class WritebackPhase(str, Enum):
    """Ordered phases of one completed replacement writeback."""

    COPY_IN = "copy_in"
    NATIVE_MUTATION = "native_mutation"
    COPY_OUT = "copy_out"
    CLEANUP = "cleanup"


class TransformationLayer(str, Enum):
    """Backend layer that owns one complete representation transformation."""

    BINDING = "binding"
    BRIDGE = "bridge"


class TransformationAction(str, Enum):
    """Typed representation or lifecycle operation selected before planning."""

    COPY_ARRAY_REPRESENTATION = "copy_array_representation"
    RELEASE_TEMPORARY = "release_temporary"


class ModuleGetterAction(str, Enum):
    """Completed Python-visible read behavior for a module variable."""

    CONSTANT_VALUE = "constant_value"
    DIRECT_VALUE = "direct_value"
    NULLABLE_SNAPSHOT = "nullable_snapshot"
    NATIVE_ARRAY_HANDLE = "native_array_handle"


class NativeArrayDescriptorKind(str, Enum):
    """Public native descriptor family."""

    ALLOCATABLE = "allocatable"
    POINTER = "pointer"


class NativeArrayHandleKind(str, Enum):
    """Completed native handle owner/use category."""

    ARGUMENT_DESCRIPTOR = "argument_descriptor"
    OPTIONAL_ABSENT_HANDLE = "optional_absent_handle"
    BORROWED_MODULE_DESCRIPTOR = "borrowed_module_descriptor"
    BORROWED_FIELD_DESCRIPTOR = "borrowed_field_descriptor"
    OWNED_RESULT_DESCRIPTOR = "owned_result_descriptor"


class NativeDescriptorHandoffABI(str, Enum):
    """Binding-to-bridge descriptor representation."""

    FACT_PACKED_CALL_LOCAL = "fact_packed_call_local"
    DIRECT_STANDARD_DESCRIPTOR = "direct_standard_descriptor"
    OWNED_RESULT_STORAGE = "owned_result_storage"


class NativeArraySourceKind(str, Enum):
    """Python runtime sources accepted by an ordinary array argument."""

    NDARRAY = "ndarray"
    ALLOCATABLE_HANDLE = "allocatable_handle"
    POINTER_HANDLE = "pointer_handle"


class NativeArrayHandleOrigin(str, Enum):
    """Completed source owner for a native handle."""

    ARGUMENT = "argument"
    PROJECTED_RESULT = "projected_result"
    RESULT = "result"
    MODULE_VARIABLE = "module_variable"
    DERIVED_FIELD = "derived_field"


class NativeArrayOwnerRetention(str, Enum):
    """Python owner retained by a runtime handle."""

    CALLER_HANDLE = "caller_handle"
    OPTIONAL_ARGUMENT = "optional_argument"
    NATIVE_MODULE = "native_module"
    PARENT_WRAPPER = "parent_wrapper"
    WRAPPER_OWNER_STORAGE = "wrapper_owner_storage"


class NativeArrayDescriptorOwnership(str, Enum):
    """Ownership of persistent standard-descriptor storage."""

    BORROWED = "borrowed"
    OWNED = "owned"


class NativeArrayGetterBehavior(str, Enum):
    """Python getter behavior for a handle owner."""

    NONE = "none"
    HANDLE = "handle"
    RETURN_HANDLE = "return_handle"


class NativeArrayOutputProjection(str, Enum):
    """Result identity/materialization selected for a handle."""

    NONE = "none"
    PROJECTED_HANDLE = "projected_handle"
    HANDLE_RESULT = "handle_result"


class NativeArrayRelease(str, Enum):
    """Completed release owner for descriptor storage."""

    NONE = "none"
    NATIVE_OWNER = "native_owner"
    WRAPPER_DEALLOC = "wrapper_dealloc"


class NativeArrayDestroyBehavior(str, Enum):
    """Runtime destruction behavior for a handle."""

    NONE = "none"
    HANDLE_FINALIZER = "handle_finalizer"
    PARENT_WRAPPER_FINALIZER = "parent_wrapper_finalizer"


class NativeArrayExtractionAction(str, Enum):
    """Completed `.to_numpy()` behavior."""

    BORROWED_VIEW = "borrowed_view"
    READ_ONLY_DETACHED_COPY = "read_only_detached_copy"
    CONTIGUOUS_VIEW = "contiguous_view"
    DESCRIPTOR_VIEW = "descriptor_view"
    COPY_ONLY = "copy_only"
    UNSUPPORTED = "unsupported"


class NativeArrayDescriptorInterop(str, Enum):
    """Standard C descriptor requirement."""

    NONE = "none"
    POINTER_C_DESCRIPTOR = "pointer_c_descriptor"
    OWNED_ALLOCATABLE_C_DESCRIPTOR = "owned_allocatable_c_descriptor"


class NativeArrayOperation(str, Enum):
    """Generated runtime operation supported by one handle."""

    ALLOCATED = "allocated"
    ASSOCIATED = "associated"
    SHAPE = "shape"
    ELEMENT_LENGTH = "element_length"
    ARRAY_ACTUAL = "array_actual"
    DESCRIPTOR = "descriptor"
    TO_NUMPY = "to_numpy"
    NATIVE_BYTE_ORDER = "native_byte_order"
    ALIGNED = "aligned"
    WRITEABLE = "writeable"
    LAYOUT = "layout"
    CONTIGUOUS = "contiguous"
    ALLOCATE = "allocate"
    DEALLOCATE = "deallocate"
    RESIZE = "resize"
    NULLIFY = "nullify"
    DESTROY = "destroy"


class PythonExceptionKind(str, Enum):
    """Completed Python exception selected for one native failure policy."""

    RUNTIME_ERROR = "RuntimeError"


@dataclass(frozen=True)
class NativeStatusOutputPolicy:
    """One validated native output consumed by status-error handling."""

    owner_path: str
    name: str
    native_name: str
    native_position: int
    result_position: int
    semantic_type_name: str
    rank: int
    character_length: int | None = None


@dataclass(frozen=True)
class NativeStatusErrorPolicy:
    """Completed native-status decision owned by post-IR policy completion."""

    status: NativeStatusOutputPolicy
    message: NativeStatusOutputPolicy | None
    success: int
    exception_kind: PythonExceptionKind


@dataclass(frozen=True)
class ModuleVariablePolicy:
    """Completed module-variable behavior before wrapper planning."""

    owner_path: str
    name: str
    python_exports: tuple[PythonExportPolicy, ...]
    native_name: str
    native_module: str
    semantic_type_name: str
    rank: int
    getter_action: ModuleGetterAction
    getter: OwnershipDecision | None
    setter_action: SetterAction
    native_assignment: AssignmentMode
    setter: OwnershipDecision | None
    descriptor_kind: str | None
    initializer: Any
    constant_value: Any
    supported: bool
    blockers: tuple[str, ...] = ()
    native_array_handle: NativeArrayHandleWrapperPolicy | None = None


@dataclass(frozen=True)
class LifecyclePolicy:
    """One completed writeback or cleanup action."""

    owner_path: str
    phase: WritebackPhase
    source_role: str
    codegen_action: CodegenAction
    semantic_type_name: str
    result_position: int
    object_kind: ObjectKind


@dataclass(frozen=True)
class ArrayHandoffPolicy:
    """Completed array storage or raw-pointee layout facts."""

    rank: int | None
    shape: tuple[str, ...]
    axes: tuple[str, ...]
    order: str | None
    native_order: str | None
    contiguous: bool | None
    itemsize: int | None = None
    category: str | None = None
    extent_references: tuple[tuple[str, ...], ...] = ()


@dataclass(frozen=True)
class TransformationPolicy:
    """One layer-owned transformation subordinate to a transfer policy."""

    phase: WritebackPhase
    layer: TransformationLayer
    action: TransformationAction
    source_representation: str
    target_representation: str
    reason: str


@dataclass(frozen=True)
class NativeArrayActualPolicy:
    """Completed accepted-source and validation facts for an ordinary array."""

    accepted_sources: tuple[NativeArraySourceKind, ...]
    dtype: str
    rank: int
    shape: tuple[str, ...]
    order: str | None
    writable: bool
    require_native_byte_order: bool
    require_aligned: bool
    require_contiguous: bool


@dataclass(frozen=True)
class NativeDescriptorHandoffPolicy:
    """Completed descriptor ABI form subordinate to one handle policy."""

    abi: NativeDescriptorHandoffABI
    rank: int
    optional_presence: bool


@dataclass(frozen=True)
class NativeArrayHandleWrapperPolicy:
    """Typed wrapper-facing projection of completed native handle policy."""

    descriptor_kind: NativeArrayDescriptorKind
    handle_kind: NativeArrayHandleKind
    origin: NativeArrayHandleOrigin
    owner: OwnershipOwner
    owner_retention: NativeArrayOwnerRetention
    descriptor_ownership: NativeArrayDescriptorOwnership
    borrowed: bool
    getter_behavior: NativeArrayGetterBehavior
    setter_action: SetterAction
    native_assignment: AssignmentMode
    output_projection: NativeArrayOutputProjection
    release: NativeArrayRelease
    target_lifetime: str
    destroy_behavior: NativeArrayDestroyBehavior
    extraction_action: NativeArrayExtractionAction
    descriptor_interop: NativeArrayDescriptorInterop
    nullable: bool
    optional_absent: bool
    storage_mode: StorageMode
    operations: tuple[NativeArrayOperation, ...]
    required_headers: tuple[str, ...]
    array: ArrayHandoffPolicy
    handoff: NativeDescriptorHandoffPolicy


@dataclass(frozen=True)
class ScalarDescriptorResultPolicy:
    """Completed nullable rank-zero descriptor result copy contract."""

    descriptor_kind: NativeArrayDescriptorKind
    runtime_length: bool
    nullable: bool
    copy_reason: str
    release_owner: OwnershipOwner


@dataclass(frozen=True)
class ArgumentPolicy:
    """Completed wrapper policy for one Python-visible argument."""

    owner_path: str
    name: str
    python_name: str
    native_name: str
    python_position: int
    native_position: int
    semantic_type_name: str
    rank: int
    optional: bool
    optional_mode: OptionalMode
    handoff_mode: ArgumentHandoffMode
    bridge_data_action: BridgeDataAction
    bridge_copy_reason: str | None
    nullable: bool
    writable: bool
    descriptor_boundary: bool
    ownership: OwnershipDecision
    codegen_action: CodegenAction
    python_barrier_action: PythonBarrierAction
    native_barrier_action: NativeBarrierAction
    storage_mode: StorageMode
    boundary_storage_mode: StorageMode
    projects_result: bool
    python_visible: bool
    result_position: int | None
    character_length: int | None
    array: ArrayHandoffPolicy | None = None
    native_array_actual: NativeArrayActualPolicy | None = None
    native_array_handle: NativeArrayHandleWrapperPolicy | None = None
    transformations: tuple[TransformationPolicy, ...] = ()


@dataclass(frozen=True)
class ResultPolicy:
    """Completed wrapper policy for one native result."""

    owner_path: str
    semantic_type_name: str
    rank: int
    ownership: OwnershipDecision
    codegen_action: CodegenAction
    python_barrier_action: PythonBarrierAction
    native_barrier_action: NativeBarrierAction
    storage_mode: StorageMode
    boundary_storage_mode: StorageMode
    bridge_data_action: BridgeDataAction
    bridge_copy_reason: str | None
    character_length: int | None = None
    array: ArrayHandoffPolicy | None = None
    source_kind: str = "direct_return"
    native_name: str | None = None
    native_position: int | None = None
    result_position: int = 0
    native_array_handle: NativeArrayHandleWrapperPolicy | None = None
    scalar_descriptor: ScalarDescriptorResultPolicy | None = None
    transformations: tuple[TransformationPolicy, ...] = ()


@dataclass(frozen=True)
class NativeCallSlotPolicy:
    """Completed native-call slot consumed by wrapper planning.

    ``object_kind`` is copied from the owning transfer decision.  Literal slots
    have no transfer owner and therefore use ``None``.
    """

    owner_path: str
    native_position: int
    source_kind: str
    python_position: int | None
    python_name: str | None
    native_name: str
    value_kind: str
    native_barrier_action: NativeBarrierAction
    codegen_action: CodegenAction
    bridge_data_action: BridgeDataAction
    bridge_copy_reason: str | None
    object_kind: ObjectKind | None
    literal_type: str | None = None
    literal_value: Any = None
    result_position: int | None = None
    semantic_type_name: str | None = None
    character_length: int | None = None
    array: ArrayHandoffPolicy | None = None
    native_array_handle: NativeArrayHandleWrapperPolicy | None = None
    scalar_descriptor: ScalarDescriptorResultPolicy | None = None


@dataclass(frozen=True)
class FunctionWrapperPolicy:
    """Completed wrapper policy for one semantic function."""

    owner_path: str
    python_exports: tuple[PythonExportPolicy, ...]
    native_name: str
    external: bool
    native_module: str | None
    native_is_subroutine: bool
    hold_gil: bool
    status_error: NativeStatusErrorPolicy | None
    supported: bool
    arguments: tuple[ArgumentPolicy, ...] = ()
    results: tuple[ResultPolicy, ...] = ()
    native_call_slots: tuple[NativeCallSlotPolicy, ...] = ()
    blockers: tuple[str, ...] = ()
    writeback_actions: tuple[LifecyclePolicy, ...] = ()
    cleanup_actions: tuple[LifecyclePolicy, ...] = ()
    release_actions: tuple[LifecyclePolicy, ...] = ()


def completed_module_variable_policy(
    variable: models.SemanticVariable,
) -> ModuleVariablePolicy:
    """Return the completed module-variable policy or fail closed."""
    policy = variable.metadata.get(models.RESOLVED_MODULE_VARIABLE_POLICY_METADATA)
    if not isinstance(policy, ModuleVariablePolicy):
        raise ValueError(f"Semantic variable {variable.name!r} has no completed module-variable policy")
    if not policy.supported:
        details = "; ".join(policy.blockers)
        raise ValueError(f"Semantic variable {policy.owner_path!r} has blocked module-variable policy: {details}")
    return policy


def build_module_variable_policy(
    variable: models.SemanticVariable,
    *,
    module_name: str,
) -> ModuleVariablePolicy:
    """Build one module-variable policy from completed decisions."""
    owner_path = f"{module_name}.{variable.name}"
    getter = _ownership_decision(variable, models.RESOLVED_GETTER_OWNERSHIP_POLICY_METADATA)
    setter = _ownership_decision(variable, models.RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA)
    descriptor_kind = _scalar_module_descriptor_kind(variable)
    constant = _is_scalar_module_constant(variable)
    native_array_handle = _native_array_handle_wrapper_policy(
        variable.semantic_type,
        variable.metadata.get(models.RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA),
        owner_path,
    )
    if native_array_handle is not None:
        blockers = _native_array_module_variable_blockers(variable, getter, setter, native_array_handle)
        return ModuleVariablePolicy(
            owner_path=owner_path,
            name=variable.name,
            python_exports=completed_python_exports(variable, variable.name),
            native_name=str(variable.origin.native_name or variable.name),
            native_module=str(variable.origin.native_scope or module_name),
            semantic_type_name=variable.semantic_type.name,
            rank=int(variable.semantic_type.rank or 0),
            getter_action=ModuleGetterAction.NATIVE_ARRAY_HANDLE,
            getter=getter,
            setter_action=native_array_handle.setter_action,
            native_assignment=native_array_handle.native_assignment,
            setter=setter,
            descriptor_kind=native_array_handle.descriptor_kind.value,
            initializer=None,
            constant_value=None,
            supported=not blockers,
            blockers=tuple(blockers),
            native_array_handle=native_array_handle,
        )
    blockers = _scalar_module_variable_blockers(variable, getter, setter, descriptor_kind, constant)
    initializer = variable.metadata.get(models.RESOLVED_MODULE_VARIABLE_INITIALIZER_METADATA)
    return ModuleVariablePolicy(
        owner_path=owner_path,
        name=variable.name,
        python_exports=completed_python_exports(variable, variable.name),
        native_name=str(variable.origin.native_name or variable.name),
        native_module=str(variable.origin.native_scope or module_name),
        semantic_type_name=variable.semantic_type.name,
        rank=int(variable.semantic_type.rank or 0),
        getter_action=_scalar_module_getter_action(getter, constant),
        getter=getter,
        setter_action=setter.setter_action if setter is not None else SetterAction.OMIT,
        native_assignment=_scalar_module_native_assignment(setter),
        setter=setter,
        descriptor_kind=descriptor_kind,
        initializer=(
            _scalar_module_literal_value(initializer, variable.semantic_type.name) if initializer is not None else None
        ),
        constant_value=(
            _scalar_module_literal_value(variable.default_value, variable.semantic_type.name)
            if constant and variable.default_value is not None
            else None
        ),
        supported=not blockers,
        blockers=tuple(blockers),
    )


def completed_function_wrapper_policy(function: models.SemanticFunction) -> FunctionWrapperPolicy:
    """Return a completed function wrapper policy or fail before planning."""

    policy = function.metadata.get(models.RESOLVED_FUNCTION_WRAPPER_POLICY_METADATA)
    if not isinstance(policy, FunctionWrapperPolicy):
        raise ValueError(
            f"Semantic function {function.name!r} is missing completed wrapper policy; "
            "run complete_semantic_policies before wrapper planning"
        )
    if not policy.supported:
        details = "; ".join(policy.blockers) or "unsupported wrapper policy"
        raise ValueError(f"Semantic function {policy.owner_path!r} has blocked wrapper policy: {details}")
    return policy


def build_function_wrapper_policy(
    function: models.SemanticFunction,
    *,
    owner_path: str,
) -> FunctionWrapperPolicy:
    """Build typed function policy from completed post-IR decisions."""

    argument_native_positions, native_call_slots, slot_blockers = _native_call_slot_policies(function, owner_path)
    arguments, argument_blockers = _argument_policies(
        function,
        owner_path,
        argument_native_positions,
        native_call_slots,
    )
    results, result_blockers = _result_policies(function, owner_path)
    writeback_actions, lifecycle_blockers = _lifecycle_policies(arguments)
    status_error = _completed_native_status_error_policy(function)
    blockers = (
        _function_shape_blockers(function)
        + argument_blockers
        + result_blockers
        + slot_blockers
        + lifecycle_blockers
        + _array_extent_reference_blockers(function, arguments, results)
        + _runtime_status_plan_blockers(status_error)
        + _string_result_status_blockers(results, status_error)
        + _string_writeback_status_blockers(arguments, status_error)
    )
    return FunctionWrapperPolicy(
        owner_path=owner_path,
        python_exports=completed_python_exports(function, function.name),
        native_name=_native_name(function),
        external=_is_external(function),
        native_module=_native_module(function, owner_path),
        native_is_subroutine=_native_is_subroutine(function),
        hold_gil=bool(function.metadata.get(models.RUNTIME_HOLD_GIL_METADATA)),
        status_error=status_error,
        supported=not blockers,
        arguments=tuple(arguments),
        results=results,
        native_call_slots=tuple(native_call_slots),
        blockers=tuple(blockers),
        writeback_actions=writeback_actions,
    )


def _argument_policies(
    function: models.SemanticFunction,
    owner_path: str,
    argument_native_positions: dict[int, int],
    native_call_slots: tuple[NativeCallSlotPolicy, ...],
) -> tuple[list[ArgumentPolicy], tuple[str, ...]]:
    policies: list[ArgumentPolicy] = []
    blockers: list[str] = []
    python_position = 0
    for argument in function.arguments:
        decision = _ownership_decision(argument, models.RESOLVED_OWNERSHIP_POLICY_METADATA)
        if decision is None:
            blockers.append(f"argument {argument.name!r} is missing completed ownership policy")
            continue
        if decision.projects_result and not decision.python_visible:
            continue
        current_python_position = python_position
        python_position += 1
        native_position = argument_native_positions.get(current_python_position)
        native_slot = next(
            (slot for slot in native_call_slots if slot.python_position == current_python_position),
            None,
        )
        if native_position is None:
            blockers.append(f"argument {argument.name!r} has no completed native-call slot")
            native_position = -1
        optional_mode = _optional_mode(argument, decision)
        array_policy = _array_handoff_policy(argument.semantic_type)
        transformations, transformation_blockers = _argument_transformation_policies(
            argument,
            decision,
            array_policy,
        )
        native_array_handle = _native_array_handle_wrapper_policy(
            argument.semantic_type,
            argument.metadata.get(models.RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA),
            f"{owner_path}.{argument.name}",
        )
        bridge_data_action, bridge_copy_reason = _argument_bridge_data_action(
            decision,
            optional_mode,
            native_slot.value_kind if native_slot is not None else None,
        )
        blockers.extend(
            _argument_blockers(
                argument,
                decision,
                bridge_data_action,
                bridge_copy_reason,
            )
        )
        blockers.extend(transformation_blockers)
        policies.append(
            ArgumentPolicy(
                owner_path=f"{owner_path}.{argument.name}",
                name=argument.name,
                python_name=argument.name,
                native_name=_argument_native_name(function, current_python_position, argument),
                python_position=current_python_position,
                native_position=native_position,
                semantic_type_name=argument.semantic_type.name,
                rank=int(argument.semantic_type.rank or 0),
                optional=argument.optional,
                optional_mode=optional_mode,
                handoff_mode=_argument_handoff_mode(decision),
                bridge_data_action=bridge_data_action,
                bridge_copy_reason=bridge_copy_reason,
                nullable=decision.nullable,
                writable=decision.mutates_native,
                descriptor_boundary=decision.descriptor_boundary,
                ownership=decision,
                codegen_action=decision.codegen_action,
                python_barrier_action=decision.python_barrier_action,
                native_barrier_action=decision.native_barrier_action,
                storage_mode=decision.storage_mode,
                boundary_storage_mode=decision.boundary_storage_mode or decision.storage_mode,
                projects_result=decision.projects_result,
                python_visible=decision.python_visible,
                result_position=_argument_result_position(function, current_python_position),
                character_length=_character_length(argument.semantic_type),
                array=array_policy,
                native_array_actual=_native_array_actual_policy(argument, decision, array_policy),
                native_array_handle=native_array_handle,
                transformations=transformations,
            )
        )
    return policies, tuple(blockers)


def _result_policies(
    function: models.SemanticFunction,
    owner_path: str,
) -> tuple[tuple[ResultPolicy, ...], tuple[str, ...]]:
    """Return every ordered binding result consumer for one function."""
    hidden_candidates = _hidden_result_policies(function, owner_path)
    hidden_results = tuple(policy for policy, _blockers in hidden_candidates if policy is not None)
    hidden_blockers = tuple(reason for _policy, blockers in hidden_candidates for reason in blockers)
    if function.return_type is None:
        projected_arguments = _visible_projected_arguments(function)
        if hidden_results and not projected_arguments:
            return hidden_results, (
                *hidden_blockers,
                *_result_position_blockers(hidden_results),
                *_string_result_aggregation_blockers(hidden_results),
            )
        if projected_arguments and not hidden_results:
            return (), hidden_blockers
        if not hidden_results and not projected_arguments:
            return (), hidden_blockers
        return (), (*hidden_blockers, "scalar lane cannot combine binding results with argument writeback")

    decision = function.metadata.get(models.RESOLVED_RETURN_OWNERSHIP_POLICY_METADATA)
    if not isinstance(decision, OwnershipDecision):
        return (), (*hidden_blockers, "function result is missing completed ownership policy")
    direct_handle = _native_array_handle_wrapper_policy(
        function.return_type,
        function.metadata.get(models.RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA),
        f"{owner_path}.return",
    )
    scalar_descriptor = _scalar_descriptor_result_policy(function.return_type, decision)
    blockers = list(_result_blockers(function.return_type, decision))
    bridge_data_action, bridge_copy_reason = _result_bridge_data_action(function.return_type)
    if bridge_data_action is BridgeDataAction.BLOCKED and decision.kind is not ObjectKind.SCALAR:
        blockers.append("result has no completed bridge data action")
    direct_result = ResultPolicy(
        owner_path=f"{owner_path}.return",
        semantic_type_name=function.return_type.name,
        rank=int(function.return_type.rank or 0),
        ownership=decision,
        codegen_action=decision.codegen_action,
        python_barrier_action=decision.python_barrier_action,
        native_barrier_action=decision.native_barrier_action,
        storage_mode=decision.storage_mode,
        boundary_storage_mode=decision.boundary_storage_mode or decision.storage_mode,
        bridge_data_action=bridge_data_action,
        bridge_copy_reason=bridge_copy_reason,
        character_length=_character_length(function.return_type),
        array=_array_handoff_policy(function.return_type),
        native_array_handle=direct_handle,
        scalar_descriptor=scalar_descriptor,
    )
    results = (direct_result, *hidden_results)
    return (
        results,
        (
            *blockers,
            *hidden_blockers,
            *_result_position_blockers(results),
            *_string_result_aggregation_blockers(results),
        ),
    )


def _hidden_result_policies(
    function: models.SemanticFunction,
    owner_path: str,
) -> tuple[tuple[ResultPolicy | None, tuple[str, ...]], ...]:
    """Return completed policy candidates for hidden scalar output projections."""
    policies = []
    suppressed_outputs = _runtime_status_output_owner_paths(function)
    for argument in function.arguments:
        decision = _ownership_decision(argument, models.RESOLVED_OWNERSHIP_POLICY_METADATA)
        if decision is None or not (decision.projects_result and not decision.python_visible):
            continue
        if f"{owner_path}.{argument.name}" in suppressed_outputs:
            continue
        mapping = next(
            (
                item
                for item in function.projection
                if item.result_position is not None and item.python_name == argument.name
            ),
            None,
        )
        if mapping is None:
            policies.append((None, (f"hidden result {argument.name!r} has no completed return projection",)))
            continue
        blockers = _hidden_result_blockers(argument, decision, mapping)
        native_array_handle = _native_array_handle_wrapper_policy(
            argument.semantic_type,
            argument.metadata.get(models.RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA),
            f"{owner_path}.{argument.name}",
        )
        scalar_descriptor = _scalar_descriptor_result_policy(
            argument.semantic_type,
            decision,
            descriptor_kind=mapping.value_kind,
        )
        bridge_data_action, bridge_copy_reason = _result_bridge_data_action(
            argument.semantic_type,
            descriptor_kind=mapping.value_kind,
        )
        if bridge_data_action is BridgeDataAction.BLOCKED and decision.kind is not ObjectKind.SCALAR:
            blockers = (*blockers, f"hidden result {argument.name!r} has no completed bridge data action")
        policies.append(
            (
                ResultPolicy(
                    owner_path=f"{owner_path}.{argument.name}",
                    semantic_type_name=argument.semantic_type.name,
                    rank=int(argument.semantic_type.rank or 0),
                    ownership=decision,
                    codegen_action=decision.codegen_action,
                    python_barrier_action=decision.python_barrier_action,
                    native_barrier_action=decision.native_barrier_action,
                    storage_mode=decision.storage_mode,
                    boundary_storage_mode=decision.boundary_storage_mode or decision.storage_mode,
                    bridge_data_action=bridge_data_action,
                    bridge_copy_reason=bridge_copy_reason,
                    character_length=_character_length(argument.semantic_type),
                    array=_array_handoff_policy(argument.semantic_type),
                    source_kind="hidden_output",
                    native_name=mapping.native_name or argument.name,
                    native_position=mapping.native_position,
                    result_position=int(mapping.result_position),
                    native_array_handle=native_array_handle,
                    scalar_descriptor=scalar_descriptor,
                ),
                tuple(blockers),
            )
        )
    return tuple(policies)


def _native_call_slot_policies(
    function: models.SemanticFunction,
    owner_path: str,
) -> tuple[dict[int, int], tuple[NativeCallSlotPolicy, ...], tuple[str, ...]]:
    if function.projection:
        return _projected_native_call_slot_policies(function, owner_path)
    return _implicit_native_call_slot_policies(function, owner_path)


def _projected_native_call_slot_policies(
    function: models.SemanticFunction,
    owner_path: str,
) -> tuple[dict[int, int], tuple[NativeCallSlotPolicy, ...], tuple[str, ...]]:
    slots: list[NativeCallSlotPolicy] = []
    blockers: list[str] = []
    positions: dict[int, int] = {}
    visible_arguments = tuple(
        argument
        for argument in function.arguments
        if (
            (decision := _ownership_decision(argument, models.RESOLVED_OWNERSHIP_POLICY_METADATA)) is not None
            and decision.python_visible
        )
    )
    for mapping in sorted(
        function.projection, key=lambda item: item.native_position if item.native_position is not None else -1
    ):
        native_position = mapping.native_position
        python_position = mapping.python_position
        if not isinstance(native_position, int):
            blockers.append("native-call projection is missing a native position")
            continue
        if mapping.value_kind == "literal":
            slot, slot_blockers = _literal_native_call_slot_policy(mapping, owner_path, native_position)
            slots.append(slot)
            blockers.extend(slot_blockers)
            continue
        if mapping.result_position is not None and python_position is None:
            slot, slot_blockers = _hidden_result_native_call_slot_policy(
                function,
                mapping,
                owner_path,
                native_position,
            )
            slots.append(slot)
            blockers.extend(slot_blockers)
            continue
        if python_position is None:
            blockers.append(f"native-call slot {native_position} is not a first-lane Python argument projection")
            continue
        if not 0 <= python_position < len(visible_arguments):
            blockers.append(f"native-call slot {native_position} references argument position {python_position}")
            continue
        argument = visible_arguments[python_position]
        decision = _ownership_decision(argument, models.RESOLVED_OWNERSHIP_POLICY_METADATA)
        if decision is None:
            blockers.append(f"native-call slot {native_position} references argument without completed policy")
            continue
        value_kind = _native_argument_value_kind(argument, mapping.value_kind or "arg")
        if value_kind not in {"addr", "allocatable", "arg", "pointer"}:
            blockers.append(f"native-call slot {native_position} uses unsupported scalar value kind {value_kind!r}")
        if python_position in positions:
            blockers.append(f"argument {argument.name!r} appears in more than one native-call slot")
        positions[python_position] = native_position
        bridge_data_action, bridge_copy_reason = _argument_bridge_data_action(
            decision,
            _optional_mode(argument, decision),
            value_kind,
        )
        if bridge_data_action is BridgeDataAction.BLOCKED:
            blockers.append(f"native-call slot {native_position} has no completed bridge data action")
        slots.append(
            NativeCallSlotPolicy(
                owner_path=f"{owner_path}.{argument.name}",
                native_position=native_position,
                source_kind="projection",
                python_position=python_position,
                python_name=mapping.python_name or argument.name,
                native_name=mapping.native_name or argument.name,
                value_kind=value_kind,
                native_barrier_action=decision.native_barrier_action,
                codegen_action=decision.codegen_action,
                bridge_data_action=bridge_data_action,
                bridge_copy_reason=bridge_copy_reason,
                object_kind=decision.kind,
                result_position=mapping.result_position,
                semantic_type_name=argument.semantic_type.name,
                character_length=_character_length(argument.semantic_type),
                array=_array_handoff_policy(argument.semantic_type),
                native_array_handle=_native_array_handle_wrapper_policy(
                    argument.semantic_type,
                    argument.metadata.get(models.RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA),
                    f"{owner_path}.{argument.name}",
                ),
            )
        )
    blockers.extend(_native_position_blockers(slot.native_position for slot in slots))
    return positions, tuple(slots), tuple(blockers)


def _hidden_result_native_call_slot_policy(
    function: models.SemanticFunction,
    mapping: models.ProjectionMapping,
    owner_path: str,
    native_position: int,
) -> tuple[NativeCallSlotPolicy, tuple[str, ...]]:
    """Return one native slot for a hidden scalar `Return(...)` projection."""
    argument = next((item for item in function.arguments if item.name == mapping.python_name), None)
    if argument is None:
        return (
            NativeCallSlotPolicy(
                owner_path=f"{owner_path}.native_slot_{native_position}",
                native_position=native_position,
                source_kind="result",
                python_position=None,
                python_name=mapping.python_name,
                native_name=mapping.native_name or f"result_{native_position}",
                value_kind=mapping.value_kind,
                native_barrier_action=NativeBarrierAction.BLOCKED,
                codegen_action=CodegenAction.BLOCKED,
                bridge_data_action=BridgeDataAction.BLOCKED,
                bridge_copy_reason=None,
                object_kind=None,
                result_position=mapping.result_position,
            ),
            (f"native-call result slot {native_position} has no hidden argument {mapping.python_name!r}",),
        )
    decision = _ownership_decision(argument, models.RESOLVED_OWNERSHIP_POLICY_METADATA)
    if decision is None:
        return (
            NativeCallSlotPolicy(
                owner_path=f"{owner_path}.{argument.name}",
                native_position=native_position,
                source_kind="result",
                python_position=None,
                python_name=argument.name,
                native_name=mapping.native_name or argument.name,
                value_kind=mapping.value_kind,
                native_barrier_action=NativeBarrierAction.BLOCKED,
                codegen_action=CodegenAction.BLOCKED,
                bridge_data_action=BridgeDataAction.BLOCKED,
                bridge_copy_reason=None,
                object_kind=None,
                result_position=mapping.result_position,
                semantic_type_name=argument.semantic_type.name,
                character_length=_character_length(argument.semantic_type),
                array=_array_handoff_policy(argument.semantic_type),
                native_array_handle=_native_array_handle_wrapper_policy(
                    argument.semantic_type,
                    argument.metadata.get(models.RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA),
                    f"{owner_path}.{argument.name}",
                ),
            ),
            (f"native-call result slot {native_position} references argument without completed policy",),
        )
    bridge_data_action, bridge_copy_reason = _native_result_bridge_data_action(
        argument.semantic_type,
        descriptor_kind=mapping.value_kind,
    )
    blockers = (
        (f"native-call result slot {native_position} has no completed bridge data action",)
        if bridge_data_action is BridgeDataAction.BLOCKED
        else ()
    )
    return (
        NativeCallSlotPolicy(
            owner_path=f"{owner_path}.{argument.name}",
            native_position=native_position,
            source_kind="result",
            python_position=None,
            python_name=argument.name,
            native_name=mapping.native_name or argument.name,
            value_kind=mapping.value_kind,
            native_barrier_action=decision.native_barrier_action,
            codegen_action=decision.codegen_action,
            bridge_data_action=bridge_data_action,
            bridge_copy_reason=bridge_copy_reason,
            object_kind=decision.kind,
            result_position=mapping.result_position,
            semantic_type_name=argument.semantic_type.name,
            character_length=_character_length(argument.semantic_type),
            array=_array_handoff_policy(argument.semantic_type),
            native_array_handle=_native_array_handle_wrapper_policy(
                argument.semantic_type,
                argument.metadata.get(models.RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA),
                f"{owner_path}.{argument.name}",
            ),
            scalar_descriptor=_scalar_descriptor_result_policy(
                argument.semantic_type,
                decision,
                descriptor_kind=mapping.value_kind,
            ),
        ),
        blockers,
    )


def _literal_native_call_slot_policy(
    mapping: models.ProjectionMapping,
    owner_path: str,
    native_position: int,
) -> tuple[NativeCallSlotPolicy, tuple[str, ...]]:
    """Return a completed hidden literal slot and any first-lane blockers."""
    literal_type, literal_value, blockers = _literal_projection_value(mapping, native_position)
    return (
        NativeCallSlotPolicy(
            owner_path=f"{owner_path}.native_slot_{native_position}",
            native_position=native_position,
            source_kind="literal",
            python_position=None,
            python_name=None,
            native_name=mapping.native_name or f"literal_{native_position}",
            value_kind="literal",
            native_barrier_action=NativeBarrierAction.PASS_VALUE,
            codegen_action=CodegenAction.DIRECT_VALUE,
            bridge_data_action=BridgeDataAction.DIRECT_TRANSFER,
            bridge_copy_reason=None,
            object_kind=None,
            literal_type=literal_type,
            literal_value=literal_value,
            semantic_type_name=literal_type,
        ),
        tuple(blockers),
    )


def _literal_projection_value(
    mapping: models.ProjectionMapping,
    native_position: int,
) -> tuple[str | None, object, list[str]]:
    """Return literal type/value details for one projection mapping."""
    value = mapping.value
    if not isinstance(value, dict):
        return None, None, [f"native-call literal slot {native_position} is missing typed literal metadata"]
    literal_type = value.get("type")
    literal_value = value.get("value")
    blockers = []
    if not isinstance(literal_type, str):
        blockers.append(f"native-call literal slot {native_position} is missing a literal type")
    elif not _is_first_lane_literal_type(literal_type):
        blockers.append(
            f"native-call literal slot {native_position} uses unsupported first-lane literal type {literal_type!r}"
        )
    return literal_type if isinstance(literal_type, str) else None, literal_value, blockers


def _implicit_native_call_slot_policies(
    function: models.SemanticFunction,
    owner_path: str,
) -> tuple[dict[int, int], tuple[NativeCallSlotPolicy, ...], tuple[str, ...]]:
    slots: list[NativeCallSlotPolicy] = []
    positions: dict[int, int] = {}
    blockers: list[str] = []
    for position, argument in enumerate(function.arguments):
        decision = _ownership_decision(argument, models.RESOLVED_OWNERSHIP_POLICY_METADATA)
        if decision is None:
            blockers.append(f"implicit native-call slot {position} references argument without completed policy")
            continue
        value_kind = _native_argument_value_kind(argument, "arg")
        bridge_data_action, bridge_copy_reason = _argument_bridge_data_action(
            decision,
            _optional_mode(argument, decision),
            value_kind,
        )
        if bridge_data_action is BridgeDataAction.BLOCKED:
            blockers.append(f"implicit native-call slot {position} has no completed bridge data action")
        positions[position] = position
        slots.append(
            NativeCallSlotPolicy(
                owner_path=f"{owner_path}.{argument.name}",
                native_position=position,
                source_kind="implicit",
                python_position=position,
                python_name=argument.name,
                native_name=argument.name,
                value_kind=value_kind,
                native_barrier_action=decision.native_barrier_action,
                codegen_action=decision.codegen_action,
                bridge_data_action=bridge_data_action,
                bridge_copy_reason=bridge_copy_reason,
                object_kind=decision.kind,
                semantic_type_name=argument.semantic_type.name,
                character_length=_character_length(argument.semantic_type),
                array=_array_handoff_policy(argument.semantic_type),
                native_array_handle=_native_array_handle_wrapper_policy(
                    argument.semantic_type,
                    argument.metadata.get(models.RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA),
                    f"{owner_path}.{argument.name}",
                ),
            )
        )
    return positions, tuple(slots), tuple(blockers)


def _native_argument_value_kind(argument: models.SemanticArgument, default: str) -> str:
    """Project descriptor kind into the native slot before wrapper lowering."""
    return native_array_descriptor_kind(argument.semantic_type) or default


def _argument_blockers(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
    bridge_data_action: BridgeDataAction,
    bridge_copy_reason: str | None,
) -> tuple[str, ...]:
    """Return datatype-family blockers without reconstructing policy in a backend."""
    return (
        *_argument_shape_blockers(argument, decision),
        *_argument_boundary_blockers(argument, decision),
        *_argument_bridge_data_blockers(argument, bridge_data_action, bridge_copy_reason),
        *_argument_projection_blockers(argument, decision),
    )


def _argument_shape_blockers(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
) -> tuple[str, ...]:
    """Dispatch one argument to its scalar/string or array policy family."""
    if int(argument.semantic_type.rank or 0) > 0:
        return _array_argument_shape_blockers(argument, decision)
    return _scalar_or_string_argument_shape_blockers(argument, decision)


# Scalar and rank-zero string argument policy.
def _scalar_or_string_argument_shape_blockers(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
) -> tuple[str, ...]:
    """Return ownership, type, and visibility blockers for one rank-zero argument."""
    blockers: list[str] = []
    if decision.is_blocked:
        blockers.append(
            f"argument {argument.name!r} has blocked ownership policy: {decision.blocker or decision.reason}"
        )
    string_value = _is_plan_string_value_type(argument.semantic_type)
    if not (_is_first_lane_scalar_type(argument.semantic_type) or string_value):
        blockers.append(f"argument {argument.name!r} is not a first-lane primitive scalar")
    if not decision.python_visible:
        blockers.append(f"argument {argument.name!r} is not Python-visible")
    expected_kind = ObjectKind.STRING if string_value else ObjectKind.SCALAR
    if decision.kind is not expected_kind:
        blockers.append(f"argument {argument.name!r} policy kind is {decision.kind.value}, not {expected_kind.value}")
    return tuple(blockers)


# Ordinary-array argument policy.
def _array_argument_shape_blockers(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
) -> tuple[str, ...]:
    """Require one supported non-descriptor array boundary."""
    blockers: list[str] = []
    if decision.is_blocked:
        blockers.append(
            f"argument {argument.name!r} has blocked ownership policy: {decision.blocker or decision.reason}"
        )
    descriptor_kind = native_array_descriptor_kind(argument.semantic_type)
    if descriptor_kind is not None:
        completed_handle = argument.metadata.get(models.RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA)
        if not isinstance(completed_handle, CompletedNativeArrayHandlePolicy):
            blockers.append(f"argument {argument.name!r} is missing completed native array handle policy")
        elif completed_handle.is_blocked:
            blockers.append(
                f"argument {argument.name!r} has blocked native array handle policy: {completed_handle.blocker}"
            )
    elif decision.python_barrier_action is PythonBarrierAction.RAW_ADDRESS:
        if not _is_phase6_raw_array_address_type(argument.semantic_type):
            blockers.append(f"argument {argument.name!r} is outside raw array address support")
    elif not _is_phase6_ordinary_array_type(argument.semantic_type):
        blockers.append(f"argument {argument.name!r} is outside ordinary array buffer support")
    if not decision.python_visible:
        blockers.append(f"argument {argument.name!r} is not Python-visible")
    if decision.kind is not ObjectKind.NUMPY_ARRAY:
        blockers.append(f"argument {argument.name!r} policy kind is {decision.kind.value}, not numpy_array")
    return tuple(blockers)


def _argument_boundary_blockers(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
) -> tuple[str, ...]:
    """Return Python/native boundary-action blockers for one argument."""
    if decision.kind is ObjectKind.STRING:
        return _string_boundary_blockers(argument, decision)
    if decision.kind is ObjectKind.NUMPY_ARRAY:
        return _array_boundary_blockers(argument, decision)
    return _scalar_boundary_blockers(argument, decision)


def _scalar_boundary_blockers(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
) -> tuple[str, ...]:
    """Validate one completed scalar value, storage, or address boundary."""
    blockers: list[str] = []
    if decision.python_barrier_action not in {
        PythonBarrierAction.SCALAR_VALUE,
        PythonBarrierAction.SCALAR_STORAGE,
        PythonBarrierAction.RAW_ADDRESS,
    }:
        blockers.append(
            f"argument {argument.name!r} has unsupported scalar Python action {decision.python_barrier_action.value}"
        )
    if decision.native_barrier_action not in {
        NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS,
        NativeBarrierAction.PASS_RAW_ADDRESS,
        NativeBarrierAction.PASS_STORAGE_ADDRESS,
        NativeBarrierAction.PASS_VALUE,
    }:
        blockers.append(
            f"argument {argument.name!r} native action is {decision.native_barrier_action.value}, "
            "not a supported scalar handoff"
        )
    if (
        decision.python_barrier_action is PythonBarrierAction.SCALAR_STORAGE
        and decision.native_barrier_action is not NativeBarrierAction.PASS_STORAGE_ADDRESS
    ):
        blockers.append(f"argument {argument.name!r} scalar storage does not use its storage address")
    if (
        decision.python_barrier_action is PythonBarrierAction.RAW_ADDRESS
        and decision.native_barrier_action is not NativeBarrierAction.PASS_RAW_ADDRESS
    ):
        blockers.append(f"argument {argument.name!r} raw address is not forwarded as a raw address")
    if argument.optional and decision.python_barrier_action is not PythonBarrierAction.SCALAR_VALUE:
        blockers.append(f"argument {argument.name!r} optional storage/address boundaries are not supported")
    return tuple(blockers)


# Ordinary-array boundary policy.
def _array_boundary_blockers(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
) -> tuple[str, ...]:
    """Dispatch one completed array boundary without backend inference."""
    action = decision.python_barrier_action
    if action is PythonBarrierAction.ARRAY_STORAGE:
        return _array_storage_boundary_blockers(argument, decision)
    if action is PythonBarrierAction.RAW_ADDRESS:
        return _raw_array_address_boundary_blockers(argument, decision)
    if action is PythonBarrierAction.WRAPPER_INSTANCE:
        return _native_array_handle_boundary_blockers(argument, decision)
    return (f"argument {argument.name!r} has unsupported array Python action {action.value}",)


def _array_storage_boundary_blockers(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
) -> tuple[str, ...]:
    """Require one caller-owned ordinary NumPy buffer handoff."""
    blockers = []
    if decision.owner is not OwnershipOwner.CALLER:
        blockers.append(f"argument {argument.name!r} array owner is {decision.owner.value}, not caller")
    expected_transfer = TransferMode.IN_PLACE if decision.mutates_native else TransferMode.CALL_LOCAL
    if decision.transfer is not expected_transfer:
        blockers.append(
            f"argument {argument.name!r} array transfer is {decision.transfer.value}, not {expected_transfer.value}"
        )
    expected_destruction = DestructionPolicy.CALLER if decision.mutates_native else DestructionPolicy.NONE
    if decision.destruction is not expected_destruction:
        blockers.append(
            f"argument {argument.name!r} array destruction is {decision.destruction.value}, "
            f"not {expected_destruction.value}"
        )
    if decision.storage_mode is not StorageMode.STACK:
        blockers.append(f"argument {argument.name!r} array storage is {decision.storage_mode.value}, not stack")
    if (decision.boundary_storage_mode or decision.storage_mode) is not StorageMode.STACK:
        blockers.append(f"argument {argument.name!r} array boundary storage is not stack")
    if decision.python_barrier_action is not PythonBarrierAction.ARRAY_STORAGE:
        blockers.append(
            f"argument {argument.name!r} array Python action is "
            f"{decision.python_barrier_action.value}, not array_storage"
        )
    if decision.native_barrier_action is not NativeBarrierAction.PASS_ARRAY_BUFFER:
        blockers.append(
            f"argument {argument.name!r} array native action is "
            f"{decision.native_barrier_action.value}, not pass_array_buffer"
        )
    expected_actions = {
        CodegenAction.CALL_LOCAL_INPUT,
        CodegenAction.IN_PLACE_ARGUMENT,
        CodegenAction.IDENTITY_OUTPUT,
    }
    if decision.codegen_action not in expected_actions:
        blockers.append(
            f"argument {argument.name!r} array action is {decision.codegen_action.value}, not a borrowed buffer action"
        )
    if decision.descriptor_boundary:
        blockers.append(f"argument {argument.name!r} ordinary array must be non-descriptor storage")
    if decision.nullable and not argument.optional:
        blockers.append(f"argument {argument.name!r} ordinary array is nullable without optional presence")
    array_policy = _array_handoff_policy(argument.semantic_type)
    if argument.optional and array_policy is not None and array_policy.rank is None:
        blockers.append(f"argument {argument.name!r} optional assumed-rank combination is not supported")
    return tuple(blockers)


def _raw_array_address_boundary_blockers(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
) -> tuple[str, ...]:
    """Require one caller-owned raw array address with completed pointee shape."""
    blockers = []
    if decision.owner is not OwnershipOwner.CALLER:
        blockers.append(f"argument {argument.name!r} raw array owner is {decision.owner.value}, not caller")
    expected_transfer = TransferMode.IN_PLACE if decision.mutates_native else TransferMode.CALL_LOCAL
    if decision.transfer is not expected_transfer:
        blockers.append(
            f"argument {argument.name!r} raw array transfer is {decision.transfer.value}, not {expected_transfer.value}"
        )
    expected_destruction = DestructionPolicy.CALLER if decision.mutates_native else DestructionPolicy.NONE
    if decision.destruction is not expected_destruction:
        blockers.append(
            f"argument {argument.name!r} raw array destruction is {decision.destruction.value}, "
            f"not {expected_destruction.value}"
        )
    if decision.storage_mode is not StorageMode.STACK:
        blockers.append(f"argument {argument.name!r} raw array storage is {decision.storage_mode.value}, not stack")
    if (decision.boundary_storage_mode or decision.storage_mode) is not StorageMode.STACK:
        blockers.append(f"argument {argument.name!r} raw array boundary storage is not stack")
    if decision.native_barrier_action is not NativeBarrierAction.PASS_RAW_ADDRESS:
        blockers.append(
            f"argument {argument.name!r} raw array native action is "
            f"{decision.native_barrier_action.value}, not pass_raw_address"
        )
    if decision.codegen_action not in {CodegenAction.CALL_LOCAL_INPUT, CodegenAction.IN_PLACE_ARGUMENT}:
        blockers.append(
            f"argument {argument.name!r} raw array action is {decision.codegen_action.value}, "
            "not a non-owning address action"
        )
    if argument.optional:
        blockers.append(f"argument {argument.name!r} optional raw array addresses are not supported")
    if decision.nullable or decision.descriptor_boundary:
        blockers.append(f"argument {argument.name!r} raw array address must be non-descriptor storage")
    if decision.projects_result:
        blockers.append(f"argument {argument.name!r} raw array address cannot project a Python result")
    return tuple(blockers)


def _native_array_handle_boundary_blockers(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
) -> tuple[str, ...]:
    """Require one caller handle transported through its native descriptor."""
    blockers = []
    if native_array_descriptor_kind(argument.semantic_type) not in {"allocatable", "pointer"}:
        blockers.append(f"argument {argument.name!r} has no native array descriptor kind")
    if decision.owner is not OwnershipOwner.CALLER:
        blockers.append(f"argument {argument.name!r} descriptor owner is {decision.owner.value}, not caller")
    if decision.transfer not in {TransferMode.CALL_LOCAL, TransferMode.IN_PLACE}:
        blockers.append(f"argument {argument.name!r} descriptor transfer is {decision.transfer.value}")
    if decision.destruction not in {DestructionPolicy.NONE, DestructionPolicy.CALLER}:
        blockers.append(f"argument {argument.name!r} descriptor destruction is {decision.destruction.value}")
    if decision.native_barrier_action is not NativeBarrierAction.PASS_NATIVE_DESCRIPTOR:
        blockers.append(f"argument {argument.name!r} does not pass a native descriptor")
    if decision.codegen_action not in {CodegenAction.CALL_LOCAL_INPUT, CodegenAction.IN_PLACE_ARGUMENT}:
        blockers.append(f"argument {argument.name!r} has unsupported descriptor action {decision.codegen_action.value}")
    if not decision.descriptor_boundary or not decision.nullable:
        blockers.append(f"argument {argument.name!r} descriptor boundary is incomplete")
    return tuple(blockers)


# String argument policy.
def _string_boundary_blockers(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
) -> tuple[str, ...]:
    """Dispatch one completed string boundary without backend inference."""
    action = decision.python_barrier_action
    if action is PythonBarrierAction.STRING_VALUE:
        return _string_value_boundary_blockers(argument, decision)
    if action is PythonBarrierAction.STRING_STORAGE:
        return _string_storage_boundary_blockers(argument, decision)
    if action is PythonBarrierAction.RAW_ADDRESS:
        return _raw_string_address_boundary_blockers(argument, decision)
    return (f"argument {argument.name!r} has unsupported string Python action {action.value}",)


def _string_value_boundary_blockers(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
) -> tuple[str, ...]:
    """Return completed string-value input or replacement blockers."""
    blockers = []
    if decision.python_barrier_action is not PythonBarrierAction.STRING_VALUE:
        blockers.append(
            f"argument {argument.name!r} has unsupported string Python action {decision.python_barrier_action.value}"
        )
    if decision.native_barrier_action is not NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS:
        blockers.append(
            f"argument {argument.name!r} native action is {decision.native_barrier_action.value}, "
            "not a string call-local address handoff"
        )
    if decision.codegen_action not in {CodegenAction.CALL_LOCAL_INPUT, CodegenAction.COPY_IN_OUT}:
        blockers.append(
            f"argument {argument.name!r} string action is {decision.codegen_action.value}, "
            "not a call-local input or copy-in/out replacement"
        )
    if decision.codegen_action is CodegenAction.CALL_LOCAL_INPUT and decision.projects_result:
        blockers.append(f"argument {argument.name!r} call-local string input unexpectedly projects a result")
    if decision.codegen_action is CodegenAction.COPY_IN_OUT:
        blockers.extend(_string_replacement_blockers(argument, decision))
    return tuple(blockers)


def _string_storage_boundary_blockers(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
) -> tuple[str, ...]:
    """Require caller-owned fixed mutable NumPy bytes storage."""
    blockers = list(
        _string_address_ownership_blockers(
            argument,
            decision,
            expected_storage=StorageMode.ALIAS,
            label="string storage",
        )
    )
    if decision.native_barrier_action is not NativeBarrierAction.PASS_STORAGE_ADDRESS:
        blockers.append(
            f"argument {argument.name!r} string storage native action is "
            f"{decision.native_barrier_action.value}, not pass_storage_address"
        )
    return tuple(blockers)


def _raw_string_address_boundary_blockers(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
) -> tuple[str, ...]:
    """Require a caller-owned unsafe fixed string address contract."""
    blockers = list(
        _string_address_ownership_blockers(
            argument,
            decision,
            expected_storage=StorageMode.STACK,
            label="raw string address",
        )
    )
    if decision.native_barrier_action is not NativeBarrierAction.PASS_RAW_ADDRESS:
        blockers.append(
            f"argument {argument.name!r} raw string native action is "
            f"{decision.native_barrier_action.value}, not pass_raw_address"
        )
    return tuple(blockers)


def _string_address_ownership_blockers(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
    *,
    expected_storage: StorageMode,
    label: str,
) -> tuple[str, ...]:
    """Validate ownership shared by fixed storage and raw-address forms."""
    blockers = []
    if _character_length(argument.semantic_type) is None:
        blockers.append(f"argument {argument.name!r} {label} requires a fixed positive character length")
    if decision.owner is not OwnershipOwner.CALLER:
        blockers.append(f"argument {argument.name!r} {label} owner is {decision.owner.value}, not caller")
    if decision.transfer is not TransferMode.IN_PLACE:
        blockers.append(f"argument {argument.name!r} {label} transfer is {decision.transfer.value}, not in_place")
    if decision.destruction is not DestructionPolicy.CALLER:
        blockers.append(f"argument {argument.name!r} {label} destruction is {decision.destruction.value}, not caller")
    if decision.storage_mode is not expected_storage:
        blockers.append(
            f"argument {argument.name!r} {label} storage is {decision.storage_mode.value}, not {expected_storage.value}"
        )
    if (decision.boundary_storage_mode or decision.storage_mode) is not expected_storage:
        blockers.append(f"argument {argument.name!r} {label} boundary storage is not {expected_storage.value}")
    if decision.codegen_action is not CodegenAction.IN_PLACE_ARGUMENT:
        blockers.append(
            f"argument {argument.name!r} {label} action is {decision.codegen_action.value}, not in_place_argument"
        )
    if not decision.mutates_native:
        blockers.append(f"argument {argument.name!r} {label} does not record native mutation")
    if decision.projects_result:
        blockers.append(f"argument {argument.name!r} {label} unexpectedly projects a result")
    if decision.nullable or argument.optional:
        blockers.append(f"argument {argument.name!r} optional {label} is unsupported")
    return tuple(blockers)


def _string_replacement_blockers(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
) -> tuple[str, ...]:
    """Require completed Phase 5C replacement ownership and projection."""
    blockers = []
    if decision.owner is not OwnershipOwner.PYTHON:
        blockers.append(f"argument {argument.name!r} replacement owner is {decision.owner.value}, not python")
    if decision.transfer is not TransferMode.COPY_RETURN:
        blockers.append(
            f"argument {argument.name!r} replacement transfer is {decision.transfer.value}, not copy_return"
        )
    if decision.destruction is not DestructionPolicy.PYTHON_REFCOUNT:
        blockers.append(
            f"argument {argument.name!r} replacement destruction is {decision.destruction.value}, not python_refcount"
        )
    if decision.storage_mode is not StorageMode.STACK:
        blockers.append(f"argument {argument.name!r} replacement storage is {decision.storage_mode.value}, not stack")
    if (decision.boundary_storage_mode or decision.storage_mode) is not StorageMode.STACK:
        blockers.append(f"argument {argument.name!r} replacement boundary storage is not stack")
    if not decision.mutates_native:
        blockers.append(f"argument {argument.name!r} replacement does not record native mutation")
    if not decision.projects_result:
        blockers.append(f"argument {argument.name!r} replacement does not project a Python result")
    if decision.nullable and not argument.optional:
        blockers.append(f"argument {argument.name!r} replacement is nullable without optional presence")
    return tuple(blockers)


def _argument_bridge_data_blockers(
    argument: models.SemanticArgument,
    bridge_data_action: BridgeDataAction,
    bridge_copy_reason: str | None,
) -> tuple[str, ...]:
    """Return incomplete or contradictory bridge data-action blockers."""
    blockers: list[str] = []
    if bridge_data_action is BridgeDataAction.BLOCKED:
        blockers.append(f"argument {argument.name!r} has no completed bridge data action")
    if bridge_data_action is BridgeDataAction.COPY_REPRESENTATION and not bridge_copy_reason:
        blockers.append(f"argument {argument.name!r} bridge representation copy has no completed reason")
    if bridge_data_action is not BridgeDataAction.COPY_REPRESENTATION and bridge_copy_reason is not None:
        blockers.append(f"argument {argument.name!r} copy-free bridge action carries a copy reason")
    return tuple(blockers)


def _argument_projection_blockers(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
) -> tuple[str, ...]:
    """Return projected-result action blockers for one argument."""
    if decision.projects_result and decision.codegen_action not in {
        CodegenAction.COPY_IN_OUT,
        CodegenAction.IN_PLACE_ARGUMENT,
    }:
        return (
            f"argument {argument.name!r} projects a result with unsupported action {decision.codegen_action.value}",
        )
    return ()


def _result_blockers(semantic_type: models.SemanticType, decision: OwnershipDecision) -> tuple[str, ...]:
    """Dispatch one result to its completed datatype and descriptor family."""
    if _is_scalar_descriptor_result_type(semantic_type):
        return _scalar_descriptor_result_blockers(semantic_type, decision, "result")
    if native_array_descriptor_kind(semantic_type) is not None:
        return _native_array_handle_result_blockers(decision, "result")
    if _is_phase6_ordinary_array_type(semantic_type):
        return _ordinary_array_result_blockers(semantic_type, decision, "result")
    if _is_fixed_plan_string_result_type(semantic_type):
        return _fixed_string_result_blockers(decision)
    return _scalar_result_blockers(semantic_type, decision)


# Scalar result policy.
def _scalar_result_blockers(
    semantic_type: models.SemanticType,
    decision: OwnershipDecision,
) -> tuple[str, ...]:
    """Return completed primitive scalar result blockers."""
    blockers: list[str] = []
    if decision.is_blocked:
        blockers.append(f"result has blocked ownership policy: {decision.blocker or decision.reason}")
    if not _is_first_lane_scalar_type(semantic_type):
        blockers.append("result is not a first-lane primitive scalar")
    if decision.kind is not ObjectKind.SCALAR:
        blockers.append(f"result policy kind is {decision.kind.value}, not scalar")
    if decision.codegen_action is not CodegenAction.DIRECT_VALUE:
        blockers.append(f"result codegen action is {decision.codegen_action.value}, not direct_value")
    if decision.python_barrier_action is not PythonBarrierAction.NONE:
        blockers.append(f"result Python action is {decision.python_barrier_action.value}, not none")
    if decision.native_barrier_action is not NativeBarrierAction.NONE:
        blockers.append(f"result native action is {decision.native_barrier_action.value}, not none")
    return tuple(blockers)


def _hidden_result_blockers(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
    mapping: models.ProjectionMapping,
) -> tuple[str, ...]:
    """Return blockers for one hidden result projection."""
    if _is_scalar_descriptor_result_type(argument.semantic_type, descriptor_kind=mapping.value_kind):
        return _scalar_descriptor_result_blockers(
            argument.semantic_type,
            decision,
            f"hidden result {argument.name!r}",
            mapping,
        )
    if native_array_descriptor_kind(argument.semantic_type) is not None:
        return _native_array_handle_result_blockers(decision, f"hidden result {argument.name!r}")
    if _is_phase6_ordinary_array_type(argument.semantic_type):
        return _ordinary_array_hidden_result_blockers(argument, decision, mapping)
    if _is_fixed_plan_string_result_type(argument.semantic_type):
        return _fixed_string_hidden_result_blockers(argument, decision, mapping)
    blockers: list[str] = []
    if decision.is_blocked:
        blockers.append(f"hidden result {argument.name!r} has blocked ownership policy: {decision.blocker}")
    if not _is_first_lane_scalar_type(argument.semantic_type):
        blockers.append(f"hidden result {argument.name!r} is not a primitive scalar")
    if decision.kind is not ObjectKind.SCALAR:
        blockers.append(f"hidden result {argument.name!r} policy kind is {decision.kind.value}, not scalar")
    if decision.codegen_action is not CodegenAction.DIRECT_VALUE:
        blockers.append(
            f"hidden result {argument.name!r} codegen action is {decision.codegen_action.value}, not direct_value"
        )
    if decision.python_barrier_action is not PythonBarrierAction.NONE:
        blockers.append(
            f"hidden result {argument.name!r} Python action is {decision.python_barrier_action.value}, not none"
        )
    if decision.native_barrier_action not in {
        NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS,
        NativeBarrierAction.PASS_STORAGE_ADDRESS,
    }:
        blockers.append(
            f"hidden result {argument.name!r} native action is {decision.native_barrier_action.value}, not address"
        )
    if decision.python_visible:
        blockers.append(f"hidden result {argument.name!r} is Python-visible")
    if not decision.projects_result:
        blockers.append(f"hidden result {argument.name!r} does not project a Python result")
    if not isinstance(mapping.native_position, int):
        blockers.append(f"hidden result {argument.name!r} is missing a native position")
    if not isinstance(mapping.result_position, int) or isinstance(mapping.result_position, bool):
        blockers.append(f"hidden result {argument.name!r} has no integer result position")
    elif mapping.result_position < 0:
        blockers.append(f"hidden result {argument.name!r} has negative result position {mapping.result_position}")
    return tuple(blockers)


def _scalar_descriptor_result_blockers(
    semantic_type: models.SemanticType,
    decision: OwnershipDecision,
    label: str,
    mapping: models.ProjectionMapping | None = None,
) -> tuple[str, ...]:
    """Require one nullable copied rank-zero allocatable/pointer result."""
    blockers = []
    if decision.is_blocked:
        blockers.append(f"{label} has blocked ownership policy: {decision.blocker or decision.reason}")
    expected_kind = ObjectKind.STRING if semantic_type.name == "String" else ObjectKind.SCALAR
    if decision.kind is not expected_kind:
        blockers.append(f"{label} policy kind is {decision.kind.value}, not {expected_kind.value}")
    if decision.owner is not OwnershipOwner.PYTHON:
        blockers.append(f"{label} owner is {decision.owner.value}, not python")
    if decision.destruction is not DestructionPolicy.PYTHON_REFCOUNT:
        blockers.append(f"{label} destruction is {decision.destruction.value}, not python_refcount")
    if not decision.nullable or not decision.descriptor_boundary:
        blockers.append(f"{label} does not preserve nullable descriptor state")
    if decision.python_barrier_action is not PythonBarrierAction.NONE:
        blockers.append(f"{label} Python action is {decision.python_barrier_action.value}, not none")
    if mapping is not None:
        if not decision.projects_result or decision.python_visible:
            blockers.append(f"{label} projection visibility is inconsistent")
        if mapping.value_kind not in {"allocatable", "pointer"}:
            blockers.append(f"{label} descriptor kind {mapping.value_kind!r} is unsupported")
        if not isinstance(mapping.native_position, int) or not isinstance(mapping.result_position, int):
            blockers.append(f"{label} has incomplete native/result positions")
    return tuple(blockers)


def _native_array_handle_result_blockers(
    decision: OwnershipDecision,
    label: str,
) -> tuple[str, ...]:
    """Require one wrapper-owned allocatable handle result."""
    blockers = []
    if decision.is_blocked:
        blockers.append(f"{label} has blocked ownership policy: {decision.blocker or decision.reason}")
        return tuple(blockers)
    expected = (
        ("kind", decision.kind, ObjectKind.NUMPY_ARRAY),
        ("owner", decision.owner, OwnershipOwner.WRAPPER),
        ("transfer", decision.transfer, TransferMode.WRAPPER_INSTANCE),
        ("destruction", decision.destruction, DestructionPolicy.WRAPPER_DEALLOC),
        ("action", decision.codegen_action, CodegenAction.WRAPPER_INSTANCE),
    )
    blockers.extend(
        f"{label} native handle {name} is {actual.value}, not {required.value}"
        for name, actual, required in expected
        if actual is not required
    )
    if not decision.nullable:
        blockers.append(f"{label} native handle must preserve unallocated state")
    return tuple(blockers)


# Ordinary-array result policy.
def _ordinary_array_result_blockers(
    semantic_type: models.SemanticType,
    decision: OwnershipDecision,
    label: str,
) -> tuple[str, ...]:
    """Require one Python-owned fixed-shape ordinary array copy result."""
    blockers = []
    if decision.is_blocked:
        blockers.append(f"{label} has blocked ownership policy: {decision.blocker or decision.reason}")
    if decision.kind is not ObjectKind.NUMPY_ARRAY:
        blockers.append(f"{label} policy kind is {decision.kind.value}, not numpy_array")
    if decision.owner is not OwnershipOwner.PYTHON:
        blockers.append(f"{label} owner is {decision.owner.value}, not python")
    if decision.transfer is not TransferMode.COPY_RETURN:
        blockers.append(f"{label} transfer is {decision.transfer.value}, not copy_return")
    if decision.destruction is not DestructionPolicy.PYTHON_REFCOUNT:
        blockers.append(f"{label} destruction is {decision.destruction.value}, not python_refcount")
    if decision.storage_mode is not StorageMode.STACK:
        blockers.append(f"{label} storage is {decision.storage_mode.value}, not stack")
    if decision.codegen_action is not CodegenAction.COPY_OUT:
        blockers.append(f"{label} action is {decision.codegen_action.value}, not copy_out")
    if decision.python_barrier_action is not PythonBarrierAction.NONE:
        blockers.append(f"{label} Python action is {decision.python_barrier_action.value}, not none")
    if decision.native_barrier_action is not NativeBarrierAction.NONE:
        blockers.append(f"{label} native action is {decision.native_barrier_action.value}, not none")
    if decision.nullable or decision.descriptor_boundary:
        blockers.append(f"{label} is descriptor-backed or nullable")
    array = _array_handoff_policy(semantic_type)
    if array is None or array.rank is None or any(shape in {":", "::Strided", "...", "Flat"} for shape in array.shape):
        blockers.append(f"{label} ordinary array shape is not fully expressible")
    elif array.native_order != array.order:
        blockers.append(f"{label} COPY_F applies only to Python-visible array arguments")
    elif array.order == "ORDER_C" and array.rank > 1:
        blockers.append(f"{label} ordinary array copy requires Fortran element order")
    return tuple(blockers)


def _ordinary_array_hidden_result_blockers(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
    mapping: models.ProjectionMapping,
) -> tuple[str, ...]:
    """Require one hidden fixed-shape array copied through bridge-owned storage."""
    label = f"hidden result {argument.name!r}"
    blockers = list(_ordinary_array_result_blockers(argument.semantic_type, decision, label))
    blockers = [item for item in blockers if " native action is " not in item]
    if decision.native_barrier_action is not NativeBarrierAction.PASS_ARRAY_BUFFER:
        blockers.append(f"{label} native action is {decision.native_barrier_action.value}, not array buffer")
    if decision.python_visible or not decision.projects_result:
        blockers.append(f"{label} projection visibility is inconsistent")
    if not isinstance(mapping.native_position, int):
        blockers.append(f"{label} is missing a native position")
    if not isinstance(mapping.result_position, int) or isinstance(mapping.result_position, bool):
        blockers.append(f"{label} has no integer result position")
    elif mapping.result_position < 0:
        blockers.append(f"{label} has negative result position {mapping.result_position}")
    return tuple(blockers)


# String result and writeback policy.
def _fixed_string_result_blockers(decision: OwnershipDecision) -> tuple[str, ...]:
    """Require the completed copy-return policy for one direct fixed string."""
    blockers = list(_fixed_string_result_ownership_blockers(decision, "result"))
    if decision.is_blocked:
        blockers.append(f"result has blocked ownership policy: {decision.blocker or decision.reason}")
    if decision.kind is not ObjectKind.STRING:
        blockers.append(f"result policy kind is {decision.kind.value}, not string")
    if decision.codegen_action is not CodegenAction.COPY_OUT:
        blockers.append(f"result codegen action is {decision.codegen_action.value}, not copy_out")
    if decision.python_barrier_action is not PythonBarrierAction.NONE:
        blockers.append(f"result Python action is {decision.python_barrier_action.value}, not none")
    if decision.native_barrier_action is not NativeBarrierAction.NONE:
        blockers.append(f"result native action is {decision.native_barrier_action.value}, not none")
    return tuple(blockers)


def _fixed_string_hidden_result_blockers(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
    mapping: models.ProjectionMapping,
) -> tuple[str, ...]:
    """Require one fixed string hidden output and its completed projection."""
    label = f"hidden result {argument.name!r}"
    blockers = list(_fixed_string_result_ownership_blockers(decision, label))
    if decision.is_blocked:
        blockers.append(
            f"hidden result {argument.name!r} has blocked ownership policy: {decision.blocker or decision.reason}"
        )
    if decision.kind is not ObjectKind.STRING:
        blockers.append(f"hidden result {argument.name!r} policy kind is {decision.kind.value}, not string")
    if decision.codegen_action is not CodegenAction.COPY_OUT:
        blockers.append(
            f"hidden result {argument.name!r} codegen action is {decision.codegen_action.value}, not copy_out"
        )
    if decision.python_barrier_action is not PythonBarrierAction.NONE:
        blockers.append(
            f"hidden result {argument.name!r} Python action is {decision.python_barrier_action.value}, not none"
        )
    if decision.native_barrier_action is not NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS:
        blockers.append(
            f"hidden result {argument.name!r} native action is "
            f"{decision.native_barrier_action.value}, not call-local address"
        )
    if decision.python_visible:
        blockers.append(f"hidden result {argument.name!r} is Python-visible")
    if not decision.projects_result:
        blockers.append(f"hidden result {argument.name!r} does not project a Python result")
    if not isinstance(mapping.native_position, int):
        blockers.append(f"hidden result {argument.name!r} is missing a native position")
    if not isinstance(mapping.result_position, int) or isinstance(mapping.result_position, bool):
        blockers.append(f"hidden result {argument.name!r} has no integer result position")
    elif mapping.result_position < 0:
        blockers.append(f"hidden result {argument.name!r} has negative result position {mapping.result_position}")
    return tuple(blockers)


def _fixed_string_result_ownership_blockers(
    decision: OwnershipDecision,
    label: str,
) -> tuple[str, ...]:
    """Require Python-owned stack-to-copy-return fixed string ownership."""
    blockers = []
    if decision.owner is not OwnershipOwner.PYTHON:
        blockers.append(f"{label} owner is {decision.owner.value}, not python")
    if decision.transfer is not TransferMode.COPY_RETURN:
        blockers.append(f"{label} transfer is {decision.transfer.value}, not copy_return")
    if decision.destruction is not DestructionPolicy.PYTHON_REFCOUNT:
        blockers.append(f"{label} destruction is {decision.destruction.value}, not python_refcount")
    if decision.storage_mode is not StorageMode.STACK:
        blockers.append(f"{label} storage is {decision.storage_mode.value}, not stack")
    if (decision.boundary_storage_mode or decision.storage_mode) is not StorageMode.STACK:
        blockers.append(f"{label} boundary storage is not stack")
    if decision.nullable:
        blockers.append(f"{label} is nullable outside deferred string results")
    return tuple(blockers)


def _string_result_aggregation_blockers(results: tuple[ResultPolicy, ...]) -> tuple[str, ...]:
    """Keep native string-allocation cleanup single-result in Phase 5B."""
    if any(result.ownership.kind is ObjectKind.STRING for result in results) and len(results) != 1:
        return ("fixed string result lane requires exactly one Python-visible result",)
    return ()


def _string_result_status_blockers(
    results: tuple[ResultPolicy, ...],
    status_error: NativeStatusErrorPolicy | None,
) -> tuple[str, ...]:
    """Block status exits until public string-result release is planned."""
    if status_error is not None and any(result.ownership.kind is ObjectKind.STRING for result in results):
        return ("fixed string result with native status error requires planned failure-path release",)
    return ()


def _string_writeback_status_blockers(
    arguments: list[ArgumentPolicy],
    status_error: NativeStatusErrorPolicy | None,
) -> tuple[str, ...]:
    """Block status exits until mutable string-buffer cleanup is planned there."""
    if status_error is not None and any(
        argument.ownership.kind is ObjectKind.STRING and argument.codegen_action is CodegenAction.COPY_IN_OUT
        for argument in arguments
    ):
        return ("string replacement with native status error requires planned failure-path cleanup",)
    return ()


def _result_position_blockers(results: tuple[ResultPolicy, ...]) -> tuple[str, ...]:
    """Require completed Python results to cover one contiguous order."""
    positions = tuple(result.result_position for result in results)
    if sorted(positions) == list(range(len(positions))) and len(set(positions)) == len(positions):
        return ()
    return (f"binding result positions must cover 0..{len(positions) - 1} exactly once; received {positions}",)


def _function_shape_blockers(function: models.SemanticFunction) -> tuple[str, ...]:
    blockers: list[str] = []
    if function.visibility != "public":
        blockers.append("function is not public")
    if isinstance(function, models.SemanticMethod):
        blockers.append("methods are outside the first scalar lane")
    if function.locals:
        blockers.append("function locals are outside the first scalar lane")
    if function.contracts:
        blockers.append("function contracts are outside the first scalar lane")
    return tuple(blockers)


def _completed_native_status_error_policy(
    function: models.SemanticFunction,
) -> NativeStatusErrorPolicy | None:
    policy = function.metadata.get(models.RESOLVED_RUNTIME_STATUS_ERROR_POLICY_METADATA)
    return policy if isinstance(policy, NativeStatusErrorPolicy) else None


def _runtime_status_output_owner_paths(function: models.SemanticFunction) -> frozenset[str]:
    policy = _completed_native_status_error_policy(function)
    if policy is None:
        return frozenset()
    outputs = [policy.status.owner_path]
    if policy.message is not None:
        outputs.append(policy.message.owner_path)
    return frozenset(outputs)


def _runtime_status_plan_blockers(policy: NativeStatusErrorPolicy | None) -> tuple[str, ...]:
    """Return Phase 2D backend blockers after semantic validity is complete."""
    if policy is None:
        return ()
    blockers = []
    if policy.status.semantic_type_name != "Int32":
        blockers.append("native status error projection requires an Int32 status in the current plan lane")
    if policy.message is not None and policy.message.character_length is None:
        blockers.append("native status error message requires a fixed positive character length")
    return tuple(blockers)


def _character_length(semantic_type: models.SemanticType) -> int | None:
    value = semantic_type.metadata.get("fortran_character_length")
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return value
    if isinstance(value, str) and value.strip().isdigit() and int(value.strip()) > 0:
        return int(value.strip())
    return None


def _lifecycle_policies(
    arguments: list[ArgumentPolicy],
) -> tuple[tuple[LifecyclePolicy, ...], tuple[str, ...]]:
    """Return completed replacement/writeback actions and structural blockers."""
    actions = []
    blockers: list[str] = []
    for argument in arguments:
        if not argument.projects_result:
            continue
        if argument.result_position is None:
            blockers.append(f"argument {argument.name!r} writeback is missing a result position")
            continue
        phases = (
            (WritebackPhase.COPY_OUT,) if argument.ownership.kind is ObjectKind.NUMPY_ARRAY else tuple(WritebackPhase)
        )
        actions.extend(
            LifecyclePolicy(
                owner_path=argument.owner_path,
                phase=phase,
                source_role=f"{argument.owner_path}:value",
                codegen_action=argument.codegen_action,
                semantic_type_name=argument.semantic_type_name,
                result_position=argument.result_position,
                object_kind=argument.ownership.kind,
            )
            for phase in phases
        )
    non_array_actions = [
        action
        for action in actions
        if next(item for item in arguments if item.owner_path == action.owner_path).ownership.kind
        is not ObjectKind.NUMPY_ARRAY
    ]
    if len(non_array_actions) > len(WritebackPhase):
        blockers.append("replacement lane currently requires exactly one non-array projected result")
    return tuple(actions), tuple(blockers)


def _native_position_blockers(native_positions: object) -> tuple[str, ...]:
    positions = tuple(native_positions)
    if sorted(positions) != list(range(len(positions))):
        return ("native-call slots must cover each native position exactly once in order",)
    return ()


def _ownership_decision(owner: object, metadata_key: str) -> OwnershipDecision | None:
    decision = getattr(owner, "metadata", {}).get(metadata_key)
    return decision if isinstance(decision, OwnershipDecision) else None


def _is_first_lane_scalar_type(semantic_type: models.SemanticType) -> bool:
    scalar_name = semantic_type.dtype or semantic_type.name
    return bool(
        int(semantic_type.rank or 0) == 0
        and semantic_type.name != "String"
        and scalar_name in _PLAN_PRIMITIVE_SCALAR_TYPES
    )


def _is_plan_string_value_type(semantic_type: models.SemanticType) -> bool:
    """Return whether one semantic type is a scalar Python string value."""
    return bool(int(semantic_type.rank or 0) == 0 and semantic_type.name == "String")


def _is_fixed_plan_string_result_type(semantic_type: models.SemanticType) -> bool:
    """Return whether one result is a fixed positive scalar string."""
    length = _character_length(semantic_type)
    return bool(_is_plan_string_value_type(semantic_type) and length is not None and length > 0)


def _is_first_lane_literal_type(literal_type: str) -> bool:
    """Return whether a hidden literal type belongs to the scalar input lane."""
    return literal_type in {"Bool", "Int32", "Float32", "Float64", "Complex64", "Complex128"}


# Native-array-handle policy projection.
def _is_scalar_descriptor_result_type(
    semantic_type: models.SemanticType,
    *,
    descriptor_kind: str | None = None,
) -> bool:
    """Return whether rank-zero result storage is allocatable or pointer-backed."""
    descriptor = descriptor_kind or _scalar_descriptor_kind(semantic_type)
    return int(semantic_type.rank or 0) == 0 and descriptor in {"allocatable", "pointer"}


def _scalar_descriptor_kind(semantic_type: models.SemanticType) -> str | None:
    """Return the explicit rank-zero descriptor marker completed by semantics."""
    if int(semantic_type.rank or 0) != 0:
        return None
    allocatable = bool(semantic_type.metadata.get("fortran_allocatable"))
    pointer = bool(semantic_type.metadata.get("fortran_pointer"))
    if allocatable and pointer:
        raise ValueError(f"Scalar type {semantic_type.name!r} cannot be both allocatable and pointer")
    if allocatable:
        return "allocatable"
    if pointer:
        return "pointer"
    return None


def _scalar_descriptor_result_policy(
    semantic_type: models.SemanticType,
    decision: OwnershipDecision,
    *,
    descriptor_kind: str | None = None,
) -> ScalarDescriptorResultPolicy | None:
    """Project one completed nullable rank-zero descriptor copy policy."""
    if not _is_scalar_descriptor_result_type(semantic_type, descriptor_kind=descriptor_kind):
        return None
    descriptor = descriptor_kind or _scalar_descriptor_kind(semantic_type)
    if descriptor is None:
        return None
    return ScalarDescriptorResultPolicy(
        descriptor_kind=NativeArrayDescriptorKind(descriptor),
        runtime_length=semantic_type.name == "String",
        nullable=decision.nullable,
        copy_reason=SCALAR_DESCRIPTOR_RESULT_COPY_REASON,
        release_owner=OwnershipOwner.PYTHON,
    )


def _native_array_handle_wrapper_policy(
    semantic_type: models.SemanticType,
    completed: object,
    owner_path: str,
) -> NativeArrayHandleWrapperPolicy | None:
    """Translate completed string selectors once into typed wrapper policy."""
    descriptor = native_array_descriptor_kind(semantic_type)
    if descriptor is None:
        return None
    if int(semantic_type.rank or 0) == 0:
        return None
    if not isinstance(completed, CompletedNativeArrayHandlePolicy):
        raise ValueError(f"Native array handle {owner_path!r} is missing completed policy")
    if completed.is_blocked:
        return None
    output_projection = _native_array_enum(
        NativeArrayOutputProjection,
        completed.output_projection,
        owner_path,
        "output projection",
    )
    handle_kind = _native_array_enum(NativeArrayHandleKind, completed.handle_kind, owner_path, "handle kind")
    handoff = NativeDescriptorHandoffPolicy(
        abi=_native_descriptor_handoff_abi(handle_kind, output_projection),
        rank=int(semantic_type.rank or 0),
        optional_presence=completed.optional_absent,
    )
    interop = _native_array_enum(
        NativeArrayDescriptorInterop,
        completed.descriptor_interop,
        owner_path,
        "descriptor interop",
    )
    operations = {
        _native_array_enum(NativeArrayOperation, item, owner_path, "operation") for item in completed.operations
    }
    operations.update(
        {
            NativeArrayOperation.SHAPE,
            NativeArrayOperation.ARRAY_ACTUAL,
            NativeArrayOperation.DESCRIPTOR,
            NativeArrayOperation.NATIVE_BYTE_ORDER,
            NativeArrayOperation.ALIGNED,
            NativeArrayOperation.WRITEABLE,
            NativeArrayOperation.LAYOUT,
        }
    )
    if semantic_type.name == "String":
        operations.add(NativeArrayOperation.ELEMENT_LENGTH)
        if semantic_type.metadata.get("fortran_character_length") == ":":
            operations.difference_update({NativeArrayOperation.ALLOCATE, NativeArrayOperation.RESIZE})
    if descriptor == "pointer":
        operations.add(NativeArrayOperation.CONTIGUOUS)
    if completed.destroy_behavior == NativeArrayDestroyBehavior.HANDLE_FINALIZER.value:
        operations.add(NativeArrayOperation.DESTROY)
    array = _array_handoff_policy(semantic_type)
    if array is None or array.rank is None:
        raise ValueError(f"Native array handle {owner_path!r} requires one concrete array handoff")
    return NativeArrayHandleWrapperPolicy(
        descriptor_kind=_native_array_enum(
            NativeArrayDescriptorKind,
            completed.descriptor_kind,
            owner_path,
            "descriptor kind",
        ),
        handle_kind=handle_kind,
        origin=_native_array_enum(NativeArrayHandleOrigin, completed.origin, owner_path, "origin"),
        owner=_native_array_enum(OwnershipOwner, completed.owner, owner_path, "owner"),
        owner_retention=_native_array_enum(
            NativeArrayOwnerRetention,
            completed.owner_retention,
            owner_path,
            "owner retention",
        ),
        descriptor_ownership=_native_array_enum(
            NativeArrayDescriptorOwnership,
            completed.descriptor_ownership,
            owner_path,
            "descriptor ownership",
        ),
        borrowed=completed.borrowed,
        getter_behavior=_native_array_enum(
            NativeArrayGetterBehavior,
            completed.getter_behavior,
            owner_path,
            "getter behavior",
        ),
        setter_action=_native_array_setter_action(completed.python_setter, owner_path),
        native_assignment=_native_array_assignment(completed.native_setter, owner_path),
        output_projection=output_projection,
        release=_native_array_enum(NativeArrayRelease, completed.release, owner_path, "release"),
        target_lifetime=completed.target_lifetime,
        destroy_behavior=_native_array_enum(
            NativeArrayDestroyBehavior,
            completed.destroy_behavior,
            owner_path,
            "destroy behavior",
        ),
        extraction_action=_native_array_enum(
            NativeArrayExtractionAction,
            completed.to_numpy,
            owner_path,
            "extraction action",
        ),
        descriptor_interop=interop,
        nullable=completed.nullable,
        optional_absent=completed.optional_absent,
        storage_mode=_native_array_enum(StorageMode, completed.storage_mode, owner_path, "storage mode"),
        operations=tuple(sorted(operations, key=lambda item: item.value)),
        required_headers=(
            (NATIVE_ARRAY_POINTER_C_DESCRIPTOR_HEADER,)
            if (
                interop is not NativeArrayDescriptorInterop.NONE
                or handle_kind
                in {
                    NativeArrayHandleKind.ARGUMENT_DESCRIPTOR,
                    NativeArrayHandleKind.OPTIONAL_ABSENT_HANDLE,
                    NativeArrayHandleKind.OWNED_RESULT_DESCRIPTOR,
                }
            )
            else ()
        ),
        array=array,
        handoff=handoff,
    )


def _native_descriptor_handoff_abi(
    handle_kind: NativeArrayHandleKind,
    output_projection: NativeArrayOutputProjection,
) -> NativeDescriptorHandoffABI:
    """Select one descriptor ABI from completed handle/result policy."""
    if handle_kind is NativeArrayHandleKind.OWNED_RESULT_DESCRIPTOR:
        return NativeDescriptorHandoffABI.OWNED_RESULT_STORAGE
    if output_projection is NativeArrayOutputProjection.PROJECTED_HANDLE:
        return NativeDescriptorHandoffABI.DIRECT_STANDARD_DESCRIPTOR
    return NativeDescriptorHandoffABI.FACT_PACKED_CALL_LOCAL


def _native_array_enum(enum_type, value: object, owner_path: str, label: str):
    """Translate one completed selector or fail at the policy boundary."""
    try:
        return enum_type(value)
    except ValueError:
        raise ValueError(f"Native array handle {owner_path!r} has unsupported {label} {value!r}") from None


def _native_array_setter_action(value: str, owner_path: str) -> SetterAction:
    """Translate semantic handle setter spelling into the shared setter enum."""
    if value == "none":
        return SetterAction.OMIT
    return _native_array_enum(SetterAction, value, owner_path, "Python setter")


# Layer-owned representation transformations.
def _argument_transformation_policies(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
    array: ArrayHandoffPolicy | None,
) -> tuple[tuple[TransformationPolicy, ...], tuple[str, ...]]:
    """Complete explicit COPY_F ownership and lifecycle before planning."""
    if array is None or array.native_order == array.order:
        return (), ()
    blockers = _copy_to_fortran_argument_blockers(argument, decision, array)
    if blockers:
        return (), blockers
    transformations = []
    reason = "explicit COPY_F converts C-order Python storage while preserving logical Fortran axes"
    if decision.codegen_action is not CodegenAction.IDENTITY_OUTPUT:
        transformations.append(
            TransformationPolicy(
                phase=WritebackPhase.COPY_IN,
                layer=TransformationLayer.BINDING,
                action=TransformationAction.COPY_ARRAY_REPRESENTATION,
                source_representation="numpy_order_c",
                target_representation="numpy_order_f",
                reason=reason,
            )
        )
    if decision.mutates_native:
        transformations.append(
            TransformationPolicy(
                phase=WritebackPhase.COPY_OUT,
                layer=TransformationLayer.BINDING,
                action=TransformationAction.COPY_ARRAY_REPRESENTATION,
                source_representation="numpy_order_f",
                target_representation="numpy_order_c",
                reason=reason,
            )
        )
    transformations.append(
        TransformationPolicy(
            phase=WritebackPhase.CLEANUP,
            layer=TransformationLayer.BINDING,
            action=TransformationAction.RELEASE_TEMPORARY,
            source_representation="numpy_order_f",
            target_representation="released",
            reason="binding owns the complete COPY_F NumPy temporary lifecycle",
        )
    )
    return tuple(transformations), ()


def _copy_to_fortran_argument_blockers(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
    array: ArrayHandoffPolicy,
) -> tuple[str, ...]:
    """Keep COPY_F on its initial required dense numeric ndarray lane."""
    blockers = []
    if argument.optional:
        blockers.append(f"argument {argument.name!r} COPY_F optional arrays are not implemented")
    if (
        decision.kind is not ObjectKind.NUMPY_ARRAY
        or decision.python_barrier_action is not PythonBarrierAction.ARRAY_STORAGE
    ):
        blockers.append(f"argument {argument.name!r} COPY_F requires ordinary NumPy array storage")
    if decision.descriptor_boundary or native_array_descriptor_kind(argument.semantic_type) is not None:
        blockers.append(f"argument {argument.name!r} COPY_F does not support native descriptors")
    if argument.semantic_type.name == "String":
        blockers.append(f"argument {argument.name!r} COPY_F character arrays are not implemented")
    if array.rank is None or array.rank <= 1 or array.contiguous is not True:
        blockers.append(f"argument {argument.name!r} COPY_F requires a concrete dense multidimensional array")
    if array.order != "ORDER_C" or array.native_order != "ORDER_F":
        blockers.append(f"argument {argument.name!r} COPY_F has inconsistent source/native order")
    return tuple(blockers)


def _native_array_assignment(value: str, owner_path: str) -> AssignmentMode:
    """Translate semantic handle native setter spelling into assignment enum."""
    return _native_array_enum(AssignmentMode, value, owner_path, "native setter")


def _native_array_actual_policy(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
    array: ArrayHandoffPolicy | None,
) -> NativeArrayActualPolicy | None:
    """Complete handle-as-array-actual acceptance for the Phase 6 buffer ABI."""
    if native_array_descriptor_kind(argument.semantic_type) is not None:
        return None
    if (
        array is None
        or array.native_order != array.order
        or array.rank is None
        or argument.optional
        or argument.semantic_type.name == "String"
        or array.contiguous is not True
        or decision.python_barrier_action is not PythonBarrierAction.ARRAY_STORAGE
        or decision.native_barrier_action is not NativeBarrierAction.PASS_ARRAY_BUFFER
    ):
        return None
    try:
        dtype = _NUMPY_DTYPE_NAMES[argument.semantic_type.name]
    except KeyError:
        return None
    return NativeArrayActualPolicy(
        accepted_sources=(
            NativeArraySourceKind.NDARRAY,
            NativeArraySourceKind.ALLOCATABLE_HANDLE,
            NativeArraySourceKind.POINTER_HANDLE,
        ),
        dtype=dtype,
        rank=array.rank,
        shape=array.shape,
        order=None if array.rank == 1 else ("F" if array.order != "ORDER_C" else "C"),
        writable=decision.mutates_native,
        require_native_byte_order=True,
        require_aligned=True,
        require_contiguous=True,
    )


def _native_array_module_variable_blockers(
    variable: models.SemanticVariable,
    getter: OwnershipDecision | None,
    setter: OwnershipDecision | None,
    handle: NativeArrayHandleWrapperPolicy,
) -> list[str]:
    """Validate one borrowed module descriptor handle before planning."""
    blockers = []
    if variable.visibility != "public":
        blockers.append("native array module variable is not public")
    if handle.handle_kind is not NativeArrayHandleKind.BORROWED_MODULE_DESCRIPTOR:
        blockers.append(f"native array module handle kind {handle.handle_kind.value!r} is unsupported")
    if getter is None or getter.is_blocked or getter.kind is not ObjectKind.NUMPY_ARRAY:
        blockers.append("native array module getter is missing a completed array policy")
    if setter is None or handle.setter_action is not SetterAction.REJECT_REPLACEMENT:
        blockers.append("native array module handle must reject replacement assignment")
    if handle.descriptor_ownership is not NativeArrayDescriptorOwnership.BORROWED or not handle.borrowed:
        blockers.append("native array module handle must borrow native descriptor storage")
    if handle.destroy_behavior is not NativeArrayDestroyBehavior.NONE:
        blockers.append("native array module handle cannot destroy native descriptor storage")
    return blockers


# Scalar module-variable policy.
def _scalar_module_variable_blockers(
    variable: models.SemanticVariable,
    getter: OwnershipDecision | None,
    setter: OwnershipDecision | None,
    descriptor_kind: str | None,
    constant: bool,
) -> list[str]:
    """Return Phase 4 blockers for one module variable."""
    blockers = []
    if variable.visibility != "public":
        blockers.append("module variable is not public")
    if not _is_first_lane_scalar_type(variable.semantic_type):
        blockers.append("module variable is not a primitive rank-zero scalar")
    if getter is None:
        blockers.append("module variable is missing completed getter policy")
    elif getter.is_blocked or getter.kind is not ObjectKind.SCALAR:
        blockers.append("module variable getter is not a supported scalar policy")
    elif getter.codegen_action not in {CodegenAction.DIRECT_VALUE, CodegenAction.SNAPSHOT_COPY}:
        blockers.append(f"module variable getter action {getter.codegen_action.value!r} is unsupported")
    if setter is None:
        blockers.append("module variable is missing completed setter policy")
    else:
        blockers.extend(_scalar_module_setter_blockers(setter, descriptor_kind, constant))
    if constant and variable.default_value is None:
        blockers.append("scalar module constant is missing its completed value")
    elif constant and not _is_scalar_module_literal(variable.default_value, variable.semantic_type.name):
        blockers.append("scalar module constant value is not a supported literal")
    initializer = variable.metadata.get(models.RESOLVED_MODULE_VARIABLE_INITIALIZER_METADATA)
    if initializer is not None and (setter is None or setter.setter_action is not SetterAction.WRITE_THROUGH):
        blockers.append("module variable initializer requires a write-through setter")
    if initializer is not None and not _is_scalar_module_literal(initializer, variable.semantic_type.name):
        blockers.append("module variable initializer is not a supported scalar literal")
    return blockers


def _scalar_module_setter_blockers(
    setter: OwnershipDecision,
    descriptor_kind: str | None,
    constant: bool,
) -> tuple[str, ...]:
    """Return completed setter consistency blockers."""
    if constant:
        if setter.setter_action is not SetterAction.OMIT or setter.assignment_mode is not AssignmentMode.NONE:
            return ("scalar constant must omit native setter assignment",)
        return ()
    if setter.setter_action is SetterAction.WRITE_THROUGH:
        if setter.assignment_mode is not AssignmentMode.VALUE_COPY:
            return ("write-through scalar setter requires value-copy native assignment",)
        if setter.python_barrier_action is not PythonBarrierAction.SCALAR_VALUE:
            return ("write-through scalar setter requires scalar-value Python conversion",)
        return ()
    if setter.setter_action is SetterAction.REJECT_REPLACEMENT:
        if descriptor_kind is None:
            return ("rejected scalar replacement requires persistent descriptor storage",)
        return ()
    return (f"non-constant scalar setter action {setter.setter_action.value!r} is unsupported",)


def _scalar_module_getter_action(
    getter: OwnershipDecision | None,
    constant: bool,
) -> ModuleGetterAction:
    if constant:
        return ModuleGetterAction.CONSTANT_VALUE
    if getter is not None and getter.codegen_action is CodegenAction.SNAPSHOT_COPY and getter.nullable:
        return ModuleGetterAction.NULLABLE_SNAPSHOT
    return ModuleGetterAction.DIRECT_VALUE


def _scalar_module_native_assignment(
    setter: OwnershipDecision | None,
) -> AssignmentMode:
    """Project the completed native setter action for bridge lowering."""
    if setter is None or setter.setter_action is not SetterAction.WRITE_THROUGH:
        return AssignmentMode.NONE
    return setter.assignment_mode


def _scalar_module_descriptor_kind(variable: models.SemanticVariable) -> str | None:
    metadata = variable.semantic_type.metadata
    if metadata.get("fortran_allocatable"):
        return "allocatable"
    if metadata.get("fortran_pointer"):
        return "pointer"
    return None


def _is_scalar_module_constant(variable: models.SemanticVariable) -> bool:
    return any(constraint.name == "Constant" for constraint in variable.semantic_type.constraints)


def _is_scalar_module_literal(value: object, semantic_type_name: str) -> bool:
    try:
        _scalar_module_literal_value(value, semantic_type_name)
    except (TypeError, ValueError, SyntaxError):
        return False
    return True


def _scalar_module_literal_value(value: object, semantic_type_name: str) -> object:
    """Normalize Python/Fortran scalar literal spelling during policy completion."""
    if not isinstance(value, str):
        return value
    text = value.strip()
    if semantic_type_name == "Bool":
        lowered = text.casefold()
        if lowered in {".true.", "true"}:
            return True
        if lowered in {".false.", "false"}:
            return False
    normalized = text.replace("D", "e").replace("d", "e")
    parsed = ast.literal_eval(normalized)
    if semantic_type_name in {"Complex64", "Complex128"} and isinstance(parsed, tuple):
        if len(parsed) != 2:
            raise ValueError("complex scalar literal requires real and imaginary components")
        return complex(parsed[0], parsed[1])
    return parsed


def _optional_mode(
    argument: models.SemanticArgument,
    decision: OwnershipDecision,
) -> OptionalMode:
    """Return the completed presence behavior for one scalar argument."""
    if not argument.optional:
        if decision.kind is ObjectKind.SCALAR and decision.descriptor_boundary:
            return OptionalMode.REQUIRED_DESCRIPTOR
        return OptionalMode.REQUIRED
    if decision.descriptor_boundary:
        return OptionalMode.DESCRIPTOR
    return OptionalMode.NULLABLE_VALUE


def _argument_bridge_data_action(
    decision: OwnershipDecision,
    optional_mode: OptionalMode,
    value_kind: str | None,
) -> tuple[BridgeDataAction, str | None]:
    """Complete whether the bridge reuses, views, or copies one input payload."""
    if decision.kind is ObjectKind.NUMPY_ARRAY:
        return _array_argument_bridge_data_action(decision, optional_mode)
    if decision.kind is ObjectKind.STRING:
        return _string_argument_bridge_data_action(decision, optional_mode)
    return _scalar_argument_bridge_data_action(decision, optional_mode, value_kind)


# Ordinary-array bridge data policy.
def _array_argument_bridge_data_action(
    decision: OwnershipDecision,
    optional_mode: OptionalMode,
) -> tuple[BridgeDataAction, str | None]:
    """Complete one buffer, raw-address, or native-descriptor bridge view."""
    if (
        optional_mode in {OptionalMode.REQUIRED, OptionalMode.DESCRIPTOR}
        and decision.python_barrier_action is PythonBarrierAction.WRAPPER_INSTANCE
        and decision.native_barrier_action is NativeBarrierAction.PASS_NATIVE_DESCRIPTOR
    ):
        if decision.codegen_action is CodegenAction.CALL_LOCAL_INPUT:
            return BridgeDataAction.ASSOCIATE_VIEW, None
        if decision.codegen_action is CodegenAction.IN_PLACE_ARGUMENT:
            return BridgeDataAction.DIRECT_TRANSFER, None
    if (
        optional_mode is OptionalMode.REQUIRED
        and decision.python_barrier_action is PythonBarrierAction.RAW_ADDRESS
        and decision.native_barrier_action is NativeBarrierAction.PASS_RAW_ADDRESS
        and decision.codegen_action in {CodegenAction.CALL_LOCAL_INPUT, CodegenAction.IN_PLACE_ARGUMENT}
    ):
        return BridgeDataAction.ASSOCIATE_VIEW, None
    if (
        optional_mode in {OptionalMode.REQUIRED, OptionalMode.NULLABLE_VALUE}
        and decision.python_barrier_action is PythonBarrierAction.ARRAY_STORAGE
        and decision.native_barrier_action is NativeBarrierAction.PASS_ARRAY_BUFFER
        and decision.codegen_action
        in {
            CodegenAction.CALL_LOCAL_INPUT,
            CodegenAction.IN_PLACE_ARGUMENT,
            CodegenAction.IDENTITY_OUTPUT,
        }
    ):
        return BridgeDataAction.ASSOCIATE_VIEW, None
    return BridgeDataAction.BLOCKED, None


# String bridge data policy.
def _string_argument_bridge_data_action(
    decision: OwnershipDecision,
    optional_mode: OptionalMode,
) -> tuple[BridgeDataAction, str | None]:
    """Complete one string value, storage, or raw-address representation."""
    if (
        optional_mode in {OptionalMode.REQUIRED, OptionalMode.NULLABLE_VALUE}
        and decision.python_barrier_action is PythonBarrierAction.STRING_VALUE
        and decision.native_barrier_action is NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS
    ):
        if decision.codegen_action is CodegenAction.CALL_LOCAL_INPUT:
            return BridgeDataAction.COPY_REPRESENTATION, STRING_INPUT_COPY_REASON
        if decision.codegen_action is CodegenAction.COPY_IN_OUT:
            return BridgeDataAction.COPY_REPRESENTATION, STRING_REPLACEMENT_COPY_REASON
    if (
        optional_mode is OptionalMode.REQUIRED
        and decision.python_barrier_action is PythonBarrierAction.STRING_STORAGE
        and decision.native_barrier_action is NativeBarrierAction.PASS_STORAGE_ADDRESS
        and decision.codegen_action is CodegenAction.IN_PLACE_ARGUMENT
    ):
        return BridgeDataAction.COPY_REPRESENTATION, STRING_STORAGE_COPY_REASON
    if (
        optional_mode is OptionalMode.REQUIRED
        and decision.python_barrier_action is PythonBarrierAction.RAW_ADDRESS
        and decision.native_barrier_action is NativeBarrierAction.PASS_RAW_ADDRESS
        and decision.codegen_action is CodegenAction.IN_PLACE_ARGUMENT
    ):
        return BridgeDataAction.COPY_REPRESENTATION, RAW_STRING_ADDRESS_COPY_REASON
    return BridgeDataAction.BLOCKED, None


# Scalar bridge data policy.
def _scalar_argument_bridge_data_action(
    decision: OwnershipDecision,
    optional_mode: OptionalMode,
    value_kind: str | None,
) -> tuple[BridgeDataAction, str | None]:
    """Complete one scalar value, storage, raw-address, or descriptor action."""
    if optional_mode in {OptionalMode.REQUIRED_DESCRIPTOR, OptionalMode.DESCRIPTOR}:
        if value_kind == "pointer":
            return BridgeDataAction.ASSOCIATE_VIEW, None
        if value_kind == "allocatable":
            return (
                BridgeDataAction.COPY_REPRESENTATION,
                "materialize owned Fortran allocatable scalar storage from the binding value",
            )
        return BridgeDataAction.BLOCKED, None
    if optional_mode is OptionalMode.NULLABLE_VALUE:
        return BridgeDataAction.ASSOCIATE_VIEW, None
    if decision.python_barrier_action in {
        PythonBarrierAction.SCALAR_STORAGE,
        PythonBarrierAction.RAW_ADDRESS,
    }:
        return BridgeDataAction.ASSOCIATE_VIEW, None
    if decision.python_barrier_action is PythonBarrierAction.SCALAR_VALUE and decision.native_barrier_action in {
        NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS,
        NativeBarrierAction.PASS_STORAGE_ADDRESS,
        NativeBarrierAction.PASS_VALUE,
    }:
        return BridgeDataAction.DIRECT_TRANSFER, None
    return BridgeDataAction.BLOCKED, None


def _result_bridge_data_action(
    semantic_type: models.SemanticType,
    *,
    descriptor_kind: str | None = None,
) -> tuple[BridgeDataAction, str | None]:
    """Complete direct result transfer without widening unsupported lanes."""
    if _is_scalar_descriptor_result_type(semantic_type, descriptor_kind=descriptor_kind):
        return BridgeDataAction.COPY_REPRESENTATION, SCALAR_DESCRIPTOR_RESULT_COPY_REASON
    if native_array_descriptor_kind(semantic_type) == "allocatable":
        return BridgeDataAction.COPY_REPRESENTATION, OWNED_NATIVE_ARRAY_HANDLE_COPY_REASON
    if _is_first_lane_scalar_type(semantic_type):
        return BridgeDataAction.DIRECT_TRANSFER, None
    if _is_phase6_ordinary_array_type(semantic_type):
        return BridgeDataAction.COPY_REPRESENTATION, ORDINARY_ARRAY_RESULT_COPY_REASON
    if _is_fixed_plan_string_result_type(semantic_type):
        return (
            BridgeDataAction.COPY_REPRESENTATION,
            FIXED_STRING_RESULT_COPY_REASON,
        )
    return BridgeDataAction.BLOCKED, None


def _native_result_bridge_data_action(
    semantic_type: models.SemanticType,
    *,
    descriptor_kind: str | None = None,
) -> tuple[BridgeDataAction, str | None]:
    """Complete bridge data movement for one hidden native output slot."""
    if _is_scalar_descriptor_result_type(semantic_type, descriptor_kind=descriptor_kind):
        return BridgeDataAction.COPY_REPRESENTATION, SCALAR_DESCRIPTOR_RESULT_COPY_REASON
    if native_array_descriptor_kind(semantic_type) == "allocatable":
        return BridgeDataAction.COPY_REPRESENTATION, OWNED_NATIVE_ARRAY_HANDLE_COPY_REASON
    if _is_first_lane_scalar_type(semantic_type):
        return BridgeDataAction.DIRECT_TRANSFER, None
    if _is_phase6_ordinary_array_type(semantic_type):
        return BridgeDataAction.COPY_REPRESENTATION, ORDINARY_ARRAY_RESULT_COPY_REASON
    if semantic_type.name == "String" and _character_length(semantic_type) is not None:
        return (
            BridgeDataAction.COPY_REPRESENTATION,
            FIXED_STRING_RESULT_COPY_REASON,
        )
    return BridgeDataAction.BLOCKED, None


def _argument_handoff_mode(decision: OwnershipDecision) -> ArgumentHandoffMode:
    """Return the completed ABI shape consumed by both backends."""
    if decision.python_barrier_action is PythonBarrierAction.RAW_ADDRESS:
        return ArgumentHandoffMode.OPAQUE_ADDRESS
    if decision.native_barrier_action is NativeBarrierAction.PASS_NATIVE_DESCRIPTOR:
        return ArgumentHandoffMode.NATIVE_DESCRIPTOR
    if decision.kind is ObjectKind.NUMPY_ARRAY:
        return ArgumentHandoffMode.ARRAY_BUFFER
    if decision.python_barrier_action in {
        PythonBarrierAction.STRING_STORAGE,
        PythonBarrierAction.RAW_ADDRESS,
    }:
        return ArgumentHandoffMode.OPAQUE_ADDRESS
    if decision.kind is ObjectKind.STRING:
        return ArgumentHandoffMode.CHARACTER_BUFFER
    if decision.python_barrier_action in {
        PythonBarrierAction.SCALAR_STORAGE,
        PythonBarrierAction.RAW_ADDRESS,
    }:
        return ArgumentHandoffMode.OPAQUE_ADDRESS
    if decision.native_barrier_action is NativeBarrierAction.PASS_VALUE:
        return ArgumentHandoffMode.VALUE
    return ArgumentHandoffMode.TYPED_REFERENCE


# Ordinary-array handoff policy.
def _array_handoff_policy(semantic_type: models.SemanticType) -> ArrayHandoffPolicy | None:
    """Copy structured buffer or raw-pointee facts into completed wrapper policy."""
    if _is_raw_array_address_type(semantic_type):
        return _raw_array_handoff_policy(semantic_type)
    storage = semantic_type.storage
    array = storage.array if storage is not None else None
    if array is None:
        return None
    assumed_rank = array.category == "assumed_rank"
    rank = None if assumed_rank else int(array.rank or semantic_type.rank or 0)
    if rank is not None and rank <= 0:
        return None
    shape = tuple(str(item) for item in (array.shape or semantic_type.shape))
    axes = tuple(str(item) for item in array.axes)
    return ArrayHandoffPolicy(
        rank=rank,
        shape=shape,
        axes=axes,
        order="ORDER_F" if assumed_rank and array.order is None else array.order,
        native_order=(
            "ORDER_F"
            if assumed_rank and array.order is None
            else (array.copy_order if array.copy_order is not None else array.order)
        ),
        contiguous=True if assumed_rank and array.contiguous is None else array.contiguous,
        itemsize=_character_length(semantic_type) if semantic_type.name == "String" else None,
        category=array.category,
        extent_references=tuple(_array_extent_references(item) for item in shape),
    )


def _is_phase6_ordinary_array_type(semantic_type: models.SemanticType) -> bool:
    """Return whether one type is an ordinary non-descriptor array buffer."""
    if _is_raw_array_address_type(semantic_type):
        return False
    array_policy = _array_handoff_policy(semantic_type)
    if array_policy is None:
        return False
    storage = semantic_type.storage
    array = storage.array if storage is not None else None
    return bool(
        array is not None
        and (
            semantic_type.name in _PLAN_PRIMITIVE_SCALAR_TYPES
            or (semantic_type.name == "String" and array_policy.itemsize is not None)
        )
        and (array_policy.rank is None or 1 <= array_policy.rank <= 15)
        and (array_policy.rank is None or len(array_policy.shape) == array_policy.rank)
        and (array_policy.rank is None or len(array_policy.axes) == array_policy.rank)
        and not array.allocatable
        and not array.pointer
    )


def _is_phase6_raw_array_address_type(semantic_type: models.SemanticType) -> bool:
    """Return whether one type is a supported concrete raw array pointee."""
    if not _is_raw_array_address_type(semantic_type):
        return False
    policy = _array_handoff_policy(semantic_type)
    if policy is None or policy.rank is None or not 1 <= policy.rank <= 15:
        return False
    if len(policy.shape) != policy.rank or len(policy.axes) != policy.rank:
        return False
    supported_element = semantic_type.name in _PLAN_PRIMITIVE_SCALAR_TYPES or (
        semantic_type.name == "String" and policy.itemsize is not None
    )
    return supported_element and all(item not in {":", "::Strided", "...", "Flat"} for item in policy.shape)


def _is_raw_array_address_type(semantic_type: models.SemanticType) -> bool:
    """Return whether one positive-rank type carries the public raw-address role."""
    storage = semantic_type.storage
    return bool(
        semantic_type.rank > 0
        and storage is not None
        and storage.kind == "address"
        and storage.metadata.get(ADDRESS_ROLE_METADATA) == ADDRESS_ROLE_RAW
    )


def _raw_array_handoff_policy(semantic_type: models.SemanticType) -> ArrayHandoffPolicy:
    """Complete dense raw-pointee shape and orientation before lowering."""
    rank = int(semantic_type.rank or 0)
    shape = tuple(str(item) for item in semantic_type.shape)
    storage = semantic_type.storage
    array = storage.array if storage is not None else None
    order = array.order if array is not None and array.order is not None else ("ORDER_C" if rank > 1 else None)
    return ArrayHandoffPolicy(
        rank=rank,
        shape=shape,
        axes=("dense",) * rank,
        order=order,
        native_order=order,
        contiguous=True,
        itemsize=_character_length(semantic_type) if semantic_type.name == "String" else None,
        category="raw_address",
        extent_references=tuple(_array_extent_references(item) for item in shape),
    )


def _array_extent_references(expression: str) -> tuple[str, ...]:
    """Return stable scalar names used by one declared extent expression."""
    if expression in {":", "::Strided", "...", "Flat"}:
        return ()
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError:
        return ("<invalid>",)
    if not _valid_array_extent_expression(tree):
        return ("<invalid>",)
    return tuple(dict.fromkeys(node.id for node in ast.walk(tree) if isinstance(node, ast.Name)))


def _valid_array_extent_expression(tree: ast.AST) -> bool:
    """Return whether an extent uses only integer arithmetic and scalar names."""
    allowed = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Name,
        ast.Load,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.FloorDiv,
        ast.Div,
        ast.Mod,
        ast.USub,
        ast.UAdd,
    )
    return all(isinstance(node, allowed) and _is_integer_constant(node) for node in ast.walk(tree))


def _is_integer_constant(node: ast.AST) -> bool:
    return not isinstance(node, ast.Constant) or (isinstance(node.value, int) and not isinstance(node.value, bool))


def _array_extent_reference_blockers(
    function: models.SemanticFunction,
    arguments: list[ArgumentPolicy],
    results: tuple[ResultPolicy, ...],
) -> tuple[str, ...]:
    """Require every declared extent name to come from a visible scalar argument."""
    scalar_names = {
        argument.name
        for argument in function.arguments
        if int(argument.semantic_type.rank or 0) == 0
        and (decision := _ownership_decision(argument, models.RESOLVED_OWNERSHIP_POLICY_METADATA)) is not None
        and decision.python_visible
    }
    blockers = []
    for owner in (*arguments, *results):
        if owner.array is None:
            continue
        for axis, references in enumerate(owner.array.extent_references):
            missing = tuple(name for name in references if name not in scalar_names)
            if missing:
                blockers.append(
                    f"array owner {owner.owner_path!r} extent axis {axis} has unavailable scalar references {missing}"
                )
    return tuple(blockers)


def _argument_result_position(function: models.SemanticFunction, python_position: int) -> int | None:
    """Return one visible argument's completed projected result position."""
    for mapping in function.projection:
        if mapping.python_position == python_position and mapping.result_position is not None:
            return int(mapping.result_position)
    return None


def _visible_projected_arguments(function: models.SemanticFunction) -> tuple[models.SemanticArgument, ...]:
    """Return Python-visible arguments whose completed policy projects results."""
    return tuple(
        argument
        for argument in function.arguments
        if (
            (decision := _ownership_decision(argument, models.RESOLVED_OWNERSHIP_POLICY_METADATA)) is not None
            and decision.projects_result
            and decision.python_visible
        )
    )


def _native_name(function: models.SemanticFunction) -> str:
    return str(function.native_name or function.origin.native_name or function.name)


def _native_module(function: models.SemanticFunction, owner_path: str) -> str | None:
    """Return the completed native module scope for non-external procedures."""
    if _is_external(function):
        return None
    return str(function.origin.native_scope or owner_path.split(".", maxsplit=1)[0])


def _native_is_subroutine(function: models.SemanticFunction) -> bool:
    """Return whether the native callable has subroutine call semantics."""
    return function.origin.source_kind == "subroutine" or function.return_type is None


def _is_external(function: models.SemanticFunction) -> bool:
    return bool(function.origin.source_language == "fortran" and function.origin.native_scope is None)


def _argument_native_name(
    function: models.SemanticFunction,
    python_position: int,
    argument: models.SemanticArgument,
) -> str:
    for mapping in function.projection:
        if mapping.python_position == python_position:
            return mapping.native_name or argument.name
    return argument.name
