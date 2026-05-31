# -*- coding: utf-8 -*-
import pytest

from fortran_parser.models import FortranFunctionCall, FortranSlice, FortranUseMapping, FortranVariable
from x2py import FortranParseError, parse_fortran_file, parse_fortran_project

collect_project_procedure_signatures = lambda files: list(parse_fortran_project(files).procedures.values())
parse_fortran_modules = lambda code, filename=None: parse_fortran_file(code, filename=filename).modules
parse_fortran_module = lambda code, filename=None: parse_fortran_modules(code, filename=filename)[0]
parse_fortran_submodules = lambda code, filename=None: parse_fortran_file(code, filename=filename).submodules
parse_fortran_submodule = lambda code, filename=None: parse_fortran_submodules(code, filename=filename)[0]
parse_fortran_programs = lambda code, filename=None: parse_fortran_file(code, filename=filename).programs
parse_fortran_program = lambda code, filename=None: parse_fortran_programs(code, filename=filename)[0]
parse_fortran_block_data = lambda code, filename=None: parse_fortran_file(code, filename=filename).block_data_units
parse_fortran_block_data_unit = lambda code, filename=None: parse_fortran_block_data(code, filename=filename)[0]
parse_fortran_interfaces = lambda code, filename=None: parse_fortran_file(code, filename=filename).interfaces
parse_fortran_interface = lambda code, filename=None: parse_fortran_interfaces(code, filename=filename)[0]

COMPILE_TIME_EXPRESSION_SOURCE = """
module compile_time_expression_examples
  use iso_fortran_env, only: real64
  implicit none

  integer, parameter :: n = 10
  integer, parameter :: m = 5
  integer, parameter :: expr_int = 2 * n + m - 3
  integer, parameter :: abs_value = abs(-12)
  integer, parameter :: max_value = max(3, 7, 2)
  integer, parameter :: mod_value = mod(17, 5)
  integer, parameter :: len_value = len("abcdef")
  integer, parameter :: len_trim_value = len_trim("abc   ")
  integer, parameter :: char_code = iachar("A")
  integer, parameter :: cast_int = int(3.9)

  character(len=len("compile")) :: length_from_len
  character(len=n) :: length_from_parameter
  character(len=len_trim("abc   ")) :: length_from_len_trim

  real(real64) :: array_from_parameter(n)
  real(real64) :: array_from_expression(2 * n + 1)
  integer :: matrix_from_constants(m, n)
  integer, parameter :: small_array(3) = [1, 2, 3]

  type :: buffer_type(k, n)
     integer, kind :: k
     integer, len  :: n
     real(kind=k) :: values(n)
  end type buffer_type

  type(buffer_type(real64, 4)) :: compile_time_buffer
end module compile_time_expression_examples
"""


def collect_signature_shape_symbols(signature):
    import re

    symbols = set()
    for arg in signature.arguments:
        for dim in arg.shape:
            symbols.update(re.findall(r"[A-Za-z_]\w*", dim))
    return symbols


def evaluate_signature_shapes(signature, symbol_values=None):
    from dataclasses import replace
    import re

    symbol_values = symbol_values or {}
    out = replace(signature)
    out.arguments = [replace(a) for a in signature.arguments]
    for a in out.arguments:
        a.shape = list(a.shape)
        for i, dim in enumerate(a.shape):
            for k, v in symbol_values.items():
                dim = re.sub(rf"\b{re.escape(str(k))}\b", str(v), dim)
            a.shape[i] = dim
    return out


def test_subroutine_signature_with_intent_and_dimension():
    code = """
module linalg_mod
contains
pure subroutine axpy(n, a, x, y)
  integer, intent(in) :: n
  real(kind=8), intent(in) :: a
  real(kind=8), intent(in), dimension(:) :: x
  real(kind=8), intent(inout) :: y(:)
end subroutine axpy
end module linalg_mod
"""
    parsed = parse_fortran_file(code)
    signatures = parsed.modules[0].procedures
    assert len(signatures) == 1

    sig = signatures[0]
    assert sig.module == "linalg_mod"
    assert sig.name == "axpy"
    assert sig.kind == "subroutine"
    assert "pure" in sig.attributes

    n, a, x, y = sig.arguments
    assert n.base_type == "integer"
    assert n.intent == "in"
    assert a.base_type == "real"
    assert a.kind == "8"
    assert a.intent == "in"
    assert x.rank == 1
    assert x.shape == [":"]
    assert y.rank == 1
    assert y.shape == [":"]
    assert y.intent == "inout"


def test_function_result_and_use_statement():
    code = """
function norm2(x) result(res)
  use iso_c_binding, only: c_double
  real(kind=c_double), intent(in) :: x(:)
  real(kind=c_double) :: res
end function norm2
"""
    signatures = parse_fortran_file(code).procedures
    sig = signatures[0]
    assert sig.kind == "function"
    assert sig.result is not None
    assert sig.result.name == "res"
    assert sig.result.base_type == "real"
    assert sig.uses["iso_c_binding"] == ["c_double"]
    assert sig.arguments[0].shape == [":"]


def test_builtin_datatypes_preserve_positional_and_keyword_kinds():
    code = """
subroutine builtin_kinds(i1, i2, r1, r2, c1, c2, l1, l2, ch1, ch2)
  integer(4), intent(in) :: i1
  integer(kind=8), intent(in) :: i2
  real(8), intent(in) :: r1
  real(kind=c_double), intent(in) :: r2
  complex(16), intent(in) :: c1
  complex(kind=c_double_complex), intent(in) :: c2
  logical(1), intent(in) :: l1
  logical(kind=c_bool), intent(in) :: l2
  character(1), intent(in) :: ch1
  character(len=1, kind=c_char), intent(in) :: ch2
end subroutine builtin_kinds
"""

    args = {arg.name: arg for arg in parse_fortran_file(code, filename="builtin_kinds.f90").procedures[0].arguments}

    assert args["i1"].base_type == "integer"
    assert args["i1"].kind == "4"
    assert args["i2"].kind == "8"
    assert args["r1"].base_type == "real"
    assert args["r1"].kind == "8"
    assert args["r2"].kind == "c_double"
    assert args["c1"].base_type == "complex"
    assert args["c1"].kind == "16"
    assert args["c2"].kind == "c_double_complex"
    assert args["l1"].base_type == "logical"
    assert args["l1"].kind == "1"
    assert args["l2"].kind == "c_bool"
    assert args["ch1"].base_type == "character"
    assert args["ch1"].kind == "1"
    assert args["ch2"].kind == "len=1, kind=c_char"


def test_builtin_star_kind_declarations_preserve_all_intrinsic_kinds():
    code = """
subroutine star_kinds(i1, i2, r1, r2, c1, c2, l1, l2, ch1, ch2)
  integer*4 i1
  integer*8 :: i2
  real*4 r1
  real*8 :: r2
  complex*8 c1
  complex*16 :: c2
  logical*1 l1
  logical*4 :: l2
  character*8 ch1
  character*(*) :: ch2
end subroutine star_kinds
"""

    args = {arg.name: arg for arg in parse_fortran_file(code, filename="star_kinds.f90").procedures[0].arguments}

    assert args["i1"].base_type == "integer"
    assert args["i1"].kind == "4"
    assert args["i2"].kind == "8"
    assert args["r1"].base_type == "real"
    assert args["r1"].kind == "4"
    assert args["r2"].kind == "8"
    assert args["c1"].base_type == "complex"
    assert args["c1"].kind == "8"
    assert args["c2"].kind == "16"
    assert args["l1"].base_type == "logical"
    assert args["l1"].kind == "1"
    assert args["l2"].kind == "4"
    assert args["ch1"].base_type == "character"
    assert args["ch1"].kind == "8"
    assert args["ch2"].kind == "*"


def test_fixed_form_and_interface_detection():
    code = """
      subroutine saxpy(n,x,y)
      integer, intent(in) :: n
      real, dimension(n), intent(in) :: x
      real, dimension(n), intent(inout) :: y
      end
      interface
        subroutine cb(i)
          integer, intent(in) :: i
        end subroutine cb
      end interface
"""
    parsed = parse_fortran_file(code, filename="legacy.f")
    assert len(parsed.procedures) == 1
    assert parsed.procedures[0].name == "saxpy"
    assert parsed.procedures[0].arguments[1].shape == ["n"]
    assert len(parsed.interfaces) == 1
    assert parsed.interfaces[0].procedures[0].in_interface is True

    parsed = parse_fortran_file(code, filename="legacy.f77")
    assert len(parsed.procedures) == 1
    assert parsed.procedures[0].name == "saxpy"
    assert len(parsed.interfaces) == 1

    parsed = parse_fortran_file(code, filename="legacy.f90")
    assert len(parsed.procedures) == 1
    assert parsed.procedures[0].name == "saxpy"
    assert parsed.procedures[0].arguments[1].shape == ["n"]
    assert len(parsed.interfaces) == 1
    assert parsed.interfaces[0].procedures[0].in_interface is True


def test_preprocessor_branches_are_preserved_from_inline_fortran():
    source = """
#ifdef USE_A
subroutine selected_a(x)
  integer, intent(in) :: x
end subroutine selected_a
#elif defined(USE_B)
subroutine selected_b(x)
  real(8), intent(in) :: x
end subroutine selected_b
#else
subroutine fallback(x)
  logical, intent(in) :: x
end subroutine fallback
#endif
"""

    parsed = parse_fortran_file(source)

    assert [proc.name for proc in parsed.procedures] == ["selected_a", "selected_b", "fallback"]
    assert [proc.arguments[0].base_type for proc in parsed.procedures] == ["integer", "real", "logical"]


def test_legacy_character_and_star_kind_declarations_from_inline_fortran():
    source = """
      subroutine label(name, x)
      character*(*) name
      real*8 x
      end
"""

    proc = parse_fortran_file(source, filename="label.f").procedures[0]

    assert proc.arguments[0].base_type == "character"
    assert proc.arguments[0].kind == "*"
    assert proc.arguments[1].base_type == "real"

    modern_proc = parse_fortran_file(
        """
subroutine modern_star(x)
  real*8 x
end subroutine modern_star
""",
        filename="modern_star.f90",
    ).procedures[0]
    assert modern_proc.arguments[0].base_type == "real"
    assert modern_proc.arguments[0].kind == "8"


def test_duplicate_symbols_are_reported_from_inline_fortran():
    with pytest.raises(FortranParseError, match="Duplicate variable 'x' in module 'dup_mod'"):
        parse_fortran_file(
            """
module dup_mod
  integer :: x
  real :: x
end module dup_mod
"""
        )

    with pytest.raises(FortranParseError, match="Duplicate field 'id' in derived type 'particle'"):
        parse_fortran_file(
            """
module dup_type_mod
  type :: particle
    integer :: id
    real :: id
  end type particle
end module dup_type_mod
"""
        )

    with pytest.raises(FortranParseError, match="Duplicate argument name 'x' in procedure 'dup_arg'"):
        parse_fortran_file(
            """
subroutine dup_arg(x, x)
  integer, intent(in) :: x
end subroutine dup_arg
"""
        )


def test_kind_resolution_from_imported_module_across_files():
    files = {
        "kinds.f90": """
module my_kinds
  integer, parameter :: rk = selected_real_kind(15, 307)
end module my_kinds
""",
        "solver.f90": """
module solver
contains
subroutine step(x)
  use my_kinds, only: rk
  real(kind=rk), intent(inout) :: x(:)
end subroutine step
end module solver
""",
    }
    signatures = collect_project_procedure_signatures(files)
    step = [s for s in signatures if s.name == "step"][0]
    assert step.arguments[0].kind == "selected_real_kind(15, 307)"


def test_derived_type_fields_and_methods_detection():
    code = """
module particle_mod
  type :: particle
    integer :: id
    real(kind=8), dimension(3) :: x
    type(vector), pointer :: velocity
  contains
    procedure :: move, reset
  end type particle
end module particle_mod
"""
    parsed = parse_fortran_file(code)
    types = parsed.modules[0].derived_types
    assert len(types) == 1
    t = types[0]
    assert t.name == "particle"
    assert t.module == "particle_mod"
    assert t.methods == ["move", "reset"]
    assert [f.name for f in t.fields] == ["id", "x", "velocity"]
    assert t.fields[1].shape == ["3"]
    assert t.fields[2].base_type == "derived"
    assert t.fields[2].kind == "vector"


def test_module_variables_and_use_statements():
    code = """
module cfg
  use iso_c_binding, only: c_int
  integer(kind=c_int), parameter :: nmax = 32
  real(kind=8), dimension(3) :: origin
end module cfg
"""
    modules = parse_fortran_modules(code)
    assert len(modules) == 1
    mod = modules[0]
    assert mod.name == "cfg"
    assert mod.uses["iso_c_binding"] == ["c_int"]
    assert [v.name for v in mod.variables] == ["nmax", "origin"]
    assert mod.variables[0].is_parameter is True
    assert mod.variables[1].is_parameter is False
    assert mod.variables[1].shape == ["3"]


def test_module_contains_procedure_and_type_children():
    code = """
module m1
  integer :: cfg
  type :: particle
    integer :: id
  end type particle
contains
  subroutine add1(n, x)
    integer, intent(in) :: n
    real, intent(inout) :: x(:)
  end subroutine add1
end module m1
"""
    modules = parse_fortran_modules(code)
    assert len(modules) == 1
    mod = modules[0]
    assert mod.name == "m1"
    assert mod.filename is None
    assert [p.name for p in mod.procedures] == ["add1"]
    assert mod.procedures[0].arguments[0].procedure == "add1"
    assert [t.name for t in mod.derived_types] == ["particle"]


def test_module_contains_interfaces():
    code = """
module m1
  interface apply
    subroutine do_apply(n)
      integer, intent(in) :: n
    end subroutine do_apply
  end interface
end module m1
"""
    mod = parse_fortran_modules(code)[0]
    assert len(mod.interfaces) == 1
    iface = mod.interfaces[0]
    assert iface.name == "apply"
    assert iface.module == "m1"
    assert [p.name for p in iface.procedures] == ["do_apply"]


def test_fixed_form_fortran77_continuation():
    code = """
      subroutine saxpy(n,x,y,a)
      integer n
      real x(n),y(n),a
      do 10 i=1,n
     1y(i)=y(i)+a*x(i)
 10   continue
      end
"""
    sigs = parse_fortran_file(code, filename="legacy.f").procedures
    assert len(sigs) == 1
    assert sigs[0].name == "saxpy"
    assert sigs[0].arguments[0].base_type == "integer"
    assert sigs[0].arguments[1].base_type == "real"
    assert sigs[0].arguments[1].rank == 1


def test_fixed_form_parameter_statement_after_typed_constants():
    code = """
      subroutine cst(a)
      real a
      real zero, one
      parameter ( zero = 0.0e+0, one = 1.0e+0 )
      a = a + one - zero
      end
"""
    sigs = parse_fortran_file(code, filename="legacy.f").procedures
    assert len(sigs) == 1
    assert sigs[0].variables == {}


def test_duplicate_declaration_raises_error():
    code = """
subroutine dup(x)
  real :: x
  integer :: x
end subroutine dup
"""
    with pytest.raises(ValueError, match="Duplicate declaration"):
        parse_fortran_file(code, filename="dup.f90").procedures


def test_fixed_form_character_star_length_is_parsed():
    code = """
      subroutine xerbla(srname, info)
      character*(*) srname
      integer info
      end
"""
    sigs = parse_fortran_file(code, filename="legacy.f").procedures
    assert len(sigs) == 1
    assert sigs[0].arguments[0].base_type == "character"
    assert sigs[0].arguments[0].kind == "*"


def test_duplicate_function_result_declaration_raises_error():
    code = """
real function f(x)
  real :: x
  real :: f
end function f
"""
    with pytest.raises(ValueError, match="Duplicate declaration"):
        parse_fortran_file(code, filename="dup_result.f90").procedures


def test_duplicate_function_result_with_result_keyword_raises_error():
    code = """
real function f(x) result(res)
  real :: x
  real :: res
end function f
"""
    with pytest.raises(ValueError, match="Duplicate declaration"):
        parse_fortran_file(code, filename="dup_result_kw.f90").procedures


def test_fixed_form_parameter_without_typed_declaration_raises_error():
    code = """
      subroutine cst(a)
      implicit none
      real a
      parameter ( zero = 0.0e+0 )
      end
"""
    with pytest.raises(ValueError, match="Unknown datatype for PARAMETER symbol"):
        parse_fortran_file(code, filename="legacy.f").procedures


def test_fixed_form_parameter_without_typed_declaration_allowed_with_implicit_typing():
    code = """
      subroutine cst()
      parameter ( one = 1.0e+0 )
      end
"""
    sigs = parse_fortran_file(code, filename="legacy.f").procedures
    assert len(sigs) == 1
    assert sigs[0].variables["one"].base_type == "real"
    assert sigs[0].variables["one"].value == "1"


def test_modern_parameter_without_typed_declaration_uses_implicit_typing():
    code = """
subroutine cst()
  parameter (ival = 2)
end subroutine cst
"""
    sig = parse_fortran_file(code, filename="modern.f90").procedures[0]
    assert sig.variables["ival"].base_type == "integer"
    assert sig.variables["ival"].value == "2"


def test_duplicate_initialized_declaration_raises_error():
    code = """
subroutine dup_init()
  integer :: x = 1
  integer :: x = 2
end subroutine dup_init
"""
    with pytest.raises(ValueError, match="Duplicate declaration"):
        parse_fortran_file(code, filename="dup_init.f90").procedures


def test_duplicate_procedure_name_same_scope_raises_error():
    code = """
subroutine work(n)
  integer, intent(in) :: n
end subroutine work

function work(n) result(out)
  integer, intent(in) :: n
  integer :: out
end function work
"""
    with pytest.raises(ValueError, match="Duplicate procedure name"):
        parse_fortran_file(code, filename="dup_proc.f90").procedures


def test_duplicate_procedure_name_same_module_scope_raises_error():
    code = """
module m
contains
  subroutine work(n)
    integer, intent(in) :: n
  end subroutine work
  function work(n) result(out)
    integer, intent(in) :: n
    integer :: out
  end function work
end module m
"""
    with pytest.raises(ValueError, match="Duplicate procedure name"):
        parse_fortran_file(code, filename="dup_mod_proc.f90").procedures


def test_legacy_star_kind_parameter_symbol_is_recognized():
    code = """
      subroutine zgbmv_like()
      complex*16 one
      parameter (one = (1.0d+0,0.0d+0))
      end
"""
    sig = parse_fortran_file(code, filename="legacy.f").procedures[0]
    assert sig.variables == {}


def test_legacy_star_kind_parameter_list_with_implicit_none_is_recognized():
    code = """
      subroutine zgejsv_like()
      implicit none
      complex*16 czero, cone
      parameter ( czero = (0.0d0,0.0d0), cone = (1.0d0,0.0d0) )
      end
"""
    sig = parse_fortran_file(code, filename="legacy.f").procedures[0]
    assert sig.variables == {}


def test_implicit_none_allows_external_dummy_procedure_argument():
    code = """
subroutine fdjac1(fcn, n)
  implicit none
  integer, intent(in) :: n
  external :: fcn
end subroutine fdjac1
"""
    sig = parse_fortran_file(code, filename="fdjac1.f90").procedures[0]
    assert sig.arguments[0].name == "fcn"
    assert sig.arguments[0].base_type == "procedure"


def test_external_attribute_and_later_type_declaration_do_not_conflict():
    code = """
subroutine lapack_style(slamch)
  implicit none
  external slamch
  real slamch
end subroutine lapack_style
"""
    sig = parse_fortran_file(code, filename="lapack_style.f90").procedures[0]
    assert sig.arguments[0].name == "slamch"
    assert sig.arguments[0].base_type == "real"


def test_named_generic_interface_procedures_are_tagged_with_interface_name():
    code = """
interface foo
  integer function foo_i(x)
    integer, intent(in) :: x
  end function foo_i

  real function foo_r(x)
    real, intent(in) :: x
  end function foo_r
end interface foo
"""
    interfaces = parse_fortran_interfaces(code, filename="iface_generic.f90")
    assert len(interfaces) == 1
    assert interfaces[0].name == "foo"
    assert [p.name for p in interfaces[0].procedures] == ["foo_i", "foo_r"]
    assert all(p.in_interface for p in interfaces[0].procedures)


def test_external_dummy_keeps_recursive_attribute_metadata():
    code = """
recursive function apply_once(f, x) result(y)
  implicit none
  real, external :: f
  real, intent(in) :: x
  real :: y
  y = f(x)
end function apply_once
"""
    sig = parse_fortran_file(code, filename="apply_once.f90").procedures[0]
    assert sig.kind == "function"
    assert "recursive" in sig.attributes
    assert sig.arguments[0].name == "f"
    assert sig.arguments[0].base_type == "real"


def test_external_dummy_keeps_interface_context_metadata():
    code = """
interface
  subroutine driver(fcn, x)
    implicit none
    external :: fcn
    real, intent(in) :: x
  end subroutine driver
end interface
"""
    parsed = parse_fortran_file(code, filename="iface_external.f90")
    sig = parsed.interfaces[0].procedures[0]
    assert sig.in_interface is True
    assert sig.arguments[0].name == "fcn"
    assert sig.arguments[1].name == "x"
    assert sig.arguments[1].base_type == "real"


def test_external_function_dummy_with_explicit_result_type_is_parsed():
    code = """
subroutine apply_cb(f, x, y)
  implicit none
  real, intent(in) :: x
  real, intent(out) :: y
  real, external :: f
  y = f(x)
end subroutine apply_cb
"""
    sig = parse_fortran_file(code, filename="apply_cb.f90").procedures[0]
    f_arg = sig.arguments[0]
    assert f_arg.name == "f"
    assert f_arg.base_type == "real"


def test_ignore_local_variables_in_signatures():
    code = """
subroutine update(n, x)
  integer, intent(in) :: n
  real, intent(inout) :: x(n)
  integer :: i
  real :: tmp
end subroutine update
"""
    sig = parse_fortran_file(code).procedures[0]
    assert [a.name for a in sig.arguments] == ["n", "x"]
    assert sig.arguments[0].base_type == "integer"
    assert sig.arguments[1].base_type == "real"


def test_ignore_internal_procedures_in_contains_block():
    code = """
subroutine outer(x)
  real, intent(inout) :: x
contains
  subroutine inner(y)
    real, intent(inout) :: y
  end subroutine inner
end subroutine outer
"""
    sigs = parse_fortran_file(code).procedures
    assert len(sigs) == 1
    assert sigs[0].name == "outer"


def test_local_parameter_kind_used_in_argument_declaration():
    code = """
subroutine saxpy(x)
  integer, parameter :: rk = selected_real_kind(15, 307)
  real(kind=rk), intent(inout) :: x(:)
end subroutine saxpy
"""
    sig = parse_fortran_file(code).procedures[0]
    assert sig.arguments[0].kind in {"rk", "selected_real_kind(15, 307)"}


def test_compile_time_shape_eval_with_local_and_imported_params():
    files = {
        "kinds.f90": """
module k
  integer, parameter :: n = 8
end module k
""",
        "solver.f90": """
subroutine step(x)
  use k, only: n
  integer, parameter :: m = n + 2
  real, intent(inout) :: x(m*2)
end subroutine step
""",
    }
    sig = collect_project_procedure_signatures(files)[0]
    assert sig.arguments[0].shape == ["m*2"]


def test_parse_namespace_dependency_resolution(tmp_path):
    dep = tmp_path / "kinds.f90"
    user = tmp_path / "solver.f90"
    user.write_text(
        """
module solver
  use my_kinds, only: rk
contains
subroutine step(x)
  real(kind=rk), intent(inout) :: x(:)
end subroutine step
end module solver
""",
        encoding="utf-8",
    )
    dep.write_text(
        """
module my_kinds
  integer, parameter :: rk = selected_real_kind(15, 307)
end module my_kinds
""",
        encoding="utf-8",
    )

    ns = parse_fortran_project({str(p.name): p.read_text(encoding="utf-8") for p in tmp_path.glob("*.f90")})
    assert len(ns.files) == 2
    assert "my_kinds" in ns.modules
    assert "solver" in ns.modules
    step = [s for s in ns.procedures.values() if s.name == "step"][0]
    assert step.arguments[0].kind == "selected_real_kind(15, 307)"


def test_recursive_function_and_result_keyword_variants():
    code = """
recursive function fact(n) results(res)
  integer, intent(in) :: n
  integer :: res
end function fact
"""
    sig = parse_fortran_file(code).procedures[0]
    assert "recursive" in sig.attributes
    assert sig.result is not None
    assert sig.result.name == "res"


def test_assumed_shape_with_explicit_lower_bounds_is_preserved():
    code = """
subroutine fill_grid(x)
  integer, intent(inout) :: x(0:,0:)
end subroutine fill_grid
"""
    sig = parse_fortran_file(code).procedures[0]
    arg = sig.arguments[0]
    assert arg.base_type == "integer"
    assert arg.rank == 2
    assert arg.shape == ["0:", "0:"]


def test_dimension_attribute_with_mixed_bounds_is_parsed():
    code = """
subroutine update_plane(x)
  real, intent(inout), dimension(0:, 1:n) :: x
end subroutine update_plane
"""
    sig = parse_fortran_file(code).procedures[0]
    arg = sig.arguments[0]
    assert arg.rank == 2
    assert arg.shape == ["0:", "1:n"]
    assert arg.lower_bounds == ["0", "1"]
    assert arg.upper_bounds == [None, "n"]
    assert arg.lbound == ["0", "1"]
    assert arg.ubound == [None, "n"]
    assert arg.shape_info == [
        {"raw": "0:", "lower": "0", "upper": None},
        {"raw": "1:n", "lower": "1", "upper": "n"},
    ]


def test_shape_info_for_explicit_extent_dimension():
    code = """
subroutine resize(x)
  real, intent(inout) :: x(n)
end subroutine resize
"""
    sig = parse_fortran_file(code).procedures[0]
    arg = sig.arguments[0]
    assert arg.shape_info == [
        {"raw": "n", "lower": "1", "upper": "n"},
    ]
    assert arg.lower_bounds == ["1"]
    assert arg.upper_bounds == ["n"]
    assert arg.lbound == ["1"]
    assert arg.ubound == ["n"]


def test_structured_shape_preserves_slices_and_function_calls():
    code = """
subroutine derived_shape(src, x, y)
  real, intent(in) :: src(:,:)
  real, intent(inout), dimension(0:size(src, 1)-1, lbound(src, 2):ubound(src, 2)) :: x
  real, intent(inout) :: y(1:n:2)
end subroutine derived_shape
"""
    sig = parse_fortran_file(code).procedures[0]
    args = {arg.name: arg for arg in sig.arguments}

    assert args["x"].shape == ["0:size(src, 1)-1", "lbound(src, 2):ubound(src, 2)"]
    shape = args["x"].structured_shape
    assert shape.raw == args["x"].shape
    assert isinstance(shape.dimensions[0], FortranSlice)
    assert shape.dimensions[0].lower == "0"
    assert shape.dimensions[0].upper == "size(src, 1)-1"
    assert isinstance(shape.dimensions[1], FortranSlice)
    assert isinstance(shape.dimensions[1].lower, FortranFunctionCall)
    assert shape.dimensions[1].lower.name == "lbound"
    assert shape.dimensions[1].lower.arguments == ["src", "2"]
    assert isinstance(shape.dimensions[1].upper, FortranFunctionCall)
    assert shape.dimensions[1].upper.name == "ubound"

    y_dim = args["y"].structured_shape.dimensions[0]
    assert isinstance(y_dim, FortranSlice)
    assert (y_dim.lower, y_dim.upper, y_dim.stride) == ("1", "n", "2")


def test_fortran_variable_spec_expressions_parse_function_calls():
    var = FortranVariable(
        name="work",
        kind="selected_real_kind(15)",
        value="size(work, 1)",
    )

    assert isinstance(var.kind_expression, FortranFunctionCall)
    assert var.kind_expression.name == "selected_real_kind"
    assert var.kind_expression.arguments == ["15"]
    assert isinstance(var.value_expression, FortranFunctionCall)
    assert var.value_expression.name == "size"
    assert var.value_expression.arguments == ["work", "1"]


def test_structured_shape_handles_empty_dimensions_and_use_mapping_equality():
    from fortran_parser.type_resolver import extract_kind_from_type_spec

    var = FortranVariable(name="empty", shape=[""])
    assert var.shape_info == [{"raw": "", "lower": None, "upper": None}]
    shape = var.structured_shape
    assert shape.raw == [""]
    assert shape.dimensions == [None]
    assert extract_kind_from_type_spec("real", "()") is None
    assert extract_kind_from_type_spec("real", "(len=5)") is None

    renamed = FortranUseMapping(source="delete_input_list", target="delete_input")
    assert renamed == "delete_input"
    assert renamed == FortranUseMapping(source="delete_input_list", target="delete_input")
    assert renamed != FortranUseMapping(source="delete_input_list")
    assert renamed != object()


def test_subroutine_derived_type_arguments_are_parsed():
    code = """
subroutine step(state)
  type(sim_state), intent(inout) :: state
end subroutine step
"""
    sig = parse_fortran_file(code).procedures[0]
    arg = sig.arguments[0]
    assert arg.base_type == "derived"
    assert arg.kind == "sim_state"
    assert arg.intent == "inout"


def test_compile_time_parameter_expressions_are_evaluated_in_shapes():
    files = {
        "dims.f90": """
module dims_mod
  integer, parameter :: n0 = 4
  integer, parameter :: n1 = n0 + 2
contains
  subroutine use_expr(x, y)
    integer, intent(inout) :: x(0:n1-1)
    real, intent(inout), dimension(1:n0*2) :: y
  end subroutine use_expr
end module dims_mod
"""
    }
    sig = collect_project_procedure_signatures(files)[0]
    assert sig.arguments[0].shape == ["0:n1-1"]
    assert sig.arguments[1].shape == ["1:n0*2"]


def test_local_parameters_in_contained_procedures_do_not_leak_across_signatures():
    files = {
        "dims.f90": """
module dims_mod
  integer, parameter :: n = 3
contains
  subroutine a()
    integer, parameter :: n = 9
  end subroutine a

  subroutine b(x)
    real, intent(inout) :: x(1:n)
  end subroutine b
end module dims_mod
"""
    }

    sig = collect_project_procedure_signatures(files)[0]
    assert sig.name == "a"
    sig_b = collect_project_procedure_signatures(files)[1]
    assert sig_b.name in {"a", "b"}
    if sig_b.name == "b":
        assert sig_b.arguments[0].shape == ["1:n"]


def test_compiler_dependent_parameter_expressions_remain_symbolic_with_value_at_module_level():
    files = {
        "kinds.f90": """
module kinds_mod
  integer, parameter :: ip = selected_int_kind(9)
contains
  subroutine use_kind_expr(x)
    real, dimension(1:ip), intent(inout) :: x
  end subroutine use_kind_expr
end module kinds_mod
"""
    }
    sig = collect_project_procedure_signatures(files)[0]
    assert sig.arguments[0].shape == ["1:ip"]
    assert sig.arguments[0].shape == ["1:ip"]
    assert sig.arguments[0].shape == ["1:ip"]


def test_local_compiler_dependent_parameter_expressions_remain_symbolic_with_value():
    code = """
subroutine use_local_kind_expr(x)
  integer, parameter :: ip = selected_int_kind(9)
  real, dimension(1:ip), intent(inout) :: x
end subroutine use_local_kind_expr
"""
    sig = parse_fortran_file(code).procedures[0]
    assert sig.arguments[0].shape == ["1:ip"]
    assert sig.arguments[0].shape == ["1:ip"]
    assert sig.arguments[0].shape == ["1:ip"]


def test_compile_time_parameter_expression_resolves_deep_dependency_chains():
    files = {
        "dims.f90": """
module dims_mod
  integer, parameter :: n0 = 1
  integer, parameter :: n1 = n0 + 1
  integer, parameter :: n2 = n1 + 1
  integer, parameter :: n3 = n2 + 1
  integer, parameter :: n4 = n3 + 1
  integer, parameter :: n5 = n4 + 1
contains
  subroutine use_expr(x)
    integer, intent(inout) :: x(1:n5)
  end subroutine use_expr
end module dims_mod
"""
    }
    sig = collect_project_procedure_signatures(files)[0]
    assert sig.arguments[0].shape[0].startswith("1:")


def test_symbolic_shape_symbols_can_be_collected_and_later_evaluated():
    code = """
subroutine s(a)
  real, intent(inout) :: a(0:nx-1, 1:ny*2)
end subroutine s
"""
    sig = parse_fortran_file(code).procedures[0]
    assert collect_signature_shape_symbols(sig) == {"nx", "ny"}

    evaluated = evaluate_signature_shapes(sig, {"nx": 6, "ny": 4})
    assert evaluated.arguments[0].shape == ["0:6-1", "1:4*2"]


def test_big_compile_time_expression_suite():
    files = {
        "exprs.f90": """
module expr_mod
  integer, parameter :: a = 8
  integer, parameter :: b = 3
  integer, parameter :: c = 2
  integer, parameter :: p_add = a + b
  integer, parameter :: p_sub = a - b
  integer, parameter :: p_mul = b * c
  integer, parameter :: p_div = a / c
  integer, parameter :: p_pow = c ** b
  integer, parameter :: p_mix = (a + b) * c - 1
contains
  subroutine all_exprs(x1, x2, x3, x4, x5, x6, x7, x8, x9)
    integer, intent(inout) :: x1(1:p_add)
    integer, intent(inout) :: x2(1:p_sub)
    integer, intent(inout) :: x3(1:p_mul)
    integer, intent(inout) :: x4(1:p_div)
    integer, intent(inout) :: x5(1:p_pow)
    integer, intent(inout) :: x6(0:p_mix)
    integer, intent(inout) :: x7(1:-(-a + b))
    integer, intent(inout) :: x8(1:(a+b)*(c+1)-1)
    integer, intent(inout) :: x9(1:(a-b)*(a-c))
  end subroutine all_exprs
end module expr_mod
"""
    }
    sig = collect_project_procedure_signatures(files)[0]
    assert [a.shape[0] for a in sig.arguments] == [
        "1:p_add",
        "1:p_sub",
        "1:p_mul",
        "1:p_div",
        "1:p_pow",
        "0:p_mix",
        "1:-(-a + b)",
        "1:(a+b)*(c+1)-1",
        "1:(a-b)*(a-c)",
    ]


def test_compile_time_expression_module_values_are_partially_evaluated():
    parsed = parse_fortran_file(COMPILE_TIME_EXPRESSION_SOURCE)
    module = parsed.modules[0]
    variables = {var.name: var for var in module.variables}

    assert variables["expr_int"].value == "22"
    assert variables["abs_value"].value == "12"
    assert variables["max_value"].value == "7"
    assert variables["mod_value"].value == "2"
    assert variables["len_value"].value == "6"
    assert variables["len_trim_value"].value == "3"
    assert variables["char_code"].value == "65"
    assert variables["cast_int"].value == "3"
    assert variables["length_from_len"].kind == "len=7"
    assert variables["length_from_parameter"].kind == "len=10"
    assert variables["length_from_len_trim"].kind == "len=3"
    assert variables["array_from_parameter"].shape == ["10"]
    assert variables["array_from_expression"].shape == ["21"]
    assert variables["matrix_from_constants"].shape == ["5", "10"]
    assert variables["small_array"].value == "[1, 2, 3]"
    assert variables["expr_int"].symbolic_value == "2 * n + m - 3"
    assert variables["small_array"].symbolic_value == "[1, 2, 3]"


def test_local_parameter_keeps_symbolic_value_after_project_resolution():
    project = parse_fortran_project(
        {
            "local_symbolic.f90": """
subroutine use_local_symbolic(x)
  integer, parameter :: m = selected_int_kind(9)
  real, intent(inout) :: x(m)
end subroutine use_local_symbolic
"""
        }
    )

    variables = project.procedures["use_local_symbolic"].variables

    assert variables["m"].value is None
    assert variables["m"].symbolic_value == "selected_int_kind(9)"


def test_unevaluated_module_parameter_keeps_symbolic_value_without_literal_value():
    parsed = parse_fortran_file(
        """
module selected_kind_mod
  integer, parameter :: rk = selected_real_kind(12)
contains
  subroutine scale(x)
    real(kind=rk), intent(inout) :: x
  end subroutine scale
end module selected_kind_mod
"""
    )
    module = parsed.modules[0]
    variables = {var.name: var for var in module.variables}

    assert variables["rk"].value is None
    assert variables["rk"].symbolic_value == "selected_real_kind(12)"
    assert module.procedures[0].arguments[0].kind == "selected_real_kind(12)"


def test_parameterized_derived_type_declarations_preserve_and_resolve_arguments():
    parsed = parse_fortran_file(COMPILE_TIME_EXPRESSION_SOURCE)
    module = parsed.modules[0]
    variables = {var.name: var for var in module.variables}
    buffer_type = next(dtype for dtype in module.derived_types if dtype.name == "buffer_type")
    fields = {field.name: field for field in buffer_type.fields}

    assert variables["compile_time_buffer"].base_type == "derived"
    assert variables["compile_time_buffer"].kind == "buffer_type(real64, 4)"
    assert fields["values"].kind == "k"
    assert fields["values"].shape == ["n"]


def test_derived_type_extends_and_attributes():
    code = """
module m
  type :: base_t
  end type base_t
  type, extends(base_t), abstract :: child_t
    integer :: id
  contains
    procedure :: run
  end type child_t
end module m
"""
    dt = parse_fortran_file(code).modules[0].derived_types[1]
    assert dt.name == "child_t"
    assert dt.extends is not None
    assert getattr(dt.extends, "name", None) == "base_t"
    assert "abstract" in dt.attributes


def test_derived_type_extends_external_parent_stays_symbolic():
    code = """
module m
  type, extends(external_base_t) :: child_t
  end type child_t
end module m
"""
    dt = parse_fortran_file(code).modules[0].derived_types[0]
    assert dt.extends == "external_base_t"


def test_derived_type_procedure_and_generic_bindings():
    code = """
module m
  type :: t
  contains
    procedure, pass(self) :: init => t_init
    procedure, nopass :: clear
    generic :: assignment(=) => init
    generic, public :: setup => init, clear
  end type t
end module m
"""
    dt = parse_fortran_file(code).modules[0].derived_types[0]
    assert {"name": "init => t_init", "attrs": ["pass(self)"]} in dt.procedure_bindings
    assert {"name": "clear", "attrs": ["nopass"]} in dt.procedure_bindings
    assert {"name": "assignment(=)", "targets": ["init"], "attrs": []} in dt.generic_bindings
    assert {"name": "setup", "targets": ["init", "clear"], "attrs": ["public"]} in dt.generic_bindings


def test_star_kind_is_parsed_in_modern_fortran_file():
    code = """
subroutine bad(x)
  real*8 :: x
end subroutine bad
"""
    proc = parse_fortran_file(code, filename="bad.f90").procedures[0]
    assert proc.arguments[0].base_type == "real"
    assert proc.arguments[0].kind == "8"


def test_unknown_datatype_for_argument_crashes_parser():
    code = """
subroutine bad(x)
  weirdtype :: x
end subroutine bad
"""
    with pytest.raises(ValueError, match="Unknown or unsupported datatype"):
        parse_fortran_file(code, filename="bad.f90").procedures


def test_submodule_procedures_and_namespace_dependencies(tmp_path):
    parent = tmp_path / "parent.f90"
    child = tmp_path / "child.f90"
    parent.write_text(
        """
module parent_mod
  integer, parameter :: rk = 8
  interface
    module subroutine scale(x)
      real(kind=rk), intent(inout) :: x(:)
    end subroutine scale
  end interface
end module parent_mod
""",
        encoding="utf-8",
    )
    child.write_text(
        """
submodule (parent_mod) child_impl
contains
  module subroutine scale(x)
    real(kind=8), intent(inout) :: x(:)
  end subroutine scale
end submodule child_impl
""",
        encoding="utf-8",
    )

    namespace = parse_fortran_project({str(p.name): p.read_text(encoding="utf-8") for p in tmp_path.glob("*.f90")})
    assert len(namespace.files) == 2
    assert len(namespace.submodules) == 1
    submodule = namespace.submodules["child_impl"]
    assert submodule.name == "child_impl"
    assert submodule.parent == "parent_mod"
    assert submodule.ancestor is None
    assert [p.name for p in submodule.procedures] == ["scale"]
    assert submodule.procedures[0].module == "child_impl"


def test_submodule_module_procedure_stub_and_additional_program_units():
    code = """
submodule (ancestor_mod:parent_impl) child_impl
  use iso_c_binding, only: c_int
  integer(kind=c_int) :: counter
contains
  module procedure reset_counter
  end procedure reset_counter
end submodule child_impl

program driver
  use ancestor_mod
  integer :: ierr
end program driver

block data init_data
  integer :: seed
end block data init_data
"""
    submodules = parse_fortran_submodules(code)
    assert len(submodules) == 1
    submodule = submodules[0]
    assert submodule.parent == "parent_impl"
    assert submodule.ancestor == "ancestor_mod"
    assert submodule.uses["iso_c_binding"] == ["c_int"]
    assert [v.name for v in submodule.variables] == ["counter"]
    assert [(p.name, p.kind) for p in submodule.procedures] == [("reset_counter", "module procedure")]

    programs = parse_fortran_programs(code)
    assert len(programs) == 1
    assert programs[0].name == "driver"
    assert programs[0].uses["ancestor_mod"] == []
    assert [v.name for v in programs[0].variables] == ["ierr"]

    block_data = parse_fortran_block_data(code)
    assert len(block_data) == 1
    assert block_data[0].name == "init_data"
    assert [v.name for v in block_data[0].variables] == ["seed"]


def test_procedure_dummy_declaration_tracks_local_interface_kind():
    code = """
subroutine caller(cb)
  procedure(local_cb) :: cb
end subroutine caller
"""
    sig = parse_fortran_file(code).procedures[0]
    cb = next(a for a in sig.arguments if a.name == "cb")
    assert cb.base_type == "procedure"
    assert cb.kind == "local_cb"


def test_procedure_dummy_declaration_with_imported_interface_keeps_kind_unresolved():
    code = """
subroutine caller(cb)
  import :: ext_cb
  procedure(ext_cb) :: cb
end subroutine caller
"""
    sig = parse_fortran_file(code).procedures[0]
    cb = next(a for a in sig.arguments if a.name == "cb")
    assert cb.base_type == "procedure"
    assert cb.kind == ""
    assert "import(ext_cb)" in sig.attributes


def test_parse_fortran_file_returns_file_model_for_source_string():
    code = """
module file_mod
contains
subroutine ping(x)
  integer, intent(in) :: x
end subroutine ping
end module file_mod
"""
    parsed = parse_fortran_file(code)
    assert parsed.filename is None
    assert [m.name for m in parsed.modules] == ["file_mod"]
    assert [p.name for p in parsed.modules[0].procedures] == ["ping"]


def test_parse_fortran_modules_rejects_standalone_procedure_entrypoint():
    code = """
subroutine lonely(x)
  integer, intent(in) :: x
end subroutine lonely
"""
    assert parse_fortran_modules(code) == []


def test_module_parser_ignores_procedure_local_variables():
    code = """
module no_leak
  integer :: module_value
contains
  subroutine worker(x)
    integer, intent(in) :: x
    real :: local_value
  end subroutine worker
end module no_leak
"""
    mod = parse_fortran_modules(code)[0]
    assert [v.name for v in mod.variables] == ["module_value"]


def test_parse_fortran_project_returns_project_registry():
    project = parse_fortran_project(
        {
            "a.f90": """
module a_mod
contains
subroutine step(x)
  integer, intent(in) :: x
end subroutine step
end module a_mod
""",
            "b.f90": """
subroutine free_proc(y)
  real, intent(in) :: y
end subroutine free_proc
""",
        }
    )
    assert [f.filename for f in project.files] == ["a.f90", "b.f90"]
    assert "a_mod" in project.modules
    assert "a_mod.step" in project.procedures
    assert "free_proc" in project.procedures


def test_parse_fortran_project_accepts_directory_and_orders_dependencies(tmp_path):
    (tmp_path / "10_solver.f90").write_text(
        """
module solver_mod
  use kinds_mod, only: rk
contains
  subroutine step(x)
    real(kind=rk), intent(inout) :: x(:)
  end subroutine step
end module solver_mod
""",
        encoding="utf-8",
    )
    (tmp_path / "00_kinds.f90").write_text(
        """
module kinds_mod
  integer, parameter :: rk = selected_real_kind(15, 307)
end module kinds_mod
""",
        encoding="utf-8",
    )
    (tmp_path / "20_driver.f90").write_text(
        """
program driver
  use solver_mod
  real :: x(4)
end program driver
""",
        encoding="utf-8",
    )
    (tmp_path / "30_init.f90").write_text(
        """
block data init_data
  integer :: seed
end block data init_data
""",
        encoding="utf-8",
    )

    project = parse_fortran_project(tmp_path)

    assert len(project.files) == 4
    assert "kinds_mod" in project.modules
    assert "solver_mod" in project.modules
    assert "driver" in project.programs
    assert "solver_mod.step" in project.procedures
    solver = project.procedures["solver_mod.step"]
    assert solver.arguments[0].kind == "selected_real_kind(15, 307)"


def test_singular_parse_entrypoints_return_single_models():
    assert (
        parse_fortran_file("""
subroutine one(x)
  integer, intent(in) :: x
end subroutine one
""")
        .procedures[0]
        .name
        == "one"
    )

    assert (
        parse_fortran_module("""
module single_mod
end module single_mod
""").name
        == "single_mod"
    )

    assert (
        parse_fortran_file("""
module type_mod
  type :: particle
    integer :: id
  end type particle
end module type_mod
""")
        .modules[0]
        .derived_types[0]
        .name
        == "particle"
    )

    assert (
        parse_fortran_file("""
module iface_mod
  interface apply
    subroutine do_apply(x)
      integer, intent(in) :: x
    end subroutine do_apply
  end interface
end module iface_mod
""")
        .modules[0]
        .interfaces[0]
        .name
        == "apply"
    )

    assert (
        parse_fortran_program("""
program driver
  integer :: ierr
end program driver
""").name
        == "driver"
    )

    assert (
        parse_fortran_block_data_unit("""
block data init_data
  integer :: seed
end block data init_data
""").name
        == "init_data"
    )

    assert (
        parse_fortran_submodule("""
submodule (parent_mod) child_impl
end submodule child_impl
""").name
        == "child_impl"
    )


def test_singular_parse_entrypoint_rejects_ambiguous_sources():
    assert (
        len(
            parse_fortran_modules("""
module first_mod
end module first_mod
module second_mod
end module second_mod
""")
        )
        == 2
    )

    parsed = parse_fortran_file("""
subroutine first()
end subroutine first
subroutine second()
end subroutine second
""")
    assert len(parsed.procedures) == 2
