
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
