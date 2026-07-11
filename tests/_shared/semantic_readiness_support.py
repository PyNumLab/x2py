import json

import subprocess

import sys

from pathlib import Path

import pytest

from x2py.contracts import CONTRACT_SYMBOLS

from x2py import parse_fortran_file

from x2py.semantics.fortran2ir import fortran_module_to_semantic_module

from x2py.semantics.models import (
    EXTERNAL_TYPE_REF_METADATA,
    POLICY_COMPLETION_PREPARED_METADATA,
    RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA,
    RESOLVED_OWNERSHIP_POLICY_METADATA,
    SemanticArrayContract,
    SemanticArgument,
    SemanticClass,
    SemanticConstraint,
    SemanticFunction,
    SemanticImport,
    SemanticImportItem,
    SemanticMethod,
    SemanticModule,
    SemanticOrigin,
    SemanticStorageContract,
    SemanticType,
)

from x2py.pipeline.pyi import pyi_text_to_semantic_module as parse_pyi_text

from x2py.semantics.readiness import (
    _SemanticTypeIndex,
    _called_shape_intrinsics,
    _constant_names,
    _constant_values,
    _import_index,
    _is_external_type_ref,
    _is_public,
    _iter_expression_values,
    _shape_expressions,
    _shape_symbols,
    assess_pyi_wrap_readiness,
    assess_prepared_semantic_wrap_readiness,
    assess_semantic_wrap_readiness,
)

from x2py.semantics.policy_completion import complete_semantic_policies

from x2py import cli as x2py_cli

TEST_FILE = Path(__file__).parents[1] / "data" / "fortran" / "general" / "basic_subroutine.f90"

CONTRACT_IMPORT = f"from x2py.contracts import {', '.join(sorted(CONTRACT_SYMBOLS))}\n"


def _readiness_from_pyi(source: str):
    module = parse_pyi_text(f"{CONTRACT_IMPORT}{source}", module_name="solver")
    return assess_semantic_wrap_readiness(module, source="solver.pyi")


def _blocker_codes(report: dict) -> set[str]:
    return {blocker["code"] for blocker in report["wrappability_blockers"]}


def _write_ready_fortran(path: Path) -> Path:
    path.write_text(
        """module m
contains
  subroutine work(n)
    integer, intent(in) :: n
  end subroutine work
end module m
""",
        encoding="utf-8",
    )
    return path


__all__ = (
    "CONTRACT_IMPORT",
    "EXTERNAL_TYPE_REF_METADATA",
    "POLICY_COMPLETION_PREPARED_METADATA",
    "RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA",
    "RESOLVED_OWNERSHIP_POLICY_METADATA",
    "TEST_FILE",
    "Path",
    "SemanticArgument",
    "SemanticArrayContract",
    "SemanticClass",
    "SemanticConstraint",
    "SemanticFunction",
    "SemanticImport",
    "SemanticImportItem",
    "SemanticMethod",
    "SemanticModule",
    "SemanticOrigin",
    "SemanticStorageContract",
    "SemanticType",
    "_SemanticTypeIndex",
    "_blocker_codes",
    "_called_shape_intrinsics",
    "_constant_names",
    "_constant_values",
    "_import_index",
    "_is_external_type_ref",
    "_is_public",
    "_iter_expression_values",
    "_readiness_from_pyi",
    "_shape_expressions",
    "_shape_symbols",
    "_write_ready_fortran",
    "assess_prepared_semantic_wrap_readiness",
    "assess_pyi_wrap_readiness",
    "assess_semantic_wrap_readiness",
    "complete_semantic_policies",
    "fortran_module_to_semantic_module",
    "json",
    "parse_fortran_file",
    "parse_pyi_text",
    "pytest",
    "subprocess",
    "sys",
    "x2py_cli",
)
