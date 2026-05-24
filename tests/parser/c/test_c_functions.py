# -*- coding: utf-8 -*-
"""C function prototype and definition parser tests."""

import pytest


def test_named_function_exposes_result_type_named_parameters_and_derived_type():
    from c_parser import CDouble, CFunctionType, CTypedef, parse_c_file

    parsed = parse_c_file(
        "double dot(size_t n, const double *x, const double *y);\n",
        filename="functions.h",
    )

    function = parsed.functions[0]
    assert function.name == "dot"
    assert isinstance(function.result_type, CDouble)
    assert [parameter.name for parameter in function.parameters] == ["n", "x", "y"]
    assert isinstance(function.parameters[0].type, CTypedef)
    assert isinstance(function.type, CFunctionType)
    assert function.type.parameter_types == [parameter.type for parameter in function.parameters]


def test_function_definitions_skip_bodies_but_preserve_start_and_end_locations():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
int add(int a, int b)
{
    return a + b;
}
""",
        filename="definitions.c",
    )

    function = parsed.functions[0]
    assert function.name == "add"
    assert function.start is not None
    assert function.end is not None
    assert function.start.line == 2
    assert function.end.line == 5


def test_void_parameter_list_and_empty_parameter_list_are_distinguished():
    from c_parser import parse_c_file

    parsed = parse_c_file("int explicit_void(void);\nint unspecified();\n", filename="void_params.h")

    functions = {function.name: function for function in parsed.functions}
    assert functions["explicit_void"].parameters == []
    assert functions["explicit_void"].prototype_style == "prototype"
    assert functions["unspecified"].prototype_style == "unspecified"


def test_variadic_functions_are_parsed_as_source_facts():
    from c_parser import parse_c_file

    parsed = parse_c_file("int log_msg(const char *fmt, ...);\n", filename="variadic.h")

    assert parsed.functions[0].is_variadic is True
    assert parsed.functions[0].type.is_variadic is True


def test_old_style_knr_function_definition_raises_unsupported_diagnostic():
    from c_parser import CParseError, parse_c_file

    source = """
int add(a, b)
int a;
int b;
{
    return a + b;
}
"""

    with pytest.raises(CParseError, match="K&R"):
        parse_c_file(source, filename="knr.c")


def test_function_pointer_parameter_is_a_callback_candidate_with_nameless_signature():
    from c_parser import CFunctionType, CInt, CPointer, parse_c_file

    parsed = parse_c_file(
        "void sort_items(void *items, int (*compare)(const void *, const void *));\n",
        filename="callbacks.h",
    )

    compare = parsed.functions[0].parameters[1]
    assert compare.callback_candidate is True
    assert compare.callback_policy is None
    assert [type(component) for component in compare.type.components] == [CPointer, CFunctionType]
    signature = compare.type.components[1]
    assert isinstance(signature.result_type, CInt)
    assert len(signature.parameter_types) == 2


def test_function_parameter_preserves_declaration_and_adjusts_to_callback_pointer():
    from c_parser import CComposedType, CFunctionType, CPointer, parse_c_file

    parsed = parse_c_file("void apply(int callback(int));\n", filename="adjusted_callback.h")

    callback = parsed.functions[0].parameters[0]
    assert isinstance(callback.declared_type, CFunctionType)
    assert isinstance(callback.type, CComposedType)
    assert [type(component) for component in callback.type.components] == [CPointer, CFunctionType]
    assert callback.type.components[1] is callback.declared_type
    assert callback.callback_candidate is True
    assert parsed.functions[0].type.parameter_types[0] is callback.type


@pytest.mark.skip(reason="function pointer typedef resolution is not implemented yet.")
def test_callback_typedef_parameter_links_to_typedef_signature():
    from c_parser import CFunctionType, CTypedef, parse_c_file

    parsed = parse_c_file(
        """
typedef int (*compare_fn)(const void *a, const void *b);
void sort_items(void *items, compare_fn compare);
""",
        filename="callback_typedef.h",
    )

    referenced = parsed.functions[0].parameters[1].type
    assert isinstance(referenced, CTypedef)
    assert isinstance(referenced.type.components[1], CFunctionType)


def test_function_returning_pointer_to_const_struct_is_preserved():
    from c_parser import CComposedType, CConst, CPointer, CStruct, parse_c_file

    parsed = parse_c_file(
        "struct state;\nconst struct state *current_state(void);\n",
        filename="return_pointer.h",
    )

    result = parsed.functions[0].result_type
    assert isinstance(result, CComposedType)
    assert isinstance(result.components[0], CPointer)
    assert isinstance(result.components[1], CStruct)
    assert result.components[1].qualifiers == [CConst()]


def test_matching_prototype_and_definition_merge_and_prefer_definition():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
int solve(int value);
int solve(int value)
{
    return value;
}
""",
        filename="redeclarations.c",
    )

    assert [function.name for function in parsed.functions] == ["solve"]
    function = parsed.functions[0]
    assert function.is_definition is True
    assert function.source_location.line == 3
    assert [location.line for location in function.declaration_locations] == [2]
    assert parsed.diagnostics == []


def test_conflicting_function_prototypes_report_diagnostic():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        "int work(int value);\ndouble work(double value);\n",
        filename="conflicting_functions.h",
    )

    assert [function.name for function in parsed.functions] == ["work"]
    assert any(diag.code == "C_CONFLICTING_FUNCTION_DECLARATION" for diag in parsed.diagnostics)


def test_duplicate_function_definitions_report_diagnostic():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
int value(void) { return 1; }
int value(void) { return 2; }
""",
        filename="duplicate_functions.c",
    )

    assert [function.name for function in parsed.functions] == ["value"]
    assert parsed.functions[0].is_definition is True
    assert any(diag.code == "C_DUPLICATE_FUNCTION_DEFINITION" for diag in parsed.diagnostics)
