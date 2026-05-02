# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FortranVariable:
    name: str
    base_type: str = "unknown"
    kind: Optional[str] = None
    rank: int = 0
    shape: list[str] = field(default_factory=list)
    value: str | None = None
    value_type: str = "unknown"
    is_parameter: bool = False
    dimensions: list[int] = field(default_factory=list)


@dataclass
class FortranArgument(FortranVariable):
    procedure: Optional[str] = None
    intent: str = "unknown"
    optional: bool = False
    pass_by_value: bool = False
    allocatable: bool = False
    pointer: bool = False


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
    variables: dict[str, FortranVariable] = field(default_factory=dict)


@dataclass
class FortranDerivedType:
    name: str
    module: Optional[str] = None
    fields: list[FortranArgument] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)
    extends: Optional["FortranDerivedType | str"] = None
    attributes: list[str] = field(default_factory=list)
    procedure_bindings: list[dict] = field(default_factory=list)
    generic_bindings: list[dict] = field(default_factory=list)


@dataclass
class FortranInterface:
    name: str | None = None
    module: Optional[str] = None
    procedures: list[FortranProcedureSignature] = field(default_factory=list)


@dataclass
class FortranModule:
    name: str
    filename: Optional[str] = None
    uses: dict[str, list[str]] = field(default_factory=dict)
    variables: list[FortranVariable] = field(default_factory=list)
    procedures: list[FortranProcedureSignature] = field(default_factory=list)
    derived_types: list[FortranDerivedType] = field(default_factory=list)
    interfaces: list[FortranInterface] = field(default_factory=list)
