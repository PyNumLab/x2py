import gc
import ctypes

import numpy as np
import pytest

import x2py
from x2py.runtime_handles import (
    _NativeArrayHandoff,
    _native_array_actual_argument_for_binding_positional,
    _native_array_actual_for_binding,
    _native_array_descriptor_argument_for_binding,
    _native_array_descriptor_argument_for_binding_positional,
    _native_array_descriptor_for_binding,
    _native_array_handle_from_generated_ops,
    _numpy_view_from_pointer_c_descriptor,
    AllocatableHandle,
    NativeArrayHandleBase,
    PointerHandle,
)


def test_runtime_handle_classes_are_public_api_exports():
    assert x2py.AllocatableHandle is AllocatableHandle
    assert x2py.NativeArrayHandleBase is NativeArrayHandleBase
    assert x2py.PointerHandle is PointerHandle
    assert {"AllocatableHandle", "NativeArrayHandleBase", "PointerHandle"} <= set(x2py.__all__)


class _ArrayState:
    def __init__(self, *, shape=None, value=None):
        self.shape = shape
        self.value = value


def _handoff(address=1):
    return _NativeArrayHandoff(address)


def _required_handoff_ops():
    return {
        "array_actual": lambda _handle: _handoff(101),
        "descriptor": lambda _handle: _handoff(102),
    }


def _common_ops(state: _ArrayState):
    return {
        **_required_handoff_ops(),
        "shape": lambda _handle: state.shape,
        "to_numpy": lambda _handle: state.value if state.shape is not None else None,
    }


def test_generated_handle_factory_adapts_private_operations_to_runtime_protocol():
    owner = object()
    value = np.arange(3, dtype=np.float64)
    calls = []

    def shape():
        calls.append(("shape", ()))
        return (3,)

    def array_actual():
        calls.append(("array_actual", ()))
        return 1001

    def descriptor():
        calls.append(("descriptor", ()))
        return ctypes.c_void_p(1002)

    def allocated():
        calls.append(("allocated", ()))
        return True

    def to_numpy():
        calls.append(("to_numpy", ()))
        return value

    handle = _native_array_handle_from_generated_ops(
        "allocatable",
        "float64",
        1,
        {
            "shape": shape,
            "array_actual": array_actual,
            "descriptor": descriptor,
            "allocated": allocated,
            "to_numpy": to_numpy,
        },
        owner=owner,
        descriptor_ownership="borrowed",
        to_numpy_policy="borrowed_view",
        generation=9,
    )

    assert isinstance(handle, AllocatableHandle)
    assert handle.owner is owner
    assert handle.generation == 9
    assert handle.shape == (3,)
    assert handle.to_numpy() is value
    assert handle._array_actual_for_binding(expected_dtype="float64", expected_rank=1).address == 1001
    assert handle._descriptor_for_binding(expected_dtype="float64", expected_rank=1) == {
        "base_addr": 1002,
        "elem_len": 8,
        "rank": 1,
        "dim": [{"lower_bound": 0, "extent": 3, "sm": 8}],
    }
    assert calls == [
        ("allocated", ()),
        ("shape", ()),
        ("allocated", ()),
        ("to_numpy", ()),
        ("allocated", ()),
        ("allocated", ()),
        ("shape", ()),
        ("array_actual", ()),
        ("allocated", ()),
        ("shape", ()),
        ("descriptor", ()),
    ]


def test_generated_handle_factory_splats_shape_operations_to_scalar_extents():
    calls = []
    handle = _native_array_handle_from_generated_ops(
        "allocatable",
        "float64",
        2,
        {
            "shape": lambda: (2, 3),
            "array_actual": lambda: 1001,
            "descriptor": lambda: 1002,
            "allocated": lambda: True,
            "resize": lambda *extents: calls.append(("resize", extents)),
        },
        to_numpy_policy="unsupported",
    )

    handle.resize((4, 5))

    assert calls == [("resize", (4, 5))]


def test_generated_owned_handle_factory_passes_persistent_owner_to_every_operation():
    calls = []
    owner = 0x1234
    value = np.arange(3, dtype=np.float64)

    def operation(name, result=None):
        def call(received_owner, *args):
            calls.append((name, received_owner, args))
            return result

        return call

    handle = _native_array_handle_from_generated_ops(
        "allocatable",
        "float64",
        1,
        {
            "shape": operation("shape", (3,)),
            "array_actual": operation("array_actual", 0x5678),
            "descriptor": operation("descriptor", 0x5678),
            "allocated": operation("allocated", True),
            "to_numpy": operation("to_numpy", value),
            "resize": operation("resize"),
            "destroy": operation("destroy"),
        },
        owner=owner,
        descriptor_ownership="owned",
    )

    assert handle.shape == (3,)
    assert handle.to_numpy() is value
    assert handle._array_actual_for_binding().address == 0x5678
    handle.resize((5,))
    handle.close()

    assert calls == [
        ("allocated", owner, ()),
        ("shape", owner, ()),
        ("allocated", owner, ()),
        ("to_numpy", owner, ()),
        ("allocated", owner, ()),
        ("allocated", owner, ()),
        ("shape", owner, ()),
        ("array_actual", owner, ()),
        ("resize", owner, (np.int64(5),)),
        ("destroy", owner, ()),
    ]


def test_generated_owned_handle_factory_releases_owner_once_when_construction_fails():
    calls = []
    owner = 0x1234

    def destroy(received_owner):
        calls.append(("destroy", received_owner))

    with pytest.raises(ValueError, match="requires generated operation 'descriptor'"):
        _native_array_handle_from_generated_ops(
            "allocatable",
            "float64",
            1,
            {
                "shape": lambda _owner: (1,),
                "array_actual": lambda _owner: 0x5678,
                "allocated": lambda _owner: True,
                "destroy": destroy,
            },
            owner=owner,
            descriptor_ownership="owned",
            to_numpy_policy="unsupported",
        )

    gc.collect()
    assert calls == [("destroy", owner)]


def test_generated_handle_factory_rejects_invalid_descriptor_kind_and_handoff_result():
    ops = {
        "shape": lambda: (1,),
        "array_actual": lambda: object(),
        "descriptor": lambda: 1,
        "allocated": lambda: True,
        "to_numpy": lambda: np.zeros(1, dtype=np.float64),
    }

    with pytest.raises(ValueError, match="generated native array handle kind"):
        _native_array_handle_from_generated_ops("target", "float64", 1, ops)

    handle = _native_array_handle_from_generated_ops("allocatable", "float64", 1, ops)
    with pytest.raises(TypeError, match="handoff address must be an integer"):
        handle._array_actual_for_binding(expected_dtype="float64", expected_rank=1)


def test_allocatable_handle_uses_common_metadata_shape_owner_and_numpy_dispatch():
    owner = object()
    state = _ArrayState(shape=(2, 3), value=np.zeros((2, 3), dtype=np.float64))
    ops = {
        **_common_ops(state),
        "allocated": lambda _handle: state.shape is not None,
        "deallocate": lambda _handle: setattr(state, "shape", None),
        "resize": lambda _handle, shape: setattr(state, "shape", shape),
    }

    handle = AllocatableHandle(
        dtype="float64",
        rank=2,
        ops=ops,
        owner=owner,
        descriptor_ownership="borrowed",
        generation=7,
    )

    assert isinstance(handle, NativeArrayHandleBase)
    assert handle.descriptor_kind == "allocatable"
    assert handle.dtype == "float64"
    assert handle.rank == 2
    assert handle.shape == (2, 3)
    assert handle.to_numpy() is state.value
    assert handle.owner is owner
    assert handle.borrowed is True
    assert handle.owned is False
    assert handle.to_numpy_policy == "borrowed_view"
    assert handle.generation == 7
    assert handle.allocated is True


def test_allocatable_to_numpy_short_circuits_unallocated_state_before_generated_extraction():
    handle = AllocatableHandle(
        dtype="float64",
        rank=1,
        ops={
            **_required_handoff_ops(),
            "shape": lambda _handle: None,
            "to_numpy": lambda _handle: pytest.fail("unallocated handles must not call generated extraction"),
            "allocated": lambda _handle: False,
        },
    )

    assert handle.to_numpy() is None


def test_pointer_to_numpy_short_circuits_unassociated_state_before_unsupported_policy():
    handle = PointerHandle(
        dtype="float64",
        rank=1,
        ops={
            **_required_handoff_ops(),
            "shape": lambda _handle: None,
            "associated": lambda _handle: False,
            "nullify": lambda _handle: None,
        },
        to_numpy_policy="unsupported",
    )

    assert handle.to_numpy() is None


def test_shape_short_circuits_absent_descriptor_state_before_generated_shape():
    def fail_shape(_handle):
        pytest.fail("absent descriptor state must not call generated shape")

    allocatable = AllocatableHandle(
        dtype="float64",
        rank=1,
        ops={
            **_required_handoff_ops(),
            "shape": fail_shape,
            "allocated": lambda _handle: False,
        },
        to_numpy_policy="unsupported",
    )
    pointer = PointerHandle(
        dtype="float64",
        rank=1,
        ops={
            **_required_handoff_ops(),
            "shape": fail_shape,
            "associated": lambda _handle: False,
            "nullify": lambda _handle: None,
        },
        to_numpy_policy="unsupported",
    )

    assert allocatable.shape is None
    assert pointer.shape is None


def test_owned_handle_close_calls_destroy_once_and_blocks_later_use():
    calls = []
    state = _ArrayState(shape=(2,), value=np.zeros(2, dtype=np.float64))
    handle = AllocatableHandle(
        dtype="float64",
        rank=1,
        ops={
            **_common_ops(state),
            "allocated": lambda _handle: True,
            "destroy": lambda _handle: calls.append(("destroy", _handle.shape, _handle.to_numpy())),
        },
        descriptor_ownership="owned",
    )

    assert handle.closed is False
    assert handle.close() is None
    assert handle.closed is True
    assert handle.close() is None
    assert calls == [("destroy", (2,), state.value)]
    with pytest.raises(ReferenceError, match="allocatable handle is closed"):
        _ = handle.shape
    with pytest.raises(ReferenceError, match="allocatable handle is closed"):
        handle.to_numpy()


def test_owned_handle_close_marks_closed_when_destroy_raises():
    calls = []

    def destroy(_handle):
        calls.append("destroy")
        raise RuntimeError("boom")

    handle = AllocatableHandle(
        dtype="float64",
        rank=1,
        ops={
            **_required_handoff_ops(),
            "shape": lambda _handle: (1,),
            "allocated": lambda _handle: True,
            "destroy": destroy,
        },
        descriptor_ownership="owned",
        to_numpy_policy="unsupported",
    )

    with pytest.raises(RuntimeError, match="boom"):
        handle.close()
    assert handle.closed is True
    assert handle.close() is None

    del handle
    gc.collect()

    assert calls == ["destroy"]


def test_owned_handle_finalizer_calls_destroy_once():
    calls = []

    handle = AllocatableHandle(
        dtype="float64",
        rank=1,
        ops={
            **_required_handoff_ops(),
            "shape": lambda _handle: (1,),
            "allocated": lambda _handle: True,
            "destroy": lambda _handle: calls.append("destroy"),
        },
        descriptor_ownership="owned",
        to_numpy_policy="unsupported",
    )

    del handle
    gc.collect()

    assert calls == ["destroy"]


def test_owned_handle_construction_requires_generated_destroy_operation():
    with pytest.raises(ValueError, match="owned native array handle requires generated operation 'destroy'"):
        AllocatableHandle(
            dtype="float64",
            rank=1,
            ops={
                **_required_handoff_ops(),
                "shape": lambda _handle: (1,),
                "allocated": lambda _handle: True,
            },
            descriptor_ownership="owned",
            to_numpy_policy="unsupported",
        )


def test_borrowed_handle_close_and_finalizer_do_not_destroy_native_storage():
    calls = []

    handle = PointerHandle(
        dtype="float64",
        rank=1,
        ops={
            **_required_handoff_ops(),
            "shape": lambda _handle: (1,),
            "associated": lambda _handle: True,
            "nullify": lambda _handle: None,
            "destroy": lambda _handle: calls.append("destroy"),
        },
        to_numpy_policy="unsupported",
    )

    assert handle.close() is None
    assert handle.closed is False
    del handle
    gc.collect()

    assert calls == []


def test_allocatable_handle_reports_absent_state_and_routes_resize_deallocate():
    state = _ArrayState()
    ops = {
        **_common_ops(state),
        "allocated": lambda _handle: state.shape is not None,
        "deallocate": lambda _handle: setattr(state, "shape", None),
        "resize": lambda _handle, shape: setattr(state, "shape", shape),
    }
    handle = AllocatableHandle(dtype="float64", rank=1, ops=ops)

    assert handle.allocated is False
    assert handle.shape is None
    assert handle.to_numpy() is None

    handle.resize(4)
    assert handle.allocated is True
    assert handle.shape == (4,)

    handle.deallocate()
    assert handle.allocated is False
    assert handle.shape is None


def test_allocatable_to_numpy_policy_returns_mutable_borrowed_view():
    source = np.array([1.0, 2.0, 3.0], dtype=np.float64)
    state = _ArrayState(shape=source.shape, value=source)
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            **_common_ops(state),
            "allocated": lambda _handle: True,
            "deallocate": lambda _handle: None,
            "resize": lambda _handle, _shape: None,
        },
        to_numpy_policy="borrowed_view",
    )

    view = handle.to_numpy()

    assert view is source
    assert view.flags.writeable is True
    view[1] = 8.0
    assert source[1] == 8.0


def test_allocatable_to_numpy_policy_returns_read_only_detached_snapshot():
    source = np.array([1.0, 2.0, 3.0], dtype=np.float64)
    state = _ArrayState(shape=source.shape, value=source)
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            **_common_ops(state),
            "allocated": lambda _handle: True,
            "deallocate": lambda _handle: None,
            "resize": lambda _handle, _shape: None,
        },
        to_numpy_policy="read_only_detached_copy",
    )

    snapshot = handle.to_numpy()

    assert np.shares_memory(snapshot, source) is False
    assert snapshot.flags.writeable is False
    source[0] = 99.0
    assert snapshot[0] == 1.0
    with pytest.raises(ValueError, match="assignment destination is read-only"):
        snapshot[0] = 4.0


def test_to_numpy_contiguous_view_policy_rejects_non_contiguous_storage():
    source = np.arange(8, dtype=np.float64)
    strided = source[::2]
    handle = PointerHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            **_required_handoff_ops(),
            "shape": lambda _handle: strided.shape,
            "to_numpy": lambda _handle: strided,
            "associated": lambda _handle: True,
            "nullify": lambda _handle: None,
        },
        to_numpy_policy="contiguous_view",
    )

    with pytest.raises(ValueError, match="must be contiguous"):
        handle.to_numpy()


def test_to_numpy_copy_only_policy_returns_detached_writeable_copy():
    source = np.arange(4, dtype=np.float64)
    handle = PointerHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            **_required_handoff_ops(),
            "shape": lambda _handle: source.shape,
            "to_numpy": lambda _handle: source,
            "associated": lambda _handle: True,
            "nullify": lambda _handle: None,
        },
        to_numpy_policy="copy_only",
    )

    copy = handle.to_numpy()

    assert np.shares_memory(copy, source) is False
    assert copy.flags.writeable is True
    copy[0] = 99.0
    assert source[0] == 0.0


@pytest.mark.parametrize(
    "policy",
    ["borrowed_view", "contiguous_view", "copy_only", "descriptor_view", "read_only_detached_copy"],
)
def test_to_numpy_rejects_generated_non_numpy_results(policy: str):
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            **_required_handoff_ops(),
            "shape": lambda _handle: (2,),
            "to_numpy": lambda _handle: [1.0, 2.0],
            "allocated": lambda _handle: True,
            "deallocate": lambda _handle: None,
            "resize": lambda _handle, _shape: None,
        },
        to_numpy_policy=policy,
    )

    with pytest.raises(TypeError, match="must return a NumPy array or None"):
        handle.to_numpy()


def test_to_numpy_rejects_generated_none_for_present_descriptor_state():
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            **_required_handoff_ops(),
            "shape": lambda _handle: (2,),
            "to_numpy": lambda _handle: None,
            "allocated": lambda _handle: True,
        },
    )

    with pytest.raises(TypeError, match="returned None for present descriptor state"):
        handle.to_numpy()


def test_to_numpy_rejects_generated_array_with_wrong_rank_or_dtype():
    wrong_rank = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            **_required_handoff_ops(),
            "shape": lambda _handle: (2,),
            "to_numpy": lambda _handle: np.zeros((1, 2), dtype=np.float64),
            "allocated": lambda _handle: True,
        },
    )
    with pytest.raises(ValueError, match="to_numpy result rank 2 does not match declared rank 1"):
        wrong_rank.to_numpy()

    wrong_dtype = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            **_required_handoff_ops(),
            "shape": lambda _handle: (2,),
            "to_numpy": lambda _handle: np.zeros(2, dtype=np.int32),
            "allocated": lambda _handle: True,
        },
    )
    with pytest.raises(TypeError, match="to_numpy result dtype"):
        wrong_dtype.to_numpy()


def test_allocatable_array_actual_hook_requires_allocated_state_without_to_numpy():
    actual = _handoff(201)
    calls = []
    state = _ArrayState()
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "descriptor": lambda _handle: _handoff(202),
            "shape": lambda _handle: state.shape,
            "allocated": lambda _handle: state.shape is not None,
            "to_numpy": lambda _handle: pytest.fail("array-actual handoff must not call to_numpy"),
            "array_actual": lambda _handle: calls.append("array_actual") or actual,
        },
    )

    with pytest.raises(ValueError, match="unallocated"):
        handle._array_actual_for_binding(expected_dtype=np.float64, expected_rank=1)

    state.shape = (4,)

    assert handle._array_actual_for_binding(expected_dtype="float64", expected_rank=1) is actual
    assert calls == ["array_actual"]


def test_array_actual_hook_rejects_generated_none_handoff():
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "descriptor": lambda _handle: _handoff(203),
            "shape": lambda _handle: (2,),
            "allocated": lambda _handle: True,
            "array_actual": lambda _handle: None,
        },
        to_numpy_policy="unsupported",
    )

    with pytest.raises(TypeError, match="array_actual operation must return a native handoff object"):
        _native_array_actual_for_binding(handle)


def test_native_array_handoff_requires_non_null_pointer_address():
    assert _NativeArrayHandoff(1).address == 1
    with pytest.raises(TypeError, match="address must be an integer"):
        _NativeArrayHandoff(True)
    with pytest.raises(TypeError, match="address must be an integer"):
        _NativeArrayHandoff("1")
    with pytest.raises(ValueError, match="non-null positive pointer"):
        _NativeArrayHandoff(0)
    with pytest.raises(ValueError, match="non-null positive pointer"):
        _NativeArrayHandoff(-1)


def test_array_actual_hook_rejects_generated_untyped_handoff_object():
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "descriptor": lambda _handle: _handoff(245),
            "shape": lambda _handle: (2,),
            "allocated": lambda _handle: True,
            "array_actual": lambda _handle: object(),
        },
        to_numpy_policy="unsupported",
    )

    with pytest.raises(TypeError, match="received object"):
        _native_array_actual_for_binding(handle)


def test_array_actual_hook_validates_expected_dtype_and_rank():
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=2,
        ops={
            "descriptor": lambda _handle: _handoff(204),
            "shape": lambda _handle: (2, 3),
            "allocated": lambda _handle: True,
            "array_actual": lambda _handle: _handoff(205),
        },
        to_numpy_policy="unsupported",
    )

    with pytest.raises(ValueError, match="expected rank 1"):
        handle._array_actual_for_binding(expected_rank=1)
    with pytest.raises(TypeError, match="expected dtype"):
        handle._array_actual_for_binding(expected_dtype=np.int32)


def test_array_actual_hook_validates_expected_shape_layout_and_writeability():
    actual = _handoff(206)
    calls = []
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=2,
        ops={
            "descriptor": lambda _handle: _handoff(207),
            "shape": lambda _handle: (0, 3),
            "allocated": lambda _handle: True,
            "layout": lambda _handle: "F",
            "writeable": lambda _handle: True,
            "array_actual": lambda _handle: calls.append("array_actual") or actual,
        },
        to_numpy_policy="unsupported",
    )

    assert (
        handle._array_actual_for_binding(
            expected_dtype=np.float64,
            expected_rank=2,
            expected_shape=(0, 3),
            expected_layout="F",
            require_writeable=True,
        )
        is actual
    )
    assert calls == ["array_actual"]

    with pytest.raises(ValueError, match=r"expected shape .* axis 0"):
        handle._array_actual_for_binding(expected_shape=(1, 3))
    with pytest.raises(ValueError, match="expected shape rank 1"):
        handle._array_actual_for_binding(expected_shape=(0,))
    assert handle._array_actual_for_binding(expected_layout="f") is actual
    with pytest.raises(ValueError, match="expected layout 'C'"):
        handle._array_actual_for_binding(expected_layout="C")

    read_only = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "descriptor": lambda _handle: _handoff(208),
            "shape": lambda _handle: (2,),
            "allocated": lambda _handle: True,
            "writeable": lambda _handle: False,
            "array_actual": lambda _handle: _handoff(209),
        },
        to_numpy_policy="unsupported",
    )
    with pytest.raises(TypeError, match="must be writeable"):
        read_only._array_actual_for_binding(require_writeable=True)

    missing_writeable = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "descriptor": lambda _handle: _handoff(210),
            "shape": lambda _handle: (2,),
            "allocated": lambda _handle: True,
            "array_actual": lambda _handle: _handoff(211),
        },
        to_numpy_policy="unsupported",
    )
    with pytest.raises(NotImplementedError, match="operation 'writeable' is not available"):
        missing_writeable._array_actual_for_binding(require_writeable=True)


def test_array_actual_hook_rejects_unsupported_layout_names_before_handoff():
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "descriptor": lambda _handle: _handoff(212),
            "shape": lambda _handle: (2,),
            "allocated": lambda _handle: True,
            "layout": lambda _handle: pytest.fail("unsupported expected layout must not call generated layout op"),
            "array_actual": lambda _handle: pytest.fail("unsupported expected layout must block native handoff"),
        },
        to_numpy_policy="unsupported",
    )

    with pytest.raises(ValueError, match="unsupported expected NumPy array layout 'A'"):
        handle._array_actual_for_binding(expected_layout="A")

    invalid_actual = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "descriptor": lambda _handle: _handoff(213),
            "shape": lambda _handle: (2,),
            "allocated": lambda _handle: True,
            "layout": lambda _handle: "K",
            "array_actual": lambda _handle: pytest.fail("unsupported actual layout must block native handoff"),
        },
        to_numpy_policy="unsupported",
    )
    with pytest.raises(ValueError, match="layout operation returned unsupported layout 'K'"):
        invalid_actual._array_actual_for_binding(expected_layout="F")


def test_array_actual_hook_validates_native_byte_order_and_alignment_ops():
    actual = _handoff(214)
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "descriptor": lambda _handle: _handoff(215),
            "shape": lambda _handle: (2,),
            "allocated": lambda _handle: True,
            "native_byte_order": lambda _handle: True,
            "aligned": lambda _handle: True,
            "array_actual": lambda _handle: actual,
        },
        to_numpy_policy="unsupported",
    )

    assert (
        handle._array_actual_for_binding(
            require_native_byte_order=True,
            require_aligned=True,
        )
        is actual
    )

    byte_swapped = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "descriptor": lambda _handle: _handoff(216),
            "shape": lambda _handle: (2,),
            "allocated": lambda _handle: True,
            "native_byte_order": lambda _handle: False,
            "array_actual": lambda _handle: _handoff(217),
        },
        to_numpy_policy="unsupported",
    )
    with pytest.raises(TypeError, match="native byte order"):
        byte_swapped._array_actual_for_binding(require_native_byte_order=True)

    unaligned = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "descriptor": lambda _handle: _handoff(218),
            "shape": lambda _handle: (2,),
            "allocated": lambda _handle: True,
            "aligned": lambda _handle: False,
            "array_actual": lambda _handle: _handoff(219),
        },
        to_numpy_policy="unsupported",
    )
    with pytest.raises(TypeError, match="aligned"):
        unaligned._array_actual_for_binding(require_aligned=True)


def test_array_actual_binding_helper_accepts_ndarray_path_with_shared_validation():
    values = np.asfortranarray(np.zeros((2, 3), dtype=np.float64))

    assert (
        _native_array_actual_for_binding(
            values,
            expected_dtype=np.float64,
            expected_rank=2,
            expected_shape=(2, 3),
            expected_layout="F",
            require_writeable=True,
        )
        is values
    )

    with pytest.raises(ValueError, match="expected rank 1"):
        _native_array_actual_for_binding(values, expected_rank=1)
    with pytest.raises(TypeError, match="expected dtype"):
        _native_array_actual_for_binding(values, expected_dtype=np.float32)
    with pytest.raises(ValueError, match=r"expected shape .* axis 0"):
        _native_array_actual_for_binding(values, expected_shape=(1, 3))
    with pytest.raises(ValueError, match="expected layout 'C'"):
        _native_array_actual_for_binding(values, expected_layout="C")

    read_only = values.copy()
    read_only.setflags(write=False)
    with pytest.raises(TypeError, match="writeable"):
        _native_array_actual_for_binding(read_only, require_writeable=True)


def test_array_actual_binding_helper_rejects_byte_swapped_and_unaligned_ndarrays():
    swapped_dtype = np.dtype(np.float64).newbyteorder("S")
    swapped = np.array([1.0, 2.0], dtype=swapped_dtype)
    with pytest.raises(TypeError, match="native byte order"):
        _native_array_actual_for_binding(swapped, require_native_byte_order=True)

    storage = np.zeros(8 * 2 + 1, dtype=np.uint8)
    unaligned = storage[1:].view(np.float64)
    assert not unaligned.flags.aligned
    with pytest.raises(TypeError, match="aligned"):
        _native_array_actual_for_binding(unaligned, require_aligned=True)


def test_array_actual_binding_helper_routes_handles_without_numpy_conversion():
    alloc_actual = _handoff(220)
    pointer_actual = _handoff(221)
    calls = []
    alloc_handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "descriptor": lambda _handle: _handoff(222),
            "shape": lambda _handle: (2,),
            "allocated": lambda _handle: True,
            "layout": lambda _handle: "F",
            "writeable": lambda _handle: True,
            "native_byte_order": lambda _handle: True,
            "aligned": lambda _handle: True,
            "to_numpy": lambda _handle: pytest.fail("array-actual handoff must not call to_numpy"),
            "array_actual": lambda _handle: calls.append("alloc") or alloc_actual,
        },
    )
    pointer_handle = PointerHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "descriptor": lambda _handle: _handoff(223),
            "shape": lambda _handle: (2,),
            "associated": lambda _handle: True,
            "nullify": lambda _handle: None,
            "layout": lambda _handle: "F",
            "writeable": lambda _handle: True,
            "native_byte_order": lambda _handle: True,
            "aligned": lambda _handle: True,
            "to_numpy": lambda _handle: pytest.fail("array-actual handoff must not call to_numpy"),
            "array_actual": lambda _handle: calls.append("pointer") or pointer_actual,
        },
    )

    assert (
        _native_array_actual_for_binding(
            alloc_handle,
            expected_dtype=np.float64,
            expected_rank=1,
            expected_shape=(2,),
            expected_layout="F",
            require_writeable=True,
            require_native_byte_order=True,
            require_aligned=True,
        )
        is alloc_actual
    )
    assert (
        _native_array_actual_for_binding(
            pointer_handle,
            expected_dtype=np.float64,
            expected_rank=1,
            expected_shape=(2,),
            expected_layout="F",
            require_writeable=True,
            require_native_byte_order=True,
            require_aligned=True,
        )
        is pointer_actual
    )
    assert calls == ["alloc", "pointer"]


def test_array_actual_binding_helper_preserves_zero_length_array_actuals():
    values = np.zeros((0,), dtype=np.float64)
    assert _native_array_actual_for_binding(values, expected_dtype=np.float64, expected_shape=(0,)) is values

    alloc_actual = _handoff(224)
    pointer_actual = _handoff(225)
    alloc_handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "descriptor": lambda _handle: _handoff(226),
            "shape": lambda _handle: (0,),
            "allocated": lambda _handle: True,
            "array_actual": lambda _handle: alloc_actual,
        },
        to_numpy_policy="unsupported",
    )
    pointer_handle = PointerHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "descriptor": lambda _handle: _handoff(227),
            "shape": lambda _handle: (0,),
            "associated": lambda _handle: True,
            "nullify": lambda _handle: None,
            "array_actual": lambda _handle: pointer_actual,
        },
        to_numpy_policy="unsupported",
    )

    assert _native_array_actual_for_binding(alloc_handle, expected_shape=(0,)) is alloc_actual
    assert _native_array_actual_for_binding(pointer_handle, expected_shape=(0,)) is pointer_actual


def test_array_actual_argument_abi_packer_uses_ndarray_data_pointer_and_shape_fields():
    values = np.asfortranarray(np.zeros((2, 3), dtype=np.float64))

    assert _native_array_actual_argument_for_binding_positional(
        values,
        np.float64,
        2,
        (2, 3),
        "F",
        True,
        True,
        True,
        True,
        True,
        True,
    ) == (values.ctypes.data, 2, values.dtype.itemsize, 2, 3, 2, 3, 1, 1)


def test_array_actual_argument_abi_packer_uses_allocatable_native_array_actual_without_numpy_conversion():
    actual = _handoff(246)
    calls = []
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "descriptor": lambda _handle: _handoff(247),
            "shape": lambda _handle: (2,),
            "allocated": lambda _handle: True,
            "layout": lambda _handle: "F",
            "writeable": lambda _handle: True,
            "native_byte_order": lambda _handle: True,
            "aligned": lambda _handle: True,
            "to_numpy": lambda _handle: pytest.fail("array-actual ABI packing must not call to_numpy"),
            "array_actual": lambda _handle: calls.append("array_actual") or actual,
        },
    )

    assert _native_array_actual_argument_for_binding_positional(
        handle,
        "float64",
        1,
        (2,),
        "F",
        True,
        True,
        True,
        True,
        True,
        True,
    ) == (actual.address, 1, np.dtype(np.float64).itemsize, 2, 2, 1)
    assert calls == ["array_actual"]


def test_array_actual_argument_abi_packer_uses_pointer_native_array_actual_dtype_metadata():
    actual = _handoff(248)
    handle = PointerHandle(
        dtype=np.dtype(np.float32),
        rank=1,
        ops={
            "descriptor": lambda _handle: _handoff(249),
            "shape": lambda _handle: (3,),
            "associated": lambda _handle: True,
            "nullify": lambda _handle: None,
            "array_actual": lambda _handle: actual,
        },
        to_numpy_policy="unsupported",
    )

    assert _native_array_actual_argument_for_binding_positional(
        handle,
        None,
        1,
        (3,),
        None,
        False,
        False,
        False,
        False,
        True,
        False,
    ) == (actual.address, np.dtype(np.float32).itemsize, 3)


def test_array_actual_argument_abi_packer_rejects_absent_handles_before_generated_handoff():
    alloc_handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "descriptor": lambda _handle: _handoff(250),
            "shape": lambda _handle: None,
            "allocated": lambda _handle: False,
            "to_numpy": lambda _handle: pytest.fail("array-actual ABI packing must not call to_numpy"),
            "array_actual": lambda _handle: pytest.fail("unallocated handle must block native array handoff"),
        },
    )
    pointer_handle = PointerHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "descriptor": lambda _handle: _handoff(251),
            "shape": lambda _handle: None,
            "associated": lambda _handle: False,
            "nullify": lambda _handle: None,
            "to_numpy": lambda _handle: pytest.fail("array-actual ABI packing must not call to_numpy"),
            "array_actual": lambda _handle: pytest.fail("unassociated handle must block native array handoff"),
        },
    )

    with pytest.raises(ValueError, match="unallocated"):
        _native_array_actual_argument_for_binding_positional(alloc_handle)
    with pytest.raises(ValueError, match="unassociated"):
        _native_array_actual_argument_for_binding_positional(pointer_handle)


def test_runtime_handle_shapes_reject_negative_extents_before_binding_handoff():
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "shape": lambda _handle: (-1,),
            "allocated": lambda _handle: True,
            "array_actual": lambda _handle: pytest.fail("negative shape must block native handoff"),
            "descriptor": lambda _handle: pytest.fail("negative shape must block descriptor handoff"),
        },
        to_numpy_policy="unsupported",
    )

    with pytest.raises(ValueError, match="non-negative"):
        _ = handle.shape
    with pytest.raises(ValueError, match="non-negative"):
        _native_array_actual_for_binding(handle)
    with pytest.raises(ValueError, match="non-negative"):
        _native_array_descriptor_for_binding(handle, descriptor_kind="allocatable")
    with pytest.raises(ValueError, match="non-negative"):
        handle.resize(-1)

    valid_handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "array_actual": lambda _handle: _handoff(228),
            "shape": lambda _handle: (1,),
            "allocated": lambda _handle: True,
            "descriptor": lambda _handle: _handoff(229),
        },
        to_numpy_policy="unsupported",
    )
    with pytest.raises(ValueError, match="non-negative"):
        valid_handle._descriptor_for_binding(expected_shape=(-1,))


def test_array_actual_binding_helper_rejects_absent_handles_none_and_non_arrays():
    alloc_handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "descriptor": lambda _handle: _handoff(230),
            "shape": lambda _handle: None,
            "allocated": lambda _handle: False,
            "to_numpy": lambda _handle: pytest.fail("array-actual handoff must not call to_numpy"),
            "array_actual": lambda _handle: _handoff(231),
        },
    )
    pointer_handle = PointerHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "descriptor": lambda _handle: _handoff(232),
            "shape": lambda _handle: None,
            "associated": lambda _handle: False,
            "nullify": lambda _handle: None,
            "to_numpy": lambda _handle: pytest.fail("array-actual handoff must not call to_numpy"),
            "array_actual": lambda _handle: _handoff(233),
        },
    )

    with pytest.raises(ValueError, match="unallocated"):
        _native_array_actual_for_binding(alloc_handle)
    with pytest.raises(ValueError, match="unassociated"):
        _native_array_actual_for_binding(pointer_handle)
    with pytest.raises(TypeError, match="received None"):
        _native_array_actual_for_binding(None)
    with pytest.raises(TypeError, match="received list"):
        _native_array_actual_for_binding([1.0, 2.0])


def test_allocatable_descriptor_hook_accepts_unallocated_descriptor_without_numpy_conversion():
    descriptor = _handoff(234)
    calls = []
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "shape": lambda _handle: None,
            "allocated": lambda _handle: False,
            "to_numpy": lambda _handle: pytest.fail("descriptor handoff must not call to_numpy"),
            "array_actual": lambda _handle: pytest.fail("descriptor handoff must not request array actual"),
            "descriptor": lambda _handle: calls.append("descriptor") or descriptor,
        },
        to_numpy_policy="unsupported",
    )

    assert handle._descriptor_for_binding(expected_dtype="float64", expected_rank=1) == {
        "base_addr": descriptor.address,
        "elem_len": 8,
        "rank": 1,
        "dim": [{"lower_bound": 0, "extent": 0, "sm": 8}],
    }
    assert calls == ["descriptor"]


def test_descriptor_hook_rejects_generated_none_handoff():
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "array_actual": lambda _handle: pytest.fail("descriptor handoff must not request array actual"),
            "shape": lambda _handle: None,
            "allocated": lambda _handle: False,
            "descriptor": lambda _handle: None,
        },
        to_numpy_policy="unsupported",
    )

    with pytest.raises(
        TypeError, match="descriptor operation must return descriptor fields or an integer data address"
    ):
        _native_array_descriptor_for_binding(handle, descriptor_kind="allocatable")


def test_descriptor_hook_validates_expected_dtype_rank_and_current_shape():
    descriptor = _handoff(235)
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=2,
        ops={
            "array_actual": lambda _handle: pytest.fail("descriptor handoff must not request array actual"),
            "shape": lambda _handle: (2, 3),
            "allocated": lambda _handle: True,
            "descriptor": lambda _handle: descriptor,
        },
        to_numpy_policy="unsupported",
    )

    assert handle._descriptor_for_binding(
        expected_dtype=np.float64,
        expected_rank=2,
        expected_shape=(2, 3),
    ) == {
        "base_addr": descriptor.address,
        "elem_len": 8,
        "rank": 2,
        "dim": [
            {"lower_bound": 0, "extent": 2, "sm": 8},
            {"lower_bound": 0, "extent": 3, "sm": 16},
        ],
    }
    with pytest.raises(ValueError, match="expected rank 1"):
        handle._descriptor_for_binding(expected_rank=1)
    with pytest.raises(TypeError, match="expected dtype"):
        handle._descriptor_for_binding(expected_dtype=np.int32)
    with pytest.raises(ValueError, match=r"expected shape .* axis 1"):
        handle._descriptor_for_binding(expected_shape=(2, 4))


def test_descriptor_binding_helper_accepts_matching_handles_and_optional_none():
    alloc_descriptor = _handoff(236)
    pointer_descriptor = _handoff(237)
    alloc_handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "array_actual": lambda _handle: pytest.fail("descriptor handoff must not request array actual"),
            "shape": lambda _handle: (0,),
            "allocated": lambda _handle: True,
            "descriptor": lambda _handle: alloc_descriptor,
        },
        to_numpy_policy="unsupported",
    )
    pointer_handle = PointerHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "array_actual": lambda _handle: pytest.fail("descriptor handoff must not request array actual"),
            "shape": lambda _handle: None,
            "associated": lambda _handle: False,
            "nullify": lambda _handle: None,
            "descriptor": lambda _handle: pointer_descriptor,
        },
        to_numpy_policy="unsupported",
    )

    assert _native_array_descriptor_for_binding(
        alloc_handle,
        descriptor_kind="allocatable",
        expected_dtype=np.float64,
        expected_rank=1,
        expected_shape=(0,),
    ) == {
        "base_addr": alloc_descriptor.address,
        "elem_len": 8,
        "rank": 1,
        "dim": [{"lower_bound": 0, "extent": 0, "sm": 8}],
    }
    assert _native_array_descriptor_for_binding(
        pointer_handle,
        descriptor_kind="pointer",
        expected_dtype=np.float64,
        expected_rank=1,
    ) == {
        "base_addr": pointer_descriptor.address,
        "elem_len": 8,
        "rank": 1,
        "dim": [{"lower_bound": 0, "extent": 0, "sm": 8}],
    }
    assert _native_array_descriptor_for_binding(None, descriptor_kind="pointer", optional=True) is None


def test_descriptor_binding_helper_rejects_plain_arrays_none_and_wrong_kind():
    alloc_handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "array_actual": lambda _handle: pytest.fail("descriptor handoff must not request array actual"),
            "shape": lambda _handle: (1,),
            "allocated": lambda _handle: True,
            "descriptor": lambda _handle: _handoff(238),
        },
        to_numpy_policy="unsupported",
    )

    with pytest.raises(TypeError, match="received ndarray"):
        _native_array_descriptor_for_binding(np.ones(1), descriptor_kind="allocatable")
    with pytest.raises(TypeError, match="received None"):
        _native_array_descriptor_for_binding(None, descriptor_kind="allocatable")
    with pytest.raises(TypeError, match="expected pointer native array handle"):
        _native_array_descriptor_for_binding(alloc_handle, descriptor_kind="pointer")
    with pytest.raises(ValueError, match="unsupported native array descriptor kind"):
        _native_array_descriptor_for_binding(alloc_handle, descriptor_kind="coarray")
    with pytest.raises(ValueError, match="unsupported native array descriptor kind"):
        _native_array_descriptor_for_binding(None, descriptor_kind="coarray", optional=True)


def test_descriptor_argument_abi_packer_returns_required_descriptor_fields():
    descriptor = _handoff(239)
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "array_actual": lambda _handle: pytest.fail("descriptor handoff must not request array actual"),
            "shape": lambda _handle: (2,),
            "allocated": lambda _handle: True,
            "descriptor": lambda _handle: descriptor,
        },
        to_numpy_policy="unsupported",
    )

    assert _native_array_descriptor_argument_for_binding(
        handle,
        descriptor_kind="allocatable",
        expected_dtype=np.float64,
        expected_rank=1,
        expected_shape=(2,),
    ) == (descriptor.address, 8, 1, 0, 2, 8)


def test_descriptor_argument_abi_packer_positional_helper_matches_generated_call_shape():
    descriptor = _handoff(242)
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "array_actual": lambda _handle: pytest.fail("descriptor handoff must not request array actual"),
            "shape": lambda _handle: (2,),
            "allocated": lambda _handle: True,
            "descriptor": lambda _handle: descriptor,
        },
        to_numpy_policy="unsupported",
    )

    assert _native_array_descriptor_argument_for_binding_positional(
        handle,
        "allocatable",
        "float64",
        1,
        None,
        False,
    ) == (descriptor.address, 8, 1, 0, 2, 8)
    assert _native_array_descriptor_argument_for_binding_positional(
        None,
        "allocatable",
        "float64",
        1,
        None,
        True,
    ) == (None, None, None, None, None, None, None)


def test_descriptor_argument_abi_packer_maps_optional_presence_and_absence():
    descriptor = _handoff(240)
    handle = PointerHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "array_actual": lambda _handle: pytest.fail("descriptor handoff must not request array actual"),
            "shape": lambda _handle: None,
            "associated": lambda _handle: False,
            "nullify": lambda _handle: None,
            "descriptor": lambda _handle: descriptor,
        },
        to_numpy_policy="unsupported",
    )

    *descriptor_fields, presence_token = _native_array_descriptor_argument_for_binding(
        handle,
        descriptor_kind="pointer",
        expected_dtype=np.float64,
        expected_rank=1,
        optional_absent=True,
    )
    assert descriptor_fields == [descriptor.address, 8, 1, 0, 0, 8]
    assert presence_token is not None
    assert presence_token != descriptor.address
    assert _native_array_descriptor_argument_for_binding(
        None,
        descriptor_kind="pointer",
        expected_rank=1,
        optional_absent=True,
    ) == (None, None, None, None, None, None, None)


def test_descriptor_argument_abi_packer_rejects_wrong_kind_and_unsupported_descriptor_kind():
    alloc_handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "array_actual": lambda _handle: pytest.fail("descriptor handoff must not request array actual"),
            "shape": lambda _handle: (1,),
            "allocated": lambda _handle: True,
            "descriptor": lambda _handle: _handoff(241),
        },
        to_numpy_policy="unsupported",
    )

    with pytest.raises(TypeError, match="expected pointer native array handle"):
        _native_array_descriptor_argument_for_binding(alloc_handle, descriptor_kind="pointer")
    with pytest.raises(ValueError, match="unsupported native array descriptor kind"):
        _native_array_descriptor_argument_for_binding(None, descriptor_kind="coarray", optional_absent=True)
    with pytest.raises(TypeError, match="received ndarray"):
        _native_array_descriptor_argument_for_binding(np.ones(1), descriptor_kind="allocatable")


def test_pointer_handle_uses_common_base_and_nullify_operation():
    state = _ArrayState(shape=(5,), value=np.zeros(5, dtype=np.int32))

    def nullify(_handle):
        state.shape = None
        state.value = None

    ops = {
        **_common_ops(state),
        "associated": lambda _handle: state.shape is not None,
        "nullify": nullify,
        "destroy": lambda _handle: None,
    }
    handle = PointerHandle(dtype="int32", rank=1, ops=ops, descriptor_ownership="owned")

    assert isinstance(handle, NativeArrayHandleBase)
    assert handle.descriptor_kind == "pointer"
    assert handle.owned is True
    assert handle.associated is True
    assert handle.shape == (5,)
    assert handle.to_numpy() is state.value

    handle.nullify()
    assert handle.associated is False
    assert handle.shape is None
    assert handle.to_numpy() is None


def test_pointer_array_actual_hook_requires_associated_state_without_to_numpy():
    actual = _handoff(242)
    calls = []
    state = _ArrayState()
    handle = PointerHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "descriptor": lambda _handle: _handoff(243),
            "shape": lambda _handle: state.shape,
            "associated": lambda _handle: state.shape is not None,
            "nullify": lambda _handle: setattr(state, "shape", None),
            "to_numpy": lambda _handle: pytest.fail("array-actual handoff must not call to_numpy"),
            "array_actual": lambda _handle: calls.append("array_actual") or actual,
        },
    )

    with pytest.raises(ValueError, match="unassociated"):
        handle._array_actual_for_binding(expected_dtype=np.float64, expected_rank=1)

    state.shape = (3,)

    assert handle._array_actual_for_binding(expected_dtype="float64", expected_rank=1) is actual
    assert calls == ["array_actual"]


def test_pointer_allocation_operations_are_policy_gated_by_ops_table():
    state = _ArrayState(shape=(1,), value=object())
    handle = PointerHandle(
        dtype="float64",
        rank=1,
        ops={
            **_common_ops(state),
            "associated": lambda _handle: True,
            "nullify": lambda _handle: None,
        },
    )

    with pytest.raises(NotImplementedError, match="pointer handle operation 'allocate' is not available"):
        handle.allocate((3,))
    with pytest.raises(NotImplementedError, match="pointer handle operation 'deallocate' is not available"):
        handle.deallocate()
    with pytest.raises(NotImplementedError, match="pointer handle operation 'resize' is not available"):
        handle.resize((4,))


def test_pointer_allocation_operations_route_when_policy_ops_exist():
    state = _ArrayState(shape=None, value=None)

    def allocate(_handle, shape):
        state.shape = shape
        state.value = object()

    def deallocate(_handle):
        state.shape = None
        state.value = None

    def resize(_handle, shape):
        state.shape = shape
        state.value = object()

    handle = PointerHandle(
        dtype="float64",
        rank=2,
        ops={
            **_common_ops(state),
            "associated": lambda _handle: state.shape is not None,
            "nullify": lambda _handle: deallocate(_handle),
            "allocate": allocate,
            "deallocate": deallocate,
            "resize": resize,
        },
    )

    assert handle.associated is False
    handle.allocate((2, 3))
    assert handle.associated is True
    assert handle.shape == (2, 3)

    handle.resize([4, 5])
    assert handle.shape == (4, 5)

    handle.deallocate()
    assert handle.associated is False
    assert handle.shape is None


def test_pointer_to_numpy_reports_missing_descriptor_extraction():
    handle = PointerHandle(
        dtype="float64",
        rank=1,
        ops={
            **_required_handoff_ops(),
            "shape": lambda _handle: (2,),
            "associated": lambda _handle: True,
            "nullify": lambda _handle: None,
        },
        to_numpy_policy="unsupported",
    )

    with pytest.raises(NotImplementedError, match="to_numpy extraction is unsupported by completed policy"):
        handle.to_numpy()


def _pointer_descriptor_for_array(value: np.ndarray):
    return {
        "base_addr": int(value.ctypes.data),
        "elem_len": int(value.dtype.itemsize),
        "rank": value.ndim,
        "dim": [
            {
                "lower_bound": 1,
                "extent": int(extent),
                "sm": int(stride),
            }
            for extent, stride in zip(value.shape, value.strides, strict=True)
        ],
    }


class _DescriptorFieldRecord:
    def __init__(self, **fields):
        self.__dict__.update(fields)


def _pointer_descriptor_record_for_array(value: np.ndarray):
    descriptor = _pointer_descriptor_for_array(value)
    return _DescriptorFieldRecord(
        base_addr=descriptor["base_addr"],
        elem_len=descriptor["elem_len"],
        rank=descriptor["rank"],
        dim=[_DescriptorFieldRecord(**dimension) for dimension in descriptor["dim"]],
    )


def test_pointer_c_descriptor_helper_builds_strided_numpy_view_from_decoded_fields():
    source = np.arange(24, dtype=np.float64).reshape((4, 6), order="F")
    expected = source[1:4:2, 2:6:3]

    view = _numpy_view_from_pointer_c_descriptor(_pointer_descriptor_for_array(expected), dtype=np.float64)

    assert view.shape == expected.shape
    assert view.strides == expected.strides
    np.testing.assert_allclose(view, expected)
    assert np.shares_memory(view, source)

    view[0, 1] = 77.0
    assert expected[0, 1] == 77.0


def test_pointer_c_descriptor_helper_builds_negative_stride_numpy_view_from_decoded_fields():
    source = np.arange(10, dtype=np.float64)
    expected = source[8:1:-2]

    view = _numpy_view_from_pointer_c_descriptor(_pointer_descriptor_for_array(expected), dtype=np.float64)

    assert view.shape == expected.shape
    assert view.strides == expected.strides
    np.testing.assert_allclose(view, expected)
    assert np.shares_memory(view, source)

    view[0] = 88.0
    assert source[8] == 88.0


def test_pointer_c_descriptor_helper_accepts_field_record_objects():
    source = np.arange(12, dtype=np.float64).reshape((3, 4))
    expected = source[:, 1:4:2]

    view = _numpy_view_from_pointer_c_descriptor(_pointer_descriptor_record_for_array(expected), dtype=np.float64)

    assert view.shape == expected.shape
    assert view.strides == expected.strides
    np.testing.assert_allclose(view, expected)
    assert np.shares_memory(view, source)

    view[1, 0] = 55.0
    assert source[1, 1] == 55.0


def test_pointer_c_descriptor_helper_validates_decoded_descriptor_fields():
    source = np.arange(4, dtype=np.float64)
    descriptor = _pointer_descriptor_for_array(source)

    assert _numpy_view_from_pointer_c_descriptor({**descriptor, "base_addr": 0}, dtype=np.float64) is None
    for field in ("base_addr", "elem_len", "rank", "dim"):
        incomplete = dict(descriptor)
        incomplete.pop(field)
        with pytest.raises(TypeError, match=f"field {field!r} is required"):
            _numpy_view_from_pointer_c_descriptor(incomplete, dtype=np.float64)
    with pytest.raises(ValueError, match="base_addr must be non-negative"):
        _numpy_view_from_pointer_c_descriptor({**descriptor, "base_addr": -1}, dtype=np.float64)
    with pytest.raises(TypeError, match="field 'base_addr' must be an integer"):
        _numpy_view_from_pointer_c_descriptor({**descriptor, "base_addr": True}, dtype=np.float64)
    with pytest.raises(ValueError, match=r"elem_len .* itemsize"):
        _numpy_view_from_pointer_c_descriptor({**descriptor, "elem_len": 4}, dtype=np.float64)
    with pytest.raises(ValueError, match="rank must be non-negative"):
        _numpy_view_from_pointer_c_descriptor({**descriptor, "rank": -1}, dtype=np.float64)
    with pytest.raises(ValueError, match="rank 2 does not match 1 dimension records"):
        _numpy_view_from_pointer_c_descriptor({**descriptor, "rank": 2}, dtype=np.float64)
    for field in ("lower_bound", "extent", "sm"):
        bad_dim_record = dict(descriptor["dim"][0])
        bad_dim_record.pop(field)
        with pytest.raises(TypeError, match=f"dim\\[0\\] field {field!r} is required"):
            _numpy_view_from_pointer_c_descriptor({**descriptor, "dim": [bad_dim_record]}, dtype=np.float64)
    with pytest.raises(TypeError, match="field 'lower_bound' must be an integer"):
        bad_dim = [{**descriptor["dim"][0], "lower_bound": True}]
        _numpy_view_from_pointer_c_descriptor({**descriptor, "dim": bad_dim}, dtype=np.float64)
    with pytest.raises(ValueError, match="dim\\[0\\]\\.extent must be non-negative"):
        bad_dim = [{**descriptor["dim"][0], "extent": -1}]
        _numpy_view_from_pointer_c_descriptor({**descriptor, "dim": bad_dim}, dtype=np.float64)
    with pytest.raises(TypeError, match="field 'sm' must be an integer"):
        bad_dim = [{**descriptor["dim"][0], "sm": True}]
        _numpy_view_from_pointer_c_descriptor({**descriptor, "dim": bad_dim}, dtype=np.float64)
    with pytest.raises(TypeError, match="field 'dim' must be a sequence"):
        _numpy_view_from_pointer_c_descriptor({**descriptor, "dim": None}, dtype=np.float64)


def test_pointer_descriptor_view_policy_uses_decoded_descriptor_fields_for_strided_view():
    source = np.arange(10, dtype=np.float64)
    strided = source[1::2]
    state = _ArrayState(shape=strided.shape, value=strided)
    handle = PointerHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            **_common_ops(state),
            "to_numpy": lambda _handle: _pointer_descriptor_for_array(strided),
            "associated": lambda _handle: True,
            "nullify": lambda _handle: None,
        },
        to_numpy_policy="descriptor_view",
    )

    view = handle.to_numpy()

    assert view is not strided
    assert np.shares_memory(view, source)
    assert view.strides == strided.strides
    np.testing.assert_allclose(view, strided)
    view[0] = 42.0
    assert source[1] == 42.0


def test_pointer_descriptor_view_policy_rejects_decoded_descriptor_rank_mismatch():
    source = np.arange(4, dtype=np.float64)
    handle = PointerHandle(
        dtype=np.dtype(np.float64),
        rank=2,
        ops={
            **_required_handoff_ops(),
            "shape": lambda _handle: (2, 2),
            "to_numpy": lambda _handle: _pointer_descriptor_for_array(source),
            "associated": lambda _handle: True,
            "nullify": lambda _handle: None,
        },
        to_numpy_policy="descriptor_view",
    )

    with pytest.raises(ValueError, match="pointer descriptor rank 1 does not match declared handle rank 2"):
        handle.to_numpy()


def test_pointer_descriptor_view_policy_maps_null_decoded_descriptor_to_none():
    source = np.arange(4, dtype=np.float64)
    descriptor = {**_pointer_descriptor_for_array(source), "base_addr": 0}
    handle = PointerHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            **_required_handoff_ops(),
            "shape": lambda _handle: None,
            "to_numpy": lambda _handle: descriptor,
            "associated": lambda _handle: False,
            "nullify": lambda _handle: None,
        },
        to_numpy_policy="descriptor_view",
    )

    assert handle.to_numpy() is None


def test_pointer_descriptor_view_policy_rejects_null_descriptor_for_present_state():
    source = np.arange(4, dtype=np.float64)
    descriptor = {**_pointer_descriptor_for_array(source), "base_addr": 0}
    handle = PointerHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            **_required_handoff_ops(),
            "shape": lambda _handle: (4,),
            "to_numpy": lambda _handle: descriptor,
            "associated": lambda _handle: True,
            "nullify": lambda _handle: None,
        },
        to_numpy_policy="descriptor_view",
    )

    with pytest.raises(TypeError, match="null descriptor for present descriptor state"):
        handle.to_numpy()


def test_to_numpy_policy_unsupported_reports_completed_policy_block():
    handle = PointerHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            **_required_handoff_ops(),
            "shape": lambda _handle: (2,),
            "to_numpy": lambda _handle: pytest.fail("unsupported policy must not call generated extraction"),
            "associated": lambda _handle: True,
            "nullify": lambda _handle: None,
        },
        to_numpy_policy="unsupported",
    )

    with pytest.raises(NotImplementedError, match="to_numpy extraction is unsupported by completed policy"):
        handle.to_numpy()


def test_common_shape_dispatch_validates_rank():
    handle = AllocatableHandle(
        dtype="float64",
        rank=2,
        ops={
            **_required_handoff_ops(),
            "shape": lambda _handle: (4,),
            "to_numpy": lambda _handle: None,
            "allocated": lambda _handle: True,
            "deallocate": lambda _handle: None,
            "resize": lambda _handle, _shape: None,
        },
    )

    with pytest.raises(ValueError, match="shape rank 1 does not match declared rank 2"):
        _ = handle.shape


def test_common_handle_rejects_invalid_descriptor_kind():
    with pytest.raises(ValueError, match="descriptor_kind must be 'allocatable' or 'pointer'"):
        NativeArrayHandleBase(
            dtype="float64",
            rank=1,
            ops={},
            descriptor_kind="target",
            descriptor_ownership="borrowed",
        )


def test_common_handle_rejects_invalid_generated_operation_table():
    with pytest.raises(TypeError, match="operation names must be strings"):
        AllocatableHandle(dtype="float64", rank=1, ops={1: lambda _handle: None})
    with pytest.raises(TypeError, match="operation 'shape' must be callable"):
        AllocatableHandle(dtype="float64", rank=1, ops={"shape": None})


def test_common_handle_requires_generated_shape_operation():
    with pytest.raises(ValueError, match="requires generated operation 'shape'"):
        AllocatableHandle(dtype="float64", rank=1, ops={})


def test_common_handle_requires_generated_handoff_operations():
    with pytest.raises(ValueError, match="requires generated operation 'array_actual'"):
        AllocatableHandle(
            dtype="float64",
            rank=1,
            ops={
                "shape": lambda _handle: (1,),
                "allocated": lambda _handle: True,
            },
            to_numpy_policy="unsupported",
        )
    with pytest.raises(ValueError, match="requires generated operation 'descriptor'"):
        AllocatableHandle(
            dtype="float64",
            rank=1,
            ops={
                "array_actual": lambda _handle: _handoff(244),
                "shape": lambda _handle: (1,),
                "allocated": lambda _handle: True,
            },
            to_numpy_policy="unsupported",
        )


def test_extraction_enabled_handle_requires_generated_to_numpy_operation():
    with pytest.raises(ValueError, match="requires generated operation 'to_numpy'"):
        AllocatableHandle(
            dtype="float64",
            rank=1,
            ops={
                **_required_handoff_ops(),
                "shape": lambda _handle: (1,),
                "allocated": lambda _handle: True,
            },
            to_numpy_policy="borrowed_view",
        )


def test_allocatable_handle_requires_generated_allocated_operation():
    with pytest.raises(ValueError, match="requires generated operation 'allocated'"):
        AllocatableHandle(
            dtype="float64",
            rank=1,
            ops={
                **_required_handoff_ops(),
                "shape": lambda _handle: (1,),
                "to_numpy": lambda _handle: None,
            },
        )


def test_pointer_handle_requires_generated_associated_and_nullify_operations():
    with pytest.raises(ValueError, match="requires generated operation 'associated'"):
        PointerHandle(
            dtype="float64",
            rank=1,
            ops={
                **_required_handoff_ops(),
                "shape": lambda _handle: (1,),
                "nullify": lambda _handle: None,
            },
        )
    with pytest.raises(ValueError, match="requires generated operation 'nullify'"):
        PointerHandle(
            dtype="float64",
            rank=1,
            ops={
                **_required_handoff_ops(),
                "shape": lambda _handle: (1,),
                "associated": lambda _handle: True,
            },
        )


def test_common_handle_rejects_invalid_descriptor_ownership():
    with pytest.raises(ValueError, match="descriptor_ownership must be 'borrowed' or 'owned'"):
        AllocatableHandle(dtype="float64", rank=1, ops={}, descriptor_ownership="temporary")


def test_common_handle_rejects_invalid_to_numpy_policy():
    with pytest.raises(ValueError, match="to_numpy_policy must be one of"):
        AllocatableHandle(dtype="float64", rank=1, ops={}, to_numpy_policy="maybe_copy")
