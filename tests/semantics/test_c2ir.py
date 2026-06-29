"""C parser model to semantic IR conversion tests."""

from dataclasses import asdict
from typing import ClassVar

import pytest

from x2py.c_parser import parse_c_file, parse_c_project
from x2py.c_parser.models import (
    CArray,
    CAtomic,
    CBool,
    CChar,
    CComposedType,
    CConst,
    CDiagnostic,
    CDouble,
    CDoubleComplex,
    CEnum,
    CFile,
    CFloat,
    CFloatComplex,
    CFunction,
    CFunctionType,
    CInitializer,
    CInt,
    CLong,
    CLongDouble,
    CLongDoubleComplex,
    CLongLong,
    CMacro,
    CMacroDependency,
    CParameter,
    CPointer,
    CProject,
    CRestrict,
    CShort,
    CSignedChar,
    CSourceLocation,
    CStruct,
    CTypedef,
    CUnion,
    CUnknownType,
    CUnsignedChar,
    CUnsignedInt,
    CUnsignedLong,
    CUnsignedLongLong,
    CUnsignedShort,
    CVariable,
    CVolatile,
    CVoid,
)
from x2py.semantics.c2ir import (
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
from x2py.semantics.models import (
    SemanticArgument,
    SemanticClass,
    SemanticField,
    SemanticModule,
    SemanticOrigin,
    SemanticStorageContract,
    SemanticType,
    SemanticVariable,
)
from x2py.semantics.pyi2ir import parse_pyi_text
from x2py.semantics.readiness import assess_semantic_wrap_readiness
from x2py.codegen.printers.pyi_printer import emit_module, emit_module_stubs


def _function(module, name):
    return next(function for function in module.functions if function.name == name)


def _c_origin(
    *,
    native_name=None,
    native_scope=None,
    source_kind=None,
    source_type=None,
    source_location=None,
    metadata=None,
):
    return {
        "source_language": "c",
        "native_name": native_name,
        "native_scope": native_scope,
        "source_kind": source_kind,
        "source_type": source_type,
        "source_location": source_location or {},
        "metadata": metadata or {},
    }


def _blocker(code, message, item):
    return {"code": code, "message": message, "items": [item]}


def _assert_unsupported_type(semantic_type, *, code, message, owner, source_type):
    assert semantic_type.name == "CUnsupported"
    assert semantic_type.dtype == "CUnsupported"
    assert semantic_type.metadata == {
        "readiness_blockers": [_blocker(code, message, {"owner": owner, "type": source_type})]
    }
    assert asdict(semantic_type.origin) == _c_origin(
        source_kind="unsupported_type",
        source_type=source_type,
    )


def test_c2ir_converts_scalar_function_signatures_and_preserves_native_order():
    parsed = parse_c_file("int add(int a, int b);\ndouble scale(double x);\n", filename="api.h")
    module = c_file_to_semantic_modules(parsed)[0]

    add = _function(module, "add")
    scale = _function(module, "scale")

    assert module.name == "api"
    assert [arg.name for arg in add.arguments] == ["a", "b"]
    assert [arg.semantic_type.name for arg in add.arguments] == ["Int", "Int"]
    assert [arg.semantic_type.dtype for arg in add.arguments] == ["Int32", "Int32"]
    assert [arg.metadata for arg in add.arguments] == [{"native_position": 0}, {"native_position": 1}]
    assert add.native_name == "add"
    assert add.visibility == "public"
    assert add.return_type.name == "Int"
    assert add.return_type.dtype == "Int32"
    assert [mapping.native_position for mapping in add.projection] == [0, 1]
    assert scale.return_type.name == "Float64"
    assert scale.arguments[0].semantic_type.metadata == {}
    assert scale.arguments[0].semantic_type.origin.metadata["c_type"] == "CDouble"
    assert module.metadata == {
        "source_language": "c",
        "counts": {
            "functions": 2,
            "structs": 0,
            "unions": 0,
            "enums": 0,
            "typedefs": 0,
            "macros": 0,
            "includes": 0,
            "diagnostics": 0,
        },
        "preprocessing": "raw",
    }
    assert add.metadata == {
        "storage": [],
        "specifiers": [],
        "prototype_style": "prototype",
        "is_definition": False,
    }
    assert [asdict(mapping) for mapping in add.projection] == [
        {
            "python_name": "a",
            "native_name": "a",
            "native_position": 0,
            "python_position": 0,
            "result_position": None,
            "value_kind": "",
            "value": None,
            "intent": "in",
        },
        {
            "python_name": "b",
            "native_name": "b",
            "native_position": 1,
            "python_position": 1,
            "result_position": None,
            "value_kind": "",
            "value": None,
            "intent": "in",
        },
    ]
    assert asdict(add.arguments[0].origin) == _c_origin(
        native_name="a",
        native_scope="add",
        source_kind="parameter",
        source_type="int a",
    )
    assert asdict(add.origin) == _c_origin(
        native_name="add",
        source_kind="function",
        source_type="CFunctionType",
        source_location={
            "filename": "api.h",
            "line": 1,
            "column": 1,
            "source_line": "int add(int a, int b);",
        },
    )
    assert asdict(module.origin) == _c_origin(
        native_name="api.h",
        native_scope="api.h",
        source_kind="translation_unit",
        metadata={"preprocessing": "raw"},
    )


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
    assert copy.projection[1].intent == "inout"
    assert asdict(src.semantic_type.ownership) == {"ownership": "borrowed", "mutable": False, "aliasing": True}
    assert asdict(dst.semantic_type.ownership) == {"ownership": "borrowed", "mutable": True, "aliasing": True}
    assert dst.metadata["readiness_blockers"] == [
        _blocker(
            "c_pointer_ownership_ambiguous",
            "Mutable C pointer parameters need explicit ownership, scalar-reference, or array policy.",
            {"owner": "copy.dst", "parameter": "dst", "type": "double *dst"},
        )
    ]
    assert asdict(src.semantic_type.storage) == {
        "kind": "reference",
        "read_only": True,
        "mutable": False,
        "pointer_depth": 1,
        "ownership": "borrowed",
        "array": None,
        "calling_convention": None,
        "metadata": {
            "c_pointer_qualifiers": [[]],
            "restrict": False,
            "source_type": "const double *src",
        },
    }
    assert asdict(dst.semantic_type.storage) == {
        "kind": "reference",
        "read_only": False,
        "mutable": True,
        "pointer_depth": 1,
        "ownership": "borrowed",
        "array": None,
        "calling_convention": None,
        "metadata": {
            "c_pointer_qualifiers": [[]],
            "restrict": False,
            "source_type": "double *dst",
        },
    }
    restricted = CToIRConverter().visit_type(
        CComposedType(
            components=[CPointer(qualifiers=[CRestrict()]), CDouble()],
            source_text="double *restrict",
        )
    )
    assert restricted.storage.metadata["restrict"] is True
    assert restricted.ownership.aliasing is False
    double_pointer = CToIRConverter().visit_type(
        CComposedType(components=[CPointer(), CPointer(), CDouble()], source_text="double **")
    )
    assert double_pointer.storage.kind == "pointer"
    assert double_pointer.storage.pointer_depth == 2


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
    assert matrix.semantic_type.shape == ["3", "4"]
    assert matrix.semantic_type.storage.array.shape == ["3", "4"]
    assert matrix.semantic_type.storage.array.order == "ORDER_C"
    assert asdict(a.semantic_type.storage) == {
        "kind": "array",
        "read_only": False,
        "mutable": True,
        "pointer_depth": 1,
        "ownership": "borrowed",
        "array": {
            "rank": 1,
            "shape": ["4"],
            "lower_bounds": [],
            "upper_bounds": [],
            "source_shape": ["4"],
            "category": "c_array",
            "order": None,
            "axes": ["dense"],
            "contiguous": True,
            "allocatable": False,
            "pointer": False,
            "metadata": {
                "c_static_minimum": [True],
                "c_variable_length": [False],
                "c_flexible": [False],
            },
        },
        "calling_convention": None,
        "metadata": {"source_type": "double a[static 4]"},
    }
    assert asdict(matrix.semantic_type.storage) == {
        "kind": "array",
        "read_only": False,
        "mutable": True,
        "pointer_depth": 1,
        "ownership": "borrowed",
        "array": {
            "rank": 2,
            "shape": ["3", "4"],
            "lower_bounds": [],
            "upper_bounds": [],
            "source_shape": ["3", "4"],
            "category": "c_array",
            "order": "ORDER_C",
            "axes": ["dense", "dense"],
            "contiguous": True,
            "allocatable": False,
            "pointer": False,
            "metadata": {
                "c_static_minimum": [False, False],
                "c_variable_length": [False, False],
                "c_flexible": [False, False],
            },
        },
        "calling_convention": None,
        "metadata": {"source_type": "int matrix[3][4]"},
    }


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
    assert all(isinstance(field, SemanticField) for field in point.fields)
    assert [field.semantic_type.name for field in point.fields] == ["Float64", "Float64"]
    assert point.native_name == "struct point"
    assert point.metadata == {"c_kind": "struct", "incomplete": False}
    assert point.origin.source_language == "c"
    assert point.origin.native_name == "struct point"
    assert point.origin.source_kind == "struct"
    assert point.origin.source_type == "struct point"
    assert context.base_classes == ["CStruct", "Opaque"]
    assert context.metadata == {"c_kind": "struct", "incomplete": True}
    assert scale_point.arguments[0].semantic_type.name == "point"
    assert context_create.return_type.name == "context"
    assert context_create.return_type.storage.kind == "reference"
    assert "class context(CStruct, Opaque):" in emit_module(module)

    report = assess_semantic_wrap_readiness(module, source="structs.h")
    assert report["wrappable"] is True


def test_c2ir_private_include_types_remain_available_as_opaque_handles():
    parsed = parse_c_file(
        """
# 1 "private.h" 1
struct private_context { int internal; };
void internal_only(void);
int hidden_value;
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
    assert _function(module, "internal_only").visibility == "private"
    assert next(variable for variable in module.variables if variable.name == "hidden_value").visibility == "private"
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
    assert stubs["private"] == "class private_context(CStruct, Opaque):\n    pass"
    assert assess_semantic_wrap_readiness(module, source="api.h")["wrappable"] is True


def test_c2ir_preserves_anonymous_aggregate_members_as_nested_c_classes():
    parsed = parse_c_file(
        "struct flags { union { int integer; float real; }; struct { int code; } meta; int tag; };\n",
        filename="flags.h",
    )

    module = c_file_to_semantic_module(parsed)
    flags = module.classes[0]
    anonymous_union, meta = flags.classes
    anonymous_field, meta_field, tag = flags.fields
    code = emit_module(module)
    reparsed = parse_pyi_text(code, module_name="flags")
    reparsed_flags = reparsed.classes[0]

    assert flags.base_classes == ["CStruct"]
    assert flags.metadata == {"c_kind": "struct", "incomplete": False}
    assert anonymous_union.base_classes == ["CUnion", "CAnonymous"]
    assert anonymous_union.metadata == {"c_kind": "union", "incomplete": False, "c_anonymous": True}
    assert [field.name for field in anonymous_union.fields] == ["integer", "real"]
    assert meta.base_classes == ["CStruct", "CAnonymous"]
    assert [field.name for field in meta.fields] == ["code"]
    assert anonymous_field.name == "_anonymous_union_0"
    assert anonymous_field.semantic_type.name == "anonymous_union_0_type"
    assert [constraint.name for constraint in anonymous_field.semantic_type.constraints] == ["CAnonymousMember"]
    assert anonymous_field.semantic_type.metadata["c_kind"] == "union"
    assert meta_field.name == "meta"
    assert meta_field.semantic_type.name == "meta_type"
    assert tag.name == "tag"
    assert "class flags(CStruct):" in code
    assert "class anonymous_union_0_type(CUnion, CAnonymous):" in code
    assert "_anonymous_union_0: Annotated[anonymous_union_0_type, CAnonymousMember]" in code
    assert [(cls.name, cls.base_classes) for cls in reparsed_flags.classes] == [
        ("anonymous_union_0_type", ["CUnion", "CAnonymous"]),
        ("meta_type", ["CStruct", "CAnonymous"]),
    ]
    assert reparsed_flags.metadata == {"c_kind": "struct"}
    assert reparsed_flags.classes[0].metadata == {"c_kind": "union", "c_anonymous": True}
    assert [constraint.name for constraint in reparsed_flags.fields[0].semantic_type.constraints] == [
        "CAnonymousMember"
    ]


def test_c2ir_explicit_project_headers_import_types_from_their_owner_module():
    project = parse_c_project(
        {
            "a_empty.h": "",
            "types.h": "struct state { int id; };\nvoid local_step(struct state *state);\n",
            "api.h": "struct state;\nvoid step(int count, struct state *state);\n",
        }
    )
    project.structs = {
        "ignored": CStruct(),
        "detached": CStruct(name="detached", source_location=CSourceLocation(filename="detached.h")),
        **project.structs,
    }
    modules = {module.name: module for module in c_project_to_semantic_modules(project)}
    api = modules["api"]
    state = _function(api, "step").arguments[1].semantic_type
    local_state = _function(modules["types"], "local_step").arguments[0].semantic_type
    stubs = emit_module_stubs(api, available_modules=modules.values())

    assert all(cls.name != "state" for cls in api.classes)
    assert any(cls.name == "state" for cls in modules["types"].classes)
    assert state.metadata["external_type_ref"] == {
        "name": "state",
        "local_name": "state",
        "origin_module": "types",
        "wrapped": True,
        "representation": "wrapped",
    }
    assert "external_type_ref" not in local_state.metadata
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
    semantic_type = _function(module, "use_context").arguments[0].semantic_type
    assert semantic_type.metadata["readiness_blockers"] == [
        _blocker(
            "c_opaque_struct_by_value",
            "Opaque C structs can only cross wrapper boundaries through explicit pointer or handle policy.",
            {"owner": "private_context", "type": "private_context"},
        )
    ]


def test_c2ir_externalizes_only_private_opaque_classes_with_external_origins():
    converter = CToIRConverter()
    public = SemanticClass(name="public", origin=SemanticOrigin(source_location={"filename": "api.h"}))
    private_plain = SemanticClass(
        name="private_plain",
        visibility="private",
        origin=SemanticOrigin(source_location={"filename": "private.h"}),
    )
    private_without_location = SemanticClass(
        name="private_without_location", visibility="private", base_classes=["Opaque"]
    )
    private_external = SemanticClass(
        name="private_external",
        visibility="private",
        base_classes=["Opaque"],
        origin=SemanticOrigin(source_location={"filename": "private.h"}),
    )
    reference = SemanticArgument(name="value", semantic_type=SemanticType(name="private_external"))
    module = SemanticModule(
        name="api",
        classes=[public, private_plain, private_without_location, private_external],
        variables=[reference],
    )

    converter._externalize_private_classes(module)

    assert [cls.name for cls in module.classes] == ["public", "private_plain", "private_without_location"]
    assert reference.semantic_type.metadata["external_type_ref"] == {
        "name": "private_external",
        "local_name": "private_external",
        "origin_module": "private",
        "wrapped": False,
        "representation": "opaque",
    }
    explicit_value = SemanticType(name="private_external", storage=SemanticStorageContract())
    converter._add_external_opaque_by_value_blocker(explicit_value)
    assert explicit_value.metadata["readiness_blockers"][0]["code"] == "c_opaque_struct_by_value"


def test_c2ir_classifies_external_types_after_owner_modules_without_rewriting_local_references():
    converter = CToIRConverter()
    local_reference = SemanticArgument(name="local", semantic_type=SemanticType(name="state"))
    external_reference = SemanticArgument(name="external", semantic_type=SemanticType(name="state"))
    owner_module = SemanticModule(
        name="types",
        variables=[local_reference],
        origin=SemanticOrigin(native_name="types.h"),
    )
    consumer_module = SemanticModule(
        name="api",
        variables=[external_reference],
        origin=SemanticOrigin(native_name="api.h"),
    )
    project = CProject(structs={"state": CStruct(name="state", source_location=CSourceLocation(filename="types.h"))})

    converter._classify_project_external_types([owner_module, consumer_module], project)

    assert "external_type_ref" not in local_reference.semantic_type.metadata
    assert external_reference.semantic_type.metadata["external_type_ref"] == {
        "name": "state",
        "local_name": "state",
        "origin_module": "types",
        "wrapped": True,
        "representation": "wrapped",
    }


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
    api_version = constants["API_VERSION"]
    assert isinstance(api_version, SemanticVariable)
    assert api_version.semantic_type.name == "Int32"
    assert api_version.semantic_type.dtype == "Int32"
    assert [asdict(constraint) for constraint in api_version.semantic_type.constraints] == [
        {"name": "Constant", "arguments": []}
    ]
    assert asdict(api_version.origin) == _c_origin(
        native_name="API_VERSION",
        source_kind="macro",
    )
    status_ok = constants["STATUS_OK"]
    assert module.classes == []
    assert status_ok.semantic_type.name == "Int"
    assert status_ok.semantic_type.dtype == "Int32"
    assert status_ok.semantic_type.metadata["enum_name"] == "status"
    assert status_ok.semantic_type.metadata["c_kind"] == "enum"
    assert status_ok.semantic_type.metadata["c_enum"] == "enum status"
    assert status_ok.semantic_type.metadata["c_underlying_type"] == "Int"
    assert status_ok.semantic_type.coercions == []
    assert asdict(status_ok.origin) == _c_origin(
        native_name="STATUS_OK",
        native_scope="enum status",
        source_kind="enum_constant",
        source_location={
            "filename": "constants.h",
            "line": 2,
            "column": 1,
            "source_line": "enum status { STATUS_OK = 0, STATUS_WARN, STATUS_ERROR = 10 };",
        },
    )


def test_c2ir_names_anonymous_typedef_enums_and_keeps_enumerators_unscoped():
    source = "typedef enum { FLAG_NONE = 0, FLAG_READ = 1 } flag_t; flag_t get_flags(void);"
    parsed = parse_c_file(source, filename="flags.h")

    module = c_file_to_semantic_module(parsed)
    project_module = c_project_to_semantic_module(parse_c_project({"flags.h": source}), name="flags")

    assert module.classes == []
    assert project_module.classes == []
    assert [variable.name for variable in module.variables] == ["FLAG_NONE", "FLAG_READ"]
    assert [variable.name for variable in project_module.variables] == ["FLAG_NONE", "FLAG_READ"]
    assert [variable.semantic_type.name for variable in module.variables] == ["Int", "Int"]
    assert module.variables[0].semantic_type.metadata["enum_name"] == "flag_t"
    assert _function(module, "get_flags").return_type.name == "Int"
    assert _function(project_module, "get_flags").return_type.name == "Int"


def test_c2ir_enum_values_emit_only_python_compatible_expressions():
    parsed = parse_c_file(
        "enum flags { FLAG_ONE = 1U, FLAG_OCTAL = 010, FLAG_SHIFT = FLAG_ONE << 1, FLAG_CHAR = 'A' };",
        filename="flags.h",
    )
    module = c_file_to_semantic_module(parsed)

    code = emit_module(module)

    assert "FLAG_ONE: Final[Int] = 1" in code
    assert "FLAG_OCTAL: Final[Int] = 8" in code
    assert "FLAG_SHIFT: Final[Int] = FLAG_ONE << 1" in code
    assert "FLAG_CHAR: Final[Int]\n" in code
    assert {variable.name: variable.default_value for variable in module.variables} == {
        "FLAG_ONE": "1U",
        "FLAG_OCTAL": "010",
        "FLAG_SHIFT": "FLAG_ONE << 1",
        "FLAG_CHAR": "'A'",
    }
    assert [variable.name for variable in parse_pyi_text(code, module_name="flags").variables] == [
        "FLAG_ONE",
        "FLAG_OCTAL",
        "FLAG_SHIFT",
        "FLAG_CHAR",
    ]


def test_c2ir_cross_header_enum_references_import_the_owner_enum():
    project = parse_c_project(
        {
            "types.h": "enum status { STATUS_OK = 0 };",
            "api.h": "enum status get_status(void);",
        }
    )

    modules = {module.name: module for module in c_project_to_semantic_modules(project)}

    assert modules["api"].classes == []
    assert modules["types"].classes == []
    assert _function(modules["api"], "get_status").return_type.name == "Int"
    assert _function(modules["api"], "get_status").return_type.metadata["c_enum"] == "enum status"

    anonymous_project = parse_c_project(
        {
            "types.h": "typedef enum { FLAG_NONE = 0 } flag_t;",
            "api.h": "flag_t get_flags(void);",
        }
    )
    anonymous_modules = {module.name: module for module in c_project_to_semantic_modules(anonymous_project)}
    assert _function(anonymous_modules["api"], "get_flags").return_type.name == "Int"


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
        CMacro(name="API_CALL", value="3", function_like=True),
        CMacro(name="API_FIRST", value="1"),
        CMacro(name="API_FORWARD", value="(API_LATE + 1)"),
        CMacro(name="API_FORWARD_CHAIN", value="(API_FORWARD_MIDDLE + 1)"),
        CMacro(name="API_FORWARD_MIDDLE", value="(API_FORWARD_LATE + 1)"),
        CMacro(name="API_FORWARD_LATE", value="2"),
        CMacro(
            name="API_LATE",
            value="4",
            source_location=CSourceLocation(
                filename="shape_macros.h", line=8, column=1, source_line="#define API_LATE 4"
            ),
        ),
    ]
    module = c_file_to_semantic_modules(parsed)[0]

    constants = {var.name: var for var in module.variables}
    assert constants["API_N0"].semantic_type.name == "Int32"
    assert constants["API_N1"].semantic_type.name == "Int32"
    assert constants["API_MASK"].semantic_type.name == "Int32"
    assert constants["API_FORWARD"].semantic_type.name == "Int32"
    assert constants["API_FORWARD_CHAIN"].semantic_type.name == "Int32"
    assert "API_TEXT" not in constants
    assert "API_CALL" not in constants
    assert asdict(constants["API_LATE"].origin) == _c_origin(
        native_name="API_LATE",
        source_kind="macro",
        source_location={
            "filename": "shape_macros.h",
            "line": 8,
            "column": 1,
            "source_line": "#define API_LATE 4",
        },
    )


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

    count = _function(module, "count")
    assert count.return_type.name == "UInt64"
    assert count.return_type.metadata == {"c_typedefs": ["size_type", "api_size"]}
    read_values = _function(module, "read_values")
    assert [arg.semantic_type.name for arg in read_values.arguments] == ["Float64", "SizeT"]
    assert read_values.arguments[0].semantic_type.storage.read_only is True
    assert read_values.arguments[1].semantic_type.metadata == {
        "c_standard_type": "size_t",
        "c_standard_type_fallback": True,
        "c_typedefs": ["size_t"],
    }

    converter = CToIRConverter()
    converter.typedefs = {
        "target_t": CTypedef(name="target_t", type=CUnknownType(spelling="missing_t", source_text="missing_t"))
    }
    resolved = converter.visit_type(CTypedef(name="target_t"), owner="result")
    inline = converter.visit_type(
        CTypedef(name="inline_t", type=CUnknownType(spelling="inline_missing_t", source_text="inline_missing_t")),
        owner="inline_result",
    )
    unresolved = converter.visit_type(CTypedef(name="absent_t"), owner="result")
    converter.typedefs["cyclic_t"] = CTypedef(name="cyclic_t")
    cyclic = converter.visit_type(CTypedef(name="cyclic_t"), owner="cycle")
    assert resolved.metadata == {
        "readiness_blockers": [
            _blocker(
                "c_unresolved_type",
                "C type references must resolve before wrapping.",
                {"owner": "result", "type": "missing_t"},
            )
        ],
        "c_typedefs": ["target_t"],
    }
    assert inline.metadata == {
        "readiness_blockers": [
            _blocker(
                "c_unresolved_type",
                "C type references must resolve before wrapping.",
                {"owner": "inline_result", "type": "inline_missing_t"},
            )
        ],
        "c_typedefs": ["inline_t"],
    }
    assert unresolved.metadata == {
        "readiness_blockers": [
            _blocker(
                "c_unresolved_typedef",
                "C typedef references must resolve to a concrete semantic type before wrapping.",
                {"owner": "result", "type": "absent_t"},
            )
        ]
    }
    assert cyclic.metadata["readiness_blockers"] == [
        _blocker(
            "c_unresolved_typedef",
            "C typedef references must resolve to a concrete semantic type before wrapping.",
            {"owner": "cycle", "type": "cyclic_t"},
        )
    ]


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


def test_c2ir_preserves_c_int_identity_and_stores_compiler_probed_precision():
    converter = CToIRConverter(
        standard_type_report={
            "types": {
                "int": {
                    "available": True,
                    "kind": "integer",
                    "signed": True,
                    "bits": 16,
                    "underlying_c_type": "int",
                }
            }
        }
    )

    semantic_type = converter.visit_type(CInt())

    assert semantic_type.name == "Int"
    assert semantic_type.dtype == "Int16"
    assert semantic_type.metadata == {
        "c_primitive": "int",
        "c_type_fact": {
            "available": True,
            "kind": "integer",
            "signed": True,
            "bits": 16,
            "underlying_c_type": "int",
        },
        "c_type_fact_source": "compiler_probe",
    }


@pytest.mark.parametrize(
    ("ctype", "primitive", "fact", "expected"),
    [
        (CChar(), "char", {"kind": "integer", "signed": False, "bits": 8}, "UInt8"),
        (CLong(), "long", {"kind": "integer", "signed": True, "bits": 32}, "Int32"),
        (CUnsignedLong(), "unsigned long", {"kind": "integer", "signed": False, "bits": 32}, "UInt32"),
        (CLongDouble(), "long double", {"kind": "real", "bits": 64}, "Float64"),
        (CLongDoubleComplex(), "long double _Complex", {"kind": "complex", "bits": 128}, "Complex128"),
        (CBool(), "_Bool", {"kind": "bool", "bits": 8}, "Bool"),
    ],
)
def test_c2ir_uses_compiler_probed_primitive_abi_facts(ctype, primitive, fact, expected):
    semantic_type = CToIRConverter(standard_type_report={"types": {primitive: fact}}).visit_type(ctype)

    assert semantic_type.name == expected
    assert semantic_type.dtype == expected
    assert semantic_type.metadata["c_primitive"] == primitive
    assert semantic_type.metadata["c_type_fact"] == fact
    assert semantic_type.metadata["c_type_fact_source"] == "compiler_probe"
    if primitive == "char":
        assert semantic_type.metadata["c_char_policy"] == "compiler-probed unsigned 8-bit code unit"


def test_c2ir_blocks_compiler_probed_primitive_abi_without_semantic_dtype():
    fact = {"kind": "integer", "signed": True, "bits": 48}
    semantic_type = CToIRConverter(standard_type_report={"types": {"long": fact}}).visit_type(CLong())

    assert semantic_type.name == "CUnsupported"
    assert semantic_type.metadata["c_primitive"] == "long"
    assert semantic_type.metadata["c_type_fact"] == fact
    assert semantic_type.metadata["readiness_blockers"][0]["code"] == "c_unsupported_primitive_abi"


def test_c2ir_uses_enum_specific_underlying_type_facts_when_supplied():
    parsed = parse_c_file(
        "enum status { STATUS_OK = 0, STATUS_ERROR = 255 }; enum status get_status(void);",
        filename="status.h",
    )
    module = CToIRConverter(
        standard_type_report={
            "types": {
                "enum status": {
                    "available": True,
                    "kind": "integer",
                    "signed": False,
                    "bits": 8,
                    "underlying_c_type": "unsigned char",
                }
            }
        }
    ).visit_file(parsed)

    return_type = _function(module, "get_status").return_type
    assert module.classes == []
    assert return_type.name == "UInt8"
    assert return_type.dtype == "UInt8"
    assert return_type.metadata["c_kind"] == "enum"
    assert return_type.metadata["c_enum_type_fact_source"] == "compiler_probe"


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
    assert close_file.arguments[0].semantic_type.dtype == "FILE"
    assert close_file.arguments[0].semantic_type.storage.kind == "reference"
    assert close_file.arguments[0].semantic_type.metadata == {
        "c_standard_type": "FILE",
        "c_standard_type_fact": {
            "available": True,
            "kind": "opaque_handle",
            "pointer_bits": 64,
        },
        "c_opaque_handle": True,
        "c_typedefs": ["FILE"],
    }
    opaque = module.classes[0]
    assert opaque.native_name == "FILE"
    assert opaque.metadata == {"c_kind": "opaque_standard_type"}
    assert asdict(opaque.origin) == _c_origin(
        native_name="FILE",
        source_kind="standard_type",
        source_type="FILE",
    )
    assert assess_semantic_wrap_readiness(module, source="stdio_api.h")["wrappable"] is True


def test_c_function_compatibility_helper_accepts_parser_function():
    parsed = parse_c_file("float half(float value);\n", filename="helpers.h")

    function = c_function_to_semantic_function(parsed.functions[0])

    assert function.name == "half"
    assert function.arguments[0].semantic_type.name == "Float32"
    assert function.return_type.name == "Float32"


def test_c_compatibility_helpers_forward_standard_type_reports():
    report = {
        "types": {
            "measured_t": {
                "available": True,
                "kind": "integer",
                "signed": False,
                "bits": 32,
            }
        }
    }
    measured_type = CTypedef(name="measured_t")
    function = CFunction(name="measure", result_type=measured_type)
    parsed_file = CFile(filename="measure.h", functions=[function])
    project = CProject(files={"measure.h": parsed_file}, functions={"measure": function})

    argument = c_parameter_to_semantic_argument(
        CParameter(name="value", type=measured_type),
        standard_type_report=report,
    )
    converted_type = c_type_to_semantic_type(measured_type, standard_type_report=report)
    converted_function = c_function_to_semantic_function(function, standard_type_report=report)
    cls = c_struct_to_semantic_class(
        CStruct(name="measurement", members=[CVariable(name="value", type=measured_type)]),
        standard_type_report=report,
    )
    assert argument.semantic_type.name == "UInt32"
    assert converted_type.name == "UInt32"
    assert converted_function.return_type.name == "UInt32"
    assert cls.fields[0].semantic_type.name == "UInt32"
    assert _function(
        c_file_to_semantic_module(parsed_file, standard_type_report=report), "measure"
    ).return_type.name == ("UInt32")
    assert _function(
        c_file_to_semantic_modules(parsed_file, standard_type_report=report)[0], "measure"
    ).return_type.name == ("UInt32")
    assert _function(
        c_project_to_semantic_modules(project, standard_type_report=report)[0], "measure"
    ).return_type.name == ("UInt32")
    assert _function(
        c_project_to_semantic_module(project, standard_type_report=report), "measure"
    ).return_type.name == ("UInt32")


@pytest.mark.parametrize(
    ("ctype", "expected_name", "expected_dtype"),
    [
        (CBool(), "Bool", "Bool"),
        (CChar(), "Int8", "Int8"),
        (CSignedChar(), "Int8", "Int8"),
        (CUnsignedChar(), "UInt8", "UInt8"),
        (CShort(), "Int16", "Int16"),
        (CUnsignedShort(), "UInt16", "UInt16"),
        (CInt(), "Int", "Int32"),
        (CUnsignedInt(), "UInt32", "UInt32"),
        (CLong(), "Int64", "Int64"),
        (CUnsignedLong(), "UInt64", "UInt64"),
        (CLongLong(), "Int64", "Int64"),
        (CUnsignedLongLong(), "UInt64", "UInt64"),
        (CFloat(), "Float32", "Float32"),
        (CDouble(), "Float64", "Float64"),
        (CLongDouble(), "Float128", "Float128"),
        (CFloatComplex(), "Complex64", "Complex64"),
        (CDoubleComplex(), "Complex128", "Complex128"),
        (CLongDoubleComplex(), "Complex256", "Complex256"),
    ],
)
def test_c_primitive_precisions_map_to_semantic_types(ctype, expected_name, expected_dtype):
    semantic_type = CToIRConverter().visit_type(ctype)

    assert semantic_type.name == expected_name
    assert semantic_type.dtype == expected_dtype


@pytest.mark.parametrize(
    ("name", "fact", "expected"),
    [
        ("int8_t", {"available": True, "kind": "integer", "signed": True, "bits": 8}, "Int8"),
        ("int16_t", {"available": True, "kind": "integer", "signed": True, "bits": 16}, "Int16"),
        ("int32_t", {"available": True, "kind": "integer", "signed": True, "bits": 32}, "Int32"),
        ("int64_t", {"available": True, "kind": "integer", "signed": True, "bits": 64}, "Int64"),
        ("uint8_t", {"available": True, "kind": "integer", "signed": False, "bits": 8}, "UInt8"),
        ("uint16_t", {"available": True, "kind": "integer", "signed": False, "bits": 16}, "UInt16"),
        ("uint32_t", {"available": True, "kind": "integer", "signed": False, "bits": 32}, "UInt32"),
        ("uint64_t", {"available": True, "kind": "integer", "signed": False, "bits": 64}, "UInt64"),
    ],
)
def test_c_standard_integer_precision_facts_map_to_semantic_types(name, fact, expected):
    semantic_type = CToIRConverter(standard_type_report={"types": {name: fact}}).visit_type(CTypedef(name=name))

    assert semantic_type.name == expected
    assert semantic_type.dtype == expected


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
    assert converter.visit(CParameter(name=None, type=CInt())).metadata["native_position"] == 0
    assert converter.visit(first.structs[0]).name == "point"
    assert converter.visit(CUnion(name="loose_union")).name == "loose_union"
    assert converter.visit(first.variables[0]).name == "value"
    assert converter.visit(CInt()).name == "Int"
    enum_type = converter.visit(CEnum(name="status"))
    assert enum_type.name == "Int"
    assert enum_type.dtype == "Int32"
    assert enum_type.metadata["c_kind"] == "enum"
    assert enum_type.metadata["c_enum"] == "enum status"
    assert enum_type.metadata["c_enum_name"] == "status"
    assert enum_type.metadata["c_underlying_type"] == "Int"
    assert enum_type.origin.native_name == "enum status"
    assert enum_type.origin.metadata["c_type"] == "CEnum"
    with pytest.raises(TypeError) as error:
        converter.visit(object())
    assert str(error.value) == "Unsupported C parse object: <class 'object'>"

    contextual_union = CUnion(name="context_union", members=[CVariable(name="value", type=CInt())])
    contextual_file = CFile(
        filename="contextual.h",
        functions=[
            CFunction(name="contextual", result_type=CTypedef(name="contextual_t")),
            CFunction(
                name="use_context_union",
                parameters=[CParameter(name="value", type=CUnion(name="context_union", is_incomplete=True))],
            ),
        ],
        unions=[contextual_union],
    )
    contextual_module = converter.visit(
        contextual_file,
        typedefs={"contextual_t": CTypedef(name="contextual_t", type=CInt())},
        unions={"context_union": contextual_union},
    )
    assert _function(contextual_module, "contextual").return_type.name == "Int"
    assert _function(contextual_module, "use_context_union").arguments[0].semantic_type.metadata["incomplete"] is False
    assert [cls.name for cls in contextual_module.classes] == ["context_union"]

    assert c_file_to_semantic_module(first).name == "a"
    assert c_type_to_semantic_type(CInt()).name == "Int"
    assert c_parameter_to_semantic_argument(CParameter(name=None, type=CInt()), position=2).name == "arg2"
    default_argument = c_parameter_to_semantic_argument(CParameter(name=None, type=CInt()))
    assert default_argument.name == "arg0"
    assert default_argument.metadata == {"native_position": 0}
    assert c_struct_to_semantic_class(first.structs[0]).name == "point"
    assert [module.name for module in c_project_to_semantic_modules(project)] == ["a", "b"]
    merged = c_project_to_semantic_module(project, name="42 api/project")
    assert merged.name == "_42_api_project"
    assert {function.name for function in merged.functions} == {"f", "g"}
    assert [cls.name for cls in merged.classes] == ["point"]
    assert [variable.name for variable in merged.variables] == ["value"]
    assert merged.metadata == {
        "source_language": "c",
        "counts": {
            "files": 2,
            "functions": 2,
            "structs": 1,
            "unions": 0,
            "enums": 0,
            "typedefs": 0,
            "macros": 0,
            "includes": 0,
            "diagnostics": 0,
        },
    }
    assert asdict(merged.origin) == _c_origin(
        native_name="42 api/project",
        native_scope="42 api/project",
        source_kind="project",
        metadata={"files": ["a.h", "b.h"]},
    )
    assert converter.visit_project_module(project).name == "c_project"
    typedef_project = parse_c_project(
        {
            "types.h": "typedef unsigned long count_t;\n",
            "api.h": "count_t count(void);\n",
        }
    )
    typedef_modules = {module.name: module for module in converter.visit_project(typedef_project)}
    assert _function(typedef_modules["api"], "count").return_type.name == "UInt64"
    assert _function(typedef_modules["api"], "count").return_type.metadata == {"c_typedefs": ["count_t"]}
    typedef_merged = converter.visit_project_module(typedef_project)
    assert _function(typedef_merged, "count").return_type.name == "UInt64"
    assert _function(typedef_merged, "count").return_type.metadata == {"c_typedefs": ["count_t"]}
    count_reference = CTypedef(name="global_count_t")
    count_function = CFunction(name="global_count", result_type=count_reference)
    reference_project = CProject(
        files={"api.h": CFile(filename="api.h", functions=[count_function])},
        functions={"global_count": count_function},
        typedefs={"global_count_t": CTypedef(name="global_count_t", type=CInt())},
    )
    reference_modules = converter.visit_project(reference_project)
    assert _function(reference_modules[0], "global_count").return_type.name == "Int"
    reference_merged = converter.visit_project_module(reference_project)
    assert _function(reference_merged, "global_count").return_type.name == "Int"
    record = CStruct(name="global_record", members=[CVariable(name="value", type=CInt())])
    choice = CUnion(name="global_choice", members=[CVariable(name="value", type=CInt())])
    registry_function = CFunction(
        name="use_global_types",
        parameters=[
            CParameter(name="record", type=CStruct(name="global_record", is_incomplete=True)),
            CParameter(name="choice", type=CUnion(name="global_choice", is_incomplete=True)),
        ],
    )
    registry_project = CProject(
        files={"api.h": CFile(filename="api.h", functions=[registry_function])},
        functions={"use_global_types": registry_function},
        structs={"global_record": record},
        unions={"global_choice": choice},
    )
    registry_modules = converter.visit_project(registry_project)
    registry_args = _function(registry_modules[0], "use_global_types").arguments
    assert registry_args[0].semantic_type.metadata == {"c_kind": "struct", "incomplete": False}
    assert registry_args[1].semantic_type.metadata["incomplete"] is False
    registry_merged = converter.visit_project_module(registry_project)
    registry_merged_args = _function(registry_merged, "use_global_types").arguments
    assert [arg.semantic_type.name for arg in registry_merged_args] == [
        "global_record",
        "global_choice",
    ]
    assert [arg.semantic_type.metadata["incomplete"] for arg in registry_merged_args] == [False, False]


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
    mutable_pointer_variable = converter.visit_variable(
        CVariable(
            name="buffer",
            type=CComposedType(components=[CPointer(), CInt()], source_text="int *buffer"),
        )
    )
    unresolved_variable = converter.visit_variable(
        CVariable(name="missing_value", type=CUnknownType(spelling="missing_t", source_text="missing_t"))
    )
    function = converter.visit_function(parse_c_file("static int legacy();\n", filename="legacy.h").functions[0])
    qualified = converter.visit_type(
        CChar(qualifiers=[CConst(), CVolatile(), CAtomic()], source_text="const volatile _Atomic char")
    )
    unnamed = converter.visit_parameter(CParameter(name=None, type=CInt()))
    located_parameter = converter.visit_parameter(
        CParameter(
            name="located",
            type=CInt(),
            source_location=CSourceLocation(filename="api.h", line=3, column=5, source_line="int located"),
        )
    )
    ownerless_missing_parameter = converter.visit_parameter(
        CParameter(name="missing", type=CUnknownType(spelling="missing_t", source_text="missing_t"))
    )
    callback_parameter = converter.visit_parameter(CParameter(name="callback", type=callback))
    variadic = converter.visit_function(parse_c_file("int log_value(const char *fmt, ...);\n").functions[0])
    direct_callback = converter.visit_type(callback)
    direct_function_type = converter.visit_type(CFunctionType(result_type=CVoid(), parameter_types=[CInt()]))
    void_type = converter.visit_type(CVoid())
    missing_parameter = converter.visit_parameter(
        CParameter(name="missing", type=CUnknownType(spelling="missing_t", source_text="missing_t")),
        owner="load",
    )
    loose_struct = converter.visit_type(CStruct(name="loose"))
    missing_return = converter.visit_function(
        CFunction(name="missing_return", result_type=CUnknownType(spelling="missing_t", source_text="missing_t"))
    )
    unnamed_function = converter.visit_function(
        CFunction(name="unnamed", parameters=[CParameter(name=None, type=CInt())])
    )

    assert variable.visibility == "private"
    assert variable.semantic_type.name == "CFunctionPointer"
    assert variable.semantic_type.dtype == "CFunctionPointer"
    assert variable.semantic_type.metadata == {"source_type": "void (*)(int)"}
    assert asdict(variable.semantic_type.origin) == _c_origin(
        source_kind="function_pointer",
        source_type="void (*)(int)",
    )
    assert field.semantic_type.metadata["c_primitive"] == "int"
    assert field.semantic_type.metadata["c_type_fact"]["bits"] == 32
    assert field.semantic_type.metadata["readiness_blockers"] == [
        _blocker(
            "c_bitfield_unsupported",
            "C bitfields require explicit semantic policy before wrapping.",
            {"owner": "bits", "field": "bits", "bit_width": "3"},
        )
    ]
    assert field.intent == "in"
    assert field.visibility == "public"
    assert mutable_pointer_variable.intent == "inout"
    assert unresolved_variable.semantic_type.metadata["readiness_blockers"][0]["items"] == [
        {"owner": "missing_value", "type": "missing_t"}
    ]
    assert asdict(field.origin) == _c_origin(
        native_name="bits",
        source_kind="variable",
        source_type="CInt",
        metadata={"storage": [], "bit_width": "3"},
    )
    assert function.visibility == "private"
    assert function.metadata == {
        "storage": ["static"],
        "specifiers": [],
        "prototype_style": "unspecified",
        "is_definition": False,
        "readiness_blockers": [
            _blocker(
                "c_unspecified_function_parameters",
                "C functions declared without a prototype do not provide complete parameter types.",
                {"owner": "legacy", "function": "legacy"},
            )
        ],
    }
    assert qualified.name == "Int8"
    assert qualified.metadata["c_char_policy"] == "implementation-defined signed 8-bit code unit"
    assert {blocker["code"] for blocker in qualified.metadata["readiness_blockers"]} == {
        "c_volatile_unsupported",
        "c_atomic_unsupported",
    }
    assert qualified.origin.metadata["c_type"] == "CChar"
    assert qualified.origin.metadata["qualifiers"] == ["const", "volatile", "_Atomic"]
    assert unnamed.name == "arg0"
    assert unnamed.metadata == {"native_position": 0}
    assert located_parameter.origin.source_location == {
        "filename": "api.h",
        "line": 3,
        "column": 5,
        "source_line": "int located",
    }
    assert ownerless_missing_parameter.semantic_type.metadata["readiness_blockers"][0]["items"] == [
        {"owner": "<function>.missing", "type": "missing_t"}
    ]
    assert callback_parameter.semantic_type.metadata == {"source_type": "void (*)(int)"}
    assert unnamed_function.projection[0].native_name == "arg0"
    assert variadic.metadata["readiness_blockers"] == [
        _blocker(
            "c_variadic_function",
            "Variadic C functions require explicit semantic .pyi policy before wrapping.",
            {"owner": "log_value", "function": "log_value"},
        )
    ]
    assert direct_callback.metadata == {"source_type": "void (*)(int)"}
    assert asdict(direct_callback.origin) == _c_origin(
        source_kind="function_pointer",
        source_type="void (*)(int)",
    )
    assert direct_function_type.metadata == {"source_type": "CFunctionType"}
    assert void_type.name == "Any"
    assert void_type.dtype == "Any"
    assert void_type.metadata == {"c_void_pointer_pointee": True}
    assert asdict(void_type.origin) == _c_origin(
        source_kind="type",
        source_type="CVoid",
        metadata={"c_type": "CVoid"},
    )
    assert missing_parameter.semantic_type.metadata["readiness_blockers"] == [
        _blocker(
            "c_unresolved_type",
            "C type references must resolve before wrapping.",
            {"owner": "load.missing", "type": "missing_t"},
        )
    ]
    assert loose_struct.name == "loose"
    assert loose_struct.dtype == "loose"
    assert loose_struct.metadata == {"c_kind": "struct", "incomplete": False}
    assert asdict(loose_struct.origin) == _c_origin(
        native_name="struct loose",
        source_kind="type",
        source_type="struct loose",
        metadata={"c_type": "CStruct"},
    )
    assert missing_return.return_type.metadata["readiness_blockers"][0]["items"] == [
        {"owner": "missing_return.return", "type": "missing_t"}
    ]
    assert converter._return_type(CVoid(), owner="nothing") is None
    assert CToIRConverter().visit_type(CTypedef(name="absent_t")).metadata["readiness_blockers"][0]["code"] == (
        "c_unresolved_typedef"
    )


def test_c2ir_reports_unsupported_type_and_declarator_compositions():
    converter = CToIRConverter(primitive_type_map={CInt: None})

    unresolved = converter.visit_type(
        CUnknownType(spelling="missing_t", source_text="missing_t"),
        owner="missing_owner",
    )
    unsupported_integer = converter.visit_type(CInt(source_text="int"), owner="integer_owner")
    empty = converter.visit_type(CComposedType(components=[], source_text="empty"), owner="empty_owner")
    array_missing_element = converter.visit_type(
        CComposedType(components=[CArray(bound="4")], source_text="missing element"),
        owner="array_owner",
    )
    array_of_pointer = converter.visit_type(
        CComposedType(components=[CArray(bound="4"), CPointer(), CDouble()], source_text="double *items[4]"),
        owner="array_pointer_owner",
    )
    pointer_missing_pointee = converter.visit_type(
        CComposedType(components=[CPointer()], source_text="missing pointee"),
        owner="pointer_owner",
    )
    pointer_composition = converter.visit_type(
        CComposedType(components=[CPointer(), CInt(), CDouble()], source_text="mixed pointer"),
        owner="pointer_composition_owner",
    )
    other_composition = converter.visit_type(
        CComposedType(components=[CInt(), CDouble()], source_text="mixed declarator"),
        owner="composition_owner",
    )

    assert unresolved.name == "missing_t"
    assert unresolved.dtype == "missing_t"
    assert unresolved.metadata == {
        "readiness_blockers": [
            _blocker(
                "c_unresolved_type",
                "C type references must resolve before wrapping.",
                {"owner": "missing_owner", "type": "missing_t"},
            )
        ]
    }
    assert asdict(unresolved.origin) == _c_origin(source_kind="type", source_type="missing_t")
    _assert_unsupported_type(
        unsupported_integer,
        code="c_unsupported_type",
        message="This C type is not supported by the semantic converter.",
        owner="integer_owner",
        source_type="int",
    )
    _assert_unsupported_type(
        empty,
        code="c_empty_composed_type",
        message="C composed type is missing a base type.",
        owner="empty_owner",
        source_type="empty",
    )
    _assert_unsupported_type(
        array_missing_element,
        code="c_array_missing_element_type",
        message="C array type is missing an element type.",
        owner="array_owner",
        source_type="missing element",
    )
    _assert_unsupported_type(
        array_of_pointer,
        code="c_array_of_pointer_unsupported",
        message="C arrays of pointers need explicit semantic policy.",
        owner="array_pointer_owner",
        source_type="double *items[4]",
    )
    _assert_unsupported_type(
        pointer_missing_pointee,
        code="c_pointer_missing_pointee",
        message="C pointer type is missing a pointee type.",
        owner="pointer_owner",
        source_type="missing pointee",
    )
    _assert_unsupported_type(
        pointer_composition,
        code="c_unsupported_composed_type",
        message="This C pointer composition needs explicit semantic policy.",
        owner="pointer_composition_owner",
        source_type="mixed pointer",
    )
    _assert_unsupported_type(
        other_composition,
        code="c_unsupported_composed_type",
        message="This C declarator composition needs explicit semantic policy.",
        owner="composition_owner",
        source_type="mixed declarator",
    )


def test_c2ir_models_pointer_to_arrays_unknown_extents_unions_and_anonymous_aliases():
    converter = CToIRConverter()
    direct_array = converter.visit_type(
        CComposedType(components=[CArray(bound="2"), CInt()], source_text="int values[2]"),
        owner="values",
    )
    ownerless_array = converter.visit_type(
        CComposedType(components=[CArray(bound=None), CInt()], source_text="int values[]")
    )
    named_unknown_array = converter.visit_type(
        CComposedType(components=[CArray(bound=None), CInt()], source_text="int named_values[]"),
        owner="named_values",
    )
    pointer_array = converter.visit_type(
        CComposedType(components=[CPointer(), CArray(bound=None), CDouble()], source_text="double (*)[]"),
        owner="matrix",
    )
    pointer_matrix = converter.visit_type(
        CComposedType(
            components=[CPointer(), CArray(bound="2"), CArray(bound="3"), CInt()],
            source_text="int (*)[2][3]",
        ),
        owner="matrix",
    )
    choice = CUnion(
        name="choice",
        members=[CVariable(name="integer", type=CInt())],
        source_location=CSourceLocation(filename="choice.h", line=1, column=1, source_line="union choice;"),
    )
    converter.unions = {"choice": choice}
    union_type = converter.visit_type(CUnion(name="choice"), owner="selected")
    anon_struct = CStruct(anonymous_id="anon_struct_1")
    anon_union = CUnion(anonymous_id="anon_union_1")
    converter.typedefs = {
        "record_t": CTypedef(name="record_t", type=anon_struct),
        "variant_t": CTypedef(name="variant_t", type=anon_union),
    }

    assert direct_array.name == "Int"
    assert direct_array.rank == 1
    assert direct_array.shape == ["2"]
    assert direct_array.storage.array.shape == ["2"]
    assert ownerless_array.metadata["readiness_blockers"] == [
        _blocker(
            "c_array_extent_ambiguous",
            "C array parameters with unknown extents need explicit semantic shape policy.",
            {"owner": "int values[]", "type": "int values[]"},
        )
    ]
    assert named_unknown_array.metadata["readiness_blockers"][0]["items"] == [
        {"owner": "named_values", "type": "int named_values[]"}
    ]
    assert pointer_array.storage.pointer_depth == 1
    assert pointer_array.storage.array.source_shape == [":"]
    assert pointer_array.storage.metadata["c_pointer_to_array"] is True
    assert pointer_array.metadata["readiness_blockers"] == [
        _blocker(
            "c_array_extent_ambiguous",
            "C array parameters with unknown extents need explicit semantic shape policy.",
            {"owner": "matrix", "type": "double (*)[]"},
        )
    ]
    assert pointer_matrix.name == "Int"
    assert pointer_matrix.shape == ["2", "3"]
    assert union_type.name == "choice"
    assert union_type.dtype == "choice"
    assert union_type.metadata == {
        "c_kind": "union",
        "incomplete": False,
        "readiness_blockers": [
            _blocker(
                "c_union_unsupported",
                "C union arguments and returns require explicit semantic policy before wrapping.",
                {"owner": "selected", "type": "union choice"},
            )
        ],
    }
    assert asdict(union_type.origin) == _c_origin(
        native_name="union choice",
        source_kind="type",
        source_type="union choice",
        metadata={"c_type": "CUnion"},
    )
    semantic_union = converter.visit_union(choice)
    assert semantic_union.name == "choice"
    assert semantic_union.native_name == "union choice"
    assert [field.name for field in semantic_union.fields] == ["integer"]
    assert semantic_union.metadata == {"c_kind": "union", "incomplete": False}
    assert asdict(semantic_union.origin) == _c_origin(
        native_name="union choice",
        source_kind="union",
        source_type="union choice",
        source_location={"filename": "choice.h", "line": 1, "column": 1, "source_line": "union choice;"},
    )
    assert converter.visit_struct(anon_struct).name == "record_t"
    assert converter.visit_union(anon_union).name == "variant_t"
    assert converter.visit_struct(CStruct()).name == "anonymous_struct"
    assert converter.visit_union(CUnion()).name == "anonymous_union"
    assert CToIRConverter().visit_type(CUnion(name="fresh_union")).name == "fresh_union"


def test_c2ir_preserves_nested_unresolved_owners_and_private_opaque_bases():
    converter = CToIRConverter()
    nested_array = converter.visit_type(
        CComposedType(
            components=[CArray(bound="2"), CUnknownType(spelling="missing_t", source_text="missing_t")],
            source_text="missing_t values[2]",
        ),
        owner="values",
    )
    nested_pointer = converter.visit_type(
        CComposedType(
            components=[CPointer(), CUnknownType(spelling="missing_t", source_text="missing_t")],
            source_text="missing_t *value",
        ),
        owner="value",
    )
    nested_pointer_array = converter.visit_type(
        CComposedType(
            components=[CPointer(), CArray(bound="2"), CUnknownType(spelling="missing_t", source_text="missing_t")],
            source_text="missing_t (*)[2]",
        ),
        owner="matrix",
    )
    singleton = converter.visit_type(
        CComposedType(components=[CUnknownType(spelling="missing_t", source_text="missing_t")]),
        owner="singleton",
    )
    private_class = SemanticClass(
        name="private_handle",
        base_classes=["Opaque"],
        origin=SemanticOrigin(source_language="c", source_location={"filename": "private.h"}),
    )
    private_module = SemanticModule(name="api", classes=[private_class])
    private_file = CFile(
        filename="api.h",
        preprocessing_recipe={"included_files": [{"path": "private.h", "exposure": "private"}]},
    )
    converter._apply_include_exposure(private_module, private_file)

    assert nested_array.metadata["readiness_blockers"][0]["items"] == [{"owner": "values", "type": "missing_t"}]
    assert nested_pointer.metadata["readiness_blockers"][0]["items"] == [{"owner": "value", "type": "missing_t"}]
    assert nested_pointer_array.metadata["readiness_blockers"][0]["items"] == [{"owner": "matrix", "type": "missing_t"}]
    assert singleton.metadata["readiness_blockers"][0]["items"] == [{"owner": "singleton", "type": "missing_t"}]
    assert private_class.visibility == "private"
    assert private_class.base_classes == ["Opaque"]


def test_c2ir_marks_incomplete_by_value_structs_and_preserves_initializer_locations():
    incomplete = CStruct(name="handle", is_incomplete=True)
    converter = CToIRConverter()
    converter.structs = {"handle": incomplete}
    parameter = converter.visit_parameter(CParameter(name="handle", type=incomplete), owner="open")
    pointer_parameter = converter.visit_parameter(
        CParameter(
            name="handle",
            type=CComposedType(
                components=[CPointer(), CPointer(), incomplete],
                source_text="struct handle **",
            ),
        ),
        owner="open",
    )
    array_parameter = converter.visit_parameter(
        CParameter(
            name="handles",
            type=CComposedType(
                components=[CArray(bound="2"), incomplete],
                source_text="struct handle handles[2]",
            ),
        ),
        owner="open",
    )
    variable = converter.visit_variable(
        CVariable(
            name=None,
            type=incomplete,
            initializer=CInitializer("factory()"),
            source_location=CSourceLocation(filename="api.h", line=2, column=4, source_line="struct handle h;"),
        )
    )
    named_variable = converter.visit_variable(CVariable(name="handle", type=incomplete))
    return_type = converter.visit_function(CFunction(name="open_handle", result_type=incomplete)).return_type

    assert parameter.semantic_type.metadata["readiness_blockers"] == [
        _blocker(
            "c_incomplete_struct_by_value",
            "Incomplete C structs can only be wrapped through explicit pointer or opaque-handle policy.",
            {"owner": "open.handle", "type": "handle"},
        )
    ]
    assert pointer_parameter.semantic_type.storage.kind == "pointer"
    assert "readiness_blockers" not in pointer_parameter.semantic_type.metadata
    assert array_parameter.semantic_type.storage.kind == "array"
    assert "readiness_blockers" not in array_parameter.semantic_type.metadata
    assert named_variable.semantic_type.metadata["readiness_blockers"] == [
        _blocker(
            "c_incomplete_struct_by_value",
            "Incomplete C structs can only be wrapped through explicit pointer or opaque-handle policy.",
            {"owner": "handle", "type": "handle"},
        )
    ]
    assert return_type.metadata["readiness_blockers"] == [
        _blocker(
            "c_incomplete_struct_by_value",
            "Incomplete C structs can only be wrapped through explicit pointer or opaque-handle policy.",
            {"owner": "open_handle.return", "type": "handle"},
        )
    ]
    assert variable.name == "<anonymous>"
    assert variable.default_value == "factory()"
    assert variable.origin.source_location["filename"] == "api.h"


def test_c2ir_standard_type_facts_and_numeric_constant_edge_cases():
    class Report:
        types: ClassVar = {
            "signed_size": {"kind": "integer", "signed": True, "bits": 16},
            "real_size": {"kind": "real", "bits": 32},
            "missing": {"available": False, "kind": "integer", "signed": False, "bits": 32},
        }

    converter = CToIRConverter(standard_type_report=Report())
    signed_size = converter._standard_semantic_type("signed_size")
    real_size = converter._standard_semantic_type("real_size")
    assert signed_size.name == "Int16"
    assert signed_size.dtype == "Int16"
    assert signed_size.metadata == {
        "c_standard_type": "signed_size",
        "c_standard_type_fact": {"kind": "integer", "signed": True, "bits": 16},
    }
    assert real_size.name == "Float32"
    assert real_size.dtype == "Float32"
    assert real_size.metadata == {
        "c_standard_type": "real_size",
        "c_standard_type_fact": {"kind": "real", "bits": 32},
    }
    fallback = CToIRConverter()._standard_semantic_type("size_t")
    assert fallback.name == "SizeT"
    assert fallback.dtype == "SizeT"
    assert fallback.metadata == {"c_standard_type": "size_t", "c_standard_type_fallback": True}
    assert converter._standard_semantic_type("missing") is None
    assert converter._standard_semantic_type("not_standard") is None
    opaque_converter = CToIRConverter(
        standard_type_report={
            "implicit_handle": {"kind": "opaque_handle"},
            "missing_handle": {"available": False, "kind": "opaque_handle"},
        }
    )
    assert opaque_converter._standard_semantic_type("implicit_handle").name == "implicit_handle"
    assert opaque_converter._standard_semantic_type("missing_handle") is None
    assert CToIRConverter._standard_type_facts(object()) == {}
    assert CToIRConverter._integer_literal_value(None) is None
    assert CToIRConverter._integer_literal_value("value") is None
    assert CToIRConverter._integer_macro_expression("(MISSING + 1)", {}) is False
    assert CToIRConverter._integer_macro_expression("(1 +)", {}) is False

    parsed = parse_c_file(
        "enum default_status { DEFAULT_OK, DEFAULT_NEXT };\nenum status { STATUS_EXPR = UNKNOWN, STATUS_NEXT };\n",
        filename="edge_constants.h",
    )
    parsed.macros = [
        CMacro(name="RATE", value="1.5"),
        CMacro(name="BAD", value="(MISSING + 1)"),
    ]
    constants = {variable.name: variable for variable in converter.visit_file(parsed).variables}
    assert constants["RATE"].semantic_type.name == "Float64"
    assert constants["DEFAULT_OK"].default_value == "0"
    assert constants["DEFAULT_NEXT"].default_value == "1"
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
    orphan_error = CDiagnostic(code="C_ORPHAN", message="orphan", severity="error")
    c_file = CFile(
        filename=None,
        macro_dependencies=[dependency],
        diagnostics=[warning, duplicate_dependency, error, orphan_error],
    )
    project = CProject(files={"bad.h": c_file}, diagnostics=[error, orphan_error])
    converter = CToIRConverter()

    module = converter.visit_file(c_file)
    merged = converter.visit_project_module(project)
    file_codes = {blocker["code"] for blocker in module.metadata["readiness_blockers"]}
    project_codes = {blocker["code"] for blocker in merged.metadata["readiness_blockers"]}

    expected_blockers = [
        _blocker(
            "c_macro_dependent_declaration",
            "Some C declarations depend on macros that were recorded but not expanded.",
            {
                "owner": "<c-source>",
                "macro": "API",
                "context": "declaration",
                "source": "API(int) f(void);",
            },
        ),
        _blocker(
            "c_c_bad_decl",
            "bad declaration",
            {
                "owner": "broken",
                "diagnostic_code": "C_BAD_DECL",
                "unit_kind": "function",
                "unit_name": "broken",
            },
        ),
        _blocker(
            "c_c_orphan",
            "orphan",
            {
                "owner": "<c-source>",
                "diagnostic_code": "C_ORPHAN",
                "unit_kind": None,
                "unit_name": None,
            },
        ),
    ]
    assert module.name == "c_module"
    assert file_codes == {"c_macro_dependent_declaration", "c_c_bad_decl", "c_c_orphan"}
    assert project_codes == {"c_macro_dependent_declaration", "c_c_bad_decl", "c_c_orphan"}
    assert module.metadata["readiness_blockers"] == expected_blockers
    assert merged.metadata["readiness_blockers"] == expected_blockers
