"""Derived-type callback argument and result conversion tests."""

from pathlib import Path

import numpy as np

from tests.wrapper.fortran._support import _build_text_and_import

CALLBACK_DERIVED_F90_TEXT = Path(__file__).with_name("fcallback_derived_f90.f90").read_text(encoding="utf-8")


def test_immediate_dummy_procedure_converts_derived_arguments_and_results(tmp_path: Path):
    module = _build_text_and_import(
        CALLBACK_DERIVED_F90_TEXT,
        "fcallback_derived_f90.f90",
        tmp_path,
        {
            "bind_c_fcallback_derived_f90_wrapper.f90",
            "fcallback_derived_f90_wrapper.c",
            "fcallback_derived_f90_wrapper.h",
        },
    )
    point = module.point_t(x=np.float64(2.0), y=np.float64(5.0))

    result = module.apply_point(
        lambda value: module.point_t(x=value.x + 1.0, y=value.y * 2.0),
        point,
    )
    assert isinstance(result, module.point_t)
    assert result.x == np.float64(3.0)
    assert result.y == np.float64(10.0)
