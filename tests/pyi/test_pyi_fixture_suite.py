from pathlib import Path

import pytest

from tests._shared.fixture_outputs import (
    C_PYI_FIXTURE_DIR,
    FORTRAN_DATA_DIR,
    PYI_FIXTURE_DIR,
    c_pyi_fixture_path,
    c_pyi_text_for_fixture_project,
    iter_general_c_fixture_projects,
    iter_general_fortran_fixtures,
    pyi_fixture_path,
    pyi_text_for_fixture,
)
from x2py.semantics.pyi_parser import parse_pyi_text
from x2py.codegen.printers.pyi_printer import emit_module


FORTRAN_FIXTURES = iter_general_fortran_fixtures()
C_FIXTURE_PROJECTS = iter_general_c_fixture_projects()


def test_pyi_fixture_suite_has_fixtures():
    assert FORTRAN_FIXTURES, "No Fortran fixtures found in tests/data/fortran/general"
    assert C_FIXTURE_PROJECTS, "No C fixtures found in tests/data/c/general"


def test_pyi_fixtures_match_fortran_data_one_to_one():
    expected = {path.with_suffix(".pyi").name for path in FORTRAN_FIXTURES}
    actual = {path.name for path in PYI_FIXTURE_DIR.glob("*.pyi")}

    assert not sorted(expected - actual)
    assert not sorted(actual - expected)


def test_c_pyi_fixtures_match_general_c_projects_one_to_one():
    expected = {project_key.with_suffix(".pyi") for project_key, _fixtures in C_FIXTURE_PROJECTS}
    actual = {path.relative_to(C_PYI_FIXTURE_DIR) for path in C_PYI_FIXTURE_DIR.rglob("*.pyi") if path.is_file()}

    assert not sorted(expected - actual)
    assert not sorted(actual - expected)


def test_pyi_fixtures_do_not_contain_unknown_types():
    unknown_fixtures = [
        path.name for path in PYI_FIXTURE_DIR.glob("*.pyi") if "Unknown" in path.read_text(encoding="utf-8")
    ]
    unknown_fixtures.extend(
        f"c/{path.relative_to(C_PYI_FIXTURE_DIR)}"
        for path in C_PYI_FIXTURE_DIR.rglob("*.pyi")
        if "Unknown" in path.read_text(encoding="utf-8")
    )

    assert not unknown_fixtures, f"Unknown semantic types in .pyi fixtures: {unknown_fixtures[:20]}"


@pytest.mark.parametrize(
    "fixture",
    FORTRAN_FIXTURES,
    ids=lambda p: str(p.relative_to(FORTRAN_DATA_DIR)),
)
def test_pyi_fixture_suite(fixture: Path):
    expected_path = pyi_fixture_path(fixture)
    expected = expected_path.read_text(encoding="utf-8").strip()

    assert pyi_text_for_fixture(fixture) == expected


@pytest.mark.parametrize(
    ("project_key", "fixtures"),
    C_FIXTURE_PROJECTS,
    ids=[str(project_key) for project_key, _fixtures in C_FIXTURE_PROJECTS],
)
def test_c_pyi_fixture_suite(project_key: Path, fixtures: list[Path]):
    expected_path = c_pyi_fixture_path(project_key)
    expected = expected_path.read_text(encoding="utf-8").strip()

    assert c_pyi_text_for_fixture_project(project_key, fixtures) == expected


@pytest.mark.parametrize(
    "fixture",
    sorted(C_PYI_FIXTURE_DIR.rglob("*.pyi")),
    ids=lambda path: str(path.relative_to(C_PYI_FIXTURE_DIR)),
)
def test_c_pyi_fixtures_round_trip_through_semantic_ir(fixture: Path):
    expected = fixture.read_text(encoding="utf-8").strip()
    module = parse_pyi_text(
        expected,
        module_name=fixture.stem,
        filename=str(fixture),
    )

    assert module.name == fixture.stem
    assert emit_module(module).strip() == expected
