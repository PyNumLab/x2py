from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional, Any


# ============================================================
# Semantic Constraints
# ============================================================

@dataclass
class SemanticConstraint:
    name: str
    arguments: list[Any] = field(default_factory=list)


# ============================================================
# Semantic Coercions
# ============================================================

@dataclass
class SemanticCoercion:
    source_type: str
    implicit: bool = True
    cost: int = 1
    zero_copy: bool = False


# ============================================================
# Ownership / Lifetime
# ============================================================

@dataclass
class OwnershipPolicy:
    ownership: str = "borrowed"
    mutable: bool = False
    aliasing: bool = True


# ============================================================
# Semantic Types
# ============================================================

@dataclass
class SemanticType:
    name: str

    rank: int = 0

    dtype: Optional[str] = None

    shape: list[str] = field(default_factory=list)

    constraints: list[SemanticConstraint] = field(default_factory=list)

    coercions: list[SemanticCoercion] = field(default_factory=list)

    ownership: OwnershipPolicy = field(default_factory=OwnershipPolicy)

    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================
# Semantic Arguments
# ============================================================

@dataclass
class SemanticArgument:
    name: str

    semantic_type: SemanticType

    intent: str = "in"

    optional: bool = False
    visibility: str = "public"

    default_value: Optional[str] = None

    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================
# Semantic Contracts
# ============================================================

@dataclass
class SemanticContract:
    name: Optional[str] = None

    preconditions: list[str] = field(default_factory=list)

    postconditions: list[str] = field(default_factory=list)

    invariants: list[str] = field(default_factory=list)


# ============================================================
# API Projection
# ============================================================

@dataclass
class ProjectionMapping:
    python_name: Optional[str] = None
    native_name: str = ""
    native_position: Optional[int] = None
    python_position: Optional[int] = None
    result_position: Optional[int] = None
    value_kind: str = ""
    value: Any = None
    intent: str = "in"


# ============================================================
# Semantic Functions
# ============================================================

@dataclass(eq=False)
class SemanticFunction:
    name: str

    native_name: Optional[str] = None

    arguments: list[SemanticArgument] = field(default_factory=list)

    return_type: Optional[SemanticType] = None

    contracts: list[SemanticContract] = field(default_factory=list)

    projection: list[ProjectionMapping] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)
    visibility: str = "public"

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return False
        if not isinstance(other, SemanticFunction):
            return False

        self_call_args = _call_arguments(self)
        other_call_args = _call_arguments(other)
        self_name_map = _argument_name_map(self_call_args)
        other_name_map = _argument_name_map(other_call_args)
        return (
            self.name,
            self.native_name,
            _function_arguments_key(self_call_args, self_name_map),
            _return_projection_key(self, self_name_map),
            self.contracts,
            _projection_key(self.projection, self_name_map),
            self.metadata,
            self.visibility,
            getattr(self, "is_static", None),
        ) == (
            other.name,
            other.native_name,
            _function_arguments_key(other_call_args, other_name_map),
            _return_projection_key(other, other_name_map),
            other.contracts,
            _projection_key(other.projection, other_name_map),
            other.metadata,
            other.visibility,
            getattr(other, "is_static", None),
        )


# ============================================================
# Semantic Methods
# ============================================================

@dataclass(eq=False)
class SemanticMethod(SemanticFunction):
    is_static: bool = False


def _call_arguments(func: SemanticFunction) -> list[SemanticArgument]:
    return [arg for arg in func.arguments if getattr(arg, "intent", "in") != "out"]


def _argument_name_map(arguments: list[SemanticArgument]) -> dict[str, str]:
    return {arg.name: f"__arg_{i}__" for i, arg in enumerate(arguments)}


def _function_arguments_key(
    arguments: list[SemanticArgument],
    name_map: dict[str, str],
) -> tuple[tuple[Any, ...], ...]:
    return tuple(_function_argument_key(arg, name_map) for arg in arguments)


def _function_argument_key(
    arg: SemanticArgument,
    name_map: dict[str, str],
) -> tuple[Any, ...]:
    return (
        _semantic_type_key(arg.semantic_type, name_map),
        arg.intent,
        arg.optional,
        arg.visibility,
        _canonical_expression(arg.default_value, name_map),
        arg.metadata,
    )


def _semantic_type_key(
    semantic_type: SemanticType | None,
    name_map: dict[str, str],
    *,
    include_ownership: bool = True,
) -> tuple[Any, ...] | None:
    if semantic_type is None:
        return None
    return (
        semantic_type.name,
        semantic_type.rank,
        semantic_type.dtype,
        tuple(_canonical_expression(item, name_map) for item in semantic_type.shape),
        tuple(_constraint_key(c, name_map) for c in semantic_type.constraints),
        tuple(semantic_type.coercions),
        semantic_type.ownership if include_ownership else None,
        semantic_type.metadata,
    )


def _return_projection_key(
    func: SemanticFunction,
    name_map: dict[str, str],
) -> tuple[tuple[Any, ...], ...]:
    returns: list[tuple[Any, ...]] = []
    if func.return_type is not None:
        returns.append((_semantic_type_key(func.return_type, name_map, include_ownership=False),))
    returns.extend(
        (_semantic_type_key(arg.semantic_type, name_map, include_ownership=False),)
        for arg in func.arguments
        if getattr(arg, "intent", "in") in {"out", "inout"}
    )
    return tuple(returns)


def _projection_key(
    projection: list[ProjectionMapping],
    name_map: dict[str, str],
) -> tuple[tuple[Any, ...], ...]:
    return tuple(
        (
            mapping.native_position,
            mapping.python_position,
            mapping.result_position,
            mapping.value_kind,
            _native_projection_value_key(mapping.value, name_map),
            mapping.intent,
        )
        for mapping in projection
        if _requires_explicit_projection_mapping(mapping)
    )


def _requires_explicit_projection_mapping(mapping: ProjectionMapping) -> bool:
    if mapping.value_kind:
        return True
    if mapping.intent == "inout":
        return mapping.python_position != mapping.native_position
    if mapping.intent != "in":
        return mapping.python_position is None
    if mapping.result_position is not None:
        return True
    if mapping.python_position is None:
        return True
    return mapping.native_position is not None and mapping.python_position != mapping.native_position


def _native_projection_value_key(value: Any, name_map: dict[str, str]) -> Any:
    if isinstance(value, dict):
        return tuple(
            sorted(
                (key, _native_projection_value_key(item, name_map))
                for key, item in value.items()
            )
        )
    if isinstance(value, (list, tuple)):
        return tuple(_native_projection_value_key(item, name_map) for item in value)
    return _canonical_expression(value, name_map)


def _constraint_key(
    constraint: SemanticConstraint,
    name_map: dict[str, str],
) -> tuple[Any, ...]:
    return (
        constraint.name,
        tuple(_canonical_expression(arg, name_map) for arg in constraint.arguments),
    )


def _canonical_expression(value: Any, name_map: dict[str, str]) -> Any:
    if isinstance(value, str):
        return _canonical_expression_text(value, name_map)
    if isinstance(value, list):
        return [_canonical_expression(item, name_map) for item in value]
    if isinstance(value, tuple):
        return tuple(_canonical_expression(item, name_map) for item in value)
    if isinstance(value, dict):
        return {
            _canonical_expression(key, name_map): _canonical_expression(item, name_map)
            for key, item in value.items()
        }
    return value


def _canonical_expression_text(text: str, name_map: dict[str, str]) -> str:
    if not name_map:
        return text
    result = text
    for name, placeholder in name_map.items():
        result = re.sub(rf"\b{re.escape(name)}\b", placeholder, result)
    return result


# ============================================================
# Semantic Classes
# ============================================================

@dataclass
class SemanticClass:
    name: str

    native_name: Optional[str] = None

    fields: list[SemanticArgument] = field(default_factory=list)

    methods: list[SemanticMethod] = field(default_factory=list)

    base_classes: list[str] = field(default_factory=list)

    contracts: list[SemanticContract] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)
    visibility: str = "public"


# ============================================================
# Semantic Modules
# ============================================================

@dataclass
class SemanticImportItem:
    source: str
    target: Optional[str] = None


@dataclass
class SemanticImport:
    module: str
    items: list[SemanticImportItem] = field(default_factory=list)


@dataclass
class SemanticModule:
    name: str

    functions: list[SemanticFunction] = field(default_factory=list)

    classes: list[SemanticClass] = field(default_factory=list)
    variables: list[SemanticArgument] = field(default_factory=list)

    imports: list[str | SemanticImport] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)
