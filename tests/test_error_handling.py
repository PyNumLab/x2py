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
# Existing semantic/error regression tests
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


def test_duplicate_declaration_raises_parse_error():
    code = """
subroutine dup(x)
  real :: x
  integer :: x
end subroutine dup
"""
    with pytest.raises(FortranParseError, match="Duplicate declaration"):
        parse_fortran_signatures(code, filename="dup.f90")


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


def test_star_kind_in_modern_source_raises_parse_error():
    code = """
subroutine bad(x)
  real*8 :: x
end subroutine bad
"""
    with pytest.raises(FortranParseError, match="star-kind"):
        parse_fortran_signatures(code, filename="bad.f90")


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


def test_f77_source_with_module_keyword_raises_parse_error():
    code = """
      module bad_module
      end module bad_module
"""
    with pytest.raises(FortranParseError, match="Fortran 77"):
        parse_fortran_signatures(code, filename="legacy.f77")


def test_function_result_shadowing_arg_name_raises_parse_error():
    code = """
function f(res) result(res)
  integer, intent(in) :: res
end function f
"""
    with pytest.raises(FortranParseError, match="shadows an argument name"):
        parse_fortran_signatures(code, filename="shadow.f90")


def test_duplicate_field_in_derived_type_raises_parse_error():
    code = """
module m
  type :: point
    real :: x
    integer :: x
  end type point
end module m
"""
    with pytest.raises(FortranParseError, match="Duplicate field"):
        parse_fortran_types(code, filename="dup_field.f90")


# ---------------------------------------------------------------------------
# New diagnostic formatting tests
# ---------------------------------------------------------------------------

def _make_error():
    code = """
subroutine dgemm_wrap(a, b, c)
  implicit none
  real(kind=8), intent(in) :: a(:,:), b(:,:)
  weirdtype :: c
end subroutine dgemm_wrap
"""
    with pytest.raises(FortranParseError) as exc_info:
        parse_fortran_signatures(code, filename="blas_wrapper.f90")
    return exc_info.value


def test_error_message_contains_diagnostic_code():
    err = _make_error()
    assert "error[PARSE001]" in str(err)


def test_error_message_contains_location_arrow():
    err = _make_error()
    assert "--> blas_wrapper.f90:4" in str(err)


def test_error_message_contains_source_context():
    err = _make_error()
    assert "weirdtype :: c" in str(err)


def test_error_debug_mode_shows_internal_location():
    err = _make_error()
    msg = err.format(debug=True)
    assert "[internal]" in msg
    assert "in " in msg


def test_error_env_debug_mode(monkeypatch):
    monkeypatch.setenv("X2PY_DEBUG_ERRORS", "1")
    err = _make_error()
    assert "[internal]" in err.format()


def test_error_color_mode_does_not_crash():
    err = _make_error()
    assert isinstance(err.format(color=True), str)


def test_realistic_f77_diagnostic_context():
    code = """
      SUBROUTINE TEST(X)
      IMPLICIT NONE
      REAL*8 X
      WEIRDTYPE Y
      END
"""
    with pytest.raises(FortranParseError) as exc_info:
        parse_fortran_signatures(code, filename="legacy_blas.f")

    msg = str(exc_info.value)

    assert "legacy_blas.f" in msg
    assert "WEIRDTYPE Y" in msg


def test_realistic_module_diagnostic_context():
    code = """
module mesh_types
  type :: node
     integer :: id
     weirdtype :: coord
  end type node
end module mesh_types
"""
    with pytest.raises(FortranParseError) as exc_info:
        parse_fortran_types(code, filename="mesh_types.f90")

    msg = str(exc_info.value)

    assert "mesh_types.f90" in msg
    assert "weirdtype :: coord" in msg
