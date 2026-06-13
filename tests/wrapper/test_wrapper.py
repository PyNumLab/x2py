import importlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

from tests.wrapper.fmath_cases import fmath_cases


SOURCE = Path(__file__).with_name("fmath.f")


def _assert_fmath_examples(module):
    cases = fmath_cases()
    missing = sorted(name for name, _, _ in cases if not hasattr(module, name))
    assert missing == []

    for name, args, expected in cases:
        actual = getattr(module, name)(*args)
        if isinstance(expected, bool):
            assert bool(actual) is expected, name
        elif isinstance(expected, int):
            assert actual == expected, name
        else:
            np.testing.assert_allclose(actual, expected, rtol=1e-6, atol=1e-6, err_msg=name)


def _build_and_import(workdir: Path):
    source = workdir / SOURCE.name
    shutil.copyfile(SOURCE, source)

    cmd = [
        sys.executable,
        "-m",
        "x2py",
        str(source),
        "--wrap",
        "--out-dir",
        str(workdir),
        "--json",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)

    shared_library = Path(payload["shared_library"])
    assert shared_library.exists()
    assert Path(payload["output_dir"]) == workdir
    assert shared_library.parent == workdir
    assert {Path(path).name for path in payload["generated_sources"]} == {
        "bind_c_fmath_wrapper.f90",
        "fmath_wrapper.c",
        "fmath_wrapper.h",
    }

    sys.modules.pop("fmath", None)
    sys.path.insert(0, str(workdir))
    try:
        return importlib.import_module("fmath")
    finally:
        sys.path.remove(str(workdir))


def test_fortran_wrapper_pipeline_builds_importable_extension(tmp_path: Path):
    module = _build_and_import(tmp_path)

    _assert_fmath_examples(module)


def test_fortran_wrapper_default_places_extension_beside_source(tmp_path: Path):
    source = tmp_path / SOURCE.name
    shutil.copyfile(SOURCE, source)

    cmd = [sys.executable, "-m", "x2py", str(source), "--wrap", "--json"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)

    build_dir = tmp_path / "__x2py__"
    shared_library = Path(payload["shared_library"])
    assert shared_library.parent == tmp_path
    assert shared_library.exists()
    assert Path(payload["output_dir"]) == build_dir
    assert (build_dir / "bind_c_fmath_wrapper.f90").exists()
    assert not list(tmp_path.glob("*_wrapper.c"))


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        module = _build_and_import(Path(tmp))
        _assert_fmath_examples(module)
    print("TEST PASSING!!")
