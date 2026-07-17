import ast

import re

from dataclasses import asdict

from pathlib import Path

import pytest

import x2py.pipeline.pyi as pyi_pipeline

from x2py.contracts import CONTRACT_SYMBOLS

from x2py.semantics.metadata import (
    ADDRESS_ROLE_METADATA,
    ADDRESS_ROLE_PROJECTION,
    ADDRESS_ROLE_RAW,
    BIND_TARGET_METADATA,
    NATIVE_ARRAY_DESCRIPTOR_METADATA,
    OPTIONAL_ABSENT_HANDLE_METADATA,
    PROJECTED_OUTPUT_METADATA,
    SUPPRESS_DEFAULT_CONSTRUCTOR_METADATA,
    USER_PRIVATE_METADATA,
)

from x2py.semantics.fortran2ir import fortran_file_to_semantic_modules

from x2py.semantics.native_array_handles import (
    is_native_array_handle,
    native_array_data_type,
    native_array_descriptor_kind,
    native_array_handle_facts,
)

from x2py.semantics.models import (
    ProjectionMapping,
    PYTHON_VALUE_IMMUTABLE,
    PYTHON_VALUE_MUTABILITY_METADATA,
    SemanticArgument,
    SemanticConstraint,
    SemanticField,
    SemanticFunction,
    SemanticImport,
    SemanticImportItem,
    SemanticModule,
    SemanticType,
    SemanticVariable,
)

from x2py.semantics.pyi2ir import (
    _PyiAstParser,
    _node_text,
    convert_pyi_to_ir,
)

from x2py.pipeline.pyi import pyi_file_to_semantic_module, pyi_paths_to_semantic_modules, pyi_text_to_semantic_module

from x2py.pyi_parser import parse_pyi_text as parse_pyi_ast_text

from x2py.semantics.native_contract import native_contract_issues

from x2py.semantics.policy_completion import complete_semantic_policies

from x2py.semantics.readiness import assess_semantic_wrap_readiness

from x2py.wrapper_codegen.printers import emit_module

from tests._shared.fixture_outputs import FORTRAN_DATA_DIR, FORTRAN_SUFFIXES

from x2py import parse_fortran_file

PYI_COMPARE_DIRS = ("general", "blas", "lapack", "scifortran")

_ALL_FORTRAN_PYI_COMPARE_FIXTURES = sorted(
    path
    for dirname in PYI_COMPARE_DIRS
    for path in (FORTRAN_DATA_DIR / dirname).rglob("*")
    if path.is_file() and path.suffix.lower() in FORTRAN_SUFFIXES
)


def _sample_pyi_compare_fixtures(paths: list[Path]) -> list[Path]:
    by_dir: dict[str, list[Path]] = {}
    for path in paths:
        by_dir.setdefault(path.relative_to(FORTRAN_DATA_DIR).parts[0], []).append(path)

    selected: list[Path] = []
    for dirname in PYI_COMPARE_DIRS:
        selected.extend(by_dir.get(dirname, [])[:8])

    for relpath in [
        "general/module_vars_use.f90",
        "lapack/clartg.f90",
        "lapack/la_constants.f90",
        "scifortran/GAUSS_QUADRATURE.f90",
    ]:
        path = FORTRAN_DATA_DIR / relpath
        if path.exists():
            selected.append(path)

    return sorted(set(selected))


FORTRAN_PYI_COMPARE_FIXTURES = _sample_pyi_compare_fixtures(_ALL_FORTRAN_PYI_COMPARE_FIXTURES)

CONTRACT_IMPORT = f"from x2py.contracts import {', '.join(sorted(CONTRACT_SYMBOLS))}\n"


def parse_pyi_text(source: str, *args, **kwargs):
    if "x2py.contracts" in source:
        return pyi_text_to_semantic_module(source, *args, **kwargs)
    return pyi_text_to_semantic_module(f"{CONTRACT_IMPORT}{source}", *args, **kwargs)


def _semantic_modules_for_source(path: Path):
    parsed = parse_fortran_file(
        path.read_text(encoding="utf-8"),
        filename=str(path.relative_to(FORTRAN_DATA_DIR)),
    )
    return fortran_file_to_semantic_modules(parsed, standalone_module_name=path.stem)


__all__ = (
    "ADDRESS_ROLE_METADATA",
    "ADDRESS_ROLE_PROJECTION",
    "ADDRESS_ROLE_RAW",
    "BIND_TARGET_METADATA",
    "CONTRACT_IMPORT",
    "CONTRACT_SYMBOLS",
    "FORTRAN_PYI_COMPARE_FIXTURES",
    "NATIVE_ARRAY_DESCRIPTOR_METADATA",
    "OPTIONAL_ABSENT_HANDLE_METADATA",
    "PROJECTED_OUTPUT_METADATA",
    "PYTHON_VALUE_IMMUTABLE",
    "PYTHON_VALUE_MUTABILITY_METADATA",
    "SUPPRESS_DEFAULT_CONSTRUCTOR_METADATA",
    "USER_PRIVATE_METADATA",
    "Path",
    "ProjectionMapping",
    "SemanticArgument",
    "SemanticConstraint",
    "SemanticField",
    "SemanticFunction",
    "SemanticImport",
    "SemanticImportItem",
    "SemanticModule",
    "SemanticType",
    "SemanticVariable",
    "_PyiAstParser",
    "_node_text",
    "_semantic_modules_for_source",
    "asdict",
    "assess_semantic_wrap_readiness",
    "ast",
    "complete_semantic_policies",
    "convert_pyi_to_ir",
    "emit_module",
    "fortran_file_to_semantic_modules",
    "is_native_array_handle",
    "native_array_data_type",
    "native_array_descriptor_kind",
    "native_array_handle_facts",
    "native_contract_issues",
    "parse_fortran_file",
    "parse_pyi_ast_text",
    "parse_pyi_text",
    "pyi_file_to_semantic_module",
    "pyi_paths_to_semantic_modules",
    "pyi_pipeline",
    "pyi_text_to_semantic_module",
    "pytest",
    "re",
)
