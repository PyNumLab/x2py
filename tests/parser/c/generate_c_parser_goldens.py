# -*- coding: utf-8 -*-
"""Generate/update golden files for grouped C parser fixture projects."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from c_parser import parse_c_project


_TESTS_DIR = Path(__file__).resolve().parents[2]
_C_DATA_DIR = _TESTS_DIR / "data" / "c"
_FIXTURES_DIR = _TESTS_DIR / "parser" / "c" / "fixtures"
_FIXTURE_GROUPS = ("general", "json", "tinyexpr", "linmath", "nanosvg", "stb")
_SOURCE_SUFFIXES = {".c", ".h", ".i"}
_SOURCE_ORDER = {".c": 0, ".h": 1, ".i": 2}
_PROJECT_OVERRIDES = {
    "nanosvg": {
        "nanosvg": ("nanosvg.h", "nanosvgrast.h"),
    },
}


def _parser_filename_for_fixture(fixture: Path) -> str:
    return fixture.relative_to(_C_DATA_DIR).as_posix()


def _fixture_sort_key(fixture: Path) -> tuple[int, str]:
    return (_SOURCE_ORDER.get(fixture.suffix.lower(), 99), fixture.as_posix())


def _project_key(fixture: Path) -> Path:
    relative = fixture.relative_to(_C_DATA_DIR)
    group = relative.parts[0]
    for project_name, filenames in _PROJECT_OVERRIDES.get(group, {}).items():
        if relative.name in filenames:
            return Path(group) / project_name
    return relative.with_suffix("")


def _group_projects(fixtures: list[Path]) -> list[tuple[Path, list[Path]]]:
    grouped: dict[Path, list[Path]] = {}
    for fixture in sorted(fixtures, key=_fixture_sort_key):
        grouped.setdefault(_project_key(fixture), []).append(fixture)
    return [
        (project_key, _ordered_project_fixtures(project_key, project_fixtures))
        for project_key, project_fixtures in sorted(grouped.items())
    ]


def _ordered_project_fixtures(project_key: Path, fixtures: list[Path]) -> list[Path]:
    group = project_key.parts[0]
    override = _PROJECT_OVERRIDES.get(group, {}).get(project_key.name)
    if override is not None:
        order = {filename: index for index, filename in enumerate(override)}
        return sorted(fixtures, key=lambda fixture: order[fixture.name])
    return sorted(fixtures, key=_fixture_sort_key)


def _normalize_resolved_paths(value):
    if isinstance(value, dict):
        resolved_path = value.get("resolved_path")
        if resolved_path:
            try:
                value["resolved_path"] = Path(resolved_path).relative_to(_C_DATA_DIR).as_posix()
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
                return path.relative_to(_C_DATA_DIR).as_posix()
        except ValueError:
            pass
    return value


def _serialize_project(fixtures: list[Path]) -> dict:
    sources = {
        _parser_filename_for_fixture(fixture): fixture.read_text(encoding="utf-8")
        for fixture in sorted(fixtures, key=_fixture_sort_key)
    }
    include_dirs = sorted({fixture.parent for fixture in fixtures})
    parsed = parse_c_project(sources, include_dirs=include_dirs)
    return _normalize_resolved_paths(parsed.to_dict())


def _sibling_fixtures(fixture: Path) -> list[Path]:
    relative = fixture.relative_to(_C_DATA_DIR)
    group = relative.parts[0]
    for filenames in _PROJECT_OVERRIDES.get(group, {}).values():
        if fixture.name in filenames:
            return [fixture.parent / filename for filename in filenames]
    return sorted(
        (
            sibling
            for sibling in fixture.parent.glob(f"{fixture.stem}.*")
            if sibling.is_file() and sibling.suffix.lower() in _SOURCE_SUFFIXES
        ),
        key=_fixture_sort_key,
    )


def _default_projects() -> list[tuple[Path, list[Path]]]:
    fixtures = [
        fixture
        for group in _FIXTURE_GROUPS
        for fixture in (_C_DATA_DIR / group).rglob("*")
        if fixture.is_file() and fixture.suffix.lower() in _SOURCE_SUFFIXES
    ]
    return _group_projects(fixtures)


def _requested_projects(items: list[str]) -> list[tuple[Path, list[Path]]]:
    fixtures: list[Path] = []
    for item in items:
        fixture = Path(item)
        if not fixture.is_absolute():
            fixture = _C_DATA_DIR / fixture
        if fixture.suffix.lower() not in _SOURCE_SUFFIXES:
            raise SystemExit(f"C fixtures must use .c, .h, or .i: {fixture}")
        if not fixture.exists():
            raise SystemExit(f"Fixture does not exist: {fixture}")
        fixtures.extend(_sibling_fixtures(fixture))
    return _group_projects(fixtures)


def _output_path_for_project(project_key: Path) -> Path:
    return (_FIXTURES_DIR / project_key).with_suffix(".json")


def main() -> None:
    requested = sys.argv[1:]
    projects = _requested_projects(requested) if requested else _default_projects()
    if not projects:
        raise SystemExit("No C parser fixtures found")

    failures = []
    for project_key, fixtures in projects:
        try:
            payload = _serialize_project(fixtures)
            out = _output_path_for_project(project_key)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            print(f"updated {out}")
        except Exception as exc:
            failures.append((project_key, exc))

    if failures:
        for project_key, exc in failures:
            print(f"failed {project_key}: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
