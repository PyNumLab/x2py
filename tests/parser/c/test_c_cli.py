# -*- coding: utf-8 -*-
"""Planned C parser CLI tests.

These tests mirror the Fortran CLI coverage but stay skipped until the C CLI
skeleton exists. Unskip one test group at a time as the explicit C mode lands.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skip(
    reason="C parser CLI roadmap tests; unskip with the matching C CLI implementation branch."
)


def test_cli_help_shows_explicit_c_language_mode():
    cmd = [sys.executable, "-m", "x2py", "--help"]

    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    assert "--language" in res.stdout
    assert "c" in res.stdout


def test_cli_c_parse_human_tree_output_for_header(tmp_path: Path):
    header = tmp_path / "api.h"
    header.write_text("int add(int a, int b);\n", encoding="utf-8")
    cmd = [sys.executable, "-m", "x2py", str(header), "--language", "c", "--parse"]

    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    assert f"File: {header}" in res.stdout
    assert "Language: c" in res.stdout
    assert "Functions: 1" in res.stdout
    assert "add" in res.stdout


def test_cli_c_parse_json_stdout_for_header(tmp_path: Path):
    header = tmp_path / "api.h"
    header.write_text("int add(int a, int b);\n", encoding="utf-8")
    cmd = [sys.executable, "-m", "x2py", str(header), "--language", "c", "--parse", "--json"]

    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(res.stdout)

    assert payload[str(header)]["language"] == "c"
    assert payload[str(header)]["functions"][0]["name"] == "add"


def test_cli_c_parse_json_out_writes_file_and_suppresses_stdout(tmp_path: Path):
    header = tmp_path / "api.h"
    output = tmp_path / "report.json"
    header.write_text("double scale(double x);\n", encoding="utf-8")
    cmd = [
        sys.executable,
        "-m",
        "x2py",
        str(header),
        "--language",
        "c",
        "--parse",
        "--json",
        "--out",
        str(output),
    ]

    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert res.stdout == ""
    assert payload[str(header)]["functions"][0]["name"] == "scale"


def test_cli_c_wrap_readiness_output_uses_fortran_diagnostic_shape(tmp_path: Path):
    header = tmp_path / "api.h"
    header.write_text("int add(int a, int b);\n", encoding="utf-8")
    cmd = [
        sys.executable,
        "-m",
        "x2py",
        str(header),
        "--language",
        "c",
        "--parse",
        "--wrap-readiness",
    ]

    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    assert "Wrappable:" in res.stdout
    assert "blocker" not in res.stdout.lower()


def test_cli_c_rejects_fortran_only_flags_with_clear_error(tmp_path: Path):
    header = tmp_path / "api.h"
    header.write_text("int add(int a, int b);\n", encoding="utf-8")
    cmd = [sys.executable, "-m", "x2py", str(header), "--language", "c", "--parse", "--show-vars"]

    res = subprocess.run(cmd, capture_output=True, text=True)

    assert res.returncode != 0
    assert "show-vars" in res.stderr
    assert "C" in res.stderr


def test_cli_c_semantics_is_rejected_until_phase_10(tmp_path: Path):
    header = tmp_path / "api.h"
    header.write_text("int add(int a, int b);\n", encoding="utf-8")
    cmd = [sys.executable, "-m", "x2py", str(header), "--language", "c", "--semantics"]

    res = subprocess.run(cmd, capture_output=True, text=True)

    assert res.returncode != 0
    assert "not supported" in res.stderr.lower()


def test_cli_c_pyi_is_rejected_until_phase_11(tmp_path: Path):
    header = tmp_path / "api.h"
    header.write_text("int add(int a, int b);\n", encoding="utf-8")
    cmd = [sys.executable, "-m", "x2py", str(header), "--language", "c", "--pyi"]

    res = subprocess.run(cmd, capture_output=True, text=True)

    assert res.returncode != 0
    assert "not supported" in res.stderr.lower()


def test_cli_c_no_color_formats_parse_errors_without_ansi(tmp_path: Path):
    header = tmp_path / "bad.h"
    header.write_text("int broken(;\n", encoding="utf-8")
    cmd = [sys.executable, "-m", "x2py", str(header), "--language", "c", "--parse", "--no-color"]

    res = subprocess.run(cmd, capture_output=True, text=True)

    assert res.returncode == 1
    assert "\033[" not in res.stderr
    assert "error[" in res.stderr


def test_cli_c_debug_traceback_reraises_parse_errors(tmp_path: Path):
    header = tmp_path / "bad.h"
    header.write_text("int broken(;\n", encoding="utf-8")
    cmd = [
        sys.executable,
        "-m",
        "x2py",
        str(header),
        "--language",
        "c",
        "--parse",
        "--debug-traceback",
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)

    assert res.returncode == 1
    assert "Traceback" in res.stderr
    assert "CParseError" in res.stderr


def test_cli_c_debug_env_reraises_parse_errors(tmp_path: Path):
    header = tmp_path / "bad.h"
    header.write_text("int broken(;\n", encoding="utf-8")
    cmd = [sys.executable, "-m", "x2py", str(header), "--language", "c", "--parse"]

    res = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env={**os.environ, "C_PARSER_DEBUG": "1"},
    )

    assert res.returncode == 1
    assert "Traceback" in res.stderr


def test_cli_without_language_keeps_fortran_default_behavior():
    fixture = Path(__file__).resolve().parents[2] / "data" / "fortran" / "general" / "basic_subroutine.f90"
    cmd = [sys.executable, "-m", "x2py", str(fixture), "--parse"]

    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    assert "subroutine add1" in res.stdout
    assert "Language: c" not in res.stdout

