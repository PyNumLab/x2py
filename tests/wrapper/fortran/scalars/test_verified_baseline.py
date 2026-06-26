"""Verified baseline runtime wrapper tests."""

from pathlib import Path


from tests.wrapper.fortran._support import (
    _assert_array_rejects_strided_views,
    _assert_fmath_array_examples,
    _assert_fmath_examples,
    _build_source_or_generated_pyi_and_import,
    wrapper_source,
)

CONTRACT_FIXTURES = Path(__file__).parent / "contracts"
SCALAR_LEGACY_SOURCE = wrapper_source("fmath.f")
ARRAY_LEGACY_SOURCE = wrapper_source("fmath_arrays.f")
SCALAR_F90_SOURCE = wrapper_source("fmath_f90.f90")
ARRAY_F90_SOURCE = wrapper_source("fmath_arrays_f90.f90")


def test_fortran_wrapper_pipeline_builds_importable_extension(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _build_source_or_generated_pyi_and_import(
        SCALAR_LEGACY_SOURCE,
        tmp_path,
        {
            "bind_c_fmath_wrapper.f90",
            "fmath_wrapper.c",
            "fmath_wrapper.h",
        },
        CONTRACT_FIXTURES / "fmath",
        pyi_parity_build_mode,
    )

    _assert_fmath_examples(module)


def test_f90_wrapper_pipeline_builds_importable_extension(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _build_source_or_generated_pyi_and_import(
        SCALAR_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fmath_f90_wrapper.f90",
            "fmath_f90_wrapper.c",
            "fmath_f90_wrapper.h",
        },
        CONTRACT_FIXTURES / "fmath_f90",
        pyi_parity_build_mode,
    )

    _assert_fmath_examples(module)


def test_fortran_array_wrapper_pipeline_matches_fmath_results_with_contiguous_arrays(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _build_source_or_generated_pyi_and_import(
        ARRAY_LEGACY_SOURCE,
        tmp_path,
        {
            "bind_c_fmath_arrays_wrapper.f90",
            "fmath_arrays_wrapper.c",
            "fmath_arrays_wrapper.h",
        },
        CONTRACT_FIXTURES / "fmath_arrays",
        pyi_parity_build_mode,
    )

    _assert_fmath_array_examples(module, strided=False)
    _assert_array_rejects_strided_views(module, "SQUARE_R4")


def test_f90_array_wrapper_distinguishes_contiguous_and_strided_contracts(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _build_source_or_generated_pyi_and_import(
        ARRAY_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fmath_arrays_f90_wrapper.f90",
            "fmath_arrays_f90_wrapper.c",
            "fmath_arrays_f90_wrapper.h",
        },
        CONTRACT_FIXTURES / "fmath_arrays_f90",
        pyi_parity_build_mode,
    )

    _assert_fmath_array_examples(module, suffix="_CONTIGUOUS", strided=False)
    _assert_array_rejects_strided_views(module, "SQUARE_R4_CONTIGUOUS")
    _assert_fmath_array_examples(module, suffix="_STRIDED", strided=True)
