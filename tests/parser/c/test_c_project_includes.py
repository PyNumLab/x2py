# -*- coding: utf-8 -*-
"""Planned C project parsing, include graph, and cross-file resolution tests."""

from pathlib import Path

import pytest

pytestmark = pytest.mark.skip(
    reason="C parser project roadmap tests; unskip with include/project resolution implementation."
)


def test_parse_c_project_accepts_directory_and_discovers_c_h_and_i_files(tmp_path: Path):
    from c_parser import parse_c_project

    (tmp_path / "api.h").write_text("int add(int a, int b);\n", encoding="utf-8")
    (tmp_path / "api.c").write_text('#include "api.h"\nint add(int a, int b) { return a + b; }\n', encoding="utf-8")
    (tmp_path / "generated.i").write_text("int generated(void);\n", encoding="utf-8")

    project = parse_c_project(tmp_path)

    assert set(project.files) == {"api.h", "api.c", "generated.i"}


def test_project_include_graph_tracks_local_and_system_includes(tmp_path: Path):
    from c_parser import parse_c_project

    (tmp_path / "api.h").write_text("#include <stddef.h>\nint run(size_t n);\n", encoding="utf-8")
    (tmp_path / "api.c").write_text('#include "api.h"\n', encoding="utf-8")

    project = parse_c_project(tmp_path)

    assert project.include_graph["api.c"] == {"api.h"}
    assert project.system_includes["api.h"] == {"stddef.h"}


def test_project_resolves_typedefs_across_headers_and_sources(tmp_path: Path):
    from c_parser import parse_c_project

    (tmp_path / "types.h").write_text("typedef unsigned long api_size;\n", encoding="utf-8")
    (tmp_path / "api.h").write_text('#include "types.h"\napi_size count(void);\n', encoding="utf-8")

    project = parse_c_project(tmp_path)

    assert project.functions["count"].result_type.type is project.typedefs["api_size"].type


def test_project_resolves_struct_tags_across_includes(tmp_path: Path):
    from c_parser import parse_c_project

    (tmp_path / "types.h").write_text("struct state { int id; };\n", encoding="utf-8")
    (tmp_path / "api.h").write_text('#include "types.h"\nvoid step(struct state *s);\n', encoding="utf-8")

    project = parse_c_project(tmp_path)

    param_type = project.functions["step"].parameters[0].type
    assert param_type.components[-1] is project.structs["state"]
    assert param_type.components[-1].members[0].name == "id"


def test_include_guards_do_not_duplicate_symbols(tmp_path: Path):
    from c_parser import parse_c_project

    (tmp_path / "types.h").write_text(
        """
#ifndef TYPES_H
#define TYPES_H
typedef int api_int;
#endif
""",
        encoding="utf-8",
    )
    (tmp_path / "a.h").write_text('#include "types.h"\napi_int a(void);\n', encoding="utf-8")
    (tmp_path / "b.h").write_text('#include "types.h"\napi_int b(void);\n', encoding="utf-8")

    project = parse_c_project(tmp_path)

    assert list(project.typedefs).count("api_int") == 1


def test_duplicate_global_function_symbols_report_project_diagnostic(tmp_path: Path):
    from c_parser import CParseError, parse_c_project

    (tmp_path / "a.h").write_text("int work(void);\n", encoding="utf-8")
    (tmp_path / "b.h").write_text("double work(double x);\n", encoding="utf-8")

    with pytest.raises(CParseError, match="Duplicate symbol 'work'"):
        parse_c_project(tmp_path)


def test_header_source_pairing_links_matching_stems(tmp_path: Path):
    from c_parser import parse_c_project

    (tmp_path / "solver.h").write_text("int solve(void);\n", encoding="utf-8")
    (tmp_path / "solver.c").write_text('#include "solver.h"\nint solve(void) { return 0; }\n', encoding="utf-8")

    project = parse_c_project(tmp_path)

    assert project.header_source_pairs["solver.h"] == {"solver.c"}
