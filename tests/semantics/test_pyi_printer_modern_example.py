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
    pass

def init_particle(
    p: Unknown,
    pid: Int32,
    mass: Float64,
    x: Float64,
    y: Float64,
    z: Float64
) -> None: ...

def kinetic_energy(
    p: Unknown,
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
