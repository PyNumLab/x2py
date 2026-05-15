from pathlib import Path

from fortran_parser import parse_fortran_file
from semantics.fortran2ir import fortran_module_to_semantic_module
from semantics.pyi_printer import emit_module


def test_modern_fortran_example_pyi_snapshot():
    fixture = Path(__file__).parent / "fixtures" / "modern_pyi_example.f90"
    source = fixture.read_text(encoding="utf-8")

    parsed = parse_fortran_file(source, filename=str(fixture.name))
    modules = [fortran_module_to_semantic_module(m) for m in parsed.modules]
    pyi = "\n\n".join(emit_module(m) for m in modules).strip()

    expected = """class particle:
    id: Int32
    mass: Float64
    position: Float64[Shape('3'), FortranContiguous]

def init_particle(
    p: particle,
    pid: Int32,
    mass: Float64,
    x: Float64,
    y: Float64,
    z: Float64
) -> None: ...

def kinetic_energy(
    p: particle,
    vx: Float64,
    vy: Float64,
    vz: Float64
) -> Float64: ...

def scale_vector(
    v: Float64[Shape(':'), FortranContiguous],
    alpha: Float64
) -> None: ...

def dot3(
    a: Float64[Shape('3'), FortranContiguous],
    b: Float64[Shape('3'), FortranContiguous]
) -> Float64: ...

def fill_identity3(
    a: Float64[Shape('3', '3'), FortranContiguous]
) -> None: ...""".strip()

    assert pyi == expected


def test_pyi_visibility_private_public_markers():
    source = """
module visibility_mod
  implicit none
  private
  public :: pub_proc, visible_t

  type :: visible_t
     integer :: a
     integer :: b
  end type visible_t

  type :: hidden_t
     integer :: z
  end type hidden_t

contains
  subroutine pub_proc(x)
    integer, intent(in) :: x
  end subroutine pub_proc

  subroutine hidden_proc(x)
    integer, intent(in) :: x
  end subroutine hidden_proc
end module visibility_mod
"""
    parsed = parse_fortran_file(source, filename="visibility_mod.f90")
    pyi = emit_module(fortran_module_to_semantic_module(parsed.modules[0])).strip()

    assert "a: Int32" in pyi
    assert "b: Int32" in pyi
    assert "@private\nclass hidden_t:" in pyi
    assert "def pub_proc(" in pyi
    assert "@private\ndef hidden_proc(" in pyi
