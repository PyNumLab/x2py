import json
import os
from dataclasses import asdict
from pathlib import Path

from fortran_parser import parse_fortran_signatures, parse_fortran_types

_TESTS_DIR = Path(__file__).parent / "fcode"
_REQUIRED_FIXTURES = {
    "f77_subroutine",
    "module_vars_use",
    "procedures_and_functions",
    "derived_types_and_methods",
}


def _load_expected(fixture_name: str):
    expected_path = _TESTS_DIR / f"{fixture_name}.json"
    with expected_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return {"signatures": data, "types": []}
    return {"signatures": data.get("signatures", []), "types": data.get("types", [])}


def _to_dict_list(items):
    return [asdict(i) for i in items]


def _dump_expected(path: Path, signatures: list[dict], types: list[dict]) -> None:
    payload = signatures if not types else {"signatures": signatures, "types": types}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def test_fortran_fixture_golden_suite():
    fixture_files = sorted(_TESTS_DIR.glob("*.f*"))
    assert fixture_files, "No fixtures found in tests/fcode"
    present = {f.stem for f in fixture_files}
    missing = sorted(_REQUIRED_FIXTURES - present)
    assert not missing, f"Missing required baseline fixtures: {missing}"

    update_mode = os.getenv("FORTRAN_PARSER_UPDATE_GOLDENS", "0") == "1"

    for fixture in fixture_files:
        key = fixture.stem
        expected_path = _TESTS_DIR / f"{key}.json"
        if not expected_path.exists() and update_mode:
            _dump_expected(expected_path, [], [])
        expected = _load_expected(key)
        source = fixture.read_text(encoding="utf-8")

        parsed_sigs = _to_dict_list(parse_fortran_signatures(source, filename=fixture.name))
        parsed_types = _to_dict_list(parse_fortran_types(source, filename=fixture.name))

        if update_mode:
            _dump_expected(expected_path, parsed_sigs, parsed_types)
            continue

        assert parsed_sigs == expected["signatures"], f"Signature mismatch for {fixture.name}"
        assert parsed_types == expected["types"], f"Derived type mismatch for {fixture.name}"
