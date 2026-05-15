import json
from dataclasses import asdict
from pathlib import Path

from fortran_parser import parse_fortran_file
from semantics.fortran2ir import fortran_module_to_semantic_module
from semantics.pyi_printer import emit_module


TESTS_DIR = Path(__file__).resolve().parents[1]
FORTRAN_DATA_DIR = TESTS_DIR / "data" / "fortran"
GENERAL_FORTRAN_DIR = FORTRAN_DATA_DIR / "general"
SEMANTICS_FIXTURE_DIR = TESTS_DIR / "semantics" / "fixtures" / "general"
PYI_FIXTURE_DIR = TESTS_DIR / "pyi" / "fixtures" / "general"
FORTRAN_SUFFIXES = {".f", ".f90", ".f95", ".f03", ".f08", ".for", ".f77", ".ftn"}


def iter_general_fortran_fixtures():
    return sorted(
        path
        for path in GENERAL_FORTRAN_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in FORTRAN_SUFFIXES
    )


def parse_fixture(path: Path):
    source = path.read_text(encoding="utf-8")
    return parse_fortran_file(source, filename=path.name)


def semantic_modules_for_fixture(path: Path):
    parsed = parse_fixture(path)
    return [fortran_module_to_semantic_module(module) for module in parsed.modules]


def semantic_payload_for_fixture(path: Path) -> dict:
    return {
        "semantic_modules": [
            asdict(module)
            for module in semantic_modules_for_fixture(path)
        ]
    }


def pyi_text_for_fixture(path: Path) -> str:
    return "\n\n".join(
        emit_module(module)
        for module in semantic_modules_for_fixture(path)
    ).strip()


def semantics_fixture_path(path: Path) -> Path:
    return (SEMANTICS_FIXTURE_DIR / path.name).with_suffix(".json")


def pyi_fixture_path(path: Path) -> Path:
    return (PYI_FIXTURE_DIR / path.name).with_suffix(".pyi")


def write_semantics_fixture(path: Path) -> Path:
    out = semantics_fixture_path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(semantic_payload_for_fixture(path), indent=2) + "\n", encoding="utf-8")
    return out


def write_pyi_fixture(path: Path) -> Path:
    out = pyi_fixture_path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(pyi_text_for_fixture(path) + "\n", encoding="utf-8")
    return out
