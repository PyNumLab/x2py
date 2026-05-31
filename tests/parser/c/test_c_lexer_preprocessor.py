# -*- coding: utf-8 -*-
"""C lexer and lightweight preprocessing coverage."""

import pytest


def test_lexer_removes_comments_without_changing_string_or_char_literals():
    from c_parser.lexer import lex_c_source

    tokens = lex_c_source(
        r"""
const char *url = "https://example.invalid/a//b";
char slash = '/';
/* removed block comment */
int value; // removed line comment
""",
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


def test_c_lexer_covers_linemarker_escapes_top_level_strings_and_eof_records():
    from c_parser import parse_c_file
    from c_parser.lexer import (
        CLogicalRecord,
        _unescape_linemarker_filename,
        lex_c_source,
        line_mappings_for_source,
        normalize_c_source,
        split_top_level_c_source,
    )
    from c_parser.preprocessor import _record_location

    assert _unescape_linemarker_filename(r"a\nb\rc\td\\e\"f\x") == 'a\nb\rc\td\\e"fx'
    assert _unescape_linemarker_filename("tail\\") == "tail\\"

    mappings = line_mappings_for_source(
        '#line 7\nint local;\n# 3 "dir\\\\api\\".h"\nint named;\n',
        filename="generated.i",
        use_linemarkers=True,
    )
    assert mappings[1].filename == "generated.i"
    assert mappings[1].line == 7
    assert mappings[3].filename == 'dir\\api".h'
    assert mappings[3].line == 3

    segments = split_top_level_c_source('"literal";\nint unfinished', filename="odd.c")
    assert [(segment.text, segment.terminator) for segment in segments] == [
        ('"literal"', ";"),
        ("int unfinished", "eof"),
    ]

    normalized = normalize_c_source("#define API \\\n", filename="defs.h")
    assert normalized.records[0].text == "#define API"
    assert (
        _record_location(CLogicalRecord(text="#define API", filename="defs.h", original_source_lines=())).source_line
        is None
    )
    assert (
        _record_location(
            CLogicalRecord(text="define API", filename="defs.h", original_source_lines=("define API",))
        ).column
        == 1
    )

    token = lex_c_source(r'char *s = "unterminated\\', filename="bad.c")[-1]
    assert token.kind == "string"
    assert token.text == r'"unterminated\\'

    parsed = parse_c_file(
        '#line 11 "dir\\\\api\\".h"\nstruct __attribute__((annotate("tag\\"ged"))) named { int value; };\n',
        filename="generated.i",
        preprocessing="preprocessed",
    )
    assert parsed.structs[0].name == "named"
    assert parsed.structs[0].source_location.filename == 'dir\\api".h'


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


@pytest.mark.parametrize(
    "directive",
    [
        "#define API_VERSION 3",
        "#undef API_VERSION",
        "#ifdef API_VERSION",
        "#include API_HEADER",
        "#error configure preprocessing",
    ],
)
def test_raw_mode_rejects_directives_that_require_preprocessing(directive):
    from c_parser import CParseError, parse_c_file

    with pytest.raises(CParseError, match="require compiler preprocessing") as exc_info:
        parse_c_file(f"{directive}\nint run(void);\n", filename="raw_macro.h")

    assert exc_info.value.code == "CPARSE_PREPROCESSING_REQUIRED"
    assert exc_info.value.line_number == 1


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


def test_compiler_preprocessed_mode_accepts_line_markers_and_expanded_declarations():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
# 1 "api.h"
int exported(void);
# line 20 "api.h"
double scale(double x);
""",
        filename="api.i",
        preprocessing="preprocessed",
    )

    assert [fn.name for fn in parsed.functions] == ["exported", "scale"]
    assert [fn.origin for fn in parsed.functions] == ["preprocessed", "preprocessed"]
    assert parsed.preprocessed_source_path == "api.i"
    assert parsed.original_source_paths == ["api.h"]
    assert parsed.functions[0].source_location.filename == "api.h"
    assert parsed.functions[0].source_location.line == 1
    assert parsed.functions[1].source_location.line == 20
    payload = parsed.to_dict()
    assert payload["functions"][0]["origin"] == "preprocessed"
    assert payload["preprocessed_source_path"] == "api.i"
    assert payload["original_source_paths"] == ["api.h"]


def test_compiler_preprocessed_mode_maps_gcc_linemarkers_across_includes_and_line_jumps():
    from c_parser import CComposedType, CFunctionType, CPointer, parse_c_file

    parsed = parse_c_file(
        """
# 10 "include/api.h" 1
typedef struct api_state api_state;
# 42 "include/api.h" 2
typedef int (*api_callback)(const char *name, int values[static 4]);
# 90 "generated/detail.h" 1
struct generated_detail {
    int id;
    double (*ops[2])(double);
};
# 120 "include/api.h" 2
int api_register(api_state *state, api_callback cb, int (*factory)(api_state *, const char *));
""",
        filename="api.i",
        preprocessing="compiler",
    )

    assert [typedef.name for typedef in parsed.typedefs] == ["api_state", "api_callback"]
    assert [typedef.origin for typedef in parsed.typedefs] == ["preprocessed", "preprocessed"]
    assert parsed.typedefs[0].source_location.filename == "include/api.h"
    assert parsed.typedefs[0].source_location.line == 10
    assert parsed.typedefs[1].source_location.filename == "include/api.h"
    assert parsed.typedefs[1].source_location.line == 42
    assert isinstance(parsed.typedefs[1].type, CComposedType)
    assert any(isinstance(component, CFunctionType) for component in parsed.typedefs[1].type.components)

    detail = parsed.structs[0]
    assert detail.origin == "preprocessed"
    assert detail.name == "generated_detail"
    assert detail.source_location.filename == "generated/detail.h"
    assert detail.source_location.line == 90
    assert [member.name for member in detail.members] == ["id", "ops"]
    assert [member.origin for member in detail.members] == ["preprocessed", "preprocessed"]
    assert detail.members[1].source_location.filename == "generated/detail.h"
    assert detail.members[1].source_location.line == 92
    assert isinstance(detail.members[1].type, CComposedType)
    assert any(isinstance(component, CPointer) for component in detail.members[1].type.components)

    function = parsed.functions[0]
    assert function.origin == "preprocessed"
    assert function.name == "api_register"
    assert function.source_location.filename == "include/api.h"
    assert function.source_location.line == 120
    assert [parameter.name for parameter in function.parameters] == ["state", "cb", "factory"]
    assert [parameter.origin for parameter in function.parameters] == ["preprocessed"] * 3
    assert parsed.original_source_paths == ["include/api.h", "generated/detail.h"]


def test_compiler_preprocessed_mode_maps_nested_aggregate_members_to_original_file():
    from c_parser import CStruct, parse_c_file

    parsed = parse_c_file(
        """
#line 33 "include/api.h"
struct outer {
    int first;
    struct { int nested; } inner;
};
""",
        filename="api.i",
        preprocessing="preprocessed",
    )

    outer = parsed.structs[0]
    inner = outer.members[1]
    assert isinstance(inner.type, CStruct)
    assert outer.origin == "preprocessed"
    assert inner.origin == "preprocessed"
    assert inner.type.origin == "preprocessed"
    assert inner.type.members[0].origin == "preprocessed"
    assert inner.source_location.filename == "include/api.h"
    assert inner.source_location.line == 35
    assert inner.type.members[0].source_location.filename == "include/api.h"
    assert inner.type.members[0].source_location.line == 35
    assert parsed.diagnostics == []


def test_compiler_preprocessed_mode_maps_fatal_parse_errors_to_original_file():
    from c_parser import CParseError, parse_c_file

    with pytest.raises(CParseError) as exc_info:
        parse_c_file(
            """
# 77 "include/bad_api.h"
unsigned float value;
""",
            filename="bad.i",
            preprocessing="compiler",
        )

    exc = exc_info.value
    assert exc.filename == "include/bad_api.h"
    assert exc.line_number == 77
    assert exc.source_line == "unsigned float value;"
