"""Builds that wrap several related Fortran source files together."""

import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from tests.wrapper.fortran._support import (
    WRAPPER_FORTRAN_DATA,
    _build_sources_and_import,
)


FIXTURES = WRAPPER_FORTRAN_DATA / "multi_source"
MODULE_FIXTURES = FIXTURES / "modules"
STANDALONE_FIXTURES = FIXTURES / "standalone"


def _source_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_multi_file_modules_build_one_merged_extension(tmp_path: Path):
    module, payload = _build_sources_and_import(
        [
            ("first_api.f90", _source_text(MODULE_FIXTURES / "first_api.f90")),
            ("second_api.f90", _source_text(MODULE_FIXTURES / "second_api.f90")),
        ],
        tmp_path,
    )

    assert payload["module_name"] == "first_api"
    assert module.first_api.add_one(np.int32(4)) == 5
    assert module.second_api.double_value(np.int32(4)) == 10
    assert module.second_api.counter == 3
    module.second_api.counter = np.int32(7)
    assert module.second_api.counter == 7
    assert not hasattr(module.second_api, "get_counter")
    assert not hasattr(module.second_api, "set_counter")
    bridge = (tmp_path / "bind_c_first_api_wrapper.f90").read_text(encoding="utf-8").lower()
    assert "use first_api" in bridge
    assert "use second_api" in bridge


def test_multi_file_standalone_procedures_build_one_merged_extension(tmp_path: Path):
    module, payload = _build_sources_and_import(
        [
            ("standalone_api.f", _source_text(STANDALONE_FIXTURES / "standalone_api.f")),
            ("double_value.f", _source_text(STANDALONE_FIXTURES / "double_value.f")),
        ],
        tmp_path,
    )

    assert payload["module_name"] == "standalone_api"
    assert module.add_one(np.int32(4)) == 5
    assert module.double_value(np.int32(4)) == 8


@pytest.mark.skipif(
    sys.platform == "win32" or shutil.which("make") is None,
    reason="generated Makefile requires GNU Make and a POSIX shell",
)
def test_makefile_mode_reproduces_multi_source_build(tmp_path: Path):
    first = tmp_path / "first_api.f90"
    second = tmp_path / "second_api.f90"
    shutil.copyfile(MODULE_FIXTURES / "first_api.f90", first)
    shutil.copyfile(MODULE_FIXTURES / "second_api.f90", second)

    command = [
        sys.executable,
        "-m",
        "x2py",
        str(first),
        str(second),
        "--makefile",
        "--out-dir",
        str(tmp_path),
        "--json",
    ]
    generated = subprocess.run(command, capture_output=True, text=True, check=True)
    payload = json.loads(generated.stdout)
    makefile = Path(payload["build_makefile"])

    assert payload["compiled"] is False
    assert makefile.is_file()
    assert not Path(payload["shared_library"]).exists()
    text = makefile.read_text(encoding="utf-8")
    assert "FC := " in text
    assert "CC := " in text
    assert "X2PY_FFLAGS ?=" in text
    assert f"{tmp_path / 'second_api.o'}: {second} {tmp_path / 'first_api.o'}" in text
    assert f"{tmp_path / 'bind_c_first_api_wrapper.o'}:" in text
    assert str(tmp_path / "first_api.o") in text
    assert str(tmp_path / "second_api.o") in text

    built = subprocess.run(
        [
            "make",
            "-j4",
            "-f",
            str(makefile),
            "all",
            "X2PY_FFLAGS=-O3",
            "X2PY_CFLAGS=-O3",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "-O3" in built.stdout
    assert Path(payload["shared_library"]).is_file()

    sys.modules.pop("first_api", None)
    sys.path.insert(0, str(tmp_path))
    try:
        module = importlib.import_module("first_api")
        assert module.second_api.double_value(np.int32(4)) == 10
    finally:
        sys.path.remove(str(tmp_path))
