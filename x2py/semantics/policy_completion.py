"""Complete post-IR semantic policies before readiness or lowering."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import replace

from x2py.numpy_types import SEMANTIC_SCALAR_TYPE_NAMES
from x2py.ownership_policy import (
    DestructionPolicy,
    OWNERSHIP_POLICY_METADATA,
    POINTER_POLICY_METADATA,
    OwnershipDecision,
    OwnershipContext,
    OwnershipOwner,
    SetterAction,
    TransferMode,
    default_ownership_policy,
    ownership_context_for_argument,
)
from x2py.semantic_metadata import (
    ADDRESS_ROLE_METADATA,
    ADDRESS_ROLE_PROJECTION,
    ADDRESS_ROLE_RAW,
    OPTIONAL_ABSENT_HANDLE_METADATA,
    PROJECTED_OUTPUT_METADATA,
    SCALAR_STORAGE_CATEGORY,
    SNAPSHOT_TYPE_METADATA,
)
from x2py.semantics import models
from x2py.semantics.native_array_handles import NativeArrayHandlePolicy, native_array_descriptor_kind

__all__ = ("complete_semantic_policies",)


_UNSUPPORTED_SNAPSHOT_CONTRACT = (
    "Snapshot[T] is not an active semantic .pyi contract; whole-object snapshots are future-only"
)
_POINTER_ALLOCATE_PERMISSION_VALUES = frozenset(
    {
        "allocate",
        "allocate_resize",
        "reallocate",
        "reassociate_allocate",
    }
)
_POINTER_DEALLOCATE_PERMISSION_VALUES = frozenset(
    {
        "deallocate",
        "deallocate_resize",
        "owner_deallocate",
        "unsafe_deallocate",
        "wrapper_dealloc",
    }
)
_POINTER_RESIZE_PERMISSION_VALUES = frozenset(
    {
        "resize",
        "allocate_resize",
        "deallocate_resize",
        "reallocate",
    }
)


def complete_semantic_policies(
    semantic_ir: models.SemanticModule | Iterable[models.SemanticModule],
) -> list[models.SemanticModule]:
    """Complete policy decisions for semantic modules after parser-to-IR conversion.

    This is the shared post-IR boundary for policies that need full semantic
    context. It completes entry export reachability, ownership, transfer, destruction,
    mutability/writeback, projection, nullability, release, codegen action, and
    contract/boundary storage modes, getter behavior, native setter assignment,
    and Python setter exposure. Future policy passes must be added here instead
    of in readiness, lowering, bridges, or bindings.
    """

    modules = list(semantic_ir) if not isinstance(semantic_ir, models.SemanticModule) else [semantic_ir]
    for module in modules:
        _complete_entry_export_policy(module)
        _complete_ownership_policies(module)
    return modules


def _complete_entry_export_policy(module: models.SemanticModule) -> None:
    """Remove public declarations not reachable from an explicit entry export policy."""
    if not module.metadata.get(models.PYTHON_EXPORTS_PREPARED_METADATA):
        return
    module.variables = [variable for variable in module.variables if _is_entry_export_reachable(variable)]
    module.functions = [function for function in module.functions if _is_entry_export_reachable(function)]
    module.overload_sets = [
        overload_set for overload_set in module.overload_sets if _is_entry_export_reachable(overload_set)
    ]


def _is_entry_export_reachable(declaration: object) -> bool:
    if getattr(declaration, "visibility", "public") == "private":
        return True
    return bool(_entry_exports(declaration))


def _entry_exports(declaration: object) -> object:
    if isinstance(declaration, models.ProcedureOverloadSet):
        if not declaration.procedures:
            return ()
        return declaration.procedures[0].metadata.get(models.PYTHON_EXPORTS_METADATA, ())
    if isinstance(declaration, models.SemanticVariable | models.SemanticFunction | models.SemanticClass):
        return declaration.metadata.get(models.PYTHON_EXPORTS_METADATA, ())
    raise TypeError(f"Unsupported semantic declaration: {type(declaration).__name__}")


def _complete_ownership_policies(module: models.SemanticModule) -> models.SemanticModule:
    """Attach resolved ownership decisions to a full semantic module.

    Raw semantic types such as ``Float64[:]`` do not carry enough context to
    decide boundary behavior or storage. This pass runs after complete
    signatures are known and before ``ir2ast`` lowering.
    """

    for variable in module.variables:
        _complete_variable(variable, OwnershipContext.module_variable())
        _complete_accessor_policies(variable, OwnershipContext.module_variable())
        _complete_module_variable_initializer(variable)
        _block_unsupported_snapshot_contract(variable)
    for semantic_class in module.classes:
        _complete_class(semantic_class)
    for function in module.functions:
        _complete_function(function)
    for overload_set in module.overload_sets:
        for procedure in overload_set.procedures:
            _complete_function(procedure)
    module.metadata[models.POLICY_COMPLETION_PREPARED_METADATA] = True
    return module


def _block_unsupported_snapshot_contract(variable: models.SemanticVariable) -> None:
    """Turn stale Snapshot IR metadata into an explicit post-IR blocker."""
    if not variable.semantic_type.metadata.get(SNAPSHOT_TYPE_METADATA):
        return
    decision = variable.metadata[models.RESOLVED_OWNERSHIP_POLICY_METADATA]
    blocked = _blocked_snapshot_decision(decision)
    variable.metadata[models.RESOLVED_OWNERSHIP_POLICY_METADATA] = blocked
    variable.metadata[models.RESOLVED_GETTER_OWNERSHIP_POLICY_METADATA] = blocked
    variable.metadata[models.RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA] = replace(
        blocked,
        setter_action=SetterAction.OMIT,
    )
    variable.semantic_type.metadata.pop(SNAPSHOT_TYPE_METADATA, None)


def _blocked_snapshot_decision(decision: OwnershipDecision) -> OwnershipDecision:
    return replace(
        decision,
        owner=OwnershipOwner.UNKNOWN,
        transfer=TransferMode.BLOCKED,
        destruction=DestructionPolicy.BLOCKED,
        borrowed=False,
        blocker=_UNSUPPORTED_SNAPSHOT_CONTRACT,
        reason="whole-object snapshots are not part of the active contract",
    )


def _complete_class(semantic_class: models.SemanticClass) -> None:
    class_type = models.SemanticType(name=semantic_class.name, dtype=semantic_class.name)
    semantic_class.metadata[models.RESOLVED_CLASS_INSTANCE_POLICY_METADATA] = (
        default_ownership_policy.decide_semantic_type(class_type, OwnershipContext.result())
    )
    semantic_class.metadata[models.RESOLVED_CLASS_SELF_POLICY_METADATA] = default_ownership_policy.decide_semantic_type(
        class_type,
        OwnershipContext.argument(writes_argument=True),
    )
    for field in semantic_class.fields:
        _complete_variable(field, OwnershipContext.field())
        _complete_accessor_policies(field, OwnershipContext.field())
    for nested in semantic_class.classes:
        _complete_class(nested)
    for method in semantic_class.methods:
        _complete_function(method)
    for overload_set in semantic_class.overload_sets:
        for procedure in overload_set.procedures:
            _complete_function(procedure)


def _complete_function(function: models.SemanticFunction) -> None:
    _complete_callable_address_policy(function)
    for argument in function.arguments:
        _complete_variable(argument, ownership_context_for_argument(function, argument))
    if function.return_type is not None:
        decision = default_ownership_policy.decide_semantic_type(function.return_type, OwnershipContext.result())
        function.metadata[models.RESOLVED_RETURN_OWNERSHIP_POLICY_METADATA] = decision
        _complete_native_array_handle_result_policy(function, decision)
    else:
        function.metadata.pop(models.RESOLVED_RETURN_OWNERSHIP_POLICY_METADATA, None)
        function.metadata.pop(models.RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA, None)


def _complete_native_array_handle_result_policy(
    function: models.SemanticFunction,
    decision: OwnershipDecision,
) -> None:
    return_type = function.return_type
    descriptor_kind = native_array_descriptor_kind(return_type)
    if descriptor_kind is None or return_type is None:
        function.metadata.pop(models.RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA, None)
        return
    policy = _native_array_handle_policy(
        descriptor_kind,
        return_type,
        decision,
        OwnershipContext.result(),
    )
    function.metadata[models.RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA] = policy


def _complete_native_array_handle_variable_policy(
    variable: models.SemanticVariable,
    context: OwnershipContext,
) -> None:
    descriptor_kind = native_array_descriptor_kind(variable.semantic_type)
    if descriptor_kind is None:
        variable.metadata.pop(models.RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA, None)
        return
    decision = variable.metadata[models.RESOLVED_OWNERSHIP_POLICY_METADATA]
    policy = _native_array_handle_policy(
        descriptor_kind,
        variable.semantic_type,
        decision,
        context,
        variable=variable,
    )
    variable.metadata[models.RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA] = policy


def _native_array_handle_policy(
    descriptor_kind: str,
    semantic_type: models.SemanticType,
    decision: OwnershipDecision,
    context: OwnershipContext,
    *,
    variable: models.SemanticVariable | None = None,
) -> NativeArrayHandlePolicy:
    optional_absent = bool(
        variable is not None and variable.optional and semantic_type.metadata.get(OPTIONAL_ABSENT_HANDLE_METADATA)
    )
    handle_kind = _native_array_handle_kind(descriptor_kind, context, optional_absent=optional_absent)
    blocker = _native_array_handle_blocker(descriptor_kind, handle_kind, decision)
    descriptor_ownership = _native_array_descriptor_ownership(handle_kind)
    to_numpy = _native_array_to_numpy_policy(descriptor_kind, handle_kind, decision, semantic_type)
    return NativeArrayHandlePolicy(
        descriptor_kind=descriptor_kind,
        handle_kind=handle_kind,
        origin=_native_array_handle_origin(context),
        owner=_native_array_handle_owner(handle_kind),
        owner_retention=_native_array_owner_retention(handle_kind),
        descriptor_ownership=descriptor_ownership,
        borrowed=descriptor_ownership == "borrowed",
        getter_behavior=_native_array_getter_behavior(handle_kind, context, blocker),
        python_setter=_native_array_python_setter(variable),
        native_setter=_native_array_native_setter(variable),
        output_projection=_native_array_output_projection(descriptor_kind, handle_kind, context),
        release=_native_array_release_responsibility(handle_kind),
        target_lifetime=_native_array_target_lifetime(descriptor_kind, handle_kind, semantic_type, blocker),
        destroy_behavior=_native_array_destroy_behavior(handle_kind, blocker),
        to_numpy=to_numpy,
        descriptor_interop=_native_array_descriptor_interop_requirement(descriptor_kind, handle_kind),
        nullable=bool(decision.nullable or optional_absent),
        optional_absent=optional_absent,
        storage_mode=decision.storage_mode.value,
        operations=_native_array_handle_operations(descriptor_kind, handle_kind, context, semantic_type),
        blocker=blocker,
    )


def _native_array_handle_kind(
    descriptor_kind: str,
    context: OwnershipContext,
    *,
    optional_absent: bool,
) -> str:
    if optional_absent:
        return "optional_absent_handle"
    if context.is_module_variable:
        return "borrowed_module_descriptor"
    if context.is_field:
        return "borrowed_field_descriptor"
    if context.is_argument and context.projects_result and not context.python_visible:
        if descriptor_kind == "allocatable":
            return "owned_result_descriptor"
        return "unsupported"
    if context.is_argument:
        return "argument_descriptor"
    if context.is_result and descriptor_kind == "allocatable":
        return "owned_result_descriptor"
    return "unsupported"


def _native_array_handle_origin(context: OwnershipContext) -> str:
    if context.is_module_variable:
        return "module_variable"
    if context.is_field:
        return "derived_field"
    if context.is_argument:
        if context.projects_result and not context.python_visible:
            return "projected_result"
        return "argument"
    if context.is_result:
        return "result"
    return "unknown"


def _native_array_handle_owner(handle_kind: str) -> str:
    return {
        "argument_descriptor": "caller",
        "borrowed_field_descriptor": "wrapper",
        "borrowed_module_descriptor": "native",
        "optional_absent_handle": "caller",
        "owned_result_descriptor": "wrapper",
    }.get(handle_kind, "unknown")


def _native_array_owner_retention(handle_kind: str) -> str:
    return {
        "argument_descriptor": "caller_handle",
        "borrowed_field_descriptor": "parent_wrapper",
        "borrowed_module_descriptor": "native_module",
        "optional_absent_handle": "optional_argument",
        "owned_result_descriptor": "wrapper_owner_storage",
    }.get(handle_kind, "unknown")


def _native_array_descriptor_ownership(handle_kind: str) -> str:
    if handle_kind == "owned_result_descriptor":
        return "owned"
    if handle_kind == "unsupported":
        return "unknown"
    return "borrowed"


def _native_array_getter_behavior(handle_kind: str, context: OwnershipContext, blocker: str | None) -> str:
    if blocker is not None:
        return "blocked"
    if context.is_module_variable or context.is_field:
        return "handle"
    if handle_kind == "owned_result_descriptor":
        return "return_handle"
    return "none"


def _native_array_python_setter(variable: models.SemanticVariable | None) -> str:
    setter = None if variable is None else variable.metadata.get(models.RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA)
    if setter is None:
        return "none"
    return setter.setter_action.value


def _native_array_native_setter(variable: models.SemanticVariable | None) -> str:
    setter = None if variable is None else variable.metadata.get(models.RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA)
    if setter is None:
        return "none"
    return setter.assignment_mode.value


def _native_array_output_projection(
    descriptor_kind: str,
    handle_kind: str,
    context: OwnershipContext,
) -> str:
    if handle_kind == "unsupported":
        return "unsupported"
    if context.is_result:
        return "handle_result" if descriptor_kind == "allocatable" else "unsupported"
    if context.is_argument and context.projects_result:
        return "projected_handle"
    return "none"


def _native_array_release_responsibility(handle_kind: str) -> str:
    return {
        "argument_descriptor": "none",
        "borrowed_field_descriptor": "wrapper_dealloc",
        "borrowed_module_descriptor": "native_owner",
        "optional_absent_handle": "none",
        "owned_result_descriptor": "wrapper_dealloc",
        "unsupported": "blocked",
    }[handle_kind]


def _native_array_target_lifetime(
    descriptor_kind: str,
    handle_kind: str,
    semantic_type: models.SemanticType,
    blocker: str | None,
) -> str:
    if handle_kind == "unsupported":
        return "unknown"
    if descriptor_kind == "pointer":
        pointer_lifetime = _pointer_policy_value(_pointer_policy_metadata(semantic_type), "lifetime")
        if pointer_lifetime:
            return pointer_lifetime
        if blocker is not None and handle_kind in {"borrowed_field_descriptor", "borrowed_module_descriptor"}:
            return "unknown"
    return {
        "argument_descriptor": "call",
        "borrowed_field_descriptor": "parent_wrapper",
        "borrowed_module_descriptor": "module",
        "optional_absent_handle": "absent_or_call",
        "owned_result_descriptor": "wrapper_owner_storage",
    }[handle_kind]


def _native_array_destroy_behavior(handle_kind: str, blocker: str | None) -> str:
    if handle_kind == "unsupported" or (
        blocker is not None
        and any(reason in blocker for reason in ("release policy", "stable owner storage", "target lifetime"))
    ):
        return "blocked"
    return {
        "argument_descriptor": "none",
        "borrowed_field_descriptor": "parent_wrapper_finalizer",
        "borrowed_module_descriptor": "none",
        "optional_absent_handle": "none",
        "owned_result_descriptor": "handle_finalizer",
        "unsupported": "blocked",
    }[handle_kind]


def _native_array_to_numpy_policy(
    descriptor_kind: str,
    handle_kind: str,
    decision: OwnershipDecision,
    semantic_type: models.SemanticType,
) -> str:
    if handle_kind == "unsupported":
        return "unsupported"
    if descriptor_kind == "pointer":
        return _native_array_pointer_to_numpy_policy(semantic_type)
    if decision.is_blocked:
        return "unsupported"
    if handle_kind == "borrowed_module_descriptor" and not decision.borrowed:
        return "read_only_detached_copy"
    return "borrowed_view"


def _native_array_pointer_to_numpy_policy(semantic_type: models.SemanticType) -> str:
    pointer_policy = _pointer_policy_metadata(semantic_type)
    if not pointer_policy:
        return "unsupported"
    if _pointer_policy_value(pointer_policy, "contiguity") == "contiguous":
        if _pointer_policy_requests_copy_extraction(pointer_policy):
            return "copy_only"
        return "contiguous_view"
    return "descriptor_view"


def _pointer_policy_requests_copy_extraction(policy: dict[str, object]) -> bool:
    return (
        _pointer_policy_value(policy, "transfer") == "snapshot_copy"
        or _pointer_policy_value(policy, "aliasing") == "independent_copy"
        or _pointer_policy_value(policy, "mutability") == "copy"
    )


def _native_array_handle_operations(
    descriptor_kind: str,
    handle_kind: str,
    context: OwnershipContext,
    semantic_type: models.SemanticType,
) -> tuple[str, ...]:
    if handle_kind == "unsupported":
        return ()
    if descriptor_kind == "allocatable":
        operations = {"allocated", "to_numpy"}
        if handle_kind in {"borrowed_module_descriptor", "borrowed_field_descriptor", "owned_result_descriptor"} or (
            context.is_argument and context.writes_argument
        ):
            operations.update({"deallocate", "resize"})
        return tuple(sorted(operations))
    operations = {"associated", "nullify", "to_numpy"}
    pointer_policy = _pointer_policy_metadata(semantic_type)
    if _pointer_policy_allows_allocate(pointer_policy):
        operations.add("allocate")
    if _pointer_policy_allows_deallocate(pointer_policy):
        operations.add("deallocate")
    if _pointer_policy_allows_resize(pointer_policy):
        operations.add("resize")
    return tuple(sorted(operations))


def _native_array_descriptor_interop_requirement(descriptor_kind: str, handle_kind: str) -> str:
    if descriptor_kind == "allocatable" and handle_kind == "owned_result_descriptor":
        return "owned_allocatable_c_descriptor"
    if descriptor_kind == "pointer" and handle_kind != "unsupported":
        return "pointer_c_descriptor"
    return "none"


def _pointer_policy_metadata(semantic_type: models.SemanticType) -> dict[str, object]:
    policy = semantic_type.metadata.get(POINTER_POLICY_METADATA)
    return dict(policy) if isinstance(policy, dict) else {}


def _pointer_policy_value(policy: dict[str, object], key: str) -> str:
    value = policy.get(key)
    return str(value).strip().casefold() if isinstance(value, str) else ""


def _pointer_policy_allows_allocate(policy: dict[str, object]) -> bool:
    return _pointer_policy_value(policy, "reassociation") in _POINTER_ALLOCATE_PERMISSION_VALUES


def _pointer_policy_allows_deallocate(policy: dict[str, object]) -> bool:
    return _pointer_policy_value(policy, "deallocation") in _POINTER_DEALLOCATE_PERMISSION_VALUES


def _pointer_policy_allows_resize(policy: dict[str, object]) -> bool:
    reassociation = _pointer_policy_value(policy, "reassociation")
    deallocation = _pointer_policy_value(policy, "deallocation")
    return reassociation in _POINTER_RESIZE_PERMISSION_VALUES and deallocation in _POINTER_RESIZE_PERMISSION_VALUES


def _native_array_handle_blocker(
    descriptor_kind: str,
    handle_kind: str,
    decision: OwnershipDecision,
) -> str | None:
    if decision.is_blocked:
        return decision.blocker or decision.reason
    if handle_kind == "unsupported" and descriptor_kind == "pointer":
        return "pointer handle results need stable owner storage and target lifetime policy before wrapping"
    if handle_kind == "unsupported":
        return "native array handle origin is unsupported before wrapper lowering"
    return None


def _complete_callable_address_policy(function: models.SemanticFunction) -> None:
    """Validate Python/native address boundaries and complete scalar projections."""
    visible_scalar_names = {
        argument.name for argument in function.arguments if _is_visible_extent_source(argument.semantic_type)
    }
    for argument in function.arguments:
        _validate_raw_address_type(
            argument.semantic_type,
            owner=function.name,
            item=argument.name,
            visible_scalar_names=visible_scalar_names,
        )
    if function.return_type is not None:
        _validate_raw_address_type(
            function.return_type,
            owner=function.name,
            item="return",
            visible_scalar_names=visible_scalar_names,
        )
    _complete_native_address_projections(function)


def _complete_native_address_projections(function: models.SemanticFunction) -> None:
    arguments_by_name = {argument.name: argument for argument in function.arguments}
    for mapping in function.projection:
        if mapping.value_kind != "addr":
            continue
        value = mapping.value
        if not isinstance(value, dict) or value.get("kind") != "arg":
            raise ValueError(
                f"Invalid native Addr projection in {function.name!r}: only Addr(Arg(i)) is supported; "
                "Return and Work projections already name native storage."
            )
        argument = arguments_by_name.get(mapping.python_name)
        if argument is None:
            position = mapping.python_position
            if not isinstance(position, int) or not 0 <= position < len(function.arguments):
                raise ValueError(f"Invalid native Addr projection in {function.name!r}: argument is out of range")
            argument = function.arguments[position]
        if not _is_primitive_scalar_value(argument.semantic_type, allow_completed_projection=True):
            raise ValueError(
                f"Invalid native Addr projection for {function.name!r} argument {argument.name!r}: "
                "Addr(Arg(i)) is only valid for primitive scalar values; use Arg(i) for arrays, strings, "
                "scalar storage, wrapped objects, and raw addresses."
            )
        _apply_scalar_address_projection(argument)


def _apply_scalar_address_projection(argument: models.SemanticArgument) -> None:
    semantic_type = argument.semantic_type
    storage = semantic_type.storage
    metadata = dict(storage.metadata) if storage is not None else {}
    metadata[ADDRESS_ROLE_METADATA] = ADDRESS_ROLE_PROJECTION
    explicit_policy = semantic_type.metadata.get(OWNERSHIP_POLICY_METADATA)
    transfer = explicit_policy.get("transfer") if isinstance(explicit_policy, dict) else None
    projects_output = bool(argument.metadata.get(PROJECTED_OUTPUT_METADATA))
    read_only = transfer == "call_local" and not projects_output
    mutable = not read_only
    semantic_type.storage = models.SemanticStorageContract(
        kind="address",
        read_only=read_only,
        mutable=mutable,
        pointer_depth=1,
        ownership=storage.ownership if storage is not None else "borrowed",
        calling_convention=storage.calling_convention if storage is not None else None,
        metadata=metadata,
    )
    semantic_type.ownership.mutable = mutable


def _is_primitive_scalar_value(
    semantic_type: models.SemanticType,
    *,
    allow_completed_projection: bool = False,
) -> bool:
    if semantic_type.rank != 0 or semantic_type.name == "String":
        return False
    if (semantic_type.dtype or semantic_type.name) not in SEMANTIC_SCALAR_TYPE_NAMES:
        return False
    storage = semantic_type.storage
    if storage is None or storage.kind == "value":
        return True
    return bool(
        allow_completed_projection
        and storage.kind == "address"
        and storage.pointer_depth == 1
        and storage.metadata.get(ADDRESS_ROLE_METADATA) == ADDRESS_ROLE_PROJECTION
    )


def _is_visible_extent_source(semantic_type: models.SemanticType) -> bool:
    if _is_primitive_scalar_value(semantic_type, allow_completed_projection=True):
        return True
    storage = semantic_type.storage
    return bool(
        semantic_type.rank == 0
        and semantic_type.name != "String"
        and (semantic_type.dtype or semantic_type.name) in SEMANTIC_SCALAR_TYPE_NAMES
        and storage is not None
        and storage.array is not None
        and storage.array.category == SCALAR_STORAGE_CATEGORY
    )


def _validate_raw_address_type(
    semantic_type: models.SemanticType,
    *,
    owner: str,
    item: str,
    visible_scalar_names: set[str],
) -> None:
    storage = semantic_type.storage
    if storage is None or storage.metadata.get(ADDRESS_ROLE_METADATA) != ADDRESS_ROLE_RAW:
        return
    if storage.pointer_depth != 1:
        raise ValueError(
            f"Invalid raw address contract for {owner!r} {item!r}: callable Addr(T) supports depth one only."
        )
    if semantic_type.rank > 0:
        if (semantic_type.dtype or semantic_type.name) not in SEMANTIC_SCALAR_TYPE_NAMES:
            raise ValueError(
                f"Invalid raw address contract for {owner!r} {item!r}: raw arrays require a primitive dtype."
            )
        dimensions = _semantic_shape(semantic_type)
        if len(dimensions) != semantic_type.rank or not all(
            _is_resolved_extent(dimension, visible_scalar_names) for dimension in dimensions
        ):
            raise ValueError(
                f"Invalid raw address contract for {owner!r} {item!r}: raw arrays require a fully resolved "
                "rank and shape using literals or visible scalar arguments."
            )
        return
    if semantic_type.name == "String":
        length = semantic_type.metadata.get("fortran_character_length")
        if length is None or not _is_resolved_extent(length, visible_scalar_names):
            raise ValueError(
                f"Invalid raw address contract for {owner!r} {item!r}: raw strings require a fixed length."
            )
        return
    if (semantic_type.dtype or semantic_type.name) not in SEMANTIC_SCALAR_TYPE_NAMES:
        raise ValueError(
            f"Invalid raw address contract for {owner!r} {item!r}: Addr(WrappedType) is not allowed; "
            "use WrappedType and Arg(i)."
        )


def _semantic_shape(semantic_type: models.SemanticType) -> list[str]:
    if semantic_type.shape:
        return [str(dimension) for dimension in semantic_type.shape]
    storage = semantic_type.storage
    array = storage.array if storage is not None else None
    if array is None:
        return []
    return [str(dimension) for dimension in (array.shape or array.source_shape)]


def _is_resolved_extent(value: object, visible_scalar_names: set[str]) -> bool:
    text = str(value).strip()
    if not text or text in {":", "*", "...", ".."} or ":" in text:
        return False
    names = set(re.findall(r"\b[A-Za-z_]\w*\b", text))
    return names <= visible_scalar_names


def _complete_variable(variable: models.SemanticVariable, context: OwnershipContext) -> None:
    decision = default_ownership_policy.decide_semantic_variable(variable, context)
    variable.metadata[models.RESOLVED_OWNERSHIP_POLICY_METADATA] = decision
    _complete_callable_policy(variable.semantic_type)
    _complete_native_array_handle_variable_policy(variable, context)


def _complete_accessor_policies(variable: models.SemanticVariable, context: OwnershipContext) -> None:
    variable.metadata[models.RESOLVED_GETTER_OWNERSHIP_POLICY_METADATA] = (
        default_ownership_policy.decide_semantic_getter(variable, context)
    )
    variable.metadata[models.RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA] = (
        default_ownership_policy.decide_semantic_setter(variable, context)
    )
    _complete_native_array_handle_variable_policy(variable, context)


def _complete_module_variable_initializer(variable: models.SemanticVariable) -> None:
    variable.metadata.pop(models.RESOLVED_MODULE_VARIABLE_INITIALIZER_METADATA, None)
    _clear_readiness_blocker(variable, models.MODULE_VARIABLE_INITIALIZER_UNSUPPORTED_BLOCKER)
    if variable.default_value is None or _is_constant(variable):
        return
    setter = variable.metadata[models.RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA]
    if variable.semantic_type.rank != 0:
        _add_readiness_blocker(
            variable,
            models.MODULE_VARIABLE_INITIALIZER_UNSUPPORTED_BLOCKER,
            "Module variable initializers require scalar storage with a write-through native setter.",
            {
                "item": variable.name,
                "rank": variable.semantic_type.rank,
                "reason": "only scalar module variables support import-time native initialization",
            },
        )
        return
    if setter.setter_action is not SetterAction.WRITE_THROUGH:
        _add_readiness_blocker(
            variable,
            models.MODULE_VARIABLE_INITIALIZER_UNSUPPORTED_BLOCKER,
            "Module variable initializers require scalar storage with a write-through native setter.",
            {
                "item": variable.name,
                "setter_action": setter.setter_action.value,
                "reason": "completed setter policy does not expose write-through native assignment",
            },
        )
        return
    variable.metadata[models.RESOLVED_MODULE_VARIABLE_INITIALIZER_METADATA] = variable.default_value


def _clear_readiness_blocker(variable: models.SemanticVariable, code: str) -> None:
    blockers = variable.metadata.get("readiness_blockers")
    if not isinstance(blockers, list):
        return
    remaining = [blocker for blocker in blockers if not isinstance(blocker, dict) or blocker.get("code") != code]
    if remaining:
        variable.metadata["readiness_blockers"] = remaining
    else:
        variable.metadata.pop("readiness_blockers", None)


def _add_readiness_blocker(
    variable: models.SemanticVariable,
    code: str,
    message: str,
    item: dict[str, object],
) -> None:
    variable.metadata.setdefault("readiness_blockers", []).append(
        {
            "code": code,
            "message": message,
            "item": item,
        }
    )


def _is_constant(variable: models.SemanticVariable) -> bool:
    return any(constraint.name == "Constant" for constraint in variable.semantic_type.constraints)


def _complete_callable_policy(semantic_type: models.SemanticType) -> None:
    if semantic_type.name != "Callable":
        return

    visible_scalar_names: set[str] = set()
    callback_arguments = semantic_type.metadata.get("callback_arguments")
    if isinstance(callback_arguments, list):
        visible_scalar_names = {
            argument.name
            for argument in callback_arguments
            if isinstance(argument, models.SemanticArgument) and _is_visible_extent_source(argument.semantic_type)
        }
        for argument in callback_arguments:
            if isinstance(argument, models.SemanticArgument):
                _validate_callback_argument_contract(argument)
                _validate_raw_address_type(
                    argument.semantic_type,
                    owner="Callable",
                    item=argument.name,
                    visible_scalar_names=visible_scalar_names,
                )
                _complete_variable(
                    argument,
                    _callback_argument_ownership_context(argument),
                )

    return_type = semantic_type.metadata.get("return")
    if isinstance(return_type, models.SemanticType) and return_type.name != "None":
        _validate_raw_address_type(
            return_type,
            owner="Callable",
            item="return",
            visible_scalar_names=visible_scalar_names,
        )
        decision = default_ownership_policy.decide_semantic_type(return_type, OwnershipContext.result())
        return_type.metadata[models.RESOLVED_OWNERSHIP_POLICY_METADATA] = decision


def _callback_argument_ownership_context(argument: models.SemanticArgument) -> OwnershipContext:
    if bool(getattr(argument.origin, "metadata", {}).get("value")):
        return OwnershipContext.argument(reads_argument=True, writes_argument=False)
    access = argument.metadata.get(models.CALLBACK_DECLARATION_ACCESS_METADATA, "read")
    match access:
        case "write":
            return OwnershipContext.argument(reads_argument=False, writes_argument=True)
        case "readwrite" | "unspecified":
            return OwnershipContext.argument(reads_argument=True, writes_argument=True)
        case _:
            return OwnershipContext.argument(reads_argument=True, writes_argument=False)


def _validate_callback_argument_contract(argument: models.SemanticArgument) -> None:
    semantic_type = argument.semantic_type
    if semantic_type.name != "String":
        return
    access = argument.metadata.get(models.CALLBACK_DECLARATION_ACCESS_METADATA, "read")
    if access == "read":
        return
    if bool(getattr(argument.origin, "metadata", {}).get("value")):
        return
    if _is_scalar_string_storage(semantic_type):
        return
    raise ValueError(
        "Writable callback strings require mutable scalar character storage; "
        "use String[n][()] inside Out(...), InOut(...), or missing-intent callback arguments"
    )


def _is_scalar_string_storage(semantic_type: models.SemanticType) -> bool:
    storage = semantic_type.storage
    array = storage.array if storage is not None else None
    return bool(
        storage is not None
        and storage.kind == "array"
        and array is not None
        and array.rank == 0
        and array.category == SCALAR_STORAGE_CATEGORY
    )
