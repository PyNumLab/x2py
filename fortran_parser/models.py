from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FortranArgument:
    name: str
    base_type: str = "unknown"
    kind: Optional[str] = None
    rank: int = 0
    shape: list[str] = field(default_factory=list)
    intent: str = "unknown"
    optional: bool = False
    value: bool = False
    allocatable: bool = False
    pointer: bool = False
    parent: object | None = field(default=None, repr=False, compare=False)


@dataclass
class FortranProcedureSignature:
    name: str
    kind: str
    module: Optional[str] = None
    arguments: list[FortranArgument] = field(default_factory=list)
    result: Optional[FortranArgument] = None
    attributes: list[str] = field(default_factory=list)
    uses: dict[str, list[str]] = field(default_factory=dict)
    in_interface: bool = False
    parent: object | None = field(default=None, repr=False, compare=False)


@dataclass
class FortranDerivedType:
    name: str
    module: Optional[str] = None
    fields: list[FortranArgument] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)
    extends: Optional[str] = None
    attributes: list[str] = field(default_factory=list)
    procedure_bindings: list[dict] = field(default_factory=list)
    generic_bindings: list[dict] = field(default_factory=list)
    parent: object | None = field(default=None, repr=False, compare=False)


@dataclass
class FortranModule:
    name: str
    uses: dict[str, list[str]] = field(default_factory=dict)
    variables: list[FortranArgument] = field(default_factory=list)
    procedures: list[FortranProcedureSignature] = field(default_factory=list)
    derived_types: list[FortranDerivedType] = field(default_factory=list)
    parent: object | None = field(default=None, repr=False, compare=False)
