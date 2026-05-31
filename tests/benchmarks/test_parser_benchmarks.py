# -*- coding: utf-8 -*-
"""Representative parser and code-generation performance benchmarks."""

from __future__ import annotations

import pytest

from c_parser import parse_c_file
from semantics.fortran2ir import fortran_file_to_semantic_modules
from semantics.pyi_printer import emit_module_stubs
from x2py import parse_fortran_file


_C_HEADER = "".join(f"int fn_{index}(int x_{index}, double y_{index});\n" for index in range(200))
_FORTRAN_MODULE = (
    "module generated\n"
    "contains\n"
    + "".join(
        f"subroutine step_{index}(x)\n  integer, intent(in) :: x\nend subroutine step_{index}\n" for index in range(50)
    )
    + "end module generated\n"
)


def _parse_convert_emit_fortran(source: str) -> dict[str, str]:
    parsed = parse_fortran_file(source, filename="benchmark.f90")
    return emit_module_stubs(fortran_file_to_semantic_modules(parsed))


@pytest.mark.benchmark
def test_parse_representative_c_header(benchmark):
    parsed = benchmark(parse_c_file, _C_HEADER, filename="benchmark.h")

    assert len(parsed.functions) == 200
    assert parsed.diagnostics == []


@pytest.mark.benchmark
def test_parse_convert_emit_representative_fortran_module(benchmark):
    stubs = benchmark(_parse_convert_emit_fortran, _FORTRAN_MODULE)

    assert stubs["generated"].count("def step_") == 50
