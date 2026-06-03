import builtins
from dataclasses import dataclass
import json
import os
import runpy
import subprocess
import sys
import types
from pathlib import Path

import pytest

from fortran_parser import cli as fortran_parser_cli
from x2py import FortranParseError
from x2py import cli as x2py_cli
from x2py.preprocessing import PreprocessingConfig, PreprocessingDiagnostic, PreprocessingError


TEST_FILE = Path(__file__).parent.parent / "data" / "fortran" / "general" / "basic_subroutine.f90"


class _MainParserError(Exception):
    pass


def _main_args(**overrides):
    values = {
        "paths": ["input.f90"],
        "language": "fortran",
        "parse": False,
        "preprocessor_adapter": "auto",
        "compiler": None,
        "compile_commands": None,
        "preprocess_template": None,
        "include_dirs": [],
        "defines": [],
        "undefs": [],
        "std": None,
        "compiler_args": [],
        "include_exposure": "reachable-project",
        "public_includes": [],
        "private_includes": [],
        "show_vars": False,
        "print_limit": None,
        "vars_limit": None,
        "wrap_readiness": False,
        "semantics": False,
        "pyi": False,
        "json": False,
        "out": None,
        "no_color": False,
        "debug": False,
    }
    values.update(overrides)
    return types.SimpleNamespace(**values)


def _install_main_parser(monkeypatch, args):
    class FakeParser:
        def add_argument(self, *_args, **_kwargs):
            pass

        def parse_args(self):
            return args

        def error(self, message):
            raise _MainParserError(message)

    parser = FakeParser()
    monkeypatch.setattr(x2py_cli.argparse, "ArgumentParser", lambda *args, **kwargs: parser)
    return parser


def _patch_main_report_payloads(
    monkeypatch,
    *,
    language="fortran",
    parse_payload=None,
    semantic_payload=None,
    readiness_payload=None,
):
    preprocessing = object()
    calls = []
    monkeypatch.setattr(x2py_cli, "_resolve_language", lambda paths, _active_language, parser: language)
    monkeypatch.setattr(x2py_cli, "_build_preprocessing_config", lambda args, parser: preprocessing)
    monkeypatch.setattr(
        x2py_cli,
        "_parse_report",
        lambda paths, active_preprocessing: calls.append(("parse", paths, active_preprocessing)) or parse_payload,
    )
    monkeypatch.setattr(
        x2py_cli,
        "_semantic_report",
        lambda paths, active_preprocessing, *, language: (
            calls.append(("semantic", paths, active_preprocessing, language)) or semantic_payload
        ),
    )
    monkeypatch.setattr(
        x2py_cli,
        "_wrap_readiness_report",
        lambda paths, active_preprocessing, *, language: (
            calls.append(("readiness", paths, active_preprocessing, language)) or readiness_payload
        ),
    )
    monkeypatch.setattr(
        x2py_cli,
        "_attach_wrap_readiness",
        lambda active_semantic_payload, active_readiness_payload: calls.append(
            ("attach", active_semantic_payload, active_readiness_payload)
        ),
    )
    return preprocessing, calls


def test_cli_readable_output():
    cmd = [sys.executable, "-m", "x2py", str(TEST_FILE), "--parse"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert f"File: {TEST_FILE}" in res.stdout
    assert "subroutine add1" in res.stdout
    assert "Variables:" not in res.stdout
    assert "Derived types: 0" not in res.stdout
    print(res.stdout)
    assert "Wrappable:" not in res.stdout


def test_cli_parse_show_vars_prints_scope_variables(tmp_path: Path):
    f90 = tmp_path / "module_vars.f90"
    f90.write_text(
        """
module module_vars
  integer :: n
  real(kind=8), dimension(3) :: x
contains
  subroutine work()
  end subroutine work
end module module_vars
""".strip(),
        encoding="utf-8",
    )

    cmd = [sys.executable, "-m", "x2py", str(f90), "--parse", "--show-vars"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    assert "    - module module_vars (vars=2, uses=0)" in res.stdout
    assert "      Variables: 2" in res.stdout
    assert "        - n:integer[0]" in res.stdout
    assert "        - x:real(8)[1]" in res.stdout


def test_cli_parse_print_limit_limits_scope_variables_when_shown(tmp_path: Path):
    f90 = tmp_path / "module_vars.f90"
    f90.write_text(
        """
module module_vars
  integer :: n
  real(kind=8), dimension(3) :: x
contains
  subroutine work()
  end subroutine work
end module module_vars
""".strip(),
        encoding="utf-8",
    )

    cmd = [sys.executable, "-m", "x2py", str(f90), "--parse", "--show-vars", "--print-limit", "1"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    assert "      Variables: 2" in res.stdout
    assert "        - n:integer[0]" in res.stdout
    assert "        - x:real(8)[1]" not in res.stdout
    assert "        ... 1 more variables" in res.stdout


def test_cli_parse_print_limit_limits_procedures(tmp_path: Path):
    f90 = tmp_path / "many_procs.f90"
    f90.write_text(
        """
module many_procs
contains
  subroutine first()
  end subroutine first

  subroutine second()
  end subroutine second
end module many_procs
""".strip(),
        encoding="utf-8",
    )

    cmd = [sys.executable, "-m", "x2py", str(f90), "--parse", "--print-limit", "1"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    assert "      Procedures: 2" in res.stdout
    assert "        - subroutine first()" in res.stdout
    assert "        - subroutine second()" not in res.stdout
    assert "        ... 1 more procedures" in res.stdout
    assert "Variables:" not in res.stdout


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
    assert "wrap_readiness" not in payload[str(TEST_FILE)]


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
    assert f"{f90}:2:1: error[PARSE_UNSUPPORTED_DECLARATION]:" in res.stderr
    assert "2 |   weirdtype :: x" in res.stderr


def test_cli_debug_flag_reraises_parse_errors(tmp_path: Path):
    f90 = tmp_path / "bad.f90"
    f90.write_text(
        """subroutine bad(x)
  weirdtype :: x
end subroutine bad
""",
        encoding="utf-8",
    )

    cmd = [sys.executable, "-m", "x2py", str(f90), "--parse", "--debug"]
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
    assert f"{f90}:2:1: error[PARSE_UNSUPPORTED_DECLARATION]:" in res.stderr


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


def test_cli_semantics_json_output():
    cmd = [sys.executable, "-m", "x2py", str(TEST_FILE), "--semantics", "--json"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(res.stdout)
    assert payload[str(TEST_FILE)]["semantic_modules"]


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


def test_cli_pyi_out_writes_explicit_file_from_inline_code(tmp_path: Path):
    f90 = tmp_path / "explicit.f90"
    f90.write_text(
        """module explicit_mod
contains
  subroutine set_value(x)
    real(8), intent(out) :: x
  end subroutine set_value
end module explicit_mod
""",
        encoding="utf-8",
    )
    out = tmp_path / "explicit_api.pyi"

    cmd = [sys.executable, "-m", "x2py", str(f90), "--pyi", "--out", str(out)]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    assert res.stdout == ""
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "def set_value(" in text
    assert "x: Annotated[Ptr(Float64), Intent('out')]" in text
    assert "-> None: ..." in text


def test_cli_rejects_conflicting_json_and_pyi_out_from_inline_code(tmp_path: Path):
    f90 = tmp_path / "conflict.f90"
    f90.write_text(
        """module conflict_mod
contains
  subroutine ping()
  end subroutine ping
end module conflict_mod
""",
        encoding="utf-8",
    )

    cmd = [sys.executable, "-m", "x2py", str(f90), "--parse", "--pyi", "--json", "--out", str(tmp_path / "out")]
    res = subprocess.run(cmd, capture_output=True, text=True)

    assert res.returncode == 2
    assert "--out cannot be used with both --json and --pyi" in res.stderr


def test_fortran_parser_cli_reports_full_source_tree_from_inline_code(tmp_path: Path):
    f90 = tmp_path / "full_tree.f90"
    f90.write_text(
        """
module parent_mod
  integer :: counter
  type :: particle
    integer :: id
    real(8) :: x(3)
  contains
    procedure :: reset
  end type particle
contains
  subroutine reset(self)
    type(particle), intent(inout) :: self
  end subroutine reset
end module parent_mod

submodule (parent_mod) child_mod
contains
  module subroutine child_step(n)
    integer, intent(in) :: n
  end subroutine child_step
end submodule child_mod

program driver
  use parent_mod
  integer :: n
end program driver

block data init_block
  integer :: flag
end block data init_block
""",
        encoding="utf-8",
    )

    cmd = [sys.executable, "-m", "fortran_parser", str(f90)]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    assert f"File: {f90}" in res.stdout
    assert "Modules: 1" in res.stdout
    assert "- module parent_mod (vars=1, uses=0)" in res.stdout
    assert "Derived types: 1" in res.stdout
    assert "- type particle (fields=2, methods=1)" in res.stdout
    assert "Fields: 2" in res.stdout
    assert "- x:real(8)[1]" in res.stdout
    assert "Submodules: 1" in res.stdout
    assert "- submodule child_mod (parent=parent_mod, vars=0, uses=0)" in res.stdout
    assert "Programs: 1" in res.stdout
    assert "- program driver (vars=1, uses=1)" in res.stdout
    assert "Block data: 1" in res.stdout
    assert "- block data init_block (vars=1)" in res.stdout


def test_fortran_parser_cli_semantics_pyi_and_empty_module_report_from_inline_code(tmp_path: Path):
    module_source = tmp_path / "semantics.f90"
    module_source.write_text(
        """
module solver_mod
contains
  subroutine solve(a, x, b)
    real(8), intent(in) :: a
    real(8), intent(out) :: x
    real(8), intent(in) :: b
  end subroutine solve
end module solver_mod
""",
        encoding="utf-8",
    )
    program_source = tmp_path / "driver.f90"
    program_source.write_text(
        """
program driver
  integer :: n
end program driver
""",
        encoding="utf-8",
    )
    json_out = tmp_path / "semantics.json"

    semantics_cmd = [
        sys.executable,
        "-m",
        "fortran_parser",
        str(module_source),
        "--semantics",
        "--json-out",
        str(json_out),
    ]
    semantics_res = subprocess.run(semantics_cmd, capture_output=True, text=True, check=True)
    payload = json.loads(json_out.read_text(encoding="utf-8"))

    assert "solver_mod" in semantics_res.stdout
    assert str(module_source) in payload
    assert payload[str(module_source)]["semantic_modules"][0]["functions"][0]["name"] == "solve"

    pyi_cmd = [sys.executable, "-m", "fortran_parser", str(module_source), "--pyi"]
    pyi_res = subprocess.run(pyi_cmd, capture_output=True, text=True, check=True)
    assert "@native_call" not in pyi_res.stdout
    assert "x: Annotated[Ptr(Float64), Intent('out')]" in pyi_res.stdout
    assert "def solve(" in pyi_res.stdout

    empty_pyi_cmd = [sys.executable, "-m", "fortran_parser", str(program_source), "--pyi"]
    empty_pyi_res = subprocess.run(empty_pyi_cmd, capture_output=True, text=True, check=True)
    assert "<no module declarations found>" in empty_pyi_res.stdout


def test_x2py_semantics_marks_explicit_cross_file_derived_type_as_wrapped(tmp_path: Path):
    types_mod = tmp_path / "types_mod.f90"
    physics = tmp_path / "physics.f90"
    types_mod.write_text(
        """
module types_mod
  type :: particle
    real :: mass
  end type particle
end module types_mod
""",
        encoding="utf-8",
    )
    physics.write_text(
        """
module physics
  use types_mod, only: particle
contains
  subroutine move(p)
    type(particle), intent(inout) :: p
  end subroutine move
end module physics
""",
        encoding="utf-8",
    )

    payload = x2py_cli._semantic_report([str(types_mod), str(physics)])
    semantic_type = payload[str(physics)]["semantic_modules"][0]["functions"][0]["arguments"][0]["semantic_type"]

    assert semantic_type["metadata"]["external_type_ref"]["wrapped"] is True
    assert "class particle" not in payload[str(physics)]["pyi"]

    readiness = x2py_cli._wrap_readiness_report([str(types_mod), str(physics)])
    readiness_type = readiness[str(physics)]["semantic_modules"][0]["functions"][0]["arguments"][0]["semantic_type"]

    assert readiness_type["metadata"]["external_type_ref"]["wrapped"] is True


def test_x2py_pyi_report_writes_opaque_dependency_stub_for_external_type(tmp_path: Path, monkeypatch):
    physics = tmp_path / "physics.f90"
    physics.write_text(
        """
module physics
  use types_mod, only: particle
contains
  function create_particle() result(p)
    type(particle) :: p
  end function create_particle
end module physics
""",
        encoding="utf-8",
    )

    payload = x2py_cli._semantic_report([str(physics)])

    assert payload[str(physics)]["pyi_dependencies"] == {"types_mod": "class particle(Opaque):\n    pass"}
    monkeypatch.setattr(sys, "argv", ["x2py", str(physics), "--pyi", "--out"])
    assert x2py_cli.main() == 0

    assert (tmp_path / "physics.pyi").exists()
    assert (tmp_path / "types_mod.pyi").read_text(encoding="utf-8") == "class particle(Opaque):\n    pass\n"


def test_x2py_pyi_report_formats_and_rejects_conflicting_dependency_stubs():
    report = {
        "first.f90": {
            "pyi": "def first() -> None: ...",
            "pyi_dependencies": {"shared": "class shared(Opaque):\n    pass"},
        },
        "second.f90": {
            "pyi": "def second() -> None: ...",
            "pyi_dependencies": {
                "shared": "class shared(Opaque):\n    pass",
                "extra": "class extra(Opaque):\n    pass",
            },
        },
        "empty.f90": {},
    }

    text = x2py_cli._format_pyi_report(report)

    assert (
        text
        == """File: first.f90
def first() -> None: ...

Dependency stub: shared.pyi
class shared(Opaque):
    pass

File: second.f90
def second() -> None: ...

Dependency stub: extra.pyi
class extra(Opaque):
    pass

File: empty.f90
<no module declarations found>"""
    )
    with pytest.raises(ValueError, match="Conflicting generated dependency stub"):
        x2py_cli._write_pyi_dependencies(
            {
                "first.f90": {"pyi_dependencies": {"shared": "class shared:\n    pass"}},
                "second.f90": {"pyi_dependencies": {"shared": "class shared:\n    value: int"}},
            }
        )


def test_x2py_write_pyi_dependencies_handles_nested_modules_and_empty_payloads(tmp_path: Path):
    output_dir = tmp_path / "out"
    text = "class Shared:\n    pass"

    x2py_cli._write_pyi_dependencies(
        {
            str(tmp_path / "nodeps.f90"): {},
            str(tmp_path / "first.f90"): {"pyi_dependencies": {"pkg.sub.shared": text}},
            str(tmp_path / "second.f90"): {"pyi_dependencies": {"pkg.sub.shared": text}},
        },
        output_dir=output_dir,
    )

    assert (output_dir / "pkg" / "sub" / "shared.pyi").read_text(encoding="utf-8") == text + "\n"
    assert not (output_dir / "pkg.sub.shared.pyi").exists()


def test_x2py_write_pyi_dependencies_uses_explicit_utf8(tmp_path: Path, monkeypatch):
    writes = []

    def write_text(path, data, *args, **kwargs):
        assert not args
        assert kwargs.get("encoding") is not None
        assert kwargs["encoding"].lower() == "utf-8"
        writes.append((path, data))
        return len(data)

    monkeypatch.setattr(Path, "write_text", write_text)

    x2py_cli._write_pyi_dependencies(
        {str(tmp_path / "first.f90"): {"pyi_dependencies": {"shared": "class Shared:\n    pass"}}},
        output_dir=tmp_path,
    )

    assert writes == [(tmp_path / "shared.pyi", "class Shared:\n    pass\n")]


def test_x2py_main_formats_preprocessing_errors_with_and_without_diagnostics(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["x2py", str(TEST_FILE), "--parse"])

    def fail_with_diagnostic(_paths, _preprocessing):
        raise PreprocessingError(
            "compiler failed",
            category="PREPROCESSOR_FAILED",
            diagnostics=[
                PreprocessingDiagnostic(
                    category="PREPROCESSOR_FAILED",
                    message="bad include",
                    path="source.F90",
                    line=9,
                )
            ],
        )

    monkeypatch.setattr(x2py_cli, "_parse_report", fail_with_diagnostic)
    assert x2py_cli.main() == 1
    assert "source.F90:9: error[PREPROCESSOR_FAILED]: bad include" in capsys.readouterr().err

    def fail_without_diagnostic(_paths, _preprocessing):
        raise PreprocessingError("plain failure", category="PREPROCESSOR_FAILED")

    monkeypatch.setattr(x2py_cli, "_parse_report", fail_without_diagnostic)
    assert x2py_cli.main() == 1
    assert "x2py: error[PREPROCESSOR_FAILED]: plain failure" in capsys.readouterr().err


def test_x2py_main_preserves_fortran_stage_dispatch_contract(monkeypatch):
    class StopAfterDispatch(Exception):
        pass

    args = _main_args(parse=True, semantics=True, pyi=True, wrap_readiness=True)
    parser = _install_main_parser(monkeypatch, args)
    preprocessing = object()
    parse_payload = {"parse": "payload"}
    semantic_payload = {"semantic": "payload"}
    readiness_payload = {"readiness": "payload"}
    calls = []

    def resolve_language(paths, language, active_parser):
        calls.append(("resolve", paths, language, active_parser))
        return "fortran"

    def build_preprocessing_config(active_args, active_parser):
        calls.append(("config", active_args, active_parser))
        return preprocessing

    def parse_report(paths, active_preprocessing):
        calls.append(("parse", paths, active_preprocessing))
        return parse_payload

    def semantic_report(paths, active_preprocessing, *, language):
        calls.append(("semantic", paths, active_preprocessing, language))
        return semantic_payload

    def readiness_report(paths, active_preprocessing, *, language):
        calls.append(("readiness", paths, active_preprocessing, language))
        return readiness_payload

    def attach_wrap_readiness(active_semantic_payload, active_readiness_payload):
        calls.append(("attach", active_semantic_payload, active_readiness_payload))
        raise StopAfterDispatch

    monkeypatch.setattr(x2py_cli, "_resolve_language", resolve_language)
    monkeypatch.setattr(x2py_cli, "_build_preprocessing_config", build_preprocessing_config)
    monkeypatch.setattr(x2py_cli, "_parse_report", parse_report)
    monkeypatch.setattr(x2py_cli, "_semantic_report", semantic_report)
    monkeypatch.setattr(x2py_cli, "_wrap_readiness_report", readiness_report)
    monkeypatch.setattr(x2py_cli, "_attach_wrap_readiness", attach_wrap_readiness)

    with pytest.raises(StopAfterDispatch):
        x2py_cli.main()

    assert calls == [
        ("resolve", args.paths, "fortran", parser),
        ("config", args, parser),
        ("parse", args.paths, preprocessing),
        ("semantic", args.paths, preprocessing, "fortran"),
        ("readiness", args.paths, preprocessing, "fortran"),
        ("attach", semantic_payload, readiness_payload),
    ]


def test_x2py_main_preserves_c_parse_dispatch_contract(monkeypatch):
    class StopAfterDispatch(Exception):
        pass

    args = _main_args(language="requested", parse=True)
    _install_main_parser(monkeypatch, args)
    preprocessing = types.SimpleNamespace(include_dirs=("include",))
    parser_mode = object()
    source_loader = object()
    parse_payload = {"parse": "payload"}
    calls = []

    monkeypatch.setattr(x2py_cli, "_resolve_language", lambda paths, language, parser: "c")
    monkeypatch.setattr(x2py_cli, "_build_preprocessing_config", lambda active_args, parser: preprocessing)
    monkeypatch.setattr(
        x2py_cli,
        "_c_parser_preprocessing_mode",
        lambda active_preprocessing: calls.append(("mode", active_preprocessing)) or parser_mode,
    )
    monkeypatch.setattr(
        x2py_cli,
        "_c_source_loader",
        lambda active_preprocessing: calls.append(("loader", active_preprocessing)) or source_loader,
    )
    monkeypatch.setattr(
        x2py_cli,
        "parse_c_report",
        lambda paths, **kwargs: calls.append(("parse", paths, kwargs)) or parse_payload,
    )
    monkeypatch.setattr(
        x2py_cli,
        "_attach_wrap_readiness",
        lambda semantic_payload, readiness_payload: (_ for _ in ()).throw(StopAfterDispatch),
    )

    with pytest.raises(StopAfterDispatch):
        x2py_cli.main()

    assert calls == [
        ("mode", preprocessing),
        ("loader", preprocessing),
        (
            "parse",
            args.paths,
            {
                "include_dirs": preprocessing.include_dirs,
                "preprocessing": parser_mode,
                "source_loader": source_loader,
            },
        ),
    ]


@pytest.mark.parametrize("stage", ["semantics", "pyi", "wrap_readiness"])
def test_x2py_main_accepts_each_non_parse_c_stage(monkeypatch, stage):
    class StopAfterDispatch(Exception):
        pass

    args = _main_args(language="c", **{stage: True})
    _install_main_parser(monkeypatch, args)
    monkeypatch.setattr(x2py_cli, "_resolve_language", lambda paths, language, parser: language)
    monkeypatch.setattr(x2py_cli, "_build_preprocessing_config", lambda active_args, parser: object())
    monkeypatch.setattr(x2py_cli, "_semantic_report", lambda *args, **kwargs: {})
    monkeypatch.setattr(x2py_cli, "_wrap_readiness_report", lambda *args, **kwargs: {})
    monkeypatch.setattr(
        x2py_cli,
        "_attach_wrap_readiness",
        lambda semantic_payload, readiness_payload: (_ for _ in ()).throw(StopAfterDispatch),
    )

    with pytest.raises(StopAfterDispatch):
        x2py_cli.main()


@pytest.mark.parametrize(
    ("overrides", "expected"),
    [
        (
            {"language": "c"},
            "--language c requires a stage flag: choose one of --parse, --semantics, --pyi, or --wrap-readiness",
        ),
        (
            {"language": "c", "parse": True, "show_vars": True},
            "--show-vars/--print-limit are Fortran-only and are not supported for --language c",
        ),
        (
            {"language": "c", "parse": True, "print_limit": 1},
            "--show-vars/--print-limit are Fortran-only and are not supported for --language c",
        ),
        (
            {"language": "c", "parse": True, "vars_limit": 1},
            "--show-vars/--print-limit are Fortran-only and are not supported for --language c",
        ),
        (
            {"out": ""},
            "--out requires a stage flag: choose one of --parse, --semantics, --pyi, or --wrap-readiness",
        ),
        ({"show_vars": True}, "--show-vars/--print-limit require --parse"),
        ({"print_limit": 1}, "--show-vars/--print-limit require --parse"),
        ({"vars_limit": 1}, "--show-vars/--print-limit require --parse"),
        ({"parse": True, "print_limit": -1}, "--print-limit must be >= 0"),
        ({}, "Select at least one stage flag: --parse, --semantics, --pyi, or --wrap-readiness"),
    ],
)
def test_x2py_main_preserves_validation_diagnostics(monkeypatch, overrides, expected):
    args = _main_args(**overrides)
    _install_main_parser(monkeypatch, args)
    monkeypatch.setattr(x2py_cli, "_resolve_language", lambda paths, language, parser: language)
    monkeypatch.setattr(x2py_cli, "_build_preprocessing_config", lambda active_args, parser: object())

    with pytest.raises(_MainParserError) as exc_info:
        x2py_cli.main()

    assert str(exc_info.value) == expected


def test_x2py_main_preserves_zero_print_limit_and_legacy_vars_limit_contract(monkeypatch, capsys):
    args = _main_args(parse=True, print_limit=0, vars_limit=7)
    _install_main_parser(monkeypatch, args)
    preprocessing = object()
    parse_payload = {"parse": "payload"}
    format_calls = []

    monkeypatch.setattr(x2py_cli, "_resolve_language", lambda paths, language, parser: language)
    monkeypatch.setattr(x2py_cli, "_build_preprocessing_config", lambda active_args, parser: preprocessing)
    monkeypatch.setattr(x2py_cli, "_parse_report", lambda paths, active_preprocessing: parse_payload)
    monkeypatch.setattr(x2py_cli, "_attach_wrap_readiness", lambda semantic_payload, readiness_payload: None)
    monkeypatch.setattr(
        x2py_cli,
        "_format_report",
        lambda payload, **kwargs: format_calls.append((payload, kwargs)) or "formatted",
    )

    assert x2py_cli.main() == 0
    assert capsys.readouterr().out == "formatted\n"
    assert format_calls == [(parse_payload, {"show_vars": True, "print_limit": 0})]


@pytest.mark.parametrize(
    ("language", "error_type", "env_name"),
    [
        ("c", x2py_cli.CParseError, "C_PARSER_DEBUG"),
        ("fortran", FortranParseError, "FORTRAN_PARSER_DEBUG"),
    ],
)
def test_x2py_main_preserves_parse_error_rendering_contract(
    monkeypatch,
    capsys,
    language,
    error_type,
    env_name,
):
    args = _main_args(language=language, parse=True, no_color=True)
    _install_main_parser(monkeypatch, args)
    preprocessing = types.SimpleNamespace(include_dirs=())
    error = error_type("bad parse")
    calls = []

    monkeypatch.setattr(x2py_cli, "_resolve_language", lambda paths, _active_language, parser: language)
    monkeypatch.setattr(x2py_cli, "_build_preprocessing_config", lambda active_args, parser: preprocessing)
    monkeypatch.setattr(x2py_cli, "_env_flag", lambda name: calls.append(("env", name)) or False)
    monkeypatch.setattr(
        x2py_cli,
        "_diagnostic_color_enabled",
        lambda *, disabled: calls.append(("color", disabled)) or "color-enabled",
    )
    monkeypatch.setattr(
        error_type,
        "format_diagnostic",
        lambda self, *, color, debug: calls.append(("render", color, debug)) or "rendered diagnostic",
    )
    if language == "c":
        monkeypatch.setattr(x2py_cli, "_c_parser_preprocessing_mode", lambda active_preprocessing: "mode")
        monkeypatch.setattr(x2py_cli, "_c_source_loader", lambda active_preprocessing: "loader")
        monkeypatch.setattr(x2py_cli, "parse_c_report", lambda *args, **kwargs: (_ for _ in ()).throw(error))
    else:
        monkeypatch.setattr(x2py_cli, "_parse_report", lambda *args, **kwargs: (_ for _ in ()).throw(error))

    assert x2py_cli.main() == 1
    assert capsys.readouterr().err == "rendered diagnostic\n"
    assert calls == [
        ("env", env_name),
        ("color", True),
        ("render", "color-enabled", False),
    ]


@pytest.mark.parametrize(
    ("language", "error_type", "env_name"),
    [
        ("c", x2py_cli.CParseError, "C_PARSER_DEBUG"),
        ("fortran", FortranParseError, "FORTRAN_PARSER_DEBUG"),
    ],
)
def test_x2py_main_reraises_parse_errors_for_debug_environment(monkeypatch, language, error_type, env_name):
    args = _main_args(language=language, parse=True)
    _install_main_parser(monkeypatch, args)
    preprocessing = types.SimpleNamespace(include_dirs=())
    error = error_type("bad parse")
    calls = []

    monkeypatch.setattr(x2py_cli, "_resolve_language", lambda paths, _active_language, parser: language)
    monkeypatch.setattr(x2py_cli, "_build_preprocessing_config", lambda active_args, parser: preprocessing)
    monkeypatch.setattr(x2py_cli, "_env_flag", lambda name: calls.append(name) or name == env_name)
    if language == "c":
        monkeypatch.setattr(x2py_cli, "_c_parser_preprocessing_mode", lambda active_preprocessing: "mode")
        monkeypatch.setattr(x2py_cli, "_c_source_loader", lambda active_preprocessing: "loader")
        monkeypatch.setattr(x2py_cli, "parse_c_report", lambda *args, **kwargs: (_ for _ in ()).throw(error))
    else:
        monkeypatch.setattr(x2py_cli, "_parse_report", lambda *args, **kwargs: (_ for _ in ()).throw(error))

    with pytest.raises(error_type):
        x2py_cli.main()

    assert calls == [env_name]


def test_x2py_main_preserves_pathless_preprocessing_diagnostic_contract(monkeypatch, capsys):
    args = _main_args(parse=True)
    _install_main_parser(monkeypatch, args)
    calls = []

    monkeypatch.setattr(x2py_cli, "_resolve_language", lambda paths, language, parser: language)
    monkeypatch.setattr(x2py_cli, "_build_preprocessing_config", lambda active_args, parser: object())
    monkeypatch.setattr(x2py_cli, "_env_flag", lambda name: calls.append(name) or False)
    monkeypatch.setattr(
        x2py_cli,
        "_parse_report",
        lambda paths, preprocessing: (_ for _ in ()).throw(
            PreprocessingError(
                "compiler failed",
                diagnostics=[PreprocessingDiagnostic(category="PREPROCESSOR_FAILED", message="bad include")],
            )
        ),
    )

    assert x2py_cli.main() == 1
    assert capsys.readouterr().err == "<preprocessor>: error[PREPROCESSOR_FAILED]: bad include\n"
    assert calls == ["X2PY_DEBUG"]


def test_x2py_main_reraises_value_errors_for_debug_environment(monkeypatch):
    args = _main_args(parse=True)
    _install_main_parser(monkeypatch, args)
    calls = []

    monkeypatch.setattr(x2py_cli, "_resolve_language", lambda paths, language, parser: language)
    monkeypatch.setattr(x2py_cli, "_build_preprocessing_config", lambda active_args, parser: object())
    monkeypatch.setattr(x2py_cli, "_env_flag", lambda name: calls.append(name) or name == "X2PY_DEBUG")
    monkeypatch.setattr(
        x2py_cli,
        "_parse_report",
        lambda paths, preprocessing: (_ for _ in ()).throw(ValueError("invalid generated interface")),
    )

    with pytest.raises(ValueError, match="invalid generated interface"):
        x2py_cli.main()

    assert calls == ["X2PY_DEBUG"]


def test_x2py_main_preserves_conflicting_json_and_pyi_out_diagnostic(monkeypatch):
    args = _main_args(pyi=True, json=True, out="/tmp/conflict.pyi")
    _install_main_parser(monkeypatch, args)
    _patch_main_report_payloads(monkeypatch, semantic_payload={"input.f90": {"pyi": "def work() -> None: ..."}})

    with pytest.raises(_MainParserError) as exc_info:
        x2py_cli.main()

    assert str(exc_info.value) == "--out cannot be used with both --json and --pyi"


def test_x2py_main_preserves_explicit_pyi_write_contract(monkeypatch):
    semantic_payload = {
        "first.f90": {"pyi": "def first() -> None: ..."},
        "empty.f90": {},
        "second.f90": {"pyi": "def second() -> None: ..."},
    }
    args = _main_args(pyi=True, out="/tmp/api.pyi")
    _install_main_parser(monkeypatch, args)
    _patch_main_report_payloads(monkeypatch, semantic_payload=semantic_payload)
    writes = []
    dependencies = []

    monkeypatch.setattr(
        Path,
        "write_text",
        lambda path, data, **kwargs: writes.append((path, data, kwargs)) or len(data),
    )
    monkeypatch.setattr(
        x2py_cli,
        "_write_pyi_dependencies",
        lambda payload, **kwargs: dependencies.append((payload, kwargs)),
    )

    assert x2py_cli.main() == 0
    assert writes == [
        (Path("/tmp/api.pyi"), "def first() -> None: ...\n\n\n\ndef second() -> None: ...\n", {"encoding": "utf-8"})
    ]
    assert dependencies == [(semantic_payload, {"output_dir": Path("/tmp")})]


def test_x2py_main_preserves_adjacent_pyi_write_contract(monkeypatch):
    semantic_payload = {
        "/tmp/first.f90": {"pyi": "def first() -> None: ..."},
        "/tmp/empty.f90": {},
    }
    args = _main_args(pyi=True, out="")
    _install_main_parser(monkeypatch, args)
    _patch_main_report_payloads(monkeypatch, semantic_payload=semantic_payload)
    writes = []
    dependencies = []

    monkeypatch.setattr(
        Path,
        "write_text",
        lambda path, data, **kwargs: writes.append((path, data, kwargs)) or len(data),
    )
    monkeypatch.setattr(
        x2py_cli,
        "_write_pyi_dependencies",
        lambda payload, **kwargs: dependencies.append((payload, kwargs)),
    )

    assert x2py_cli.main() == 0
    assert writes == [
        (Path("/tmp/first.pyi"), "def first() -> None: ...\n", {"encoding": "utf-8"}),
        (Path("/tmp/empty.pyi"), "\n", {"encoding": "utf-8"}),
    ]
    assert dependencies == [(semantic_payload, {})]


def test_x2py_main_preserves_explicit_and_adjacent_json_write_contracts(monkeypatch):
    writes = []
    monkeypatch.setattr(
        Path,
        "write_text",
        lambda path, data, **kwargs: writes.append((path, data, kwargs)) or len(data),
    )

    explicit_payload = {"input.f90": {"node": 1}}
    explicit_args = _main_args(parse=True, out="/tmp/report.json")
    _install_main_parser(monkeypatch, explicit_args)
    _patch_main_report_payloads(monkeypatch, parse_payload=explicit_payload)
    assert x2py_cli.main() == 0

    adjacent_payload = {
        "/tmp/first.f90": {"node": 1},
        "/tmp/empty.f90": {},
    }
    adjacent_args = _main_args(parse=True, out="")
    _install_main_parser(monkeypatch, adjacent_args)
    _patch_main_report_payloads(monkeypatch, parse_payload=adjacent_payload)
    assert x2py_cli.main() == 0

    readiness_payload = {"readiness": {"wrappable": True}}
    combined_args = _main_args(parse=True, wrap_readiness=True, out="/tmp/combined.json")
    _install_main_parser(monkeypatch, combined_args)
    _patch_main_report_payloads(
        monkeypatch,
        parse_payload=explicit_payload,
        readiness_payload=readiness_payload,
    )
    assert x2py_cli.main() == 0

    readiness_args = _main_args(wrap_readiness=True, out="/tmp/readiness.json")
    _install_main_parser(monkeypatch, readiness_args)
    _patch_main_report_payloads(monkeypatch, readiness_payload=readiness_payload)
    assert x2py_cli.main() == 0

    assert writes == [
        (Path("/tmp/report.json"), json.dumps(explicit_payload, indent=2), {"encoding": "utf-8"}),
        (
            Path("/tmp/first.json"),
            json.dumps({"/tmp/first.f90": {"node": 1}}, indent=2),
            {"encoding": "utf-8"},
        ),
        (Path("/tmp/empty.json"), json.dumps({"/tmp/empty.f90": {}}, indent=2), {"encoding": "utf-8"}),
        (
            Path("/tmp/combined.json"),
            json.dumps({"parse": explicit_payload, "wrap_readiness": readiness_payload}, indent=2),
            {"encoding": "utf-8"},
        ),
        (Path("/tmp/readiness.json"), json.dumps(readiness_payload, indent=2), {"encoding": "utf-8"}),
    ]


def test_x2py_main_preserves_stdout_mode_matrix(monkeypatch, capsys):
    parse_payload = {"parse": {"node": 1}}
    semantic_payload = {"semantic": {"node": 2}}
    readiness_payload = {"readiness": {"wrappable": True}}
    scenarios = [
        (
            {"parse": True, "wrap_readiness": True, "json": True},
            json.dumps({"parse": parse_payload, "wrap_readiness": readiness_payload}, indent=2) + "\n",
            [],
        ),
        ({"semantics": True}, json.dumps(semantic_payload, indent=2) + "\n", []),
        ({"parse": True, "json": True}, json.dumps(parse_payload, indent=2) + "\n", []),
        ({"wrap_readiness": True, "json": True}, json.dumps(readiness_payload, indent=2) + "\n", []),
        ({"wrap_readiness": True}, "READINESS\n", [("readiness-format", readiness_payload)]),
        ({"pyi": True}, "", [("pyi-format", semantic_payload), ("pyi-output", "PYI")]),
        (
            {"parse": True, "wrap_readiness": True, "vars_limit": 2},
            "PARSE\n\nREADINESS\n",
            [
                ("parse-format", parse_payload, {"show_vars": True, "print_limit": 2}),
                ("readiness-format", readiness_payload),
            ],
        ),
        (
            {"pyi": True, "wrap_readiness": True},
            "\nREADINESS\n",
            [
                ("pyi-format", semantic_payload),
                ("pyi-output", "PYI"),
                ("readiness-format", readiness_payload),
            ],
        ),
        (
            {"semantics": True, "wrap_readiness": True},
            json.dumps(semantic_payload, indent=2) + "\n",
            [],
        ),
        (
            {"parse": True},
            "PARSE\n",
            [("parse-format", parse_payload, {"show_vars": False, "print_limit": None})],
        ),
        (
            {"parse": True, "semantics": True},
            json.dumps(parse_payload, indent=2) + "\n",
            [],
        ),
    ]

    for overrides, expected_stdout, expected_formats in scenarios:
        args = _main_args(**overrides)
        _install_main_parser(monkeypatch, args)
        _patch_main_report_payloads(
            monkeypatch,
            parse_payload=parse_payload,
            semantic_payload=semantic_payload,
            readiness_payload=readiness_payload,
        )
        formats = []
        monkeypatch.setattr(
            x2py_cli,
            "_format_report",
            lambda payload, _formats=formats, **kwargs: _formats.append(("parse-format", payload, kwargs)) or "PARSE",
        )
        monkeypatch.setattr(
            x2py_cli,
            "_format_semantic_readiness",
            lambda payload, _formats=formats: _formats.append(("readiness-format", payload)) or "READINESS",
        )
        monkeypatch.setattr(
            x2py_cli,
            "_format_pyi_report",
            lambda payload, _formats=formats: _formats.append(("pyi-format", payload)) or "PYI",
        )
        monkeypatch.setattr(
            x2py_cli,
            "print_pyi_output",
            lambda text, _formats=formats: _formats.append(("pyi-output", text)),
        )

        assert x2py_cli.main() == 0
        assert capsys.readouterr().out == expected_stdout
        assert formats == expected_formats


def test_x2py_main_preserves_c_readable_stdout_contract(monkeypatch, capsys):
    args = _main_args(language="c", parse=True)
    _install_main_parser(monkeypatch, args)
    preprocessing = types.SimpleNamespace(include_dirs=())
    parse_payload = {"parse": {"node": 1}}
    formats = []

    monkeypatch.setattr(x2py_cli, "_resolve_language", lambda paths, language, parser: language)
    monkeypatch.setattr(x2py_cli, "_build_preprocessing_config", lambda active_args, parser: preprocessing)
    monkeypatch.setattr(x2py_cli, "_c_parser_preprocessing_mode", lambda active_preprocessing: "mode")
    monkeypatch.setattr(x2py_cli, "_c_source_loader", lambda active_preprocessing: "loader")
    monkeypatch.setattr(x2py_cli, "parse_c_report", lambda *args, **kwargs: parse_payload)
    monkeypatch.setattr(x2py_cli, "_attach_wrap_readiness", lambda semantic_payload, readiness_payload: None)
    monkeypatch.setattr(
        x2py_cli,
        "format_c_report",
        lambda payload: formats.append(payload) or "C REPORT",
    )

    assert x2py_cli.main() == 0
    assert capsys.readouterr().out == "C REPORT\n"
    assert formats == [parse_payload]


def test_x2py_cli_helpers_cover_language_and_preprocessing_edges(tmp_path: Path, monkeypatch):
    class ErrorParser:
        def error(self, message):
            raise ValueError(message)

    def args(**overrides):
        values = {
            "defines": [],
            "undefs": [],
            "compiler": None,
            "compile_commands": None,
            "preprocessor_adapter": "auto",
            "preprocess_template": None,
            "include_dirs": [],
            "std": None,
            "compiler_args": [],
            "include_exposure": "reachable-project",
            "public_includes": [],
            "private_includes": [],
            "language": "fortran",
        }
        values.update(overrides)
        return types.SimpleNamespace(**values)

    parser = ErrorParser()
    api_h = tmp_path / "api.h"
    api_h.write_text("int add(int x);\n", encoding="utf-8")
    stub = tmp_path / "api.pyi"
    stub.write_text("def add(x: Int32) -> Int32: ...\n", encoding="utf-8")
    upper_stub = tmp_path / "upper.PYI"
    upper_stub.write_text("def upper() -> None: ...\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("ignore", encoding="utf-8")

    assert x2py_cli._expand_pyi_paths([str(tmp_path), str(stub)]) == [stub]
    assert x2py_cli._expand_pyi_paths([str(stub)]) == [stub]
    assert x2py_cli._expand_pyi_paths([str(upper_stub)]) == [upper_stub]
    assert x2py_cli._expand_pyi_paths([str(tmp_path / "notes.txt")]) == []
    assert x2py_cli._resolve_language([str(api_h)], "c", parser) == "c"
    with pytest.raises(ValueError, match="incompatible with --language fortran"):
        x2py_cli._resolve_language([str(api_h)], "fortran", parser)
    with pytest.raises(ValueError, match="requires explicit --language c"):
        x2py_cli._resolve_language([str(api_h)], None, parser)
    with pytest.raises(ValueError, match="Cannot determine"):
        x2py_cli._resolve_language([str(tmp_path / "notes.txt")], None, parser)

    with pytest.raises(ValueError, match="--preprocess-template requires"):
        x2py_cli._build_preprocessing_config(
            args(
                compiler="cc",
                preprocess_template="{compiler} -E {source}",
            ),
            parser,
        )

    class Recipe:
        def to_dict(self):
            return {"mode": "compiler"}

    def preprocess(path, *, language, config):
        assert path == api_h.with_suffix(".f90")
        assert language == "fortran"
        assert config.compiler == "gfortran"
        return "subroutine work()\nend subroutine work\n", Recipe()

    source = api_h.with_suffix(".f90")
    source.write_text("subroutine ignored()\nend subroutine ignored\n", encoding="utf-8")
    monkeypatch.setattr(x2py_cli, "run_compiler_preprocessor_with_recipe", preprocess)
    code, recipe = x2py_cli._fortran_source_for_path(
        source,
        PreprocessingConfig(mode="compiler", compiler="gfortran"),
    )
    assert "subroutine work" in code
    assert recipe == {"mode": "compiler"}
    report = x2py_cli._parse_report(
        [str(source)],
        PreprocessingConfig(mode="compiler", compiler="gfortran"),
    )
    assert report[str(source)]["preprocessing_recipe"] == {"mode": "compiler"}


def test_x2py_build_preprocessing_config_preserves_full_config_contract(monkeypatch):
    args = types.SimpleNamespace(
        defines=["USE_FAST=1"],
        undefs=["LEGACY"],
        compiler="cc",
        compile_commands="compile_commands.json",
        preprocessor_adapter="command-template",
        preprocess_template="{compiler} -E {source}",
        include_dirs=["include"],
        std="c11",
        compiler_args=["--target=test"],
        include_exposure="all-project",
        public_includes=["public.h"],
        private_includes=["private.h"],
        language="c",
    )
    config = types.SimpleNamespace(
        uses_compiler=True,
        command_template=args.preprocess_template,
        adapter=args.preprocessor_adapter,
        compiler=args.compiler,
        compile_commands=args.compile_commands,
        include_dirs=args.include_dirs,
    )
    calls = []

    class Parser:
        def error(self, message):
            raise AssertionError(message)

    def validate(value, option):
        calls.append(("validate", value, option))

    def build(**kwargs):
        calls.append(("build", kwargs))
        return config

    monkeypatch.setattr(x2py_cli, "validate_macro_name", validate)
    monkeypatch.setattr(x2py_cli, "PreprocessingConfig", build)

    assert x2py_cli._build_preprocessing_config(args, Parser()) is config
    assert calls == [
        ("validate", "USE_FAST=1", "--define/-D"),
        ("validate", "LEGACY", "--undef/-U"),
        (
            "build",
            {
                "mode": "compiler",
                "compiler": "cc",
                "compile_commands": "compile_commands.json",
                "adapter": "command-template",
                "command_template": "{compiler} -E {source}",
                "include_dirs": ["include"],
                "defines": ["USE_FAST=1"],
                "undefs": ["LEGACY"],
                "std": "c11",
                "compiler_args": ["--target=test"],
                "include_exposure": "all-project",
                "public_includes": ["public.h"],
                "private_includes": ["private.h"],
            },
        ),
    ]


def test_x2py_build_preprocessing_config_preserves_macro_validation_errors(monkeypatch):
    class Parser:
        def error(self, message):
            raise ValueError(message)

    def args(**overrides):
        values = {
            "defines": [],
            "undefs": [],
            "compiler": None,
            "compile_commands": None,
            "preprocessor_adapter": "auto",
            "preprocess_template": None,
            "include_dirs": [],
            "std": None,
            "compiler_args": [],
            "include_exposure": "reachable-project",
            "public_includes": [],
            "private_includes": [],
            "language": "fortran",
        }
        values.update(overrides)
        return types.SimpleNamespace(**values)

    def reject(value, option):
        raise PreprocessingError(f"{option}: invalid {value}", category="INVALID_MACRO_NAME")

    monkeypatch.setattr(x2py_cli, "validate_macro_name", reject)

    with pytest.raises(ValueError) as define_error:
        x2py_cli._build_preprocessing_config(args(defines=["=bad"]), Parser())
    assert str(define_error.value) == "--define/-D: invalid =bad"

    with pytest.raises(ValueError) as undef_error:
        x2py_cli._build_preprocessing_config(args(undefs=["=bad"]), Parser())
    assert str(undef_error.value) == "--undef/-U: invalid =bad"


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        (
            {"compiler": "cc", "preprocess_template": "{source}"},
            "--preprocess-template requires --preprocessor-adapter command-template",
        ),
    ],
)
def test_x2py_build_preprocessing_config_preserves_validation_diagnostics(overrides, message):
    values = {
        "defines": [],
        "undefs": [],
        "compiler": None,
        "compile_commands": None,
        "preprocessor_adapter": "auto",
        "preprocess_template": None,
        "include_dirs": [],
        "std": None,
        "compiler_args": [],
        "include_exposure": "reachable-project",
        "public_includes": [],
        "private_includes": [],
        "language": "fortran",
    }
    values.update(overrides)

    class Parser:
        def error(self, received):
            raise ValueError(received)

    with pytest.raises(ValueError) as error:
        x2py_cli._build_preprocessing_config(types.SimpleNamespace(**values), Parser())
    assert str(error.value) == message


def test_x2py_resolve_language_handles_requested_and_default_edges(tmp_path: Path):
    class ErrorParser:
        def error(self, message):
            raise ValueError(message)

    parser = ErrorParser()
    input_dir = tmp_path / "inputs"
    input_dir.mkdir()
    c_header = tmp_path / "api.h"
    c_header.write_text("int add(int x);\n", encoding="utf-8")
    f_source = tmp_path / "solver.F90"
    f_source.write_text("subroutine solve()\nend subroutine solve\n", encoding="utf-8")
    stub = tmp_path / "iface.PYI"
    stub.write_text("def solve() -> None: ...\n", encoding="utf-8")
    unknown = tmp_path / "notes.txt"
    unknown.write_text("notes\n", encoding="utf-8")

    assert x2py_cli._resolve_language([str(unknown)], "c", parser) == "c"
    with pytest.raises(ValueError) as requested_error:
        x2py_cli._resolve_language([str(input_dir), str(c_header)], "fortran", parser)
    assert str(requested_error.value) == (
        f"C input {c_header} is incompatible with --language fortran; pass --language c. Use --help for examples."
    )

    with pytest.raises(ValueError) as directory_error:
        x2py_cli._resolve_language([str(input_dir)], None, parser)
    assert str(directory_error.value) == (
        f"Input directory {input_dir} requires an explicit frontend; "
        "pass --language fortran or --language c. Use --help for examples."
    )

    assert x2py_cli._resolve_language([str(f_source)], None, parser) == "fortran"
    assert x2py_cli._resolve_language([str(stub)], None, parser) == "fortran"

    with pytest.raises(ValueError) as unknown_error:
        x2py_cli._resolve_language([str(unknown)], None, parser)
    assert str(unknown_error.value) == (
        f"Cannot determine the input language for {unknown}; "
        "pass --language fortran or --language c. Use --help for examples."
    )


def test_x2py_and_fortran_module_entrypoints_and_debug_errors(monkeypatch, capsys):
    original_fortran_main = fortran_parser_cli.main
    monkeypatch.setattr(x2py_cli, "main", lambda: 0)
    with pytest.raises(SystemExit) as x2py_exit:
        runpy.run_module("x2py.__main__", run_name="__main__")
    assert x2py_exit.value.code == 0

    monkeypatch.setattr(fortran_parser_cli, "main", lambda: 0)
    with pytest.raises(SystemExit) as fortran_exit:
        runpy.run_module("fortran_parser.__main__", run_name="__main__")
    assert fortran_exit.value.code == 0
    monkeypatch.setattr(fortran_parser_cli, "main", original_fortran_main)

    def fail_parse(_paths):
        raise FortranParseError("bad", filename="bad.f90", line_number=1, source_line="bad")

    monkeypatch.setattr(fortran_parser_cli, "_parse_paths", fail_parse)
    monkeypatch.setattr(sys, "argv", ["fortran_parser", "bad.f90", "--no-color"])
    assert fortran_parser_cli.main() == 1
    assert "bad.f90:1:1: error[PARSE_ERROR]: bad" in capsys.readouterr().err
    monkeypatch.setenv("FORTRAN_PARSER_DEBUG", "1")
    with pytest.raises(FortranParseError):
        fortran_parser_cli.main()


def test_x2py_main_debug_reraises_preprocessing_errors(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["x2py", str(TEST_FILE), "--parse"])
    monkeypatch.setenv("X2PY_DEBUG", "1")

    def fail_parse(_paths, _preprocessing):
        raise PreprocessingError("plain failure", category="PREPROCESSOR_FAILED")

    monkeypatch.setattr(x2py_cli, "_parse_report", fail_parse)
    with pytest.raises(PreprocessingError):
        x2py_cli.main()


def test_cli_out_requires_stage_flag():
    cmd = [sys.executable, "-m", "x2py", str(TEST_FILE), "--out"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 2
    assert "--out requires a stage flag" in res.stderr


def test_cli_help_includes_examples():
    cmd = [sys.executable, "-m", "x2py", "--help"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "Examples:" in res.stdout
    assert "Parse, compact tree:" in res.stdout
    assert "python -m x2py path/to/file.f90 --parse" in res.stdout
    assert "python -m x2py path/to/file.f90 --parse --show-vars" in res.stdout
    assert "python -m x2py path/to/file.f90 --parse --print-limit 50" in res.stdout
    assert "python -m x2py path/to/file.f90 --pyi --out module.pyi" in res.stdout


def test_x2py_main_preserves_argument_parser_contract(monkeypatch):
    class StopAfterParserSetup(Exception):
        pass

    captured = {}

    class FakeParser:
        def __init__(self, *args, **kwargs):
            captured["parser"] = (args, kwargs)
            captured["arguments"] = []

        def add_argument(self, *args, **kwargs):
            captured["arguments"].append((args, kwargs))

        def parse_args(self):
            raise StopAfterParserSetup

    monkeypatch.setattr(x2py_cli.argparse, "ArgumentParser", FakeParser)

    with pytest.raises(StopAfterParserSetup):
        x2py_cli.main()

    assert captured["parser"] == (
        (),
        {
            "description": "x2py CLI for parser and semantic conversion stages.",
            "formatter_class": x2py_cli.argparse.RawDescriptionHelpFormatter,
            "epilog": (
                "Examples:\n"
                "  Parse, compact tree:\n"
                "    python -m x2py path/to/file.f90 --parse\n"
                "  Parse, include scope variables:\n"
                "    python -m x2py path/to/file.f90 --parse --show-vars\n"
                "  Parse, cap every repeated section to 50 items:\n"
                "    python -m x2py path/to/file.f90 --parse --print-limit 50\n"
                "  Parse, include variables and cap every repeated section:\n"
                "    python -m x2py path/to/file.f90 --parse --show-vars --print-limit 50\n"
                "  Parse directory recursively:\n"
                "    python -m x2py path/to/src_dir --language fortran --parse --print-limit 20\n"
                "  Print parser JSON:\n"
                "    python -m x2py path/to/file.f90 --parse --json\n"
                "  Parse C subset JSON:\n"
                "    python -m x2py path/to/api.h --language c --parse --json\n"
                "  Parse C with an exact compiler executable and API flags:\n"
                "    python -m x2py path/to/api.h --language c --parse --compiler clang-18 -I include -D API_EXPORT= --std c11\n"
                "  Parse C with a compiler path and target/sysroot passthrough flags:\n"
                "    python -m x2py path/to/api.c --language c --parse --compiler /usr/bin/gcc-13 --compiler-arg=--sysroot=/opt/sdk\n"
                "  Parse C with compile_commands.json for project flags:\n"
                "    python -m x2py path/to/api.c --language c --parse --compile-commands build/compile_commands.json\n"
                "  Parse Fortran with an exact compiler executable:\n"
                "    python -m x2py path/to/file.F90 --parse --compiler /usr/bin/gfortran-12 -I include -D USE_MPI\n"
                "  Parse with a custom preprocessing command template:\n"
                "    python -m x2py path/to/api.h --language c --parse --preprocessor-adapter command-template --preprocess-template 'cc -E {include_dirs} {defines} {source}'\n"
                "  Write parser JSON:\n"
                "    python -m x2py path/to/file.f90 --parse --json --out report.json\n"
                "  Write one JSON file next to each source:\n"
                "    python -m x2py path/to/src_dir --language fortran --parse --out\n"
                "  Show wrap-readiness only:\n"
                "    python -m x2py path/to/file.f90 --wrap-readiness\n"
                "  Print semantic IR JSON:\n"
                "    python -m x2py path/to/file.f90 --semantics\n"
                "  Print generated Python stub text:\n"
                "    python -m x2py path/to/file.f90 --pyi\n"
                "  Write generated Python stub text:\n"
                "    python -m x2py path/to/file.f90 --pyi --out module.pyi\n"
                "  Print semantic IR with readiness attached:\n"
                "    python -m x2py path/to/file.f90 --semantics --wrap-readiness\n"
                "  Check edited .pyi semantic readiness:\n"
                "    python -m x2py path/to/module.pyi --wrap-readiness\n"
                "  Print semantic readiness JSON:\n"
                "    python -m x2py path/to/module.pyi --wrap-readiness --json\n"
                "\nOptional:\n"
                "  Install 'rich' for colored terminal syntax highlighting:\n"
                "      pip install rich"
            ),
        },
    )
    assert captured["arguments"] == [
        (("paths",), {"nargs": "+", "help": "Source file(s), .pyi file(s), or directory path(s)"}),
        (
            ("--language",),
            {
                "choices": ("fortran", "c"),
                "default": None,
                "help": (
                    "Frontend language. Omission is allowed for recognizable Fortran files and .pyi readiness input; "
                    "C files, directories, and unknown-suffix source inputs require this flag."
                ),
            },
        ),
        (("--parse",), {"action": "store_true", "help": "Run and output parser stage report"}),
        (
            ("--preprocessor-adapter",),
            {
                "choices": ("auto", "gcc-compatible-c", "gnu-fortran", "command-template"),
                "default": "auto",
                "help": "Compiler adapter family. Use command-template for unsupported compiler families.",
            },
        ),
        (
            ("--compiler",),
            {
                "help": (
                    "Exact compiler/preprocessor executable, e.g. gcc-13, "
                    "clang-18, /usr/bin/gfortran-12, or /opt/intel/oneapi/compiler/latest/bin/ifx."
                )
            },
        ),
        (
            ("--compile-commands",),
            {
                "metavar": "PATH",
                "help": "compile_commands.json database used for compiler preprocessing.",
            },
        ),
        (
            ("--preprocess-template",),
            {
                "metavar": "TEMPLATE",
                "help": (
                    "Custom preprocessing command template. Supported placeholders include {source}, "
                    "{include_dirs}, {defines}, {undefs}, {standard}, and {compiler_args}."
                ),
            },
        ),
        (
            ("-I", "--include-dir"),
            {
                "dest": "include_dirs",
                "action": "append",
                "metavar": "DIR",
                "help": "Include directory passed as -IDIR during compiler preprocessing.",
            },
        ),
        (
            ("-D", "--define"),
            {
                "dest": "defines",
                "action": "append",
                "metavar": "NAME[=VALUE]",
                "help": "Define a preprocessing macro. NAME means NAME=1; NAME=VALUE preserves VALUE.",
            },
        ),
        (
            ("-U", "--undef"),
            {
                "dest": "undefs",
                "action": "append",
                "metavar": "NAME",
                "help": "Undefine a preprocessing macro.",
            },
        ),
        (
            ("--std",),
            {
                "metavar": "STANDARD",
                "help": "Language standard passed to compiler mode, e.g. c11, c23, f2008, or f2018.",
            },
        ),
        (
            ("--compiler-arg",),
            {
                "dest": "compiler_args",
                "action": "append",
                "metavar": "ARG",
                "help": "Raw compiler preprocessing argument. Use --compiler-arg=-target for values starting with '-'.",
            },
        ),
        (
            ("--include-exposure",),
            {
                "choices": ("reachable-project", "roots-only"),
                "default": "reachable-project",
                "help": "Public wrapper exposure policy for reachable included files.",
            },
        ),
        (
            ("--public-include",),
            {
                "dest": "public_includes",
                "action": "append",
                "metavar": "PATH_OR_PATTERN",
                "help": "Force a matched included file to be public in wrapper output.",
            },
        ),
        (
            ("--private-include",),
            {
                "dest": "private_includes",
                "action": "append",
                "metavar": "PATH_OR_PATTERN",
                "help": "Force a matched included file to be private in wrapper output.",
            },
        ),
        (
            ("--show-vars",),
            {
                "action": "store_true",
                "help": "Include module, submodule, program, and block-data variables in the human-readable parse report.",
            },
        ),
        (
            ("--print-limit",),
            {
                "type": int,
                "metavar": "N",
                "help": "Show at most N items per repeated section in the human-readable parse report.",
            },
        ),
        (("--vars-limit",), {"type": int, "metavar": "N", "help": x2py_cli.argparse.SUPPRESS}),
        (
            ("--wrap-readiness",),
            {
                "action": "store_true",
                "help": "Convert Fortran, C, or .pyi input to semantic IR and show wrapper readiness",
            },
        ),
        (
            ("--semantics",),
            {"action": "store_true", "help": "Generate semantic IR models from parsed source modules"},
        ),
        (("--pyi",), {"action": "store_true", "help": "Generate semantic Python .pyi content"}),
        (("--json",), {"action": "store_true", "help": "Print JSON to stdout"}),
        (
            ("--out",),
            {
                "nargs": "?",
                "const": "",
                "type": str,
                "help": "Write stage output to file (optional explicit output filename)",
            },
        ),
        (("--no-color",), {"action": "store_true", "help": "Disable ANSI color in parse diagnostics"}),
        (
            ("--debug", "--debug-traceback"),
            {
                "dest": "debug",
                "action": "store_true",
                "help": "Re-raise parser errors so Python prints a traceback for parser debugging",
            },
        ),
    ]


def test_cli_requires_explicit_language_for_directory_and_unknown_suffix(tmp_path: Path):
    source = tmp_path / "solver.source"
    source.write_text("subroutine solve()\nend subroutine solve\n", encoding="utf-8")

    unknown = subprocess.run(
        [sys.executable, "-m", "x2py", str(source), "--parse"],
        capture_output=True,
        text=True,
    )
    assert unknown.returncode == 2
    assert "Cannot determine the input language" in unknown.stderr
    assert "--language fortran or --language c" in unknown.stderr

    directory = subprocess.run(
        [sys.executable, "-m", "x2py", str(tmp_path), "--parse"],
        capture_output=True,
        text=True,
    )
    assert directory.returncode == 2
    assert "requires an explicit frontend" in directory.stderr

    explicit = subprocess.run(
        [sys.executable, "-m", "x2py", str(source), "--language", "fortran", "--parse"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "subroutine solve" in explicit.stdout


def test_cli_rejects_fortran_file_with_explicit_c_frontend(tmp_path: Path):
    source = tmp_path / "solver.f90"
    source.write_text("subroutine solve()\nend subroutine solve\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "x2py", str(source), "--language", "c", "--parse"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "incompatible with --language c" in result.stderr
    assert "pass --language fortran" in result.stderr


def test_cli_fortran_rejects_embedded_c_declaration_outside_execution_body(tmp_path: Path):
    source = tmp_path / "solver.f90"
    source.write_text(
        "subroutine solve()\n  int add(int a, int b);\nend subroutine solve\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "x2py", str(source), "--pyi"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "PARSE_UNSUPPORTED_DECLARATION" in result.stderr
    assert "Unknown or unsupported datatype declaration" in result.stderr


def test_cli_parse_shows_module_derived_types_and_derived_arg_kinds():
    fixture = Path(__file__).parent.parent / "data" / "fortran" / "general" / "modern_pyi_example.f90"
    cmd = [sys.executable, "-m", "x2py", str(fixture), "--parse"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    assert "      Derived types: 3" in res.stdout
    assert "type particle" in res.stdout
    assert "Fields: 3" in res.stdout
    assert "- id:integer[0]" in res.stdout
    assert "- mass:real(8)[0]" in res.stdout
    assert "- position:real(8)[1]" in res.stdout
    assert "init_particle(p:type(particle)[0]" in res.stdout


def test_cli_parse_modern_fixture_prints_derived_block_verbatim():
    fixture = Path(__file__).parent.parent / "data" / "fortran" / "general" / "modern_pyi_example.f90"
    cmd = [sys.executable, "-m", "x2py", str(fixture), "--parse"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    expected_block = """      Derived types: 3
        - type particle (fields=3, methods=0)
          Fields: 3
            - id:integer[0]
            - mass:real(8)[0]
            - position:real(8)[1]
        - type vector3 (fields=1, methods=0)
          Fields: 1
            - values:real(8)[1]
        - type hidden_state (fields=1, methods=0)
          Fields: 1
            - code:integer[0]
"""
    assert expected_block in res.stdout


def test_fortran_parser_cli_helper_branches(tmp_path: Path, monkeypatch):
    @dataclass
    class Node:
        name: str
        parent: object = None

    monkeypatch.setenv("FORTRAN_PARSER_TEST_FLAG", " yes ")
    assert fortran_parser_cli._env_flag("FORTRAN_PARSER_TEST_FLAG") is True
    monkeypatch.delenv("FORTRAN_PARSER_TEST_FLAG")
    assert fortran_parser_cli._env_flag("FORTRAN_PARSER_TEST_FLAG") is False

    assert fortran_parser_cli._diagnostic_color_enabled(disabled=True) is False
    monkeypatch.setenv("NO_COLOR", "1")
    assert fortran_parser_cli._diagnostic_color_enabled(disabled=False) is False
    monkeypatch.delenv("NO_COLOR")
    assert fortran_parser_cli._diagnostic_color_enabled(disabled=False) is True

    parent = Node("root")
    assert fortran_parser_cli._to_dict_no_parent(Node("child", parent=parent)) == {"name": "child"}
    assert fortran_parser_cli._to_dict_no_parent(Node("child", parent="root")) == {
        "name": "child",
        "parent": "root",
    }

    source = tmp_path / "nested" / "mini.f90"
    source.parent.mkdir()
    source.write_text("subroutine work(n)\n  integer, intent(in) :: n\nend subroutine work\n", encoding="utf-8")
    (source.parent / "notes.txt").write_text("ignore", encoding="utf-8")

    assert fortran_parser_cli._collect_extensions(tmp_path) == [source]
    report = fortran_parser_cli._parse_paths([str(tmp_path)])
    assert list(report) == [str(source)]
    assert report[str(source)]["signatures"][0]["name"] == "work"


def test_fortran_parser_cli_formatting_branches():
    report = fortran_parser_cli._format_report(
        {
            "types.f90": {
                "signatures": [],
                "types": [{"name": "particle", "fields": [], "methods": []}],
                "modules": [],
                "submodules": [],
                "programs": [],
                "block_data": [],
            }
        }
    )
    assert "Derived types: 1" in report
    assert "- type particle (fields=0, methods=0)" in report
    assert (
        fortran_parser_cli._format_var_type({"base_type": "derived", "kind": "particle", "rank": 0})
        == "type(particle)[0]"
    )
    assert fortran_parser_cli._format_var_type({"base_type": "real", "kind": "4", "rank": 2}) == "real(4)[2]"


def test_fortran_parser_cli_format_report_print_limit_covers_sections():
    var_a = {"name": "a", "base_type": "integer", "kind": "", "rank": 0}
    var_b = {"name": "b", "base_type": "real", "kind": "8", "rank": 1}
    field_a = {"name": "left", "base_type": "integer", "kind": "", "rank": 0}
    field_b = {"name": "right", "base_type": "integer", "kind": "", "rank": 0}
    proc_a = {"kind": "subroutine", "name": "first", "arguments": [var_a], "result": None}
    proc_b = {"kind": "function", "name": "second", "arguments": [], "result": var_b}
    dtype_a = {"name": "pair", "fields": [field_a, field_b], "methods": []}
    dtype_b = {"name": "hidden_pair", "fields": [], "methods": []}

    report = fortran_parser_cli._format_report(
        {
            "mixed.f90": {
                "signatures": [proc_a, proc_b],
                "types": [dtype_a, dtype_b],
                "modules": [
                    {
                        "name": "m1",
                        "variables": [var_a, var_b],
                        "uses": {},
                        "derived_types": [dtype_a, dtype_b],
                        "procedures": [proc_a, proc_b],
                    },
                    {
                        "name": "m2",
                        "variables": [],
                        "uses": {},
                        "derived_types": [],
                        "procedures": [],
                    },
                ],
                "submodules": [
                    {
                        "name": "sm1",
                        "parent": "m1",
                        "ancestor": None,
                        "variables": [var_a, var_b],
                        "uses": {},
                        "procedures": [proc_a, proc_b],
                    },
                    {
                        "name": "sm2",
                        "parent": "m1",
                        "ancestor": "root",
                        "variables": [],
                        "uses": {},
                        "procedures": [],
                    },
                ],
                "programs": [
                    {"name": "driver", "variables": [var_a, var_b], "uses": {}},
                    {"name": "other_driver", "variables": [], "uses": {}},
                ],
                "block_data": [
                    {"name": None, "variables": [var_a, var_b]},
                    {"name": "named_block", "variables": []},
                ],
            }
        },
        show_vars=True,
        print_limit=1,
    )

    assert "  Procedures: 2" in report
    assert "    - subroutine first(a:integer[0])" in report
    assert "    ... 1 more procedures" in report
    assert "  Derived types: 2" in report
    assert "    ... 1 more derived types" in report
    assert "  Modules: 2" in report
    assert "    - module m1 (vars=2, uses=0)" in report
    assert "      Variables: 2" in report
    assert "        - a:integer[0]" in report
    assert "        ... 1 more variables" in report
    assert "            - left:integer[0]" in report
    assert "            ... 1 more fields" in report
    assert "        ... 1 more derived types" in report
    assert "        ... 1 more procedures" in report
    assert "    ... 1 more modules" in report
    assert "  Submodules: 2" in report
    assert "    - submodule sm1 (parent=m1, vars=2, uses=0)" in report
    assert "    ... 1 more submodules" in report
    assert "  Programs: 2" in report
    assert "    - program driver (vars=2, uses=0)" in report
    assert "    ... 1 more programs" in report
    assert "  Block data: 2" in report
    assert "    - block data <unnamed> (vars=2)" in report
    assert "    ... 1 more block data units" in report

    assert fortran_parser_cli._format_variable_lines([], indent="  ", print_limit=1) == []


def test_fortran_parser_cli_json_and_parse_errors(tmp_path: Path):
    good = tmp_path / "good.f90"
    good.write_text("subroutine work(n)\n  integer, intent(in) :: n\nend subroutine work\n", encoding="utf-8")

    json_cmd = [sys.executable, "-m", "fortran_parser", str(good), "--json"]
    json_res = subprocess.run(json_cmd, capture_output=True, text=True, check=True)
    assert str(good) in json.loads(json_res.stdout)

    bad = tmp_path / "bad.f90"
    bad.write_text("subroutine bad(x)\n  weirdtype :: x\nend subroutine bad\n", encoding="utf-8")
    bad_cmd = [sys.executable, "-m", "fortran_parser", str(bad), "--no-color"]
    bad_res = subprocess.run(bad_cmd, capture_output=True, text=True)
    assert bad_res.returncode == 1
    assert bad_res.stdout == ""
    assert "Traceback" not in bad_res.stderr
    assert "Unknown or unsupported datatype" in bad_res.stderr


def test_x2py_cli_helper_branches(tmp_path: Path, monkeypatch, capsys):
    @dataclass
    class Node:
        name: str
        parent: object = None

    @dataclass
    class ParentFirstNode:
        parent: object
        name: str

    monkeypatch.setenv("X2PY_TEST_FLAG", "ON")
    assert x2py_cli._env_flag("X2PY_TEST_FLAG") is True
    monkeypatch.delenv("X2PY_TEST_FLAG")
    assert x2py_cli._env_flag("X2PY_TEST_FLAG") is False

    assert x2py_cli._diagnostic_color_enabled(disabled=True) is False
    monkeypatch.setenv("NO_COLOR", "1")
    assert x2py_cli._diagnostic_color_enabled(disabled=False) is False
    monkeypatch.delenv("NO_COLOR")

    assert x2py_cli._to_dict_no_parent(Node("child", parent=Node("root"))) == {"name": "child"}
    assert x2py_cli._to_dict_no_parent(ParentFirstNode(parent=Node("root"), name="child")) == {"name": "child"}
    assert x2py_cli._to_dict_no_parent({"node": Node("child", parent=Node("root"))}) == {"node": {"name": "child"}}

    source = tmp_path / "mini.f90"
    source.write_text("subroutine work(n)\n  integer, intent(in) :: n\nend subroutine work\n", encoding="utf-8")
    assert x2py_cli._collect_extensions(tmp_path) == [source]
    assert x2py_cli._expand_paths([str(tmp_path)]) == [source]

    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    real_import = builtins.__import__

    def fail_rich_import(name, *args, **kwargs):
        if name.startswith("rich"):
            raise ImportError("rich disabled for test")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fail_rich_import)
    x2py_cli.print_pyi_output("def f() -> None: ...")
    assert "def f() -> None: ..." in capsys.readouterr().out


def test_x2py_print_pyi_output_uses_rich_and_falls_back(monkeypatch, capsys):
    calls = []

    class FakeSyntax:
        def __init__(self, code, lexer, **options):
            self.code = code
            self.lexer = lexer
            self.options = options

    class FakeConsole:
        def __init__(self, **options):
            self.options = options

        def print(self, syntax):
            calls.append((syntax.code, syntax.lexer, syntax.options, self.options))

    rich_module = types.ModuleType("rich")
    console_module = types.ModuleType("rich.console")
    syntax_module = types.ModuleType("rich.syntax")
    console_module.Console = FakeConsole
    syntax_module.Syntax = FakeSyntax
    monkeypatch.setitem(sys.modules, "rich", rich_module)
    monkeypatch.setitem(sys.modules, "rich.console", console_module)
    monkeypatch.setitem(sys.modules, "rich.syntax", syntax_module)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)

    x2py_cli.print_pyi_output("def f() -> None: ...")
    assert calls == [
        (
            "def f() -> None: ...",
            "python",
            {
                "theme": "ansi_dark",
                "background_color": "default",
                "line_numbers": False,
                "word_wrap": False,
            },
            {"force_terminal": True, "color_system": "auto"},
        )
    ]
    assert capsys.readouterr().out == ""

    class RaisingConsole(FakeConsole):
        def print(self, syntax):
            raise RuntimeError("terminal failed")

    console_module.Console = RaisingConsole
    x2py_cli.print_pyi_output("def g() -> None: ...")
    assert "def g() -> None: ..." in capsys.readouterr().out


@pytest.mark.parametrize(
    ("extra_args", "message"),
    [
        ([], "Select at least one stage flag"),
    ],
)
def test_x2py_cli_rejects_invalid_stage_combinations(extra_args, message):
    cmd = [sys.executable, "-m", "x2py", str(TEST_FILE), *extra_args]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 2
    assert message in res.stderr


def test_fortran_parser_cli_debug_flag_reraises_parse_errors(tmp_path: Path):
    f90 = tmp_path / "bad.f90"
    f90.write_text(
        """subroutine bad(x)
  weirdtype :: x
end subroutine bad
""",
        encoding="utf-8",
    )

    cmd = [sys.executable, "-m", "fortran_parser", str(f90), "--debug"]
    res = subprocess.run(cmd, capture_output=True, text=True)

    assert res.returncode == 1
    assert "Traceback" in res.stderr
    assert "FortranParseError" in res.stderr


def test_fortran_parser_cli_debug_traceback_env_reraises_parse_errors(tmp_path: Path):
    f90 = tmp_path / "bad.f90"
    f90.write_text(
        """subroutine bad(x)
  weirdtype :: x
end subroutine bad
""",
        encoding="utf-8",
    )

    cmd = [sys.executable, "-m", "fortran_parser", str(f90)]
    res = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env={**os.environ, "FORTRAN_PARSER_DEBUG": "1"},
    )

    assert res.returncode == 1
    assert "Traceback" in res.stderr
    assert "note: parser raised at" in res.stderr


def test_fortran_parser_main_public_api_modes_from_inline_source(tmp_path: Path, monkeypatch, capsys):
    f90 = tmp_path / "mini.f90"
    f90.write_text(
        """module m
contains
  subroutine work(n)
    integer, intent(in) :: n
  end subroutine work
end module m
""",
        encoding="utf-8",
    )
    json_out = tmp_path / "report.json"

    monkeypatch.setattr(sys, "argv", ["fortran_parser", str(f90), "--json-out", str(json_out), "--json"])
    assert fortran_parser_cli.main() == 0
    stdout_payload = json.loads(capsys.readouterr().out)
    assert str(f90) in stdout_payload
    assert json_out.exists()

    monkeypatch.setattr(sys, "argv", ["fortran_parser", str(f90), "--pyi"])
    assert fortran_parser_cli.main() == 0
    pyi_out = capsys.readouterr().out
    assert "File:" in pyi_out
    assert "def work(" in pyi_out

    monkeypatch.setattr(sys, "argv", ["fortran_parser", str(f90)])
    assert fortran_parser_cli.main() == 0
    readable = capsys.readouterr().out
    assert "module m" in readable


def test_x2py_main_public_api_modes_from_inline_source(tmp_path: Path, monkeypatch, capsys):
    f90 = tmp_path / "mini.f90"
    f90.write_text(
        """module m
contains
  subroutine work(n)
    integer, intent(in) :: n
  end subroutine work
end module m
""",
        encoding="utf-8",
    )
    json_out = tmp_path / "parse.json"

    monkeypatch.setattr(sys, "argv", ["x2py", str(f90), "--parse", "--json", "--out", str(json_out)])
    assert x2py_cli.main() == 0
    assert capsys.readouterr().out == ""
    assert json.loads(json_out.read_text(encoding="utf-8")).get(str(f90)) is not None

    monkeypatch.setattr(sys, "argv", ["x2py", str(f90), "--pyi"])
    assert x2py_cli.main() == 0
    assert "def work(" in capsys.readouterr().out

    monkeypatch.setattr(sys, "argv", ["x2py", str(f90), "--parse"])
    assert x2py_cli.main() == 0
    assert "module m" in capsys.readouterr().out


def test_x2py_readiness_formatting_and_compiler_without_requirements():
    assert (
        x2py_cli._format_semantic_blocker_item(
            "unresolved_semantic_types",
            {"owner": "module.api", "type": "external_t"},
        )
        == "module.api uses unresolved type external_t"
    )
    assert (
        x2py_cli._format_semantic_blocker_item(
            "unresolved_shape_symbols",
            {"owner": "module.api", "expression": "n + 1", "symbol": "n"},
        )
        == "module.api shape 'n + 1' uses unresolved symbol n"
    )
    assert (
        x2py_cli._format_semantic_blocker_item(
            "missing_compile_time_values",
            {"owner": "module.api", "symbol": "dp"},
        )
        == "module.api needs literal value for Final constant dp"
    )
    assert (
        x2py_cli._format_semantic_blocker_item(
            "callback_signature_incomplete",
            {"owner": "handler", "needs": ["arguments", "return type"]},
        )
        == "handler needs Callable[[...], ...] metadata (arguments, return type)"
    )
    assert x2py_cli._format_semantic_blocker_item("c_unknown_type", {"owner": "api", "type": "widget"}) == "api: widget"
    assert x2py_cli._format_semantic_blocker_item("c_unknown_type", {"type": "widget"}) == "<c-source>: widget"
    assert x2py_cli._format_semantic_blocker_item("c_macro_value", {"owner": "api", "source": "SIZE"}) == "api: SIZE"
    assert (
        x2py_cli._format_semantic_blocker_item("c_function_pointer", {"owner": "api", "function": "callback"})
        == "api: callback"
    )
    assert (
        x2py_cli._format_semantic_blocker_item("c_parameter_type", {"owner": "api", "parameter": "arg"}) == "api: arg"
    )
    assert x2py_cli._format_semantic_blocker_item("c_unresolved_type", {"owner": "api", "type": "missing_t"}) == (
        "api: missing_t"
    )
    assert (
        x2py_cli._format_semantic_blocker_item("no_public_api", {"owner": "module", "needs": ["function", "class"]})
        == "module needs function, class"
    )
    assert x2py_cli._format_semantic_blocker_item("unknown", {"value": 1}) == "{'value': 1}"

    semantic_payload = {"source": {"semantic_modules": []}}
    x2py_cli._attach_wrap_readiness(semantic_payload, {"other": {"wrap_readiness": {"wrappable": True}}})
    assert "wrap_readiness" not in semantic_payload["source"]

    parsed = x2py_cli.FortranParser().visit_file("module empty\nend module empty\n", filename="empty.f90")
    config = x2py_cli.PreprocessingConfig(mode="compiler", compiler="gfortran")
    assert x2py_cli._fortran_compile_time_values(parsed, config) is None


def test_x2py_fortran_readiness_helpers_attach_and_compile(monkeypatch):
    ready = {"wrappable": True, "n_functions": 1}
    payload = {"missing.f90": {}, "api.f90": {}}
    x2py_cli._attach_wrap_readiness(payload, {"api.f90": {"wrap_readiness": ready}})
    assert payload == {"missing.f90": {}, "api.f90": {"wrap_readiness": ready}}

    x2py_cli._attach_wrap_readiness(None, {"api.f90": {"wrap_readiness": ready}})
    x2py_cli._attach_wrap_readiness({"api.f90": {}}, None)

    parsed = x2py_cli.FortranParser().visit_file(
        "module api_mod\n  type :: Widget_T\n  end type Widget_T\nend module api_mod\n",
        filename="api.f90",
    )
    assert x2py_cli._fortran_wrapped_derived_types([parsed]) == {("api_mod", "widget_t")}

    calls = []
    requirements = {"api_mod": {"dp": "kind(1.0d0)"}}
    values = {"api_mod.dp": 8}

    def collect_requirements(received):
        assert received is parsed
        calls.append(("collect", received))
        return requirements

    def evaluate_requirements(received_config, received_requirements):
        assert received_config is compiler_config
        assert received_requirements is requirements
        calls.append(("evaluate", received_config, received_requirements))
        return values

    monkeypatch.setattr("semantics.fortran2ir.collect_semantic_compile_time_requirements", collect_requirements)
    monkeypatch.setattr("x2py.fortran_type_probe.evaluate_fortran_type_requirements", evaluate_requirements)

    raw_config_with_compiler = x2py_cli.PreprocessingConfig(compiler="gfortran")
    assert x2py_cli._fortran_compile_time_values(parsed, raw_config_with_compiler) is None
    assert calls == []

    compiler_config = x2py_cli.PreprocessingConfig(mode="compiler", compiler="gfortran")
    assert x2py_cli._fortran_compile_time_values(parsed, compiler_config) == values
    assert calls == [("collect", parsed), ("evaluate", compiler_config, requirements)]


def test_x2py_fortran_source_for_path_raw_uses_utf8_and_internal_recipe():
    class RawPath:
        def read_text(self, *, encoding):
            assert encoding is not None
            assert encoding.lower() == "utf-8"
            return "subroutine raw()\nend subroutine raw\n"

    class RawPreprocessing:
        uses_compiler = False

        def fortran_internal_recipe(self, received):
            assert received is path
            return {"mode": "internal"}

    path = RawPath()

    assert x2py_cli._fortran_source_for_path(path, RawPreprocessing()) == (
        "subroutine raw()\nend subroutine raw\n",
        {"mode": "internal"},
    )


def test_x2py_parse_report_preserves_fortran_parser_and_recipe_contracts(monkeypatch):
    path = Path("api.F90")
    explicit_config = object()
    default_config = object()
    recipe = {"mode": "compiler"}
    nodes = {
        "signature": object(),
        "type": object(),
        "module": object(),
        "submodule": object(),
        "program": object(),
        "block_data": object(),
    }
    labels = {node: {"node": label} for label, node in nodes.items()}
    parsed = types.SimpleNamespace(
        procedures=[nodes["signature"]],
        derived_types=[nodes["type"]],
        modules=[nodes["module"]],
        submodules=[nodes["submodule"]],
        programs=[nodes["program"]],
        block_data_units=[nodes["block_data"]],
    )
    calls = []

    def make_config():
        calls.append(("config",))
        return default_config

    def expand(paths):
        assert paths == ["api"]
        calls.append(("expand", paths))
        return [path]

    def source(received_path, config):
        assert received_path == path
        assert config in {explicit_config, default_config}
        calls.append(("source", received_path, config))
        if config is explicit_config:
            return "explicit source", recipe
        return "default source", None

    class Parser:
        def visit_file(self, code, *, filename):
            assert code in {"explicit source", "default source"}
            assert filename == str(path)
            calls.append(("visit", code, filename))
            return parsed

    def serialize(node):
        assert node in labels
        calls.append(("serialize", node))
        return labels[node]

    payload = {
        "signatures": [labels[nodes["signature"]]],
        "types": [labels[nodes["type"]]],
        "modules": [labels[nodes["module"]]],
        "submodules": [labels[nodes["submodule"]]],
        "programs": [labels[nodes["program"]]],
        "block_data": [labels[nodes["block_data"]]],
    }

    monkeypatch.setattr(x2py_cli, "PreprocessingConfig", make_config)
    monkeypatch.setattr(x2py_cli, "FortranParser", Parser)
    monkeypatch.setattr(x2py_cli, "_expand_paths", expand)
    monkeypatch.setattr(x2py_cli, "_fortran_source_for_path", source)
    monkeypatch.setattr(x2py_cli, "_to_dict_no_parent", serialize)

    assert x2py_cli._parse_report(["api"], explicit_config) == {str(path): {**payload, "preprocessing_recipe": recipe}}
    assert ("config",) not in calls

    calls.clear()
    assert x2py_cli._parse_report(["api"]) == {str(path): payload}
    assert calls[0] == ("config",)


def test_x2py_semantic_report_preserves_c_module_and_dependency_contracts(monkeypatch):
    path = Path("api.h")
    config = object()
    project = object()
    module = types.SimpleNamespace(name="api", origin=types.SimpleNamespace(native_name=str(path)))
    stubs = {
        "api": "def api() -> None: ...",
        "shared": "class Shared:\n    pass",
    }

    def parse_project(paths, preprocessing):
        assert paths == ["api"]
        assert preprocessing is config
        return project

    def convert(received):
        assert received is project
        return [module]

    def expand(paths):
        assert paths == ["api"]
        return [path]

    def emit(modules, *, available_modules):
        assert modules == [module]
        assert available_modules == [module]
        return stubs

    def serialize(received):
        assert received is module
        return {"name": "api"}

    monkeypatch.setattr(x2py_cli, "_parse_c_project", parse_project)
    monkeypatch.setattr(x2py_cli, "c_project_to_semantic_modules", convert)
    monkeypatch.setattr(x2py_cli, "expand_c_paths", expand)
    monkeypatch.setattr("semantics.pyi_printer.emit_module_stubs", emit)
    monkeypatch.setattr(x2py_cli, "asdict", serialize)

    assert x2py_cli._semantic_report(["api"], config, language="c") == {
        str(path): {
            "semantic_modules": [{"name": "api"}],
            "pyi": "def api() -> None: ...",
            "pyi_dependencies": {"shared": "class Shared:\n    pass"},
        }
    }


def test_x2py_semantic_report_preserves_fortran_conversion_and_stub_contracts(monkeypatch):
    path = Path("api.f90")
    config = object()
    wrapped_types = {("types_mod", "widget")}
    expected_compile_time_values = {"api.dp": 8}
    native_left = object()
    native_right = object()
    left = types.SimpleNamespace(name="left")
    right = types.SimpleNamespace(name="right")
    parsed = types.SimpleNamespace(modules=[native_left, native_right])
    stubs = {
        "left": "class Left:\n    pass",
        "right": "class Right:\n    pass",
        "shared": "class Shared:\n    pass",
    }

    class Parser:
        def visit_file(self, code, *, filename):
            assert code == "fortran source"
            assert filename == str(path)
            return parsed

    def expand(paths):
        assert paths == ["api"]
        return [path]

    def source(received_path, preprocessing):
        assert received_path == path
        assert preprocessing is config
        return "fortran source", None

    def wrapped(parsed_files):
        assert list(parsed_files) == [parsed]
        return wrapped_types

    def compile_values(received, preprocessing):
        assert received is parsed
        assert preprocessing is config
        return expected_compile_time_values

    def convert(module, *, compile_time_values: object, wrapped_derived_types):
        assert compile_time_values is expected_compile_time_values
        assert wrapped_derived_types is wrapped_types
        return {native_left: left, native_right: right}[module]

    def emit(modules, *, available_modules):
        assert modules == [left, right]
        assert available_modules == [left, right]
        return stubs

    def serialize(module):
        assert module is left or module is right
        return {"name": module.name}

    monkeypatch.setattr(x2py_cli, "FortranParser", Parser)
    monkeypatch.setattr(x2py_cli, "_expand_paths", expand)
    monkeypatch.setattr(x2py_cli, "_fortran_source_for_path", source)
    monkeypatch.setattr(x2py_cli, "_fortran_wrapped_derived_types", wrapped)
    monkeypatch.setattr(x2py_cli, "_fortran_compile_time_values", compile_values)
    monkeypatch.setattr("semantics.fortran2ir.fortran_module_to_semantic_module", convert)
    monkeypatch.setattr("semantics.pyi_printer.emit_module_stubs", emit)
    monkeypatch.setattr(x2py_cli, "asdict", serialize)

    assert x2py_cli._semantic_report(["api"], config) == {
        str(path): {
            "semantic_modules": [{"name": "left"}, {"name": "right"}],
            "pyi": "class Left:\n    pass\n\nclass Right:\n    pass",
            "pyi_dependencies": {"shared": "class Shared:\n    pass"},
        }
    }


def test_x2py_wrap_readiness_report_preserves_c_and_pyi_contracts(monkeypatch):
    path = Path("api.h")
    stub = Path("api.pyi")
    config = object()
    project = object()
    module = types.SimpleNamespace(name="api", origin=types.SimpleNamespace(native_name=str(path)))
    readiness = {"wrappable": True, "source": str(path)}
    pyi_report = {str(stub): {"source_kind": "pyi"}}

    def expand(paths):
        assert paths == ["api"]
        return [path, stub]

    def parse_project(paths, preprocessing):
        assert paths == [str(path)]
        assert preprocessing is config
        return project

    def convert(received):
        assert received is project
        return [module]

    def serialize(received):
        assert received is module
        return {"name": "api"}

    def assess(modules, *, source):
        assert modules == [module]
        assert source == str(path)
        return readiness

    def pyi(paths):
        assert paths == ["api"]
        return pyi_report

    monkeypatch.setattr(x2py_cli, "expand_c_paths", expand)
    monkeypatch.setattr(x2py_cli, "_parse_c_project", parse_project)
    monkeypatch.setattr(x2py_cli, "c_project_to_semantic_modules", convert)
    monkeypatch.setattr(x2py_cli, "asdict", serialize)
    monkeypatch.setattr(x2py_cli, "assess_semantic_wrap_readiness", assess)
    monkeypatch.setattr(x2py_cli, "_pyi_readiness_report", pyi)

    assert x2py_cli._wrap_readiness_report(["api"], config, language="c") == {
        str(path): {
            "source_kind": "c",
            "semantic_modules": [{"name": "api"}],
            "wrap_readiness": readiness,
        },
        **pyi_report,
    }


def test_x2py_wrap_readiness_report_preserves_fortran_and_pyi_contracts(monkeypatch):
    path = Path("api.f90")
    stub = Path("api.pyi")
    config = object()
    parsed = object()
    wrapped_types = {("types_mod", "widget")}
    compile_time_values = {"api.dp": 8}
    module = types.SimpleNamespace(name="api")
    readiness = {"wrappable": True, "source": str(path)}
    pyi_report = {str(stub): {"source_kind": "pyi"}}

    class Parser:
        def visit_file(self, code, *, filename):
            assert code == "fortran source"
            assert filename == str(path)
            return parsed

    def expand(paths):
        assert paths == ["api"]
        return [path, stub]

    def source(received_path, preprocessing):
        assert received_path == path
        assert preprocessing is config
        return "fortran source", None

    def wrapped(parsed_files):
        assert list(parsed_files) == [parsed]
        return wrapped_types

    def compile_values(received, preprocessing):
        assert received is parsed
        assert preprocessing is config
        return compile_time_values

    def convert(received, *, standalone_module_name, compile_time_values: object, wrapped_derived_types):
        assert received is parsed
        assert standalone_module_name == "api"
        assert compile_time_values is expected_compile_time_values
        assert wrapped_derived_types is wrapped_types
        return [module]

    def serialize(received):
        assert received is module
        return {"name": "api"}

    def assess(modules, *, source):
        assert modules == [module]
        assert source == str(path)
        return readiness

    def pyi(paths):
        assert paths == ["api"]
        return pyi_report

    expected_compile_time_values = compile_time_values
    monkeypatch.setattr(x2py_cli, "FortranParser", Parser)
    monkeypatch.setattr(x2py_cli, "_expand_readiness_paths", expand)
    monkeypatch.setattr(x2py_cli, "_fortran_source_for_path", source)
    monkeypatch.setattr(x2py_cli, "_fortran_wrapped_derived_types", wrapped)
    monkeypatch.setattr(x2py_cli, "_fortran_compile_time_values", compile_values)
    monkeypatch.setattr(x2py_cli, "fortran_file_to_semantic_modules", convert)
    monkeypatch.setattr(x2py_cli, "asdict", serialize)
    monkeypatch.setattr(x2py_cli, "assess_semantic_wrap_readiness", assess)
    monkeypatch.setattr(x2py_cli, "_pyi_readiness_report", pyi)

    assert x2py_cli._wrap_readiness_report(["api"], config) == {
        str(path): {
            "source_kind": "fortran",
            "semantic_modules": [{"name": "api"}],
            "wrap_readiness": readiness,
        },
        **pyi_report,
    }


def test_x2py_parse_c_path_preserves_parser_and_preprocessing_arguments(tmp_path: Path, monkeypatch):
    path = tmp_path / "api.h"
    raw_parsed = object()
    compiled_parsed = object()

    class RawParser:
        def visit_file(self, source, *, filename, include_dirs, preprocessing):
            assert source == path
            assert filename == str(path)
            assert include_dirs == ["include"]
            assert preprocessing == "raw"
            return raw_parsed

    raw_config = x2py_cli.PreprocessingConfig(include_dirs=["include"])
    assert x2py_cli._parse_c_path(RawParser(), path, raw_config) is raw_parsed

    class Recipe:
        def to_dict(self):
            return {"mode": "compiler"}

    def preprocess(received_path, *, language, config):
        assert received_path == path
        assert language == "c"
        assert config is compiler_config
        return "int add(int x);\n", Recipe()

    class CompilerParser:
        def visit_file(self, source, *, filename, include_dirs, preprocessing):
            assert source == "int add(int x);\n"
            assert filename == str(path)
            assert include_dirs == ["include"]
            assert preprocessing == "compiler"
            return compiled_parsed

    def attach_recipe(parsed, recipe):
        assert parsed is compiled_parsed
        assert recipe == {"mode": "compiler"}

    compiler_config = x2py_cli.PreprocessingConfig(mode="compiler", compiler="cc", include_dirs=["include"])
    monkeypatch.setattr(x2py_cli, "run_compiler_preprocessor_with_recipe", preprocess)
    monkeypatch.setattr(x2py_cli, "attach_preprocessing_recipe", attach_recipe)

    assert x2py_cli._parse_c_path(CompilerParser(), path, compiler_config) is compiled_parsed


def test_x2py_readiness_path_helpers_include_fortran_and_pyi(tmp_path: Path):
    source = tmp_path / "mini.f90"
    stub = tmp_path / "api.pyi"
    ignored = tmp_path / "notes.txt"
    source.write_text("module mini\nend module mini\n", encoding="utf-8")
    stub.write_text("def work() -> None: ...\n", encoding="utf-8")
    ignored.write_text("ignore", encoding="utf-8")

    assert set(x2py_cli._collect_readiness_extensions(tmp_path)) == {source, stub}
    assert set(x2py_cli._expand_readiness_paths([str(tmp_path), str(source), str(ignored)])) == {
        source,
        stub,
        ignored,
    }


def test_x2py_pyi_readiness_report_preserves_loading_and_assessment_contracts(tmp_path: Path, monkeypatch):
    package = tmp_path / "package"
    package.mkdir()
    stub = tmp_path / "api.pyi"
    ignored = tmp_path / "notes.txt"
    module = object()
    readiness = {"wrappable": True, "source": str(stub)}
    calls = []

    def expand(paths):
        assert paths == [str(package), str(stub), str(ignored)]
        calls.append(("expand", paths))
        return [stub]

    def load(paths):
        assert paths == [str(package), str(stub)]
        calls.append(("load", paths))
        return [module]

    def serialize(received):
        assert received is module
        calls.append(("asdict", received))
        return {"name": "api"}

    def assess(modules, *, source):
        assert modules == [module]
        assert source == str(stub)
        calls.append(("assess", modules, source))
        return readiness

    monkeypatch.setattr(x2py_cli, "_expand_pyi_paths", expand)
    monkeypatch.setattr(x2py_cli, "load_pyi_modules", load)
    monkeypatch.setattr(x2py_cli, "asdict", serialize)
    monkeypatch.setattr(x2py_cli, "assess_semantic_wrap_readiness", assess)

    assert x2py_cli._pyi_readiness_report([str(package), str(stub), str(ignored)]) == {
        str(stub): {
            "source_kind": "pyi",
            "semantic_modules": [{"name": "api"}],
            "wrap_readiness": readiness,
        }
    }
    assert calls == [
        ("expand", [str(package), str(stub), str(ignored)]),
        ("load", [str(package), str(stub)]),
        ("asdict", module),
        ("assess", [module], str(stub)),
    ]

    calls.clear()
    monkeypatch.setattr(x2py_cli, "_expand_pyi_paths", lambda _paths: [])
    assert x2py_cli._pyi_readiness_report([str(ignored)]) == {}
    assert calls == []


def test_x2py_format_semantic_readiness_reports_wrappable_and_blocked_sources():
    report = {
        "api.f90": {
            "source_kind": "fortran",
            "semantic_modules": [{"name": "api_mod"}],
            "wrap_readiness": {
                "wrappable": False,
                "n_functions": 1,
                "n_classes": 0,
                "n_variables": 2,
                "wrappability_blockers": [
                    {
                        "code": "unresolved_semantic_types",
                        "message": "unresolved external type",
                        "items": [{"owner": "api_mod.solve", "type": "external_t"}],
                    },
                    {
                        "code": "callback_signature_incomplete",
                        "message": "callback metadata incomplete",
                        "items": [{"owner": "api_mod.apply", "needs": ["arguments"]}],
                    },
                ],
            },
        },
        "interface.pyi": {
            "source_kind": "pyi",
            "semantic_modules": [],
            "wrap_readiness": {
                "wrappable": True,
                "n_functions": 0,
                "n_classes": 1,
                "n_variables": 0,
                "wrappability_blockers": [],
            },
        },
        "partial.f90": {
            "semantic_modules": [{}],
        },
    }

    text = x2py_cli._format_semantic_readiness(report)
    assert (
        text
        == """File: api.f90
  Source: fortran
  Semantic modules: api_mod
  Wrappable: no
  Public functions: 1
  Public classes: 0
  Public variables: 2
  Why not wrappable:
    - unresolved_semantic_types: unresolved external type
      * api_mod.solve uses unresolved type external_t
    - callback_signature_incomplete: callback metadata incomplete
      * api_mod.apply needs Callable[[...], ...] metadata (arguments)

File: interface.pyi
  Source: pyi
  Semantic modules: <none>
  Wrappable: yes
  Public functions: 0
  Public classes: 1
  Public variables: 0
  No semantic readiness blockers detected.

File: partial.f90
  Source: <unknown>
  Semantic modules: <unknown>
  Wrappable: no
  Public functions: 0
  Public classes: 0
  Public variables: 0
  No semantic readiness blockers detected."""
    )

    assert "File: api.f90" in text
    assert "  Source: fortran" in text
    assert "  Semantic modules: api_mod" in text
    assert "  Wrappable: no" in text
    assert "  Public functions: 1" in text
    assert "  Public classes: 0" in text
    assert "  Public variables: 2" in text
    assert "  Why not wrappable:" in text
    assert "    - unresolved_semantic_types: unresolved external type" in text
    assert "      * api_mod.solve uses unresolved type external_t" in text
    assert "      * api_mod.apply needs Callable[[...], ...] metadata (arguments)" in text
    assert "File: interface.pyi" in text
    assert "  Source: pyi" in text
    assert "  Semantic modules: <none>" in text
    assert "  Wrappable: yes" in text
    assert "  No semantic readiness blockers detected." in text
    assert "File: partial.f90" in text
    assert "  Source: <unknown>" in text
    assert "  Semantic modules: <unknown>" in text


def test_x2py_format_semantic_readiness_defaults_and_multiple_modules():
    report = {
        "missing.f90": {
            "wrap_readiness": {
                "wrappable": False,
                "wrappability_blockers": [
                    {
                        "message": "missing code",
                        "items": [{"value": 2}],
                    }
                ],
            },
        },
        "multi.f90": {
            "source_kind": "fortran",
            "semantic_modules": [{"name": "left"}, {"name": "right"}],
            "wrap_readiness": {
                "wrappable": True,
                "n_functions": 2,
                "n_classes": 1,
                "n_variables": 3,
                "wrappability_blockers": [],
            },
        },
    }

    assert (
        x2py_cli._format_semantic_readiness(report)
        == """File: missing.f90
  Source: <unknown>
  Semantic modules: <none>
  Wrappable: no
  Public functions: 0
  Public classes: 0
  Public variables: 0
  Why not wrappable:
    - None: missing code
      * {'value': 2}

File: multi.f90
  Source: fortran
  Semantic modules: left, right
  Wrappable: yes
  Public functions: 2
  Public classes: 1
  Public variables: 3
  No semantic readiness blockers detected."""
    )


@pytest.mark.parametrize("macro_flag", ["-D", "-U"])
def test_x2py_main_rejects_invalid_macro_names(macro_flag: str, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["x2py", str(TEST_FILE), "--parse", macro_flag, "=invalid"])
    with pytest.raises(SystemExit):
        x2py_cli.main()


def test_x2py_main_formats_value_errors_or_reraises_for_debug(tmp_path: Path, monkeypatch, capsys):
    source = tmp_path / "input.f90"
    source.write_text("module input\nend module input\n", encoding="utf-8")

    def fail_parse(_paths, _preprocessing):
        raise ValueError("invalid generated interface")

    monkeypatch.setattr(x2py_cli, "_parse_report", fail_parse)
    monkeypatch.setattr(sys, "argv", ["x2py", str(source), "--parse"])
    assert x2py_cli.main() == 1
    assert "x2py: error: invalid generated interface" in capsys.readouterr().err

    monkeypatch.setattr(sys, "argv", ["x2py", str(source), "--parse", "--debug"])
    with pytest.raises(ValueError, match="invalid generated interface"):
        x2py_cli.main()
