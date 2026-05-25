# -*- coding: utf-8 -*-
"""Compiler-derived C standard-library type fact tests."""

import json
import shutil
import subprocess
import sys

import pytest

from x2py.c_type_probe import (
    CStandardTypeProbeError,
    build_c_standard_type_probe_source,
    probe_c_standard_types,
)
from x2py.preprocessing import PreprocessingConfig


_CC = shutil.which("cc")


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


@pytest.mark.skipif(_CC is None, reason="requires an available native C compiler")
def test_c_standard_type_probe_reports_semantic_facts_from_native_compiler():
    report = probe_c_standard_types(
        PreprocessingConfig(mode="compiler", compiler=_CC, std="c11")
    )

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
    assert report.recipe.compiler == _CC
    assert "-std=c11" in report.recipe.compile_argv
    assert "#include <time.h>" in report.source_text


@pytest.mark.skipif(_CC is None, reason="requires an available native C compiler")
def test_c_standard_type_probe_carries_target_relevant_user_flags(tmp_path):
    include_dir = tmp_path / "include"
    include_dir.mkdir()

    report = probe_c_standard_types(
        PreprocessingConfig(
            mode="compiler",
            compiler=_CC,
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


@pytest.mark.skipif(_CC is None, reason="requires an available native C compiler")
def test_c_standard_type_probe_module_cli_emits_json_for_semantic_input():
    completed = subprocess.run(
        [sys.executable, "-m", "x2py.c_type_probe", "--compiler", _CC],
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["types"]["size_t"]["semantic_category"] == "unsigned_integer"
    assert payload["types"]["FILE"]["kind"] == "opaque_handle"
    assert payload["recipe"]["compiler"] == _CC
    assert payload["source_text"].startswith("#include <limits.h>")
