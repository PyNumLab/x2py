from pathlib import Path

import pytest

import x2py

from x2py.contracts import CONTRACT_SYMBOLS

from x2py import parse_fortran_file as parse_fortran_source

from x2py.semantics.metadata import SNAPSHOT_TYPE_METADATA

from x2py.codegen.binding_pipeline import BindingPipeline

from x2py.codegen.codegen import Codegen

from x2py.codegen.scope import Scope

from x2py.semantics.fortran2ir import (
    fortran_module_to_semantic_module,
)

from x2py.pipeline.pyi import pyi_text_to_semantic_module as _parse_pyi_text

from x2py.semantics.ir2ast import semantic_ir_to_codegen_ast as _semantic_ir_to_codegen_ast

from x2py.codegen.printers.pyi_printer import (
    emit_module,
    emit_module_stubs,
    opaque_dependency_modules,
    PyiPrinter,
)

from x2py.semantics.models import (
    CALLBACK_DECLARATION_ACCESS_METADATA,
    ProjectionMapping,
    RUNTIME_HOLD_GIL_METADATA,
    RUNTIME_STATUS_ERROR_METADATA,
    SemanticArgument,
    SemanticArrayContract,
    SemanticClass,
    SemanticConstraint,
    SemanticImport,
    SemanticMethod,
    SemanticModule,
    SemanticOrigin,
    SemanticFunction,
    SemanticField,
    SemanticStorageContract,
    SemanticType,
    SemanticVariable,
)

from x2py.semantics.policy_completion import complete_semantic_policies

WRAPPER_FORTRAN_DATA = Path(__file__).parents[2] / "data" / "fortran" / "wrapper"

OPERATOR_F90_SOURCE = WRAPPER_FORTRAN_DATA / "foperators_f90.f90"

CONTRACT_IMPORT = f"from x2py.contracts import {', '.join(sorted(CONTRACT_SYMBOLS))}\n"


def parse_pyi_text(source: str, *args, **kwargs):
    if "x2py.contracts" in source:
        return _parse_pyi_text(source, *args, **kwargs)
    return _parse_pyi_text(f"{CONTRACT_IMPORT}{source}", *args, **kwargs)


def semantic_ir_to_codegen_ast(node, *args, **kwargs):
    if isinstance(node, SemanticModule):
        complete_semantic_policies(node)
    return _semantic_ir_to_codegen_ast(node, *args, **kwargs)


def generate_pyi(source: str) -> str:
    fmod = parse_fortran_source(source)

    smod = fortran_module_to_semantic_module(fmod)

    return emit_module(smod)


def normalize(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


__all__ = (
    "CALLBACK_DECLARATION_ACCESS_METADATA",
    "OPERATOR_F90_SOURCE",
    "RUNTIME_HOLD_GIL_METADATA",
    "RUNTIME_STATUS_ERROR_METADATA",
    "SNAPSHOT_TYPE_METADATA",
    "BindingPipeline",
    "Codegen",
    "Path",
    "ProjectionMapping",
    "PyiPrinter",
    "Scope",
    "SemanticArgument",
    "SemanticArrayContract",
    "SemanticClass",
    "SemanticConstraint",
    "SemanticField",
    "SemanticFunction",
    "SemanticImport",
    "SemanticMethod",
    "SemanticModule",
    "SemanticOrigin",
    "SemanticStorageContract",
    "SemanticType",
    "SemanticVariable",
    "_parse_pyi_text",
    "emit_module",
    "emit_module_stubs",
    "fortran_module_to_semantic_module",
    "generate_pyi",
    "normalize",
    "opaque_dependency_modules",
    "parse_fortran_source",
    "parse_pyi_text",
    "pytest",
    "semantic_ir_to_codegen_ast",
    "x2py",
)
