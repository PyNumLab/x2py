from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, fields, is_dataclass
from pathlib import Path

from x2py.c_parser.cli import attach_preprocessing_recipe, expand_c_paths, format_c_report, parse_c_report
from x2py.c_parser.models import CParseError
from x2py.c_parser.parser import CParser
from x2py.fortran_parser.cli import _format_report
from x2py.fortran_parser.models import FortranParseError
from x2py.fortran_parser.parser import FortranParser
from x2py.semantics.c2ir import c_project_to_semantic_modules
from x2py.semantics.fortran2ir import fortran_file_to_semantic_modules
from x2py.semantics.pyi_parser import load_pyi_modules
from x2py.semantics.readiness import assess_semantic_wrap_readiness
from x2py.c_type_probe import (
    CStandardTypeProbeError,
    load_c_standard_type_probe_report,
    probe_c_standard_types_cached,
)
from x2py.fortran_type_probe import (
    FortranTypeProbeReport,
    load_fortran_type_probe_report,
)
from x2py.preprocessing import (
    PreprocessingConfig,
    PreprocessingError,
    run_compiler_preprocessor_with_recipe,
    validate_macro_name,
)

_TRUE_VALUES = {"1", "true", "yes", "on"}
_FORTRAN_SOURCE_SUFFIXES = {".f", ".for", ".ftn", ".f77", ".f90", ".f95", ".f03", ".f08"}
_C_SOURCE_SUFFIXES = {".c", ".h", ".i"}
_SOURCE_SUFFIXES_BY_LANGUAGE = {
    "fortran": _FORTRAN_SOURCE_SUFFIXES,
    "c": _C_SOURCE_SUFFIXES,
}
_STAGE_FLAGS_DESCRIPTION = "--parse, --semantics, --pyi, --wrap-readiness, or --wrap"


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
            if f.name == "parent" and not isinstance(value, str | type(None)):
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


def _expand_pyi_paths(paths: list[str]) -> list[Path]:
    expanded: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            expanded.extend(_collect_pyi_extensions(p))
        elif p.suffix.lower() == ".pyi":
            expanded.append(p)
    return sorted(set(expanded))


def _resolve_language(
    paths: list[str],
    requested: str | None,
    parser: argparse.ArgumentParser,
) -> str:
    def language_for_suffix(suffix: str) -> str | None:
        return next(
            (language for language, suffixes in _SOURCE_SUFFIXES_BY_LANGUAGE.items() if suffix in suffixes),
            None,
        )

    if requested is not None:
        for raw in paths:
            path = Path(raw)
            if path.is_dir():
                continue
            suffix = path.suffix.lower()
            detected = language_for_suffix(suffix)
            if detected is not None and detected != requested:
                parser.error(
                    f"{detected.capitalize()} input {path} is incompatible with --language {requested}; "
                    f"pass --language {detected}. Use --help for examples."
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
            parser.error(f"C input {path} requires explicit --language c. Use --help for examples.")
        if suffix not in _FORTRAN_SOURCE_SUFFIXES and suffix != ".pyi":
            parser.error(
                f"Cannot determine the input language for {path}; "
                "pass --language fortran or --language c. Use --help for examples."
            )
    return "fortran"


def _fortran_source_for_path(
    path: Path,
    preprocessing: PreprocessingConfig,
) -> tuple[str, dict[str, object] | None]:
    if preprocessing.uses_compiler:
        source, recipe = run_compiler_preprocessor_with_recipe(
            path,
            language="fortran",
            config=preprocessing,
        )
        return source, recipe.to_dict()
    return (
        path.read_text(encoding="utf-8"),
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
    attach_preprocessing_recipe(parsed, preprocessing_recipe)
    return parsed


def _parse_c_project(
    paths: list[str],
    preprocessing: PreprocessingConfig,
):
    parser = CParser()
    parsed_files = {str(path): _parse_c_path(parser, path, preprocessing) for path in expand_c_paths(paths)}
    return parser.visit_parsed_project(parsed_files)


def _parse_report(paths: list[str], preprocessing: PreprocessingConfig | None = None) -> dict[str, dict]:
    preprocessing = preprocessing or PreprocessingConfig()
    out: dict[str, dict] = {}
    parser = FortranParser()
    for p in _expand_paths(paths):
        code, preprocessing_recipe = _fortran_source_for_path(p, preprocessing)
        parsed = parser.visit_file(code, filename=str(p))
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


def _convert_c_project(project, *, c_standard_type_report: dict[str, object] | None):
    if c_standard_type_report is None:
        return c_project_to_semantic_modules(project)
    return c_project_to_semantic_modules(project, standard_type_report=c_standard_type_report)


def _c_standard_type_report(
    preprocessing: PreprocessingConfig,
    *,
    report_path: str | None = None,
    runner: list[str] | None = None,
    cache_dir: str | None = None,
    refresh: bool = False,
) -> dict[str, object] | None:
    """Load or probe target C ABI facts used by semantic conversion."""
    if report_path is not None:
        return load_c_standard_type_probe_report(report_path).to_dict()
    if not isinstance(preprocessing, PreprocessingConfig) or not preprocessing.compiler:
        return None
    if preprocessing.compile_commands or preprocessing.command_template:
        raise CStandardTypeProbeError(
            "automatic C ABI probing requires a direct compiler configuration; "
            "generate a reusable report with `python -m x2py.c_type_probe` and pass it with --c-type-report"
        )
    return probe_c_standard_types_cached(
        preprocessing,
        runner=runner,
        cache_dir=cache_dir,
        refresh=refresh,
    ).to_dict()


def _fortran_probe_options(
    *,
    report: FortranTypeProbeReport | None,
    runner: list[str] | None,
    cache_dir: str | None,
    refresh: bool,
) -> dict[str, object]:
    options: dict[str, object] = {}
    if report is not None:
        options["report"] = report
    if runner is not None:
        options["runner"] = runner
    if cache_dir is not None:
        options["cache_dir"] = cache_dir
    if refresh:
        options["refresh"] = True
    return options


def _semantic_report(
    paths: list[str],
    preprocessing: PreprocessingConfig | None = None,
    *,
    language: str = "fortran",
    c_standard_type_report: dict[str, object] | None = None,
    fortran_type_report: FortranTypeProbeReport | None = None,
    fortran_type_probe_runner: list[str] | None = None,
    fortran_type_probe_cache_dir: str | None = None,
    refresh_fortran_type_probe: bool = False,
) -> dict[str, dict]:
    preprocessing = preprocessing or PreprocessingConfig()
    if language == "c":
        return _c_semantic_report(paths, preprocessing, c_standard_type_report=c_standard_type_report)
    return _fortran_semantic_report(
        paths,
        preprocessing,
        fortran_type_report=fortran_type_report,
        fortran_type_probe_runner=fortran_type_probe_runner,
        fortran_type_probe_cache_dir=fortran_type_probe_cache_dir,
        refresh_fortran_type_probe=refresh_fortran_type_probe,
    )


def _c_semantic_report(
    paths: list[str],
    preprocessing: PreprocessingConfig,
    *,
    c_standard_type_report: dict[str, object] | None,
) -> dict[str, dict]:
    if c_standard_type_report is None:
        c_standard_type_report = _c_standard_type_report(preprocessing)
    project = _parse_c_project(paths, preprocessing)
    modules_by_source = {
        module.origin.native_name: [module]
        for module in _convert_c_project(project, c_standard_type_report=c_standard_type_report)
    }
    converted_files = [(path, modules_by_source[str(path)]) for path in expand_c_paths(paths)]
    return _semantic_payload_for_converted_files(converted_files)


def _fortran_semantic_report(
    paths: list[str],
    preprocessing: PreprocessingConfig,
    *,
    fortran_type_report: FortranTypeProbeReport | None,
    fortran_type_probe_runner: list[str] | None,
    fortran_type_probe_cache_dir: str | None,
    refresh_fortran_type_probe: bool,
) -> dict[str, dict]:
    from x2py.semantics.fortran2ir import fortran_module_to_semantic_module

    parser = FortranParser()
    parsed_files = []
    for p in _expand_paths(paths):
        code, _preprocessing_recipe = _fortran_source_for_path(p, preprocessing)
        fobj = parser.visit_file(code, filename=str(p))
        parsed_files.append((p, fobj))
    wrapped_derived_types = _fortran_wrapped_derived_types(fobj for _p, fobj in parsed_files)
    converted_files = []
    probe_options = _fortran_probe_options(
        report=fortran_type_report,
        runner=fortran_type_probe_runner,
        cache_dir=fortran_type_probe_cache_dir,
        refresh=refresh_fortran_type_probe,
    )
    for p, fobj in parsed_files:
        compile_time_values = _fortran_compile_time_values(fobj, preprocessing, **probe_options)
        type_facts = _fortran_type_facts(
            fobj,
            preprocessing,
            compile_time_values=compile_time_values,
            **probe_options,
        )
        modules = [
            fortran_module_to_semantic_module(
                m,
                compile_time_values=compile_time_values,
                wrapped_derived_types=wrapped_derived_types,
                **({"type_facts": type_facts} if type_facts is not None else {}),
            )
            for m in fobj.modules
        ]
        converted_files.append((p, modules))
    return _semantic_payload_for_converted_files(converted_files)


def _semantic_payload_for_converted_files(converted_files) -> dict[str, dict]:
    from x2py.codegen.printers.pyi_printer import emit_module_stubs

    out: dict[str, dict] = {}
    available_modules = [module for _p, modules in converted_files for module in modules]
    for p, modules in converted_files:
        stubs = emit_module_stubs(modules, available_modules=available_modules)
        primary_names = {module.name for module in modules}
        out[str(p)] = {
            "semantic_modules": [asdict(m) for m in modules],
            "pyi": "\n\n".join(stubs[module.name] for module in modules).strip(),
        }
        dependencies = {module_name: text for module_name, text in stubs.items() if module_name not in primary_names}
        if dependencies:
            out[str(p)]["pyi_dependencies"] = dependencies
    return out


def _format_pyi_report(semantic_report: dict[str, dict]) -> str:
    lines: list[str] = []
    emitted_dependencies: set[str] = set()
    for fname, payload in semantic_report.items():
        lines.append(f"File: {fname}")
        lines.append(payload.get("pyi") or "<no module declarations found>")
        lines.append("")
        for module_name, text in payload.get("pyi_dependencies", {}).items():
            if module_name in emitted_dependencies:
                continue
            emitted_dependencies.add(module_name)
            lines.append(f"Dependency stub: {module_name}.pyi")
            lines.append(text)
            lines.append("")
    return "\n".join(lines).rstrip()


def _write_pyi_dependencies(
    semantic_report: dict[str, dict],
    *,
    output_dir: Path | None = None,
) -> None:
    outputs: dict[Path, str] = {}
    for fname, payload in semantic_report.items():
        parent = output_dir or Path(fname).parent
        for module_name, text in payload.get("pyi_dependencies", {}).items():
            path = parent.joinpath(*module_name.split(".")).with_suffix(".pyi")
            existing = outputs.get(path)
            if existing is not None and existing != text:
                raise ValueError(f"Conflicting generated dependency stub for {path}")
            outputs[path] = text
    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n", encoding="utf-8")


def _wrap_readiness_report(
    paths: list[str],
    preprocessing: PreprocessingConfig | None = None,
    *,
    language: str = "fortran",
    c_standard_type_report: dict[str, object] | None = None,
    fortran_type_report: FortranTypeProbeReport | None = None,
    fortran_type_probe_runner: list[str] | None = None,
    fortran_type_probe_cache_dir: str | None = None,
    refresh_fortran_type_probe: bool = False,
) -> dict[str, dict]:
    preprocessing = preprocessing or PreprocessingConfig()
    out: dict[str, dict] = {}
    if language == "c":
        c_paths = [path for path in expand_c_paths(paths) if path.suffix.lower() != ".pyi"]
        if c_paths:
            if c_standard_type_report is None:
                c_standard_type_report = _c_standard_type_report(preprocessing)
            project = _parse_c_project([str(path) for path in c_paths], preprocessing)
            converted_files = {
                module.origin.native_name: [module]
                for module in _convert_c_project(project, c_standard_type_report=c_standard_type_report)
            }
            for p in c_paths:
                modules = converted_files[str(p)]
                out[str(p)] = {
                    "source_kind": "c",
                    "semantic_modules": [asdict(module) for module in modules],
                    "wrap_readiness": assess_semantic_wrap_readiness(modules, source=str(p)),
                }
        out.update(_pyi_readiness_report(paths))
        return out

    parser = FortranParser()
    expanded_paths = [path for path in _expand_readiness_paths(paths) if path.suffix.lower() != ".pyi"]
    parsed_files = {}
    for p in expanded_paths:
        code, _preprocessing_recipe = _fortran_source_for_path(p, preprocessing)
        parsed_files[p] = parser.visit_file(code, filename=str(p))
    wrapped_derived_types = _fortran_wrapped_derived_types(parsed_files.values())

    probe_options = _fortran_probe_options(
        report=fortran_type_report,
        runner=fortran_type_probe_runner,
        cache_dir=fortran_type_probe_cache_dir,
        refresh=refresh_fortran_type_probe,
    )
    for p in expanded_paths:
        parsed = parsed_files[p]
        compile_time_values = _fortran_compile_time_values(parsed, preprocessing, **probe_options)
        type_facts = _fortran_type_facts(
            parsed,
            preprocessing,
            compile_time_values=compile_time_values,
            **probe_options,
        )
        modules = fortran_file_to_semantic_modules(
            parsed,
            standalone_module_name=p.stem,
            compile_time_values=compile_time_values,
            wrapped_derived_types=wrapped_derived_types,
            **({"type_facts": type_facts} if type_facts is not None else {}),
        )

        out[str(p)] = {
            "source_kind": "fortran",
            "semantic_modules": [asdict(module) for module in modules],
            "wrap_readiness": assess_semantic_wrap_readiness(modules, source=str(p)),
        }
    out.update(_pyi_readiness_report(paths))
    return out


def _pyi_readiness_report(paths: list[str]) -> dict[str, dict]:
    """Load one edited `.pyi` file set and report each interface path."""

    pyi_paths = _expand_pyi_paths(paths)
    if not pyi_paths:
        return {}
    modules = load_pyi_modules([raw for raw in paths if Path(raw).is_dir() or Path(raw).suffix.lower() == ".pyi"])
    return {
        str(path): {
            "source_kind": "pyi",
            "semantic_modules": [asdict(module) for module in modules],
            "wrap_readiness": assess_semantic_wrap_readiness(modules, source=str(path)),
        }
        for path in pyi_paths
    }


def _fortran_wrapped_derived_types(parsed_files) -> set[tuple[str, str]]:
    return {
        (dtype.module.lower(), dtype.name.lower())
        for parsed in parsed_files
        for module in parsed.modules
        for dtype in module.derived_types
        if dtype.module
    }


def _fortran_compile_time_values(
    parsed,
    preprocessing: PreprocessingConfig,
    *,
    report: FortranTypeProbeReport | None = None,
    runner: list[str] | None = None,
    cache_dir: str | None = None,
    refresh: bool = False,
) -> dict[str, int] | None:
    """Evaluate compiler-dependent Fortran values when a compiler is configured."""
    if report is None and (
        not isinstance(preprocessing, PreprocessingConfig)
        or not preprocessing.uses_compiler
        or not preprocessing.compiler
    ):
        return None

    from x2py.semantics.fortran2ir import collect_semantic_compile_time_requirements
    from x2py.fortran_type_probe import evaluate_fortran_type_requirements

    requirements = collect_semantic_compile_time_requirements(parsed)
    if not requirements:
        return None
    probe_options = _fortran_probe_options(report=report, runner=runner, cache_dir=cache_dir, refresh=refresh)
    return evaluate_fortran_type_requirements(preprocessing, requirements, **probe_options)


def _fortran_type_facts(
    parsed,
    preprocessing: PreprocessingConfig,
    *,
    compile_time_values: dict[str, int] | None = None,
    report: FortranTypeProbeReport | None = None,
    runner: list[str] | None = None,
    cache_dir: str | None = None,
    refresh: bool = False,
) -> dict[tuple[str, str | None], dict[str, object]] | None:
    """Measure compiler-dependent storage for intrinsic types used by one source."""
    if report is None and (
        not isinstance(preprocessing, PreprocessingConfig)
        or not preprocessing.uses_compiler
        or not preprocessing.compiler
    ):
        return None

    from x2py.semantics.fortran2ir import collect_fortran_type_storage_requirements
    from x2py.fortran_type_probe import evaluate_fortran_type_facts

    requirements = collect_fortran_type_storage_requirements(parsed, compile_time_values=compile_time_values)
    if not requirements:
        return None
    probe_options = _fortran_probe_options(report=report, runner=runner, cache_dir=cache_dir, refresh=refresh)
    return evaluate_fortran_type_facts(preprocessing, requirements, **probe_options)


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
        module_names = [module.get("name", "<unknown>") for module in payload.get("semantic_modules", [])]
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
    compiler = args.compiler
    if compiler is None and args.compile_commands is None and args.preprocess_template is None:
        compiler = "cc" if args.language == "c" else "gfortran"
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
        mode="compiler",
        compiler=compiler,
        compile_commands=args.compile_commands,
        adapter=args.preprocessor_adapter,
        command_template=args.preprocess_template,
        include_dirs=list(args.include_dirs or []),
        defines=defines,
        undefs=undefs,
        std=args.std,
        compiler_args=list(args.compiler_args or []),
        include_exposure=args.include_exposure,
        public_includes=list(args.public_includes or []),
        private_includes=list(args.private_includes or []),
    )

    if config.uses_compiler and config.command_template and config.adapter != "command-template":
        parser.error("--preprocess-template requires --preprocessor-adapter command-template")
    return config


def _validate_fortran_type_probe_options(
    *,
    language: str,
    has_semantic_stage: bool,
    report_path: str | None,
    automatic_options: tuple[object, ...],
    parser: argparse.ArgumentParser,
) -> None:
    options_used = bool(report_path or any(automatic_options))
    if language != "fortran":
        if options_used:
            parser.error("Fortran type probe options require --language fortran")
        return
    if options_used and not has_semantic_stage:
        parser.error("Fortran type probe options require --semantics, --pyi, --wrap-readiness, or --wrap")
    if report_path and any(automatic_options):
        parser.error("--fortran-type-report cannot be combined with automatic Fortran type probe options")


def _has_stage(args: argparse.Namespace) -> bool:
    return bool(args.parse or args.semantics or args.pyi or args.wrap_readiness or getattr(args, "wrap", False))


def _path_is_fortran_source(path: str) -> bool:
    return Path(path).suffix.lower() in _FORTRAN_SOURCE_SUFFIXES


def _stage_defaults_to_wrap(args: argparse.Namespace) -> bool:
    return bool(
        args.language == "fortran"
        and not _has_stage(args)
        and any(Path(path).is_dir() or _path_is_fortran_source(path) for path in args.paths)
    )


def _should_run_wrap(args: argparse.Namespace) -> bool:
    return bool(getattr(args, "wrap", False) or _stage_defaults_to_wrap(args))


def _has_semantic_stage(args: argparse.Namespace) -> bool:
    return bool(args.semantics or args.pyi or args.wrap_readiness)


def _automatic_c_type_probe_options(args: argparse.Namespace) -> tuple[object, ...]:
    return (
        getattr(args, "c_type_probe_runner", None),
        getattr(args, "c_type_probe_cache_dir", None),
        getattr(args, "refresh_c_type_probe", False),
    )


def _automatic_fortran_type_probe_options(args: argparse.Namespace) -> tuple[object, ...]:
    return (
        getattr(args, "fortran_type_probe_runner", None),
        getattr(args, "fortran_type_probe_cache_dir", None),
        getattr(args, "refresh_fortran_type_probe", False),
    )


def _c_type_probe_options_used(args: argparse.Namespace) -> bool:
    return bool(getattr(args, "c_type_report", None) or any(_automatic_c_type_probe_options(args)))


def _fortran_type_probe_options_used(args: argparse.Namespace) -> bool:
    return bool(getattr(args, "fortran_type_report", None) or any(_automatic_fortran_type_probe_options(args)))


def _validate_c_type_probe_options(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    report_path = getattr(args, "c_type_report", None)
    automatic_options = _automatic_c_type_probe_options(args)
    options_used = bool(report_path or any(automatic_options))
    if args.language != "c":
        if options_used:
            parser.error("C type probe options require --language c")
        return
    if options_used and not _has_semantic_stage(args):
        parser.error("C type probe options require --semantics, --pyi, or --wrap-readiness")
    if report_path and any(automatic_options):
        parser.error("--c-type-report cannot be combined with automatic C type probe options")


def _validate_wrap_options(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if not _should_run_wrap(args):
        return
    if args.language != "fortran":
        parser.error("--wrap currently requires --language fortran")
    if len(args.paths) != 1:
        parser.error("--wrap expects exactly one Fortran source file")
    if Path(args.paths[0]).is_dir():
        parser.error("--wrap expects a Fortran source file, not a directory")
    if args.parse or args.semantics or args.pyi or args.wrap_readiness:
        parser.error("--wrap cannot be combined with --parse, --semantics, --pyi, or --wrap-readiness")
    if args.out is not None:
        parser.error("--wrap writes build artifacts; use --out-dir instead of --out")


def _validate_c_main_options(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.language != "c":
        return
    if not _has_stage(args):
        parser.error(f"--language c requires a stage flag: choose one of {_STAGE_FLAGS_DESCRIPTION}")
    if args.show_vars:
        parser.error("--show-vars is Fortran-only and is not supported for --language c")


def _validate_output_options(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.out is not None and not _has_stage(args):
        parser.error(f"--out requires a stage flag: choose one of {_STAGE_FLAGS_DESCRIPTION}")
    if (args.show_vars or args.print_limit is not None or args.vars_limit is not None) and not args.parse:
        parser.error("--show-vars/--print-limit require --parse")


def _validate_main_options(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int | None:
    _validate_wrap_options(args, parser)
    _validate_c_main_options(args, parser)

    _validate_c_type_probe_options(args, parser)
    _validate_fortran_type_probe_options(
        language=args.language,
        has_semantic_stage=_has_semantic_stage(args) or _should_run_wrap(args),
        report_path=getattr(args, "fortran_type_report", None),
        automatic_options=_automatic_fortran_type_probe_options(args),
        parser=parser,
    )
    _validate_output_options(args, parser)

    print_limit = args.print_limit if args.print_limit is not None else args.vars_limit
    if print_limit is not None and print_limit < 0:
        parser.error("--print-limit must be >= 0")
    if not _has_stage(args) and not _stage_defaults_to_wrap(args):
        parser.error(f"Select at least one stage flag: {_STAGE_FLAGS_DESCRIPTION}")
    return print_limit


def _load_c_type_report_for_stages(args: argparse.Namespace, preprocessing: PreprocessingConfig):
    if args.language != "c" or not _has_semantic_stage(args):
        return None
    return _c_standard_type_report(
        preprocessing,
        report_path=getattr(args, "c_type_report", None),
        runner=getattr(args, "c_type_probe_runner", None),
        cache_dir=getattr(args, "c_type_probe_cache_dir", None),
        refresh=getattr(args, "refresh_c_type_probe", False),
    )


def _load_fortran_type_report_for_stages(args: argparse.Namespace) -> FortranTypeProbeReport | None:
    report_path = getattr(args, "fortran_type_report", None)
    return load_fortran_type_probe_report(report_path) if report_path is not None else None


def _semantic_stage_options(
    args: argparse.Namespace,
    *,
    c_standard_type_report: dict[str, object] | None,
    fortran_type_report: FortranTypeProbeReport | None,
) -> dict[str, object]:
    options: dict[str, object] = {"language": args.language}
    if c_standard_type_report is not None:
        options["c_standard_type_report"] = c_standard_type_report
    if _fortran_type_probe_options_used(args):
        options.update(
            {
                "fortran_type_report": fortran_type_report,
                "fortran_type_probe_runner": getattr(args, "fortran_type_probe_runner", None),
                "fortran_type_probe_cache_dir": getattr(args, "fortran_type_probe_cache_dir", None),
                "refresh_fortran_type_probe": getattr(args, "refresh_fortran_type_probe", False),
            }
        )
    return options


def _parse_stage_report(args: argparse.Namespace, preprocessing: PreprocessingConfig):
    if not args.parse:
        return None
    if args.language == "c":
        return parse_c_report(
            args.paths,
            include_dirs=preprocessing.include_dirs,
            preprocessing=_c_parser_preprocessing_mode(preprocessing),
            source_loader=_c_source_loader(preprocessing),
        )
    return _parse_report(args.paths, preprocessing)


def _run_stage_reports(args: argparse.Namespace, preprocessing: PreprocessingConfig):
    c_standard_type_report = _load_c_type_report_for_stages(args, preprocessing)
    fortran_type_report = _load_fortran_type_report_for_stages(args)
    semantic_options = _semantic_stage_options(
        args,
        c_standard_type_report=c_standard_type_report,
        fortran_type_report=fortran_type_report,
    )
    parse_payload = _parse_stage_report(args, preprocessing)
    semantic_payload = (
        _semantic_report(args.paths, preprocessing, **semantic_options) if (args.semantics or args.pyi) else None
    )
    readiness_payload = (
        _wrap_readiness_report(args.paths, preprocessing, **semantic_options) if args.wrap_readiness else None
    )
    _attach_wrap_readiness(semantic_payload, readiness_payload)
    return parse_payload, semantic_payload, readiness_payload


def _run_stage_reports_with_diagnostics(args: argparse.Namespace, preprocessing: PreprocessingConfig):
    try:
        return _run_stage_reports(args, preprocessing)
    except CParseError as exc:
        if args.debug or _env_flag("C_PARSER_DEBUG"):
            raise
        print(
            exc.format_diagnostic(color=_diagnostic_color_enabled(disabled=args.no_color), debug=False), file=sys.stderr
        )
    except FortranParseError as exc:
        if args.debug or _env_flag("FORTRAN_PARSER_DEBUG"):
            raise
        print(
            exc.format_diagnostic(color=_diagnostic_color_enabled(disabled=args.no_color), debug=False), file=sys.stderr
        )
    except PreprocessingError as exc:
        if args.debug or _env_flag("X2PY_DEBUG"):
            raise
        if exc.diagnostics:
            for diagnostic in exc.diagnostics:
                location = diagnostic.path or "<preprocessor>"
                if diagnostic.line is not None:
                    location = f"{location}:{diagnostic.line}"
                print(f"{location}: error[{diagnostic.category}]: {diagnostic.message}", file=sys.stderr)
        else:
            print(f"x2py: error[{exc.category}]: {exc}", file=sys.stderr)
    except (SyntaxError, ValueError) as exc:
        if args.debug or _env_flag("X2PY_DEBUG"):
            raise
        print(f"x2py: error: {exc}", file=sys.stderr)
    return None


def _run_wrap_build(args: argparse.Namespace, preprocessing: PreprocessingConfig):
    from x2py.wrapping import build_fortran_extension

    return build_fortran_extension(
        args.paths[0],
        output_dir=getattr(args, "out_dir", None),
        preprocessing=preprocessing,
        strict_wrapper_names=getattr(args, "strict_wrapper_names", False),
        fortran_type_report=_load_fortran_type_report_for_stages(args),
        fortran_type_probe_runner=getattr(args, "fortran_type_probe_runner", None),
        fortran_type_probe_cache_dir=getattr(args, "fortran_type_probe_cache_dir", None),
        refresh_fortran_type_probe=getattr(args, "refresh_fortran_type_probe", False),
        verbose=1 if getattr(args, "verbose", False) else 0,
    )


def _run_wrap_build_with_diagnostics(args: argparse.Namespace, preprocessing: PreprocessingConfig):
    try:
        return _run_wrap_build(args, preprocessing)
    except FortranParseError as exc:
        if args.debug or _env_flag("FORTRAN_PARSER_DEBUG"):
            raise
        print(
            exc.format_diagnostic(color=_diagnostic_color_enabled(disabled=args.no_color), debug=False), file=sys.stderr
        )
    except PreprocessingError as exc:
        if args.debug or _env_flag("X2PY_DEBUG"):
            raise
        if exc.diagnostics:
            for diagnostic in exc.diagnostics:
                location = diagnostic.path or "<preprocessor>"
                if diagnostic.line is not None:
                    location = f"{location}:{diagnostic.line}"
                print(f"{location}: error[{diagnostic.category}]: {diagnostic.message}", file=sys.stderr)
        else:
            print(f"x2py: error[{exc.category}]: {exc}", file=sys.stderr)
    except (FileNotFoundError, RuntimeError, SyntaxError, ValueError) as exc:
        if args.debug or _env_flag("X2PY_DEBUG"):
            raise
        print(f"x2py: error: {exc}", file=sys.stderr)
    return None


def _select_main_payload(args: argparse.Namespace, parse_payload, semantic_payload, readiness_payload):
    if args.parse and args.wrap_readiness and (args.json or args.out is not None):
        return {
            "parse": parse_payload or {},
            "wrap_readiness": readiness_payload or {},
        }
    if args.parse:
        return parse_payload or {}
    if args.semantics or args.pyi:
        return semantic_payload or {}
    return readiness_payload or {}


def _write_pyi_output(args: argparse.Namespace, semantic_payload: dict[str, dict]) -> None:
    if args.out:
        pyi_text = "\n\n".join((report.get("pyi") or "") for report in semantic_payload.values()).strip()
        Path(args.out).write_text(pyi_text + "\n", encoding="utf-8")
        _write_pyi_dependencies(semantic_payload, output_dir=Path(args.out).parent)
        return
    for fname, report in semantic_payload.items():
        Path(fname).with_suffix(".pyi").write_text((report.get("pyi") or "") + "\n", encoding="utf-8")
    _write_pyi_dependencies(semantic_payload)


def _write_json_output(args: argparse.Namespace, payload: dict) -> None:
    if args.out:
        Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return
    for fname, report in payload.items():
        Path(fname).with_suffix(".json").write_text(json.dumps({fname: report}, indent=2), encoding="utf-8")


def _write_main_output(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
    payload: dict,
    semantic_payload: dict[str, dict] | None,
) -> bool:
    if args.out is None:
        return False
    if args.json and args.pyi:
        parser.error("--out cannot be used with both --json and --pyi")
    if args.pyi:
        _write_pyi_output(args, semantic_payload or {})
    else:
        _write_json_output(args, payload)
    return True


def _print_parse_output(args: argparse.Namespace, parse_payload: dict, print_limit: int | None) -> None:
    if args.language == "c":
        print(format_c_report(parse_payload, print_limit=print_limit))
        return
    print(
        _format_report(
            parse_payload,
            show_vars=args.show_vars or args.vars_limit is not None,
            print_limit=print_limit,
        )
    )


def _print_main_output(
    args: argparse.Namespace,
    payload: dict,
    parse_payload: dict[str, dict] | None,
    semantic_payload: dict[str, dict] | None,
    readiness_payload: dict[str, dict] | None,
    print_limit: int | None,
) -> None:
    if args.wrap_readiness:
        _print_wrap_readiness_output(
            args,
            payload,
            parse_payload=parse_payload,
            semantic_payload=semantic_payload,
            readiness_payload=readiness_payload,
            print_limit=print_limit,
        )
        return
    if args.pyi and not args.json:
        print_pyi_output(_format_pyi_report(semantic_payload or {}))
    elif args.parse and not (args.semantics or args.json or args.pyi):
        _print_parse_output(args, parse_payload or {}, print_limit)
    else:
        print(json.dumps(payload, indent=2))


def _print_wrap_readiness_output(
    args: argparse.Namespace,
    payload: dict,
    *,
    parse_payload: dict[str, dict] | None,
    semantic_payload: dict[str, dict] | None,
    readiness_payload: dict[str, dict] | None,
    print_limit: int | None,
) -> None:
    if args.parse and not args.json:
        _print_parse_output(args, parse_payload or {}, print_limit)
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


def _print_wrap_build_output(args: argparse.Namespace, result) -> None:
    payload = result.to_dict()
    if args.json:
        print(json.dumps(payload, indent=2))
        return

    print(f"Built extension: {payload['shared_library']}")
    generated_sources = payload.get("generated_sources") or []
    if generated_sources:
        print("Generated sources:")
        for path in generated_sources:
            print(f"  - {path}")


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
            theme="ansi_dark",  # terminal-friendly
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
            "  Parse C readable report with capped repeated sections:\n"
            "    python -m x2py path/to/api.h --language c --parse --print-limit 50\n"
            "  Parse C with an exact compiler executable and API flags:\n"
            "    python -m x2py path/to/api.h --language c --parse --compiler clang-18 -I include -D API_EXPORT= --std c11\n"
            "  Parse C with a compiler path and target/sysroot passthrough flags:\n"
            "    python -m x2py path/to/api.c --language c --parse --compiler /usr/bin/gcc-13 --compiler-arg=--sysroot=/opt/sdk\n"
            "  Parse C with compile_commands.json for project flags:\n"
            "    python -m x2py path/to/api.c --language c --parse --compile-commands build/compile_commands.json\n"
            "  Parse Fortran with an exact compiler executable:\n"
            "    python -m x2py path/to/file.F90 --parse --compiler /usr/bin/gfortran-12 -I include -D USE_MPI\n"
            "  Parse with a custom preprocessing command template:\n"
            "    python -m x2py path/to/api.h --language c --parse --preprocessor-adapter command-template --preprocess-template 'cc -E {include_dirs} {defines} {source}'\n"
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
            "  Build a Python extension from a Fortran source:\n"
            "    python -m x2py path/to/file.f\n"
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
        "--preprocessor-adapter",
        choices=("auto", "gcc-compatible-c", "gnu-fortran", "command-template"),
        default="auto",
        help="Compiler adapter family. Use command-template for unsupported compiler families.",
    )
    parser.add_argument(
        "--compiler",
        help=(
            "Exact compiler/preprocessor executable, e.g. gcc-13, "
            "clang-18, /usr/bin/gfortran-12, or /opt/intel/oneapi/compiler/latest/bin/ifx."
        ),
    )
    parser.add_argument(
        "--compile-commands",
        metavar="PATH",
        help="compile_commands.json database used for compiler preprocessing.",
    )
    parser.add_argument(
        "--preprocess-template",
        metavar="TEMPLATE",
        help="Custom preprocessing command template. Supported placeholders include {source}, {include_dirs}, {defines}, {undefs}, {standard}, and {compiler_args}.",
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
        "--c-type-report",
        metavar="PATH",
        help="Reuse a C ABI report generated by `python -m x2py.c_type_probe`.",
    )
    parser.add_argument(
        "--c-type-probe-runner",
        dest="c_type_probe_runner",
        action="append",
        metavar="ARG",
        help="Runner command item for a cross-compiled C ABI probe; repeat for arguments.",
    )
    parser.add_argument(
        "--c-type-probe-cache-dir",
        metavar="PATH",
        help="Directory for reusable automatic C ABI probe results.",
    )
    parser.add_argument(
        "--refresh-c-type-probe",
        action="store_true",
        help="Ignore a reusable C ABI result and probe the selected compiler target again.",
    )
    parser.add_argument(
        "--fortran-type-report",
        metavar="PATH",
        help="Reuse a Fortran type report generated by `python -m x2py.fortran_type_probe`.",
    )
    parser.add_argument(
        "--fortran-type-probe-runner",
        dest="fortran_type_probe_runner",
        action="append",
        metavar="ARG",
        help="Runner command item for a cross-compiled Fortran type probe; repeat for arguments.",
    )
    parser.add_argument(
        "--fortran-type-probe-cache-dir",
        metavar="PATH",
        help="Directory for reusable automatic Fortran type probe results.",
    )
    parser.add_argument(
        "--refresh-fortran-type-probe",
        action="store_true",
        help="Ignore reusable Fortran type results and probe the selected compiler target again.",
    )
    parser.add_argument(
        "--include-exposure",
        choices=("reachable-project", "roots-only"),
        default="reachable-project",
        help="Public wrapper exposure policy for reachable included files.",
    )
    parser.add_argument(
        "--public-include",
        dest="public_includes",
        action="append",
        metavar="PATH_OR_PATTERN",
        help="Force a matched included file to be public in wrapper output.",
    )
    parser.add_argument(
        "--private-include",
        dest="private_includes",
        action="append",
        metavar="PATH_OR_PATTERN",
        help="Force a matched included file to be private in wrapper output.",
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
    parser.add_argument(
        "--wrap",
        action="store_true",
        help="Explicitly build a Python extension module from one Fortran source file",
    )
    parser.add_argument(
        "--strict-wrapper-names",
        action="store_true",
        help="Reject Python wrapper names that require escaping or collision suffixes",
    )
    parser.add_argument(
        "--semantics", action="store_true", help="Generate semantic IR models from parsed source modules"
    )
    parser.add_argument("--pyi", action="store_true", help="Generate semantic Python .pyi content")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    parser.add_argument(
        "--out", nargs="?", const="", type=str, help="Write stage output to file (optional explicit output filename)"
    )
    parser.add_argument(
        "--out-dir",
        metavar="DIR",
        help=(
            "Directory for --wrap generated sources, objects, and extension module; "
            "by default build files go in __x2py__ and the extension is written beside the source"
        ),
    )
    parser.add_argument("--verbose", action="store_true", help="Print wrapper compiler commands and build steps")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI color in parse diagnostics")
    parser.add_argument(
        "--debug",
        "--debug-traceback",
        dest="debug",
        action="store_true",
        help="Re-raise parser errors so Python prints a traceback for parser debugging",
    )
    args = parser.parse_args()
    args.language = _resolve_language(args.paths, args.language, parser)
    preprocessing = _build_preprocessing_config(args, parser)
    print_limit = _validate_main_options(args, parser)
    if _should_run_wrap(args):
        result = _run_wrap_build_with_diagnostics(args, preprocessing)
        if result is None:
            return 1
        _print_wrap_build_output(args, result)
        return 0
    reports = _run_stage_reports_with_diagnostics(args, preprocessing)
    if reports is None:
        return 1
    parse_payload, semantic_payload, readiness_payload = reports
    payload = _select_main_payload(args, parse_payload, semantic_payload, readiness_payload)
    if _write_main_output(args, parser, payload, semantic_payload):
        return 0
    _print_main_output(args, payload, parse_payload, semantic_payload, readiness_payload, print_limit)
    return 0
