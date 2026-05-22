# -*- coding: utf-8 -*-
"""C parser public API coverage for the current partial subset."""

from pathlib import Path


def test_parse_c_file_accepts_inline_source_and_returns_typed_model():
    from c_parser import CFile, parse_c_file

    parsed = parse_c_file("int add(int a, int b);\n", filename="inline.h")

    assert isinstance(parsed, CFile)
    assert parsed.filename == "inline.h"
    assert parsed.language == "c"
    assert parsed.parser_status == "partial"
    assert [fn.name for fn in parsed.functions] == ["add"]


def test_parse_c_file_accepts_path_input_and_preserves_filename(tmp_path: Path):
    from c_parser import parse_c_file

    header = tmp_path / "api.h"
    header.write_text("double scale(double x);\n", encoding="utf-8")

    parsed = parse_c_file(header)

    assert parsed.filename == str(header)
    assert [fn.name for fn in parsed.functions] == ["scale"]


def test_parse_c_file_accepts_empty_source_and_unknown_suffix():
    from c_parser import parse_c_file

    parsed = parse_c_file("", filename="empty.src")

    assert parsed.filename == "empty.src"
    assert parsed.functions == []
    assert parsed.diagnostics == []


def test_parse_c_project_accepts_mapping_sources():
    from c_parser import CProject, parse_c_project

    project = parse_c_project(
        {
            "types.h": "typedef int api_int;\n",
            "api.h": '#include "types.h"\napi_int answer(void);\n',
        }
    )

    assert isinstance(project, CProject)
    assert set(project.files) == {"types.h", "api.h"}
    assert project.files["api.h"].language == "c"
    assert set(project.functions) == {"answer"}


def test_parse_c_project_indexes_forward_structs_by_tag_name():
    from c_parser import parse_c_project

    project = parse_c_project(
        {
            "types.h": "struct handle;\n",
            "api.h": "struct handle *open_handle(void);\n",
        }
    )

    assert set(project.structs) == {"handle"}
    assert project.structs["handle"].opaque is True
    assert project.files["types.h"].structs[0].name == "handle"


def test_parse_c_project_accepts_directory_input_with_c_and_h_files(tmp_path: Path):
    from c_parser import parse_c_project

    (tmp_path / "api.h").write_text("int add(int a, int b);\n", encoding="utf-8")
    (tmp_path / "api.c").write_text('#include "api.h"\n', encoding="utf-8")
    (tmp_path / "notes.txt").write_text("ignored\n", encoding="utf-8")

    project = parse_c_project(tmp_path)

    assert set(project.files) == {"api.h", "api.c"}


def test_c_file_serialization_is_json_stable():
    from c_parser import parse_c_file

    parsed = parse_c_file("", filename="empty.c")

    assert parsed.to_dict() == {
        "filename": "empty.c",
        "language": "c",
        "parser_status": "partial",
        "preprocessing": "raw",
        "functions": [],
        "structs": [],
        "unions": [],
        "enums": [],
        "typedefs": [],
        "globals": [],
        "macros": [],
        "includes": [],
        "diagnostics": [],
    }


def test_public_c_parser_entrypoints_do_not_include_parser_side_readiness():
    import c_parser

    assert hasattr(c_parser, "parse_c_file")
    assert hasattr(c_parser, "parse_c_project")
    assert not hasattr(c_parser, "assess_c_wrap_readiness")


def test_c_parse_error_attributes_and_diagnostic_formatting():
    from c_parser import CParseError

    err = CParseError(
        "unexpected token",
        filename="bad.h",
        line_number=2,
        column=5,
        source_line="int broken(;",
    )

    assert err.filename == "bad.h"
    assert err.line_number == 2
    assert err.column == 5
    assert err.base_message == "unexpected token"
    assert err.code == "CPARSE001"

    diagnostic = err.format_diagnostic(color=False, debug=True)
    assert "bad.h:2:5: error[CPARSE001]: unexpected token" in diagnostic
    assert "2 | int broken(;" in diagnostic
    assert "note: parser raised at" in diagnostic


def test_c_parse_error_color_and_no_color_formatting():
    from c_parser import CParseError

    err = CParseError(
        "unexpected token",
        filename="bad.h",
        line_number=2,
        column=5,
        source_line="int broken(;",
    )

    plain = err.format_diagnostic(color=False)
    colored = err.format_diagnostic(color=True)

    assert "\x1b[" not in plain
    assert "\x1b[" in colored
