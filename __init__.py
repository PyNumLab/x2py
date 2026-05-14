# -*- coding: utf-8 -*-

"""Compatibility layer for the minimal Fortran signature parser."""

from fortran_parser import (
    FortranArgument,
    FortranDerivedType,
    FortranModule,
    FortranProcedureSignature,
    FortranParser,
    collect_signature_shape_symbols,
    evaluate_signature_shapes,
)

__all__ = (
    "FortranArgument",
    "FortranDerivedType",
    "FortranModule",
    "FortranProcedureSignature",
    "FortranParser",
    "collect_signature_shape_symbols",
    "evaluate_signature_shapes",
)
