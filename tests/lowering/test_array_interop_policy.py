"""Tests split by stable ownership concept from `test_handle_policy_dispatch.py`."""

from tests._shared.ownership_policy_support import (
    Scope,
    _semantic_ir_to_codegen_ast,
    complete_semantic_policies,
    parse_pyi_text,
)


def test_lowering_attaches_one_array_interop_policy_for_data_buffer_and_descriptor_lanes():
    module = parse_pyi_text(
        """
def consume_array(values: Float64[:]) -> Float64[:]: ...
def consume_handle(values: Allocatable[Float64[:]]) -> None: ...
""",
        module_name="array_interop_policy_selectors",
    )
    complete_semantic_policies(module)
    lowered = _semantic_ir_to_codegen_ast(module, Scope(name=module.name, scope_type="module"))
    array_function = lowered.funcs[0]
    handle_function = lowered.funcs[1]

    array_argument_policy = array_function.arguments[0].var.array_interop_policy
    array_result_policy = array_function.results.var.array_interop_policy
    handle_argument = handle_function.arguments[0].var
    handle_argument_policy = handle_argument.array_interop_policy

    assert array_argument_policy.abi == "data_buffer"
    assert array_argument_policy.descriptor_kind is None
    assert array_result_policy.abi == "data_buffer"
    assert handle_argument_policy.abi == "descriptor"
    assert handle_argument_policy.descriptor_kind == "allocatable"
    assert handle_argument_policy.handle_kind == "argument_descriptor"
    assert handle_argument.native_array_handle_policy.descriptor_kind == "allocatable"
