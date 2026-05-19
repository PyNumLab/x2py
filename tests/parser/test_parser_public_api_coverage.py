# -*- coding: utf-8 -*-
import pytest

from fortran_parser.parser import FortranParser, collect_signature_shape_symbols, evaluate_signature_shapes
from x2py import FortranParseError, assess_wrap_readiness, parse_fortran_file, parse_fortran_project


def test_parser_public_entrypoint_aliases_and_singular_contracts_use_inline_sources():
    parser = FortranParser()
    module_code = """
module alias_mod
contains
  subroutine ping(x)
    integer, intent(in) :: x
  end subroutine ping
end module alias_mod
"""

    assert parser.visit_file(module_code).modules[0].name == "alias_mod"
    assert parser.visit_file(module_code).modules[0].procedures[0].name == "ping"
    assert "alias_mod" in parser.visit_project({"alias.f90": module_code}).modules
    assert "alias_mod.ping" in parser.visit_project({"alias.f90": module_code}).procedures
    assert parser.visit_wrap_readiness(module_code)["wrappable"] is True

    assert parser.visit_fortran_module("module single_mod\nend module single_mod\n").name == "single_mod"
    assert parser.visit_fortran_program("program driver\nend program driver\n").name == "driver"
    assert parser.visit_fortran_derived_type("type :: state_t\nend type state_t\n").name == "state_t"
    assert parser.visit_fortran_interface(
        """
interface callback
  subroutine cb()
  end subroutine cb
end interface callback
"""
    ).name == "callback"
    assert parser.visit_fortran_submodule(
        "submodule (parent_mod) child_mod\nend submodule child_mod\n"
    ).name == "child_mod"
    assert parser.visit_fortran_block_data_unit(
        "block data init_data\n  integer seed\nend block data init_data\n"
    ).name == "init_data"

    with pytest.raises(FortranParseError, match="none were found"):
        parser.visit_fortran_module("program not_a_module\nend program not_a_module\n")

    with pytest.raises(FortranParseError, match="found 2"):
        parser.visit_fortran_module(
            """
module first_mod
end module first_mod
module second_mod
end module second_mod
"""
        )


def test_typed_function_result_headers_are_parsed_from_inline_fortran():
    code = """
module typed_result_mod
  type :: point
    real :: x
  end type point
contains
  type(point) function make_point()
  end function make_point

  class(point), pointer function current_point()
  end function current_point

  character(len=8) function label_name()
  end function label_name

  real(8) function weighted_value()
  end function weighted_value

  double precision function norm2()
  end function norm2
end module typed_result_mod
"""

    procedures = {proc.name: proc for proc in parse_fortran_file(code).modules[0].procedures}

    assert procedures["make_point"].result.base_type == "derived"
    assert procedures["make_point"].result.kind == "point"
    assert procedures["current_point"].result.base_type == "derived"
    assert procedures["current_point"].result.kind == "point"
    assert procedures["label_name"].result.base_type == "character"
    assert procedures["label_name"].result.kind == "len=8"
    assert procedures["weighted_value"].result.base_type == "real"
    assert procedures["weighted_value"].result.kind == "8"
    assert procedures["norm2"].result.base_type == "real"


def test_legacy_star_kind_function_headers_are_parsed_from_inline_fixed_form():
    code = """
      complex*16 function zdotc(n, zx, zy)
      integer n
      complex*16 zx(n), zy(n)
      zdotc = zx(1) * zy(1)
      end

      character*1 function trans_name(itrans)
      integer itrans
      trans_name = 'N'
      end

      character*(*) function any_name()
      any_name = 'x'
      end
"""

    procedures = {proc.name: proc for proc in parse_fortran_file(code, filename="legacy_funcs.f").procedures}

    assert procedures["zdotc"].result.base_type == "complex"
    assert procedures["zdotc"].result.kind == "16"
    assert procedures["trans_name"].result.base_type == "character"
    assert procedures["trans_name"].result.kind == "1"
    assert procedures["any_name"].result.base_type == "character"
    assert procedures["any_name"].result.kind == "*"


def test_no_argument_headers_without_parentheses_are_parsed():
    code = """
subroutine setup
end subroutine setup

integer function answer
  answer = 42
end function answer
"""

    procedures = {proc.name: proc for proc in parse_fortran_file(code).procedures}

    assert procedures["setup"].kind == "subroutine"
    assert procedures["setup"].arguments == []
    assert procedures["answer"].kind == "function"
    assert procedures["answer"].result.base_type == "integer"


def test_typed_nested_interface_function_marks_dummy_as_procedure():
    code = """
subroutine caller(cb)
  interface
    real function cb(x)
      real, intent(in) :: x
    end function cb
  end interface
end subroutine caller
"""

    sig = parse_fortran_file(code).procedures[0]

    assert sig.arguments[0].base_type == "procedure"


def test_unsupported_procedure_like_header_raises_instead_of_being_dropped():
    code = """
vector function make_value(x)
  integer, intent(in) :: x
end function make_value
"""

    with pytest.raises(FortranParseError, match="Unsupported function result type prefix 'vector'"):
        parse_fortran_file(code, filename="bad_header.f90")


def test_malformed_module_header_raises_instead_of_creating_bad_symbol():
    code = """
module :: bad_mod
end module bad_mod
"""

    with pytest.raises(FortranParseError, match="Unsupported or malformed module header"):
        parse_fortran_file(code, filename="bad_module_header.f90")


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


def test_module_visibility_public_and_private_spec_lines_are_applied():
    code = """
module visibility_mod
  private
  public :: exported
  private :: hidden
  integer :: exported, hidden, inherited
end module visibility_mod

module public_mod
  public
  real :: visible
end module public_mod
"""

    modules = {module.name: module for module in parse_fortran_file(code).modules}
    visibility = {var.name: var.visibility for var in modules["visibility_mod"].variables}

    assert modules["visibility_mod"].default_visibility == "private"
    assert visibility == {
        "exported": "public",
        "hidden": "private",
        "inherited": "private",
    }
    assert modules["public_mod"].variables[0].visibility == "public"


def test_submodule_types_interfaces_and_project_dependencies_attach_to_public_models():
    code = """
submodule (ancestor_mod:parent_mod) child_mod
  type :: child_state
    integer :: id
  end type child_state

  interface callbacks
    subroutine on_step(x)
      integer, intent(in) :: x
    end subroutine on_step
  end interface callbacks
contains
  module procedure reset
  end procedure reset
end submodule child_mod
"""

    parsed = parse_fortran_file(code)
    submodule = parsed.submodules[0]

    assert submodule.parent == "parent_mod"
    assert submodule.ancestor == "ancestor_mod"
    assert [dtype.name for dtype in submodule.derived_types] == ["child_state"]
    assert [iface.name for iface in submodule.interfaces] == ["callbacks"]
    assert [proc.name for proc in submodule.procedures] == ["reset"]

    project = parse_fortran_project({"child.f90": code})
    assert project.dependencies["child_mod"] == {"ancestor_mod", "parent_mod"}
    assert "child_mod.reset" in project.procedures


def test_project_registry_includes_module_types_interfaces_and_program_dependencies():
    project = parse_fortran_project(
        {
            "api.f90": """
module api_mod
  type :: state_t
    integer :: id
  end type state_t

  interface apply
    subroutine apply_i(x)
      integer, intent(in) :: x
    end subroutine apply_i
  end interface apply
contains
  subroutine step(state)
    type(state_t), intent(inout) :: state
  end subroutine step
end module api_mod
""",
            "driver.f90": """
program driver
  use api_mod
  integer :: ierr
end program driver
""",
        }
    )

    assert "api_mod.state_t" in project.derived_types
    assert "state_t" in project.derived_types
    assert "api_mod.apply" in project.interfaces
    assert "apply" in project.interfaces
    assert project.dependencies["driver"] == {"api_mod"}


def test_duplicate_project_scope_names_raise_public_parse_errors():
    with pytest.raises(FortranParseError, match="Duplicate symbol 'dup_mod' in project module scope"):
        parse_fortran_project(
            {
                "a.f90": "module dup_mod\nend module dup_mod\n",
                "b.f90": "module dup_mod\nend module dup_mod\n",
            }
        )


def test_wrap_readiness_reports_unresolved_function_result_type_and_kind():
    code = """
function make_state() result(state)
  use state_mod, only: sim_state
  type(sim_state) :: state
end function make_state

function make_value() result(value)
  use kinds_mod, only: rk
  real(kind=rk) :: value
end function make_value
"""

    report = assess_wrap_readiness(code)

    assert report["wrappable"] is False
    assert report["unresolved_derived_type_arguments"] == [
        {
            "procedure": "make_state",
            "module": None,
            "argument": "state",
            "type": "sim_state",
            "import_modules": ["state_mod"],
        }
    ]
    assert report["unresolved_kind_arguments"] == [
        {
            "procedure": "make_value",
            "module": None,
            "argument": "value",
            "kind": "rk",
            "import_modules": ["kinds_mod"],
        }
    ]


def test_wrap_readiness_accepts_module_and_use_associated_kind_parameters():
    code = """
module kinds_mod
  integer, parameter :: rk = selected_real_kind(12)
end module kinds_mod

module solver_mod
  use kinds_mod
  integer, parameter :: ik = selected_int_kind(9)
contains
  subroutine scale(x, i)
    real(kind=rk), intent(inout) :: x
    integer(kind=ik), intent(out) :: i
  end subroutine scale
end module solver_mod
"""

    report = assess_wrap_readiness(code)

    assert report["wrappable"] is True
    assert report["unresolved_kind_arguments"] == []


def test_wrap_readiness_requires_intrinsic_kind_symbols_to_be_imported():
    missing_import = """
subroutine scale(x)
  real(kind=c_double), intent(inout) :: x
end subroutine scale
"""
    report = assess_wrap_readiness(missing_import)

    assert report["wrappable"] is False
    assert report["unresolved_kind_arguments"] == [
        {
            "procedure": "scale",
            "module": None,
            "argument": "x",
            "kind": "c_double",
            "import_modules": [],
        }
    ]

    imported = """
subroutine scale(x, y)
  use, intrinsic :: iso_c_binding, only: c_double, cd => c_float
  real(kind=c_double), intent(inout) :: x
  real(kind=cd), intent(inout) :: y
end subroutine scale
"""
    report = assess_wrap_readiness(imported)

    assert report["wrappable"] is True
    assert report["unresolved_kind_arguments"] == []


def test_wrap_readiness_accepts_arbitrary_imported_kind_symbols_and_expressions():
    code = """
module kinds_mod
  integer, parameter :: wp = selected_real_kind(12)
  integer, parameter :: extra = 1
end module kinds_mod

module solver_mod
contains
  subroutine scale(x, name)
    use kinds_mod, only: local_wp => wp, extra
    real(kind=local_wp + extra), intent(inout) :: x
    character(len=extra, kind=local_wp), intent(out) :: name
  end subroutine scale
end module solver_mod
"""

    report = assess_wrap_readiness(code)

    assert report["wrappable"] is True
    assert report["unresolved_kind_arguments"] == []


def test_wrap_readiness_reports_missing_symbols_inside_kind_expressions():
    code = """
module kinds_mod
  integer, parameter :: wp = selected_real_kind(12)
end module kinds_mod

subroutine scale(x)
  use kinds_mod, only: wp
  real(kind=wp + missing_offset), intent(inout) :: x
end subroutine scale
"""

    report = assess_wrap_readiness(code)

    assert report["wrappable"] is False
    assert report["unresolved_kind_arguments"] == [
        {
            "procedure": "scale",
            "module": None,
            "argument": "x",
            "kind": "missing_offset",
            "import_modules": [],
            "kind_expression": "wp + missing_offset",
        }
    ]


def test_signature_shape_helpers_evaluate_publicly_parsed_signature():
    code = """
subroutine fill(a)
  real, intent(inout) :: a(0:nx-1, 1:ny)
end subroutine fill
"""

    sig = parse_fortran_file(code).procedures[0]

    assert collect_signature_shape_symbols(sig) == {"nx", "ny"}
    evaluated = evaluate_signature_shapes(sig, {"NX": 4, "ny": 3})
    assert evaluated.arguments[0].shape == ["0:3", "1:3"]
    assert sig.arguments[0].shape == ["0:nx-1", "1:ny"]


def test_ifndef_and_defined_without_parentheses_macro_selection():
    code = """
#if defined USE_FAST
subroutine fast_path(x)
  integer, intent(in) :: x
end subroutine fast_path
#else
subroutine slow_path(x)
  real, intent(in) :: x
end subroutine slow_path
#endif

#ifndef USE_SLOW
subroutine default_path(x)
  logical, intent(in) :: x
end subroutine default_path
#else
subroutine selected_slow_path(x)
  real, intent(in) :: x
end subroutine selected_slow_path
#endif
"""

    parsed = parse_fortran_file(code, macro_defines={"USE_FAST": True})

    assert [proc.name for proc in parsed.procedures] == ["fast_path", "default_path"]


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


def test_include_and_ignored_spec_lines_do_not_change_public_signature():
    code = """
subroutine legacy_specs(x)
  include 'params.inc'
  intrinsic abs
  save
  common /blk/ tmp
  data tmp /0.0/
  equivalence (tmp, x)
  format(1x, f8.3)
  real, intent(inout) :: x
  real :: tmp
end subroutine legacy_specs
"""

    sig = parse_fortran_file(code, filename="legacy_specs.f90").procedures[0]

    assert [arg.name for arg in sig.arguments] == ["x"]
    assert sig.arguments[0].base_type == "real"


def test_execution_part_boundaries_and_local_types_are_not_misread_as_declarations():
    code = """
subroutine exec_edges(x)
  real, intent(inout) :: x
  integer :: i
  type scratch_t
    integer :: id
  end type scratch_t
  x = x + 1.0
  go to 10
10 continue
  call noop()
end subroutine exec_edges
"""

    sig = parse_fortran_file(code).procedures[0]

    assert [arg.name for arg in sig.arguments] == ["x"]
    assert sig.arguments[0].base_type == "real"
    assert "i" not in sig.variables


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
    assert args["name"].kind == ""
    assert args["table"].shape == ["0:"]
    assert args["table"].lbound == ["0"]
    assert args["table"].ubound == [None]


def test_file_path_and_unknown_filename_public_parse_paths(tmp_path):
    source_path = tmp_path / "path_input.f90"
    source_path.write_text(
        """
subroutine from_path(i)
  integer, intent(in) :: i
end subroutine from_path
""",
        encoding="utf-8",
    )

    parsed_from_path = parse_fortran_file(source_path)
    parsed_unknown_suffix = parse_fortran_file(
        """
subroutine from_unknown(i)
  integer, intent(in) :: i
end subroutine from_unknown
""",
        filename="from_unknown.src",
    )
    parsed_literal = parse_fortran_file(12345)

    assert parsed_from_path.filename == str(source_path)
    assert parsed_from_path.format == "modern"
    assert parsed_from_path.procedures[0].name == "from_path"
    assert parsed_unknown_suffix.format == "unknown"
    assert parsed_literal.procedures == []


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


def test_program_execution_part_is_ignored_after_first_executable_statement():
    code = """
program driver
  use iso_fortran_env
  integer :: ierr
  write(*,*) "running"
  maybe_decl looking_body_statement
contains
  subroutine inner()
  end subroutine inner
end program driver
"""

    program = parse_fortran_file(code, filename="driver.f90").programs[0]

    assert [var.name for var in program.variables] == ["ierr"]


def test_executable_statement_in_module_spec_part_raises():
    code = """
module bad_exec_mod
  write(*,*) "not allowed"
end module bad_exec_mod
"""

    with pytest.raises(FortranParseError, match="Executable statement is not allowed"):
        parse_fortran_file(code, filename="bad_exec_mod.f90")


def test_openmp_declarative_directives_raise_but_executable_directives_are_body_lines():
    declarative = """
module omp_mod
  integer :: state
!$omp threadprivate(state)
end module omp_mod
"""
    executable = """
subroutine omp_body(x)
  integer, intent(inout) :: x
!$omp parallel do
  do i = 1, x
    x = x + i
  end do
end subroutine omp_body
"""
    proc_declarative = """
subroutine omp_decl(x)
!$omp declare simd
  integer, intent(inout) :: x
end subroutine omp_decl
"""
    type_declarative = """
module omp_type_mod
  type :: state
!$omp declare target
    integer :: value
  end type state
end module omp_type_mod
"""
    module_executable = """
module bad_omp_mod
!$omp parallel
end module bad_omp_mod
"""
    fixed_form_executable = """
      subroutine fixed_omp(n)
      integer n
C$OMP PARALLEL DO
      do 10 i = 1, n
10    continue
      end
"""

    with pytest.raises(FortranParseError, match="Unsupported OpenMP declarative directive"):
        parse_fortran_file(declarative, filename="omp_mod.f90")
    with pytest.raises(FortranParseError, match="Unsupported OpenMP declarative directive"):
        parse_fortran_file(proc_declarative, filename="omp_decl.f90")
    with pytest.raises(FortranParseError, match="Unsupported OpenMP declarative directive"):
        parse_fortran_file(type_declarative, filename="omp_type.f90")
    with pytest.raises(FortranParseError, match="Executable statement is not allowed"):
        parse_fortran_file(module_executable, filename="bad_omp_mod.f90")
    assert parse_fortran_file(executable, filename="omp_body.f90").procedures[0].name == "omp_body"
    assert parse_fortran_file(fixed_form_executable, filename="fixed_omp.f").procedures[0].name == "fixed_omp"


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


def test_cpp_selection_false_and_malformed_expressions_choose_else_branch():
    code = """
#if 0
subroutine false_if_branch()
end subroutine false_if_branch
#else
subroutine false_if_else()
end subroutine false_if_else
#endif

#if defined(USE_A) && (
subroutine malformed_if_branch()
end subroutine malformed_if_branch
#else
subroutine malformed_if_else()
end subroutine malformed_if_else
#endif
"""

    parsed = parse_fortran_file(code, macro_defines=set())

    assert [proc.name for proc in parsed.procedures] == ["false_if_else", "malformed_if_else"]


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


def test_project_directory_namespace_orders_ancestor_submodule_dependencies(tmp_path):
    (tmp_path / "ancestor.f90").write_text(
        """
module ancestor_mod
end module ancestor_mod
""",
        encoding="utf-8",
    )
    (tmp_path / "parent.f90").write_text(
        """
module parent_mod
  use ancestor_mod
end module parent_mod
""",
        encoding="utf-8",
    )
    (tmp_path / "child.f90").write_text(
        """
submodule (ancestor_mod:parent_mod) child_mod
  use helper_mod
contains
  module procedure reset
  end procedure reset
end submodule child_mod
""",
        encoding="utf-8",
    )
    (tmp_path / "helper.f90").write_text(
        """
module helper_mod
end module helper_mod
""",
        encoding="utf-8",
    )

    project = parse_fortran_project(tmp_path)

    assert "ancestor_mod" in project.modules
    assert "parent_mod" in project.modules
    assert "child_mod" in project.submodules
    assert project.dependencies["child_mod"] == {"ancestor_mod", "parent_mod", "helper_mod"}


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


def test_program_contains_and_unnamed_block_data_public_models():
    code = """
program main
  use callback_mod
  integer :: ierr
contains
  subroutine internal()
  end subroutine internal
end program main

block data
  integer seed
end
"""

    parsed = parse_fortran_file(code, filename="units.f90")

    assert parsed.programs[0].uses["callback_mod"] == []
    assert [var.name for var in parsed.programs[0].variables] == ["ierr"]
    assert parsed.block_data_units[0].name is None
    assert [var.name for var in parsed.block_data_units[0].variables] == ["seed"]


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


def test_preprocessor_without_macro_selection_keeps_distinct_conditional_procedures():
    code = """
#ifdef USE_A
subroutine from_ifdef()
end subroutine from_ifdef
#elif USE_B
subroutine from_elif()
end subroutine from_elif
#else
subroutine from_else()
end subroutine from_else
#endif

#ifndef USE_C
subroutine from_ifndef()
end subroutine from_ifndef
#endif
"""

    parsed = parse_fortran_file(code)

    assert [proc.name for proc in parsed.procedures] == [
        "from_ifdef",
        "from_elif",
        "from_else",
        "from_ifndef",
    ]


def test_statement_function_and_numeric_label_before_execution_part():
    code = """
subroutine old_style(x)
  real x
  real f
10 continue
  f(x) = x + 1.0
end subroutine old_style
"""

    sig = parse_fortran_file(code, filename="old_style.f90").procedures[0]

    assert sig.arguments[0].base_type == "real"


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


def test_readiness_accepts_procedure_local_kind_parameter():
    code = """
subroutine scale(x)
  integer, parameter :: rk = 8
  real(kind=rk), intent(inout) :: x
end subroutine scale
"""

    report = assess_wrap_readiness(code, filename="local_kind.f90")

    assert report["wrappable"] is True
    assert report["unresolved_kind_arguments"] == []


def test_preprocessor_boolean_identifiers_and_stray_directives_from_public_parse():
    code = """
#if USE_FAST && !USE_SLOW
subroutine selected_fast()
end subroutine selected_fast
#else
subroutine selected_slow()
end subroutine selected_slow
#endif

#else
#elif USE_OTHER
#endif

subroutine after_stray_directives()
end subroutine after_stray_directives
"""

    parsed = parse_fortran_file(code, filename="cpp_edges.f90", macro_defines={"USE_FAST": True})

    assert [proc.name for proc in parsed.procedures] == [
        "selected_fast",
        "after_stray_directives",
    ]


def test_malformed_public_procedure_headers_raise_from_source_lines():
    with pytest.raises(FortranParseError, match="Unsupported or malformed module procedure header"):
        parse_fortran_file(
            """
submodule (parent_mod) child_mod
contains
  module procedure reset(x)
end submodule child_mod
""",
            filename="bad_module_proc.f90",
        )

    with pytest.raises(FortranParseError, match="Unsupported or malformed procedure header"):
        parse_fortran_file(
            """
recursive, pure subroutine broken_header(x)
  integer :: x
end subroutine broken_header
""",
            filename="bad_proc_header.f90",
        )


def test_implicit_mapping_parameter_noise_and_assignment_lines_do_not_break_procedure_parse():
    code = """
subroutine declaration_noise(x)
  implicit real(a-h,o-z)
  integer, parameter :: n = 3, ignored_token
  parameter (m = 4, malformed_token)
  x = 1.0
  real x
end subroutine declaration_noise
"""

    sig = parse_fortran_file(code, filename="declaration_noise.f90").procedures[0]

    assert sig.arguments[0].name == "x"
    assert sig.arguments[0].base_type == "real"


def test_type_contains_ignores_executable_like_lines_and_rejects_bad_declarations():
    ok_code = """
module type_contains_ok_mod
  type :: state
  contains
    call ignored_statement()
  end type state
end module type_contains_ok_mod
"""
    bad_code = """
module type_contains_bad_mod
  type :: state
  contains
!$omp declare target
  end type state
end module type_contains_bad_mod
"""
    comma_bad_code = """
module type_contains_comma_bad_mod
  type :: state
  contains
    integer, public :: bad_binding
  end type state
end module type_contains_comma_bad_mod
"""

    parsed = parse_fortran_file(ok_code, filename="type_contains_ok.f90")
    assert parsed.modules[0].derived_types[0].methods == []

    with pytest.raises(FortranParseError, match="Unsupported or malformed type-bound declaration"):
        parse_fortran_file(bad_code, filename="type_contains_omp.f90")
    with pytest.raises(FortranParseError, match="Unsupported or malformed type-bound declaration"):
        parse_fortran_file(comma_bad_code, filename="type_contains_comma.f90")


def test_public_models_finalize_program_block_data_and_file_level_types_interfaces():
    project = parse_fortran_project(
        {
            "units_a.f90": """
type :: file_state
  integer :: id
end type file_state

interface file_callback
  subroutine cb()
  end subroutine cb
end interface file_callback

program driver
  integer :: status
end program driver

block data init_data
  integer seed
end block data init_data
""",
            "units_b.f90": """
program worker
  integer :: status
end program worker
""",
        }
    )

    assert "file_state" in project.derived_types
    assert "file_callback" in project.interfaces
    assert "driver" in project.programs
    assert "worker" in project.programs


def test_duplicate_program_and_block_data_variables_report_scope_labels():
    with pytest.raises(FortranParseError, match="Duplicate variable 'status' in program 'driver'"):
        parse_fortran_file(
            """
program driver
  integer :: status
  real :: status
end program driver
""",
            filename="dup_program_var.f90",
        )

    with pytest.raises(FortranParseError, match="Duplicate variable 'seed' in block data 'init_data'"):
        parse_fortran_file(
            """
block data init_data
  integer seed
  real seed
end block data init_data
""",
            filename="dup_block_var.f90",
        )


def test_use_statement_empty_only_items_are_ignored():
    code = """
module use_empty_items_mod
  use constants_mod, only: rk, , ik
  integer :: value
end module use_empty_items_mod
"""

    module = parse_fortran_file(code, filename="use_empty_items.f90").modules[0]

    assert [item.local_name for item in module.uses["constants_mod"]] == ["rk", "ik"]


def test_public_instance_visitor_entrypoints_use_source_strings():
    parser = FortranParser()

    assert parser.visit_file(
        """
subroutine alias_proc()
end subroutine alias_proc
"""
    ).procedures[0].name == "alias_proc"
    assert "alias_mod" in parser.visit_project(
        {
            "alias_mod.f90": """
module alias_mod
end module alias_mod
"""
        }
    ).modules

    with pytest.raises(FortranParseError, match="only standalone procedures were found"):
        parser.visit_fortran_module(
            """
subroutine lone_proc()
end subroutine lone_proc
"""
        )


def test_directory_project_resolves_module_kinds_and_orders_dependencies(tmp_path):
    (tmp_path / "kinds.f90").write_text(
        """
module kinds_mod
  integer, parameter :: rk = 8
end module kinds_mod
""",
        encoding="utf-8",
    )
    (tmp_path / "solver.f90").write_text(
        """
module solver_mod
  use kinds_mod, only: rk
contains
  function make_value(x) result(value)
    real(kind=rk), intent(in) :: x(1:rk)
    real(kind=rk) :: value
  end function make_value
end module solver_mod
""",
        encoding="utf-8",
    )

    project = parse_fortran_project(tmp_path)
    proc = project.procedures["solver_mod.make_value"]

    assert proc.arguments[0].kind == "8"
    assert proc.arguments[0].shape == ["1:rk"]
    assert proc.result.kind == "8"
    assert project.dependencies["solver_mod"] == {"kinds_mod"}


def test_directory_project_tracks_renamed_kind_imports_from_other_files(tmp_path):
    (tmp_path / "precision.f90").write_text(
        """
module precision_mod
  integer, parameter :: word = 4
  integer, parameter :: stride = 2
  integer, parameter :: wp = word * stride
  integer, parameter :: wide = wp * stride
end module precision_mod
""",
        encoding="utf-8",
    )
    (tmp_path / "solver.f90").write_text(
        """
module solver_mod
  use precision_mod, only: local_wp => wp, stride, local_wide => wide
contains
  subroutine consume(x, y)
    real(kind=local_wp), intent(in) :: x(1:stride)
    complex(kind=local_wide), intent(out) :: y
  end subroutine consume
end module solver_mod
""",
        encoding="utf-8",
    )

    project = parse_fortran_project(tmp_path)
    proc = project.procedures["solver_mod.consume"]
    args = {arg.name: arg for arg in proc.arguments}

    assert args["x"].kind == "8"
    assert args["x"].shape == ["1:stride"]
    assert args["y"].kind == "16"
    assert [(mapping.source, mapping.target) for mapping in proc.uses["precision_mod"]] == [
        ("wp", "local_wp"),
        ("stride", None),
        ("wide", "local_wide"),
    ]
    assert project.dependencies["solver_mod"] == {"precision_mod"}


def test_type_field_spec_variants_and_empty_entities_from_public_source():
    code = """
module type_field_edges_mod
  type :: state
    type :: nested_marker
    sequence
    private
    call ignored_in_type_spec()
    integer :: first, , second
  end type state
end module type_field_edges_mod
"""

    dtype = parse_fortran_file(code, filename="type_field_edges.f90").modules[0].derived_types[0]

    assert [field.name for field in dtype.fields] == ["first", "second"]


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
  integer :: kept
end program type_stmt_program
"""

    module = FortranParser().visit_fortran_modules(
        module_code,
        filename="module_like_edges.f90",
        signatures=[],
        types=[],
        interfaces=[],
    )[0]
    program = parse_fortran_file(program_code, filename="module_like_edges.f90").programs[0]

    assert [var.name for var in module.variables] == ["first", "second"]
    assert [var.name for var in program.variables] == ["kept"]


def test_interface_finalizes_pending_procedure_at_end_interface_and_import_attrs():
    code = """
interface named_callback
  subroutine cb(x)
    import :: c_int
    integer(c_int), intent(in) :: x
end interface named_callback
"""

    iface = parse_fortran_file(code, filename="pending_interface.f90").interfaces[0]
    proc = iface.procedures[0]

    assert proc.name == "cb"
    assert "interface(named_callback)" in proc.attributes
    assert "import(c_int)" in proc.attributes


def test_wrap_readiness_infers_interface_argument_types_for_readiness():
    code = """
interface
  subroutine cb(x)
    implicit none
  end subroutine cb
end interface
"""

    report = assess_wrap_readiness(code, filename="unknown_interface_arg.f90")

    assert report["wrappable"] is True
    assert report["unknown_argument_types"] == []


def test_stray_end_unit_lines_are_ignored_by_public_file_parse():
    parsed = parse_fortran_file(
        """
end module stray_mod
end submodule stray_submod
end program stray_program
end interface

subroutine kept()
end subroutine kept
""",
        filename="stray_ends.f90",
    )

    assert [proc.name for proc in parsed.procedures] == ["kept"]


def test_directory_namespace_records_missing_and_parent_only_submodule_dependencies(tmp_path):
    (tmp_path / "parent.f90").write_text(
        """
module parent_mod
end module parent_mod
""",
        encoding="utf-8",
    )
    (tmp_path / "child.f90").write_text(
        """
submodule (parent_mod) child_mod
  use missing_mod
contains
  module procedure reset
  end procedure reset
end submodule child_mod
""",
        encoding="utf-8",
    )

    project = parse_fortran_project(tmp_path)

    assert project.dependencies["child_mod"] == {"parent_mod", "missing_mod"}


def test_program_and_block_data_scope_errors_use_public_parse_paths():
    with pytest.raises(FortranParseError, match="Unsupported OpenMP declarative directive in program 'driver'"):
        parse_fortran_file(
            """
program driver
!$omp threadprivate(counter)
end program driver
""",
            filename="program_omp_decl.f90",
        )

    with pytest.raises(FortranParseError, match="Unsupported OpenMP declarative directive in block data 'init_data'"):
        parse_fortran_file(
            """
block data init_data
!$omp threadprivate(seed)
end block data init_data
""",
            filename="block_omp_decl.f90",
        )

    with pytest.raises(FortranParseError, match="Unknown or unsupported datatype declaration in program 'driver'"):
        parse_fortran_file(
            """
program driver
  weirdtype state
end program driver
""",
            filename="program_unknown_decl.f90",
        )

    with pytest.raises(FortranParseError, match="Unknown or unsupported datatype declaration in block data 'init_data'"):
        parse_fortran_file(
            """
block data init_data
  weirdtype seed
end block data init_data
""",
            filename="block_unknown_decl.f90",
        )


def test_public_assess_wrap_readiness_alias_and_module_parameter_noise(tmp_path):
    parser = FortranParser()
    code = """
module noisy_params_mod
  integer, parameter :: rk = 8, ignored_token
contains
  subroutine scale(x)
    real(kind=rk), intent(inout) :: x
  end subroutine scale
end module noisy_params_mod
"""

    report = parser.visit_wrap_readiness(code, filename="noisy_params.f90")

    assert report["wrappable"] is True

    source_path = tmp_path / "listed_project.f90"
    source_path.write_text(
        """
module listed_project_mod
contains
  subroutine work()
  end subroutine work
end module listed_project_mod
""",
        encoding="utf-8",
    )

    project = parse_fortran_project([source_path])

    assert "listed_project_mod" in project.modules
    assert "listed_project_mod.work" in project.procedures


def test_project_resolution_keeps_relevant_local_parameter_variables():
    project = parse_fortran_project(
        {
            "local_params.f90": """
subroutine use_relevant_local_param(e)
  integer, parameter :: n = 8
  integer, parameter :: one = 1.0d+0
  real, intent(inout) :: e(1:+n-one)
end subroutine use_relevant_local_param
"""
        }
    )

    proc = project.procedures["use_relevant_local_param"]

    assert proc.arguments[0].shape == ["1:+(8)-one"]
    assert proc.variables["one"].value == "1"


def test_project_resolution_uses_file_level_use_only_and_local_parameters(tmp_path):
    (tmp_path / "params.f90").write_text(
        """
module public_params_mod
  integer, parameter :: rk = selected_real_kind(12)
  integer, parameter :: n = 4
end module public_params_mod
""",
        encoding="utf-8",
    )
    (tmp_path / "worker.f90").write_text(
        """
subroutine file_level_worker(x, y)
  use public_params_mod, only: rk, , n
  integer, parameter :: local_rk = selected_real_kind(6)
  real(kind=rk), intent(inout) :: x(1:n)
  real(kind=local_rk), intent(out) :: y
end subroutine file_level_worker
""",
        encoding="utf-8",
    )
    project = parse_fortran_project(tmp_path)

    proc = project.procedures["file_level_worker"]
    args = {arg.name: arg for arg in proc.arguments}

    assert args["x"].kind == "selected_real_kind(12)"
    assert args["x"].shape == ["1:n"]
    assert args["y"].kind == "selected_real_kind(6)"
    assert [mapping.local_name for mapping in proc.uses["public_params_mod"]] == ["rk", "n"]


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
