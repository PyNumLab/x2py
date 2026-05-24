# -*- coding: utf-8 -*-
"""C lexer and lightweight preprocessing coverage."""

from pathlib import Path

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


def test_top_level_split_helpers_ignore_nested_commas_and_function_bodies():
    from c_parser.lexer import split_top_level_c_source, top_level_split

    assert top_level_split("int (*cmp)(int, int), int value") == [
        "int (*cmp)(int, int)",
        "int value",
    ]

    segments = split_top_level_c_source(
        'int add(int a, int b) { const char *s = "{;}"; return a + b; }\nint next(void);\n',
        filename="split.c",
    )

    assert [(segment.text, segment.terminator) for segment in segments] == [
        ("int add(int a, int b)", "block"),
        ("int next(void)", ";"),
    ]


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


def test_raw_mode_records_undef_directives_as_macro_provenance():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
#define API_FEATURE 1
#undef API_FEATURE
""",
        filename="undefs.h",
        preprocessing="raw",
    )

    assert [(macro.name, macro.directive, macro.value) for macro in parsed.macros] == [
        ("API_FEATURE", "define", "1"),
        ("API_FEATURE", "undef", None),
    ]


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
    assert parsed.functions == []
    assert any(diag.code == "C_UNSUPPORTED_FUNCTION_LIKE_MACRO" for diag in parsed.diagnostics)
    assert any(diag.code == "C_MACRO_DEPENDENT_DECLARATION" for diag in parsed.diagnostics)


def test_raw_mode_fixture_keeps_macro_shaped_declaration_deferred_until_preprocessing():
    from c_parser import parse_c_file

    fixture = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "c"
        / "general"
        / "c_richer_features.h"
    )

    parsed = parse_c_file(fixture)

    function_names = {fn.name for fn in parsed.functions}
    assert "x2py_sort" not in function_names
    assert any(
        diag.code == "C_UNSUPPORTED_FUNCTION_LIKE_MACRO" and diag.unit_name == "X2PY_API"
        for diag in parsed.diagnostics
    )
    assert any(macro.name == "X2PY_API" and macro.directive == "undef" for macro in parsed.macros)


def test_raw_conditional_directives_do_not_select_active_branches():
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

    assert {fn.name for fn in parsed.functions} == {"run_fast", "run_slow"}
    assert [(item.directive, item.argument) for item in parsed.raw_directives] == [
        ("ifdef", "USE_FAST"),
        ("else", None),
        ("endif", None),
    ]


def test_raw_mode_records_pragmas_as_metadata_without_hiding_declarations():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
#pragma once
#pragma GCC diagnostic push
int configured(void);
""",
        filename="pragmas.h",
        preprocessing="raw",
    )

    assert [fn.name for fn in parsed.functions] == ["configured"]
    assert [(item.directive, item.argument) for item in parsed.raw_directives] == [
        ("pragma", "once"),
        ("pragma", "GCC diagnostic push"),
    ]
    assert parsed.raw_directives[0].source_location.line == 2


def test_raw_mode_openmp_declaration_pragmas_do_not_hide_declarations():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
#pragma omp declare simd
int saxpy(int n, const float *x, float *y);

#pragma omp declare target
extern int omp_global;
int omp_helper(void);
#pragma omp end declare target
""",
        filename="openmp_pragmas.h",
        preprocessing="raw",
    )

    assert [fn.name for fn in parsed.functions] == ["saxpy", "omp_helper"]
    assert [variable.name for variable in parsed.variables] == ["omp_global"]
    assert [(item.directive, item.argument) for item in parsed.raw_directives] == [
        ("pragma", "omp declare simd"),
        ("pragma", "omp declare target"),
        ("pragma", "omp end declare target"),
    ]


def test_raw_mode_records_macro_dependency_metadata_for_macro_shaped_declarations():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
#define API_DECL(ret) ret
API_DECL(int) exported(void);
""",
        filename="macro_dependency.h",
        preprocessing="raw",
    )

    assert [(item.name, item.context) for item in parsed.macro_dependencies] == [
        ("API_DECL", "declaration")
    ]
    assert parsed.macro_dependencies[0].source_text == "API_DECL(int) exported(void)"
    assert parsed.macro_dependencies[0].source_location.line == 3
    assert [(diag.code, diag.unit_kind, diag.unit_name) for diag in parsed.diagnostics] == [
        ("C_UNSUPPORTED_FUNCTION_LIKE_MACRO", "macro", "API_DECL"),
        ("C_MACRO_DEPENDENT_DECLARATION", "macro_dependent_declaration", "API_DECL"),
    ]


def test_raw_mode_conditional_macro_directive_is_not_treated_as_knr_function():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
#define ENABLED(value) value
#if ENABLED(API)
typedef int api_value;
#endif
int run(void);
""",
        filename="conditional_macro.h",
        preprocessing="raw",
    )

    assert [function.name for function in parsed.functions] == ["run"]
    assert any(macro.name == "ENABLED" for macro in parsed.macros)


def test_raw_mode_defers_declarations_prefixed_by_object_like_macros():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
#define API_INLINE inline
static API_INLINE void run(void) {}
""",
        filename="object_macro_decl.h",
        preprocessing="raw",
    )

    assert parsed.functions == []
    assert [(item.name, item.context) for item in parsed.macro_dependencies] == [
        ("API_INLINE", "declaration")
    ]
    assert [(diag.code, diag.unit_kind, diag.unit_name) for diag in parsed.diagnostics] == [
        ("C_MACRO_DEPENDENT_DECLARATION", "macro_dependent_declaration", "API_INLINE"),
    ]


def test_raw_mode_macro_initializers_do_not_hide_parseable_declarations():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
#define INIT(value) value
int answer = INIT(42);
""",
        filename="macro_initializer.h",
        preprocessing="raw",
    )

    assert [variable.name for variable in parsed.variables] == ["answer"]
    assert parsed.variables[0].initializer is not None
    assert parsed.variables[0].initializer.source_text == "INIT(42)"
    assert parsed.macro_dependencies == []
    assert [diagnostic.code for diagnostic in parsed.diagnostics] == [
        "C_UNSUPPORTED_FUNCTION_LIKE_MACRO"
    ]


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
