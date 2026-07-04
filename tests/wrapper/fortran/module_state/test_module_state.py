"""Module variables, parameters, saved state, and synchronization tests."""

import gc
import importlib
import sys
from pathlib import Path

import numpy as np
import pytest

from tests.wrapper.fortran._support import (
    _build_source_or_generated_pyi_and_import,
    wrapper_source,
    _sole_native_module,
)

MODULE_VARIABLES_F90_SOURCE = wrapper_source("fmodule_vars_f90.f90")
DERIVED_ALIAS_F90_SOURCE = wrapper_source("fmodule_derived_alias_f90.f90")
DERIVED_SNAPSHOT_F90_SOURCE = wrapper_source("fmodule_derived_snapshot_f90.f90")
CONTRACT_FIXTURES = Path(__file__).parent / "contracts"


def _module_variables_build_dir(tmp_path: Path, build_mode: str) -> Path:
    if build_mode == "source":
        return tmp_path / "source_build"
    return tmp_path / "generated_pyi_build" / "pyi_build"


def test_scalar_module_variables_use_attributes_and_parameters_have_no_native_setter(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _build_source_or_generated_pyi_and_import(
        MODULE_VARIABLES_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fmodule_vars_f90_wrapper.f90",
            "fmodule_vars_f90_wrapper.c",
            "fmodule_vars_f90_wrapper.h",
        },
        CONTRACT_FIXTURES / "fmodule_vars_f90",
        pyi_parity_build_mode,
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

    build_dir = _module_variables_build_dir(tmp_path, pyi_parity_build_mode)
    if pyi_parity_build_mode == "source":
        wrapper_source = (build_dir / "fmodule_vars_f90_wrapper.c").read_text(encoding="utf-8")
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
    sys.path.insert(0, str(build_dir))
    try:
        second_module = _sole_native_module(importlib.import_module("fmodule_vars_f90"))
    finally:
        sys.path.remove(str(build_dir))

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


def test_aliased_derived_module_object_borrows_native_state(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _build_source_or_generated_pyi_and_import(
        DERIVED_ALIAS_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fmodule_derived_alias_f90_wrapper.f90",
            "fmodule_derived_alias_f90_wrapper.c",
            "fmodule_derived_alias_f90_wrapper.h",
        },
        CONTRACT_FIXTURES / "fmodule_derived_alias_f90",
        pyi_parity_build_mode,
    )

    current = module.current
    assert isinstance(current, module.box)
    assert current.values is None

    module.allocate_current(np.int32(3))
    view = current.values
    assert view.base is current
    np.testing.assert_allclose(view, np.array([1.0, 2.0, 3.0], dtype=np.float64))

    view[0] = np.float64(10.0)
    assert module.current_sum() == np.float64(15.0)
    assert module.current.values_sum() == np.float64(15.0)

    owned = module.box()
    owned.allocate_values(np.int32(2))
    owned.values[0] = np.float64(20.0)
    assert owned.values_sum() == np.float64(22.0)
    assert module.current_sum() == np.float64(15.0)

    del view
    del current
    gc.collect()
    assert module.current_sum() == np.float64(15.0)

    with np.testing.assert_raises(AttributeError):
        module.current = owned

    build_dir = _module_variables_build_dir(tmp_path, pyi_parity_build_mode)
    bridge_source = (build_dir / "bind_c_fmodule_derived_alias_f90_wrapper.f90").read_text(encoding="utf-8")
    assert "c_loc(current)" in bridge_source
    assert "bind_c_set_current" not in bridge_source

    module.deallocate_current()
    assert module.current.values is None


def test_plain_derived_module_object_returns_recursive_snapshot(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _build_source_or_generated_pyi_and_import(
        DERIVED_SNAPSHOT_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fmodule_derived_snapshot_f90_wrapper.f90",
            "fmodule_derived_snapshot_f90_wrapper.c",
            "fmodule_derived_snapshot_f90_wrapper.h",
        },
        CONTRACT_FIXTURES / "fmodule_derived_snapshot_f90",
        pyi_parity_build_mode,
    )

    assert hasattr(module, "Snapshot")
    assert hasattr(module, "box_snapshot")
    assert hasattr(module, "child_snapshot")
    module.initialise_current(np.int32(3))

    current = module.current
    assert type(current) is module.box_snapshot
    assert isinstance(current, module.Snapshot)
    assert not isinstance(current, module.box)
    assert current.snapshot_type is module.box
    assert current.scalar == np.int32(7)
    np.testing.assert_allclose(current.fixed, np.array([1.5, 2.5], dtype=np.float64))
    np.testing.assert_allclose(current.values, np.array([1.0, 2.0, 3.0], dtype=np.float64))
    assert current.fixed.flags.writeable is False
    assert current.values.flags.writeable is False
    assert type(current.nested) is module.child_snapshot
    assert isinstance(current.nested, module.Snapshot)
    assert current.nested.snapshot_type is module.child
    assert current.nested.id == np.int32(11)
    assert not hasattr(current, "scalar_plus_nested")

    with np.testing.assert_raises(ValueError):
        current.values[0] = np.float64(9.0)
    with pytest.raises(AttributeError, match="read-only snapshot"):
        current.scalar = np.int32(99)
    with pytest.raises(AttributeError, match="read-only snapshot"):
        current.scalar_plus_nested()

    module.mutate_current()
    assert current.scalar == np.int32(7)
    np.testing.assert_allclose(current.fixed, np.array([1.5, 2.5], dtype=np.float64))
    np.testing.assert_allclose(current.values, np.array([1.0, 2.0, 3.0], dtype=np.float64))
    assert current.nested.id == np.int32(11)

    updated = module.current
    assert updated.scalar == np.int32(17)
    np.testing.assert_allclose(updated.fixed, np.array([101.5, 102.5], dtype=np.float64))
    np.testing.assert_allclose(updated.values, np.array([1001.0, 1002.0, 1003.0], dtype=np.float64))
    assert updated.nested.id == np.int32(111)

    module.release_current()
    assert module.current.values is None

    build_dir = _module_variables_build_dir(tmp_path, pyi_parity_build_mode)
    wrapper_source_text = (build_dir / "fmodule_derived_snapshot_f90_wrapper.c").read_text(encoding="utf-8")
    bridge_source = (build_dir / "bind_c_fmodule_derived_snapshot_f90_wrapper.f90").read_text(encoding="utf-8")
    assert "class Snapshot:" in wrapper_source_text
    assert "class box_snapshot(Snapshot):" in wrapper_source_text
    assert "c_loc(current)" not in bridge_source
