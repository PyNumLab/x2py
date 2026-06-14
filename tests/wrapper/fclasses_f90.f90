module fclasses_f90
  implicit none

  type :: vector
    real(8) :: x
    real(8) :: y
  contains
    procedure :: scale
    procedure :: magnitude
  end type vector

  type :: vector_store
    real(8), allocatable :: values(:)
  contains
    procedure :: allocate_values
    procedure, nopass :: make => make_vector_store
  end type vector_store

contains
  subroutine scale(self, factor)
    class(vector), intent(inout) :: self
    real(8), intent(in) :: factor

    self%x = self%x * factor
    self%y = self%y * factor
  end subroutine scale

  function magnitude(self) result(value)
    class(vector), intent(in) :: self
    real(8) :: value

    value = sqrt(self%x * self%x + self%y * self%y)
  end function magnitude

  subroutine allocate_values(self, n)
    class(vector_store), intent(inout) :: self
    integer(8), intent(in) :: n

    if (allocated(self%values)) then
      deallocate(self%values)
    end if
    allocate(self%values(n))
  end subroutine allocate_values

  function make_vector_store(n, fill_value) result(self)
    integer(8), intent(in) :: n
    real(8), intent(in) :: fill_value
    type(vector_store) :: self

    allocate(self%values(n))
    self%values = fill_value
  end function make_vector_store
end module fclasses_f90
