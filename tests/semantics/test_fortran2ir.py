import json
from dataclasses import asdict

from x2py import parse_fortran_file as parse_fortran_source

from semantics.fortran2ir import (
    fortran_file_to_semantic_modules,
    fortran_module_to_semantic_module,
)

from semantics.models import (
    ProjectionMapping,
    SemanticArgument,
    SemanticModule,
    SemanticClass,
    SemanticFunction,
    SemanticConstraint,
    SemanticType,
)


# ============================================================
# Helpers
# ============================================================

def get_function(module: SemanticModule, name: str) -> SemanticFunction:

    for f in module.functions:
        if f.name == name:
            return f

    raise AssertionError(f"Function '{name}' not found")


def get_class(module: SemanticModule, name: str) -> SemanticClass:

    for c in module.classes:
        if c.name == name:
            return c

    raise AssertionError(f"Class '{name}' not found")


def has_constraint(obj, name: str) -> bool:

    return any(c.name == name for c in obj.constraints)


# ============================================================
# Basic scalar test
# ============================================================

def test_basic_scalar_arguments():

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

    fmod = parse_fortran_source(source)

    smod = fortran_module_to_semantic_module(fmod)

    assert smod.name == "math_mod"

    func = get_function(smod, "add")

    assert len(func.arguments) == 3

    a = func.arguments[0]
    b = func.arguments[1]
    c = func.arguments[2]

    assert a.name == "a"
    assert a.intent == "in"

    assert a.semantic_type.name == "Float64"
    assert a.semantic_type.rank == 0

    assert c.intent == "out"

    assert c.semantic_type.ownership.mutable is True


# ============================================================
# Array semantics test
# ============================================================

def test_array_constraints():

    source = """
module array_mod

contains

subroutine scale(x)

    real(8), intent(inout) :: x(:)

end subroutine

end module
"""

    fmod = parse_fortran_source(source)

    smod = fortran_module_to_semantic_module(fmod)

    func = get_function(smod, "scale")

    x = func.arguments[0]

    assert x.semantic_type.name == "Float64"

    assert x.semantic_type.rank == 1

    assert has_constraint(
        x.semantic_type,
        "Shape",
    )

    assert has_constraint(
        x.semantic_type,
        "ORDER_F",
    )

    assert x.semantic_type.shape == [":"]


# ============================================================
# Multi-dimensional array test
# ============================================================

def test_matrix_semantics():

    source = """
module linalg_mod

contains

subroutine matvec(A, x, y)

    real(8), intent(in) :: A(:, :)
    real(8), intent(in) :: x(:)
    real(8), intent(out) :: y(:)

end subroutine

end module
"""

    fmod = parse_fortran_source(source)

    smod = fortran_module_to_semantic_module(fmod)

    func = get_function(smod, "matvec")

    A = func.arguments[0]

    assert A.semantic_type.rank == 2

    assert A.semantic_type.shape == [":", ":"]

    assert has_constraint(
        A.semantic_type,
        "Shape",
    )

    assert has_constraint(
        A.semantic_type,
        "ORDER_F",
    )


# ============================================================
# Optional arguments
# ============================================================

def test_optional_argument():

    source = """
module opt_mod

contains

subroutine solve(A, tol)

    real(8), intent(in) :: A(:, :)
    real(8), intent(in), optional :: tol

end subroutine

end module
"""

    fmod = parse_fortran_source(source)

    smod = fortran_module_to_semantic_module(fmod)

    func = get_function(smod, "solve")

    tol = func.arguments[1]

    assert tol.optional is True


# ============================================================
# Allocatable + pointer semantics
# ============================================================

def test_allocatable_pointer():

    source = """
module alloc_mod

contains

subroutine build(x)

    real(8), allocatable, intent(out) :: x(:)

end subroutine

end module
"""

    fmod = parse_fortran_source(source)

    smod = fortran_module_to_semantic_module(fmod)

    func = get_function(smod, "build")

    x = func.arguments[0]

    assert has_constraint(
        x.semantic_type,
        "Allocatable",
    )


# ============================================================
# Derived type conversion
# ============================================================

def test_derived_type():

    source = """
module sparse_mod

type :: sparse_matrix
    integer :: nrows
    integer :: ncols
end type

contains

subroutine multiply(A, x, y)

    type(sparse_matrix), intent(in) :: A

    real(8), intent(in) :: x(:)

    real(8), intent(out) :: y(:)

end subroutine

end module
"""

    fmod = parse_fortran_source(source)

    smod = fortran_module_to_semantic_module(fmod)

    cls = get_class(smod, "sparse_matrix")

    assert cls.name == "sparse_matrix"

    assert len(cls.fields) == 2

    field_names = {f.name for f in cls.fields}

    assert "nrows" in field_names
    assert "ncols" in field_names


# ============================================================
# Inheritance test
# ============================================================

def test_derived_type_inheritance():

    source = """
module inheritance_mod

type :: base_matrix
end type

type, extends(base_matrix) :: sparse_matrix
end type

end module
"""

    fmod = parse_fortran_source(source)

    smod = fortran_module_to_semantic_module(fmod)

    cls = get_class(smod, "sparse_matrix")

    assert "base_matrix" in cls.base_classes


# ============================================================
# Function return type
# ============================================================

def test_function_result():

    source = """
module func_mod

contains

function norm2(x) result(r)

    real(8), intent(in) :: x(:)

    real(8) :: r

end function

end module
"""

    fmod = parse_fortran_source(source)

    smod = fortran_module_to_semantic_module(fmod)

    func = get_function(smod, "norm2")

    assert func.return_type is not None

    assert func.return_type.name == "Float64"


# ============================================================
# Shape preservation
# ============================================================

def test_explicit_shape():

    source = """
module shape_mod

contains

subroutine foo(A)

    real(8), intent(in) :: A(10, 20)

end subroutine

end module
"""

    fmod = parse_fortran_source(source)

    smod = fortran_module_to_semantic_module(fmod)

    func = get_function(smod, "foo")

    A = func.arguments[0]

    assert A.semantic_type.shape == ["10", "20"]


# ============================================================
# JSON serialization test
# ============================================================

def test_semantic_ir_serialization():

    source = """
module simple_mod

contains

subroutine hello(x)

    integer, intent(in) :: x

end subroutine

end module
"""

    fmod = parse_fortran_source(source)

    smod = fortran_module_to_semantic_module(fmod)

    data = asdict(smod)

    json_text = json.dumps(data, indent=2)

    assert "hello" in json_text

    assert "Int32" in json_text


# ============================================================
# Complicated mixed example
# ============================================================

def test_complex_module():

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

    fmod = parse_fortran_source(source)

    smod = fortran_module_to_semantic_module(fmod)

    # --------------------------------------------------------
    # Module structure
    # --------------------------------------------------------

    assert smod.name == "fem_mod"

    assert len(smod.functions) == 2

    assert len(smod.classes) == 1

    # --------------------------------------------------------
    # Class checks
    # --------------------------------------------------------

    mesh_cls = get_class(smod, "mesh")

    assert len(mesh_cls.fields) == 2

    # --------------------------------------------------------
    # Procedure checks
    # --------------------------------------------------------

    assemble = get_function(smod, "assemble")

    assert len(assemble.arguments) == 3

    K = next(arg for arg in assemble.arguments if arg.name == "K")

    assert K.intent == "out"

    assert K.semantic_type.rank == 2

    assert has_constraint(
        K.semantic_type,
        "ORDER_F",
    )

    connectivity = next(arg for arg in assemble.arguments if arg.name == "connectivity")

    assert connectivity.semantic_type.name == "Int32"

    # --------------------------------------------------------
    # Function return
    # --------------------------------------------------------

    norm = get_function(smod, "compute_norm")

    assert norm.return_type.name == "Float64"


def test_module_conversion_public_api_entrypoint():

    source = """
module class_mod

contains

subroutine touch(x)

    integer, intent(inout) :: x

end subroutine

end module
"""

    fmod = parse_fortran_source(source)

    smod = fortran_module_to_semantic_module(fmod)

    assert smod.name == "class_mod"
    assert get_function(smod, "touch").arguments[0].semantic_type.name == "Int32"


def test_fortran_to_ir_preserves_module_semantics_from_inline_source():
    source = """
module m
  use iso_c_binding
  private
  public :: doit
  integer, parameter :: p = 2
  integer :: x(0:)
  type, extends(base) :: thing
    integer, allocatable :: vals(:)
  end type thing
contains
  subroutine doit(a)
    integer, allocatable, intent(inout) :: a(:)
  end subroutine doit
end module m
"""
    parsed = parse_fortran_source(source, filename="m.f90")
    semantic_module = fortran_module_to_semantic_module(parsed)
    semantic_file_modules = fortran_file_to_semantic_modules(parsed, standalone_module_name="standalone")
    semantic_var = semantic_module.variables[0]
    semantic_proc = get_function(semantic_module, "doit")
    semantic_arg = semantic_proc.arguments[0]
    semantic_dtype = get_class(semantic_module, "thing")

    assert semantic_var.semantic_type.name == "Int32"
    assert semantic_arg.intent == "inout"
    assert semantic_arg.semantic_type.constraints[-1].name == "Allocatable"
    assert semantic_proc.projection[0].python_position == 0
    assert semantic_dtype.base_classes == ["base"]
    assert semantic_module.imports == ["iso_c_binding"]
    assert semantic_dtype.visibility == "private"
    assert semantic_proc.visibility == "public"
    assert semantic_file_modules[0].name == "m"


def test_fortran_file_to_semantic_modules_keeps_standalone_procedures_from_inline_source():
    source = """
subroutine scale(n, x)
  integer, intent(in) :: n
  real(8), intent(inout) :: x(n)
end subroutine scale
"""

    parsed = parse_fortran_source(source)
    modules = fortran_file_to_semantic_modules(parsed)

    assert len(modules) == 1
    assert modules[0].name == "standalone"
    func = get_function(modules[0], "scale")
    assert [arg.name for arg in func.arguments] == ["n", "x"]
    assert func.projection[0].python_position == 0
    assert func.projection[1].result_position == 0


def test_semantic_function_projection_equality_and_placeholders():
    left = SemanticFunction(
        name="f",
        native_name="f",
        arguments=[
            SemanticArgument("x", SemanticType("Int32", dtype="Int32")),
            SemanticArgument("y", SemanticType("Float64", dtype="Float64"), intent="out"),
        ],
        projection=[ProjectionMapping(native_position=1, result_position=0, intent="out")],
    )
    right = SemanticFunction(
        name="f",
        native_name="f",
        arguments=[
            SemanticArgument("a", SemanticType("Int32", dtype="Int32")),
            SemanticArgument("b", SemanticType("Float64", dtype="Float64"), intent="out"),
        ],
        projection=[ProjectionMapping(native_position=1, result_position=0, intent="out")],
    )

    assert left == right
