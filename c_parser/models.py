# -*- coding: utf-8 -*-
from __future__ import annotations

import inspect
import os
import sys
from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any


_ANSI = {
    "bold": "\033[1m",
    "red": "\033[31m",
    "blue": "\033[34m",
    "cyan": "\033[36m",
    "reset": "\033[0m",
}
_TRUE_VALUES = {"1", "true", "yes", "on"}


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in _TRUE_VALUES


def _apply_color(text: str, *styles: str, enabled: bool) -> str:
    if not enabled:
        return text
    prefix = "".join(_ANSI[style] for style in styles)
    return f"{prefix}{text}{_ANSI['reset']}"


def _enable_windows_ansi() -> None:  # pragma: no cover - Windows-only console setup.
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


def c_model_to_dict(obj: Any) -> Any:
    """Convert C parser dataclasses into stable JSON-compatible values."""
    if is_dataclass(obj):
        return {f.name: c_model_to_dict(getattr(obj, f.name)) for f in fields(obj)}
    if isinstance(obj, list):
        return [c_model_to_dict(v) for v in obj]
    if isinstance(obj, dict):
        return {k: c_model_to_dict(v) for k, v in obj.items()}
    if isinstance(obj, set):
        return sorted(c_model_to_dict(v) for v in obj)
    return obj


class CParseError(ValueError):
    """C parser error with compiler-style diagnostic rendering support."""

    default_code = "CPARSE001"

    def __init__(
        self,
        message: str,
        filename: str | None = None,
        line_number: int | None = None,
        column: int | None = None,
        source_line: str | None = None,
        *,
        code: str | None = None,
    ):
        self.filename = filename
        self.line_number = line_number
        self.column = column
        self.source_line = source_line
        self.base_message = message
        self.code = code or self.default_code
        frame = inspect.stack()[1]
        self.parser_file = frame.filename
        self.parser_line_number = frame.lineno
        self.parser_function = frame.function
        super().__init__(self.format_diagnostic(color=False))

    def format_diagnostic(self, *, color: bool = False, debug: bool | None = None) -> str:
        if color:
            _enable_windows_ansi()
        if debug is None:
            debug = _env_flag("C_PARSER_DEBUG")

        location = self.filename or "<unknown>"
        if self.line_number is not None:
            column = self.column if self.column is not None else 1
            location = f"{location}:{self.line_number}:{column}"

        severity = _apply_color("error", "red", "bold", enabled=color)
        code = _apply_color(f"[{self.code}]", "cyan", enabled=color)
        lines = [f"{_apply_color(location, 'bold', enabled=color)}: {severity}{code}: {self.base_message}"]

        if self.source_line is not None:
            line_no = str(self.line_number) if self.line_number is not None else "?"
            gutter_width = max(len(line_no), 1)
            source = self.source_line.rstrip("\n")
            marker_column = max((self.column or 1) - 1, 0)
            marker = " " * marker_column + "^" if source.strip() else ""
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
class CSourceLocation:
    filename: str | None = None
    line: int | None = None
    column: int | None = None
    source_line: str | None = None

    @property
    def display(self) -> str:
        location = self.filename or "<unknown>"
        if self.line is not None:
            column = self.column if self.column is not None else 1
            location = f"{location}:{self.line}:{column}"
        return location


@dataclass
class CDiagnostic:
    code: str
    message: str
    severity: str = "warning"
    location: CSourceLocation | None = None
    unit_kind: str | None = None
    unit_name: str | None = None


@dataclass
class CPointer:
    qualifiers: list[str] = field(default_factory=list)


@dataclass
class CArray:
    size: str | None = None
    static: bool = False


@dataclass
class CTypeRef:
    base: str | None = None
    qualifiers: list[str] = field(default_factory=list)
    storage_class: list[str] = field(default_factory=list)
    sign: str | None = None
    width: str | None = None
    tag_kind: str | None = None
    tag_name: str | None = None
    typedef_name: str | None = None
    pointers: list[CPointer] = field(default_factory=list)
    arrays: list[CArray] = field(default_factory=list)
    kind: str = "type"
    source_text: str = ""
    resolved: Any = None

    @property
    def pointer_depth(self) -> int:
        return len(self.pointers)

    @property
    def array_rank(self) -> int:
        return len(self.arrays)

    @property
    def effective_type_text(self) -> str:
        if self.source_text:
            return self.source_text
        if self.typedef_name:
            return self.typedef_name
        if self.tag_kind and self.tag_name:
            return f"{self.tag_kind} {self.tag_name}"
        return self.base or "unknown"

    @property
    def is_const_pointer(self) -> bool:
        return bool(self.pointers) and "const" in self.qualifiers

    @property
    def is_opaque_type(self) -> bool:
        return bool(self.tag_kind and self.tag_name and self.resolved is None)


@dataclass
class CParameter:
    name: str | None = None
    type: CTypeRef = field(default_factory=CTypeRef)
    source_location: CSourceLocation | None = None


@dataclass
class CFunction:
    name: str
    return_type: CTypeRef = field(default_factory=CTypeRef)
    parameters: list[CParameter] = field(default_factory=list)
    storage: list[str] = field(default_factory=list)
    specifiers: list[str] = field(default_factory=list)
    variadic: bool = False
    is_definition: bool = False
    prototype_style: str | None = None
    source_location: CSourceLocation | None = None


@dataclass
class CField:
    name: str | None = None
    type: CTypeRef = field(default_factory=CTypeRef)
    source_location: CSourceLocation | None = None


@dataclass
class CStruct:
    name: str | None = None
    fields: list[CField] = field(default_factory=list)
    anonymous_id: str | None = None
    opaque: bool = False
    source_location: CSourceLocation | None = None


@dataclass
class CUnion:
    name: str | None = None
    fields: list[CField] = field(default_factory=list)
    anonymous_id: str | None = None
    source_location: CSourceLocation | None = None


@dataclass
class CEnumerator:
    name: str
    value: str | None = None
    source_location: CSourceLocation | None = None


@dataclass
class CEnum:
    name: str | None = None
    constants: list[CEnumerator] = field(default_factory=list)
    anonymous_id: str | None = None
    source_location: CSourceLocation | None = None


@dataclass
class CTypedef:
    name: str
    type: CTypeRef = field(default_factory=CTypeRef)
    source_location: CSourceLocation | None = None


@dataclass
class CGlobal:
    name: str
    type: CTypeRef = field(default_factory=CTypeRef)
    source_location: CSourceLocation | None = None


@dataclass
class CMacro:
    name: str
    value: str | None = None
    function_like: bool = False
    directive: str = "define"
    source_location: CSourceLocation | None = None


@dataclass
class CInclude:
    target: str
    kind: str = "local"
    resolved_path: str | None = None
    source_location: CSourceLocation | None = None


@dataclass
class CFile:
    filename: str | None = None
    language: str = "c"
    parser_status: str = "partial"
    preprocessing: str = "raw"
    functions: list[CFunction] = field(default_factory=list)
    structs: list[CStruct] = field(default_factory=list)
    unions: list[CUnion] = field(default_factory=list)
    enums: list[CEnum] = field(default_factory=list)
    typedefs: list[CTypedef] = field(default_factory=list)
    globals: list[CGlobal] = field(default_factory=list)
    macros: list[CMacro] = field(default_factory=list)
    includes: list[CInclude] = field(default_factory=list)
    diagnostics: list[CDiagnostic] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return c_model_to_dict(self)


@dataclass
class CProject:
    files: dict[str, CFile] = field(default_factory=dict)
    functions: dict[str, CFunction] = field(default_factory=dict)
    structs: dict[str, CStruct] = field(default_factory=dict)
    unions: dict[str, CUnion] = field(default_factory=dict)
    enums: dict[str, CEnum] = field(default_factory=dict)
    typedefs: dict[str, CTypedef] = field(default_factory=dict)
    globals: dict[str, CGlobal] = field(default_factory=dict)
    macros: dict[str, CMacro] = field(default_factory=dict)
    includes: dict[str, CInclude] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return c_model_to_dict(self)
