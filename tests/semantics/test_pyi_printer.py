from x2py import parse_fortran_file as parse_fortran_source

from semantics.fortran2ir import (
    fortran_module_to_semantic_module,
)

from semantics.pyi_printer import (
    emit_module,
    PyiPrinter,
)
from semantics.models import (
    SemanticClass,
    SemanticMethod,
    SemanticModule,
)


# ============================================================
# Helpers
# ============================================================

def generate_pyi(source: str) -> str:

    fmod = parse_fortran_source(source)

    smod = fortran_module_to_semantic_module(fmod)

    return emit_module(smod)


def normalize(text: str) -> str:

    return "\n".join(
        line.rstrip()
        for line in text.strip().splitlines()
    )


# ============================================================
# Basic scalar function
# ============================================================

def test_emit_basic_scalar_function():

    source = """
module math_mod

contains

subroutine add(a, b, c)

    real(8), intent(in) :: a
    real(8), intent(in) :: b
    real(8), intent(out) :: c

end subroutine

end module
"""

    code = generate_pyi(source)

    assert "def add(" in code

    assert "a: Float64" in code
    assert "b: Float64" in code
    assert "-> Float64" in code
    assert 'Returns["c", Float64]' not in code

    assert "-> None" not in code


def test_emit_no_argument_subroutine_is_single_line_signature():
    source = """
module no_arg_mod

contains

subroutine ping()
end subroutine

end module
"""

    code = generate_pyi(source)

    assert "def ping() -> None: ..." in code
    assert "def ping(\n    \n)" not in code


# ============================================================
# Array annotations
# ============================================================

def test_emit_array_constraints():

    source = """
module array_mod

contains

subroutine scale(x)

    real(8), intent(inout) :: x(:)

end subroutine

end module
"""

    code = generate_pyi(source)

    assert "def scale(" in code

    assert "Float64[" in code

    assert "Shape" in code

    assert "FortranContiguous" in code


# ============================================================
# Matrix shapes
# ============================================================

def test_emit_matrix_shapes():

    source = """
module matrix_mod

contains

subroutine matvec(A, x, y)

    real(8), intent(in) :: A(:, :)
    real(8), intent(in) :: x(:)
    real(8), intent(out) :: y(:)

end subroutine

end module
"""

    code = generate_pyi(source)

    assert "A: Float64[" in code

    assert "Shape(':', ':')" in code

    assert "x: Float64[" in code

    assert "-> Float64[" in code
    assert 'Returns["y", Float64[' not in code


# ============================================================
# Optional arguments
# ============================================================

def test_emit_optional_argument():

    source = """
module opt_mod

contains

subroutine solve(A, tol)

    real(8), intent(in) :: A(:, :)
    real(8), intent(in), optional :: tol

end subroutine

end module
"""

    code = generate_pyi(source)

    assert "tol:" in code

    assert "= ..." in code


# ============================================================
# Allocatable constraint
# ============================================================

def test_emit_allocatable():

    source = """
module alloc_mod

contains

subroutine build(x)

    real(8), allocatable, intent(out) :: x(:)

end subroutine

end module
"""

    code = generate_pyi(source)

    assert "Allocatable" in code


# ============================================================
# Derived type emission
# ============================================================

def test_emit_class():

    source = """
module sparse_mod

type :: sparse_matrix

    integer :: nrows
    integer :: ncols

end type

end module
"""

    code = generate_pyi(source)

    assert "class sparse_matrix" in code


# ============================================================
# Derived type inheritance
# ============================================================

def test_emit_inheritance():

    source = """
module inheritance_mod

type :: base_matrix
end type

type, extends(base_matrix) :: sparse_matrix
end type

end module
"""

    code = generate_pyi(source)

    assert "class sparse_matrix(base_matrix)" in code


# ============================================================
# Function result
# ============================================================

def test_emit_function_result():

    source = """
module func_mod

contains

function norm2(x) result(r)

    real(8), intent(in) :: x(:)

    real(8) :: r

end function

end module
"""

    code = generate_pyi(source)

    assert "def norm2(" in code

    assert "-> Float64" in code


# ============================================================
# Explicit shape emission
# ============================================================

def test_emit_explicit_shape():

    source = """
module shape_mod

contains

subroutine foo(A)

    real(8), intent(in) :: A(10, 20)

end subroutine

end module
"""

    code = generate_pyi(source)

    assert "Shape('10', '20')" in code


# ============================================================
# Imports
# ============================================================

def test_emit_imports():

    source = """
module user_mod

use iso_c_binding

contains

subroutine foo(x)

    integer, intent(in) :: x

end subroutine

end module
"""

    code = generate_pyi(source)

    assert "import iso_c_binding" in code


# ============================================================
# Multiple procedures
# ============================================================

def test_emit_multiple_functions():

    source = """
module multi_mod

contains

subroutine foo(x)

    integer, intent(in) :: x

end subroutine

subroutine bar(y)

    real(8), intent(in) :: y

end subroutine

end module
"""

    code = generate_pyi(source)

    assert "def foo(" in code

    assert "def bar(" in code


# ============================================================
# Complex FEM example
# ============================================================

def test_emit_complex_fem_module():

    source = """
module fem_mod

type :: mesh

    integer :: nelements
    integer :: nnodes

end type

contains

subroutine assemble(K, coords, connectivity)

    real(8), intent(out) :: K(:, :)

    real(8), intent(in) :: coords(:, :)

    integer, intent(in) :: connectivity(:, :)

end subroutine

function compute_norm(x) result(r)

    real(8), intent(in) :: x(:)

    real(8) :: r

end function

end module
"""

    code = generate_pyi(source)

    # --------------------------------------------------------
    # Class
    # --------------------------------------------------------

    assert "class mesh" in code

    # --------------------------------------------------------
    # Procedures
    # --------------------------------------------------------

    assert "def assemble(" in code

    assert "def compute_norm(" in code

    # --------------------------------------------------------
    # Matrix annotations
    # --------------------------------------------------------

    assert "-> Float64[" in code
    assert 'Returns["K", Float64[' not in code

    assert "coords: Float64[" in code

    assert "connectivity: Int32[" in code

    # --------------------------------------------------------
    # Return type
    # --------------------------------------------------------

    assert "-> Float64" in code


# ============================================================
# Golden test
# ============================================================

def test_emit_exact_output():

    source = """
module simple_mod

contains

subroutine scale(x)

    real(8), intent(inout) :: x(:)

end subroutine

end module
"""

    code = normalize(generate_pyi(source))

    expected = normalize(
        '''
def scale(
    x: Float64[Shape(':'), FortranContiguous]
) -> Returns["x", Float64[Shape(':'), FortranContiguous]]: ...
'''
    )

    assert expected in code


def test_roundtrip_mode_keeps_output_argument_name():
    source = """
module output_name_mod

contains

subroutine add(a, b, c)

    real(8), intent(in) :: a
    real(8), intent(in) :: b
    real(8), intent(out) :: c

end subroutine

end module
"""

    fmod = parse_fortran_source(source)
    smod = fortran_module_to_semantic_module(fmod)

    code = PyiPrinter(roundtrip=True).emit_module(smod)

    assert 'Returns["c", Float64]' in code


# ============================================================
# Empty module
# ============================================================

def test_emit_empty_module():

    source = """
module empty_mod
end module
"""

    code = generate_pyi(source)

    assert isinstance(code, str)


# ============================================================
# Stability test
# ============================================================

def test_emit_is_deterministic():

    source = """
module stable_mod

contains

subroutine foo(x)

    integer, intent(in) :: x

end subroutine

end module
"""

    code1 = generate_pyi(source)

    code2 = generate_pyi(source)

    assert code1 == code2


def test_printer_class_entrypoint():

    source = """
module class_print_mod

contains

subroutine touch(x)

    integer, intent(inout) :: x

end subroutine

end module
"""

    fmod = parse_fortran_source(source)

    smod = fortran_module_to_semantic_module(fmod)

    code = PyiPrinter().emit_module(smod)

    assert "def touch(" in code
    assert "x: Int32" in code


def test_emit_class_method_keeps_method_indentation():
    module = SemanticModule(
        name="method_mod",
        classes=[
            SemanticClass(
                name="thing",
                methods=[SemanticMethod(name="reset")],
            )
        ],
    )

    code = emit_module(module)

    assert "class thing:\n    def reset(self) -> None: ..." in code


def test_emit_module_variables_with_visibility():
    source = """
module state_mod
  implicit none
  private
  public :: counter
  integer :: counter
  real(8) :: hidden_scale
contains
  subroutine ping(x)
    integer, intent(in) :: x
  end subroutine
end module
"""
    code = generate_pyi(source)
    assert "counter: Int32" in code
    assert "hidden_scale: private[Float64]" in code
