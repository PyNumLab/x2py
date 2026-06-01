"""C parser model to semantic IR conversion tests."""

import pytest

from c_parser import parse_c_file, parse_c_project
from c_parser.models import (
    CArray,
    CAtomic,
    CChar,
    CComposedType,
    CConst,
    CDiagnostic,
    CDouble,
    CFile,
    CFunctionType,
    CInitializer,
    CInt,
    CLongDouble,
    CMacro,
    CMacroDependency,
    CParameter,
    CPointer,
    CProject,
    CSourceLocation,
    CStruct,
    CTypedef,
    CUnion,
    CUnknownType,
    CVariable,
    CVolatile,
    CVoid,
)
from semantics.c2ir import (
    CToIRConverter,
    c_file_to_semantic_module,
    c_file_to_semantic_modules,
    c_function_to_semantic_function,
    c_parameter_to_semantic_argument,
    c_project_to_semantic_module,
    c_project_to_semantic_modules,
    c_struct_to_semantic_class,
    c_type_to_semantic_type,
)
from semantics.readiness import assess_semantic_wrap_readiness
from semantics.pyi_printer import emit_module, emit_module_stubs


def _function(module, name):
    return next(function for function in module.functions if function.name == name)


def test_c2ir_converts_scalar_function_signatures_and_preserves_native_order():
    parsed = parse_c_file("int add(int a, int b);\ndouble scale(double x);\n", filename="api.h")
    module = c_file_to_semantic_modules(parsed)[0]

    add = _function(module, "add")
    scale = _function(module, "scale")

    assert module.name == "api"
    assert [arg.name for arg in add.arguments] == ["a", "b"]
    assert [arg.semantic_type.name for arg in add.arguments] == ["Int32", "Int32"]
    assert add.return_type.name == "Int32"
    assert [mapping.native_position for mapping in add.projection] == [0, 1]
    assert scale.return_type.name == "Float64"
    assert scale.arguments[0].semantic_type.metadata == {}
    assert scale.arguments[0].semantic_type.origin.metadata["c_type"] == "CDouble"
    assert module.metadata["counts"]["functions"] == 2


def test_c2ir_maps_const_and_mutable_pointers_to_storage_contracts():
    parsed = parse_c_file(
        "void copy(const double *src, double *dst);\n",
        filename="copy.h",
    )
    module = c_file_to_semantic_modules(parsed)[0]
    copy = _function(module, "copy")
    src, dst = copy.arguments

    assert src.semantic_type.name == "Float64"
    assert src.semantic_type.storage.kind == "reference"
    assert src.semantic_type.storage.read_only is True
    assert src.intent == "in"

    assert dst.semantic_type.name == "Float64"
    assert dst.semantic_type.storage.kind == "reference"
    assert dst.semantic_type.storage.read_only is False
    assert dst.intent == "inout"
    assert dst.metadata["readiness_blockers"][0]["code"] == "c_pointer_ownership_ambiguous"


def test_c2ir_uses_declared_c_array_bounds_before_parameter_adjustment():
    parsed = parse_c_file(
        "void solve(double a[static 4], const int shape[2], int matrix[3][4]);\n",
        filename="arrays.h",
    )
    module = c_file_to_semantic_modules(parsed)[0]
    solve = _function(module, "solve")
    a, shape, matrix = solve.arguments

    assert a.semantic_type.storage.kind == "array"
    assert a.semantic_type.storage.array.shape == ["4"]
    assert a.semantic_type.storage.array.metadata["c_static_minimum"] == [True]
    assert a.intent == "inout"

    assert shape.semantic_type.storage.read_only is True
    assert shape.semantic_type.storage.array.shape == ["2"]
    assert shape.intent == "in"

    assert matrix.semantic_type.rank == 2
    assert matrix.semantic_type.storage.array.shape == ["3", "4"]
    assert matrix.semantic_type.storage.array.order == "ORDER_C"


def test_c2ir_converts_structs_and_opaque_struct_pointers():
    parsed = parse_c_file(
        """
struct point { double x; double y; };
struct context;
struct point scale_point(struct point p, double factor);
struct context *context_create(void);
void context_destroy(struct context *ctx);
""",
        filename="structs.h",
    )
    module = c_file_to_semantic_modules(parsed)[0]

    point = next(cls for cls in module.classes if cls.name == "point")
    context = next(cls for cls in module.classes if cls.name == "context")
    scale_point = _function(module, "scale_point")
    context_create = _function(module, "context_create")

    assert [field.name for field in point.fields] == ["x", "y"]
    assert [field.semantic_type.name for field in point.fields] == ["Float64", "Float64"]
    assert context.base_classes == ["Opaque"]
    assert scale_point.arguments[0].semantic_type.name == "point"
    assert context_create.return_type.name == "context"
    assert context_create.return_type.storage.kind == "reference"
    assert "class context(Opaque):" in emit_module(module)

    report = assess_semantic_wrap_readiness(module, source="structs.h")
    assert report["wrappable"] is True


def test_c2ir_private_include_types_remain_available_as_opaque_handles():
    parsed = parse_c_file(
        """
# 1 "private.h" 1
struct private_context { int internal; };
# 1 "api.h" 2
struct private_context *make_context(void);
void use_context(struct private_context *ctx);
""",
        filename="api.h",
        preprocessing="compiler",
    )
    parsed.preprocessing_recipe = {
        "included_files": [
            {"path": "api.h", "dependency_kind": "root", "exposure": "public"},
            {"path": "private.h", "dependency_kind": "project", "exposure": "private"},
        ]
    }

    module = c_file_to_semantic_modules(parsed)[0]
    make_context = _function(module, "make_context")
    use_context = _function(module, "use_context")
    stubs = emit_module_stubs(module)

    assert all(cls.name != "private_context" for cls in module.classes)
    assert make_context.return_type.name == "private_context"
    assert use_context.arguments[0].semantic_type.name == "private_context"
    assert make_context.return_type.metadata["external_type_ref"] == {
        "name": "private_context",
        "local_name": "private_context",
        "origin_module": "private",
        "wrapped": False,
        "representation": "opaque",
    }
    assert "from private import private_context" in stubs["api"]
    assert stubs["private"] == "class private_context(Opaque):\n    pass"
    assert assess_semantic_wrap_readiness(module, source="api.h")["wrappable"] is True


def test_c2ir_explicit_project_headers_import_types_from_their_owner_module():
    project = parse_c_project(
        {
            "types.h": "struct state { int id; };\n",
            "api.h": "struct state;\nvoid step(struct state *state);\n",
        }
    )
    modules = {module.name: module for module in c_project_to_semantic_modules(project)}
    api = modules["api"]
    state = _function(api, "step").arguments[0].semantic_type
    stubs = emit_module_stubs(api, available_modules=modules.values())

    assert all(cls.name != "state" for cls in api.classes)
    assert state.metadata["external_type_ref"] == {
        "name": "state",
        "local_name": "state",
        "origin_module": "types",
        "wrapped": True,
        "representation": "wrapped",
    }
    assert "from types import state" in stubs["api"]
    assert "class state" not in stubs["api"]
    assert assess_semantic_wrap_readiness(api, source="api.h")["wrappable"] is True


def test_c2ir_private_include_opaque_struct_by_value_remains_blocked():
    parsed = parse_c_file(
        """
# 1 "private.h" 1
struct private_context { int internal; };
# 1 "api.h" 2
void use_context(struct private_context ctx);
""",
        filename="api.h",
        preprocessing="compiler",
    )
    parsed.preprocessing_recipe = {
        "included_files": [
            {"path": "api.h", "dependency_kind": "root", "exposure": "public"},
            {"path": "private.h", "dependency_kind": "project", "exposure": "private"},
        ]
    }

    module = c_file_to_semantic_modules(parsed)[0]
    report = assess_semantic_wrap_readiness(module, source="api.h")

    assert report["wrappable"] is False
    assert "c_opaque_struct_by_value" in {blocker["code"] for blocker in report["wrappability_blockers"]}


def test_c2ir_converts_enum_constants_and_simple_macro_constants():
    parsed = parse_c_file(
        """
enum status { STATUS_OK = 0, STATUS_WARN, STATUS_ERROR = 10 };
""",
        filename="constants.h",
    )
    parsed.macros = [CMacro(name="API_VERSION", value="3")]
    module = c_file_to_semantic_modules(parsed)[0]

    constants = {var.name: var for var in module.variables}
    assert constants["API_VERSION"].default_value == "3"
    assert constants["API_VERSION"].semantic_type.constraints[0].name == "Constant"
    assert constants["STATUS_WARN"].default_value == "1"
    assert constants["STATUS_ERROR"].default_value == "10"


def test_c2ir_converts_integer_expression_macro_constants_when_resolvable():
    parsed = parse_c_file(
        """
void fill(int x[static API_N1]);
""",
        filename="shape_macros.h",
    )
    parsed.macros = [
        CMacro(name="API_N0", value="4"),
        CMacro(name="API_N1", value="(API_N0 + 2)"),
        CMacro(name="API_MASK", value="(1U << API_N1)"),
        CMacro(name="API_TEXT", value='"not a semantic integer constant"'),
    ]
    module = c_file_to_semantic_modules(parsed)[0]

    constants = {var.name: var for var in module.variables}
    assert constants["API_N0"].semantic_type.name == "Int32"
    assert constants["API_N1"].semantic_type.name == "Int32"
    assert constants["API_MASK"].semantic_type.name == "Int32"
    assert "API_TEXT" not in constants


def test_c2ir_resolves_local_typedef_chains_and_standard_size_t_fallback():
    parsed = parse_c_file(
        """
typedef unsigned long size_type;
typedef size_type api_size;
api_size count(void);
int read_values(const double *values, size_t n);
""",
        filename="typedefs.h",
    )
    module = c_file_to_semantic_modules(parsed)[0]

    assert _function(module, "count").return_type.name == "UInt64"
    read_values = _function(module, "read_values")
    assert [arg.semantic_type.name for arg in read_values.arguments] == ["Float64", "SizeT"]
    assert read_values.arguments[0].semantic_type.storage.read_only is True


def test_c2ir_uses_standard_type_probe_facts_when_supplied():
    parsed = parse_c_file("size_t count(void);\n", filename="probe.h")
    converter = CToIRConverter(
        standard_type_report={
            "types": {
                "size_t": {
                    "available": True,
                    "kind": "integer",
                    "signed": False,
                    "bits": 32,
                }
            }
        }
    )

    module = converter.visit_file(parsed)

    assert _function(module, "count").return_type.name == "UInt32"


def test_c2ir_uses_standard_type_probe_opaque_handle_facts():
    parsed = parse_c_file("void close_file(FILE *stream);\n", filename="stdio_api.h")
    converter = CToIRConverter(
        standard_type_report={
            "types": {
                "FILE": {
                    "available": True,
                    "kind": "opaque_handle",
                    "pointer_bits": 64,
                }
            }
        }
    )

    module = converter.visit_file(parsed)
    close_file = _function(module, "close_file")

    assert [(cls.name, cls.base_classes) for cls in module.classes] == [("FILE", ["Opaque"])]
    assert close_file.arguments[0].semantic_type.name == "FILE"
    assert close_file.arguments[0].semantic_type.storage.kind == "reference"
    assert assess_semantic_wrap_readiness(module, source="stdio_api.h")["wrappable"] is True


def test_c_function_compatibility_helper_accepts_parser_function():
    parsed = parse_c_file("float half(float value);\n", filename="helpers.h")

    function = c_function_to_semantic_function(parsed.functions[0])

    assert function.name == "half"
    assert function.arguments[0].semantic_type.name == "Float32"
    assert function.return_type.name == "Float32"


def test_c2ir_visitor_and_project_compatibility_entrypoints_cover_supported_nodes():
    first = parse_c_file("struct point { int x; };\nint value;\nint f(int x);\n", filename="a.h")
    second = parse_c_file("double g(double y);\n", filename="b.h")
    project = CProject(
        files={"b.h": second, "a.h": first},
        functions={"f": first.functions[0], "g": second.functions[0]},
        structs={"point": first.structs[0]},
        variables={"value": first.variables[0]},
    )
    converter = CToIRConverter()

    assert [module.name for module in converter.visit(project)] == ["a", "b"]
    assert converter.visit(first).name == "a"
    assert converter.visit(first.functions[0]).name == "f"
    assert converter.visit(first.functions[0].parameters[0], position=3).metadata["native_position"] == 3
    assert converter.visit(first.structs[0]).name == "point"
    assert converter.visit(first.variables[0]).name == "value"
    assert converter.visit(CInt()).name == "Int32"
    with pytest.raises(TypeError, match="Unsupported C parse object"):
        converter.visit(object())

    assert c_file_to_semantic_module(first).name == "a"
    assert c_type_to_semantic_type(CInt()).name == "Int32"
    assert c_parameter_to_semantic_argument(CParameter(name=None, type=CInt()), position=2).name == "arg2"
    assert c_struct_to_semantic_class(first.structs[0]).name == "point"
    assert [module.name for module in c_project_to_semantic_modules(project)] == ["a", "b"]
    merged = c_project_to_semantic_module(project, name="42 api/project")
    assert merged.name == "_42_api_project"
    assert {function.name for function in merged.functions} == {"f", "g"}


def test_c2ir_converts_qualifiers_callbacks_bitfields_and_unspecified_functions():
    callback = CComposedType(
        components=[
            CPointer(),
            CFunctionType(result_type=CVoid(), parameter_types=[CInt()]),
        ],
        source_text="void (*)(int)",
    )
    converter = CToIRConverter()
    variable = converter.visit_variable(CVariable(name="handler", type=callback, storage=["static"]))
    field = converter.visit_variable(CVariable(name="bits", type=CInt(), bit_width="3"))
    function = converter.visit_function(parse_c_file("static int legacy();\n", filename="legacy.h").functions[0])
    qualified = converter.visit_type(
        CChar(qualifiers=[CConst(), CVolatile(), CAtomic()], source_text="const volatile _Atomic char")
    )

    assert variable.visibility == "private"
    assert variable.semantic_type.name == "CFunctionPointer"
    assert field.semantic_type.metadata["readiness_blockers"][0]["code"] == "c_bitfield_unsupported"
    assert function.visibility == "private"
    assert function.metadata["readiness_blockers"][0]["code"] == "c_unspecified_function_parameters"
    assert qualified.name == "Int8"
    assert qualified.metadata["c_char_policy"]
    assert {blocker["code"] for blocker in qualified.metadata["readiness_blockers"]} == {
        "c_volatile_unsupported",
        "c_atomic_unsupported",
    }
    assert qualified.origin.metadata["c_type"] == "CChar"
    assert qualified.origin.metadata["qualifiers"] == ["const", "volatile", "_Atomic"]


def test_c2ir_reports_unsupported_type_and_declarator_compositions():
    converter = CToIRConverter(primitive_type_map={CInt: None})

    unresolved = converter.visit_type(CUnknownType(spelling="missing_t", source_text="missing_t"))
    unsupported_integer = converter.visit_type(CInt(source_text="int"))
    unsupported_precision = converter.visit_type(CLongDouble(source_text="long double"))
    empty = converter.visit_type(CComposedType(components=[]))
    array_missing_element = converter.visit_type(CComposedType(components=[CArray(bound="4")]))
    array_of_pointer = converter.visit_type(CComposedType(components=[CArray(bound="4"), CPointer(), CDouble()]))
    pointer_missing_pointee = converter.visit_type(CComposedType(components=[CPointer()]))
    pointer_composition = converter.visit_type(CComposedType(components=[CPointer(), CInt(), CDouble()]))
    other_composition = converter.visit_type(CComposedType(components=[CInt(), CDouble()]))

    assert unresolved.metadata["readiness_blockers"][0]["code"] == "c_unresolved_type"
    assert unsupported_integer.metadata["readiness_blockers"][0]["code"] == "c_unsupported_type"
    assert unsupported_precision.metadata["readiness_blockers"][0]["code"] == "c_long_double_unsupported"
    assert empty.metadata["readiness_blockers"][0]["code"] == "c_empty_composed_type"
    assert array_missing_element.metadata["readiness_blockers"][0]["code"] == "c_array_missing_element_type"
    assert array_of_pointer.metadata["readiness_blockers"][0]["code"] == "c_array_of_pointer_unsupported"
    assert pointer_missing_pointee.metadata["readiness_blockers"][0]["code"] == "c_pointer_missing_pointee"
    assert pointer_composition.metadata["readiness_blockers"][0]["code"] == "c_unsupported_composed_type"
    assert other_composition.metadata["readiness_blockers"][0]["code"] == "c_unsupported_composed_type"


def test_c2ir_models_pointer_to_arrays_unknown_extents_unions_and_anonymous_aliases():
    converter = CToIRConverter()
    pointer_array = converter.visit_type(
        CComposedType(components=[CPointer(), CArray(bound=None), CDouble()], source_text="double (*)[]"),
        owner="matrix",
    )
    choice = CUnion(name="choice", members=[CVariable(name="integer", type=CInt())])
    converter.unions = {"choice": choice}
    union_type = converter.visit_type(CUnion(name="choice"), owner="selected")
    anon_struct = CStruct(anonymous_id="anon_struct_1")
    anon_union = CUnion(anonymous_id="anon_union_1")
    converter.typedefs = {
        "record_t": CTypedef(name="record_t", type=anon_struct),
        "variant_t": CTypedef(name="variant_t", type=anon_union),
    }

    assert pointer_array.storage.pointer_depth == 1
    assert pointer_array.storage.metadata["c_pointer_to_array"] is True
    assert pointer_array.metadata["readiness_blockers"][0]["code"] == "c_array_extent_ambiguous"
    assert union_type.metadata["readiness_blockers"][0]["code"] == "c_union_unsupported"
    assert converter.visit_struct(anon_struct).name == "record_t"
    assert converter.visit_union(anon_union).name == "variant_t"


def test_c2ir_marks_incomplete_by_value_structs_and_preserves_initializer_locations():
    incomplete = CStruct(name="handle", is_incomplete=True)
    converter = CToIRConverter()
    converter.structs = {"handle": incomplete}
    parameter = converter.visit_parameter(CParameter(name="handle", type=incomplete), owner="open")
    variable = converter.visit_variable(
        CVariable(
            name=None,
            type=incomplete,
            initializer=CInitializer("factory()"),
            source_location=CSourceLocation(filename="api.h", line=2, column=4, source_line="struct handle h;"),
        )
    )

    assert parameter.semantic_type.metadata["readiness_blockers"][0]["code"] == "c_incomplete_struct_by_value"
    assert variable.name == "<anonymous>"
    assert variable.default_value == "factory()"
    assert variable.origin.source_location["filename"] == "api.h"


def test_c2ir_standard_type_facts_and_numeric_constant_edge_cases():
    class Report:
        types = {
            "signed_size": {"kind": "integer", "signed": True, "bits": 16},
            "real_size": {"kind": "real", "bits": 32},
            "missing": {"available": False, "kind": "integer", "signed": False, "bits": 32},
        }

    converter = CToIRConverter(standard_type_report=Report())
    assert converter._standard_semantic_type("signed_size").name == "Int16"
    assert converter._standard_semantic_type("real_size").name == "Float32"
    assert converter._standard_semantic_type("missing") is None
    assert converter._standard_semantic_type("not_standard") is None
    assert CToIRConverter._standard_type_facts(object()) == {}
    assert CToIRConverter._integer_literal_value(None) is None
    assert CToIRConverter._integer_literal_value("value") is None
    assert CToIRConverter._integer_macro_expression("(MISSING + 1)", {}) is False
    assert CToIRConverter._integer_macro_expression("(1 +)", {}) is False

    parsed = parse_c_file(
        "enum status { STATUS_EXPR = UNKNOWN, STATUS_NEXT };\n",
        filename="edge_constants.h",
    )
    parsed.macros = [
        CMacro(name="RATE", value="1.5"),
        CMacro(name="BAD", value="(MISSING + 1)"),
    ]
    constants = {variable.name: variable for variable in converter.visit_file(parsed).variables}
    assert constants["RATE"].semantic_type.name == "Float64"
    assert constants["STATUS_EXPR"].default_value == "UNKNOWN"
    assert constants["STATUS_NEXT"].default_value is None


def test_c2ir_propagates_file_and_project_diagnostic_blockers():
    dependency = CMacroDependency(name="API", source_text="API(int) f(void);")
    warning = CDiagnostic(code="C_WARNING", message="warning", severity="warning")
    duplicate_dependency = CDiagnostic(
        code="C_MACRO_DEPENDENT_DECLARATION",
        message="already represented",
        severity="error",
    )
    error = CDiagnostic(
        code="C_BAD_DECL",
        message="bad declaration",
        severity="error",
        unit_kind="function",
        unit_name="broken",
    )
    c_file = CFile(
        filename=None,
        macro_dependencies=[dependency],
        diagnostics=[warning, duplicate_dependency, error],
    )
    project = CProject(files={"bad.h": c_file}, diagnostics=[error])
    converter = CToIRConverter()

    module = converter.visit_file(c_file)
    merged = converter.visit_project_module(project)
    file_codes = {blocker["code"] for blocker in module.metadata["readiness_blockers"]}
    project_codes = {blocker["code"] for blocker in merged.metadata["readiness_blockers"]}

    assert module.name == "c_module"
    assert file_codes == {"c_macro_dependent_declaration", "c_c_bad_decl"}
    assert project_codes == {"c_macro_dependent_declaration", "c_c_bad_decl"}
