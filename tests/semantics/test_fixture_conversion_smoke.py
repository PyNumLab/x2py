from pathlib import Path

import pytest

from fortran_parser import parse_fortran_file
from semantics.fortran2ir import fortran_module_to_semantic_module
from semantics.pyi_printer import emit_module


_TESTS_DIR = Path(__file__).resolve().parents[1] / "parser" / "fcode"
_FORTRAN_SUFFIXES = {".f", ".f90", ".f95", ".f03", ".f08"}


def _iter_fortran_fixtures():
    for path in _TESTS_DIR.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() not in _FORTRAN_SUFFIXES:
            continue

        # Skip parse-failing fixtures covered by dedicated parser error tests.
        relpath = path.relative_to(_TESTS_DIR).as_posix()
        if relpath.startswith("errors/") or relpath.startswith("SciFortran/errors/"):
            continue

        # Restrict to fixtures with parser goldens to avoid known parse-failing
        # files (tracked separately in parser error-manifest tests).
        if not path.with_suffix(".json").exists():
            continue

        yield path


_FORTRAN_FIXTURES = sorted(_iter_fortran_fixtures())


def _parse_fixture(path: Path):
    source = path.read_text(encoding="utf-8")
    relpath = str(path.relative_to(_TESTS_DIR))
    return parse_fortran_file(source, filename=relpath)


def test_semantics_fixture_suite_has_fixtures():
    assert _FORTRAN_FIXTURES, "No Fortran fixtures found in tests/parser/fcode"


@pytest.mark.parametrize(
    "fixture",
    _FORTRAN_FIXTURES,
    ids=lambda p: str(p.relative_to(_TESTS_DIR)),
)
def test_semantic_model_conversion_smoke(fixture: Path):
    parsed = _parse_fixture(fixture)

    for module in parsed.modules:
        fortran_module_to_semantic_module(module)


@pytest.mark.parametrize(
    "fixture",
    _FORTRAN_FIXTURES,
    ids=lambda p: str(p.relative_to(_TESTS_DIR)),
)
def test_pyi_printer_conversion_smoke(fixture: Path):
    parsed = _parse_fixture(fixture)

    for module in parsed.modules:
        semantic_module = fortran_module_to_semantic_module(module)
        emit_module(semantic_module)
