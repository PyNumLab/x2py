import gc
import importlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest

from tests.wrapper.fmath_cases import fmath_cases


SCALAR_LEGACY_SOURCE = Path(__file__).with_name("fmath.f")
ARRAY_LEGACY_SOURCE = Path(__file__).with_name("fmath_arrays.f")
SCALAR_F90_SOURCE = Path(__file__).with_name("fmath_f90.f90")
ARRAY_F90_SOURCE = Path(__file__).with_name("fmath_arrays_f90.f90")
STRING_LEGACY_SOURCE = Path(__file__).with_name("fstrings.f")
STRING_F90_SOURCE = Path(__file__).with_name("fstrings_f90.f90")
CLASS_F90_SOURCE = Path(__file__).with_name("fclasses_f90.f90")
OVERLOAD_F90_SOURCE = Path(__file__).with_name("foverloads_f90.f90")
OVERLOAD_FIXED_SOURCE = Path(__file__).with_name("foverloads_fixed.f")
OPERATOR_F90_SOURCE = Path(__file__).with_name("foperators_f90.f90")
ALLOCATABLE_VIEW_F90_SOURCE = Path(__file__).with_name("fallocatable_views_f90.f90")
OUTPUTS_F90_SOURCE = Path(__file__).with_name("foutputs_f90.f90")


SCALAR_KINDS_F90_TEXT = """
module fscalar_kinds_f90
  use iso_fortran_env, only: int8, int16, int32, int64, real32, real64
  use iso_c_binding, only: c_bool, c_int32_t, c_float, c_double, c_float_complex, c_double_complex
  implicit none
contains
  integer(int8) function id_i8(value) result(out)
    integer(int8), intent(in) :: value

    out = value
  end function id_i8

  integer(int16) function id_i16(value) result(out)
    integer(int16), intent(in) :: value

    out = value
  end function id_i16

  integer(int32) function id_i32(value) result(out)
    integer(int32), intent(in) :: value

    out = value
  end function id_i32

  integer(int64) function id_i64(value) result(out)
    integer(int64), intent(in) :: value

    out = value
  end function id_i64

  subroutine copy_i16(n, values, out)
    integer, intent(in) :: n
    integer(int16), intent(in) :: values(n)
    integer(int16), intent(out) :: out(n)

    out = values
  end subroutine copy_i16

  logical(c_bool) function not_flag(value) result(out)
    logical(c_bool), intent(in) :: value

    out = .not. value
  end function not_flag

  subroutine invert_flags(n, values, out)
    integer, intent(in) :: n
    logical(c_bool), intent(in) :: values(n)
    logical(c_bool), intent(out) :: out(n)

    out = .not. values
  end subroutine invert_flags

  real(real32) function id_r32(value) result(out)
    real(real32), intent(in) :: value

    out = value
  end function id_r32

  real(real64) function id_r64(value) result(out)
    real(real64), intent(in) :: value

    out = value
  end function id_r64

  subroutine copy_r64(n, values, out)
    integer, intent(in) :: n
    real(real64), intent(in) :: values(n)
    real(real64), intent(out) :: out(n)

    out = values
  end subroutine copy_r64

  complex(real32) function conj_c64(value) result(out)
    complex(real32), intent(in) :: value

    out = conjg(value)
  end function conj_c64

  complex(real64) function shift_c128(value) result(out)
    complex(real64), intent(in) :: value

    out = value + cmplx(1.0_real64, -2.0_real64, kind=real64)
  end function shift_c128

  subroutine copy_c128(n, values, out)
    integer, intent(in) :: n
    complex(real64), intent(in) :: values(n)
    complex(real64), intent(out) :: out(n)

    out = values
  end subroutine copy_c128

  integer(c_int32_t) function id_c_i32(value) result(out)
    integer(c_int32_t), intent(in) :: value

    out = value
  end function id_c_i32

  real(c_float) function id_c_float(value) result(out)
    real(c_float), intent(in) :: value

    out = value
  end function id_c_float

  real(c_double) function id_c_double(value) result(out)
    real(c_double), intent(in) :: value

    out = value
  end function id_c_double

  complex(c_float_complex) function conj_c_float_complex(value) result(out)
    complex(c_float_complex), intent(in) :: value

    out = conjg(value)
  end function conj_c_float_complex

  complex(c_double_complex) function conj_c_double_complex(value) result(out)
    complex(c_double_complex), intent(in) :: value

    out = conjg(value)
  end function conj_c_double_complex
end module fscalar_kinds_f90
"""


NAMING_F90_TEXT = """
module fnaming_f90
  implicit none
  private
  public :: lambda, lambda_, get_value, value, visible_t

  integer :: value = 7

  type :: hidden_t
    integer :: value = 99
  end type hidden_t

  type :: visible_t
    integer :: lambda = 3
    integer :: lambda_ = 4
  contains
    procedure, public :: from => visible_from
    procedure, private :: hidden => visible_hidden
  end type visible_t

contains
  integer function lambda(value) result(out)
    integer, intent(in) :: value

    out = value + 1
  end function lambda

  integer function lambda_(value) result(out)
    integer, intent(in) :: value

    out = value + 2
  end function lambda_

  integer function get_value() result(out)
    out = 100
  end function get_value

  integer function visible_from(self) result(out)
    class(visible_t), intent(in) :: self

    out = self%lambda + self%lambda_
  end function visible_from

  integer function visible_hidden(self) result(out)
    class(visible_t), intent(in) :: self

    out = -1
  end function visible_hidden

  integer function hidden_proc() result(out)
    out = -10
  end function hidden_proc
end module fnaming_f90
"""


POINTERS_F90_TEXT = """
module fpointers_f90
contains
  real(8) function read_pointer(value)
    real(8), pointer, intent(in) :: value

    read_pointer = value
  end function read_pointer

  function pointer_to_scalar(value, use_value) result(selected)
    real(8), target, intent(in) :: value
    integer, intent(in) :: use_value
    real(8), pointer :: selected

    if (use_value /= 0) then
      selected => value
    else
      nullify(selected)
    end if
  end function pointer_to_scalar

  real(8) function sum_pointer(values)
    real(8), pointer, intent(in) :: values(:)
    integer :: i

    sum_pointer = 0.0_8
    do i = 1, size(values)
      sum_pointer = sum_pointer + values(i)
    end do
  end function sum_pointer

  function pointer_to_values(values, use_values) result(selected)
    real(8), target, intent(in) :: values(:)
    integer, intent(in) :: use_values
    real(8), pointer :: selected(:)

    if (use_values /= 0) then
      selected => values
    else
      nullify(selected)
    end if
  end function pointer_to_values
end module fpointers_f90
"""


BIND_VALUE_F90_TEXT = """
module fbind_value_f90
  use iso_c_binding
contains
  integer(c_int) function plus_value(n) bind(C, name="x2py_plus_value") result(res)
    integer(c_int), value, intent(in) :: n

    res = n + 7_c_int
  end function plus_value

  integer(c_int) function double_value(n) bind(C) result(res)
    integer(c_int), value, intent(in) :: n

    res = n * 2_c_int
  end function double_value

  integer(c_int) function plus_reference(n) bind(C) result(res)
    integer(c_int), intent(in) :: n

    res = n + 11_c_int
  end function plus_reference

  real(c_double) function scale_real(x) bind(C, name="x2py_scale_real") result(res)
    real(c_double), value, intent(in) :: x

    res = 2.5_c_double * x
  end function scale_real

  complex(c_double_complex) function conjugate_value(z) bind(C, name="x2py_conjugate_value") result(res)
    complex(c_double_complex), value, intent(in) :: z

    res = conjg(z)
  end function conjugate_value

  logical(c_bool) function invert_flag(flag) bind(C, name="x2py_invert_flag") result(res)
    logical(c_bool), value, intent(in) :: flag

    res = .not. flag
  end function invert_flag

  integer(c_int) function char_code(ch) bind(C) result(res)
    character(kind=c_char), value, intent(in) :: ch

    res = iachar(ch, c_int)
  end function char_code
end module fbind_value_f90
"""


ALLOCATABLE_INOUT_F90_TEXT = """
module fallocatable_inout_f90
contains
  subroutine replace_values(values, mode)
    real(8), allocatable, intent(inout) :: values(:)
    integer, intent(in) :: mode
    integer :: i

    if (mode == 0) then
      if (allocated(values)) deallocate(values)
    else if (mode == 1) then
      if (allocated(values)) then
        values = values + 10.0_8
      else
        allocate(values(2))
        values = [1.0_8, 2.0_8]
      end if
    else
      if (allocated(values)) deallocate(values)
      allocate(values(3))
      do i = 1, 3
        values(i) = real(i * mode, 8)
      end do
    end if
  end subroutine replace_values
end module fallocatable_inout_f90
"""


OPTIONAL_F90_TEXT = """
module foptional_f90
  implicit none

  type :: sample
    integer :: value
  end type sample

contains
  integer function summarize(required, scale, values, label, item)
    integer, intent(in) :: required
    integer, intent(in), optional :: scale
    real(8), intent(in), optional :: values(:)
    character(len=*), intent(in), optional :: label
    type(sample), intent(in), optional :: item

    summarize = required
    if (present(scale)) summarize = summarize + scale
    if (present(values)) summarize = summarize + int(sum(values))
    if (present(label)) summarize = summarize + len_trim(label)
    if (present(item)) summarize = summarize + item%value
  end function summarize

  subroutine mutate_optional(values, amount)
    real(8), intent(inout), optional :: values(:)
    real(8), intent(in), optional :: amount

    if (present(values)) then
      if (present(amount)) then
        values = values + amount
      else
        values = values + 1.0_8
      end if
    end if
  end subroutine mutate_optional

  subroutine fill_optional(n, values)
    integer, intent(in) :: n
    real(8), intent(out), optional :: values(:)
    integer :: i

    if (present(values)) then
      do i = 1, n
        values(i) = 10.0_8 + real(i, 8)
      end do
    end if
  end subroutine fill_optional

  integer function optional_status(base, status)
    integer, intent(in) :: base
    integer, intent(out), optional :: status

    optional_status = base
    if (present(status)) status = base + 50
  end function optional_status
end module foptional_f90
"""


OPTIONAL_FIXED_TEXT = """
      integer function optional_scale(base, factor)
      integer, intent(in) :: base
      integer, intent(in), optional :: factor
      optional_scale = base
      if (present(factor)) optional_scale = optional_scale + factor
      end function optional_scale
"""


CHARACTER_EDGES_F90_TEXT = """
module fcharacter_edges_f90
  implicit none
contains
  subroutine fixed_inout(name)
    character(len=8), intent(inout) :: name

    name(1:1) = 'Z'
    name(8:8) = '!'
  end subroutine fixed_inout

  subroutine assumed_inout(name)
    character(len=*), intent(inout) :: name

    if (len(name) > 0) name(1:1) = 'Q'
  end subroutine assumed_inout

  subroutine optional_inout(label)
    character(len=*), intent(inout), optional :: label

    if (present(label)) then
      if (len(label) > 0) label(1:1) = 'P'
    end if
  end subroutine optional_inout

  subroutine make_out(label)
    character(len=6), intent(out) :: label

    label = 'go'
  end subroutine make_out

  character(len=5) function unicode_echo(label) result(out)
    character(len=*), intent(in) :: label

    out = label
  end function unicode_echo
end module fcharacter_edges_f90
"""


CONSTRUCTOR_F90_TEXT = """
module fconstructors_f90
  implicit none
  private
  public :: initialized, get_final_count, reset_final_count

  integer :: final_count = 0

  type :: initialized
    integer :: id = 7
    real(8) :: scale = 2.5
  contains
    final :: cleanup_initialized
  end type initialized

contains
  subroutine cleanup_initialized(self)
    type(initialized) :: self

    final_count = final_count + 1
  end subroutine cleanup_initialized

  integer function get_final_count()
    get_final_count = final_count
  end function get_final_count

  subroutine reset_final_count()
    final_count = 0
  end subroutine reset_final_count
end module fconstructors_f90
"""


BORROWED_FINALIZER_F90_TEXT = """
module fborrowed_finalizer_f90
  implicit none
  private
  public :: child, parent, get_final_count, reset_final_count

  integer :: final_count = 0

  type :: child
  contains
    final :: cleanup_child
  end type child

  type :: parent
    type(child) :: value
  end type parent

contains
  subroutine cleanup_child(self)
    type(child) :: self

    final_count = final_count + 1
  end subroutine cleanup_child

  integer function get_final_count()
    get_final_count = final_count
  end function get_final_count

  subroutine reset_final_count()
    final_count = 0
  end subroutine reset_final_count
end module fborrowed_finalizer_f90
"""


MODULE_VARIABLES_F90_TEXT = """
module fmodule_vars_f90
  use iso_c_binding
  implicit none
  private
  public :: nmax, counter, scale, saved_counter
  public :: red, blue, green, yellow, summarize, scaled_counter, next_local

  integer(c_int), parameter :: nmax = 12
  enum, bind(C)
    enumerator :: red = -1, blue, green = 10, yellow
  end enum
  integer(c_int) :: counter = 3
  real(c_double) :: scale = 1.5d0
  integer(c_int), save :: saved_counter = 6
  integer(c_int) :: hidden_counter = 17

contains
  integer(c_int) function summarize() result(value)
    value = counter + nmax
  end function summarize

  real(c_double) function scaled_counter() result(value)
    value = real(counter, c_double) * scale
  end function scaled_counter

  integer(c_int) function next_local() result(value)
    integer(c_int), save :: local_counter = 0

    local_counter = local_counter + 1
    value = local_counter
  end function next_local
end module fmodule_vars_f90
"""


COMMON_BLOCK_F90_TEXT = """
module fcommon_block_f90
  use iso_c_binding
  implicit none
  public :: shared_value, write_shared, read_shared

  integer(c_int) :: shared_value
  common /shared_state/ shared_value

contains
  subroutine write_shared(value)
    integer(c_int), intent(in) :: value

    shared_value = value
  end subroutine write_shared

  integer(c_int) function read_shared() result(value)
    value = shared_value
  end function read_shared
end module fcommon_block_f90
"""


BIND_C_DERIVED_LAYOUT_F90_TEXT = """
module fbind_c_derived_layout_f90
  use iso_c_binding
  implicit none
  private
  public :: point, tagged_point, populate, score_by_value

  type, bind(C) :: point
    real(c_double) :: x
    integer(c_int) :: axis
  end type point

  type, bind(C) :: tagged_point
    type(point) :: position
    complex(c_double_complex) :: weight
  end type tagged_point

contains
  subroutine populate(value, x, axis, weight) bind(C)
    type(tagged_point), intent(inout) :: value
    real(c_double), value, intent(in) :: x
    integer(c_int), value, intent(in) :: axis
    complex(c_double_complex), value, intent(in) :: weight

    value%position%x = x
    value%position%axis = axis
    value%weight = weight
  end subroutine populate

  real(c_double) function score_by_value(value) result(score) bind(C)
    type(tagged_point), value :: value

    value%position%x = value%position%x + 100.0_c_double
    score = value%position%x + real(value%position%axis, c_double) + real(value%weight, c_double)
  end function score_by_value
end module fbind_c_derived_layout_f90
"""


_MAX_WRAPPER_TEST_RANK = 15


def _rank_shape_spec(rank: int) -> str:
    return ", ".join(["2", *(["1"] * (rank - 1))])


def _rank_index_spec(rank: int, first_axis_index: int) -> str:
    return ", ".join([str(first_axis_index), *(["1"] * (rank - 1))])


def _colon_shape_spec(rank: int) -> str:
    return ", ".join([":"] * rank)


def _rank_result_functions() -> str:
    functions = []
    for rank in range(1, _MAX_WRAPPER_TEST_RANK + 1):
        shape = _rank_shape_spec(rank)
        second_value_index = _rank_index_spec(rank, 2)
        functions.append(
            f"""
  function rank{rank}_result() result(values)
    real(8) :: values({shape})

    values = real({rank}, 8)
    values({second_value_index}) = real({rank}, 8) + 0.5_8
  end function rank{rank}_result
"""
        )
    return "".join(functions)


def _rank_contract_subroutines() -> str:
    subroutines = []
    for rank in range(1, _MAX_WRAPPER_TEST_RANK + 1):
        shape = _colon_shape_spec(rank)
        subroutines.append(
            f"""
  subroutine shift{rank}(values, out)
    real(8), intent(in) :: values({shape})
    real(8), intent(out) :: out({shape})

    out = values + {rank}.0_8
  end subroutine shift{rank}
"""
        )
    return "".join(subroutines)


def _assumed_rank_sum_cases() -> str:
    cases = []
    for rank in range(1, _MAX_WRAPPER_TEST_RANK + 1):
        cases.append(
            f"""
    rank({rank})
      total = real({rank}, 8) + sum(values)
"""
        )
    return "".join(cases)


def _assumed_rank_bump_cases() -> str:
    cases = []
    for rank in range(1, _MAX_WRAPPER_TEST_RANK + 1):
        cases.append(
            f"""
    rank({rank})
      values = values + real({rank}, 8)
"""
        )
    return "".join(cases)


def _assumed_rank_score_cases(name: str, factor: int) -> str:
    cases = []
    for rank in range(1, _MAX_WRAPPER_TEST_RANK + 1):
        cases.append(
            f"""
    rank({rank})
      score = score + {factor * rank} + int(sum({name}))
"""
        )
    return "".join(cases)


ARRAY_RESULTS_F90_TEXT = (
    """
module farray_results_f90
contains
  function fixed_vector() result(values)
    real(8) :: values(3)

    values = [1.0_8, 2.0_8, 3.0_8]
  end function fixed_vector

  function automatic_vector(n) result(values)
    integer, intent(in) :: n
    real(8) :: values(n)
    integer :: i

    do i = 1, n
      values(i) = real(i, 8) * 2.0_8
    end do
  end function automatic_vector

  function automatic_matrix(rows, cols) result(values)
    integer, intent(in) :: rows
    integer, intent(in) :: cols
    real(8) :: values(0:rows - 1, 2:cols + 1)
    integer :: i
    integer :: j

    do j = 2, cols + 1
      do i = 0, rows - 1
        values(i, j) = real(10 * (i + 1) + j, 8)
      end do
    end do
  end function automatic_matrix

  function rank3_cube(n1, n2, n3) result(values)
    integer, intent(in) :: n1
    integer, intent(in) :: n2
    integer, intent(in) :: n3
    real(8) :: values(n1, n2, n3)
    integer :: i
    integer :: j
    integer :: k

    do k = 1, n3
      do j = 1, n2
        do i = 1, n1
          values(i, j, k) = real(100 * i + 10 * j + k, 8)
        end do
      end do
    end do
  end function rank3_cube
"""
    + _rank_result_functions()
    + """

  function zero_vector() result(values)
    real(8) :: values(0)
  end function zero_vector

  function zero_alloc_vector() result(values)
    real(8), allocatable :: values(:)

    allocate(values(0))
  end function zero_alloc_vector

  function maybe_alloc_vector(n) result(values)
    integer, intent(in) :: n
    real(8), allocatable :: values(:)
    integer :: i

    if (n > 0) then
      allocate(values(n))
      do i = 1, n
        values(i) = real(5 * i, 8)
      end do
    end if
  end function maybe_alloc_vector
end module farray_results_f90
"""
)


ARRAY_CONTRACTS_F90_TEXT = (
    """
module farray_contracts_f90
contains
  real(8) function sum_assumed_size(n, values) result(total)
    integer, intent(in) :: n
    real(8), intent(in) :: values(*)
    integer :: i

    total = 0.0_8
    do i = 1, n
      total = total + values(i)
    end do
  end function sum_assumed_size

  subroutine scale_lower(n, values)
    integer, intent(in) :: n
    real(8), intent(inout) :: values(0:n - 1)

    values = values * 2.0_8
  end subroutine scale_lower

  real(8) function sum_in(values) result(total)
    real(8), intent(in) :: values(:)

    total = sum(values)
  end function sum_in

  subroutine bump_inout(values)
    real(8), intent(inout) :: values(:)

    values = values + 1.0_8
  end subroutine bump_inout

  subroutine fill_out(values)
    real(8), intent(out) :: values(:)

    values = 7.0_8
  end subroutine fill_out
"""
    + _rank_contract_subroutines()
    + """
end module farray_contracts_f90
"""
)


ASSUMED_RANK_F90_TEXT = (
    """
module fassumed_rank_f90
contains
  real(8) function rank_weighted_sum(values) result(total)
    real(8), intent(in) :: values(..)

    total = -1.0_8
    select rank(values)
"""
    + _assumed_rank_sum_cases()
    + """
    rank default
      total = -99.0_8
    end select
  end function rank_weighted_sum

  subroutine bump_assumed_rank(values)
    real(8), intent(inout) :: values(..)

    select rank(values)
"""
    + _assumed_rank_bump_cases()
    + """
    rank default
      return
    end select
  end subroutine bump_assumed_rank

  integer function rank_pair_score(left, right) result(score)
    real(8), intent(in) :: left(..)
    real(8), intent(in) :: right(..)

    score = 0
    select rank(left)
"""
    + _assumed_rank_score_cases("left", 100)
    + """
    rank default
      score = score - 100000
    end select

    select rank(right)
"""
    + _assumed_rank_score_cases("right", 1)
    + """
    rank default
      score = score - 100000
    end select
  end function rank_pair_score
end module fassumed_rank_f90
"""
)


DERIVED_BOUNDARY_F90_TEXT = """
module fderived_boundary_f90
  implicit none

  type :: point
    real(8) :: x
    real(8) :: y
    real(8), private :: hidden
  end type point

  type :: holder
    type(point) :: origin
    real(8) :: scale
  end type holder
contains
  real(8) function point_sum(p) result(total)
    type(point), intent(in) :: p

    total = p%x + p%y
  end function point_sum

  subroutine move_point(p, dx, dy)
    type(point), intent(inout) :: p
    real(8), intent(in) :: dx
    real(8), intent(in) :: dy

    p%x = p%x + dx
    p%y = p%y + dy
  end subroutine move_point

  subroutine make_point_out(p, x, y)
    type(point), intent(out) :: p
    real(8), intent(in) :: x
    real(8), intent(in) :: y

    p%x = x
    p%y = y
    p%hidden = 99.0_8
  end subroutine make_point_out

  type(point) function make_point(x, y) result(p)
    real(8), intent(in) :: x
    real(8), intent(in) :: y

    p%x = x
    p%y = y
    p%hidden = 123.0_8
  end function make_point

  subroutine set_holder_origin(h, p)
    type(holder), intent(inout) :: h
    type(point), intent(in) :: p

    h%origin = p
  end subroutine set_holder_origin

  real(8) function holder_origin_x(h) result(value)
    type(holder), intent(in) :: h

    value = h%origin%x
  end function holder_origin_x
end module fderived_boundary_f90
"""


INHERITANCE_F90_TEXT = """
module finheritance_f90
  implicit none

  type :: base_shape
    real(8) :: size
  contains
    procedure :: area => base_area
    procedure :: set_size => base_set_size
  end type base_shape

  type, extends(base_shape) :: circle
    real(8) :: radius
  contains
    procedure :: area => circle_area
  end type circle

  type, extends(base_shape) :: box
    real(8) :: width
  contains
    procedure :: area => box_area
  end type box
contains
  real(8) function base_area(self) result(value)
    class(base_shape), intent(in) :: self

    value = self%size
  end function base_area

  subroutine base_set_size(self, value)
    class(base_shape), intent(inout) :: self
    real(8), intent(in) :: value

    self%size = value
  end subroutine base_set_size

  real(8) function circle_area(self) result(value)
    class(circle), intent(in) :: self

    value = self%size + self%radius * self%radius
  end function circle_area

  real(8) function box_area(self) result(value)
    class(box), intent(in) :: self

    value = self%size + 10.0_8 * self%width
  end function box_area

  real(8) function describe_shape(item) result(value)
    class(base_shape), intent(in) :: item

    value = item%area()
  end function describe_shape
end module finheritance_f90
"""


CALLBACK_SCALAR_F90_TEXT = """
module fcallback_scalar_f90
  implicit none

  abstract interface
    real(8) function scalar_callback(value) result(output)
      real(8), intent(in) :: value
    end function scalar_callback
    subroutine notify_callback(value)
      real(8), intent(in) :: value
    end subroutine notify_callback
  end interface

contains
  real(8) function apply_scalar(callback, value) result(output)
    procedure(scalar_callback) :: callback
    real(8), intent(in) :: value

    output = callback(value)
  end function apply_scalar

  real(8) function apply_explicit(callback, value) result(output)
    interface
      real(8) function callback(value) result(callback_output)
        real(8), intent(in) :: value
      end function callback
    end interface
    real(8), intent(in) :: value

    output = callback(value)
  end function apply_explicit

  subroutine call_notify(callback, value)
    procedure(notify_callback) :: callback
    real(8), intent(in) :: value

    call callback(value)
  end subroutine call_notify
end module fcallback_scalar_f90
"""


CALLBACK_ARRAY_F90_TEXT = """
module fcallback_array_f90
  implicit none

  abstract interface
    real(8) function reduce_callback(count, values) result(output)
      integer, intent(in) :: count
      real(8), intent(in) :: values(count)
    end function reduce_callback

    function transform_callback(count, values) result(output)
      integer, intent(in) :: count
      real(8), intent(in) :: values(count)
      real(8) :: output(count)
    end function transform_callback
  end interface

contains
  real(8) function apply_reduce(callback, count, values) result(output)
    procedure(reduce_callback) :: callback
    integer, intent(in) :: count
    real(8), intent(in) :: values(count)

    output = callback(count, values)
  end function apply_reduce

  subroutine apply_transform(callback, count, values, output)
    procedure(transform_callback) :: callback
    integer, intent(in) :: count
    real(8), intent(in) :: values(count)
    real(8), intent(out) :: output(count)

    output = callback(count, values)
  end subroutine apply_transform
end module fcallback_array_f90
"""


CALLBACK_DERIVED_F90_TEXT = """
module fcallback_derived_f90
  implicit none

  type :: point_t
    real(8) :: x
    real(8) :: y
  end type point_t

  abstract interface
    function point_callback(value) result(output)
      import :: point_t
      type(point_t), intent(in) :: value
      type(point_t) :: output
    end function point_callback
  end interface

contains
  subroutine apply_point(callback, value, output)
    procedure(point_callback) :: callback
    type(point_t), intent(in) :: value
    type(point_t), intent(out) :: output

    output = callback(value)
  end subroutine apply_point
end module fcallback_derived_f90
"""


def _assert_fmath_examples(module):
    cases = fmath_cases()
    missing = sorted(name.lower() for name, _, _ in cases if not hasattr(module, name.lower()))
    assert missing == []

    for name, args, expected in cases:
        public_name = name.lower()
        actual = getattr(module, public_name)(*args)
        if isinstance(expected, bool):
            assert bool(actual) is expected, public_name
        elif isinstance(expected, int):
            assert actual == expected, public_name
        else:
            np.testing.assert_allclose(actual, expected, rtol=1e-6, atol=1e-6, err_msg=public_name)


def _build_and_import(source_template: Path, workdir: Path, expected_generated_sources: set[str]):
    source = workdir / source_template.name
    module_name = source_template.stem
    shutil.copyfile(source_template, source)

    cmd = [
        sys.executable,
        "-m",
        "x2py",
        str(source),
        "--out-dir",
        str(workdir),
        "--json",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)

    shared_library = Path(payload["shared_library"])
    assert shared_library.exists()
    assert Path(payload["output_dir"]) == workdir
    assert shared_library.parent == workdir
    assert {Path(path).name for path in payload["generated_sources"]} == expected_generated_sources
    generated_files = [Path(path) for path in payload["generated_files"]]
    assert any(path.name == "python_runtime.c" and path.parent.name == "x2py_runtime" for path in generated_files)

    sys.modules.pop(module_name, None)
    sys.path.insert(0, str(workdir))
    try:
        return importlib.import_module(module_name)
    finally:
        sys.path.remove(str(workdir))


def _build_text_and_import(source_text: str, filename: str, workdir: Path, expected_generated_sources: set[str]):
    source = workdir / filename
    source.write_text(source_text, encoding="utf-8")
    module_name = source.stem

    cmd = [
        sys.executable,
        "-m",
        "x2py",
        str(source),
        "--out-dir",
        str(workdir),
        "--json",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)

    shared_library = Path(payload["shared_library"])
    assert shared_library.exists()
    assert {Path(path).name for path in payload["generated_sources"]} == expected_generated_sources

    sys.modules.pop(module_name, None)
    sys.path.insert(0, str(workdir))
    try:
        return importlib.import_module(module_name)
    finally:
        sys.path.remove(str(workdir))


def _build_sources_and_import(source_texts: list[tuple[str, str]], workdir: Path):
    sources = []
    for filename, source_text in source_texts:
        source = workdir / filename
        source.write_text(source_text, encoding="utf-8")
        sources.append(source)

    cmd = [
        sys.executable,
        "-m",
        "x2py",
        *(str(source) for source in sources),
        "--wrap",
        "--out-dir",
        str(workdir),
        "--json",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)
    module_name = payload["module_name"]

    assert payload["sources"] == [str(source) for source in sources]
    assert payload["compiled"] is True
    assert payload["build_makefile"] is None
    assert Path(payload["shared_library"]).exists()
    for source in sources:
        assert any(Path(path).name == f"{source.stem}.o" for path in payload["generated_files"])

    sys.modules.pop(module_name, None)
    sys.path.insert(0, str(workdir))
    try:
        return importlib.import_module(module_name), payload
    finally:
        sys.path.remove(str(workdir))


def test_multi_file_modules_build_one_merged_extension(tmp_path: Path):
    module, payload = _build_sources_and_import(
        [
            (
                "first_api.f90",
                """module first_api
contains
  integer function add_one(value) result(output)
    integer, intent(in) :: value
    output = value + 1
  end function add_one
end module first_api
""",
            ),
            (
                "second_api.f90",
                """module second_api
  use first_api, only: add_one
  integer :: counter = 3
contains
  integer function double_value(value) result(output)
    integer, intent(in) :: value
    output = add_one(value) * 2
  end function double_value
end module second_api
""",
            ),
        ],
        tmp_path,
    )

    assert payload["module_name"] == "first_api"
    assert module.add_one(np.int32(4)) == 5
    assert module.double_value(np.int32(4)) == 10
    assert module.get_counter() == 3
    module.set_counter(np.int32(7))
    assert module.get_counter() == 7
    bridge = (tmp_path / "bind_c_first_api_wrapper.f90").read_text(encoding="utf-8").lower()
    assert "use first_api" in bridge
    assert "use second_api" in bridge


def test_multi_file_standalone_procedures_build_one_merged_extension(tmp_path: Path):
    module, payload = _build_sources_and_import(
        [
            (
                "standalone_api.f",
                """      integer function add_one(value)
      integer value
      add_one = value + 1
      end
""",
            ),
            (
                "double_value.f",
                """      integer function double_value(value)
      integer value
      double_value = value * 2
      end
""",
            ),
        ],
        tmp_path,
    )

    assert payload["module_name"] == "standalone_api"
    assert module.add_one(np.int32(4)) == 5
    assert module.double_value(np.int32(4)) == 8


@pytest.mark.skipif(
    sys.platform == "win32" or shutil.which("make") is None,
    reason="generated Makefile requires GNU Make and a POSIX shell",
)
def test_makefile_mode_generates_parallel_build_without_compiling(tmp_path: Path):
    first = tmp_path / "first_api.f90"
    second = tmp_path / "second_api.f90"
    first.write_text(
        """module first_api
contains
  integer function add_one(value) result(output)
    integer, intent(in) :: value
    output = value + 1
  end function add_one
end module first_api
""",
        encoding="utf-8",
    )
    second.write_text(
        """module second_api
  use first_api, only: add_one
contains
  integer function double_value(value) result(output)
    integer, intent(in) :: value
    output = add_one(value) * 2
  end function double_value
end module second_api
""",
        encoding="utf-8",
    )

    command = [
        sys.executable,
        "-m",
        "x2py",
        str(first),
        str(second),
        "--makefile",
        "--out-dir",
        str(tmp_path),
        "--json",
    ]
    generated = subprocess.run(command, capture_output=True, text=True, check=True)
    payload = json.loads(generated.stdout)
    makefile = Path(payload["build_makefile"])

    assert payload["compiled"] is False
    assert makefile.is_file()
    assert not Path(payload["shared_library"]).exists()
    text = makefile.read_text(encoding="utf-8")
    assert "FC := " in text
    assert "CC := " in text
    assert "X2PY_FFLAGS ?=" in text
    assert f"{tmp_path / 'second_api.o'}: {second} {tmp_path / 'first_api.o'}" in text
    assert f"{tmp_path / 'bind_c_first_api_wrapper.o'}:" in text
    assert str(tmp_path / "first_api.o") in text
    assert str(tmp_path / "second_api.o") in text

    built = subprocess.run(
        [
            "make",
            "-j4",
            "-f",
            str(makefile),
            "all",
            "X2PY_FFLAGS=-O3",
            "X2PY_CFLAGS=-O3",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "-O3" in built.stdout
    assert Path(payload["shared_library"]).is_file()

    sys.modules.pop("first_api", None)
    sys.path.insert(0, str(tmp_path))
    try:
        module = importlib.import_module("first_api")
        assert module.double_value(np.int32(4)) == 10
    finally:
        sys.path.remove(str(tmp_path))


def test_verbose_mode_prints_full_direct_build_commands(tmp_path: Path):
    source = tmp_path / "verbose_api.f90"
    source.write_text(
        """module verbose_api
contains
  subroutine ping()
  end subroutine ping
end module verbose_api
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(source),
            "--verbose",
            "--out-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    command_lines = result.stdout.splitlines()

    assert any(str(source) in line and "-c" in line for line in command_lines)
    assert any("bind_c_verbose_api_wrapper.f90" in line and "-c" in line for line in command_lines)
    assert any("verbose_api_wrapper.c" in line and "-c" in line for line in command_lines)
    assert any("-shared" in line and "verbose_api" in line for line in command_lines)
    assert "Built extension:" in result.stdout


def _normalized_fortran_source(source: Path):
    return " ".join(source.read_text().replace("&", "").split())


def _result_dtype(expected):
    if isinstance(expected, bool):
        return np.dtype(np.bool_)
    if isinstance(expected, int):
        return np.dtype(np.int32)
    return np.asarray(expected).dtype


def _array_argument(value, size: int, *, strided: bool):
    dtype = np.asarray(value).dtype
    if strided:
        storage = np.zeros(2 * size, dtype=dtype)
        array = storage[::2]
    else:
        array = np.zeros(size, dtype=dtype)
    array[:] = value
    return array


def _array_result(expected, size: int, *, strided: bool):
    dtype = _result_dtype(expected)
    if strided:
        storage = np.zeros(2 * size, dtype=dtype)
        return storage[1::2]
    return np.zeros(size, dtype=dtype)


def _assert_array_result(function_name, result, expected, size):
    expected_array = np.full(size, expected, dtype=result.dtype)
    if result.dtype == np.dtype(np.bool_):
        np.testing.assert_array_equal(result, expected_array, err_msg=function_name)
    else:
        np.testing.assert_allclose(
            result,
            expected_array,
            rtol=1e-6,
            atol=1e-6,
            err_msg=function_name,
        )


def _assert_fmath_array_examples(module, *, suffix="", strided=False):
    cases = fmath_cases()
    missing = sorted(
        f"{name}{suffix}".lower() for name, _, _ in cases if not hasattr(module, f"{name}{suffix}".lower())
    )
    assert missing == []

    size = 4
    for function_name, scalar_args, expected in cases:
        wrapped_name = f"{function_name}{suffix}".lower()
        array_args = [_array_argument(scalar_arg, size, strided=strided) for scalar_arg in scalar_args]
        result = _array_result(expected, size, strided=strided)

        getattr(module, wrapped_name)(np.int32(size), *array_args, result)

        _assert_array_result(wrapped_name, result, expected, size)


def _assert_array_rejects_strided_views(module, function_name):
    size = 4
    values = _array_argument(np.float32(2.0), size, strided=True)
    result = _array_result(np.float32(4.0), size, strided=True)

    with pytest.raises(TypeError, match="contiguous"):
        getattr(module, function_name.lower())(np.int32(size), values, result)


def _assert_legacy_string_examples(module):
    assert module.char_code_default("A") == ord("A")
    assert module.char_code_star1(np.str_("B")) == ord("B")
    assert module.string_len_star8("short") == 5
    assert module.string_len_star8("too-long-value") == 8
    assert module.string_len_assumed("variable length") == 15
    assert module.string_len_entity("python") == 6
    assert module.char_result_default() == "L"
    assert module.string_result_star8() == "LEGACY!!"
    assert module.string_result_padded() == "PAD     "
    assert module.string_result_declared() == "STRING"


def _assert_modern_string_examples(module):
    assert module.char_code_default("A") == ord("A")
    assert module.char_code_len1(np.str_("B")) == ord("B")
    assert module.char_code_kind1("C") == ord("C")
    assert module.char_code_c_char("D") == ord("D")
    assert module.string_len_fixed("short") == 5
    assert module.string_len_fixed("too-long-value") == 8
    assert module.string_len_assumed("variable length") == 15
    assert module.string_len_c_char("c-char") == 6
    assert module.char_result_default() == "M"
    assert module.char_result_c_char() == "C"
    assert module.string_result_fixed() == "MODERN!!"
    assert module.string_result_padded() == "PAD     "
    assert module.string_result_c_char() == "C-CHAR!!"
    assert module.string_result_deferred("dynamic") == "dynamic-deferred"
    assert module.string_result_deferred("café") == "café-deferred"


def _assert_modern_class_examples(module):
    assert hasattr(module, "vector")
    value = module.vector()
    value.x = np.float64(3.0)
    value.y = np.float64(4.0)

    assert value.magnitude() == np.float64(5.0)
    value.scale(np.float64(2.0))
    assert value.x == np.float64(6.0)
    assert value.y == np.float64(8.0)
    assert value.magnitude() == np.float64(10.0)
    value.shift(np.float64(1.5), np.float64(-2.0))
    assert value.x == np.float64(7.5)
    assert value.y == np.float64(6.0)

    assert hasattr(module, "vector_store")
    store = module.vector_store()
    assert store.values is None
    assert store.matrix is None

    with pytest.raises(AttributeError, match="reallocate"):
        store.values = np.array([9.0], dtype=np.float64)

    store.allocate_values(np.int64(3))
    store.values[:] = np.array([1.0, 2.0, 3.0], dtype=np.float64)
    np.testing.assert_allclose(store.values, np.array([1.0, 2.0, 3.0]))

    store.set_values(np.array([4.0, 5.0], dtype=np.float64))
    np.testing.assert_allclose(store.values, np.array([4.0, 5.0]))

    matrix = np.asfortranarray(np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], dtype=np.float64))
    store.allocate_matrix(np.int64(2), np.int64(3))
    store.matrix[:, :] = matrix
    np.testing.assert_allclose(store.matrix, matrix)
    assert store.matrix.flags.f_contiguous

    replacement = np.asfortranarray(matrix * 2.0)
    store.set_matrix(replacement)
    np.testing.assert_allclose(store.matrix, replacement)
    assert store.matrix.flags.f_contiguous

    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        store.set_matrix(np.array(replacement, order="C"))

    made = module.vector_store.make(np.int64(4), np.float64(1.5))
    np.testing.assert_allclose(made.values, np.full(4, 1.5, dtype=np.float64))


def test_scalar_kind_coverage_uses_compiler_probed_wrapper_types(tmp_path: Path):
    module = _build_text_and_import(
        SCALAR_KINDS_F90_TEXT,
        "fscalar_kinds_f90.f90",
        tmp_path,
        {
            "bind_c_fscalar_kinds_f90_wrapper.f90",
            "fscalar_kinds_f90_wrapper.c",
            "fscalar_kinds_f90_wrapper.h",
        },
    )

    assert module.id_i8(np.int8(np.iinfo(np.int8).min)) == np.iinfo(np.int8).min
    assert module.id_i16(np.int16(np.iinfo(np.int16).max)) == np.iinfo(np.int16).max
    assert module.id_i32(np.int32(np.iinfo(np.int32).min)) == np.iinfo(np.int32).min
    assert module.id_i64(np.int64(2**40)) == 2**40
    assert module.id_c_i32(np.int32(123456)) == 123456

    values_i16 = np.array([np.iinfo(np.int16).min, -1, np.iinfo(np.int16).max], dtype=np.int16)
    out_i16 = np.empty_like(values_i16)
    module.copy_i16(np.int32(values_i16.size), values_i16, out_i16)
    np.testing.assert_array_equal(out_i16, values_i16)

    assert bool(module.not_flag(True)) is False
    flags = np.array([True, False, True], dtype=np.bool_)
    inverted = np.empty_like(flags)
    module.invert_flags(np.int32(flags.size), flags, inverted)
    np.testing.assert_array_equal(inverted, np.logical_not(flags))

    assert np.isnan(module.id_r32(np.float32(np.nan)))
    assert np.isposinf(module.id_r64(np.float64(np.inf)))
    assert module.id_c_float(np.float32(1.25)) == np.float32(1.25)
    assert module.id_c_double(np.float64(-2.5)) == np.float64(-2.5)

    values_r64 = np.array([np.finfo(np.float64).min, np.inf, np.nan], dtype=np.float64)
    out_r64 = np.empty_like(values_r64)
    module.copy_r64(np.int32(values_r64.size), values_r64, out_r64)
    np.testing.assert_allclose(out_r64, values_r64, equal_nan=True)

    np.testing.assert_allclose(module.conj_c64(np.complex64(1 + 2j)), np.complex64(1 - 2j))
    np.testing.assert_allclose(module.shift_c128(np.complex128(2 + 3j)), np.complex128(3 + 1j))
    np.testing.assert_allclose(module.conj_c_float_complex(np.complex64(-1 + 4j)), np.complex64(-1 - 4j))
    np.testing.assert_allclose(
        module.conj_c_double_complex(np.complex128(-2 - 5j)),
        np.complex128(-2 + 5j),
    )

    values_c128 = np.array([1 + 2j, np.inf - 3j, np.nan + 4j], dtype=np.complex128)
    out_c128 = np.empty_like(values_c128)
    module.copy_c128(np.int32(values_c128.size), values_c128, out_c128)
    np.testing.assert_allclose(out_c128, values_c128, equal_nan=True)


def test_visibility_and_default_python_name_fixing_policy(tmp_path: Path):
    module = _build_text_and_import(
        NAMING_F90_TEXT,
        "fnaming_f90.f90",
        tmp_path,
        {
            "bind_c_fnaming_f90_wrapper.f90",
            "fnaming_f90_wrapper.c",
            "fnaming_f90_wrapper.h",
        },
    )

    assert module.lambda_(np.int32(3)) == 4
    assert module.lambda__2(np.int32(3)) == 5
    assert module.get_value() == 100
    assert module.get_value_2() == 7
    module.set_value(np.int32(11))
    assert module.get_value_2() == 11

    assert not hasattr(module, "hidden_t")
    assert not hasattr(module, "hidden_proc")

    item = module.visible_t(lambda_=np.int32(5), lambda__2=np.int32(6))
    assert item.lambda_ == 5
    assert item.lambda__2 == 6
    assert item.from_() == 11
    assert not hasattr(item, "hidden")


def test_strict_wrapper_names_reject_python_name_fixes(tmp_path: Path):
    source = tmp_path / "fnaming_f90.f90"
    source.write_text(NAMING_F90_TEXT, encoding="utf-8")

    cmd = [
        sys.executable,
        "-m",
        "x2py",
        str(source),
        "--out-dir",
        str(tmp_path),
        "--json",
        "--strict-wrapper-names",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    assert result.returncode != 0
    assert "strict wrapper naming" in result.stderr


def test_scalar_derived_types_cross_procedure_boundaries(tmp_path: Path):
    module = _build_text_and_import(
        DERIVED_BOUNDARY_F90_TEXT,
        "fderived_boundary_f90.f90",
        tmp_path,
        {
            "bind_c_fderived_boundary_f90_wrapper.f90",
            "fderived_boundary_f90_wrapper.c",
            "fderived_boundary_f90_wrapper.h",
        },
    )

    point = module.point()
    point.x = np.float64(1.0)
    point.y = np.float64(2.0)
    assert not hasattr(point, "hidden")
    assert module.point_sum(point) == np.float64(3.0)

    identity = id(point)
    assert module.move_point(point, np.float64(4.0), np.float64(5.0)) is None
    assert id(point) == identity
    assert point.x == np.float64(5.0)
    assert point.y == np.float64(7.0)

    out_point = module.make_point_out(np.float64(8.0), np.float64(9.0))
    assert isinstance(out_point, module.point)
    assert out_point.x == np.float64(8.0)
    assert out_point.y == np.float64(9.0)

    result_point = module.make_point(np.float64(10.0), np.float64(11.0))
    assert isinstance(result_point, module.point)
    assert result_point.x == np.float64(10.0)
    assert result_point.y == np.float64(11.0)

    holder = module.holder()
    holder.scale = np.float64(2.5)
    assert module.set_holder_origin(holder, result_point) is None
    origin = holder.origin
    assert isinstance(origin, module.point)
    assert origin.x == np.float64(10.0)
    origin.x = np.float64(12.0)
    assert module.holder_origin_x(holder) == np.float64(12.0)

    del holder
    gc.collect()
    assert origin.x == np.float64(12.0)


def test_fortran_extension_types_generate_python_inheritance(tmp_path: Path):
    module = _build_text_and_import(
        INHERITANCE_F90_TEXT,
        "finheritance_f90.f90",
        tmp_path,
        {
            "bind_c_finheritance_f90_wrapper.f90",
            "finheritance_f90_wrapper.c",
            "finheritance_f90_wrapper.h",
        },
    )

    assert issubclass(module.circle, module.base_shape)
    assert issubclass(module.box, module.base_shape)

    base = module.base_shape()
    base.size = np.float64(3.0)
    assert base.area() == np.float64(3.0)
    assert module.describe_shape(base) == np.float64(3.0)

    circle = module.circle()
    assert isinstance(circle, module.base_shape)
    circle.set_size(np.float64(5.0))
    circle.radius = np.float64(2.0)
    assert circle.size == np.float64(5.0)
    assert circle.area() == np.float64(9.0)
    assert module.describe_shape(circle) == np.float64(9.0)

    module.base_shape.set_size(circle, np.float64(7.0))
    assert circle.size == np.float64(7.0)

    box = module.box()
    assert isinstance(box, module.base_shape)
    box.set_size(np.float64(2.0))
    box.width = np.float64(3.0)
    assert box.area() == np.float64(32.0)
    assert module.describe_shape(box) == np.float64(32.0)


def test_immediate_scalar_dummy_procedure_calls_python_callback(tmp_path: Path):
    module = _build_text_and_import(
        CALLBACK_SCALAR_F90_TEXT,
        "fcallback_scalar_f90.f90",
        tmp_path,
        {
            "bind_c_fcallback_scalar_f90_wrapper.f90",
            "fcallback_scalar_f90_wrapper.c",
            "fcallback_scalar_f90_wrapper.h",
        },
    )

    assert module.apply_scalar(lambda value: value * 3.0, np.float64(2.5)) == np.float64(7.5)
    assert module.apply_explicit(lambda value: value - 1.0, np.float64(2.5)) == np.float64(1.5)
    notified = []
    assert module.call_notify(lambda value: notified.append(value), np.float64(6.0)) is None
    assert notified == [6.0]
    assert module.apply_scalar(
        lambda value: module.apply_scalar(lambda nested: nested + 1.0, np.float64(value)) * 2.0,
        np.float64(3.0),
    ) == np.float64(8.0)

    class Callback:
        def __call__(self, value):
            return value

    callback = Callback()
    references_before = sys.getrefcount(callback)
    assert module.apply_scalar(callback, np.float64(3.0)) == np.float64(3.0)
    assert sys.getrefcount(callback) == references_before
    with pytest.raises(TypeError, match="must be callable"):
        module.apply_scalar(42, np.float64(1.0))

    wrapper_source = (tmp_path / "fcallback_scalar_f90_wrapper.c").read_text(encoding="utf-8")
    assert "static _Thread_local" in wrapper_source
    assert "PyThread_get_thread_ident()" in wrapper_source
    assert "PyGILState_Ensure()" in wrapper_source
    assert "PyGILState_Release(" in wrapper_source
    assert "PyErr_PrintEx(0);" in wrapper_source
    assert "abort();" in wrapper_source
    assert "Py_INCREF(bound_callback_obj);" in wrapper_source
    assert "Py_DECREF(" in wrapper_source


def test_callback_exception_prints_traceback_and_aborts_host_process(tmp_path: Path):
    _build_text_and_import(
        CALLBACK_SCALAR_F90_TEXT,
        "fcallback_scalar_f90.f90",
        tmp_path,
        {
            "bind_c_fcallback_scalar_f90_wrapper.f90",
            "fcallback_scalar_f90_wrapper.c",
            "fcallback_scalar_f90_wrapper.h",
        },
    )
    script = """
import numpy as np
import fcallback_scalar_f90 as module

def fail(value):
    raise ValueError(f"callback exploded at {value}")

module.apply_scalar(fail, np.float64(4.0))
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "Traceback (most recent call last)" in result.stderr
    assert "ValueError: callback exploded at 4.0" in result.stderr

    invalid_return = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import numpy as np; import fcallback_scalar_f90 as module; "
                "module.apply_scalar(lambda value: 'wrong', np.float64(4.0))"
            ),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert invalid_return.returncode != 0
    assert "TypeError" in invalid_return.stderr

    invalid_signature = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import numpy as np; import fcallback_scalar_f90 as module; "
                "module.apply_scalar(lambda: np.float64(1.0), np.float64(4.0))"
            ),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert invalid_signature.returncode != 0
    assert "TypeError" in invalid_signature.stderr


def test_immediate_dummy_procedure_converts_array_arguments_and_results(tmp_path: Path):
    module = _build_text_and_import(
        CALLBACK_ARRAY_F90_TEXT,
        "fcallback_array_f90.f90",
        tmp_path,
        {
            "bind_c_fcallback_array_f90_wrapper.f90",
            "fcallback_array_f90_wrapper.c",
            "fcallback_array_f90_wrapper.h",
        },
    )
    values = np.asfortranarray(np.array([1.0, 2.0, 3.0], dtype=np.float64))

    assert module.apply_reduce(lambda count, data: data[:count].sum(), np.int32(3), values) == np.float64(6.0)
    transformed = np.empty_like(values)
    result = module.apply_transform(
        lambda count, data: np.asfortranarray(data[:count] * 2.0),
        np.int32(3),
        values,
        transformed,
    )
    assert result is transformed
    np.testing.assert_array_equal(transformed, np.array([2.0, 4.0, 6.0], dtype=np.float64))


def test_immediate_dummy_procedure_converts_derived_arguments_and_results(tmp_path: Path):
    module = _build_text_and_import(
        CALLBACK_DERIVED_F90_TEXT,
        "fcallback_derived_f90.f90",
        tmp_path,
        {
            "bind_c_fcallback_derived_f90_wrapper.f90",
            "fcallback_derived_f90_wrapper.c",
            "fcallback_derived_f90_wrapper.h",
        },
    )
    point = module.point_t(x=np.float64(2.0), y=np.float64(5.0))

    result = module.apply_point(
        lambda value: module.point_t(x=value.x + 1.0, y=value.y * 2.0),
        point,
    )
    assert isinstance(result, module.point_t)
    assert result.x == np.float64(3.0)
    assert result.y == np.float64(10.0)


def test_fortran_wrapper_pipeline_builds_importable_extension(tmp_path: Path):
    module = _build_and_import(
        SCALAR_LEGACY_SOURCE,
        tmp_path,
        {
            "bind_c_fmath_wrapper.f90",
            "fmath_wrapper.c",
            "fmath_wrapper.h",
        },
    )

    _assert_fmath_examples(module)


def test_f90_wrapper_pipeline_builds_importable_extension(tmp_path: Path):
    module = _build_and_import(
        SCALAR_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fmath_f90_wrapper.f90",
            "fmath_f90_wrapper.c",
            "fmath_f90_wrapper.h",
        },
    )

    _assert_fmath_examples(module)


def test_fortran_array_wrapper_pipeline_matches_fmath_results_with_contiguous_arrays(tmp_path: Path):
    module = _build_and_import(
        ARRAY_LEGACY_SOURCE,
        tmp_path,
        {
            "bind_c_fmath_arrays_wrapper.f90",
            "fmath_arrays_wrapper.c",
            "fmath_arrays_wrapper.h",
        },
    )

    _assert_fmath_array_examples(module, strided=False)
    _assert_array_rejects_strided_views(module, "SQUARE_R4")


def test_f90_array_wrapper_distinguishes_contiguous_and_strided_contracts(tmp_path: Path):
    module = _build_and_import(
        ARRAY_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fmath_arrays_f90_wrapper.f90",
            "fmath_arrays_f90_wrapper.c",
            "fmath_arrays_f90_wrapper.h",
        },
    )

    _assert_fmath_array_examples(module, suffix="_CONTIGUOUS", strided=False)
    _assert_array_rejects_strided_views(module, "SQUARE_R4_CONTIGUOUS")
    _assert_fmath_array_examples(module, suffix="_STRIDED", strided=True)


def test_legacy_fortran_character_arguments_and_results(tmp_path: Path):
    module = _build_and_import(
        STRING_LEGACY_SOURCE,
        tmp_path,
        {
            "bind_c_fstrings_wrapper.f90",
            "fstrings_wrapper.c",
            "fstrings_wrapper.h",
        },
    )

    bind_c_source = _normalized_fortran_source(tmp_path / "bind_c_fstrings_wrapper.f90")
    assert "C_fixed = transfer(C_0001, C_fixed)" in bind_c_source
    assert "C = transfer(C_0001, C) C_fixed = C" not in bind_c_source
    assert (
        "CHAR_RESULT_DEFAULT_ptr = transfer(CHAR_RESULT_DEFAULT_0001, CHAR_RESULT_DEFAULT_ptr, CHAR_RESULT_DEFAULT_len)"
    ) in bind_c_source
    assert "do Dummy_" not in bind_c_source

    _assert_legacy_string_examples(module)


def test_modern_fortran_character_arguments_and_results(tmp_path: Path):
    module = _build_and_import(
        STRING_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fstrings_f90_wrapper.f90",
            "fstrings_f90_wrapper.c",
            "fstrings_f90_wrapper.h",
        },
    )

    _assert_modern_string_examples(module)


def test_fortran_character_edge_cases_follow_copy_in_copy_out_policy(tmp_path: Path):
    module = _build_text_and_import(
        CHARACTER_EDGES_F90_TEXT,
        "fcharacter_edges_f90.f90",
        tmp_path,
        {
            "bind_c_fcharacter_edges_f90_wrapper.f90",
            "fcharacter_edges_f90_wrapper.c",
            "fcharacter_edges_f90_wrapper.h",
        },
    )

    original = "abc"
    assert module.fixed_inout(original) == "Zbc    !"
    assert original == "abc"
    assert module.fixed_inout("abcdefgh") == "Zbcdefg!"
    assert module.fixed_inout("abcdefghi") == "Zbcdefg!"
    assert module.assumed_inout("abc") == "Qbc"
    assert module.assumed_inout("") == ""
    assert module.optional_inout() is None
    assert module.optional_inout(None) is None
    assert module.optional_inout("abc") == "Pbc"
    assert module.make_out() == "go    "
    assert module.unicode_echo("café") == "café"

    with pytest.raises(TypeError, match="embedded NUL"):
        module.assumed_inout("a\0b")
    with pytest.raises(TypeError, match="embedded NUL"):
        module.unicode_echo("a\0b")


def test_modern_fortran_derived_type_exposes_class_and_type_bound_methods(tmp_path: Path):
    module = _build_and_import(
        CLASS_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fclasses_f90_wrapper.f90",
            "fclasses_f90_wrapper.c",
            "fclasses_f90_wrapper.h",
        },
    )

    _assert_modern_class_examples(module)


def test_fortran_default_constructor_keywords_and_finalization(tmp_path: Path):
    module = _build_text_and_import(
        CONSTRUCTOR_F90_TEXT,
        "fconstructors_f90.f90",
        tmp_path,
        {
            "bind_c_fconstructors_f90_wrapper.f90",
            "fconstructors_f90_wrapper.c",
            "fconstructors_f90_wrapper.h",
        },
    )

    module.reset_final_count()

    defaulted = module.initialized()
    assert defaulted.id == np.int32(7)
    assert defaulted.scale == np.float64(2.5)

    partial = module.initialized(id=np.int32(11))
    assert partial.id == np.int32(11)
    assert partial.scale == np.float64(2.5)

    keyword = module.initialized(id=np.int32(4), scale=np.float64(6.5))
    assert keyword.id == np.int32(4)
    assert keyword.scale == np.float64(6.5)

    del defaulted
    gc.collect()
    gc.collect()
    assert module.get_final_count() == np.int32(1)

    del partial
    del keyword
    gc.collect()
    gc.collect()
    assert module.get_final_count() == np.int32(3)

    with pytest.raises(TypeError):
        module.initialized(np.int32(1))
    gc.collect()
    assert module.get_final_count() == np.int32(4)

    with pytest.raises(TypeError):
        module.initialized(missing=np.int32(1))
    gc.collect()
    assert module.get_final_count() == np.int32(5)

    gc.collect()
    gc.collect()
    assert module.get_final_count() == np.int32(5)


def test_borrowed_child_wrapper_never_finalizes_native_component(tmp_path: Path):
    module = _build_text_and_import(
        BORROWED_FINALIZER_F90_TEXT,
        "fborrowed_finalizer_f90.f90",
        tmp_path,
        {
            "bind_c_fborrowed_finalizer_f90_wrapper.f90",
            "fborrowed_finalizer_f90_wrapper.c",
            "fborrowed_finalizer_f90_wrapper.h",
        },
    )

    module.reset_final_count()
    owner = module.parent()
    borrowed = owner.value

    del borrowed
    gc.collect()
    assert module.get_final_count() == np.int32(0)

    borrowed = owner.value
    del owner
    gc.collect()
    assert module.get_final_count() == np.int32(0)

    del borrowed
    gc.collect()
    gc.collect()
    assert module.get_final_count() == np.int32(1)


def test_fortran_generic_interfaces_dispatch_in_generated_c_extension(tmp_path: Path):
    module = _build_and_import(
        OVERLOAD_F90_SOURCE,
        tmp_path,
        {
            "bind_c_foverloads_f90_wrapper.f90",
            "foverloads_f90_wrapper.c",
            "foverloads_f90_wrapper.h",
        },
    )

    assert module.convert(np.int32(4)) == np.int32(14)
    assert module.convert(np.float64(4.0)) == np.float64(4.5)
    assert module.convert(np.complex128(2.0 + 3.0j)) == np.complex128(3.0 + 2.0j)
    assert module.summarize(np.float64(2.5)) == np.float64(2.5)
    assert module.summarize(np.array([1.0, 2.0, 3.0], dtype=np.float64)) == np.float64(6.0)

    value = module.accumulator()
    value.add(np.int32(2))
    value.add(np.float64(0.5))
    assert value.total == np.float64(2.5)
    assert module.inspect(value) == np.float64(2.5)

    sample = module.sample()
    sample.value = np.float64(7.25)
    assert module.inspect(sample) == np.float64(7.25)

    with pytest.raises(TypeError):
        module.convert("not numeric")
    with pytest.raises(TypeError):
        value.add(np.complex128(1.0 + 0.0j))


def test_scalar_module_variables_use_accessors_and_parameters_have_no_setter(tmp_path: Path):
    module = _build_text_and_import(
        MODULE_VARIABLES_F90_TEXT,
        "fmodule_vars_f90.f90",
        tmp_path,
        {
            "bind_c_fmodule_vars_f90_wrapper.f90",
            "fmodule_vars_f90_wrapper.c",
            "fmodule_vars_f90_wrapper.h",
        },
    )

    assert module.nmax == np.int32(12)
    assert module.red == np.int32(-1)
    assert module.blue == np.int32(0)
    assert module.green == np.int32(10)
    assert module.yellow == np.int32(11)
    assert not hasattr(module, "counter")
    assert not hasattr(module, "scale")
    assert not hasattr(module, "set_nmax")
    assert not hasattr(module, "set_red")
    assert not hasattr(module, "hidden_counter")
    assert not hasattr(module, "get_hidden_counter")

    assert module.get_counter() == np.int32(3)
    assert module.summarize() == np.int32(15)
    module.set_counter(np.int32(9))
    assert module.get_counter() == np.int32(9)
    assert module.summarize() == np.int32(21)

    assert module.get_scale() == np.float64(1.5)
    module.set_scale(np.float64(2.0))
    assert module.scaled_counter() == np.float64(18.0)

    assert module.get_saved_counter() == np.int32(6)
    module.set_saved_counter(np.int32(8))
    assert module.get_saved_counter() == np.int32(8)
    assert module.next_local() == np.int32(1)
    assert module.next_local() == np.int32(2)
    assert not hasattr(module, "get_local_counter")

    sys.modules.pop("fmodule_vars_f90", None)
    sys.path.insert(0, str(tmp_path))
    try:
        second_module = importlib.import_module("fmodule_vars_f90")
    finally:
        sys.path.remove(str(tmp_path))

    assert second_module is not module
    assert second_module.get_counter() == np.int32(9)
    assert second_module.get_saved_counter() == np.int32(8)
    second_module.set_counter(np.int32(4))
    assert module.get_counter() == np.int32(4)

    module.nmax = np.int32(99)
    assert module.nmax == np.int32(99)
    assert second_module.nmax == np.int32(12)
    assert module.summarize() == np.int32(16)
    assert second_module.summarize() == np.int32(16)


def test_common_block_storage_stays_internal_to_wrapped_fortran(tmp_path: Path):
    module = _build_text_and_import(
        COMMON_BLOCK_F90_TEXT,
        "fcommon_block_f90.f90",
        tmp_path,
        {
            "bind_c_fcommon_block_f90_wrapper.f90",
            "fcommon_block_f90_wrapper.c",
            "fcommon_block_f90_wrapper.h",
        },
    )

    assert not hasattr(module, "shared_value")
    assert not hasattr(module, "get_shared_value")
    assert not hasattr(module, "set_shared_value")

    module.write_shared(np.int32(17))
    assert module.read_shared() == np.int32(17)
    module.write_shared(np.int32(-3))
    assert module.read_shared() == np.int32(-3)


def test_bind_c_derived_types_use_accessors_and_fortran_value_copy(tmp_path: Path):
    module = _build_text_and_import(
        BIND_C_DERIVED_LAYOUT_F90_TEXT,
        "fbind_c_derived_layout_f90.f90",
        tmp_path,
        {
            "bind_c_fbind_c_derived_layout_f90_wrapper.f90",
            "fbind_c_derived_layout_f90_wrapper.c",
            "fbind_c_derived_layout_f90_wrapper.h",
        },
    )
    bridge_source = (tmp_path / "bind_c_fbind_c_derived_layout_f90_wrapper.f90").read_text()

    assert "function tagged_point_position_getter" in bridge_source
    assert "subroutine tagged_point_position_setter" in bridge_source
    assert "function tagged_point_weight_getter" in bridge_source
    assert "subroutine tagged_point_weight_setter" in bridge_source
    assert "type(c_ptr), value :: bound_value" in bridge_source
    assert "type(tagged_point), pointer :: value_0001" in bridge_source

    value = module.tagged_point()
    module.populate(
        value,
        np.float64(2.5),
        np.int32(4),
        np.complex128(3.0 + 2.0j),
    )

    position = value.position
    assert position.x == np.float64(2.5)
    assert position.axis == np.int32(4)
    assert value.weight == np.complex128(3.0 + 2.0j)

    assert module.score_by_value(value) == np.float64(109.5)
    assert position.x == np.float64(2.5)


def test_fixed_form_fortran_generic_interface_dispatches_in_generated_c_extension(tmp_path: Path):
    module = _build_and_import(
        OVERLOAD_FIXED_SOURCE,
        tmp_path,
        {
            "bind_c_foverloads_fixed_wrapper.f90",
            "foverloads_fixed_wrapper.c",
            "foverloads_fixed_wrapper.h",
        },
    )

    assert module.convert(np.int32(2)) == np.int32(22)
    assert module.convert(np.float64(2.0)) == np.float64(2.25)
    with pytest.raises(TypeError):
        module.convert(np.complex128(2.0 + 0.0j))


def test_fortran_defined_operators_and_assignment_dispatch_in_generated_c_extension(tmp_path: Path):
    module = _build_and_import(
        OPERATOR_F90_SOURCE,
        tmp_path,
        {
            "bind_c_foperators_f90_wrapper.f90",
            "foperators_f90_wrapper.c",
            "foperators_f90_wrapper.h",
        },
    )

    def vector(value):
        result = module.vector()
        result.value = np.float64(value)
        return result

    def offset(value):
        result = module.offset()
        result.value = np.float64(value)
        return result

    left = vector(5.0)
    right = vector(2.0)

    assert module.convert(np.int32(2)) == np.int32(12)
    assert module.convert(np.float64(2.0)) == np.float64(2.5)
    assert (left + right).value == np.float64(7.0)
    assert (left + np.int32(3)).value == np.float64(8.0)
    assert (left + np.float64(0.5)).value == np.float64(5.5)
    assert (np.float64(1.5) + left).value == np.float64(106.5)
    assert (left + np.array([1.0, 2.0], dtype=np.float64)).value == np.float64(8.0)
    assert (left + offset(4.0)).value == np.float64(9.0)
    temporary_result = vector(1.0) + vector(2.0)
    gc.collect()
    assert temporary_result.value == np.float64(3.0)
    assert (+left).value == np.float64(5.0)
    assert (left - np.float64(1.5)).value == np.float64(3.5)
    assert (np.float64(9.0) - left).value == np.float64(4.0)
    assert (-left).value == np.float64(-5.0)
    assert (left * np.float64(2.0)).value == np.float64(10.0)
    assert (left / np.float64(2.0)).value == np.float64(2.5)
    assert (left ** np.int32(2)).value == np.float64(25.0)
    with pytest.raises(TypeError, match="modulus is not supported"):
        pow(left, np.int32(2), np.int32(3))

    assert left == vector(5.0)
    assert left != right
    assert right < left
    assert left < np.float64(6.0)
    assert np.float64(1.0) < left
    assert right <= left
    assert left > right
    assert left >= right
    assert bool(left & right) is True
    assert bool(vector(0.0) | right) is True
    assert bool(~vector(0.0)) is True
    assert left == offset(1.0)
    assert left != np.int32(0)
    assert left.operator_dot(right) == np.float64(10.0)
    assert left.r_operator_shift(np.float64(2.0)).value == np.float64(207.0)

    assigned = vector(1.0)
    assigned_identity = id(assigned)
    assert assigned.assign(np.int32(7)) is None
    assert id(assigned) == assigned_identity
    assert assigned.value == np.float64(7.0)
    assert assigned.assign(np.float64(3.5)) is None
    assert assigned.value == np.float64(3.5)
    assert assigned.assign(assigned) is None
    assert assigned.value == np.float64(3.5)

    counter = module.counter()
    counter.value = np.int32(4)
    assert (counter + np.int32(3)).value == np.int32(7)

    with pytest.raises(TypeError):
        left + np.complex128(1.0 + 0.0j)
    with pytest.raises(TypeError):
        assigned.assign(np.complex128(1.0 + 0.0j))


def test_allocatable_module_and_derived_type_arrays_are_borrowed_views(tmp_path: Path):
    module = _build_and_import(
        ALLOCATABLE_VIEW_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fallocatable_views_f90_wrapper.f90",
            "fallocatable_views_f90_wrapper.c",
            "fallocatable_views_f90_wrapper.h",
        },
    )

    assert "Functions" in module.__doc__
    assert "build_values" in module.__doc__
    assert "buffer" in module.__doc__
    assert "build_values(n) -> ndarray[float64] | None" in module.build_values.__doc__
    assert "n : int32" in module.build_values.__doc__
    assert "Intent: in" in module.build_values.__doc__
    assert "values : ndarray[float64] or None" in module.build_values.__doc__
    assert "Rank: 1" in module.build_values.__doc__
    assert "Ownership: Python-owned" in module.build_values.__doc__
    assert "Returns None when unallocated." in module.build_values.__doc__
    assert "TypeError" in module.build_values.__doc__
    assert "Rank: 2" in module.build_matrix.__doc__
    assert "Layout: F-contiguous" in module.build_matrix.__doc__
    assert "get_module_values() -> ndarray[float64] | None" in module.get_module_values.__doc__
    assert "Ownership: Native-owned" in module.get_module_values.__doc__
    assert "zero-copy view of native Fortran memory" in module.get_module_values.__doc__
    assert "Fields" in module.buffer.__doc__
    assert "values : ndarray[float64] or None" in module.buffer.__doc__
    assert "Ownership: Wrapper-owned" in module.buffer.values.__doc__

    assert module.get_module_values() is None
    module.allocate_module_values(np.int32(3))
    module_values = module.get_module_values()
    np.testing.assert_allclose(module_values, np.array([1.0, 2.0, 3.0], dtype=np.float64))

    module_values[0] = np.float64(10.0)
    assert module.module_values_sum() == np.float64(15.0)
    module.scale_module_values(np.float64(2.0))
    np.testing.assert_allclose(module_values, np.array([20.0, 4.0, 6.0], dtype=np.float64))

    module.deallocate_module_values()
    assert module.get_module_values() is None

    built_values = module.build_values(np.int32(4))
    np.testing.assert_allclose(built_values, np.array([2.0, 4.0, 6.0, 8.0], dtype=np.float64))
    built_values[0] = np.float64(-1.0)
    np.testing.assert_allclose(built_values, np.array([-1.0, 4.0, 6.0, 8.0], dtype=np.float64))
    assert module.build_values(np.int32(0)) is None

    built_matrix = module.build_matrix(np.int32(2), np.int32(2))
    np.testing.assert_allclose(
        built_matrix,
        np.array([[11.0, 21.0], [12.0, 22.0]], dtype=np.float64),
    )
    assert module.build_matrix(np.int32(0), np.int32(2)) is None

    made_values = module.make_values(np.int32(3))
    np.testing.assert_allclose(made_values, np.array([3.0, 6.0, 9.0], dtype=np.float64))
    assert module.make_values(np.int32(0)) is None

    made_matrix = module.make_matrix(np.int32(2), np.int32(2))
    np.testing.assert_allclose(
        made_matrix,
        np.array([[111.0, 121.0], [112.0, 122.0]], dtype=np.float64),
    )
    assert module.make_matrix(np.int32(2), np.int32(0)) is None

    values = module.buffer()
    assert values.values is None
    values.allocate_values(np.int32(3))
    field_view = values.values
    assert field_view.base is values
    np.testing.assert_allclose(field_view, np.array([1.0, 2.0, 3.0], dtype=np.float64))

    field_view[1] = np.float64(8.0)
    assert values.values_sum() == np.float64(12.0)
    values.scale_values(np.float64(0.5))
    np.testing.assert_allclose(field_view, np.array([0.5, 4.0, 1.5], dtype=np.float64))

    with pytest.raises(AttributeError, match="Can't reallocate memory"):
        values.values = np.array([1.0, 2.0], dtype=np.float64)

    retained_view = values.values
    del values
    gc.collect()
    np.testing.assert_allclose(retained_view, np.array([0.5, 4.0, 1.5], dtype=np.float64))

    owner = retained_view.base
    owner.deallocate_values()
    assert owner.values is None


def test_pointer_arrays_use_call_local_inputs_and_snapshot_results(tmp_path: Path):
    module = _build_text_and_import(
        POINTERS_F90_TEXT,
        "fpointers_f90.f90",
        tmp_path,
        {
            "bind_c_fpointers_f90_wrapper.f90",
            "fpointers_f90_wrapper.c",
            "fpointers_f90_wrapper.h",
        },
    )

    values = np.array([1.0, 2.0, 3.0], dtype=np.float64)
    assert module.read_pointer(np.float64(4.5)) == np.float64(4.5)
    assert module.pointer_to_scalar(np.float64(7.25), np.int32(1)) == np.float64(7.25)
    assert module.pointer_to_scalar(np.float64(7.25), np.int32(0)) is None
    assert "pointer_to_scalar(value, use_value) -> float64 | None" in module.pointer_to_scalar.__doc__
    assert "Pointer scalar results are copied into detached Python values." in module.pointer_to_scalar.__doc__
    assert "Unassociated pointer results return None." in module.pointer_to_scalar.__doc__

    assert module.sum_pointer(values) == np.float64(6.0)

    selected = module.pointer_to_values(values, np.int32(1))
    np.testing.assert_allclose(selected, values)
    assert selected.base is not None

    second_snapshot = module.pointer_to_values(values, np.int32(1))
    assert not np.shares_memory(selected, second_snapshot)

    selected[0] = np.float64(99.0)
    np.testing.assert_allclose(values, np.array([1.0, 2.0, 3.0], dtype=np.float64))
    np.testing.assert_allclose(second_snapshot, values)

    assert module.pointer_to_values(values, np.int32(0)) is None
    assert "pointer_to_values(values, use_values) -> ndarray[float64] | None" in module.pointer_to_values.__doc__
    assert "Pointer array results are copied into Python-owned NumPy arrays." in module.pointer_to_values.__doc__
    assert "Unassociated pointer results return None." in module.pointer_to_values.__doc__

    del values
    gc.collect()
    np.testing.assert_allclose(selected, np.array([99.0, 2.0, 3.0], dtype=np.float64))

    with pytest.raises(TypeError):
        module.sum_pointer(np.array([1.0, 2.0, 3.0], dtype=np.float32))


def test_array_valued_function_results_are_python_owned_copies(tmp_path: Path):
    module = _build_text_and_import(
        ARRAY_RESULTS_F90_TEXT,
        "farray_results_f90.f90",
        tmp_path,
        {
            "bind_c_farray_results_f90_wrapper.f90",
            "farray_results_f90_wrapper.c",
            "farray_results_f90_wrapper.h",
        },
    )

    fixed = module.fixed_vector()
    np.testing.assert_allclose(fixed, np.array([1.0, 2.0, 3.0], dtype=np.float64))
    assert fixed.base is not None

    automatic = module.automatic_vector(np.int32(4))
    np.testing.assert_allclose(automatic, np.array([2.0, 4.0, 6.0, 8.0], dtype=np.float64))
    assert automatic.base is not None

    matrix = module.automatic_matrix(np.int32(2), np.int32(3))
    np.testing.assert_allclose(
        matrix,
        np.array([[12.0, 13.0, 14.0], [22.0, 23.0, 24.0]], dtype=np.float64),
    )
    assert matrix.flags.f_contiguous
    assert matrix.base is not None

    cube = module.rank3_cube(np.int32(2), np.int32(2), np.int32(2))
    expected_cube = np.empty((2, 2, 2), dtype=np.float64, order="F")
    for i, j, k in np.ndindex(expected_cube.shape):
        expected_cube[i, j, k] = 100.0 * (i + 1) + 10.0 * (j + 1) + (k + 1)
    np.testing.assert_allclose(cube, expected_cube)
    assert cube.flags.f_contiguous

    rank_results = []
    for rank in range(1, _MAX_WRAPPER_TEST_RANK + 1):
        result = getattr(module, f"rank{rank}_result")()
        shape = (2, *([1] * (rank - 1)))
        expected = np.full(shape, float(rank), dtype=np.float64, order="F")
        expected[(1, *([0] * (rank - 1)))] = float(rank) + 0.5

        assert result.shape == shape
        assert result.flags.f_contiguous
        assert result.base is not None
        np.testing.assert_allclose(result, expected)
        rank_results.append((result, expected))

    zero = module.zero_vector()
    assert zero.shape == (0,)
    assert zero.dtype == np.dtype(np.float64)
    assert zero.base is not None

    zero_alloc = module.zero_alloc_vector()
    assert zero_alloc.shape == (0,)
    assert zero_alloc.base is not None

    allocated = module.maybe_alloc_vector(np.int32(3))
    np.testing.assert_allclose(allocated, np.array([5.0, 10.0, 15.0], dtype=np.float64))
    assert allocated.base is not None
    assert module.maybe_alloc_vector(np.int32(0)) is None

    del module
    gc.collect()
    np.testing.assert_allclose(matrix, np.array([[12.0, 13.0, 14.0], [22.0, 23.0, 24.0]], dtype=np.float64))
    np.testing.assert_allclose(cube, expected_cube)
    for result, expected in rank_results:
        np.testing.assert_allclose(result, expected)


def test_remaining_array_contracts_are_validated_before_fortran_calls(tmp_path: Path):
    module = _build_text_and_import(
        ARRAY_CONTRACTS_F90_TEXT,
        "farray_contracts_f90.f90",
        tmp_path,
        {
            "bind_c_farray_contracts_f90_wrapper.f90",
            "farray_contracts_f90_wrapper.c",
            "farray_contracts_f90_wrapper.h",
        },
    )

    readonly = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float64)
    readonly.setflags(write=False)
    assert module.sum_assumed_size(np.int32(4), readonly) == np.float64(10.0)
    assert module.sum_in(readonly) == np.float64(10.0)

    lower_bound_values = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float64)
    assert module.scale_lower(np.int32(4), lower_bound_values) is None
    np.testing.assert_allclose(lower_bound_values, np.array([2.0, 4.0, 6.0, 8.0], dtype=np.float64))
    with pytest.raises(TypeError, match="incompatible shape at axis 0"):
        module.scale_lower(np.int32(4), np.ones(3, dtype=np.float64))

    with pytest.raises(TypeError, match="writeable"):
        module.bump_inout(readonly)
    readonly_out = np.empty(4, dtype=np.float64)
    readonly_out.setflags(write=False)
    with pytest.raises(TypeError, match="writeable"):
        module.fill_out(readonly_out)

    swapped_dtype = np.dtype(np.float64).newbyteorder("S")
    swapped = np.array([1.0, 2.0], dtype=swapped_dtype)
    with pytest.raises(TypeError, match="native byte order"):
        module.sum_in(swapped)

    storage = np.zeros(8 * 4 + 1, dtype=np.uint8)
    misaligned = storage[1:].view(np.float64)
    assert not misaligned.flags.aligned
    with pytest.raises(TypeError, match="aligned"):
        module.sum_in(misaligned)

    with pytest.raises(TypeError, match="dtype"):
        module.sum_in(np.array([1.0, 2.0], dtype=np.float32))

    empty_rank4 = np.empty((0, 1, 1, 1), dtype=np.float64, order="F")
    empty_rank4_out = np.empty_like(empty_rank4, order="F")
    assert module.shift4(empty_rank4, empty_rank4_out) is empty_rank4_out
    assert empty_rank4_out.shape == empty_rank4.shape

    for rank in range(1, _MAX_WRAPPER_TEST_RANK + 1):
        shape = (2, *([1] * (rank - 1)))
        source = np.asfortranarray(np.arange(np.prod(shape), dtype=np.float64).reshape(shape, order="F"))
        out = np.empty(shape, dtype=np.float64, order="F")

        assert getattr(module, f"shift{rank}")(source, out) is out
        np.testing.assert_allclose(out, source + rank)


def test_assumed_rank_arguments_dispatch_to_runtime_rank(tmp_path: Path):
    module = _build_text_and_import(
        ASSUMED_RANK_F90_TEXT,
        "fassumed_rank_f90.f90",
        tmp_path,
        {
            "bind_c_fassumed_rank_f90_wrapper.f90",
            "fassumed_rank_f90_wrapper.c",
            "fassumed_rank_f90_wrapper.h",
        },
    )

    assert "Rank: 1..15" in module.rank_weighted_sum.__doc__
    assert "Rank: 1..15" in module.bump_assumed_rank.__doc__

    for rank in range(1, _MAX_WRAPPER_TEST_RANK + 1):
        shape = (2, *([1] * (rank - 1)))
        values = np.asfortranarray(np.arange(np.prod(shape), dtype=np.float64).reshape(shape, order="F"))
        expected_sum = np.float64(rank + values.sum())

        assert module.rank_weighted_sum(values) == expected_sum
        assert module.bump_assumed_rank(values) is None
        np.testing.assert_allclose(values, np.arange(np.prod(shape), dtype=np.float64).reshape(shape, order="F") + rank)

    with pytest.raises(TypeError):
        module.rank_weighted_sum(np.float64(1.0))

    rank16 = np.empty((1,) * (_MAX_WRAPPER_TEST_RANK + 1), dtype=np.float64, order="F")
    with pytest.raises(TypeError):
        module.rank_weighted_sum(rank16)


def test_assumed_rank_bridge_dispatches_each_runtime_rank_argument(tmp_path: Path):
    module = _build_text_and_import(
        ASSUMED_RANK_F90_TEXT,
        "fassumed_rank_f90.f90",
        tmp_path,
        {
            "bind_c_fassumed_rank_f90_wrapper.f90",
            "fassumed_rank_f90_wrapper.c",
            "fassumed_rank_f90_wrapper.h",
        },
    )

    for left_rank in range(1, _MAX_WRAPPER_TEST_RANK + 1):
        right_rank = _MAX_WRAPPER_TEST_RANK + 1 - left_rank
        left_shape = (2, *([1] * (left_rank - 1)))
        right_shape = (2, *([1] * (right_rank - 1)))
        left = np.ones(left_shape, dtype=np.float64, order="F")
        right = np.ones(right_shape, dtype=np.float64, order="F")

        assert module.rank_pair_score(left, right) == 100 * left_rank + right_rank + 4


def test_value_and_existing_bind_c_renamed_symbol_use_correct_abi(tmp_path: Path):
    module = _build_text_and_import(
        BIND_VALUE_F90_TEXT,
        "fbind_value_f90.f90",
        tmp_path,
        {
            "bind_c_fbind_value_f90_wrapper.f90",
            "fbind_value_f90_wrapper.c",
            "fbind_value_f90_wrapper.h",
        },
    )

    assert module.plus_value(np.int32(5)) == np.int32(12)
    assert module.double_value(np.int32(6)) == np.int32(12)
    assert module.plus_reference(np.int32(5)) == np.int32(16)
    assert module.scale_real(np.float64(4.0)) == np.float64(10.0)
    assert module.conjugate_value(np.complex128(2.0 + 3.0j)) == np.complex128(2.0 - 3.0j)
    assert bool(module.invert_flag(True)) is False
    assert module.char_code("A") == np.int32(65)

    bridge_source = (tmp_path / "bind_c_fbind_value_f90_wrapper.f90").read_text(encoding="utf-8").lower()
    assert "bind_c_plus_value" not in bridge_source
    assert "bind_c_double_value" not in bridge_source
    assert "bind_c_plus_reference" in bridge_source
    assert "bind_c_scale_real" not in bridge_source
    assert "bind_c_conjugate_value" not in bridge_source
    assert "bind_c_invert_flag" not in bridge_source
    assert "bind_c_char_code" in bridge_source


def test_allocatable_inout_arrays_are_replaced_with_python_owned_results(tmp_path: Path):
    module = _build_text_and_import(
        ALLOCATABLE_INOUT_F90_TEXT,
        "fallocatable_inout_f90.f90",
        tmp_path,
        {
            "bind_c_fallocatable_inout_f90_wrapper.f90",
            "fallocatable_inout_f90_wrapper.c",
            "fallocatable_inout_f90_wrapper.h",
        },
    )

    assert "values : ndarray[float64] or None" in module.replace_values.__doc__
    assert "May be passed as None for initially unallocated storage." in module.replace_values.__doc__
    assert "Mutates: no; returns a replacement array or None" in module.replace_values.__doc__

    allocated = module.replace_values(None, np.int32(1))
    np.testing.assert_allclose(allocated, np.array([1.0, 2.0], dtype=np.float64))
    assert allocated.base is not None

    original = np.array([3.0, 4.0], dtype=np.float64)
    replaced = module.replace_values(original, np.int32(1))
    np.testing.assert_allclose(original, np.array([3.0, 4.0], dtype=np.float64))
    np.testing.assert_allclose(replaced, np.array([13.0, 14.0], dtype=np.float64))

    reallocated = module.replace_values(original, np.int32(3))
    np.testing.assert_allclose(original, np.array([3.0, 4.0], dtype=np.float64))
    np.testing.assert_allclose(reallocated, np.array([3.0, 6.0, 9.0], dtype=np.float64))

    assert module.replace_values(reallocated, np.int32(0)) is None
    assert module.replace_values(None, np.int32(0)) is None

    del allocated, replaced, reallocated
    gc.collect()

    with pytest.raises(TypeError):
        module.replace_values(np.array([1.0], dtype=np.float32), np.int32(1))
    with pytest.raises(TypeError):
        module.replace_values(np.array([[1.0]], dtype=np.float64), np.int32(1))


def test_optional_arguments_drive_fortran_present_behavior(tmp_path: Path):
    module = _build_text_and_import(
        OPTIONAL_F90_TEXT,
        "foptional_f90.f90",
        tmp_path,
        {
            "bind_c_foptional_f90_wrapper.f90",
            "foptional_f90_wrapper.c",
            "foptional_f90_wrapper.h",
        },
    )

    assert "scale : int32 or None" in module.summarize.__doc__
    assert "May be omitted or passed as None." in module.summarize.__doc__

    values = np.array([1.0, 2.0, 3.0], dtype=np.float64)
    item = module.sample()
    item.value = np.int32(7)

    assert module.summarize(np.int32(5)) == np.int32(5)
    assert module.summarize(np.int32(5), np.int32(4)) == np.int32(9)
    assert module.summarize(np.int32(5), None) == np.int32(5)
    assert module.summarize(np.int32(5), scale=None) == np.int32(5)
    assert module.summarize(np.int32(5), values=values) == np.int32(11)
    assert module.summarize(np.int32(5), label="trimmed") == np.int32(12)
    assert module.summarize(np.int32(5), item=item) == np.int32(12)
    assert module.summarize(np.int32(5), item=item, values=values, label="abc") == np.int32(21)
    assert module.summarize(np.int32(5), None, values=values, item=item) == np.int32(18)

    mutable = np.array([1.0, 2.0], dtype=np.float64)
    assert module.mutate_optional() is None
    assert module.mutate_optional(None, np.float64(100.0)) is None
    assert module.mutate_optional(mutable) is None
    np.testing.assert_allclose(mutable, np.array([2.0, 3.0], dtype=np.float64))
    assert module.mutate_optional(mutable, None) is None
    np.testing.assert_allclose(mutable, np.array([3.0, 4.0], dtype=np.float64))
    assert module.mutate_optional(mutable, np.float64(2.5)) is None
    np.testing.assert_allclose(mutable, np.array([5.5, 6.5], dtype=np.float64))

    output = np.empty(3, dtype=np.float64)
    returned_output = module.fill_optional(np.int32(3), output)
    assert returned_output is output
    np.testing.assert_allclose(output, np.array([11.0, 12.0, 13.0], dtype=np.float64))
    assert module.fill_optional(np.int32(3)) is None
    assert module.fill_optional(np.int32(3), None) is None
    assert module.optional_status(np.int32(8)) == (np.int32(8), np.int32(58))

    with pytest.raises(TypeError):
        module.summarize(np.int32(5), scale="bad")
    with pytest.raises(TypeError):
        module.fill_optional(np.int32(3), np.empty(3, dtype=np.float32))


def test_fixed_form_optional_arguments_drive_fortran_present_behavior(tmp_path: Path):
    module = _build_text_and_import(
        OPTIONAL_FIXED_TEXT,
        "foptional_fixed.f",
        tmp_path,
        {
            "bind_c_foptional_fixed_wrapper.f90",
            "foptional_fixed_wrapper.c",
            "foptional_fixed_wrapper.h",
        },
    )

    assert module.optional_scale(np.int32(3)) == np.int32(3)
    assert module.optional_scale(np.int32(3), np.int32(4)) == np.int32(7)
    assert module.optional_scale(np.int32(3), None) == np.int32(3)
    assert module.optional_scale(base=np.int32(3), factor=np.int32(6)) == np.int32(9)


def test_output_arguments_and_multiple_results_follow_python_projection_rules(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    module = _build_and_import(
        OUTPUTS_F90_SOURCE,
        tmp_path,
        {
            "bind_c_foutputs_f90_wrapper.f90",
            "foutputs_f90_wrapper.c",
            "foutputs_f90_wrapper.h",
        },
    )

    assert "scalar_status(n) -> int32" in module.scalar_status.__doc__
    assert "status : int32" in module.scalar_status.__doc__
    assert "fill_vector(n, values) -> ndarray[float64]" in module.fill_vector.__doc__
    assert "Intent: out" in module.fill_vector.__doc__
    assert "Initial contents are ignored." in module.fill_vector.__doc__
    assert "Ownership: Caller-owned" in module.fill_vector.__doc__
    assert "Allocatable array outputs and replacements are copied into Python-owned NumPy arrays." in (
        module.build_alloc.__doc__
    )
    assert "copy adds overhead" in module.build_alloc.__doc__
    assert "make_label() -> str" in module.make_label.__doc__
    assert "make_point(scale) -> output_point" in module.make_point.__doc__

    assert module.scalar_status(np.int32(5)) == np.int32(15)

    vector = np.empty(4, dtype=np.float64)
    returned_vector = module.fill_vector(np.int32(4), vector)
    assert returned_vector is vector
    np.testing.assert_allclose(vector, np.array([2.0, 4.0, 6.0, 8.0], dtype=np.float64))

    matrix = np.empty((2, 3), dtype=np.float64, order="F")
    returned_matrix = module.fill_matrix(np.int32(2), np.int32(3), matrix)
    assert returned_matrix is matrix
    np.testing.assert_allclose(
        matrix,
        np.array([[11.0, 21.0, 31.0], [12.0, 22.0, 32.0]], dtype=np.float64),
    )

    allocated = module.build_alloc(np.int32(3))
    np.testing.assert_allclose(allocated, np.array([3.0, 6.0, 9.0], dtype=np.float64))
    assert allocated.base is not None
    assert module.build_alloc(np.int32(0)) is None

    assert module.with_scalar(np.int32(4)) == (np.int32(8), np.int32(7))

    mixed_vector = np.empty(3, dtype=np.float64)
    mixed_result = module.mixed_outputs(np.int32(3), mixed_vector)
    assert mixed_result[0] == np.float64(3.5)
    assert mixed_result[1] is mixed_vector
    assert mixed_result[2] == np.int32(23)
    np.testing.assert_allclose(mixed_result[1], np.array([101.0, 102.0, 103.0], dtype=np.float64))
    np.testing.assert_allclose(mixed_result[3], np.array([201.0, 202.0, 203.0], dtype=np.float64))

    inout_values = np.array([1.0, 2.0], dtype=np.float64)
    assert module.increment(inout_values) is None
    np.testing.assert_allclose(inout_values, np.array([2.0, 3.0], dtype=np.float64))
    assert module.increment_with_status(inout_values) == np.int32(2)
    np.testing.assert_allclose(inout_values, np.array([4.0, 5.0], dtype=np.float64))

    assert module.make_label() == "RESULT!!"

    point = module.make_point(np.int32(6))
    assert isinstance(point, module.output_point)
    assert point.x == np.float64(6.25)
    assert point.tag == np.int32(46)

    with pytest.raises(TypeError):
        module.scalar_status(np.int32(1), np.int32(0))
    with pytest.raises(TypeError):
        module.build_alloc(np.int32(2), np.empty(2, dtype=np.float64))
    with pytest.raises(TypeError):
        module.fill_vector(np.int32(4), np.empty(4, dtype=np.float32))
    with pytest.raises(TypeError):
        module.fill_vector(np.int32(4), np.empty((4, 1), dtype=np.float64))
    with pytest.raises(TypeError):
        module.fill_vector(np.int32(4), np.empty(3, dtype=np.float64))
    with pytest.raises(TypeError):
        module.fill_matrix(np.int32(2), np.int32(3), np.empty((2, 3), dtype=np.float64, order="C"))

    monkeypatch.setenv("X2PY_WRAPPER_FAIL_ALLOC", "1")
    with pytest.raises(MemoryError, match="copy-return output array"):
        module.build_alloc(np.int32(3))


def test_fortran_wrapper_default_places_extension_beside_source(tmp_path: Path):
    source = tmp_path / SCALAR_LEGACY_SOURCE.name
    shutil.copyfile(SCALAR_LEGACY_SOURCE, source)

    cmd = [sys.executable, "-m", "x2py", str(source), "--json"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)

    build_dir = tmp_path / "__x2py__"
    shared_library = Path(payload["shared_library"])
    assert shared_library.parent == tmp_path
    assert shared_library.exists()
    assert Path(payload["output_dir"]) == build_dir
    assert (build_dir / "bind_c_fmath_wrapper.f90").exists()
    assert not list(tmp_path.glob("*_wrapper.c"))


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        module = _build_and_import(
            SCALAR_LEGACY_SOURCE,
            Path(tmp),
            {
                "bind_c_fmath_wrapper.f90",
                "fmath_wrapper.c",
                "fmath_wrapper.h",
            },
        )
        _assert_fmath_examples(module)
    print("TEST PASSING!!")
