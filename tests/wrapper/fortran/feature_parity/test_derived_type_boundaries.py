"""Scalar derived-type arguments, results, fields, and lifetime tests."""

import gc
from pathlib import Path

import numpy as np

from tests.wrapper.fortran._support import (
    wrapper_source,
    _build_text_and_import,
)

DERIVED_BOUNDARY_F90_TEXT = wrapper_source("fderived_boundary_f90.f90").read_text(encoding="utf-8")


def test_scalar_derived_types_cross_procedure_boundaries(tmp_path: Path):
    module = _build_text_and_import(
        DERIVED_BOUNDARY_F90_TEXT,
        "fderived_boundary_f90.f90",
        tmp_path,
        {
            "bind_c_fderived_boundary_f90_wrapper.f90",
            "fderived_boundary_f90_wrapper.c",
            "fderived_boundary_f90_wrapper.h",
        },
    )

    point = module.point()
    point.x = np.float64(1.0)
    point.y = np.float64(2.0)
    assert not hasattr(point, "hidden")
    assert module.point_sum(point) == np.float64(3.0)

    identity = id(point)
    assert module.move_point(point, np.float64(4.0), np.float64(5.0)) is None
    assert id(point) == identity
    assert point.x == np.float64(5.0)
    assert point.y == np.float64(7.0)

    out_point = module.make_point_out(np.float64(8.0), np.float64(9.0))
    assert isinstance(out_point, module.point)
    assert out_point.x == np.float64(8.0)
    assert out_point.y == np.float64(9.0)

    result_point = module.make_point(np.float64(10.0), np.float64(11.0))
    assert isinstance(result_point, module.point)
    assert result_point.x == np.float64(10.0)
    assert result_point.y == np.float64(11.0)

    holder = module.holder()
    holder.scale = np.float64(2.5)
    assert module.set_holder_origin(holder, result_point) is None
    origin = holder.origin
    assert isinstance(origin, module.point)
    assert origin.x == np.float64(10.0)
    origin.x = np.float64(12.0)
    assert module.holder_origin_x(holder) == np.float64(12.0)

    del holder
    gc.collect()
    assert origin.x == np.float64(12.0)
