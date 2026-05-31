# -*- coding: utf-8 -*-
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

    assert payload[str(physics)]["pyi_dependencies"] == {
        "types_mod": "class particle(Opaque):\n    pass"
    }
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
            "pyi_dependencies": {"shared": "class shared(Opaque):\n    pass"},
        },
    }

    text = x2py_cli._format_pyi_report(report)

    assert text.count("Dependency stub: shared.pyi") == 1
    assert "def first() -> None: ..." in text
    with pytest.raises(ValueError, match="Conflicting generated dependency stub"):
        x2py_cli._write_pyi_dependencies(
            {
                "first.f90": {"pyi_dependencies": {"shared": "class shared:\n    pass"}},
                "second.f90": {"pyi_dependencies": {"shared": "class shared:\n    value: int"}},
            }
        )


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


def test_x2py_cli_helpers_cover_language_and_preprocessing_edges(tmp_path: Path, monkeypatch):
    class ErrorParser:
        def error(self, message):
            raise ValueError(message)

    def args(**overrides):
        values = {
            "defines": [],
            "undefs": [],
            "preprocess": "raw",
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
    (tmp_path / "notes.txt").write_text("ignore", encoding="utf-8")

    assert x2py_cli._expand_pyi_paths([str(tmp_path), str(stub)]) == [stub]
    assert x2py_cli._resolve_language([str(api_h)], "c", parser) == "c"
    with pytest.raises(ValueError, match="incompatible with --language fortran"):
        x2py_cli._resolve_language([str(api_h)], "fortran", parser)
    with pytest.raises(ValueError, match="requires explicit --language c"):
        x2py_cli._resolve_language([str(api_h)], None, parser)
    with pytest.raises(ValueError, match="Cannot determine"):
        x2py_cli._resolve_language([str(tmp_path / "notes.txt")], None, parser)

    with pytest.raises(ValueError, match="--compiler requires --preprocess compiler"):
        x2py_cli._build_preprocessing_config(args(compiler="gfortran"), parser)
    with pytest.raises(ValueError, match="--preprocess-template requires"):
        x2py_cli._build_preprocessing_config(
            args(
                preprocess="compiler",
                compiler="cc",
                preprocess_template="{compiler} -E {source}",
            ),
            parser,
        )
    with pytest.raises(ValueError, match="requires --compiler"):
        x2py_cli._build_preprocessing_config(args(preprocess="compiler"), parser)
    with pytest.raises(ValueError, match="--compile-commands requires"):
        x2py_cli._build_preprocessing_config(args(compile_commands="compile_commands.json"), parser)
    with pytest.raises(ValueError, match="raw C mode records source macros"):
        x2py_cli._build_preprocessing_config(args(language="c", defines=["USE_FAST"]), parser)
    with pytest.raises(ValueError, match="internal Fortran parsing does not evaluate CPP branches"):
        x2py_cli._build_preprocessing_config(args(defines=["USE_FAST"]), parser)
    with pytest.raises(ValueError, match="-I/--include-dir affects Fortran only"):
        x2py_cli._build_preprocessing_config(args(include_dirs=["include"]), parser)

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
    assert fortran_parser_cli._format_var_type({"base_type": "derived", "kind": "particle", "rank": 0}) == "type(particle)[0]"
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

    monkeypatch.setenv("X2PY_TEST_FLAG", "ON")
    assert x2py_cli._env_flag("X2PY_TEST_FLAG") is True
    monkeypatch.delenv("X2PY_TEST_FLAG")
    assert x2py_cli._env_flag("X2PY_TEST_FLAG") is False

    assert x2py_cli._diagnostic_color_enabled(disabled=True) is False
    monkeypatch.setenv("NO_COLOR", "1")
    assert x2py_cli._diagnostic_color_enabled(disabled=False) is False
    monkeypatch.delenv("NO_COLOR")

    assert x2py_cli._to_dict_no_parent(Node("child", parent=Node("root"))) == {"name": "child"}

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
            calls.append((syntax.code, syntax.lexer, self.options))

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
    assert calls == [("def f() -> None: ...", "python", {"force_terminal": True, "color_system": "auto"})]
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
            "callback_signature_incomplete",
            {"owner": "handler", "needs": ["arguments", "return type"]},
        )
        == "handler needs Callable[[...], ...] metadata (arguments, return type)"
    )
    assert x2py_cli._format_semantic_blocker_item("c_unknown_type", {"owner": "api", "type": "widget"}) == "api: widget"
    assert x2py_cli._format_semantic_blocker_item("c_parser_status", {"owner": "api"}) == "{'owner': 'api'}"

    semantic_payload = {"source": {"semantic_modules": []}}
    x2py_cli._attach_wrap_readiness(semantic_payload, {"other": {"wrap_readiness": {"wrappable": True}}})
    assert "wrap_readiness" not in semantic_payload["source"]

    parsed = x2py_cli.FortranParser().visit_file("module empty\nend module empty\n", filename="empty.f90")
    config = x2py_cli.PreprocessingConfig(mode="compiler", compiler="gfortran")
    assert x2py_cli._fortran_compile_time_values(parsed, config) is None


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
