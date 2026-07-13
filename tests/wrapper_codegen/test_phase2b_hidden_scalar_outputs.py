"""Hidden scalar output lowering through the public generator."""

from __future__ import annotations

from tests._shared.ownership_policy_support import parse_pyi_text
from x2py.semantics.policy_completion import complete_semantic_policies
from x2py.wrapper_codegen import WrapperCodeGenerator, WrapperPlanner


def test_hidden_scalar_result_is_one_bridge_output_and_one_python_result():
    module = parse_pyi_text(
        """
@bind("SCALE_OUT")
@external
@native_call([Addr(Arg(0)), Return("result", 0)])
def scale(x: Float64) -> Float64: ...
""",
        module_name="hidden_result",
    )
    complete_semantic_policies(module)
    plan = WrapperPlanner().build(module)
    function = plan.namespaces[0].functions[0]
    result = function.results[0]

    assert result.native_call_slot is function.native_call_slots[result.bridge.abi_position]

    artifacts = WrapperCodeGenerator().generate(plan)
    c_source = next(source.text for source in artifacts.sources if source.path.suffix == ".c")
    fortran_source = next(source.text for source in artifacts.sources if source.path.suffix == ".f90")

    assert "void bind_c_scale(double * x, double * result);" in c_source
    assert "bind_c_scale(&x, &result);" in c_source
    assert "PyObject * result_obj = Double_to_PyDouble(&result);" in c_source
    assert 'subroutine bind_c_scale(x, result) bind(c, name="bind_c_scale")' in fortran_source
    assert "call SCALE_OUT(x, result)" in fortran_source
