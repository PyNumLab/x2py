import json
from dataclasses import asdict
from pathlib import Path

import pytest

from x2py.fortran_parser.models import (
    FortranArgument,
    FortranBlockData,
    FortranDerivedType,
    FortranFile,
    FortranModule,
    FortranProgram,
    FortranProject,
    FortranProcedureSignature,
    FortranSubmodule,
    FortranUseMapping,
    FortranVariable,
)
from x2py import parse_fortran_file as parse_fortran_source
from x2py import parse_fortran_project

from x2py.semantics.fortran2ir import (
    FortranToIRConverter,
    _compile_time_requirement_message,
    _iter_fortran_variable_contexts,
    _requirement_unit_name,
    _resolve_compile_time_text,
    collect_fortran_type_storage_requirements,
    collect_semantic_compile_time_requirements,
    fortran_type_storage_expression,
    fortran_file_to_semantic_modules,
    fortran_module_to_semantic_module,
    fortran_project_to_semantic_modules,
    resolve_semantic_compile_time_values,
)
from x2py.semantics import models as semantic_models
from x2py.semantics.readiness import assess_semantic_wrap_readiness

from x2py.semantics.models import (
    ProjectionMapping,
    SemanticArgument,
    SemanticField,
    SemanticMethod,
    SemanticModule,
    SemanticClass,
    SemanticFunction,
    SemanticConstraint,
    SemanticType,
    SemanticVariable,
)

OPERATOR_F90_SOURCE = Path(__file__).parents[1] / "wrapper" / "foperators_f90.f90"


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


def array_contract(semantic_type: SemanticType):
    assert semantic_type.storage is not None
    assert semantic_type.storage.array is not None
    return semantic_type.storage.array


def test_bind_c_name_and_value_calling_convention_reach_semantic_ir():
    parsed = parse_fortran_source(
        """
module c_api
  use iso_c_binding
contains
  integer(c_int) function renamed(n) bind(C, name="x2py_renamed") result(res)
    integer(c_int), value, intent(in) :: n
    res = n
  end function renamed
end module c_api
"""
    )

    module = fortran_module_to_semantic_module(parsed.modules[0])
    renamed = get_function(module, "renamed")

    assert renamed.metadata["fortran_bind_c"] is True
    assert renamed.metadata["fortran_bind_c_name"] == "x2py_renamed"
    assert renamed.arguments[0].origin.metadata["value"] is True
    assert renamed.arguments[0].semantic_type.storage is None


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
    assert converter.visit(proc).visibility == "public"

    semantic_arg = converter.visit(arg)
    assert semantic_arg.intent == "inout"
    assert semantic_arg.semantic_type.storage.kind == "reference"
    assert semantic_arg.semantic_type.storage.mutable is True
    assert semantic_arg.visibility == "public"
    assert semantic_arg.origin.source_language == "fortran"
    assert semantic_arg.origin.native_name == "x"
    assert semantic_arg.origin.source_kind == "argument"

    semantic_var = converter.variable_to_semantic_type(scale)
    assert semantic_var.name == "Float64"
    assert has_constraint(semantic_var, "Constant")
    assert converter.argument_to_semantic_argument(arg).name == "x"
    assert converter.procedure_to_semantic_function(proc).name == "work"
    assert converter.procedure_to_semantic_function(proc).visibility == "public"
    assert converter.derived_type_to_semantic_class(dtype, procedure_lookup={}).base_classes == ["base_t"]
    assert converter.module_to_semantic_module(module).imports[0].items[0].target == "i32"

    modules = converter.file_to_semantic_modules(parsed)
    assert [module.name for module in modules] == ["m", "standalone_source"]
    assert converter.visit(FortranProject(files=[parsed]))[0].name == "m"


def test_converter_preserves_imported_derived_contexts_through_dispatch_paths():
    converter = FortranToIRConverter()
    imported_type = FortranVariable(name="state", base_type="derived", kind="local_state")
    imported_argument = FortranArgument(name="arg", base_type="derived", kind="local_state", intent="inout")
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
    assert converter.visit(parsed_file).classes[0].fields[0].semantic_type.metadata["external_type_ref"] == external_ref
    assert converter.visit(project)[0].classes[0].fields[0].semantic_type.metadata["external_type_ref"] == external_ref
    assert semantic_module.classes[0].fields[0].semantic_type.metadata["external_type_ref"] == external_ref
    assert "external_type_ref" not in semantic_module.classes[0].fields[1].semantic_type.metadata
    assert semantic_class.fields[0].semantic_type.metadata["external_type_ref"] == external_ref
    assert isinstance(semantic_class.fields[0], SemanticField)
    assert [field.intent for field in semantic_class.fields] == ["in", "in"]
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
    assert semantic_module.variables[0].intent == "in"
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
            "intent": "inout",
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
    assert converter.visit_derived_type(FortranDerivedType(name="default_t")).visibility == "public"
    assert (
        converter.visit_variable(FortranVariable(name="local", base_type="derived", kind="state_t")).name == "state_t"
    )


def test_converter_normalizes_wrapped_types_and_resolves_wildcard_imports():
    converter = FortranToIRConverter(wrapped_derived_types={("types_mod", "state_t")})
    module = FortranModule(name="consumer", uses={"OTHER_MOD": [], "TYPES_MOD": []})
    context = converter._module_derived_type_context(module)

    state = converter.visit_argument(
        FortranArgument(name="state", base_type="derived", kind="state_t"),
        derived_type_context=context,
    ).semantic_type
    opaque_context = converter._module_derived_type_context(FortranModule(name="consumer", uses={"OPAQUE_MOD": []}))
    opaque = converter.visit_argument(
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


def test_converter_rejects_unsupported_inputs_and_missing_derived_type_names():
    converter = FortranToIRConverter()

    with pytest.raises(TypeError) as error:
        converter.visit(object())
    assert str(error.value) == "Unsupported Fortran parse object: <class 'object'>"

    with pytest.raises(TypeError, match="Unsupported Fortran parse object"):
        converter.first_module(object())

    with pytest.raises(ValueError) as error:
        converter.first_module(FortranFile())
    assert str(error.value) == "Expected at least one Fortran module in parsed file"

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

    with pytest.raises(ValueError) as error:
        converter.visit_variable(FortranVariable(name="x", base_type="real", kind="selected_real_kind(33)"))
    assert str(error.value) == "Unsupported Fortran semantic type for variable 'x': real(kind=selected_real_kind(33))"


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
            passed_object_name="state",
            passed_object_position=0,
        )
    ]
    assert converter.visit(FortranVariable(name="count", base_type="integer")).name == "Int32"


def test_converter_preserves_module_and_type_bound_generic_overload_sets():
    source = """
module generic_mod
  private
  public :: box, convert
  interface convert
    module procedure convert_integer, convert_real
  end interface convert
  type :: box
  contains
    procedure, private :: set_integer
    procedure, private :: set_real
    generic, public :: set => set_integer, set_real
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
    module = FortranToIRConverter().visit_module(parse_fortran_source(source).modules[0])

    assert [(item.name, [proc.name for proc in item.procedures]) for item in module.overload_sets] == [
        ("convert", ["convert_integer", "convert_real"])
    ]
    assert all(proc.visibility == "public" for proc in module.overload_sets[0].procedures)
    box = module.classes[0]
    assert [(item.name, [proc.name for proc in item.procedures]) for item in box.overload_sets] == [
        ("set", ["set_integer", "set_real"])
    ]
    assert all(proc.visibility == "public" for proc in box.overload_sets[0].procedures)


def test_converter_preserves_allocatable_target_metadata():
    source = """
module alloc_target_mod
  real(8), allocatable, target :: values(:)
  type :: box
    real(8), allocatable :: field(:)
  end type box
end module alloc_target_mod
"""
    module = FortranToIRConverter().visit_module(parse_fortran_source(source).modules[0])

    values = module.variables[0]
    assert values.name == "values"
    assert values.semantic_type.storage.array.allocatable is True
    assert values.semantic_type.metadata["fortran_target"] is True

    field = module.classes[0].fields[0]
    assert field.semantic_type.storage.array.allocatable is True
    assert "fortran_target" not in field.semantic_type.metadata


def test_converter_reports_missing_generic_target_as_readiness_blocker():
    converter = FortranToIRConverter()
    source = """
module generic_mod
  interface convert
    module procedure missing
  end interface convert
end module generic_mod
"""
    module = converter.visit_module(parse_fortran_source(source).modules[0])
    report = assess_semantic_wrap_readiness(module)

    assert module.overload_sets[0].procedures == []
    blocker = next(
        blocker for blocker in report["wrappability_blockers"] if blocker["code"] == "fortran_generic_target_unresolved"
    )
    assert blocker["items"] == [
        {
            "owner": "generic_mod",
            "item": "generic_mod",
            "generic": "convert",
            "detail": "references missing specific procedure(s)",
            "missing_targets": ["missing"],
        }
    ]
    assert (
        converter.first_module([FortranProcedureSignature(name="hidden", kind="subroutine", in_interface=True)]).name
        == ""
    )
    assert FortranToIRConverter._literal_kind_key("kind(1.0q0)") == "16"
    assert FortranToIRConverter._literal_kind_key("kind(1)") is None


def test_converter_leaves_defined_operators_and_assignment_for_operator_lowering():
    source = """
module operator_mod
  interface operator(+)
    module procedure add_values
  end interface operator(+)
  interface assignment(=)
    module procedure assign_value
  end interface assignment(=)
contains
  integer function add_values(left, right)
    integer :: left, right
    add_values = left + right
  end function add_values
  subroutine assign_value(left, right)
    integer :: left, right
    left = right
  end subroutine assign_value
end module operator_mod
"""
    module = FortranToIRConverter().visit_module(parse_fortran_source(source).modules[0])

    assert module.overload_sets == []


def test_converter_preserves_defined_operators_assignment_and_type_bound_operators():
    module = FortranToIRConverter().visit_module(
        parse_fortran_source(
            OPERATOR_F90_SOURCE.read_text(),
            filename=str(OPERATOR_F90_SOURCE),
        ).modules[0]
    )

    assert [(item.name, len(item.procedures)) for item in module.overload_sets] == [("convert", 2)]
    classes = {cls.name: cls for cls in module.classes}
    vector_sets = {item.name: item for item in classes["vector"].overload_sets}
    assert set(vector_sets) == {
        "__add__",
        "__pos__",
        "__sub__",
        "__neg__",
        "__mul__",
        "__truediv__",
        "__pow__",
        "__eq__",
        "__ne__",
        "__lt__",
        "__le__",
        "__gt__",
        "__ge__",
        "__and__",
        "__or__",
        "__invert__",
        "operator_dot",
        "r_operator_shift",
        "assign",
    }
    assert [procedure.name for procedure in vector_sets["__add__"].procedures] == [
        "add_vectors",
        "add_vector_integer",
        "add_vector_real",
        "add_real_vector",
        "add_vector_array",
        "add_vector_offset",
    ]
    reflected = next(
        procedure for procedure in vector_sets["__add__"].procedures if procedure.name == "add_real_vector"
    )
    assert reflected.metadata["python_method_name"] == "__radd__"
    assert reflected.metadata["python_bound_position"] == 1
    assert reflected.metadata["fortran_generic_name"] == "operator(+)"
    assert vector_sets["assign"].procedures[0].metadata["fortran_generic_name"] == "assignment(=)"
    assert vector_sets["operator_dot"].procedures[0].metadata["python_method_name"] == "operator_dot"
    assert vector_sets["r_operator_shift"].procedures[0].metadata["python_method_name"] == "r_operator_shift"

    assert [
        (item.name, [procedure.name for procedure in item.procedures]) for item in classes["counter"].overload_sets
    ] == [("__add__", ["counter_add_integer"])]


def test_converter_reports_invalid_defined_assignment_as_readiness_blocker():
    source = """
module invalid_assignment
  interface assignment(=)
    module procedure assign_value
  end interface assignment(=)
  type :: box
    integer :: value
  end type box
contains
  subroutine assign_value(left, right)
    type(box), intent(in) :: left
    integer, intent(in) :: right
  end subroutine assign_value
end module invalid_assignment
"""
    module = FortranToIRConverter().visit_module(parse_fortran_source(source).modules[0])
    report = assess_semantic_wrap_readiness(module)
    blocker = next(
        blocker for blocker in report["wrappability_blockers"] if blocker["code"] == "fortran_defined_generic_invalid"
    )

    assert blocker["items"][0]["generic"] == "assignment(=)"
    assert "intent(out) or intent(inout)" in blocker["items"][0]["detail"]


def test_converter_reports_missing_defined_operator_target_as_readiness_blocker():
    source = """
module missing_operator
  type :: box
    integer :: value
  end type box
  interface operator(+)
    module procedure missing
  end interface operator(+)
end module missing_operator
"""
    module = FortranToIRConverter().visit_module(parse_fortran_source(source).modules[0])
    report = assess_semantic_wrap_readiness(module)
    blocker = next(
        blocker for blocker in report["wrappability_blockers"] if blocker["code"] == "fortran_generic_target_unresolved"
    )

    assert blocker["items"][0]["generic"] == "operator(+)"
    assert blocker["items"][0]["missing_targets"] == ["missing"]


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
    assert {(item["code"], item["symbol"], item["expression"]) for item in requirements} >= {
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
                    FortranVariable(
                        name="rk", base_type="integer", is_parameter=True, symbolic_value="selected_real_kind(12)"
                    ),
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
                procedures=[
                    FortranProcedureSignature(
                        name="child_step",
                        kind="subroutine",
                        arguments=[FortranArgument(name="y", base_type="real", kind="rk")],
                    )
                ],
                derived_types=[
                    FortranDerivedType(
                        name="child_t", fields=[FortranArgument(name="value", base_type="real", kind="rk")]
                    )
                ],
            )
        ],
        programs=[
            FortranProgram(
                variables=[FortranVariable(name="program_scale", base_type="real", kind="rk")],
                procedures=[
                    FortranProcedureSignature(
                        name="program_step",
                        kind="subroutine",
                        arguments=[FortranArgument(name="z", base_type="real", kind="rk")],
                    )
                ],
            )
        ],
        block_data_units=[
            FortranBlockData(variables=[FortranVariable(name="saved_scale", base_type="real", kind="rk")])
        ],
        procedures=[
            FortranProcedureSignature(
                name="free_step", kind="subroutine", arguments=[FortranArgument(name="q", base_type="real", kind="rk")]
            )
        ],
        derived_types=[
            FortranDerivedType(name="free_t", fields=[FortranArgument(name="payload", base_type="real", kind="rk")])
        ],
    )

    contexts = {var.name: ctx for var, ctx in _iter_fortran_variable_contexts(parsed)}
    requirements = collect_semantic_compile_time_requirements(parsed)
    supplied = collect_semantic_compile_time_requirements(
        parsed,
        compile_time_values={"rk": 8, "selected_real_kind(12)": 8, "n": 2},
    )

    assert contexts == {
        "file_param": {
            "unit_kind": "file",
            "unit": "<source>",
            "module": None,
            "symbol": "file_param",
            "role": "variable",
        },
        "rk": {
            "unit_kind": "module",
            "unit": "solver_mod",
            "module": "solver_mod",
            "symbol": "rk",
            "role": "variable",
        },
        "scale": {
            "unit_kind": "module",
            "unit": "solver_mod",
            "module": "solver_mod",
            "symbol": "scale",
            "role": "variable",
        },
        "x": {
            "unit_kind": "procedure",
            "unit": "solver_mod.step",
            "module": "solver_mod",
            "procedure": "step",
            "symbol": "x",
            "role": "argument",
        },
        "r": {
            "unit_kind": "procedure",
            "unit": "solver_mod.step",
            "module": "solver_mod",
            "procedure": "step",
            "symbol": "r",
            "role": "result",
        },
        "scratch": {
            "unit_kind": "procedure",
            "unit": "solver_mod.step",
            "module": "solver_mod",
            "procedure": "step",
            "symbol": "scratch",
            "role": "variable",
        },
        "mass": {
            "unit_kind": "derived_type",
            "unit": "solver_mod.state_t",
            "module": "solver_mod",
            "type_owner": "state_t",
            "symbol": "mass",
            "role": "field",
        },
        "child_scale": {
            "unit_kind": "submodule",
            "unit": "solver_child",
            "module": "solver_child",
            "symbol": "child_scale",
            "role": "variable",
        },
        "y": {
            "unit_kind": "procedure",
            "unit": "solver_child.child_step",
            "module": "solver_child",
            "procedure": "child_step",
            "symbol": "y",
            "role": "argument",
        },
        "value": {
            "unit_kind": "derived_type",
            "unit": "solver_child.child_t",
            "module": "solver_child",
            "type_owner": "child_t",
            "symbol": "value",
            "role": "field",
        },
        "program_scale": {
            "unit_kind": "program",
            "unit": "<program>",
            "module": None,
            "symbol": "program_scale",
            "role": "variable",
        },
        "z": {
            "unit_kind": "procedure",
            "unit": "program_step",
            "module": None,
            "procedure": "program_step",
            "symbol": "z",
            "role": "argument",
        },
        "saved_scale": {
            "unit_kind": "block_data",
            "unit": "<block_data>",
            "module": None,
            "symbol": "saved_scale",
            "role": "variable",
        },
        "q": {
            "unit_kind": "procedure",
            "unit": "free_step",
            "module": None,
            "procedure": "free_step",
            "symbol": "q",
            "role": "argument",
        },
        "payload": {
            "unit_kind": "derived_type",
            "unit": "free_t",
            "module": None,
            "type_owner": "free_t",
            "symbol": "payload",
            "role": "field",
        },
    }
    assert {"file", "module", "submodule", "program", "block_data", "procedure", "derived_type"} <= {
        ctx["unit_kind"] for ctx in contexts.values()
    }
    assert {ctx["role"] for ctx in contexts.values()} >= {"variable", "argument", "result", "field"}
    assert ("parameter_value", "rk", "selected_real_kind(12)") in {
        (item["code"], item["symbol"], item["expression"]) for item in requirements
    }
    assert any(item["code"] == "unsupported_kind" and item["symbol"] == "scale" for item in requirements)
    by_symbol = {(item["code"], item["symbol"]): item for item in requirements}
    assert by_symbol[("parameter_value", "rk")] == {
        "code": "parameter_value",
        "unit_kind": "module",
        "unit": "solver_mod",
        "module": "solver_mod",
        "procedure": None,
        "type_owner": None,
        "role": "variable",
        "symbol": "rk",
        "base_type": None,
        "kind": None,
        "expression": "selected_real_kind(12)",
        "message": "Parameter 'rk' needs a compile-time value for expression 'selected_real_kind(12)'.",
    }
    assert by_symbol[("unsupported_kind", "mass")] == {
        "code": "unsupported_kind",
        "unit_kind": "derived_type",
        "unit": "solver_mod.state_t",
        "module": "solver_mod",
        "procedure": None,
        "type_owner": "state_t",
        "role": "field",
        "symbol": "mass",
        "base_type": "real",
        "kind": "rk",
        "expression": "rk",
        "message": "Kind expression for 'mass' needs a supported compile-time value.",
    }
    assert by_symbol[("unsupported_kind", "x")]["procedure"] == "step"
    assert supplied == []
    assert (
        collect_semantic_compile_time_requirements(
            FortranFile(variables=[FortranVariable(name="custom", base_type="real", kind="rk")]),
            type_map={("real", "rk"): "FloatCustom"},
        )
        == []
    )
    assert (
        collect_semantic_compile_time_requirements(
            FortranFile(variables=[FortranVariable(name="runtime", base_type="integer", value="n + 1")])
        )
        == []
    )
    assert (
        collect_semantic_compile_time_requirements(
            FortranFile(
                variables=[
                    FortranVariable(
                        name="provided",
                        base_type="integer",
                        is_parameter=True,
                        symbolic_value="external_value()",
                    )
                ]
            ),
            compile_time_values={"provided": 4},
        )
        == []
    )
    unsupported = collect_semantic_compile_time_requirements(
        FortranFile(
            variables=[
                FortranVariable(name="bad_integer", base_type="integer", kind="bad"),
                FortranVariable(name="bad_real", base_type="real", kind="bad"),
                FortranVariable(name="bad_complex", base_type="complex", kind="bad"),
                FortranVariable(name="bad_logical", base_type="logical", kind="bad"),
                FortranVariable(name="bad_character", base_type="character", kind="bad"),
                FortranVariable(name="callback", base_type="procedure", kind="f_iface"),
            ]
        )
    )
    assert {item["symbol"] for item in unsupported} == {
        "bad_integer",
        "bad_real",
        "bad_complex",
    }
    resolved_kind = collect_semantic_compile_time_requirements(
        FortranFile(variables=[FortranVariable(name="resolved_bad", base_type="real", kind="rk + 1")]),
        compile_time_values={"rk": 8},
    )
    assert resolved_kind[0]["expression"] == "8 + 1"
    named_contexts = {
        var.name: ctx
        for var, ctx in _iter_fortran_variable_contexts(
            FortranFile(
                filename="units.f90",
                variables=[FortranVariable(name="file_named")],
                programs=[FortranProgram(name="driver", variables=[FortranVariable(name="program_named")])],
                block_data_units=[FortranBlockData(name="saved", variables=[FortranVariable(name="block_named")])],
            )
        )
    }
    assert named_contexts["file_named"]["unit"] == "units.f90"
    assert named_contexts["program_named"]["unit"] == "driver"
    assert named_contexts["block_named"]["unit"] == "saved"
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
                    storage=semantic_models.SemanticStorageContract(
                        kind="array",
                        array=semantic_models.SemanticArrayContract(
                            rank=1,
                            shape=["1:n"],
                            source_shape=["1:n"],
                        ),
                    ),
                ),
            )
        ],
    )

    resolved = resolve_semantic_compile_time_values(module, {"n": 8})

    assert module.variables[0].semantic_type.shape == ["1:n"]
    assert resolved.variables[0].semantic_type.shape == ["1:8"]
    assert resolved.variables[0].semantic_type.storage.array.shape == ["1:8"]


def test_resolve_semantic_compile_time_values_handles_enum_declarations():
    enumerator = SemanticArgument(
        name="STATUS_LIMIT",
        semantic_type=SemanticType("status"),
        default_value="n",
    )
    module = SemanticModule(
        name="status_mod",
        classes=[
            semantic_models.SemanticEnum(
                name="status",
                underlying_type=SemanticType("Int", metadata={"bits": "n"}),
                enumerators=[enumerator],
            )
        ],
        variables=[enumerator],
    )

    resolved = resolve_semantic_compile_time_values(module, {"n": 16})

    assert resolved.enums[0].underlying_type.metadata == {"bits": "16"}
    assert resolved.enums[0].enumerators[0].default_value == "16"


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
                    storage=semantic_models.SemanticStorageContract(
                        kind="array",
                        array=semantic_models.SemanticArrayContract(
                            rank=1,
                            shape=["n"],
                            source_shape=["1:n"],
                            lower_bounds=["n"],
                            upper_bounds=["n"],
                        ),
                    ),
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
    assert resolved_module.variables[0].semantic_type.storage.array.shape == ["4"]
    assert resolved_module.variables[0].semantic_type.storage.array.source_shape == ["1:4"]
    assert resolved_module.variables[0].semantic_type.storage.array.lower_bounds == ["4"]
    assert resolved_module.variables[0].semantic_type.storage.array.upper_bounds == ["4"]
    assert resolved_module.variables[0].semantic_type.metadata == {"bounds": ("4", ["2"])}
    assert resolved_module.variables[0].default_value == "4"
    assert resolved_module.variables[0].metadata == {"alias": "2"}
    assert resolved_module.functions[0].arguments[0].semantic_type.shape == ["2"]
    assert resolved_module.functions[0].arguments[0].metadata == {"scale": "4"}
    assert resolved_module.functions[0].projection[0].value == {"shape": ["4", ("2",)]}
    assert resolved_module.functions[0].metadata == {"work": ["4", {"inner": "2"}]}
    assert resolved_module.functions[1].return_type.metadata == {"extent": "4"}
    assert resolved_module.classes[0].fields[0].semantic_type.shape == ["4"]
    assert resolved_module.classes[0].fields[0].default_value == "2"
    assert resolved_module.classes[0].methods[0].arguments[0].semantic_type.metadata == {"n": "4"}
    assert resolved_module.classes[0].methods[0].return_type.metadata == {"m": "2"}
    assert resolved_module.classes[0].methods[0].projection[0].value == ("4", {"m": "2"})
    assert resolved_module.classes[0].methods[0].metadata == {"method": "4"}
    assert resolved_module.classes[0].metadata == {"class": "2"}
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
        ("integer", None, "Int32"),
        ("integer", "1", "Int8"),
        ("integer", "2", "Int16"),
        ("integer", "4", "Int32"),
        ("integer", "8", "Int64"),
        ("integer", "int8", "Int8"),
        ("integer", "int16", "Int16"),
        ("integer", "int32", "Int32"),
        ("integer", "int64", "Int64"),
        ("integer", "c_signed_char", "Int8"),
        ("integer", "c_short", "Int16"),
        ("integer", "c_int", "Int32"),
        ("integer", "c_long_long", "Int64"),
        ("integer", "c_int8_t", "Int8"),
        ("integer", "c_int16_t", "Int16"),
        ("integer", "c_int32_t", "Int32"),
        ("integer", "c_int64_t", "Int64"),
        ("real", None, "Float32"),
        ("real", "4", "Float32"),
        ("real", "8", "Float64"),
        ("real", "16", "Float128"),
        ("real", "real32", "Float32"),
        ("real", "real64", "Float64"),
        ("real", "real128", "Float128"),
        ("real", "c_float", "Float32"),
        ("real", "c_double", "Float64"),
        ("real", "kind(1.0e0)", "Float32"),
        ("real", "kind(1.0d0)", "Float64"),
        ("real", "kind(1.0q0)", "Float128"),
        ("complex", None, "Complex64"),
        ("complex", "4", "Complex64"),
        ("complex", "8", "Complex128"),
        ("complex", "16", "Complex256"),
        ("complex", "real32", "Complex64"),
        ("complex", "real64", "Complex128"),
        ("complex", "real128", "Complex256"),
        ("complex", "c_float_complex", "Complex64"),
        ("complex", "c_double_complex", "Complex128"),
        ("logical", None, "Bool"),
        ("logical", "1", "Bool"),
        ("logical", "2", "Bool"),
        ("logical", "4", "Bool"),
        ("logical", "8", "Bool"),
        ("logical", "c_bool", "Bool"),
        ("character", None, "String"),
        ("character", "1", "String"),
        ("character", "c_char", "String"),
        ("character", "len=12, kind=c_char", "String"),
        ("procedure", "f_iface", "Procedure"),
    ]

    for base_type, kind, expected in cases:
        variable = FortranVariable(name=f"{base_type}_{kind or 'default'}", base_type=base_type, kind=kind)
        assert converter.visit_variable(variable).name == expected


def test_fortran2ir_uses_compiler_probed_storage_facts_and_preserves_provenance():
    fact = {
        "base_type": "real",
        "kind": None,
        "bits": 64,
        "expression": "storage_size(real(0.0))",
    }
    semantic_type = FortranToIRConverter(type_facts={("real", None): fact}).visit_variable(
        FortranVariable(name="value", base_type="real")
    )

    assert semantic_type.name == "Float64"
    assert semantic_type.dtype == "Float64"
    assert semantic_type.metadata["fortran_type_fact"] == fact
    assert semantic_type.metadata["fortran_type_fact_source"] == "compiler_probe"


def test_fortran2ir_rejects_compiler_storage_without_semantic_dtype():
    fact = {
        "base_type": "integer",
        "kind": None,
        "bits": 48,
        "expression": "storage_size(int(0))",
    }

    with pytest.raises(ValueError, match="integer uses 48-bit storage"):
        FortranToIRConverter(type_facts={("integer", None): fact}).visit_variable(
            FortranVariable(name="value", base_type="integer")
        )


def test_fortran_storage_requirements_follow_resolved_kinds_and_actual_source_types():
    parsed = FortranFile(
        variables=[
            FortranVariable(name="default_real", base_type="real"),
            FortranVariable(name="selected", base_type="real", kind="rk"),
            FortranVariable(name="flag", base_type="logical", kind="8"),
            FortranVariable(name="text", base_type="character", kind="len=12, kind=c_char"),
        ]
    )

    assert fortran_type_storage_expression("complex", "8") == "storage_size(cmplx(0.0,kind=8))"
    requirements = collect_fortran_type_storage_requirements(parsed, compile_time_values={"rk": 8})
    assert {(item["base_type"], item["kind"], item["expression"]) for item in requirements} == {
        ("real", None, "storage_size(real(0.0))"),
        ("real", "8", "storage_size(real(0.0,kind=8))"),
        ("logical", "8", "storage_size(logical(.false.,kind=8))"),
        ("character", "c_char", "storage_size(char(65,kind=c_char))"),
    }


def test_legacy_fortran_storage_uses_fixed_star_widths_and_probes_double_types():
    parsed = parse_fortran_source(
        """
subroutine legacy(c8, c16, dp, dc, label, explicit_kind)
  complex*8 c8
  complex*16 c16
  double precision dp
  double complex dc
  character*8 label
  character(kind=1) explicit_kind
end subroutine legacy
""",
        filename="legacy_types.f90",
    )
    args = {arg.name: arg for arg in parsed.procedures[0].arguments}
    converter = FortranToIRConverter()

    assert converter.visit_variable(args["c8"]).name == "Complex64"
    assert converter.visit_variable(args["c16"]).name == "Complex128"
    assert converter.visit_variable(args["c16"]).metadata["fortran_type_fact_source"] == "legacy_star_storage"

    requirements = collect_fortran_type_storage_requirements(parsed)
    assert {(item["base_type"], item["kind"], item["expression"]) for item in requirements} == {
        ("real", "kind(1.0d0)", "storage_size(real(0.0,kind=kind(1.0d0)))"),
        ("complex", "kind(1.0d0)", "storage_size(cmplx(0.0,kind=kind(1.0d0)))"),
        ("character", None, "storage_size(char(65))"),
        ("character", "1", "storage_size(char(65,kind=1))"),
    }


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

    contract = array_contract(x.semantic_type)
    assert contract.category == "assumed_shape"
    assert contract.shape == ["::Strided"]
    assert contract.source_shape == [":"]
    assert contract.order is None


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

    contract = array_contract(A.semantic_type)
    assert A.semantic_type.shape == ["::Strided", "::Strided"]
    assert contract.source_shape == [":", ":"]
    assert contract.category == "assumed_shape"
    assert contract.order == "ORDER_F"


def test_fortran_native_storage_contracts_cover_array_categories_and_scalars():
    source = """
module contract_mod
contains
subroutine contracts(n, m, explicit, legacy, assumed, contig, alloc, ptr, scalar_value, scalar_ref, scalar_out)
  integer, intent(in) :: n
  integer, intent(in) :: m
  real(8), intent(in) :: explicit(n, m)
  real(8), intent(inout) :: legacy(n, *)
  real(8), intent(in) :: assumed(:, :)
  real(8), contiguous, intent(inout) :: contig(:, :)
  real(8), allocatable, intent(out) :: alloc(:)
  real(8), pointer, intent(inout) :: ptr(:)
  real(8), value, intent(in) :: scalar_value
  real(8), intent(in) :: scalar_ref
  real(8), intent(out) :: scalar_out
end subroutine contracts
end module contract_mod
"""
    module = fortran_module_to_semantic_module(parse_fortran_source(source))
    func = get_function(module, "contracts")
    args = {arg.name: arg for arg in func.arguments}

    explicit = array_contract(args["explicit"].semantic_type)
    assert explicit.category == "explicit_shape"
    assert explicit.shape == ["n", "m"]
    assert explicit.order == "ORDER_F"
    assert args["explicit"].semantic_type.storage.read_only is True

    legacy = array_contract(args["legacy"].semantic_type)
    assert legacy.category == "assumed_size"
    assert legacy.shape == ["n", ":"]
    assert legacy.source_shape == ["n", "*"]
    assert legacy.order == "ORDER_F"

    assumed = array_contract(args["assumed"].semantic_type)
    assert assumed.category == "assumed_shape"
    assert assumed.shape == ["::Strided", "::Strided"]
    assert assumed.order == "ORDER_F"

    contig = array_contract(args["contig"].semantic_type)
    assert contig.category == "assumed_shape"
    assert contig.shape == [":", ":"]
    assert contig.order == "ORDER_F"
    assert contig.contiguous is True

    assert array_contract(args["alloc"].semantic_type).allocatable is True
    assert array_contract(args["ptr"].semantic_type).pointer is True
    assert args["scalar_value"].semantic_type.storage is None
    assert args["scalar_ref"].semantic_type.storage.read_only is True
    assert args["scalar_out"].semantic_type.storage.mutable is True


def test_fortran_native_storage_contracts_preserve_exact_bounds_and_member_flags():
    converter = FortranToIRConverter(compile_time_values={"n": 4})
    matrix = FortranArgument(
        name="matrix",
        base_type="real",
        kind="8",
        rank=2,
        shape=["0:n - 1", "*"],
        intent="inout",
    )
    matrix.contiguous = True
    member = FortranArgument(
        name="items",
        base_type="real",
        kind="8",
        rank=1,
        shape=[":"],
        optional=True,
        allocatable=True,
        pointer=True,
        visibility="private",
    )

    matrix_type = converter.visit_argument(matrix).semantic_type
    assumed_rank = converter.visit_variable(FortranVariable(name="any_rank", base_type="real", rank=1, shape=[".."]))
    semantic_member = converter.visit_data_member(member)
    plain_member = converter.visit_data_member(FortranVariable(name="plain", base_type="real", rank=1, shape=[":"]))
    mixed_bounds = converter.visit_variable(
        FortranVariable(name="mixed", base_type="real", rank=3, shape=["3", "1:n", "0:n"])
    )
    spaced_intent = converter.visit_argument(FortranArgument(name="spaced", base_type="integer", intent="in out"))
    out_member = converter.visit_data_member(FortranVariable(name="out_value", base_type="integer"), intent="out")

    assert asdict(matrix_type.storage) == {
        "kind": "array",
        "read_only": False,
        "mutable": True,
        "pointer_depth": 0,
        "ownership": "borrowed",
        "array": {
            "rank": 2,
            "shape": ["4 - 1 - 0 + 1", ":"],
            "lower_bounds": ["0", None],
            "upper_bounds": ["4 - 1", "*"],
            "source_shape": ["0:4 - 1", "*"],
            "category": "assumed_size",
            "order": "ORDER_F",
            "axes": ["dense", "dense"],
            "contiguous": True,
            "allocatable": False,
            "pointer": False,
            "metadata": {},
        },
        "calling_convention": None,
        "metadata": {},
    }
    assert asdict(assumed_rank.storage.array) == {
        "rank": 1,
        "shape": ["..."],
        "lower_bounds": [],
        "upper_bounds": [],
        "source_shape": [".."],
        "category": "assumed_rank",
        "order": None,
        "axes": ["dense"],
        "contiguous": None,
        "allocatable": False,
        "pointer": False,
        "metadata": {},
    }
    assert semantic_member.name == "items"
    assert semantic_member.intent == "in"
    assert semantic_member.optional is True
    assert semantic_member.visibility == "private"
    assert semantic_member.semantic_type.storage.array.category == "deferred_shape"
    assert semantic_member.semantic_type.storage.array.allocatable is True
    assert semantic_member.semantic_type.storage.array.pointer is True
    assert plain_member.optional is False
    assert plain_member.visibility == "public"
    assert plain_member.semantic_type.storage.array.shape == ["::Strided"]
    assert plain_member.semantic_type.storage.array.allocatable is False
    assert plain_member.semantic_type.storage.array.pointer is False
    assert plain_member.origin.source_language == "fortran"
    assert plain_member.origin.native_name == "plain"
    assert plain_member.origin.source_kind == "variable"
    assert mixed_bounds.storage.array.lower_bounds == [None, None, "0"]
    assert mixed_bounds.storage.array.upper_bounds == [None, "4", "4"]
    assert spaced_intent.intent == "inout"
    assert out_member.intent == "out"


def test_explicit_bound_ranges_remain_shaped_storage_contracts():
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
    module = fortran_module_to_semantic_module(parse_fortran_source(source))
    args = {arg.name: arg for arg in get_function(module, "bounded").arguments}

    default_bound = array_contract(args["default_bound"].semantic_type)
    assert default_bound.category == "explicit_shape"
    assert default_bound.shape == ["n"]

    zero_bound = array_contract(args["zero_bound"].semantic_type)
    assert zero_bound.category == "explicit_shape"
    assert zero_bound.shape == ["n - 1 - 0 + 1"]


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

    assert array_contract(x.semantic_type).allocatable is True
    assert x.intent == "out"
    assert func.projection == [
        ProjectionMapping(
            python_name="x",
            native_name="x",
            native_position=0,
            python_position=None,
            result_position=0,
            intent="out",
        )
    ]


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
    assert semantic_arg.intent == "inout"
    assert array_contract(semantic_arg.semantic_type).allocatable is True
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
    assert func.projection[1].python_position == 1
    assert func.projection[1].result_position is None


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


def test_fortran_file_and_project_helpers_forward_compile_time_values():
    proc = FortranProcedureSignature(
        name="scale",
        kind="subroutine",
        arguments=[FortranArgument(name="x", base_type="real", kind="rk")],
    )
    parsed_file = FortranFile(modules=[FortranModule(name="solver", procedures=[proc])])
    project = FortranProject(files=[parsed_file])

    file_module = fortran_file_to_semantic_modules(parsed_file, compile_time_values={"rk": 8})[0]
    project_module = fortran_project_to_semantic_modules(project, compile_time_values={"rk": 8})[0]

    assert get_function(file_module, "scale").arguments[0].semantic_type.name == "Float64"
    assert get_function(project_module, "scale").arguments[0].semantic_type.name == "Float64"


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
