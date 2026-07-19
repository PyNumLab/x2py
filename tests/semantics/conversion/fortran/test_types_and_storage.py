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
    ProjectionMapping,
    SemanticArgument,
    SemanticConstraint,
    SemanticFunction,
    SemanticMethod,
    SemanticType,
    array_contract,
    asdict,
    collect_fortran_type_storage_requirements,
    emit_module,
    fortran_module_to_semantic_module,
    fortran_type_storage_expression,
    get_class,
    get_function,
    has_constraint,
    json,
    native_contract_issues,
    parse_fortran_source,
    parse_pyi_text,
    pytest,
    re,
)


def test_converter_visitor_and_compatibility_methods_cover_public_paths():
    converter = FortranToIRConverter()
    scale = FortranVariable(name="scale", base_type="real", kind="8", is_parameter=True)
    arg = FortranArgument(
        name="x",
        base_type="real",
        kind="8",
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

    assert converter.visit(parsed)[0].name == "m"
    assert converter.visit(module).functions[0].visibility == "private"
    assert converter.visit(proc, visibility="private").visibility == "private"
    assert converter.visit(proc).visibility == "public"

    semantic_arg = converter.visit(arg)
    assert semantic_arg.semantic_type.storage.kind == "reference"
    assert semantic_arg.semantic_type.storage.mutable is True
    assert semantic_arg.visibility == "public"
    assert semantic_arg.origin.source_language == "fortran"
    assert semantic_arg.origin.native_name == "x"
    assert semantic_arg.origin.source_kind == "argument"

    semantic_var = converter.visit(scale)
    assert semantic_var.name == "Float64"
    assert has_constraint(semantic_var, "Constant")
    assert converter.visit(arg).name == "x"
    assert converter.visit(proc).name == "work"
    assert converter.visit(proc).visibility == "public"
    assert converter.visit(dtype, procedure_lookup={}).base_classes == ["base_t"]
    assert converter.visit(module).imports[0].items[0].target == "i32"

    modules = converter.visit(parsed)
    assert [module.name for module in modules] == ["m", "standalone_source"]
    assert converter.visit(FortranProject(files=[parsed]))[0].name == "m"


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
        converter.visit(FortranVariable(name="state", base_type="derived"))

    with pytest.raises(ValueError, match="Unknown Fortran datatype"):
        converter.visit(FortranVariable(name="x", base_type="unknown"))

    with pytest.raises(ValueError) as error:
        converter.visit(FortranVariable(name="x", base_type="real", kind="selected_real_kind(33)"))
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


def test_converter_preserves_allocatable_target_metadata():
    source = """
module alloc_target_mod
  real(8), allocatable, target :: values(:)
  type :: box
    real(8), allocatable :: field(:)
  end type box
end module alloc_target_mod
"""
    module = FortranToIRConverter().visit(parse_fortran_source(source).modules[0])

    values = module.variables[0]
    assert values.name == "values"
    assert values.semantic_type.storage.array.allocatable is True
    assert values.semantic_type.metadata["aliased"] is True

    field = module.classes[0].fields[0]
    assert field.semantic_type.storage.array.allocatable is True
    assert "aliased" not in field.semantic_type.metadata


def test_fortran_enum_bind_c_lowers_to_integer_constants():
    source = """
module colors_mod
  enum, bind(C)
    enumerator :: red = -1, blue, green = red + 11, yellow
  end enum
contains
  integer(c_int) function get_color() bind(C)
    use iso_c_binding, only: c_int
    get_color = green
  end function get_color
end module colors_mod
"""

    parsed = parse_fortran_source(source)
    module = fortran_module_to_semantic_module(parsed)
    constants = {var.name: var for var in module.variables}

    assert [(name, constants[name].default_value) for name in ("red", "blue", "green", "yellow")] == [
        ("red", "-1"),
        ("blue", "0"),
        ("green", "10"),
        ("yellow", "11"),
    ]
    assert constants["red"].semantic_type.name == "Int32"
    assert constants["red"].semantic_type.constraints == [SemanticConstraint("Constant")]
    assert constants["red"].semantic_type.metadata["fortran_bind_c"] is True
    assert constants["green"].metadata["fortran_initializer"] == "red + 11"
    emitted = emit_module(module)
    assert "red: Final[Int32] = -1" in emitted
    assert "yellow: Final[Int32] = 11" in emitted
    assert "def get_color() -> Int32: ..." in emitted


def test_derived_type_initializers_and_finalizers_reach_semantic_ir():
    source = """
module lifecycle_mod
  type :: state
    integer :: count = 7
  contains
    final :: cleanup
  end type state
contains
  subroutine cleanup(self)
    type(state), intent(inout) :: self
  end subroutine cleanup
end module lifecycle_mod
"""

    parsed = parse_fortran_source(source)
    module = fortran_module_to_semantic_module(parsed)
    state = module.classes[0]

    assert state.fields[0].default_value == "7"
    assert state.fields[0].metadata["fortran_initializer"] == "7"
    assert state.metadata["fortran_final_procedures"] == ["cleanup"]
    emitted = emit_module(module)
    assert "@native_type(finalizers=('cleanup',))" in emitted
    assert native_contract_issues(parse_pyi_text(emitted, module_name=module.name)) == []


def test_bind_c_and_sequence_types_preserve_accessor_layout_metadata():
    source = """
module layout_mod
  use iso_c_binding
  type, bind(C) :: point
    real(c_double) :: x
    integer(c_int) :: axis
  end type point
  type, bind(C) :: tagged_point
    type(point) :: position
    logical(c_bool) :: active
    complex(c_double_complex) :: weight
  end type tagged_point
  type :: ordered_pair
    sequence
    integer :: first
    integer :: second
  end type ordered_pair
end module layout_mod
"""

    module = fortran_module_to_semantic_module(parse_fortran_source(source))
    point, tagged, ordered = module.classes

    assert point.metadata["fortran_type_attributes"] == ["bind(c)"]
    assert "@native_type(attributes=('bind(c)',))" in emit_module(module)
    assert point.metadata["fortran_bind_c"] is True
    assert point.metadata["fortran_layout_policy"] == "accessors"
    assert point.metadata["fortran_direct_layout"] is False
    assert point.metadata["fortran_component_order"] == ["x", "axis"]
    assert point.metadata["fortran_component_facts"] == [
        {
            "name": "x",
            "source_type": "real(kind=c_double)",
            "kind": "c_double",
            "rank": 0,
            "shape": [],
            "allocatable": False,
            "pointer": False,
            "target": False,
        },
        {
            "name": "axis",
            "source_type": "integer(kind=c_int)",
            "kind": "c_int",
            "rank": 0,
            "shape": [],
            "allocatable": False,
            "pointer": False,
            "target": False,
        },
    ]
    assert [field.name for field in tagged.fields] == ["position", "active", "weight"]
    assert tagged.fields[0].origin.source_type == "type(point)"
    assert tagged.fields[1].origin.source_type == "logical(kind=c_bool)"
    assert tagged.fields[2].origin.source_type == "complex(kind=c_double_complex)"
    assert ordered.metadata["fortran_type_attributes"] == ["sequence"]
    assert "@native_type(attributes=('sequence',))" in emit_module(module)
    assert ordered.metadata["fortran_sequence"] is True
    assert ordered.metadata["fortran_layout_policy"] == "accessors"


def test_bind_c_derived_value_argument_is_accessor_routed():
    interoperable_source = """
module bind_c_value_mod
  use iso_c_binding
  type, bind(C) :: point
    real(c_double) :: x
  end type point
contains
  subroutine consume(value) bind(C)
    type(point), value :: value
  end subroutine consume
end module bind_c_value_mod
"""
    interoperable = fortran_module_to_semantic_module(parse_fortran_source(interoperable_source))
    assert interoperable.classes[0].name == "point"


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
        ("real", "real32", "Float32"),
        ("real", "real64", "Float64"),
        ("real", "c_float", "Float32"),
        ("real", "c_double", "Float64"),
        ("real", "kind(1.0e0)", "Float32"),
        ("real", "kind(1.0d0)", "Float64"),
        ("complex", None, "Complex64"),
        ("complex", "4", "Complex64"),
        ("complex", "8", "Complex128"),
        ("complex", "real32", "Complex64"),
        ("complex", "real64", "Complex128"),
        ("complex", "c_float_complex", "Complex64"),
        ("complex", "c_double_complex", "Complex128"),
        ("logical", None, "Bool"),
        ("logical", "c_bool", "Bool"),
        ("character", None, "String"),
        ("character", "1", "String"),
        ("character", "c_char", "String"),
        ("character", "len=12, kind=c_char", "String"),
        ("procedure", "f_iface", "Procedure"),
    ]

    for base_type, kind, expected in cases:
        variable = FortranVariable(name=f"{base_type}_{kind or 'default'}", base_type=base_type, kind=kind)
        assert converter.visit(variable, as_type=True).name == expected


@pytest.mark.parametrize(
    ("base_type", "kind", "message"),
    [
        ("real", "16", "real(kind=16)"),
        ("real", "real128", "real(kind=real128)"),
        ("real", "kind(1.0q0)", "real(kind=16)"),
        ("complex", "16", "complex(kind=16)"),
        ("complex", "real128", "complex(kind=real128)"),
        ("logical", "8", "logical(kind=8)"),
    ],
)
def test_intrinsic_builtin_kinds_reject_unsupported_wrapper_mappings(base_type, kind, message):
    variable = FortranVariable(name="value", base_type=base_type, kind=kind)

    with pytest.raises(ValueError, match=re.escape(message)):
        FortranToIRConverter().visit(variable, as_type=True)


def test_fortran2ir_uses_compiler_probed_storage_facts_and_preserves_provenance():
    fact = {
        "base_type": "real",
        "kind": None,
        "bits": 64,
        "expression": "storage_size(real(0.0))",
    }
    semantic_type = FortranToIRConverter(type_facts={("real", None): fact}).visit(
        FortranVariable(name="value", base_type="real"),
        as_type=True,
    )

    assert semantic_type.name == "Float64"
    assert semantic_type.dtype == "Float64"
    assert semantic_type.metadata["fortran_type_fact"] == fact
    assert semantic_type.metadata["fortran_type_fact_source"] == "compiler_probe"

    logical_fact = {
        "base_type": "logical",
        "kind": "1",
        "bits": 8,
        "expression": "storage_size(logical(.false.,kind=1))",
    }
    logical_type = FortranToIRConverter(type_facts={("logical", "1"): logical_fact}).visit(
        FortranVariable(name="flag", base_type="logical", kind="1")
    )

    assert logical_type.name == "Bool"
    assert logical_type.metadata["fortran_type_fact"] == logical_fact


def test_fortran2ir_rejects_compiler_storage_without_semantic_dtype():
    fact = {
        "base_type": "integer",
        "kind": None,
        "bits": 48,
        "expression": "storage_size(int(0))",
    }

    with pytest.raises(ValueError, match="integer uses 48-bit storage"):
        FortranToIRConverter(type_facts={("integer", None): fact}).visit(
            FortranVariable(name="value", base_type="integer")
        )


@pytest.mark.parametrize(
    "fact",
    [
        {"base_type": "real", "kind": "3", "bits": 24},
        {"base_type": "complex", "kind": "3", "bits": 96},
        {"base_type": "integer", "kind": "6", "bits": 48},
    ],
)
def test_fortran2ir_rejects_compiler_probed_unknown_storage_widths(fact):
    with pytest.raises(ValueError, match="Unsupported Fortran target storage"):
        FortranToIRConverter(type_facts={(fact["base_type"], fact["kind"]): fact}).visit(
            FortranVariable(name="value", base_type=fact["base_type"], kind=fact["kind"])
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

    assert converter.visit(args["c8"], as_type=True).name == "Complex64"
    assert converter.visit(args["c16"], as_type=True).name == "Complex128"
    assert converter.visit(args["c16"], as_type=True).metadata["fortran_type_fact_source"] == "legacy_star_storage"

    requirements = collect_fortran_type_storage_requirements(parsed)
    assert {(item["base_type"], item["kind"], item["expression"]) for item in requirements} == {
        ("real", "kind(1.0d0)", "storage_size(real(0.0,kind=kind(1.0d0)))"),
        ("complex", "kind(1.0d0)", "storage_size(cmplx(0.0,kind=kind(1.0d0)))"),
        ("character", None, "storage_size(char(65))"),
        ("character", "1", "storage_size(char(65,kind=1))"),
    }


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

    assert a.semantic_type.name == "Float64"
    assert a.semantic_type.rank == 0

    assert c.semantic_type.ownership.mutable is True


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
subroutine contracts(n, m, explicit, legacy, assumed, contig, alloc, ptr, scalar_ptr, scalar_value, scalar_ref, scalar_out)
  integer, intent(in) :: n
  integer, intent(in) :: m
  real(8), intent(in) :: explicit(n, m)
  real(8), intent(inout) :: legacy(n, *)
  real(8), intent(in) :: assumed(:, :)
  real(8), contiguous, intent(inout) :: contig(:, :)
  real(8), allocatable, intent(out) :: alloc(:)
  real(8), pointer, intent(inout) :: ptr(:)
  real(8), pointer, intent(in) :: scalar_ptr
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
    scalar_ptr = args["scalar_ptr"].semantic_type
    assert scalar_ptr.metadata["fortran_pointer"] is True
    assert scalar_ptr.metadata["fortran_pointer_association"] == "runtime"
    assert scalar_ptr.storage.pointer_depth == 1
    assert args["scalar_ptr"].origin.metadata == {
        "rank": 0,
        "shape": [],
        "lower_bounds": [],
        "upper_bounds": [],
        "allocatable": False,
        "pointer": True,
        "target": False,
        "contiguous": False,
        "optional": False,
        "value": False,
        "association": "runtime",
    }
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

    matrix_type = converter.visit(matrix).semantic_type
    assumed_rank = converter.visit(FortranVariable(name="any_rank", base_type="real", rank=1, shape=[".."]))
    semantic_member = converter.visit(member, as_data_member=True)
    plain_member = converter.visit(
        FortranVariable(name="plain", base_type="real", rank=1, shape=[":"]),
        as_data_member=True,
    )
    mixed_bounds = converter.visit(FortranVariable(name="mixed", base_type="real", rank=3, shape=["3", "1:n", "0:n"]))

    assert asdict(matrix_type.storage) == {
        "kind": "array",
        "read_only": False,
        "mutable": True,
        "pointer_depth": 0,
        "ownership": "borrowed",
        "array": {
            "rank": 2,
            "shape": ["4", ":"],
            "lower_bounds": ["0", None],
            "upper_bounds": ["4 - 1", "*"],
            "source_shape": ["0:4 - 1", "*"],
            "category": "assumed_size",
            "order": "ORDER_F",
            "copy_order": None,
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
        "copy_order": None,
        "axes": ["dense"],
        "contiguous": None,
        "allocatable": False,
        "pointer": False,
        "metadata": {},
    }
    assert semantic_member.name == "items"
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


def test_explicit_bound_ranges_remain_shaped_storage_contracts():
    source = """
module bound_mod
contains
subroutine bounded(n, default_bound, zero_bound, shifted_bound)
  integer, intent(in) :: n
  real(8), intent(inout) :: default_bound(1:n)
  real(8), intent(inout) :: zero_bound(0:n-1)
  real(8), intent(inout) :: shifted_bound(2:n+1)
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
    assert zero_bound.shape == ["n"]

    shifted_bound = array_contract(args["shifted_bound"].semantic_type)
    assert shifted_bound.category == "explicit_shape"
    assert shifted_bound.shape == ["n"]


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
    assert func.projection == [
        ProjectionMapping(
            python_name="x",
            native_name="x",
            native_position=0,
            python_position=None,
            result_position=0,
        )
    ]


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


def test_class_declarations_preserve_polymorphic_source_fact():
    source = """
module polymorphic_source_mod
  type :: base
  contains
    procedure :: touch
  end type base
contains
  subroutine touch(self)
    class(base), intent(inout) :: self
  end subroutine touch
  subroutine accept(value)
    class(base), intent(in) :: value
  end subroutine accept
end module polymorphic_source_mod
"""

    module = FortranToIRConverter().visit(parse_fortran_source(source).modules[0])
    touch_self = module.functions[0].arguments[0].semantic_type
    accept_value = module.functions[1].arguments[0].semantic_type

    assert touch_self.origin.source_type == "class(base)"
    assert touch_self.metadata["fortran_polymorphic"] is True
    assert module.functions[0].metadata["fortran_type_bound_target"] is True
    assert module.functions[0].metadata["fortran_passed_object_name"] == "self"
    assert accept_value.origin.source_type == "class(base)"
    assert accept_value.metadata["fortran_polymorphic"] is True


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
