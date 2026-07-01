"""Allocatable result, module-array, and component-view ownership tests."""

import gc
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from tests.wrapper.fortran._support import (
    _build_source_or_generated_pyi_and_import,
    _build_text_and_import,
    _compile_native_object,
    _import_from_build_dir,
    _sole_native_module,
    wrapper_source,
)
from x2py import build_pyi_extension

ALLOCATABLE_VIEW_F90_SOURCE = wrapper_source("fallocatable_views_f90.f90")
CONTRACT_FIXTURES = Path(__file__).parent / "contracts"
PLAIN_ALLOCATABLE_MODULE_SOURCE = """\
module fallocatable_snapshot_f90
  implicit none
  real(8), allocatable :: values(:)
contains
  subroutine allocate_values(n)
    integer(4), intent(in) :: n
    integer(4) :: i

    if (allocated(values)) deallocate(values)
    allocate(values(n))
    values = [(1.0_8 * i, i = 1, n)]
  end subroutine allocate_values

  subroutine scale_values(scale)
    real(8), intent(in) :: scale

    values = scale * values
  end subroutine scale_values

  subroutine deallocate_values()
    if (allocated(values)) deallocate(values)
  end subroutine deallocate_values
end module fallocatable_snapshot_f90
"""


def _plain_allocatable_snapshot_module(build_mode: str, tmp_path: Path):
    filename = "fallocatable_snapshot_f90.f90"
    if build_mode == "source":
        source_build_dir = tmp_path / "source_build"
        source_build_dir.mkdir(parents=True)
        module = _build_text_and_import(
            PLAIN_ALLOCATABLE_MODULE_SOURCE,
            filename,
            source_build_dir,
            {
                "bind_c_fallocatable_snapshot_f90_wrapper.f90",
                "fallocatable_snapshot_f90_wrapper.c",
                "fallocatable_snapshot_f90_wrapper.h",
            },
        )
        return module, (source_build_dir / "fallocatable_snapshot_f90_wrapper.c").read_text(encoding="utf-8")

    source_dir = tmp_path / "source"
    source_dir.mkdir(parents=True)
    source = source_dir / filename
    source.write_text(PLAIN_ALLOCATABLE_MODULE_SOURCE, encoding="utf-8")
    contract_dir = tmp_path / "contracts" / source.stem
    subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(source),
            "--pyi",
            "--out",
            str(contract_dir),
        ],
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
    module = _sole_native_module(_import_from_build_dir(result.module_name, result.output_dir))
    return module, (result.output_dir / "fallocatable_snapshot_f90_wrapper.c").read_text(encoding="utf-8")


def test_allocatable_module_and_derived_type_arrays_are_borrowed_views(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _build_source_or_generated_pyi_and_import(
        ALLOCATABLE_VIEW_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fallocatable_views_f90_wrapper.f90",
            "fallocatable_views_f90_wrapper.c",
            "fallocatable_views_f90_wrapper.h",
        },
        CONTRACT_FIXTURES / "fallocatable_views_f90",
        pyi_parity_build_mode,
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
    assert not hasattr(module, "get_module_values")
    assert "Fields" in module.buffer.__doc__
    assert "values : ndarray[float64] or None" in module.buffer.__doc__
    assert "Ownership: Wrapper-owned" in module.buffer.values.__doc__

    assert module.module_values is None
    module.allocate_module_values(np.int32(3))
    module_values = module.module_values
    np.testing.assert_allclose(module_values, np.array([1.0, 2.0, 3.0], dtype=np.float64))

    module_values[0] = np.float64(10.0)
    assert module.module_values_sum() == np.float64(15.0)
    module.scale_module_values(np.float64(2.0))
    np.testing.assert_allclose(module_values, np.array([20.0, 4.0, 6.0], dtype=np.float64))

    module.deallocate_module_values()
    assert module.module_values is None

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


def test_plain_allocatable_module_array_is_read_only_snapshot(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module, wrapper_source_text = _plain_allocatable_snapshot_module(pyi_parity_build_mode, tmp_path)

    assert (
        "Plain allocatable module arrays without Aliased are copied into Python-owned NumPy arrays."
        in wrapper_source_text
    )
    assert "Returned snapshots are read-only and detached from later native changes." in wrapper_source_text

    assert module.values is None
    module.allocate_values(np.int32(3))

    snapshot = module.values
    np.testing.assert_allclose(snapshot, np.array([1.0, 2.0, 3.0], dtype=np.float64))
    assert snapshot.flags.writeable is False
    with pytest.raises(ValueError, match="read-only"):
        snapshot[0] = np.float64(9.0)

    module.scale_values(np.float64(2.0))
    np.testing.assert_allclose(snapshot, np.array([1.0, 2.0, 3.0], dtype=np.float64))

    fresh = module.values
    assert fresh.flags.writeable is False
    np.testing.assert_allclose(fresh, np.array([2.0, 4.0, 6.0], dtype=np.float64))

    module.deallocate_values()
    assert module.values is None
