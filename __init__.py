# -*- coding: utf-8 -*-

"""Compatibility layer for the minimal Fortran signature parser."""

from fortran_parser import (
    FortranArgument,
    FortranDerivedType,
    FortranModule,
    FortranProcedureSignature,
    assess_wrap_readiness,
    parse_fortran_file,
    parse_fortran_namespace,
    parse_fortran_modules,
    parse_fortran_project_signatures,
    parse_fortran_signatures,
    parse_fortran_types,
    collect_signature_shape_symbols,
    evaluate_signature_shapes,
)

__all__ = (
    "FortranArgument",
    "FortranDerivedType",
    "FortranModule",
    "FortranProcedureSignature",
    "assess_wrap_readiness",
    "parse_fortran_file",
    "parse_fortran_namespace",
    "parse_fortran_modules",
    "parse_fortran_project_signatures",
    "parse_fortran_signatures",
    "parse_fortran_types",
    "collect_signature_shape_symbols",
    "evaluate_signature_shapes",
)
