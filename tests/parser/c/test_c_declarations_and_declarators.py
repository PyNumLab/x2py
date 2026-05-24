# -*- coding: utf-8 -*-
"""C declaration-specifier and composed-type parser tests."""

import pytest


def test_primitive_specifiers_create_concrete_primitive_types():
    from c_parser import CBool, CShort, CUnsignedLongLong, parse_c_file

    parsed = parse_c_file(
        """
unsigned long long next_id(void);
signed short clamp_short(signed short value);
_Bool enabled(void);
""",
        filename="primitives.h",
    )

    functions = {function.name: function for function in parsed.functions}
    assert isinstance(functions["next_id"].result_type, CUnsignedLongLong)
    assert isinstance(functions["clamp_short"].parameters[0].type, CShort)
    assert isinstance(functions["enabled"].result_type, CBool)


@pytest.mark.parametrize(
    ("spelling", "expected_name"),
    [
        ("void", "CVoid"),
        ("_Bool", "CBool"),
        ("char", "CChar"),
        ("signed char", "CSignedChar"),
        ("unsigned char", "CUnsignedChar"),
        ("short", "CShort"),
        ("short int", "CShort"),
        ("signed short", "CShort"),
        ("signed short int", "CShort"),
        ("unsigned short", "CUnsignedShort"),
        ("unsigned short int", "CUnsignedShort"),
        ("int", "CInt"),
        ("signed", "CInt"),
        ("signed int", "CInt"),
        ("unsigned", "CUnsignedInt"),
        ("unsigned int", "CUnsignedInt"),
        ("long", "CLong"),
        ("long int", "CLong"),
        ("signed long", "CLong"),
        ("signed long int", "CLong"),
        ("unsigned long", "CUnsignedLong"),
        ("unsigned long int", "CUnsignedLong"),
        ("long long", "CLongLong"),
        ("long long int", "CLongLong"),
        ("signed long long", "CLongLong"),
        ("signed long long int", "CLongLong"),
        ("unsigned long long", "CUnsignedLongLong"),
        ("unsigned long long int", "CUnsignedLongLong"),
        ("float", "CFloat"),
        ("double", "CDouble"),
        ("long double", "CLongDouble"),
        ("float _Complex", "CFloatComplex"),
        ("_Complex", "CDoubleComplex"),
        ("double _Complex", "CDoubleComplex"),
        ("long double _Complex", "CLongDoubleComplex"),
    ],
)
def test_every_supported_primitive_spelling_creates_a_concrete_ctype(spelling, expected_name):
    import c_parser
    from c_parser import CType, parse_c_file

    function = parse_c_file(f"{spelling} primitive(void);\n", filename="primitive_table.h").functions[0]
    expected = getattr(c_parser, expected_name)

    assert isinstance(function.result_type, expected)
    assert isinstance(function.result_type, CType)


@pytest.mark.parametrize(
    ("spelling", "expected_name"),
    [
        ("int unsigned", "CUnsignedInt"),
        ("int long unsigned", "CUnsignedLong"),
        ("double long", "CLongDouble"),
        ("_Complex float", "CFloatComplex"),
    ],
)
def test_valid_reordered_primitive_specifiers_are_normalized(spelling, expected_name):
    import c_parser
    from c_parser import parse_c_file

    function = parse_c_file(f"{spelling} primitive(void);\n", filename="reordered_primitives.h").functions[0]

    assert isinstance(function.result_type, getattr(c_parser, expected_name))
    assert function.result_type.source_text == spelling


@pytest.mark.parametrize(
    ("source", "expected_column"),
    [
        ("unsigned float value;\n", 1),
        ("void bad(long char value);\n", 1),
        ("struct bad { signed unsigned value; };\n", 14),
        ("unsigned float bad(void) { return 0; }\n", 1),
    ],
)
def test_invalid_primitive_specifier_sequences_raise_parse_errors(source, expected_column):
    from c_parser import CParseError, parse_c_file

    with pytest.raises(CParseError, match="Invalid type specifier sequence") as error:
        parse_c_file(source, filename="invalid_specifiers.h")

    assert error.value.code == "CPARSE003"
    assert (
        f"invalid_specifiers.h:1:{expected_column}: error[CPARSE003]"
        in error.value.format_diagnostic(color=False)
    )


def test_unresolved_single_typedef_name_is_preserved_until_resolution():
    from c_parser import CTypedef, parse_c_file

    parsed = parse_c_file("external_type value;\n", filename="deferred_typedef.h")

    assert isinstance(parsed.variables[0].type, CTypedef)
    assert parsed.variables[0].type.name == "external_type"
    assert parsed.diagnostics == []


def test_pointer_qualifiers_belong_to_the_component_they_qualify():
    from c_parser import CComposedType, CConst, CDouble, CPointer, CRestrict, parse_c_file

    parsed = parse_c_file(
        "void copy(const double * restrict src, double * restrict dst);\n",
        filename="qualifiers.h",
    )

    params = {parameter.name: parameter for parameter in parsed.functions[0].parameters}
    src = params["src"].type
    dst = params["dst"].type
    assert isinstance(src, CComposedType)
    assert isinstance(src.components[0], CPointer)
    assert src.components[0].qualifiers == [CRestrict()]
    assert isinstance(src.components[1], CDouble)
    assert src.components[1].qualifiers == [CConst()]
    assert dst.components[0].qualifiers == [CRestrict()]


def test_array_parameters_preserve_declarations_and_expose_adjusted_pointer_types():
    from c_parser import CArray, CComposedType, CConst, CDouble, CInt, CPointer, parse_c_file

    parsed = parse_c_file(
        "void solve(size_t n, double a[static 4], const int shape[2], int work[const *], int matrix[3][4]);\n",
        filename="arrays.h",
    )

    params = {parameter.name: parameter for parameter in parsed.functions[0].parameters}
    a_declared = params["a"].declared_type
    assert isinstance(a_declared, CComposedType)
    assert [type(component) for component in a_declared.components] == [CArray, CDouble]
    assert a_declared.components[0].bound == "4"
    assert a_declared.components[0].is_static_minimum is True
    assert [type(component) for component in params["a"].type.components] == [CPointer, CDouble]

    shape_declared = params["shape"].declared_type
    assert shape_declared.components[0].bound == "2"
    assert shape_declared.components[-1].qualifiers == [CConst()]
    assert [type(component) for component in params["shape"].type.components] == [CPointer, CInt]
    assert params["shape"].type.components[-1].qualifiers == [CConst()]

    work_declared = params["work"].declared_type
    assert work_declared.components[0].qualifiers == [CConst()]
    assert work_declared.components[0].is_variable_length is True
    assert params["work"].type.components[0].qualifiers == [CConst()]

    matrix_declared = params["matrix"].declared_type
    assert [type(component) for component in matrix_declared.components] == [CArray, CArray, CInt]
    assert [component.bound for component in matrix_declared.components[:2]] == ["3", "4"]
    assert [type(component) for component in params["matrix"].type.components] == [CPointer, CArray, CInt]
    assert params["matrix"].type.components[1].bound == "4"


def test_multiple_declarators_share_specifiers_but_have_distinct_compositions():
    from c_parser import CArray, CComposedType, CConst, CInt, CPointer, parse_c_file

    parsed = parse_c_file("extern const int *left, right[4];\n", filename="variables.h")

    variables = {variable.name: variable for variable in parsed.variables}
    assert variables["left"].storage == ["extern"]
    assert isinstance(variables["left"].type, CComposedType)
    assert [type(component) for component in variables["left"].type.components] == [CPointer, CInt]
    assert [type(component) for component in variables["right"].type.components] == [CArray, CInt]
    assert variables["right"].type.components[0].bound == "4"
    assert variables["right"].type.components[-1].qualifiers == [CConst()]


def test_typedefs_and_typedef_references_are_concrete_types():
    from c_parser import CArray, CComposedType, CDouble, CPointer, CStruct, CTypedef, CUnsignedLong, parse_c_file

    parsed = parse_c_file(
        """
struct state;
typedef unsigned long api_size;
typedef const struct state *state_ref;
typedef double vector3[3];
typedef vector3 basis3[3];
state_ref current_state(void);
void set_basis(basis3 basis);
""",
        filename="typedef_layers.h",
    )

    typedefs = {typedef.name: typedef for typedef in parsed.typedefs}
    assert isinstance(typedefs["api_size"].type, CUnsignedLong)
    state_ref = typedefs["state_ref"].type
    assert isinstance(state_ref, CComposedType)
    assert [type(component) for component in state_ref.components] == [CPointer, CStruct]
    assert state_ref.components[-1].name == "state"
    assert isinstance(typedefs["vector3"].type.components[0], CArray)
    assert isinstance(typedefs["vector3"].type.components[-1], CDouble)
    assert isinstance(typedefs["basis3"].type.components[-1], CTypedef)
    assert typedefs["basis3"].type.components[-1].name == "vector3"
    assert isinstance(parsed.functions[1].parameters[0].type, CTypedef)


def test_variables_preserve_initializer_text_arrays_and_concrete_tag_types():
    from c_parser import CArray, CComposedType, CEnum, CInt, CStruct, CUnion, parse_c_file

    parsed = parse_c_file(
        """
const struct state *global_state = 0;
volatile union scalar *global_scalar;
const enum status last_status = STATUS_OK;
double matrix[3][4];
int answer = 42;
""",
        filename="variables_richer.h",
    )

    variables = {variable.name: variable for variable in parsed.variables}
    assert isinstance(variables["global_state"].type.components[-1], CStruct)
    assert variables["global_state"].type.components[-1].name == "state"
    assert variables["global_state"].initializer.source_text == "0"
    assert isinstance(variables["global_scalar"].type.components[-1], CUnion)
    assert isinstance(variables["last_status"].type, CEnum)
    assert variables["last_status"].initializer.source_text == "STATUS_OK"
    assert [component.bound for component in variables["matrix"].type.components[:2]] == ["3", "4"]
    assert all(isinstance(component, CArray) for component in variables["matrix"].type.components[:2])
    assert isinstance(variables["answer"].type, CInt)
    assert variables["answer"].initializer.source_text == "42"


def test_parameters_preserve_concrete_struct_union_and_enum_uses():
    from c_parser import CEnum, CStruct, CUnion, parse_c_file

    parsed = parse_c_file(
        "void consume(const struct state *s, union scalar *u, enum status status);\n",
        filename="tag_params.h",
    )

    params = {parameter.name: parameter for parameter in parsed.functions[0].parameters}
    assert isinstance(params["s"].type.components[-1], CStruct)
    assert params["s"].type.components[-1].name == "state"
    assert isinstance(params["u"].type.components[-1], CUnion)
    assert isinstance(params["status"].type, CEnum)


def test_incomplete_structs_and_pointer_uses_are_concrete_objects():
    from c_parser import CComposedType, CPointer, CStruct, parse_c_file

    parsed = parse_c_file(
        """
struct handle;
struct handle *open_handle(void);
void close_handle(struct handle *handle);
""",
        filename="opaque.h",
    )

    handle = parsed.structs[0]
    assert isinstance(handle, CStruct)
    assert handle.name == "handle"
    assert handle.is_incomplete is True
    assert handle.members == []

    functions = {function.name: function for function in parsed.functions}
    result = functions["open_handle"].result_type
    assert isinstance(result, CComposedType)
    assert isinstance(result.components[0], CPointer)
    assert isinstance(result.components[1], CStruct)
    assert result.components[1].name == "handle"


def test_storage_is_declaration_metadata_and_qualifiers_are_type_metadata():
    from c_parser import CAtomic, CConst, CUnsignedLong, CVolatile, parse_c_file

    parsed = parse_c_file(
        """
extern int api_errno;
static const double scale_factor = 1.0;
_Thread_local unsigned long tls_counter;
register volatile int scratch;
_Atomic int atomic_counter;
""",
        filename="storage_variables.h",
    )

    variables = {variable.name: variable for variable in parsed.variables}
    assert variables["api_errno"].storage == ["extern"]
    assert variables["scale_factor"].storage == ["static"]
    assert variables["scale_factor"].type.qualifiers == [CConst()]
    assert variables["tls_counter"].storage == ["_Thread_local"]
    assert isinstance(variables["tls_counter"].type, CUnsignedLong)
    assert variables["scratch"].storage == ["register"]
    assert variables["scratch"].type.qualifiers == [CVolatile()]
    assert variables["atomic_counter"].type.qualifiers == [CAtomic()]


def test_function_bodies_do_not_contribute_local_variables():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
int compute(int x) { int local_value = x + 1; return local_value; }
extern int exported_value;
""",
        filename="locals.c",
    )

    assert [variable.name for variable in parsed.variables] == ["exported_value"]


def test_declarations_return_concrete_objects_instead_of_kind_fields():
    from c_parser import CArray, CFunction, CFunctionType, CInt, CPointer, CStruct, CTypedef, CVariable, parse_c_file

    parsed = parse_c_file(
        """
struct handle;
typedef int (*compare_fn)(const void *, const void *);
extern int *values[4];
extern int (*matrix)[4];
int add(int a, int b);
void sort_items(int (*fallback)(const void *, const void *));
""",
        filename="declaration_matrix.h",
    )

    assert isinstance(parsed.structs[0], CStruct)
    assert all(isinstance(typedef, CTypedef) for typedef in parsed.typedefs)
    assert all(isinstance(variable, CVariable) for variable in parsed.variables)
    assert all(isinstance(function, CFunction) for function in parsed.functions)

    compare = parsed.typedefs[0].type
    assert [type(component) for component in compare.components] == [CPointer, CFunctionType]
    values, matrix = parsed.variables
    assert [type(component) for component in values.type.components] == [CArray, CPointer, CInt]
    assert [type(component) for component in matrix.type.components] == [CPointer, CArray, CInt]
    assert parsed.functions[1].parameters[0].callback_candidate is True


def test_composite_definitions_are_concrete_objects_and_static_assert_is_diagnostic():
    from c_parser import CEnum, CStruct, CUnion, CVariable, parse_c_file

    parsed = parse_c_file(
        """
struct point { double x; double y; };
union value { int i; double d; };
enum status { STATUS_OK = 0 };
_Static_assert(sizeof(int) == 4, "expected int width");
""",
        filename="composites.h",
    )

    assert isinstance(parsed.structs[0], CStruct)
    assert all(isinstance(member, CVariable) for member in parsed.structs[0].members)
    assert [member.name for member in parsed.structs[0].members] == ["x", "y"]
    assert isinstance(parsed.unions[0], CUnion)
    assert isinstance(parsed.enums[0], CEnum)
    assert [diagnostic.unit_kind for diagnostic in parsed.diagnostics] == ["static_assert"]


def test_parenthesized_declarators_preserve_pointer_array_order():
    from c_parser import CArray, CInt, CPointer, parse_c_file

    parsed = parse_c_file("extern int *values[4];\nextern int (*matrix)[4];\n", filename="paren_decl.h")
    variables = {variable.name: variable for variable in parsed.variables}

    assert [type(component) for component in variables["values"].type.components] == [CArray, CPointer, CInt]
    assert [type(component) for component in variables["matrix"].type.components] == [CPointer, CArray, CInt]


def test_function_type_discards_placeholder_parameter_names():
    from c_parser import CFunctionType, CPointer, parse_c_file

    parsed = parse_c_file(
        "typedef int (*compare_fn)(const void *left, const void *right);\n",
        filename="callback_typedef.h",
    )

    type_ = parsed.typedefs[0].type
    assert isinstance(type_.components[0], CPointer)
    signature = type_.components[1]
    assert isinstance(signature, CFunctionType)
    assert len(signature.parameter_types) == 2
    assert not hasattr(signature, "parameters")


def test_recursive_compositions_cover_tables_callback_arrays_and_function_results():
    from c_parser import CArray, CFunctionType, CInt, CPointer, parse_c_file

    parsed = parse_c_file(
        """
extern int *(*table)[4];
typedef int (*callback_table[8])(int);
int (*factory(void))(int);
int direct(void), *value;
""",
        filename="recursive_declarators.h",
    )

    variables = {variable.name: variable for variable in parsed.variables}
    assert [type(component) for component in variables["table"].type.components] == [
        CPointer,
        CArray,
        CPointer,
        CInt,
    ]
    assert [type(component) for component in variables["value"].type.components] == [CPointer, CInt]
    callbacks = parsed.typedefs[0].type
    assert [type(component) for component in callbacks.components] == [CArray, CPointer, CFunctionType]
    functions = {function.name: function for function in parsed.functions}
    assert set(functions) == {"factory", "direct"}
    assert [type(component) for component in functions["factory"].result_type.components] == [
        CPointer,
        CFunctionType,
    ]


def test_unimplemented_declaration_extensions_are_diagnosed_not_partially_modeled():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        """
int visible __attribute__((visibility("default")));
int outdated [[deprecated]];
_Alignas(16) int aligned_value;
_Atomic(int) atomic_value;
""",
        filename="extensions.h",
    )

    assert parsed.variables == []
    assert [diagnostic.unit_kind for diagnostic in parsed.diagnostics] == [
        "attribute_declaration",
        "attribute_declaration",
        "alignment_declaration",
        "atomic_type_declaration",
    ]


def test_unconsumed_declarator_suffixes_are_diagnosed_not_silently_discarded():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        'extern int retained, pinned asm("r0");\nint run(int value asm("r0"));\n',
        filename="declarator_extensions.h",
    )

    assert [variable.name for variable in parsed.variables] == ["retained"]
    assert parsed.functions == []
    assert [diagnostic.code for diagnostic in parsed.diagnostics] == [
        "C_UNSUPPORTED_DECLARATOR",
        "C_UNSUPPORTED_DECLARATOR",
    ]


def test_storage_class_and_inline_specifiers_are_recorded_on_functions():
    from c_parser import parse_c_file

    parsed = parse_c_file(
        "static inline int local_add(int a, int b) { return a + b; }\nextern int exported_add(int a, int b);\n",
        filename="storage.c",
    )

    functions = {function.name: function for function in parsed.functions}
    assert functions["local_add"].storage == ["static"]
    assert "inline" in functions["local_add"].specifiers
    assert functions["exported_add"].storage == ["extern"]
