# -*- coding: utf-8 -*-
"""C aggregate type, enum, and typedef parser tests."""


def test_named_struct_members_are_variables_in_source_order():
    from c_parser import CArray, CComposedType, CVariable, parse_c_file

    parsed = parse_c_file(
        "struct point { double x; double y; double coordinates[2]; };\n",
        filename="structs.h",
    )

    point = parsed.structs[0]
    assert [member.name for member in point.members] == ["x", "y", "coordinates"]
    assert all(isinstance(member, CVariable) for member in point.members)
    assert isinstance(point.members[2].type, CComposedType)
    assert isinstance(point.members[2].type.components[0], CArray)
    assert point.members[2].type.components[0].bound == "2"


def test_typedef_struct_alias_refers_to_the_concrete_struct_object():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        "typedef struct point { double x; double y; } point_t;\n",
        filename="typedef_struct.h",
    )

    assert parsed.structs[0].name == "point"
    assert parsed.typedefs[0].name == "point_t"
    assert parsed.typedefs[0].type is parsed.structs[0]


def test_anonymous_struct_typedef_gets_stable_anonymous_id():
    from c_parser import parse_c_file

    parsed = parse_c_file("typedef struct { int code; } result_t;\n", filename="anon_struct.h")

    assert parsed.structs[0].name is None
    assert parsed.structs[0].anonymous_id
    assert parsed.typedefs[0].type is parsed.structs[0]


def test_union_members_are_variables_without_struct_field_class():
    from c_parser import CUnion, CVariable, parse_c_file

    parsed = parse_c_file("union value { int i; double d; };\n", filename="union.h")

    value = parsed.unions[0]
    assert isinstance(value, CUnion)
    assert [member.name for member in value.members] == ["i", "d"]
    assert all(isinstance(member, CVariable) for member in value.members)


def test_anonymous_union_typedef_refers_to_the_concrete_union_object():
    from c_parser import CUnion, parse_c_file

    parsed = parse_c_file("typedef union { int i; double d; } value_t;\n", filename="anon_union.h")

    assert isinstance(parsed.unions[0], CUnion)
    assert parsed.unions[0].anonymous_id
    assert parsed.typedefs[0].type is parsed.unions[0]


def test_incomplete_union_and_tag_typedef_aliases_use_concrete_tag_classes():
    from c_parser import CStruct, CUnion, parse_c_file

    parsed = parse_c_file(
        "struct handle;\nunion payload;\ntypedef struct handle handle_t;\ntypedef union payload payload_t;\n",
        filename="tag_aliases.h",
    )

    assert parsed.structs[0].is_incomplete is True
    assert parsed.unions[0].is_incomplete is True
    typedefs = {typedef.name: typedef for typedef in parsed.typedefs}
    assert isinstance(typedefs["handle_t"].type, CStruct)
    assert typedefs["handle_t"].type.name == "handle"
    assert isinstance(typedefs["payload_t"].type, CUnion)
    assert typedefs["payload_t"].type.name == "payload"


def test_enum_constants_preserve_explicit_implicit_and_symbolic_values():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
enum status {
    STATUS_OK = 0,
    STATUS_WARN,
    STATUS_ERROR = 10,
    STATUS_NEXT = STATUS_ERROR + 1
};
""",
        filename="enum.h",
    )

    assert [(item.name, item.value) for item in parsed.enums[0].constants] == [
        ("STATUS_OK", "0"),
        ("STATUS_WARN", None),
        ("STATUS_ERROR", "10"),
        ("STATUS_NEXT", "STATUS_ERROR + 1"),
    ]


def test_typedef_enum_and_trailing_tag_variable_are_separate_objects():
    from c_parser import CEnum, CStruct, parse_c_file

    parsed = parse_c_file(
        "typedef enum { FLAG_NONE = 0, FLAG_READ = 1 } flag_t;\nstruct point { int x; } origin;\n",
        filename="tag_declarators.h",
    )

    assert parsed.enums[0].anonymous_id
    assert isinstance(parsed.typedefs[0].type, CEnum)
    assert parsed.typedefs[0].type is parsed.enums[0]
    assert parsed.variables[0].name == "origin"
    assert isinstance(parsed.variables[0].type, CStruct)
    assert parsed.variables[0].type is parsed.structs[0]


def test_recursive_struct_pointer_uses_an_incomplete_struct_component_without_cycles():
    from c_parser import CComposedType, CPointer, CStruct, parse_c_file

    parsed = parse_c_file(
        "typedef struct node { int value; struct node *next; } node_t;\n",
        filename="recursive_struct.h",
    )

    node = parsed.structs[0]
    next_type = node.members[1].type
    assert isinstance(next_type, CComposedType)
    assert isinstance(next_type.components[0], CPointer)
    assert isinstance(next_type.components[1], CStruct)
    assert next_type.components[1].name == "node"
    assert next_type.components[1].is_incomplete is True


def test_typedef_chains_preserve_typedef_objects_before_resolution():
    from c_parser import CTypedef, CUnsignedLong, parse_c_file

    parsed = parse_c_file(
        "typedef unsigned long size_type;\ntypedef size_type api_size;\napi_size count(void);\n",
        filename="typedef_chain.h",
    )

    typedefs = {typedef.name: typedef for typedef in parsed.typedefs}
    assert isinstance(typedefs["size_type"].type, CUnsignedLong)
    assert isinstance(typedefs["api_size"].type, CTypedef)
    assert typedefs["api_size"].type.name == "size_type"
    assert isinstance(parsed.functions[0].result_type, CTypedef)


def test_struct_members_use_same_components_for_callbacks_arrays_and_bitfields():
    from c_parser import CArray, CFunctionType, CPointer, parse_c_file

    parsed = parse_c_file(
        "struct hooks { int (*compare)(const void *, const void *); unsigned enabled : 1; int values[4]; };\n",
        filename="members.h",
    )

    compare, enabled, values = parsed.structs[0].members
    assert [type(component) for component in compare.type.components] == [CPointer, CFunctionType]
    assert compare.callback_candidate is True
    assert enabled.bit_width == "1"
    assert isinstance(values.type.components[0], CArray)
    assert values.type.components[0].bound == "4"


def test_nested_aggregate_member_definition_is_diagnosed_explicitly():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        "struct outer { struct { int nested; } inner; int kept; };\n",
        filename="nested_member.h",
    )

    assert [member.name for member in parsed.structs[0].members] == ["kept"]
    assert parsed.diagnostics[0].code == "C_UNSUPPORTED_FIELD_DECLARATION"
    assert parsed.diagnostics[0].unit_kind == "struct_field"
