"""Output argument and multiple-result runtime wrapper tests."""

from pathlib import Path

import numpy as np
import pytest

from x2py.runtime_handles import AllocatableHandle
from tests.wrapper.fortran._support import (
    _build_source_or_generated_pyi_and_import,
    wrapper_source,
)

OUTPUTS_F90_SOURCE = wrapper_source("foutputs_f90.f90")
CONTRACT_FIXTURES = Path(__file__).parent / "contracts"


def test_output_arguments_and_multiple_results_follow_python_projection_rules(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _build_source_or_generated_pyi_and_import(
        OUTPUTS_F90_SOURCE,
        tmp_path,
        {
            "bind_c_foutputs_f90_wrapper.f90",
            "foutputs_f90_wrapper.c",
            "foutputs_f90_wrapper.h",
        },
        CONTRACT_FIXTURES / "foutputs_f90",
        pyi_parity_build_mode,
    )

    assert "scalar_status(n) -> int32" in module.scalar_status.__doc__
    assert "status : int32" in module.scalar_status.__doc__
    assert "fill_vector(n, values) -> ndarray[float64]" in module.fill_vector.__doc__
    assert "Direction:" not in module.fill_vector.__doc__
    assert "Initial contents are ignored." not in module.fill_vector.__doc__
    assert "Ownership: Caller-owned" in module.fill_vector.__doc__
    assert "build_alloc(n) -> AllocatableHandle[float64]" in module.build_alloc.__doc__
    assert "Descriptor ownership: owned" in module.build_alloc.__doc__
    assert "Unallocated state remains inside the returned handle." in module.build_alloc.__doc__
    assert "make_label() -> str" in module.make_label.__doc__
    assert "make_point(scale) -> output_point" in module.make_point.__doc__

    assert module.scalar_status(np.int32(5)) == np.int32(15)

    vector = np.empty(4, dtype=np.float64)
    returned_vector = module.fill_vector(np.int32(4), vector)
    assert returned_vector is vector
    np.testing.assert_allclose(vector, np.array([2.0, 4.0, 6.0, 8.0], dtype=np.float64))

    matrix = np.empty((2, 3), dtype=np.float64, order="F")
    returned_matrix = module.fill_matrix(np.int32(2), np.int32(3), matrix)
    assert returned_matrix is matrix
    np.testing.assert_allclose(
        matrix,
        np.array([[11.0, 21.0, 31.0], [12.0, 22.0, 32.0]], dtype=np.float64),
    )

    allocated = module.build_alloc(np.int32(3))
    assert isinstance(allocated, AllocatableHandle)
    assert allocated.owned is True
    np.testing.assert_allclose(allocated.to_numpy(), np.array([3.0, 6.0, 9.0], dtype=np.float64))
    unallocated = module.build_alloc(np.int32(0))
    assert isinstance(unallocated, AllocatableHandle)
    assert unallocated.allocated is False
    assert unallocated.to_numpy() is None

    assert module.with_scalar(np.int32(4)) == (np.int32(8), np.int32(7))

    mixed_vector = np.empty(3, dtype=np.float64)
    mixed_result = module.mixed_outputs(np.int32(3), mixed_vector)
    assert mixed_result[0] == np.float64(3.5)
    assert mixed_result[1] is mixed_vector
    assert mixed_result[2] == np.int32(23)
    np.testing.assert_allclose(mixed_result[1], np.array([101.0, 102.0, 103.0], dtype=np.float64))
    assert isinstance(mixed_result[3], AllocatableHandle)
    np.testing.assert_allclose(
        mixed_result[3].to_numpy(),
        np.array([201.0, 202.0, 203.0], dtype=np.float64),
    )

    inout_values = np.array([1.0, 2.0], dtype=np.float64)
    assert module.increment(inout_values) is None
    np.testing.assert_allclose(inout_values, np.array([2.0, 3.0], dtype=np.float64))
    assert module.increment_with_status(inout_values) == np.int32(2)
    np.testing.assert_allclose(inout_values, np.array([4.0, 5.0], dtype=np.float64))

    assert module.make_label() == "RESULT!!"

    point = module.make_point(np.int32(6))
    assert isinstance(point, module.output_point)
    assert point.x == np.float64(6.25)
    assert point.tag == np.int32(46)

    with pytest.raises(TypeError):
        module.scalar_status(np.int32(1), np.int32(0))
    with pytest.raises(TypeError):
        module.build_alloc(np.int32(2), np.empty(2, dtype=np.float64))
    with pytest.raises(TypeError):
        module.fill_vector(np.int32(4), np.empty(4, dtype=np.float32))
    with pytest.raises(TypeError):
        module.fill_vector(np.int32(4), np.empty((4, 1), dtype=np.float64))
    with pytest.raises(TypeError):
        module.fill_vector(np.int32(4), np.empty(3, dtype=np.float64))
    with pytest.raises(TypeError):
        module.fill_matrix(np.int32(2), np.int32(3), np.empty((2, 3), dtype=np.float64, order="C"))
