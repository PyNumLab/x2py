# -*- coding: utf-8 -*-
from __future__ import annotations

import inspect
import os
import sys
from dataclasses import dataclass, field
from typing import Optional

try:
    from colorama import just_fix_windows_console
    just_fix_windows_console()
except ImportError:
    pass


def _supports_color() -> bool:
    return sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


class _Theme:
    ERROR = ""
    INFO = ""
    MUTED = ""
    CARET = ""
    RESET = ""


class _AnsiTheme(_Theme):
    ERROR = "\033[1;31m"
    INFO = "\033[36m"
    MUTED = "\033[90m"
    CARET = "\033[1;31m"
    RESET = "\033[0m"


class FortranParseError(ValueError):
    def __init__(
        self,
        message: str,
        filename: str | None = None,
        line_number: int | None = None,
        source_line: str | None = None,
        column_number: int | None = None,
        code: str = "PARSE001",
    ):
        self.filename = filename
        self.line_number = line_number
        self.source_line = source_line
        self.column_number = column_number
        self.code = code
        self.base_message = message

        frame = inspect.currentframe()
        caller = frame.f_back if frame is not None else None

        self.internal_file = caller.f_code.co_filename if caller else None
        self.internal_line = caller.f_lineno if caller else None
        self.internal_function = caller.f_code.co_name if caller else None

        super().__init__(self.format())

    def format(self, color: bool | str = "auto", debug: bool | None = None) -> str:
        if color == "auto":
            use_color = _supports_color()
        else:
            use_color = bool(color)

        if debug is None:
            debug = os.environ.get("X2PY_DEBUG_ERRORS", "0") in ("1", "true", "TRUE")

        theme = _AnsiTheme() if use_color else _Theme()

        lines = []

        lines.append(
            f"{theme.ERROR}error[{self.code}]{theme.RESET}: {self.base_message}"
        )

        if self.filename or self.line_number is not None:
            location = self.filename or "<unknown>"
            if self.line_number is not None:
                location += f":{self.line_number}"
            if self.column_number is not None:
                location += f":{self.column_number}"

            lines.append("")
            lines.append(f"  {theme.INFO}-->{theme.RESET} {location}")

        if self.source_line is not None:
            lineno = str(self.line_number) if self.line_number is not None else " "
            stripped = self.source_line.rstrip("\n")

            lines.append(f"   {theme.INFO}|{theme.RESET}")
            lines.append(f"{theme.INFO}{lineno}{theme.RESET} {theme.INFO}|{theme.RESET} {stripped}")

            if self.column_number is not None:
                caret_pad = " " * max(self.column_number - 1, 0)
                lines.append(
                    f"   {theme.INFO}|{theme.RESET} {caret_pad}{theme.CARET}^{theme.RESET}"
                )

        if debug:
            lines.append("")
            lines.append("[internal]")
            lines.append(
                f"{self.internal_file}:{self.internal_line} in {self.internal_function}"
            )

        return "\n".join(lines)

    def __str__(self):
        return self.format(color=False)


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
