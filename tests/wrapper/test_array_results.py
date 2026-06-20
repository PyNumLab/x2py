"""Array-valued function result runtime wrapper tests."""

import gc
from pathlib import Path

import numpy as np

from tests.wrapper._support import (
    _build_text_and_import,
)

ARRAY_RESULTS_F90_TEXT = Path(__file__).with_name("farray_results_f90.f90").read_text(encoding="utf-8")
_MAX_WRAPPER_TEST_RANK = 15


def test_array_valued_function_results_are_python_owned_copies(tmp_path: Path):
    module = _build_text_and_import(
        ARRAY_RESULTS_F90_TEXT,
        "farray_results_f90.f90",
        tmp_path,
        {
            "bind_c_farray_results_f90_wrapper.f90",
            "farray_results_f90_wrapper.c",
            "farray_results_f90_wrapper.h",
        },
    )

    fixed = module.fixed_vector()
    np.testing.assert_allclose(fixed, np.array([1.0, 2.0, 3.0], dtype=np.float64))
    assert fixed.base is not None

    automatic = module.automatic_vector(np.int32(4))
    np.testing.assert_allclose(automatic, np.array([2.0, 4.0, 6.0, 8.0], dtype=np.float64))
    assert automatic.base is not None

    matrix = module.automatic_matrix(np.int32(2), np.int32(3))
    np.testing.assert_allclose(
        matrix,
        np.array([[12.0, 13.0, 14.0], [22.0, 23.0, 24.0]], dtype=np.float64),
    )
    assert matrix.flags.f_contiguous
    assert matrix.base is not None

    cube = module.rank3_cube(np.int32(2), np.int32(2), np.int32(2))
    expected_cube = np.empty((2, 2, 2), dtype=np.float64, order="F")
    for i, j, k in np.ndindex(expected_cube.shape):
        expected_cube[i, j, k] = 100.0 * (i + 1) + 10.0 * (j + 1) + (k + 1)
    np.testing.assert_allclose(cube, expected_cube)
    assert cube.flags.f_contiguous

    rank_results = []
    for rank in range(1, _MAX_WRAPPER_TEST_RANK + 1):
        result = getattr(module, f"rank{rank}_result")()
        shape = (2, *([1] * (rank - 1)))
        expected = np.full(shape, float(rank), dtype=np.float64, order="F")
        expected[(1, *([0] * (rank - 1)))] = float(rank) + 0.5

        assert result.shape == shape
        assert result.flags.f_contiguous
        assert result.base is not None
        np.testing.assert_allclose(result, expected)
        rank_results.append((result, expected))

    zero = module.zero_vector()
    assert zero.shape == (0,)
    assert zero.dtype == np.dtype(np.float64)
    assert zero.base is not None

    zero_alloc = module.zero_alloc_vector()
    assert zero_alloc.shape == (0,)
    assert zero_alloc.base is not None

    allocated = module.maybe_alloc_vector(np.int32(3))
    np.testing.assert_allclose(allocated, np.array([5.0, 10.0, 15.0], dtype=np.float64))
    assert allocated.base is not None
    assert module.maybe_alloc_vector(np.int32(0)) is None

    del module
    gc.collect()
    np.testing.assert_allclose(matrix, np.array([[12.0, 13.0, 14.0], [22.0, 23.0, 24.0]], dtype=np.float64))
    np.testing.assert_allclose(cube, expected_cube)
    for result, expected in rank_results:
        np.testing.assert_allclose(result, expected)
