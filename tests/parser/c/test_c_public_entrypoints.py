# -*- coding: utf-8 -*-
"""Planned public C parser entrypoint tests."""

from pathlib import Path

import pytest

pytestmark = pytest.mark.skip(
    reason="C parser public API roadmap tests; unskip with public API implementation."
)


def test_parse_c_file_accepts_inline_header_source():
    from c_parser import parse_c_file

    parsed = parse_c_file("int add(int a, int b);\n", filename="inline.h")

    assert parsed.filename == "inline.h"
    assert parsed.language == "c"
    assert [fn.name for fn in parsed.functions] == ["add"]


def test_parse_c_file_accepts_path_input_and_preserves_filename(tmp_path: Path):
    from c_parser import parse_c_file

    header = tmp_path / "api.h"
    header.write_text("double scale(double x);\n", encoding="utf-8")

    parsed = parse_c_file(header)

    assert parsed.filename == str(header)
    assert parsed.functions[0].name == "scale"


def test_parse_c_file_accepts_empty_translation_unit():
    from c_parser import parse_c_file

    parsed = parse_c_file("\n/* intentionally empty */\n", filename="empty.c")

    assert parsed.filename == "empty.c"
    assert parsed.functions == []
    assert parsed.diagnostics == []


def test_parse_c_project_accepts_mapping_sources():
    from c_parser import parse_c_project

    project = parse_c_project(
        {
            "types.h": "typedef int api_int;\n",
            "api.h": '#include "types.h"\napi_int answer(void);\n',
        }
    )

    assert "types.h" in project.files
    assert "api.h" in project.files
    assert "answer" in project.functions


def test_parse_c_project_accepts_directory_input(tmp_path: Path):
    from c_parser import parse_c_project

    (tmp_path / "api.h").write_text("int add(int a, int b);\n", encoding="utf-8")
    (tmp_path / "api.c").write_text('#include "api.h"\nint add(int a, int b) { return a + b; }\n', encoding="utf-8")

    project = parse_c_project(tmp_path)

    assert set(project.files) == {"api.h", "api.c"}
    assert "add" in project.functions


def test_c_parser_instance_entrypoints_match_public_functions():
    from c_parser import CParser, parse_c_file, parse_c_project

    source = "int answer(void);\n"
    parser = CParser()

    assert parser.visit_file(source, filename="api.h") == parse_c_file(source, filename="api.h")
    assert parser.visit_project({"api.h": source}) == parse_c_project({"api.h": source})


def test_public_c_parser_entrypoints_do_not_include_parser_side_readiness():
    import c_parser

    assert hasattr(c_parser, "parse_c_file")
    assert hasattr(c_parser, "parse_c_project")
    assert not hasattr(c_parser, "assess_c_wrap_readiness")
