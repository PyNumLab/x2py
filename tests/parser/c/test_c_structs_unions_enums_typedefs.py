# -*- coding: utf-8 -*-
"""Planned C aggregate type, enum, and typedef parser tests."""

import pytest

pytestmark = pytest.mark.skip(
    reason="C parser type roadmap tests; unskip with struct/union/enum/typedef implementation."
)


def test_named_struct_fields_are_parsed_with_source_order():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
struct point {
    double x;
    double y;
};
""",
        filename="structs.h",
    )

    point = parsed.structs[0]
    assert point.name == "point"
    assert [field.name for field in point.fields] == ["x", "y"]


def test_typedef_struct_alias_links_alias_to_struct_definition():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
typedef struct point {
    double x;
    double y;
} point_t;
""",
        filename="typedef_struct.h",
    )

    assert parsed.structs[0].name == "point"
    assert parsed.typedefs[0].name == "point_t"
    assert parsed.typedefs[0].type.resolved is parsed.structs[0]


def test_anonymous_struct_typedef_gets_stable_anonymous_id():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
typedef struct {
    int code;
} result_t;
""",
        filename="anon_struct.h",
    )

    assert parsed.structs[0].name is None
    assert parsed.structs[0].anonymous_id
    assert parsed.typedefs[0].name == "result_t"


def test_union_fields_are_parsed_without_confusing_struct_tags():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
union value {
    int i;
    double d;
};
""",
        filename="union.h",
    )

    value = parsed.unions[0]
    assert value.name == "value"
    assert [field.name for field in value.fields] == ["i", "d"]


def test_enum_constants_preserve_explicit_and_implicit_values():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
enum status {
    STATUS_OK = 0,
    STATUS_WARN,
    STATUS_ERROR = 10
};
""",
        filename="enum.h",
    )

    enum = parsed.enums[0]
    assert [(item.name, item.value) for item in enum.constants] == [
        ("STATUS_OK", "0"),
        ("STATUS_WARN", None),
        ("STATUS_ERROR", "10"),
    ]


def test_forward_declared_struct_pointer_is_modeled_as_opaque_type():
    from c_parser import assess_c_wrap_readiness, parse_c_file

    parsed = parse_c_file(
        """
struct handle;
struct handle *open_handle(void);
void close_handle(struct handle *handle);
""",
        filename="opaque.h",
    )
    report = assess_c_wrap_readiness(parsed)

    assert parsed.structs[0].name == "handle"
    assert parsed.structs[0].opaque is True
    assert report["wrappable"] is False
    assert any(blocker["code"] == "C_OPAQUE_POLICY_REQUIRED" for blocker in report["blockers"])


def test_recursive_struct_pointer_does_not_recurse_infinitely():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
typedef struct node {
    int value;
    struct node *next;
} node_t;
""",
        filename="recursive_struct.h",
    )

    node = parsed.structs[0]
    assert node.fields[1].type.pointers
    assert node.fields[1].type.tag == "node"


def test_typedef_chains_resolve_to_final_underlying_type():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
typedef unsigned long size_type;
typedef size_type api_size;
api_size count(void);
""",
        filename="typedef_chain.h",
    )

    fn = parsed.functions[0]
    assert fn.return_type.typedef_name == "api_size"
    assert fn.return_type.resolved.base == "unsigned long"

