module compile_time_expression_examples
  use iso_fortran_env, only: int32, int64, real32, real64
  implicit none

  ! ============================================================
  ! 1. Literal constants
  ! ============================================================

  integer, parameter :: lit_int = 42
  real,    parameter :: lit_real = 3.14
  real,    parameter :: lit_double = 1.0d0
  logical, parameter :: lit_logical = .true.
  character(len=*), parameter :: lit_string = "hello"
  complex, parameter :: lit_complex = (1.0, 2.0)

  ! ============================================================
  ! 2. Named constants / parameters
  ! ============================================================

  integer, parameter :: n = 10
  integer, parameter :: m = 5
  real(real64), parameter :: pi = 3.141592653589793_real64

  ! ============================================================
  ! 3. Constant expressions using operators
  ! ============================================================

  integer, parameter :: expr_int = 2 * n + m - 3
  real(real64), parameter :: expr_real = pi / 2.0_real64
  logical, parameter :: expr_logical = (n > m) .and. lit_logical

  ! ============================================================
  ! 4. Kind expressions
  ! ============================================================

  integer, parameter :: default_real_kind = kind(1.0)
  integer, parameter :: double_kind = kind(1.0d0)
  integer, parameter :: selected_i_kind = selected_int_kind(9)
  integer, parameter :: selected_r_kind = selected_real_kind(15, 300)

  integer(kind=selected_i_kind), parameter :: big_int_const = 123456789_selected_i_kind
  real(kind=selected_r_kind), parameter :: precise_real_const = 1.23456789012345_selected_r_kind

  real(kind=real64) :: real64_variable
  integer(kind=int64) :: int64_variable

  ! ============================================================
  ! 5. Intrinsic functions in initialization expressions
  ! ============================================================

  integer, parameter :: abs_value = abs(-12)
  integer, parameter :: max_value = max(3, 7, 2)
  integer, parameter :: min_value = min(3, 7, 2)
  integer, parameter :: mod_value = mod(17, 5)
  integer, parameter :: len_value = len("abcdef")
  integer, parameter :: len_trim_value = len_trim("abc   ")

  integer, parameter :: char_code = iachar("A")
  character(len=1), parameter :: char_from_code = achar(65)

  integer, parameter :: cast_int = int(3.9)
  real(real64), parameter :: cast_real = real(3, kind=real64)
  complex(real64), parameter :: cast_complex = cmplx(1.0_real64, 2.0_real64, kind=real64)

  ! ============================================================
  ! 6. Character length constants
  ! ============================================================

  character(len=5) :: fixed_length_name
  character(len=len("compile")) :: length_from_len
  character(len=n) :: length_from_parameter
  character(len=len_trim("abc   ")) :: length_from_len_trim

  ! ============================================================
  ! 7. Array bounds from compile-time constants
  ! ============================================================

  real(real64) :: array_from_parameter(n)
  real(real64) :: array_from_expression(2 * n + 1)
  integer :: matrix_from_constants(m, n)

  ! ============================================================
  ! 8. Array constructors as constants
  ! ============================================================

  integer, parameter :: small_array(3) = [1, 2, 3]
  integer, parameter :: implied_do_array(5) = [(i, i = 1, 5)]

  ! Need this only for implied-do above
  integer :: i

  ! ============================================================
  ! 9. Derived type with kind and len parameters
  ! ============================================================

  type :: buffer_type(k, n)
     integer, kind :: k
     integer, len  :: n
     real(kind=k) :: values(n)
  end type buffer_type

  type(buffer_type(real64, 4)) :: compile_time_buffer

  ! ============================================================
  ! 10. Derived type constructor in constant expression
  ! ============================================================

  type :: point_type
     real(real64) :: x
     real(real64) :: y
  end type point_type

  type(point_type), parameter :: origin = point_type(0.0_real64, 0.0_real64)
  type(point_type), parameter :: unit_x = point_type(1.0_real64, 0.0_real64)

  ! ============================================================
  ! 11. enum / bind(C) constants
  ! ============================================================

  enum, bind(c)
     enumerator :: color_red = 1
     enumerator :: color_green = 2
     enumerator :: color_blue = 3
  end enum

contains

  ! ============================================================
  ! 12. Runtime specification expression
  !     Allowed in declarations, but not compile-time.
  ! ============================================================

  subroutine runtime_spec_expression_example(runtime_n)
    integer, intent(in) :: runtime_n

    real(real64) :: local_array(runtime_n)

    local_array = 0.0_real64
  end subroutine runtime_spec_expression_example

  ! ============================================================
  ! 13. Character length depending on dummy argument
  !     Runtime specification expression, not compile-time.
  ! ============================================================

  subroutine runtime_character_length_example(input)
    character(len=*), intent(in) :: input

    character(len=len_trim(input)) :: trimmed_copy

    trimmed_copy = trim(input)
  end subroutine runtime_character_length_example

  ! ============================================================
  ! 14. Assumed-length dummy argument
  ! ============================================================

  subroutine assumed_length_example(name)
    character(len=*), intent(in) :: name

    print *, "name length at runtime:", len(name)
  end subroutine assumed_length_example

  ! ============================================================
  ! 15. Inquiry intrinsics in specification expressions
  ! ============================================================

  subroutine inquiry_spec_expression_example(x)
    real(real64), intent(in) :: x(:)

    real(real64) :: copy(size(x))

    copy = x
  end subroutine inquiry_spec_expression_example

  ! ============================================================
  ! 16. present() is runtime, not compile-time
  ! ============================================================

  subroutine present_is_runtime_example(x)
    real(real64), optional, intent(in) :: x

    if (present(x)) then
       print *, "x is present:", x
    else
       print *, "x is absent"
    end if
  end subroutine present_is_runtime_example

  ! ============================================================
  ! 17. PDT kind parameter must be compile-time
  ! ============================================================

  subroutine pdt_kind_parameter_example()
    type(buffer_type(real64, 8)) :: a

    a%values = 0.0_real64
  end subroutine pdt_kind_parameter_example

  ! ============================================================
  ! 18. PDT len parameter may be runtime
  ! ============================================================

  subroutine pdt_len_parameter_runtime_example(runtime_n)
    integer, intent(in) :: runtime_n

    type(buffer_type(real64, runtime_n)) :: a

    a%values = 0.0_real64
  end subroutine pdt_len_parameter_runtime_example

  ! ============================================================
  ! 19. Invalid examples shown as comments
  ! ============================================================

  subroutine invalid_examples(runtime_k)
    integer, intent(in) :: runtime_k

    ! Invalid: kind cannot depend on runtime value.
    !
    ! real(kind=runtime_k) :: x

    ! Invalid: PDT kind parameter cannot be runtime.
    !
    ! type(buffer_type(runtime_k, 10)) :: b

    ! Invalid: parameter value must be compile-time.
    !
    ! integer, parameter :: bad_param = runtime_k

  end subroutine invalid_examples

end module compile_time_expression_examples
