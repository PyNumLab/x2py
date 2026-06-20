
module fmodule_vars_f90
  use iso_c_binding
  implicit none
  private
  public :: nmax, counter, scale, saved_counter
  public :: summarize, scaled_counter, next_local

  integer(c_int), parameter :: nmax = 12
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
