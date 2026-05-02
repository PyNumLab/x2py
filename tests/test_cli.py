import json
import subprocess
import sys
from pathlib import Path


def test_cli_readable_output():
    cmd = [sys.executable, "-m", "fortran_parser", "tests/fcode/basic_subroutine.f90"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "File: tests/fcode/basic_subroutine.f90" in res.stdout
    assert "subroutine add1" in res.stdout


def test_cli_json_out(tmp_path: Path):
    out = tmp_path / "report.json"
    cmd = [
        sys.executable,
        "-m",
        "fortran_parser",
        "tests/fcode/basic_subroutine.f90",
        "--json",
        "--json-out",
        str(out),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(res.stdout)
    assert "tests/fcode/basic_subroutine.f90" in payload
    assert out.exists()
    file_payload = json.loads(out.read_text())
    assert payload == file_payload
