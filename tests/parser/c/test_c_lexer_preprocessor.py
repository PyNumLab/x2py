# -*- coding: utf-8 -*-
"""C lexer and lightweight preprocessing coverage."""

import pytest


def test_lexer_removes_comments_without_changing_string_or_char_literals():
    from c_parser.lexer import lex_c_source

    tokens = lex_c_source(
        r'''
const char *url = "https://example.invalid/a//b";
char slash = '/';
/* removed block comment */
int value; // removed line comment
''',
        filename="comments.c",
    )

    spellings = [token.text for token in tokens]
    assert '"https://example.invalid/a//b"' in spellings
    assert "'/'" in spellings
    assert "comment" not in spellings


def test_lexer_removes_multiline_block_comments_but_preserves_following_line_numbers():
    from c_parser.lexer import lex_c_source

    tokens = lex_c_source(
        "int first;\n/* removed\n   block */\nint second;\n",
        filename="block_comments.c",
    )

    identifiers = [token for token in tokens if token.kind == "identifier"]
    assert [token.text for token in identifiers] == ["int", "first", "int", "second"]
    assert identifiers[-2].line == 4
    assert identifiers[-1].column == 5


def test_line_continuations_preserve_original_line_numbers():
    from c_parser.preprocessor import normalize_c_source

    normalized = normalize_c_source(
        "#define SUM(a, b) \\\n  ((a) + (b))\nint x;\n",
        filename="continuations.h",
    )

    assert normalized.records[0].original_start_line == 1
    assert normalized.records[0].original_end_line == 2
    assert normalized.records[1].original_start_line == 3


def test_raw_mode_records_includes_without_expanding_them():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        '#include "api_types.h"\n#include <stddef.h>\nint run(void);\n',
        filename="includes.h",
        preprocessing="raw",
    )

    assert [include.target for include in parsed.includes] == ["api_types.h", "stddef.h"]
    assert [include.kind for include in parsed.includes] == ["local", "system"]


def test_raw_mode_resolves_local_includes_relative_to_path_input(tmp_path):
    from c_parser import parse_c_file

    header = tmp_path / "api.h"
    types = tmp_path / "api_types.h"
    header.write_text('#include "api_types.h"\n', encoding="utf-8")
    types.write_text("typedef int api_int;\n", encoding="utf-8")

    parsed = parse_c_file(header)

    assert parsed.includes[0].resolved_path == str(types)
    assert parsed.diagnostics == []


def test_raw_mode_records_simple_object_like_macros_as_constants():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
#define API_VERSION 3
#define API_NAME "demo"
int version(void);
""",
        filename="macros.h",
        preprocessing="raw",
    )

    macros = {macro.name: macro for macro in parsed.macros}
    assert macros["API_VERSION"].value == "3"
    assert macros["API_NAME"].value == '"demo"'
    assert macros["API_VERSION"].function_like is False


def test_raw_mode_marks_function_like_macros_as_unsupported_until_expanded():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
#define API_DECL(ret) ret
API_DECL(int) exported(void);
""",
        filename="macro_decl.h",
        preprocessing="raw",
    )

    macros = {macro.name: macro for macro in parsed.macros}
    assert macros["API_DECL"].function_like is True
    assert any(diag.code == "C_UNSUPPORTED_FUNCTION_LIKE_MACRO" for diag in parsed.diagnostics)


@pytest.mark.skip(reason="compiler-preprocessed mode lands after raw metadata collection.")
def test_compiler_preprocessed_mode_accepts_line_markers_and_expanded_declarations():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
# 1 "api.h"
int exported(void);
# 20 "api.h"
double scale(double x);
""",
        filename="api.i",
        preprocessing="preprocessed",
    )

    assert [fn.name for fn in parsed.functions] == ["exported", "scale"]
    assert parsed.functions[1].source_location.line == 20


@pytest.mark.skip(reason="conditional branch tracking lands after raw include/macro metadata.")
def test_conditional_compilation_regions_are_tracked_in_raw_mode():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
#ifdef USE_FAST
int run_fast(void);
#else
int run_slow(void);
#endif
""",
        filename="conditional.h",
        preprocessing="raw",
    )

    assert len(parsed.conditional_regions) == 1
    assert {fn.name for fn in parsed.functions} == {"run_fast", "run_slow"}
