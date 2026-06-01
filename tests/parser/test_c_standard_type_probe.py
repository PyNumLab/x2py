"""Compiler-derived C standard-library type fact tests."""

import json
import shutil
import subprocess
import sys
from types import SimpleNamespace

import pytest

import x2py.c_type_probe as c_type_probe
from x2py.c_type_probe import (
    CStandardTypeProbeError,
    _semantic_type_facts,
    build_c_standard_type_probe_source,
    probe_c_standard_types,
)
from x2py.preprocessing import PreprocessingConfig


_CC = shutil.which("cc")


def _required_c_compiler() -> str:
    assert _CC is not None, "the full C pipeline test suite requires an available native C compiler"
    return _CC


def test_c_standard_type_probe_source_queries_standard_headers_without_layout_claims():
    source = build_c_standard_type_probe_source()

    assert "#include <stddef.h>" in source
    assert "#include <stdint.h>" in source
    assert "#include <time.h>" in source
    assert "#include <stdio.h>" in source
    assert 'X2PY_PRINT_ARITHMETIC("size_t"' in source
    assert 'X2PY_PRINT_ARITHMETIC("uint32_t"' in source
    assert 'X2PY_PRINT_ARITHMETIC("time_t"' in source
    assert "sizeof(FILE *)" in source
    assert "sizeof(FILE)" not in source


def test_c_standard_type_probe_requires_an_explicit_compiler():
    with pytest.raises(CStandardTypeProbeError, match="exact compiler"):
        probe_c_standard_types(PreprocessingConfig(mode="compiler"))


def test_c_standard_type_probe_rejects_compile_database_and_classifies_all_arithmetic_categories():
    with pytest.raises(CStandardTypeProbeError, match="does not consume compile_commands"):
        probe_c_standard_types(
            PreprocessingConfig(mode="compiler", compiler="cc", compile_commands="compile_commands.json")
        )

    types = {
        "real": {"available": True, "kind": "arithmetic", "underlying_c_type": "double"},
        "char": {"available": True, "kind": "arithmetic", "underlying_c_type": "char"},
        "other": {"available": True, "kind": "arithmetic", "underlying_c_type": "other"},
        "unavailable": {"available": False, "kind": "arithmetic", "underlying_c_type": "double"},
    }
    _semantic_type_facts(types)

    assert types["real"]["semantic_category"] == "real"
    assert types["char"]["semantic_category"] == "integer_implementation_signedness"
    assert types["other"]["semantic_category"] == "implementation_defined"
    assert "semantic_category" not in types["unavailable"]


@pytest.mark.parametrize(
    ("results", "message"),
    [
        ([OSError("missing")], "failed to run C type probe compiler"),
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
            "missing 'types'",
        ),
    ],
)
def test_c_standard_type_probe_reports_compiler_and_runner_failures(monkeypatch, results, message):
    responses = iter(results)

    def run(*_args, **_kwargs):
        result = next(responses)
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(c_type_probe.subprocess, "run", run)
    with pytest.raises(CStandardTypeProbeError, match=message):
        probe_c_standard_types(PreprocessingConfig(mode="compiler", compiler="cc"), runner=["runner"])


def test_c_standard_type_probe_accepts_explicit_runner_and_cli_validates_macros(monkeypatch):
    responses = iter(
        [
            SimpleNamespace(returncode=0, stderr=""),
            SimpleNamespace(returncode=0, stdout='{"types": {}}', stderr=""),
        ]
    )
    monkeypatch.setattr(c_type_probe.subprocess, "run", lambda *_args, **_kwargs: next(responses))

    report = probe_c_standard_types(PreprocessingConfig(mode="compiler", compiler="cc"), runner=["emulator"])
    assert report.recipe.run_argv[0] == "emulator"

    with pytest.raises(SystemExit):
        c_type_probe.main(["--compiler", "cc", "-D", "=bad"])
    with pytest.raises(SystemExit):
        c_type_probe.main(["--compiler", "cc", "-U", "=bad"])


def test_c_standard_type_probe_reports_semantic_facts_from_native_compiler():
    compiler = _required_c_compiler()
    report = probe_c_standard_types(PreprocessingConfig(mode="compiler", compiler=compiler, std="c11"))

    size_t = report.types["size_t"]
    assert size_t["available"] is True
    assert size_t["kind"] == "integer"
    assert size_t["signed"] is False
    assert size_t["semantic_category"] == "unsigned_integer"
    assert size_t["bits"] > 0

    uint32_t = report.types["uint32_t"]
    if uint32_t["available"]:
        assert uint32_t["kind"] == "integer"
        assert uint32_t["signed"] is False
        assert uint32_t["bits"] == 32

    time_t = report.types["time_t"]
    assert time_t["available"] is True
    assert time_t["semantic_category"] in {
        "signed_integer",
        "unsigned_integer",
        "real",
        "integer_implementation_signedness",
        "implementation_defined",
    }

    file_type = report.types["FILE"]
    assert file_type["kind"] == "opaque_handle"
    assert file_type["pointer_bits"] > 0
    assert report.recipe.compiler == compiler
    assert "-std=c11" in report.recipe.compile_argv
    assert "#include <time.h>" in report.source_text


def test_c_standard_type_probe_carries_target_relevant_user_flags(tmp_path):
    compiler = _required_c_compiler()
    include_dir = tmp_path / "include"
    include_dir.mkdir()

    report = probe_c_standard_types(
        PreprocessingConfig(
            mode="compiler",
            compiler=compiler,
            include_dirs=[str(include_dir)],
            defines=["X2PY_FEATURE=1"],
            undefs=["X2PY_OLD_FEATURE"],
            std="c99",
            compiler_args=["-funsigned-char"],
        )
    )

    argv = report.recipe.compile_argv
    assert f"-I{include_dir}" in argv
    assert "-DX2PY_FEATURE=1" in argv
    assert "-UX2PY_OLD_FEATURE" in argv
    assert "-std=c11" in argv
    assert "-funsigned-char" in argv
    assert report.recipe.requested_standard == "c99"
    assert report.recipe.include_dirs == [str(include_dir)]
    assert report.recipe.defines == ["X2PY_FEATURE=1"]
    assert report.recipe.undefs == ["X2PY_OLD_FEATURE"]
    assert report.recipe.compiler_args == ["-funsigned-char"]


def test_c_standard_type_probe_module_cli_emits_json_for_semantic_input():
    compiler = _required_c_compiler()
    completed = subprocess.run(
        [sys.executable, "-m", "x2py.c_type_probe", "--compiler", compiler],
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["types"]["size_t"]["semantic_category"] == "unsigned_integer"
    assert payload["types"]["FILE"]["kind"] == "opaque_handle"
    assert payload["recipe"]["compiler"] == compiler
    assert payload["source_text"].startswith("#include <limits.h>")
