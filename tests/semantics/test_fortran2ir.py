import json
from dataclasses import asdict

import pytest

from fortran_parser.models import (
    FortranArgument,
    FortranBlockData,
    FortranDerivedType,
    FortranFile,
    FortranModule,
    FortranProgram,
    FortranProcedureSignature,
    FortranSubmodule,
    FortranUseMapping,
    FortranVariable,
)
from x2py import parse_fortran_file as parse_fortran_source

from semantics.fortran2ir import (
    FortranToIRConverter,
    _compile_time_requirement_message,
    _iter_fortran_variable_contexts,
    collect_semantic_compile_time_requirements,
    fortran_file_to_semantic_modules,
    fortran_module_to_semantic_module,
    resolve_semantic_compile_time_values,
)
from semantics import models as semantic_models

from semantics.models import (
    ProjectionMapping,
    SemanticArgument,
    SemanticMethod,
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


def test_converter_visitor_and_compatibility_methods_cover_public_paths():
    converter = FortranToIRConverter()
    scale = FortranVariable(name="scale", base_type="real", kind="8", is_parameter=True)
    arg = FortranArgument(
        name="x",
        base_type="real",
        kind="8",
        intent="unknown",
        allocatable=True,
        pointer=True,
    )
    proc = FortranProcedureSignature(name="work", kind="subroutine", arguments=[arg])
    base = FortranDerivedType(name="base_t")
    dtype = FortranDerivedType(
        name="child_t",
        fields=[FortranArgument(name="payload", base_type="derived", kind="base_t")],
        extends=base,
    )
    module = FortranModule(
        name="m",
        uses={
            "iso_c_binding": [FortranUseMapping(source="c_int", target="i32")],
            "plain_import": [],
        },
        variables=[scale],
        procedures=[proc],
        derived_types=[dtype],
        private_symbols=["work"],
    )
    parsed = FortranFile(filename="/tmp/standalone_source.f90", modules=[module], procedures=[proc])

    assert converter.visit(parsed).name == "m"
    assert converter.visit(module).functions[0].visibility == "private"
    assert converter.visit(proc, visibility="private").visibility == "private"

    semantic_arg = converter.visit(arg)
    assert semantic_arg.intent == "inout"
    assert has_constraint(semantic_arg.semantic_type, "Allocatable")
    assert has_constraint(semantic_arg.semantic_type, "Pointer")

    semantic_var = converter.variable_to_semantic_type(scale)
    assert semantic_var.name == "Float64"
    assert has_constraint(semantic_var, "Constant")
    assert converter.argument_to_semantic_argument(arg).name == "x"
    assert converter.procedure_to_semantic_function(proc).name == "work"
    assert converter.derived_type_to_semantic_class(dtype, procedure_lookup={}).base_classes == ["base_t"]
    assert converter.module_to_semantic_module(module).imports[0].items[0].target == "i32"

    modules = converter.file_to_semantic_modules(parsed)
    assert [module.name for module in modules] == ["m", "standalone_source"]


def test_converter_rejects_unsupported_inputs_and_missing_derived_type_names():
    converter = FortranToIRConverter()

    with pytest.raises(TypeError, match="Unsupported Fortran parse object"):
        converter.visit(object())

    with pytest.raises(TypeError, match="Unsupported Fortran parse object"):
        converter.first_module(object())

    with pytest.raises(ValueError, match="Expected at least one Fortran module"):
        converter.first_module(FortranFile())

    from_list = converter.first_module(
        [
            FortranProcedureSignature(
                name="inside",
                kind="subroutine",
                module="legacy_mod",
                in_interface=True,
            ),
            FortranProcedureSignature(name="outside", kind="subroutine"),
        ]
    )
    assert from_list.name == "legacy_mod"
    assert [proc.name for proc in from_list.procedures] == ["outside"]

    with pytest.raises(ValueError, match="missing concrete type name"):
        converter.visit_variable(FortranVariable(name="state", base_type="derived"))

    with pytest.raises(ValueError, match="Unknown Fortran datatype"):
        converter.visit_variable(FortranVariable(name="x", base_type="unknown"))

    with pytest.raises(ValueError, match="Unsupported Fortran semantic type"):
        converter.visit_variable(FortranVariable(name="x", base_type="real", kind="selected_real_kind(33)"))


def test_converter_covers_derived_dispatch_methods_and_kind_edges():
    converter = FortranToIRConverter()
    callback = SemanticFunction(
        name="advance",
        native_name="advance_impl",
        arguments=[SemanticArgument("state", SemanticType("particle_t"))],
        return_type=SemanticType("Int32"),
        contracts=[SemanticConstraint("Pure")],
        visibility="private",
    )
    dtype = FortranDerivedType(
        name="particle_t",
        fields=[FortranArgument(name="id", base_type="integer")],
        methods=["missing_binding", "advance"],
    )

    semantic_class = converter.visit(dtype, procedure_lookup={"advance": callback})

    assert semantic_class.methods == [
        SemanticMethod(
            name="advance",
            native_name="advance_impl",
            arguments=callback.arguments,
            return_type=callback.return_type,
            contracts=callback.contracts,
            visibility="private",
        )
    ]
    assert converter.visit(FortranVariable(name="count", base_type="integer")).name == "Int32"
    assert converter.first_module([FortranProcedureSignature(name="hidden", kind="subroutine", in_interface=True)]).name == ""
    assert FortranToIRConverter._literal_kind_key("kind(1.0q0)") == "16"
    assert FortranToIRConverter._literal_kind_key("kind(1)") is None


def test_semantic_compile_time_requirements_can_be_supplied_for_kind_selection():
    source = """
module solver_mod
  integer, parameter :: rk = selected_real_kind(12)
contains
subroutine scale(x)
  real(kind=rk), intent(inout) :: x
end subroutine scale
end module solver_mod
"""
    parsed = parse_fortran_source(source)

    with pytest.raises(ValueError, match="Unsupported Fortran semantic type"):
        fortran_module_to_semantic_module(parsed)

    requirements = collect_semantic_compile_time_requirements(parsed)
    assert {
        (item["code"], item["symbol"], item["expression"])
        for item in requirements
    } >= {
        ("parameter_value", "rk", "selected_real_kind(12)"),
        ("unsupported_kind", "x", "selected_real_kind(12)"),
    }

    module = fortran_module_to_semantic_module(
        parsed,
        compile_time_values={"selected_real_kind(12)": 8},
    )
    arg_type = get_function(module, "scale").arguments[0].semantic_type
    assert arg_type.name == "Float64"


def test_semantic_compile_time_requirements_cover_all_parser_contexts():
    proc = FortranProcedureSignature(
        name="step",
        kind="function",
        module="solver_mod",
        arguments=[FortranArgument(name="x", base_type="real", kind="rk")],
        result=FortranArgument(name="r", base_type="real", kind="rk"),
        variables={
            "scratch": FortranVariable(name="scratch", base_type="real", kind="rk"),
        },
    )
    dtype = FortranDerivedType(
        name="state_t",
        module="solver_mod",
        fields=[FortranArgument(name="mass", base_type="real", kind="rk")],
    )
    parsed = FortranFile(
        variables=[FortranVariable(name="file_param", base_type="integer", is_parameter=True, symbolic_value="n + 1")],
        modules=[
            FortranModule(
                name="solver_mod",
                variables=[
                    FortranVariable(name="rk", base_type="integer", is_parameter=True, symbolic_value="selected_real_kind(12)"),
                    FortranVariable(name="scale", base_type="real", kind="rk"),
                ],
                procedures=[proc],
                derived_types=[dtype],
            )
        ],
        submodules=[
            FortranSubmodule(
                name="solver_child",
                parent="solver_mod",
                variables=[FortranVariable(name="child_scale", base_type="real", kind="rk")],
                procedures=[FortranProcedureSignature(name="child_step", kind="subroutine", arguments=[FortranArgument(name="y", base_type="real", kind="rk")])],
                derived_types=[FortranDerivedType(name="child_t", fields=[FortranArgument(name="value", base_type="real", kind="rk")])],
            )
        ],
        programs=[
            FortranProgram(
                variables=[FortranVariable(name="program_scale", base_type="real", kind="rk")],
                procedures=[FortranProcedureSignature(name="program_step", kind="subroutine", arguments=[FortranArgument(name="z", base_type="real", kind="rk")])],
            )
        ],
        block_data_units=[
            FortranBlockData(variables=[FortranVariable(name="saved_scale", base_type="real", kind="rk")])
        ],
        procedures=[FortranProcedureSignature(name="free_step", kind="subroutine", arguments=[FortranArgument(name="q", base_type="real", kind="rk")])],
        derived_types=[FortranDerivedType(name="free_t", fields=[FortranArgument(name="payload", base_type="real", kind="rk")])],
    )

    contexts = [ctx for _var, ctx in _iter_fortran_variable_contexts(parsed)]
    requirements = collect_semantic_compile_time_requirements(parsed)
    supplied = collect_semantic_compile_time_requirements(
        parsed,
        compile_time_values={"rk": 8, "selected_real_kind(12)": 8, "n": 2},
    )

    assert {"file", "module", "submodule", "program", "block_data", "procedure", "derived_type"} <= {
        ctx["unit_kind"] for ctx in contexts
    }
    assert {ctx["role"] for ctx in contexts} >= {"variable", "argument", "result", "field"}
    assert ("parameter_value", "rk", "selected_real_kind(12)") in {
        (item["code"], item["symbol"], item["expression"])
        for item in requirements
    }
    assert any(item["code"] == "unsupported_kind" and item["symbol"] == "scale" for item in requirements)
    assert supplied == []
    assert _compile_time_requirement_message("other", "n", "n + 1") == "Compile-time value required for 'n'."


def test_resolve_semantic_compile_time_values_rewrites_shapes_and_constraints():
    module = SemanticModule(
        name="shape_mod",
        variables=[
            SemanticArgument(
                name="values",
                semantic_type=SemanticType(
                    name="Float64",
                    dtype="Float64",
                    rank=1,
                    shape=["1:n"],
                    constraints=[SemanticConstraint("Shape", ["1:n"])],
                ),
            )
        ],
    )

    resolved = resolve_semantic_compile_time_values(module, {"n": 8})

    assert module.variables[0].semantic_type.shape == ["1:n"]
    assert resolved.variables[0].semantic_type.shape == ["1:8"]
    assert resolved.variables[0].semantic_type.constraints[0].arguments == ["1:8"]


def test_resolve_semantic_compile_time_values_handles_nested_modules():
    module = SemanticModule(
        name="nested_mod",
        variables=[
            SemanticArgument(
                name="values",
                semantic_type=SemanticType(
                    name="Float64",
                    dtype="Float64",
                    rank=1,
                    shape=["n"],
                    constraints=[SemanticConstraint("Shape", [{"extent": "n"}])],
                    metadata={"bounds": ("n", ["m"])},
                ),
                default_value="n",
                metadata={"alias": "m"},
            )
        ],
        functions=[
            SemanticFunction(
                name="step",
                arguments=[
                    SemanticArgument(
                        name="x",
                        semantic_type=SemanticType("Float64", rank=1, shape=["m"]),
                        metadata={"scale": "n"},
                    )
                ],
                projection=[ProjectionMapping(value={"shape": ["n", ("m",)]})],
                metadata={"work": ["n", {"inner": "m"}]},
            ),
            SemanticFunction(
                name="with_result",
                return_type=SemanticType("Int32", metadata={"extent": "n"}),
            ),
        ],
        classes=[
            SemanticClass(
                name="state_t",
                fields=[
                    SemanticArgument(
                        name="field",
                        semantic_type=SemanticType("Float64", shape=["n"]),
                        default_value="m",
                    )
                ],
                methods=[
                    SemanticMethod(
                        name="touch",
                        arguments=[SemanticArgument("self", SemanticType("state_t", metadata={"n": "n"}))],
                        return_type=SemanticType("Int32", metadata={"m": "m"}),
                        projection=[ProjectionMapping(value=("n", {"m": "m"}))],
                        metadata={"method": "n"},
                    )
                ],
                metadata={"class": "m"},
            )
        ],
        metadata={"module": ["n", ("m",)]},
    )

    resolved = resolve_semantic_compile_time_values([module], {"n": 4, "m": 2})

    assert module.variables[0].semantic_type.shape == ["n"]
    resolved_module = resolved[0]
    assert resolved_module.variables[0].semantic_type.shape == ["4"]
    assert resolved_module.variables[0].semantic_type.constraints[0].arguments == [{"extent": "4"}]
    assert resolved_module.variables[0].semantic_type.metadata == {"bounds": ("4", ["2"])}
    assert resolved_module.functions[0].projection[0].value == {"shape": ["4", ("2",)]}
    assert resolved_module.functions[1].return_type.metadata == {"extent": "4"}
    assert resolved_module.classes[0].methods[0].projection[0].value == ("4", {"m": "2"})
    assert resolved_module.metadata == {"module": ["4", ("2",)]}


def test_iso_c_module_variable_kinds_map_to_semantic_types():
    source = """
module constants_mod
  use iso_c_binding, only: c_int, c_double
  integer(kind=c_int), parameter :: nmax = 100
  real(kind=c_double), dimension(3) :: origin
end module constants_mod
"""

    parsed = parse_fortran_source(source)
    module = fortran_module_to_semantic_module(parsed)
    variables = {var.name: var.semantic_type for var in module.variables}

    assert variables["nmax"].name == "Int32"
    assert has_constraint(variables["nmax"], "Constant")
    assert variables["origin"].name == "Float64"
    assert variables["origin"].shape == ["3"]


def test_intrinsic_builtin_kinds_map_to_semantic_types():
    converter = FortranToIRConverter()
    cases = [
        (FortranVariable(name="i1", base_type="integer", kind="1"), "Int8"),
        (FortranVariable(name="i2", base_type="integer", kind="2"), "Int16"),
        (FortranVariable(name="i8", base_type="integer", kind="8"), "Int64"),
        (FortranVariable(name="r4", base_type="real", kind="4"), "Float32"),
        (FortranVariable(name="r16", base_type="real", kind="16"), "Float128"),
        (FortranVariable(name="c8", base_type="complex", kind="8"), "Complex128"),
        (FortranVariable(name="ciso", base_type="complex", kind="c_double_complex"), "Complex128"),
        (FortranVariable(name="flag", base_type="logical", kind="8"), "Bool"),
        (FortranVariable(name="text", base_type="character", kind="len=12, kind=c_char"), "String"),
        (FortranVariable(name="callback", base_type="procedure", kind="f_iface"), "Procedure"),
    ]

    for variable, expected in cases:
        assert converter.visit_variable(variable).name == expected


def test_semantic_model_helpers_cover_projection_and_canonical_edge_cases():
    assert SemanticFunction("f") != SemanticMethod("f")
    assert semantic_models._semantic_type_key(None, {}) is None
    assert semantic_models._canonical_expression(
        ["n", ("m",), {"extent": "n + m"}],
        {"n": "$0", "m": "$1"},
    ) == ["$0", ("$1",), {"extent": "$0 + $1"}]

    projection = [
        ProjectionMapping(native_position=0, python_position=1, intent="inout"),
        ProjectionMapping(native_position=1, python_position=None, intent="out"),
        ProjectionMapping(native_position=2, result_position=0, intent="in"),
        ProjectionMapping(native_position=3, python_position=None, intent="in"),
        ProjectionMapping(
            native_position=4,
            value_kind="shape",
            value={"value": ["n", ("m",)], "dim": {"extent": "n + m"}},
            intent="in",
        ),
    ]

    key = semantic_models._projection_key(projection, {"n": "$0", "m": "$1"})

    assert len(key) == len(projection)
    assert key[-1][4] == (("dim", (("extent", "$0 + $1"),)), ("value", ("$0", ("$1",))))


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
