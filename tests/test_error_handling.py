# -*- coding: utf-8 -*-
import pytest

from fortran_parser import (
    FortranParseError,
    parse_fortran_interfaces,
    parse_fortran_modules,
    parse_fortran_signatures,
    parse_fortran_types,
)


# ---------------------------------------------------------------------------
# FortranParseError attributes
# ---------------------------------------------------------------------------

def test_parse_error_carries_filename():
    code = """
subroutine bad(x)
  weirdtype :: x
end subroutine bad
"""
    with pytest.raises(FortranParseError) as exc_info:
        parse_fortran_signatures(code, filename="bad.f90")
    err = exc_info.value
    assert err.filename == "bad.f90"
    assert err.line_number is not None
    assert err.source_line is not None


def test_parse_error_message_includes_filename_and_lineno():
    code = """
subroutine bad(x)
  weirdtype :: x
end subroutine bad
"""
    with pytest.raises(FortranParseError) as exc_info:
        parse_fortran_signatures(code, filename="myfile.f90")
    msg = str(exc_info.value)
    assert "myfile.f90" in msg
    assert "line" in msg


def test_parse_error_message_includes_source_line():
    code = """
subroutine bad(x)
  weirdtype :: x
end subroutine bad
"""
    with pytest.raises(FortranParseError) as exc_info:
        parse_fortran_signatures(code, filename="myfile.f90")
    msg = str(exc_info.value)
    assert "weirdtype" in msg


def test_parse_error_without_filename_has_no_location_prefix():
    code = """
subroutine bad(x)
  weirdtype :: x
end subroutine bad
"""
    with pytest.raises(FortranParseError) as exc_info:
        parse_fortran_signatures(code)
    msg = str(exc_info.value)
    assert "Unknown or unsupported datatype" in msg


def test_parse_error_is_subclass_of_value_error():
    code = """
subroutine bad(x)
  weirdtype :: x
end subroutine bad
"""
    with pytest.raises(ValueError):
        parse_fortran_signatures(code, filename="bad.f90")


# ---------------------------------------------------------------------------
# Duplicate declaration errors
# ---------------------------------------------------------------------------

def test_duplicate_declaration_raises_parse_error():
    code = """
subroutine dup(x)
  real :: x
  integer :: x
end subroutine dup
"""
    with pytest.raises(FortranParseError, match="Duplicate declaration"):
        parse_fortran_signatures(code, filename="dup.f90")


def test_duplicate_function_result_raises_parse_error():
    code = """
real function f(x)
  real :: x
  real :: f
end function f
"""
    with pytest.raises(FortranParseError, match="Duplicate declaration"):
        parse_fortran_signatures(code, filename="dup_result.f90")


def test_duplicate_function_result_with_result_keyword_raises_parse_error():
    code = """
real function f(x) result(res)
  real :: x
  real :: res
end function f
"""
    with pytest.raises(FortranParseError, match="Duplicate declaration"):
        parse_fortran_signatures(code, filename="dup_result_kw.f90")


def test_duplicate_initialized_declaration_raises_parse_error():
    code = """
subroutine dup_init()
  integer :: x = 1
  integer :: x = 2
end subroutine dup_init
"""
    with pytest.raises(FortranParseError, match="Duplicate declaration"):
        parse_fortran_signatures(code, filename="dup_init.f90")


# ---------------------------------------------------------------------------
# Duplicate procedure name errors
# ---------------------------------------------------------------------------

def test_duplicate_procedure_name_global_scope_raises_parse_error():
    code = """
subroutine work(n)
  integer, intent(in) :: n
end subroutine work

function work(n) result(out)
  integer, intent(in) :: n
  integer :: out
end function work
"""
    with pytest.raises(FortranParseError, match="Duplicate procedure name"):
        parse_fortran_signatures(code, filename="dup_proc.f90")


def test_duplicate_procedure_name_in_module_raises_parse_error():
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
    with pytest.raises(FortranParseError, match="Duplicate procedure name"):
        parse_fortran_signatures(code, filename="dup_mod_proc.f90")


def test_duplicate_procedure_name_error_carries_location():
    code = """
subroutine work(n)
  integer, intent(in) :: n
end subroutine work

subroutine work(n)
  integer, intent(in) :: n
end subroutine work
"""
    with pytest.raises(FortranParseError) as exc_info:
        parse_fortran_signatures(code, filename="dup.f90")
    err = exc_info.value
    assert err.filename == "dup.f90"
    assert err.line_number is not None


# ---------------------------------------------------------------------------
# Star-kind errors
# ---------------------------------------------------------------------------

def test_star_kind_in_modern_source_raises_parse_error():
    code = """
subroutine bad(x)
  real*8 :: x
end subroutine bad
"""
    with pytest.raises(FortranParseError, match="star-kind"):
        parse_fortran_signatures(code, filename="bad.f90")


def test_star_kind_error_in_derived_type_field():
    code = """
module m
  type :: t
    real*8 :: x
  end type t
end module m
"""
    with pytest.raises(FortranParseError, match="star-kind"):
        parse_fortran_types(code, filename="bad.f90")


def test_star_kind_error_in_module_variable():
    code = """
module m
  real*8 :: x
end module m
"""
    with pytest.raises(FortranParseError, match="star-kind"):
        parse_fortran_modules(code, filename="bad.f90")


# ---------------------------------------------------------------------------
# Unknown/unsupported type declaration errors
# ---------------------------------------------------------------------------

def test_unknown_type_in_subroutine_raises_parse_error():
    code = """
subroutine bad(x)
  weirdtype :: x
end subroutine bad
"""
    with pytest.raises(FortranParseError, match="Unknown or unsupported datatype"):
        parse_fortran_signatures(code, filename="bad.f90")


def test_unknown_type_in_module_variable_raises_parse_error():
    code = """
module m
  weirdtype :: x
end module m
"""
    with pytest.raises(FortranParseError, match="Unknown or unsupported datatype"):
        parse_fortran_modules(code, filename="bad.f90")


def test_unknown_type_in_derived_type_field_raises_parse_error():
    code = """
module m
  type :: t
    weirdtype :: x
  end type t
end module m
"""
    with pytest.raises(FortranParseError, match="Unknown or unsupported datatype"):
        parse_fortran_types(code, filename="bad.f90")


def test_unknown_type_in_interface_raises_parse_error():
    code = """
module m
  interface foo
    subroutine bar(x)
      weirdtype :: x
    end subroutine bar
  end interface
end module m
"""
    with pytest.raises(FortranParseError, match="Unknown or unsupported datatype"):
        parse_fortran_interfaces(code, filename="bad.f90")


# ---------------------------------------------------------------------------
# Module variable type validation
# ---------------------------------------------------------------------------

def test_module_variable_with_unknown_type_raises_parse_error():
    code = """
module m
  integer :: n
end module m
"""
    modules = parse_fortran_modules(code)
    assert modules[0].variables[0].base_type == "integer"


def test_module_variable_parsed_correctly_no_error():
    code = """
module cfg
  real(kind=8) :: tolerance
  integer :: max_iter
  logical :: verbose
end module cfg
"""
    modules = parse_fortran_modules(code)
    assert len(modules[0].variables) == 3
    assert modules[0].variables[0].base_type == "real"
    assert modules[0].variables[1].base_type == "integer"
    assert modules[0].variables[2].base_type == "logical"


# ---------------------------------------------------------------------------
# Derived type field type validation
# ---------------------------------------------------------------------------

def test_derived_type_fields_have_known_types():
    code = """
module m
  type :: point
    real :: x
    real :: y
    integer :: id
  end type point
end module m
"""
    types = parse_fortran_types(code)
    for field in types[0].fields:
        assert field.base_type != "unknown"


# ---------------------------------------------------------------------------
# Parameter symbol errors
# ---------------------------------------------------------------------------

def test_parameter_without_type_in_implicit_none_scope_raises_parse_error():
    code = """
      subroutine cst(a)
      implicit none
      real a
      parameter ( zero = 0.0e+0 )
      end
"""
    with pytest.raises(FortranParseError, match="Unknown datatype for PARAMETER symbol"):
        parse_fortran_signatures(code, filename="legacy.f")


def test_duplicate_parameter_declaration_raises_parse_error():
    code = """
subroutine dup_param()
  integer, parameter :: n = 5
  integer, parameter :: n = 10
end subroutine dup_param
"""
    with pytest.raises(FortranParseError, match="Duplicate PARAMETER declaration"):
        parse_fortran_signatures(code, filename="dup_param.f90")


# ---------------------------------------------------------------------------
# Fortran 77 source form errors
# ---------------------------------------------------------------------------

def test_f77_source_with_module_keyword_raises_parse_error():
    code = """
      module bad_module
      end module bad_module
"""
    with pytest.raises(FortranParseError, match="Fortran 77"):
        parse_fortran_signatures(code, filename="legacy.f77")


def test_f77_source_error_carries_filename():
    code = """
      module bad_module
      end module bad_module
"""
    with pytest.raises(FortranParseError) as exc_info:
        parse_fortran_signatures(code, filename="legacy.f77")
    err = exc_info.value
    assert err.filename == "legacy.f77"


# ---------------------------------------------------------------------------
# Function result type errors
# ---------------------------------------------------------------------------

def test_function_with_implicit_none_and_missing_result_type_raises():
    code = """
function f(x) result(res)
  implicit none
  real :: x
end function f
"""
    with pytest.raises(FortranParseError, match="Unknown datatype for function result"):
        parse_fortran_signatures(code, filename="bad.f90")


# ---------------------------------------------------------------------------
# Error location accuracy
# ---------------------------------------------------------------------------

def test_error_reports_correct_line_number():
    code = "subroutine foo(x)\n  integer :: x\n  weirdtype :: y\nend subroutine foo\n"
    with pytest.raises(FortranParseError) as exc_info:
        parse_fortran_signatures(code, filename="foo.f90")
    err = exc_info.value
    assert err.line_number == 3


def test_error_reports_source_line_content():
    code = "subroutine foo(x)\n  integer :: x\n  weirdtype :: y\nend subroutine foo\n"
    with pytest.raises(FortranParseError) as exc_info:
        parse_fortran_signatures(code, filename="foo.f90")
    err = exc_info.value
    assert "weirdtype" in (err.source_line or "")
