from fortran_parser import (
    assess_wrap_readiness,
    collect_signature_shape_symbols,
    evaluate_signature_shapes,
    parse_fortran_namespace,
    parse_fortran_project_signatures,
    parse_fortran_signatures,
    parse_fortran_interfaces,
    parse_fortran_modules,
    parse_fortran_types,
)


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
    signatures = parse_fortran_signatures(code)
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
    signatures = parse_fortran_signatures(code)
    sig = signatures[0]
    assert sig.kind == "function"
    assert sig.result is not None
    assert sig.result.name == "res"
    assert sig.result.base_type == "real"
    assert sig.uses["iso_c_binding"] == ["c_double"]
    assert sig.arguments[0].shape == [":"]


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
    signatures = parse_fortran_signatures(code, filename="legacy.f")
    assert len(signatures) == 2
    assert signatures[0].name == "saxpy"
    assert signatures[0].arguments[1].shape == ["n"]
    assert signatures[1].in_interface is True


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
    signatures = parse_fortran_project_signatures(files)
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
    types = parse_fortran_types(code)
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
  integer(kind=c_int) :: nmax
  real(kind=8), dimension(3) :: origin
end module cfg
"""
    modules = parse_fortran_modules(code)
    assert len(modules) == 1
    mod = modules[0]
    assert mod.name == "cfg"
    assert mod.uses["iso_c_binding"] == ["c_int"]
    assert [v.name for v in mod.variables] == ["nmax", "origin"]
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
    assert [p.name for p in mod.procedures] == ["add1"]
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
    interfaces = parse_fortran_interfaces(code)
    assert len(interfaces) == 1
    iface = interfaces[0]
    assert iface.name == "apply"
    assert iface.module == "m1"
    assert [p.name for p in iface.procedures] == ["do_apply"]
    mod = parse_fortran_modules(code)[0]
    assert len(mod.interfaces) == 1


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
    sigs = parse_fortran_signatures(code, filename="legacy.f")
    assert len(sigs) == 1
    assert sigs[0].name == "saxpy"


def test_ignore_local_variables_in_signatures():
    code = """
subroutine update(n, x)
  integer, intent(in) :: n
  real, intent(inout) :: x(n)
  integer :: i
  real :: tmp
end subroutine update
"""
    sig = parse_fortran_signatures(code)[0]
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
    sigs = parse_fortran_signatures(code)
    assert len(sigs) == 1
    assert sigs[0].name == "outer"


def test_local_parameter_kind_used_in_argument_declaration():
    code = """
subroutine saxpy(x)
  integer, parameter :: rk = selected_real_kind(15, 307)
  real(kind=rk), intent(inout) :: x(:)
end subroutine saxpy
"""
    sig = parse_fortran_signatures(code)[0]
    assert sig.arguments[0].kind == "selected_real_kind(15, 307)"


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
    sig = parse_fortran_project_signatures(files)[0]
    assert sig.arguments[0].shape == ["20"]


def test_assess_wrap_readiness_supported_and_unsupported():
    supported = """
subroutine saxpy(n, x, y)
  integer, intent(in) :: n
  real(kind=8), intent(in) :: x(:)
  real(kind=8), intent(inout) :: y(:)
end subroutine saxpy
"""
    report_ok = assess_wrap_readiness(supported)
    assert report_ok["wrappable"] is True
    assert report_ok["unsupported_constructs"] == []

    unsupported = """
subroutine s(a)
  class(*), intent(inout) :: a
end subroutine s
"""
    report_bad = assess_wrap_readiness(unsupported)
    assert report_bad["wrappable"] is False
    assert report_bad["unsupported_constructs"]


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

    ns = parse_fortran_namespace(tmp_path)
    assert len(ns["files"]) == 2
    assert ns["module_to_file"]["my_kinds"].endswith("kinds.f90")
    assert ns["module_to_file"]["solver"].endswith("solver.f90")
    step = [s for s in ns["signatures"] if s.name == "step"][0]
    assert step.arguments[0].kind == "selected_real_kind(15, 307)"


def test_recursive_function_and_result_keyword_variants():
    code = """
recursive function fact(n) results(res)
  integer, intent(in) :: n
  integer :: res
end function fact
"""
    sig = parse_fortran_signatures(code)[0]
    assert "recursive" in sig.attributes
    assert sig.result is not None
    assert sig.result.name == "res"


def test_assumed_shape_with_explicit_lower_bounds_is_preserved():
    code = """
subroutine fill_grid(x)
  integer, intent(inout) :: x(0:,0:)
end subroutine fill_grid
"""
    sig = parse_fortran_signatures(code)[0]
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
    sig = parse_fortran_signatures(code)[0]
    arg = sig.arguments[0]
    assert arg.rank == 2
    assert arg.shape == ["0:", "1:n"]


def test_subroutine_derived_type_arguments_are_parsed():
    code = """
subroutine step(state)
  type(sim_state), intent(inout) :: state
end subroutine step
"""
    sig = parse_fortran_signatures(code)[0]
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
    sig = parse_fortran_project_signatures(files)[0]
    assert sig.arguments[0].shape == ["0:5"]
    assert sig.arguments[1].shape == ["1:8"]


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

    sig = parse_fortran_project_signatures(files)[0]
    assert sig.name == "a"
    sig_b = parse_fortran_project_signatures(files)[1]
    assert sig_b.name == "b"
    assert sig_b.arguments[0].shape == ["1:3"]


def test_compiler_dependent_parameter_expressions_remain_symbolic():
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
    sig = parse_fortran_project_signatures(files)[0]
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
    sig = parse_fortran_project_signatures(files)[0]
    assert sig.arguments[0].shape == ["1:6"]


def test_symbolic_shape_symbols_can_be_collected_and_later_evaluated():
    code = """
subroutine s(a)
  real, intent(inout) :: a(0:nx-1, 1:ny*2)
end subroutine s
"""
    sig = parse_fortran_signatures(code)[0]
    assert collect_signature_shape_symbols(sig) == {"nx", "ny"}

    evaluated = evaluate_signature_shapes(sig, {"nx": 6, "ny": 4})
    assert evaluated.arguments[0].shape == ["0:5", "1:8"]


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
    sig = parse_fortran_project_signatures(files)[0]
    assert [a.shape[0] for a in sig.arguments] == ["1:11", "1:5", "1:6", "1:4", "1:8", "0:21", "1:5", "1:32", "1:30"]


def test_derived_type_extends_and_attributes():
    code = """
module m
  type, extends(base_t), abstract :: child_t
    integer :: id
  contains
    procedure :: run
  end type child_t
end module m
"""
    dt = parse_fortran_types(code)[0]
    assert dt.name == "child_t"
    assert dt.extends == "base_t"
    assert "abstract" in dt.attributes


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
    dt = parse_fortran_types(code)[0]
    assert {"name": "init => t_init", "attrs": ["pass(self)"]} in dt.procedure_bindings
    assert {"name": "clear", "attrs": ["nopass"]} in dt.procedure_bindings
    assert {"name": "assignment(=)", "targets": ["init"], "attrs": []} in dt.generic_bindings
    assert {"name": "setup", "targets": ["init", "clear"], "attrs": ["public"]} in dt.generic_bindings
