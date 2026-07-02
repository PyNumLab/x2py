"""Optional argument runtime wrapper tests."""

from pathlib import Path

import numpy as np
import pytest

from tests.wrapper.fortran._support import (
    _build_source_or_generated_pyi_and_import,
    wrapper_source,
)

OPTIONAL_F90_SOURCE = wrapper_source("foptional_f90.f90")
OPTIONAL_FIXED_SOURCE = wrapper_source("foptional_fixed.f")
CONTRACT_FIXTURES = Path(__file__).parent / "contracts"


def test_optional_arguments_drive_fortran_present_behavior(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _build_source_or_generated_pyi_and_import(
        OPTIONAL_F90_SOURCE,
        tmp_path,
        {
            "bind_c_foptional_f90_wrapper.f90",
            "foptional_f90_wrapper.c",
            "foptional_f90_wrapper.h",
        },
        CONTRACT_FIXTURES / "foptional_f90",
        pyi_parity_build_mode,
    )

    assert "scale : int32 or None" in module.summarize.__doc__
    assert "May be omitted or passed as None." in module.summarize.__doc__

    values = np.array([1.0, 2.0, 3.0], dtype=np.float64)
    item = module.sample()
    item.value = np.int32(7)

    assert module.summarize(np.int32(5)) == np.int32(5)
    assert module.summarize(np.int32(5), np.int32(4)) == np.int32(9)
    assert module.summarize(np.int32(5), None) == np.int32(5)
    assert module.summarize(np.int32(5), scale=None) == np.int32(5)
    assert module.summarize(np.int32(5), values=values) == np.int32(11)
    assert module.summarize(np.int32(5), label="trimmed") == np.int32(12)
    assert module.summarize(np.int32(5), item=item) == np.int32(12)
    assert module.summarize(np.int32(5), item=item, values=values, label="abc") == np.int32(21)
    assert module.summarize(np.int32(5), None, values=values, item=item) == np.int32(18)

    mutable = np.array([1.0, 2.0], dtype=np.float64)
    assert module.mutate_optional() is None
    assert module.mutate_optional(None, np.float64(100.0)) is None
    assert module.mutate_optional(mutable) is None
    np.testing.assert_allclose(mutable, np.array([2.0, 3.0], dtype=np.float64))
    assert module.mutate_optional(mutable, None) is None
    np.testing.assert_allclose(mutable, np.array([3.0, 4.0], dtype=np.float64))
    assert module.mutate_optional(mutable, np.float64(2.5)) is None
    np.testing.assert_allclose(mutable, np.array([5.5, 6.5], dtype=np.float64))

    output = np.empty(3, dtype=np.float64)
    returned_output = module.fill_optional(np.int32(3), output)
    assert returned_output is output
    np.testing.assert_allclose(output, np.array([11.0, 12.0, 13.0], dtype=np.float64))
    assert module.fill_optional(np.int32(3)) is None
    assert module.fill_optional(np.int32(3), None) is None
    assert module.optional_status(np.int32(8)) == (np.int32(8), np.int32(58))

    with pytest.raises(TypeError):
        module.summarize(np.int32(5), scale="bad")
    with pytest.raises(TypeError):
        module.fill_optional(np.int32(3), np.empty(3, dtype=np.float32))


def test_fixed_form_optional_arguments_drive_fortran_present_behavior(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _build_source_or_generated_pyi_and_import(
        OPTIONAL_FIXED_SOURCE,
        tmp_path,
        {
            "bind_c_foptional_fixed_wrapper.f90",
            "foptional_fixed_wrapper.c",
            "foptional_fixed_wrapper.h",
        },
        CONTRACT_FIXTURES / "foptional_fixed",
        pyi_parity_build_mode,
    )

    assert module.optional_scale(np.int32(3)) == np.int32(3)
    assert module.optional_scale(np.int32(3), np.int32(4)) == np.int32(7)
    assert module.optional_scale(np.int32(3), None) == np.int32(3)
    assert module.optional_scale(base=np.int32(3), factor=np.int32(6)) == np.int32(9)
