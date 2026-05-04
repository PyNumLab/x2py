# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


class FortranParseError(ValueError):
    def __init__(self, message: str, filename: str | None = None, line_number: int | None = None, source_line: str | None = None):
        self.filename = filename
        self.line_number = line_number
        self.source_line = source_line
        parts = []
        if filename:
            parts.append(f"File '{filename}'")
        if line_number is not None:
            parts.append(f"line {line_number}")
        location = ", ".join(parts)
        if location:
            full_message = f"{location}: {message}"
        else:
            full_message = message
        if source_line is not None:
            full_message += f"\n    {source_line.strip()}"
        super().__init__(full_message)
        self.base_message = message


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
