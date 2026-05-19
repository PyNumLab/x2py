import pytest

from x2py import parse_fortran_file as parse_fortran_source

from semantics.fortran2ir import (
    fortran_module_to_semantic_module,
)

from semantics.pyi_printer import (
    emit_module,
    PyiPrinter,
)
from semantics.models import (
    ProjectionMapping,
    SemanticArgument,
    SemanticClass,
    SemanticConstraint,
    SemanticImport,
    SemanticMethod,
    SemanticModule,
    SemanticFunction,
    SemanticType,
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

    assert "ORDER_F" in code


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


def test_emit_import_renames():

    source = """
module user_mod

use list_input, delete_input => delete_input_list

end module
"""

    code = generate_pyi(source)

    assert "from list_input import delete_input_list as delete_input" in code


def test_emit_structured_import_without_items_as_plain_import():
    module = SemanticModule(
        name="imports",
        imports=[SemanticImport(module="iso_c_binding")],
    )

    code = emit_module(module)

    assert "import iso_c_binding" in code


def test_parameter_target_sanitizes_non_identifier_names():
    assert PyiPrinter._parameter_target("has-dash") == "has_dash"
    assert PyiPrinter._parameter_target("1value") == "arg_1value"
    assert PyiPrinter._parameter_target("class!") == "class_"
    assert PyiPrinter._parameter_target("!!!") == "arg"
    assert PyiPrinter._requires_explicit_projection_mapping(
        ProjectionMapping(native_position=1, result_position=0)
    )


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
    x: Float64[Shape(':'), ORDER_F]
) -> Returns["x", Float64[Shape(':'), ORDER_F]]: ...
'''
    )

    assert expected in code


def test_output_argument_uses_plain_return_annotation():
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

    code = PyiPrinter().emit_module(smod)

    assert "-> Float64" in code
    assert 'Returns["c", Float64]' not in code


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


def test_printer_emit_visitor_dispatches_semantic_models():
    printer = PyiPrinter()
    constraint = SemanticConstraint("Shape", [":"])
    semantic_type = SemanticType("Float64", dtype="Float64", constraints=[constraint])
    argument = SemanticArgument("class", semantic_type, optional=True)
    method = SemanticMethod(name="reset")
    cls = SemanticClass(
        name="thing",
        fields=[SemanticArgument("bad-name", semantic_type)],
        methods=[method],
        visibility="private",
    )
    func = SemanticFunction(name="wrap", arguments=[argument])
    module = SemanticModule(name="visitor_mod", classes=[cls], functions=[func])

    assert printer.emit(constraint) == "Shape(':')"
    assert printer.emit(semantic_type) == "Float64[Shape(':')]"
    assert printer.emit(argument) == 'class_: Annotated[Float64[Shape(\':\')], Name("class")] = ...'
    assert "def reset(self) -> None: ..." in printer.emit(method)
    assert "@private\nclass thing:" in printer.emit(cls)
    assert "var['bad-name']: Float64[Shape(':')]" in printer.emit(cls)
    assert "def wrap(" in printer.emit(func)
    assert "class thing:" in printer.emit(module)

    with pytest.raises(TypeError, match="Unsupported semantic model"):
        printer.emit(object())


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


def test_emit_type_bound_procedure_as_python_method_without_duplicate_self():
    source = """
module vector_mod
  private
  public :: vector

  type :: vector
    real(8), allocatable :: values(:)
  contains
    procedure :: scale
  end type vector

contains
  subroutine scale(self, alpha)
    type(vector), intent(inout) :: self
    real(8), intent(in) :: alpha
  end subroutine scale
end module vector_mod
"""

    code = generate_pyi(source)

    assert "class vector:" in code
    assert "values: Float64[Shape(':'), ORDER_F, Allocatable]" in code
    assert "    def scale(\n        self,\n        alpha: Float64\n    ) -> Returns[\"self\", vector]: ..." in code
    assert "        self: vector" not in code


def test_emit_module_variables_with_visibility():
    source = """
module state_mod
  implicit none
  private
  public :: counter
  integer, parameter :: answer = 42
  integer :: counter
  real(8) :: hidden_scale
contains
  subroutine ping(x)
    integer, intent(in) :: x
  end subroutine
end module
"""
    code = generate_pyi(source)
    assert "answer: private[Final[Int32]]" in code
    assert "answer: private[Int32[Constant]]" not in code
    assert "counter: Int32" in code
    assert "hidden_scale: private[Float64]" in code


def test_emit_module_with_projection_helpers_and_private_function():
    module = SemanticModule(
        name="projection_mod",
        functions=[
            SemanticFunction(
                name="wrapper",
                native_name="wrapper",
                arguments=[
                    SemanticArgument("x", SemanticType("Float64", dtype="Float64")),
                    SemanticArgument("b", SemanticType("Int32", dtype="Int32"), optional=True),
                ],
                projection=[
                    ProjectionMapping(native_position=0, python_position=0),
                    ProjectionMapping(native_position=1, value_kind="const", value=1),
                    ProjectionMapping(
                        native_position=2,
                        value_kind="len",
                        value={"kind": "arg", "position": 0},
                    ),
                    ProjectionMapping(
                        native_position=3,
                        value_kind="shape",
                        value={"value": {"kind": "arg", "position": 0}, "dim": 0},
                    ),
                    ProjectionMapping(
                        native_position=4,
                        value_kind="is_present",
                        value={"kind": "arg", "position": 1},
                    ),
                    ProjectionMapping(native_position=5, value_kind="work", value="tmp"),
                ],
            )
        ],
    )

    code = emit_module(module)

    assert "@native_call([Arg(0), Const(1), Len(Arg(0)), Shape(Arg(0), 0), IsPresent(Arg(1)), Work('tmp')])" in code


def test_emit_native_call_supports_return_and_work_value_references():
    module = SemanticModule(
        name="projection_refs_mod",
        functions=[
            SemanticFunction(
                name="wrapper",
                native_name="wrapper",
                return_type=SemanticType("Float64", dtype="Float64"),
                projection=[
                    ProjectionMapping(
                        native_position=0,
                        value_kind="len",
                        value={"kind": "return", "position": 0},
                    ),
                    ProjectionMapping(
                        native_position=1,
                        value_kind="shape",
                        value={"value": {"kind": "work", "name": "tmp"}, "dim": 1},
                    ),
                ],
            )
        ],
    )

    code = emit_module(module)

    assert "@native_call([Len(Return(0)), Shape(Work('tmp'), 1)])" in code
    assert "def wrapper() -> Float64: ..." in code


@pytest.mark.parametrize(
    "projection, message",
    [
        (
            [ProjectionMapping(native_position=0)],
            "native-only projection entry",
        ),
        (
            [ProjectionMapping(native_position=0, value_kind="unknown", value=None)],
            "Unsupported native_call projection entry",
        ),
        (
            [
                ProjectionMapping(
                    native_position=0,
                    value_kind="len",
                    value={"kind": "unknown"},
                )
            ],
            "Unsupported native_call value reference",
        ),
    ],
)
def test_emit_native_call_rejects_unrepresentable_projection_entries(projection, message):
    module = SemanticModule(
        name="bad_projection_mod",
        functions=[
            SemanticFunction(
                name="wrapper",
                native_name="wrapper",
                projection=projection,
            )
        ],
    )

    with pytest.raises(ValueError, match=message):
        emit_module(module)
