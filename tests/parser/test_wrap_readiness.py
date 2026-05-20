# -*- coding: utf-8 -*-
"""Wrap-readiness decisions and blocker reporting."""

from x2py import assess_wrap_readiness

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
