"""Typed direct scalar result lowering through the public generator."""

from __future__ import annotations

import pytest

from tests._shared.ownership_policy_support import parse_pyi_text
from x2py.semantics.policy_completion import complete_semantic_policies
from x2py.wrapper_codegen import WrapperCodeGenerator, WrapperPlanner


@pytest.mark.parametrize(
    ("type_name", "converter"),
    [
        ("Bool", "Bool_to_PyBool"),
        ("Int32", "Int32_to_PyLong"),
        ("Float32", "Float_to_NumpyDouble"),
        ("Float64", "Double_to_PyDouble"),
        ("Complex64", "Complex64_to_NumpyComplex"),
        ("Complex128", "Complex128_to_PyComplex"),
    ],
)
def test_direct_scalar_result_registry_projects_supported_type_facts(type_name, converter):
    module = parse_pyi_text(f"def identity(x: {type_name}) -> {type_name}: ...", module_name="scalar_result")
    complete_semantic_policies(module)
    artifacts = WrapperCodeGenerator().generate(WrapperPlanner().build(module))
    c_source = next(source.text for source in artifacts.sources if source.path.suffix == ".c")

    assert f"PyObject * result_obj = {converter}(&result);" in c_source
    assert "return result_obj;" in c_source
