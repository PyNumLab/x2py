# -*- coding: utf-8 -*-

"""Compatibility layer for the minimal Fortran parser API."""

from fortran_parser import (
    FortranArgument,
    FortranDerivedType,
    FortranFile,
    FortranModule,
    FortranProcedureSignature,
    FortranProject,
    parse_fortran_file,
    parse_fortran_project,
)

__all__ = (
    "FortranArgument",
    "FortranDerivedType",
    "FortranFile",
    "FortranModule",
    "FortranProcedureSignature",
    "FortranProject",
    "parse_fortran_file",
    "parse_fortran_project",
)
