import pytest

from x2py.runtime_handles import AllocatableHandle, NativeArrayHandleBase, PointerHandle


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
