import json
import os
from dataclasses import asdict
from pathlib import Path

import pytest

from fortran_parser import parse_fortran_signatures, parse_fortran_types

_TESTS_DIR = Path(__file__).parent / "fcode"
_REQUIRED_FIXTURES = {
    "f77_subroutine",
    "module_vars_use",
    "procedures_and_functions",
    "derived_types_and_methods",
    "assumed_shape_and_derived_args",
    "compile_time_shape_exprs",
    "compile_time_all_exprs",
}
_REQUIRED_BLAS_LAPACK_FIXTURES = {
    "lapack/chetrd_hb2st.F",
    "lapack/dsytrd_sb2st.F",
    "lapack/iparam2stage.F",
    "lapack/la_xisnan.F90",
    "lapack/ssytrd_sb2st.F",
    "lapack/zhetrd_hb2st.F",
}
_GOLDEN_FIXTURES = sorted(_TESTS_DIR.glob("*.f*"))
_BLAS_LAPACK_FIXTURES = sorted(
    f
    for f in _TESTS_DIR.rglob("*")
    if f.is_file()
    and f.suffix.lower() in {".f", ".f90", ".f95", ".f03", ".f08"}
    and any(part in {"blas", "lapack"} for part in f.parts)
)


def _load_expected(expected_path: Path):
    with expected_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return {"signatures": data, "types": []}
    return {"signatures": data.get("signatures", []), "types": data.get("types", [])}


def _strip_parent_fields(value):
    if isinstance(value, dict):
        return {k: _strip_parent_fields(v) for k, v in value.items() if k != "parent"}
    if isinstance(value, list):
        return [_strip_parent_fields(v) for v in value]
    return value


def _to_dict_list(items):
    return [_strip_parent_fields(asdict(i)) for i in items]


def _dump_expected(path: Path, signatures: list[dict], types: list[dict]) -> None:
    payload = signatures if not types else {"signatures": signatures, "types": types}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def test_fortran_fixture_golden_suite_has_fixtures():
    assert _GOLDEN_FIXTURES, "No fixtures found in tests/fcode"
    present = {f.stem for f in _GOLDEN_FIXTURES}
    missing = sorted(_REQUIRED_FIXTURES - present)
    assert not missing, f"Missing required baseline fixtures: {missing}"


@pytest.mark.parametrize("fixture", _GOLDEN_FIXTURES, ids=lambda f: f.name)
def test_fortran_fixture_golden_suite(fixture):

    update_mode = os.getenv("FORTRAN_PARSER_UPDATE_GOLDENS", "0") == "1"

    expected_path = fixture.with_suffix(".json")
    if not expected_path.exists() and update_mode:
        _dump_expected(expected_path, [], [])
    expected = _load_expected(expected_path)
    source = fixture.read_text(encoding="utf-8")

    parsed_sigs = _to_dict_list(parse_fortran_signatures(source, filename=fixture.name))
    parsed_types = _to_dict_list(parse_fortran_types(source, filename=fixture.name))

    if update_mode:
        _dump_expected(expected_path, parsed_sigs, parsed_types)
        return

    assert parsed_sigs == expected["signatures"], f"Signature mismatch for {fixture.name}"
    assert parsed_types == expected["types"], f"Derived type mismatch for {fixture.name}"


def test_fortran_blas_lapack_parse_suite_has_fixtures():
    assert _BLAS_LAPACK_FIXTURES, "No BLAS/LAPACK fixtures found in tests/fcode"
    relpaths = {str(f.relative_to(_TESTS_DIR)) for f in _BLAS_LAPACK_FIXTURES}
    assert any(path.startswith("blas/") for path in relpaths), "No BLAS fixtures found in tests/fcode"
    assert any(path.startswith("lapack/") for path in relpaths), "No LAPACK fixtures found in tests/fcode"
    missing = sorted(_REQUIRED_BLAS_LAPACK_FIXTURES - relpaths)
    assert not missing, f"Missing required BLAS/LAPACK fixtures: {missing}"


@pytest.mark.parametrize("fixture", _BLAS_LAPACK_FIXTURES, ids=lambda f: str(f.relative_to(_TESTS_DIR)))
def test_fortran_blas_lapack_parse_suite(fixture):
    source = fixture.read_text(encoding="utf-8")
    relpath = str(fixture.relative_to(_TESTS_DIR))
    parsed_sigs = parse_fortran_signatures(source, filename=relpath)
    parsed_types = parse_fortran_types(source, filename=relpath)

    assert source.strip(), f"Fixture is empty: {relpath}"
    assert isinstance(parsed_sigs, list), f"Signature parse did not return a list for {relpath}"
    assert isinstance(parsed_types, list), f"Type parse did not return a list for {relpath}"
