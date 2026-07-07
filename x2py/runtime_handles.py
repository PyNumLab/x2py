"""Runtime helpers for native Fortran array descriptor handles."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any


HandleOperation = Callable[..., Any]


class NativeArrayHandleBase:
    """Shared runtime state and operation dispatch for native array handles."""

    _VALID_DESCRIPTOR_OWNERSHIP = frozenset({"borrowed", "owned"})

    def __init__(
        self,
        *,
        dtype: Any,
        rank: int,
        ops: Mapping[str, HandleOperation],
        owner: Any = None,
        descriptor_kind: str,
        descriptor_ownership: str,
        generation: int | None = None,
    ) -> None:
        if rank < 0:
            raise ValueError("native array handle rank must be non-negative")
        if descriptor_ownership not in self._VALID_DESCRIPTOR_OWNERSHIP:
            raise ValueError("native array handle descriptor_ownership must be 'borrowed' or 'owned'")
        self._dtype = dtype
        self._rank = int(rank)
        self._ops = dict(ops)
        self._owner = owner
        self._descriptor_kind = descriptor_kind
        self._descriptor_ownership = descriptor_ownership
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
    def borrowed(self) -> bool:
        return self.descriptor_ownership == "borrowed"

    @property
    def owned(self) -> bool:
        return self.descriptor_ownership == "owned"

    @property
    def generation(self) -> int | None:
        return self._generation

    def to_numpy(self) -> Any:
        """Return the current NumPy view/copy, or ``None`` for absent state."""
        return self._call_op("to_numpy")

    def _call_op(self, name: str, *args: Any) -> Any:
        try:
            operation = self._ops[name]
        except KeyError:
            raise NotImplementedError(f"{self.descriptor_kind} handle operation {name!r} is not available") from None
        return operation(self, *args)

    @staticmethod
    def _normalize_shape(shape: Sequence[int] | int) -> tuple[int, ...]:
        if isinstance(shape, int):
            return (shape,)
        return tuple(int(dimension) for dimension in shape)


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
        generation: int | None = None,
    ) -> None:
        super().__init__(
            dtype=dtype,
            rank=rank,
            ops=ops,
            owner=owner,
            descriptor_kind="allocatable",
            descriptor_ownership=descriptor_ownership,
            generation=generation,
        )

    @property
    def allocated(self) -> bool:
        return bool(self._call_op("allocated"))

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
        generation: int | None = None,
    ) -> None:
        super().__init__(
            dtype=dtype,
            rank=rank,
            ops=ops,
            owner=owner,
            descriptor_kind="pointer",
            descriptor_ownership=descriptor_ownership,
            generation=generation,
        )

    @property
    def associated(self) -> bool:
        return bool(self._call_op("associated"))

    def nullify(self) -> Any:
        return self._call_op("nullify")

    def allocate(self, shape: Sequence[int] | int) -> Any:
        return self._call_op("allocate", self._normalize_shape(shape))

    def deallocate(self) -> Any:
        return self._call_op("deallocate")

    def resize(self, shape: Sequence[int] | int) -> Any:
        return self._call_op("resize", self._normalize_shape(shape))


__all__ = (
    "AllocatableHandle",
    "NativeArrayHandleBase",
    "PointerHandle",
)
