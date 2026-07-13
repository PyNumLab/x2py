"""GIL release/hold and native status-to-exception policy tests."""

import importlib
import shutil
import sys
import threading
import time
from pathlib import Path

import numpy as np
import pytest

from tests.wrapper.fortran._support import (
    _compile_native_object,
    _import_from_build_dir,
    _sole_native_module,
    wrapper_source,
)
from x2py import build_pyi_extension

RUNTIME_POLICY_SOURCE = wrapper_source("fruntime_policy_f90.f90")
MODIFIED_POLICY_CONTRACT = (
    Path(__file__).parent / "modified_contracts" / "fruntime_policy_f90" / "fruntime_policy_f90.pyi"
)
ROUTES = (
    pytest.param("legacy", {"_force_legacy_wrapper_route": True}, id="legacy"),
    pytest.param("wrapper-plan", {"_force_wrapper_plan_route": True}, id="wrapper-plan"),
)


def _wrapper_start(source: str, route: str, function_name: str) -> int:
    marker = (
        f"static PyObject* bind_c_{function_name}_wrapper"
        if route == "legacy"
        else f"static PyObject * wrap_{function_name}"
    )
    return source.index(marker)


def _assert_runtime_policy_source(source: str, route: str) -> None:
    released_start = _wrapper_start(source, route, "pause_for_one_second")
    held_start = _wrapper_start(source, route, "pause_with_gil")
    solve_start = _wrapper_start(source, route, "solve")
    released_wrapper = source[released_start:held_start]
    held_wrapper = source[held_start:solve_start]
    assert "Py_BEGIN_ALLOW_THREADS" in released_wrapper
    assert "Py_END_ALLOW_THREADS" in released_wrapper
    assert "Py_BEGIN_ALLOW_THREADS" not in held_wrapper
    assert "Py_END_ALLOW_THREADS" not in held_wrapper
    assert "PyErr_SetObject(PyExc_RuntimeError" in source


@pytest.mark.parametrize(("route", "route_kwargs"), ROUTES)
def test_compiled_runtime_policies_release_gil_and_project_native_errors(
    tmp_path: Path,
    monkeypatch,
    route: str,
    route_kwargs: dict[str, bool],
):
    from x2py.pipeline import build
    from x2py.semantics.models import RUNTIME_HOLD_GIL_METADATA, RUNTIME_STATUS_ERROR_METADATA

    source = tmp_path / "fruntime_policy_f90.f90"
    shutil.copyfile(RUNTIME_POLICY_SOURCE, source)

    convert = build.fortran_project_to_semantic_modules

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

    monkeypatch.setattr(build, "fortran_project_to_semantic_modules", convert_with_runtime_policy)
    result = build.build_fortran_extension(source, output_dir=tmp_path, **route_kwargs)

    sys.modules.pop(result.module_name, None)
    sys.path.insert(0, str(tmp_path))
    try:
        module = _sole_native_module(importlib.import_module(result.module_name))
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
    _assert_runtime_policy_source(wrapper_source, route)


@pytest.mark.parametrize(("route", "route_kwargs"), ROUTES)
def test_pyi_runtime_policies_release_gil_and_project_native_errors(
    tmp_path: Path,
    route: str,
    route_kwargs: dict[str, bool],
):
    native_object = _compile_native_object(RUNTIME_POLICY_SOURCE, tmp_path / "native")
    result = build_pyi_extension(
        MODIFIED_POLICY_CONTRACT,
        native_objects=[native_object],
        native_include_dirs=[native_object.parent],
        output_dir=tmp_path / "pyi_build",
        **route_kwargs,
    )
    module = _sole_native_module(_import_from_build_dir(result.module_name, result.output_dir))

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

    wrapper_source = (result.output_dir / "fruntime_policy_f90_wrapper.c").read_text(encoding="utf-8")
    _assert_runtime_policy_source(wrapper_source, route)
