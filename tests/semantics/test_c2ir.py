# -*- coding: utf-8 -*-
"""C parser model to semantic IR conversion tests."""

from c_parser import parse_c_file
from semantics.c2ir import (
    CToIRConverter,
    c_file_to_semantic_modules,
    c_function_to_semantic_function,
)
from semantics.readiness import assess_semantic_wrap_readiness


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

    report = assess_semantic_wrap_readiness(module, source="structs.h")
    assert report["wrappable"] is True


def test_c2ir_converts_enum_constants_and_simple_macro_constants():
    parsed = parse_c_file(
        """
#define API_VERSION 3
enum status { STATUS_OK = 0, STATUS_WARN, STATUS_ERROR = 10 };
""",
        filename="constants.h",
    )
    module = c_file_to_semantic_modules(parsed)[0]

    constants = {var.name: var for var in module.variables}
    assert constants["API_VERSION"].default_value == "3"
    assert constants["API_VERSION"].semantic_type.constraints[0].name == "Constant"
    assert constants["STATUS_WARN"].default_value == "1"
    assert constants["STATUS_ERROR"].default_value == "10"


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
