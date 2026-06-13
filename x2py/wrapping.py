"""End-to-end Fortran-to-Python extension build pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from filelock import FileLock

from x2py.codegen.codegen import Codegen
from x2py.codegen.scope import Scope
from x2py.compiling.basic import CompileObj
from x2py.compiling.compilers import Compiler, get_condaless_search_path
from x2py.compiling.python_wrapper import create_shared_library
from x2py.fortran_parser.parser import parse_fortran_file
from x2py.preprocessing import PreprocessingConfig, preprocess_source
from x2py.semantics.fortran2ir import fortran_file_to_semantic_modules
from x2py.semantics.ir2ast import semantic_ir_to_codegen_ast


_FIXED_FORM_SUFFIXES = {".f", ".for", ".ftn", ".f77"}
_DEFAULT_BUILD_DIR_NAME = "__x2py__"


@dataclass(frozen=True)
class WrapperBuildResult:
    """Artifacts produced by one wrapper build."""

    source: Path
    module_name: str
    output_dir: Path
    shared_library: Path
    generated_sources: tuple[Path, ...]
    generated_files: tuple[Path, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "source": str(self.source),
            "module_name": self.module_name,
            "output_dir": str(self.output_dir),
            "shared_library": str(self.shared_library),
            "generated_sources": [str(path) for path in self.generated_sources],
            "generated_files": [str(path) for path in self.generated_files],
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


def _new_gnu_compiler() -> Compiler:
    Compiler.acceptable_bin_paths = get_condaless_search_path("verbose")
    return Compiler("GNU", debug=True)


def _is_fixed_form_legacy_source(path: Path) -> bool:
    return path.suffix.lower() in _FIXED_FORM_SUFFIXES


def _expected_generated_files(
    *,
    source: Path,
    output_dir: Path,
    module_name: str,
    shared_library: Path,
) -> tuple[Path, ...]:
    candidates = [
        output_dir / f"{source.stem}.o",
        output_dir / f"bind_c_{module_name}.mod",
        output_dir / f"bind_c_{module_name}_wrapper.f90",
        output_dir / f"bind_c_{module_name}_wrapper.o",
        output_dir / f"{module_name}_wrapper.c",
        output_dir / f"{module_name}_wrapper.h",
        output_dir / f"{module_name}_wrapper.o",
        shared_library,
    ]
    cwrapper_dir = output_dir / "cwrapper"
    if cwrapper_dir.is_dir():
        candidates.extend(sorted(path for path in cwrapper_dir.rglob("*") if path.is_file()))
    return tuple(path for path in candidates if path.exists())


def _source_compile_object(source_path: Path, output_dir: Path) -> CompileObj:
    compile_obj = CompileObj(
        file_name=source_path.name,
        folder=str(source_path.parent),
        has_target_file=True,
    )
    target = output_dir / f"{source_path.stem}.o"
    if target != compile_obj.module_target:
        compile_obj._module_target = target
        compile_obj._lock_target = FileLock(str(target.with_suffix(target.suffix + ".lock")))
        compile_obj._include.add(output_dir)
    return compile_obj


def build_fortran_extension(
    source: str | Path,
    *,
    output_dir: str | Path | None = None,
    preprocessing: PreprocessingConfig | None = None,
    verbose: bool | int = False,
) -> WrapperBuildResult:
    """Build a Python extension module from one Fortran source file."""

    source_path = Path(source)
    if not source_path.is_file():
        raise FileNotFoundError(f"Fortran source not found: {source_path}")

    output_path = Path(output_dir) if output_dir is not None else source_path.parent / _DEFAULT_BUILD_DIR_NAME
    shared_library_output_path = Path(output_dir) if output_dir is not None else source_path.parent
    output_path.mkdir(parents=True, exist_ok=True)
    preprocessing = preprocessing or _default_preprocessing_config()

    preprocessed_source = _fortran_source_for_pipeline(source_path, preprocessing)
    parsed = parse_fortran_file(preprocessed_source, filename=str(source_path))
    modules = fortran_file_to_semantic_modules(parsed)
    if len(modules) != 1:
        names = ", ".join(module.name for module in modules) or "<none>"
        raise ValueError(
            "wrapper build currently expects exactly one generated semantic module; "
            f"{source_path} produced {len(modules)} ({names})"
        )

    module = modules[0]
    module_name = module.name
    scope = Scope(name=module_name, scope_type="module")
    codegen_ast = semantic_ir_to_codegen_ast(module, scope, legacy=_is_fixed_form_legacy_source(source_path))

    compiler = _new_gnu_compiler()
    source_obj = _source_compile_object(source_path, output_path)
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
        dependencies=(source_obj,),
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
        source=source_path,
        output_dir=output_path,
        module_name=module_name,
        shared_library=shared_library_path,
    )
    return WrapperBuildResult(
        source=source_path,
        module_name=module_name,
        output_dir=output_path,
        shared_library=shared_library_path,
        generated_sources=generated_sources,
        generated_files=generated_files,
    )
