"""Semantic .pyi driven wrapper build tests."""

import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from x2py import build_pyi_extension
from x2py.wrapping import build_fortran_extension

SOURCE = Path(__file__).with_name("fruntime_abi_f90.f90")
PYI_FIXTURE = Path(__file__).with_name("pyi") / "fruntime_abi_f90.pyi"


def _compile_native_object(source: Path, workdir: Path) -> Path:
    compiler = shutil.which("gfortran")
    if compiler is None:
        pytest.skip("gfortran is required to compile native .pyi wrapper test artifacts")

    workdir.mkdir(parents=True, exist_ok=True)
    native_source = workdir / source.name
    shutil.copyfile(source, native_source)
    native_object = workdir / f"{source.stem}.o"
    subprocess.run(
        [
            compiler,
            "-fPIC",
            "-c",
            str(native_source),
            "-o",
            str(native_object),
            "-J",
            str(workdir),
        ],
        check=True,
    )
    return native_object


def _import_from_build_dir(module_name: str, build_dir: Path):
    sys.modules.pop(module_name, None)
    sys.path.insert(0, str(build_dir))
    try:
        return importlib.import_module(module_name)
    finally:
        sys.path.remove(str(build_dir))


def _build_pyi_cli(pyi_path: Path, native_object: Path, build_dir: Path):
    cmd = [
        sys.executable,
        "-m",
        "x2py",
        str(pyi_path),
        "--wrap",
        "--native-object",
        str(native_object),
        "--native-include-dir",
        str(native_object.parent),
        "--out-dir",
        str(build_dir),
        "--json",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)
    return _import_from_build_dir(payload["module_name"], build_dir), payload


def _generate_pyi(source: Path, output: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(source),
            "--pyi",
            "--out",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=True,
    )


def _assert_scale_runtime_contract(module) -> None:
    assert module.scale(np.float64(2.0), np.float64(4.0)) == np.float64(8.0)


@pytest.fixture
def scale_runtime_module(pyi_parity_build_mode: str, tmp_path: Path):
    if pyi_parity_build_mode == "source":
        result = build_fortran_extension(SOURCE, output_dir=tmp_path / "source_build")
        return _import_from_build_dir(result.module_name, result.output_dir)

    generated_pyi = tmp_path / PYI_FIXTURE.name
    _generate_pyi(SOURCE, generated_pyi)
    native_object = _compile_native_object(SOURCE, tmp_path / "native")
    module, _payload = _build_pyi_cli(generated_pyi, native_object, tmp_path / "pyi_build")
    return module


def test_pyi_cli_requires_a_native_link_input(tmp_path: Path):
    result = subprocess.run(
        [sys.executable, "-m", "x2py", str(PYI_FIXTURE), "--wrap", "--out-dir", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "--wrap from .pyi requires --native-object or --native-library" in result.stderr


def test_pyi_python_api_rejects_a_missing_native_artifact(tmp_path: Path):
    missing_object = tmp_path / "missing.o"

    with pytest.raises(FileNotFoundError, match=f"Native artifact not found: {missing_object}"):
        build_pyi_extension(PYI_FIXTURE, native_objects=[missing_object], output_dir=tmp_path / "build")


def test_handwritten_pyi_fixture_builds_from_native_object_without_source_reparse(tmp_path: Path):
    native_object = _compile_native_object(SOURCE, tmp_path / "native")
    module, payload = _build_pyi_cli(PYI_FIXTURE, native_object, tmp_path / "pyi_build")

    assert Path(payload["shared_library"]).is_file()
    assert payload["sources"] == [str(PYI_FIXTURE)]
    assert str(native_object) in payload["native_inputs"]
    assert module.scale(np.float64(2.0), np.float64(4.0)) == np.float64(8.0)


def test_generated_pyi_matches_checked_in_fixture(tmp_path: Path):
    generated_pyi = tmp_path / "fruntime_abi_f90.pyi"
    _generate_pyi(SOURCE, generated_pyi)

    assert generated_pyi.read_text(encoding="utf-8") == PYI_FIXTURE.read_text(encoding="utf-8")


def test_scale_runtime_contract(scale_runtime_module):
    _assert_scale_runtime_contract(scale_runtime_module)
