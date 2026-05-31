# -*- coding: utf-8 -*-
"""C semantic wrap-readiness tests.

These tests intentionally live under ``tests/semantics`` because readiness is
owned by semantic IR or edited ``.pyi`` interfaces, not by the C parser.
"""


def test_c_semantic_readiness_accepts_plain_primitive_function_signatures():
    from c_parser import parse_c_file
    from semantics.c2ir import c_file_to_semantic_modules
    from semantics.readiness import assess_semantic_wrap_readiness

    parsed = parse_c_file(
        """
int add(int a, int b);
double scale(double x);
""",
        filename="simple.h",
    )
    modules = c_file_to_semantic_modules(parsed)
    report = assess_semantic_wrap_readiness(modules, source="simple.h")

    assert report["wrappable"] is True
    assert report["wrappability_blockers"] == []


def test_c_semantic_readiness_reports_unresolved_typedefs():
    from c_parser import parse_c_file
    from semantics.c2ir import c_file_to_semantic_modules
    from semantics.readiness import assess_semantic_wrap_readiness

    parsed = parse_c_file("api_size count(void);\n", filename="unresolved_typedef.h")
    modules = c_file_to_semantic_modules(parsed)
    report = assess_semantic_wrap_readiness(modules, source="unresolved_typedef.h")

    assert report["wrappable"] is False
    assert any(blocker["code"] == "unresolved_semantic_types" for blocker in report["wrappability_blockers"])


def test_c_semantic_readiness_reports_variadic_functions_as_blockers():
    from c_parser import parse_c_file
    from semantics.c2ir import c_file_to_semantic_modules
    from semantics.readiness import assess_semantic_wrap_readiness

    parsed = parse_c_file("int log_msg(const char *fmt, ...);\n", filename="variadic.h")
    modules = c_file_to_semantic_modules(parsed)
    report = assess_semantic_wrap_readiness(modules, source="variadic.h")

    assert report["wrappable"] is False
    assert any(blocker["code"] == "c_variadic_function" for blocker in report["wrappability_blockers"])


def test_c_semantic_readiness_reports_callback_policy_required():
    from c_parser import parse_c_file
    from semantics.c2ir import c_file_to_semantic_modules
    from semantics.readiness import assess_semantic_wrap_readiness

    parsed = parse_c_file(
        "void each_item(void *items, void (*visit)(void *item, void *userdata), void *userdata);\n",
        filename="callback.h",
    )
    modules = c_file_to_semantic_modules(parsed)
    report = assess_semantic_wrap_readiness(modules, source="callback.h")

    assert report["wrappable"] is False
    assert any(blocker["code"] == "callback_signature_incomplete" for blocker in report["wrappability_blockers"])


def test_completed_pyi_callback_policy_can_make_c_api_semantically_ready():
    from semantics.pyi_parser import parse_pyi_text
    from semantics.readiness import assess_semantic_wrap_readiness

    module = parse_pyi_text(
        """
from typing import Any, Callable

def each_item(
    items: Ptr(Any),
    visit: Callable[[Ptr(Any), Ptr(Any)], None],
    userdata: Ptr(Any),
) -> None: ...
""",
        module_name="callback_api",
    )

    report = assess_semantic_wrap_readiness(module, source="callback_api.pyi")

    assert report["wrappable"] is True
    assert report["wrappability_blockers"] == []


def test_c_semantic_readiness_reports_pointer_ownership_ambiguity():
    from c_parser import parse_c_file
    from semantics.c2ir import c_file_to_semantic_modules
    from semantics.readiness import assess_semantic_wrap_readiness

    parsed = parse_c_file("int read_values(double *values, size_t n);\n", filename="buffers.h")
    modules = c_file_to_semantic_modules(parsed)
    report = assess_semantic_wrap_readiness(modules, source="buffers.h")

    assert report["wrappable"] is False
    assert any(blocker["code"] == "c_pointer_ownership_ambiguous" for blocker in report["wrappability_blockers"])


def test_c_semantic_readiness_aggregates_file_and_function_blockers():
    from c_parser import parse_c_file
    from semantics.c2ir import c_file_to_semantic_modules
    from semantics.readiness import assess_semantic_wrap_readiness

    parsed = parse_c_file(
        """
unknown_t make_unknown(void);
int log_msg(const char *fmt, ...);
""",
        filename="mixed_blockers.h",
    )
    modules = c_file_to_semantic_modules(parsed)
    report = assess_semantic_wrap_readiness(modules, source="mixed_blockers.h")

    assert report["wrappable"] is False
    assert {blocker["code"] for blocker in report["wrappability_blockers"]} >= {
        "unresolved_semantic_types",
        "c_variadic_function",
    }
