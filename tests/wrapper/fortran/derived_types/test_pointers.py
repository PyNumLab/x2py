"""Pointer argument, result, association, and handle-readiness tests."""

import gc
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from tests.wrapper.fortran._support import (
    _build_text_and_import,
    _compile_native_object,
    _import_from_build_dir,
    _build_source_or_generated_pyi_and_import,
    _sole_native_module,
    wrapper_source,
)
from x2py import build_pyi_extension
from x2py.runtime_handles import AllocatableHandle, PointerHandle

POINTERS_F90_SOURCE = wrapper_source("fpointers_f90.f90")
CONTRACT_FIXTURES = Path(__file__).parent / "contracts"
POINTER_HANDLE_SOURCE = """\
module fpointer_handles_f90
  implicit none

  real(8), target :: module_storage(5) = [1.0_8, 2.0_8, 3.0_8, 4.0_8, 5.0_8]
  real(8), target :: field_storage(4) = [6.0_8, 7.0_8, 8.0_8, 9.0_8]
  real(8), pointer :: module_values(:) => null()
  real(8), allocatable, target :: module_allocatable(:)

  type :: pointer_box
    real(8), pointer :: values(:) => null()
  contains
    procedure :: associate_values => box_associate_values
    procedure :: associate_values_strided => box_associate_values_strided
  end type pointer_box

contains

  subroutine associate_module_slice()
    module_values => module_storage(2:5:2)
  end subroutine associate_module_slice

  subroutine associate_module_contiguous()
    module_values => module_storage(2:4)
  end subroutine associate_module_contiguous

  subroutine allocate_module_values()
    if (allocated(module_allocatable)) deallocate(module_allocatable)
    allocate(module_allocatable(3))
    module_allocatable = [10.0_8, 20.0_8, 30.0_8]
  end subroutine allocate_module_values

  subroutine box_associate_values(self)
    class(pointer_box), intent(inout) :: self
    self%values => field_storage(2:4)
  end subroutine box_associate_values

  subroutine box_associate_values_strided(self)
    class(pointer_box), intent(inout) :: self
    self%values => field_storage(1:4:2)
  end subroutine box_associate_values_strided

  function sum_values(values) result(total)
    real(8), intent(in) :: values(:)
    real(8) :: total
    total = sum(values)
  end function sum_values

  function sum_pointer_descriptor(values) result(total)
    real(8), pointer, intent(in) :: values(:)
    real(8) :: total
    if (associated(values)) then
      total = sum(values)
    else
      total = -1.0_8
    end if
  end function sum_pointer_descriptor

  function sum_allocatable_descriptor(values) result(total)
    real(8), allocatable, intent(in) :: values(:)
    real(8) :: total
    if (allocated(values)) then
      total = sum(values)
    else
      total = -1.0_8
    end if
  end function sum_allocatable_descriptor

end module fpointer_handles_f90
"""


def _pointer_handle_module(build_mode: str, tmp_path: Path):
    filename = "fpointer_handles_f90.f90"
    expected_sources = {
        "bind_c_fpointer_handles_f90_wrapper.f90",
        "fpointer_handles_f90_wrapper.c",
        "fpointer_handles_f90_wrapper.h",
    }
    if build_mode == "source":
        source_build_dir = tmp_path / "source_build"
        source_build_dir.mkdir(parents=True)
        return _build_text_and_import(
            POINTER_HANDLE_SOURCE,
            filename,
            source_build_dir,
            expected_sources,
        )

    source_dir = tmp_path / "source"
    source_dir.mkdir(parents=True)
    source = source_dir / filename
    source.write_text(POINTER_HANDLE_SOURCE, encoding="utf-8")
    contract_dir = tmp_path / "contracts" / source.stem
    subprocess.run(
        [sys.executable, "-m", "x2py", str(source), "--pyi", "--out", str(contract_dir)],
        capture_output=True,
        text=True,
        check=True,
    )
    native_object = _compile_native_object(source, tmp_path / "native")
    result = build_pyi_extension(
        contract_dir / "__init__.pyi",
        native_objects=[native_object],
        native_include_dirs=[native_object.parent],
        output_dir=tmp_path / "pyi_build",
    )
    return _sole_native_module(_import_from_build_dir(result.module_name, result.output_dir))


def _pointer_descriptor_view_module(tmp_path: Path):
    source_dir = tmp_path / "source"
    source_dir.mkdir(parents=True)
    source = source_dir / "fpointer_handles_f90.f90"
    source.write_text(POINTER_HANDLE_SOURCE, encoding="utf-8")
    native_object = _compile_native_object(source, tmp_path / "native")
    contract = CONTRACT_FIXTURES / "fpointer_handles_policy" / "__init__.pyi"
    result = build_pyi_extension(
        contract,
        native_objects=[native_object],
        native_include_dirs=[native_object.parent],
        output_dir=tmp_path / "pyi_build",
    )
    return _sole_native_module(_import_from_build_dir(result.module_name, result.output_dir))


def test_module_and_derived_pointer_handles_track_native_association(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _pointer_handle_module(pyi_parity_build_mode, tmp_path)

    module_handle = module.module_values
    assert isinstance(module_handle, PointerHandle)
    assert module_handle.owner.__name__ == module.__name__.split(".", maxsplit=1)[0]
    assert module_handle.associated is False
    assert module_handle.shape is None
    assert module_handle.to_numpy() is None

    module.associate_module_slice()
    assert module.module_values is module_handle
    assert module_handle.associated is True
    assert module_handle.shape == (2,)
    with pytest.raises(ValueError, match="target is noncontiguous"):
        module.sum_values(module_handle)
    with pytest.raises(NotImplementedError, match="to_numpy extraction is unsupported"):
        module_handle.to_numpy()

    module.associate_module_contiguous()
    assert module_handle.shape == (3,)
    assert module.sum_values(module_handle) == np.float64(9.0)

    module_handle.nullify()
    assert module_handle.associated is False
    assert module_handle.shape is None

    owner = module.pointer_box()
    field_handle = owner.values
    assert isinstance(field_handle, PointerHandle)
    assert field_handle.owner is owner
    assert field_handle.associated is False
    assert field_handle.shape is None
    owner.associate_values()
    assert field_handle.associated is True
    assert field_handle.shape == (3,)
    assert module.sum_values(field_handle) == np.float64(24.0)

    owner_id = id(owner)
    del owner
    gc.collect()
    assert id(field_handle.owner) == owner_id
    assert field_handle.associated is True
    field_handle.nullify()
    assert field_handle.associated is False


def test_pointer_descriptor_views_preserve_slice_shape_strides_and_parent_lifetime(tmp_path: Path):
    module = _pointer_descriptor_view_module(tmp_path)

    module_handle = module.module_values
    module.associate_module_slice()
    module_view = module_handle.to_numpy()
    np.testing.assert_allclose(module_view, np.array([2.0, 4.0], dtype=np.float64))
    assert module_view.shape == (2,)
    assert module_view.strides == (16,)
    module_view[1] = np.float64(12.0)
    np.testing.assert_allclose(module_handle.to_numpy(), np.array([2.0, 12.0], dtype=np.float64))
    assert module.sum_pointer_descriptor(module_handle) == np.float64(14.0)

    allocatable_handle = module.module_allocatable
    assert isinstance(allocatable_handle, AllocatableHandle)
    assert allocatable_handle.allocated is False
    assert module.sum_allocatable_descriptor(allocatable_handle) == np.float64(-1.0)
    module.allocate_module_values()
    assert allocatable_handle.allocated is True
    assert module.sum_allocatable_descriptor(allocatable_handle) == np.float64(60.0)

    owner = module.pointer_box()
    owner.associate_values_strided()
    field_handle = owner.values
    field_view = field_handle.to_numpy()
    np.testing.assert_allclose(field_view, np.array([6.0, 8.0], dtype=np.float64))
    assert field_view.shape == (2,)
    assert field_view.strides == (16,)

    del field_handle
    del owner
    gc.collect()
    np.testing.assert_allclose(field_view, np.array([6.0, 8.0], dtype=np.float64))


def test_pointer_array_handles_block_on_unsupported_result_owner_policy(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    with pytest.raises((subprocess.CalledProcessError, ValueError)) as exc_info:
        _build_source_or_generated_pyi_and_import(
            POINTERS_F90_SOURCE,
            tmp_path,
            {
                "bind_c_fpointers_f90_wrapper.f90",
                "fpointers_f90_wrapper.c",
                "fpointers_f90_wrapper.h",
            },
            CONTRACT_FIXTURES / "fpointers_f90",
            pyi_parity_build_mode,
        )

    error = exc_info.value.stderr if isinstance(exc_info.value, subprocess.CalledProcessError) else str(exc_info.value)
    assert "pointer handle results need stable owner storage and target lifetime policy before wrapping" in error
