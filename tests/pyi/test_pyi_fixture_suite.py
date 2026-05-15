from pathlib import Path

import pytest

from tests._shared.fixture_outputs import (
    FORTRAN_DATA_DIR,
    PYI_FIXTURE_DIR,
    iter_general_fortran_fixtures,
    pyi_fixture_path,
    pyi_text_for_fixture,
)


FORTRAN_FIXTURES = iter_general_fortran_fixtures()


def test_pyi_fixture_suite_has_fixtures():
    assert FORTRAN_FIXTURES, "No Fortran fixtures found in tests/data/fortran/general"


def test_pyi_fixtures_match_fortran_data_one_to_one():
    expected = {path.with_suffix(".pyi").name for path in FORTRAN_FIXTURES}
    actual = {path.name for path in PYI_FIXTURE_DIR.glob("*.pyi")}

    assert not sorted(expected - actual)
    assert not sorted(actual - expected)


@pytest.mark.parametrize(
    "fixture",
    FORTRAN_FIXTURES,
    ids=lambda p: str(p.relative_to(FORTRAN_DATA_DIR)),
)
def test_pyi_fixture_suite(fixture: Path):
    expected_path = pyi_fixture_path(fixture)
    expected = expected_path.read_text(encoding="utf-8").strip()

    assert pyi_text_for_fixture(fixture) == expected
