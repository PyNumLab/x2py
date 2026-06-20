"""Verbose direct-build and default output-location tests."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

VERBOSE_SOURCE = Path(__file__).with_name("verbose_api.f90")
DEFAULT_OUTPUT_SOURCE = Path(__file__).with_name("fdefault_output.f")


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
