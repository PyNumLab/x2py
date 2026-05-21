from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, fields, is_dataclass
from pathlib import Path

from c_parser.cli import format_c_report, parse_c_report
from c_parser.models import CParseError
from fortran_parser.models import FortranParseError
from fortran_parser.parser import FortranParser
from fortran_parser.cli import _format_report
from semantics.fortran2ir import fortran_file_to_semantic_modules
from semantics.pyi_parser import load_pyi_file
from semantics.readiness import assess_semantic_wrap_readiness

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
            value = getattr(obj, f.name)
            if f.name == "parent" and not isinstance(value, (str, type(None))):
                continue
            out[f.name] = _to_dict_no_parent(value)
        return out
    if isinstance(obj, list):
        return [_to_dict_no_parent(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _to_dict_no_parent(v) for k, v in obj.items()}
    return obj


def _collect_extensions(path: Path) -> list[Path]:
    exts = {".f", ".for", ".ftn", ".f77", ".f90", ".f95", ".f03", ".f08"}
    return sorted(p for p in path.rglob("*") if p.suffix.lower() in exts)


def _collect_pyi_extensions(path: Path) -> list[Path]:
    return sorted(p for p in path.rglob("*.pyi") if p.is_file())


def _collect_readiness_extensions(path: Path) -> list[Path]:
    return sorted({*_collect_extensions(path), *_collect_pyi_extensions(path)})


def _expand_paths(paths: list[str]) -> list[Path]:
    expanded: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            expanded.extend(_collect_extensions(p))
        else:
            expanded.append(p)
    return sorted(set(expanded))


def _expand_readiness_paths(paths: list[str]) -> list[Path]:
    expanded: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            expanded.extend(_collect_readiness_extensions(p))
        else:
            expanded.append(p)
    return sorted(set(expanded))


def _parse_report(paths: list[str]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    parser = FortranParser()
    for p in _expand_paths(paths):
        code = p.read_text(encoding="utf-8")
        parsed = parser.visit_file(code, filename=str(p))
        out[str(p)] = {
            "signatures": [_to_dict_no_parent(s) for s in parsed.procedures],
            "types": [_to_dict_no_parent(t) for t in parsed.derived_types],
            "modules": [_to_dict_no_parent(m) for m in parsed.modules],
            "submodules": [_to_dict_no_parent(m) for m in parsed.submodules],
            "programs": [_to_dict_no_parent(m) for m in parsed.programs],
            "block_data": [_to_dict_no_parent(m) for m in parsed.block_data_units],
        }
    return out


def _semantic_report(paths: list[str]) -> dict[str, dict]:
    from semantics.fortran2ir import fortran_module_to_semantic_module
    from semantics.pyi_printer import emit_module

    out: dict[str, dict] = {}
    parser = FortranParser()
    for p in _expand_paths(paths):
        code = p.read_text(encoding="utf-8")
        fobj = parser.visit_file(code, filename=str(p))
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


def _wrap_readiness_report(paths: list[str]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    parser = FortranParser()
    for p in _expand_readiness_paths(paths):
        if p.suffix.lower() == ".pyi":
            modules = [load_pyi_file(p)]
            source_kind = "pyi"
        else:
            code = p.read_text(encoding="utf-8")
            parsed = parser.visit_file(code, filename=str(p))
            modules = fortran_file_to_semantic_modules(parsed, standalone_module_name=p.stem)
            source_kind = "fortran"

        out[str(p)] = {
            "source_kind": source_kind,
            "semantic_modules": [asdict(module) for module in modules],
            "wrap_readiness": assess_semantic_wrap_readiness(modules, source=str(p)),
        }
    return out


def _attach_wrap_readiness(payload: dict[str, dict] | None, readiness_report: dict[str, dict] | None) -> None:
    if not payload or not readiness_report:
        return
    for fname, report in payload.items():
        readiness = readiness_report.get(fname)
        if readiness is None:
            continue
        report["wrap_readiness"] = readiness["wrap_readiness"]


def _format_semantic_blocker_item(code: str, item) -> str:
    if code == "unresolved_semantic_types":
        return f"{item['owner']} uses unresolved type {item['type']}"
    if code == "unresolved_shape_symbols":
        return f"{item['owner']} shape {item['expression']!r} uses unresolved symbol {item['symbol']}"
    if code == "missing_compile_time_values":
        return f"{item['owner']} needs literal value for Final constant {item['symbol']}"
    if code == "callback_signature_incomplete":
        needs = ", ".join(item.get("needs") or [])
        return f"{item['owner']} needs Callable[[...], ...] metadata ({needs})"
    if code == "no_public_api":
        needs = ", ".join(item.get("needs") or [])
        return f"{item['owner']} needs {needs}"
    return str(item)


def _format_semantic_readiness(readiness_report: dict[str, dict]) -> str:
    lines: list[str] = []
    for fname, payload in readiness_report.items():
        readiness = payload.get("wrap_readiness", {})
        module_names = [
            module.get("name", "<unknown>")
            for module in payload.get("semantic_modules", [])
        ]
        lines.append(f"File: {fname}")
        lines.append(f"  Source: {payload.get('source_kind', '<unknown>')}")
        lines.append(f"  Semantic modules: {', '.join(module_names) or '<none>'}")
        lines.append(f"  Wrappable: {'yes' if readiness.get('wrappable') else 'no'}")
        lines.append(f"  Public functions: {readiness.get('n_functions', 0)}")
        lines.append(f"  Public classes: {readiness.get('n_classes', 0)}")
        lines.append(f"  Public variables: {readiness.get('n_variables', 0)}")
        blockers = readiness.get("wrappability_blockers") or []
        if blockers:
            lines.append("  Why not wrappable:")
            for blocker in blockers:
                lines.append(f"    - {blocker.get('code')}: {blocker.get('message')}")
                for item in blocker.get("items") or []:
                    lines.append(f"      * {_format_semantic_blocker_item(blocker.get('code', ''), item)}")
        else:
            lines.append("  No semantic readiness blockers detected.")
        lines.append("")
    return "\n".join(lines).rstrip()


def print_pyi_output(code: str) -> None:
    # Safe fallback for files, pipes, CI, unsupported terminals, etc.
    if not sys.stdout.isatty():
        print(code)
        return

    try:
        from rich.console import Console
        from rich.syntax import Syntax
    except ImportError:
        print(code)
        return

    try:
        console = Console(force_terminal=True, color_system="auto")
        syntax = Syntax(
            code,
            "python",
            theme="ansi_dark",   # terminal-friendly
            background_color="default",
            line_numbers=False,
            word_wrap=False,
        )
        console.print(syntax)
    except Exception:
        # Never let colored output crash the CLI.
        print(code)

def main() -> int:
    parser = argparse.ArgumentParser(
        description="x2py CLI for parser and semantic conversion stages.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  Parse, compact tree:\n"
            "    python -m x2py path/to/file.f90 --parse\n"
            "  Parse, include scope variables:\n"
            "    python -m x2py path/to/file.f90 --parse --show-vars\n"
            "  Parse, cap every repeated section to 50 items:\n"
            "    python -m x2py path/to/file.f90 --parse --print-limit 50\n"
            "  Parse, include variables and cap every repeated section:\n"
            "    python -m x2py path/to/file.f90 --parse --show-vars --print-limit 50\n"
            "  Parse directory recursively:\n"
            "    python -m x2py path/to/src_dir --parse --print-limit 20\n"
            "  Print parser JSON:\n"
            "    python -m x2py path/to/file.f90 --parse --json\n"
            "  Parse C skeleton JSON:\n"
            "    python -m x2py path/to/api.h --language c --parse --json\n"
            "  Write parser JSON:\n"
            "    python -m x2py path/to/file.f90 --parse --json --out report.json\n"
            "  Write one JSON file next to each source:\n"
            "    python -m x2py path/to/src_dir --parse --out\n"
            "  Show wrap-readiness only:\n"
            "    python -m x2py path/to/file.f90 --wrap-readiness\n"
            "  Print semantic IR JSON:\n"
            "    python -m x2py path/to/file.f90 --semantics\n"
            "  Print generated Python stub text:\n"
            "    python -m x2py path/to/file.f90 --pyi\n"
            "  Write generated Python stub text:\n"
            "    python -m x2py path/to/file.f90 --pyi --out module.pyi\n"
            "  Print semantic IR with readiness attached:\n"
            "    python -m x2py path/to/file.f90 --semantics --wrap-readiness\n"
            "  Check edited .pyi semantic readiness:\n"
            "    python -m x2py path/to/module.pyi --wrap-readiness\n"
            "  Print semantic readiness JSON:\n"
            "    python -m x2py path/to/module.pyi --wrap-readiness --json\n"
            "\nOptional:\n"
            "  Install 'rich' for colored terminal syntax highlighting:\n"
            "      pip install rich"
        ),
    )
    parser.add_argument("paths", nargs="+", help="Source file(s), .pyi file(s), or directory path(s)")
    parser.add_argument(
        "--language",
        choices=("fortran", "c"),
        default="fortran",
        help="Frontend language. Defaults to fortran; C currently supports only --parse skeleton output.",
    )
    parser.add_argument("--parse", action="store_true", help="Run and output parser stage report")
    parser.add_argument(
        "--show-vars",
        action="store_true",
        help="Include module, submodule, program, and block-data variables in the human-readable parse report.",
    )
    parser.add_argument(
        "--print-limit",
        type=int,
        metavar="N",
        help="Show at most N items per repeated section in the human-readable parse report.",
    )
    parser.add_argument(
        "--vars-limit",
        type=int,
        metavar="N",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--wrap-readiness",
        action="store_true",
        help="Convert Fortran or .pyi input to semantic IR and show wrapper readiness",
    )
    parser.add_argument("--semantics", action="store_true", help="Generate semantic IR models from parsed Fortran modules")
    parser.add_argument("--pyi", action="store_true", help="Generate Python .pyi content")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    parser.add_argument("--out", nargs="?", const="", type=str, help="Write stage output to file (optional explicit output filename)")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI color in parse diagnostics")
    parser.add_argument("--debug-traceback", action="store_true", help="Re-raise parser errors for debug")
    args = parser.parse_args()

    if args.language == "c":
        if not (args.parse or args.semantics or args.pyi or args.wrap_readiness):
            parser.error("--language c requires --parse; C semantics and .pyi output are not supported yet")
        if args.semantics:
            parser.error("--semantics is not supported for --language c yet")
        if args.pyi:
            parser.error("--pyi is not supported for --language c yet")
        if args.wrap_readiness:
            parser.error("--wrap-readiness is semantic-layer output and is not supported for --language c yet")
        if args.show_vars or args.print_limit is not None or args.vars_limit is not None:
            parser.error("--show-vars/--print-limit are Fortran-only and are not supported for --language c")

    if args.out is not None and not (args.parse or args.semantics or args.pyi or args.wrap_readiness):
        parser.error("--out requires a stage flag: choose one of --parse, --semantics, --pyi, or --wrap-readiness")

    if (args.show_vars or args.print_limit is not None or args.vars_limit is not None) and not args.parse:
        parser.error("--show-vars/--print-limit require --parse")

    print_limit = args.print_limit if args.print_limit is not None else args.vars_limit
    if print_limit is not None and print_limit < 0:
        parser.error("--print-limit must be >= 0")

    if not (args.parse or args.semantics or args.pyi or args.wrap_readiness):
        parser.error("Select at least one stage flag: --parse, --semantics, --pyi, or --wrap-readiness")

    try:
        parse_payload = (
            parse_c_report(args.paths)
            if args.parse and args.language == "c"
            else _parse_report(args.paths) if args.parse else None
        )
        semantic_payload = _semantic_report(args.paths) if (args.semantics or args.pyi) else None
        readiness_payload = _wrap_readiness_report(args.paths) if args.wrap_readiness else None
        _attach_wrap_readiness(semantic_payload, readiness_payload)
    except CParseError as exc:
        if args.debug_traceback or _env_flag("C_PARSER_DEBUG"):
            raise
        print(exc.format_diagnostic(color=_diagnostic_color_enabled(disabled=args.no_color), debug=False), file=sys.stderr)
        return 1
    except FortranParseError as exc:
        if args.debug_traceback or _env_flag("FORTRAN_PARSER_DEBUG"):
            raise
        print(exc.format_diagnostic(color=_diagnostic_color_enabled(disabled=args.no_color), debug=False), file=sys.stderr)
        return 1
    except (SyntaxError, ValueError) as exc:
        if args.debug_traceback or _env_flag("X2PY_DEBUG"):
            raise
        print(f"x2py: error: {exc}", file=sys.stderr)
        return 1

    if args.parse and args.wrap_readiness and (args.json or args.out is not None):
        payload = {
            "parse": parse_payload or {},
            "wrap_readiness": readiness_payload or {},
        }
    elif args.parse:
        payload = parse_payload or {}
    elif args.semantics or args.pyi:
        payload = semantic_payload or {}
    else:
        payload = readiness_payload or {}

    if args.out is not None:
        if args.json and args.pyi:
            parser.error("--out cannot be used with both --json and --pyi")

        if args.pyi:
            if args.out:
                pyi_text = "\n\n".join((report.get("pyi") or "") for report in (semantic_payload or {}).values()).strip()
                Path(args.out).write_text(pyi_text + "\n", encoding="utf-8")
            else:
                for fname, report in (semantic_payload or {}).items():
                    Path(fname).with_suffix(".pyi").write_text((report.get("pyi") or "") + "\n", encoding="utf-8")
        else:
            if args.out:
                Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
            else:
                for fname, report in payload.items():
                    Path(fname).with_suffix(".json").write_text(json.dumps({fname: report}, indent=2), encoding="utf-8")


    if args.out is not None:
        return 0

    if args.wrap_readiness:
        if args.parse and not args.json:
            print(_format_report(parse_payload or {}, show_vars=args.show_vars or args.vars_limit is not None, print_limit=print_limit))
            print()
            print(_format_semantic_readiness(readiness_payload or {}))
        elif args.pyi and not args.json:
            print_pyi_output(_format_pyi_report(semantic_payload or {}))
            print()
            print(_format_semantic_readiness(readiness_payload or {}))
        elif args.parse or args.semantics or args.pyi:
            print(json.dumps(payload, indent=2))
        elif args.json:
            print(json.dumps(readiness_payload or {}, indent=2))
        else:
            print(_format_semantic_readiness(readiness_payload or {}))
    elif args.pyi and not args.json:
        print_pyi_output(_format_pyi_report(semantic_payload or {}))
    elif args.parse and not (args.semantics or args.json or args.pyi):
        if args.language == "c":
            print(format_c_report(parse_payload or {}))
        else:
            print(_format_report(parse_payload or {}, show_vars=args.show_vars or args.vars_limit is not None, print_limit=print_limit))
    else:
        print(json.dumps(payload, indent=2))

    return 0
