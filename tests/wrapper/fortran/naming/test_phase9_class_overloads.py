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
    """Build the same reduced edited contract through both wrapper routes."""
    root = tmp_path_factory.mktemp("phase9_class_overloads")
    native_object = _compile_native_object(SOURCE, root / "native")
    modules = {}
    for route, kwargs in (
        ("legacy", {"_force_legacy_wrapper_route": True}),
        ("wrapper_plan", {"_force_wrapper_plan_route": True}),
    ):
        result = build_pyi_extension(
            CONTRACT,
            native_objects=[native_object],
            native_include_dirs=[native_object.parent],
            output_dir=root / route,
            **kwargs,
        )
        package = _import_from_build_dir(result.module_name, result.output_dir)
        modules[route] = _sole_native_module(package)
    return modules


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
        _force_wrapper_plan_route=True,
    )
    package = _import_from_build_dir(result.module_name, result.output_dir)
    return _sole_native_module(package)


@pytest.mark.parametrize("route", ("legacy", "wrapper_plan"))
def test_exact_method_overloads_match_without_trial_calls(class_overloads, route: str):
    module = class_overloads[route]
    value = module.accumulator()
    value.add(np.int32(2))
    value.add(np.float64(0.5))
    assert value.total == np.float64(2.5)

    with pytest.raises(TypeError) as exc_info:
        value.add(np.complex128(1.0 + 0.0j))
    if route == "wrapper_plan":
        assert "no matching overload for add" in str(exc_info.value)


def test_constructor_overloads_share_owned_allocation_and_exact_matching(constructor_overloads):
    module = constructor_overloads
    integer = module.accumulator(np.int32(3))
    real = module.accumulator(np.float64(1.25))
    assert integer.total == np.float64(3.0)
    assert real.total == np.float64(1.25)

    with pytest.raises(TypeError, match="no matching overload for __init__"):
        module.accumulator("wrong")
