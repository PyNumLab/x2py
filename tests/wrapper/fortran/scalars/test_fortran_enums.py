"""Fortran enum semantic, stub, and runtime wrapper tests."""

from pathlib import Path

import numpy as np

from x2py import parse_fortran_file as parse_fortran_source
from x2py.codegen.printers.pyi_printer import emit_module
from x2py.semantics.fortran2ir import fortran_module_to_semantic_module

from tests.wrapper.fortran._support import _build_source_or_generated_pyi_and_import, wrapper_source


ENUM_SOURCE = wrapper_source("fenums_f90.f90")
CONTRACT_FIXTURES = Path(__file__).parent / "contracts"


def test_fortran_enums_preserve_values_in_generated_pyi_contract():
    parsed = parse_fortran_source(ENUM_SOURCE.read_text(encoding="utf-8"))
    semantic = fortran_module_to_semantic_module(parsed)
    constants = {variable.name: variable for variable in semantic.variables}

    assert [(name, constants[name].default_value) for name in ("red", "blue", "green", "yellow")] == [
        ("red", "-1"),
        ("blue", "0"),
        ("green", "10"),
        ("yellow", "11"),
    ]
    assert constants["red"].semantic_type.metadata["fortran_bind_c"] is True
    stub = emit_module(semantic)
    assert "red: Final[Int32] = -1" in stub
    assert "yellow: Final[Int32] = 11" in stub
    assert "class Enum" not in stub
    assert "class IntEnum" not in stub


def test_fortran_enums_preserve_integer_runtime_surface(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _build_source_or_generated_pyi_and_import(
        ENUM_SOURCE,
        tmp_path,
        {
            "bind_c_fenums_f90_wrapper.f90",
            "fenums_f90_wrapper.c",
            "fenums_f90_wrapper.h",
        },
        CONTRACT_FIXTURES / "fenums_f90",
        pyi_parity_build_mode,
    )

    assert module.red == np.int32(-1)
    assert module.blue == np.int32(0)
    assert module.green == np.int32(10)
    assert module.yellow == np.int32(11)
    assert module.round_trip_color(np.int32(module.green)) == np.int32(10)

    sample = module.paint()
    assert sample.color == np.int32(-1)
    sample.color = np.int32(module.yellow)
    assert sample.color == np.int32(11)
