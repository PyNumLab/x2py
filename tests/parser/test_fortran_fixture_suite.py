# -*- coding: utf-8 -*-
import json
import os
from dataclasses import asdict
from pathlib import Path

import pytest

from fortran_parser import parse_fortran_file


def parse_fortran_modules(source, filename=None):
    return parse_fortran_file(source, filename=filename).modules


_TESTS_DIR = Path(__file__).resolve().parents[1] / "data" / "fortran"
_FIXTURES_DIR = Path(__file__).parent / "fortran" / "fixtures"


def _has_direct_expected_json(fixture: Path) -> bool:
    return (_FIXTURES_DIR / fixture.relative_to(_TESTS_DIR)).with_suffix(".json").exists()


_GOLDEN_FIXTURES = sorted(
    f for f in (_TESTS_DIR / "general").glob("*")
    if f.is_file() and f.suffix.lower() in {".f", ".f90", ".f95", ".f03", ".f08", ".for"}
    and _has_direct_expected_json(f)
)
_BLAS_FIXTURES = sorted(
    f
    for f in (_TESTS_DIR / "blas").rglob("*")
    if f.is_file() and f.suffix.lower() in {".f", ".f90", ".f95", ".f03", ".f08"}
)
_LAPACK_FIXTURES = sorted(
    f
    for f in (_TESTS_DIR / "lapack").rglob("*")
    if f.is_file() and f.suffix.lower() in {".f", ".f90", ".f95", ".f03", ".f08"}
)
_SCIFORTRAN_FIXTURES = sorted(
    f
    for f in (_TESTS_DIR / "scifortran").glob("*")
    if f.is_file()
    and f.suffix.lower() in {".f", ".f90", ".f95", ".f03", ".f08"}
    and _has_direct_expected_json(f)
    )



def _expected_json_for_fixture(fixture: Path) -> Path:
    rel = fixture.relative_to(_TESTS_DIR)
    direct = (_FIXTURES_DIR / rel).with_suffix(".json")
    if direct.exists():
        return direct
    fallback = _FIXTURES_DIR / "general" / (fixture.stem + ".json")
    return fallback


def _parser_filename_for_fixture(fixture: Path) -> str:
    relpath = str(fixture.relative_to(_TESTS_DIR))
    if relpath.startswith("scifortran/"):
        direct = (_FIXTURES_DIR / Path(relpath)).with_suffix(".json")
        if direct.exists():
            return relpath.replace("scifortran/", "SciFortran/", 1)
        return fixture.name
    return relpath if "/" in relpath else fixture.name
def _load_expected(expected_path: Path):
    with expected_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _strip_parent_fields(value):
    if isinstance(value, dict):
        return {k: _strip_parent_fields(v) for k, v in value.items() if k != "parent"}
    if isinstance(value, list):
        return [_strip_parent_fields(v) for v in value]
    return value


def _to_dict(value):
    return _strip_parent_fields(asdict(value))


def _dump_expected(path: Path, parsed: dict) -> None:
    payload = parsed
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _run_fixture_comparison(fixture: Path, *, filename_for_parser: str, expected_path: Path) -> None:
    source = fixture.read_text(encoding="utf-8")
    assert source.strip(), f"Fixture is empty: {filename_for_parser}"

    parsed = _to_dict(parse_fortran_file(source, filename=filename_for_parser))

    update_mode = os.getenv("FORTRAN_PARSER_UPDATE_GOLDENS", "0") == "1"
    if update_mode:
        _dump_expected(expected_path, parsed)
        return

    expected = _load_expected(expected_path)
    assert parsed == expected, f"FortranFile mismatch for {fixture.name}"


def test_fortran_fixture_golden_suite_has_fixtures():
    assert _GOLDEN_FIXTURES, "No fixtures found in tests/data/fortran"


@pytest.mark.parametrize("fixture", _GOLDEN_FIXTURES, ids=lambda f: f.name)
def test_fortran_fixture_golden_suite(fixture):
    _run_fixture_comparison(
        fixture,
        filename_for_parser=fixture.name,
        expected_path=_expected_json_for_fixture(fixture),
    )


def test_fortran_blas_parse_suite_has_fixtures():
    assert _BLAS_FIXTURES, "No BLAS fixtures found in tests/data/fortran/blas"


@pytest.mark.parametrize("fixture", _BLAS_FIXTURES, ids=lambda f: str(f.relative_to(_TESTS_DIR)))
def test_fortran_blas_parse_suite(fixture):
    _run_fixture_comparison(
        fixture,
        filename_for_parser=_parser_filename_for_fixture(fixture),
        expected_path=_expected_json_for_fixture(fixture),
    )


def test_fortran_lapack_parse_suite_has_fixtures():
    assert _LAPACK_FIXTURES, "No LAPACK fixtures found in tests/data/fortran/lapack"


@pytest.mark.parametrize("fixture", _LAPACK_FIXTURES, ids=lambda f: str(f.relative_to(_TESTS_DIR)))
def test_fortran_lapack_parse_suite(fixture):
    _run_fixture_comparison(
        fixture,
        filename_for_parser=_parser_filename_for_fixture(fixture),
        expected_path=_expected_json_for_fixture(fixture),
    )


def test_fortran_scifortran_parse_suite_has_fixtures():
    assert _SCIFORTRAN_FIXTURES, "No scifortran fixtures found in tests/data/fortran/scifortran"


@pytest.mark.parametrize("fixture", _SCIFORTRAN_FIXTURES, ids=lambda f: str(f.relative_to(_TESTS_DIR)))
def test_fortran_scifortran_parse_suite(fixture):
    _run_fixture_comparison(
        fixture,
        filename_for_parser=_parser_filename_for_fixture(fixture),
        expected_path=_expected_json_for_fixture(fixture),
    )
