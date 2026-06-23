"""Visibility, naming, and Python API surface runtime wrapper tests."""

import subprocess
import sys
from pathlib import Path

import numpy as np

from tests.wrapper.fortran._support import (
    _build_text_and_import,
)

NAMING_F90_TEXT = Path(__file__).with_name("fnaming_f90.f90").read_text(encoding="utf-8")


def test_visibility_and_default_python_name_fixing_policy(tmp_path: Path):
    module = _build_text_and_import(
        NAMING_F90_TEXT,
        "fnaming_f90.f90",
        tmp_path,
        {
            "bind_c_fnaming_f90_wrapper.f90",
            "fnaming_f90_wrapper.c",
            "fnaming_f90_wrapper.h",
        },
    )

    assert module.lambda_(np.int32(3)) == 4
    assert module.lambda__2(np.int32(3)) == 5
    assert module.get_value() == 100
    assert module.value == 7
    module.value = np.int32(11)
    assert module.value == 11
    assert not hasattr(module, "get_value_2")
    assert not hasattr(module, "set_value")

    assert not hasattr(module, "hidden_t")
    assert not hasattr(module, "hidden_proc")

    item = module.visible_t(lambda_=np.int32(5), lambda__2=np.int32(6))
    assert item.lambda_ == 5
    assert item.lambda__2 == 6
    assert item.from_() == 11
    assert not hasattr(item, "hidden")


def test_strict_wrapper_names_reject_python_name_fixes(tmp_path: Path):
    source = tmp_path / "fnaming_f90.f90"
    source.write_text(NAMING_F90_TEXT, encoding="utf-8")

    cmd = [
        sys.executable,
        "-m",
        "x2py",
        str(source),
        "--out-dir",
        str(tmp_path),
        "--json",
        "--strict-wrapper-names",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    assert result.returncode != 0
    assert "strict wrapper naming" in result.stderr
