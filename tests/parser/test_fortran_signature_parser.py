# -*- coding: utf-8 -*-
import pytest

from fortran_parser.cli import _format_wrap_readiness

from fortran_parser import (
    FortranParseError,
    assess_wrap_readiness,
    collect_signature_shape_symbols,
    evaluate_signature_shapes,
    parse_fortran_file,
    parse_fortran_project,
    parse_fortran_namespace,
    parse_fortran_project_signatures,
    parse_fortran_signature,
    parse_fortran_signatures,
    parse_fortran_block_data,
    parse_fortran_block_data_unit,
    parse_fortran_derived_type,
    parse_fortran_interface,
    parse_fortran_interfaces,
    parse_fortran_module,
    parse_fortran_modules,
    parse_fortran_program,
    parse_fortran_programs,
    parse_fortran_submodule,
    parse_fortran_submodules,
    parse_fortran_types,
)


def test_subroutine_signature_with_intent_and_dimension():
    code = """
module linalg_mod
contains
pure subroutine axpy(n, a, x, y)
  integer, intent(in) :: n
  real(kind=8), intent(in) :: a
  real(kind=8), intent(in), dimension(:) :: x
  real(kind=8), intent(inout) :: y(:)
end subroutine axpy
end module linalg_mod
"""
    signatures = FortranParser().parse_file(code)
    assert len(signatures) == 1

    sig = signatures[0]
    assert sig.module == "linalg_mod"
    assert sig.name == "axpy"
    assert sig.kind == "subroutine"
    assert "pure" in sig.attributes

    n, a, x, y = sig.arguments
    assert n.base_type == "integer"
    assert n.intent == "in"
    assert a.base_type == "real"
    assert a.kind == "8"
    assert a.intent == "in"
    assert x.rank == 1
    assert x.shape == [":"]
    assert y.rank == 1
    assert y.shape == [":"]
    assert y.intent == "inout"


def test_function_result_and_use_statement():
    code = """
function norm2(x) result(res)
  use iso_c_binding, only: c_double
  real(kind=c_double), intent(in) :: x(:)
  real(kind=c_double) :: res
end function norm2
"""
    signatures = FortranParser().parse_file(code)
    sig = signatures[0]
    assert sig.kind == "function"
    assert sig.result is not None
    assert sig.result.name == "res"
    assert sig.result.base_type == "real"
    assert sig.uses["iso_c_binding"] == ["c_double"]
    assert sig.arguments[0].shape == [":"]


def test_fixed_form_and_interface_detection():
    code = """
      subroutine saxpy(n,x,y)
      integer, intent(in) :: n
      real, dimension(n), intent(in) :: x
      real, dimension(n), intent(inout) :: y
      end
      interface
        subroutine cb(i)
          integer, intent(in) :: i
        end subroutine cb
      end interface
"""
    signatures = FortranParser().parse_file(code, filename="legacy.f")
    assert len(signatures) == 2
    assert signatures[0].name == "saxpy"
    assert signatures[0].arguments[1].shape == ["n"]
    assert signatures[1].in_interface is True

    with pytest.raises(ValueError, match="Fortran 77"):
        FortranParser().parse_file(code, filename="legacy.f77")

    signatures = FortranParser().parse_file(code, filename="legacy.f90")
    assert len(signatures) == 2
    assert signatures[0].name == "saxpy"
    assert signatures[0].arguments[1].shape == ["n"]
    assert signatures[1].in_interface is True


def test_kind_resolution_from_imported_module_across_files():
    files = {
        "kinds.f90": """
module my_kinds
  integer, parameter :: rk = selected_real_kind(15, 307)
end module my_kinds
""",
        "solver.f90": """
module solver
contains
subroutine step(x)
  use my_kinds, only: rk
  real(kind=rk), intent(inout) :: x(:)
end subroutine step
end module solver
""",
    }
    signatures = parse_fortran_project_signatures(files)
    step = [s for s in signatures if s.name == "step"][0]
    assert step.arguments[0].kind == "selected_real_kind(15, 307)"


def test_derived_type_fields_and_methods_detection():
    code = """
module particle_mod
  type :: particle
    integer :: id
    real(kind=8), dimension(3) :: x
    type(vector), pointer :: velocity
  contains
    procedure :: move, reset
  end type particle
end module particle_mod
"""
    types = FortranParser().parse_file(code)
    assert len(types) == 1
    t = types[0]
    assert t.name == "particle"
    assert t.module == "particle_mod"
    assert t.methods == ["move", "reset"]
    assert [f.name for f in t.fields] == ["id", "x", "velocity"]
    assert t.fields[1].shape == ["3"]
    assert t.fields[2].base_type == "derived"
    assert t.fields[2].kind == "vector"


def test_module_variables_and_use_statements():
    code = """
module cfg
  use iso_c_binding, only: c_int
  integer(kind=c_int) :: nmax
  real(kind=8), dimension(3) :: origin
end module cfg
"""
    modules = FortranParser().parse_file(code)
    assert len(modules) == 1
    mod = modules[0]
    assert mod.name == "cfg"
    assert mod.uses["iso_c_binding"] == ["c_int"]
    assert [v.name for v in mod.variables] == ["nmax", "origin"]
    assert mod.variables[1].shape == ["3"]


def test_module_contains_procedure_and_type_children():
    code = """
module m1
  integer :: cfg
  type :: particle
    integer :: id
  end type particle
contains
  subroutine add1(n, x)
    integer, intent(in) :: n
    real, intent(inout) :: x(:)
  end subroutine add1
end module m1
"""
    modules = FortranParser().parse_file(code)
    assert len(modules) == 1
    mod = modules[0]
    assert mod.name == "m1"
    assert mod.filename is None
    assert [p.name for p in mod.procedures] == ["add1"]
    assert mod.procedures[0].arguments[0].procedure == "add1"
    assert [t.name for t in mod.derived_types] == ["particle"]


def test_module_contains_interfaces():
    code = """
module m1
  interface apply
    subroutine do_apply(n)
      integer, intent(in) :: n
    end subroutine do_apply
  end interface
end module m1
"""
    interfaces = FortranParser().parse_file(code)
    assert len(interfaces) == 1
    iface = interfaces[0]
    assert iface.name == "apply"
    assert iface.module == "m1"
    assert [p.name for p in iface.procedures] == ["do_apply"]
    mod = FortranParser().parse_file(code)[0]
    assert len(mod.interfaces) == 1


def test_fixed_form_fortran77_continuation():
    code = """
      subroutine saxpy(n,x,y,a)
      integer n
      real x(n),y(n),a
      do 10 i=1,n
     1y(i)=y(i)+a*x(i)
 10   continue
      end
"""
    sigs = FortranParser().parse_file(code, filename="legacy.f")
    assert len(sigs) == 1
    assert sigs[0].name == "saxpy"
    assert sigs[0].arguments[0].base_type == "integer"
    assert sigs[0].arguments[1].base_type == "real"
    assert sigs[0].arguments[1].rank == 1


def test_fixed_form_parameter_statement_after_typed_constants():
    code = """
      subroutine cst(a)
      real a
      real zero, one
      parameter ( zero = 0.0e+0, one = 1.0e+0 )
      a = a + one - zero
      end
"""
    sigs = FortranParser().parse_file(code, filename="legacy.f")
    assert len(sigs) == 1
    assert sigs[0].variables == {}


def test_duplicate_declaration_raises_error():
    code = """
subroutine dup(x)
  real :: x
  integer :: x
end subroutine dup
"""
    with pytest.raises(ValueError, match="Duplicate declaration"):
        FortranParser().parse_file(code, filename="dup.f90")


def test_fixed_form_character_star_length_is_parsed():
    code = """
      subroutine xerbla(srname, info)
      character*(*) srname
      integer info
      end
"""
    sigs = FortranParser().parse_file(code, filename="legacy.f")
    assert len(sigs) == 1
    assert sigs[0].arguments[0].base_type == "character"
    assert sigs[0].arguments[0].kind == "*"


def test_duplicate_function_result_declaration_raises_error():
    code = """
real function f(x)
  real :: x
  real :: f
end function f
"""
    with pytest.raises(ValueError, match="Duplicate declaration"):
        FortranParser().parse_file(code, filename="dup_result.f90")


def test_duplicate_function_result_with_result_keyword_raises_error():
    code = """
real function f(x) result(res)
  real :: x
  real :: res
end function f
"""
    with pytest.raises(ValueError, match="Duplicate declaration"):
        FortranParser().parse_file(code, filename="dup_result_kw.f90")


def test_fixed_form_parameter_without_typed_declaration_raises_error():
    code = """
      subroutine cst(a)
      implicit none
      real a
      parameter ( zero = 0.0e+0 )
      end
"""
    with pytest.raises(ValueError, match="Unknown datatype for PARAMETER symbol"):
        FortranParser().parse_file(code, filename="legacy.f")


def test_fixed_form_parameter_without_typed_declaration_allowed_with_implicit_typing():
    code = """
      subroutine cst()
      parameter ( one = 1.0e+0 )
      end
"""
    sigs = FortranParser().parse_file(code, filename="legacy.f")
    assert len(sigs) == 1
    assert sigs[0].variables["one"].base_type == "real"
    assert sigs[0].variables["one"].value == "1"


def test_modern_parameter_without_typed_declaration_uses_implicit_typing():
    code = """
subroutine cst()
  parameter (ival = 2)
end subroutine cst
"""
    sig = FortranParser().parse_file(code, filename="modern.f90")[0]
    assert sig.variables["ival"].base_type == "integer"
    assert sig.variables["ival"].value == "2"


def test_duplicate_initialized_declaration_raises_error():
    code = """
subroutine dup_init()
  integer :: x = 1
  integer :: x = 2
end subroutine dup_init
"""
    with pytest.raises(ValueError, match="Duplicate declaration"):
        FortranParser().parse_file(code, filename="dup_init.f90")


def test_duplicate_procedure_name_same_scope_raises_error():
    code = """
subroutine work(n)
  integer, intent(in) :: n
end subroutine work

function work(n) result(out)
  integer, intent(in) :: n
  integer :: out
end function work
"""
    with pytest.raises(ValueError, match="Duplicate procedure name"):
        FortranParser().parse_file(code, filename="dup_proc.f90")


def test_duplicate_procedure_name_same_module_scope_raises_error():
    code = """
module m
contains
  subroutine work(n)
    integer, intent(in) :: n
  end subroutine work
  function work(n) result(out)
    integer, intent(in) :: n
    integer :: out
  end function work
end module m
"""
    with pytest.raises(ValueError, match="Duplicate procedure name"):
        FortranParser().parse_file(code, filename="dup_mod_proc.f90")


def test_legacy_star_kind_parameter_symbol_is_recognized():
    code = """
      subroutine zgbmv_like()
      complex*16 one
      parameter (one = (1.0d+0,0.0d+0))
      end
"""
    sig = FortranParser().parse_file(code, filename="legacy.f")[0]
    assert sig.variables == {}


def test_legacy_star_kind_parameter_list_with_implicit_none_is_recognized():
    code = """
      subroutine zgejsv_like()
      implicit none
      complex*16 czero, cone
      parameter ( czero = (0.0d0,0.0d0), cone = (1.0d0,0.0d0) )
      end
"""
    sig = FortranParser().parse_file(code, filename="legacy.f")[0]
    assert sig.variables == {}


def test_implicit_none_allows_external_dummy_procedure_argument():
    code = """
subroutine fdjac1(fcn, n)
  implicit none
  integer, intent(in) :: n
  external :: fcn
end subroutine fdjac1
"""
    sig = FortranParser().parse_file(code, filename="fdjac1.f90")[0]
    assert sig.arguments[0].name == "fcn"
    assert sig.arguments[0].base_type == "procedure"

def test_external_attribute_and_later_type_declaration_do_not_conflict():
    code = """
subroutine lapack_style(slamch)
  implicit none
  external slamch
  real slamch
end subroutine lapack_style
"""
    sig = FortranParser().parse_file(code, filename="lapack_style.f90")[0]
    assert sig.arguments[0].name == "slamch"
    assert sig.arguments[0].base_type == "real"


def test_named_generic_interface_procedures_are_tagged_with_interface_name():
    code = """
interface foo
  integer function foo_i(x)
    integer, intent(in) :: x
  end function foo_i

  real function foo_r(x)
    real, intent(in) :: x
  end function foo_r
end interface foo
"""
    interfaces = FortranParser().parse_file(code, filename="iface_generic.f90")
    assert len(interfaces) == 1
    assert interfaces[0].name == "foo"
    assert [p.name for p in interfaces[0].procedures] == ["foo_i", "foo_r"]
    assert all(p.in_interface for p in interfaces[0].procedures)


def test_external_dummy_keeps_recursive_attribute_metadata():
    code = """
recursive function apply_once(f, x) result(y)
  implicit none
  real, external :: f
  real, intent(in) :: x
  real :: y
  y = f(x)
end function apply_once
"""
    sig = FortranParser().parse_file(code, filename="apply_once.f90")[0]
    assert sig.kind == "function"
    assert "recursive" in sig.attributes
    assert sig.arguments[0].name == "f"
    assert sig.arguments[0].base_type == "real"


def test_external_dummy_keeps_interface_context_metadata():
    code = """
interface
  subroutine driver(fcn, x)
    implicit none
    external :: fcn
    real, intent(in) :: x
  end subroutine driver
end interface
"""
    sig = FortranParser().parse_file(code, filename="iface_external.f90")[0]
    assert sig.in_interface is True
    assert sig.arguments[0].name == "fcn"
    assert sig.arguments[1].name == "x"
    assert sig.arguments[1].base_type == "real"


def test_external_function_dummy_with_explicit_result_type_is_parsed():
    code = """
subroutine apply_cb(f, x, y)
  implicit none
  real, intent(in) :: x
  real, intent(out) :: y
  real, external :: f
  y = f(x)
end subroutine apply_cb
"""
    sig = FortranParser().parse_file(code, filename="apply_cb.f90")[0]
    f_arg = sig.arguments[0]
    assert f_arg.name == "f"
    assert f_arg.base_type == "real"

def test_ignore_local_variables_in_signatures():
    code = """
subroutine update(n, x)
  integer, intent(in) :: n
  real, intent(inout) :: x(n)
  integer :: i
  real :: tmp
end subroutine update
"""
    sig = FortranParser().parse_file(code)[0]
    assert [a.name for a in sig.arguments] == ["n", "x"]
    assert sig.arguments[0].base_type == "integer"
    assert sig.arguments[1].base_type == "real"


def test_ignore_internal_procedures_in_contains_block():
    code = """
subroutine outer(x)
  real, intent(inout) :: x
contains
  subroutine inner(y)
    real, intent(inout) :: y
  end subroutine inner
end subroutine outer
"""
    sigs = FortranParser().parse_file(code)
    assert len(sigs) == 1
    assert sigs[0].name == "outer"


def test_local_parameter_kind_used_in_argument_declaration():
    code = """
subroutine saxpy(x)
  integer, parameter :: rk = selected_real_kind(15, 307)
  real(kind=rk), intent(inout) :: x(:)
end subroutine saxpy
"""
    sig = FortranParser().parse_file(code)[0]
    assert sig.arguments[0].kind == "selected_real_kind(15, 307)"


def test_compile_time_shape_eval_with_local_and_imported_params():
    files = {
        "kinds.f90": """
module k
  integer, parameter :: n = 8
end module k
""",
        "solver.f90": """
subroutine step(x)
  use k, only: n
  integer, parameter :: m = n + 2
  real, intent(inout) :: x(m*2)
end subroutine step
""",
    }
    sig = parse_fortran_project_signatures(files)[0]
    assert sig.arguments[0].shape == ["20"]


def test_assess_wrap_readiness_supported_and_unsupported():
    supported = """
subroutine saxpy(n, x, y)
  integer, intent(in) :: n
  real(kind=8), intent(in) :: x(:)
  real(kind=8), intent(inout) :: y(:)
end subroutine saxpy
"""
    report_ok = assess_wrap_readiness(supported)
    assert report_ok["wrappable"] is True
    assert report_ok["unsupported_constructs"] == []

    unsupported = """
subroutine s(a)
  class(*), intent(inout) :: a
end subroutine s
"""
    report_bad = assess_wrap_readiness(unsupported)
    assert report_bad["wrappable"] is False
    assert report_bad["unsupported_constructs"]


def test_assess_wrap_readiness_explains_no_procedures_found():
    code = """
module constants
  integer, parameter :: n = 4
end module constants
"""
    report = assess_wrap_readiness(code, filename="constants.f90")
    assert report["wrappable"] is False
    assert report["why_not_wrappable"] == ["No procedure signatures were found to wrap."]
    assert report["wrappability_blockers"] == [
        {
            "code": "no_signatures",
            "message": "No procedure signatures were found to wrap.",
            "items": [],
        }
    ]


def test_assess_wrap_readiness_explains_unsupported_constructs():
    code = """
subroutine visit(obj)
  class(*), intent(inout) :: obj
end subroutine visit
"""
    report = assess_wrap_readiness(code, filename="unsupported.f90")
    assert report["wrappable"] is False
    assert [b["code"] for b in report["wrappability_blockers"]] == ["unsupported_constructs"]
    assert report["wrappability_blockers"][0]["items"][0]["text"] == "class(*), intent(inout) :: obj"


def test_assess_wrap_readiness_reports_imported_derived_type_argument_without_definition():
    code = """
module solver
  use state_mod, only: sim_state
contains
subroutine step(state)
  type(sim_state), intent(inout) :: state
end subroutine step
end module solver
"""
    report = assess_wrap_readiness(code, filename="solver.f90")
    assert report["wrappable"] is False
    assert report["unresolved_derived_type_arguments"] == [
        {
            "procedure": "step",
            "module": "solver",
            "argument": "state",
            "type": "sim_state",
            "import_modules": ["state_mod"],
        }
    ]


def test_assess_wrap_readiness_accepts_derived_type_argument_defined_in_same_source():
    code = """
module state_mod
  type :: sim_state
    real :: value
  end type sim_state
end module state_mod

module solver
  use state_mod, only: sim_state
contains
subroutine step(state)
  type(sim_state), intent(inout) :: state
end subroutine step
end module solver
"""
    report = assess_wrap_readiness(code, filename="solver_with_state.f90")
    assert report["wrappable"] is True
    assert report["unresolved_derived_type_arguments"] == []


def test_assess_wrap_readiness_reports_imported_derived_type_field_without_definition():
    code = """
module mesh_mod
  use point_mod, only: point
  type :: mesh
    type(point) :: origin
  end type mesh
contains
subroutine update(m)
  type(mesh), intent(inout) :: m
end subroutine update
end module mesh_mod
"""
    report = assess_wrap_readiness(code, filename="mesh.f90")
    assert report["wrappable"] is False
    assert report["unresolved_derived_type_arguments"] == []
    assert report["unresolved_derived_type_fields"] == [
        {
            "type_owner": "mesh",
            "module": "mesh_mod",
            "field": "origin",
            "type": "point",
            "import_modules": ["point_mod"],
        }
    ]


def test_assess_wrap_readiness_reports_imported_kind_argument_without_definition():
    code = """
subroutine scale(x)
  use kinds_mod, only: rk
  real(kind=rk), intent(inout) :: x
end subroutine scale
"""
    report = assess_wrap_readiness(code, filename="scale.f90")
    assert report["wrappable"] is False
    assert report["unresolved_kind_arguments"] == [
        {
            "procedure": "scale",
            "module": None,
            "argument": "x",
            "kind": "rk",
            "import_modules": ["kinds_mod"],
        }
    ]
    assert [b["code"] for b in report["wrappability_blockers"]] == ["unresolved_kind_arguments"]


def test_assess_wrap_readiness_reports_imported_kind_field_without_definition():
    code = """
module state_mod
  use kinds_mod, only: rk
  type :: sim_state
    real(kind=rk) :: value
  end type sim_state
contains
subroutine update(state)
  type(sim_state), intent(inout) :: state
end subroutine update
end module state_mod
"""
    report = assess_wrap_readiness(code, filename="state.f90")
    assert report["wrappable"] is False
    assert report["unresolved_derived_type_fields"] == []
    assert report["unresolved_kind_fields"] == [
        {
            "type_owner": "sim_state",
            "module": "state_mod",
            "field": "value",
            "kind": "rk",
            "import_modules": ["kinds_mod"],
        }
    ]


def test_assess_wrap_readiness_accumulates_multiple_blocker_reasons():
    code = """
module state_mod
  use point_mod, only: point
  use kinds_mod, only: rk
  type :: sim_state
    type(point) :: origin
    real(kind=rk) :: value
  end type sim_state
contains
subroutine update(state, x)
  type(missing_state), intent(inout) :: state
  real(kind=rk), intent(inout) :: x
end subroutine update
end module state_mod
"""
    report = assess_wrap_readiness(code, filename="multi_blocker.f90")
    assert report["wrappable"] is False
    assert [b["code"] for b in report["wrappability_blockers"]] == [
        "unresolved_derived_type_arguments",
        "unresolved_derived_type_fields",
        "unresolved_kind_arguments",
        "unresolved_kind_fields",
    ]


def test_cli_wrap_readiness_format_reports_status_and_reasons():
    report = {
        "bad.f90": {
            "wrap_readiness": {
                "wrappable": False,
                "wrappability_blockers": [
                    {
                        "code": "unresolved_derived_type_arguments",
                        "message": "Some derived-type procedure arguments refer to types missing from the parsed source.",
                        "items": [
                            {
                                "procedure": "step",
                                "module": "solver",
                                "argument": "state",
                                "type": "sim_state",
                                "import_modules": ["state_mod"],
                            }
                        ],
                    }
                ],
            }
        }
    }
    text = _format_wrap_readiness(report)
    assert "Wrappable: no" in text
    assert "Why not wrappable:" in text
    assert "step:state uses type(sim_state) from state_mod" in text


def test_assess_wrap_readiness_accepts_intrinsic_module_kind_symbols():
    code = """
subroutine scale(x)
  use iso_c_binding, only: c_double
  real(kind=c_double), intent(inout) :: x
end subroutine scale
"""
    report = assess_wrap_readiness(code, filename="intrinsic_kind.f90")
    assert report["wrappable"] is True
    assert report["unresolved_kind_arguments"] == []


def test_parse_namespace_dependency_resolution(tmp_path):
    dep = tmp_path / "kinds.f90"
    user = tmp_path / "solver.f90"
    user.write_text(
        """
module solver
  use my_kinds, only: rk
contains
subroutine step(x)
  real(kind=rk), intent(inout) :: x(:)
end subroutine step
end module solver
""",
        encoding="utf-8",
    )
    dep.write_text(
        """
module my_kinds
  integer, parameter :: rk = selected_real_kind(15, 307)
end module my_kinds
""",
        encoding="utf-8",
    )

    ns = parse_fortran_namespace(tmp_path)
    assert len(ns["files"]) == 2
    assert ns["module_to_file"]["my_kinds"].endswith("kinds.f90")
    assert ns["module_to_file"]["solver"].endswith("solver.f90")
    step = [s for s in ns["signatures"] if s.name == "step"][0]
    assert step.arguments[0].kind == "selected_real_kind(15, 307)"


def test_recursive_function_and_result_keyword_variants():
    code = """
recursive function fact(n) results(res)
  integer, intent(in) :: n
  integer :: res
end function fact
"""
    sig = FortranParser().parse_file(code)[0]
    assert "recursive" in sig.attributes
    assert sig.result is not None
    assert sig.result.name == "res"


def test_assumed_shape_with_explicit_lower_bounds_is_preserved():
    code = """
subroutine fill_grid(x)
  integer, intent(inout) :: x(0:,0:)
end subroutine fill_grid
"""
    sig = FortranParser().parse_file(code)[0]
    arg = sig.arguments[0]
    assert arg.base_type == "integer"
    assert arg.rank == 2
    assert arg.shape == ["0:", "0:"]


def test_dimension_attribute_with_mixed_bounds_is_parsed():
    code = """
subroutine update_plane(x)
  real, intent(inout), dimension(0:, 1:n) :: x
end subroutine update_plane
"""
    sig = FortranParser().parse_file(code)[0]
    arg = sig.arguments[0]
    assert arg.rank == 2
    assert arg.shape == ["0:", "1:n"]
    assert arg.lower_bounds == ["0", "1"]
    assert arg.upper_bounds == [None, "n"]
    assert arg.lbound == ["0", "1"]
    assert arg.ubound == [None, "n"]
    assert arg.shape_info == [
        {"raw": "0:", "lower": "0", "upper": None},
        {"raw": "1:n", "lower": "1", "upper": "n"},
    ]


def test_shape_info_for_explicit_extent_dimension():
    code = """
subroutine resize(x)
  real, intent(inout) :: x(n)
end subroutine resize
"""
    sig = FortranParser().parse_file(code)[0]
    arg = sig.arguments[0]
    assert arg.shape_info == [
        {"raw": "n", "lower": "1", "upper": "n"},
    ]
    assert arg.lower_bounds == ["1"]
    assert arg.upper_bounds == ["n"]
    assert arg.lbound == ["1"]
    assert arg.ubound == ["n"]


def test_subroutine_derived_type_arguments_are_parsed():
    code = """
subroutine step(state)
  type(sim_state), intent(inout) :: state
end subroutine step
"""
    sig = FortranParser().parse_file(code)[0]
    arg = sig.arguments[0]
    assert arg.base_type == "derived"
    assert arg.kind == "sim_state"
    assert arg.intent == "inout"


def test_compile_time_parameter_expressions_are_evaluated_in_shapes():
    files = {
        "dims.f90": """
module dims_mod
  integer, parameter :: n0 = 4
  integer, parameter :: n1 = n0 + 2
contains
  subroutine use_expr(x, y)
    integer, intent(inout) :: x(0:n1-1)
    real, intent(inout), dimension(1:n0*2) :: y
  end subroutine use_expr
end module dims_mod
"""
    }
    sig = parse_fortran_project_signatures(files)[0]
    assert sig.arguments[0].shape == ["0:5"]
    assert sig.arguments[1].shape == ["1:8"]


def test_local_parameters_in_contained_procedures_do_not_leak_across_signatures():
    files = {
        "dims.f90": """
module dims_mod
  integer, parameter :: n = 3
contains
  subroutine a()
    integer, parameter :: n = 9
  end subroutine a

  subroutine b(x)
    real, intent(inout) :: x(1:n)
  end subroutine b
end module dims_mod
"""
    }

    sig = parse_fortran_project_signatures(files)[0]
    assert sig.name == "a"
    sig_b = parse_fortran_project_signatures(files)[1]
    assert sig_b.name == "b"
    assert sig_b.arguments[0].shape == ["1:3"]




def test_compiler_dependent_parameter_expressions_remain_symbolic_with_value_at_module_level():
    files = {
        "kinds.f90": """
module kinds_mod
  integer, parameter :: ip = selected_int_kind(9)
contains
  subroutine use_kind_expr(x)
    real, dimension(1:ip), intent(inout) :: x
  end subroutine use_kind_expr
end module kinds_mod
"""
    }
    sig = parse_fortran_project_signatures(files)[0]
    assert sig.arguments[0].shape == ["1:ip"]
    assert sig.variables["ip"].name == "ip"
    assert sig.variables["ip"].value == "selected_int_kind(9)"


def test_local_compiler_dependent_parameter_expressions_remain_symbolic_with_value():
    code = """
subroutine use_local_kind_expr(x)
  integer, parameter :: ip = selected_int_kind(9)
  real, dimension(1:ip), intent(inout) :: x
end subroutine use_local_kind_expr
"""
    sig = FortranParser().parse_file(code)[0]
    assert sig.arguments[0].shape == ["1:ip"]
    assert sig.variables["ip"].name == "ip"
    assert sig.variables["ip"].value == "selected_int_kind(9)"


def test_compile_time_parameter_expression_resolves_deep_dependency_chains():
    files = {
        "dims.f90": """
module dims_mod
  integer, parameter :: n0 = 1
  integer, parameter :: n1 = n0 + 1
  integer, parameter :: n2 = n1 + 1
  integer, parameter :: n3 = n2 + 1
  integer, parameter :: n4 = n3 + 1
  integer, parameter :: n5 = n4 + 1
contains
  subroutine use_expr(x)
    integer, intent(inout) :: x(1:n5)
  end subroutine use_expr
end module dims_mod
"""
    }
    sig = parse_fortran_project_signatures(files)[0]
    assert sig.arguments[0].shape == ["1:6"]


def test_symbolic_shape_symbols_can_be_collected_and_later_evaluated():
    code = """
subroutine s(a)
  real, intent(inout) :: a(0:nx-1, 1:ny*2)
end subroutine s
"""
    sig = FortranParser().parse_file(code)[0]
    assert collect_signature_shape_symbols(sig) == {"nx", "ny"}

    evaluated = evaluate_signature_shapes(sig, {"nx": 6, "ny": 4})
    assert evaluated.arguments[0].shape == ["0:5", "1:8"]


def test_big_compile_time_expression_suite():
    files = {
        "exprs.f90": """
module expr_mod
  integer, parameter :: a = 8
  integer, parameter :: b = 3
  integer, parameter :: c = 2
  integer, parameter :: p_add = a + b
  integer, parameter :: p_sub = a - b
  integer, parameter :: p_mul = b * c
  integer, parameter :: p_div = a / c
  integer, parameter :: p_pow = c ** b
  integer, parameter :: p_mix = (a + b) * c - 1
contains
  subroutine all_exprs(x1, x2, x3, x4, x5, x6, x7, x8, x9)
    integer, intent(inout) :: x1(1:p_add)
    integer, intent(inout) :: x2(1:p_sub)
    integer, intent(inout) :: x3(1:p_mul)
    integer, intent(inout) :: x4(1:p_div)
    integer, intent(inout) :: x5(1:p_pow)
    integer, intent(inout) :: x6(0:p_mix)
    integer, intent(inout) :: x7(1:-(-a + b))
    integer, intent(inout) :: x8(1:(a+b)*(c+1)-1)
    integer, intent(inout) :: x9(1:(a-b)*(a-c))
  end subroutine all_exprs
end module expr_mod
"""
    }
    sig = parse_fortran_project_signatures(files)[0]
    assert [a.shape[0] for a in sig.arguments] == ["1:11", "1:5", "1:6", "1:4", "1:8", "0:21", "1:5", "1:32", "1:30"]


def test_derived_type_extends_and_attributes():
    code = """
module m
  type :: base_t
  end type base_t
  type, extends(base_t), abstract :: child_t
    integer :: id
  contains
    procedure :: run
  end type child_t
end module m
"""
    dt = FortranParser().parse_file(code)[1]
    assert dt.name == "child_t"
    assert dt.extends is not None
    assert getattr(dt.extends, "name", None) == "base_t"
    assert "abstract" in dt.attributes


def test_derived_type_extends_external_parent_stays_symbolic():
    code = """
module m
  type, extends(external_base_t) :: child_t
  end type child_t
end module m
"""
    dt = FortranParser().parse_file(code)[0]
    assert dt.extends == "external_base_t"


def test_derived_type_procedure_and_generic_bindings():
    code = """
module m
  type :: t
  contains
    procedure, pass(self) :: init => t_init
    procedure, nopass :: clear
    generic :: assignment(=) => init
    generic, public :: setup => init, clear
  end type t
end module m
"""
    dt = FortranParser().parse_file(code)[0]
    assert {"name": "init => t_init", "attrs": ["pass(self)"]} in dt.procedure_bindings
    assert {"name": "clear", "attrs": ["nopass"]} in dt.procedure_bindings
    assert {"name": "assignment(=)", "targets": ["init"], "attrs": []} in dt.generic_bindings
    assert {"name": "setup", "targets": ["init", "clear"], "attrs": ["public"]} in dt.generic_bindings


def test_star_kind_is_rejected_in_modern_fortran_file():
    code = """
subroutine bad(x)
  real*8 :: x
end subroutine bad
"""
    with pytest.raises(ValueError, match="star-kind"):
        FortranParser().parse_file(code, filename="bad.f90")


def test_unknown_datatype_for_argument_crashes_parser():
    code = """
subroutine bad(x)
  weirdtype :: x
end subroutine bad
"""
    with pytest.raises(ValueError, match="Unknown or unsupported datatype"):
        FortranParser().parse_file(code, filename="bad.f90")


def test_submodule_procedures_and_namespace_dependencies(tmp_path):
    parent = tmp_path / "parent.f90"
    child = tmp_path / "child.f90"
    parent.write_text(
        """
module parent_mod
  integer, parameter :: rk = 8
  interface
    module subroutine scale(x)
      real(kind=rk), intent(inout) :: x(:)
    end subroutine scale
  end interface
end module parent_mod
""",
        encoding="utf-8",
    )
    child.write_text(
        """
submodule (parent_mod) child_impl
contains
  module subroutine scale(x)
    real(kind=8), intent(inout) :: x(:)
  end subroutine scale
end submodule child_impl
""",
        encoding="utf-8",
    )

    namespace = parse_fortran_namespace(tmp_path)
    assert namespace["files"] == [str(parent), str(child)]
    assert namespace["file_dependencies"][str(child)] == [str(parent)]
    assert namespace["submodule_to_file"] == {"child_impl": str(child)}
    assert len(namespace["submodules"]) == 1
    submodule = namespace["submodules"][0]
    assert submodule.name == "child_impl"
    assert submodule.parent == "parent_mod"
    assert submodule.ancestor is None
    assert [p.name for p in submodule.procedures] == ["scale"]
    assert submodule.procedures[0].module == "child_impl"


def test_submodule_module_procedure_stub_and_additional_program_units():
    code = """
submodule (ancestor_mod:parent_impl) child_impl
  use iso_c_binding, only: c_int
  integer(kind=c_int) :: counter
contains
  module procedure reset_counter
  end procedure reset_counter
end submodule child_impl

program driver
  use ancestor_mod
  integer :: ierr
end program driver

block data init_data
  integer :: seed
end block data init_data
"""
    submodules = parse_fortran_submodules(code)
    assert len(submodules) == 1
    submodule = submodules[0]
    assert submodule.parent == "parent_impl"
    assert submodule.ancestor == "ancestor_mod"
    assert submodule.uses["iso_c_binding"] == ["c_int"]
    assert [v.name for v in submodule.variables] == ["counter"]
    assert [(p.name, p.kind) for p in submodule.procedures] == [("reset_counter", "module procedure")]

    programs = parse_fortran_programs(code)
    assert len(programs) == 1
    assert programs[0].name == "driver"
    assert programs[0].uses["ancestor_mod"] == []
    assert [v.name for v in programs[0].variables] == ["ierr"]

    block_data = parse_fortran_block_data(code)
    assert len(block_data) == 1
    assert block_data[0].name == "init_data"
    assert [v.name for v in block_data[0].variables] == ["seed"]

    readiness = assess_wrap_readiness(code)
    assert readiness["n_submodules"] == 1
    assert readiness["n_programs"] == 1
    assert readiness["n_block_data"] == 1


def test_procedure_dummy_declaration_tracks_local_interface_kind():
    code = """
subroutine caller(cb)
  procedure(local_cb) :: cb
end subroutine caller
"""
    sig = FortranParser().parse_file(code)[0]
    cb = next(a for a in sig.arguments if a.name == "cb")
    assert cb.base_type == "procedure"
    assert cb.kind == "local_cb"


def test_procedure_dummy_declaration_with_imported_interface_keeps_kind_unresolved():
    code = """
subroutine caller(cb)
  import :: ext_cb
  procedure(ext_cb) :: cb
end subroutine caller
"""
    sig = FortranParser().parse_file(code)[0]
    cb = next(a for a in sig.arguments if a.name == "cb")
    assert cb.base_type == "procedure"
    assert cb.kind is None


def test_parse_fortran_file_returns_file_model_for_source_string():
    code = """
module file_mod
contains
subroutine ping(x)
  integer, intent(in) :: x
end subroutine ping
end module file_mod
"""
    parsed = FortranParser().parse_file(code)
    assert parsed.filename is None
    assert [m.name for m in parsed.modules] == ["file_mod"]
    assert [p.name for p in parsed.modules[0].procedures] == ["ping"]


def test_parse_fortran_modules_rejects_standalone_procedure_entrypoint():
    code = """
subroutine lonely(x)
  integer, intent(in) :: x
end subroutine lonely
"""
    with pytest.raises(FortranParseError, match="expected a module"):
        FortranParser().parse_file(code)


def test_module_parser_ignores_procedure_local_variables():
    code = """
module no_leak
  integer :: module_value
contains
  subroutine worker(x)
    integer, intent(in) :: x
    real :: local_value
  end subroutine worker
end module no_leak
"""
    mod = FortranParser().parse_file(code)[0]
    assert [v.name for v in mod.variables] == ["module_value"]


def test_parse_fortran_project_returns_project_registry():
    project = FortranParser().parse_multiple_files({
        "a.f90": """
module a_mod
contains
subroutine step(x)
  integer, intent(in) :: x
end subroutine step
end module a_mod
""",
        "b.f90": """
subroutine free_proc(y)
  real, intent(in) :: y
end subroutine free_proc
""",
    })
    assert [f.filename for f in project.files] == ["a.f90", "b.f90"]
    assert "a_mod" in project.modules
    assert "a_mod.step" in project.procedures
    assert "free_proc" in project.procedures


def test_parse_fortran_file_preprocesses_source_once(monkeypatch):
    import fortran_parser.parser as parser_module

    calls = 0
    original = parser_module.preprocess_lines

    def counting_preprocess(code, filename=None):
        nonlocal calls
        calls += 1
        return original(code, filename)

    monkeypatch.setattr(parser_module, "preprocess_lines", counting_preprocess)
    parsed = parser_module.FortranParser().parse_file("""
module once_mod
contains
subroutine ping(x)
  integer, intent(in) :: x
end subroutine ping
end module once_mod
""")

    assert calls == 1
    assert parsed.modules[0].procedures[0].name == "ping"



def test_singular_parse_entrypoints_return_single_models():
    assert parse_fortran_signature("""
subroutine one(x)
  integer, intent(in) :: x
end subroutine one
""").name == "one"

    assert parse_fortran_module("""
module single_mod
end module single_mod
""").name == "single_mod"

    assert parse_fortran_derived_type("""
module type_mod
  type :: particle
    integer :: id
  end type particle
end module type_mod
""").name == "particle"

    assert parse_fortran_interface("""
module iface_mod
  interface apply
    subroutine do_apply(x)
      integer, intent(in) :: x
    end subroutine do_apply
  end interface
end module iface_mod
""").name == "apply"

    assert parse_fortran_program("""
program driver
  integer :: ierr
end program driver
""").name == "driver"

    assert parse_fortran_block_data_unit("""
block data init_data
  integer :: seed
end block data init_data
""").name == "init_data"

    assert parse_fortran_submodule("""
submodule (parent_mod) child_impl
end submodule child_impl
""").name == "child_impl"


def test_singular_parse_entrypoint_rejects_ambiguous_sources():
    with pytest.raises(FortranParseError, match="expected exactly one module"):
        parse_fortran_module("""
module first_mod
end module first_mod
module second_mod
end module second_mod
""")

    with pytest.raises(FortranParseError, match="expected exactly one procedure signature"):
        parse_fortran_signature("""
subroutine first()
end subroutine first
subroutine second()
end subroutine second
""")
