"""Optional, assumed-rank, and fixed-width character array lowering."""

from __future__ import annotations

import pytest

from tests._shared.ownership_policy_support import parse_pyi_text
from x2py.semantics.ownership import CodegenAction, NativeBarrierAction, ObjectKind
from x2py.semantics.policy_completion import complete_semantic_policies
from x2py.semantics.wrapper_policy import BridgeDataAction, OptionalMode
from x2py.wrapper_codegen import WrapperCodeGenerator, WrapperPlanner
from x2py.wrapper_codegen.plan import DatatypeFamily


def _later_array_plan():
    module = parse_pyi_text(
        """
from x2py.contracts import Float64, String

def optional(values: Float64[:] = ...) -> None: ...
def any_rank(values: Float64[...]) -> Float64: ...
def labels(values: String[8][:]) -> None: ...
""",
        module_name="later_array_buffers",
    )
    complete_semantic_policies(module)
    return WrapperPlanner().build(module)


def _character_array_result_plan():
    module = parse_pyi_text(
        """
def direct_labels() -> String[5][3]: ...

@native_call([Return("labels", 0)])
def hidden_labels() -> String[4][2]: ...
""",
        module_name="character_array_results",
    )
    complete_semantic_policies(module)
    return WrapperPlanner().build(module)


def test_optional_assumed_rank_and_character_arrays_have_explicit_distinct_roles():
    functions = {function.binding.python_name: function for function in _later_array_plan().namespaces[0].functions}
    optional = functions["optional"].arguments[0]
    assumed = functions["any_rank"].arguments[0].array
    character = functions["labels"].arguments[0].array

    assert optional.binding.optional_mode is OptionalMode.NULLABLE_VALUE
    assert optional.bridge.optional_mode is OptionalMode.NULLABLE_VALUE
    assert assumed is not None
    assert assumed.rank is None
    assert assumed.contiguous is True
    assert assumed.runtime_rank_role == "later_array_buffers.any_rank.values:rank"
    assert len(assumed.extent_roles) == 15
    assert character is not None
    assert character.rank == 1
    assert character.itemsize == 8
    assert character.itemsize_role == "later_array_buffers.labels.values:itemsize"


def test_optional_assumed_rank_and_character_lowering_follow_named_plan_fields():
    artifacts = WrapperCodeGenerator().generate(_later_array_plan())
    c_source = next(source.text for source in artifacts.sources if source.path.suffix == ".c")
    bridge_source = next(source.text for source in artifacts.sources if source.path.suffix == ".f90")

    assert "PyObject * bound_values_obj = Py_None;" in c_source
    assert "if (bound_values_obj != Py_None)" in c_source
    assert "PyArray_NDIM((PyArrayObject *)bound_values_obj) < 1" in c_source
    assert "bound_values_rank = (int64_t)PyArray_NDIM" in c_source
    assert "PyArray_TYPE((PyArrayObject *)bound_values_obj) != NPY_STRING" in c_source
    assert "bound_values_itemsize != 8" in c_source
    assert "if (c_associated(bound_values)) then" in bridge_source
    assert "select case (values_rank)" in bridge_source
    assert "case (1)" in bridge_source
    assert "case (15)" in bridge_source
    assert "character(kind=c_char, len=8), pointer, dimension(:) :: values" in bridge_source
    assert max(map(len, bridge_source.splitlines())) <= 132


def test_character_itemsize_edit_fails_before_backend_lowering():
    plan = _later_array_plan()
    character = plan.namespaces[0].functions[2].arguments[0].array
    assert character is not None
    character.itemsize_role = None

    with pytest.raises(ValueError, match="invalid-array-itemsize"):
        WrapperCodeGenerator().generate(plan)


def test_fixed_width_character_array_results_reuse_the_ordinary_array_copy_plan():
    direct_function, hidden_function = _character_array_result_plan().namespaces[0].functions
    direct = direct_function.results[0]
    hidden = hidden_function.results[0]

    for result, itemsize in ((direct, 5), (hidden, 4)):
        assert result.object_kind is ObjectKind.NUMPY_ARRAY
        assert result.datatype_family is DatatypeFamily.STRING
        assert result.array is not None
        assert result.array.itemsize == itemsize
        assert result.character_length == itemsize
        assert result.binding.codegen_action is CodegenAction.COPY_OUT
        assert result.bridge.data_action is BridgeDataAction.COPY_REPRESENTATION
    assert direct.bridge.native_action is NativeBarrierAction.NONE
    assert hidden.bridge.native_action is NativeBarrierAction.PASS_ARRAY_BUFFER
    assert hidden.native_call_slot.object_kind is ObjectKind.NUMPY_ARRAY


def test_fixed_width_character_array_results_lower_itemsize_into_both_backends():
    artifacts = WrapperCodeGenerator().generate(_character_array_result_plan())
    c_source = next(source.text for source in artifacts.sources if source.path.suffix == ".c")
    bridge_source = next(source.text for source in artifacts.sources if source.path.suffix == ".f90")

    assert (
        "PyArray_New(&PyArray_Type, 1, result_obj_dims, NPY_STRING, NULL, result, 5, "
        "NPY_ARRAY_C_CONTIGUOUS | NPY_ARRAY_WRITEABLE, NULL)" in c_source
    )
    assert (
        "PyArray_New(&PyArray_Type, 1, result_obj_dims, NPY_STRING, NULL, labels, 4, "
        "NPY_ARRAY_C_CONTIGUOUS | NPY_ARRAY_WRITEABLE, NULL)" in c_source
    )
    assert "PyCapsule_New(result, NULL, capsule_cleanup)" in c_source
    assert "PyCapsule_New(labels, NULL, capsule_cleanup)" in c_source
    assert "character(kind=c_char, len=5), dimension(3) :: result_value" in bridge_source
    assert "character(kind=c_char), pointer, dimension(:) :: result_copy" in bridge_source
    assert "5_c_size_t * size(result_value, kind=c_size_t)" in bridge_source
    assert "result_copy = transfer(result_value, result_copy, 5 * size(result_value))" in bridge_source
    assert "character(kind=c_char, len=4), dimension(2) :: labels_value" in bridge_source
    assert "labels_copy = transfer(labels_value, labels_copy, 4 * size(labels_value))" in bridge_source
    assert max(map(len, bridge_source.splitlines())) <= 132


def test_fixed_width_character_array_result_itemsize_edit_fails_before_lowering():
    plan = _character_array_result_plan()
    result = plan.namespaces[0].functions[0].results[0]
    result.array.itemsize = None

    with pytest.raises(ValueError, match="invalid-array-result-itemsize"):
        WrapperCodeGenerator().generate(plan)
