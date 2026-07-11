"""Tests split by stable ownership concept from `test_compile_time_values.py`."""

from tests.semantics.conversion.fortran._support import (
    FortranArgument,
    FortranDerivedType,
    FortranFile,
    FortranModule,
    FortranProcedureSignature,
    FortranProject,
    FortranToIRConverter,
    FortranUseMapping,
    FortranVariable,
    SemanticField,
    SemanticVariable,
    _requirement_unit_name,
    _resolve_compile_time_text,
    array_contract,
    asdict,
    fortran_file_to_semantic_modules,
    fortran_module_to_semantic_module,
    fortran_project_to_semantic_modules,
    get_class,
    get_function,
    has_constraint,
    parse_fortran_project,
    parse_fortran_source,
)


def test_converter_preserves_imported_derived_contexts_through_dispatch_paths():
    converter = FortranToIRConverter()
    imported_type = FortranVariable(name="state", base_type="derived", kind="local_state")
    imported_argument = FortranArgument(name="arg", base_type="derived", kind="local_state")
    local_field = FortranArgument(name="nested", base_type="derived", kind="container_t")
    dtype = FortranDerivedType(
        name="container_t",
        module="consumer",
        fields=[FortranArgument(name="state", base_type="derived", kind="local_state"), local_field],
        methods=["step"],
    )
    dtype.visibility = "private"
    proc = FortranProcedureSignature(
        name="step",
        kind="subroutine",
        module="consumer",
        arguments=[imported_argument],
    )
    module = FortranModule(
        name="consumer",
        uses={
            "plain_mod": [],
            "types_mod": [FortranUseMapping(source="state_t", target="local_state")],
        },
        variables=[FortranVariable(name="module_state", base_type="derived", kind="local_state")],
        procedures=[proc],
        derived_types=[dtype],
        private_symbols=["container_t"],
    )
    parsed_file = FortranFile(modules=[module])
    project = FortranProject(files=[parsed_file])
    context = converter._module_derived_type_context(module)

    semantic_module = converter.visit(module)
    semantic_class = converter.visit(dtype, derived_type_context=context)
    external_ref = {
        "name": "state_t",
        "local_name": "local_state",
        "origin_module": "types_mod",
        "wrapped": False,
        "representation": "opaque",
    }

    assert converter.visit(imported_type, derived_type_context=context).metadata["external_type_ref"] == external_ref
    assert (
        converter.visit(imported_argument, derived_type_context=context).semantic_type.metadata["external_type_ref"]
        == external_ref
    )
    assert converter.visit(proc, derived_type_context=context).arguments[0].semantic_type.metadata[
        "external_type_ref"
    ] == (external_ref)
    assert (
        converter.visit(parsed_file)[0].classes[0].fields[0].semantic_type.metadata["external_type_ref"] == external_ref
    )
    assert converter.visit(project)[0].classes[0].fields[0].semantic_type.metadata["external_type_ref"] == external_ref
    assert semantic_module.classes[0].fields[0].semantic_type.metadata["external_type_ref"] == external_ref
    assert "external_type_ref" not in semantic_module.classes[0].fields[1].semantic_type.metadata
    assert semantic_class.fields[0].semantic_type.metadata["external_type_ref"] == external_ref
    assert isinstance(semantic_class.fields[0], SemanticField)
    assert semantic_class.visibility == "private"
    assert asdict(semantic_class.origin) == {
        "source_language": "fortran",
        "native_name": "container_t",
        "native_scope": "consumer",
        "source_kind": "derived_type",
        "source_type": None,
        "source_location": {},
        "metadata": {},
    }
    semantic_proc = semantic_module.functions[0]
    assert semantic_proc.native_name == "step"
    assert semantic_proc.locals == []
    assert semantic_proc.arguments[0].semantic_type.metadata["external_type_ref"] == external_ref
    assert semantic_module.variables[0].semantic_type.metadata["external_type_ref"] == external_ref
    assert isinstance(semantic_module.variables[0], SemanticVariable)
    assert [method.name for method in semantic_module.classes[0].methods] == ["step"]
    assert semantic_module.classes[0].methods[0].projection == semantic_proc.projection
    assert asdict(semantic_module.classes[0].methods[0].origin) == asdict(semantic_proc.origin)
    assert asdict(semantic_proc.origin) == {
        "source_language": "fortran",
        "native_name": "step",
        "native_scope": "consumer",
        "source_kind": "subroutine",
        "source_type": None,
        "source_location": {},
        "metadata": {},
    }
    assert [asdict(mapping) for mapping in semantic_proc.projection] == [
        {
            "python_name": "arg",
            "native_name": "arg",
            "native_position": 0,
            "python_position": 0,
            "result_position": None,
            "value_kind": "",
            "value": None,
        }
    ]
    assert asdict(semantic_module.origin) == {
        "source_language": "fortran",
        "native_name": "consumer",
        "native_scope": "consumer",
        "source_kind": "module",
        "source_type": None,
        "source_location": {},
        "metadata": {},
    }
    assert converter.visit(FortranDerivedType(name="default_t")).visibility == "public"
    assert converter.visit(FortranVariable(name="local", base_type="derived", kind="state_t")).name == "state_t"


def test_converter_normalizes_wrapped_types_and_resolves_wildcard_imports():
    converter = FortranToIRConverter(wrapped_derived_types={("types_mod", "state_t")})
    module = FortranModule(name="consumer", uses={"OTHER_MOD": [], "TYPES_MOD": []})
    context = converter._module_derived_type_context(module)

    state = converter.visit(
        FortranArgument(name="state", base_type="derived", kind="state_t"),
        derived_type_context=context,
    ).semantic_type
    opaque_context = converter._module_derived_type_context(FortranModule(name="consumer", uses={"OPAQUE_MOD": []}))
    opaque = converter.visit(
        FortranArgument(name="opaque", base_type="derived", kind="opaque_t"),
        derived_type_context=opaque_context,
    ).semantic_type
    merged = FortranToIRConverter()._with_additional_wrapped_types({("TYPES_MOD", "State_T")})

    assert state.metadata["external_type_ref"] == {
        "name": "state_t",
        "local_name": "state_t",
        "origin_module": "TYPES_MOD",
        "wrapped": True,
        "representation": "wrapped",
    }
    assert opaque.metadata["external_type_ref"] == {
        "name": "opaque_t",
        "local_name": "opaque_t",
        "origin_module": "OPAQUE_MOD",
        "wrapped": False,
        "representation": "opaque",
    }
    assert merged.wrapped_derived_types == {("types_mod", "state_t")}
    custom_type_map = {("integer", None): "CustomInt"}
    configured = FortranToIRConverter(type_map=custom_type_map, compile_time_values={"rk": 8})
    configured = configured._with_additional_wrapped_types({("types_mod", "state_t")})
    assert configured.type_map is custom_type_map
    assert configured.compile_time_values == {"rk": "8"}
    assert FortranToIRConverter(compile_time_values={" ": 4, " RK ": 8}).compile_time_values == {"rk": "8"}
    assert _resolve_compile_time_text("n + missing", {"n": "4"}) == "4 + missing"
    assert _resolve_compile_time_text("N + missing", {"n": "4"}) == "4 + missing"
    assert _requirement_unit_name(module="m") == "m"
    assert _requirement_unit_name(unit_name="step") == "step"
    assert _requirement_unit_name() == "<source>"


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

    assert K.semantic_type.rank == 2

    assert array_contract(K.semantic_type).order == "ORDER_F"

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
    assert array_contract(semantic_arg.semantic_type).allocatable is True
    assert semantic_proc.projection[0].python_position == 0
    assert semantic_dtype.base_classes == ["base"]
    assert semantic_module.imports == ["iso_c_binding"]
    assert semantic_dtype.visibility == "private"
    assert semantic_proc.visibility == "public"
    assert semantic_file_modules[0].name == "m"


def test_scalar_character_inout_is_projected_as_replacement_return():
    parsed = parse_fortran_source(
        """
module chars
contains
  subroutine normalize(name)
    character(len=8), intent(inout) :: name
  end subroutine normalize
end module chars
"""
    )

    func = get_function(fortran_module_to_semantic_module(parsed), "normalize")
    mapping = func.projection[0]

    assert func.arguments[0].semantic_type.name == "String"
    assert mapping.python_position == 0
    assert mapping.native_position == 0
    assert mapping.result_position == 0


def test_imported_derived_type_is_an_opaque_external_reference_by_default():
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
    particle = get_function(module, "move").arguments[0].semantic_type

    assert module.classes == []
    assert particle.storage.kind == "reference"
    assert particle.metadata["external_type_ref"] == {
        "name": "particle",
        "local_name": "particle",
        "origin_module": "types_mod",
        "wrapped": False,
        "representation": "opaque",
    }
    wrapped_modules = fortran_file_to_semantic_modules(
        parsed,
        wrapped_derived_types={("types_mod", "particle")},
    )
    wrapped_particle = get_function(wrapped_modules[0], "move").arguments[0].semantic_type
    assert wrapped_particle.metadata["external_type_ref"]["wrapped"] is True
    assert wrapped_particle.metadata["external_type_ref"]["representation"] == "wrapped"
    wrapped_module = fortran_module_to_semantic_module(
        parsed,
        wrapped_derived_types={("types_mod", "particle")},
    )
    assert (
        get_function(wrapped_module, "move").arguments[0].semantic_type.metadata["external_type_ref"]["wrapped"] is True
    )


def test_explicit_project_target_resolves_imported_derived_type_without_reexport():
    project = parse_fortran_project(
        {
            "types_mod.f90": """
module types_mod
  type :: particle
    real :: mass
  end type particle
end module types_mod
""",
            "physics.f90": """
module physics
  use types_mod, only: particle
contains
  subroutine move(p)
    type(particle), intent(inout) :: p
  end subroutine move
end module physics
""",
        }
    )

    modules = {module.name: module for module in fortran_project_to_semantic_modules(project)}
    particle = get_function(modules["physics"], "move").arguments[0].semantic_type

    assert [cls.name for cls in modules["types_mod"].classes] == ["particle"]
    assert modules["physics"].classes == []
    assert sum(cls.name == "particle" for module in modules.values() for cls in module.classes) == 1
    assert particle.metadata["external_type_ref"] == {
        "name": "particle",
        "local_name": "particle",
        "origin_module": "types_mod",
        "wrapped": True,
        "representation": "wrapped",
    }
