"""Array shape, rank, mutability, dtype, alignment, and byte-order tests."""

from pathlib import Path

import numpy as np
import pytest
from numpy.lib.stride_tricks import as_strided

from tests.wrapper._support import (
    _build_text_and_import,
)

ARRAY_CONTRACTS_F90_TEXT = Path(__file__).with_name("farray_contracts_f90.f90").read_text(encoding="utf-8")
_MAX_WRAPPER_TEST_RANK = 15


def test_remaining_array_contracts_are_validated_before_fortran_calls(tmp_path: Path):
    module = _build_text_and_import(
        ARRAY_CONTRACTS_F90_TEXT,
        "farray_contracts_f90.f90",
        tmp_path,
        {
            "bind_c_farray_contracts_f90_wrapper.f90",
            "farray_contracts_f90_wrapper.c",
            "farray_contracts_f90_wrapper.h",
        },
    )

    readonly = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float64)
    readonly.setflags(write=False)
    assert module.sum_assumed_size(np.int32(4), readonly) == np.float64(10.0)
    assert module.sum_in(readonly) == np.float64(10.0)

    lower_bound_values = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float64)
    assert module.scale_lower(np.int32(4), lower_bound_values) is None
    np.testing.assert_allclose(lower_bound_values, np.array([2.0, 4.0, 6.0, 8.0], dtype=np.float64))
    with pytest.raises(TypeError, match="incompatible shape at axis 0"):
        module.scale_lower(np.int32(4), np.ones(3, dtype=np.float64))

    with pytest.raises(TypeError, match="writeable"):
        module.bump_inout(readonly)
    readonly_out = np.empty(4, dtype=np.float64)
    readonly_out.setflags(write=False)
    with pytest.raises(TypeError, match="writeable"):
        module.fill_out(readonly_out)

    swapped_dtype = np.dtype(np.float64).newbyteorder("S")
    swapped = np.array([1.0, 2.0], dtype=swapped_dtype)
    with pytest.raises(TypeError, match="native byte order"):
        module.sum_in(swapped)

    storage = np.zeros(8 * 4 + 1, dtype=np.uint8)
    misaligned = storage[1:].view(np.float64)
    assert not misaligned.flags.aligned
    with pytest.raises(TypeError, match="aligned"):
        module.sum_in(misaligned)

    with pytest.raises(TypeError, match="dtype"):
        module.sum_in(np.array([1.0, 2.0], dtype=np.float32))

    empty_rank4 = np.empty((0, 1, 1, 1), dtype=np.float64, order="F")
    empty_rank4_out = np.empty_like(empty_rank4, order="F")
    assert module.shift4(empty_rank4, empty_rank4_out) is empty_rank4_out
    assert empty_rank4_out.shape == empty_rank4.shape

    zero_stride_empty = as_strided(
        np.empty(1, dtype=np.float64),
        shape=empty_rank4.shape,
        strides=(0, 0, 0, 0),
    )
    zero_stride_empty_out = as_strided(
        np.empty(1, dtype=np.float64),
        shape=empty_rank4.shape,
        strides=(0, 0, 0, 0),
    )
    assert zero_stride_empty.flags.f_contiguous
    assert zero_stride_empty_out.flags.f_contiguous
    assert module.shift4(zero_stride_empty, zero_stride_empty_out) is zero_stride_empty_out

    for rank in range(1, _MAX_WRAPPER_TEST_RANK + 1):
        shape = (2, *([1] * (rank - 1)))
        source = np.asfortranarray(np.arange(np.prod(shape), dtype=np.float64).reshape(shape, order="F"))
        out = np.empty(shape, dtype=np.float64, order="F")

        assert getattr(module, f"shift{rank}")(source, out) is out
        np.testing.assert_allclose(out, source + rank)
