"""Direct Phase 9 proof for explicit constructor bindings."""

from pathlib import Path

import numpy as np
from tests.wrapper.fortran._support import (
    _compile_native_object,
    _import_from_build_dir,
    _sole_native_module,
    wrapper_source,
)
from x2py import build_pyi_extension

SOURCE = wrapper_source("fclasses_f90.f90")
CONTRACT = Path(__file__).parent / "contracts" / "fbound_constructor_phase9" / "__init__.pyi"


def test_bound_constructor_replaces_field_initialization_and_reuses_method_plan(
    tmp_path: Path,
):
    native_object = _compile_native_object(SOURCE, tmp_path / "native")
    result = build_pyi_extension(
        CONTRACT,
        native_objects=[native_object],
        native_include_dirs=[native_object.parent],
        output_dir=tmp_path / "wrapper_plan",
    )
    module = _sole_native_module(_import_from_build_dir(result.module_name, result.output_dir))

    assert "_x2py_class_" not in module.__doc__
    assert "Constructor\n-----------\nvector(dx, dy) -> vector" in module.vector.__doc__
    assert "Fields\n------\nx : float64\ny : float64" in module.vector.__doc__
    assert "Methods\n-------\nshift(dx, dy) -> None" in module.vector.__doc__
    assert "vector(dx, dy) -> vector" in module.vector.__init__.__doc__
    assert "dx : float64" in module.vector.__init__.__doc__
    assert "shift(dx, dy) -> None" in module.vector.shift.__doc__
    assert "Updates the wrapped native instance in place." in module.vector.shift.__doc__
    assert "owner" not in module.vector.shift.__doc__
    assert "Assignment writes through to native storage." in module.vector.x.__doc__

    value = module.vector(np.float64(2.0), np.float64(3.0))
    assert (value.x, value.y) == (np.float64(2.0), np.float64(3.0))
    value.shift(np.float64(1.0), np.float64(-1.0))
    assert (value.x, value.y) == (np.float64(3.0), np.float64(2.0))
