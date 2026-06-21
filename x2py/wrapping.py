"""End-to-end Fortran-to-Python extension build pipeline."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
import shlex

from filelock import FileLock

from x2py.codegen.codegen import Codegen
from x2py.codegen.scope import Scope
from x2py.compiling.basic import CompileObj
from x2py.compiling.compilers import Compiler, get_condaless_search_path
from x2py.compiling.python_wrapper import create_shared_library
from x2py.fortran_parser.parser import parse_fortran_project
from x2py.fortran_type_probe import evaluate_fortran_type_facts, evaluate_fortran_type_requirements
from x2py.naming.public import PublicNamePolicy
from x2py.preprocessing import PreprocessingConfig, preprocess_source
from x2py.semantics.fortran2ir import (
    collect_fortran_type_storage_requirements,
    collect_semantic_compile_time_requirements,
    fortran_project_to_semantic_modules,
)
from x2py.semantics.ir2ast import semantic_ir_to_codegen_ast
from x2py.semantics.models import SemanticModule
from x2py.semantics.pyi_parser import load_pyi_modules


_DEFAULT_BUILD_DIR_NAME = "__x2py__"
_FORTRAN_SOURCE_SUFFIXES = {".f", ".f03", ".f08", ".f77", ".f90", ".f95", ".for", ".ftn"}
_C_SOURCE_SUFFIXES = {".c"}


@dataclass(frozen=True)
class WrapperBuildResult:
    """Artifacts produced by one wrapper build."""

    sources: tuple[Path, ...]
    module_name: str
    output_dir: Path
    shared_library: Path
    build_makefile: Path | None
    compiled: bool
    generated_sources: tuple[Path, ...]
    generated_files: tuple[Path, ...]
    native_inputs: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "sources": [str(source) for source in self.sources],
            "module_name": self.module_name,
            "output_dir": str(self.output_dir),
            "shared_library": str(self.shared_library),
            "build_makefile": str(self.build_makefile) if self.build_makefile is not None else None,
            "compiled": self.compiled,
            "generated_sources": [str(path) for path in self.generated_sources],
            "generated_files": [str(path) for path in self.generated_files],
            "native_inputs": list(self.native_inputs),
        }


def _default_preprocessing_config() -> PreprocessingConfig:
    return PreprocessingConfig(
        mode="compiler",
        compiler="gfortran",
        defines=[],
        include_dirs=[],
    )


def _fortran_source_for_pipeline(path: Path, preprocessing: PreprocessingConfig) -> str:
    if preprocessing.uses_compiler:
        return preprocess_source(path, language="fortran", config=preprocessing).source
    return path.read_text(encoding="utf-8")


def _new_gnu_compiler(*, execute_commands: bool = True) -> Compiler:
    Compiler.acceptable_bin_paths = get_condaless_search_path("verbose")
    return Compiler("GNU", debug=True, execute_commands=execute_commands)


def _expected_generated_files(
    *,
    source_objects: tuple[CompileObj, ...],
    output_dir: Path,
    module_name: str,
    shared_library: Path,
) -> tuple[Path, ...]:
    candidates = [
        *(source_obj.module_target for source_obj in source_objects),
        output_dir / f"bind_c_{module_name}.mod",
        output_dir / f"bind_c_{module_name}_wrapper.f90",
        output_dir / f"bind_c_{module_name}_wrapper.o",
        output_dir / f"{module_name}_wrapper.c",
        output_dir / f"{module_name}_wrapper.h",
        output_dir / f"{module_name}_wrapper.o",
        shared_library,
    ]
    runtime_support_dir = output_dir / "x2py_runtime"
    if runtime_support_dir.is_dir():
        candidates.extend(sorted(path for path in runtime_support_dir.rglob("*") if path.is_file()))
    return tuple(path for path in candidates if path.exists())


def _source_compile_object(source_path: Path, output_dir: Path, *, object_stem: str) -> CompileObj:
    compile_obj = CompileObj(
        file_name=source_path.name,
        folder=str(source_path.parent),
        has_target_file=True,
    )
    target = output_dir / f"{object_stem}.o"
    if target != compile_obj.module_target:
        compile_obj._module_target = target
        compile_obj._lock_target = FileLock(str(target.with_suffix(target.suffix + ".lock")))
        compile_obj._include.add(output_dir)
    return compile_obj


def _source_paths(sources: str | Path | Iterable[str | Path]) -> tuple[Path, ...]:
    paths = (Path(sources),) if isinstance(sources, str | Path) else tuple(Path(source) for source in sources)
    if not paths:
        raise ValueError("wrapper build requires at least one Fortran source file")
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(f"Fortran source not found: {path}")
    return paths


def _pyi_contract_paths(contracts: str | Path | Iterable[str | Path]) -> tuple[Path, ...]:
    paths = (Path(contracts),) if isinstance(contracts, str | Path) else tuple(Path(contract) for contract in contracts)
    if not paths:
        raise ValueError(".pyi wrapper build requires at least one semantic contract file")
    for path in paths:
        if path.suffix.lower() != ".pyi":
            raise ValueError(f".pyi wrapper build expects semantic contract files, not {path}")
        if not path.is_file():
            raise FileNotFoundError(f"Semantic .pyi contract not found: {path}")
    return paths


def _existing_paths(
    paths: Iterable[str | Path] | None,
    *,
    kind: str,
    require_directory: bool = False,
) -> tuple[Path, ...]:
    resolved = tuple(Path(path) for path in (paths or ()))
    for path in resolved:
        if require_directory:
            if not path.is_dir():
                raise FileNotFoundError(f"{kind} directory not found: {path}")
        elif not path.is_file():
            raise FileNotFoundError(f"{kind} not found: {path}")
    return resolved


def _native_artifact_compile_object(path: Path) -> CompileObj:
    compile_obj = CompileObj(
        file_name=path.name,
        folder=str(path.parent),
        has_target_file=True,
        include=(path.parent,),
        libdir=(path.parent,) if path.suffix.lower() in {".so", ".dylib", ".dll"} else (),
    )
    if compile_obj.module_target != path:
        compile_obj._module_target = path
        compile_obj._lock_target = FileLock(str(path.with_suffix(path.suffix + ".lock")))
    return compile_obj


def _normalize_pyi_modules_for_fortran_wrapping(modules: Iterable[SemanticModule]) -> None:
    for module in modules:
        native_module_name = str(module.origin.native_name or module.name)
        _normalize_module_origin(module, native_module_name)
        for variable in module.variables:
            _normalize_variable_origin(variable, native_module_name, source_kind="variable")
        for function in module.functions:
            _normalize_function_origin(function, native_module_name, source_kind="function")
        for overload_set in module.overload_sets:
            for procedure in overload_set.procedures:
                _normalize_function_origin(procedure, native_module_name, source_kind="function")
        for semantic_class in module.classes:
            _normalize_class_origin(semantic_class, native_module_name)


def _normalize_module_origin(module: SemanticModule, native_module_name: str) -> None:
    module.origin.source_language = module.origin.source_language or "fortran"
    module.origin.native_name = module.origin.native_name or native_module_name
    module.origin.native_scope = module.origin.native_scope or native_module_name
    module.origin.source_kind = module.origin.source_kind or "module"


def _normalize_variable_origin(variable, native_module_name: str, *, source_kind: str) -> None:
    variable.origin.source_language = variable.origin.source_language or "fortran"
    variable.origin.native_name = variable.origin.native_name or variable.name
    variable.origin.native_scope = variable.origin.native_scope or native_module_name
    variable.origin.source_kind = variable.origin.source_kind or source_kind


def _normalize_function_origin(function, native_module_name: str, *, source_kind: str) -> None:
    function.origin.source_language = function.origin.source_language or "fortran"
    function.origin.native_name = function.origin.native_name or function.native_name or function.name
    function.origin.native_scope = function.origin.native_scope or native_module_name
    function.origin.source_kind = function.origin.source_kind or source_kind
    function.native_name = function.native_name or function.name
    for argument in function.arguments:
        _normalize_variable_origin(argument, native_module_name, source_kind="argument")


def _normalize_class_origin(semantic_class, native_module_name: str) -> None:
    semantic_class.origin.source_language = semantic_class.origin.source_language or "fortran"
    semantic_class.origin.native_name = (
        semantic_class.origin.native_name or semantic_class.native_name or semantic_class.name
    )
    semantic_class.origin.native_scope = semantic_class.origin.native_scope or native_module_name
    semantic_class.origin.source_kind = semantic_class.origin.source_kind or "derived_type"
    semantic_class.native_name = semantic_class.native_name or semantic_class.name
    for field in semantic_class.fields:
        _normalize_variable_origin(field, native_module_name, source_kind="field")
    for method in semantic_class.methods:
        _normalize_function_origin(method, native_module_name, source_kind="method")
    for overload_set in semantic_class.overload_sets:
        for procedure in overload_set.procedures:
            _normalize_function_origin(procedure, native_module_name, source_kind="method")
    for nested in semantic_class.classes:
        _normalize_class_origin(nested, native_module_name)


def _source_object_stems(source_paths: tuple[Path, ...]) -> tuple[str, ...]:
    totals: dict[str, int] = {}
    for source_path in source_paths:
        totals[source_path.stem] = totals.get(source_path.stem, 0) + 1

    seen: dict[str, int] = {}
    stems = []
    for source_path in source_paths:
        stem = source_path.stem
        seen[stem] = seen.get(stem, 0) + 1
        stems.append(stem if totals[stem] == 1 else f"{stem}_{seen[stem]}")
    return tuple(stems)


def _merge_wrapper_modules(modules: list[SemanticModule]) -> SemanticModule:
    if not modules:
        raise ValueError("wrapper build found no Fortran modules or standalone procedures")

    native_modules = list(
        dict.fromkeys(
            str(module.origin.native_name or module.name) for module in modules if module.origin.source_kind == "module"
        )
    )
    readiness_blockers = [blocker for module in modules for blocker in module.metadata.get("readiness_blockers", ())]
    metadata: dict[str, object] = {"wrapper_native_modules": native_modules}
    if readiness_blockers:
        metadata["readiness_blockers"] = readiness_blockers
    return SemanticModule(
        name=modules[0].name,
        functions=[function for module in modules for function in module.functions],
        overload_sets=[overload for module in modules for overload in module.overload_sets],
        classes=[semantic_class for module in modules for semantic_class in module.classes],
        variables=[variable for module in modules for variable in module.variables],
        metadata=metadata,
        origin=modules[0].origin,
    )


def _command_output(command: tuple[str, ...]) -> str | None:
    try:
        return command[command.index("-o") + 1]
    except (ValueError, IndexError):
        return None


def _command_source(command: tuple[str, ...]) -> str | None:
    for part in command:
        if Path(part).suffix.lower() in _FORTRAN_SOURCE_SUFFIXES | _C_SOURCE_SUFFIXES:
            return part
    return None


def _command_language(command: tuple[str, ...]) -> str | None:
    source = _command_source(command)
    if source is None:
        return None
    return "fortran" if Path(source).suffix.lower() in _FORTRAN_SOURCE_SUFFIXES else "c"


def _absolute_command_path(path: str | Path, working_directory: Path) -> Path:
    result = Path(path)
    return result if result.is_absolute() else working_directory / result


def _make_target(path: Path) -> str:
    return str(path).replace("$", "$$").replace("#", r"\#").replace(" ", r"\ ")


def _make_shell_literal(text: str) -> str:
    return text.replace("$", "$$")


def _make_recipe(command: tuple[str, ...], working_directory: Path) -> str:
    language = _command_language(command)
    if "-shared" in command:
        compiler_var, flags_var = "X2PY_LD", "X2PY_LDFLAGS"
    elif language == "fortran":
        compiler_var, flags_var = "FC", "X2PY_FFLAGS"
    else:
        compiler_var, flags_var = "CC", "X2PY_CFLAGS"

    output_index = command.index("-o")
    before_output = _make_shell_literal(shlex.join(command[1:output_index]))
    output_and_after = _make_shell_literal(shlex.join(command[output_index:]))
    directory = _make_shell_literal(shlex.quote(str(working_directory)))
    return f"\tcd {directory} && $({compiler_var}) {before_output} $({flags_var}) {output_and_after}".rstrip()


def _compiler_executable(commands: tuple[tuple[str, ...], ...], *, language: str | None, shared: bool) -> str:
    for command in commands:
        if ("-shared" in command) == shared and (shared or _command_language(command) == language):
            return command[0]
    return "gfortran" if language == "fortran" or shared else "gcc"


def _write_build_makefile(
    *,
    path: Path,
    commands: tuple[tuple[str, ...], ...],
    source_objects: tuple[CompileObj, ...],
    working_directory: Path,
) -> Path:
    """Write a GNU Make build from recorded compiler commands."""
    compile_commands = tuple(command for command in commands if "-c" in command and _command_output(command))
    link_command = next((command for command in reversed(commands) if "-shared" in command), None)
    if link_command is None:
        raise RuntimeError("cannot generate Makefile without a shared-library link command")

    user_outputs = tuple(
        _absolute_command_path(source_object.module_target, working_directory) for source_object in source_objects
    )
    compile_outputs = tuple(
        _absolute_command_path(_command_output(command), working_directory) for command in compile_commands
    )
    makefile_path = path.resolve()
    lines = [
        "# Generated by x2py. Edit variables or override them on the make command line.",
        "# User Fortran sources are conservatively chained in supplied order.",
        "# Independent generated C/runtime objects may be built in parallel with make -j.",
        f"FC := {_make_shell_literal(shlex.quote(_compiler_executable(commands, language='fortran', shared=False)))}",
        f"CC := {_make_shell_literal(shlex.quote(_compiler_executable(commands, language='c', shared=False)))}",
        f"X2PY_LD := {_make_shell_literal(shlex.quote(_compiler_executable(commands, language=None, shared=True)))}",
        "X2PY_FFLAGS ?=",
        "X2PY_CFLAGS ?=",
        "X2PY_LDFLAGS ?=",
        "",
    ]

    link_output = _absolute_command_path(_command_output(link_command), working_directory)
    lines.extend([".PHONY: all rebuild clean", f"all: {_make_target(link_output)}", ""])

    previous_user_output = None
    for command, output in zip(compile_commands, compile_outputs, strict=True):
        source = _absolute_command_path(_command_source(command), working_directory)
        dependencies = [source]
        if output in user_outputs:
            if previous_user_output is not None:
                dependencies.append(previous_user_output)
            previous_user_output = output
        elif _command_language(command) == "fortran":
            dependencies.extend(user_outputs)
        dependency_text = " ".join(_make_target(dependency) for dependency in dict.fromkeys(dependencies))
        lines.extend(
            [
                f"{_make_target(output)}: {dependency_text}",
                _make_recipe(command, working_directory),
                "",
            ]
        )

    object_dependencies = " ".join(_make_target(output) for output in compile_outputs)
    lines.extend(
        [
            f"{_make_target(link_output)}: {object_dependencies}",
            _make_recipe(link_command, working_directory),
            "",
            "rebuild:",
            f"\t$(MAKE) -f {_make_target(makefile_path)} clean",
            f"\t$(MAKE) -f {_make_target(makefile_path)} all",
            "",
            "clean:",
            "\trm -f " + " ".join(shlex.quote(str(output)) for output in (*compile_outputs, link_output)),
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _can_probe_fortran_types(preprocessing: PreprocessingConfig) -> bool:
    return preprocessing.uses_compiler and bool(preprocessing.compiler)


def _wrap_compile_time_values(
    parsed,
    preprocessing: PreprocessingConfig,
    *,
    report=None,
    runner: list[str] | None = None,
    cache_dir: str | Path | None = None,
    refresh: bool = False,
) -> dict[str, int] | None:
    if report is None and not _can_probe_fortran_types(preprocessing):
        return None
    requirements = collect_semantic_compile_time_requirements(parsed)
    if not requirements:
        return None
    return evaluate_fortran_type_requirements(
        preprocessing,
        requirements,
        report=report,
        runner=runner,
        cache_dir=cache_dir,
        refresh=refresh,
    )


def _wrap_type_facts(
    parsed,
    preprocessing: PreprocessingConfig,
    *,
    compile_time_values: dict[str, int] | None,
    report=None,
    runner: list[str] | None = None,
    cache_dir: str | Path | None = None,
    refresh: bool = False,
) -> dict[tuple[str, str | None], dict[str, object]] | None:
    if report is None and not _can_probe_fortran_types(preprocessing):
        return None
    requirements = collect_fortran_type_storage_requirements(parsed, compile_time_values=compile_time_values)
    if not requirements:
        return None
    return evaluate_fortran_type_facts(
        preprocessing,
        requirements,
        report=report,
        runner=runner,
        cache_dir=cache_dir,
        refresh=refresh,
    )


def build_fortran_extension(
    sources: str | Path | Iterable[str | Path],
    *,
    output_dir: str | Path | None = None,
    preprocessing: PreprocessingConfig | None = None,
    strict_wrapper_names: bool = False,
    fortran_type_report=None,
    fortran_type_probe_runner: list[str] | None = None,
    fortran_type_probe_cache_dir: str | Path | None = None,
    refresh_fortran_type_probe: bool = False,
    makefile: bool = False,
    verbose: bool | int = False,
) -> WrapperBuildResult:
    """Build one extension, or generate its Makefile, from ordered sources."""

    if makefile and verbose:
        raise ValueError("makefile generation and verbose direct compilation are separate modes")

    source_paths = _source_paths(sources)
    primary_source = source_paths[0]

    output_path = Path(output_dir) if output_dir is not None else primary_source.parent / _DEFAULT_BUILD_DIR_NAME
    shared_library_output_path = Path(output_dir) if output_dir is not None else primary_source.parent
    output_path.mkdir(parents=True, exist_ok=True)
    preprocessing = preprocessing or _default_preprocessing_config()

    preprocessed_sources = {
        str(source_path): _fortran_source_for_pipeline(source_path, preprocessing) for source_path in source_paths
    }
    parsed = parse_fortran_project(preprocessed_sources)
    compile_time_values = _wrap_compile_time_values(
        parsed,
        preprocessing,
        report=fortran_type_report,
        runner=fortran_type_probe_runner,
        cache_dir=fortran_type_probe_cache_dir,
        refresh=refresh_fortran_type_probe,
    )
    type_facts = _wrap_type_facts(
        parsed,
        preprocessing,
        compile_time_values=compile_time_values,
        report=fortran_type_report,
        runner=fortran_type_probe_runner,
        cache_dir=fortran_type_probe_cache_dir,
        refresh=refresh_fortran_type_probe,
    )
    modules = fortran_project_to_semantic_modules(
        parsed,
        compile_time_values=compile_time_values,
        type_facts=type_facts,
    )
    module = _merge_wrapper_modules(modules)
    scope = Scope(
        name=module.name,
        scope_type="module",
        public_name_policy=PublicNamePolicy(strict=strict_wrapper_names),
        public_namespace=(module.name.casefold(),),
    )
    codegen_ast = semantic_ir_to_codegen_ast(module, scope)
    module_name = str(codegen_ast.scope.get_python_name(codegen_ast.name))

    compiler = _new_gnu_compiler(execute_commands=not makefile)
    source_objects = tuple(
        _source_compile_object(source_path, output_path, object_stem=object_stem)
        for source_path, object_stem in zip(source_paths, _source_object_stems(source_paths), strict=True)
    )
    for source_obj in source_objects:
        compiler.compile_module(
            source_obj,
            output_folder=str(output_path),
            language="fortran",
            verbose=verbose,
        )

    codegen = Codegen(module_name, codegen_ast, codegen_ast.scope)
    module_obj = CompileObj(
        file_name=module_name,
        folder=str(output_path),
        has_target_file=False,
    )
    shared_library, _timings = create_shared_library(
        codegen,
        module_obj,
        language="fortran",
        wrapper_flags="",
        x2py_dirpath=str(output_path),
        output_dirpath=str(shared_library_output_path),
        compiler=compiler,
        sharedlib_modname=module_name,
        dependencies=source_objects,
        verbose=verbose,
    )

    shared_library_path = Path(shared_library)
    build_makefile = (
        _write_build_makefile(
            path=output_path / "Makefile.x2py",
            commands=compiler.command_log,
            source_objects=source_objects,
            working_directory=Path.cwd(),
        )
        if makefile
        else None
    )
    generated_sources = tuple(
        path
        for path in (
            output_path / f"bind_c_{module_name}_wrapper.f90",
            output_path / f"{module_name}_wrapper.c",
            output_path / f"{module_name}_wrapper.h",
        )
        if path.exists()
    )
    generated_files = _expected_generated_files(
        source_objects=source_objects,
        output_dir=output_path,
        module_name=module_name,
        shared_library=shared_library_path,
    )
    if build_makefile is not None:
        generated_files = (*generated_files, build_makefile)
    return WrapperBuildResult(
        sources=source_paths,
        module_name=module_name,
        output_dir=output_path,
        shared_library=shared_library_path,
        build_makefile=build_makefile,
        compiled=not makefile,
        generated_sources=generated_sources,
        generated_files=generated_files,
    )


def build_pyi_extension(
    contracts: str | Path | Iterable[str | Path],
    *,
    native_objects: Iterable[str | Path] | None = None,
    native_libraries: Iterable[str] | None = None,
    native_library_dirs: Iterable[str | Path] | None = None,
    native_include_dirs: Iterable[str | Path] | None = None,
    output_dir: str | Path | None = None,
    strict_wrapper_names: bool = False,
    makefile: bool = False,
    verbose: bool | int = False,
) -> WrapperBuildResult:
    """Build one extension from semantic `.pyi` contracts and native link inputs."""

    if makefile:
        raise ValueError("makefile generation is not yet supported for .pyi wrapper builds")

    contract_paths = _pyi_contract_paths(contracts)
    artifact_paths = _existing_paths(native_objects, kind="Native artifact")
    libraries = tuple(native_libraries or ())
    library_dirs = _existing_paths(native_library_dirs, kind="Native library", require_directory=True)
    explicit_include_dirs = _existing_paths(native_include_dirs, kind="Native include", require_directory=True)
    if not artifact_paths and not libraries:
        raise ValueError(".pyi wrapper build requires at least one native object, archive, shared library, or -l name")

    primary_contract = contract_paths[0]
    output_path = Path(output_dir) if output_dir is not None else primary_contract.parent / _DEFAULT_BUILD_DIR_NAME
    shared_library_output_path = Path(output_dir) if output_dir is not None else primary_contract.parent
    output_path.mkdir(parents=True, exist_ok=True)

    modules = load_pyi_modules(contract_paths)
    _normalize_pyi_modules_for_fortran_wrapping(modules)
    module = _merge_wrapper_modules(modules)
    scope = Scope(
        name=module.name,
        scope_type="module",
        public_name_policy=PublicNamePolicy(strict=strict_wrapper_names),
        public_namespace=(module.name.casefold(),),
    )
    codegen_ast = semantic_ir_to_codegen_ast(module, scope)
    module_name = str(codegen_ast.scope.get_python_name(codegen_ast.name))

    artifact_dependencies = tuple(_native_artifact_compile_object(path) for path in artifact_paths)
    inferred_include_dirs = tuple(dict.fromkeys(path.parent for path in artifact_paths))
    include_dirs = (*explicit_include_dirs, *inferred_include_dirs)
    compiler = _new_gnu_compiler()
    codegen = Codegen(module_name, codegen_ast, codegen_ast.scope)
    module_obj = CompileObj(
        file_name=module_name,
        folder=str(output_path),
        has_target_file=False,
        include=include_dirs,
        libs=libraries,
        libdir=library_dirs,
    )
    shared_library, _timings = create_shared_library(
        codegen,
        module_obj,
        language="fortran",
        wrapper_flags="",
        x2py_dirpath=str(output_path),
        output_dirpath=str(shared_library_output_path),
        compiler=compiler,
        sharedlib_modname=module_name,
        dependencies=artifact_dependencies,
        verbose=verbose,
    )

    shared_library_path = Path(shared_library)
    generated_sources = tuple(
        path
        for path in (
            output_path / f"bind_c_{module_name}_wrapper.f90",
            output_path / f"{module_name}_wrapper.c",
            output_path / f"{module_name}_wrapper.h",
        )
        if path.exists()
    )
    generated_files = _expected_generated_files(
        source_objects=(),
        output_dir=output_path,
        module_name=module_name,
        shared_library=shared_library_path,
    )
    native_inputs = (
        *(str(path) for path in artifact_paths),
        *(f"-l{library}" if not str(library).startswith("-l") else str(library) for library in libraries),
        *(f"-L{path}" for path in library_dirs),
        *(f"-I{path}" for path in include_dirs),
    )
    return WrapperBuildResult(
        sources=contract_paths,
        module_name=module_name,
        output_dir=output_path,
        shared_library=shared_library_path,
        build_makefile=None,
        compiled=True,
        generated_sources=generated_sources,
        generated_files=generated_files,
        native_inputs=native_inputs,
    )
