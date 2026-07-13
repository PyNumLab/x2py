"""Direct wrapper generation and editable-plan assembly tests."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from tests._shared.ownership_policy_support import parse_pyi_text
from x2py.semantics.ownership import CodegenAction
from x2py.semantics.policy_completion import complete_semantic_policies
from x2py.semantics.wrapper_policy import OptionalMode
from x2py.stage_values import FrozenStageRecordError
from x2py.wrapper_codegen import (
    CBindingGenerator,
    CSourcePrinter,
    FortranBridgeGenerator,
    FortranSourcePrinter,
    WrapperCodeGenerator,
    WrapperPlanner,
)


def _plan(source: str, *, module_name: str):
    module = parse_pyi_text(source, module_name=module_name)
    complete_semantic_policies(module)
    return WrapperPlanner().build(module)


def _rendered_source(artifacts, suffix: str) -> str:
    return next(source.text for source in artifacts.sources if source.path.name.endswith(suffix))


def test_public_generator_directly_returns_complete_rendered_artifacts():
    plan = _plan(
        """
@hold_gil
@bind("SWAP_ARGS")
@external
@native_call([Addr(Arg(1)), Addr(Arg(0))])
def swap_args(x: Float64, y: Float64) -> Float64: ...
""",
        module_name="render_demo",
    )

    artifacts = WrapperCodeGenerator().generate(plan)
    c_source = _rendered_source(artifacts, ".c")
    c_header = _rendered_source(artifacts, ".h")
    fortran_source = _rendered_source(artifacts, ".f90")

    assert artifacts.artifacts.module_name == "render_demo"
    assert artifacts.source_paths == (
        Path("bind_c_render_demo_wrapper.f90"),
        Path("render_demo_wrapper.c"),
        Path("render_demo_wrapper.h"),
    )
    assert artifacts.extension_init_name == "PyInit_render_demo"
    assert "double bind_c_swap_args(double * y, double * x);" in c_source
    assert 'static char * kwlist[] = {"x", "y", NULL};' in c_source
    assert 'PyArg_ParseTupleAndKeywords(args, kwargs, "OO", kwlist, &x_obj, &y_obj)' in c_source
    assert "x = PyDouble_to_Double(x_obj);" in c_source
    assert "result = bind_c_swap_args(&y, &x);" in c_source
    assert "PyObject * result_obj = Double_to_PyDouble(&result);" in c_source
    assert "PyMODINIT_FUNC PyInit_render_demo(void)" in c_source
    assert "static PyObject * wrap_swap_args" in c_header
    assert "module bind_c_render_demo_wrapper" in fortran_source
    assert 'function bind_c_swap_args(y, x) result(result) bind(c, name="bind_c_swap_args")' in fortran_source
    assert "real(c_double), external :: SWAP_ARGS" in fortran_source
    assert "result = SWAP_ARGS(y, x)" in fortran_source


def test_function_lowering_names_are_direct_and_identical_across_backends():
    for generator in (CBindingGenerator, FortranBridgeGenerator):
        assert generator.lowering_method_name("argument", OptionalMode.REQUIRED) == "_lower_argument_required"
        assert (
            generator.lowering_method_name("argument", OptionalMode.NULLABLE_VALUE) == "_lower_argument_nullable_value"
        )
        assert generator.lowering_method_name("argument", OptionalMode.DESCRIPTOR) == "_lower_argument_descriptor"
        assert generator.lowering_method_name("result", CodegenAction.DIRECT_VALUE) == "_lower_result_direct_value"
        assert generator.lowering_method_name("result", CodegenAction.HIDDEN_OUTPUT) == "_lower_result_hidden_output"


def test_direct_plan_edits_change_binding_and_bridge_generation_then_freeze_plan():
    plan = _plan(
        """
@bind("ADD_R8")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1))])
def calculate(x: Float64, y: Float64) -> Float64: ...
""",
        module_name="editable_plan",
    )
    function = plan.namespaces[0].functions[0]
    function.binding.python_name = "subtract"
    function.owner_path = "editable_plan.subtract"
    function.bridge.native_name = "SUB_R8"

    artifacts = WrapperCodeGenerator().generate(plan)

    assert '"subtract", (PyCFunction)wrap_calculate' in _rendered_source(artifacts, ".c")
    assert "result = SUB_R8(x, y)" in _rendered_source(artifacts, ".f90")
    with pytest.raises(FrozenStageRecordError):
        function.bridge.native_name = "ADD_R8"


def test_backend_visitors_return_complete_nodes_and_printers_freeze_them():
    plan = _plan(
        """
@bind("SCALE")
@native_call([Int32(1), Arg(0), Bool(False)])
def scale(x: Float64) -> Float64: ...
""",
        module_name="backend_nodes",
    )
    c_generator = CBindingGenerator()
    fortran_generator = FortranBridgeGenerator()
    c_generator.require_supported(plan)
    fortran_generator.require_supported(plan)

    c_module, c_header = c_generator.visit(plan)
    fortran_module = fortran_generator.visit(plan)

    assert [function.name for function in c_module.functions] == ["wrap_scale", "PyInit_backend_nodes"]
    assert [prototype.name for prototype in c_header.prototypes] == ["wrap_scale"]
    assert [procedure.name for procedure in fortran_module.procedures] == ["bind_c_scale"]
    assert "result = native_scale(1, x, .false.)" in FortranSourcePrinter().doprint(fortran_module)
    CSourcePrinter().doprint(c_module)
    with pytest.raises(FrozenStageRecordError):
        c_module.name = "later"
    with pytest.raises(FrozenStageRecordError):
        fortran_module.name = "later"


def test_generator_rejects_unregistered_typed_lowering_combination():
    plan = _plan(
        """
def scale(x: Float64) -> Float64: ...
""",
        module_name="unsupported_lowering",
    )
    function = plan.namespaces[0].functions[0]
    invalid_argument = replace(
        function.arguments[0],
        binding=replace(function.arguments[0].binding, optional_mode="x"),
        bridge=replace(function.arguments[0].bridge, optional_mode="x"),
    )
    root = plan.namespaces[0]
    invalid = replace(
        plan,
        namespaces=(replace(root, functions=(replace(function, arguments=(invalid_argument,)),)),),
    )

    with pytest.raises(ValueError, match="Unsupported C lowering action"):
        WrapperCodeGenerator().generate(invalid)
