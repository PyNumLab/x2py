# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import fields, is_dataclass
from pathlib import Path

from .models import FortranParseError
from .parser import assess_wrap_readiness, parse_fortran_block_data, parse_fortran_modules, parse_fortran_programs, parse_fortran_signatures, parse_fortran_submodules, parse_fortran_types


_TRUE_VALUES = {"1", "true", "yes", "on"}


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in _TRUE_VALUES


def _diagnostic_color_enabled(*, disabled: bool) -> bool:
    if disabled:
        return False
    return "NO_COLOR" not in os.environ


def _to_dict_no_parent(obj):
    """Convert dataclass-based parse models into JSON-serializable dicts.

    The `FortranDerivedType.extends` field may contain a parent object reference.
    To keep JSON acyclic and stable for goldens, we drop any `parent`-like
    back-reference fields during serialization.
    """
    if is_dataclass(obj):
        out = {}
        for f in fields(obj):
            if f.name == "parent":
                continue
            out[f.name] = _to_dict_no_parent(getattr(obj, f.name))
        return out
    if isinstance(obj, list):
        return [_to_dict_no_parent(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _to_dict_no_parent(v) for k, v in obj.items()}
    return obj


def _collect_extensions(path: Path) -> list[Path]:
    """Recursively collect Fortran source files under a directory."""
    exts = {".f", ".for", ".ftn", ".f77", ".f90", ".f95", ".f03", ".f08"}
    return sorted(p for p in path.rglob("*") if p.suffix.lower() in exts)


def _parse_paths(paths: list[str]) -> dict[str, dict]:
    """Parse one or more files/directories into a per-file report structure."""
    out: dict[str, dict] = {}
    expanded: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            expanded.extend(_collect_extensions(p))
        else:
            expanded.append(p)

    for p in sorted(set(expanded)):
        code = p.read_text(encoding="utf-8")
        out[str(p)] = {
            "signatures": [_to_dict_no_parent(s) for s in parse_fortran_signatures(code, filename=str(p))],
            "types": [_to_dict_no_parent(t) for t in parse_fortran_types(code, filename=str(p))],
            "modules": [_to_dict_no_parent(m) for m in parse_fortran_modules(code, filename=str(p))],
            "submodules": [_to_dict_no_parent(m) for m in parse_fortran_submodules(code, filename=str(p))],
            "programs": [_to_dict_no_parent(m) for m in parse_fortran_programs(code, filename=str(p))],
            "block_data": [_to_dict_no_parent(m) for m in parse_fortran_block_data(code, filename=str(p))],
            "wrap_readiness": assess_wrap_readiness(code, filename=str(p)),
        }
    return out


def _format_blocker_item(code: str, item) -> str:
    """Format one wrap-readiness blocker item for human-readable output."""
    if code == "unsupported_constructs":
        return f"line {item['line']}: {item['text']}"
    if code == "unknown_argument_types":
        return str(item)
    if code == "unresolved_derived_type_arguments":
        providers = ", ".join(item.get("import_modules") or []) or "<not imported>"
        return f"{item['procedure']}:{item['argument']} uses type({item['type']}) from {providers}"
    if code == "unresolved_derived_type_fields":
        providers = ", ".join(item.get("import_modules") or []) or "<not imported>"
        return f"{item['type_owner']}:{item['field']} uses type({item['type']}) from {providers}"
    if code == "unresolved_kind_arguments":
        providers = ", ".join(item.get("import_modules") or []) or "<not imported>"
        return f"{item['procedure']}:{item['argument']} uses kind {item['kind']} from {providers}"
    if code == "unresolved_kind_fields":
        providers = ", ".join(item.get("import_modules") or []) or "<not imported>"
        return f"{item['type_owner']}:{item['field']} uses kind {item['kind']} from {providers}"
    return str(item)


def _format_wrap_readiness(report: dict[str, dict]) -> str:
    """Format only wrap-readiness status and blockers for each parsed file."""
    lines: list[str] = []
    for fname, parsed in report.items():
        readiness = parsed["wrap_readiness"]
        status = "yes" if readiness["wrappable"] else "no"
        lines.append(f"File: {fname}")
        lines.append(f"  Wrappable: {status}")
        blockers = readiness.get("wrappability_blockers", [])
        if blockers:
            lines.append("  Why not wrappable:")
            for blocker in blockers:
                lines.append(f"    - {blocker['message']}")
                for item in blocker.get("items", []):
                    lines.append(f"      * {_format_blocker_item(blocker['code'], item)}")
        else:
            lines.append("  No wrap-readiness blockers detected.")
        lines.append("")
    return "\n".join(lines).rstrip()


def _format_report(report: dict[str, dict]) -> str:
    """Format the per-file parse report as a stable, human-readable tree."""
    lines: list[str] = []
    for fname, parsed in report.items():
        lines.append(f"File: {fname}")
        free_procedures = [s for s in parsed["signatures"] if s.get("module") is None]

        if free_procedures:
            lines.append(f"  Procedures: {len(free_procedures)}")
            for s in free_procedures:
                args = ", ".join(f"{a['name']}:{a['base_type']}[{a['rank']}]" for a in s["arguments"])
                result_txt = f" -> {s['result']['base_type']}[{s['result']['rank']}]" if s.get('result') else ""
                lines.append(f"    - {s['kind']} {s['name']}({args}){result_txt}")

        if parsed["types"]:
            lines.append(f"  Derived types: {len(parsed['types'])}")
            for t in parsed["types"]:
                lines.append(f"    - type {t['name']} (fields={len(t['fields'])}, methods={len(t['methods'])})")

        if parsed["modules"]:
            lines.append(f"  Modules: {len(parsed['modules'])}")
            for mod in parsed["modules"]:
                lines.append(f"    - module {mod['name']} (vars={len(mod['variables'])}, uses={len(mod['uses'])})")
                if mod.get("procedures"):
                    lines.append(f"      Procedures: {len(mod['procedures'])}")
                    for s in mod["procedures"]:
                        args = ", ".join(f"{a['name']}:{a['base_type']}[{a['rank']}]" for a in s["arguments"])
                        result_txt = f" -> {s['result']['base_type']}[{s['result']['rank']}]" if s.get('result') else ""
                        lines.append(f"        - {s['kind']} {s['name']}({args}){result_txt}")

        if parsed.get("submodules"):
            lines.append(f"  Submodules: {len(parsed['submodules'])}")
            for submod in parsed["submodules"]:
                parent = submod["parent"] if submod.get("ancestor") is None else f"{submod['ancestor']}:{submod['parent']}"
                lines.append(f"    - submodule {submod['name']} (parent={parent}, vars={len(submod['variables'])}, uses={len(submod['uses'])})")
                if submod.get("procedures"):
                    lines.append(f"      Procedures: {len(submod['procedures'])}")
                    for proc in submod["procedures"]:
                        args = ", ".join(f"{a['name']}:{a['base_type']}[{a['rank']}]" for a in proc["arguments"])
                        result_txt = f" -> {proc['result']['base_type']}[{proc['result']['rank']}]" if proc.get('result') else ""
                        lines.append(f"        - {proc['kind']} {proc['name']}({args}){result_txt}")

        if parsed.get("programs"):
            lines.append(f"  Programs: {len(parsed['programs'])}")
            for prog in parsed["programs"]:
                lines.append(f"    - program {prog['name']} (vars={len(prog['variables'])}, uses={len(prog['uses'])})")

        if parsed.get("block_data"):
            lines.append(f"  Block data: {len(parsed['block_data'])}")
            for block in parsed["block_data"]:
                name = block["name"] or "<unnamed>"
                lines.append(f"    - block data {name} (vars={len(block['variables'])})")

        readiness = parsed["wrap_readiness"]
        lines.append(f"  Wrappable: {'yes' if readiness['wrappable'] else 'no'}")
        if readiness.get("wrappability_blockers"):
            lines.append("  Why not wrappable:")
            for blocker in readiness["wrappability_blockers"]:
                lines.append(f"    - {blocker['message']}")
                for item in blocker.get("items", []):
                    lines.append(f"      * {_format_blocker_item(blocker['code'], item)}")
        lines.append("")
    return "\n".join(lines).rstrip()


def main() -> int:
    """CLI entrypoint for `python -m fortran_parser` and `fortran_parser.cli`.

    The CLI supports:
    - parsing one or more paths (files and/or directories)
    - printing a human-readable report, or JSON
    - optionally writing the JSON report to a file
    """
    parser = argparse.ArgumentParser(description="Parse Fortran files and print a human-readable report or JSON.")
    parser.add_argument("paths", nargs="+", help="Fortran file(s) or directory path(s)")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    parser.add_argument(
        "--wrap-readiness",
        action="store_true",
        help="Print only whether each input is wrap-ready and, when it is not, why.",
    )
    parser.add_argument("--json-out", type=Path, help="Write JSON report to this file")
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color in parse diagnostics. Diagnostics are colored by default when available.",
    )
    parser.add_argument(
        "--debug-traceback",
        action="store_true",
        help="Re-raise parser errors so Python prints a traceback for parser debugging. "
        "Can also be enabled with FORTRAN_PARSER_DEBUG=1.",
    )
    args = parser.parse_args()

    try:
        report = _parse_paths(args.paths)
    except FortranParseError as exc:
        if args.debug_traceback or _env_flag("FORTRAN_PARSER_DEBUG"):
            raise
        print(exc.format_diagnostic(color=_diagnostic_color_enabled(disabled=args.no_color), debug=False), file=sys.stderr)
        return 1

    if args.json_out:
        args.json_out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    elif args.wrap_readiness:
        print(_format_wrap_readiness(report))
    else:
        print(_format_report(report))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
