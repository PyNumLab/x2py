"""Unified naming-policy tests."""

import pytest

from x2py.naming import NamingPolicy
from x2py.naming import normalize_public_name


def test_public_python_names_escape_keywords_and_collisions():
    policy = NamingPolicy()

    assert normalize_public_name("def").name == "def_"
    assert policy.reserve_public_name(("mod",), "def", category="function") == "def_"
    assert policy.reserve_public_name(("mod",), "def_", category="function") == "def__2"


def test_strict_public_names_reject_keyword_escaping():
    policy = NamingPolicy(strict_public_names=True)

    with pytest.raises(ValueError, match="strict wrapper naming"):
        policy.reserve_public_name(("mod",), "def", category="function")


def test_generated_symbols_apply_target_language_rules():
    policy = NamingPolicy()

    assert (
        policy.generated_symbol(
            "module",
            set(),
            language="fortran",
            prefix="owner__",
            context="function",
            parent_context="module",
        )
        == "module_0001"
    )
    assert (
        policy.generated_symbol(
            "return",
            set(),
            language="c",
            prefix="owner__",
            context="function",
            parent_context="module",
        )
        == "owner__return"
    )
    assert (
        policy.generated_symbol(
            "value",
            {"Value"},
            language="fortran",
            prefix="owner__",
            context="variable",
            parent_context="function",
        )
        == "value_0001"
    )
