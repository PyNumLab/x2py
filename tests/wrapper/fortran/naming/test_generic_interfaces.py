"""Generic procedure interface runtime wrapper tests."""

from pathlib import Path

import numpy as np
import pytest

from tests.wrapper.fortran._support import (
    _build_source_or_generated_pyi_and_import,
    wrapper_source,
)

OVERLOAD_F90_SOURCE = wrapper_source("foverloads_f90.f90")
OVERLOAD_FIXED_SOURCE = wrapper_source("foverloads_fixed.f")
CONTRACT_FIXTURES = Path(__file__).parent / "contracts"


def test_fortran_generic_interfaces_dispatch_in_generated_c_extension(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _build_source_or_generated_pyi_and_import(
        OVERLOAD_F90_SOURCE,
        tmp_path,
        {
            "bind_c_foverloads_f90_wrapper.f90",
            "foverloads_f90_wrapper.c",
            "foverloads_f90_wrapper.h",
        },
        CONTRACT_FIXTURES / "foverloads_f90",
        pyi_parity_build_mode,
    )

    assert module.convert(np.int32(4)) == np.int32(14)
    assert module.convert(np.float64(4.0)) == np.float64(4.5)
    assert module.convert(np.complex128(2.0 + 3.0j)) == np.complex128(3.0 + 2.0j)
    assert module.summarize(np.float64(2.5)) == np.float64(2.5)
    assert module.summarize(np.array([1.0, 2.0, 3.0], dtype=np.float64)) == np.float64(6.0)

    value = module.accumulator()
    value.add(np.int32(2))
    value.add(np.float64(0.5))
    assert value.total == np.float64(2.5)
    assert module.inspect(value) == np.float64(2.5)

    sample = module.sample()
    sample.value = np.float64(7.25)
    assert module.inspect(sample) == np.float64(7.25)

    with pytest.raises(TypeError):
        module.convert("not numeric")
    with pytest.raises(TypeError):
        value.add(np.complex128(1.0 + 0.0j))


def test_fixed_form_fortran_generic_interface_dispatches_in_generated_c_extension(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _build_source_or_generated_pyi_and_import(
        OVERLOAD_FIXED_SOURCE,
        tmp_path,
        {
            "bind_c_foverloads_fixed_wrapper.f90",
            "foverloads_fixed_wrapper.c",
            "foverloads_fixed_wrapper.h",
        },
        CONTRACT_FIXTURES / "foverloads_fixed",
        pyi_parity_build_mode,
    )

    assert module.convert(np.int32(2)) == np.int32(22)
    assert module.convert(np.float64(2.0)) == np.float64(2.25)
    with pytest.raises(TypeError):
        module.convert(np.complex128(2.0 + 0.0j))
