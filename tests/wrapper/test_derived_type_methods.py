"""Derived-type field and type-bound method wrapper tests."""

from pathlib import Path

from tests.wrapper._support import _assert_modern_class_examples, _build_and_import

CLASS_F90_SOURCE = Path(__file__).with_name("fclasses_f90.f90")


def test_modern_fortran_derived_type_exposes_class_and_type_bound_methods(tmp_path: Path):
    module = _build_and_import(
        CLASS_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fclasses_f90_wrapper.f90",
            "fclasses_f90_wrapper.c",
            "fclasses_f90_wrapper.h",
        },
    )

    _assert_modern_class_examples(module)
