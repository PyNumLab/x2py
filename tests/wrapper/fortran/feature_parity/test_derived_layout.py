"""Derived-type layout and interoperability runtime wrapper tests."""

from pathlib import Path

import numpy as np

from tests.wrapper.fortran._support import (
    wrapper_source,
    _build_text_and_import,
)

BIND_C_DERIVED_LAYOUT_F90_TEXT = wrapper_source("fbind_c_derived_layout_f90.f90").read_text(encoding="utf-8")


def test_bind_c_derived_types_use_accessors_and_fortran_value_copy(tmp_path: Path):
    module = _build_text_and_import(
        BIND_C_DERIVED_LAYOUT_F90_TEXT,
        "fbind_c_derived_layout_f90.f90",
        tmp_path,
        {
            "bind_c_fbind_c_derived_layout_f90_wrapper.f90",
            "fbind_c_derived_layout_f90_wrapper.c",
            "fbind_c_derived_layout_f90_wrapper.h",
        },
    )
    bridge_source = (tmp_path / "bind_c_fbind_c_derived_layout_f90_wrapper.f90").read_text()

    assert "function tagged_point_position_getter" in bridge_source
    assert "subroutine tagged_point_position_setter" in bridge_source
    assert "function tagged_point_weight_getter" in bridge_source
    assert "subroutine tagged_point_weight_setter" in bridge_source
    assert "type(c_ptr), value :: bound_value" in bridge_source
    assert "type(tagged_point), pointer :: value_0001" in bridge_source

    value = module.tagged_point()
    module.populate(
        value,
        np.float64(2.5),
        np.int32(4),
        np.complex128(3.0 + 2.0j),
    )

    position = value.position
    assert position.x == np.float64(2.5)
    assert position.axis == np.int32(4)
    assert value.weight == np.complex128(3.0 + 2.0j)

    assert module.score_by_value(value) == np.float64(109.5)
    assert position.x == np.float64(2.5)
