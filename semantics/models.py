from __future__ import annotations

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
    python_name: str
    native_name: str


# ============================================================
# Semantic Functions
# ============================================================

@dataclass
class SemanticFunction:
    name: str

    native_name: Optional[str] = None

    arguments: list[SemanticArgument] = field(default_factory=list)

    return_type: Optional[SemanticType] = None

    contracts: list[SemanticContract] = field(default_factory=list)

    projection: list[ProjectionMapping] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================
# Semantic Methods
# ============================================================

@dataclass
class SemanticMethod(SemanticFunction):
    is_static: bool = False


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


# ============================================================
# Semantic Modules
# ============================================================

@dataclass
class SemanticModule:
    name: str

    functions: list[SemanticFunction] = field(default_factory=list)

    classes: list[SemanticClass] = field(default_factory=list)

    imports: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)
