# -*- coding: utf-8 -*-
"""Active coverage for current C project include/index behavior."""

from pathlib import Path


def test_project_include_graph_tracks_local_system_missing_and_cycles(tmp_path: Path):
    from c_parser import parse_c_project

    (tmp_path / "a.h").write_text('#include "b.h"\n#include "missing.h"\n', encoding="utf-8")
    (tmp_path / "b.h").write_text('#include "a.h"\n#include <stddef.h>\n', encoding="utf-8")

    project = parse_c_project(tmp_path)

    assert project.include_graph["a.h"] == {"b.h", "missing.h"}
    assert project.include_graph["b.h"] == {"a.h"}
    assert project.system_includes["b.h"] == {"stddef.h"}
    assert project.unresolved_includes["a.h"] == {"missing.h"}
    assert any(diag.code == "C_UNRESOLVED_INCLUDE" for diag in project.files["a.h"].diagnostics)


def test_project_resolves_quoted_includes_through_include_dirs(tmp_path: Path):
    from c_parser import parse_c_project

    include_dir = tmp_path / "include"
    src_dir = tmp_path / "src"
    include_dir.mkdir()
    src_dir.mkdir()
    types = include_dir / "types.h"
    api = src_dir / "api.h"
    types.write_text("typedef int api_int;\n", encoding="utf-8")
    api.write_text('#include "types.h"\napi_int answer(void);\n', encoding="utf-8")

    project = parse_c_project([api], include_dirs=[include_dir])

    include = project.files[str(api)].includes[0]
    assert include.target == "types.h"
    assert include.resolved_path == str(types)
    assert project.unresolved_includes[str(api)] == set()


def test_project_records_local_include_without_recursively_parsing_resolved_header(tmp_path: Path):
    from c_parser import parse_c_project

    include_dir = tmp_path / "generated"
    include_dir.mkdir()
    generated = include_dir / "generated_types.h"
    api = tmp_path / "api.h"
    generated.write_text("typedef int generated_int;\n", encoding="utf-8")
    api.write_text('#include "generated_types.h"\nint run(void);\n', encoding="utf-8")

    project = parse_c_project([api], include_dirs=[include_dir])

    assert set(project.files) == {str(api)}
    assert project.files[str(api)].includes[0].resolved_path == str(generated)
    assert project.include_graph[str(api)] == {str(generated)}
    assert "generated_int" not in project.typedefs


def test_project_records_system_include_without_searching_or_parsing_local_copy(tmp_path: Path):
    from c_parser import parse_c_project

    local_system_header = tmp_path / "stddef.h"
    api = tmp_path / "api.h"
    local_system_header.write_text("typedef unsigned long size_t;\n", encoding="utf-8")
    api.write_text("#include <stddef.h>\nint run(void);\n", encoding="utf-8")

    project = parse_c_project([api], include_dirs=[tmp_path])

    assert set(project.files) == {str(api)}
    assert project.files[str(api)].includes[0].resolved_path is None
    assert project.system_includes[str(api)] == {"stddef.h"}
    assert "size_t" not in project.typedefs


def test_parse_c_project_directory_discovers_preprocessed_i_files(tmp_path: Path):
    from c_parser import parse_c_project

    (tmp_path / "api.c").write_text("int from_source(void);\n", encoding="utf-8")
    (tmp_path / "generated.i").write_text(
        '# 8 "include/generated_api.h"\nint generated(void);\n',
        encoding="utf-8",
    )

    project = parse_c_project(tmp_path)

    assert set(project.files) == {"api.c", "generated.i"}
    generated = project.files["generated.i"]
    assert generated.preprocessing == "preprocessed"
    assert generated.preprocessed_source_path == "generated.i"
    assert generated.original_source_paths == ["include/generated_api.h"]
    assert generated.functions[0].origin == "preprocessed"
    assert generated.functions[0].source_location.filename == "include/generated_api.h"
    assert generated.functions[0].source_location.line == 8
    assert generated.to_dict()["functions"][0]["origin"] == "preprocessed"


def test_project_retains_mutually_exclusive_function_variants_out_of_unique_index():
    from c_parser import parse_c_project

    project = parse_c_project(
        {
            "api.h": """
#ifdef API_V2
int configure(int option);
#else
double configure(double option);
#endif
"""
        }
    )

    assert "configure" not in project.functions
    assert [fn.condition_set for fn in project.conditional_function_variants["configure"]] == [
        frozenset({"g1:b0"}),
        frozenset({"g1:b1"}),
    ]
    assert not any(
        diag.code == "C_CONFLICTING_FUNCTION_DECLARATION"
        for diag in project.diagnostics
    )
    payload = project.to_dict()
    assert payload["conditional_function_variants"]["configure"][0]["condition_set"] == ["g1:b0"]


def test_project_indexes_functions_by_file_and_enum_constants(tmp_path: Path):
    from c_parser import parse_c_project

    (tmp_path / "api.h").write_text(
        "enum status { STATUS_OK = 0, STATUS_ERROR = -1 };\n"
        "int run(void);\n"
        "int stop(void);\n",
        encoding="utf-8",
    )

    project = parse_c_project(tmp_path)

    assert project.functions_by_file["api.h"] == ["run", "stop"]
    assert set(project.enum_constants) == {"STATUS_OK", "STATUS_ERROR"}
    assert project.enum_constants["STATUS_OK"].value == "0"


def test_project_indexes_file_scope_variables_and_macros(tmp_path: Path):
    from c_parser import parse_c_project

    (tmp_path / "api.h").write_text(
        "#define API_VERSION 3\n"
        "extern int global_count;\n",
        encoding="utf-8",
    )

    project = parse_c_project(tmp_path)

    assert project.variables["global_count"].storage == ["extern"]
    assert project.macros["API_VERSION"].value == "3"


def test_project_function_index_prefers_definition_over_compatible_prototype(tmp_path: Path):
    from c_parser import parse_c_project

    (tmp_path / "api.h").write_text("int solve(int value);\n", encoding="utf-8")
    (tmp_path / "api.c").write_text("int solve(int value) { return value; }\n", encoding="utf-8")

    project = parse_c_project(tmp_path)

    assert project.functions["solve"].is_definition is True
    assert project.functions["solve"].declaration_locations
    assert not any(diag.code.startswith("C_CONFLICTING") for diag in project.diagnostics)


def test_project_reports_conflicting_function_declarations(tmp_path: Path):
    from c_parser import parse_c_project

    (tmp_path / "a.h").write_text("int work(int value);\n", encoding="utf-8")
    (tmp_path / "b.h").write_text("double work(double value);\n", encoding="utf-8")

    project = parse_c_project(tmp_path)

    assert any(diag.code == "C_CONFLICTING_FUNCTION_DECLARATION" for diag in project.diagnostics)


def test_project_resolves_typedefs_and_struct_tags_across_files(tmp_path: Path):
    from c_parser import CComposedType, CTypedef, parse_c_project

    (tmp_path / "types.h").write_text(
        "typedef unsigned long api_size;\n"
        "struct state { int id; };\n",
        encoding="utf-8",
    )
    (tmp_path / "api.h").write_text(
        '#include "types.h"\n'
        "api_size count(void);\n"
        "void step(struct state *s);\n",
        encoding="utf-8",
    )

    project = parse_c_project(tmp_path)

    assert isinstance(project.functions["count"].result_type, CTypedef)
    assert project.functions["count"].result_type is project.typedefs["api_size"]
    param_type = project.functions["step"].parameters[0].type
    assert isinstance(param_type, CComposedType)
    assert param_type.components[-1] is project.structs["state"]


def test_project_completes_forward_struct_tags_regardless_of_file_order():
    from c_parser import CComposedType, parse_c_project

    project = parse_c_project(
        {
            "forward.h": "struct state;\nvoid step(struct state *s);\n",
            "definition.h": "struct state { int id; };\n",
        }
    )

    assert project.structs["state"].is_incomplete is False
    assert project.structs["state"].members[0].name == "id"
    param_type = project.functions["step"].parameters[0].type
    assert isinstance(param_type, CComposedType)
    assert param_type.components[-1] is project.structs["state"]


def test_project_keeps_complete_union_definition_when_forward_seen_later():
    from c_parser import CComposedType, parse_c_project

    project = parse_c_project(
        {
            "definition.h": "union value { int i; };\n",
            "forward.h": "union value;\nvoid set_value(union value *v);\n",
        }
    )

    assert project.unions["value"].is_incomplete is False
    assert project.unions["value"].members[0].name == "i"
    param_type = project.functions["set_value"].parameters[0].type
    assert isinstance(param_type, CComposedType)
    assert param_type.components[-1] is project.unions["value"]


def test_project_resolves_typedef_chains_while_preserving_alias_objects(tmp_path: Path):
    from c_parser import CTypedef, CUnsignedLong, parse_c_project

    (tmp_path / "types.h").write_text(
        "typedef unsigned long raw_size;\n"
        "typedef raw_size api_size;\n",
        encoding="utf-8",
    )
    (tmp_path / "api.h").write_text("api_size count(void);\n", encoding="utf-8")

    project = parse_c_project(tmp_path)

    assert project.typedefs["api_size"].type is project.typedefs["raw_size"]
    assert isinstance(project.typedefs["raw_size"].type, CUnsignedLong)
    assert isinstance(project.functions["count"].result_type, CTypedef)
    assert project.functions["count"].result_type is project.typedefs["api_size"]
    assert project.functions["count"].result_type.source_text == "api_size"


def test_project_reports_typedef_cycles_without_crashing():
    from c_parser import parse_c_project

    project = parse_c_project({"cycle.h": "typedef b a;\ntypedef a b;\n"})

    assert {diag.code for diag in project.diagnostics} == {"C_TYPEDEF_CYCLE"}


def test_project_resolves_union_and_enum_tag_references(tmp_path: Path):
    from c_parser import CComposedType, parse_c_project

    (tmp_path / "types.h").write_text(
        "union value { int i; };\n"
        "enum status { STATUS_OK = 0 };\n",
        encoding="utf-8",
    )
    (tmp_path / "api.h").write_text(
        "void set_value(union value *v);\n"
        "enum status current_status(void);\n",
        encoding="utf-8",
    )

    project = parse_c_project(tmp_path)

    value_type = project.functions["set_value"].parameters[0].type
    assert isinstance(value_type, CComposedType)
    assert value_type.components[-1] is project.unions["value"]
    assert project.functions["current_status"].result_type is project.enums["status"]


def test_project_resolves_opaque_pointer_typedefs_across_files(tmp_path: Path):
    from c_parser import CComposedType, CTypedef, parse_c_project

    (tmp_path / "types.h").write_text(
        "struct handle;\n"
        "typedef struct handle *handle_t;\n",
        encoding="utf-8",
    )
    (tmp_path / "api.h").write_text("handle_t open_handle(void);\n", encoding="utf-8")

    project = parse_c_project(tmp_path)

    assert project.typedefs["handle_t"].type.components[-1] is project.structs["handle"]
    assert project.structs["handle"].is_incomplete is True
    assert isinstance(project.functions["open_handle"].result_type, CTypedef)
    assert project.functions["open_handle"].result_type is project.typedefs["handle_t"]
    assert isinstance(project.typedefs["handle_t"].type, CComposedType)


def test_project_preserves_unresolved_type_references_for_later_diagnostics():
    from c_parser import CTypedef, parse_c_project

    project = parse_c_project({"api.h": "missing_type value(void);\n"})

    assert isinstance(project.functions["value"].result_type, CTypedef)
    assert project.functions["value"].result_type.name == "missing_type"
    assert project.functions["value"].result_type.type is None


def test_project_header_source_pairs_use_matching_stems_and_direct_includes(tmp_path: Path):
    from c_parser import parse_c_project

    (tmp_path / "solver.h").write_text("int solve(void);\n", encoding="utf-8")
    (tmp_path / "solver.c").write_text('#include "solver.h"\n', encoding="utf-8")
    (tmp_path / "driver.h").write_text("int drive(void);\n", encoding="utf-8")
    (tmp_path / "main.c").write_text('#include "driver.h"\n', encoding="utf-8")

    project = parse_c_project(tmp_path)

    assert project.header_source_pairs["solver.h"] == {"solver.c"}
    assert project.header_source_pairs["driver.h"] == {"main.c"}


def test_project_header_source_pairs_preserve_many_to_many_relationships(tmp_path: Path):
    from c_parser import parse_c_project

    (tmp_path / "a.h").write_text("int a(void);\n", encoding="utf-8")
    (tmp_path / "b.h").write_text("int b(void);\n", encoding="utf-8")
    (tmp_path / "one.c").write_text('#include "a.h"\n#include "b.h"\n', encoding="utf-8")
    (tmp_path / "two.c").write_text('#include "a.h"\n', encoding="utf-8")

    project = parse_c_project(tmp_path)

    assert project.header_source_pairs["a.h"] == {"one.c", "two.c"}
    assert project.header_source_pairs["b.h"] == {"one.c"}


def test_project_serialization_keeps_include_indexes_json_stable(tmp_path: Path):
    from c_parser import parse_c_project

    (tmp_path / "api.h").write_text("#include <stddef.h>\nint run(void);\n", encoding="utf-8")

    payload = parse_c_project(tmp_path).to_dict()

    assert payload["include_graph"] == {"api.h": []}
    assert payload["system_includes"] == {"api.h": ["stddef.h"]}
    assert payload["functions_by_file"] == {"api.h": ["run"]}
