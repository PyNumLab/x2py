# -*- coding: utf-8 -*-
"""Planned JSON schema sanity tests for C parser goldens."""

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.skip(
    reason="C parser JSON sanity roadmap tests; unskip when C JSON goldens exist."
)


_FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _iter_json_payloads():
    for path in _FIXTURES_DIR.rglob("*.json"):
        if path.name.endswith("_errors.json"):
            continue
        yield path, json.loads(path.read_text(encoding="utf-8"))


def test_c_json_fixtures_are_valid_json():
    for path in _FIXTURES_DIR.rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))


def test_c_json_fixtures_have_stable_top_level_shape():
    required_keys = {
        "language",
        "filename",
        "functions",
        "structs",
        "unions",
        "enums",
        "typedefs",
        "variables",
        "macros",
        "includes",
        "diagnostics",
    }

    for path, payload in _iter_json_payloads():
        assert required_keys <= set(payload), f"missing keys in {path}"
        assert payload["language"] == "c"


def test_c_json_functions_have_names_types_and_source_locations():
    for path, payload in _iter_json_payloads():
        for fn in payload.get("functions", []):
            assert fn["name"], f"function without name in {path}"
            assert fn["result_type"], f"function without result type in {path}"
            assert isinstance(fn["parameters"], list)
            assert fn["source_location"]["line"] >= 1
            assert fn["source_location"]["column"] >= 1


def test_c_json_types_have_distinct_names_or_anonymous_ids():
    for path, payload in _iter_json_payloads():
        for key in ("structs", "unions", "enums"):
            for entry in payload.get(key, []):
                assert entry.get("name") or entry.get("anonymous_id"), f"anonymous {key} missing id in {path}"


def test_c_json_diagnostics_have_codes_locations_and_severities():
    allowed = {"info", "warning", "error"}

    for path, payload in _iter_json_payloads():
        for diagnostic in payload.get("diagnostics", []):
            assert diagnostic["code"]
            assert diagnostic["severity"] in allowed
            assert diagnostic.get("message")
            if diagnostic.get("source_location"):
                assert diagnostic["source_location"]["line"] >= 1
