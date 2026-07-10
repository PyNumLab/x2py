"""Optional argument runtime wrapper tests."""

from pathlib import Path

import numpy as np
import pytest

from x2py import build_pyi_extension
from tests.wrapper.fortran._support import (
    _compile_native_object,
    _build_source_or_generated_pyi_and_import,
    _import_from_build_dir,
    _sole_native_module,
    wrapper_source,
)
from x2py.runtime_handles import _NativeArrayHandoff, AllocatableHandle, PointerHandle

OPTIONAL_F90_SOURCE = wrapper_source("foptional_f90.f90")
OPTIONAL_FIXED_SOURCE = wrapper_source("foptional_fixed.f")
CONTRACT_FIXTURES = Path(__file__).parent / "contracts"


def _unallocated_handle_for_rejected_optional_array():
    return AllocatableHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "array_actual": lambda _handle: pytest.fail("optional array path must reject handles before handoff"),
            "descriptor": lambda _handle: _NativeArrayHandoff(501),
            "shape": lambda _handle: None,
            "to_numpy": lambda _handle: None,
            "allocated": lambda _handle: False,
            "deallocate": lambda _handle: None,
            "resize": lambda _handle, _shape: None,
        },
    )


def _unassociated_handle_for_rejected_optional_array():
    return PointerHandle(
        dtype=np.dtype(np.float64),
        rank=1,
        ops={
            "array_actual": lambda _handle: pytest.fail("optional array path must reject handles before handoff"),
            "descriptor": lambda _handle: _NativeArrayHandoff(502),
            "shape": lambda _handle: None,
            "to_numpy": lambda _handle: None,
            "associated": lambda _handle: False,
            "nullify": lambda _handle: None,
        },
    )


def test_optional_allocatable_scalar_descriptor_distinguishes_omitted_none_and_value(tmp_path: Path):
    source = tmp_path / "scalar_optional_descriptors.f90"
    source.write_text(
        """
module scalar_optional_descriptors
contains
  integer(4) function alloc_state(value) result(state)
    real(8), allocatable, optional, intent(in) :: value

    if (.not. present(value)) then
      state = 0
    else if (.not. allocated(value)) then
      state = 1
    else if (abs(value - 2.5_8) < 1.0e-12_8) then
      state = 2
    else
      state = -1
    end if
  end function alloc_state
end module scalar_optional_descriptors
""",
        encoding="utf-8",
    )
    native_object = _compile_native_object(source, tmp_path / "native")
    contract_dir = tmp_path / "contracts"
    contract_dir.mkdir()
    entry = contract_dir / "scalar_optional_descriptors.pyi"
    entry.write_text(
        """
from x2py.contracts import Allocatable, Annotated, Arg, Float64, Immutable, Int32, native_call

@native_call([Allocatable(Arg(0))])
def alloc_state(value: Annotated[Float64, Immutable] | None = ...) -> Int32: ...
""",
        encoding="utf-8",
    )

    result = build_pyi_extension(
        entry,
        native_objects=[native_object],
        native_include_dirs=[native_object.parent],
        output_dir=tmp_path / "pyi_build",
    )
    module = _sole_native_module(_import_from_build_dir(result.module_name, result.output_dir))

    assert module.alloc_state() == np.int32(0)
    assert module.alloc_state(None) == np.int32(1)
    assert module.alloc_state(np.float64(2.5)) == np.int32(2)
    assert "Omit to make the native optional dummy absent." in module.alloc_state.__doc__
    assert "Pass None for a present unallocated or unassociated descriptor." in module.alloc_state.__doc__
    assert "Default is None." not in module.alloc_state.__doc__


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
    assert module.optional_status(np.int32(8)) == (np.int32(8), None)
    assert module.optional_status(np.int32(8), None) == (np.int32(8), None)
    status = np.empty((), dtype=np.int32)
    returned_base, returned_status = module.optional_status(np.int32(8), status)
    assert returned_base == np.int32(8)
    assert returned_status is status
    assert status[()] == np.int32(58)

    with pytest.raises(TypeError):
        module.summarize(np.int32(5), scale="bad")
    with pytest.raises(TypeError):
        module.fill_optional(np.int32(3), np.empty(3, dtype=np.float32))
    with pytest.raises(TypeError):
        module.fill_optional(np.int32(3), _unallocated_handle_for_rejected_optional_array())
    with pytest.raises(TypeError):
        module.fill_optional(np.int32(3), _unassociated_handle_for_rejected_optional_array())


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
