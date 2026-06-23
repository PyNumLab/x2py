"""End-to-end Fortran-to-Python extension build pipeline."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
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
from x2py.semantics.models import (
    PYTHON_EXPORTS_METADATA,
    PYTHON_EXPORTS_PREPARED_METADATA,
    PYI_LOADED_METADATA,
    PYI_NATIVE_CONTRACT_PREPARED_METADATA,
    ProcedureOverloadSet,
    SemanticClass,
    SemanticFunction,
    SemanticImport,
    SemanticModule,
    SemanticVariable,
)
from x2py.semantics.pyi_parser import load_pyi_file, load_pyi_modules
from x2py.semantics.native_contract import validate_pyi_native_contract


_DEFAULT_BUILD_DIR_NAME = "__x2py__"
_FORTRAN_SOURCE_SUFFIXES = {".f", ".f03", ".f08", ".f77", ".f90", ".f95", ".for", ".ftn"}
_C_SOURCE_SUFFIXES = {".c"}
_NATIVE_PATH_LINK_KINDS = frozenset({"object", "archive", "shared_library"})
_NATIVE_LINK_KINDS = frozenset({*_NATIVE_PATH_LINK_KINDS, "named_library", "linker_argument"})


@dataclass(frozen=True)
class NativeCompilationUnit:
    """One caller-supplied native source and the object it produces."""

    source: Path
    object_path: Path
    language: str
    module_dir: Path | None = None
    include_dirs: tuple[Path, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "source", Path(self.source))
        object.__setattr__(self, "object_path", Path(self.object_path))
        if self.module_dir is not None:
            object.__setattr__(self, "module_dir", Path(self.module_dir))
        object.__setattr__(self, "include_dirs", tuple(Path(path) for path in self.include_dirs))

    def to_dict(self) -> dict[str, object]:
        return {
            "source": str(self.source),
            "object": str(self.object_path),
            "language": self.language,
            "module_dir": str(self.module_dir) if self.module_dir is not None else None,
            "include_dirs": [str(path) for path in self.include_dirs],
        }


@dataclass(frozen=True)
class NativePrebuiltArtifact:
    """One caller-supplied native artifact used by the extension link."""

    path: Path
    kind: str

    def __post_init__(self) -> None:
        if self.kind not in _NATIVE_PATH_LINK_KINDS:
            raise ValueError(f"Unsupported native artifact kind: {self.kind!r}")
        object.__setattr__(self, "path", Path(self.path))

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "path": str(self.path),
        }


@dataclass(frozen=True)
class NativeLinkItem:
    """One ordered item in the native implementation link plan."""

    kind: str
    value: Path | str

    def __post_init__(self) -> None:
        if self.kind not in _NATIVE_LINK_KINDS:
            raise ValueError(f"Unsupported native link item kind: {self.kind!r}")
        if self.kind in _NATIVE_PATH_LINK_KINDS:
            object.__setattr__(self, "value", Path(self.value))
        else:
            object.__setattr__(self, "value", str(self.value))

    def to_dict(self) -> dict[str, object]:
        if self.kind in _NATIVE_PATH_LINK_KINDS:
            return {
                "kind": self.kind,
                "path": str(self.value),
            }
        if self.kind == "named_library":
            return {
                "kind": self.kind,
                "name": str(self.value),
            }
        return {
            "kind": self.kind,
            "argument": str(self.value),
        }


@dataclass(frozen=True)
class NativeBuildPlan:
    """Extension-level native implementation build and link plan."""

    compilation_units: tuple[NativeCompilationUnit, ...] = ()
    produced_objects: tuple[Path, ...] = ()
    prebuilt_artifacts: tuple[NativePrebuiltArtifact, ...] = ()
    module_dirs: tuple[Path, ...] = ()
    include_dirs: tuple[Path, ...] = ()
    library_dirs: tuple[Path, ...] = ()
    link_items: tuple[NativeLinkItem, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "compilation_units", tuple(self.compilation_units))
        object.__setattr__(self, "produced_objects", tuple(Path(path) for path in self.produced_objects))
        object.__setattr__(self, "prebuilt_artifacts", tuple(self.prebuilt_artifacts))
        object.__setattr__(self, "module_dirs", tuple(Path(path) for path in self.module_dirs))
        object.__setattr__(self, "include_dirs", tuple(Path(path) for path in self.include_dirs))
        object.__setattr__(self, "library_dirs", tuple(Path(path) for path in self.library_dirs))
        object.__setattr__(self, "link_items", tuple(self.link_items))

    def to_dict(self) -> dict[str, object]:
        return {
            "compilation_units": [unit.to_dict() for unit in self.compilation_units],
            "produced_objects": [str(path) for path in self.produced_objects],
            "prebuilt_artifacts": [artifact.to_dict() for artifact in self.prebuilt_artifacts],
            "module_dirs": [str(path) for path in self.module_dirs],
            "include_dirs": [str(path) for path in self.include_dirs],
            "library_dirs": [str(path) for path in self.library_dirs],
            "link_items": [item.to_dict() for item in self.link_items],
        }


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
    native_build_plan: NativeBuildPlan = field(default_factory=NativeBuildPlan)

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
            "native_build_plan": self.native_build_plan.to_dict(),
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


def _pyi_entry_path(contract: str | Path) -> Path:
    if not isinstance(contract, str | Path):
        raise TypeError(".pyi wrapper build accepts exactly one entry contract path")
    path = Path(contract)
    if path.suffix.lower() != ".pyi":
        raise ValueError(f".pyi wrapper build expects one semantic contract file, not {path}")
    if not path.is_file():
        raise FileNotFoundError(f"Semantic .pyi contract not found: {path}")
    return path


@dataclass(frozen=True)
class _PyiContractBundle:
    entry: Path
    leaves: tuple[Path, ...]
    paths: tuple[Path, ...]
    modules: tuple[SemanticModule, ...]


def _pyi_contract_bundle(
    entry: Path,
) -> _PyiContractBundle:
    discovered = {entry, *_discover_pyi_imports(entry)}
    sorted_paths = tuple(sorted(discovered))
    loaded_modules = load_pyi_modules(sorted_paths)
    modules_by_path = dict(zip(sorted_paths, loaded_modules, strict=True))
    _apply_pyi_python_exports(entry, modules_by_path)
    leaves = [path for path in sorted_paths if _module_has_native_declarations(modules_by_path[path])]
    if not leaves:
        raise ValueError("Entry contract does not resolve any native declarations")
    return _PyiContractBundle(
        entry=entry,
        leaves=tuple(leaves),
        paths=(entry, *sorted(discovered - {entry})),
        modules=tuple(modules_by_path[path] for path in leaves),
    )


def _discover_pyi_imports(root: Path) -> tuple[Path, ...]:
    discovered: set[Path] = set()
    pending = [root]
    while pending:
        path = pending.pop()
        module = load_pyi_file(path)
        for dependency in _relative_pyi_dependencies(path, module):
            if dependency in discovered or dependency == root:
                continue
            if not dependency.is_file():
                raise FileNotFoundError(f"Imported semantic .pyi contract not found: {dependency}")
            discovered.add(dependency)
            pending.append(dependency)
    return tuple(sorted(discovered))


def _relative_pyi_dependencies(path: Path, module: SemanticModule) -> tuple[Path, ...]:
    dependencies: list[Path] = []
    for semantic_import in module.imports:
        if not isinstance(semantic_import, SemanticImport) or not semantic_import.module.startswith("."):
            continue
        level = len(semantic_import.module) - len(semantic_import.module.lstrip("."))
        parent = path.parent
        for _ in range(level - 1):
            parent = parent.parent
        imported_module = semantic_import.module[level:]
        if imported_module:
            dependencies.append(_pyi_dependency_path(parent, imported_module))
        else:
            dependencies.extend(_pyi_dependency_path(parent, item.source) for item in semantic_import.items)
    return tuple(dependencies)


def _pyi_dependency_path(parent: Path, dotted_name: str) -> Path:
    target = parent.joinpath(*dotted_name.split("."))
    module_file = target.with_suffix(".pyi")
    if module_file.is_file() or not target.is_dir():
        return module_file
    return target / "__init__.pyi"


def _module_has_native_declarations(module: SemanticModule) -> bool:
    return bool(module.variables or module.functions or module.classes or module.overload_sets)


@dataclass
class _PyiExportNode:
    declarations: list[object] = field(default_factory=list)
    children: dict[str, _PyiExportNode] = field(default_factory=dict)
    origins: set[Path] = field(default_factory=set)


def _apply_pyi_python_exports(entry: Path, modules_by_path: dict[Path, SemanticModule]) -> None:
    for module in modules_by_path.values():
        module.metadata[PYTHON_EXPORTS_PREPARED_METADATA] = True
        for declaration in _module_declarations(module):
            _set_declaration_exports(declaration, [])

    tree = _pyi_export_tree(entry, modules_by_path, cache={}, pending=set())
    _record_pyi_exports(tree)


def _pyi_export_tree(
    path: Path,
    modules_by_path: dict[Path, SemanticModule],
    *,
    cache: dict[Path, _PyiExportNode],
    pending: set[Path],
) -> _PyiExportNode:
    if path in cache:
        return cache[path]
    if path in pending:
        raise ValueError(f"Cyclic relative .pyi export imports include {path}")
    pending.add(path)
    module = modules_by_path[path]
    tree = _PyiExportNode(origins={path})
    for declaration in _module_declarations(module):
        if getattr(declaration, "visibility", "public") == "public":
            _merge_export_child(
                tree,
                declaration.name,
                _PyiExportNode(declarations=[declaration], origins={path}),
                origin=path,
            )

    for semantic_import in module.imports:
        if not isinstance(semantic_import, SemanticImport) or not semantic_import.module.startswith("."):
            continue
        _merge_relative_import(tree, path, semantic_import, modules_by_path, cache, pending)
    pending.remove(path)
    cache[path] = tree
    return tree


def _merge_relative_import(
    tree: _PyiExportNode,
    path: Path,
    semantic_import: SemanticImport,
    modules_by_path: dict[Path, SemanticModule],
    cache: dict[Path, _PyiExportNode],
    pending: set[Path],
) -> None:
    imported_module = semantic_import.module.lstrip(".")
    if imported_module:
        dependency = _relative_import_path(path, semantic_import.module, imported_module)
        dependency_tree = _required_export_tree(dependency, modules_by_path, cache, pending)
        for item in semantic_import.items:
            if item.source == "*":
                for name, child in dependency_tree.children.items():
                    _merge_export_child(tree, name, child, origin=path)
                continue
            if item.source not in dependency_tree.children:
                raise ValueError(f"Imported semantic name {item.source!r} not found in {dependency}")
            _merge_export_child(tree, item.target or item.source, dependency_tree.children[item.source], origin=path)
        return

    for item in semantic_import.items:
        dependency = _relative_import_path(path, semantic_import.module, item.source)
        dependency_tree = _required_export_tree(dependency, modules_by_path, cache, pending)
        _merge_export_child(tree, item.target or item.source, dependency_tree, origin=path)


def _relative_import_path(path: Path, module: str, imported_module: str) -> Path:
    level = len(module) - len(module.lstrip("."))
    parent = path.parent
    for _ in range(level - 1):
        parent = parent.parent
    return _pyi_dependency_path(parent, imported_module)


def _required_export_tree(
    path: Path,
    modules_by_path: dict[Path, SemanticModule],
    cache: dict[Path, _PyiExportNode],
    pending: set[Path],
) -> _PyiExportNode:
    if path not in modules_by_path:
        raise FileNotFoundError(f"Imported semantic .pyi contract not found: {path}")
    return _pyi_export_tree(path, modules_by_path, cache=cache, pending=pending)


def _merge_export_child(tree: _PyiExportNode, name: str, child: _PyiExportNode, *, origin: Path) -> None:
    existing = tree.children.get(name)
    if existing is None or existing is child:
        tree.children[name] = child
        return
    existing_origins = ", ".join(str(path) for path in sorted(existing.origins))
    new_origins = ", ".join(str(path) for path in sorted(child.origins))
    raise ValueError(
        f"Conflicting .pyi exports for {name!r} while resolving {origin}: "
        f"existing from {existing_origins}; new from {new_origins}"
    )


def _record_pyi_exports(tree: _PyiExportNode, namespace: tuple[str, ...] = ()) -> None:
    for name, child in tree.children.items():
        for declaration in child.declarations:
            exports = _declaration_exports(declaration)
            export = {"namespace": namespace, "name": name}
            if export not in exports:
                exports.append(export)
        _record_pyi_exports(child, (*namespace, name))


def _module_declarations(module: SemanticModule) -> tuple[object, ...]:
    return (*module.variables, *module.functions, *module.overload_sets, *module.classes)


def _declaration_metadata(declaration: object) -> dict[str, object]:
    if isinstance(declaration, ProcedureOverloadSet):
        if not declaration.procedures:
            return {}
        return declaration.procedures[0].metadata
    if isinstance(declaration, SemanticVariable | SemanticFunction | SemanticClass):
        return declaration.metadata
    raise TypeError(f"Unsupported semantic declaration: {type(declaration).__name__}")


def _declaration_exports(declaration: object) -> list[dict[str, object]]:
    metadata = _declaration_metadata(declaration)
    return metadata.setdefault(PYTHON_EXPORTS_METADATA, [])


def _set_declaration_exports(declaration: object, exports: list[dict[str, object]]) -> None:
    metadata = _declaration_metadata(declaration)
    metadata[PYTHON_EXPORTS_METADATA] = exports


def _apply_source_python_exports(modules: list[SemanticModule]) -> None:
    for module in modules:
        module.metadata[PYTHON_EXPORTS_PREPARED_METADATA] = True
        namespace = (module.name.casefold(),) if module.origin.source_kind == "module" else ()
        for declaration in _module_declarations(module):
            _set_declaration_exports(
                declaration,
                [{"namespace": namespace, "name": None}],
            )


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


def _native_artifact_kind(path: Path) -> str:
    name = path.name.lower()
    suffix = path.suffix.lower()
    if suffix in {".a", ".lib"}:
        return "archive"
    if suffix in {".so", ".dylib", ".dll"} or ".so." in name:
        return "shared_library"
    return "object"


def _unique_paths(paths: Iterable[Path]) -> tuple[Path, ...]:
    return tuple(dict.fromkeys(Path(path) for path in paths))


def _source_native_build_plan(
    source_paths: tuple[Path, ...],
    source_objects: tuple[CompileObj, ...],
    *,
    module_dir: Path,
) -> NativeBuildPlan:
    produced_objects = tuple(Path(source_object.module_target) for source_object in source_objects)
    return NativeBuildPlan(
        compilation_units=tuple(
            NativeCompilationUnit(
                source=source_path,
                object_path=source_object.module_target,
                language="fortran",
                module_dir=module_dir,
                include_dirs=(module_dir,),
            )
            for source_path, source_object in zip(source_paths, source_objects, strict=True)
        ),
        produced_objects=produced_objects,
        module_dirs=(module_dir,),
        include_dirs=(module_dir,),
        link_items=tuple(NativeLinkItem("object", object_path) for object_path in produced_objects),
    )


def _pyi_native_build_plan(
    *,
    artifact_paths: tuple[Path, ...],
    libraries: tuple[str, ...],
    library_dirs: tuple[Path, ...],
    explicit_include_dirs: tuple[Path, ...],
    include_dirs: tuple[Path, ...],
) -> NativeBuildPlan:
    prebuilt_artifacts = tuple(
        NativePrebuiltArtifact(path=path, kind=_native_artifact_kind(path)) for path in artifact_paths
    )
    artifact_link_items = tuple(NativeLinkItem(artifact.kind, artifact.path) for artifact in prebuilt_artifacts)
    library_link_items = tuple(NativeLinkItem("named_library", library) for library in libraries)
    return NativeBuildPlan(
        prebuilt_artifacts=prebuilt_artifacts,
        module_dirs=explicit_include_dirs,
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        link_items=(*artifact_link_items, *library_link_items),
    )


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


def _merge_wrapper_modules(modules: list[SemanticModule], *, name: str | None = None) -> SemanticModule:
    if not modules:
        raise ValueError("wrapper build found no Fortran modules or standalone procedures")

    return SemanticModule(
        name=name or modules[0].name,
        functions=[function for module in modules for function in module.functions],
        overload_sets=[overload for module in modules for overload in module.overload_sets],
        classes=[semantic_class for module in modules for semantic_class in module.classes],
        variables=[variable for module in modules for variable in module.variables],
        metadata=_wrapper_module_metadata(modules),
        origin=modules[0].origin,
    )


def _wrapper_module_metadata(modules: list[SemanticModule]) -> dict[str, object]:
    metadata: dict[str, object] = {"wrapper_native_modules": _wrapper_native_modules(modules)}
    if any(module.metadata.get(PYTHON_EXPORTS_PREPARED_METADATA) for module in modules):
        metadata[PYTHON_EXPORTS_PREPARED_METADATA] = True
    if any(module.metadata.get(PYI_LOADED_METADATA) for module in modules):
        metadata[PYI_LOADED_METADATA] = True
        metadata[PYI_NATIVE_CONTRACT_PREPARED_METADATA] = True
    readiness_blockers = [blocker for module in modules for blocker in module.metadata.get("readiness_blockers", ())]
    if readiness_blockers:
        metadata["readiness_blockers"] = readiness_blockers
    return metadata


def _wrapper_native_modules(modules: list[SemanticModule]) -> list[str]:
    return list(
        dict.fromkeys(
            str(module.origin.native_name or module.name)
            for module in modules
            if module.origin.source_kind == "module" and _module_requires_native_scope(module)
        )
    )


def _module_requires_native_scope(module: SemanticModule) -> bool:
    if module.variables or module.classes:
        return True
    functions = [*module.functions, *(procedure for item in module.overload_sets for procedure in item.procedures)]
    return any(function.origin.native_scope is not None for function in functions)


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
    _apply_source_python_exports(modules)
    module = _merge_wrapper_modules(modules, name=primary_source.stem)
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
    native_build_plan = _source_native_build_plan(
        source_paths,
        source_objects,
        module_dir=output_path,
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
        native_build_plan=native_build_plan,
    )


def build_pyi_extension(
    contract: str | Path,
    *,
    native_objects: Iterable[str | Path] | None = None,
    native_libraries: Iterable[str] | None = None,
    native_library_dirs: Iterable[str | Path] | None = None,
    native_include_dirs: Iterable[str | Path] | None = None,
    extension_name: str | None = None,
    output_dir: str | Path | None = None,
    strict_wrapper_names: bool = False,
    makefile: bool = False,
    verbose: bool | int = False,
) -> WrapperBuildResult:
    """Build one extension from one entry `.pyi` and native link inputs."""

    if makefile:
        raise ValueError("makefile generation is not yet supported for .pyi wrapper builds")

    entry = _pyi_entry_path(contract)
    bundle = _pyi_contract_bundle(entry)
    artifact_paths = _existing_paths(native_objects, kind="Native artifact")
    libraries = tuple(native_libraries or ())
    library_dirs = _existing_paths(native_library_dirs, kind="Native library", require_directory=True)
    explicit_include_dirs = _existing_paths(native_include_dirs, kind="Native include", require_directory=True)
    if not artifact_paths and not libraries:
        raise ValueError(".pyi wrapper build requires at least one native object, archive, shared library, or -l name")

    primary_contract = bundle.entry
    output_path = Path(output_dir) if output_dir is not None else primary_contract.parent / _DEFAULT_BUILD_DIR_NAME
    shared_library_output_path = Path(output_dir) if output_dir is not None else primary_contract.parent
    output_path.mkdir(parents=True, exist_ok=True)

    modules = list(bundle.modules)
    validate_pyi_native_contract(modules)
    requested_name = extension_name or _bundle_extension_name(bundle)
    if not requested_name.isidentifier():
        raise ValueError(f"Extension name must be a valid Python identifier: {requested_name!r}")
    module = _merge_wrapper_modules(modules, name=requested_name)
    scope = Scope(
        name=module.name,
        scope_type="module",
        public_name_policy=PublicNamePolicy(strict=strict_wrapper_names),
        public_namespace=(module.name.casefold(),),
    )
    codegen_ast = semantic_ir_to_codegen_ast(module, scope)
    module_name = str(codegen_ast.scope.get_python_name(codegen_ast.name))

    artifact_dependencies = tuple(_native_artifact_compile_object(path) for path in artifact_paths)
    inferred_include_dirs = _unique_paths(path.parent for path in artifact_paths)
    include_dirs = _unique_paths((*explicit_include_dirs, *inferred_include_dirs))
    native_build_plan = _pyi_native_build_plan(
        artifact_paths=artifact_paths,
        libraries=libraries,
        library_dirs=library_dirs,
        explicit_include_dirs=explicit_include_dirs,
        include_dirs=include_dirs,
    )
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
    return WrapperBuildResult(
        sources=bundle.paths,
        module_name=module_name,
        output_dir=output_path,
        shared_library=shared_library_path,
        build_makefile=None,
        compiled=True,
        generated_sources=generated_sources,
        generated_files=generated_files,
        native_build_plan=native_build_plan,
    )


def _bundle_extension_name(bundle: _PyiContractBundle) -> str:
    if bundle.entry.name == "__init__.pyi":
        return bundle.entry.resolve().parent.name
    return bundle.entry.stem
