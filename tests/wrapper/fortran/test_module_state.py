"""Module variables, parameters, saved state, and synchronization tests."""

import importlib
import sys
from pathlib import Path

import numpy as np

from tests.wrapper.fortran._support import (
    _build_text_and_import,
    _sole_native_module,
)

MODULE_VARIABLES_F90_TEXT = Path(__file__).with_name("fmodule_vars_f90.f90").read_text(encoding="utf-8")


def test_scalar_module_variables_use_attributes_and_parameters_have_no_native_setter(tmp_path: Path):
    module = _build_text_and_import(
        MODULE_VARIABLES_F90_TEXT,
        "fmodule_vars_f90.f90",
        tmp_path,
        {
            "bind_c_fmodule_vars_f90_wrapper.f90",
            "fmodule_vars_f90_wrapper.c",
            "fmodule_vars_f90_wrapper.h",
        },
    )

    assert module.nmax == np.int32(12)
    assert module.counter == np.int32(3)
    assert module.scale == np.float64(1.5)
    assert not hasattr(module, "get_counter")
    assert not hasattr(module, "set_counter")
    assert not hasattr(module, "get_scale")
    assert not hasattr(module, "set_scale")
    assert not hasattr(module, "set_nmax")
    assert not hasattr(module, "set_red")
    assert not hasattr(module, "hidden_counter")
    assert not hasattr(module, "get_hidden_counter")

    assert module.summarize() == np.int32(15)
    module.counter = np.int32(9)
    assert module.counter == np.int32(9)
    assert module.summarize() == np.int32(21)

    module.scale = np.float64(2.0)
    assert module.scaled_counter() == np.float64(18.0)

    assert module.saved_counter == np.int32(6)
    module.saved_counter = np.int32(8)
    assert module.saved_counter == np.int32(8)
    assert module.next_local() == np.int32(1)
    assert module.next_local() == np.int32(2)

    wrapper_source = (tmp_path / "fmodule_vars_f90_wrapper.c").read_text(encoding="utf-8")
    summarize_start = wrapper_source.index("static PyObject* bind_c_summarize_wrapper")
    scaled_start = wrapper_source.index("static PyObject* bind_c_scaled_counter_wrapper")
    getter_start = wrapper_source.index("static PyObject* bind_c_get_counter_wrapper")
    setter_start = wrapper_source.index("static PyObject* bind_c_set_counter_wrapper")
    next_getter_start = wrapper_source.index("static PyObject* bind_c_get_scale_wrapper")
    assert "Py_BEGIN_ALLOW_THREADS" in wrapper_source[summarize_start:scaled_start]
    assert "Py_END_ALLOW_THREADS" in wrapper_source[summarize_start:scaled_start]
    assert "Py_BEGIN_ALLOW_THREADS" not in wrapper_source[getter_start:setter_start]
    assert "Py_END_ALLOW_THREADS" not in wrapper_source[getter_start:setter_start]
    assert "Py_BEGIN_ALLOW_THREADS" not in wrapper_source[setter_start:next_getter_start]
    assert "Py_END_ALLOW_THREADS" not in wrapper_source[setter_start:next_getter_start]
    assert not hasattr(module, "get_local_counter")

    sys.modules.pop("fmodule_vars_f90", None)
    sys.path.insert(0, str(tmp_path))
    try:
        second_module = _sole_native_module(importlib.import_module("fmodule_vars_f90"))
    finally:
        sys.path.remove(str(tmp_path))

    assert second_module is not module
    assert second_module.counter == np.int32(9)
    assert second_module.saved_counter == np.int32(8)
    second_module.counter = np.int32(4)
    assert module.counter == np.int32(4)

    module.nmax = np.int32(99)
    assert module.nmax == np.int32(99)
    assert second_module.nmax == np.int32(12)
    assert module.summarize() == np.int32(16)
    assert second_module.summarize() == np.int32(16)
