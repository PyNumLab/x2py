"""Allocatable ``intent(inout)`` replacement and ownership tests."""

import gc
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from x2py.runtime_handles import AllocatableHandle
from tests.wrapper.fortran._support import (
    WRAPPER_TEST_ROOT,
    _build_source_or_generated_pyi_and_import,
    wrapper_source,
)

ALLOCATABLE_INOUT_F90_SOURCE = wrapper_source("fallocatable_inout_f90.f90")
ALLOCATABLE_FACTORY_F90_SOURCE = wrapper_source("fallocatable_views_f90.f90")
CONTRACT_FIXTURES = Path(__file__).parent / "contracts"


def _allocatable_replacement_build_dir(tmp_path: Path, build_mode: str) -> Path:
    if build_mode == "source":
        return tmp_path / "source_build"
    return tmp_path / "generated_pyi_build" / "pyi_build"


def _build_allocatable_factory(build_mode: str, tmp_path: Path):
    return _build_source_or_generated_pyi_and_import(
        ALLOCATABLE_FACTORY_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fallocatable_views_f90_wrapper.f90",
            "fallocatable_views_f90_wrapper.c",
            "fallocatable_views_f90_wrapper.h",
        },
        CONTRACT_FIXTURES / "fallocatable_views_f90",
        build_mode,
    )


def test_allocatable_inout_arrays_mutate_and_return_the_same_handle(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _build_source_or_generated_pyi_and_import(
        ALLOCATABLE_INOUT_F90_SOURCE,
        tmp_path / "replacement",
        {
            "bind_c_fallocatable_inout_f90_wrapper.f90",
            "fallocatable_inout_f90_wrapper.c",
            "fallocatable_inout_f90_wrapper.h",
        },
        CONTRACT_FIXTURES / "fallocatable_inout_f90",
        pyi_parity_build_mode,
    )

    factory = _build_allocatable_factory(pyi_parity_build_mode, tmp_path / "factory")

    assert "replace_values(values, mode) -> AllocatableHandle[float64]" in module.replace_values.__doc__
    assert "values : AllocatableHandle[float64]" in module.replace_values.__doc__

    values = factory.build_values(np.int32(2))
    assert isinstance(values, AllocatableHandle)
    returned = module.replace_values(values, np.int32(1))
    assert returned is values
    np.testing.assert_allclose(values.to_numpy(), np.array([12.0, 14.0], dtype=np.float64))

    returned = module.replace_values(values, np.int32(3))
    assert returned is values
    np.testing.assert_allclose(values.to_numpy(), np.array([3.0, 6.0, 9.0], dtype=np.float64))

    returned = module.replace_values(values, np.int32(0))
    assert returned is values
    assert values.allocated is False
    assert values.to_numpy() is None

    returned = module.replace_values(values, np.int32(1))
    assert returned is values
    np.testing.assert_allclose(values.to_numpy(), np.array([1.0, 2.0], dtype=np.float64))

    del values
    gc.collect()

    with pytest.raises(TypeError):
        module.replace_values(np.array([1.0], dtype=np.float32), np.int32(1))
    with pytest.raises(TypeError):
        module.replace_values(np.array([[1.0]], dtype=np.float64), np.int32(1))


@pytest.mark.skipif(shutil.which("valgrind") is None, reason="Valgrind is required for native ownership checks")
def test_allocatable_replacement_has_no_native_memory_errors(pyi_parity_build_mode: str, tmp_path: Path):
    _build_source_or_generated_pyi_and_import(
        ALLOCATABLE_INOUT_F90_SOURCE,
        tmp_path / "replacement",
        {
            "bind_c_fallocatable_inout_f90_wrapper.f90",
            "fallocatable_inout_f90_wrapper.c",
            "fallocatable_inout_f90_wrapper.h",
        },
        CONTRACT_FIXTURES / "fallocatable_inout_f90",
        pyi_parity_build_mode,
    )
    _build_allocatable_factory(pyi_parity_build_mode, tmp_path / "factory")
    build_dir = _allocatable_replacement_build_dir(tmp_path / "replacement", pyi_parity_build_mode)
    factory_build_dir = _allocatable_replacement_build_dir(tmp_path / "factory", pyi_parity_build_mode)
    script = f"""
import gc
import numpy as np
import sys

sys.path.insert(0, {str(factory_build_dir)!r})
import fallocatable_inout_f90 as module
import fallocatable_views_f90 as factory

module = module.fallocatable_inout_f90
factory = factory.fallocatable_views_f90
value = factory.build_values(np.int32(2))

for mode in (1, 2, 0) * 50:
    returned = module.replace_values(value, np.int32(mode))
    assert returned is value
value.close()
gc.collect()
"""
    result = subprocess.run(
        [
            "valgrind",
            "--quiet",
            f"--suppressions={WRAPPER_TEST_ROOT / 'valgrind.supp'}",
            "--error-exitcode=99",
            "--leak-check=full",
            "--show-leak-kinds=definite",
            "--errors-for-leak-kinds=definite",
            "--track-origins=yes",
            sys.executable,
            "-c",
            script,
        ],
        cwd=build_dir,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
