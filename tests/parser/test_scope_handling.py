import pytest

from fortran_parser import parse_fortran_signatures
from fortran_parser.models import FortranParseError


def test_same_argument_name_in_different_procedures_is_allowed():
    code = """
subroutine a(x)
  implicit none
  integer :: x
end subroutine a

subroutine b(x)
  implicit none
  real(8) :: x
end subroutine b
"""
    sigs = parse_fortran_signatures(code, filename="scope_args_ok.f90")
    assert [s.name for s in sigs] == ["a", "b"]


def test_interface_argument_names_do_not_conflict_with_host_locals():
    code = """
subroutine host(func, x)
  implicit none
  interface
     function func(x)
       real(8) :: x
       real(8) :: func
     end function func
  end interface
  real(8) :: x
end subroutine host
"""
    sigs = parse_fortran_signatures(code, filename="scope_interface_ok.f90")
    assert len(sigs) == 1
    assert sigs[0].name == "host"


def test_same_contained_procedure_name_in_different_hosts_is_allowed():
    code = """
module m
contains
  subroutine host_a()
  contains
    subroutine helper(y)
      integer :: y
    end subroutine helper
  end subroutine host_a

  subroutine host_b()
  contains
    subroutine helper(y)
      real(8) :: y
    end subroutine helper
  end subroutine host_b
end module m
"""
    sigs = parse_fortran_signatures(code, filename="scope_contains_ok.f90")
    assert [s.name.lower() for s in sigs] == ["host_a", "host_b"]


def test_duplicate_procedure_name_in_same_scope_still_errors():
    code = """
module m
contains
  subroutine work(n)
    integer :: n
  end subroutine work
  function work(n) result(out)
    integer :: n
    integer :: out
  end function work
end module m
"""
    with pytest.raises(FortranParseError, match="Duplicate procedure name"):
        parse_fortran_signatures(code, filename="scope_dup_err.f90")


def test_same_name_in_mutually_exclusive_ifdef_branches_is_allowed():
    code = """
module m
#ifdef USE_A
contains
  subroutine work(n)
    integer :: n
  end subroutine work
#else
contains
  function work(n) result(out)
    integer :: n
    integer :: out
  end function work
#endif
end module m
"""
    sigs = parse_fortran_signatures(code, filename="scope_ifdef_ok.f90")
    assert len(sigs) == 2


def test_same_name_in_overlapping_ifdef_branches_errors_when_both_active():
    code = """
module m
#ifdef USE_A
contains
  subroutine work(n)
    integer :: n
  end subroutine work
#endif
#ifdef USE_B
contains
  function work(n) result(out)
    integer :: n
    integer :: out
  end function work
#endif
end module m
"""
    with pytest.raises(FortranParseError, match="Duplicate procedure name"):
        parse_fortran_signatures(code, filename="scope_ifdef_overlap.f90", macro_defines={"USE_A", "USE_B"})


def test_fortran_parser_class_entrypoint():
    from fortran_parser import FortranParser

    source = """
subroutine touch(x)
    integer, intent(inout) :: x
end subroutine
"""

    signatures = FortranParser().parse_signatures(source)

    assert len(signatures) == 1
    assert signatures[0].name == "touch"
