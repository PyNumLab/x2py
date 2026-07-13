"""Phase 4 scalar module-variable planning and lowering tests."""

from __future__ import annotations

from dataclasses import replace

import pytest

from tests._shared.ownership_policy_support import parse_pyi_text
from x2py.semantics.ownership import AssignmentMode, SetterAction
from x2py.semantics.policy_completion import complete_semantic_policies
from x2py.semantics.wrapper_policy import ModuleGetterAction
from x2py.wrapper_codegen import WrapperCodeGenerator, WrapperPlanner
from x2py.wrapper_codegen.c.binding import CBindingGenerator
from x2py.wrapper_codegen.fortran.bridge import FortranBridgeGenerator


SCALAR_MODULE_CONTRACT = """
limit: Final[Int32] = 12
counter: Int32 = 3
target_scale: Annotated[Float64, Aliased]
optional_scale: Allocatable[Float64]
selected_scale: Pointer[Float64]

def summarize() -> Int32: ...
"""


def _plan():
    module = parse_pyi_text(SCALAR_MODULE_CONTRACT, module_name="scalar_state")
    complete_semantic_policies(module)
    return WrapperPlanner().build(module)


def _source(artifacts, suffix: str) -> str:
    return next(item.text for item in artifacts.sources if item.path.name.endswith(suffix))


def test_module_variable_plan_contains_only_completed_dispatch_facts():
    plan = _plan()
    variables = {variable.binding.python_names[0]: variable for variable in plan.namespaces[0].variables}

    assert variables["limit"].binding.getter_action is ModuleGetterAction.CONSTANT_VALUE
    assert variables["limit"].binding.setter_action is SetterAction.OMIT
    assert variables["limit"].bridge.native_assignment is AssignmentMode.NONE
    assert variables["limit"].binding.constant_value == 12
    assert variables["counter"].binding.getter_action is ModuleGetterAction.DIRECT_VALUE
    assert variables["counter"].binding.setter_action is SetterAction.WRITE_THROUGH
    assert variables["counter"].bridge.native_assignment is AssignmentMode.VALUE_COPY
    assert variables["counter"].binding.initializer == 3
    assert variables["optional_scale"].binding.getter_action is ModuleGetterAction.NULLABLE_SNAPSHOT
    assert variables["optional_scale"].bridge.descriptor_kind == "allocatable"
    assert variables["optional_scale"].binding.setter_action is SetterAction.REJECT_REPLACEMENT
    assert variables["selected_scale"].bridge.descriptor_kind == "pointer"


def test_module_variable_lowering_names_are_direct_and_identical_across_backends():
    for generator in (CBindingGenerator, FortranBridgeGenerator):
        assert generator.lowering_method_name("module_getter", ModuleGetterAction.DIRECT_VALUE) == (
            "_lower_module_getter_direct_value"
        )
        assert generator.lowering_method_name("module_getter", ModuleGetterAction.NULLABLE_SNAPSHOT) == (
            "_lower_module_getter_nullable_snapshot"
        )
        assert generator.lowering_method_name("module_setter", SetterAction.WRITE_THROUGH) == (
            "_lower_module_setter_write_through"
        )


def test_module_variable_generators_dispatch_get_set_and_rejection_from_plan():
    artifacts = WrapperCodeGenerator().generate(_plan())
    c_source = _source(artifacts, ".c")
    fortran_source = _source(artifacts, ".f90")

    assert "scalar_state_root_module_property_setup_getattro" in c_source
    assert "scalar_state_root_module_property_setup_setattro" in c_source
    assert 'PyModule_AddObject(mod, "limit"' in c_source
    assert "bind_c_set_counter(3);" in c_source
    assert "return bind_c_get_counter();" not in c_source
    assert "bind_c_get_counter()" in c_source
    assert "bind_c_set_counter(value)" in c_source
    assert "module variable optional_scale is read-only" in c_source
    assert "module variable selected_scale is read-only" in c_source
    assert 'getenv("X2PY_WRAPPER_FAIL_ALLOC")' in c_source
    assert "result = native_counter" in fortran_source
    assert "native_counter = value" in fortran_source
    assert "allocated(native_optional_scale)" in fortran_source
    assert "associated(native_selected_scale)" in fortran_source
    assert "optional_scale = value" not in fortran_source
    assert "selected_scale = value" not in fortran_source


def test_generator_rejects_python_module_setter_without_bridge_handoff():
    plan = _plan()
    counter = next(
        variable for variable in plan.namespaces[0].variables if variable.binding.python_names == ("counter",)
    )
    invalid_counter = replace(counter, bridge=replace(counter.bridge, setter_role=None))
    invalid = replace(
        plan,
        namespaces=(
            replace(
                plan.namespaces[0],
                variables=tuple(
                    invalid_counter if variable is counter else variable for variable in plan.namespaces[0].variables
                ),
            ),
        ),
    )

    with pytest.raises(ValueError, match="missing-module-setter-role"):
        WrapperCodeGenerator().generate(invalid)


def test_generator_rejects_binding_bridge_module_getter_disagreement():
    plan = _plan()
    counter = next(
        variable for variable in plan.namespaces[0].variables if variable.binding.python_names == ("counter",)
    )
    invalid_counter = replace(
        counter,
        bridge=replace(counter.bridge, getter_action=ModuleGetterAction.NULLABLE_SNAPSHOT),
    )
    invalid = replace(
        plan,
        namespaces=(
            replace(
                plan.namespaces[0],
                variables=tuple(
                    invalid_counter if variable is counter else variable for variable in plan.namespaces[0].variables
                ),
            ),
        ),
    )

    with pytest.raises(ValueError, match="inconsistent-module-getter-action"):
        WrapperCodeGenerator().generate(invalid)
