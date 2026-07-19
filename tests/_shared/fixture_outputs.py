import json
import shutil
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path
from tempfile import TemporaryDirectory

from x2py.parsers.c import CParser
from x2py.parsers.c.cli import attach_preprocessing_recipe
from x2py import parse_fortran_file
from x2py.pipeline.preprocessing import PreprocessingConfig, preprocess_source
from x2py.semantics.c2ir import c_project_to_semantic_module
from x2py.semantics.fortran2ir import fortran_module_to_semantic_module
from x2py.wrapper_codegen.printers import emit_module
from x2py.cli import _fortran_contract_files, _semantic_report

TESTS_DIR = Path(__file__).resolve().parents[1]
FORTRAN_DATA_DIR = TESTS_DIR / "data" / "fortran"
GENERAL_FORTRAN_DIR = FORTRAN_DATA_DIR / "general"
C_DATA_DIR = TESTS_DIR / "data" / "c"
GENERAL_C_DIR = C_DATA_DIR / "general"
SEMANTICS_FIXTURE_DIR = TESTS_DIR / "semantics" / "fixtures" / "general"
PYI_FIXTURE_DIR = TESTS_DIR / "pyi" / "fixtures" / "general"
PYI_WRAPPER_CONTRACT_FIXTURE_DIR = TESTS_DIR / "pyi" / "fixtures" / "wrapper_contracts"
C_PYI_FIXTURE_DIR = TESTS_DIR / "pyi" / "fixtures" / "c" / "general"
FORTRAN_SUFFIXES = {".f", ".f90", ".f95", ".f03", ".f08", ".for", ".f77", ".ftn"}
C_SOURCE_SUFFIXES = {".c", ".h", ".i"}
C_SOURCE_ORDER = {".c": 0, ".h": 1, ".i": 2}


def iter_general_fortran_fixtures():
    return sorted(
        path for path in GENERAL_FORTRAN_DIR.iterdir() if path.is_file() and path.suffix.lower() in FORTRAN_SUFFIXES
    )


def fortran_fixture_requires_compiler_preprocessing(path: Path) -> bool:
    return any(line.lstrip().startswith("#") for line in path.read_text(encoding="utf-8").splitlines())


def _c_fixture_sort_key(path: Path) -> tuple[int, str]:
    return (C_SOURCE_ORDER.get(path.suffix.lower(), 99), path.as_posix())


def iter_general_c_fixture_projects() -> list[tuple[Path, list[Path]]]:
    grouped: dict[Path, list[Path]] = {}
    for path in sorted(GENERAL_C_DIR.iterdir(), key=_c_fixture_sort_key):
        if path.is_file() and path.suffix.lower() in C_SOURCE_SUFFIXES:
            grouped.setdefault(Path(path.stem), []).append(path)
    return [(project_key, sorted(paths, key=_c_fixture_sort_key)) for project_key, paths in sorted(grouped.items())]


def parse_fixture(path: Path):
    source = path.read_text(encoding="utf-8")
    return parse_fortran_file(source, filename=path.name)


def semantic_modules_for_fixture(path: Path):
    parsed = parse_fixture(path)
    return [fortran_module_to_semantic_module(module) for module in parsed.modules]


def _prune_empty_nested_class_lists(value):
    if isinstance(value, list):
        return [_prune_empty_nested_class_lists(item) for item in value]
    if not isinstance(value, dict):
        return value

    is_class_payload = {"fields", "methods", "base_classes"}.issubset(value)
    return {
        key: _prune_empty_nested_class_lists(item)
        for key, item in value.items()
        if not (is_class_payload and key == "classes" and item == [])
    }


def semantic_payload_for_fixture(path: Path) -> dict:
    return {
        "semantic_modules": [
            _prune_empty_nested_class_lists(asdict(module)) for module in semantic_modules_for_fixture(path)
        ]
    }


@lru_cache
def pyi_files_for_fixture(path: Path) -> dict[Path, str]:
    report = _semantic_report([str(path)])[str(path)]
    return _fortran_contract_files(path, report)


def parse_c_fixture_project(paths: list[Path]):
    compiler = shutil.which("cc")
    if compiler is None:
        raise RuntimeError("C fixture preprocessing requires cc")

    parser = CParser()
    parsed_files = {}
    root_paths = {str(path.resolve()) for path in paths}
    with TemporaryDirectory() as tmp_dir:
        system_include_dir = Path(tmp_dir)
        (system_include_dir / "stddef.h").write_text("", encoding="utf-8")
        (system_include_dir / "stdbool.h").write_text(
            "#define bool _Bool\n#define true 1\n#define false 0\n",
            encoding="utf-8",
        )
        (system_include_dir / "math.h").write_text("", encoding="utf-8")
        config = PreprocessingConfig(
            mode="compiler",
            compiler=compiler,
            include_dirs=sorted({str(path.parent) for path in paths}),
            compiler_args=["-dD", f"-isystem{system_include_dir}"],
        )
        for path in sorted(paths, key=_c_fixture_sort_key):
            preprocessed = preprocess_source(path, language="c", config=config)
            recipe = dict(preprocessed.recipe)
            recipe["macros"] = [item for item in recipe["macros"] if item.get("path") in root_paths]
            filename = path.relative_to(C_DATA_DIR).as_posix()
            parsed = parser.parse_file(
                preprocessed.source,
                filename=filename,
                preprocessing="compiler",
            )
            attach_preprocessing_recipe(parsed, recipe)
            parsed_files[filename] = parsed
    return parser._assemble_project(parsed_files)


def c_semantic_module_for_fixture_project(project_key: Path, paths: list[Path]):
    return c_project_to_semantic_module(
        parse_c_fixture_project(paths),
        name=project_key.as_posix().replace("/", "_"),
    )


def c_pyi_text_for_fixture_project(project_key: Path, paths: list[Path]) -> str:
    return emit_module(c_semantic_module_for_fixture_project(project_key, paths)).strip()


def semantics_fixture_path(path: Path) -> Path:
    return (SEMANTICS_FIXTURE_DIR / path.name).with_suffix(".json")


def c_pyi_fixture_path(project_key: Path) -> Path:
    return (C_PYI_FIXTURE_DIR / project_key).with_suffix(".pyi")


def write_semantics_fixture(path: Path) -> Path:
    out = semantics_fixture_path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(semantic_payload_for_fixture(path), indent=2) + "\n", encoding="utf-8")
    return out


def reset_fortran_pyi_fixtures() -> None:
    PYI_FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    for path in PYI_FIXTURE_DIR.iterdir():
        if path.is_dir():
            shutil.rmtree(path)
        elif path.suffix == ".pyi":
            path.unlink()


def write_pyi_fixture_package(path: Path) -> Path:
    package_dir = PYI_FIXTURE_DIR / path.stem
    for relative_path, text in pyi_files_for_fixture(path).items():
        target = PYI_FIXTURE_DIR / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text + "\n", encoding="utf-8")
    return package_dir


def write_c_pyi_fixture(project_key: Path, paths: list[Path]) -> Path:
    out = c_pyi_fixture_path(project_key)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(c_pyi_text_for_fixture_project(project_key, paths) + "\n", encoding="utf-8")
    return out
