"""Tests split by stable ownership concept from `test_wrap_readiness.py`."""

from tests._shared.semantic_readiness_support import (
    CONTRACT_IMPORT,
    Path,
    TEST_FILE,
    _blocker_codes,
    _write_ready_fortran,
    json,
    pytest,
    subprocess,
    sys,
    x2py_cli,
)


def test_cli_wrap_readiness_uses_pyi_filename_as_native_contract(tmp_path: Path):
    pyi = tmp_path / "solver.pyi"
    pyi.write_text(
        f"""
{CONTRACT_IMPORT}
n: Final[Int32] = 8

def fill(x: Float64[n]) -> None: ...
""",
        encoding="utf-8",
    )

    cmd = [sys.executable, "-m", "x2py", str(pyi), "--wrap-readiness"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    assert "Source: pyi" in res.stdout
    assert "Wrappable: yes" in res.stdout
    assert "No semantic readiness blockers detected." in res.stdout


def test_cli_wrap_readiness_json_uses_pyi_filename_as_native_contract(tmp_path: Path):
    pyi = tmp_path / "solver.pyi"
    pyi.write_text(f"{CONTRACT_IMPORT}def fill(n: Int32) -> None: ...\n", encoding="utf-8")

    cmd = [sys.executable, "-m", "x2py", str(pyi), "--wrap-readiness", "--json"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(res.stdout)

    assert payload[str(pyi)]["source_kind"] == "pyi"
    report = payload[str(pyi)]["wrap_readiness"]
    assert report["wrappable"] is True
    assert _blocker_codes(report) == set()


def test_cli_wrap_readiness_output_from_fortran():
    cmd = [sys.executable, "-m", "x2py", str(TEST_FILE), "--wrap-readiness"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert f"File: {TEST_FILE}" in res.stdout
    assert "Source: fortran" in res.stdout
    assert "Wrappable: yes" in res.stdout
    assert "No semantic readiness blockers detected." in res.stdout
    assert "Modules:" not in res.stdout


def test_cli_wrap_readiness_json_output_from_fortran():
    cmd = [sys.executable, "-m", "x2py", str(TEST_FILE), "--wrap-readiness", "--json"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(res.stdout)
    assert payload[str(TEST_FILE)]["source_kind"] == "fortran"
    assert payload[str(TEST_FILE)]["wrap_readiness"]["wrappable"] is True


def test_cli_help_includes_semantic_wrap_readiness_examples():
    cmd = [sys.executable, "-m", "x2py", "--help"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "python3 -m x2py path/to/file.f90 --wrap-readiness" in res.stdout
    assert "python3 -m x2py path/to/module.pyi --wrap-readiness" in res.stdout


def test_x2py_main_wrap_readiness_mode_from_inline_source(tmp_path: Path, monkeypatch, capsys):
    f90 = _write_ready_fortran(tmp_path / "mini.f90")

    monkeypatch.setattr(sys, "argv", ["x2py", str(f90), "--wrap-readiness"])
    assert x2py_cli.main() == 0
    assert "Wrappable: yes" in capsys.readouterr().out


def test_x2py_main_wrap_readiness_json_directory_expands_fortran_and_pyi(tmp_path: Path, monkeypatch, capsys):
    f90 = _write_ready_fortran(tmp_path / "mini.f90")
    pyi = tmp_path / "solver.pyi"
    pyi.write_text(f"{CONTRACT_IMPORT}def fill(n: Int32) -> None: ...\n", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["x2py", str(tmp_path), "--language", "fortran", "--wrap-readiness", "--json"])
    assert x2py_cli.main() == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload[str(f90)]["source_kind"] == "fortran"
    assert payload[str(pyi)]["source_kind"] == "pyi"


def test_x2py_main_semantic_readiness_blocker_formatting():
    text = x2py_cli._format_semantic_readiness(
        {
            "solver.pyi": {
                "source_kind": "pyi",
                "semantic_modules": [{"name": "solver"}],
                "wrap_readiness": {
                    "wrappable": False,
                    "n_functions": 1,
                    "n_classes": 0,
                    "n_variables": 0,
                    "wrappability_blockers": [
                        {
                            "code": "unresolved_semantic_types",
                            "message": "Unresolved semantic types.",
                            "items": [{"owner": "step", "type": "sim_state"}],
                        },
                        {
                            "code": "unresolved_shape_symbols",
                            "message": "Unresolved shape symbols.",
                            "items": [{"owner": "fill", "expression": "n", "symbol": "n"}],
                        },
                        {
                            "code": "missing_compile_time_values",
                            "message": "Missing compile-time values.",
                            "items": [{"owner": "fill", "symbol": "n"}],
                        },
                        {
                            "code": "callback_signature_incomplete",
                            "message": "Callback signature incomplete.",
                            "items": [{"owner": "integrate.objective", "needs": ["callback argument types"]}],
                        },
                        {
                            "code": "no_public_api",
                            "message": "No public API.",
                            "items": [{"owner": "empty", "needs": ["public functions"]}],
                        },
                        {
                            "code": "custom",
                            "message": "Custom blocker.",
                            "items": [{"payload": 1}],
                        },
                    ],
                },
            }
        }
    )

    assert "step uses unresolved type sim_state" in text
    assert "fill shape 'n' uses unresolved symbol n" in text
    assert "fill needs literal value for Final constant n" in text
    assert "integrate.objective needs Callable[[...], ...] metadata (callback argument types)" in text
    assert "empty needs public functions" in text
    assert "{'payload': 1}" in text


def test_x2py_main_argument_validation_errors(tmp_path: Path, monkeypatch, capsys):
    f90 = _write_ready_fortran(tmp_path / "mini.f90")

    monkeypatch.setattr(sys, "argv", ["x2py", str(f90), "--show-vars"])
    with pytest.raises(SystemExit) as show_vars_error:
        x2py_cli.main()
    assert show_vars_error.value.code == 2
    assert "--show-vars/--print-limit require --parse" in capsys.readouterr().err

    monkeypatch.setattr(sys, "argv", ["x2py", str(f90), "--parse", "--print-limit", "-1"])
    with pytest.raises(SystemExit) as print_limit_error:
        x2py_cli.main()
    assert print_limit_error.value.code == 2
    assert "--print-limit must be >= 0" in capsys.readouterr().err

    pyi = tmp_path / "mini.pyi"
    pyi.write_text("def f() -> None: ...\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["x2py", str(pyi)])
    with pytest.raises(SystemExit) as stage_error:
        x2py_cli.main()
    assert stage_error.value.code == 2
    assert "Select at least one stage flag" in capsys.readouterr().err
