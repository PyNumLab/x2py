from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, fields, is_dataclass
from pathlib import Path

from c_parser.cli import expand_c_paths, format_c_report, parse_c_report
from c_parser.models import CParseError
from c_parser.parser import CParser
from fortran_parser.models import FortranParseError
from fortran_parser.parser import FortranParser
from fortran_parser.cli import _format_report
from semantics.c2ir import c_file_to_semantic_modules
from semantics.fortran2ir import fortran_file_to_semantic_modules
from semantics.pyi_parser import load_pyi_file
from semantics.readiness import assess_semantic_wrap_readiness
from x2py.preprocessing import (
    PreprocessingConfig,
    PreprocessingError,
    run_compiler_preprocessor_with_recipe,
    validate_macro_name,
)

_TRUE_VALUES = {"1", "true", "yes", "on"}
_FORTRAN_SOURCE_SUFFIXES = {".f", ".for", ".ftn", ".f77", ".f90", ".f95", ".f03", ".f08"}
_C_SOURCE_SUFFIXES = {".c", ".h", ".i"}


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
    return sorted(p for p in path.rglob("*") if p.suffix.lower() in _FORTRAN_SOURCE_SUFFIXES)


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


def _resolve_language(
    paths: list[str],
    requested: str | None,
    parser: argparse.ArgumentParser,
) -> str:
    if requested is not None:
        for raw in paths:
            path = Path(raw)
            if path.is_dir():
                continue
            suffix = path.suffix.lower()
            if requested == "fortran" and suffix in _C_SOURCE_SUFFIXES:
                parser.error(
                    f"C input {path} is incompatible with --language fortran; "
                    "pass --language c. Use --help for examples."
                )
            if requested == "c" and suffix in _FORTRAN_SOURCE_SUFFIXES:
                parser.error(
                    f"Fortran input {path} is incompatible with --language c; "
                    "pass --language fortran. Use --help for examples."
                )
        return requested

    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            parser.error(
                f"Input directory {path} requires an explicit frontend; "
                "pass --language fortran or --language c. Use --help for examples."
            )

        suffix = path.suffix.lower()
        if suffix in _C_SOURCE_SUFFIXES:
            parser.error(
                f"C input {path} requires explicit --language c. "
                "Use --help for examples."
            )
        if suffix not in _FORTRAN_SOURCE_SUFFIXES and suffix != ".pyi":
            parser.error(
                f"Cannot determine the input language for {path}; "
                "pass --language fortran or --language c. Use --help for examples."
            )
    return "fortran"


def _fortran_source_for_path(
    path: Path,
    preprocessing: PreprocessingConfig,
) -> tuple[str, dict[str, int | str] | None, dict[str, object] | None]:
    if preprocessing.uses_compiler:
        source, recipe = run_compiler_preprocessor_with_recipe(
            path,
            language="fortran",
            config=preprocessing,
        )
        return source, None, recipe.to_dict()
    macro_defines = preprocessing.fortran_macro_defines()
    return (
        path.read_text(encoding="utf-8"),
        macro_defines or None,
        preprocessing.fortran_internal_recipe(path),
    )


def _c_source_loader(preprocessing: PreprocessingConfig):
    if not preprocessing.uses_compiler:
        return None

    def load(path: Path) -> tuple[str, dict[str, object]]:
        source, recipe = run_compiler_preprocessor_with_recipe(
            path,
            language="c",
            config=preprocessing,
        )
        return source, recipe.to_dict()

    return load


def _c_parser_preprocessing_mode(preprocessing: PreprocessingConfig) -> str:
    return "compiler" if preprocessing.uses_compiler else "raw"


def _parse_c_path(
    parser: CParser,
    path: Path,
    preprocessing: PreprocessingConfig,
):
    source_loader = _c_source_loader(preprocessing)
    if source_loader is None:
        return parser.visit_file(
            path,
            filename=str(path),
            include_dirs=preprocessing.include_dirs,
            preprocessing=_c_parser_preprocessing_mode(preprocessing),
        )

    source, preprocessing_recipe = source_loader(path)
    parsed = parser.visit_file(
        source,
        filename=str(path),
        include_dirs=preprocessing.include_dirs,
        preprocessing=_c_parser_preprocessing_mode(preprocessing),
    )
    parsed.preprocessing_recipe = preprocessing_recipe
    return parsed


def _parse_report(paths: list[str], preprocessing: PreprocessingConfig | None = None) -> dict[str, dict]:
    preprocessing = preprocessing or PreprocessingConfig()
    out: dict[str, dict] = {}
    parser = FortranParser()
    for p in _expand_paths(paths):
        code, macro_defines, preprocessing_recipe = _fortran_source_for_path(p, preprocessing)
        parsed = parser.visit_file(code, filename=str(p), macro_defines=macro_defines)
        payload = {
            "signatures": [_to_dict_no_parent(s) for s in parsed.procedures],
            "types": [_to_dict_no_parent(t) for t in parsed.derived_types],
            "modules": [_to_dict_no_parent(m) for m in parsed.modules],
            "submodules": [_to_dict_no_parent(m) for m in parsed.submodules],
            "programs": [_to_dict_no_parent(m) for m in parsed.programs],
            "block_data": [_to_dict_no_parent(m) for m in parsed.block_data_units],
        }
        if preprocessing_recipe is not None:
            payload["preprocessing_recipe"] = preprocessing_recipe
        out[str(p)] = payload
    return out


def _semantic_report(
    paths: list[str],
    preprocessing: PreprocessingConfig | None = None,
    *,
    language: str = "fortran",
) -> dict[str, dict]:
    from semantics.fortran2ir import fortran_module_to_semantic_module
    from semantics.pyi_printer import emit_module

    preprocessing = preprocessing or PreprocessingConfig()
    out: dict[str, dict] = {}
    if language == "c":
        parser = CParser()
        for p in expand_c_paths(paths):
            parsed = _parse_c_path(parser, p, preprocessing)
            modules = c_file_to_semantic_modules(parsed)
            out[str(p)] = {
                "semantic_modules": [asdict(module) for module in modules],
                "pyi": "\n\n".join(emit_module(module) for module in modules).strip(),
            }
        return out

    parser = FortranParser()
    for p in _expand_paths(paths):
        code, macro_defines, _preprocessing_recipe = _fortran_source_for_path(p, preprocessing)
        fobj = parser.visit_file(code, filename=str(p), macro_defines=macro_defines)
        compile_time_values = _fortran_compile_time_values(fobj, preprocessing)
        modules = [
            fortran_module_to_semantic_module(m, compile_time_values=compile_time_values)
            for m in fobj.modules
        ]
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


def _wrap_readiness_report(
    paths: list[str],
    preprocessing: PreprocessingConfig | None = None,
    *,
    language: str = "fortran",
) -> dict[str, dict]:
    preprocessing = preprocessing or PreprocessingConfig()
    out: dict[str, dict] = {}
    if language == "c":
        parser = CParser()
        for p in expand_c_paths(paths):
            parsed = _parse_c_path(parser, p, preprocessing)
            modules = c_file_to_semantic_modules(parsed)
            out[str(p)] = {
                "source_kind": "c",
                "semantic_modules": [asdict(module) for module in modules],
                "wrap_readiness": assess_semantic_wrap_readiness(modules, source=str(p)),
            }
        return out

    parser = FortranParser()
    for p in _expand_readiness_paths(paths):
        if p.suffix.lower() == ".pyi":
            modules = [load_pyi_file(p)]
            source_kind = "pyi"
        else:
            code, macro_defines, _preprocessing_recipe = _fortran_source_for_path(p, preprocessing)
            parsed = parser.visit_file(code, filename=str(p), macro_defines=macro_defines)
            compile_time_values = _fortran_compile_time_values(parsed, preprocessing)
            modules = fortran_file_to_semantic_modules(
                parsed,
                standalone_module_name=p.stem,
                compile_time_values=compile_time_values,
            )
            source_kind = "fortran"

        out[str(p)] = {
            "source_kind": source_kind,
            "semantic_modules": [asdict(module) for module in modules],
            "wrap_readiness": assess_semantic_wrap_readiness(modules, source=str(p)),
        }
    return out


def _fortran_compile_time_values(
    parsed,
    preprocessing: PreprocessingConfig,
) -> dict[str, int] | None:
    """Evaluate compiler-dependent Fortran values when a compiler is configured."""
    if not preprocessing.uses_compiler or not preprocessing.compiler:
        return None

    from semantics.fortran2ir import collect_semantic_compile_time_requirements
    from x2py.fortran_type_probe import evaluate_fortran_type_requirements

    requirements = collect_semantic_compile_time_requirements(parsed)
    if not requirements:
        return None
    return evaluate_fortran_type_requirements(preprocessing, requirements)


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
    if code.startswith("c_"):
        owner = item.get("owner", "<c-source>")
        detail = item.get("type") or item.get("source") or item.get("function") or item.get("parameter")
        return f"{owner}: {detail}" if detail else str(item)
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


def _build_preprocessing_config(args: argparse.Namespace, parser: argparse.ArgumentParser) -> PreprocessingConfig:
    """Build and validate the shared preprocessing CLI configuration."""
    defines = list(args.defines or [])
    undefs = list(args.undefs or [])
    for define in defines:
        try:
            validate_macro_name(define, "--define/-D")
        except PreprocessingError as exc:
            parser.error(str(exc))
    for undef in undefs:
        try:
            validate_macro_name(undef, "--undef/-U")
        except PreprocessingError as exc:
            parser.error(str(exc))

    config = PreprocessingConfig(
        mode=args.preprocess,
        compiler=args.compiler,
        compile_commands=args.compile_commands,
        include_dirs=list(args.include_dirs or []),
        defines=defines,
        undefs=undefs,
        std=args.std,
        compiler_args=list(args.compiler_args or []),
    )

    compiler_only_flags = [
        ("--compiler", args.compiler),
        ("--compile-commands", args.compile_commands),
        ("--std", args.std),
        ("--compiler-arg", args.compiler_args),
    ]
    for option, value in compiler_only_flags:
        if value and not config.uses_compiler:
            parser.error(f"{option} requires --preprocess compiler")

    if config.uses_compiler and not config.compiler and not config.compile_commands:
        parser.error("--preprocess compiler requires --compiler with an exact executable, for example gcc-13 or /usr/bin/clang-18")
    if config.compile_commands and args.language != "c":
        parser.error("--compile-commands is only supported with --language c")
    if config.compile_commands and not config.uses_compiler:
        parser.error("--compile-commands requires --preprocess compiler")
    if args.language == "c" and not config.uses_compiler and (defines or undefs):
        parser.error("-D/--define and -U/--undef affect C only with --preprocess compiler; raw C mode records source macros without selecting branches")
    if args.language == "fortran" and not config.uses_compiler and config.include_dirs:
        parser.error("-I/--include-dir affects Fortran only with --preprocess compiler")
    return config


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
            "    python -m x2py path/to/src_dir --language fortran --parse --print-limit 20\n"
            "  Print parser JSON:\n"
            "    python -m x2py path/to/file.f90 --parse --json\n"
            "  Parse C subset JSON:\n"
            "    python -m x2py path/to/api.h --language c --parse --json\n"
            "  Parse C with an exact compiler executable and API flags:\n"
            "    python -m x2py path/to/api.h --language c --parse --preprocess compiler --compiler clang-18 -I include -D API_EXPORT= --std c11\n"
            "  Parse C with a compiler path and target/sysroot passthrough flags:\n"
            "    python -m x2py path/to/api.c --language c --parse --preprocess compiler --compiler /usr/bin/gcc-13 --compiler-arg=--sysroot=/opt/sdk\n"
            "  Parse C with compile_commands.json for project flags:\n"
            "    python -m x2py path/to/api.c --language c --parse --preprocess compiler --compile-commands build/compile_commands.json\n"
            "  Parse Fortran with internal macro branch selection:\n"
            "    python -m x2py path/to/file.F90 --parse -D USE_MPI -U DEBUG\n"
            "  Parse Fortran with an exact compiler executable:\n"
            "    python -m x2py path/to/file.F90 --parse --preprocess compiler --compiler /usr/bin/gfortran-12 -I include -D USE_MPI\n"
            "  Write parser JSON:\n"
            "    python -m x2py path/to/file.f90 --parse --json --out report.json\n"
            "  Write one JSON file next to each source:\n"
            "    python -m x2py path/to/src_dir --language fortran --parse --out\n"
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
        default=None,
        help=(
            "Frontend language. Omission is allowed for recognizable Fortran files and .pyi readiness input; "
            "C files, directories, and unknown-suffix source inputs require this flag."
        ),
    )
    parser.add_argument("--parse", action="store_true", help="Run and output parser stage report")
    parser.add_argument(
        "--preprocess",
        choices=("internal", "compiler"),
        default="internal",
        help=(
            "Preprocessing mode. 'internal' keeps the current lightweight parser preprocessing "
            "(Fortran macro selection, C raw directive metadata). 'compiler' runs the exact "
            "compiler/preprocessor configured by --compiler or --compile-commands."
        ),
    )
    parser.add_argument(
        "--compiler",
        help=(
            "Exact compiler/preprocessor executable for --preprocess compiler, e.g. gcc-13, "
            "clang-18, /usr/bin/gfortran-12, or /opt/intel/oneapi/compiler/latest/bin/ifx."
        ),
    )
    parser.add_argument(
        "--compile-commands",
        metavar="PATH",
        help="C compile_commands.json database used with --language c --preprocess compiler.",
    )
    parser.add_argument(
        "-I",
        "--include-dir",
        dest="include_dirs",
        action="append",
        metavar="DIR",
        help="Include directory passed as -IDIR during compiler preprocessing.",
    )
    parser.add_argument(
        "-D",
        "--define",
        dest="defines",
        action="append",
        metavar="NAME[=VALUE]",
        help="Define a preprocessing macro. NAME means NAME=1; NAME=VALUE preserves VALUE.",
    )
    parser.add_argument(
        "-U",
        "--undef",
        dest="undefs",
        action="append",
        metavar="NAME",
        help="Undefine a preprocessing macro.",
    )
    parser.add_argument(
        "--std",
        metavar="STANDARD",
        help="Language standard passed to compiler mode, e.g. c11, c23, f2008, or f2018.",
    )
    parser.add_argument(
        "--compiler-arg",
        dest="compiler_args",
        action="append",
        metavar="ARG",
        help="Raw compiler preprocessing argument. Use --compiler-arg=-target for values starting with '-'.",
    )
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
        help="Convert Fortran, C, or .pyi input to semantic IR and show wrapper readiness",
    )
    parser.add_argument("--semantics", action="store_true", help="Generate semantic IR models from parsed source modules")
    parser.add_argument("--pyi", action="store_true", help="Generate semantic Python .pyi content")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    parser.add_argument("--out", nargs="?", const="", type=str, help="Write stage output to file (optional explicit output filename)")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI color in parse diagnostics")
    parser.add_argument("--debug-traceback", action="store_true", help="Re-raise parser errors for debug")
    args = parser.parse_args()
    args.language = _resolve_language(args.paths, args.language, parser)
    preprocessing = _build_preprocessing_config(args, parser)

    if args.language == "c":
        if not (args.parse or args.semantics or args.pyi or args.wrap_readiness):
            parser.error("--language c requires a stage flag: choose one of --parse, --semantics, --pyi, or --wrap-readiness")
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
            parse_c_report(
                args.paths,
                include_dirs=preprocessing.include_dirs,
                preprocessing=_c_parser_preprocessing_mode(preprocessing),
                source_loader=_c_source_loader(preprocessing),
            )
            if args.parse and args.language == "c"
            else _parse_report(args.paths, preprocessing) if args.parse else None
        )
        semantic_payload = _semantic_report(args.paths, preprocessing, language=args.language) if (args.semantics or args.pyi) else None
        readiness_payload = _wrap_readiness_report(args.paths, preprocessing, language=args.language) if args.wrap_readiness else None
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
