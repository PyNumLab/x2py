# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import CFile, c_model_to_dict
from .parser import CParser


_C_SOURCE_SUFFIXES = {".c", ".h"}


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


def parse_c_report(paths: list[str]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    parser = CParser()
    for p in expand_c_paths(paths):
        parsed = parser.visit_file(p, filename=str(p))
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
        lines.append(f"  Globals: {len(parsed.get('globals') or [])}")
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
    args = parser.parse_args(argv)

    payload = parse_c_report(args.paths)
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
