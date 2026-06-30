module scale
contains
  real(8) function scale_scalar(value, factor) result(output)
    real(8), intent(in) :: value
    real(8), intent(in) :: factor
    output = value * factor
  end function scale_scalar
end module scale
