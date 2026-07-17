from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import sys
from collections.abc import Callable
from dataclasses import asdict, dataclass, fields, is_dataclass, replace
from pathlib import Path

from x2py.parsers.c.cli import attach_preprocessing_recipe, expand_c_paths, format_c_report, parse_c_report
from x2py.parsers.c.models import CParseError
from x2py.parsers.c.parser import CParser
from x2py.parsers.fortran.cli import _format_report
from x2py.parsers.fortran.models import FortranParseError
from x2py.parsers.fortran.parser import FortranParser
from x2py.semantics.c2ir import c_project_to_semantic_modules
from x2py.semantics.fortran2ir import fortran_file_to_semantic_modules
from x2py.pipeline.pyi import pyi_paths_to_semantic_modules
from x2py.semantics.readiness import assess_semantic_wrap_readiness
from x2py.probes.c_types import (
    CStandardTypeProbeError,
    load_c_standard_type_probe_report,
    probe_c_standard_types_cached,
)
from x2py.probes.fortran_types import (
    FortranTypeProbeReport,
    load_fortran_type_probe_report,
)
from x2py.pipeline.preprocessing import (
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
_CLI_HELP_DESCRIPTION = "x2py CLI for source inspection, semantic contracts, and wrapper builds."
_CLI_HELP_EPILOG = (
    "Examples:\n"
    "  Inspect Fortran source:\n"
    "    python3 -m x2py path/to/file.f90 --parse\n"
    "    python3 -m x2py path/to/file.f90 --parse --show-vars\n"
    "    python3 -m x2py path/to/file.f90 --parse --print-limit 50\n"
    "    python3 -m x2py path/to/file.f90 --semantics\n"
    "    python3 -m x2py path/to/file.f90 --pyi --out contracts\n"
    "\n"
    "  Inspect C source:\n"
    "    python3 -m x2py path/to/api.h --language c --parse --json\n"
    "    python3 -m x2py path/to/api.h --language c --parse --print-limit 50\n"
    "\n"
    "  Use compiler preprocessing:\n"
    "    python3 -m x2py path/to/api.h --language c --parse --compiler clang-18 -I include -D API_EXPORT= --std c11\n"
    "    python3 -m x2py path/to/api.c --language c --parse --compiler /usr/bin/gcc-13 --compiler-arg=--sysroot=/opt/sdk\n"
    "    python3 -m x2py path/to/api.c --language c --parse --compile-commands build/compile_commands.json\n"
    "    python3 -m x2py path/to/file.F90 --parse --compiler /usr/bin/gfortran-12 -I include -D USE_MPI\n"
    "    python3 -m x2py path/to/api.h --language c --parse --preprocessor-adapter command-template --preprocess-template 'cc -E {include_dirs} {defines} {source}'\n"
    "\n"
    "  Check wrapper readiness:\n"
    "    python3 -m x2py path/to/file.f90 --wrap-readiness\n"
    "    python3 -m x2py path/to/module.pyi --wrap-readiness --json\n"
    "\n"
    "  Build wrappers:\n"
    "    python3 -m x2py path/to/file.f\n"
    "    python3 -m x2py path/to/file.f90 --out my_extension\n"
    "    python3 -m x2py dependency.f90 api.f90 --makefile --out-dir build\n"
    "    python3 -m x2py contracts/__init__.pyi --out my_extension --native-objects native.o\n"
    "    python3 -m x2py --build-manifest build/x2py-build.json\n"
    "\n"
    "  Write stage output:\n"
    "    python3 -m x2py path/to/file.f90 --parse --json --out report.json\n"
    "    python3 -m x2py path/to/src_dir --language fortran --parse --out\n"
    "\n"
    "Optional:\n"
    "  Install 'rich' for colored terminal syntax highlighting:\n"
    "      pip install rich"
)


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
    return list(dict.fromkeys(expanded))


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
        return parser.parse_file(
            path,
            filename=str(path),
            include_dirs=preprocessing.include_dirs,
            preprocessing=_c_parser_preprocessing_mode(preprocessing),
        )

    source, preprocessing_recipe = source_loader(path)
    parsed = parser.parse_file(
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
    return parser._assemble_project(parsed_files)


def _parse_report(paths: list[str], preprocessing: PreprocessingConfig | None = None) -> dict[str, dict]:
    preprocessing = preprocessing or PreprocessingConfig()
    out: dict[str, dict] = {}
    parser = FortranParser()
    for p in _expand_paths(paths):
        code, preprocessing_recipe = _fortran_source_for_path(p, preprocessing)
        parsed = parser.parse_file(code, filename=str(p))
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
            "generate a reusable report with `python -m x2py.probes.c_types` and pass it with --c-type-report"
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


@dataclass(frozen=True)
class _SemanticPipelineContext:
    paths: list[str]
    source_paths: tuple[Path, ...]
    preprocessing: PreprocessingConfig
    include_contract_paths: bool = False
    c_standard_type_report: dict[str, object] | None = None
    fortran_type_report: FortranTypeProbeReport | None = None
    fortran_type_probe_runner: list[str] | None = None
    fortran_type_probe_cache_dir: str | None = None
    refresh_fortran_type_probe: bool = False


@dataclass(frozen=True)
class _ParsedSemanticSources:
    source_paths: tuple[Path, ...]
    parsed: object


@dataclass(frozen=True)
class _SourceSemanticPipeline:
    parser: Callable[[_SemanticPipelineContext], _ParsedSemanticSources]
    converter_to_ir: Callable[[_ParsedSemanticSources, _SemanticPipelineContext], list[tuple[Path, list[object]]]]


def _source_paths_for_semantic_pipeline(
    paths: list[str],
    *,
    language: str,
    include_contract_paths: bool,
) -> tuple[Path, ...]:
    if language == "c":
        expanded = expand_c_paths(paths)
    elif include_contract_paths:
        expanded = _expand_readiness_paths(paths)
    else:
        expanded = _expand_paths(paths)
    return tuple(path for path in expanded if path.suffix.lower() != ".pyi")


def _converted_semantic_files(
    paths: list[str],
    preprocessing: PreprocessingConfig,
    *,
    language: str,
    include_contract_paths: bool = False,
    c_standard_type_report: dict[str, object] | None = None,
    fortran_type_report: FortranTypeProbeReport | None = None,
    fortran_type_probe_runner: list[str] | None = None,
    fortran_type_probe_cache_dir: str | None = None,
    refresh_fortran_type_probe: bool = False,
) -> list[tuple[Path, list[object]]]:
    context = _SemanticPipelineContext(
        paths=paths,
        source_paths=_source_paths_for_semantic_pipeline(
            paths,
            language=language,
            include_contract_paths=include_contract_paths,
        ),
        preprocessing=preprocessing,
        include_contract_paths=include_contract_paths,
        c_standard_type_report=c_standard_type_report,
        fortran_type_report=fortran_type_report,
        fortran_type_probe_runner=fortran_type_probe_runner,
        fortran_type_probe_cache_dir=fortran_type_probe_cache_dir,
        refresh_fortran_type_probe=refresh_fortran_type_probe,
    )
    pipeline = _SOURCE_SEMANTIC_PIPELINES[language]
    parsed = pipeline.parser(context)
    return pipeline.converter_to_ir(parsed, context)


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
    converted_files = _converted_semantic_files(
        paths,
        preprocessing,
        language=language,
        c_standard_type_report=c_standard_type_report,
        fortran_type_report=fortran_type_report,
        fortran_type_probe_runner=fortran_type_probe_runner,
        fortran_type_probe_cache_dir=fortran_type_probe_cache_dir,
        refresh_fortran_type_probe=refresh_fortran_type_probe,
    )
    return _semantic_payload_for_converted_files(converted_files)


def _parse_fortran_source_files(
    paths: list[Path],
    preprocessing: PreprocessingConfig,
):
    """Parse Fortran sources and resolve cross-file module parameters."""
    parser = FortranParser()
    parsed_files = []
    for path in paths:
        code, _preprocessing_recipe = _fortran_source_for_path(path, preprocessing)
        parsed_files.append((path, parser.parse_file(code, filename=str(path))))

    if len(parsed_files) > 1:
        _resolve_fortran_project_parameters(parser, [parsed for _path, parsed in parsed_files])
    return parsed_files


def _resolve_fortran_project_parameters(parser: FortranParser, parsed_files) -> None:
    """Apply project-wide parameter facts without enforcing global symbols."""
    module_params: dict[str, dict[str, str]] = {}
    for parsed_file in parsed_files:
        if parsed_file.source is not None:
            module_params.update(parser._collect_module_parameters(parsed_file.source, parsed_file.filename))

    seen_procedures: set[int] = set()
    for parsed_file in parsed_files:
        for proc in parsed_file.procedures:
            if id(proc) not in seen_procedures:
                parser._resolve_signature_kinds(proc, module_params, resolve_shapes=False)
                seen_procedures.add(id(proc))
        for module in parsed_file.modules:
            parser._resolve_module_variable_kinds(module, module_params)
            for proc in module.procedures:
                if id(proc) not in seen_procedures:
                    parser._resolve_signature_kinds(proc, module_params, resolve_shapes=False)
                    seen_procedures.add(id(proc))
        for submodule in parsed_file.submodules:
            parser._resolve_module_variable_kinds(submodule, module_params)
            for proc in submodule.procedures:
                if id(proc) not in seen_procedures:
                    parser._resolve_signature_kinds(proc, module_params, resolve_shapes=False)
                    seen_procedures.add(id(proc))
        for program in parsed_file.programs:
            parser._resolve_module_variable_kinds(program, module_params)
        for block_data in parsed_file.block_data_units:
            parser._resolve_module_variable_kinds(block_data, module_params)


def _parse_c_semantic_sources(context: _SemanticPipelineContext) -> _ParsedSemanticSources:
    if not context.source_paths:
        return _ParsedSemanticSources(context.source_paths, None)
    parse_paths = [str(path) for path in context.source_paths] if context.include_contract_paths else context.paths
    return _ParsedSemanticSources(
        context.source_paths,
        _parse_c_project(parse_paths, context.preprocessing),
    )


def _convert_c_semantic_sources(
    parsed_sources: _ParsedSemanticSources,
    context: _SemanticPipelineContext,
) -> list[tuple[Path, list[object]]]:
    if parsed_sources.parsed is None:
        return []
    c_standard_type_report = context.c_standard_type_report
    if c_standard_type_report is None:
        c_standard_type_report = _c_standard_type_report(context.preprocessing)
    modules_by_source = {
        module.origin.native_name: [module]
        for module in _convert_c_project(parsed_sources.parsed, c_standard_type_report=c_standard_type_report)
    }
    return [(path, modules_by_source[str(path)]) for path in parsed_sources.source_paths]


def _parse_fortran_semantic_sources(context: _SemanticPipelineContext) -> _ParsedSemanticSources:
    if not context.source_paths:
        return _ParsedSemanticSources(context.source_paths, [])
    return _ParsedSemanticSources(
        context.source_paths,
        _parse_fortran_source_files(list(context.source_paths), context.preprocessing),
    )


def _convert_fortran_semantic_sources(
    parsed_sources: _ParsedSemanticSources,
    context: _SemanticPipelineContext,
) -> list[tuple[Path, list[object]]]:
    parsed_files = list(parsed_sources.parsed)
    if not parsed_files:
        return []
    wrapped_derived_types = _fortran_wrapped_derived_types(fobj for _p, fobj in parsed_files)
    probe_options = _fortran_probe_options(
        report=context.fortran_type_report,
        runner=context.fortran_type_probe_runner,
        cache_dir=context.fortran_type_probe_cache_dir,
        refresh=context.refresh_fortran_type_probe,
    )
    converted_files = []
    for p, fobj in parsed_files:
        compile_time_values = _fortran_compile_time_values(fobj, context.preprocessing, **probe_options)
        type_facts = _fortran_type_facts(
            fobj,
            context.preprocessing,
            compile_time_values=compile_time_values,
            **probe_options,
        )
        modules = fortran_file_to_semantic_modules(
            fobj,
            standalone_module_name=p.stem,
            compile_time_values=compile_time_values,
            wrapped_derived_types=wrapped_derived_types,
            **({"type_facts": type_facts} if type_facts is not None else {}),
        )
        converted_files.append((p, modules))
    return converted_files


_SOURCE_SEMANTIC_PIPELINES = {
    "c": _SourceSemanticPipeline(
        parser=_parse_c_semantic_sources,
        converter_to_ir=_convert_c_semantic_sources,
    ),
    "fortran": _SourceSemanticPipeline(
        parser=_parse_fortran_semantic_sources,
        converter_to_ir=_convert_fortran_semantic_sources,
    ),
}


def _semantic_payload_for_converted_files(converted_files) -> dict[str, dict]:
    from x2py.wrapper_codegen.printers import emit_module_stubs

    out: dict[str, dict] = {}
    available_modules = [module for _p, modules in converted_files for module in modules]
    primary_names = {module.name for module in available_modules}
    for p, modules in converted_files:
        if _is_fortran_semantic_file(modules):
            out[str(p)] = _fortran_contract_payload(Path(p), modules, available_modules)
            continue
        stubs = emit_module_stubs(modules, available_modules=available_modules)
        module_stubs = {module.name: stubs[module.name] for module in modules}
        out[str(p)] = {
            "semantic_modules": [asdict(m) for m in modules],
            "pyi": "\n\n".join(module_stubs.values()).strip(),
            "pyi_modules": module_stubs,
        }
        dependencies = {module_name: text for module_name, text in stubs.items() if module_name not in primary_names}
        if dependencies:
            out[str(p)]["pyi_dependencies"] = dependencies
    return out


def _is_fortran_semantic_file(modules) -> bool:
    return any(getattr(getattr(module, "origin", None), "source_language", None) == "fortran" for module in modules)


def _fortran_contract_payload(path: Path, modules, available_modules) -> dict[str, object]:
    from x2py.wrapper_codegen.printers import emit_module_stubs

    native_modules = [module for module in modules if module.origin.source_kind == "module"]
    external_modules = [module for module in modules if module.origin.source_kind != "module"]
    root_modules = [module.name for module in native_modules]
    emitted = (
        emit_module_stubs(
            native_modules,
            available_modules=available_modules,
            normalize_fortran_public_names=True,
        )
        if native_modules
        else {}
    )
    module_stubs = {module.name: emitted.pop(module.name) for module in native_modules}
    dependencies = dict(emitted)
    external_text = []
    for module in external_modules:
        external_stubs = emit_module_stubs(
            [module],
            available_modules=available_modules,
            normalize_fortran_public_names=True,
        )
        external_text.append(external_stubs.pop(module.name))
        for name, text in external_stubs.items():
            if name in dependencies and dependencies[name] != text:
                raise ValueError(f"Conflicting generated dependency stub for {name}")
            dependencies[name] = text

    root_stub = _source_root_stub(root_modules, external_text)
    payload: dict[str, object] = {
        "semantic_modules": [asdict(module) for module in modules],
        "pyi": "\n\n".join([*module_stubs.values(), *external_text]).strip(),
        "pyi_modules": module_stubs,
        "pyi_root": root_stub,
        "pyi_root_modules": root_modules,
        "pyi_root_externals": external_text,
    }
    if dependencies:
        payload["pyi_dependencies"] = dependencies
    return payload


def _source_root_stub(module_names: list[str], external_text: list[str]) -> str:
    contract_imports: set[str] = set()
    external_sections = []
    for text in external_text:
        imports, body = _split_contract_imports(text)
        contract_imports.update(imports)
        if body:
            external_sections.append(body)
    contract_section = f"from x2py.contracts import {', '.join(sorted(contract_imports))}" if contract_imports else ""
    lines = [f"from . import {name}" for name in module_names]
    import_section = "\n".join(line for line in [contract_section, *lines] if line)
    sections = [import_section, *external_sections]
    return "\n\n".join(section for section in sections if section).strip()


def _split_contract_imports(text: str) -> tuple[set[str], str]:
    imports: set[str] = set()
    body_lines = []
    for line in text.splitlines():
        if line.startswith("from x2py.contracts import "):
            imports.update(item.strip() for item in line.removeprefix("from x2py.contracts import ").split(","))
            continue
        body_lines.append(line)
    return imports, "\n".join(body_lines).strip()


def _format_pyi_report(semantic_report: dict[str, dict]) -> str:
    lines: list[str] = []
    emitted_dependencies: set[str] = set()
    for fname, payload in semantic_report.items():
        lines.append(f"File: {fname}")
        root = payload.get("pyi_root")
        if root:
            entry_name = (
                "__init__.pyi" if Path(fname).stem in payload.get("pyi_modules", {}) else f"{Path(fname).stem}.pyi"
            )
            lines.append(f"Root contract: {Path(fname).stem}/{entry_name}")
            lines.append(root)
            lines.append("")
        for module_name, text in payload.get("pyi_modules", {}).items():
            lines.append(f"Module contract: {module_name}.pyi")
            lines.append(text)
            lines.append("")
        if not payload.get("pyi_modules"):
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
    converted_files = _converted_semantic_files(
        paths,
        preprocessing,
        language=language,
        include_contract_paths=True,
        c_standard_type_report=c_standard_type_report,
        fortran_type_report=fortran_type_report,
        fortran_type_probe_runner=fortran_type_probe_runner,
        fortran_type_probe_cache_dir=fortran_type_probe_cache_dir,
        refresh_fortran_type_probe=refresh_fortran_type_probe,
    )
    out = {
        str(path): {
            "source_kind": language,
            "semantic_modules": [asdict(module) for module in modules],
            "wrap_readiness": assess_semantic_wrap_readiness(modules, source=str(path)),
        }
        for path, modules in converted_files
    }
    out.update(_pyi_readiness_report(paths, native_language=language))
    return out


def _pyi_readiness_report(paths: list[str], *, native_language: str = "fortran") -> dict[str, dict]:
    """Load one edited `.pyi` file set and report each interface path."""

    pyi_paths = _expand_pyi_paths(paths)
    if not pyi_paths:
        return {}
    modules = pyi_paths_to_semantic_modules(
        [raw for raw in paths if Path(raw).is_dir() or Path(raw).suffix.lower() == ".pyi"],
        native_language=native_language,
    )
    return {
        str(path): {
            "source_kind": "pyi",
            "semantic_modules": [asdict(module) for module in modules],
            "wrap_readiness": assess_semantic_wrap_readiness(
                modules,
                source=str(path),
                require_native_contract=True,
            ),
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
    from x2py.probes.fortran_types import evaluate_fortran_type_requirements

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
    from x2py.probes.fortran_types import evaluate_fortran_type_facts

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
        return f"{item['owner']} needs a complete named @prototype ({needs})"
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


def _selected_stage_flags(args: argparse.Namespace) -> list[str]:
    return [
        flag
        for flag, selected in (
            ("--parse", args.parse),
            ("--semantics", args.semantics),
            ("--pyi", args.pyi),
            ("--wrap-readiness", args.wrap_readiness),
            ("--wrap", getattr(args, "wrap", False)),
        )
        if selected
    ]


def _path_is_fortran_source(path: str) -> bool:
    return Path(path).suffix.lower() in _FORTRAN_SOURCE_SUFFIXES


def _path_is_pyi_contract(path: str) -> bool:
    return Path(path).suffix.lower() == ".pyi"


def _wrap_uses_build_manifest(args: argparse.Namespace) -> bool:
    return _should_run_wrap(args) and getattr(args, "build_manifest", None) is not None


def _wrap_uses_pyi_contract(args: argparse.Namespace) -> bool:
    return (
        _should_run_wrap(args)
        and not _wrap_uses_build_manifest(args)
        and any(_path_is_pyi_contract(path) for path in args.paths)
    )


def _native_link_options_used(args: argparse.Namespace) -> bool:
    return bool(
        getattr(args, "native_fortran_sources", None)
        or getattr(args, "native_fortran_flags", None)
        or getattr(args, "native_objects", None)
        or getattr(args, "native_libraries", None)
        or getattr(args, "native_link_items", None)
        or getattr(args, "native_library_dirs", None)
        or getattr(args, "native_include_dirs", None)
    )


def _wrapper_compile_options_used(args: argparse.Namespace) -> bool:
    return bool(
        getattr(args, "wrapper_compiler_debug", False)
        or getattr(args, "wrapper_fortran_flags", None)
        or getattr(args, "wrapper_c_flags", None)
    )


def _stage_defaults_to_wrap(args: argparse.Namespace) -> bool:
    """Return whether wrapper-specific input selects the default build stage."""
    return bool(
        args.language == "fortran"
        and not _has_stage(args)
        and (
            getattr(args, "build_manifest", None) is not None
            or any(
                Path(path).is_dir() or _path_is_fortran_source(path) or _path_is_pyi_contract(path)
                for path in args.paths
            )
        )
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


def _validate_pyi_wrap_options(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if any(Path(path).is_dir() for path in args.paths):
        parser.error("A .pyi wrapper build expects semantic contract files, not directories")
    if any(not _path_is_pyi_contract(path) for path in args.paths):
        parser.error("A .pyi wrapper build cannot mix positional native sources; pass native artifacts with flags")
    if len(args.paths) != 1:
        parser.error("A .pyi wrapper build accepts exactly one entry contract")
    if not (
        getattr(args, "native_fortran_sources", None)
        or getattr(args, "native_objects", None)
        or getattr(args, "native_libraries", None)
        or getattr(args, "native_link_items", None)
    ):
        parser.error(
            "A .pyi wrapper build requires --native-fortran-sources, --native-objects, "
            "--native-library, or --native-link-item"
        )


def _validate_manifest_wrap_options(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.paths:
        parser.error("--build-manifest replays the saved entry contract; do not pass positional inputs")
    if _native_link_options_used(args):
        parser.error("--build-manifest replays saved native inputs; do not pass native build flags")
    if _wrapper_compile_options_used(args):
        parser.error("--build-manifest replays saved wrapper compiler flags")


def _validate_source_wrap_options(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if not args.paths:
        parser.error("A wrapper build expects at least one Fortran source file or a semantic .pyi contract")
    if _native_link_options_used(args):
        parser.error("Native artifact link flags are only supported for .pyi wrapper builds")
    if any(Path(path).is_dir() for path in args.paths):
        parser.error("A wrapper build expects Fortran source files, not directories")


def _validate_wrapper_out(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.out is None:
        return
    if args.out == "":
        parser.error("--out for wrapper builds requires an output name")
    output_path = Path(args.out)
    if output_path.suffix and output_path.suffix != ".so":
        parser.error("--out for wrapper builds expects NAME or NAME.so")
    if not output_path.stem.isidentifier():
        parser.error("--out for wrapper builds expects a valid Python module name")


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
    if args.parse or args.semantics or args.pyi or args.wrap_readiness:
        parser.error("--wrap cannot be combined with --parse, --semantics, --pyi, or --wrap-readiness")
    if getattr(args, "makefile", False) and getattr(args, "verbose", False):
        parser.error("--makefile cannot be combined with --verbose")
    if args.out is not None and getattr(args, "makefile", False):
        parser.error("--out names a compiled wrapper extension and cannot be combined with --makefile")
    _validate_wrapper_out(args, parser)

    if _wrap_uses_build_manifest(args):
        _validate_manifest_wrap_options(args, parser)
        return

    if _wrap_uses_pyi_contract(args):
        _validate_pyi_wrap_options(args, parser)
        return

    _validate_source_wrap_options(args, parser)


def _validate_c_main_options(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.language != "c":
        return
    if not _has_stage(args):
        parser.error(f"--language c requires a stage flag: choose one of {_STAGE_FLAGS_DESCRIPTION}")
    if args.show_vars:
        parser.error("--show-vars is Fortran-only and is not supported for --language c")


def _validate_output_options(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.out is not None and not (_has_stage(args) or _stage_defaults_to_wrap(args)):
        parser.error(f"--out requires a stage flag: choose one of {_STAGE_FLAGS_DESCRIPTION}")
    if (args.show_vars or args.print_limit is not None or args.vars_limit is not None) and not args.parse:
        parser.error("--show-vars/--print-limit require --parse")


def _validate_stage_selection(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    selected = _selected_stage_flags(args)
    if len(selected) > 1:
        parser.error(f"Choose exactly one stage flag; cannot combine {', '.join(selected)}")


def _validate_main_options(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int | None:
    _validate_stage_selection(args, parser)
    if not args.paths and getattr(args, "build_manifest", None) is None:
        parser.error("Source input is required unless --build-manifest is used")

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


def _cli_native_link_items(raw_items: list[str] | None) -> tuple[dict[str, object], ...]:
    if not raw_items:
        return ()
    aliases = {
        "arg": "linker_argument",
        "archive": "archive",
        "linker-argument": "linker_argument",
        "linker_argument": "linker_argument",
        "library": "named_library",
        "named-library": "named_library",
        "named_library": "named_library",
        "object": "object",
        "shared-library": "shared_library",
        "shared_library": "shared_library",
    }
    parsed = []
    for raw in raw_items:
        kind_text, separator, value = raw.partition(":")
        kind = aliases.get(kind_text)
        if separator != ":" or kind is None or not value:
            raise ValueError(
                "--native-link-item expects KIND:VALUE where KIND is object, archive, shared-library, library, or arg"
            )
        if kind in {"object", "archive", "shared_library"}:
            parsed.append({"kind": kind, "path": value})
        elif kind == "named_library":
            parsed.append({"kind": kind, "name": value})
        else:
            parsed.append({"kind": kind, "argument": value})
    return tuple(parsed)


def _cli_compiler_flags(raw_flags: list[str] | None, *, option_name: str) -> tuple[str, ...]:
    if not raw_flags:
        return ()
    flags = []
    for raw in raw_flags:
        try:
            flags.extend(shlex.split(raw))
        except ValueError as exc:
            raise ValueError(f"Invalid {option_name} value {raw!r}: {exc}") from exc
    return tuple(flags)


def _cli_native_fortran_flags(raw_flags: list[str] | None) -> tuple[str, ...]:
    return _cli_compiler_flags(raw_flags, option_name="--native-fortran-flags")


def _cli_wrapper_fortran_flags(raw_flags: list[str] | None) -> tuple[str, ...]:
    return _cli_compiler_flags(raw_flags, option_name="--wrapper-fortran-flags")


def _cli_wrapper_c_flags(raw_flags: list[str] | None) -> tuple[str, ...]:
    return _cli_compiler_flags(raw_flags, option_name="--wrapper-c-flags")


def _wrapper_shared_library_alias_path(result, raw_out: str | None) -> Path:
    if raw_out in (None, ""):
        return Path.cwd() / f"{result.module_name}.so"

    path = Path(raw_out)
    target = path if path.suffix else path.with_suffix(".so")
    if not target.is_absolute() and target.parent == Path("."):
        return Path.cwd() / target.name
    return target


def _wrapper_output_name(args: argparse.Namespace) -> str | None:
    if getattr(args, "out", None) is None:
        return None
    return Path(args.out).stem


def _copy_wrapper_shared_library_alias(args: argparse.Namespace, result):
    if not result.compiled:
        return result

    target = _wrapper_shared_library_alias_path(result, getattr(args, "out", None))
    if target != result.shared_library:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(result.shared_library, target)

    generated_files = result.generated_files
    if target not in generated_files:
        generated_files = (*generated_files, target)
    return replace(result, shared_library=target, generated_files=generated_files)


def _cli_native_libraries(raw_libraries: list[str] | None) -> tuple[str, ...]:
    if not raw_libraries:
        return ()
    libraries = []
    for raw in raw_libraries:
        try:
            libraries.extend(shlex.split(raw))
        except ValueError as exc:
            raise ValueError(f"Invalid --native-library value {raw!r}: {exc}") from exc
    return tuple(libraries)


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
    from x2py.pipeline.build import build_fortran_extension, build_pyi_extension, build_pyi_extension_from_manifest

    def record_total_build_time(elapsed: float) -> None:
        args._verbose_total_build_time = elapsed

    total_build_time_reporter = record_total_build_time if getattr(args, "verbose", False) else None
    if _wrap_uses_build_manifest(args):
        result = build_pyi_extension_from_manifest(
            args.build_manifest,
            output_name=_wrapper_output_name(args),
            makefile=getattr(args, "makefile", False),
            verbose=1 if getattr(args, "verbose", False) else 0,
            _on_total_build_time=total_build_time_reporter,
        )
        return _copy_wrapper_shared_library_alias(args, result)

    if _wrap_uses_pyi_contract(args):
        result = build_pyi_extension(
            args.paths[0],
            native_fortran_sources=getattr(args, "native_fortran_sources", None),
            native_fortran_flags=_cli_native_fortran_flags(getattr(args, "native_fortran_flags", None)),
            native_objects=getattr(args, "native_objects", None),
            native_libraries=_cli_native_libraries(getattr(args, "native_libraries", None)),
            native_link_items=_cli_native_link_items(getattr(args, "native_link_items", None)),
            native_library_dirs=getattr(args, "native_library_dirs", None),
            native_include_dirs=getattr(args, "native_include_dirs", None),
            output_name=_wrapper_output_name(args),
            output_dir=getattr(args, "out_dir", None),
            strict_wrapper_names=getattr(args, "strict_wrapper_names", False),
            makefile=getattr(args, "makefile", False),
            verbose=1 if getattr(args, "verbose", False) else 0,
            wrapper_compiler_debug=getattr(args, "wrapper_compiler_debug", False),
            wrapper_fortran_flags=_cli_wrapper_fortran_flags(getattr(args, "wrapper_fortran_flags", None)),
            wrapper_c_flags=_cli_wrapper_c_flags(getattr(args, "wrapper_c_flags", None)),
            _on_total_build_time=total_build_time_reporter,
        )
        return _copy_wrapper_shared_library_alias(args, result)

    result = build_fortran_extension(
        args.paths,
        output_dir=getattr(args, "out_dir", None),
        output_name=_wrapper_output_name(args),
        preprocessing=preprocessing,
        strict_wrapper_names=getattr(args, "strict_wrapper_names", False),
        fortran_type_report=_load_fortran_type_report_for_stages(args),
        fortran_type_probe_runner=getattr(args, "fortran_type_probe_runner", None),
        fortran_type_probe_cache_dir=getattr(args, "fortran_type_probe_cache_dir", None),
        refresh_fortran_type_probe=getattr(args, "refresh_fortran_type_probe", False),
        makefile=getattr(args, "makefile", False),
        verbose=1 if getattr(args, "verbose", False) else 0,
        wrapper_compiler_debug=getattr(args, "wrapper_compiler_debug", False),
        wrapper_fortran_flags=_cli_wrapper_fortran_flags(getattr(args, "wrapper_fortran_flags", None)),
        wrapper_c_flags=_cli_wrapper_c_flags(getattr(args, "wrapper_c_flags", None)),
        _on_total_build_time=total_build_time_reporter,
    )
    return _copy_wrapper_shared_library_alias(args, result)


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
    if args.parse:
        return parse_payload or {}
    if args.semantics or args.pyi:
        return semantic_payload or {}
    return readiness_payload or {}


def _write_pyi_output(args: argparse.Namespace, semantic_payload: dict[str, dict]) -> None:
    if any("pyi_root" in report for report in semantic_payload.values()):
        output_parent = Path(args.out) if args.out else None
        if output_parent is not None and output_parent.suffix.lower() == ".pyi":
            raise ValueError(
                "--out for Fortran --pyi expects a directory, not a single .pyi file; "
                "generated contracts use one file per module"
            )
        _write_fortran_contract_packages(semantic_payload, output_parent=output_parent)
        return
    if args.out:
        roots = [report.get("pyi_root") for report in semantic_payload.values() if report.get("pyi_root")]
        pyi_text = "\n\n".join(roots).strip()
        if not pyi_text:
            pyi_text = "\n\n".join((report.get("pyi") or "") for report in semantic_payload.values()).strip()
        Path(args.out).write_text(pyi_text + "\n", encoding="utf-8")
        _write_pyi_modules(semantic_payload, output_dir=Path(args.out).parent, skip=Path(args.out))
        _write_pyi_dependencies(semantic_payload, output_dir=Path(args.out).parent)
        return
    _write_pyi_modules(semantic_payload)
    for fname, report in semantic_payload.items():
        root = report.get("pyi_root")
        if root:
            Path(fname).with_suffix(".pyi").write_text(root + "\n", encoding="utf-8")
    _write_pyi_dependencies(semantic_payload)


def _write_fortran_contract_packages(
    semantic_payload: dict[str, dict],
    *,
    output_parent: Path | None,
) -> None:
    if output_parent is not None:
        for relative_path, text in _combined_fortran_contract_files(semantic_payload).items():
            target = output_parent / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text + "\n", encoding="utf-8")
        return

    for fname, report in semantic_payload.items():
        source = Path(fname)
        for relative_path, text in _fortran_contract_files(source, report).items():
            target = source.parent / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text + "\n", encoding="utf-8")


def _combined_fortran_contract_files(semantic_payload: dict[str, dict]) -> dict[Path, str]:
    module_names: list[str] = []
    external_text: list[str] = []
    files: dict[Path, str] = {}
    dependency_files: dict[Path, str] = {}

    for report in semantic_payload.values():
        for module_name in report.get("pyi_root_modules", ()):
            if module_name not in module_names:
                module_names.append(module_name)
        external_text.extend(str(text) for text in report.get("pyi_root_externals", ()))
        _merge_contract_mapping(files, Path(), report.get("pyi_modules", {}))
        _merge_contract_mapping(dependency_files, Path(), report.get("pyi_dependencies", {}))

    package_files = {Path("__init__.pyi"): _source_root_stub(module_names, external_text)}
    package_files.update(files)
    for path, text in dependency_files.items():
        existing = package_files.get(path)
        if existing is not None and existing != text:
            raise ValueError(f"Conflicting generated contract for {path}")
        package_files[path] = text
    return package_files


def _fortran_contract_files(source: Path, report: dict[str, object]) -> dict[Path, str]:
    package_dir = Path(source.stem)
    entry_name = "__init__.pyi" if source.stem in report.get("pyi_modules", {}) else f"{source.stem}.pyi"
    files = {package_dir / entry_name: str(report.get("pyi_root", ""))}
    _add_contract_mapping(files, package_dir, report.get("pyi_modules", {}))
    _add_contract_mapping(files, package_dir, report.get("pyi_dependencies", {}))
    return files


def _add_contract_mapping(files: dict[Path, str], package_dir: Path, contracts: object) -> None:
    _merge_contract_mapping(files, package_dir, contracts)


def _merge_contract_mapping(files: dict[Path, str], package_dir: Path, contracts: object) -> None:
    if not isinstance(contracts, dict):
        raise TypeError("Generated contract mapping must be a dictionary")
    for module_name, text in contracts.items():
        target = package_dir.joinpath(*str(module_name).split(".")).with_suffix(".pyi")
        contract_text = str(text)
        existing = files.get(target)
        if existing is not None and existing != contract_text:
            raise ValueError(f"Conflicting generated contract for {target}")
        files[target] = contract_text


def _write_pyi_modules(
    semantic_payload: dict[str, dict],
    *,
    output_dir: Path | None = None,
    skip: Path | None = None,
) -> None:
    for fname, report in semantic_payload.items():
        target_dir = output_dir or Path(fname).parent
        for module_name, text in report.get("pyi_modules", {}).items():
            target = target_dir.joinpath(module_name).with_suffix(".pyi")
            if skip is not None and target.resolve() == skip.resolve():
                continue
            target.write_text(text + "\n", encoding="utf-8")


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
    _payload: dict,
    *,
    parse_payload: dict[str, dict] | None,
    semantic_payload: dict[str, dict] | None,
    readiness_payload: dict[str, dict] | None,
    print_limit: int | None,
) -> None:
    _ = (parse_payload, semantic_payload, print_limit)
    if args.json:
        print(json.dumps(readiness_payload or {}, indent=2))
    else:
        print(_format_semantic_readiness(readiness_payload or {}))


def _print_wrap_build_output(args: argparse.Namespace, result) -> None:
    payload = result.to_dict()
    if args.json:
        print(json.dumps(payload, indent=2))
        _print_verbose_total_build_time(args)
        return

    if payload.get("compiled", True):
        print(f"Built extension: {payload['shared_library']}")
    else:
        if payload.get("build_manifest"):
            print(f"Generated build manifest: {payload['build_manifest']}")
        print(f"Generated Makefile: {payload['build_makefile']}")
        print(f"Shared library target: {payload['shared_library']}")
        print(f"Build with: make -f {payload['build_makefile']} -j")
    generated_sources = payload.get("generated_sources") or []
    if generated_sources:
        print("Generated sources:")
        for path in generated_sources:
            print(f"  - {path}")
    _print_verbose_total_build_time(args)


def _print_verbose_total_build_time(args: argparse.Namespace) -> None:
    """Print the delayed CLI total after its final artifact summary line."""
    elapsed = getattr(args, "_verbose_total_build_time", None)
    if elapsed is not None:
        print(f">> Total build time: {elapsed:.3f}s")


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
        prog="python3 -m x2py",
        description=_CLI_HELP_DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_CLI_HELP_EPILOG,
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Source file(s), .pyi file(s), or directory path(s); omit when using --build-manifest",
    )

    input_group = parser.add_argument_group("input selection")
    inspection_group = parser.add_argument_group("inspection stages")
    preprocessing_group = parser.add_argument_group("compiler preprocessing")
    type_probe_group = parser.add_argument_group("target type probes")
    include_group = parser.add_argument_group("C include exposure")
    parse_report_group = parser.add_argument_group("parse report controls")
    wrapper_group = parser.add_argument_group("wrapper builds")
    output_group = parser.add_argument_group("output and diagnostics")

    input_group.add_argument(
        "--language",
        choices=("fortran", "c"),
        default=None,
        help=(
            "Frontend language. Omission is allowed for recognizable Fortran files and .pyi readiness input; "
            "C files, directories, and unknown-suffix source inputs require this flag."
        ),
    )
    inspection_group.add_argument("--parse", action="store_true", help="Run and output parser stage report")
    inspection_group.add_argument(
        "--semantics", action="store_true", help="Generate semantic IR models from parsed source modules"
    )
    inspection_group.add_argument("--pyi", action="store_true", help="Generate semantic Python .pyi content")
    inspection_group.add_argument(
        "--wrap-readiness",
        action="store_true",
        help="Convert Fortran, C, or .pyi input to semantic IR and show wrapper readiness",
    )
    preprocessing_group.add_argument(
        "--preprocessor-adapter",
        choices=("auto", "gcc-compatible-c", "gnu-fortran", "command-template"),
        default="auto",
        help="Compiler adapter family. Use command-template for unsupported compiler families.",
    )
    preprocessing_group.add_argument(
        "--compiler",
        help=(
            "Exact compiler/preprocessor executable, e.g. gcc-13, "
            "clang-18, /usr/bin/gfortran-12, or /opt/intel/oneapi/compiler/latest/bin/ifx."
        ),
    )
    preprocessing_group.add_argument(
        "--compile-commands",
        metavar="PATH",
        help="compile_commands.json database used for compiler preprocessing.",
    )
    preprocessing_group.add_argument(
        "--preprocess-template",
        metavar="TEMPLATE",
        help="Custom preprocessing command template. Supported placeholders include {source}, {include_dirs}, {defines}, {undefs}, {standard}, and {compiler_args}.",
    )
    preprocessing_group.add_argument(
        "-I",
        "--include-dir",
        dest="include_dirs",
        action="append",
        metavar="DIR",
        help="Include directory passed as -IDIR during compiler preprocessing.",
    )
    preprocessing_group.add_argument(
        "-D",
        "--define",
        dest="defines",
        action="append",
        metavar="NAME[=VALUE]",
        help="Define a preprocessing macro. NAME means NAME=1; NAME=VALUE preserves VALUE.",
    )
    preprocessing_group.add_argument(
        "-U",
        "--undef",
        dest="undefs",
        action="append",
        metavar="NAME",
        help="Undefine a preprocessing macro.",
    )
    preprocessing_group.add_argument(
        "--std",
        metavar="STANDARD",
        help="Language standard passed to compiler mode, e.g. c11, c23, f2008, or f2018.",
    )
    preprocessing_group.add_argument(
        "--compiler-arg",
        dest="compiler_args",
        action="append",
        metavar="ARG",
        help="Raw compiler preprocessing argument. Use --compiler-arg=-target for values starting with '-'.",
    )
    type_probe_group.add_argument(
        "--c-type-report",
        metavar="PATH",
        help="Reuse a C ABI report generated by `python3 -m x2py.probes.c_types`.",
    )
    type_probe_group.add_argument(
        "--c-type-probe-runner",
        dest="c_type_probe_runner",
        action="append",
        metavar="ARG",
        help="Runner command item for a cross-compiled C ABI probe; repeat for arguments.",
    )
    type_probe_group.add_argument(
        "--c-type-probe-cache-dir",
        metavar="PATH",
        help="Directory for reusable automatic C ABI probe results.",
    )
    type_probe_group.add_argument(
        "--refresh-c-type-probe",
        action="store_true",
        help="Ignore a reusable C ABI result and probe the selected compiler target again.",
    )
    type_probe_group.add_argument(
        "--fortran-type-report",
        metavar="PATH",
        help="Reuse a Fortran type report generated by `python3 -m x2py.probes.fortran_types`.",
    )
    type_probe_group.add_argument(
        "--fortran-type-probe-runner",
        dest="fortran_type_probe_runner",
        action="append",
        metavar="ARG",
        help="Runner command item for a cross-compiled Fortran type probe; repeat for arguments.",
    )
    type_probe_group.add_argument(
        "--fortran-type-probe-cache-dir",
        metavar="PATH",
        help="Directory for reusable automatic Fortran type probe results.",
    )
    type_probe_group.add_argument(
        "--refresh-fortran-type-probe",
        action="store_true",
        help="Ignore reusable Fortran type results and probe the selected compiler target again.",
    )
    include_group.add_argument(
        "--include-exposure",
        choices=("reachable-project", "roots-only"),
        default="reachable-project",
        help="Public wrapper exposure policy for reachable included files.",
    )
    include_group.add_argument(
        "--public-include",
        dest="public_includes",
        action="append",
        metavar="PATH_OR_PATTERN",
        help="Force a matched included file to be public in wrapper output.",
    )
    include_group.add_argument(
        "--private-include",
        dest="private_includes",
        action="append",
        metavar="PATH_OR_PATTERN",
        help="Force a matched included file to be private in wrapper output.",
    )
    parse_report_group.add_argument(
        "--show-vars",
        action="store_true",
        help="Include module, submodule, program, and block-data variables in the human-readable parse report.",
    )
    parse_report_group.add_argument(
        "--print-limit",
        type=int,
        metavar="N",
        help="Show at most N items per repeated section in the human-readable parse report.",
    )
    parse_report_group.add_argument(
        "--vars-limit",
        type=int,
        metavar="N",
        help=argparse.SUPPRESS,
    )
    wrapper_group.add_argument(
        "--wrap",
        action="store_true",
        help="Explicitly build one Python extension module from Fortran source files or semantic .pyi contracts",
    )
    wrapper_group.add_argument(
        "--makefile",
        action="store_true",
        help="Generate wrapper sources and a GNU Make build without compiling",
    )
    wrapper_group.add_argument(
        "--strict-wrapper-names",
        action="store_true",
        help="Reject Python wrapper names that require escaping or collision suffixes",
    )
    wrapper_group.add_argument(
        "--wrapper-compiler-debug",
        action="store_true",
        help="Use the compiler debug profile for direct wrapper builds instead of the default release profile",
    )
    wrapper_group.add_argument(
        "--wrapper-fortran-flags",
        dest="wrapper_fortran_flags",
        action="extend",
        nargs="+",
        metavar="FLAG",
        help="Fortran compiler flags appended to generated wrapper bridge compilation commands",
    )
    wrapper_group.add_argument(
        "--wrapper-c-flags",
        dest="wrapper_c_flags",
        action="extend",
        nargs="+",
        metavar="FLAG",
        help="C compiler flags appended to generated CPython wrapper compilation commands",
    )
    wrapper_group.add_argument(
        "--build-manifest",
        metavar="PATH",
        help="Replay a saved semantic .pyi wrapper build manifest",
    )
    wrapper_group.add_argument(
        "--native-fortran-sources",
        dest="native_fortran_sources",
        action="extend",
        nargs="+",
        metavar="PATH",
        help="Native Fortran implementation source paths compiled for a .pyi wrapper build",
    )
    wrapper_group.add_argument(
        "--native-fortran-flags",
        dest="native_fortran_flags",
        action="extend",
        nargs="+",
        metavar="FLAG",
        help="Fortran compiler flags applied to each source passed with --native-fortran-sources",
    )
    wrapper_group.add_argument(
        "--native-objects",
        dest="native_objects",
        action="extend",
        nargs="+",
        metavar="PATH",
        help="Native object, static archive, or shared library paths linked into a .pyi wrapper build",
    )
    wrapper_group.add_argument(
        "--native-library",
        dest="native_libraries",
        action="extend",
        nargs="+",
        metavar="NAME",
        help="Native libraries linked into a .pyi wrapper build, passed as -lNAME unless already prefixed",
    )
    wrapper_group.add_argument(
        "--native-link-item",
        dest="native_link_items",
        action="extend",
        nargs="+",
        metavar="KIND:VALUE",
        help="Ordered native link items for .pyi builds: object, archive, shared-library, library, or arg",
    )
    wrapper_group.add_argument(
        "--native-library-dir",
        "--library-dir",
        dest="native_library_dirs",
        action="extend",
        nargs="+",
        metavar="DIR",
        help="Directories searched and added to rpath for native libraries in a .pyi wrapper build",
    )
    wrapper_group.add_argument(
        "--native-include-dir",
        dest="native_include_dirs",
        action="extend",
        nargs="+",
        metavar="DIR",
        help="Directories containing native module/interface files needed to compile .pyi wrapper bridges",
    )
    output_group.add_argument("--json", action="store_true", help="Print JSON to stdout")
    output_group.add_argument(
        "--out",
        nargs="?",
        const="",
        type=str,
        help=(
            "Write stage output, select the generated Fortran .pyi package directory, "
            "or name the wrapper Python module and final .so"
        ),
    )
    output_group.add_argument(
        "--out-dir",
        metavar="DIR",
        help=(
            "Directory for --wrap generated sources, objects, and extension module; "
            "by default build files and the ABI-suffixed extension go in ./__x2py__, "
            "with a stable .so alias in the current directory"
        ),
    )
    output_group.add_argument("--verbose", action="store_true", help="Print wrapper compiler commands and build steps")
    output_group.add_argument("--no-color", action="store_true", help="Disable ANSI color in parse diagnostics")
    output_group.add_argument(
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
