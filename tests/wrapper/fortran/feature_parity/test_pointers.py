"""Pointer argument, result, association, and snapshot tests."""

import gc
from pathlib import Path

import numpy as np
import pytest

from tests.wrapper.fortran._support import (
    wrapper_source,
    _build_text_and_import,
)

POINTERS_F90_TEXT = wrapper_source("fpointers_f90.f90").read_text(encoding="utf-8")


def test_pointer_arrays_use_call_local_inputs_and_snapshot_results(tmp_path: Path):
    module = _build_text_and_import(
        POINTERS_F90_TEXT,
        "fpointers_f90.f90",
        tmp_path,
        {
            "bind_c_fpointers_f90_wrapper.f90",
            "fpointers_f90_wrapper.c",
            "fpointers_f90_wrapper.h",
        },
    )

    values = np.array([1.0, 2.0, 3.0], dtype=np.float64)
    assert module.read_pointer(np.float64(4.5)) == np.float64(4.5)
    assert module.pointer_to_scalar(np.float64(7.25), np.int32(1)) == np.float64(7.25)
    assert module.pointer_to_scalar(np.float64(7.25), np.int32(0)) is None
    assert "pointer_to_scalar(value, use_value) -> float64 | None" in module.pointer_to_scalar.__doc__
    assert "Pointer scalar results are copied into detached Python values." in module.pointer_to_scalar.__doc__
    assert "Unassociated pointer results return None." in module.pointer_to_scalar.__doc__

    assert module.sum_pointer(values) == np.float64(6.0)

    selected = module.pointer_to_values(values, np.int32(1))
    np.testing.assert_allclose(selected, values)
    assert selected.base is not None

    second_snapshot = module.pointer_to_values(values, np.int32(1))
    assert not np.shares_memory(selected, second_snapshot)

    selected[0] = np.float64(99.0)
    np.testing.assert_allclose(values, np.array([1.0, 2.0, 3.0], dtype=np.float64))
    np.testing.assert_allclose(second_snapshot, values)

    assert module.pointer_to_values(values, np.int32(0)) is None
    assert "pointer_to_values(values, use_values) -> ndarray[float64] | None" in module.pointer_to_values.__doc__
    assert "Pointer array results are copied into Python-owned NumPy arrays." in module.pointer_to_values.__doc__
    assert "Unassociated pointer results return None." in module.pointer_to_values.__doc__

    del values
    gc.collect()
    np.testing.assert_allclose(selected, np.array([99.0, 2.0, 3.0], dtype=np.float64))

    with pytest.raises(TypeError):
        module.sum_pointer(np.array([1.0, 2.0, 3.0], dtype=np.float32))
