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


def test_pointer_array_typedefs_and_typedef_name_references_are_preserved():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
struct state;
typedef const struct state *state_ref;
typedef double vector3[3];
typedef vector3 basis3[3];
state_ref current_state(void);
void set_basis(basis3 basis);
""",
        filename="typedef_layers.h",
    )

    typedefs = {typedef.name: typedef for typedef in parsed.typedefs}
    assert typedefs["state_ref"].type.tag_kind == "struct"
    assert typedefs["state_ref"].type.tag_name == "state"
    assert typedefs["state_ref"].type.pointers
    assert typedefs["vector3"].type.arrays[0].size == "3"
    assert typedefs["basis3"].type.typedef_name == "vector3"
    assert typedefs["basis3"].type.arrays[0].size == "3"
    assert parsed.functions[1].parameters[0].type.typedef_name == "basis3"


def test_globals_with_initializers_multidimensional_arrays_and_tag_refs_parse():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
const struct state *global_state = 0;
volatile union scalar *global_scalar;
const enum status last_status = STATUS_OK;
double matrix[3][4];
int answer = 42;
""",
        filename="globals_richer.h",
    )

    globals_by_name = {glob.name: glob for glob in parsed.globals}
    assert globals_by_name["global_state"].type.tag_kind == "struct"
    assert globals_by_name["global_state"].type.tag_name == "state"
    assert globals_by_name["global_state"].type.pointers
    assert globals_by_name["global_scalar"].type.tag_kind == "union"
    assert globals_by_name["last_status"].type.tag_kind == "enum"
    assert [array.size for array in globals_by_name["matrix"].type.arrays] == ["3", "4"]
    assert globals_by_name["answer"].type.base == "int"


def test_parameters_preserve_struct_union_and_enum_references():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        "void consume(const struct state *s, union scalar *u, enum status status);\n",
        filename="tag_params.h",
    )

    params = {param.name: param for param in parsed.functions[0].parameters}
    assert params["s"].type.tag_kind == "struct"
    assert params["s"].type.tag_name == "state"
    assert params["u"].type.tag_kind == "union"
    assert params["u"].type.tag_name == "scalar"
    assert params["status"].type.tag_kind == "enum"
    assert params["status"].type.tag_name == "status"


def test_forward_struct_declarations_are_recorded_as_opaque_source_facts():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
struct handle;
struct handle *open_handle(void);
void close_handle(struct handle *handle);
""",
        filename="opaque.h",
    )

    assert len(parsed.structs) == 1
    handle = parsed.structs[0]
    assert handle.name == "handle"
    assert handle.opaque is True
    assert handle.fields == []
    assert handle.source_location is not None
    assert handle.source_location.line == 2

    functions = {fn.name: fn for fn in parsed.functions}
    assert functions["open_handle"].return_type.tag_kind == "struct"
    assert functions["open_handle"].return_type.tag_name == "handle"
    assert functions["open_handle"].return_type.pointers
    assert functions["close_handle"].parameters[0].type.tag_name == "handle"


def test_storage_classes_and_qualifiers_are_recorded_for_globals():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
extern int api_errno;
static const double scale_factor = 1.0;
_Thread_local unsigned long tls_counter;
register volatile int scratch;
""",
        filename="storage_globals.h",
    )

    globals_by_name = {glob.name: glob for glob in parsed.globals}
    assert globals_by_name["api_errno"].type.storage_class == ["extern"]
    assert globals_by_name["scale_factor"].type.storage_class == ["static"]
    assert globals_by_name["scale_factor"].type.qualifiers == ["const"]
    assert globals_by_name["tls_counter"].type.storage_class == ["_Thread_local"]
    assert globals_by_name["scratch"].type.storage_class == ["register"]
    assert globals_by_name["scratch"].type.qualifiers == ["volatile"]


def test_function_bodies_do_not_contribute_local_declarations_to_globals():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
int compute(int x)
{
    int local_value = x + 1;
    return local_value;
}
extern int exported_value;
""",
        filename="locals.c",
    )

    assert [global_.name for global_ in parsed.globals] == ["exported_value"]


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
