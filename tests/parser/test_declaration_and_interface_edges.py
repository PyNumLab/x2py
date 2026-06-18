"""Declaration parsing, interfaces, and less common scope edges."""

import pytest

from x2py.fortran_parser.models import FortranModule
from x2py.fortran_parser.parser import FortranParser, _ParserScope
from x2py import FortranParseError, parse_fortran_file, parse_fortran_project


def test_legacy_star_kind_and_declarations_without_double_colon_are_resolved():
    code = """
      subroutine legacy_decl(x, z, p, c, f)
      real*8 x
      complex*16 z
      type(point) p
      class(point) c
      procedure(cb) f
      end
"""

    sig = parse_fortran_file(code, filename="legacy_decl.f").procedures[0]
    args = {arg.name: arg for arg in sig.arguments}

    assert args["x"].base_type == "real"
    assert args["x"].kind == "8"
    assert args["z"].base_type == "complex"
    assert args["z"].kind == "16"
    assert args["p"].base_type == "derived"
    assert args["p"].kind == "point"
    assert args["c"].base_type == "derived"
    assert args["c"].kind == "point"
    assert args["f"].base_type == "procedure"
    assert args["f"].kind == "cb"


def test_bind_c_and_dummy_argument_attributes_from_inline_fortran():
    code = """
subroutine c_step(n, x, y, work, cb) bind(c, name="c_step")
  integer, value, intent(in) :: n
  real, optional, intent(inout) :: x(:)
  real, pointer, intent(out) :: y(:)
  real, allocatable, intent(inout) :: work(:)
  real, external :: cb
end subroutine c_step
"""

    sig = parse_fortran_file(code).procedures[0]
    args = {arg.name: arg for arg in sig.arguments}

    assert "bind(c)" in sig.attributes
    assert args["n"].pass_by_value is True
    assert args["x"].optional is True
    assert args["y"].pointer is True
    assert args["work"].allocatable is True
    assert args["cb"].base_type == "real"


def test_character_entity_lengths_and_assumed_bounds_are_preserved():
    code = """
      subroutine label(name, table)
      character name*6
      real table(0:)
      end
"""

    sig = parse_fortran_file(code, filename="label.f").procedures[0]
    args = {arg.name: arg for arg in sig.arguments}

    assert args["name"].base_type == "character"
    assert args["name"].kind == "6"
    assert args["name"].character_length_syntax is True
    assert args["table"].shape == ["0:"]
    assert args["table"].lbound == ["0"]
    assert args["table"].ubound == [None]


def test_project_duplicate_registries_raise_for_public_scopes():
    with pytest.raises(FortranParseError, match="Duplicate symbol 'work' in project procedure scope"):
        parse_fortran_project(
            {
                "a.f90": """
subroutine work()
end subroutine work
""",
                "b.f90": """
subroutine work()
end subroutine work
""",
            }
        )

    with pytest.raises(FortranParseError, match="Duplicate symbol 'driver' in project program scope"):
        parse_fortran_project(
            {
                "a.f90": """
program driver
end program driver
""",
                "b.f90": """
program driver
end program driver
""",
            }
        )


def test_module_scope_ignores_non_variable_spec_lines():
    code = """
module spec_mod
  public ::
  private ::
  import :: external_symbol
  implicit none
  save
  integer :: kept
contains
  subroutine worker()
  end subroutine worker
end module spec_mod
"""

    module = parse_fortran_file(code).modules[0]

    assert module.default_visibility == "private"
    assert [var.name for var in module.variables] == ["kept"]


def test_module_declarations_without_double_colon_are_parsed_not_dropped():
    code = """
module legacy_module_decls
  integer kept
  real values(2)
end module legacy_module_decls
"""

    module = parse_fortran_file(code).modules[0]
    variables = {var.name: var for var in module.variables}

    assert variables["kept"].base_type == "integer"
    assert variables["values"].base_type == "real"
    assert variables["values"].shape == ["2"]


def test_use_rename_and_intrinsic_forms_are_recorded():
    code = """
module use_forms
  use list_input, delete_input => delete_input_list
  use, intrinsic :: iso_c_binding, only: c_int, c_double
end module use_forms
"""

    module = parse_fortran_file(code).modules[0]

    assert module.uses["list_input"] == ["delete_input"]
    assert module.uses["list_input"][0].source == "delete_input_list"
    assert module.uses["list_input"][0].target == "delete_input"
    assert module.uses["iso_c_binding"] == ["c_int", "c_double"]
    assert [(item.source, item.target) for item in module.uses["iso_c_binding"]] == [
        ("c_int", None),
        ("c_double", None),
    ]


def test_unknown_no_colon_declarations_raise_in_metadata_scopes():
    module_code = """
module bad_mod
  weirdtype value
end module bad_mod
"""
    type_code = """
module bad_type_mod
  type :: bad_type
    weirdtype value
  end type bad_type
end module bad_type_mod
"""

    with pytest.raises(FortranParseError, match="Unknown or unsupported datatype declaration in module"):
        parse_fortran_file(module_code, filename="bad_mod.f90")
    with pytest.raises(FortranParseError, match="Unknown or unsupported datatype declaration in type"):
        parse_fortran_file(type_code, filename="bad_type.f90")


def test_declaration_and_execution_edge_branches_from_inline_fortran():
    code = """
subroutine declaration_edges(i, x, y)
  integer ( kind = 4 ) i
  double precision y
  real x
  go to 10
10 continue
end subroutine declaration_edges
"""

    sig = parse_fortran_file(code, filename="declaration_edges.f90").procedures[0]
    args = {arg.name: arg for arg in sig.arguments}

    assert args["i"].base_type == "integer"
    assert args["i"].kind == "4"
    assert args["x"].base_type == "real"
    assert args["y"].base_type == "real"
    assert args["y"].target_kind_expression == "kind(1.0d0)"


def test_nested_interface_dummy_procedure_and_generic_module_procedure_interface():
    code = """
module callback_mod
  interface apply
    module procedure apply_impl
  end interface apply
contains
  subroutine caller(cb)
    interface
      subroutine cb(x)
        integer, intent(in) :: x
      end subroutine cb
    end interface
  end subroutine caller

  subroutine apply_impl(x)
    integer, intent(in) :: x
  end subroutine apply_impl
end module callback_mod
"""

    parsed = parse_fortran_file(code)
    procedures = {proc.name: proc for proc in parsed.modules[0].procedures}

    assert procedures["caller"].arguments[0].base_type == "procedure"
    assert parsed.modules[0].interfaces[0].name == "apply"


def test_cross_file_kind_resolution_for_arguments_results_and_local_parameters():
    project = parse_fortran_project(
        {
            "kinds.f90": """
module kinds_mod
  integer, parameter :: base = 4
  integer, parameter :: offset = base
  integer, parameter :: rk = base + offset
end module kinds_mod
""",
            "solver.f90": """
module solver_mod
  use kinds_mod
contains
  function make_value() result(value)
    real(kind=rk) :: value
  end function make_value

  subroutine use_local(x)
    integer, parameter :: n = 4
    real, intent(inout) :: x(1:n)
  end subroutine use_local
end module solver_mod
""",
        }
    )

    result_proc = project.procedures["solver_mod.make_value"]
    local_proc = project.procedures["solver_mod.use_local"]

    assert result_proc.result.kind == "8"
    assert local_proc.arguments[0].shape == ["1:4"]


def test_local_kind_parameter_chain_resolves_to_final_integer_kind():
    parsed = parse_fortran_file(
        """
subroutine consume(x, y)
  integer, parameter :: word = 4
  integer, parameter :: twice = 2
  integer, parameter :: rk = word * twice
  integer, parameter :: ck = rk * twice
  real(kind=rk), intent(in) :: x
  complex(kind=ck), intent(out) :: y
end subroutine consume
""",
        filename="local_kind_chain.f90",
    )
    args = {arg.name: arg for arg in parsed.procedures[0].arguments}

    assert args["x"].kind == "8"
    assert args["y"].kind == "16"


def test_local_compile_time_arithmetic_is_folded_for_shapes_and_parameters():
    code = """
subroutine arithmetic_shapes(a, b, c, d, e, f)
  integer, parameter :: n = 8
  integer, parameter :: m = 3
  integer, parameter :: one = 1.0d+0
  real, intent(inout) :: a(1:n-m)
  real, intent(inout) :: b(1:n*m)
  real, intent(inout) :: c(1:n/m)
  real, intent(inout) :: d(1:m**2)
  real, intent(inout) :: e(1:+n-one)
  real, intent(inout) :: f(1:+n)
end subroutine arithmetic_shapes
"""

    sig = parse_fortran_file(code).procedures[0]

    assert [arg.shape[0] for arg in sig.arguments] == [
        "1:5",
        "1:24",
        "1:(8)/(3)",
        "1:9",
        "1:+(8)-one",
        "1:8",
    ]
    assert sig.variables["one"].value == "1"


def test_type_contains_accepts_bindings_and_rejects_other_lines():
    valid_code = """
module type_contains_valid_mod
  type :: state
  contains
    procedure :: update
    final :: destroy
  end type state
end module type_contains_valid_mod
"""

    parsed = parse_fortran_file(valid_code, filename="type_contains_valid.f90")
    dtype = parsed.modules[0].derived_types[0]
    assert dtype.methods == ["update"]
    assert dtype.final_procedures == ["destroy"]

    for invalid_line in ("call ignored_statement()", "!$omp declare target", "integer, public :: bad_binding"):
        code = f"""
module type_contains_bad_mod
  type :: state
  contains
    {invalid_line}
  end type state
end module type_contains_bad_mod
"""
        with pytest.raises(FortranParseError, match="Unsupported or malformed type-bound declaration"):
            parse_fortran_file(code, filename="type_contains_bad.f90")


def test_derived_type_field_default_initializers_are_preserved():
    code = """
module init_mod
  type :: state
    integer :: count = 7
    logical :: enabled = .true.
  end type state
end module init_mod
"""

    dtype = parse_fortran_file(code).modules[0].derived_types[0]
    fields = {field.name: field for field in dtype.fields}

    assert fields["count"].value == "7"
    assert fields["count"].symbolic_value == "7"
    assert fields["enabled"].value == "1"
    assert fields["enabled"].symbolic_value == ".true."


def test_contains_alternative_line_validation_accepts_spec_lines_without_mutating_scope():
    parser = FortranParser()
    module = FortranModule("alternative_mod")
    scope = _ParserScope(kind="module", name=module.name, model=module, module_owner=module.name)

    assert parser._helper_is_valid_contains_alternative_line(scope, "integer :: fallback") is True
    assert parser._helper_is_valid_contains_alternative_line(scope, "call fallback()") is False
    assert parser._helper_is_valid_contains_alternative_line(scope, "@@@") is False
    assert module.variables == []


def test_valid_enum_subunit_accepts_optional_separator_and_multiple_enumerators():
    parsed = parse_fortran_file(
        """
module enum_valid_mod
  enum, bind(c)
    enumerator first
    enumerator :: second = 2, third = selected_int_kind(4)
  end enum
end module enum_valid_mod
""",
        filename="valid_enum.f90",
    )

    assert parsed.modules[0].name == "enum_valid_mod"


@pytest.mark.parametrize(
    "invalid_line",
    [
        "enumerator :: valid = 1, 2invalid",
        "integer :: invalid",
        "interface invalid",
    ],
)
def test_enum_subunit_rejects_malformed_lines_and_nested_units(invalid_line):
    code = f"""
module enum_invalid_mod
  enum, bind(c)
    {invalid_line}
  end enum
end module enum_invalid_mod
"""

    with pytest.raises(FortranParseError, match="Invalid Fortran syntax"):
        parse_fortran_file(code, filename="invalid_enum.f90")


def test_malformed_type_bound_declaration_raises():
    code = """
module bad_binding_mod
  type :: t
  contains
    procedure broken_binding
  end type t
end module bad_binding_mod
"""

    with pytest.raises(FortranParseError, match="Unsupported or malformed type-bound declaration"):
        parse_fortran_file(code, filename="bad_binding.f90")


def test_use_statement_empty_only_items_are_ignored():
    code = """
module use_empty_items_mod
  use constants_mod, only: rk, , ik
  integer :: value
end module use_empty_items_mod
"""

    module = parse_fortran_file(code, filename="use_empty_items.f90").modules[0]

    assert [item.local_name for item in module.uses["constants_mod"]] == ["rk", "ik"]


def test_type_field_spec_variants_and_empty_entities_from_public_source():
    code = """
module type_field_edges_mod
  type :: state
    sequence
    private
    integer :: first, , second
  end type state
end module type_field_edges_mod
"""

    dtype = parse_fortran_file(code, filename="type_field_edges.f90").modules[0].derived_types[0]

    assert [field.name for field in dtype.fields] == ["first", "second"]
    assert dtype.attributes == ["sequence"]


def test_bind_c_derived_type_attribute_and_component_order_are_preserved():
    code = """
module bind_c_type_mod
  use iso_c_binding
  type, bind(C) :: sample
    real(c_double) :: x
    integer(c_int) :: tag
    logical(c_bool) :: active
  end type sample
end module bind_c_type_mod
"""

    dtype = parse_fortran_file(code, filename="bind_c_type.f90").modules[0].derived_types[0]

    assert dtype.attributes == ["bind(c)"]
    assert [field.name for field in dtype.fields] == ["x", "tag", "active"]


@pytest.mark.parametrize("invalid_line", ["type :: nested_marker", "call invalid_in_type_spec()"])
def test_type_field_specification_rejects_invalid_nested_syntax(invalid_line):
    code = f"""
module type_field_invalid_mod
  type :: state
    {invalid_line}
  end type state
end module type_field_invalid_mod
"""

    with pytest.raises(FortranParseError):
        parse_fortran_file(code, filename="type_field_invalid.f90")


def test_module_like_declaration_edges_from_program_and_module_sources():
    module_code = """
module module_spec_edges_mod
  module procedure :: ignored_impl
  integer :: first, , second
end module module_spec_edges_mod
"""

    program_code = """
program type_stmt_program
  type :: local_state
    integer :: marker
  end type local_state
  integer :: kept
end program type_stmt_program
"""

    module = FortranParser().visit_fortran_module(
        module_code,
        filename="module_like_edges.f90",
    )
    program = parse_fortran_file(program_code, filename="module_like_edges.f90").programs[0]

    assert [var.name for var in module.variables] == ["first", "second"]
    assert [var.name for var in program.variables] == ["kept"]


def test_public_parse_paths_ignore_empty_declaration_entities():
    parsed = parse_fortran_file(
        """
module empty_entity_mod
  integer :: kept, , also_kept

  type :: state
    real :: x, , y
  end type state
end module empty_entity_mod
""",
        filename="empty_entities.f90",
    )

    module = parsed.modules[0]

    assert [var.name for var in module.variables] == ["kept", "also_kept"]
    assert [field.name for field in module.derived_types[0].fields] == ["x", "y"]


def test_nested_interface_procedure_without_matching_dummy_stays_publicly_parseable():
    sig = parse_fortran_file(
        """
subroutine caller()
  interface
    subroutine helper(x)
      integer, intent(in) :: x
    end subroutine helper
  end interface
end subroutine caller
"""
    ).procedures[0]

    assert sig.name == "caller"
    assert sig.arguments == []
