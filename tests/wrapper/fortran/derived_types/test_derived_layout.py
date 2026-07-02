"""Derived-type layout and interoperability runtime wrapper tests."""

from pathlib import Path

import numpy as np

from tests.wrapper.fortran._support import (
    _build_source_or_generated_pyi_and_import,
    wrapper_source,
)

BIND_C_DERIVED_LAYOUT_F90_SOURCE = wrapper_source("fbind_c_derived_layout_f90.f90")
CONTRACT_FIXTURES = Path(__file__).parent / "contracts"


def test_bind_c_derived_types_use_accessors_and_fortran_value_copy(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _build_source_or_generated_pyi_and_import(
        BIND_C_DERIVED_LAYOUT_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fbind_c_derived_layout_f90_wrapper.f90",
            "fbind_c_derived_layout_f90_wrapper.c",
            "fbind_c_derived_layout_f90_wrapper.h",
        },
        CONTRACT_FIXTURES / "fbind_c_derived_layout_f90",
        pyi_parity_build_mode,
    )

    if pyi_parity_build_mode == "source":
        bridge_source = (tmp_path / "source_build" / "bind_c_fbind_c_derived_layout_f90_wrapper.f90").read_text()

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
