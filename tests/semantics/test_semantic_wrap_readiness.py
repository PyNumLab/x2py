import json
import subprocess
import sys
from pathlib import Path

import pytest

from semantics.pyi_parser import parse_pyi_text
from semantics.models import (
    SemanticArgument,
    SemanticClass,
    SemanticFunction,
    SemanticMethod,
    SemanticModule,
    SemanticType,
)
from semantics.readiness import (
    _iter_expression_values,
    assess_pyi_wrap_readiness,
    assess_semantic_wrap_readiness,
)
from x2py import cli as x2py_cli


TEST_FILE = Path(__file__).parent.parent / "data" / "fortran" / "general" / "basic_subroutine.f90"


def _readiness_from_pyi(source: str):
    module = parse_pyi_text(source, module_name="solver")
    return assess_semantic_wrap_readiness(module, source="solver.pyi")


def _blocker_codes(report: dict) -> set[str]:
    return {blocker["code"] for blocker in report["wrappability_blockers"]}


def _write_ready_fortran(path: Path) -> Path:
    path.write_text(
        """module m
contains
  subroutine work(n)
    integer, intent(in) :: n
  end subroutine work
end module m
""",
        encoding="utf-8",
    )
    return path


def test_completed_pyi_interface_is_semantically_ready():
    report = _readiness_from_pyi(
        """
from typing import Callable, Final

rk: Final[Int32] = 8
nmax: Final[Int32] = 32

class sim_state:
    n: Int32
    values: Float64[n]

def step(
    state: sim_state,
    t: Float64,
    objective: Callable[[sim_state, Float64], Float64],
    scratch: Float64[nmax]
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
def fill(n: Int32, x: Float64[n]) -> None: ...
"""
    )

    assert report["wrappable"] is True


def test_final_constant_needs_literal_value_for_shape_readiness():
    report = _readiness_from_pyi(
        """
n: Final[Int32]

def fill(x: Float64[n]) -> None: ...
"""
    )

    assert report["wrappable"] is False
    assert "missing_compile_time_values" in _blocker_codes(report)


def test_final_constant_literal_value_makes_shape_ready():
    report = _readiness_from_pyi(
        """
n: Final[Int32] = 16

def fill(x: Float64[n]) -> None: ...
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


def test_assess_pyi_wrap_readiness_expands_directory_and_deduplicates_paths(tmp_path: Path):
    nested = tmp_path / "nested"
    nested.mkdir()
    first = tmp_path / "first.pyi"
    second = nested / "second.pyi"
    ignored = nested / "ignored.txt"
    first.write_text("def first(x: Int32) -> None: ...\n", encoding="utf-8")
    second.write_text("def second(x: Int32) -> None: ...\n", encoding="utf-8")
    ignored.write_text("not a stub", encoding="utf-8")

    report = assess_pyi_wrap_readiness([tmp_path, first])

    assert report["wrappable"] is True
    assert report["n_modules"] == 2
    assert report["source"] == [str(first), str(second)]


def test_readiness_skips_private_api_and_normalizes_metadata_blocker_items():
    module = SemanticModule(
        name="policy",
        metadata={
            "readiness_blockers": [
                "ignored",
                {"code": "default_item", "message": "default", "item": {"detail": "fallback"}},
                {
                    "code": "scalar_item",
                    "message": "scalar",
                    "items": "detail text",
                    "unit": "policy.override",
                    "unit_kind": "policy",
                },
            ]
        },
        variables=[SemanticArgument("hidden", SemanticType("Undeclared"), visibility="private")],
        classes=[
            SemanticClass(name="Private", fields=[SemanticArgument("missing", SemanticType("Undeclared"))], visibility="private"),
            SemanticClass(
                name="Public",
                methods=[
                    SemanticMethod(name="hidden", arguments=[SemanticArgument("missing", SemanticType("Undeclared"))], visibility="private"),
                    SemanticMethod(name="ready", arguments=[SemanticArgument("value", SemanticType("Int32"))]),
                ],
            ),
        ],
        functions=[SemanticFunction(name="hidden", arguments=[SemanticArgument("missing", SemanticType("Undeclared"))], visibility="private")],
    )

    report = assess_semantic_wrap_readiness(module)
    blockers = {blocker["code"]: blocker for blocker in report["wrappability_blockers"]}

    assert set(blockers) == {"default_item", "scalar_item"}
    assert blockers["default_item"]["items"][0]["detail"] == "fallback"
    assert blockers["scalar_item"]["items"][0]["detail"] == "detail text"
    assert {unit["unit"] for unit in report["unit_blockers"]} == {"policy", "policy.override"}


def test_readiness_accepts_qualified_types_from_imported_modules_and_aliases():
    report = _readiness_from_pyi(
        """
import state_mod
import mesh_mod as mesh
from values_mod import value_t as imported_value

def step(a: state_mod.state_t, b: mesh.mesh_t, c: imported_value) -> None: ...
"""
    )

    assert report["wrappable"] is True


def test_readiness_empty_public_surface_and_nested_expression_utility():
    report = assess_semantic_wrap_readiness(SemanticModule(name="empty"))

    assert _blocker_codes(report) == {"no_public_api"}
    assert list(_iter_expression_values({"a": ["n", ("m", {"deep": "k"})]})) == ["n", "m", "k"]


def test_cli_wrap_readiness_loads_completed_pyi(tmp_path: Path):
    pyi = tmp_path / "solver.pyi"
    pyi.write_text(
        """
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


def test_cli_wrap_readiness_json_loads_pyi(tmp_path: Path):
    pyi = tmp_path / "solver.pyi"
    pyi.write_text("def fill(n: Int32) -> None: ...\n", encoding="utf-8")

    cmd = [sys.executable, "-m", "x2py", str(pyi), "--wrap-readiness", "--json"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(res.stdout)

    assert payload[str(pyi)]["source_kind"] == "pyi"
    assert payload[str(pyi)]["wrap_readiness"]["wrappable"] is True


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


def test_cli_parse_can_print_semantic_wrap_readiness():
    cmd = [sys.executable, "-m", "x2py", str(TEST_FILE), "--parse", "--wrap-readiness"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "subroutine add1" in res.stdout
    assert "Source: fortran" in res.stdout
    assert "Wrappable: yes" in res.stdout


def test_cli_parse_wrap_readiness_json_keeps_stage_payloads_separate():
    cmd = [sys.executable, "-m", "x2py", str(TEST_FILE), "--parse", "--wrap-readiness", "--json"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(res.stdout)
    assert str(TEST_FILE) in payload["parse"]
    assert "wrap_readiness" not in payload["parse"][str(TEST_FILE)]
    assert payload["wrap_readiness"][str(TEST_FILE)]["wrap_readiness"]["wrappable"] is True


def test_cli_semantics_can_include_semantic_wrap_readiness():
    cmd = [sys.executable, "-m", "x2py", str(TEST_FILE), "--semantics", "--wrap-readiness"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(res.stdout)
    assert payload[str(TEST_FILE)]["semantic_modules"]
    assert payload[str(TEST_FILE)]["wrap_readiness"]["wrappable"] is True


def test_cli_help_includes_semantic_wrap_readiness_examples():
    cmd = [sys.executable, "-m", "x2py", "--help"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "python -m x2py path/to/file.f90 --wrap-readiness" in res.stdout
    assert "python -m x2py path/to/file.f90 --semantics --wrap-readiness" in res.stdout
    assert "python -m x2py path/to/module.pyi --wrap-readiness" in res.stdout


def test_x2py_main_wrap_readiness_mode_from_inline_source(tmp_path: Path, monkeypatch, capsys):
    f90 = _write_ready_fortran(tmp_path / "mini.f90")

    monkeypatch.setattr(sys, "argv", ["x2py", str(f90), "--wrap-readiness"])
    assert x2py_cli.main() == 0
    assert "Wrappable: yes" in capsys.readouterr().out


def test_x2py_main_parse_wrap_readiness_json_keeps_payloads_separate(tmp_path: Path, monkeypatch, capsys):
    f90 = _write_ready_fortran(tmp_path / "mini.f90")

    monkeypatch.setattr(sys, "argv", ["x2py", str(f90), "--parse", "--wrap-readiness", "--json"])
    assert x2py_cli.main() == 0
    payload = json.loads(capsys.readouterr().out)

    assert str(f90) in payload["parse"]
    assert "wrap_readiness" not in payload["parse"][str(f90)]
    assert payload["wrap_readiness"][str(f90)]["wrap_readiness"]["wrappable"] is True


def test_x2py_main_parse_wrap_readiness_out_keeps_payloads_separate(tmp_path: Path, monkeypatch, capsys):
    f90 = _write_ready_fortran(tmp_path / "mini.f90")
    out = tmp_path / "report.json"

    monkeypatch.setattr(sys, "argv", ["x2py", str(f90), "--parse", "--wrap-readiness", "--out", str(out)])
    assert x2py_cli.main() == 0
    assert capsys.readouterr().out == ""
    payload = json.loads(out.read_text(encoding="utf-8"))

    assert str(f90) in payload["parse"]
    assert "wrap_readiness" not in payload["parse"][str(f90)]
    assert payload["wrap_readiness"][str(f90)]["wrap_readiness"]["wrappable"] is True


def test_x2py_main_semantics_wrap_readiness_attaches_semantic_payload(tmp_path: Path, monkeypatch, capsys):
    f90 = _write_ready_fortran(tmp_path / "mini.f90")

    monkeypatch.setattr(sys, "argv", ["x2py", str(f90), "--semantics", "--wrap-readiness"])
    assert x2py_cli.main() == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload[str(f90)]["semantic_modules"]
    assert payload[str(f90)]["wrap_readiness"]["wrappable"] is True


def test_x2py_main_wrap_readiness_json_directory_expands_fortran_and_pyi(tmp_path: Path, monkeypatch, capsys):
    f90 = _write_ready_fortran(tmp_path / "mini.f90")
    pyi = tmp_path / "solver.pyi"
    pyi.write_text("def fill(n: Int32) -> None: ...\n", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["x2py", str(tmp_path), "--wrap-readiness", "--json"])
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

    monkeypatch.setattr(sys, "argv", ["x2py", str(f90)])
    with pytest.raises(SystemExit) as stage_error:
        x2py_cli.main()
    assert stage_error.value.code == 2
    assert "Select at least one stage flag" in capsys.readouterr().err
