# -*- coding: utf-8 -*-
from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from .lexer import CLogicalRecord, NormalizedCSource, normalize_c_source
from .models import CDiagnostic, CInclude, CMacro, CSourceLocation


_INCLUDE_RE = re.compile(r'^\s*#\s*include\s*(?:"([^"]+)"|<([^>]+)>)')
_DEFINE_RE = re.compile(r"^\s*#\s*define\s+([A-Za-z_]\w*)(\([^)]*\))?(?:\s+(.*))?$")


@dataclass
class CPreprocessorMetadata:
    includes: list[CInclude] = field(default_factory=list)
    macros: list[CMacro] = field(default_factory=list)
    diagnostics: list[CDiagnostic] = field(default_factory=list)


def _record_location(record: CLogicalRecord) -> CSourceLocation:
    source_line = record.source_line
    column = 1
    if source_line is not None:
        marker = source_line.find("#")
        if marker >= 0:
            column = marker + 1
    return CSourceLocation(
        filename=record.filename,
        line=record.original_start_line,
        column=column,
        source_line=source_line,
    )


def _resolve_local_include(
    target: str,
    filename: str | None,
    include_dirs: Sequence[str | Path] | None,
) -> str | None:
    candidates: list[Path] = []
    if filename:
        candidates.append(Path(filename).parent / target)
    candidates.extend(Path(include_dir) / target for include_dir in include_dirs or ())

    for candidate in candidates:
        try:
            if candidate.is_file():
                return str(candidate)
        except OSError:
            continue
    return None


def collect_preprocessor_metadata(
    source: str,
    filename: str | None = None,
    *,
    include_dirs: Sequence[str | Path] | None = None,
) -> CPreprocessorMetadata:
    normalized = normalize_c_source(source, filename=filename)
    metadata = CPreprocessorMetadata()

    for record in normalized.records:
        include_match = _INCLUDE_RE.match(record.text)
        if include_match:
            local_target, system_target = include_match.groups()
            target = local_target or system_target
            kind = "local" if local_target is not None else "system"
            resolved_path = (
                _resolve_local_include(target, filename, include_dirs)
                if kind == "local"
                else None
            )
            location = _record_location(record)
            metadata.includes.append(
                CInclude(
                    target=target,
                    kind=kind,
                    resolved_path=resolved_path,
                    source_location=location,
                )
            )
            if kind == "local" and resolved_path is None:
                metadata.diagnostics.append(
                    CDiagnostic(
                        code="C_UNRESOLVED_INCLUDE",
                        message=f'Could not resolve local include "{target}".',
                        severity="warning",
                        location=location,
                        unit_kind="include",
                        unit_name=target,
                    )
                )
            continue

        define_match = _DEFINE_RE.match(record.text)
        if define_match:
            name, parameters, value = define_match.groups()
            location = _record_location(record)
            function_like = parameters is not None
            metadata.macros.append(
                CMacro(
                    name=name,
                    value=value.strip() if value else None,
                    function_like=function_like,
                    source_location=location,
                )
            )
            if function_like:
                metadata.diagnostics.append(
                    CDiagnostic(
                        code="C_UNSUPPORTED_FUNCTION_LIKE_MACRO",
                        message=f"Function-like macro {name!r} is recorded but not expanded.",
                        severity="warning",
                        location=location,
                        unit_kind="macro",
                        unit_name=name,
                    )
                )

    return metadata


__all__ = (
    "CPreprocessorMetadata",
    "NormalizedCSource",
    "collect_preprocessor_metadata",
    "normalize_c_source",
)
