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
    SemanticArrayContract,
    SemanticClass,
    SemanticConstraint,
    SemanticImport,
    SemanticMethod,
    SemanticModule,
    SemanticFunction,
    SemanticStorageContract,
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

    assert "a: Ptr(Const(Float64))" in code
    assert "b: Ptr(Const(Float64))" in code
    assert "c: Annotated[Ptr(Float64), Intent('out')]" in code
    assert 'Returns["c", Float64]' not in code

    assert "-> None" in code


def test_emit_rejects_unknown_semantic_type():
    module = SemanticModule(
        name="bad",
        variables=[
            SemanticArgument(
                name="x",
                semantic_type=SemanticType("Unknown", dtype="Unknown"),
            )
        ],
    )

    with pytest.raises(ValueError, match="unresolved semantic type 'Unknown'"):
        emit_module(module)


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

    assert "Shape" not in code
    assert "Float64[::Strided]" in code
    assert "ArrayCategory" not in code
    assert "SourceDims" not in code


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

    assert "A: Annotated[Const(Float64[::Strided, ::Strided]), ORDER_F" in code
    assert "Shape" not in code
    assert "x: Const(Float64[::Strided])" in code
    assert "y: Annotated[Float64[::Strided], Intent('out')]" in code
    assert "-> None" in code
    assert 'Returns["y", Float64[' not in code


def test_emit_explicit_bound_ranges_as_extents_without_source_dimension_metadata():
    source = """
module bound_mod
contains
subroutine bounded(n, default_bound, zero_bound)
  integer, intent(in) :: n
  real(8), intent(inout) :: default_bound(1:n)
  real(8), intent(inout) :: zero_bound(0:n-1)
end subroutine bounded
end module bound_mod
"""
    code = generate_pyi(source)

    assert "default_bound: Float64[n]" in code
    assert "zero_bound: Float64[n - 1 - 0 + 1]" in code
    assert "ArrayCategory" not in code
    assert "SourceDims" not in code


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

    assert "A: Annotated[Const(Float64[10, 20]), ORDER_F]" in code


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

    assert "K: Annotated[Float64[::Strided, ::Strided], ORDER_F" in code
    assert 'Returns["K", Float64[' not in code

    assert "coords: Annotated[Const(Float64[::Strided, ::Strided]), ORDER_F" in code

    assert "connectivity: Annotated[Const(Int32[::Strided, ::Strided]), ORDER_F" in code

    # --------------------------------------------------------
    # Return type
    # --------------------------------------------------------

    assert "def compute_norm(" in code
    assert ") -> Float64: ..." in code


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
    x: Float64[::Strided]
) -> None: ...
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

    assert "-> None" in code
    assert "c: Annotated[Ptr(Float64), Intent('out')]" in code
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
    assert "x: Ptr(Int32)" in code


def test_printer_emit_visitor_dispatches_semantic_models():
    printer = PyiPrinter()
    constraint = SemanticConstraint("Finite")
    semantic_type = SemanticType(
        "Float64",
        dtype="Float64",
        rank=1,
        shape=[":"],
        storage=SemanticStorageContract(
            kind="array",
            array=SemanticArrayContract(rank=1, shape=[":"], source_shape=[":"]),
        ),
    )
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

    assert printer.emit(constraint) == "Finite"
    assert printer.emit(semantic_type) == "Float64[:]"
    assert printer.emit(argument) == 'class_: Annotated[Float64[:], Name("class")] = ...'
    assert "def reset(self) -> None: ..." in printer.emit(method)
    assert "@private\nclass thing:" in printer.emit(cls)
    assert "var['bad-name']: Float64[:]" in printer.emit(cls)
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
    assert "values: Annotated[Float64[:], Allocatable]" in code
    assert "    def scale(\n        self,\n        alpha: Ptr(Const(Float64))\n    ) -> None: ..." in code
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

    assert "@native_call([Arg(0), Const(1), Len(Arg(0)), Arg(0).shape[0], IsPresent(Arg(1)), Work('tmp')])" in code


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

    assert "@native_call([Len(Return(0)), Work('tmp').shape[1]])" in code
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


def test_printer_emits_extended_storage_and_callable_forms():
    printer = PyiPrinter()
    readonly_value = SemanticType(
        "Int32",
        storage=SemanticStorageContract(kind="value", read_only=True),
    )
    mutable_value = SemanticType("Int32", storage=SemanticStorageContract(kind="value"))
    deep_pointer = SemanticType(
        "Float64",
        storage=SemanticStorageContract(kind="pointer", read_only=True, pointer_depth=3),
    )
    unspecified_storage = SemanticType("Int32", storage=SemanticStorageContract(kind="custom"))
    inferred_array = SemanticType(
        "Float64",
        rank=2,
        storage=SemanticStorageContract(kind="array"),
    )
    annotated_array = SemanticType(
        "Float64",
        constraints=[SemanticConstraint("Finite"), SemanticConstraint("Range", [1, 3])],
        storage=SemanticStorageContract(
            kind="array",
            array=SemanticArrayContract(
                rank=2,
                shape=[":", ":"],
                order="ORDER_ANY",
                allocatable=True,
                pointer=True,
            ),
        ),
    )
    full_callback = SemanticType(
        "Callable",
        metadata={
            "arguments": [SemanticType("Int32")],
            "return": SemanticType("Float64"),
        },
    )
    any_callback = SemanticType("Callable", metadata={"return": SemanticType("Float64")})

    canonical_constant = SemanticArgument(
        "answer",
        SemanticType("Int32", constraints=[SemanticConstraint("Constant")]),
    )
    assert printer.emit_argument(canonical_constant) == "answer: Final[Int32]"
    with pytest.raises(ValueError, match=r"Final\[\.\.\.\]"):
        printer.emit_semantic_type(canonical_constant.semantic_type)
    assert printer.emit_semantic_type(readonly_value) == "Const(Int32)"
    assert printer.emit_semantic_type(mutable_value) == "Int32"
    assert printer.emit_semantic_type(deep_pointer) == "Ptr[3](Const(Float64))"
    assert printer.emit_semantic_type(unspecified_storage) == "Int32"
    assert printer.emit_semantic_type(inferred_array) == "Float64[:, :]"
    assert printer.emit_semantic_type(annotated_array) == (
        "Annotated[Float64[:, :], ORDER_ANY, Allocatable, Pointer, Finite, Range(1, 3)]"
    )
    assert printer.emit_semantic_type(full_callback) == "Callable[[Int32], Float64]"
    assert printer.emit_semantic_type(any_callback) == "Callable[..., Float64]"
    assert printer.emit_semantic_type(SemanticType("Callable")) == "Callable"


def test_printer_projection_return_helpers_and_keyword_data_members():
    printer = PyiPrinter()
    argument = SemanticArgument("x", SemanticType("Float64"), intent="inout", optional=True)
    plain = SemanticArgument("value", SemanticType("Int32"))
    module = SemanticModule(
        name="returns",
        variables=[SemanticArgument("class", SemanticType("Int32"))],
        functions=[
            SemanticFunction(
                name="created",
                projection=[ProjectionMapping(native_position=0, result_position=0)],
            )
        ],
    )

    assert printer._projected_argument_return(argument) == 'Returns["x", Float64, Optional]'
    assert printer._projected_argument_return(plain) == "Int32"
    assert "var['class']: Int32" in emit_module(module)
    assert "@native_call([Return(0)])" in emit_module(module)
