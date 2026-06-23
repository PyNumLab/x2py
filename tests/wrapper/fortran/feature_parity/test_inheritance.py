"""Inheritance and polymorphism runtime wrapper tests."""

from pathlib import Path

import numpy as np

from tests.wrapper.fortran._support import (
    wrapper_source,
    _build_text_and_import,
)

INHERITANCE_F90_TEXT = wrapper_source("finheritance_f90.f90").read_text(encoding="utf-8")


def test_fortran_extension_types_generate_python_inheritance(tmp_path: Path):
    module = _build_text_and_import(
        INHERITANCE_F90_TEXT,
        "finheritance_f90.f90",
        tmp_path,
        {
            "bind_c_finheritance_f90_wrapper.f90",
            "finheritance_f90_wrapper.c",
            "finheritance_f90_wrapper.h",
        },
    )

    assert issubclass(module.circle, module.base_shape)
    assert issubclass(module.box, module.base_shape)

    base = module.base_shape()
    base.size = np.float64(3.0)
    assert base.area() == np.float64(3.0)
    assert module.describe_shape(base) == np.float64(3.0)

    circle = module.circle()
    assert isinstance(circle, module.base_shape)
    circle.set_size(np.float64(5.0))
    circle.radius = np.float64(2.0)
    assert circle.size == np.float64(5.0)
    assert circle.area() == np.float64(9.0)
    assert module.describe_shape(circle) == np.float64(9.0)

    module.base_shape.set_size(circle, np.float64(7.0))
    assert circle.size == np.float64(7.0)

    box = module.box()
    assert isinstance(box, module.base_shape)
    box.set_size(np.float64(2.0))
    box.width = np.float64(3.0)
    assert box.area() == np.float64(32.0)
    assert module.describe_shape(box) == np.float64(32.0)
