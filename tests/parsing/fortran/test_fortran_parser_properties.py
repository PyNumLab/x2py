"""Tests split by stable ownership concept from `test_properties.py`."""

from tests._shared.parser_property_support import (
    FortranParseError,
    _FORTRAN_IDENTIFIER_STEMS,
    _FORTRAN_SCALAR_TYPES,
    _FUZZ_TEXT,
    emit_module_stubs,
    fortran_file_to_semantic_modules,
    fortran_subroutines,
    given,
    parse_fortran_file,
    parse_pyi_text,
    pytest,
    st,
    suppress,
)


@pytest.mark.property
@given(fortran_subroutines())
def test_generated_fortran_subroutines_preserve_argument_order(case):
    proc_name, arg_names, source = case

    parsed = parse_fortran_file(source, filename=f"{proc_name}.f90")

    assert parsed.diagnostics == []
    assert len(parsed.procedures) == 1
    procedure = parsed.procedures[0]
    assert procedure.name == proc_name
    assert [arg.name for arg in procedure.arguments] == arg_names


@pytest.mark.property
@given(fortran_subroutines())
def test_generated_fortran_subroutines_survive_case_changes(case):
    proc_name, arg_names, source = case

    parsed = parse_fortran_file(source.upper(), filename=f"{proc_name}.f90")

    assert parsed.diagnostics == []
    assert len(parsed.procedures) == 1
    procedure = parsed.procedures[0]
    assert procedure.name.lower() == proc_name
    assert [arg.name.lower() for arg in procedure.arguments] == arg_names


@pytest.mark.property
@given(fortran_subroutines())
def test_generated_fortran_subroutines_round_trip_through_pyi(case):
    proc_name, arg_names, source = case

    parsed = parse_fortran_file(source, filename=f"{proc_name}.f90")
    modules = fortran_file_to_semantic_modules(parsed, standalone_module_name="generated")
    stub = emit_module_stubs(modules)["generated"]
    reparsed = parse_pyi_text(stub, module_name="generated")

    assert len(reparsed.functions) == 1
    procedure = reparsed.functions[0]
    assert procedure.name == proc_name
    assert [arg.name for arg in procedure.arguments] == arg_names


@pytest.mark.property
@given(
    module_stem=_FORTRAN_IDENTIFIER_STEMS, procedure_stem=_FORTRAN_IDENTIFIER_STEMS, scalar_type=_FORTRAN_SCALAR_TYPES
)
def test_generated_fortran_modules_preserve_owned_declarations(module_stem, procedure_stem, scalar_type):
    module_name = f"mod_{module_stem}"
    procedure_name = f"proc_{procedure_stem}"
    source = (
        f"module {module_name}\n"
        f"  {scalar_type} :: state\n"
        "contains\n"
        f"  subroutine {procedure_name}(value)\n"
        f"    {scalar_type}, intent(in) :: value\n"
        f"  end subroutine {procedure_name}\n"
        f"end module {module_name}\n"
    )

    parsed = parse_fortran_file(source, filename=f"{module_name}.f90")

    assert parsed.diagnostics == []
    assert len(parsed.modules) == 1
    module = parsed.modules[0]
    assert module.name == module_name
    assert [(variable.name, variable.base_type) for variable in module.variables] == [("state", scalar_type)]
    assert [(procedure.name, procedure.module) for procedure in module.procedures] == [(procedure_name, module_name)]
    assert [(argument.name, argument.base_type) for argument in module.procedures[0].arguments] == [
        ("value", scalar_type)
    ]


@pytest.mark.property
@given(
    module_stem=_FORTRAN_IDENTIFIER_STEMS,
    type_stem=_FORTRAN_IDENTIFIER_STEMS,
    field_types=st.lists(_FORTRAN_SCALAR_TYPES, min_size=1, max_size=5),
)
def test_generated_fortran_derived_types_preserve_fields(module_stem, type_stem, field_types):
    module_name = f"mod_{module_stem}"
    type_name = f"type_{type_stem}"
    fields = [f"field_{index}" for index in range(len(field_types))]
    field_lines = "".join(
        f"    {field_type} :: {field_name}\n" for field_name, field_type in zip(fields, field_types, strict=True)
    )
    source = (
        f"module {module_name}\n  type :: {type_name}\n{field_lines}  end type {type_name}\nend module {module_name}\n"
    )

    parsed = parse_fortran_file(source, filename=f"{module_name}.f90")

    assert parsed.diagnostics == []
    assert len(parsed.modules) == 1
    assert len(parsed.modules[0].derived_types) == 1
    derived_type = parsed.modules[0].derived_types[0]
    assert derived_type.name == type_name
    assert derived_type.module == module_name
    assert [(field.name, field.base_type) for field in derived_type.fields] == list(
        zip(fields, field_types, strict=True)
    )


@pytest.mark.property
@given(base_type=_FORTRAN_SCALAR_TYPES, kind=st.integers(min_value=1, max_value=32), keyword=st.booleans())
def test_generated_fortran_intrinsic_kinds_are_preserved(base_type, kind, keyword):
    type_spec = f"{base_type}({'kind=' if keyword else ''}{kind})"
    source = f"subroutine generated_kind(value)\n  {type_spec}, intent(in) :: value\nend subroutine generated_kind\n"

    parsed = parse_fortran_file(source, filename="generated_kind.f90")

    assert parsed.diagnostics == []
    assert len(parsed.procedures) == 1
    assert parsed.procedures[0].arguments[0].base_type == base_type
    assert parsed.procedures[0].arguments[0].kind == str(kind)


@pytest.mark.fuzz
@given(_FUZZ_TEXT)
def test_fortran_parser_fuzz_fragments_only_raise_owned_errors(source):
    with suppress(FortranParseError):
        parse_fortran_file(source, filename="fuzz.f90")
