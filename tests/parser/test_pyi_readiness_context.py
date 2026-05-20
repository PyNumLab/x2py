# -*- coding: utf-8 -*-
"""User-provided .pyi facts can clear wrap-readiness blockers."""

import json
import subprocess
import sys
from pathlib import Path

from x2py import assess_wrap_readiness


def _write(path: Path, text: str) -> Path:
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return path


def test_pyi_context_resolves_imported_derived_type_argument(tmp_path: Path):
    source = """
module solver_mod
  use state_mod, only: sim_state
contains
  subroutine step(state)
    type(sim_state), intent(inout) :: state
  end subroutine step
end module solver_mod
"""
    context = _write(
        tmp_path / "state_mod.pyi",
        """
class sim_state:
    n: Int32
    values: Float64[Shape('n'), ORDER_F]
""",
    )

    before = assess_wrap_readiness(source, filename="solver.f90")
    after = assess_wrap_readiness(source, filename="solver.f90", pyi_files=[context])

    assert before["wrappable"] is False
    assert before["wrappability_blockers"][0]["code"] == "unresolved_derived_type_arguments"
    assert after["wrappable"] is True
    assert after["unresolved_derived_type_arguments"] == []
    assert after["pyi_context"]["provided_types"] == ["sim_state"]


def test_pyi_context_resolves_imported_derived_type_result(tmp_path: Path):
    source = """
function current_state() result(state)
  use state_mod, only: sim_state
  type(sim_state) :: state
end function current_state
"""
    context = _write(
        tmp_path / "state_mod.pyi",
        """
class sim_state:
    id: Int32
""",
    )

    before = assess_wrap_readiness(source, filename="current_state.f90")
    after = assess_wrap_readiness(source, filename="current_state.f90", pyi_files=[context])

    assert before["unresolved_derived_type_arguments"][0]["argument"] == "state"
    assert after["wrappable"] is True
    assert after["unresolved_derived_type_arguments"] == []


def test_pyi_context_resolves_missing_derived_type_field(tmp_path: Path):
    source = """
module mesh_mod
  use point_mod, only: point

  type :: mesh
    type(point) :: origin
  end type mesh
contains
  subroutine move(m)
    type(mesh), intent(inout) :: m
  end subroutine move
end module mesh_mod
"""
    context = _write(
        tmp_path / "point_mod.pyi",
        """
class point:
    x: Float64
    y: Float64
""",
    )

    before = assess_wrap_readiness(source, filename="mesh.f90")
    after = assess_wrap_readiness(source, filename="mesh.f90", pyi_files=[context])

    assert before["wrappability_blockers"][0]["code"] == "unresolved_derived_type_fields"
    assert after["wrappable"] is True
    assert after["unresolved_derived_type_fields"] == []


def test_pyi_context_final_constant_resolves_imported_kind_argument(tmp_path: Path):
    source = """
subroutine scale(x)
  use kinds_mod, only: rk
  real(kind=rk), intent(inout) :: x
end subroutine scale
"""
    context = _write(
        tmp_path / "kinds_mod.pyi",
        """
from typing import Final

rk: Final[Int32] = 8
""",
    )

    before = assess_wrap_readiness(source, filename="scale.f90")
    after = assess_wrap_readiness(source, filename="scale.f90", pyi_files=[context])

    assert before["unresolved_kind_arguments"][0]["kind"] == "rk"
    assert after["wrappable"] is True
    assert after["unresolved_kind_arguments"] == []
    assert after["pyi_context"]["provided_constants"] == {"rk": "8"}


def test_pyi_context_final_constant_resolves_imported_kind_field(tmp_path: Path):
    source = """
module state_mod
  use kinds_mod, only: rk

  type :: sim_state
    real(kind=rk) :: energy
  end type sim_state
contains
  subroutine update(state)
    type(sim_state), intent(inout) :: state
  end subroutine update
end module state_mod
"""
    context = _write(
        tmp_path / "kinds_mod.pyi",
        """
from typing import Final

rk: Final[Int32] = 8
""",
    )

    before = assess_wrap_readiness(source, filename="state.f90")
    after = assess_wrap_readiness(source, filename="state.f90", pyi_files=[context])

    assert before["wrappability_blockers"][0]["code"] == "unresolved_kind_fields"
    assert after["wrappable"] is True
    assert after["unresolved_kind_fields"] == []


def test_pyi_context_requires_literal_final_value_for_kind_resolution(tmp_path: Path):
    source = """
subroutine scale(x)
  use kinds_mod, only: rk
  real(kind=rk), intent(inout) :: x
end subroutine scale
"""
    context = _write(
        tmp_path / "kinds_mod.pyi",
        """
from typing import Final

rk: Final[Int32]
""",
    )

    report = assess_wrap_readiness(source, filename="scale.f90", pyi_files=[context])

    assert report["wrappable"] is False
    assert report["unresolved_kind_arguments"][0]["kind"] == "rk"
    assert report["pyi_context"]["provided_constants"] == {}


def test_pyi_context_callable_signature_resolves_callback_and_imported_type(tmp_path: Path):
    source = """
module solver_mod
  use state_mod, only: sim_state
  use callback_mod, only: objective_fn
contains
  subroutine step(state, t, objective, score)
    type(sim_state), intent(inout) :: state
    real(8), intent(in) :: t
    procedure(objective_fn) :: objective
    real(8), intent(out) :: score
  end subroutine step
end module solver_mod
"""
    context = _write(
        tmp_path / "solver_context.pyi",
        """
from typing import Callable

class sim_state:
    n: Int32
    values: Float64[Shape('n'), ORDER_F]

def step(
    state: sim_state,
    t: Float64,
    objective: Callable[[sim_state, Float64], Float64],
) -> tuple[Returns["state", sim_state], Returns["score", Float64]]: ...
""",
    )

    before = assess_wrap_readiness(source, filename="solver.f90")
    after = assess_wrap_readiness(source, filename="solver.f90", pyi_files=[context])

    assert before["wrappable"] is False
    assert {blocker["code"] for blocker in before["wrappability_blockers"]} == {
        "unresolved_derived_type_arguments",
        "callback_arguments_requiring_pyi",
    }
    assert after["wrappable"] is True
    assert after["callback_arguments_requiring_pyi"] == []
    assert after["pyi_context"]["provided_callbacks"] == [
        {"procedure": "step", "argument": "objective"}
    ]


def test_pyi_context_does_not_clear_callback_without_callable_annotation(tmp_path: Path):
    source = """
subroutine apply(f, x, y)
  procedure(callback_fn) :: f
  real(8), intent(in) :: x
  real(8), intent(out) :: y
end subroutine apply
"""
    context = _write(
        tmp_path / "apply_context.pyi",
        """
def apply(f: Procedure, x: Float64) -> Returns["y", Float64]: ...
""",
    )

    report = assess_wrap_readiness(source, filename="apply.f90", pyi_files=[context])

    assert report["wrappable"] is False
    assert report["callback_arguments_requiring_pyi"][0]["argument"] == "f"


def test_pyi_context_combines_multiple_files(tmp_path: Path):
    source = """
module solver_mod
  use state_mod, only: sim_state
  use kinds_mod, only: rk
  use callback_mod, only: objective_fn
contains
  subroutine step(state, objective, score)
    type(sim_state), intent(inout) :: state
    procedure(objective_fn) :: objective
    real(kind=rk), intent(out) :: score
  end subroutine step
end module solver_mod
"""
    types = _write(
        tmp_path / "state_mod.pyi",
        """
class sim_state:
    value: Float64
""",
    )
    constants = _write(
        tmp_path / "kinds_mod.pyi",
        """
from typing import Final

rk: Final[Int32] = 8
""",
    )
    callbacks = _write(
        tmp_path / "callback_mod.pyi",
        """
from typing import Callable

def step(
    state: sim_state,
    objective: Callable[[sim_state], Float64],
) -> tuple[Returns["state", sim_state], Returns["score", Float64]]: ...
""",
    )

    report = assess_wrap_readiness(source, filename="solver.f90", pyi_files=[types, constants, callbacks])

    assert report["wrappable"] is True
    assert set(report["pyi_context"]["files"]) == {str(types), str(constants), str(callbacks)}
    assert report["pyi_context"]["provided_constants"] == {"rk": "8"}


def test_cli_wrap_readiness_uses_pyi_context(tmp_path: Path):
    source = _write(
        tmp_path / "solver.f90",
        """
module solver_mod
  use state_mod, only: sim_state
contains
  subroutine step(state)
    type(sim_state), intent(inout) :: state
  end subroutine step
end module solver_mod
""",
    )
    context = _write(
        tmp_path / "state_mod.pyi",
        """
class sim_state:
    n: Int32
""",
    )
    cmd = [
        sys.executable,
        "-m",
        "x2py",
        str(source),
        "--parse",
        "--wrap-readiness",
        "--readiness-pyi",
        str(context),
    ]

    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    assert "Wrappable: yes" in res.stdout
    assert "No wrap-readiness blockers detected." in res.stdout


def test_cli_parse_json_includes_pyi_context_and_cleared_readiness(tmp_path: Path):
    source = _write(
        tmp_path / "scale.f90",
        """
subroutine scale(x)
  use kinds_mod, only: rk
  real(kind=rk), intent(inout) :: x
end subroutine scale
""",
    )
    context = _write(
        tmp_path / "kinds_mod.pyi",
        """
from typing import Final

rk: Final[Int32] = 8
""",
    )
    cmd = [
        sys.executable,
        "-m",
        "x2py",
        str(source),
        "--parse",
        "--json",
        "--readiness-pyi",
        str(context),
    ]

    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(res.stdout)
    readiness = payload[str(source)]["wrap_readiness"]

    assert readiness["wrappable"] is True
    assert readiness["pyi_context"]["provided_constants"] == {"rk": "8"}


def test_cli_repeated_readiness_pyi_files_are_combined(tmp_path: Path):
    source = _write(
        tmp_path / "solver.f90",
        """
module solver_mod
  use state_mod, only: sim_state
  use callback_mod, only: objective_fn
contains
  subroutine step(state, objective)
    type(sim_state), intent(inout) :: state
    procedure(objective_fn) :: objective
  end subroutine step
end module solver_mod
""",
    )
    types = _write(
        tmp_path / "state_mod.pyi",
        """
class sim_state:
    value: Float64
""",
    )
    callbacks = _write(
        tmp_path / "callback_mod.pyi",
        """
from typing import Callable

def step(
    state: sim_state,
    objective: Callable[[sim_state], None],
) -> Returns["state", sim_state]: ...
""",
    )
    cmd = [
        sys.executable,
        "-m",
        "x2py",
        str(source),
        "--parse",
        "--wrap-readiness",
        "--readiness-pyi",
        str(types),
        "--readiness-pyi",
        str(callbacks),
    ]

    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    assert "Wrappable: yes" in res.stdout


def test_cli_readiness_pyi_requires_parse_stage(tmp_path: Path):
    context = _write(tmp_path / "state_mod.pyi", "class sim_state:\n    value: Float64")
    source = _write(tmp_path / "solver.f90", "module solver_mod\nend module solver_mod")
    cmd = [sys.executable, "-m", "x2py", str(source), "--pyi", "--readiness-pyi", str(context)]

    res = subprocess.run(cmd, capture_output=True, text=True)

    assert res.returncode != 0
    assert "--readiness-pyi requires --parse" in res.stderr

