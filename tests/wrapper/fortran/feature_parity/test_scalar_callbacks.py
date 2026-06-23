"""Scalar callbacks, callback lifetime, GIL handling, and fatal errors."""

import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from tests.wrapper.fortran._support import (
    wrapper_source,
    _build_text_and_import,
)

CALLBACK_SCALAR_F90_TEXT = wrapper_source("fcallback_scalar_f90.f90").read_text(encoding="utf-8")


def test_immediate_scalar_dummy_procedure_calls_python_callback(tmp_path: Path):
    module = _build_text_and_import(
        CALLBACK_SCALAR_F90_TEXT,
        "fcallback_scalar_f90.f90",
        tmp_path,
        {
            "bind_c_fcallback_scalar_f90_wrapper.f90",
            "fcallback_scalar_f90_wrapper.c",
            "fcallback_scalar_f90_wrapper.h",
        },
    )

    assert module.apply_scalar(lambda value: value * 3.0, np.float64(2.5)) == np.float64(7.5)
    assert module.apply_explicit(lambda value: value - 1.0, np.float64(2.5)) == np.float64(1.5)
    notified = []
    assert module.call_notify(lambda value: notified.append(value), np.float64(6.0)) is None
    assert notified == [6.0]
    assert module.apply_scalar(
        lambda value: module.apply_scalar(lambda nested: nested + 1.0, np.float64(value)) * 2.0,
        np.float64(3.0),
    ) == np.float64(8.0)

    class Callback:
        def __call__(self, value):
            return value

    callback = Callback()
    references_before = sys.getrefcount(callback)
    assert module.apply_scalar(callback, np.float64(3.0)) == np.float64(3.0)
    assert sys.getrefcount(callback) == references_before
    with pytest.raises(TypeError, match="must be callable"):
        module.apply_scalar(42, np.float64(1.0))

    wrapper_source = (tmp_path / "fcallback_scalar_f90_wrapper.c").read_text(encoding="utf-8")
    assert "static _Thread_local" in wrapper_source
    assert "PyThread_get_thread_ident()" in wrapper_source
    assert "PyGILState_Ensure()" in wrapper_source
    assert "PyGILState_Release(" in wrapper_source
    assert "Py_BEGIN_ALLOW_THREADS" not in wrapper_source
    assert "Py_END_ALLOW_THREADS" not in wrapper_source
    assert "PyErr_PrintEx(0);" in wrapper_source
    assert "abort();" in wrapper_source
    assert "Py_INCREF(bound_callback_obj);" in wrapper_source
    assert "Py_DECREF(" in wrapper_source


def test_callback_exception_prints_traceback_and_aborts_host_process(tmp_path: Path):
    _build_text_and_import(
        CALLBACK_SCALAR_F90_TEXT,
        "fcallback_scalar_f90.f90",
        tmp_path,
        {
            "bind_c_fcallback_scalar_f90_wrapper.f90",
            "fcallback_scalar_f90_wrapper.c",
            "fcallback_scalar_f90_wrapper.h",
        },
    )
    script = """
import numpy as np
import fcallback_scalar_f90 as module
module = module.fcallback_scalar_f90

def fail(value):
    raise ValueError(f"callback exploded at {value}")

module.apply_scalar(fail, np.float64(4.0))
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "Traceback (most recent call last)" in result.stderr
    assert "ValueError: callback exploded at 4.0" in result.stderr

    invalid_return = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import numpy as np; import fcallback_scalar_f90 as root; module = root.fcallback_scalar_f90; "
                "module.apply_scalar(lambda value: 'wrong', np.float64(4.0))"
            ),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert invalid_return.returncode != 0
    assert "TypeError" in invalid_return.stderr

    invalid_signature = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import numpy as np; import fcallback_scalar_f90 as root; module = root.fcallback_scalar_f90; "
                "module.apply_scalar(lambda: np.float64(1.0), np.float64(4.0))"
            ),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert invalid_signature.returncode != 0
    assert "TypeError" in invalid_signature.stderr
