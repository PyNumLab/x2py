"""Typed scalar input lowering through the public generator."""

from __future__ import annotations

import pytest

from tests._shared.ownership_policy_support import parse_pyi_text
from x2py.semantics.policy_completion import complete_semantic_policies
from x2py.wrapper_codegen import WrapperCodeGenerator, WrapperPlanner


@pytest.mark.parametrize(
    ("type_name", "c_type", "converter", "check"),
    [
        ("Bool", "bool", "PyBool_to_Bool", "PyArray_IsScalar(x_obj, Bool)"),
        ("Int32", "int32_t", "PyInt32_to_Int32", "PyArray_IsScalar(x_obj, Int)"),
        ("Float32", "float", "PyFloat_to_Float", "PyArray_IsScalar(x_obj, Float)"),
        ("Float64", "double", "PyDouble_to_Double", "PyArray_IsScalar(x_obj, Double)"),
        ("Complex64", "float complex", "PyComplex_to_Complex64", "PyArray_IsScalar(x_obj, CFloat)"),
        ("Complex128", "double complex", "PyComplex_to_Complex128", "PyArray_IsScalar(x_obj, CDouble)"),
    ],
)
def test_scalar_input_registry_lowers_supported_type_facts(type_name, c_type, converter, check):
    module = parse_pyi_text(f"def identity(x: {type_name}) -> {type_name}: ...", module_name="scalar_input")
    complete_semantic_policies(module)
    plan = WrapperPlanner().build(module)

    artifacts = WrapperCodeGenerator().generate(plan)
    c_source = next(source.text for source in artifacts.sources if source.path.suffix == ".c")

    assert f"{c_type} x;" in c_source
    assert f"x = {converter}(x_obj);" in c_source
    assert check in c_source
