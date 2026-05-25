"""Public x2py API."""

from importlib import import_module

from c_parser.models import CFile, CParseError, CProject
from c_parser.parser import parse_c_file, parse_c_project
from fortran_parser.models import (
    FortranArgument,
    FortranBlockData,
    FortranDerivedType,
    FortranFile,
    FortranInterface,
    FortranModule,
    FortranParseError,
    FortranProcedureSignature,
    FortranProgram,
    FortranProject,
    FortranSubmodule,
)
from fortran_parser.parser import parse_fortran_file, parse_fortran_project
from semantics.fortran2ir import (
    collect_semantic_compile_time_requirements,
    fortran_file_to_semantic_modules,
    fortran_module_to_semantic_module,
    resolve_semantic_compile_time_values,
)
from semantics.pyi_parser import convert_pyi_to_ir, load_pyi_file, parse_pyi_text
from semantics.readiness import assess_pyi_wrap_readiness, assess_semantic_wrap_readiness

from .cli import main

_FORTRAN_TYPE_PROBE_EXPORTS = {
    "FortranTypeProbeError",
    "FortranTypeProbeReport",
    "build_fortran_type_probe_source",
    "evaluate_fortran_type_requirements",
    "fortran_type_probe_expressions",
    "probe_fortran_type_expressions",
}


def __getattr__(name: str):
    if name in _FORTRAN_TYPE_PROBE_EXPORTS:
        module = import_module("x2py.fortran_type_probe")
        return getattr(module, name)
    raise AttributeError(f"module 'x2py' has no attribute {name!r}")

__all__ = (
    "CFile",
    "CParseError",
    "CProject",
    "FortranTypeProbeError",
    "FortranTypeProbeReport",
    "FortranArgument",
    "FortranBlockData",
    "FortranDerivedType",
    "FortranFile",
    "FortranInterface",
    "FortranModule",
    "FortranParseError",
    "FortranProcedureSignature",
    "FortranProgram",
    "FortranProject",
    "FortranSubmodule",
    "assess_pyi_wrap_readiness",
    "assess_semantic_wrap_readiness",
    "build_fortran_type_probe_source",
    "collect_semantic_compile_time_requirements",
    "convert_pyi_to_ir",
    "evaluate_fortran_type_requirements",
    "fortran_file_to_semantic_modules",
    "fortran_type_probe_expressions",
    "fortran_module_to_semantic_module",
    "load_pyi_file",
    "main",
    "parse_c_file",
    "parse_c_project",
    "parse_fortran_file",
    "parse_fortran_project",
    "parse_pyi_text",
    "probe_fortran_type_expressions",
    "resolve_semantic_compile_time_values",
)
