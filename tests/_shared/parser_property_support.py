"""Property-based parser invariants for small generated source subsets."""

from __future__ import annotations

from contextlib import suppress

import json

from pathlib import Path

import sys

from tempfile import TemporaryDirectory

from unittest.mock import patch

import pytest

pytest.importorskip("hypothesis")

from hypothesis import given, strategies as st

import x2py.pipeline.preprocessing as preprocessing

from x2py.c_parser import CParseError, parse_c_file

from x2py.c_parser.lexer import split_top_level_c_source, top_level_split

from x2py.semantics.fortran2ir import fortran_file_to_semantic_modules

from x2py.pipeline.pyi import pyi_text_to_semantic_module as parse_pyi_text

from x2py.codegen.printers.pyi_printer import emit_module_stubs

from x2py import FortranParseError, parse_fortran_file

from x2py.pipeline.preprocessing import PreprocessingConfig, preprocess_source

_FORTRAN_SCALAR_TYPES = st.sampled_from(["integer", "real", "logical"])

_FORTRAN_IDENTIFIER_STEMS = st.from_regex(r"[a-z][a-z0-9_]{0,8}", fullmatch=True)

_C_SCALAR_TYPES = st.sampled_from(["int", "double", "float", "char"])

_C_MODEL_NAMES = {
    "char": "CChar",
    "double": "CDouble",
    "float": "CFloat",
    "int": "CInt",
}

_C_IDENTIFIERS = st.from_regex(r"[a-z][a-z0-9_]{0,8}", fullmatch=True)

_FUZZ_TEXT = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_()[]{}*,;:#=+-/! \t\n'\"",
    max_size=80,
)


@st.composite
def fortran_subroutines(draw):
    proc_name = f"sub_{draw(st.integers(min_value=0, max_value=9999))}"
    arg_ids = draw(st.lists(st.integers(min_value=0, max_value=99), max_size=5, unique=True))
    arg_names = [f"arg_{value}" for value in arg_ids]
    arg_types = draw(st.lists(_FORTRAN_SCALAR_TYPES, min_size=len(arg_names), max_size=len(arg_names)))

    lines = [f"subroutine {proc_name}({', '.join(arg_names)})"]
    lines.extend(
        f"  {type_spec}, intent(in) :: {arg_name}" for type_spec, arg_name in zip(arg_types, arg_names, strict=True)
    )
    lines.append(f"end subroutine {proc_name}")

    return proc_name, arg_names, "\n".join(lines) + "\n"


@st.composite
def c_prototypes(draw):
    function_name = f"fn_{draw(st.integers(min_value=0, max_value=9999))}"
    result_type = draw(_C_SCALAR_TYPES)
    parameter_ids = draw(st.lists(st.integers(min_value=0, max_value=99), max_size=6, unique=True))
    parameter_types = draw(st.lists(_C_SCALAR_TYPES, min_size=len(parameter_ids), max_size=len(parameter_ids)))

    if parameter_ids:
        parameters = [
            f"{type_spec} p_{parameter_id}"
            for type_spec, parameter_id in zip(parameter_types, parameter_ids, strict=True)
        ]
        parameter_names = [f"p_{parameter_id}" for parameter_id in parameter_ids]
    else:
        parameters = ["void"]
        parameter_names = []

    source = f"{result_type} {function_name}({', '.join(parameters)});\n"
    return function_name, parameter_names, source


@st.composite
def c_nested_variable_declarations(draw):
    scalar_type = draw(_C_SCALAR_TYPES)
    bound = draw(st.integers(min_value=1, max_value=99))
    shape = draw(st.sampled_from(["pointer", "array", "array_of_pointers", "pointer_to_array", "callback"]))

    if shape == "pointer":
        source = f"{scalar_type} *value;\n"
        components = ["CPointer", _C_MODEL_NAMES[scalar_type]]
    elif shape == "array":
        source = f"{scalar_type} value[{bound}];\n"
        components = ["CArray", _C_MODEL_NAMES[scalar_type]]
    elif shape == "array_of_pointers":
        source = f"{scalar_type} *value[{bound}];\n"
        components = ["CArray", "CPointer", _C_MODEL_NAMES[scalar_type]]
    elif shape == "pointer_to_array":
        source = f"{scalar_type} (*value)[{bound}];\n"
        components = ["CPointer", "CArray", _C_MODEL_NAMES[scalar_type]]
    else:
        parameter_type = draw(_C_SCALAR_TYPES)
        source = f"{scalar_type} (*value)({parameter_type});\n"
        components = ["CPointer", "CFunctionType"]

    return source, components


__all__ = (
    "_C_IDENTIFIERS",
    "_FORTRAN_IDENTIFIER_STEMS",
    "_FORTRAN_SCALAR_TYPES",
    "_FUZZ_TEXT",
    "CParseError",
    "FortranParseError",
    "Path",
    "PreprocessingConfig",
    "TemporaryDirectory",
    "c_nested_variable_declarations",
    "c_prototypes",
    "emit_module_stubs",
    "fortran_file_to_semantic_modules",
    "fortran_subroutines",
    "given",
    "json",
    "parse_c_file",
    "parse_fortran_file",
    "parse_pyi_text",
    "patch",
    "preprocess_source",
    "preprocessing",
    "pytest",
    "split_top_level_c_source",
    "st",
    "suppress",
    "sys",
    "top_level_split",
)
