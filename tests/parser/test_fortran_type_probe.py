# -*- coding: utf-8 -*-
"""Compiler-derived Fortran kind expression probe tests."""

import json
import shutil
import subprocess
import sys

import pytest

from semantics.fortran2ir import (
    collect_semantic_compile_time_requirements,
    fortran_module_to_semantic_module,
)
from x2py import parse_fortran_file as parse_fortran_source
from x2py.fortran_type_probe import (
    FortranTypeProbeError,
    build_fortran_type_probe_source,
    evaluate_fortran_type_requirements,
    fortran_type_probe_expressions,
    probe_fortran_type_expressions,
)
from x2py.preprocessing import PreprocessingConfig


_FC = shutil.which("gfortran") or shutil.which("f95")


def test_fortran_type_probe_source_evaluates_integer_initialization_expressions():
    source = build_fortran_type_probe_source(
        ["selected_real_kind(12)", "real64", "c_double"]
    )

    assert "use, intrinsic :: iso_fortran_env, only: real64" in source
    assert "use, intrinsic :: iso_c_binding, only: c_double" in source
    assert "integer, parameter :: x2py_value_0 = selected_real_kind(12)" in source
    assert "integer, parameter :: x2py_value_1 = real64" in source
    assert "integer, parameter :: x2py_value_2 = c_double" in source
    assert '{"values":[' in source


def test_fortran_type_probe_rejects_statement_injection():
    with pytest.raises(FortranTypeProbeError, match="single initialization expression"):
        build_fortran_type_probe_source(["selected_real_kind(12); stop"])


def test_fortran_type_probe_requires_an_explicit_compiler():
    with pytest.raises(FortranTypeProbeError, match="exact compiler"):
        probe_fortran_type_expressions(
            PreprocessingConfig(mode="compiler"),
            ["selected_real_kind(12)"],
        )


def test_fortran_type_probe_expressions_extracts_semantic_requirement_inputs():
    requirements = [
        {"code": "parameter_value", "symbol": "rk", "expression": "selected_real_kind(12)"},
        {"code": "unsupported_kind", "symbol": "x", "expression": "selected_real_kind(12)"},
        {"code": "parameter_value", "symbol": "ik", "expression": "selected_int_kind(9)"},
    ]

    assert fortran_type_probe_expressions(requirements) == [
        "selected_real_kind(12)",
        "selected_int_kind(9)",
    ]


@pytest.mark.skipif(_FC is None, reason="requires an available native Fortran compiler")
def test_fortran_type_probe_reports_values_from_native_compiler():
    report = probe_fortran_type_expressions(
        PreprocessingConfig(mode="compiler", compiler=_FC),
        ["selected_int_kind(9)", "selected_real_kind(12)", "kind(1.0d0)"],
    )

    assert report.values["selected_int_kind(9)"] > 0
    assert report.values["selected_real_kind(12)"] > 0
    assert report.values["kind(1.0d0)"] > 0
    assert report.recipe.compiler == _FC
    assert "-cpp" in report.recipe.compile_argv
    assert "selected_real_kind(12)" in report.source_text


@pytest.mark.skipif(_FC is None, reason="requires an available native Fortran compiler")
def test_fortran_type_probe_carries_target_relevant_user_flags(tmp_path):
    include_dir = tmp_path / "include"
    include_dir.mkdir()

    report = probe_fortran_type_expressions(
        PreprocessingConfig(
            mode="compiler",
            compiler=_FC,
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


@pytest.mark.skipif(_FC is None, reason="requires an available native Fortran compiler")
def test_fortran_type_probe_evaluates_collected_semantic_requirements():
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
        PreprocessingConfig(mode="compiler", compiler=_FC),
        requirements,
    )
    module = fortran_module_to_semantic_module(parsed, compile_time_values=values)

    assert values["rk"] == values["selected_real_kind(12)"]
    assert module.functions[0].arguments[0].semantic_type.name == "Float64"


@pytest.mark.skipif(_FC is None, reason="requires an available native Fortran compiler")
def test_fortran_type_probe_module_cli_emits_json_for_semantic_input():
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py.fortran_type_probe",
            "--compiler",
            _FC,
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
    assert payload["recipe"]["compiler"] == _FC
    assert payload["source_text"].startswith("program x2py_fortran_type_probe")


@pytest.mark.skipif(_FC is None, reason="requires an available native Fortran compiler")
def test_x2py_semantics_cli_evaluates_collected_fortran_type_requirements(tmp_path):
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
            _FC,
            "--json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(completed.stdout)
    semantic_type = payload[str(source)]["semantic_modules"][0]["functions"][0]["arguments"][0][
        "semantic_type"
    ]
    assert semantic_type["name"] == "Float64"
