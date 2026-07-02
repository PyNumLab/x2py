
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
