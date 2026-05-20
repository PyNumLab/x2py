# -*- coding: utf-8 -*-
"""Planned C parser fixture/golden tests."""

from dataclasses import asdict, is_dataclass
import json
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.skip(
    reason="C parser fixture roadmap tests; unskip when C parser goldens exist."
)


_TESTS_DIR = Path(__file__).resolve().parents[2]
_DATA_DIR = _TESTS_DIR / "data" / "c"
_FIXTURES_DIR = Path(__file__).parent / "fixtures"
_SOURCE_SUFFIXES = {".c", ".h", ".i"}


def _source_json_relpaths(root: Path) -> set[Path]:
    return {
        path.relative_to(root).with_suffix(".json")
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in _SOURCE_SUFFIXES
    }


def _fixture_json_relpaths(root: Path) -> set[Path]:
    return {path.relative_to(root) for path in root.rglob("*.json") if path.is_file()}


def _to_jsonable(value):
    if is_dataclass(value):
        return asdict(value)
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return value


def test_c_fixture_golden_suite_has_general_fixtures():
    fixtures = sorted((_DATA_DIR / "general").glob("*"))
    assert any(path.suffix.lower() in _SOURCE_SUFFIXES for path in fixtures)


@pytest.mark.parametrize(
    ("data_subdir", "fixture_subdir"),
    [
        ("general", "general"),
        ("scientific", "scientific"),
    ],
)
def test_c_parser_fixtures_match_data_files_one_to_one(data_subdir, fixture_subdir):
    data_root = _DATA_DIR / data_subdir
    fixture_root = _FIXTURES_DIR / fixture_subdir

    expected = _source_json_relpaths(data_root)
    actual = _fixture_json_relpaths(fixture_root)

    assert not sorted(expected - actual)
    assert not sorted(actual - expected)


def test_c_fixture_golden_suite_compares_model_json():
    from c_parser import parse_c_file

    update_mode = os.getenv("C_PARSER_UPDATE_GOLDENS", "0") == "1"

    for fixture in sorted((_DATA_DIR / "general").glob("*")):
        if fixture.suffix.lower() not in _SOURCE_SUFFIXES:
            continue
        expected_path = (_FIXTURES_DIR / "general" / fixture.name).with_suffix(".json")
        parsed = _to_jsonable(parse_c_file(fixture.read_text(encoding="utf-8"), filename=fixture.name))

        if update_mode:
            expected_path.write_text(json.dumps(parsed, indent=2) + "\n", encoding="utf-8")
            continue

        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        assert parsed == expected


def test_c_fixture_golden_suite_keeps_source_locations_stable():
    from c_parser import parse_c_file

    fixture = _DATA_DIR / "general" / "basic_functions.h"
    parsed = parse_c_file(fixture)

    assert parsed.functions[0].source_location.filename.endswith("basic_functions.h")
    assert parsed.functions[0].source_location.line >= 1
    assert parsed.functions[0].source_location.column >= 1

