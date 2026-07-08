import pytest
import numpy as np

import x2py
from x2py.runtime_handles import (
    _native_array_actual_for_binding,
    _native_array_descriptor_for_binding,
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


def _common_ops(state: _ArrayState):
    return {
        "shape": lambda _handle: state.shape,
        "to_numpy": lambda _handle: state.value if state.shape is not None else None,
    }


def test_allocatable_handle_uses_common_metadata_shape_owner_and_numpy_dispatch():
    owner = object()
    state = _ArrayState(shape=(2, 3), value=object())
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


def test_allocatable_array_actual_hook_requires_allocated_state_without_to_numpy():
    actual = object()
    calls = []
    state = _ArrayState()
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
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


def test_array_actual_hook_validates_expected_dtype_and_rank():
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=2,
        ops={
            "shape": lambda _handle: (2, 3),
            "allocated": lambda _handle: True,
            "array_actual": lambda _handle: object(),
        },
    )

    with pytest.raises(ValueError, match="expected rank 1"):
        handle._array_actual_for_binding(expected_rank=1)
    with pytest.raises(TypeError, match="expected dtype"):
        handle._array_actual_for_binding(expected_dtype=np.int32)


def test_array_actual_hook_validates_expected_shape_layout_and_writeability():
    actual = object()
    calls = []
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=2,
        ops={
            "shape": lambda _handle: (0, 3),
            "allocated": lambda _handle: True,
            "layout": lambda _handle: "F",
            "writeable": lambda _handle: True,
            "array_actual": lambda _handle: calls.append("array_actual") or actual,
        },
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
    with pytest.raises(ValueError, match="expected layout 'C'"):
        handle._array_actual_for_binding(expected_layout="C")

    read_only = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "shape": lambda _handle: (2,),
            "allocated": lambda _handle: True,
            "writeable": lambda _handle: False,
            "array_actual": lambda _handle: object(),
        },
    )
    with pytest.raises(TypeError, match="must be writeable"):
        read_only._array_actual_for_binding(require_writeable=True)

    missing_writeable = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "shape": lambda _handle: (2,),
            "allocated": lambda _handle: True,
            "array_actual": lambda _handle: object(),
        },
    )
    with pytest.raises(NotImplementedError, match="operation 'writeable' is not available"):
        missing_writeable._array_actual_for_binding(require_writeable=True)


def test_array_actual_hook_validates_native_byte_order_and_alignment_ops():
    actual = object()
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "shape": lambda _handle: (2,),
            "allocated": lambda _handle: True,
            "native_byte_order": lambda _handle: True,
            "aligned": lambda _handle: True,
            "array_actual": lambda _handle: actual,
        },
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
            "shape": lambda _handle: (2,),
            "allocated": lambda _handle: True,
            "native_byte_order": lambda _handle: False,
            "array_actual": lambda _handle: object(),
        },
    )
    with pytest.raises(TypeError, match="native byte order"):
        byte_swapped._array_actual_for_binding(require_native_byte_order=True)

    unaligned = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "shape": lambda _handle: (2,),
            "allocated": lambda _handle: True,
            "aligned": lambda _handle: False,
            "array_actual": lambda _handle: object(),
        },
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
    alloc_actual = object()
    pointer_actual = object()
    calls = []
    alloc_handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
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

    alloc_actual = object()
    pointer_actual = object()
    alloc_handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "shape": lambda _handle: (0,),
            "allocated": lambda _handle: True,
            "array_actual": lambda _handle: alloc_actual,
        },
    )
    pointer_handle = PointerHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "shape": lambda _handle: (0,),
            "associated": lambda _handle: True,
            "array_actual": lambda _handle: pointer_actual,
        },
    )

    assert _native_array_actual_for_binding(alloc_handle, expected_shape=(0,)) is alloc_actual
    assert _native_array_actual_for_binding(pointer_handle, expected_shape=(0,)) is pointer_actual


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
            "shape": lambda _handle: (1,),
            "allocated": lambda _handle: True,
            "descriptor": lambda _handle: object(),
        },
    )
    with pytest.raises(ValueError, match="non-negative"):
        valid_handle._descriptor_for_binding(expected_shape=(-1,))


def test_array_actual_binding_helper_rejects_absent_handles_none_and_non_arrays():
    alloc_handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "shape": lambda _handle: None,
            "allocated": lambda _handle: False,
            "to_numpy": lambda _handle: pytest.fail("array-actual handoff must not call to_numpy"),
            "array_actual": lambda _handle: object(),
        },
    )
    pointer_handle = PointerHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "shape": lambda _handle: None,
            "associated": lambda _handle: False,
            "nullify": lambda _handle: None,
            "to_numpy": lambda _handle: pytest.fail("array-actual handoff must not call to_numpy"),
            "array_actual": lambda _handle: object(),
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
    descriptor = object()
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
    )

    assert handle._descriptor_for_binding(expected_dtype="float64", expected_rank=1) is descriptor
    assert calls == ["descriptor"]


def test_descriptor_hook_validates_expected_dtype_rank_and_current_shape():
    descriptor = object()
    handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=2,
        ops={
            "shape": lambda _handle: (2, 3),
            "allocated": lambda _handle: True,
            "descriptor": lambda _handle: descriptor,
        },
    )

    assert (
        handle._descriptor_for_binding(
            expected_dtype=np.float64,
            expected_rank=2,
            expected_shape=(2, 3),
        )
        is descriptor
    )
    with pytest.raises(ValueError, match="expected rank 1"):
        handle._descriptor_for_binding(expected_rank=1)
    with pytest.raises(TypeError, match="expected dtype"):
        handle._descriptor_for_binding(expected_dtype=np.int32)
    with pytest.raises(ValueError, match=r"expected shape .* axis 1"):
        handle._descriptor_for_binding(expected_shape=(2, 4))


def test_descriptor_binding_helper_accepts_matching_handles_and_optional_none():
    alloc_descriptor = object()
    pointer_descriptor = object()
    alloc_handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "shape": lambda _handle: (0,),
            "allocated": lambda _handle: True,
            "descriptor": lambda _handle: alloc_descriptor,
        },
    )
    pointer_handle = PointerHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "shape": lambda _handle: None,
            "associated": lambda _handle: False,
            "nullify": lambda _handle: None,
            "descriptor": lambda _handle: pointer_descriptor,
        },
    )

    assert (
        _native_array_descriptor_for_binding(
            alloc_handle,
            descriptor_kind="allocatable",
            expected_dtype=np.float64,
            expected_rank=1,
            expected_shape=(0,),
        )
        is alloc_descriptor
    )
    assert (
        _native_array_descriptor_for_binding(
            pointer_handle,
            descriptor_kind="pointer",
            expected_dtype=np.float64,
            expected_rank=1,
        )
        is pointer_descriptor
    )
    assert _native_array_descriptor_for_binding(None, descriptor_kind="pointer", optional=True) is None


def test_descriptor_binding_helper_rejects_plain_arrays_none_and_wrong_kind():
    alloc_handle = AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "shape": lambda _handle: (1,),
            "allocated": lambda _handle: True,
            "descriptor": lambda _handle: object(),
        },
    )

    with pytest.raises(TypeError, match="received ndarray"):
        _native_array_descriptor_for_binding(np.ones(1), descriptor_kind="allocatable")
    with pytest.raises(TypeError, match="received None"):
        _native_array_descriptor_for_binding(None, descriptor_kind="allocatable")
    with pytest.raises(TypeError, match="expected pointer native array handle"):
        _native_array_descriptor_for_binding(alloc_handle, descriptor_kind="pointer")
    with pytest.raises(ValueError, match="unsupported native array descriptor kind"):
        _native_array_descriptor_for_binding(alloc_handle, descriptor_kind="coarray")


def test_pointer_handle_uses_common_base_and_nullify_operation():
    state = _ArrayState(shape=(5,), value=object())

    def nullify(_handle):
        state.shape = None
        state.value = None

    ops = {
        **_common_ops(state),
        "associated": lambda _handle: state.shape is not None,
        "nullify": nullify,
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
    actual = object()
    calls = []
    state = _ArrayState()
    handle = PointerHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
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
            "shape": lambda _handle: (2,),
            "associated": lambda _handle: True,
            "nullify": lambda _handle: None,
        },
    )

    with pytest.raises(NotImplementedError, match="pointer handle operation 'to_numpy' is not available"):
        handle.to_numpy()


def test_pointer_descriptor_view_policy_returns_backend_strided_view():
    source = np.arange(10, dtype=np.float64)
    strided = source[1::2]
    state = _ArrayState(shape=strided.shape, value=strided)
    handle = PointerHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            **_common_ops(state),
            "associated": lambda _handle: True,
            "nullify": lambda _handle: None,
        },
        to_numpy_policy="descriptor_view",
    )

    view = handle.to_numpy()

    assert view is strided
    assert view.strides == strided.strides
    view[0] = 42.0
    assert source[1] == 42.0


def test_to_numpy_policy_unsupported_reports_completed_policy_block():
    handle = PointerHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
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
            "shape": lambda _handle: (4,),
            "to_numpy": lambda _handle: None,
            "allocated": lambda _handle: True,
            "deallocate": lambda _handle: None,
            "resize": lambda _handle, _shape: None,
        },
    )

    with pytest.raises(ValueError, match="shape rank 1 does not match declared rank 2"):
        _ = handle.shape


def test_common_handle_rejects_invalid_descriptor_ownership():
    with pytest.raises(ValueError, match="descriptor_ownership must be 'borrowed' or 'owned'"):
        AllocatableHandle(dtype="float64", rank=1, ops={}, descriptor_ownership="temporary")


def test_common_handle_rejects_invalid_to_numpy_policy():
    with pytest.raises(ValueError, match="to_numpy_policy must be one of"):
        AllocatableHandle(dtype="float64", rank=1, ops={}, to_numpy_policy="maybe_copy")
