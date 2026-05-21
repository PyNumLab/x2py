# -*- coding: utf-8 -*-
"""C parser CLI skeleton coverage."""

import json
import subprocess
import sys
from pathlib import Path


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
    assert "Functions: 0" in res.stdout
    assert "Parser status: skeleton" in res.stdout


def test_cli_c_parse_json_stdout_for_header(tmp_path: Path):
    header = tmp_path / "api.h"
    header.write_text("int add(int a, int b);\n", encoding="utf-8")
    cmd = [sys.executable, "-m", "x2py", str(header), "--language", "c", "--parse", "--json"]

    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(res.stdout)
    file_payload = payload[str(header)]

    assert file_payload["language"] == "c"
    assert file_payload["parser_status"] == "skeleton"
    assert file_payload["functions"] == []
    assert file_payload["structs"] == []
    assert file_payload["unions"] == []
    assert file_payload["enums"] == []
    assert file_payload["typedefs"] == []
    assert file_payload["globals"] == []
    assert file_payload["macros"] == []
    assert file_payload["includes"] == []
    assert file_payload["diagnostics"] == []


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
    assert payload[str(header)]["language"] == "c"
    assert payload[str(header)]["parser_status"] == "skeleton"


def test_cli_c_parse_out_without_json_writes_json_and_suppresses_stdout(tmp_path: Path):
    header = tmp_path / "api.h"
    output = tmp_path / "report.json"
    header.write_text("int run(void);\n", encoding="utf-8")
    cmd = [
        sys.executable,
        "-m",
        "x2py",
        str(header),
        "--language",
        "c",
        "--parse",
        "--out",
        str(output),
    ]

    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert res.stdout == ""
    assert payload[str(header)]["parser_status"] == "skeleton"


def test_cli_c_semantic_stages_are_rejected_until_implemented(tmp_path: Path):
    header = tmp_path / "api.h"
    header.write_text("int add(int a, int b);\n", encoding="utf-8")

    for stage in ("--semantics", "--pyi", "--wrap-readiness"):
        cmd = [sys.executable, "-m", "x2py", str(header), "--language", "c", stage]
        res = subprocess.run(cmd, capture_output=True, text=True)

        assert res.returncode != 0
        assert "not supported" in res.stderr.lower()


def test_cli_c_rejects_fortran_only_parse_flags(tmp_path: Path):
    header = tmp_path / "api.h"
    header.write_text("int add(int a, int b);\n", encoding="utf-8")
    cmd = [sys.executable, "-m", "x2py", str(header), "--language", "c", "--parse", "--show-vars"]

    res = subprocess.run(cmd, capture_output=True, text=True)

    assert res.returncode != 0
    assert "show-vars" in res.stderr
    assert "Fortran-only" in res.stderr


def test_cli_c_no_color_and_debug_traceback_flags_are_accepted(tmp_path: Path):
    header = tmp_path / "api.h"
    header.write_text("int run(void);\n", encoding="utf-8")
    cmd = [
        sys.executable,
        "-m",
        "x2py",
        str(header),
        "--language",
        "c",
        "--parse",
        "--no-color",
        "--debug-traceback",
    ]

    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    assert "Parser status: skeleton" in res.stdout


def test_cli_without_language_keeps_fortran_default_behavior():
    fixture = Path(__file__).resolve().parents[2] / "data" / "fortran" / "general" / "basic_subroutine.f90"
    cmd = [sys.executable, "-m", "x2py", str(fixture), "--parse"]

    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    assert "subroutine add1" in res.stdout
    assert "Language: c" not in res.stdout
