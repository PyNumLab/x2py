import pytest

from fortran_parser import parse_fortran_file
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
    parsed = parse_fortran_file(code, filename="scope_args_ok.f90")
    assert [s.name for s in parsed.procedures] == ["a", "b"]


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
    parsed = parse_fortran_file(code, filename="scope_interface_ok.f90")
    assert len(parsed.procedures) == 1
    assert parsed.procedures[0].name == "host"


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
    parsed = parse_fortran_file(code, filename="scope_contains_ok.f90")
    module = parsed.modules[0]
    assert [s.name.lower() for s in module.procedures] == ["host_a", "host_b"]


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
        parse_fortran_file(code, filename="scope_dup_err.f90")


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
    parsed = parse_fortran_file(code, filename="scope_ifdef_ok.f90")
    module = parsed.modules[0]
    assert len(module.procedures) == 2


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
        parse_fortran_file(code, filename="scope_ifdef_overlap.f90", macro_defines={"USE_A", "USE_B"})


def test_module_symbol_tables_keep_derived_type_fields_scoped_to_type():
    code = """
module sparse_types
  implicit none

  type sf_sparse_dmatrix_coo
     integer,dimension(:),allocatable :: rows
     integer,dimension(:),allocatable :: cols
     real(8),dimension(:),allocatable :: vals
  end type sf_sparse_dmatrix_coo

  type sf_sparse_cmatrix_coo
     integer,dimension(:),allocatable :: rows
     integer,dimension(:),allocatable :: cols
     complex(8),dimension(:),allocatable :: vals
  end type sf_sparse_cmatrix_coo

  integer :: module_counter
end module sparse_types
"""
    parsed = parse_fortran_file(code, filename="scope_types_scoped.f90")
    module = parsed.modules[0]

    assert {v.name for v in module.variables} == {"module_counter"}
    assert set(parsed.symbols) == {"sparse_types"}
    assert [t.name for t in module.derived_types] == ["sf_sparse_dmatrix_coo", "sf_sparse_cmatrix_coo"]
    assert {f.name for f in module.derived_types[0].fields} == {"rows", "cols", "vals"}
    assert {f.name for f in module.derived_types[1].fields} == {"rows", "cols", "vals"}


def test_legacy_type_header_without_double_colon_is_scoped_as_derived_type():
    code = """
module legacy_type_header
  implicit none
  type sf_sparse_dmatrix_coo
     real(8),dimension(:),allocatable :: vals
  end type sf_sparse_dmatrix_coo
end module legacy_type_header
"""
    parsed = parse_fortran_file(code, filename="scope_legacy_type_header.f90")
    module = parsed.modules[0]

    assert list(module.variables) == []
    assert [t.name for t in module.derived_types] == ["sf_sparse_dmatrix_coo"]
    assert {f.name for f in module.derived_types[0].fields} == {"vals"}


def test_type_components_do_not_conflict_with_host_procedure_locals():
    code = """
module component_vs_local
  implicit none
  type :: box_t
     integer :: n
  end type box_t
contains
  subroutine touch()
    implicit none
    integer :: n
  end subroutine touch
end module component_vs_local
"""
    parsed = parse_fortran_file(code, filename="scope_component_local_ok.f90")
    module = parsed.modules[0]
    assert [s.name for s in module.procedures] == ["touch"]


def test_module_variable_and_type_component_same_name_is_allowed():
    code = """
module module_vs_component
  implicit none
  integer :: vals
  type :: payload
     integer :: vals
  end type payload
end module module_vs_component
"""
    parsed = parse_fortran_file(code, filename="scope_module_component_same_name_ok.f90")
    module = parsed.modules[0]

    assert {v.name for v in module.variables} == {"vals"}
    assert [t.name for t in module.derived_types] == ["payload"]
    assert {f.name for f in module.derived_types[0].fields} == {"vals"}


def test_type_component_names_do_not_leak_between_different_modules():
    code = """
module a_mod
  type :: t
     integer :: vals
  end type t
end module a_mod

module b_mod
  type :: t
     real(8) :: vals
  end type t
end module b_mod
"""
    parsed = parse_fortran_file(code, filename="scope_cross_module_components_ok.f90")
    assert [m.name for m in parsed.modules] == ["a_mod", "b_mod"]
    assert {f.name for f in parsed.modules[0].derived_types[0].fields} == {"vals"}
    assert {f.name for f in parsed.modules[1].derived_types[0].fields} == {"vals"}


def test_duplicate_type_component_name_still_errors_inside_single_type_scope():
    code = """
module dup_component_mod
  implicit none
  type :: thing
    integer :: vals
    real(8) :: vals
  end type thing
end module dup_component_mod
"""
    with pytest.raises(FortranParseError, match="Duplicate field 'vals' in derived type 'thing'"):
        parse_fortran_file(code, filename="scope_component_dup_err.f90")


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
