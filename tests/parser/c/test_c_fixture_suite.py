# -*- coding: utf-8 -*-
"""C parser grouped-project fixture/golden regression tests."""

import json
import os
from pathlib import Path

import pytest

_TESTS_DIR = Path(__file__).resolve().parents[2]
_DATA_DIR = _TESTS_DIR / "data" / "c"
_FIXTURES_DIR = Path(__file__).parent / "fixtures"
_SOURCE_SUFFIXES = {".c", ".h", ".i"}
_SOURCE_ORDER = {".c": 0, ".h": 1, ".i": 2}
_FIXTURE_GROUPS = ("general", "json", "tinyexpr", "linmath", "nanosvg", "stb")
_PROJECT_OVERRIDES = {
    "nanosvg": {
        "nanosvg": ("nanosvg.h", "nanosvgrast.h"),
    },
}


def _parser_filename_for_fixture(fixture: Path) -> str:
    return fixture.relative_to(_DATA_DIR).as_posix()


def _fixture_sort_key(fixture: Path) -> tuple[int, str]:
    return (_SOURCE_ORDER.get(fixture.suffix.lower(), 99), fixture.as_posix())


def _project_key(fixture: Path, root: Path) -> Path:
    relative = fixture.relative_to(root)
    for project_name, filenames in _PROJECT_OVERRIDES.get(root.name, {}).items():
        if relative.name in filenames:
            return Path(project_name)
    return relative.with_suffix("")


def _project_groups(root: Path) -> list[tuple[Path, list[Path]]]:
    grouped: dict[Path, list[Path]] = {}
    for fixture in sorted(root.rglob("*"), key=_fixture_sort_key):
        if fixture.is_file() and fixture.suffix.lower() in _SOURCE_SUFFIXES:
            grouped.setdefault(_project_key(fixture, root), []).append(fixture)
    projects = []
    for project_key, fixtures in sorted(grouped.items()):
        override = _PROJECT_OVERRIDES.get(root.name, {}).get(project_key.name)
        if override is not None:
            order = {filename: index for index, filename in enumerate(override)}
            fixtures = sorted(fixtures, key=lambda fixture: order[fixture.name])
        else:
            fixtures = sorted(fixtures, key=_fixture_sort_key)
        projects.append((project_key, fixtures))
    return projects


def _source_json_relpaths(root: Path) -> set[Path]:
    return {project_key.with_suffix(".json") for project_key, _ in _project_groups(root)}


def _fixture_json_relpaths(root: Path) -> set[Path]:
    return {path.relative_to(root) for path in root.rglob("*.json") if path.is_file()}


def _expected_path_for_project(data_subdir: str, project_key: Path) -> Path:
    return (_FIXTURES_DIR / data_subdir / project_key).with_suffix(".json")


def _load_expected(expected_path: Path) -> dict:
    return json.loads(expected_path.read_text(encoding="utf-8"))


def _dump_expected(path: Path, parsed: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(parsed, indent=2) + "\n", encoding="utf-8")


def _normalize_resolved_paths(value):
    if isinstance(value, dict):
        resolved_path = value.get("resolved_path")
        if resolved_path:
            try:
                value["resolved_path"] = Path(resolved_path).relative_to(_DATA_DIR).as_posix()
            except ValueError:
                pass
        for key, nested in value.items():
            value[key] = _normalize_resolved_paths(nested)
    elif isinstance(value, list):
        return [_normalize_resolved_paths(nested) for nested in value]
    elif isinstance(value, str):
        try:
            path = Path(value)
            if path.is_absolute():
                return path.relative_to(_DATA_DIR).as_posix()
        except ValueError:
            pass
    return value


def _parse_project(fixtures: list[Path]):
    from c_parser import parse_c_project

    sources = {
        _parser_filename_for_fixture(fixture): fixture.read_text(encoding="utf-8")
        for fixture in sorted(fixtures, key=_fixture_sort_key)
    }
    include_dirs = sorted({fixture.parent for fixture in fixtures})
    return parse_c_project(sources, include_dirs=include_dirs)


def _serialize_project(fixtures: list[Path]) -> dict:
    return _normalize_resolved_paths(_parse_project(fixtures).to_dict())


def _update_mode_enabled() -> bool:
    return os.getenv("C_PARSER_UPDATE_GOLDENS", "0") == "1"


@pytest.mark.parametrize("data_subdir", _FIXTURE_GROUPS)
def test_c_fixture_golden_suite_has_inputs(data_subdir):
    fixtures = sorted((_DATA_DIR / data_subdir).glob("*"))
    assert any(path.suffix.lower() in _SOURCE_SUFFIXES for path in fixtures)


@pytest.mark.parametrize("data_subdir", _FIXTURE_GROUPS)
def test_c_parser_project_goldens_match_fixture_stems_one_to_one(data_subdir):
    data_root = _DATA_DIR / data_subdir
    fixture_root = _FIXTURES_DIR / data_subdir

    expected = _source_json_relpaths(data_root)
    actual = _fixture_json_relpaths(fixture_root)

    assert not sorted(expected - actual)
    assert not sorted(actual - expected)


@pytest.mark.parametrize("data_subdir", _FIXTURE_GROUPS)
def test_c_fixture_golden_suite_compares_project_json(data_subdir):
    for project_key, fixtures in _project_groups(_DATA_DIR / data_subdir):
        expected_path = _expected_path_for_project(data_subdir, project_key)
        parsed = _serialize_project(fixtures)

        if _update_mode_enabled():
            _dump_expected(expected_path, parsed)
            continue

        expected = _load_expected(expected_path)
        assert parsed == expected


def test_c_fixture_golden_suite_keeps_source_locations_stable():
    project = _parse_project(
        [
            _DATA_DIR / "general" / "basic_array_update.h",
            _DATA_DIR / "general" / "basic_array_update.c",
        ]
    )
    function = project.files["general/basic_array_update.h"].functions[0]

    assert function.source_location.filename == "general/basic_array_update.h"
    assert function.source_location.line >= 1
    assert function.source_location.column >= 1


def test_c_fixture_golden_suite_groups_matching_source_and_header_source_first():
    fixtures = [
        _DATA_DIR / "json" / "cJSON.h",
        _DATA_DIR / "json" / "cJSON.c",
    ]
    project = _parse_project(fixtures)

    assert list(project.files) == ["json/cJSON.c", "json/cJSON.h"]
    assert project.header_source_pairs["json/cJSON.h"] == {"json/cJSON.c"}


def test_c_fixture_golden_suite_groups_dependent_headers_dependency_first():
    project = _parse_project(
        [
            _DATA_DIR / "nanosvg" / "nanosvg.h",
            _DATA_DIR / "nanosvg" / "nanosvgrast.h",
        ]
    )

    assert list(project.files) == ["nanosvg/nanosvg.h", "nanosvg/nanosvgrast.h"]
    assert project.include_graph["nanosvg/nanosvgrast.h"] == {"nanosvg/nanosvg.h"}
