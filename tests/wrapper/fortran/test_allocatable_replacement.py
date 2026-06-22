"""Allocatable ``intent(inout)`` replacement and ownership tests."""

import gc
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from tests.wrapper.fortran._support import (
    _build_text_and_import,
)

ALLOCATABLE_INOUT_F90_TEXT = Path(__file__).with_name("fallocatable_inout_f90.f90").read_text(encoding="utf-8")


def test_allocatable_inout_arrays_are_replaced_with_python_owned_results(tmp_path: Path):
    module = _build_text_and_import(
        ALLOCATABLE_INOUT_F90_TEXT,
        "fallocatable_inout_f90.f90",
        tmp_path,
        {
            "bind_c_fallocatable_inout_f90_wrapper.f90",
            "fallocatable_inout_f90_wrapper.c",
            "fallocatable_inout_f90_wrapper.h",
        },
    )

    assert "values : ndarray[float64] or None" in module.replace_values.__doc__
    assert "May be passed as None for initially unallocated storage." in module.replace_values.__doc__
    assert "Mutates: no; returns a replacement array or None" in module.replace_values.__doc__

    allocated = module.replace_values(None, np.int32(1))
    np.testing.assert_allclose(allocated, np.array([1.0, 2.0], dtype=np.float64))
    assert allocated.base is not None

    original = np.array([3.0, 4.0], dtype=np.float64)
    replaced = module.replace_values(original, np.int32(1))
    np.testing.assert_allclose(original, np.array([3.0, 4.0], dtype=np.float64))
    np.testing.assert_allclose(replaced, np.array([13.0, 14.0], dtype=np.float64))

    reallocated = module.replace_values(original, np.int32(3))
    np.testing.assert_allclose(original, np.array([3.0, 4.0], dtype=np.float64))
    np.testing.assert_allclose(reallocated, np.array([3.0, 6.0, 9.0], dtype=np.float64))

    assert module.replace_values(reallocated, np.int32(0)) is None
    assert module.replace_values(None, np.int32(0)) is None

    del allocated, replaced, reallocated
    gc.collect()

    for mode in (1, 2, 0) * 5:
        transient = module.replace_values(None, np.int32(mode))
        del transient
        gc.collect()

    with pytest.raises(TypeError):
        module.replace_values(np.array([1.0], dtype=np.float32), np.int32(1))
    with pytest.raises(TypeError):
        module.replace_values(np.array([[1.0]], dtype=np.float64), np.int32(1))


@pytest.mark.skipif(shutil.which("valgrind") is None, reason="Valgrind is required for native ownership checks")
def test_allocatable_replacement_has_no_native_memory_errors(tmp_path: Path):
    _build_text_and_import(
        ALLOCATABLE_INOUT_F90_TEXT,
        "fallocatable_inout_f90.f90",
        tmp_path,
        {
            "bind_c_fallocatable_inout_f90_wrapper.f90",
            "fallocatable_inout_f90_wrapper.c",
            "fallocatable_inout_f90_wrapper.h",
        },
    )
    script = """
import gc
import numpy as np
import fallocatable_inout_f90 as module
module = module.fallocatable_inout_f90

for mode in (1, 2, 0) * 50:
    value = module.replace_values(None, np.int32(mode))
    del value
gc.collect()
"""
    result = subprocess.run(
        [
            "valgrind",
            "--quiet",
            f"--suppressions={Path(__file__).with_name('valgrind.supp')}",
            "--error-exitcode=99",
            "--leak-check=full",
            "--show-leak-kinds=definite",
            "--errors-for-leak-kinds=definite",
            "--track-origins=yes",
            sys.executable,
            "-c",
            script,
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
