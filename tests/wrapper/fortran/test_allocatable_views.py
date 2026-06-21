"""Allocatable result, module-array, and component-view ownership tests."""

import gc
from pathlib import Path

import numpy as np
import pytest

from tests.wrapper.fortran._support import _build_and_import

ALLOCATABLE_VIEW_F90_SOURCE = Path(__file__).with_name("fallocatable_views_f90.f90")


def test_allocatable_module_and_derived_type_arrays_are_borrowed_views(tmp_path: Path):
    module = _build_and_import(
        ALLOCATABLE_VIEW_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fallocatable_views_f90_wrapper.f90",
            "fallocatable_views_f90_wrapper.c",
            "fallocatable_views_f90_wrapper.h",
        },
    )

    assert "Functions" in module.__doc__
    assert "build_values" in module.__doc__
    assert "buffer" in module.__doc__
    assert "build_values(n) -> ndarray[float64] | None" in module.build_values.__doc__
    assert "n : int32" in module.build_values.__doc__
    assert "Intent: in" in module.build_values.__doc__
    assert "values : ndarray[float64] or None" in module.build_values.__doc__
    assert "Rank: 1" in module.build_values.__doc__
    assert "Ownership: Python-owned" in module.build_values.__doc__
    assert "Returns None when unallocated." in module.build_values.__doc__
    assert "TypeError" in module.build_values.__doc__
    assert "Rank: 2" in module.build_matrix.__doc__
    assert "Layout: F-contiguous" in module.build_matrix.__doc__
    assert "get_module_values() -> ndarray[float64] | None" in module.get_module_values.__doc__
    assert "Ownership: Native-owned" in module.get_module_values.__doc__
    assert "zero-copy view of native Fortran memory" in module.get_module_values.__doc__
    assert "Fields" in module.buffer.__doc__
    assert "values : ndarray[float64] or None" in module.buffer.__doc__
    assert "Ownership: Wrapper-owned" in module.buffer.values.__doc__

    assert module.get_module_values() is None
    module.allocate_module_values(np.int32(3))
    module_values = module.get_module_values()
    np.testing.assert_allclose(module_values, np.array([1.0, 2.0, 3.0], dtype=np.float64))

    module_values[0] = np.float64(10.0)
    assert module.module_values_sum() == np.float64(15.0)
    module.scale_module_values(np.float64(2.0))
    np.testing.assert_allclose(module_values, np.array([20.0, 4.0, 6.0], dtype=np.float64))

    module.deallocate_module_values()
    assert module.get_module_values() is None

    built_values = module.build_values(np.int32(4))
    np.testing.assert_allclose(built_values, np.array([2.0, 4.0, 6.0, 8.0], dtype=np.float64))
    built_values[0] = np.float64(-1.0)
    np.testing.assert_allclose(built_values, np.array([-1.0, 4.0, 6.0, 8.0], dtype=np.float64))
    assert module.build_values(np.int32(0)) is None

    built_matrix = module.build_matrix(np.int32(2), np.int32(2))
    np.testing.assert_allclose(
        built_matrix,
        np.array([[11.0, 21.0], [12.0, 22.0]], dtype=np.float64),
    )
    assert module.build_matrix(np.int32(0), np.int32(2)) is None

    made_values = module.make_values(np.int32(3))
    np.testing.assert_allclose(made_values, np.array([3.0, 6.0, 9.0], dtype=np.float64))
    assert module.make_values(np.int32(0)) is None

    made_matrix = module.make_matrix(np.int32(2), np.int32(2))
    np.testing.assert_allclose(
        made_matrix,
        np.array([[111.0, 121.0], [112.0, 122.0]], dtype=np.float64),
    )
    assert module.make_matrix(np.int32(2), np.int32(0)) is None

    values = module.buffer()
    assert values.values is None
    values.allocate_values(np.int32(3))
    field_view = values.values
    assert field_view.base is values
    np.testing.assert_allclose(field_view, np.array([1.0, 2.0, 3.0], dtype=np.float64))

    field_view[1] = np.float64(8.0)
    assert values.values_sum() == np.float64(12.0)
    values.scale_values(np.float64(0.5))
    np.testing.assert_allclose(field_view, np.array([0.5, 4.0, 1.5], dtype=np.float64))

    with pytest.raises(AttributeError, match="Can't reallocate memory"):
        values.values = np.array([1.0, 2.0], dtype=np.float64)

    retained_view = values.values
    del values
    gc.collect()
    np.testing.assert_allclose(retained_view, np.array([0.5, 4.0, 1.5], dtype=np.float64))

    owner = retained_view.base
    owner.deallocate_values()
    assert owner.values is None
