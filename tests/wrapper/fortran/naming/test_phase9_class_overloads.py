"""Direct-plan Phase 9 class overload and constructor parity."""

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

SOURCE = wrapper_source("foverloads_f90.f90")
CONTRACT = Path(__file__).parent / "contracts" / "fclass_overloads_phase9" / "__init__.pyi"
CONSTRUCTOR_CONTRACT = Path(__file__).parent / "contracts" / "fconstructor_overloads_phase9" / "__init__.pyi"


@pytest.fixture(scope="module")
def class_overloads(tmp_path_factory):
    """Build the reduced edited contract through the canonical plan."""
    root = tmp_path_factory.mktemp("phase9_class_overloads")
    native_object = _compile_native_object(SOURCE, root / "native")
    result = build_pyi_extension(
        CONTRACT,
        native_objects=[native_object],
        native_include_dirs=[native_object.parent],
        output_dir=root / "build",
    )
    package = _import_from_build_dir(result.module_name, result.output_dir)
    return _sole_native_module(package)


@pytest.fixture(scope="module")
def constructor_overloads(tmp_path_factory):
    """Build the constructor-overload improvement through the direct plan."""
    root = tmp_path_factory.mktemp("phase9_constructor_overloads")
    native_object = _compile_native_object(SOURCE, root / "native")
    result = build_pyi_extension(
        CONSTRUCTOR_CONTRACT,
        native_objects=[native_object],
        native_include_dirs=[native_object.parent],
        output_dir=root / "wrapper_plan",
    )
    package = _import_from_build_dir(result.module_name, result.output_dir)
    return _sole_native_module(package)


def test_exact_method_overloads_match_without_trial_calls(class_overloads):
    module = class_overloads
    assert "add(*args, **kwargs)" in module.accumulator.add.__doc__
    assert "add(value: int32) -> None" in module.accumulator.add.__doc__
    assert "add(value: float64) -> None" in module.accumulator.add.__doc__
    assert "Dispatches to a native operation on the wrapped instance." in module.accumulator.add.__doc__
    assert "accumulator_add_" not in module.accumulator.add.__doc__

    value = module.accumulator()
    value.add(np.int32(2))
    value.add(np.float64(0.5))
    assert value.total == np.float64(2.5)

    with pytest.raises(TypeError, match="no matching overload for add"):
        value.add(np.complex128(1.0 + 0.0j))


def test_constructor_overloads_share_owned_allocation_and_exact_matching(constructor_overloads):
    module = constructor_overloads
    assert "accumulator(*args, **kwargs) -> accumulator" in module.accumulator.__init__.__doc__
    assert "accumulator(value: int32) -> accumulator" in module.accumulator.__init__.__doc__
    assert "accumulator(value: float64) -> accumulator" in module.accumulator.__init__.__doc__
    assert "accumulator_add_" not in module.accumulator.__init__.__doc__

    integer = module.accumulator(np.int32(3))
    real = module.accumulator(np.float64(1.25))
    assert integer.total == np.float64(3.0)
    assert real.total == np.float64(1.25)

    with pytest.raises(TypeError, match="no matching overload for __init__"):
        module.accumulator("wrong")
