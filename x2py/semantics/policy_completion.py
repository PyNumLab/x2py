"""Complete post-IR semantic policies before readiness or lowering."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import replace

from x2py.numpy_types import SEMANTIC_SCALAR_TYPE_NAMES
from x2py.ownership_policy import (
    DestructionPolicy,
    OWNERSHIP_POLICY_METADATA,
    ObjectKind,
    OwnershipDecision,
    OwnershipContext,
    OwnershipOwner,
    SetterAction,
    SnapshotFieldAction,
    TransferMode,
    default_ownership_policy,
    ownership_context_for_argument,
)
from x2py.semantic_metadata import (
    ADDRESS_ROLE_METADATA,
    ADDRESS_ROLE_PROJECTION,
    ADDRESS_ROLE_RAW,
    PROJECTED_OUTPUT_METADATA,
    SCALAR_STORAGE_CATEGORY,
    SNAPSHOT_TYPE_METADATA,
)
from x2py.semantics import models

__all__ = ("complete_semantic_policies",)


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

    class_lookup = _semantic_class_lookup(module)
    for variable in module.variables:
        _complete_variable(variable, OwnershipContext.module_variable())
        _complete_accessor_policies(variable, OwnershipContext.module_variable())
        _complete_module_variable_initializer(variable)
    for semantic_class in module.classes:
        _complete_class(semantic_class)
    _clear_snapshot_field_actions(module.classes)
    for variable in module.variables:
        _complete_module_snapshot_policy(variable, class_lookup)
    for function in module.functions:
        _complete_function(function)
    for overload_set in module.overload_sets:
        for procedure in overload_set.procedures:
            _complete_function(procedure)
    module.metadata[models.POLICY_COMPLETION_PREPARED_METADATA] = True
    return module


def _semantic_class_lookup(module: models.SemanticModule) -> dict[str, models.SemanticClass]:
    """Return all classes addressable by semantic type name in this module."""
    lookup: dict[str, models.SemanticClass] = {}

    def visit(semantic_class: models.SemanticClass) -> None:
        lookup.setdefault(semantic_class.name, semantic_class)
        if semantic_class.native_name:
            lookup.setdefault(semantic_class.native_name, semantic_class)
        for nested in semantic_class.classes:
            visit(nested)

    for semantic_class in module.classes:
        visit(semantic_class)
    return lookup


def _complete_module_snapshot_policy(
    variable: models.SemanticVariable,
    class_lookup: dict[str, models.SemanticClass],
) -> None:
    """Complete recursive snapshot eligibility for a derived module variable."""
    decision = variable.metadata[models.RESOLVED_OWNERSHIP_POLICY_METADATA]
    if not _is_module_derived_snapshot(decision, variable.semantic_type):
        if variable.semantic_type.metadata.get(SNAPSHOT_TYPE_METADATA):
            blocker = _invalid_snapshot_annotation_blocker(variable, decision)
            blocked = _blocked_snapshot_decision(decision, blocker)
            variable.metadata[models.RESOLVED_OWNERSHIP_POLICY_METADATA] = blocked
            variable.metadata[models.RESOLVED_GETTER_OWNERSHIP_POLICY_METADATA] = blocked
            variable.metadata[models.RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA] = replace(
                blocked,
                setter_action=SetterAction.OMIT,
            )
        else:
            variable.semantic_type.metadata.pop(SNAPSHOT_TYPE_METADATA, None)
        return

    blocker, actions = _snapshot_plan(variable.semantic_type, class_lookup, (variable.semantic_type.name,))
    if blocker is not None:
        blocked = _blocked_snapshot_decision(decision, blocker)
        variable.metadata[models.RESOLVED_OWNERSHIP_POLICY_METADATA] = blocked
        variable.metadata[models.RESOLVED_GETTER_OWNERSHIP_POLICY_METADATA] = blocked
        variable.metadata[models.RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA] = replace(
            blocked,
            setter_action=SetterAction.OMIT,
        )
        variable.semantic_type.metadata.pop(SNAPSHOT_TYPE_METADATA, None)
        return

    for field, action in actions:
        field.metadata[models.RESOLVED_SNAPSHOT_FIELD_ACTION_METADATA] = action
    variable.semantic_type.metadata[SNAPSHOT_TYPE_METADATA] = True


def _is_module_derived_snapshot(decision: OwnershipDecision, semantic_type: models.SemanticType) -> bool:
    return bool(
        decision.kind is ObjectKind.DERIVED_TYPE
        and decision.transfer is TransferMode.SNAPSHOT_COPY
        and semantic_type.rank == 0
    )


def _invalid_snapshot_annotation_blocker(
    variable: models.SemanticVariable,
    decision: OwnershipDecision,
) -> str:
    if decision.kind is not ObjectKind.DERIVED_TYPE or variable.semantic_type.rank != 0:
        return "Snapshot[T] is supported only for scalar derived module variables"
    return (
        f"Snapshot[{variable.semantic_type.name}] conflicts with the completed "
        f"{decision.transfer.value} transfer policy"
    )


def _blocked_snapshot_decision(decision: OwnershipDecision, blocker: str) -> OwnershipDecision:
    return replace(
        decision,
        owner=OwnershipOwner.UNKNOWN,
        transfer=TransferMode.BLOCKED,
        destruction=DestructionPolicy.BLOCKED,
        borrowed=False,
        blocker=blocker,
        reason="recursive derived module snapshot policy is incomplete",
    )


def _clear_snapshot_field_actions(classes: Iterable[models.SemanticClass]) -> None:
    for semantic_class in classes:
        for field in semantic_class.fields:
            field.metadata.pop(models.RESOLVED_SNAPSHOT_FIELD_ACTION_METADATA, None)
        _clear_snapshot_field_actions(semantic_class.classes)


def _snapshot_plan(
    semantic_type: models.SemanticType,
    class_lookup: dict[str, models.SemanticClass],
    stack: tuple[str, ...],
) -> tuple[str | None, list[tuple[models.SemanticField, SnapshotFieldAction]]]:
    semantic_class = class_lookup.get(semantic_type.name)
    if semantic_class is None:
        return f"snapshot type {semantic_type.name!r} is not declared in this module", []
    actions: list[tuple[models.SemanticField, SnapshotFieldAction]] = []
    for field in semantic_class.fields:
        blocker, field_actions = _snapshot_field_plan(field, class_lookup, stack)
        if blocker is not None:
            return blocker, []
        actions.extend(field_actions)
    return None, actions


def _snapshot_field_plan(
    field: models.SemanticField,
    class_lookup: dict[str, models.SemanticClass],
    stack: tuple[str, ...],
) -> tuple[str | None, list[tuple[models.SemanticField, SnapshotFieldAction]]]:
    path = ".".join((*stack, field.name))
    semantic_type = field.semantic_type
    blocker = _snapshot_field_storage_blocker(semantic_type, path)
    if blocker is not None:
        return blocker, []
    if semantic_type.name in class_lookup:
        return _snapshot_derived_field_plan(field, class_lookup, stack, path)
    return _snapshot_value_field_plan(field, path)


def _snapshot_field_storage_blocker(semantic_type: models.SemanticType, path: str) -> str | None:
    storage = semantic_type.storage
    array = storage.array if storage is not None else None
    if semantic_type.name in {"Callable", "Procedure", "Callback", "FunctionPointer", "CFunctionPointer"}:
        return f"snapshot field {path} is a procedure or callback"
    if semantic_type.metadata.get("fortran_assumed_type") or semantic_type.metadata.get("fortran_polymorphic"):
        return f"snapshot field {path} uses unsupported polymorphic or assumed-type storage"
    if array is not None and array.pointer:
        return f"snapshot field {path} is a pointer array without a completed pointer snapshot policy"
    if semantic_type.metadata.get("fortran_pointer") or (storage is not None and storage.pointer_depth > 0):
        return f"snapshot field {path} is pointer storage without a completed pointer snapshot policy"
    return None


def _snapshot_derived_field_plan(
    field: models.SemanticField,
    class_lookup: dict[str, models.SemanticClass],
    stack: tuple[str, ...],
    path: str,
) -> tuple[str | None, list[tuple[models.SemanticField, SnapshotFieldAction]]]:
    semantic_type = field.semantic_type
    if semantic_type.rank > 0 and semantic_type.name in class_lookup:
        return f"snapshot field {path} is an array of derived values", []
    if semantic_type.metadata.get("fortran_allocatable"):
        return f"snapshot field {path} is an allocatable derived scalar without a nullable copy policy", []
    if semantic_type.name in stack:
        return f"snapshot field {path} creates a recursive derived snapshot cycle", []
    blocker, nested_actions = _snapshot_plan(semantic_type, class_lookup, (*stack, semantic_type.name))
    if blocker is not None:
        return blocker, []
    return None, [(field, SnapshotFieldAction.NESTED_SNAPSHOT), *nested_actions]


def _snapshot_value_field_plan(
    field: models.SemanticField,
    path: str,
) -> tuple[str | None, list[tuple[models.SemanticField, SnapshotFieldAction]]]:
    semantic_type = field.semantic_type
    scalar_name = semantic_type.dtype or semantic_type.name
    if semantic_type.rank > 0:
        if scalar_name not in SEMANTIC_SCALAR_TYPE_NAMES or scalar_name == "Void":
            return f"snapshot field {path} has unsupported array element type {scalar_name!r}", []
        return None, [(field, SnapshotFieldAction.ARRAY_COPY)]
    if semantic_type.metadata.get("fortran_allocatable"):
        return f"snapshot field {path} is an allocatable scalar without a nullable copy policy", []
    if scalar_name not in SEMANTIC_SCALAR_TYPE_NAMES or scalar_name == "Void":
        return f"snapshot field {path} has no safe scalar copy policy for type {scalar_name!r}", []
    return None, [(field, SnapshotFieldAction.SCALAR_COPY)]


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
    else:
        function.metadata.pop(models.RESOLVED_RETURN_OWNERSHIP_POLICY_METADATA, None)


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


def _complete_accessor_policies(variable: models.SemanticVariable, context: OwnershipContext) -> None:
    variable.metadata[models.RESOLVED_GETTER_OWNERSHIP_POLICY_METADATA] = (
        default_ownership_policy.decide_semantic_getter(variable, context)
    )
    variable.metadata[models.RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA] = (
        default_ownership_policy.decide_semantic_setter(variable, context)
    )


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
