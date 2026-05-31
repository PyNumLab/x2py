# -*- coding: utf-8 -*-
"""Preprocessor selection and declaration/execution boundary handling."""

import ast
from dataclasses import replace
import re

import pytest

from x2py import FortranParseError, parse_fortran_file


def collect_signature_shape_symbols(signature):
    symbols = set()
    for arg in signature.arguments:
        for dim in arg.shape:
            symbols.update(re.findall(r"[A-Za-z_]\w*", dim))
    return symbols


def evaluate_signature_shapes(signature, symbol_values=None):
    symbol_values = symbol_values or {}
    out = replace(signature)
    out.arguments = [replace(a) for a in signature.arguments]

    def fold_integer_expr(text):
        try:
            tree = ast.parse(text, mode="eval")
        except SyntaxError:
            return text
        allowed = (
            ast.Expression,
            ast.BinOp,
            ast.UnaryOp,
            ast.Constant,
            ast.Add,
            ast.Sub,
            ast.Mult,
            ast.Div,
            ast.FloorDiv,
            ast.Mod,
            ast.Pow,
            ast.USub,
            ast.UAdd,
        )
        if any(not isinstance(node, allowed) for node in ast.walk(tree)):
            return text
        value = eval(compile(tree, "<shape>", "eval"), {"__builtins__": {}}, {})
        return str(int(value)) if isinstance(value, (int, float)) and value == int(value) else text

    for arg in out.arguments:
        arg.shape = list(arg.shape)
        for index, dim in enumerate(arg.shape):
            for key, value in symbol_values.items():
                dim = re.sub(rf"\b{re.escape(str(key))}\b", str(value), dim, flags=re.IGNORECASE)
            if ":" in dim:
                dim = ":".join(fold_integer_expr(part) if part.strip() else part for part in dim.split(":"))
            else:
                dim = fold_integer_expr(dim)
            arg.shape[index] = dim
    return out

def test_signature_shape_helpers_evaluate_publicly_parsed_signature():
    code = """
subroutine fill(a)
  real, intent(inout) :: a(0:nx-1, 1:ny)
end subroutine fill
"""

    sig = parse_fortran_file(code).procedures[0]

    assert collect_signature_shape_symbols(sig) == {"nx", "ny"}
    evaluated = evaluate_signature_shapes(sig, {"NX": 4, "ny": 3})
    assert evaluated.arguments[0].shape == ["0:3", "1:3"]
    assert sig.arguments[0].shape == ["0:nx-1", "1:ny"]

def test_cpp_directives_are_preserved_without_parser_branch_selection():
    code = """
#if defined USE_FAST
subroutine fast_path(x)
  integer, intent(in) :: x
end subroutine fast_path
#else
subroutine slow_path(x)
  real, intent(in) :: x
end subroutine slow_path
#endif

#ifndef USE_SLOW
subroutine default_path(x)
  logical, intent(in) :: x
end subroutine default_path
#else
subroutine selected_slow_path(x)
  real, intent(in) :: x
end subroutine selected_slow_path
#endif
"""

    parsed = parse_fortran_file(code, macro_defines={"USE_FAST": True})

    assert [proc.name for proc in parsed.procedures] == [
        "fast_path",
        "slow_path",
        "default_path",
        "selected_slow_path",
    ]

def test_include_and_ignored_spec_lines_do_not_change_public_signature():
    code = """
subroutine legacy_specs(x)
  include 'params.inc'
  intrinsic abs
  save
  common /blk/ tmp
  data tmp /0.0/
  equivalence (tmp, x)
  format(1x, f8.3)
  real, intent(inout) :: x
  real :: tmp
end subroutine legacy_specs
"""

    sig = parse_fortran_file(code, filename="legacy_specs.f90").procedures[0]

    assert [arg.name for arg in sig.arguments] == ["x"]
    assert sig.arguments[0].base_type == "real"

def test_execution_part_boundaries_and_local_types_are_not_misread_as_declarations():
    code = """
subroutine exec_edges(x)
  real, intent(inout) :: x
  integer :: i
  type scratch_t
    integer :: id
  end type scratch_t
  x = x + 1.0
  go to 10
10 continue
  call noop()
end subroutine exec_edges
"""

    sig = parse_fortran_file(code).procedures[0]

    assert [arg.name for arg in sig.arguments] == ["x"]
    assert sig.arguments[0].base_type == "real"
    assert "i" not in sig.variables

def test_program_execution_part_is_ignored_after_first_executable_statement():
    code = """
program driver
  use iso_fortran_env
  integer :: ierr
  write(*,*) "running"
  maybe_decl looking_body_statement
contains
  subroutine inner()
  end subroutine inner
end program driver
"""

    program = parse_fortran_file(code, filename="driver.f90").programs[0]

    assert [var.name for var in program.variables] == ["ierr"]

def test_executable_statement_in_module_spec_part_raises():
    code = """
module bad_exec_mod
  write(*,*) "not allowed"
end module bad_exec_mod
"""

    with pytest.raises(FortranParseError, match="Executable statement is not allowed"):
        parse_fortran_file(code, filename="bad_exec_mod.f90")

def test_openmp_declarative_directives_raise_but_executable_directives_are_body_lines():
    declarative = """
module omp_mod
  integer :: state
!$omp threadprivate(state)
end module omp_mod
"""
    executable = """
subroutine omp_body(x)
  integer, intent(inout) :: x
!$omp parallel do
  do i = 1, x
    x = x + i
  end do
end subroutine omp_body
"""
    proc_declarative = """
subroutine omp_decl(x)
!$omp declare simd
  integer, intent(inout) :: x
end subroutine omp_decl
"""
    type_declarative = """
module omp_type_mod
  type :: state
!$omp declare target
    integer :: value
  end type state
end module omp_type_mod
"""
    module_executable = """
module bad_omp_mod
!$omp parallel
end module bad_omp_mod
"""
    fixed_form_executable = """
      subroutine fixed_omp(n)
      integer n
C$OMP PARALLEL DO
      do 10 i = 1, n
10    continue
      end
"""

    with pytest.raises(FortranParseError, match="Unsupported OpenMP declarative directive"):
        parse_fortran_file(declarative, filename="omp_mod.f90")
    with pytest.raises(FortranParseError, match="Unsupported OpenMP declarative directive"):
        parse_fortran_file(proc_declarative, filename="omp_decl.f90")
    with pytest.raises(FortranParseError, match="Unsupported OpenMP declarative directive"):
        parse_fortran_file(type_declarative, filename="omp_type.f90")
    with pytest.raises(FortranParseError, match="Executable statement is not allowed"):
        parse_fortran_file(module_executable, filename="bad_omp_mod.f90")
    assert parse_fortran_file(executable, filename="omp_body.f90").procedures[0].name == "omp_body"
    assert parse_fortran_file(fixed_form_executable, filename="fixed_omp.f").procedures[0].name == "fixed_omp"

def test_cpp_false_and_malformed_expressions_are_not_evaluated_by_parser():
    code = """
#if 0
subroutine false_if_branch()
end subroutine false_if_branch
#else
subroutine false_if_else()
end subroutine false_if_else
#endif

#if defined(USE_A) && (
subroutine malformed_if_branch()
end subroutine malformed_if_branch
#else
subroutine malformed_if_else()
end subroutine malformed_if_else
#endif
"""

    parsed = parse_fortran_file(code, macro_defines=set())

    assert [proc.name for proc in parsed.procedures] == [
        "false_if_branch",
        "false_if_else",
        "malformed_if_branch",
        "malformed_if_else",
    ]

def test_statement_function_and_numeric_label_before_execution_part():
    code = """
subroutine old_style(x)
  real x
  real f
10 continue
  f(x) = x + 1.0
end subroutine old_style
"""

    sig = parse_fortran_file(code, filename="old_style.f90").procedures[0]

    assert sig.arguments[0].base_type == "real"

def test_preprocessor_boolean_identifiers_are_not_evaluated_by_public_parse():
    code = """
#if USE_FAST && !USE_SLOW
subroutine selected_fast()
end subroutine selected_fast
#else
subroutine selected_slow()
end subroutine selected_slow
#endif

#else
#elif USE_OTHER
#endif

subroutine after_stray_directives()
end subroutine after_stray_directives
"""

    parsed = parse_fortran_file(code, filename="cpp_edges.f90", macro_defines={"USE_FAST": True})

    assert [proc.name for proc in parsed.procedures] == [
        "selected_fast",
        "selected_slow",
        "after_stray_directives",
    ]

def test_implicit_mapping_parameter_noise_and_assignment_lines_do_not_break_procedure_parse():
    code = """
subroutine declaration_noise(x)
  implicit real(a-h,o-z)
  integer, parameter :: n = 3, ignored_token
  parameter (m = 4, malformed_token)
  x = 1.0
  real x
end subroutine declaration_noise
"""

    sig = parse_fortran_file(code, filename="declaration_noise.f90").procedures[0]

    assert sig.arguments[0].name == "x"
    assert sig.arguments[0].base_type == "real"

def test_stray_end_unit_lines_are_rejected_by_public_file_parse():
    with pytest.raises(FortranParseError, match="Invalid Fortran syntax") as exc_info:
        parse_fortran_file(
        """
end module stray_mod
end submodule stray_submod
end program stray_program
end interface

subroutine kept()
end subroutine kept
""",
        filename="stray_ends.f90",
    )

    assert exc_info.value.code == "PARSE_INVALID_SYNTAX"
