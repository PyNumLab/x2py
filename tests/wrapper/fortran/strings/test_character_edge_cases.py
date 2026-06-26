"""Character copy-in/copy-out, length, Unicode, and NUL tests."""

from pathlib import Path

import pytest

from tests.wrapper.fortran._support import _build_source_or_generated_pyi_and_import, wrapper_source

CHARACTER_EDGES_F90_SOURCE = wrapper_source("fcharacter_edges_f90.f90")
CONTRACT_FIXTURES = Path(__file__).parent / "contracts"


def test_fortran_character_edge_cases_follow_copy_in_copy_out_policy(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _build_source_or_generated_pyi_and_import(
        CHARACTER_EDGES_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fcharacter_edges_f90_wrapper.f90",
            "fcharacter_edges_f90_wrapper.c",
            "fcharacter_edges_f90_wrapper.h",
        },
        CONTRACT_FIXTURES / "fcharacter_edges_f90",
        pyi_parity_build_mode,
    )

    original = "abc"
    assert module.fixed_inout(original) == "Zbc    !"
    assert original == "abc"
    assert module.fixed_inout("abcdefgh") == "Zbcdefg!"
    assert module.fixed_inout("abcdefghi") == "Zbcdefg!"
    assert module.assumed_inout("abc") == "Qbc"
    assert module.assumed_inout("") == ""
    assert module.optional_inout() is None
    assert module.optional_inout(None) is None
    assert module.optional_inout("abc") == "Pbc"
    assert module.make_out() == "go    "
    assert module.unicode_echo("café") == "café"

    with pytest.raises(TypeError, match="embedded NUL"):
        module.assumed_inout("a\0b")
    with pytest.raises(TypeError, match="embedded NUL"):
        module.unicode_echo("a\0b")
