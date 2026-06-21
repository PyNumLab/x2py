"""Verified baseline runtime wrapper tests."""

from pathlib import Path


from tests.wrapper.fortran._support import (
    _assert_fmath_examples,
    _build_and_import,
    _assert_fmath_array_examples,
    _assert_array_rejects_strided_views,
)

SCALAR_LEGACY_SOURCE = Path(__file__).with_name("fmath.f")
ARRAY_LEGACY_SOURCE = Path(__file__).with_name("fmath_arrays.f")
SCALAR_F90_SOURCE = Path(__file__).with_name("fmath_f90.f90")
ARRAY_F90_SOURCE = Path(__file__).with_name("fmath_arrays_f90.f90")


def test_fortran_wrapper_pipeline_builds_importable_extension(tmp_path: Path):
    module = _build_and_import(
        SCALAR_LEGACY_SOURCE,
        tmp_path,
        {
            "bind_c_fmath_wrapper.f90",
            "fmath_wrapper.c",
            "fmath_wrapper.h",
        },
    )

    _assert_fmath_examples(module)


def test_f90_wrapper_pipeline_builds_importable_extension(tmp_path: Path):
    module = _build_and_import(
        SCALAR_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fmath_f90_wrapper.f90",
            "fmath_f90_wrapper.c",
            "fmath_f90_wrapper.h",
        },
    )

    _assert_fmath_examples(module)


def test_fortran_array_wrapper_pipeline_matches_fmath_results_with_contiguous_arrays(tmp_path: Path):
    module = _build_and_import(
        ARRAY_LEGACY_SOURCE,
        tmp_path,
        {
            "bind_c_fmath_arrays_wrapper.f90",
            "fmath_arrays_wrapper.c",
            "fmath_arrays_wrapper.h",
        },
    )

    _assert_fmath_array_examples(module, strided=False)
    _assert_array_rejects_strided_views(module, "SQUARE_R4")


def test_f90_array_wrapper_distinguishes_contiguous_and_strided_contracts(tmp_path: Path):
    module = _build_and_import(
        ARRAY_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fmath_arrays_f90_wrapper.f90",
            "fmath_arrays_f90_wrapper.c",
            "fmath_arrays_f90_wrapper.h",
        },
    )

    _assert_fmath_array_examples(module, suffix="_CONTIGUOUS", strided=False)
    _assert_array_rejects_strided_views(module, "SQUARE_R4_CONTIGUOUS")
    _assert_fmath_array_examples(module, suffix="_STRIDED", strided=True)
