"""Verified baseline runtime wrapper tests."""

from pathlib import Path

import numpy as np
import pytest

from tests.wrapper.fortran._support import (
    _assert_array_rejects_strided_views,
    _assert_fmath_array_examples,
    _assert_fmath_examples,
    _build_source_legacy_and_import,
    _build_source_or_generated_pyi_and_import,
    _build_source_wrapper_plan_and_import,
    wrapper_source,
)

CONTRACT_FIXTURES = Path(__file__).parent / "contracts"
SCALAR_FIXED_SOURCE = wrapper_source("fmath.f")
ARRAY_FIXED_SOURCE = wrapper_source("fmath_arrays.f")
SCALAR_F90_SOURCE = wrapper_source("fmath_f90.f90")
ARRAY_F90_SOURCE = wrapper_source("fmath_arrays_f90.f90")


def test_fortran_wrapper_pipeline_builds_importable_extension(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _build_source_or_generated_pyi_and_import(
        SCALAR_FIXED_SOURCE,
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


@pytest.mark.parametrize(
    "source",
    [SCALAR_FIXED_SOURCE, SCALAR_F90_SOURCE],
    ids=["fixed-form-externals", "free-form-module"],
)
def test_fmath_scalar_sources_match_legacy_and_wrapper_plan_routes(
    tmp_path: Path,
    source: Path,
):
    expected_generated_sources = {
        f"bind_c_{source.stem}_wrapper.f90",
        f"{source.stem}_wrapper.c",
        f"{source.stem}_wrapper.h",
    }
    legacy_module = _build_source_legacy_and_import(
        source,
        tmp_path / "legacy",
        expected_generated_sources,
    )
    wrapper_plan_root, wrapper_plan_result = _build_source_wrapper_plan_and_import(
        source,
        tmp_path / "wrapper_plan",
        unwrap_namespace=False,
    )

    if source == SCALAR_F90_SOURCE:
        assert not hasattr(wrapper_plan_root, "add_r8")
        assert hasattr(wrapper_plan_root, "fmath_f90")
        wrapper_plan_module = wrapper_plan_root.fmath_f90
    else:
        assert hasattr(wrapper_plan_root, "add_r8")
        wrapper_plan_module = wrapper_plan_root

    assert {path.name for path in wrapper_plan_result.generated_sources} == expected_generated_sources
    assert any(path.name == f"{source.stem}_wrapper.h" for path in wrapper_plan_result.generated_files)
    assert any(
        path.name == "python_runtime.c" and path.parent.name == "x2py_runtime"
        for path in wrapper_plan_result.generated_files
    )
    assert wrapper_plan_result.compiled is True
    assert wrapper_plan_result.shared_library.exists()

    _assert_fmath_examples(legacy_module)
    _assert_fmath_examples(wrapper_plan_module)

    legacy_failure = _scalar_conversion_failure(legacy_module)
    wrapper_plan_failure = _scalar_conversion_failure(wrapper_plan_module)
    assert wrapper_plan_failure == legacy_failure


def _scalar_conversion_failure(module) -> tuple[type[BaseException], str]:
    with pytest.raises(TypeError) as error_info:
        module.add_r8("not-a-real", np.float64(1.0))

    np.testing.assert_allclose(module.add_r8(np.float64(1.5), np.float64(2.25)), np.float64(3.75))
    return type(error_info.value), str(error_info.value)


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
        ARRAY_FIXED_SOURCE,
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
