# -*- coding: utf-8 -*-
from __future__ import annotations

import inspect
import os
import sys
from dataclasses import dataclass, field
from typing import Optional


_ANSI = {
    "bold": "\033[1m",
    "red": "\033[31m",
    "blue": "\033[34m",
    "cyan": "\033[36m",
    "reset": "\033[0m",
}
_TRUE_VALUES = {"1", "true", "yes", "on"}


def _parse_shape_dim(dim: str) -> dict[str, str | None]:
    token = (dim or "").strip()
    if not token:
        return {"raw": "", "lower": None, "upper": None, "extent": None}
    if ":" not in token:
        return {"raw": token, "lower": None, "upper": token, "extent": token}
    lo, hi = token.split(":", 1)
    lo = lo.strip() or None
    hi = hi.strip() or None
    return {"raw": token, "lower": lo, "upper": hi, "extent": None}


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in _TRUE_VALUES


def _apply_color(text: str, *styles: str, enabled: bool) -> str:
    if not enabled:
        return text
    prefix = "".join(_ANSI[style] for style in styles)
    return f"{prefix}{text}{_ANSI['reset']}"


def _enable_windows_ansi() -> None:
    """Enable ANSI escape sequence handling on Windows terminals when possible."""
    if os.name != "nt":
        return

    if sys.modules.get("colorama") is not None:
        sys.modules["colorama"].just_fix_windows_console()
        return

    import importlib.util

    if importlib.util.find_spec("colorama") is not None:
        import importlib

        colorama = importlib.import_module("colorama")
        colorama.just_fix_windows_console()


class FortranParseError(ValueError):
    """Parser error with compiler-style diagnostic rendering support."""

    default_code = "PARSE001"

    def __init__(
        self,
        message: str,
        filename: str | None = None,
        line_number: int | None = None,
        source_line: str | None = None,
        *,
        code: str | None = None,
    ):
        self.filename = filename
        self.line_number = line_number
        self.source_line = source_line
        self.base_message = message
        self.code = code or self.default_code
        frame = inspect.stack()[1]
        self.parser_file = frame.filename
        self.parser_line_number = frame.lineno
        self.parser_function = frame.function
        super().__init__(self.format_diagnostic(color=False))

    def format_diagnostic(self, *, color: bool = False, debug: bool | None = None) -> str:
        """Return a Fortran/compiler-style diagnostic for this parse error."""
        if color:
            _enable_windows_ansi()
        if debug is None:
            debug = _env_flag("FORTRAN_PARSER_DEBUG")

        location = self.filename or "<unknown>"
        if self.line_number is not None:
            location = f"{location}:{self.line_number}:1"

        severity = _apply_color("error", "red", "bold", enabled=color)
        code = _apply_color(f"[{self.code}]", "cyan", enabled=color)
        lines = [f"{_apply_color(location, 'bold', enabled=color)}: {severity}{code}: {self.base_message}"]

        if self.source_line is not None:
            line_no = str(self.line_number) if self.line_number is not None else "?"
            gutter_width = max(len(line_no), 1)
            source = self.source_line.rstrip("\n")
            marker = "^" if source.strip() else ""
            lines.extend(
                [
                    f"{' ' * gutter_width} {_apply_color('|', 'blue', enabled=color)}",
                    f"{_apply_color(line_no.rjust(gutter_width), 'blue', enabled=color)} {_apply_color('|', 'blue', enabled=color)} {source}",
                    f"{' ' * gutter_width} {_apply_color('|', 'blue', enabled=color)} {_apply_color(marker, 'red', 'bold', enabled=color)}",
                ]
            )

        if debug:
            lines.append(
                _apply_color(
                    f"note: parser raised at {self.parser_file}:{self.parser_line_number} in {self.parser_function}()",
                    "cyan",
                    enabled=color,
                )
            )

        return "\n".join(lines)


@dataclass
class FortranVariable:
    name: str
    base_type: str = "unknown"
    kind: Optional[str] = None
    rank: int = 0
    shape: list[str] = field(default_factory=list)
    @property
    def shape_info(self) -> list[dict[str, str | None]]:
        """Structured per-dimension shape metadata derived from `shape` tokens."""
        return [_parse_shape_dim(dim) for dim in self.shape]

    @property
    def lower_bounds(self) -> list[str | None]:
        return [d["lower"] for d in self.shape_info]

    @property
    def upper_bounds(self) -> list[str | None]:
        return [d["upper"] for d in self.shape_info]

    lbound: list[str | None] = field(default_factory=list)
    ubound: list[str | None] = field(default_factory=list)
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


@dataclass
class FortranSubmodule:
    name: str
    parent: str
    ancestor: Optional[str] = None
    filename: Optional[str] = None
    uses: dict[str, list[str]] = field(default_factory=dict)
    variables: list[FortranVariable] = field(default_factory=list)
    procedures: list[FortranProcedureSignature] = field(default_factory=list)
    derived_types: list[FortranDerivedType] = field(default_factory=list)
    interfaces: list[FortranInterface] = field(default_factory=list)


@dataclass
class FortranProgram:
    name: Optional[str] = None
    filename: Optional[str] = None
    uses: dict[str, list[str]] = field(default_factory=dict)
    variables: list[FortranVariable] = field(default_factory=list)
    procedures: list[FortranProcedureSignature] = field(default_factory=list)


@dataclass
class FortranBlockData:
    name: Optional[str] = None
    filename: Optional[str] = None
    variables: list[FortranVariable] = field(default_factory=list)
