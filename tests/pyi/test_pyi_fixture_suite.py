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
    pyi_files_for_fixture,
)
from x2py.semantics.pyi2ir import parse_pyi_text
from x2py.codegen.printers.pyi_printer import emit_module
from x2py.wrapping import _discover_pyi_imports


FORTRAN_FIXTURES = iter_general_fortran_fixtures()
C_FIXTURE_PROJECTS = iter_general_c_fixture_projects()


def test_pyi_fixture_suite_has_fixtures():
    assert FORTRAN_FIXTURES, "No Fortran fixtures found in tests/data/fortran/general"
    assert C_FIXTURE_PROJECTS, "No C fixtures found in tests/data/c/general"


def test_pyi_fixtures_match_fortran_data_one_to_one():
    expected = {name for path in FORTRAN_FIXTURES for name in pyi_files_for_fixture(path)}
    actual = {path.relative_to(PYI_FIXTURE_DIR) for path in PYI_FIXTURE_DIR.rglob("*.pyi")}

    assert not sorted(expected - actual)
    assert not sorted(actual - expected)


def test_fortran_pyi_fixtures_are_source_owned_contract_directories():
    assert not list(PYI_FIXTURE_DIR.glob("*.pyi"))
    assert {path.name for path in PYI_FIXTURE_DIR.iterdir() if path.is_dir()} == {
        path.stem for path in FORTRAN_FIXTURES
    }


def test_c_pyi_fixtures_match_general_c_projects_one_to_one():
    expected = {project_key.with_suffix(".pyi") for project_key, _fixtures in C_FIXTURE_PROJECTS}
    actual = {path.relative_to(C_PYI_FIXTURE_DIR) for path in C_PYI_FIXTURE_DIR.rglob("*.pyi") if path.is_file()}

    assert not sorted(expected - actual)
    assert not sorted(actual - expected)


def test_pyi_fixtures_do_not_contain_unknown_types():
    unknown_fixtures = [
        str(path.relative_to(PYI_FIXTURE_DIR))
        for path in PYI_FIXTURE_DIR.rglob("*.pyi")
        if "Unknown" in path.read_text(encoding="utf-8")
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
    generated = pyi_files_for_fixture(fixture)
    for name, text in generated.items():
        expected = PYI_FIXTURE_DIR.joinpath(name).read_text(encoding="utf-8").strip()
        assert text == expected


@pytest.mark.parametrize(
    ("source_name", "expected_files"),
    [
        (
            "basic_subroutine",
            {"basic_subroutine/basic_subroutine.pyi", "basic_subroutine/m1.pyi"},
        ),
        (
            "contract_standalone_only",
            {"contract_standalone_only/contract_standalone_only.pyi"},
        ),
        (
            "contract_mixed_module_external",
            {
                "contract_mixed_module_external/contract_mixed_module_external.pyi",
                "contract_mixed_module_external/contract_math_mod.pyi",
            },
        ),
        (
            "contract_same_name",
            {"contract_same_name/__init__.pyi", "contract_same_name/contract_same_name.pyi"},
        ),
        (
            "contract_multi_module",
            {
                "contract_multi_module/contract_multi_module.pyi",
                "contract_multi_module/contract_left_mod.pyi",
                "contract_multi_module/contract_right_mod.pyi",
            },
        ),
    ],
)
def test_generated_contract_layout_cases(source_name: str, expected_files: set[str]):
    source = next(path for path in FORTRAN_FIXTURES if path.stem == source_name)

    assert {str(path) for path in pyi_files_for_fixture(source)} == expected_files


def test_generated_standalone_contract_marks_every_procedure_external():
    entry = PYI_FIXTURE_DIR / "contract_standalone_only" / "contract_standalone_only.pyi"
    text = entry.read_text(encoding="utf-8")

    assert text.count("@external") == 2
    assert "def standalone_ping() -> None: ..." in text
    assert "def standalone_double(" in text
    assert "@native_call([Ref(Arg(0))])" in text
    assert "value: Const(Int32)" in text
    assert ") -> Int32: ..." in text


def test_generated_mixed_contract_keeps_module_and_external_placement_separate():
    package = PYI_FIXTURE_DIR / "contract_mixed_module_external"

    assert (
        (package / "contract_mixed_module_external.pyi")
        .read_text(encoding="utf-8")
        .startswith("from . import contract_math_mod\n\n@external\n")
    )
    assert "@external" not in (package / "contract_math_mod.pyi").read_text(encoding="utf-8")


def test_generated_same_name_contract_uses_init_entry():
    package = PYI_FIXTURE_DIR / "contract_same_name"

    assert (package / "__init__.pyi").read_text(encoding="utf-8") == (
        "from . import contract_same_name\n\n@external\ndef external_ping() -> None: ...\n"
    )
    assert "def module_ping() -> None: ..." in (package / "contract_same_name.pyi").read_text(encoding="utf-8")


def test_generated_multi_module_contract_preserves_colliding_child_namespaces():
    package = PYI_FIXTURE_DIR / "contract_multi_module"

    assert (package / "contract_multi_module.pyi").read_text(encoding="utf-8") == (
        "from . import contract_left_mod\nfrom . import contract_right_mod\n"
    )
    for module_name in ("contract_left_mod", "contract_right_mod"):
        assert "def shared_value(" in (package / f"{module_name}.pyi").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "fixture",
    FORTRAN_FIXTURES,
    ids=lambda path: path.stem,
)
def test_generated_entry_recursively_discovers_its_complete_contract_directory(fixture: Path):
    package = PYI_FIXTURE_DIR / fixture.stem
    init_entry = package / "__init__.pyi"
    entry = init_entry if init_entry.is_file() else package / f"{fixture.stem}.pyi"

    discovered = {entry, *_discover_pyi_imports(entry)}

    assert discovered == set(package.rglob("*.pyi"))


@pytest.mark.parametrize(
    "fixture",
    sorted(PYI_FIXTURE_DIR.rglob("*.pyi")),
    ids=lambda path: str(path.relative_to(PYI_FIXTURE_DIR)),
)
def test_fortran_pyi_fixtures_round_trip_through_semantic_ir(fixture: Path):
    expected = fixture.read_text(encoding="utf-8").strip()
    module_name = fixture.parent.name if fixture.name == "__init__.pyi" else fixture.stem
    module = parse_pyi_text(
        expected,
        module_name=module_name,
        filename=str(fixture),
    )

    assert emit_module(module).strip() == expected


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
