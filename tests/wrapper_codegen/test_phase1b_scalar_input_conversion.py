"""Typed scalar input lowering through the public generator."""

from __future__ import annotations

import pytest

from tests._shared.ownership_policy_support import parse_pyi_text
from x2py.semantics.policy_completion import complete_semantic_policies
from x2py.wrapper_codegen import WrapperCodeGenerator, WrapperPlanner


@pytest.mark.parametrize(
    ("type_name", "c_type", "converter", "check"),
    [
        ("Bool", "bool", "PyBool_to_Bool", "PyIs_Bool(bound_x_obj)"),
        ("Int8", "int8_t", "PyInt8_to_Int8", "PyIs_Int8(bound_x_obj)"),
        ("Int16", "int16_t", "PyInt16_to_Int16", "PyIs_Int16(bound_x_obj)"),
        ("Int32", "int32_t", "PyInt32_to_Int32", "PyArray_IsScalar(bound_x_obj, Int)"),
        ("Int64", "int64_t", "PyInt64_to_Int64", "PyIs_Int64(bound_x_obj)"),
        ("Float32", "float", "PyFloat_to_Float", "PyArray_IsScalar(bound_x_obj, Float)"),
        ("Float64", "double", "PyDouble_to_Double", "PyArray_IsScalar(bound_x_obj, Double)"),
        ("Complex64", "float complex", "PyComplex_to_Complex64", "PyArray_IsScalar(bound_x_obj, CFloat)"),
        ("Complex128", "double complex", "PyComplex_to_Complex128", "PyArray_IsScalar(bound_x_obj, CDouble)"),
    ],
)
def test_scalar_input_registry_lowers_supported_type_facts(type_name, c_type, converter, check):
    module = parse_pyi_text(f"def identity(x: {type_name}) -> {type_name}: ...", module_name="scalar_input")
    complete_semantic_policies(module)
    plan = WrapperPlanner().build(module)

    artifacts = WrapperCodeGenerator().generate(plan)
    c_source = next(source.text for source in artifacts.sources if source.path.suffix == ".c")

    assert f"{c_type} bound_x;" in c_source
    assert f"bound_x = {converter}(bound_x_obj);" in c_source
    assert check in c_source


def test_binding_locals_are_isolated_from_identifiers_imported_by_c_headers():
    module = parse_pyi_text("def identity(complex: Float64) -> Float64: ...", module_name="header_names")
    complete_semantic_policies(module)

    c_source = next(
        source.text
        for source in WrapperCodeGenerator().generate(WrapperPlanner().build(module)).sources
        if source.path.suffix == ".c"
    )

    assert "#include <complex.h>" in c_source
    assert "double bound_complex;" in c_source
    assert "bound_complex = PyDouble_to_Double(bound_complex_obj);" in c_source
    assert "double complex;" not in c_source
