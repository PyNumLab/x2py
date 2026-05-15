import json
from pathlib import Path

import pytest

from _fixture_conversion_utils import FORTRAN_FIXTURES, TESTS_DIR, parse_fixture
from tests._shared.fixture_outputs import (
    SEMANTICS_FIXTURE_DIR,
    semantic_payload_for_fixture,
    semantics_fixture_path,
)


def test_semantics_fixture_suite_has_fixtures():
    assert FORTRAN_FIXTURES, "No Fortran fixtures found in tests/data/fortran/general"


def test_semantic_fixtures_match_fortran_data_one_to_one():
    expected = {path.with_suffix(".json").name for path in FORTRAN_FIXTURES}
    actual = {path.name for path in SEMANTICS_FIXTURE_DIR.glob("*.json")}

    assert not sorted(expected - actual)
    assert not sorted(actual - expected)


@pytest.mark.parametrize(
    "fixture",
    FORTRAN_FIXTURES,
    ids=lambda p: str(p.relative_to(TESTS_DIR)),
)
def test_semantic_model_fixture_suite(fixture: Path):
    parse_fixture(fixture)
    expected_path = semantics_fixture_path(fixture)
    expected = json.loads(expected_path.read_text(encoding="utf-8"))

    assert semantic_payload_for_fixture(fixture) == expected
