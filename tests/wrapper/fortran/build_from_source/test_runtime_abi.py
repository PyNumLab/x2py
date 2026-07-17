"""Debug and optimized native wrapper ABI tests."""

import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from tests.wrapper.fortran._support import _build_text_and_import, _sole_native_module, wrapper_source

RUNTIME_ABI_SOURCE = wrapper_source("fruntime_abi_f90.f90")


@pytest.mark.skipif(
    sys.platform == "win32" or shutil.which("make") is None,
    reason="optimized wrapper ABI smoke test requires GNU Make and a POSIX shell",
)
def test_debug_and_optimized_wrapper_builds_preserve_runtime_abi(tmp_path: Path):
    source_text = RUNTIME_ABI_SOURCE.read_text(encoding="utf-8")
    expected_generated_sources = {
        "bind_c_fruntime_abi_f90_wrapper.f90",
        "fruntime_abi_f90_wrapper.c",
        "fruntime_abi_f90_wrapper.h",
    }
    debug_dir = tmp_path / "debug"
    optimized_dir = tmp_path / "optimized"
    debug_dir.mkdir()
    optimized_dir.mkdir()

    debug_module = _build_text_and_import(
        source_text,
        "fruntime_abi_f90.f90",
        debug_dir,
        expected_generated_sources,
    )
    assert debug_module.scale(np.float64(3.0), np.float64(2.5)) == np.float64(7.5)

    optimized_source = optimized_dir / "fruntime_abi_f90.f90"
    optimized_source.write_text(source_text, encoding="utf-8")
    generated = subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(optimized_source),
            "--makefile",
            "--out-dir",
            str(optimized_dir),
            "--json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(generated.stdout)
    makefile = Path(payload["build_makefile"])
    subprocess.run(
        [
            "make",
            "-j4",
            "-f",
            str(makefile),
            "all",
            "X2PY_FFLAGS=-O3",
            "X2PY_CFLAGS=-O3",
            "X2PY_LDFLAGS=-O3",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    sys.modules.pop("fruntime_abi_f90", None)
    sys.path.insert(0, str(optimized_dir))
    try:
        optimized_module = _sole_native_module(importlib.import_module("fruntime_abi_f90"))
        assert optimized_module.scale(np.float64(4.0), np.float64(1.25)) == np.float64(5.0)
    finally:
        sys.path.remove(str(optimized_dir))
