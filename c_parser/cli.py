# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from .models import CFile, CMacro, CParseError, CSourceLocation, c_model_to_dict
from .parser import CParser


_C_SOURCE_SUFFIXES = {".c", ".h", ".i"}
_TRUE_VALUES = {"1", "true", "yes", "on"}


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in _TRUE_VALUES


def _diagnostic_color_enabled(*, disabled: bool) -> bool:
    return not disabled and "NO_COLOR" not in os.environ


def _collect_c_extensions(path: Path) -> list[Path]:
    return sorted(
        p
        for p in path.rglob("*")
        if p.is_file() and p.suffix.lower() in _C_SOURCE_SUFFIXES
    )


def expand_c_paths(paths: list[str]) -> list[Path]:
    expanded: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            expanded.extend(_collect_c_extensions(p))
        else:
            expanded.append(p)
    return sorted(set(expanded))


def attach_preprocessing_recipe(parsed: CFile, preprocessing_recipe: dict[str, Any] | None) -> None:
    """Attach compiler recipe side-channel facts to a parsed C file."""

    parsed.preprocessing_recipe = preprocessing_recipe
    if not preprocessing_recipe:
        return
    existing = {(macro.name, macro.source_location.filename if macro.source_location else None, macro.source_location.line if macro.source_location else None) for macro in parsed.macros}
    for item in preprocessing_recipe.get("macros") or []:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if not isinstance(name, str) or not name:
            continue
        location = CSourceLocation(
            filename=item.get("path") if isinstance(item.get("path"), str) else None,
            line=item.get("line") if isinstance(item.get("line"), int) else None,
            column=1,
        )
        key = (name, location.filename, location.line)
        if key in existing:
            continue
        parsed.macros.append(
            CMacro(
                name=name,
                value=item.get("value") if isinstance(item.get("value"), str) else None,
                function_like=bool(item.get("function_like")),
                source_location=location,
            )
        )
        existing.add(key)


def parse_c_report(
    paths: list[str],
    *,
    include_dirs: Sequence[str | Path] | None = None,
    preprocessing: str = "raw",
    source_loader: Callable[[Path], str | tuple[str, dict[str, Any] | None]] | None = None,
) -> dict[str, dict]:
    out: dict[str, dict] = {}
    parser = CParser()
    for p in expand_c_paths(paths):
        if source_loader is None:
            parsed = parser.visit_file(
                p,
                filename=str(p),
                include_dirs=include_dirs,
                preprocessing=preprocessing,
            )
        else:
            loaded = source_loader(p)
            source, preprocessing_recipe = loaded if isinstance(loaded, tuple) else (loaded, None)
            parsed = parser.visit_file(
                source,
                filename=str(p),
                include_dirs=include_dirs,
                preprocessing=preprocessing,
            )
            attach_preprocessing_recipe(parsed, preprocessing_recipe)
        out[str(p)] = c_model_to_dict(parsed)
    return out


def format_c_report(report: dict[str, dict]) -> str:
    lines: list[str] = []
    for fname, parsed in report.items():
        lines.append(f"File: {fname}")
        lines.append(f"  Language: {parsed.get('language', 'c')}")
        lines.append(f"  Functions: {len(parsed.get('functions') or [])}")
        lines.append(f"  Structs: {len(parsed.get('structs') or [])}")
        lines.append(f"  Unions: {len(parsed.get('unions') or [])}")
        lines.append(f"  Enums: {len(parsed.get('enums') or [])}")
        lines.append(f"  Typedefs: {len(parsed.get('typedefs') or [])}")
        lines.append(f"  Variables: {len(parsed.get('variables') or [])}")
        lines.append(f"  Macros: {len(parsed.get('macros') or [])}")
        lines.append(f"  Includes: {len(parsed.get('includes') or [])}")
        lines.append(f"  Diagnostics: {len(parsed.get('diagnostics') or [])}")
        lines.append(f"  Parser status: {parsed.get('parser_status', 'partial')}")
        lines.append("")
    return "\n".join(lines).rstrip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="C parser CLI for the implemented C subset.")
    parser.add_argument("paths", nargs="+", help="C source/header file(s) or directory path(s)")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    parser.add_argument("--out", type=str, help="Write parser JSON to a file")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI color in parse diagnostics")
    parser.add_argument(
        "--debug",
        "--debug-traceback",
        dest="debug",
        action="store_true",
        help="Re-raise parser errors so Python prints a traceback for parser debugging.",
    )
    args = parser.parse_args(argv)

    try:
        payload = parse_c_report(args.paths)
    except CParseError as exc:
        if args.debug or _env_flag("C_PARSER_DEBUG"):
            raise
        print(exc.format_diagnostic(color=_diagnostic_color_enabled(disabled=args.no_color), debug=False), file=sys.stderr)
        return 1
    if args.out:
        Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return 0

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(format_c_report(payload))
    return 0


__all__ = (
    "CFile",
    "expand_c_paths",
    "format_c_report",
    "main",
    "parse_c_report",
)
