import json
from dataclasses import asdict
from pathlib import Path

from x2py import parse_fortran_file
from semantics.fortran2ir import fortran_file_to_semantic_modules, fortran_module_to_semantic_module
from semantics.pyi_printer import emit_module
from semantics.readiness import assess_semantic_wrap_readiness


TESTS_DIR = Path(__file__).resolve().parents[1]
FORTRAN_DATA_DIR = TESTS_DIR / "data" / "fortran"
GENERAL_FORTRAN_DIR = FORTRAN_DATA_DIR / "general"
SEMANTICS_FIXTURE_DIR = TESTS_DIR / "semantics" / "fixtures" / "general"
SEMANTIC_READINESS_FIXTURE_PATH = TESTS_DIR / "semantics" / "fixtures" / "wrap_readiness_messages.json"
PYI_FIXTURE_DIR = TESTS_DIR / "pyi" / "fixtures" / "general"
FORTRAN_SUFFIXES = {".f", ".f90", ".f95", ".f03", ".f08", ".for", ".f77", ".ftn"}
WRAP_READINESS_CORPUS_DIRS = ("general", "blas", "lapack", "scifortran")


def iter_general_fortran_fixtures():
    return sorted(
        path
        for path in GENERAL_FORTRAN_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in FORTRAN_SUFFIXES
    )


def iter_wrap_readiness_fortran_fixtures():
    return sorted(
        path
        for dirname in WRAP_READINESS_CORPUS_DIRS
        for path in (FORTRAN_DATA_DIR / dirname).rglob("*")
        if path.is_file() and path.suffix.lower() in FORTRAN_SUFFIXES
    )


def readiness_fixture_key(path: Path) -> str:
    return path.relative_to(FORTRAN_DATA_DIR).as_posix()


def parser_filename_for_fixture(path: Path) -> str:
    relpath = readiness_fixture_key(path)
    if relpath.startswith("scifortran/"):
        return relpath.replace("scifortran/", "SciFortran/", 1)
    return relpath


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


def wrap_readiness_message_payload_for_fixture(path: Path) -> dict:
    source_key = readiness_fixture_key(path)
    try:
        source = path.read_text(encoding="utf-8")
        parsed = parse_fortran_file(source, filename=parser_filename_for_fixture(path))
        modules = fortran_file_to_semantic_modules(parsed, standalone_module_name=path.stem)
        readiness = assess_semantic_wrap_readiness(modules, source=source_key)
    except Exception as exc:
        return {
            "wrappable": False,
            "status": "semantic_error",
            "messages": [str(exc)],
            "blockers": [
                {
                    "code": "semantic_conversion_error",
                    "message": str(exc),
                    "n_items": 0,
                }
            ],
        }

    return {
        "wrappable": readiness["wrappable"],
        "status": "ok",
        "n_modules": readiness["n_modules"],
        "n_functions": readiness["n_functions"],
        "n_classes": readiness["n_classes"],
        "n_variables": readiness["n_variables"],
        "messages": list(readiness["why_not_wrappable"]),
        "blockers": [
            {
                "code": blocker["code"],
                "message": blocker["message"],
                "n_items": len(blocker.get("items") or []),
            }
            for blocker in readiness["wrappability_blockers"]
        ],
    }


def wrap_readiness_message_payload_for_corpus() -> dict:
    return {
        "corpus": list(WRAP_READINESS_CORPUS_DIRS),
        "files": {
            readiness_fixture_key(path): wrap_readiness_message_payload_for_fixture(path)
            for path in iter_wrap_readiness_fortran_fixtures()
        },
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


def write_wrap_readiness_message_fixture() -> Path:
    SEMANTIC_READINESS_FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SEMANTIC_READINESS_FIXTURE_PATH.write_text(
        json.dumps(wrap_readiness_message_payload_for_corpus(), indent=2) + "\n",
        encoding="utf-8",
    )
    return SEMANTIC_READINESS_FIXTURE_PATH
