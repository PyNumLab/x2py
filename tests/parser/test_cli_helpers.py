from __future__ import annotations

import builtins
import runpy
import sys
import types
from pathlib import Path

import pytest

import fortran_parser.cli as fortran_cli
import fortran_parser.utils as fortran_utils
import x2py.cli as x2py_cli


def test_entrypoint_modules_delegate_to_cli_main(monkeypatch):
    monkeypatch.setattr(x2py_cli, "main", lambda: 7)
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("x2py.__main__", run_name="__main__")
    assert exc.value.code == 7

    monkeypatch.setattr(fortran_cli, "main", lambda: 11)
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("fortran_parser.__main__", run_name="__main__")
    assert exc.value.code == 11


def test_fortran_utils_detect_source_form_and_split_csv():
    assert fortran_utils.detect_source_form("", filename="demo.f90") == "free"
    assert fortran_utils.detect_source_form("", filename="demo.for") == "fixed"
    assert fortran_utils.detect_source_form("     X\n") == "fixed"
    assert fortran_utils.detect_source_form("subroutine x\nend subroutine") == "free"
    assert fortran_utils.split_csv("a, b(c, d), e") == ["a", "b(c, d)", "e"]
    assert fortran_utils.split_csv("") == []


def test_fortran_cli_helpers_cover_directory_expansion_and_formatting(tmp_path: Path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.f90").write_text("subroutine a()\nend subroutine a\n", encoding="utf-8")
    (src / "ignore.txt").write_text("skip", encoding="utf-8")
    nested = src / "nested"
    nested.mkdir()
    (nested / "b.for").write_text("subroutine b()\nend subroutine b\n", encoding="utf-8")

    collected = fortran_cli._collect_extensions(src)
    assert {p.name for p in collected} == {"a.f90", "b.for"}

    report = fortran_cli._parse_paths([str(src / "a.f90")])
    assert str(src / "a.f90") in report
    expanded = fortran_cli._parse_paths([str(src)])
    assert set(expanded) == {str(src / "a.f90"), str(src / "nested" / "b.for")}
    text = fortran_cli._format_report(report)
    assert "File:" in text

    wrap_text = fortran_cli._format_wrap_readiness(
        {
            str(src / "a.f90"): {
                "wrap_readiness": {
                    "wrappable": False,
                    "wrappability_blockers": [
                        {
                            "message": "not ready",
                            "code": "unsupported_constructs",
                            "items": [{"line": 3, "text": "foo"}],
                        }
                    ],
                }
            }
        }
    )
    assert "Wrappable: no" in wrap_text
    assert "line 3: foo" in wrap_text


def test_x2py_cli_helpers_cover_report_formatting_and_pyi_output(monkeypatch, capsys):
    report = x2py_cli._format_pyi_report({"x": {"pyi": "def f() -> None: ..."}})
    assert "File: x" in report
    assert "def f() -> None: ..." in report
    assert fortran_cli._format_var_type({"base_type": "derived", "kind": "thing", "rank": 2}) == "type(thing)[2]"
    assert fortran_cli._format_var_type({"base_type": "real", "kind": "8", "rank": 1}) == "real(8)[1]"

    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    x2py_cli.print_pyi_output("hello")
    assert capsys.readouterr().out.strip() == "hello"

    fake_rich = types.ModuleType("rich")
    fake_rich.__path__ = []  # type: ignore[attr-defined]
    fake_console = types.ModuleType("rich.console")
    fake_syntax = types.ModuleType("rich.syntax")
    calls: dict[str, object] = {}

    class DummyConsole:
        def __init__(self, **kwargs):
            calls["console_kwargs"] = kwargs

        def print(self, syntax):
            calls["printed"] = syntax

    class DummySyntax:
        def __init__(self, code, *args, **kwargs):
            calls["syntax"] = (code, args, kwargs)

    fake_console.Console = DummyConsole
    fake_syntax.Syntax = DummySyntax
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setitem(sys.modules, "rich", fake_rich)
    monkeypatch.setitem(sys.modules, "rich.console", fake_console)
    monkeypatch.setitem(sys.modules, "rich.syntax", fake_syntax)
    x2py_cli.print_pyi_output("highlight me")
    assert calls["console_kwargs"]["force_terminal"] is True
    assert calls["syntax"][0] == "highlight me"


def test_x2py_print_pyi_output_falls_back_without_rich(monkeypatch, capsys):
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "rich" or name.startswith("rich."):
            raise ImportError("rich is unavailable")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    x2py_cli.print_pyi_output("fallback")
    assert capsys.readouterr().out.strip() == "fallback"


def test_x2py_print_pyi_output_falls_back_on_render_error(monkeypatch, capsys):
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    fake_rich = types.ModuleType("rich")
    fake_rich.__path__ = []  # type: ignore[attr-defined]
    fake_console = types.ModuleType("rich.console")
    fake_syntax = types.ModuleType("rich.syntax")

    class DummyConsole:
        def __init__(self, **kwargs):
            pass

        def print(self, syntax):
            raise RuntimeError("render failed")

    class DummySyntax:
        def __init__(self, code, *args, **kwargs):
            self.code = code

    fake_console.Console = DummyConsole
    fake_syntax.Syntax = DummySyntax
    monkeypatch.setitem(sys.modules, "rich", fake_rich)
    monkeypatch.setitem(sys.modules, "rich.console", fake_console)
    monkeypatch.setitem(sys.modules, "rich.syntax", fake_syntax)
    x2py_cli.print_pyi_output("fallback-again")
    assert capsys.readouterr().out.strip() == "fallback-again"


def test_fortran_cli_main_handles_parse_and_wrap_readiness(tmp_path: Path, monkeypatch, capsys):
    src = tmp_path / "mini.f90"
    src.write_text("subroutine work(n)\n  integer, intent(in) :: n\nend subroutine work\n", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["fortran_parser", str(src), "--json"])
    assert fortran_cli.main() == 0
    assert str(src) in capsys.readouterr().out

    monkeypatch.setattr(sys, "argv", ["fortran_parser", str(src), "--wrap-readiness"])
    assert fortran_cli.main() == 0
    assert "Wrappable:" in capsys.readouterr().out


@pytest.mark.parametrize(
    "argv",
    [
        ["x2py", "demo.f90", "--out"],
        ["x2py", "demo.f90", "--wrap-readiness"],
        ["x2py", "demo.f90", "--json"],
    ],
)
def test_x2py_cli_rejects_invalid_flag_combinations(monkeypatch, argv):
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit):
        x2py_cli.main()
