"""Runtime helpers for native Fortran array descriptor handles."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

import numpy as np


HandleOperation = Callable[..., Any]


class NativeArrayHandleBase:
    """Shared runtime state and operation dispatch for native array handles."""

    _VALID_DESCRIPTOR_OWNERSHIP = frozenset({"borrowed", "owned"})
    _VALID_TO_NUMPY_POLICIES = frozenset(
        {
            "borrowed_view",
            "descriptor_view",
            "read_only_detached_copy",
            "unsupported",
        }
    )

    def __init__(
        self,
        *,
        dtype: Any,
        rank: int,
        ops: Mapping[str, HandleOperation],
        owner: Any = None,
        descriptor_kind: str,
        descriptor_ownership: str,
        to_numpy_policy: str = "borrowed_view",
        generation: int | None = None,
    ) -> None:
        if rank < 0:
            raise ValueError("native array handle rank must be non-negative")
        if descriptor_ownership not in self._VALID_DESCRIPTOR_OWNERSHIP:
            raise ValueError("native array handle descriptor_ownership must be 'borrowed' or 'owned'")
        if to_numpy_policy not in self._VALID_TO_NUMPY_POLICIES:
            raise ValueError(
                f"native array handle to_numpy_policy must be one of {sorted(self._VALID_TO_NUMPY_POLICIES)!r}"
            )
        self._dtype = dtype
        self._rank = int(rank)
        self._ops = dict(ops)
        self._owner = owner
        self._descriptor_kind = descriptor_kind
        self._descriptor_ownership = descriptor_ownership
        self._to_numpy_policy = to_numpy_policy
        self._generation = generation

    @property
    def dtype(self) -> Any:
        return self._dtype

    @property
    def rank(self) -> int:
        return self._rank

    @property
    def shape(self) -> tuple[int, ...] | None:
        shape = self._call_op("shape")
        if shape is None:
            return None
        normalized = self._normalize_shape(shape)
        if len(normalized) != self.rank:
            raise ValueError(
                f"{self.descriptor_kind} handle shape rank {len(normalized)} does not match declared rank {self.rank}"
            )
        return normalized

    @property
    def owner(self) -> Any:
        return self._owner

    @property
    def descriptor_kind(self) -> str:
        return self._descriptor_kind

    @property
    def descriptor_ownership(self) -> str:
        return self._descriptor_ownership

    @property
    def to_numpy_policy(self) -> str:
        return self._to_numpy_policy

    @property
    def borrowed(self) -> bool:
        return self.descriptor_ownership == "borrowed"

    @property
    def owned(self) -> bool:
        return self.descriptor_ownership == "owned"

    @property
    def generation(self) -> int | None:
        return self._generation

    def _array_actual_for_binding(
        self,
        *,
        expected_dtype: Any = None,
        expected_rank: int | None = None,
        expected_shape: Sequence[int | None] | int | None = None,
        expected_layout: str | None = None,
        require_writeable: bool = False,
        require_native_byte_order: bool = False,
        require_aligned: bool = False,
    ) -> Any:
        """Return the generated native array actual after validating handle state."""
        self._validate_array_actual_state()
        if expected_rank is not None and self.rank != int(expected_rank):
            raise ValueError(
                f"{self.descriptor_kind} handle rank {self.rank} does not match expected rank {int(expected_rank)}"
            )
        if expected_dtype is not None and not self._dtype_matches(expected_dtype):
            raise TypeError(
                f"{self.descriptor_kind} handle dtype {self.dtype!r} does not match expected dtype {expected_dtype!r}"
            )
        shape = self.shape
        if shape is None:
            raise ValueError(f"{self.descriptor_kind} handle has no valid array actual")
        self._validate_expected_shape(shape, expected_shape)
        self._validate_expected_layout(expected_layout)
        self._validate_writeable(require_writeable)
        self._validate_native_byte_order(require_native_byte_order)
        self._validate_aligned(require_aligned)
        return self._call_op("array_actual")

    def _descriptor_for_binding(
        self,
        *,
        expected_dtype: Any = None,
        expected_rank: int | None = None,
        expected_shape: Sequence[int | None] | int | None = None,
    ) -> Any:
        """Return the generated native descriptor after validating handle metadata."""
        if expected_rank is not None and self.rank != int(expected_rank):
            raise ValueError(
                f"{self.descriptor_kind} handle rank {self.rank} does not match expected rank {int(expected_rank)}"
            )
        if expected_dtype is not None and not self._dtype_matches(expected_dtype):
            raise TypeError(
                f"{self.descriptor_kind} handle dtype {self.dtype!r} does not match expected dtype {expected_dtype!r}"
            )
        shape = self.shape
        if shape is not None:
            self._validate_expected_shape(shape, expected_shape)
        return self._call_op("descriptor")

    def to_numpy(self) -> Any:
        """Return the current NumPy view/copy, or ``None`` for absent state."""
        if self.to_numpy_policy == "unsupported":
            raise NotImplementedError(
                f"{self.descriptor_kind} handle to_numpy extraction is unsupported by completed policy"
            )
        value = self._call_op("to_numpy")
        if value is None:
            return None
        if self.to_numpy_policy == "read_only_detached_copy":
            return self._read_only_detached_numpy_copy(value)
        return value

    def _call_op(self, name: str, *args: Any) -> Any:
        try:
            operation = self._ops[name]
        except KeyError:
            raise NotImplementedError(f"{self.descriptor_kind} handle operation {name!r} is not available") from None
        return operation(self, *args)

    def _validate_array_actual_state(self) -> None:
        """Validate descriptor-specific presence before native array-actual handoff."""
        raise NotImplementedError(f"{self.descriptor_kind} handle array-actual validation is not available")

    def _dtype_matches(self, expected_dtype: Any) -> bool:
        try:
            return np.dtype(self.dtype) == np.dtype(expected_dtype)
        except TypeError:
            return self.dtype == expected_dtype

    def _validate_expected_shape(
        self,
        shape: tuple[int, ...],
        expected_shape: Sequence[int | None] | int | None,
    ) -> None:
        """Validate a concrete expected shape before native array-actual handoff."""
        if expected_shape is None:
            return
        expected = self._normalize_expected_shape(expected_shape)
        if len(expected) != len(shape):
            raise ValueError(
                f"{self.descriptor_kind} handle shape rank {len(shape)} does not match expected shape rank "
                f"{len(expected)}"
            )
        for axis, (actual, wanted) in enumerate(zip(shape, expected, strict=True)):
            if wanted is not None and actual != wanted:
                raise ValueError(
                    f"{self.descriptor_kind} handle shape {shape!r} does not match expected shape "
                    f"{expected!r} at axis {axis}"
                )

    def _validate_expected_layout(self, expected_layout: str | None) -> None:
        """Validate a required native layout before native array-actual handoff."""
        if expected_layout is None:
            return
        actual_layout = self._call_op("layout")
        if actual_layout != expected_layout:
            raise ValueError(
                f"{self.descriptor_kind} handle layout {actual_layout!r} does not match expected layout "
                f"{expected_layout!r}"
            )

    def _validate_writeable(self, require_writeable: bool) -> None:
        """Validate writeability before native array-actual handoff."""
        if not require_writeable:
            return
        if not bool(self._call_op("writeable")):
            raise TypeError(f"{self.descriptor_kind} handle array actual must be writeable")

    def _validate_native_byte_order(self, require_native_byte_order: bool) -> None:
        """Validate native byte order before native array-actual handoff."""
        if not require_native_byte_order:
            return
        if not bool(self._call_op("native_byte_order")):
            raise TypeError(f"{self.descriptor_kind} handle array actual must use native byte order")

    def _validate_aligned(self, require_aligned: bool) -> None:
        """Validate native alignment before native array-actual handoff."""
        if not require_aligned:
            return
        if not bool(self._call_op("aligned")):
            raise TypeError(f"{self.descriptor_kind} handle array actual must be aligned")

    @staticmethod
    def _normalize_shape(shape: Sequence[int] | int) -> tuple[int, ...]:
        normalized = (int(shape),) if isinstance(shape, int) else tuple(int(dimension) for dimension in shape)
        for dimension in normalized:
            if dimension < 0:
                raise ValueError(f"native array handle shape dimensions must be non-negative; received {normalized!r}")
        return normalized

    @staticmethod
    def _normalize_expected_shape(shape: Sequence[int | None] | int) -> tuple[int | None, ...]:
        if isinstance(shape, int):
            normalized = (int(shape),)
        else:
            normalized = tuple(None if dimension is None else int(dimension) for dimension in shape)
        for dimension in normalized:
            if dimension is not None and dimension < 0:
                raise ValueError(
                    f"expected native array shape dimensions must be non-negative; received {normalized!r}"
                )
        return normalized

    @staticmethod
    def _read_only_detached_numpy_copy(value: Any) -> np.ndarray:
        snapshot = np.array(value, copy=True, order="K")
        snapshot.setflags(write=False)
        return snapshot


class AllocatableHandle(NativeArrayHandleBase):
    """Runtime handle for a native allocatable array descriptor."""

    def __init__(
        self,
        *,
        dtype: Any,
        rank: int,
        ops: Mapping[str, HandleOperation],
        owner: Any = None,
        descriptor_ownership: str = "borrowed",
        to_numpy_policy: str = "borrowed_view",
        generation: int | None = None,
    ) -> None:
        super().__init__(
            dtype=dtype,
            rank=rank,
            ops=ops,
            owner=owner,
            descriptor_kind="allocatable",
            descriptor_ownership=descriptor_ownership,
            to_numpy_policy=to_numpy_policy,
            generation=generation,
        )

    @property
    def allocated(self) -> bool:
        return bool(self._call_op("allocated"))

    def _validate_array_actual_state(self) -> None:
        if not self.allocated:
            raise ValueError("allocatable handle is unallocated and cannot be passed as an array actual")

    def deallocate(self) -> Any:
        return self._call_op("deallocate")

    def resize(self, shape: Sequence[int] | int) -> Any:
        return self._call_op("resize", self._normalize_shape(shape))


class PointerHandle(NativeArrayHandleBase):
    """Runtime handle for a native pointer array descriptor."""

    def __init__(
        self,
        *,
        dtype: Any,
        rank: int,
        ops: Mapping[str, HandleOperation],
        owner: Any = None,
        descriptor_ownership: str = "borrowed",
        to_numpy_policy: str = "borrowed_view",
        generation: int | None = None,
    ) -> None:
        super().__init__(
            dtype=dtype,
            rank=rank,
            ops=ops,
            owner=owner,
            descriptor_kind="pointer",
            descriptor_ownership=descriptor_ownership,
            to_numpy_policy=to_numpy_policy,
            generation=generation,
        )

    @property
    def associated(self) -> bool:
        return bool(self._call_op("associated"))

    def _validate_array_actual_state(self) -> None:
        if not self.associated:
            raise ValueError("pointer handle is unassociated and cannot be passed as an array actual")

    def nullify(self) -> Any:
        return self._call_op("nullify")

    def allocate(self, shape: Sequence[int] | int) -> Any:
        return self._call_op("allocate", self._normalize_shape(shape))

    def deallocate(self) -> Any:
        return self._call_op("deallocate")

    def resize(self, shape: Sequence[int] | int) -> Any:
        return self._call_op("resize", self._normalize_shape(shape))


def _native_array_actual_for_binding(
    value: Any,
    *,
    expected_dtype: Any = None,
    expected_rank: int | None = None,
    expected_shape: Sequence[int | None] | int | None = None,
    expected_layout: str | None = None,
    require_writeable: bool = False,
    require_native_byte_order: bool = False,
    require_aligned: bool = False,
) -> Any:
    """Return an ndarray or generated native array actual for a normal array argument."""
    if isinstance(value, NativeArrayHandleBase):
        return value._array_actual_for_binding(
            expected_dtype=expected_dtype,
            expected_rank=expected_rank,
            expected_shape=expected_shape,
            expected_layout=expected_layout,
            require_writeable=require_writeable,
            require_native_byte_order=require_native_byte_order,
            require_aligned=require_aligned,
        )
    if isinstance(value, np.ndarray):
        _validate_ndarray_array_actual(
            value,
            expected_dtype=expected_dtype,
            expected_rank=expected_rank,
            expected_shape=expected_shape,
            expected_layout=expected_layout,
            require_writeable=require_writeable,
            require_native_byte_order=require_native_byte_order,
            require_aligned=require_aligned,
        )
        return value
    if value is None:
        raise TypeError("normal array argument is required; received None")
    raise TypeError(f"expected NumPy array or native array handle argument; received {type(value).__name__}")


def _native_array_descriptor_for_binding(
    value: Any,
    *,
    descriptor_kind: str,
    expected_dtype: Any = None,
    expected_rank: int | None = None,
    expected_shape: Sequence[int | None] | int | None = None,
    optional: bool = False,
) -> Any:
    """Return a generated native descriptor for a handle-typed binding argument."""
    if value is None:
        if optional:
            return None
        raise TypeError(f"{descriptor_kind} native array handle argument is required; received None")
    try:
        expected_type = {
            "allocatable": AllocatableHandle,
            "pointer": PointerHandle,
        }[descriptor_kind]
    except KeyError:
        raise ValueError(f"unsupported native array descriptor kind: {descriptor_kind!r}") from None
    if not isinstance(value, expected_type):
        raise TypeError(f"expected {descriptor_kind} native array handle argument; received {type(value).__name__}")
    return value._descriptor_for_binding(
        expected_dtype=expected_dtype,
        expected_rank=expected_rank,
        expected_shape=expected_shape,
    )


def _validate_ndarray_array_actual(
    value: np.ndarray,
    *,
    expected_dtype: Any = None,
    expected_rank: int | None = None,
    expected_shape: Sequence[int | None] | int | None = None,
    expected_layout: str | None = None,
    require_writeable: bool = False,
    require_native_byte_order: bool = False,
    require_aligned: bool = False,
) -> None:
    _validate_ndarray_expected_rank(value, expected_rank)
    _validate_ndarray_expected_dtype(value, expected_dtype)
    _validate_ndarray_expected_shape(tuple(int(dimension) for dimension in value.shape), expected_shape)
    _validate_ndarray_expected_layout(value, expected_layout)
    _validate_ndarray_writeable(value, require_writeable)
    _validate_ndarray_native_byte_order(value, require_native_byte_order)
    _validate_ndarray_aligned(value, require_aligned)


def _validate_ndarray_expected_rank(value: np.ndarray, expected_rank: int | None) -> None:
    if expected_rank is not None and value.ndim != int(expected_rank):
        raise ValueError(f"NumPy array rank {value.ndim} does not match expected rank {int(expected_rank)}")


def _validate_ndarray_expected_dtype(value: np.ndarray, expected_dtype: Any) -> None:
    if expected_dtype is not None and np.dtype(value.dtype) != np.dtype(expected_dtype):
        raise TypeError(f"NumPy array dtype {value.dtype!r} does not match expected dtype {np.dtype(expected_dtype)!r}")


def _validate_ndarray_writeable(value: np.ndarray, require_writeable: bool) -> None:
    if require_writeable and not value.flags.writeable:
        raise TypeError("NumPy array actual must be writeable")


def _validate_ndarray_native_byte_order(value: np.ndarray, require_native_byte_order: bool) -> None:
    if require_native_byte_order and not value.dtype.isnative:
        raise TypeError("NumPy array actual must use native byte order")


def _validate_ndarray_aligned(value: np.ndarray, require_aligned: bool) -> None:
    if require_aligned and not value.flags.aligned:
        raise TypeError("NumPy array actual must be aligned")


def _validate_ndarray_expected_shape(
    shape: tuple[int, ...],
    expected_shape: Sequence[int | None] | int | None,
) -> None:
    if expected_shape is None:
        return
    expected = NativeArrayHandleBase._normalize_expected_shape(expected_shape)
    if len(expected) != len(shape):
        raise ValueError(f"NumPy array shape rank {len(shape)} does not match expected shape rank {len(expected)}")
    for axis, (actual, wanted) in enumerate(zip(shape, expected, strict=True)):
        if wanted is not None and actual != wanted:
            raise ValueError(f"NumPy array shape {shape!r} does not match expected shape {expected!r} at axis {axis}")


def _validate_ndarray_expected_layout(value: np.ndarray, expected_layout: str | None) -> None:
    if expected_layout is None:
        return
    required = expected_layout.upper()
    if required == "F":
        matches = value.flags.f_contiguous
    elif required == "C":
        matches = value.flags.c_contiguous
    else:
        raise ValueError(f"unsupported expected NumPy array layout {expected_layout!r}")
    if not matches:
        raise ValueError(f"NumPy array layout does not match expected layout {expected_layout!r}")


__all__ = (
    "AllocatableHandle",
    "NativeArrayHandleBase",
    "PointerHandle",
)
