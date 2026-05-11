# -*- coding: utf-8 -*-
import json
from pathlib import Path

import pytest

_FCODE_DIR = Path(__file__).parent / "fcode"
_ALLOWLIST_PATH = _FCODE_DIR / "json_sanity_allowlist.json"


def _is_external_argument(arg: dict) -> bool:
    """Return True for procedure/external arguments where base_type may be unresolved."""
    attrs = {str(a).lower() for a in (arg.get("attributes") or [])}
    return arg.get("base_type") == "procedure" or "external" in attrs


def _has_known_base_type(entry: dict) -> bool:
    return entry.get("base_type") not in (None, "", "unknown")


def _is_valid_rank(entry: dict) -> bool:
    rank = entry.get("rank")
    return isinstance(rank, int) and rank >= 0


def _load_fixture_payload(path: Path):
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return {"signatures": data, "types": []}
    return {"signatures": data.get("signatures", []), "types": data.get("types", [])}


def test_fortran_json_fixtures_are_valid_json():
    for path in _FCODE_DIR.rglob("*.json"):
        if path.name.endswith("_errors.json"):
            continue
        with path.open("r", encoding="utf-8") as f:
            json.load(f)


def test_fortran_json_fixtures_have_sane_types():
    with _ALLOWLIST_PATH.open("r", encoding="utf-8") as f:
        allowlist = {
            (item["file"], item["kind"], item["owner"], item["name"])
            for item in json.load(f)["allowed_unknown_base_types"]
        }

    unknown_entries = []
    invalid_rank_entries = []
    duplicate_argument_entries = []

    for path in _FCODE_DIR.rglob("*.json"):
        if path.name.endswith("_errors.json") or path.name == _ALLOWLIST_PATH.name:
            continue

        payload = _load_fixture_payload(path)
        relpath = str(path.relative_to(_FCODE_DIR))

        for sig in payload["signatures"]:
            arg_names = []
            for arg in sig.get("arguments", []):
                arg_name = arg.get("name")
                arg_names.append(arg_name)

                if not _is_valid_rank(arg):
                    invalid_rank_entries.append((relpath, "argument", sig.get("name"), arg_name, arg.get("rank")))

                if not _has_known_base_type(arg) and not _is_external_argument(arg):
                    unknown_entries.append((relpath, "argument", sig.get("name"), arg.get("name")))

            if len(arg_names) != len(set(arg_names)):
                duplicate_argument_entries.append((relpath, sig.get("name")))

            for var_name, var in sig.get("variables", {}).items():
                if not _is_valid_rank(var):
                    invalid_rank_entries.append((relpath, "variable", sig.get("name"), var_name, var.get("rank")))

                if not _has_known_base_type(var):
                    unknown_entries.append((relpath, "variable", sig.get("name"), var_name))

        for dtype in payload["types"]:
            for field in dtype.get("fields", []):
                if not _is_valid_rank(field):
                    invalid_rank_entries.append((relpath, "field", dtype.get("name"), field.get("name"), field.get("rank")))

                if not _has_known_base_type(field):
                    unknown_entries.append((relpath, "field", dtype.get("name"), field.get("name")))

    unexpected = sorted(e for e in unknown_entries if e not in allowlist)
    stale_allowlist = sorted(e for e in allowlist if e not in set(unknown_entries))

    assert not unexpected, f"Unexpected unknown base_type entries: {unexpected[:20]}"
    assert not stale_allowlist, f"Stale allowlist entries: {stale_allowlist[:20]}"
    assert not invalid_rank_entries, f"Invalid rank entries: {invalid_rank_entries[:20]}"
    assert not duplicate_argument_entries, f"Duplicate argument names in signatures: {duplicate_argument_entries[:20]}"
