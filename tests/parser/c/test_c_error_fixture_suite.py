# -*- coding: utf-8 -*-
"""Planned C parser error fixture and diagnostic golden tests."""

import json
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.skip(
    reason="C parser error fixture roadmap tests; unskip when CParseError and error goldens exist."
)


_TESTS_DIR = Path(__file__).resolve().parents[2]
_ERRORS_DIR = _TESTS_DIR / "data" / "c" / "errors" / "parser"
_EXPECTED_ERRORS_DIR = Path(__file__).parent / "fixtures" / "errors"
_SOURCE_SUFFIXES = {".c", ".h", ".i"}


def _load_expected_error(expected_path: Path) -> dict:
    return json.loads(expected_path.read_text(encoding="utf-8"))


def test_c_error_fixture_suite_has_fixtures():
    fixtures = [path for path in _ERRORS_DIR.glob("*") if path.suffix.lower() in _SOURCE_SUFFIXES]
    assert fixtures, "No C parser error fixtures found in tests/data/c/errors/parser"


def test_c_error_fixtures_have_matching_expected_json():
    fixture_stems = {path.stem for path in _ERRORS_DIR.glob("*") if path.suffix.lower() in _SOURCE_SUFFIXES}
    expected_stems = {path.stem for path in _EXPECTED_ERRORS_DIR.glob("*.json")}

    assert not sorted(fixture_stems - expected_stems)
    assert not sorted(expected_stems - fixture_stems)


def test_c_error_fixture_suite_reports_expected_diagnostics():
    from c_parser import CParseError, parse_c_file

    update_mode = os.getenv("C_PARSER_UPDATE_GOLDENS", "0") == "1"

    for fixture in sorted(_ERRORS_DIR.glob("*")):
        if fixture.suffix.lower() not in _SOURCE_SUFFIXES:
            continue
        expected_path = _EXPECTED_ERRORS_DIR / f"{fixture.stem}.json"
        source = fixture.read_text(encoding="utf-8")

        if update_mode:
            with pytest.raises(CParseError) as exc_info:
                parse_c_file(source, filename=fixture.name)
            payload = {
                "parser": "parse_c_file",
                "error_type": "CParseError",
                "message_contains": [exc_info.value.base_message],
                "diagnostic_contains": [
                    f"error[{exc_info.value.code}]",
                    exc_info.value.base_message,
                    exc_info.value.source_line.strip() if exc_info.value.source_line else "",
                ],
            }
            expected_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            continue

        expected = _load_expected_error(expected_path)
        with pytest.raises(CParseError) as exc_info:
            parse_c_file(source, filename=fixture.name)

        for fragment in expected["message_contains"]:
            assert fragment in str(exc_info.value)
        diagnostic = exc_info.value.format_diagnostic(color=False)
        for fragment in expected.get("diagnostic_contains", []):
            if fragment:
                assert fragment in diagnostic

