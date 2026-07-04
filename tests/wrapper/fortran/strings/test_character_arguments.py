"""Legacy and modern scalar character argument/result tests."""

from pathlib import Path

from tests.wrapper.fortran._support import (
    _build_source_or_generated_pyi_and_import,
    _normalized_fortran_source,
    _assert_legacy_string_examples,
    _assert_modern_string_examples,
    wrapper_source,
)

STRING_LEGACY_SOURCE = wrapper_source("fstrings.f")
STRING_F90_SOURCE = wrapper_source("fstrings_f90.f90")
CONTRACT_FIXTURES = Path(__file__).parent / "contracts"


def test_legacy_fortran_character_arguments_and_results(pyi_parity_build_mode: str, tmp_path: Path):
    module = _build_source_or_generated_pyi_and_import(
        STRING_LEGACY_SOURCE,
        tmp_path,
        {
            "bind_c_fstrings_wrapper.f90",
            "fstrings_wrapper.c",
            "fstrings_wrapper.h",
        },
        CONTRACT_FIXTURES / "fstrings",
        pyi_parity_build_mode,
    )

    if pyi_parity_build_mode == "source":
        bind_c_source = _normalized_fortran_source(tmp_path / "source_build" / "bind_c_fstrings_wrapper.f90")
        assert "C = transfer(C_0001, C)" in bind_c_source
        assert "C = transfer(C_0001, C) C_fixed = C" not in bind_c_source
        assert (
            "CHAR_RESULT_DEFAULT_ptr = transfer("
            "CHAR_RESULT_DEFAULT_0001, CHAR_RESULT_DEFAULT_ptr, CHAR_RESULT_DEFAULT_len)"
        ) in bind_c_source
        assert "do Dummy_" not in bind_c_source

    _assert_legacy_string_examples(module)


def test_modern_fortran_character_arguments_and_results(pyi_parity_build_mode: str, tmp_path: Path):
    module = _build_source_or_generated_pyi_and_import(
        STRING_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fstrings_f90_wrapper.f90",
            "fstrings_f90_wrapper.c",
            "fstrings_f90_wrapper.h",
        },
        CONTRACT_FIXTURES / "fstrings_f90",
        pyi_parity_build_mode,
    )

    _assert_modern_string_examples(module)
