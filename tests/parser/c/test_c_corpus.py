# -*- coding: utf-8 -*-
"""Planned C parser corpus tests.

cJSON is the first target corpus because it is small, realistic, and exercises
headers, typedef structs, recursive pointers, function declarations, macros,
constants, and callback hook fields without requiring a large build system.
"""

from pathlib import Path

import pytest

pytestmark = pytest.mark.skip(
    reason="C parser corpus roadmap tests; unskip after fixture and corpus workflow exists."
)


_TESTS_DIR = Path(__file__).resolve().parents[2]
_CJSON_DIR = _TESTS_DIR / "data" / "c" / "corpus" / "cjson"


def test_cjson_corpus_files_are_pinned_and_provenanced():
    assert (_CJSON_DIR / "cJSON.h").exists()
    assert (_CJSON_DIR / "cJSON.c").exists()
    assert (_CJSON_DIR / "LICENSE").exists()
    assert (_CJSON_DIR / "SOURCE.md").read_text(encoding="utf-8").strip()


def test_cjson_header_parse_records_public_functions_and_typedefs():
    from c_parser import parse_c_file

    parsed = parse_c_file(_CJSON_DIR / "cJSON.h")

    assert "cJSON_Parse" in {fn.name for fn in parsed.functions}
    assert "cJSON" in {typedef.name for typedef in parsed.typedefs}
    assert "cJSON_bool" in {typedef.name for typedef in parsed.typedefs}


def test_cjson_header_raw_mode_records_public_macro_wrappers():
    from c_parser import parse_c_file

    parsed = parse_c_file(_CJSON_DIR / "cJSON.h", preprocessing="raw")

    assert "CJSON_PUBLIC" in {macro.name for macro in parsed.macros}
    assert any(diag.code == "C_MACRO_DECL_WRAPPER" for diag in parsed.diagnostics)


def test_cjson_header_preprocessed_mode_accepts_compiler_expanded_declarations():
    from c_parser import parse_c_file

    parsed = parse_c_file(_CJSON_DIR / "cJSON.h", preprocessing="compiler")

    assert "cJSON_ParseWithOpts" in {fn.name for fn in parsed.functions}
    assert not any(diag.severity == "error" for diag in parsed.diagnostics)


def test_cjson_callback_hook_fields_are_modeled_with_policy_placeholders():
    from c_parser import parse_c_file

    parsed = parse_c_file(_CJSON_DIR / "cJSON.h")

    assert "cJSON_Hooks" in {struct.name for struct in parsed.structs}
    hooks = next(struct for struct in parsed.structs if struct.name == "cJSON_Hooks")
    callback_members = [member for member in hooks.members if member.callback_candidate]
    assert callback_members
    assert all(member.callback_policy is None for member in callback_members)


def test_cjson_source_file_parse_skips_function_bodies_safely():
    from c_parser import parse_c_file

    parsed = parse_c_file(_CJSON_DIR / "cJSON.c")

    assert any(fn.name == "cJSON_Parse" for fn in parsed.functions)
    assert not any(hasattr(fn, "body") for fn in parsed.functions)


def test_cjson_project_parse_links_header_and_source():
    from c_parser import parse_c_project

    project = parse_c_project(_CJSON_DIR)

    assert "cJSON.h" in project.files
    assert "cJSON.c" in project.files
    assert project.header_source_pairs["cJSON.h"] == {"cJSON.c"}
