# -*- coding: utf-8 -*-
from .models import FortranArgument, FortranBlockData, FortranDerivedType, FortranFile, FortranInterface, FortranModule, FortranParseError, FortranProcedureSignature, FortranProgram, FortranProject, FortranSubmodule
from .parser import (
    FortranParser,
    collect_signature_shape_symbols,
    evaluate_signature_shapes,
)


def parse_fortran_file(source_or_path, filename=None, macro_defines=None, encoding="utf-8"):
    return FortranParser(macro_defines=macro_defines).parse_file(
        source_or_path, filename=filename, macro_defines=macro_defines, encoding=encoding
    )


def parse_fortran_project(files, *, encoding="utf-8"):
    return FortranParser().parse_multiple_files(files, encoding=encoding)


def parse_fortran_signatures(code, filename=None, macro_defines=None):
    parser = FortranParser(macro_defines=macro_defines)
    parsed = parser.parse_file(code, filename=filename, macro_defines=macro_defines)
    out = list(parsed.procedures)
    for m in parsed.modules:
        out.extend(m.procedures)
    for sm in parsed.submodules:
        out.extend(sm.procedures)
    return out


def parse_fortran_project_signatures(files):
    project = FortranParser().parse_multiple_files(files)
    return list(project.procedures.values())


def parse_fortran_signature(code, filename=None, macro_defines=None):
    items = parse_fortran_signatures(code, filename=filename, macro_defines=macro_defines)
    if len(items) != 1:
        raise ValueError(f"Expected exactly one signature, got {len(items)}")
    return items[0]


def parse_fortran_types(code, filename=None):
    return parse_fortran_file(code, filename=filename).derived_types


def parse_fortran_derived_type(code, filename=None):
    items = parse_fortran_types(code, filename=filename)
    if len(items) != 1:
        raise ValueError(f"Expected exactly one derived type, got {len(items)}")
    return items[0]


def parse_fortran_modules(code, filename=None):
    return parse_fortran_file(code, filename=filename).modules


def parse_fortran_module(code, filename=None):
    items = parse_fortran_modules(code, filename=filename)
    if len(items) != 1:
        raise ValueError(f"Expected exactly one module, got {len(items)}")
    return items[0]


def parse_fortran_interfaces(code, filename=None):
    return parse_fortran_file(code, filename=filename).interfaces


def parse_fortran_interface(code, filename=None):
    items = parse_fortran_interfaces(code, filename=filename)
    if len(items) != 1:
        raise ValueError(f"Expected exactly one interface, got {len(items)}")
    return items[0]


def parse_fortran_submodules(code, filename=None):
    return parse_fortran_file(code, filename=filename).submodules


def parse_fortran_submodule(code, filename=None):
    items = parse_fortran_submodules(code, filename=filename)
    if len(items) != 1:
        raise ValueError(f"Expected exactly one submodule, got {len(items)}")
    return items[0]


def parse_fortran_programs(code, filename=None):
    return parse_fortran_file(code, filename=filename).programs


def parse_fortran_program(code, filename=None):
    items = parse_fortran_programs(code, filename=filename)
    if len(items) != 1:
        raise ValueError(f"Expected exactly one program, got {len(items)}")
    return items[0]


def parse_fortran_block_data(code, filename=None):
    return parse_fortran_file(code, filename=filename).block_data_units


def parse_fortran_block_data_unit(code, filename=None):
    items = parse_fortran_block_data(code, filename=filename)
    if len(items) != 1:
        raise ValueError(f"Expected exactly one block data unit, got {len(items)}")
    return items[0]


def assess_wrap_readiness(code, filename=None):
    return FortranParser()._assess_wrap_readiness(code, filename=filename)


def parse_fortran_namespace(root, extensions=(".f", ".for", ".ftn", ".f77", ".f90", ".f95", ".f03", ".f08")):
    return FortranParser()._parse_namespace(root, extensions=extensions)

__all__ = (
    "FortranParser",
    "FortranArgument",
    "FortranBlockData",
    "FortranDerivedType",
    "FortranModule",
    "FortranProgram",
    "FortranSubmodule",
    "FortranFile",
    "FortranInterface",
    "FortranParseError",
    "FortranProject",
    "FortranProcedureSignature",
    "parse_fortran_file",
    "parse_fortran_project",
    "parse_fortran_signatures",
    "parse_fortran_project_signatures",
    "parse_fortran_signature",
    "parse_fortran_types",
    "parse_fortran_derived_type",
    "parse_fortran_modules",
    "parse_fortran_module",
    "parse_fortran_interfaces",
    "parse_fortran_interface",
    "parse_fortran_submodules",
    "parse_fortran_submodule",
    "parse_fortran_programs",
    "parse_fortran_program",
    "parse_fortran_block_data",
    "parse_fortran_block_data_unit",
    "assess_wrap_readiness",
    "parse_fortran_namespace",
    "collect_signature_shape_symbols",
    "evaluate_signature_shapes",
)
