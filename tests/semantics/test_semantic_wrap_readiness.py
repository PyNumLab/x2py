import json
import subprocess
import sys
from pathlib import Path

from semantics.pyi_parser import parse_pyi_text
from semantics.readiness import assess_semantic_wrap_readiness


def _readiness_from_pyi(source: str):
    module = parse_pyi_text(source, module_name="solver")
    return assess_semantic_wrap_readiness(module, source="solver.pyi")


def _blocker_codes(report: dict) -> set[str]:
    return {blocker["code"] for blocker in report["wrappability_blockers"]}


def test_completed_pyi_interface_is_semantically_ready():
    report = _readiness_from_pyi(
        """
from typing import Callable, Final

rk: Final[Int32] = 8
nmax: Final[Int32] = 32

class sim_state:
    n: Int32
    values: Float64[Shape('n'), ORDER_F]

def step(
    state: sim_state,
    t: Float64,
    objective: Callable[[sim_state, Float64], Float64],
    scratch: Float64[Shape('nmax'), ORDER_F]
) -> tuple[Returns["state", sim_state], Returns["score", Float64]]: ...
"""
    )

    assert report["wrappable"] is True
    assert report["wrappability_blockers"] == []


def test_imported_type_can_complete_semantic_readiness():
    report = _readiness_from_pyi(
        """
from state_mod import sim_state

def step(state: sim_state) -> Returns["state", sim_state]: ...
"""
    )

    assert report["wrappable"] is True


def test_missing_semantic_type_blocks_readiness():
    report = _readiness_from_pyi(
        """
def step(state: sim_state) -> Returns["state", sim_state]: ...
"""
    )

    assert report["wrappable"] is False
    assert "unresolved_semantic_types" in _blocker_codes(report)


def test_shape_argument_makes_shape_symbol_ready():
    report = _readiness_from_pyi(
        """
def fill(n: Int32, x: Float64[Shape('n'), ORDER_F]) -> Returns["x", Float64[Shape('n'), ORDER_F]]: ...
"""
    )

    assert report["wrappable"] is True


def test_final_constant_needs_literal_value_for_shape_readiness():
    report = _readiness_from_pyi(
        """
n: Final[Int32]

def fill(x: Float64[Shape('n'), ORDER_F]) -> Returns["x", Float64[Shape('n'), ORDER_F]]: ...
"""
    )

    assert report["wrappable"] is False
    assert "missing_compile_time_values" in _blocker_codes(report)


def test_final_constant_literal_value_makes_shape_ready():
    report = _readiness_from_pyi(
        """
n: Final[Int32] = 16

def fill(x: Float64[Shape('n'), ORDER_F]) -> Returns["x", Float64[Shape('n'), ORDER_F]]: ...
"""
    )

    assert report["wrappable"] is True


def test_callback_placeholder_blocks_until_callable_signature_is_supplied():
    report = _readiness_from_pyi(
        """
def integrate(objective: Procedure, x0: Float64) -> Float64: ...
"""
    )

    assert report["wrappable"] is False
    assert "callback_signature_incomplete" in _blocker_codes(report)
    blocker = report["wrappability_blockers"][0]["items"][0]
    assert blocker["needs"] == [
        "callback argument order",
        "callback argument types",
        "callback return type",
    ]


def test_callable_with_signature_makes_callback_ready():
    report = _readiness_from_pyi(
        """
from typing import Callable

def integrate(objective: Callable[[Float64], Float64], x0: Float64) -> Float64: ...
"""
    )

    assert report["wrappable"] is True


def test_callable_without_argument_list_is_not_enough_for_readiness():
    report = _readiness_from_pyi(
        """
from typing import Callable

def integrate(objective: Callable[..., Float64], x0: Float64) -> Float64: ...
"""
    )

    assert report["wrappable"] is False
    assert "callback_signature_incomplete" in _blocker_codes(report)


def test_cli_wrap_readiness_loads_completed_pyi(tmp_path: Path):
    pyi = tmp_path / "solver.pyi"
    pyi.write_text(
        """
n: Final[Int32] = 8

def fill(x: Float64[Shape('n'), ORDER_F]) -> Returns["x", Float64[Shape('n'), ORDER_F]]: ...
""",
        encoding="utf-8",
    )

    cmd = [sys.executable, "-m", "x2py", str(pyi), "--wrap-readiness"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    assert "Source: pyi" in res.stdout
    assert "Wrappable: yes" in res.stdout
    assert "No semantic readiness blockers detected." in res.stdout


def test_cli_wrap_readiness_json_loads_pyi(tmp_path: Path):
    pyi = tmp_path / "solver.pyi"
    pyi.write_text("def fill(n: Int32) -> None: ...\n", encoding="utf-8")

    cmd = [sys.executable, "-m", "x2py", str(pyi), "--wrap-readiness", "--json"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(res.stdout)

    assert payload[str(pyi)]["source_kind"] == "pyi"
    assert payload[str(pyi)]["wrap_readiness"]["wrappable"] is True
