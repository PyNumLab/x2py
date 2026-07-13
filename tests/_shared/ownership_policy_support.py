from dataclasses import replace

import pytest

from x2py.contracts import CONTRACT_SYMBOLS

from x2py.semantics.metadata import (
    ADDRESS_ROLE_METADATA,
    ADDRESS_ROLE_PROJECTION,
    ADDRESS_ROLE_RAW,
    PROJECTED_OUTPUT_METADATA,
    SCALAR_STORAGE_CATEGORY,
)

from x2py.codegen.bind_c import (
    BindCArrayType,
    BindCFunctionDef,
    BindCNativeArrayDescriptorType,
    BindCNativeArrayHandleProperty,
    BindCNativeArrayHandleVariable,
    BindCPointer,
    BindCAccessorModuleVariable,
    native_array_descriptor_argument_type,
)

from x2py.codegen.bindings.c_concepts import CFIDescriptorType

from x2py.codegen.bindings.c_to_python import CPythonBindingGenerator

from x2py.codegen.bindings.cpython_api import PythonObjectType

from x2py.codegen.bridges.fortran_to_c import FortranToCBridgeGenerator

from x2py.codegen.models.core import (
    Declare,
    FunctionCall,
    FunctionDef,
    FunctionDefArgument,
    FunctionDefResult,
    IndexedElement,
    Return,
    Variable,
)

from x2py.codegen.models.datatypes import NIL, NumpyFloat64Type, NumpyNDArrayType, convert_to_literal

from x2py.codegen.printers.ccode import CCodePrinter

from x2py.codegen.printers.cpythoncode import CPythonCodePrinter

from x2py.codegen.printers.fcode import FCodePrinter

from x2py.codegen.printers.pyi_printer import PyiPrinter

from x2py.codegen.scope import Scope

from x2py.semantics.ownership import (
    AssignmentMode,
    CodegenAction,
    DestructionPolicy,
    NativeBarrierAction,
    NativeBarrierDispatcher,
    ObjectKind,
    OwnershipContext,
    OwnershipDecision,
    OwnershipOwner,
    OwnershipPolicyResolver,
    PolicyActionDispatcher,
    PythonBarrierAction,
    PythonBarrierDispatcher,
    SetterAction,
    StorageMode,
    TransferMode,
    codegen_action_for_variable,
    default_ownership_policy,
    set_ownership_metadata,
)

from x2py.semantics.ir2ast import semantic_ir_to_codegen_ast as _semantic_ir_to_codegen_ast

from x2py.semantics.models import (
    POLICY_COMPLETION_PREPARED_METADATA,
    MODULE_VARIABLE_INITIALIZER_UNSUPPORTED_BLOCKER,
    PYTHON_EXPORTS_METADATA,
    PYTHON_EXPORTS_PREPARED_METADATA,
    RESOLVED_GETTER_OWNERSHIP_POLICY_METADATA,
    RESOLVED_MODULE_VARIABLE_INITIALIZER_METADATA,
    RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA,
    RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA,
    RESOLVED_OWNERSHIP_POLICY_METADATA,
    RESOLVED_RETURN_OWNERSHIP_POLICY_METADATA,
    RESOLVED_SNAPSHOT_FIELD_ACTION_METADATA,
    ProjectionMapping,
    SemanticArgument,
    SemanticArrayContract,
    SemanticClass,
    SemanticConstraint,
    SemanticField,
    SemanticFunction,
    SemanticModule,
    SemanticStorageContract,
    SemanticType,
    SemanticVariable,
)

from x2py.semantics.native_array_handles import (
    ArrayInteropPolicy,
    ArrayInteropPolicyDispatcher,
    NativeArrayBuildRequirement,
    NativeArrayHandlePolicy,
    NativeArrayHandlePolicyDispatcher,
    native_array_descriptor_kind,
    native_array_handle_build_requirements,
)

from x2py.semantics.policy_completion import complete_semantic_policies

from x2py.pipeline.pyi import pyi_text_to_semantic_module as _parse_pyi_text

CONTRACT_IMPORT = f"from x2py.contracts import {', '.join(sorted(CONTRACT_SYMBOLS))}\n"


def parse_pyi_text(source: str, *args, **kwargs):
    if "x2py.contracts" in source:
        return _parse_pyi_text(source, *args, **kwargs)
    return _parse_pyi_text(f"{CONTRACT_IMPORT}{source}", *args, **kwargs)


def _model_call_names(node, seen=None):
    """Collect function-call names from a generated model subtree."""
    if seen is None:
        seen = set()
    node_id = id(node)
    if node_id in seen:
        return
    seen.add(node_id)
    if isinstance(node, FunctionCall):
        yield str(node.func_name)
    for attr in getattr(node, "_attribute_nodes", ()):
        value = getattr(node, attr)
        if isinstance(value, tuple | list):
            for item in value:
                yield from _model_call_names(item, seen)
        elif value is not None:
            yield from _model_call_names(value, seen)


def _scalar_type(name: str = "Int32") -> SemanticType:
    return SemanticType(name=name, dtype=name)


def semantic_ir_to_codegen_ast(node, *args, **kwargs):
    if isinstance(node, SemanticModule):
        complete_semantic_policies(node)
    return _semantic_ir_to_codegen_ast(node, *args, **kwargs)


def _string_type() -> SemanticType:
    return SemanticType(name="String", dtype="String")


def _array_type(
    *,
    allocatable: bool = False,
    pointer: bool = False,
    metadata: dict[str, object] | None = None,
) -> SemanticType:
    return SemanticType(
        name="Float64",
        dtype="Float64",
        rank=1,
        shape=[":"],
        metadata=metadata or {},
        storage=SemanticStorageContract(
            kind="array",
            array=SemanticArrayContract(
                rank=1,
                shape=[":"],
                allocatable=allocatable,
                pointer=pointer,
            ),
        ),
    )


def _scalar_storage_type() -> SemanticType:
    return SemanticType(
        name="Int32",
        dtype="Int32",
        rank=0,
        storage=SemanticStorageContract(
            kind="array",
            array=SemanticArrayContract(rank=0, shape=[], category=SCALAR_STORAGE_CATEGORY),
        ),
    )


def _string_storage_type() -> SemanticType:
    return SemanticType(
        name="String",
        dtype="String",
        rank=0,
        metadata={"fortran_character_length": "8"},
        storage=SemanticStorageContract(
            kind="array",
            array=SemanticArrayContract(rank=0, shape=[], category=SCALAR_STORAGE_CATEGORY),
        ),
    )


def _address_type(role: str) -> SemanticType:
    return SemanticType(
        name="Int32",
        dtype="Int32",
        storage=SemanticStorageContract(kind="address", metadata={ADDRESS_ROLE_METADATA: role}),
    )


def _derived_type(
    name: str = "point",
    *,
    metadata: dict[str, object] | None = None,
) -> SemanticType:
    return SemanticType(name=name, dtype=name, metadata=metadata or {})


def _read_only_argument_context(**kwargs) -> OwnershipContext:
    return OwnershipContext.argument(**kwargs)


def _writable_argument_context(**kwargs) -> OwnershipContext:
    return OwnershipContext.argument(writes_argument=True, **kwargs)


def _hidden_output_context(**kwargs) -> OwnershipContext:
    return OwnershipContext.argument(reads_argument=False, writes_argument=True, **kwargs)


def _native_array_policy(
    *,
    descriptor_kind: str = "allocatable",
    handle_kind: str = "borrowed_module_descriptor",
    to_numpy: str = "borrowed_view",
    descriptor_interop: str = "none",
    nullable: bool = False,
    optional_absent: bool = False,
    operations: tuple[str, ...] = ("allocated", "to_numpy"),
) -> NativeArrayHandlePolicy:
    return NativeArrayHandlePolicy(
        descriptor_kind=descriptor_kind,
        handle_kind=handle_kind,
        origin="module_variable",
        owner="native",
        owner_retention="native_module",
        descriptor_ownership="borrowed",
        borrowed=True,
        getter_behavior="handle",
        python_setter="none",
        native_setter="none",
        output_projection="none",
        release="native_owner",
        target_lifetime="module",
        destroy_behavior="none",
        to_numpy=to_numpy,
        descriptor_interop=descriptor_interop,
        nullable=nullable,
        optional_absent=optional_absent,
        storage_mode="alias",
        operations=operations,
    )


__all__ = (
    "ADDRESS_ROLE_METADATA",
    "ADDRESS_ROLE_PROJECTION",
    "ADDRESS_ROLE_RAW",
    "MODULE_VARIABLE_INITIALIZER_UNSUPPORTED_BLOCKER",
    "NIL",
    "POLICY_COMPLETION_PREPARED_METADATA",
    "PROJECTED_OUTPUT_METADATA",
    "PYTHON_EXPORTS_METADATA",
    "PYTHON_EXPORTS_PREPARED_METADATA",
    "RESOLVED_GETTER_OWNERSHIP_POLICY_METADATA",
    "RESOLVED_MODULE_VARIABLE_INITIALIZER_METADATA",
    "RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA",
    "RESOLVED_OWNERSHIP_POLICY_METADATA",
    "RESOLVED_RETURN_OWNERSHIP_POLICY_METADATA",
    "RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA",
    "RESOLVED_SNAPSHOT_FIELD_ACTION_METADATA",
    "ArrayInteropPolicy",
    "ArrayInteropPolicyDispatcher",
    "AssignmentMode",
    "BindCAccessorModuleVariable",
    "BindCArrayType",
    "BindCFunctionDef",
    "BindCNativeArrayDescriptorType",
    "BindCNativeArrayHandleProperty",
    "BindCNativeArrayHandleVariable",
    "BindCPointer",
    "CCodePrinter",
    "CFIDescriptorType",
    "CPythonBindingGenerator",
    "CPythonCodePrinter",
    "CodegenAction",
    "Declare",
    "DestructionPolicy",
    "FCodePrinter",
    "FortranToCBridgeGenerator",
    "FunctionDef",
    "FunctionDefArgument",
    "FunctionDefResult",
    "IndexedElement",
    "NativeArrayBuildRequirement",
    "NativeArrayHandlePolicyDispatcher",
    "NativeBarrierAction",
    "NativeBarrierDispatcher",
    "NumpyFloat64Type",
    "NumpyNDArrayType",
    "ObjectKind",
    "OwnershipContext",
    "OwnershipDecision",
    "OwnershipOwner",
    "OwnershipPolicyResolver",
    "PolicyActionDispatcher",
    "ProjectionMapping",
    "PyiPrinter",
    "PythonBarrierAction",
    "PythonBarrierDispatcher",
    "PythonObjectType",
    "Return",
    "Scope",
    "SemanticArgument",
    "SemanticClass",
    "SemanticConstraint",
    "SemanticField",
    "SemanticFunction",
    "SemanticModule",
    "SemanticType",
    "SemanticVariable",
    "SetterAction",
    "StorageMode",
    "TransferMode",
    "Variable",
    "_address_type",
    "_array_type",
    "_derived_type",
    "_hidden_output_context",
    "_model_call_names",
    "_native_array_policy",
    "_read_only_argument_context",
    "_scalar_storage_type",
    "_scalar_type",
    "_semantic_ir_to_codegen_ast",
    "_string_storage_type",
    "_string_type",
    "_writable_argument_context",
    "codegen_action_for_variable",
    "complete_semantic_policies",
    "convert_to_literal",
    "default_ownership_policy",
    "native_array_descriptor_argument_type",
    "native_array_descriptor_kind",
    "native_array_handle_build_requirements",
    "parse_pyi_text",
    "pytest",
    "replace",
    "semantic_ir_to_codegen_ast",
    "set_ownership_metadata",
)
