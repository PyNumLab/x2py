"""Maintainer replay command coverage for retained wrapper-plan artifacts."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests.wrapper.fortran._support import REPO_ROOT


@pytest.mark.parametrize("entry", ("source", "pyi"))
def test_maintainer_replay_command_retains_dual_route_fmath_evidence(tmp_path: Path, entry: str):
    if shutil.which("gfortran") is None:
        pytest.skip("gfortran is required for maintained wrapper-plan replay")

    output_dir = tmp_path / entry
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.replay_wrapper_plan",
            "--entry",
            entry,
            "--unit",
            "fmath",
            "--output-dir",
            str(output_dir),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Retained wrapper-plan replay:" in result.stdout
    assert (output_dir / "legacy").is_dir()
    assert (output_dir / "wrapper-plan").is_dir()

    route_report = (output_dir / "route-report.txt").read_text(encoding="utf-8")
    assert f"entry={entry}" in route_report
    assert "legacy.selected_route=legacy" in route_report
    assert "wrapper-plan.selected_route=wrapper-plan" in route_report
    assert "artifact_names_equal=true" in route_report
    assert "runtime_assertions=passed" in route_report
    assert "conversion_failure_parity=passed" in route_report
