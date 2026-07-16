"""Direct wrapper generation and editable-plan assembly tests."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from tests._shared.ownership_policy_support import parse_pyi_text
from x2py.semantics.ownership import CodegenAction
from x2py.semantics.policy_completion import complete_semantic_policies
from x2py.semantics.wrapper_policy import WritebackPhase
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
    assert "function SWAP_ARGS(y, x) result(native_result)" in fortran_source
    assert "real(c_double) :: native_result" in fortran_source
    assert "result = SWAP_ARGS(y, x)" in fortran_source


@pytest.mark.parametrize(
    ("source", "c_fragment", "fortran_fragment"),
    [
        (
            "def required_value(x: Float64) -> Float64: ...",
            "PyObject * x_obj;",
            "result = native_required_value(x)",
        ),
        (
            "def optional_value(x: Int32 = ...) -> Int32: ...",
            "PyObject * x_obj = Py_None;",
            "if (c_associated(bound_x)) then",
        ),
        (
            """
@native_call([Allocatable(Arg(0))])
def descriptor_value(value: Annotated[Float64, Immutable] | None = ...) -> Int32: ...
""",
            "PyObject * value_obj = NULL;",
            "type(c_ptr), value :: bound_value_present",
        ),
        (
            """
@native_call([Addr(Arg(0)), Return("result", 0)])
def hidden_value(x: Float64) -> Float64: ...
""",
            "void bind_c_hidden_value(double * x, double * result);",
            "subroutine bind_c_hidden_value(x, result)",
        ),
    ],
)
def test_supported_function_actions_select_their_backend_behavior(source, c_fragment, fortran_fragment):
    artifacts = WrapperCodeGenerator().generate(_plan(source, module_name="action_dispatch"))

    assert c_fragment in _rendered_source(artifacts, ".c")
    assert fortran_fragment in _rendered_source(artifacts, ".f90")


@pytest.mark.parametrize(
    "codegen_action",
    (CodegenAction.COPY_IN_OUT, CodegenAction.IN_PLACE_ARGUMENT),
)
def test_supported_writeback_actions_select_scalar_result_behavior(codegen_action):
    plan = _plan(
        'def bump(value: Annotated[Int32, Immutable]) -> Returns["value", Int32]: ...',
        module_name="writeback_dispatch",
    )
    function = plan.namespaces[0].functions[0]
    actions = tuple(
        replace(
            action,
            codegen_action=codegen_action,
            binding=replace(action.binding, codegen_action=codegen_action),
        )
        if action.phase is WritebackPhase.COPY_OUT
        else action
        for action in function.writeback_actions
    )
    root = plan.namespaces[0]
    edited = replace(
        plan,
        namespaces=(replace(root, functions=(replace(function, writeback_actions=actions),)),),
    )

    c_source = _rendered_source(WrapperCodeGenerator().generate(edited), ".c")

    assert "bind_c_bump(&value);" in c_source
    if codegen_action is CodegenAction.COPY_IN_OUT:
        assert "PyObject * result_obj = NULL;" in c_source
        assert "result_obj = Int32_to_PyLong(&value);" in c_source
    else:
        assert "PyObject * result_obj = value_obj;" in c_source
        assert "Py_INCREF(result_obj);" in c_source


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

    with pytest.raises(ValueError, match="Unsupported C argument optional mode"):
        WrapperCodeGenerator().generate(invalid)
