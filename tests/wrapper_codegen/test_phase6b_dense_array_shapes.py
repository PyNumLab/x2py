"""Declared extents, flat storage, dense rank, and order lowering."""

from __future__ import annotations

import pytest

from tests._shared.ownership_policy_support import parse_pyi_text
from x2py.semantics.policy_completion import complete_semantic_policies
from x2py.wrapper_codegen import WrapperCodeGenerator, WrapperPlanner


def _dense_plan():
    module = parse_pyi_text(
        """
from x2py.contracts import Annotated, Flat, Float64, Int32, ORDER_C, ORDER_F

def dense_f(rows: Int32, cols: Int32, values: Annotated[Float64[rows, cols], ORDER_F]) -> None: ...
def dense_c(rows: Int32, cols: Int32, values: Annotated[Float64[rows, cols], ORDER_C]) -> None: ...
def flat(n: Int32, values: Float64[Flat]) -> None: ...
""",
        module_name="dense_array_shapes",
    )
    complete_semantic_policies(module)
    return WrapperPlanner().build(module)


def test_dense_array_plan_records_extent_dependencies_flat_storage_and_order():
    functions = {function.binding.python_name: function for function in _dense_plan().namespaces[0].functions}
    dense_f = functions["dense_f"].arguments[-1].array
    dense_c = functions["dense_c"].arguments[-1].array
    flat = functions["flat"].arguments[-1].array

    assert dense_f is not None
    assert dense_f.rank == 2
    assert dense_f.shape == ("rows", "cols")
    assert dense_f.order == "ORDER_F"
    assert dense_f.extent_reference_roles == (
        ("dense_array_shapes.dense_f.rows:value",),
        ("dense_array_shapes.dense_f.cols:value",),
    )
    assert dense_c is not None
    assert dense_c.order == "ORDER_C"
    assert flat is not None
    assert flat.rank == 1
    assert flat.shape == (":",)
    assert flat.category == "assumed_size"


def test_dense_array_lowering_uses_planned_shape_checks_and_bridge_orientation():
    artifacts = WrapperCodeGenerator().generate(_dense_plan())
    c_source = next(source.text for source in artifacts.sources if source.path.suffix == ".c")
    bridge_source = next(source.text for source in artifacts.sources if source.path.suffix == ".f90")

    assert "PyArray_DIM((PyArrayObject *)values_obj, 0) != (npy_intp)(rows)" in c_source
    assert "PyArray_DIM((PyArrayObject *)values_obj, 1) != (npy_intp)(cols)" in c_source
    assert "!PyArray_IS_F_CONTIGUOUS((PyArrayObject *)values_obj)" in c_source
    assert "!PyArray_IS_C_CONTIGUOUS((PyArrayObject *)values_obj)" in c_source
    assert "call c_f_pointer(bound_values, values, [values_extent_0, values_extent_1])" in bridge_source
    assert "call c_f_pointer(bound_values, values, [values_extent_1, values_extent_0])" in bridge_source
    assert "subroutine bind_c_flat(n, bound_values, values_extent_0)" in bridge_source


def test_unavailable_dense_extent_role_fails_before_backend_lowering():
    plan = _dense_plan()
    array = plan.namespaces[0].functions[0].arguments[-1].array
    assert array is not None
    array.extent_reference_roles = (("edited.missing:value",), array.extent_reference_roles[1])

    with pytest.raises(ValueError, match="unavailable-array-extent-reference"):
        WrapperCodeGenerator().generate(plan)
