# -*- coding: utf-8 -*-
import json
import os
import subprocess
import sys
from pathlib import Path


TEST_FILE = Path(__file__).parent / "fcode" / "basic_subroutine.f90"


def test_cli_readable_output():
    cmd = [sys.executable, "-m", "x2py", str(TEST_FILE), "--parse"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert f"File: {TEST_FILE}" in res.stdout
    assert "subroutine add1" in res.stdout
    assert "Derived types: 0" not in res.stdout
    print(res.stdout)
    assert "Wrappable:" not in res.stdout


def test_cli_json_out(tmp_path: Path):
    out = tmp_path / "report.json"
    cmd = [
        sys.executable,
        "-m",
        "x2py",
        str(TEST_FILE),
        "--parse",
        "--json",
        "--out",
        str(out),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert res.stdout == ""
    assert out.exists()
    file_payload = json.loads(out.read_text())
    assert str(TEST_FILE) in file_payload



def test_cli_out_without_filename_uses_source_basename_json(tmp_path: Path):
    f90 = tmp_path / "mini.f90"
    f90.write_text("subroutine work(n)\n  integer, intent(in) :: n\nend subroutine work\n", encoding="utf-8")
    cmd = [sys.executable, "-m", "x2py", str(f90), "--parse", "--out"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert res.stdout == ""
    out = tmp_path / "mini.json"
    assert out.exists()
    file_payload = json.loads(out.read_text())
    assert str(f90) in file_payload


def test_cli_json_output_without_out():
    cmd = [sys.executable, "-m", "x2py", str(TEST_FILE), "--parse", "--json"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(res.stdout)
    assert str(TEST_FILE) in payload


def test_cli_pyi_output_without_out():
    cmd = [sys.executable, "-m", "x2py", str(TEST_FILE), "--pyi"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert f"File: {TEST_FILE}" in res.stdout
    assert "def add1(" in res.stdout
def test_cli_keeps_free_procedure_when_module_has_same_name(tmp_path: Path):
    f90 = tmp_path / "same_name_scopes.f90"
    f90.write_text(
        """
subroutine work(n)
  integer, intent(in) :: n
end subroutine work

module m
contains
  subroutine work(n)
    integer, intent(in) :: n
  end subroutine work
end module m
""".strip()
    )

    cmd = [sys.executable, "-m", "x2py", str(f90), "--parse"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    assert "  Procedures: 1" in res.stdout
    assert "    - subroutine work(n:integer[0])" in res.stdout
    assert "  Modules: 1" in res.stdout
    assert "      Procedures: 1" in res.stdout


def test_cli_formats_parse_errors_without_traceback(tmp_path: Path):
    f90 = tmp_path / "bad.f90"
    f90.write_text(
        """subroutine bad(x)
  weirdtype :: x
end subroutine bad
""",
        encoding="utf-8",
    )

    cmd = [sys.executable, "-m", "x2py", str(f90), "--parse", "--no-color"]
    res = subprocess.run(cmd, capture_output=True, text=True)

    assert res.returncode == 1
    assert res.stdout == ""
    assert "Traceback" not in res.stderr
    assert f"{f90}:2:1: error[PARSE001]:" in res.stderr
    assert "2 |   weirdtype :: x" in res.stderr


def test_cli_debug_traceback_flag_reraises_parse_errors(tmp_path: Path):
    f90 = tmp_path / "bad.f90"
    f90.write_text(
        """subroutine bad(x)
  weirdtype :: x
end subroutine bad
""",
        encoding="utf-8",
    )

    cmd = [sys.executable, "-m", "x2py", str(f90), "--parse", "--debug-traceback"]
    res = subprocess.run(cmd, capture_output=True, text=True)

    assert res.returncode == 1
    assert "Traceback" in res.stderr
    assert "FortranParseError" in res.stderr


def test_cli_debug_traceback_env_reraises_parse_errors(tmp_path: Path):
    f90 = tmp_path / "bad.f90"
    f90.write_text(
        """subroutine bad(x)
  weirdtype :: x
end subroutine bad
""",
        encoding="utf-8",
    )

    cmd = [sys.executable, "-m", "x2py", str(f90), "--parse"]
    res = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env={**os.environ, "FORTRAN_PARSER_DEBUG": "1"},
    )

    assert res.returncode == 1
    assert "Traceback" in res.stderr
    assert "note: parser raised at" in res.stderr


def test_cli_formats_parse_error_with_ansi_by_default(tmp_path: Path):
    f90 = tmp_path / "bad.f90"
    f90.write_text(
        """subroutine bad(x)
  weirdtype :: x
end subroutine bad
""",
        encoding="utf-8",
    )

    cmd = [sys.executable, "-m", "x2py", str(f90), "--parse"]
    env = {k: v for k, v in os.environ.items() if k != "NO_COLOR"}
    res = subprocess.run(cmd, capture_output=True, text=True, env=env)

    assert res.returncode == 1
    assert "\033[" in res.stderr
    assert "error" in res.stderr


def test_cli_no_color_env_disables_default_ansi(tmp_path: Path):
    f90 = tmp_path / "bad.f90"
    f90.write_text(
        """subroutine bad(x)
  weirdtype :: x
end subroutine bad
""",
        encoding="utf-8",
    )

    cmd = [sys.executable, "-m", "x2py", str(f90), "--parse"]
    res = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env={**os.environ, "NO_COLOR": "1"},
    )

    assert res.returncode == 1
    assert "\033[" not in res.stderr
    assert f"{f90}:2:1: error[PARSE001]:" in res.stderr




def test_cli_semantics_out_writes_json_without_stdout(tmp_path: Path):
    out = tmp_path / "semantics.json"
    cmd = [sys.executable, "-m", "x2py", str(TEST_FILE), "--semantics", "--out", str(out)]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    assert res.stdout == ""
    assert out.exists()
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert str(TEST_FILE) in payload
    assert "semantic_modules" in payload[str(TEST_FILE)]

def test_cli_semantics_without_json_output():
    cmd = [sys.executable, "-m", "x2py", str(TEST_FILE), "--semantics"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(res.stdout)
    assert str(TEST_FILE) in payload
    assert "semantic_modules" in payload[str(TEST_FILE)]


def test_cli_semantics_json_requires_parse():
    cmd = [sys.executable, "-m", "x2py", str(TEST_FILE), "--semantics", "--json"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 2
    assert "JSON output currently supports only the parsing stage" in res.stderr


def test_cli_pyi_output():
    cmd = [sys.executable, "-m", "x2py", str(TEST_FILE), "--pyi"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert f"File: {TEST_FILE}" in res.stdout
    assert "def add1(" in res.stdout



def test_cli_pyi_out_writes_adjacent_file(tmp_path: Path):
    f90 = tmp_path / "mini.f90"
    f90.write_text(
        """module m
contains
  subroutine add1(x)
    integer, intent(inout) :: x
    x = x + 1
  end subroutine add1
end module m
""",
        encoding="utf-8",
    )

    cmd = [sys.executable, "-m", "x2py", str(f90), "--pyi", "--out"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    assert res.stdout == ""
    out = tmp_path / "mini.pyi"
    assert out.exists()
    assert "def add1" in out.read_text(encoding="utf-8")



def test_cli_out_requires_stage_flag():
    cmd = [sys.executable, "-m", "x2py", str(TEST_FILE), "--out"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 2
    assert "--out requires a stage flag" in res.stderr

def test_cli_help_includes_examples():
    cmd = [sys.executable, "-m", "x2py", "--help"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "Examples:" in res.stdout
    assert "python -m x2py path/to/file.f90 --parse" in res.stdout


def test_cli_parse_shows_module_derived_types_and_derived_arg_kinds():
    fixture = Path(__file__).parent.parent / "semantics" / "fixtures" / "modern_pyi_example.f90"
    cmd = [sys.executable, "-m", "x2py", str(fixture), "--parse"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    assert "      Derived types: 3" in res.stdout
    assert "type particle" in res.stdout
    assert "Fields: 3" in res.stdout
    assert "- id:integer[0]" in res.stdout
    assert "- mass:real[0]" in res.stdout
    assert "- position:real[1]" in res.stdout
    assert "init_particle(p:type(particle)[0]" in res.stdout


def test_cli_parse_modern_fixture_prints_derived_block_verbatim():
    fixture = Path(__file__).parent.parent / "semantics" / "fixtures" / "modern_pyi_example.f90"
    cmd = [sys.executable, "-m", "x2py", str(fixture), "--parse"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    expected_block = """      Derived types: 3
        - type particle (fields=3, methods=0)
          Fields: 3
            - id:integer[0]
            - mass:real[0]
            - position:real[1]
        - type vector3 (fields=1, methods=0)
          Fields: 1
            - values:real[1]
        - type hidden_state (fields=1, methods=0)
          Fields: 1
            - code:integer[0]
"""
    assert expected_block in res.stdout
