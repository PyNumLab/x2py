from pathlib import Path

import pytest

import x2py
from x2py.contracts import CONTRACT_SYMBOLS
from x2py import parse_fortran_file as parse_fortran_source
from x2py.semantic_metadata import SNAPSHOT_TYPE_METADATA
from x2py.codegen.binding_pipeline import BindingPipeline
from x2py.codegen.codegen import Codegen
from x2py.codegen.scope import Scope

from x2py.semantics.fortran2ir import (
    fortran_module_to_semantic_module,
)

from x2py.pyi_pipeline import pyi_text_to_semantic_module as _parse_pyi_text
from x2py.semantics.ir2ast import semantic_ir_to_codegen_ast as _semantic_ir_to_codegen_ast
from x2py.codegen.printers.pyi_printer import (
    emit_module,
    emit_module_stubs,
    opaque_dependency_modules,
    PyiPrinter,
)
from x2py.semantics.models import (
    CALLBACK_DECLARATION_ACCESS_METADATA,
    ProjectionMapping,
    RUNTIME_HOLD_GIL_METADATA,
    RUNTIME_STATUS_ERROR_METADATA,
    SemanticArgument,
    SemanticArrayContract,
    SemanticClass,
    SemanticConstraint,
    SemanticImport,
    SemanticMethod,
    SemanticModule,
    SemanticOrigin,
    SemanticFunction,
    SemanticField,
    SemanticStorageContract,
    SemanticType,
    SemanticVariable,
)
from x2py.semantics.policy_completion import complete_semantic_policies

WRAPPER_FORTRAN_DATA = Path(__file__).parents[1] / "data" / "fortran" / "wrapper"
OPERATOR_F90_SOURCE = WRAPPER_FORTRAN_DATA / "foperators_f90.f90"
CONTRACT_IMPORT = f"from x2py.contracts import {', '.join(sorted(CONTRACT_SYMBOLS))}\n"


def parse_pyi_text(source: str, *args, **kwargs):
    if "x2py.contracts" in source:
        return _parse_pyi_text(source, *args, **kwargs)
    return _parse_pyi_text(f"{CONTRACT_IMPORT}{source}", *args, **kwargs)


# ============================================================
# Helpers
# ============================================================


def semantic_ir_to_codegen_ast(node, *args, **kwargs):
    if isinstance(node, SemanticModule):
        complete_semantic_policies(node)
    return _semantic_ir_to_codegen_ast(node, *args, **kwargs)


def test_x2py_public_api_exports_module_stub_emitter():
    assert "emit_module_stubs" in x2py.__all__
    assert x2py.emit_module_stubs is emit_module_stubs


def generate_pyi(source: str) -> str:
    fmod = parse_fortran_source(source)

    smod = fortran_module_to_semantic_module(fmod)

    return emit_module(smod)


def normalize(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


# ============================================================
# Basic scalar function
# ============================================================


def test_emit_snapshot_type_wrapper_round_trips():
    module = SemanticModule(
        name="snapshot_mod",
        classes=[SemanticClass(name="box", fields=[SemanticField("value", SemanticType("Float64"))])],
        variables=[
            SemanticArgument(
                "current",
                SemanticType("box", dtype="box", metadata={SNAPSHOT_TYPE_METADATA: True}),
            )
        ],
    )

    code = emit_module(module)

    assert "current: Snapshot[box]" in code
    parsed = parse_pyi_text(code, module_name="snapshot_mod")
    assert parsed.variables[0].semantic_type.name == "box"
    assert parsed.variables[0].semantic_type.metadata[SNAPSHOT_TYPE_METADATA] is True


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

    assert "@native_call([Addr(Arg(0)), Addr(Arg(1)), Return('c', 0)])" in code
    assert "a: Float64" in code
    assert "b: Float64" in code
    assert "c: Addr(Float64)" not in code
    assert 'Returns["c"' not in code
    assert ") -> Float64: ..." in code


def test_fortran_generated_contracts_emit_python_name_and_bind_original_name():
    module = SemanticModule(
        name="math_mod",
        functions=[
            SemanticFunction(
                "SQUARE_R4",
                native_name="SQUARE_R4",
                arguments=[SemanticArgument("X", SemanticType("Float32"))],
                return_type=SemanticType("Float32"),
                origin=SemanticOrigin(source_language="fortran", native_name="SQUARE_R4", native_scope="math_mod"),
            )
        ],
        origin=SemanticOrigin(source_language="fortran", source_kind="module"),
    )

    code = emit_module(module, normalize_fortran_public_names=True)

    assert '@bind("SQUARE_R4")\ndef square_r4(' in code


def test_fortran_generated_contracts_reserve_colliding_public_names_by_namespace():
    int32_type = SemanticType("Int32")
    origin = SemanticOrigin(source_language="fortran", native_scope="naming_mod")
    module = SemanticModule(
        name="naming_mod",
        classes=[
            SemanticClass(
                name="visible_t",
                fields=[
                    SemanticField("lambda", int32_type),
                    SemanticField("lambda_", int32_type),
                ],
                origin=origin,
            )
        ],
        functions=[
            SemanticFunction("lambda", native_name="lambda", return_type=int32_type, origin=origin),
            SemanticFunction("lambda_", native_name="lambda_", return_type=int32_type, origin=origin),
        ],
        origin=origin,
    )

    code = emit_module(module, normalize_fortran_public_names=True)

    assert 'lambda_: Annotated[Int32, Name("lambda")]' in code
    assert 'lambda__2: Annotated[Int32, Name("lambda_")]' in code
    assert '@bind("lambda")\ndef lambda_() -> Int32: ...' in code
    assert '@bind("lambda_")\ndef lambda__2() -> Int32: ...' in code
    assert "def lambda__3" not in code


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


def test_printer_validation_and_opaque_dependency_edge_cases():
    printer = PyiPrinter()

    with pytest.raises(ValueError, match="Shape constraints are not canonical"):
        printer.emit(SemanticConstraint("Shape"))

    plain_type = SemanticType("Float64", dtype="Float64")
    assert printer._emit_storage_type(plain_type) == "Float64"

    malformed_import = SemanticType(
        "external_type",
        dtype="external_type",
        metadata={
            "external_type_ref": {
                "origin_module": "",
                "name": "external_type",
                "local_name": "external_type",
            }
        },
    )
    assert (
        printer._effective_imports(SemanticModule(name="api", variables=[SemanticArgument("value", malformed_import)]))
        == []
    )

    invalid_opaque_ref = SemanticType(
        "external_type",
        dtype="external_type",
        metadata={
            "external_type_ref": {
                "representation": "opaque",
                "origin_module": "types",
                "name": 42,
            }
        },
    )
    known_opaque_ref = SemanticType(
        "external_type",
        dtype="external_type",
        metadata={
            "external_type_ref": {
                "representation": "opaque",
                "origin_module": "types",
                "name": "external_type",
            }
        },
    )
    assert (
        opaque_dependency_modules(
            SemanticModule(
                name="api",
                variables=[
                    SemanticArgument("invalid", invalid_opaque_ref),
                    SemanticArgument("known", known_opaque_ref),
                ],
            ),
            available_modules=[SemanticModule(name="types", classes=[SemanticClass(name="external_type")])],
        )
        == []
    )

    with pytest.raises(ValueError, match="duplicate semantic module"):
        emit_module_stubs([SemanticModule(name="duplicate"), SemanticModule(name="duplicate")])


def test_opaque_dependency_modules_scan_all_references_and_preserve_metadata():
    plain_type = SemanticType("Float64", dtype="Float64")
    invalid_opaque_ref = SemanticType(
        "invalid_type",
        dtype="invalid_type",
        metadata={
            "external_type_ref": {
                "representation": "opaque",
                "origin_module": "types",
                "name": 42,
            }
        },
    )
    known_opaque_ref = SemanticType(
        "known_type",
        dtype="known_type",
        metadata={
            "external_type_ref": {
                "representation": "opaque",
                "origin_module": "types",
                "name": "known_type",
            }
        },
    )
    missing_opaque_ref = SemanticType(
        "missing_type",
        dtype="missing_type",
        metadata={
            "external_type_ref": {
                "representation": "opaque",
                "origin_module": "types",
                "name": "missing_type",
            }
        },
    )

    dependencies = opaque_dependency_modules(
        SemanticModule(
            name="api",
            variables=[
                SemanticArgument("plain", plain_type),
                SemanticArgument("invalid", invalid_opaque_ref),
                SemanticArgument("known", known_opaque_ref),
                SemanticArgument("missing", missing_opaque_ref),
            ],
        ),
        available_modules=[SemanticModule(name="types", classes=[SemanticClass(name="known_type")])],
    )

    assert dependencies == [
        SemanticModule(
            name="types",
            classes=[
                SemanticClass(
                    name="missing_type",
                    native_name="missing_type",
                    base_classes=["Opaque"],
                    metadata={"representation": "opaque"},
                )
            ],
        )
    ]


def test_emit_module_stubs_honors_available_opaque_dependency_modules():
    known_opaque_ref = SemanticType(
        "known_type",
        dtype="known_type",
        metadata={
            "external_type_ref": {
                "representation": "opaque",
                "origin_module": "types",
                "name": "known_type",
            }
        },
    )
    stubs = emit_module_stubs(
        SemanticModule(
            name="api",
            variables=[SemanticArgument("known", known_opaque_ref)],
        ),
        available_modules=[SemanticModule(name="types", classes=[SemanticClass(name="known_type")])],
    )

    assert set(stubs) == {"api"}


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
    assert "Float64[::]" in code
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

    assert "A: Annotated[Float64[::, ::], ORDER_F" in code
    assert "Shape" not in code
    assert "x: Float64[::]" in code
    assert "y: Float64[::]" in code
    assert "Annotated[Float64[::]" not in code
    assert 'Returns["y", Float64[::]]' in code


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


def test_emit_optional_scalar_output_as_visible_scalar_storage():
    source = """
module opt_out_mod
contains
subroutine maybe_status(status)
    integer(4), intent(out), optional :: status
end subroutine maybe_status
end module opt_out_mod
"""

    code = generate_pyi(source)

    assert "Return('status'" not in code
    assert "status: Int32[()] = ..." in code
    assert ') -> Returns["status", Int32[()]] | None: ...' in code


def test_emit_optional_allocatable_output_as_visible_argument():
    source = """
module opt_alloc_out_mod
contains
subroutine maybe_values(values)
    real(8), allocatable, intent(out), optional :: values(:)
end subroutine maybe_values
end module opt_alloc_out_mod
"""

    code = generate_pyi(source)

    assert "Return('values'" not in code
    assert "values: Allocatable[Float64[:]] | None = ..." in code
    assert ') -> Returns["values", Allocatable[Float64[:]]] | None: ...' in code


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

function make_values() result(x)

    real(8), allocatable :: x(:)

end function

end module
"""

    code = generate_pyi(source)

    assert "Allocatable" in code
    assert "@native_call([Return('x', 0)])" in code
    assert "def build() -> Allocatable[Float64[:]]: ..." in code
    assert "def make_values() -> Allocatable[Float64[:]]: ..." in code


def test_emit_scalar_character_inout_as_replacement_return():
    source = """
module m
contains
subroutine normalize(name)
    character(len=8), intent(inout) :: name
end subroutine
end module
"""

    code = generate_pyi(source)

    annotation = "String[8]"
    assert "@native_call([Arg(0)])" not in code
    assert f"name: {annotation}" in code
    assert f') -> Returns["name", {annotation}]: ...' in code


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

    assert "A: Annotated[Float64[10, 20], ORDER_F]" in code


# ============================================================
# Imports
# ============================================================


def test_emit_omits_resolved_source_kind_imports():
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

    assert "iso_c_binding" not in code


def test_emit_import_renames():
    source = """
module user_mod

use list_input, delete_input => delete_input_list

end module
"""

    code = generate_pyi(source)

    assert "from list_input import delete_input_list as delete_input" in code


def test_emit_imported_derived_type_reference_without_reexporting_class():
    parsed = parse_fortran_source(
        """
module physics
  use types_mod, only: particle
contains
  subroutine move(p)
    type(particle), intent(inout) :: p
  end subroutine move
end module physics
"""
    )
    module = fortran_module_to_semantic_module(parsed)
    stubs = emit_module_stubs(module)
    code = stubs["physics"]

    assert "from types_mod import particle" in code
    assert "from . import types_mod" not in code
    assert "p: particle" in code
    assert "Addr(particle)" not in code
    assert "class particle" not in code
    assert stubs["types_mod"].endswith("class particle(Opaque):\n    pass")


def test_emit_procedure_local_imported_derived_types_as_qualified_module_refs():
    parsed = parse_fortran_source(
        """
module physics
contains
  subroutine use_a(p)
    use a_types, only: state
    type(state), intent(inout) :: p
  end subroutine use_a

  subroutine use_b(p)
    use b_types, only: state
    type(state), intent(inout) :: p
  end subroutine use_b
end module physics
"""
    )

    module = fortran_module_to_semantic_module(parsed)
    code = emit_module(module)

    assert "from . import a_types, b_types" in code
    assert "p: a_types.state" in code
    assert "p: b_types.state" in code
    assert "from a_types import state" not in code
    assert "from b_types import state" not in code
    assert "from .a_types import state" not in code
    assert "from .b_types import state" not in code
    assert " as imported_a_types" not in code


def test_emit_procedure_local_import_namespace_collision_fails_without_alias():
    parsed = parse_fortran_source(
        """
module physics
contains
  subroutine a_types()
  end subroutine a_types

  subroutine use_state(p)
    use a_types, only: state
    type(state), intent(inout) :: p
  end subroutine use_state
end module physics
"""
    )

    module = fortran_module_to_semantic_module(parsed)

    with pytest.raises(ValueError, match="Procedure-local Fortran import namespace collides"):
        emit_module(module)


def test_emit_procedure_local_import_namespace_collision_with_synthetic_import_fails():
    procedure_ref = {
        "name": "state",
        "local_name": "a_types.state",
        "origin_module": "a_types",
        "wrapped": False,
        "representation": "opaque",
        "import_scope": "procedure",
    }
    flattened_ref = {
        "name": "a_types",
        "local_name": "a_types",
        "origin_module": "other_types",
        "wrapped": False,
        "representation": "opaque",
    }
    module = SemanticModule(
        name="api",
        functions=[
            SemanticFunction(
                "use_state",
                arguments=[
                    SemanticArgument("p", SemanticType("a_types.state", metadata={"external_type_ref": procedure_ref}))
                ],
            ),
            SemanticFunction(
                "use_flat",
                arguments=[
                    SemanticArgument("p", SemanticType("a_types", metadata={"external_type_ref": flattened_ref}))
                ],
            ),
        ],
    )

    with pytest.raises(ValueError, match="Procedure-local Fortran import namespace collides"):
        emit_module(module)


def test_emit_bare_use_adds_import_for_opaque_dependency_type():
    parsed = parse_fortran_source(
        """
module physics
  use types_mod
contains
  subroutine move(p)
    type(particle), intent(inout) :: p
  end subroutine move
end module physics
"""
    )
    stubs = emit_module_stubs(fortran_module_to_semantic_module(parsed))

    assert "import types_mod" in stubs["physics"]
    assert "from types_mod import particle" in stubs["physics"]
    assert stubs["types_mod"].endswith("class particle(Opaque):\n    pass")


def test_emit_omits_structured_source_kind_import_without_items():
    module = SemanticModule(
        name="imports",
        imports=[SemanticImport(module="iso_c_binding")],
    )

    code = emit_module(module)

    assert code == ""


def test_parameter_target_sanitizes_non_identifier_names():
    assert PyiPrinter._parameter_target("has-dash") == "has_dash"
    assert PyiPrinter._parameter_target("1value") == "arg_1value"
    assert PyiPrinter._parameter_target("class!") == "class_"
    assert PyiPrinter._parameter_target("!!!") == "arg"
    assert PyiPrinter._requires_explicit_projection_mapping(ProjectionMapping(native_position=1, result_position=0))


def test_emit_argument_escapes_original_name_metadata():
    emitted = PyiPrinter().emit(SemanticArgument('quote"name', SemanticType("Int32")))
    reparsed = parse_pyi_text(f"def consume({emitted}) -> None: ...\n", module_name="quoted")

    assert emitted == 'quote_name: Annotated[Int32, Name("quote\\"name")]'
    assert reparsed.functions[0].arguments[0].name == 'quote"name'


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

    assert "K: Annotated[Float64[::, ::], ORDER_F" in code
    assert 'Returns["K", Annotated[Float64[::, ::], ORDER_F]]' in code

    assert "coords: Annotated[Float64[::, ::], ORDER_F" in code

    assert "connectivity: Annotated[Int32[::, ::], ORDER_F" in code

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
        """
def scale(
    x: Float64[::]
) -> None: ...
"""
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

    code = PyiPrinter().emit(smod)

    assert "c: Annotated[Addr(Float64)" not in code
    assert 'Returns["c"' not in code
    assert ") -> Float64: ..." in code


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

    code = PyiPrinter().emit(smod)

    assert "def touch(" in code
    assert "@native_call([Addr(Arg(0))])" in code
    assert "x: Int32" in code


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

    with pytest.raises(TypeError) as unsupported:
        printer.emit(object())
    assert str(unsupported.value) == "Unsupported semantic model for .pyi emission: <class 'object'>"


def test_printer_emits_flat_dimension_for_assumed_size_arrays():
    fortran_type = SemanticType(
        "Float64",
        dtype="Float64",
        rank=2,
        shape=["3", ":"],
        storage=SemanticStorageContract(
            kind="array",
            array=SemanticArrayContract(
                rank=2,
                shape=["3", ":"],
                category="assumed_size",
                source_shape=["3", "*"],
                order="ORDER_F",
                contiguous=True,
            ),
        ),
    )
    c_type = SemanticType(
        "Float64",
        dtype="Float64",
        rank=2,
        shape=[":", "3"],
        storage=SemanticStorageContract(
            kind="array",
            array=SemanticArrayContract(
                rank=2,
                shape=[":", "3"],
                category="assumed_size",
                source_shape=["*", "3"],
                order="ORDER_C",
                contiguous=True,
            ),
        ),
    )

    assert PyiPrinter().emit(fortran_type) == "Float64[3, Flat]"
    assert PyiPrinter().emit(c_type) == "Annotated[Float64[Flat, 3], ORDER_C]"

    lower_bound_assumed_size = SemanticType(
        "Float64",
        dtype="Float64",
        rank=1,
        shape=[":"],
        storage=SemanticStorageContract(
            kind="array",
            array=SemanticArrayContract(
                rank=1,
                shape=[":"],
                category="assumed_size",
                source_shape=["0:*"],
                order="ORDER_F",
                contiguous=True,
            ),
        ),
    )
    assert PyiPrinter().emit(lower_bound_assumed_size) == 'Annotated[Float64[Flat], SourceDims("0:*")]'


def test_emit_module_aliases_contract_import_when_user_name_collides():
    array_type = SemanticType(
        "Float64",
        dtype="Float64",
        rank=1,
        shape=[":"],
        storage=SemanticStorageContract(
            kind="array",
            array=SemanticArrayContract(
                rank=1,
                shape=[":"],
                category="assumed_size",
                source_shape=["*"],
                order="ORDER_F",
                contiguous=True,
            ),
        ),
    )
    module = SemanticModule(
        name="alias_mod",
        variables=[
            SemanticVariable(
                "Flat",
                SemanticType("Int32", constraints=[SemanticConstraint("Constant")]),
                default_value="10",
            )
        ],
        functions=[SemanticFunction("inspect", arguments=[SemanticArgument("values", array_type)])],
    )

    code = emit_module(module)

    assert "Flat as " in code.splitlines()[0]
    reparsed = _parse_pyi_text(code, module_name="alias_mod")
    assert reparsed.variables[0].name == "Flat"
    assert reparsed.functions[0].arguments[0].semantic_type.storage.array.category == "assumed_size"


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
    assert "values: Allocatable[Float64[:]]" in code
    assert "    @native_call([Pass(), Addr(Arg(0))])" in code
    assert "    def scale(\n        self,\n        alpha: Float64\n    ) -> None: ..." in code
    assert "        self: vector" not in code


def test_emit_fortran_type_default_constructor_and_field_values():
    source = """
module constructor_mod
  type :: state
    integer :: id = 7
    real(8) :: scale = 2.5
    logical :: enabled = .true.
  end type state
end module constructor_mod
"""

    code = generate_pyi(source)

    assert normalize(
        """
class state:
    def __init__(
        self,
        *,
        id: Int32 = 7,
        scale: Float64 = 2.5,
        enabled: Bool = True
    ) -> None: ...
"""
    ) in normalize(code)
    assert "    id: Int32 = 7" in code
    assert "    scale: Float64 = 2.5" in code
    assert "    enabled: Bool = True" in code


def test_emit_explicit_pass_name_and_nopass_methods():
    source = """
module pass_mod
  type :: vector
  contains
    procedure, pass(owner) :: shift => shift_vector
    procedure, nopass :: make => make_vector
  end type vector
contains
  subroutine shift_vector(dx, owner, dy)
    real(8), intent(in) :: dx
    class(vector), intent(inout) :: owner
    real(8), intent(in) :: dy
  end subroutine shift_vector
  function make_vector(value) result(created)
    real(8), intent(in) :: value
    type(vector) :: created
  end function make_vector
end module pass_mod
"""

    code = generate_pyi(source)

    assert "    def shift(\n        self,\n        dx: Float64,\n        dy: Float64" in code
    assert "        owner: Addr(vector)" not in code
    assert "@native_call([Addr(Arg(0)), Pass(), Addr(Arg(1))])" in code
    assert '    @staticmethod\n    @bind("make_vector")' in code
    assert "value: Float64" in code
    assert "-> vector: ..." in code


def test_emit_and_load_module_and_type_bound_overload_sets():
    source = """
module generic_mod
  interface convert
    module procedure convert_integer, convert_real
  end interface convert
  type :: box
  contains
    procedure :: set_integer
    procedure :: set_real
    generic :: set => set_integer, set_real
  end type box
contains
  integer function convert_integer(value)
    integer :: value
    convert_integer = value
  end function convert_integer
  real function convert_real(value)
    real :: value
    convert_real = value
  end function convert_real
  subroutine set_integer(self, value)
    class(box) :: self
    integer :: value
  end subroutine set_integer
  subroutine set_real(self, value)
    class(box) :: self
    real :: value
  end subroutine set_real
end module generic_mod
"""
    code = generate_pyi(source)

    assert "from typing import overload" not in code
    assert code.count('@overload("convert_integer")\ndef convert(') == 1
    assert code.count('@overload("convert_real")\ndef convert(') == 1
    assert code.count('    @overload("set_integer")\n    def set(') == 1
    assert code.count('    @overload("set_real")\n    def set(') == 1
    assert '@overload("convert_integer")\n@native_call' not in code
    assert '    @overload("set_integer")\n    @native_call' not in code

    loaded = parse_pyi_text(code, module_name="generic_mod")
    assert [(item.name, len(item.procedures)) for item in loaded.overload_sets] == [("convert", 2)]
    assert [procedure.name for procedure in loaded.overload_sets[0].procedures] == [
        "convert_integer",
        "convert_real",
    ]
    assert loaded.imports == []
    assert [(item.name, len(item.procedures)) for item in loaded.classes[0].overload_sets] == [("set", 2)]
    assert [procedure.name for procedure in loaded.classes[0].overload_sets[0].procedures] == [
        "set_integer",
        "set_real",
    ]


def test_emit_and_load_allocatable_module_variable_declaration():
    source = """
module alloc_view_mod
  real(8), allocatable, target :: values(:)
  type :: box
    real(8), allocatable :: field(:)
  end type box
end module alloc_view_mod
"""
    code = generate_pyi(source)

    assert "values: Annotated[Allocatable[Float64[:]], Aliased]" in code
    assert "field: Allocatable[Float64[:]]" in code

    loaded = parse_pyi_text(code, module_name="alloc_view_mod")
    assert [variable.name for variable in loaded.variables] == ["values"]
    assert loaded.variables[0].semantic_type.storage.array.allocatable is True
    assert loaded.variables[0].semantic_type.metadata["aliased"] is True
    assert loaded.classes[0].fields[0].semantic_type.storage.array.allocatable is True
    assert "aliased" not in loaded.classes[0].fields[0].semantic_type.metadata

    codegen_module = semantic_ir_to_codegen_ast(
        loaded,
        Scope(name=loaded.name, scope_type="module"),
    )
    assert codegen_module.variables[0].is_target is True


def test_emit_and_load_aliased_derived_module_variable_declaration():
    source = """
module derived_module_state
  type :: box
    real(8), allocatable :: values(:)
  end type box
  type(box), target :: current
end module derived_module_state
"""
    code = generate_pyi(source)

    assert "current: Annotated[box, Aliased]" in code

    loaded = parse_pyi_text(code, module_name="derived_module_state")
    assert [variable.name for variable in loaded.variables] == ["current"]
    assert loaded.variables[0].semantic_type.name == "box"
    assert loaded.variables[0].semantic_type.metadata["aliased"] is True

    codegen_module = semantic_ir_to_codegen_ast(
        loaded,
        Scope(name=loaded.name, scope_type="module"),
    )
    assert codegen_module.variables[0].is_target is True


def test_emit_module_stubs_prints_plain_derived_module_variable_as_snapshot():
    source = """
module derived_module_snapshot
  type :: box
    real(8) :: value
  end type box
  type(box) :: current
end module derived_module_snapshot
"""
    parsed = parse_fortran_source(source)
    semantic_module = fortran_module_to_semantic_module(parsed)

    code = emit_module_stubs(semantic_module)["derived_module_snapshot"]

    assert "current: Snapshot[box]" in code
    loaded = parse_pyi_text(code, module_name="derived_module_snapshot")
    assert loaded.variables[0].semantic_type.metadata[SNAPSHOT_TYPE_METADATA] is True


def test_defined_operator_pyi_round_trip_preserves_native_links_without_fortran_source():
    semantic_module = fortran_module_to_semantic_module(
        parse_fortran_source(OPERATOR_F90_SOURCE.read_text(), filename=str(OPERATOR_F90_SOURCE))
    )
    code = emit_module(semantic_module)

    assert '@overload("add_real_vector")' in code
    assert "def __radd__(" in code
    assert '@overload("assign_vector_real")' in code
    assert "def assign(" in code
    assert "left: Annotated[Addr(vector)" not in code
    assert "left: vector" in code
    assert '-> Returns["left", vector]: ...' in code
    assert "right: Float64\n    ) -> vector: ..." in code
    assert '@overload("dot_vectors")' in code
    assert "def operator_dot(" in code
    assert '@overload("equivalent_vector_offset", generic="operator(.eqv.)")' in code
    assert '@overload("not_equivalent_vector_integer", generic="operator(.neqv.)")' in code
    assert "from typing import overload" not in code

    loaded = parse_pyi_text(code, module_name=semantic_module.name)
    assert emit_module(loaded) == code
    codegen_module = semantic_ir_to_codegen_ast(
        loaded,
        Scope(name=loaded.name, scope_type="module"),
    )
    vector = next(cls for cls in codegen_module.classes if str(cls.name) == "vector")
    overload_sets = {item.name: item.native_name for item in vector.overload_sets}
    assert overload_sets["__add__"] == "operator(+)"
    assert overload_sets["operator_dot"] == "operator(.dot.)"
    assert overload_sets["assign"] == "assignment(=)"
    assert set(next(item for item in vector.overload_sets if item.name == "__eq__").native_names) == {
        "operator(==)",
        "operator(.eqv.)",
    }


def test_defined_operator_pyi_generates_wrapper_sources_without_fortran_source(tmp_path: Path):
    semantic_module = fortran_module_to_semantic_module(
        parse_fortran_source(OPERATOR_F90_SOURCE.read_text(), filename=str(OPERATOR_F90_SOURCE))
    )
    pyi = emit_module(semantic_module)
    loaded = parse_pyi_text(pyi, module_name=semantic_module.name)
    scope = Scope(name=loaded.name, scope_type="module")
    codegen_module = semantic_ir_to_codegen_ast(loaded, scope)
    pipeline = BindingPipeline(
        Codegen(loaded.name, codegen_module, codegen_module.scope),
        loaded.name,
        "fortran",
        verbose=0,
    )

    pipeline.generate(str(tmp_path))
    generated = pipeline.write(tmp_path)

    assert [path.name for path in generated] == [
        "bind_c_foperators_f90_wrapper.f90",
        "foperators_f90_wrapper.c",
    ]
    fortran_wrapper = generated[0].read_text()
    c_wrapper = generated[1].read_text()
    assert "left + right" in fortran_wrapper
    assert "left = right" in fortran_wrapper
    assert "left .eqv. right" in fortran_wrapper
    assert "left .neqv. right" in fortran_wrapper
    assert ".nb_add = (binaryfunc)" in c_wrapper
    assert ".tp_richcompare =" in c_wrapper


def test_bound_constructor_pyi_generates_single_initializer_without_keyword_default(tmp_path: Path):
    loaded = parse_pyi_text(
        """
class state:
    @private
    def init_state(self, seed: Addr(Int32)) -> None: ...

    @bind("init_state")
    def __init__(self, seed: Addr(Int32)) -> None: ...

    id: Int32
""",
        module_name="edited",
    )
    scope = Scope(name=loaded.name, scope_type="module")
    codegen_module = semantic_ir_to_codegen_ast(loaded, scope)
    pipeline = BindingPipeline(
        Codegen(loaded.name, codegen_module, codegen_module.scope),
        loaded.name,
        "fortran",
        verbose=0,
    )

    pipeline.generate(str(tmp_path))
    generated = pipeline.write(tmp_path)

    assert [path.name for path in generated] == [
        "bind_c_edited_wrapper.f90",
        "edited_wrapper.c",
    ]
    c_wrapper = generated[1].read_text()
    assert "init_state" in generated[0].read_text()
    assert "state__default_init_wrapper" not in c_wrapper
    assert '(char*)"seed"' in c_wrapper
    assert 'PyArg_ParseTupleAndKeywords(args, kwargs, "O", kwlist, &seed_obj)' in c_wrapper
    assert "Py_BEGIN_ALLOW_THREADS" not in c_wrapper
    assert "Py_END_ALLOW_THREADS" not in c_wrapper


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
    assert "answer:" not in code
    assert "counter: Int32" in code
    assert "hidden_scale" not in code
    assert "ping" not in code


def test_emit_fortran_parameter_defaults_only_when_resolved_to_literals():
    source = """
module trig_constants
  real, parameter :: c = cos(0.0)
  integer, parameter :: n = 3 + 4
end module
"""
    code = generate_pyi(source)

    assert "c: Final[Float32]\n" in code
    assert "c: Final[Float32] = cos(0.0)" not in code
    assert "n: Final[Int32] = 7" in code


def test_emit_omits_fortran_source_private_methods_and_fields():
    source = """
module private_method_mod
  implicit none
  private
  public :: box
  type :: box
    private
    integer, public :: id
    integer, private :: secret
  contains
    procedure, private :: hidden => hidden_impl
    procedure, public :: visible => visible_impl
  end type box
contains
  subroutine hidden_impl(self)
    class(box) :: self
  end subroutine hidden_impl
  subroutine visible_impl(self)
    class(box) :: self
  end subroutine visible_impl
end module
"""

    code = generate_pyi(source)

    assert "class box:" in code
    assert "    id: Int32" in code
    assert "secret" not in code
    assert "hidden" not in code
    assert "hidden_impl" not in code
    assert '@bind("visible_impl")' in code
    assert "    def visible(self) -> None: ..." in code


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
                    ProjectionMapping(
                        native_position=1,
                        value_kind="literal",
                        value={"type": "Int32", "value": 1},
                    ),
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

    assert "@native_call([Arg(0), Int32(1), Len(Arg(0)), Arg(0).shape[0], IsPresent(Arg(1)), Work('tmp')])" in code


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


def test_runtime_policy_decorators_round_trip_through_pyi_and_codegen(tmp_path: Path):
    loaded = parse_pyi_text(
        """
@raises(status="status", message="message", success=0)
def solve(
    x: Float64
) -> tuple[Float64, Returns["status", Int32], Returns["message", String]]: ...

@hold_gil
def serialized(x: Float64) -> Float64: ...
""",
        module_name="runtime_policy",
    )

    func = loaded.functions[0]
    assert func.metadata[RUNTIME_STATUS_ERROR_METADATA] == {
        "status": "status",
        "message": "message",
        "success": 0,
    }
    assert loaded.functions[1].metadata[RUNTIME_HOLD_GIL_METADATA] is True

    code = emit_module(loaded)
    assert '@raises(status="status", message="message", success=0)' in code
    assert "@hold_gil" in code
    assert emit_module(parse_pyi_text(code, module_name="runtime_policy")) == code

    scope = Scope(name=loaded.name, scope_type="module")
    codegen_module = semantic_ir_to_codegen_ast(loaded, scope)
    pipeline = BindingPipeline(
        Codegen(loaded.name, codegen_module, codegen_module.scope),
        loaded.name,
        "fortran",
        verbose=0,
    )

    pipeline.generate(str(tmp_path))
    generated = pipeline.write(tmp_path)

    c_wrapper = generated[1].read_text()
    solve_start = c_wrapper.index("static PyObject* bind_c_solve_wrapper")
    serialized_start = c_wrapper.index("static PyObject* bind_c_serialized_wrapper")
    solve_wrapper = c_wrapper[solve_start:serialized_start]
    serialized_wrapper = c_wrapper[serialized_start : c_wrapper.index("static PyMethodDef", serialized_start)]
    assert "Py_BEGIN_ALLOW_THREADS" in solve_wrapper
    assert "Py_END_ALLOW_THREADS" in solve_wrapper
    assert "Py_BEGIN_ALLOW_THREADS" not in serialized_wrapper
    assert "Py_END_ALLOW_THREADS" not in serialized_wrapper
    assert "PyErr_SetObject(PyExc_RuntimeError" in c_wrapper
    assert "return solve_0001_obj;" in c_wrapper
    assert "PyTuple_Pack" not in c_wrapper
    assert c_wrapper.count("Py_DECREF(status_obj);") == 2
    assert c_wrapper.count("Py_DECREF(message_obj);") == 2
    assert "solve(x) -> float64" in c_wrapper
    assert "RuntimeError" in c_wrapper


def test_callback_contract_holds_gil_and_release_gil_is_removed(tmp_path: Path):
    loaded = parse_pyi_text(
        """
def apply(callback: Callable[[Float64], Float64], x: Float64) -> Float64: ...
""",
        module_name="callback_policy",
    )
    scope = Scope(name=loaded.name, scope_type="module")
    codegen_module = semantic_ir_to_codegen_ast(loaded, scope)
    pipeline = BindingPipeline(
        Codegen(loaded.name, codegen_module, codegen_module.scope),
        loaded.name,
        "fortran",
        verbose=0,
    )
    pipeline.generate(str(tmp_path))
    generated = pipeline.write(tmp_path)

    c_wrapper = generated[1].read_text()
    assert "Py_BEGIN_ALLOW_THREADS" not in c_wrapper
    assert "Py_END_ALLOW_THREADS" not in c_wrapper

    with pytest.raises(ValueError, match=r"Unsupported \.pyi decorator: 'release_gil'"):
        parse_pyi_text(
            "@release_gil\ndef removed(x: Float64) -> Float64: ...",
            module_name="removed_release_gil",
        )


@pytest.mark.parametrize(
    "source, message",
    [
        (
            '@raises(status="status")\ndef solve() -> Returns["status", Float64]: ...',
            "must be a scalar integer hidden output",
        ),
        (
            '@raises(status="status")\ndef solve(status: Int32) -> None: ...',
            "status target must name a hidden output",
        ),
        (
            '@raises(status="status", message="message")\n'
            'def solve() -> tuple[Returns["status", Int32], Returns["message", Int32]]: ...',
            "must be a scalar string hidden output",
        ),
    ],
)
def test_runtime_status_policy_rejects_invalid_output_contracts(source: str, message: str):
    loaded = parse_pyi_text(source, module_name="invalid_runtime_policy")

    with pytest.raises(ValueError, match=message):
        semantic_ir_to_codegen_ast(loaded, Scope(name=loaded.name, scope_type="module"))


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


def test_printer_rejects_optional_absent_array_handles_outside_callable_arguments():
    variable = SemanticVariable(
        "values",
        SemanticType(
            "Float64",
            rank=1,
            storage=SemanticStorageContract(
                kind="array",
                array=SemanticArrayContract(rank=1, shape=[":"], allocatable=True),
            ),
        ),
    )
    variable.optional = True
    module = SemanticModule(
        name="bad_optional_handle_mod",
        variables=[variable],
    )

    with pytest.raises(ValueError, match="only be emitted for callable arguments"):
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
    double_pointer = SemanticType(
        "Float64",
        storage=SemanticStorageContract(kind="pointer", pointer_depth=2),
    )
    unspecified_storage = SemanticType("Int32", storage=SemanticStorageContract(kind="custom"))
    inferred_array = SemanticType(
        "Float64",
        rank=2,
        storage=SemanticStorageContract(kind="array"),
    )
    allocatable_handle = SemanticType(
        "Float64",
        rank=2,
        storage=SemanticStorageContract(
            kind="array",
            array=SemanticArrayContract(
                rank=2,
                shape=[":", ":"],
                order="ORDER_F",
                allocatable=True,
            ),
        ),
    )
    pointer_handle = SemanticType(
        "Float64",
        rank=1,
        metadata={"fortran_pointer_association": "runtime"},
        storage=SemanticStorageContract(
            kind="array",
            array=SemanticArrayContract(rank=1, shape=[":"], pointer=True),
        ),
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
            ),
        ),
    )
    full_callback = SemanticType(
        "Callable",
        metadata={
            "arguments": [SemanticType("Int32"), SemanticType("Float64")],
            "return": SemanticType("Float64"),
        },
    )
    any_callback = SemanticType("Callable", metadata={"return": SemanticType("Float64")})
    character = SemanticType(
        "String",
        metadata={"fortran_character_length": "16"},
        storage=SemanticStorageContract(kind="reference", mutable=True, pointer_depth=1),
    )
    allocatable_character = SemanticType(
        "String",
        metadata={"fortran_character_length": ":", "fortran_allocatable": True},
    )
    pointer_scalar = SemanticType(
        "Int32",
        metadata={"fortran_pointer": True, "fortran_pointer_association": "runtime"},
        storage=SemanticStorageContract(kind="reference", mutable=True, pointer_depth=1),
    )

    canonical_constant = SemanticArgument(
        "answer",
        SemanticType("Int32", constraints=[SemanticConstraint("Constant")]),
    )
    assert printer.emit(canonical_constant) == "answer: Final[Int32]"
    with pytest.raises(ValueError, match=r"Final\[\.\.\.\]"):
        printer.emit(canonical_constant.semantic_type)
    assert printer.emit(readonly_value) == "Int32"
    assert printer.emit(mutable_value) == "Int32"
    assert printer.emit(deep_pointer) == "Addr[3](Float64)"
    assert printer.emit(double_pointer) == "Addr[2](Float64)"
    assert printer.emit(unspecified_storage) == "Int32"
    assert printer.emit(inferred_array) == "Float64[:, :]"
    assert printer.emit(allocatable_handle) == "Allocatable[Annotated[Float64[:, :], ORDER_F]]"
    assert printer.emit(pointer_handle) == 'Annotated[Pointer[Float64[:]], PointerAssociation("runtime")]'
    assert printer.emit(annotated_array) == "Annotated[Float64[:, :], ORDER_ANY, Finite, Range(1, 3)]"
    assert printer.emit(character) == "String[16]"
    assert printer.emit(allocatable_character) == "Allocatable[String]"
    assert printer.emit(pointer_scalar) == "Pointer[Int32]"
    assert printer.emit(full_callback) == "Callable[[Int32, Float64], Float64]"
    assert printer.emit(any_callback) == "Callable[..., Float64]"
    assert printer.emit(SemanticType("Callable")) == "Callable"


@pytest.mark.parametrize(
    ("argument_type", "projection"),
    [
        (
            SemanticType(
                "Float64",
                metadata={"fortran_allocatable": True},
            ),
            "Allocatable",
        ),
        (
            SemanticType(
                "Float64",
                metadata={"fortran_pointer": True, "fortran_pointer_association": "runtime"},
                storage=SemanticStorageContract(kind="reference", mutable=True, pointer_depth=1),
            ),
            "Pointer",
        ),
    ],
)
def test_printer_emits_nullable_scalar_descriptor_boundary_projections(argument_type, projection):
    module = SemanticModule(
        name="pointer_descriptor_mod",
        functions=[
            SemanticFunction(
                name="read_pointer",
                native_name="read_pointer",
                arguments=[SemanticArgument("value", argument_type)],
                return_type=argument_type,
                projection=[ProjectionMapping(native_position=0, python_position=0)],
            )
        ],
    )

    code = emit_module(module)

    assert f"@native_call([{projection}(Arg(0))], result={projection}(Return(0)))" in code
    assert "value: Float64 | None" in code
    assert ") -> Float64 | None: ..." in code


def test_defaulted_scalar_descriptors_preserve_omitted_vs_none_in_generated_wrappers(tmp_path):
    loaded = parse_pyi_text(
        """
@native_call([Allocatable(Arg(0)), Pointer(Arg(1))])
def update(scale: Float64 | None = ..., target: Float64 | None = ...) -> None: ...
""",
        module_name="optional_scalar_descriptors",
    )
    scope = Scope(name=loaded.name, scope_type="module")
    codegen_module = semantic_ir_to_codegen_ast(loaded, scope)
    pipeline = BindingPipeline(
        Codegen(loaded.name, codegen_module, codegen_module.scope),
        loaded.name,
        "fortran",
        verbose=0,
    )

    pipeline.generate(str(tmp_path))
    bridge_path, c_wrapper_path, *_ = pipeline.write(tmp_path)
    bridge_source = bridge_path.read_text()
    c_wrapper = c_wrapper_path.read_text()

    assert "bound_scale_present" in bridge_source
    assert "bound_target_present" in bridge_source
    assert "if (c_associated(bound_scale_present)) then" in bridge_source
    assert "if (c_associated(bound_target_present)) then" in bridge_source
    assert "call update()" in bridge_source
    assert "call update(scale = scale_descriptor)" in bridge_source
    assert "call update(target = target_descriptor)" in bridge_source
    assert "call update(scale = scale_descriptor, target = target_descriptor" in bridge_source

    assert "scale_obj = NULL;" in c_wrapper
    assert "target_obj = NULL;" in c_wrapper
    assert "if (scale_obj != NULL)" in c_wrapper
    assert "scale_present = &scale_value;" in c_wrapper
    assert "if ((scale_obj != NULL) && (scale_obj != Py_None))" in c_wrapper
    assert "scale_nullable = &scale_value;" in c_wrapper
    assert "bind_c_update(scale_nullable, scale_present, target_nullable, target_present);" in c_wrapper
    assert "Omit to make the native optional dummy absent." in c_wrapper
    assert "Pass None for a present unallocated or unassociated descriptor." in c_wrapper
    assert "Default is None." not in c_wrapper


def test_printer_emits_callback_argument_abi_wrappers():
    printer = PyiPrinter()
    missing_reference = SemanticType(
        "Float64",
        storage=SemanticStorageContract(kind="reference", mutable=True, pointer_depth=1),
    )
    missing_array = SemanticType(
        "Float64",
        rank=1,
        shape=[":"],
        storage=SemanticStorageContract(
            kind="array",
            mutable=True,
            array=SemanticArrayContract(rank=1, shape=[":"]),
        ),
    )
    input_reference = SemanticType(
        "Int32",
        storage=SemanticStorageContract(kind="reference", read_only=True, pointer_depth=1),
    )
    output_array = SemanticType(
        "Float64",
        rank=1,
        shape=[":"],
        storage=SemanticStorageContract(
            kind="array",
            mutable=True,
            array=SemanticArrayContract(rank=1, shape=[":"]),
        ),
    )
    inout_array = SemanticType(
        "Float64",
        rank=1,
        shape=[":"],
        storage=SemanticStorageContract(
            kind="array",
            mutable=True,
            array=SemanticArrayContract(rank=1, shape=[":"]),
        ),
    )
    callback_arguments = [
        SemanticArgument(
            "value",
            SemanticType("Int32"),
            metadata={CALLBACK_DECLARATION_ACCESS_METADATA: "read"},
            origin=SemanticOrigin(metadata={"value": True}),
        ),
        SemanticArgument(
            "missing",
            missing_reference,
            metadata={CALLBACK_DECLARATION_ACCESS_METADATA: "unspecified"},
            origin=SemanticOrigin(metadata={"value": False}),
        ),
        SemanticArgument(
            "missing_array",
            missing_array,
            metadata={CALLBACK_DECLARATION_ACCESS_METADATA: "unspecified"},
            origin=SemanticOrigin(metadata={"value": False}),
        ),
        SemanticArgument(
            "read",
            input_reference,
            metadata={CALLBACK_DECLARATION_ACCESS_METADATA: "read"},
            origin=SemanticOrigin(metadata={"value": False}),
        ),
        SemanticArgument(
            "write",
            output_array,
            metadata={CALLBACK_DECLARATION_ACCESS_METADATA: "write"},
            origin=SemanticOrigin(metadata={"value": False}),
        ),
        SemanticArgument(
            "readwrite",
            inout_array,
            metadata={CALLBACK_DECLARATION_ACCESS_METADATA: "readwrite"},
            origin=SemanticOrigin(metadata={"value": False}),
        ),
    ]
    callback = SemanticType(
        "Callable",
        metadata={
            "arguments": [argument.semantic_type for argument in callback_arguments],
            "callback_arguments": callback_arguments,
            "return": SemanticType("None"),
        },
    )

    assert printer.emit(callback) == (
        "Callable[[Int32, PassByRef(Float64), Float64[:], In(Int32), Out(Float64[:]), InOut(Float64[:])], None]"
    )


def test_character_array_pyi_spelling_round_trips_fixed_and_deferred_lengths():
    source = """
module char_array_mod
contains
  subroutine use_labels(labels)
    character(len=4), intent(in) :: labels(:)
  end subroutine use_labels
  subroutine replace_names(names)
    character(len=:), allocatable, intent(inout) :: names(:)
  end subroutine replace_names
end module char_array_mod
"""
    semantic_module = fortran_module_to_semantic_module(parse_fortran_source(source))
    emitted = emit_module(semantic_module)

    assert "String[4][::]" in emitted
    assert "Allocatable[String[:][:]]" in emitted

    parsed = parse_pyi_text(emitted, module_name="char_array_mod")
    use_labels = next(func for func in parsed.functions if func.name == "use_labels")
    assert use_labels.arguments[0].semantic_type.metadata["fortran_character_length"] == "4"

    replace_names = next(func for func in parsed.functions if func.name == "replace_names")
    names_type = replace_names.arguments[0].semantic_type
    assert names_type.metadata["fortran_character_length"] == ":"
    assert names_type.storage.array.allocatable is True


def test_printer_projection_return_helpers_and_keyword_data_members():
    printer = PyiPrinter()
    argument = SemanticArgument(
        "x",
        SemanticType(
            "Float64",
            storage=SemanticStorageContract(kind="reference", mutable=True, pointer_depth=1),
        ),
        optional=True,
    )
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

    assert printer._projected_argument_return(argument, visible=True) == 'Returns["x", Addr(Float64)] | None'
    assert printer._named_return(plain) == 'Returns["value", Int32]'
    assert printer._projected_argument_return(argument, visible=False) == "Float64 | None"
    assert printer._projected_argument_return(plain, visible=False) == "Int32"
    assert "var['class']: Int32" in emit_module(module)
    assert "@native_call([Return(0)])" in emit_module(module)


def test_printer_rejects_each_unresolved_semantic_type_field():
    printer = PyiPrinter()
    message = "Cannot emit .pyi with unresolved semantic type 'Unknown'"

    with pytest.raises(ValueError) as unknown_name:
        printer.emit(SemanticType("Unknown", dtype="Int32"))
    with pytest.raises(ValueError) as unknown_dtype:
        printer.emit(SemanticType("Int32", dtype="Unknown"))

    assert str(unknown_name.value) == message
    assert str(unknown_dtype.value) == message


def test_printer_preserves_structured_class_and_decorator_layout():
    printer = PyiPrinter()
    decorated_method = SemanticMethod(
        name="lookup",
        return_type=SemanticType("Float64"),
        visibility="private",
        projection=[ProjectionMapping(native_position=0, result_position=0)],
    )
    cls = SemanticClass(
        name="thing",
        base_classes=["Opaque", "Protocol"],
        fields=[SemanticArgument("value", SemanticType("Int32"))],
        methods=[decorated_method, SemanticMethod(name="reset")],
    )
    decorated_function = SemanticFunction(
        name="wrapper",
        visibility="private",
        projection=[ProjectionMapping(native_position=0, result_position=0)],
    )

    assert (
        printer.emit(cls)
        == """class thing(Opaque, Protocol):
    value: Int32

    @private
    @native_call([Return(0)])
    def lookup(self) -> Float64: ...

    def reset(self) -> None: ..."""
    )
    assert (
        printer.emit(decorated_function)
        == """@private
@native_call([Return(0)])
def wrapper() -> None: ..."""
    )


def test_native_call_sorts_synthetic_entries_before_native_positions():
    projection = [
        ProjectionMapping(native_position=0, value_kind="literal", value={"type": "Int32", "value": 1}),
        ProjectionMapping(result_position=0),
    ]

    assert PyiPrinter()._native_call(projection) == "@native_call([Return(0), Int32(1)])"
