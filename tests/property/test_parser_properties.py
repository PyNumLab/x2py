# -*- coding: utf-8 -*-
"""Property-based parser invariants for small generated source subsets."""

from __future__ import annotations

import json

import pytest

pytest.importorskip("hypothesis")

from hypothesis import given, strategies as st

from c_parser import CParseError, parse_c_file
from c_parser.lexer import split_top_level_c_source, top_level_split
from semantics.fortran2ir import fortran_file_to_semantic_modules
from semantics.pyi_parser import parse_pyi_text
from semantics.pyi_printer import emit_module_stubs
from x2py import FortranParseError, parse_fortran_file


_FORTRAN_SCALAR_TYPES = st.sampled_from(["integer", "real", "logical"])
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
    assert all(arg.intent == "in" for arg in procedure.arguments)


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


@pytest.mark.fuzz
@given(_FUZZ_TEXT)
def test_c_parser_fuzz_fragments_only_raise_owned_errors(source):
    try:
        parse_c_file(source, filename="fuzz.h")
    except CParseError:
        pass


@pytest.mark.fuzz
@given(_FUZZ_TEXT)
def test_fortran_parser_fuzz_fragments_only_raise_owned_errors(source):
    try:
        parse_fortran_file(source, filename="fuzz.f90")
    except FortranParseError:
        pass
