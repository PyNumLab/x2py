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
    assert "line" in msg or "-->" in msg


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

# Existing tests preserved from main...


# ---------------------------------------------------------------------------
# Diagnostic formatting tests
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


def test_error_debug_mode_shows_internal_location():
    err = _make_error()
    msg = err.format(debug=True)
    assert "[internal]" in msg


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
