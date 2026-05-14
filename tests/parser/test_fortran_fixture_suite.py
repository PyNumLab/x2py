# -*- coding: utf-8 -*-
import json
import os
from dataclasses import asdict
from pathlib import Path

import pytest

from fortran_parser import parse_fortran_file


def parse_fortran_modules(source, filename=None):
    return parse_fortran_file(source, filename=filename).modules


_TESTS_DIR = Path(__file__).parent / "fcode"
_GOLDEN_FIXTURES = sorted(_TESTS_DIR.glob("*.f*"))
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
    for f in (_TESTS_DIR / "SciFortran").glob("*")
    if f.is_file()
    and f.suffix.lower() in {".f", ".f90", ".f95", ".f03", ".f08"}
    and f.with_suffix(".json").exists()
)
_SCIFORTRAN_ERROR_EXPECTATIONS = _TESTS_DIR / "SciFortran" / "errors" / "SciFortran_errors.json"

def _load_expected(expected_path: Path):
    with expected_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _strip_parent_fields(value):
    if isinstance(value, dict):
        return {
            k: _strip_parent_fields(v)
            for k, v in value.items()
            if k not in {"parent", "source_span", "line", "column", "end_line", "end_column"}
        }
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
    assert _GOLDEN_FIXTURES, "No fixtures found in tests/fcode"


@pytest.mark.parametrize("fixture", _GOLDEN_FIXTURES, ids=lambda f: f.name)
def test_fortran_fixture_golden_suite(fixture):
    _run_fixture_comparison(
        fixture,
        filename_for_parser=fixture.name,
        expected_path=fixture.with_suffix(".json"),
    )


def test_fortran_blas_parse_suite_has_fixtures():
    assert _BLAS_FIXTURES, "No BLAS fixtures found in tests/fcode/blas"


@pytest.mark.parametrize("fixture", _BLAS_FIXTURES, ids=lambda f: str(f.relative_to(_TESTS_DIR)))
def test_fortran_blas_parse_suite(fixture):
    relpath = str(fixture.relative_to(_TESTS_DIR))
    _run_fixture_comparison(
        fixture,
        filename_for_parser=relpath,
        expected_path=fixture.with_suffix(".json"),
    )


def test_fortran_lapack_parse_suite_has_fixtures():
    assert _LAPACK_FIXTURES, "No LAPACK fixtures found in tests/fcode/lapack"


@pytest.mark.parametrize("fixture", _LAPACK_FIXTURES, ids=lambda f: str(f.relative_to(_TESTS_DIR)))
def test_fortran_lapack_parse_suite(fixture):
    relpath = str(fixture.relative_to(_TESTS_DIR))
    _run_fixture_comparison(
        fixture,
        filename_for_parser=relpath,
        expected_path=fixture.with_suffix(".json"),
    )


def test_fortran_scifortran_parse_suite_has_fixtures():
    assert _SCIFORTRAN_FIXTURES, "No SciFortran fixtures found in tests/fcode/SciFortran"


@pytest.mark.parametrize("fixture", _SCIFORTRAN_FIXTURES, ids=lambda f: str(f.relative_to(_TESTS_DIR)))
def test_fortran_scifortran_parse_suite(fixture):
    relpath = str(fixture.relative_to(_TESTS_DIR))
    _run_fixture_comparison(
        fixture,
        filename_for_parser=relpath,
        expected_path=fixture.with_suffix(".json"),
    )


def test_fortran_scifortran_error_manifest_is_in_sync():
    with _SCIFORTRAN_ERROR_EXPECTATIONS.open("r", encoding="utf-8") as f:
        error_expectations = json.load(f)

    for item in error_expectations:
        relpath = item["fixture"]
        fixture = _TESTS_DIR / relpath
        source = fixture.read_text(encoding="utf-8")

        with pytest.raises(Exception) as exc_info:
            parse_fortran_file(source, filename=relpath)

        message = str(exc_info.value)
        for fragment in item.get("message_fragments", []):
            assert fragment in message, f"Missing message fragment {fragment!r} for {relpath}"

        for fragment in item.get("diagnostic_fragments", []):
            assert fragment in message, f"Missing diagnostic fragment {fragment!r} for {relpath}"


def test_fortran_scifortran_error_manifest_covers_error_directory():
    with _SCIFORTRAN_ERROR_EXPECTATIONS.open("r", encoding="utf-8") as f:
        error_expectations = json.load(f)

    manifest_paths = {item["fixture"] for item in error_expectations}
    error_dir_paths = {
        str(p.relative_to(_TESTS_DIR))
        for p in (_TESTS_DIR / "SciFortran" / "errors").glob("*.f90")
    }

    assert manifest_paths == error_dir_paths, (
        "SciFortran error manifest and SciFortran/errors directory are out of sync"
    )


def test_fortran_scifortran_error_manifest_uses_error_directory_only():
    with _SCIFORTRAN_ERROR_EXPECTATIONS.open("r", encoding="utf-8") as f:
        error_expectations = json.load(f)

    for item in error_expectations:
        relpath = item["fixture"]
        assert relpath.startswith("SciFortran/errors/"), (
            f"Error manifest fixture must live in SciFortran/errors: {relpath}"
        )
        assert item.get("message_fragments"), (
            f"Error manifest item must document at least one error fragment: {relpath}"
        )


def test_fortran_scifortran_main_directory_has_no_error_fixtures():
    with _SCIFORTRAN_ERROR_EXPECTATIONS.open("r", encoding="utf-8") as f:
        error_expectations = json.load(f)

    manifest_basenames = {Path(item["fixture"]).name for item in error_expectations}
    main_scifortran_fixtures = {
        p.name
        for p in (_TESTS_DIR / "SciFortran").glob("*.f90")
    }

    overlap = sorted(manifest_basenames & main_scifortran_fixtures)
    assert not overlap, (
        "Files listed as parse-failing must be moved out of SciFortran/ and into "
        f"SciFortran/errors first: {overlap[:10]}"
    )
