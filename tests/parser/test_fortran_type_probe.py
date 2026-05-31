# -*- coding: utf-8 -*-
"""Compiler-derived Fortran kind expression probe tests."""

import json
import shutil
import subprocess
import sys
from types import SimpleNamespace

import pytest

import x2py.fortran_type_probe as fortran_type_probe
from semantics.fortran2ir import (
    collect_semantic_compile_time_requirements,
    fortran_module_to_semantic_module,
)
from x2py import parse_fortran_file as parse_fortran_source
from x2py.fortran_type_probe import (
    FortranTypeProbeRecipe,
    FortranTypeProbeReport,
    FortranTypeProbeError,
    _value_for_expression,
    build_fortran_type_probe_source,
    evaluate_fortran_type_requirements,
    fortran_type_probe_expressions,
    probe_fortran_type_expressions,
)
from x2py.preprocessing import PreprocessingConfig


_FC = shutil.which("gfortran") or shutil.which("f95")


def _required_fortran_compiler() -> str:
    assert _FC is not None, "the full Fortran pipeline test suite requires an available native Fortran compiler"
    return _FC


def test_fortran_type_probe_source_evaluates_integer_initialization_expressions():
    source = build_fortran_type_probe_source(["selected_real_kind(12)", "real64", "c_double"])

    assert "use, intrinsic :: iso_fortran_env, only: real64" in source
    assert "use, intrinsic :: iso_c_binding, only: c_double" in source
    assert "integer, parameter :: x2py_value_0 = selected_real_kind(12)" in source
    assert "integer, parameter :: x2py_value_1 = real64" in source
    assert "integer, parameter :: x2py_value_2 = c_double" in source
    assert '{"values":[' in source

    normalized = build_fortran_type_probe_source(["", "real64", "REAL64"])
    assert "integer, parameter :: x2py_value_0 = real64" in normalized
    assert "x2py_value_1" not in normalized


def test_x2py_public_api_lazily_exposes_type_probe_symbols_and_rejects_unknown_names():
    import x2py

    assert x2py.FortranTypeProbeError is FortranTypeProbeError
    assert x2py.FortranTypeProbeReport is FortranTypeProbeReport
    with pytest.raises(AttributeError, match="not_exported"):
        x2py.not_exported


def test_fortran_type_probe_rejects_statement_injection():
    with pytest.raises(FortranTypeProbeError, match="single initialization expression"):
        build_fortran_type_probe_source(["selected_real_kind(12); stop"])


def test_fortran_type_probe_requires_an_explicit_compiler():
    with pytest.raises(FortranTypeProbeError, match="exact compiler"):
        probe_fortran_type_expressions(
            PreprocessingConfig(mode="compiler"),
            ["selected_real_kind(12)"],
        )


def test_fortran_type_probe_rejects_compile_database_and_validates_expression_forms():
    with pytest.raises(FortranTypeProbeError, match="does not consume compile_commands"):
        probe_fortran_type_expressions(
            PreprocessingConfig(mode="compiler", compiler="gfortran", compile_commands="compile_commands.json"),
            ["selected_real_kind(12)"],
        )
    with pytest.raises(FortranTypeProbeError, match="unsupported characters"):
        build_fortran_type_probe_source(["selected_real_kind(12)!"])


def test_fortran_type_probe_expressions_extracts_semantic_requirement_inputs():
    requirements = [
        {"code": "parameter_value", "symbol": "blank", "expression": " "},
        {"code": "parameter_value", "symbol": "rk", "expression": "selected_real_kind(12)"},
        {"code": "unsupported_kind", "symbol": "x", "expression": "selected_real_kind(12)"},
        {"code": "parameter_value", "symbol": "ik", "expression": "selected_int_kind(9)"},
    ]

    assert fortran_type_probe_expressions(requirements) == [
        "selected_real_kind(12)",
        "selected_int_kind(9)",
    ]


def test_fortran_type_probe_report_resolves_only_matching_parameter_requirements():
    report = FortranTypeProbeReport(
        values={"Selected_Real_Kind(12)": 8},
        recipe=FortranTypeProbeRecipe(
            compiler="gfortran",
            compile_argv=[],
            run_argv=[],
            expressions=["Selected_Real_Kind(12)"],
        ),
        source_text="",
    )
    requirements = [
        {"code": "parameter_value", "symbol": "rk", "expression": "selected_real_kind(12)"},
        {"code": "unsupported_kind", "symbol": "not_added", "expression": "selected_real_kind(12)"},
        {"code": "parameter_value", "symbol": "", "expression": "selected_real_kind(12)"},
        {"code": "parameter_value", "symbol": "missing", "expression": "missing_expr"},
    ]

    assert report.to_compile_time_values() == {"Selected_Real_Kind(12)": 8}
    assert report.to_compile_time_values(requirements)["rk"] == 8
    assert "not_added" not in report.to_compile_time_values(requirements)
    assert _value_for_expression({}, "not_present") is None
    assert evaluate_fortran_type_requirements(PreprocessingConfig(mode="compiler"), []) == {}


@pytest.mark.parametrize(
    ("results", "message"),
    [
        ([OSError("missing")], "failed to run Fortran type probe compiler"),
        ([SimpleNamespace(returncode=1, stderr="compile failed")], "compilation failed"),
        ([SimpleNamespace(returncode=0, stderr=""), OSError("cannot execute")], "failed to execute"),
        (
            [SimpleNamespace(returncode=0, stderr=""), SimpleNamespace(returncode=2, stderr="run failed")],
            "execution failed",
        ),
        (
            [SimpleNamespace(returncode=0, stderr=""), SimpleNamespace(returncode=0, stdout="not json", stderr="")],
            "invalid JSON",
        ),
        (
            [SimpleNamespace(returncode=0, stderr=""), SimpleNamespace(returncode=0, stdout="{}", stderr="")],
            "missing 'values'",
        ),
        (
            [
                SimpleNamespace(returncode=0, stderr=""),
                SimpleNamespace(returncode=0, stdout='{"values":[]}', stderr=""),
            ],
            "count does not match",
        ),
        (
            [
                SimpleNamespace(returncode=0, stderr=""),
                SimpleNamespace(returncode=0, stdout='{"values":["bad"]}', stderr=""),
            ],
            "is not an integer",
        ),
    ],
)
def test_fortran_type_probe_reports_compiler_and_runner_failures(monkeypatch, results, message):
    responses = iter(results)

    def run(*_args, **_kwargs):
        result = next(responses)
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(fortran_type_probe.subprocess, "run", run)
    with pytest.raises(FortranTypeProbeError, match=message):
        probe_fortran_type_expressions(
            PreprocessingConfig(mode="compiler", compiler="gfortran"),
            ["selected_real_kind(12)"],
            runner=["runner"],
        )


def test_fortran_type_probe_accepts_runner_and_cli_validates_macro_names(monkeypatch):
    responses = iter(
        [
            SimpleNamespace(returncode=0, stderr=""),
            SimpleNamespace(returncode=0, stdout='{"values":[8]}', stderr=""),
        ]
    )
    monkeypatch.setattr(fortran_type_probe.subprocess, "run", lambda *_args, **_kwargs: next(responses))
    report = probe_fortran_type_expressions(
        PreprocessingConfig(mode="compiler", compiler="gfortran"),
        ["selected_real_kind(12)"],
        runner=["emulator"],
    )
    assert report.recipe.run_argv[0] == "emulator"

    with pytest.raises(SystemExit):
        fortran_type_probe.main(["--compiler", "gfortran", "-D", "=bad"])
    with pytest.raises(SystemExit):
        fortran_type_probe.main(["--compiler", "gfortran", "-U", "=bad"])


def test_fortran_type_probe_reports_values_from_native_compiler():
    compiler = _required_fortran_compiler()
    report = probe_fortran_type_expressions(
        PreprocessingConfig(mode="compiler", compiler=compiler),
        ["selected_int_kind(9)", "selected_real_kind(12)", "kind(1.0d0)"],
    )

    assert report.values["selected_int_kind(9)"] > 0
    assert report.values["selected_real_kind(12)"] > 0
    assert report.values["kind(1.0d0)"] > 0
    assert report.recipe.compiler == compiler
    assert "-cpp" in report.recipe.compile_argv
    assert "selected_real_kind(12)" in report.source_text


def test_fortran_type_probe_carries_target_relevant_user_flags(tmp_path):
    compiler = _required_fortran_compiler()
    include_dir = tmp_path / "include"
    include_dir.mkdir()

    report = probe_fortran_type_expressions(
        PreprocessingConfig(
            mode="compiler",
            compiler=compiler,
            include_dirs=[str(include_dir)],
            defines=["X2PY_FEATURE=1"],
            undefs=["X2PY_OLD_FEATURE"],
            std="f2008",
            compiler_args=["-fno-range-check"],
        ),
        ["selected_real_kind(12)"],
    )

    argv = report.recipe.compile_argv
    assert "-cpp" in argv
    assert f"-I{include_dir}" in argv
    assert "-DX2PY_FEATURE=1" in argv
    assert "-UX2PY_OLD_FEATURE" in argv
    assert "-std=f2008" in argv
    assert "-fno-range-check" in argv
    assert report.recipe.requested_standard == "f2008"
    assert report.recipe.include_dirs == [str(include_dir)]
    assert report.recipe.defines == ["X2PY_FEATURE=1"]
    assert report.recipe.undefs == ["X2PY_OLD_FEATURE"]
    assert report.recipe.compiler_args == ["-fno-range-check"]


def test_fortran_type_probe_evaluates_collected_semantic_requirements():
    compiler = _required_fortran_compiler()
    parsed = parse_fortran_source(
        """
module solver_mod
  integer, parameter :: rk = selected_real_kind(12)
contains
subroutine scale(x)
  real(kind=rk), intent(inout) :: x
end subroutine scale
end module solver_mod
"""
    )
    requirements = collect_semantic_compile_time_requirements(parsed)

    values = evaluate_fortran_type_requirements(
        PreprocessingConfig(mode="compiler", compiler=compiler),
        requirements,
    )
    module = fortran_module_to_semantic_module(parsed, compile_time_values=values)

    assert values["rk"] == values["selected_real_kind(12)"]
    assert module.functions[0].arguments[0].semantic_type.name == "Float64"


def test_fortran_type_probe_module_cli_emits_json_for_semantic_input():
    compiler = _required_fortran_compiler()
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py.fortran_type_probe",
            "--compiler",
            compiler,
            "--expr",
            "selected_int_kind(9)",
            "--expr",
            "selected_real_kind(12)",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["values"]["selected_int_kind(9)"] > 0
    assert payload["values"]["selected_real_kind(12)"] > 0
    assert payload["recipe"]["compiler"] == compiler
    assert payload["source_text"].startswith("program x2py_fortran_type_probe")


def test_x2py_semantics_cli_evaluates_collected_fortran_type_requirements(tmp_path):
    compiler = _required_fortran_compiler()
    source = tmp_path / "solver.f90"
    source.write_text(
        """
module solver_mod
  integer, parameter :: rk = selected_real_kind(12)
contains
subroutine scale(x)
  real(kind=rk), intent(inout) :: x
end subroutine scale
end module solver_mod
""",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(source),
            "--semantics",
            "--preprocess",
            "compiler",
            "--compiler",
            compiler,
            "--json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(completed.stdout)
    semantic_type = payload[str(source)]["semantic_modules"][0]["functions"][0]["arguments"][0]["semantic_type"]
    assert semantic_type["name"] == "Float64"
