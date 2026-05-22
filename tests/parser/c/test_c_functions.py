# -*- coding: utf-8 -*-
"""C function prototype and definition parser tests."""

import pytest


def test_function_prototypes_preserve_return_type_parameter_order_and_names():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        "double dot(size_t n, const double *x, const double *y);\n",
        filename="functions.h",
    )

    fn = parsed.functions[0]
    assert fn.name == "dot"
    assert fn.return_type.base == "double"
    assert [param.name for param in fn.parameters] == ["n", "x", "y"]


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

    fn = parsed.functions[0]
    assert fn.name == "add"
    assert fn.start is not None
    assert fn.end is not None
    assert fn.start.line == 2
    assert fn.end.line == 5


def test_void_parameter_list_and_empty_parameter_list_are_distinguished():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
int explicit_void(void);
int unspecified();
""",
        filename="void_params.h",
    )

    functions = {fn.name: fn for fn in parsed.functions}
    assert functions["explicit_void"].parameters == []
    assert functions["explicit_void"].prototype_style == "prototype"
    assert functions["unspecified"].prototype_style == "unspecified"


def test_variadic_functions_are_parsed_as_source_facts():
    from c_parser import parse_c_file

    parsed = parse_c_file("int log_msg(const char *fmt, ...);\n", filename="variadic.h")

    assert parsed.functions[0].variadic is True


def test_old_style_knr_function_definition_raises_or_records_unsupported_diagnostic():
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


@pytest.mark.skip(reason="function pointer parameters are not implemented yet.")
def test_function_pointer_parameter_is_modeled_as_callback_candidate():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        "void sort_items(void *items, int (*compare)(const void *, const void *));\n",
        filename="callbacks.h",
    )

    compare = parsed.functions[0].parameters[1]
    assert compare.type.kind == "function_pointer"
    assert compare.callback_candidate is True
    assert compare.callback_policy is None


@pytest.mark.skip(reason="function pointer typedef resolution is not implemented yet.")
def test_callback_typedef_parameter_links_to_typedef_signature():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
typedef int (*compare_fn)(const void *a, const void *b);
void sort_items(void *items, compare_fn compare);
""",
        filename="callback_typedef.h",
    )

    fn = parsed.functions[0]
    assert fn.parameters[1].type.typedef_name == "compare_fn"
    assert fn.parameters[1].type.resolved.kind == "function_pointer"


def test_function_returning_pointer_to_const_struct_is_preserved():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
struct state;
const struct state *current_state(void);
""",
        filename="return_pointer.h",
    )

    fn = parsed.functions[0]
    assert fn.return_type.qualifiers == ["const"]
    assert fn.return_type.tag_name == "state"
    assert fn.return_type.pointers
