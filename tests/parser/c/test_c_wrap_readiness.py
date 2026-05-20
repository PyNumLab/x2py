# -*- coding: utf-8 -*-
"""Planned C wrap-readiness diagnostics tests."""

import pytest

pytestmark = pytest.mark.skip(
    reason="C parser readiness roadmap tests; unskip with readiness implementation."
)


def test_readiness_accepts_plain_primitive_function_signatures():
    from c_parser import assess_c_wrap_readiness

    report = assess_c_wrap_readiness(
        """
int add(int a, int b);
double scale(double x);
""",
        filename="simple.h",
    )

    assert report["wrappable"] is True
    assert report["blockers"] == []


def test_readiness_reports_unresolved_typedefs():
    from c_parser import assess_c_wrap_readiness

    report = assess_c_wrap_readiness("api_size count(void);\n", filename="unresolved_typedef.h")

    assert report["wrappable"] is False
    assert report["unresolved_typedefs"] == [
        {
            "function": "count",
            "parameter": None,
            "typedef": "api_size",
            "include_candidates": [],
        }
    ]


def test_readiness_reports_macro_dependent_declarations_in_raw_mode():
    from c_parser import assess_c_wrap_readiness

    report = assess_c_wrap_readiness(
        """
#define API(ret) ret
API(int) exported(void);
""",
        filename="macro_dependent.h",
    )

    assert report["wrappable"] is False
    assert any(blocker["code"] == "C_MACRO_DEPENDENT_DECLARATION" for blocker in report["blockers"])


def test_readiness_reports_variadic_functions_as_blockers():
    from c_parser import assess_c_wrap_readiness

    report = assess_c_wrap_readiness("int log_msg(const char *fmt, ...);\n", filename="variadic.h")

    assert report["wrappable"] is False
    assert any(blocker["code"] == "C_VARIADIC_FUNCTION" for blocker in report["blockers"])


def test_readiness_reports_callback_policy_required_for_function_pointer_parameters():
    from c_parser import assess_c_wrap_readiness

    report = assess_c_wrap_readiness(
        "void each_item(void *items, void (*visit)(void *item, void *userdata), void *userdata);\n",
        filename="callback.h",
    )

    assert report["wrappable"] is False
    assert report["callback_policy_required"] == [
        {
            "function": "each_item",
            "parameter": "visit",
            "needs": [
                "signature",
                "direction",
                "lifetime",
                "userdata",
                "nullability",
                "calling_convention",
                "threading",
                "ownership",
                "release_api",
                "exception_policy",
            ],
        }
    ]


def test_readiness_accepts_callback_when_user_pyi_policy_supplies_required_metadata():
    from c_parser import assess_c_wrap_readiness

    source = "void each_item(void *items, void (*visit)(void *item, void *userdata), void *userdata);\n"
    pyi_policy = """
@callback_policy(
    parameter="visit",
    direction="input",
    lifetime="call",
    userdata="userdata",
    nullable=False,
    calling_convention="c",
    threading="sync",
    ownership="borrowed",
    release_api=None,
    exception_policy="translate_to_error"
)
def each_item(items: Pointer[Any], visit: Callable[[Pointer[Any], Pointer[Any]], None], userdata: Pointer[Any]) -> None: ...
"""

    report = assess_c_wrap_readiness(source, filename="callback.h", pyi_policy=pyi_policy)

    assert report["wrappable"] is True
    assert report["callback_policy_required"] == []


def test_readiness_reports_pointer_ownership_ambiguity_for_output_buffers():
    from c_parser import assess_c_wrap_readiness

    report = assess_c_wrap_readiness("int read_values(double *values, size_t n);\n", filename="buffers.h")

    assert report["wrappable"] is False
    assert any(blocker["code"] == "C_POINTER_OWNERSHIP_AMBIGUOUS" for blocker in report["blockers"])


def test_readiness_aggregates_file_level_and_function_level_blockers():
    from c_parser import assess_c_wrap_readiness

    report = assess_c_wrap_readiness(
        """
unknown_t make_unknown(void);
int log_msg(const char *fmt, ...);
""",
        filename="mixed_blockers.h",
    )

    assert report["wrappable"] is False
    assert {blocker["code"] for blocker in report["blockers"]} >= {
        "C_UNRESOLVED_TYPE",
        "C_VARIADIC_FUNCTION",
    }

