"""Character copy-in/copy-out, length, Unicode, and NUL tests."""

import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from tests.wrapper.fortran._support import (
    _build_source_or_generated_pyi_and_import,
    _build_text_and_import,
    _compile_native_object,
    _import_from_build_dir,
    _sole_native_module,
    wrapper_source,
)
from x2py import build_pyi_extension

CHARACTER_EDGES_F90_SOURCE = wrapper_source("fcharacter_edges_f90.f90")
CONTRACT_FIXTURES = Path(__file__).parent / "contracts"
CHARACTER_ARRAY_BYTES_SOURCE = """
module fcharacter_array_bytes_f90
contains
  subroutine replace_names(names)
    character(len=:), allocatable, intent(inout) :: names(:)
    integer :: n

    if (allocated(names)) then
      n = size(names)
    else
      n = 2
    end if

    if (allocated(names)) deallocate(names)
    allocate(character(len=5) :: names(n))
    names = '     '
    if (n >= 1) names(1) = 'red'
    if (n >= 2) names(2) = 'blue'
  end subroutine replace_names
end module fcharacter_array_bytes_f90
"""


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

    original = "abc     "
    assert module.fixed_inout(original) == "Zbc    !"
    assert original == "abc     "
    with pytest.raises(TypeError, match="exactly 8 bytes"):
        module.fixed_inout("abc")
    assert module.fixed_inout("abcdefgh") == "Zbcdefg!"
    with pytest.raises(TypeError, match="exactly 8 bytes"):
        module.fixed_inout("abcdefghi")
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


def test_allocatable_character_array_replacement_returns_fixed_width_bytes(tmp_path: Path):
    module = _build_text_and_import(
        CHARACTER_ARRAY_BYTES_SOURCE,
        "fcharacter_array_bytes_f90.f90",
        tmp_path,
        {
            "bind_c_fcharacter_array_bytes_f90_wrapper.f90",
            "fcharacter_array_bytes_f90_wrapper.c",
            "fcharacter_array_bytes_f90_wrapper.h",
        },
    )

    original = np.array([b"aa", b"bbb"], dtype="S3")
    replacement = module.replace_names(original)

    assert original.tolist() == [b"aa", b"bbb"]
    assert replacement.dtype == np.dtype("S5")
    assert replacement.tolist() == [b"red  ", b"blue "]


def test_allocatable_character_array_generated_pyi_build_returns_fixed_width_bytes(tmp_path: Path):
    source = tmp_path / "fcharacter_array_bytes_f90.f90"
    source.write_text(CHARACTER_ARRAY_BYTES_SOURCE, encoding="utf-8")
    pyi_dir = tmp_path / "contracts"
    subprocess.run(
        [sys.executable, "-m", "x2py", str(source), "--pyi", "--out", str(pyi_dir)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Allocatable[String[:][:]]" in (pyi_dir / "fcharacter_array_bytes_f90.pyi").read_text(encoding="utf-8")
    native_object = _compile_native_object(source, tmp_path / "native")
    result = build_pyi_extension(
        pyi_dir / "__init__.pyi",
        native_objects=[native_object],
        native_include_dirs=[native_object.parent],
        output_dir=tmp_path / "pyi_build",
    )

    module = _sole_native_module(_import_from_build_dir(result.module_name, result.output_dir))
    replacement = module.replace_names(np.array([b"aa", b"bbb"], dtype="S3"))

    assert replacement.dtype == np.dtype("S5")
    assert replacement.tolist() == [b"red  ", b"blue "]
