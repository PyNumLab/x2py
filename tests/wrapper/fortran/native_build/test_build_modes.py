"""Verbose direct-build and default output-location tests."""

import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests.wrapper.fortran._support import _assert_fmath_examples, _sole_native_module, wrapper_source
from x2py.preprocessing import PreprocessingConfig
from x2py.wrapping import build_fortran_extension

VERBOSE_SOURCE = wrapper_source("verbose_api.f90")
DEFAULT_OUTPUT_SOURCE = wrapper_source("fdefault_output.f")
SCALAR_SOURCE = wrapper_source("fmath.f")


def test_verbose_mode_prints_full_direct_build_commands(tmp_path: Path):
    source = tmp_path / "verbose_api.f90"
    shutil.copyfile(VERBOSE_SOURCE, source)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(source),
            "--verbose",
            "--out-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    command_lines = result.stdout.splitlines()

    assert any(str(source) in line and "-c" in line for line in command_lines)
    assert any("bind_c_verbose_api_wrapper.f90" in line and "-c" in line for line in command_lines)
    assert any("verbose_api_wrapper.c" in line and "-c" in line for line in command_lines)
    assert any("-shared" in line and "verbose_api" in line for line in command_lines)
    assert "Built extension:" in result.stdout


def test_fortran_wrapper_default_places_extension_beside_source(tmp_path: Path):
    source = tmp_path / DEFAULT_OUTPUT_SOURCE.name
    shutil.copyfile(DEFAULT_OUTPUT_SOURCE, source)

    cmd = [sys.executable, "-m", "x2py", str(source), "--json"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)

    build_dir = tmp_path / "__x2py__"
    shared_library = Path(payload["shared_library"])
    assert shared_library.parent == tmp_path
    assert shared_library.exists()
    assert Path(payload["output_dir"]) == build_dir
    assert (build_dir / "bind_c_fdefault_output_wrapper.f90").exists()
    assert not list(tmp_path.glob("*_wrapper.c"))


def test_internal_preprocessing_mode_still_builds_importable_runtime_wrapper(tmp_path: Path):
    source = tmp_path / SCALAR_SOURCE.name
    build_dir = tmp_path / "build"
    shutil.copyfile(SCALAR_SOURCE, source)

    result = build_fortran_extension(
        source,
        output_dir=build_dir,
        preprocessing=PreprocessingConfig(),
    )

    assert result.compiled is True
    assert result.build_makefile is None
    assert any(
        path.name == "python_runtime.c" and path.parent.name == "x2py_runtime" for path in result.generated_files
    )

    sys.modules.pop(result.module_name, None)
    sys.path.insert(0, str(build_dir))
    try:
        module = _sole_native_module(importlib.import_module(result.module_name))
    finally:
        sys.path.remove(str(build_dir))
    _assert_fmath_examples(module)


def test_wrapper_build_rejects_empty_source_list(tmp_path: Path):
    with pytest.raises(ValueError, match="at least one Fortran source"):
        build_fortran_extension([], output_dir=tmp_path)


def test_wrapper_build_rejects_missing_source(tmp_path: Path):
    missing = tmp_path / "missing.f90"

    with pytest.raises(FileNotFoundError, match="Fortran source not found"):
        build_fortran_extension(missing, output_dir=tmp_path)


def test_wrapper_build_rejects_makefile_verbose_combination(tmp_path: Path):
    source = tmp_path / DEFAULT_OUTPUT_SOURCE.name
    shutil.copyfile(DEFAULT_OUTPUT_SOURCE, source)

    with pytest.raises(ValueError, match="makefile generation and verbose direct compilation"):
        build_fortran_extension(source, output_dir=tmp_path, makefile=True, verbose=True)
