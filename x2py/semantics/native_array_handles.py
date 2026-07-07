from __future__ import annotations

from copy import deepcopy

from x2py.ownership_policy import OWNERSHIP_POLICY_METADATA, POINTER_POLICY_METADATA
from x2py.semantic_metadata import (
    NATIVE_ARRAY_DESCRIPTOR_METADATA,
    OPTIONAL_ABSENT_HANDLE_METADATA,
)
from x2py.semantics.models import PYTHON_VALUE_MUTABILITY_METADATA, SemanticType


_HANDLE_ONLY_METADATA = (
    NATIVE_ARRAY_DESCRIPTOR_METADATA,
    OPTIONAL_ABSENT_HANDLE_METADATA,
    OWNERSHIP_POLICY_METADATA,
    POINTER_POLICY_METADATA,
    PYTHON_VALUE_MUTABILITY_METADATA,
    "aliased",
    "fortran_allocatable",
    "fortran_pointer",
    "fortran_pointer_association",
)


def native_array_descriptor_kind(semantic_type: SemanticType | None) -> str | None:
    """Return the native descriptor kind for an array handle type."""
    if semantic_type is None:
        return None
    storage = semantic_type.storage
    if semantic_type.rank <= 0 or storage is None or storage.array is None:
        return None
    descriptor = semantic_type.metadata.get(NATIVE_ARRAY_DESCRIPTOR_METADATA)
    if descriptor in {"allocatable", "pointer"}:
        return str(descriptor)
    if storage.array.allocatable and storage.array.pointer:
        raise ValueError(f"Array type {semantic_type.name!r} cannot be both allocatable and pointer")
    if storage.array.allocatable:
        return "allocatable"
    if storage.array.pointer:
        return "pointer"
    return None


def is_native_array_handle(semantic_type: SemanticType | None) -> bool:
    """Return whether a semantic type is a native array descriptor handle."""
    return native_array_descriptor_kind(semantic_type) is not None


def mark_native_array_handle(semantic_type: SemanticType, descriptor: str) -> None:
    """Mark an array semantic type as an allocatable or pointer handle."""
    storage = semantic_type.storage
    if storage is None or storage.array is None or semantic_type.rank <= 0:
        raise ValueError(f"{descriptor.capitalize()} array handles require array storage")
    if descriptor not in {"allocatable", "pointer"}:
        raise ValueError(f"Unsupported native array descriptor kind: {descriptor!r}")
    existing = native_array_descriptor_kind(semantic_type)
    if existing is not None and existing != descriptor:
        raise ValueError(
            f"Array descriptor handle cannot be both {existing!r} and {descriptor!r}: {semantic_type.name}"
        )
    storage.array.allocatable = descriptor == "allocatable"
    storage.array.pointer = descriptor == "pointer"
    semantic_type.metadata[NATIVE_ARRAY_DESCRIPTOR_METADATA] = descriptor


def native_array_data_type(semantic_type: SemanticType) -> SemanticType:
    """Return the ordinary array data facet for a native array handle type."""
    if native_array_descriptor_kind(semantic_type) is None:
        raise ValueError(f"Semantic type {semantic_type.name!r} is not a native array handle")
    data_type = deepcopy(semantic_type)
    for key in _HANDLE_ONLY_METADATA:
        data_type.metadata.pop(key, None)
    storage = data_type.storage
    if storage is not None and storage.array is not None:
        storage.array.allocatable = False
        storage.array.pointer = False
    return data_type


__all__ = (
    "is_native_array_handle",
    "mark_native_array_handle",
    "native_array_data_type",
    "native_array_descriptor_kind",
)
