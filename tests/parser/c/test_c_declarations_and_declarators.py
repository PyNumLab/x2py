# -*- coding: utf-8 -*-
"""C declaration-specifier and declarator parser tests."""

import pytest


def test_declaration_specifiers_parse_primitive_signedness_and_widths():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
unsigned long long next_id(void);
signed short clamp_short(signed short value);
_Bool enabled(void);
""",
        filename="primitives.h",
    )

    functions = {fn.name: fn for fn in parsed.functions}
    assert functions["next_id"].return_type.base == "unsigned long long"
    assert functions["clamp_short"].parameters[0].type.base == "signed short"
    assert functions["enabled"].return_type.base == "_Bool"


def test_pointer_qualifiers_are_preserved_in_order():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        "void copy(const double * restrict src, double * restrict dst);\n",
        filename="qualifiers.h",
    )

    params = {param.name: param for param in parsed.functions[0].parameters}
    assert params["src"].type.qualifiers == ["const"]
    assert params["src"].type.pointers[0].qualifiers == ["restrict"]
    assert params["dst"].type.pointers[0].qualifiers == ["restrict"]


def test_array_declarators_preserve_dimensions_and_static_bounds():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        "void solve(size_t n, double a[static 4], const int shape[2]);\n",
        filename="arrays.h",
    )

    params = {param.name: param for param in parsed.functions[0].parameters}
    assert params["a"].type.arrays[0].size == "4"
    assert params["a"].type.arrays[0].static is True
    assert params["shape"].type.arrays[0].size == "2"


def test_multiple_declarators_share_specifiers_but_keep_distinct_types():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        "extern const int *left, right[4];\n",
        filename="globals.h",
    )

    globals_by_name = {glob.name: glob for glob in parsed.globals}
    assert globals_by_name["left"].type.pointers
    assert globals_by_name["right"].type.arrays[0].size == "4"
    assert globals_by_name["right"].type.qualifiers == ["const"]


def test_typedef_declaration_preserves_alias_and_underlying_type_text():
    from c_parser import parse_c_file

    parsed = parse_c_file("typedef unsigned long api_size;\n", filename="typedefs.h")

    typedef = parsed.typedefs[0]
    assert typedef.name == "api_size"
    assert typedef.type.base == "unsigned long"
    assert typedef.type.storage_class == ["typedef"]


@pytest.mark.skip(reason="recursive pointer/array type layers are not implemented yet.")
def test_parenthesized_declarators_distinguish_pointer_arrays_from_array_pointers():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
extern int *values[4];
extern int (*matrix)[4];
""",
        filename="paren_decl.h",
    )

    values = {glob.name: glob for glob in parsed.globals}
    assert values["values"].type.arrays[0].size == "4"
    assert values["values"].type.element_type.pointers
    assert values["matrix"].type.pointers
    assert values["matrix"].type.pointee.arrays[0].size == "4"


@pytest.mark.skip(reason="function pointer declarators are not implemented yet.")
def test_function_pointer_declarator_is_modeled_not_flattened():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        "typedef int (*compare_fn)(const void *a, const void *b);\n",
        filename="callback_typedef.h",
    )

    typedef = parsed.typedefs[0]
    assert typedef.name == "compare_fn"
    assert typedef.type.kind == "function_pointer"
    assert [param.name for param in typedef.type.parameters] == ["a", "b"]


def test_storage_class_and_inline_attributes_are_recorded():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
static inline int local_add(int a, int b) { return a + b; }
extern int exported_add(int a, int b);
""",
        filename="storage.c",
    )

    functions = {fn.name: fn for fn in parsed.functions}
    assert functions["local_add"].storage == ["static"]
    assert "inline" in functions["local_add"].specifiers
    assert functions["exported_add"].storage == ["extern"]
