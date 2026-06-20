"""GIL release/hold and native status-to-exception policy tests."""

import importlib
import shutil
import sys
import threading
import time
from pathlib import Path

import numpy as np
import pytest

RUNTIME_POLICY_SOURCE = Path(__file__).with_name("fruntime_policy_f90.f90")


def test_compiled_runtime_policies_release_gil_and_project_native_errors(tmp_path: Path, monkeypatch):
    from x2py import wrapping
    from x2py.semantics.models import RUNTIME_HOLD_GIL_METADATA, RUNTIME_STATUS_ERROR_METADATA

    source = tmp_path / "fruntime_policy_f90.f90"
    shutil.copyfile(RUNTIME_POLICY_SOURCE, source)

    convert = wrapping.fortran_project_to_semantic_modules

    def convert_with_runtime_policy(*args, **kwargs):
        modules = convert(*args, **kwargs)
        functions = {function.name: function for module in modules for function in module.functions}
        functions["pause_with_gil"].metadata[RUNTIME_HOLD_GIL_METADATA] = True
        functions["solve"].metadata[RUNTIME_STATUS_ERROR_METADATA] = {
            "status": "status",
            "message": "message",
            "success": 0,
        }
        return modules

    monkeypatch.setattr(wrapping, "fortran_project_to_semantic_modules", convert_with_runtime_policy)
    result = wrapping.build_fortran_extension(source, output_dir=tmp_path)

    sys.modules.pop(result.module_name, None)
    sys.path.insert(0, str(tmp_path))
    try:
        module = importlib.import_module(result.module_name)
        assert module.solve(np.int32(1)) is None
        with pytest.raises(RuntimeError, match="negative input"):
            module.solve(np.int32(-1))

        failures = []

        def native_pause():
            try:
                module.pause_for_one_second()
            except BaseException as error:  # pragma: no cover - reported by the assertion below
                failures.append(error)

        worker = threading.Thread(target=native_pause)
        worker.start()
        time.sleep(0.05)
        assert worker.is_alive(), "the native call kept the GIL and blocked the test thread"
        worker.join(timeout=2.0)
        assert not worker.is_alive()

        held_worker = threading.Thread(target=lambda: module.pause_with_gil())
        held_worker.start()
        time.sleep(0.05)
        held_worker.join(timeout=0.1)
        assert not held_worker.is_alive(), "@hold_gil did not serialize the native call"
        assert failures == []
    finally:
        sys.path.remove(str(tmp_path))

    wrapper_source = (tmp_path / "fruntime_policy_f90_wrapper.c").read_text(encoding="utf-8")
    released_start = wrapper_source.index("static PyObject* bind_c_pause_for_one_second_wrapper")
    held_start = wrapper_source.index("static PyObject* bind_c_pause_with_gil_wrapper")
    solve_start = wrapper_source.index("static PyObject* bind_c_solve_wrapper")
    released_wrapper = wrapper_source[released_start:held_start]
    held_wrapper = wrapper_source[held_start:solve_start]
    assert "Py_BEGIN_ALLOW_THREADS" in released_wrapper
    assert "Py_END_ALLOW_THREADS" in released_wrapper
    assert "Py_BEGIN_ALLOW_THREADS" not in held_wrapper
    assert "Py_END_ALLOW_THREADS" not in held_wrapper
    assert "PyErr_SetObject(PyExc_RuntimeError" in wrapper_source
