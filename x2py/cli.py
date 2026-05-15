from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, fields, is_dataclass
from pathlib import Path

from fortran_parser.models import FortranParseError
from fortran_parser.parser import FortranParser
from fortran_parser.cli import _format_report

_TRUE_VALUES = {"1", "true", "yes", "on"}


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in _TRUE_VALUES


def _diagnostic_color_enabled(*, disabled: bool) -> bool:
    if disabled:
        return False
    return "NO_COLOR" not in os.environ


def _to_dict_no_parent(obj):
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
    exts = {".f", ".for", ".ftn", ".f77", ".f90", ".f95", ".f03", ".f08"}
    return sorted(p for p in path.rglob("*") if p.suffix.lower() in exts)


def _expand_paths(paths: list[str]) -> list[Path]:
    expanded: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            expanded.extend(_collect_extensions(p))
        else:
            expanded.append(p)
    return sorted(set(expanded))


def _parse_report(paths: list[str]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    parser = FortranParser()
    for p in _expand_paths(paths):
        code = p.read_text(encoding="utf-8")
        parsed = parser.parse_file(code, filename=str(p))
        out[str(p)] = {
            "signatures": [_to_dict_no_parent(s) for s in parsed.procedures],
            "types": [_to_dict_no_parent(t) for t in parsed.derived_types],
            "modules": [_to_dict_no_parent(m) for m in parsed.modules],
            "submodules": [_to_dict_no_parent(m) for m in parsed.submodules],
            "programs": [_to_dict_no_parent(m) for m in parsed.programs],
            "block_data": [_to_dict_no_parent(m) for m in parsed.block_data_units],
            "wrap_readiness": parser.assess_wrap_readiness(code, filename=str(p)),
        }
    return out


def _semantic_report(paths: list[str]) -> dict[str, dict]:
    from semantics.fortran2ir import fortran_module_to_semantic_module
    from semantics.pyi_printer import emit_module

    out: dict[str, dict] = {}
    parser = FortranParser()
    for p in _expand_paths(paths):
        code = p.read_text(encoding="utf-8")
        fobj = parser.parse_file(code, filename=str(p))
        modules = [fortran_module_to_semantic_module(m) for m in fobj.modules]
        out[str(p)] = {
            "semantic_modules": [asdict(m) for m in modules],
            "pyi": "\n\n".join(emit_module(m) for m in modules).strip(),
        }
    return out


def _format_pyi_report(semantic_report: dict[str, dict]) -> str:
    lines: list[str] = []
    for fname, payload in semantic_report.items():
        lines.append(f"File: {fname}")
        lines.append(payload.get("pyi") or "<no module declarations found>")
        lines.append("")
    return "\n".join(lines).rstrip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="x2py CLI for parser and semantic conversion stages.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m x2py path/to/file.f90 --parse\n"
            "  python -m x2py path/to/file.f90 --parse --json --out [report.json]\n"
            "  python -m x2py path/to/file.f90 --semantics\n"
            "  python -m x2py path/to/file.f90 --pyi --out [module.pyi]"
        ),
    )
    parser.add_argument("paths", nargs="+", help="Fortran file(s) or directory path(s)")
    parser.add_argument("--parse", action="store_true", help="Run and output parser stage report")
    parser.add_argument("--semantics", action="store_true", help="Generate semantic IR models from parsed Fortran modules")
    parser.add_argument("--pyi", action="store_true", help="Generate Python .pyi content")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    parser.add_argument("--out", nargs="?", const="", type=str, help="Write stage output to file (optional explicit output filename)")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI color in parse diagnostics")
    parser.add_argument("--debug-traceback", action="store_true", help="Re-raise parser errors for debug")
    args = parser.parse_args()

    if not (args.parse or args.semantics or args.pyi):
        parser.error("Select at least one stage flag: --parse, --semantics, or --pyi")

    if args.json and not args.parse:
        parser.error("JSON output currently supports only the parsing stage. Use --parse with --json/--out.")

    try:
        parse_payload = _parse_report(args.paths) if args.parse else None
        semantic_payload = _semantic_report(args.paths) if (args.semantics or args.pyi) else None
    except FortranParseError as exc:
        if args.debug_traceback or _env_flag("FORTRAN_PARSER_DEBUG"):
            raise
        print(exc.format_diagnostic(color=_diagnostic_color_enabled(disabled=args.no_color), debug=False), file=sys.stderr)
        return 1

    payload = parse_payload or {} if args.parse else semantic_payload or {}

    if args.out is not None:
        if args.json and args.pyi:
            parser.error("--out cannot be used with both --json and --pyi")

        out_mode_json = args.json or (args.parse and not args.pyi)

        if out_mode_json:
            if args.out:
                Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
            else:
                for fname, report in (parse_payload or {}).items():
                    Path(fname).with_suffix(".json").write_text(json.dumps({fname: report}, indent=2), encoding="utf-8")

        if args.pyi:
            if args.out:
                pyi_text = "\n\n".join((report.get("pyi") or "") for report in (semantic_payload or {}).values()).strip()
                Path(args.out).write_text(pyi_text + "\n", encoding="utf-8")
            else:
                for fname, report in (semantic_payload or {}).items():
                    Path(fname).with_suffix(".pyi").write_text((report.get("pyi") or "") + "\n", encoding="utf-8")

    if args.pyi and not args.json and args.out is None:
        print(_format_pyi_report(semantic_payload or {}))
    elif args.parse and not (args.semantics or args.json or args.pyi) and args.out is None:
        print(_format_report(parse_payload or {}))
    else:
        print(json.dumps(payload, indent=2))

    return 0
