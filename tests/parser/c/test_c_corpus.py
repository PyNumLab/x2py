# -*- coding: utf-8 -*-
"""Active cJSON parser regression tests.

cJSON is the first target corpus because it is small, realistic, and exercises
headers, typedef structs, recursive pointers, function declarations, macros,
constants, and callback hook fields without requiring a large build system.
"""

from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parents[2]
_CJSON_DIR = _TESTS_DIR / "data" / "c" / "json"


def test_cjson_regression_source_and_header_are_available():
    assert (_CJSON_DIR / "cJSON.h").exists()
    assert (_CJSON_DIR / "cJSON.c").exists()


def test_cjson_header_parse_records_unsupported_wrapped_declarations_explicitly():
    from c_parser import parse_c_file

    parsed = parse_c_file(_CJSON_DIR / "cJSON.h")

    assert parsed.parser_status == "partial"
    assert "CJSON_PUBLIC" in {macro.name for macro in parsed.macros}
    assert any(diag.code == "C_UNSUPPORTED_DECLARATOR" for diag in parsed.diagnostics)


def test_cjson_header_raw_mode_records_public_macro_wrappers():
    from c_parser import parse_c_file

    parsed = parse_c_file(_CJSON_DIR / "cJSON.h", preprocessing="raw")

    assert "CJSON_PUBLIC" in {macro.name for macro in parsed.macros}
    assert any(diag.code == "C_UNSUPPORTED_FUNCTION_LIKE_MACRO" for diag in parsed.diagnostics)


def test_cjson_header_preprocessed_mode_preserves_explicit_partial_status():
    from c_parser import parse_c_file

    parsed = parse_c_file(_CJSON_DIR / "cJSON.h", preprocessing="compiler")

    assert parsed.parser_status == "partial"
    assert any(diag.code == "C_UNSUPPORTED_DECLARATOR" for diag in parsed.diagnostics)
    assert not any(diag.severity == "error" for diag in parsed.diagnostics)


def test_cjson_callback_hook_declarations_are_deferred_without_error_diagnostics():
    from c_parser import parse_c_file

    parsed = parse_c_file(_CJSON_DIR / "cJSON.h")

    assert not parsed.structs
    assert any(diag.code == "C_UNSUPPORTED_DECLARATOR" for diag in parsed.diagnostics)
    assert not any(diag.severity == "error" for diag in parsed.diagnostics)


def test_cjson_source_file_parse_skips_function_bodies_safely():
    from c_parser import parse_c_file

    parsed = parse_c_file(_CJSON_DIR / "cJSON.c")

    assert any(fn.name == "parse_number" for fn in parsed.functions)
    assert parsed.parser_status == "partial"
    assert not any(hasattr(fn, "body") for fn in parsed.functions)


def test_cjson_project_parse_links_header_and_source():
    from c_parser import parse_c_project

    project = parse_c_project(_CJSON_DIR)

    assert "cJSON.h" in project.files
    assert "cJSON.c" in project.files
    assert project.header_source_pairs["cJSON.h"] == {"cJSON.c"}
