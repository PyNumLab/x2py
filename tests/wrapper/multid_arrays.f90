module multid_arrays
  implicit none

contains

  subroutine scale2_contiguous(a, out)
    implicit none

    real(8), contiguous, intent(in) :: a(:, :)
    real(8), contiguous, intent(out) :: out(:, :)

    out = 2.0d0 * a
  end subroutine scale2_contiguous

  subroutine scale2_strided(a, out)
    implicit none

    real(8), intent(in) :: a(:, :)
    real(8), intent(out) :: out(:, :)

    out = 3.0d0 * a
  end subroutine scale2_strided

  subroutine scale2_explicit(rows, cols, a, out)
    implicit none

    integer, intent(in) :: rows
    integer, intent(in) :: cols
    real(8), intent(in) :: a(rows, cols)
    real(8), intent(out) :: out(rows, cols)

    out = 4.0d0 * a
  end subroutine scale2_explicit

  subroutine shift3_contiguous(a, out)
    implicit none

    real(8), contiguous, intent(in) :: a(:, :, :)
    real(8), contiguous, intent(out) :: out(:, :, :)

    out = a + 10.0d0
  end subroutine shift3_contiguous

  subroutine shift3_strided(a, out)
    implicit none

    real(8), intent(in) :: a(:, :, :)
    real(8), intent(out) :: out(:, :, :)

    out = a + 20.0d0
  end subroutine shift3_strided

end module multid_arrays
