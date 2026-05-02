import json
import subprocess
import sys
from pathlib import Path


TEST_FILE = Path(__file__).parent / "fcode" / "basic_subroutine.f90"


def test_cli_readable_output():
    cmd = [sys.executable, "-m", "fortran_parser", str(TEST_FILE)]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert f"File: {TEST_FILE}" in res.stdout
    assert "subroutine add1" in res.stdout
    assert "Derived types: 0" not in res.stdout
    assert "Wrappable:" not in res.stdout


def test_cli_json_out(tmp_path: Path):
    out = tmp_path / "report.json"
    cmd = [
        sys.executable,
        "-m",
        "fortran_parser",
        str(TEST_FILE),
        "--json",
        "--json-out",
        str(out),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(res.stdout)
    assert str(TEST_FILE) in payload
    assert out.exists()
    file_payload = json.loads(out.read_text())
    assert payload == file_payload
