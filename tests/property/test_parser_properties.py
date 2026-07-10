"""Property-based parser invariants for small generated source subsets."""

from __future__ import annotations

from contextlib import suppress
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

pytest.importorskip("hypothesis")

from hypothesis import given, strategies as st

import x2py.pipeline.preprocessing as preprocessing
from x2py.c_parser import CParseError, parse_c_file
from x2py.c_parser.lexer import split_top_level_c_source, top_level_split
from x2py.semantics.fortran2ir import fortran_file_to_semantic_modules
from x2py.pipeline.pyi import pyi_text_to_semantic_module as parse_pyi_text
from x2py.codegen.printers.pyi_printer import emit_module_stubs
from x2py import FortranParseError, parse_fortran_file
from x2py.pipeline.preprocessing import PreprocessingConfig, preprocess_source


_FORTRAN_SCALAR_TYPES = st.sampled_from(["integer", "real", "logical"])
_FORTRAN_IDENTIFIER_STEMS = st.from_regex(r"[a-z][a-z0-9_]{0,8}", fullmatch=True)
_C_SCALAR_TYPES = st.sampled_from(["int", "double", "float", "char"])
_C_MODEL_NAMES = {
    "char": "CChar",
    "double": "CDouble",
    "float": "CFloat",
    "int": "CInt",
}
_C_IDENTIFIERS = st.from_regex(r"[a-z][a-z0-9_]{0,8}", fullmatch=True)
_FUZZ_TEXT = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_()[]{}*,;:#=+-/! \t\n'\"",
    max_size=80,
)


@st.composite
def fortran_subroutines(draw):
    proc_name = f"sub_{draw(st.integers(min_value=0, max_value=9999))}"
    arg_ids = draw(st.lists(st.integers(min_value=0, max_value=99), max_size=5, unique=True))
    arg_names = [f"arg_{value}" for value in arg_ids]
    arg_types = draw(st.lists(_FORTRAN_SCALAR_TYPES, min_size=len(arg_names), max_size=len(arg_names)))

    lines = [f"subroutine {proc_name}({', '.join(arg_names)})"]
    lines.extend(
        f"  {type_spec}, intent(in) :: {arg_name}" for type_spec, arg_name in zip(arg_types, arg_names, strict=True)
    )
    lines.append(f"end subroutine {proc_name}")

    return proc_name, arg_names, "\n".join(lines) + "\n"


@st.composite
def c_prototypes(draw):
    function_name = f"fn_{draw(st.integers(min_value=0, max_value=9999))}"
    result_type = draw(_C_SCALAR_TYPES)
    parameter_ids = draw(st.lists(st.integers(min_value=0, max_value=99), max_size=6, unique=True))
    parameter_types = draw(st.lists(_C_SCALAR_TYPES, min_size=len(parameter_ids), max_size=len(parameter_ids)))

    if parameter_ids:
        parameters = [
            f"{type_spec} p_{parameter_id}"
            for type_spec, parameter_id in zip(parameter_types, parameter_ids, strict=True)
        ]
        parameter_names = [f"p_{parameter_id}" for parameter_id in parameter_ids]
    else:
        parameters = ["void"]
        parameter_names = []

    source = f"{result_type} {function_name}({', '.join(parameters)});\n"
    return function_name, parameter_names, source


@st.composite
def c_nested_variable_declarations(draw):
    scalar_type = draw(_C_SCALAR_TYPES)
    bound = draw(st.integers(min_value=1, max_value=99))
    shape = draw(st.sampled_from(["pointer", "array", "array_of_pointers", "pointer_to_array", "callback"]))

    if shape == "pointer":
        source = f"{scalar_type} *value;\n"
        components = ["CPointer", _C_MODEL_NAMES[scalar_type]]
    elif shape == "array":
        source = f"{scalar_type} value[{bound}];\n"
        components = ["CArray", _C_MODEL_NAMES[scalar_type]]
    elif shape == "array_of_pointers":
        source = f"{scalar_type} *value[{bound}];\n"
        components = ["CArray", "CPointer", _C_MODEL_NAMES[scalar_type]]
    elif shape == "pointer_to_array":
        source = f"{scalar_type} (*value)[{bound}];\n"
        components = ["CPointer", "CArray", _C_MODEL_NAMES[scalar_type]]
    else:
        parameter_type = draw(_C_SCALAR_TYPES)
        source = f"{scalar_type} (*value)({parameter_type});\n"
        components = ["CPointer", "CFunctionType"]

    return source, components


@pytest.mark.property
@given(fortran_subroutines())
def test_generated_fortran_subroutines_preserve_argument_order(case):
    proc_name, arg_names, source = case

    parsed = parse_fortran_file(source, filename=f"{proc_name}.f90")

    assert parsed.diagnostics == []
    assert len(parsed.procedures) == 1
    procedure = parsed.procedures[0]
    assert procedure.name == proc_name
    assert [arg.name for arg in procedure.arguments] == arg_names


@pytest.mark.property
@given(fortran_subroutines())
def test_generated_fortran_subroutines_survive_case_changes(case):
    proc_name, arg_names, source = case

    parsed = parse_fortran_file(source.upper(), filename=f"{proc_name}.f90")

    assert parsed.diagnostics == []
    assert len(parsed.procedures) == 1
    procedure = parsed.procedures[0]
    assert procedure.name.lower() == proc_name
    assert [arg.name.lower() for arg in procedure.arguments] == arg_names


@pytest.mark.property
@given(fortran_subroutines())
def test_generated_fortran_subroutines_round_trip_through_pyi(case):
    proc_name, arg_names, source = case

    parsed = parse_fortran_file(source, filename=f"{proc_name}.f90")
    modules = fortran_file_to_semantic_modules(parsed, standalone_module_name="generated")
    stub = emit_module_stubs(modules)["generated"]
    reparsed = parse_pyi_text(stub, module_name="generated")

    assert len(reparsed.functions) == 1
    procedure = reparsed.functions[0]
    assert procedure.name == proc_name
    assert [arg.name for arg in procedure.arguments] == arg_names


@pytest.mark.property
@given(
    module_stem=_FORTRAN_IDENTIFIER_STEMS, procedure_stem=_FORTRAN_IDENTIFIER_STEMS, scalar_type=_FORTRAN_SCALAR_TYPES
)
def test_generated_fortran_modules_preserve_owned_declarations(module_stem, procedure_stem, scalar_type):
    module_name = f"mod_{module_stem}"
    procedure_name = f"proc_{procedure_stem}"
    source = (
        f"module {module_name}\n"
        f"  {scalar_type} :: state\n"
        "contains\n"
        f"  subroutine {procedure_name}(value)\n"
        f"    {scalar_type}, intent(in) :: value\n"
        f"  end subroutine {procedure_name}\n"
        f"end module {module_name}\n"
    )

    parsed = parse_fortran_file(source, filename=f"{module_name}.f90")

    assert parsed.diagnostics == []
    assert len(parsed.modules) == 1
    module = parsed.modules[0]
    assert module.name == module_name
    assert [(variable.name, variable.base_type) for variable in module.variables] == [("state", scalar_type)]
    assert [(procedure.name, procedure.module) for procedure in module.procedures] == [(procedure_name, module_name)]
    assert [(argument.name, argument.base_type) for argument in module.procedures[0].arguments] == [
        ("value", scalar_type)
    ]


@pytest.mark.property
@given(
    module_stem=_FORTRAN_IDENTIFIER_STEMS,
    type_stem=_FORTRAN_IDENTIFIER_STEMS,
    field_types=st.lists(_FORTRAN_SCALAR_TYPES, min_size=1, max_size=5),
)
def test_generated_fortran_derived_types_preserve_fields(module_stem, type_stem, field_types):
    module_name = f"mod_{module_stem}"
    type_name = f"type_{type_stem}"
    fields = [f"field_{index}" for index in range(len(field_types))]
    field_lines = "".join(
        f"    {field_type} :: {field_name}\n" for field_name, field_type in zip(fields, field_types, strict=True)
    )
    source = (
        f"module {module_name}\n  type :: {type_name}\n{field_lines}  end type {type_name}\nend module {module_name}\n"
    )

    parsed = parse_fortran_file(source, filename=f"{module_name}.f90")

    assert parsed.diagnostics == []
    assert len(parsed.modules) == 1
    assert len(parsed.modules[0].derived_types) == 1
    derived_type = parsed.modules[0].derived_types[0]
    assert derived_type.name == type_name
    assert derived_type.module == module_name
    assert [(field.name, field.base_type) for field in derived_type.fields] == list(
        zip(fields, field_types, strict=True)
    )


@pytest.mark.property
@given(base_type=_FORTRAN_SCALAR_TYPES, kind=st.integers(min_value=1, max_value=32), keyword=st.booleans())
def test_generated_fortran_intrinsic_kinds_are_preserved(base_type, kind, keyword):
    type_spec = f"{base_type}({'kind=' if keyword else ''}{kind})"
    source = f"subroutine generated_kind(value)\n  {type_spec}, intent(in) :: value\nend subroutine generated_kind\n"

    parsed = parse_fortran_file(source, filename="generated_kind.f90")

    assert parsed.diagnostics == []
    assert len(parsed.procedures) == 1
    assert parsed.procedures[0].arguments[0].base_type == base_type
    assert parsed.procedures[0].arguments[0].kind == str(kind)


@pytest.mark.property
@given(include_stem=_FORTRAN_IDENTIFIER_STEMS)
def test_generated_fortran_native_includes_do_not_change_public_signature(include_stem):
    target = f"{include_stem}.inc"
    baseline = "subroutine generated_include(value)\n  integer, intent(in) :: value\nend subroutine generated_include\n"
    with_include = (
        f"subroutine generated_include(value)\n"
        f"  include '{target}'\n"
        "  integer, intent(in) :: value\n"
        "end subroutine generated_include\n"
    )

    baseline_parsed = parse_fortran_file(baseline, filename="generated_include.f90")
    included_parsed = parse_fortran_file(with_include, filename="generated_include.f90")

    assert included_parsed.diagnostics == []
    assert included_parsed.procedures == baseline_parsed.procedures


@pytest.mark.property
@given(feature_stem=_FORTRAN_IDENTIFIER_STEMS)
def test_generated_fortran_raw_preprocessor_directives_require_preprocessing(feature_stem):
    feature = f"feature_{feature_stem}"
    source = f"#ifdef {feature}\nsubroutine generated_conditional()\nend subroutine generated_conditional\n#endif\n"

    with pytest.raises(FortranParseError, match="require compiler preprocessing") as exc_info:
        parse_fortran_file(source, filename="generated_conditional.F90")

    assert exc_info.value.code == "PARSE_PREPROCESSING_REQUIRED"


@pytest.mark.property
@given(feature_stem=_FORTRAN_IDENTIFIER_STEMS, select_feature=st.booleans())
def test_generated_fortran_compiler_preprocessing_selects_macro_branch(feature_stem, select_feature):
    feature = f"feature_{feature_stem}"
    with TemporaryDirectory() as tmp_dir:
        source_path = Path(tmp_dir) / "generated_conditional.F90"
        source_path.write_text(
            f"#ifdef {feature}\n"
            "subroutine selected_path()\n"
            "end subroutine selected_path\n"
            "#else\n"
            "subroutine fallback_path()\n"
            "end subroutine fallback_path\n"
            "#endif\n",
            encoding="utf-8",
        )
        captured_argv = []

        def run_compiler(argv, **_kwargs):
            captured_argv.extend(argv)
            selected = f"-D{feature}" in argv
            procedure_name = "selected_path" if selected else "fallback_path"
            stdout = f"subroutine {procedure_name}()\nend subroutine {procedure_name}\n"
            return type("Done", (), {"returncode": 0, "stdout": stdout, "stderr": ""})()

        defines = [feature] if select_feature else []
        with patch.object(preprocessing.subprocess, "run", run_compiler):
            result = preprocess_source(
                source_path,
                language="fortran",
                config=PreprocessingConfig(mode="compiler", compiler=sys.executable, defines=defines),
            )
        parsed = parse_fortran_file(result.source, filename=str(source_path))

    assert "-cpp" in captured_argv
    assert (f"-D{feature}" in captured_argv) is select_feature
    assert result.recipe["defines"] == defines
    assert [procedure.name for procedure in parsed.procedures] == [
        "selected_path" if select_feature else "fallback_path"
    ]


@pytest.mark.property
@given(c_prototypes())
def test_generated_c_prototypes_are_json_stable(case):
    function_name, parameter_names, source = case

    parsed = parse_c_file(source, filename=f"{function_name}.h")
    reparsed = parse_c_file(source, filename=f"{function_name}.h")

    assert parsed.diagnostics == []
    assert len(parsed.functions) == 1
    assert parsed.functions[0].name == function_name
    assert [param.name for param in parsed.functions[0].parameters] == parameter_names
    assert json.loads(json.dumps(parsed.to_dict(), sort_keys=True)) == reparsed.to_dict()


@pytest.mark.property
@given(c_prototypes(), st.sampled_from([" ", "\t", "\n  "]))
def test_generated_c_prototype_whitespace_preserves_signature(case, whitespace):
    function_name, parameter_names, source = case
    variant = source.replace("(", f"{whitespace}(").replace(", ", f",{whitespace}").replace(");", f"){whitespace};")

    parsed = parse_c_file(variant, filename=f"{function_name}.h")

    assert parsed.diagnostics == []
    assert len(parsed.functions) == 1
    assert parsed.functions[0].name == function_name
    assert [param.name for param in parsed.functions[0].parameters] == parameter_names


@pytest.mark.property
@given(c_nested_variable_declarations())
def test_generated_c_nested_declarators_preserve_component_order(case):
    source, expected_components = case

    parsed = parse_c_file(source, filename="nested.h")
    reparsed = parse_c_file(source, filename="nested.h")

    assert parsed.diagnostics == []
    assert len(parsed.variables) == 1
    variable = parsed.variables[0]
    assert variable.name == "value"
    assert type(variable.type).__name__ == "CComposedType"
    assert [type(component).__name__ for component in variable.type.components] == expected_components
    assert parsed.to_dict() == reparsed.to_dict()


@pytest.mark.property
@given(st.lists(_C_IDENTIFIERS, min_size=1, max_size=6, unique=True))
def test_top_level_c_split_ignores_nested_commas_and_literal_commas(names):
    parts = [f'call_{index}({name}, nested({name}, "{name},literal"))' for index, name in enumerate(names)]

    assert top_level_split(", ".join(parts)) == parts


@pytest.mark.property
@given(st.lists(_C_IDENTIFIERS, min_size=1, max_size=6, unique=True))
def test_top_level_c_source_split_ignores_function_body_delimiters(names):
    source = "".join(f'int {name}(void) {{ const char *text = "{{;}}"; return 0; }}\n' for name in names)

    segments = split_top_level_c_source(source, filename="generated.c")

    assert [(segment.text, segment.terminator) for segment in segments] == [
        (f"int {name}(void)", "block") for name in names
    ]


@pytest.mark.property
@given(
    feature=_C_IDENTIFIERS,
    function_names=st.lists(_C_IDENTIFIERS, min_size=2, max_size=2, unique=True),
)
def test_generated_c_raw_conditionals_require_preprocessing(feature, function_names):
    source = f"#ifdef {feature}\nint {function_names[0]}(void);\n#else\nint {function_names[1]}(void);\n#endif\n"

    with pytest.raises(CParseError, match="require compiler preprocessing") as exc_info:
        parse_c_file(source, filename="conditional.h", preprocessing="raw")

    assert exc_info.value.code == "CPARSE_PREPROCESSING_REQUIRED"


@pytest.mark.property
@given(line_number=st.integers(min_value=1, max_value=100_000), stem=_C_IDENTIFIERS)
def test_generated_c_linemarkers_map_function_origin(line_number, stem):
    mapped_filename = f"{stem}.h"
    source = f'#line {line_number} "{mapped_filename}"\nint exported(void);\n'

    parsed = parse_c_file(source, filename="generated.i", preprocessing="preprocessed")

    assert parsed.diagnostics == []
    assert len(parsed.functions) == 1
    assert parsed.functions[0].source_location is not None
    assert parsed.functions[0].source_location.filename == mapped_filename
    assert parsed.functions[0].source_location.line == line_number


@pytest.mark.property
@given(local_stem=_C_IDENTIFIERS, system_stem=_C_IDENTIFIERS)
def test_generated_c_raw_includes_record_local_and_system_targets(local_stem, system_stem):
    local_target = f"hypothesis_missing_{local_stem}.h"
    system_target = f"{system_stem}.h"
    source = f'#include "{local_target}"\n#include <{system_target}>\nint exported(void);\n'

    parsed = parse_c_file(source, filename="generated_api.h", preprocessing="raw")

    assert [(include.target, include.kind) for include in parsed.includes] == [
        (local_target, "local"),
        (system_target, "system"),
    ]
    assert [diagnostic.code for diagnostic in parsed.diagnostics] == ["C_UNRESOLVED_INCLUDE"]


@pytest.mark.property
@given(function_name=_C_IDENTIFIERS)
def test_generated_c_visibility_attributes_are_tolerated(function_name):
    source = f'int {function_name}(void) __attribute__((visibility("default")));\n'

    parsed = parse_c_file(source, filename="compiler.h", preprocessing="compiler")

    assert parsed.diagnostics == []
    assert [function.name for function in parsed.functions] == [function_name]


@pytest.mark.fuzz
@given(_FUZZ_TEXT)
def test_c_parser_fuzz_fragments_only_raise_owned_errors(source):
    with suppress(CParseError):
        parse_c_file(source, filename="fuzz.h")


@pytest.mark.fuzz
@given(_FUZZ_TEXT)
def test_fortran_parser_fuzz_fragments_only_raise_owned_errors(source):
    with suppress(FortranParseError):
        parse_fortran_file(source, filename="fuzz.f90")
