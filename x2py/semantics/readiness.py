from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

from x2py.semantics.metadata import PROJECTED_OUTPUT_METADATA

from .models import (
    EXTERNAL_TYPE_REF_METADATA,
    RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA,
    RESOLVED_OWNERSHIP_POLICY_METADATA,
    RESOLVED_RETURN_OWNERSHIP_POLICY_METADATA,
    SemanticArgument,
    SemanticClass,
    SemanticFunction,
    SemanticImport,
    SemanticMethod,
    SemanticModule,
    SemanticType,
    SemanticVariable,
)
from .native_contract import native_contract_issues
from .native_array_handles import native_array_descriptor_kind
from .policy_completion import complete_semantic_policies


__all__ = (
    "assess_prepared_semantic_wrap_readiness",
    "assess_pyi_wrap_readiness",
    "assess_semantic_wrap_readiness",
)


_BUILTIN_TYPES = frozenset(
    {
        "Any",
        "Bool",
        "Complex64",
        "Complex128",
        "Float32",
        "Float64",
        "Int",
        "Int8",
        "Int16",
        "Int32",
        "Int64",
        "Matrix",
        "None",
        "SizeT",
        "String",
        "UInt8",
        "UInt16",
        "UInt32",
        "UInt64",
        "Vector",
        "void",
    }
)
_CALLBACK_PLACEHOLDERS = frozenset({"Procedure", "Callback", "FunctionPointer", "CFunctionPointer"})
_IDENTIFIER_RE = re.compile(r"\b[A-Za-z_]\w*\b")
_SHAPE_INTRINSIC_CALLS = frozenset({"lbound", "shape", "size", "ubound"})
_NON_EXTENT_DIMENSIONS = frozenset({"", "*", ":", "::", "..."})
_MAX_SUPPORTED_ARRAY_RANK = 15
_POINTER_C_DESCRIPTOR_INTEROP_AVAILABLE = True
_ISO_C_KIND_TOKENS = frozenset(
    {
        "c_bool",
        "c_char",
        "c_double",
        "c_double_complex",
        "c_float",
        "c_float_complex",
        "c_int",
        "c_int16_t",
        "c_int32_t",
        "c_int64_t",
        "c_int8_t",
        "c_long_double",
        "c_long_double_complex",
        "c_long_long",
        "c_short",
        "c_signed_char",
        "c_size_t",
    }
)


def assess_pyi_wrap_readiness(
    paths: str | Path | Iterable[str | Path],
    *,
    encoding: str = "utf-8",
    native_language: str = "fortran",
) -> dict:
    """Load one or more edited .pyi files and assess semantic wrap-readiness."""
    from x2py.pipeline.pyi import pyi_paths_to_semantic_modules

    raw_paths = [paths] if isinstance(paths, str | Path) else list(paths)
    expanded = _expand_pyi_paths(raw_paths)
    modules = pyi_paths_to_semantic_modules(
        raw_paths,
        encoding=encoding,
        native_language=native_language,
    )
    return assess_semantic_wrap_readiness(
        modules,
        source=[str(path) for path in expanded],
        require_native_contract=True,
    )


def assess_semantic_wrap_readiness(
    semantic_ir: SemanticModule | Iterable[SemanticModule],
    *,
    source: str | list[str] | None = None,
    require_native_contract: bool = False,
) -> dict:
    """Complete semantic policies, then assess whether IR can drive wrapping.

    The parser is intentionally not consulted here. Once a user edits a .pyi
    interface, this semantic check treats that interface as the source of truth.
    """
    modules = complete_semantic_policies(semantic_ir)
    return assess_prepared_semantic_wrap_readiness(
        modules,
        source=source,
        require_native_contract=require_native_contract,
    )


def assess_prepared_semantic_wrap_readiness(
    semantic_ir: SemanticModule | Iterable[SemanticModule],
    *,
    source: str | list[str] | None = None,
    require_native_contract: bool = False,
) -> dict:
    """Assess policy-completed semantic IR without rerunning policy completion."""

    modules = list(semantic_ir) if not isinstance(semantic_ir, SemanticModule) else [semantic_ir]
    checker = _SemanticReadinessChecker(modules, require_native_contract=require_native_contract)
    return checker.assess(source=source)


def _expand_pyi_paths(paths: str | Path | Iterable[str | Path]) -> list[Path]:
    raw_paths = [paths] if isinstance(paths, str | Path) else list(paths)
    expanded: list[Path] = []
    for raw in raw_paths:
        path = Path(raw)
        if path.is_dir():
            expanded.extend(sorted(item for item in path.rglob("*.pyi") if item.is_file()))
        else:
            expanded.append(path)
    return sorted(set(expanded))


class _SemanticReadinessChecker:
    def __init__(self, modules: list[SemanticModule], *, require_native_contract: bool = False):
        self.modules = modules
        self.require_native_contract = require_native_contract
        self.index = _SemanticTypeIndex(modules)
        self._blockers: dict[str, dict] = {}
        self._unit_blockers: dict[str, dict] = {}

    def assess(self, *, source: str | list[str] | None) -> dict:
        counts = self._public_api_counts()
        if counts["n_functions"] + counts["n_classes"] + counts["n_variables"] == 0:
            self._add_blocker(
                "no_public_api",
                "The semantic interface does not declare any public wrapper API.",
                {"owner": "<semantic-ir>", "needs": ["public function, class, or variable"]},
                unit="<semantic-ir>",
                unit_kind="module",
            )

        for module in self.modules:
            self._check_module(module)

        blockers = list(self._blockers.values())
        return {
            "wrappable": not blockers,
            "source": source,
            "n_modules": len(self.modules),
            **counts,
            "wrappability_blockers": blockers,
            "unit_blockers": list(self._unit_blockers.values()),
            "why_not_wrappable": [blocker["message"] for blocker in blockers],
        }

    def _public_api_counts(self) -> dict[str, int]:
        n_functions = 0
        n_classes = 0
        n_variables = 0

        for module in self.modules:
            n_functions += sum(1 for func in module.functions if _is_public(func))
            n_functions += sum(
                1 for overload_set in module.overload_sets if any(_is_public(proc) for proc in overload_set.procedures)
            )
            n_variables += sum(1 for var in module.variables if _is_public(var))
            for cls in module.classes:
                if not isinstance(cls, SemanticClass):
                    continue
                if not _is_public(cls):
                    continue
                public_classes = [cls, *_iter_public_classes(cls)]
                n_classes += len(public_classes)
                n_functions += sum(
                    1 for public_class in public_classes for method in public_class.methods if _is_public(method)
                )
                n_functions += sum(
                    1
                    for public_class in public_classes
                    for overload_set in public_class.overload_sets
                    if any(_is_public(proc) for proc in overload_set.procedures)
                )

        return {
            "n_functions": n_functions,
            "n_classes": n_classes,
            "n_variables": n_variables,
        }

    def _check_module(self, module: SemanticModule) -> None:
        if self.require_native_contract:
            for issue in native_contract_issues(module):
                self._add_blocker(
                    issue.code,
                    issue.message,
                    {"owner": issue.owner, "item": issue.owner.rsplit(".", 1)[-1]},
                    unit=issue.owner,
                    unit_kind="native_contract",
                )
        self._check_metadata_blockers(
            getattr(module, "metadata", {}),
            owner=module.name,
            item=module.name,
            unit=module.name,
            unit_kind="module",
        )
        module_constants = _constant_values(module.variables)
        module_constant_names = _constant_names(module.variables)

        for var in module.variables:
            if not _is_public(var):
                continue
            self._check_ownership_policy(
                var.metadata.get(RESOLVED_OWNERSHIP_POLICY_METADATA),
                owner=f"{module.name}.{var.name}",
                item=var.name,
                unit=f"{module.name}.{var.name}",
                unit_kind="variable",
            )
            self._check_argument(
                var,
                owner=f"{module.name}.{var.name}",
                module=module,
                known_shape_symbols=set(module_constants),
                constant_names=module_constant_names,
                unit=f"{module.name}.{var.name}",
                unit_kind="variable",
            )

        for cls in module.classes:
            if not isinstance(cls, SemanticClass):
                continue
            if not _is_public(cls):
                continue
            self._check_class(
                cls,
                module=module,
                module_constants=module_constants,
                module_constant_names=module_constant_names,
            )

        for func in module.functions:
            if not _is_public(func):
                continue
            self._check_function(
                func,
                module=module,
                known_shape_symbols=set(module_constants),
                constant_names=module_constant_names,
                owner=f"{module.name}.{func.name}",
                unit=f"{module.name}.{func.name}",
                unit_kind="function",
            )
        for overload_set in module.overload_sets:
            for procedure in overload_set.procedures:
                if not _is_public(procedure):
                    continue
                self._check_function(
                    procedure,
                    module=module,
                    known_shape_symbols=set(module_constants),
                    constant_names=module_constant_names,
                    owner=f"{module.name}.{overload_set.name}",
                    unit=f"{module.name}.{overload_set.name}",
                    unit_kind="overload_set",
                )

    def _check_class(
        self,
        cls: SemanticClass,
        *,
        module: SemanticModule,
        module_constants: dict[str, str],
        module_constant_names: set[str],
    ) -> None:
        self._check_metadata_blockers(
            getattr(cls, "metadata", {}),
            owner=f"{module.name}.{cls.name}",
            item=cls.name,
            unit=f"{module.name}.{cls.name}",
            unit_kind="class",
        )
        class_symbols = {field.name for field in cls.fields}
        known_shape_symbols = set(module_constants) | class_symbols
        constant_names = module_constant_names | _constant_names(cls.fields)

        for nested in cls.classes:
            if not _is_public(nested):
                continue
            self._check_class(
                nested,
                module=module,
                module_constants=module_constants,
                module_constant_names=module_constant_names,
            )

        for field in cls.fields:
            self._check_ownership_policy(
                field.metadata.get(RESOLVED_OWNERSHIP_POLICY_METADATA),
                owner=f"{module.name}.{cls.name}.{field.name}",
                item=field.name,
                unit=f"{module.name}.{cls.name}",
                unit_kind="class",
            )
            self._check_argument(
                field,
                owner=f"{module.name}.{cls.name}.{field.name}",
                module=module,
                known_shape_symbols=known_shape_symbols,
                constant_names=constant_names,
                unit=f"{module.name}.{cls.name}",
                unit_kind="class",
            )

        for method in cls.methods:
            if not _is_public(method):
                continue
            self._check_function(
                method,
                module=module,
                known_shape_symbols=known_shape_symbols,
                constant_names=constant_names,
                owner=f"{module.name}.{cls.name}.{method.name}",
                unit=f"{module.name}.{cls.name}.{method.name}",
                unit_kind="method",
            )
        for overload_set in cls.overload_sets:
            for procedure in overload_set.procedures:
                if not _is_public(procedure):
                    continue
                self._check_function(
                    procedure,
                    module=module,
                    known_shape_symbols=known_shape_symbols,
                    constant_names=constant_names,
                    owner=f"{module.name}.{cls.name}.{overload_set.name}",
                    unit=f"{module.name}.{cls.name}.{overload_set.name}",
                    unit_kind="overload_set",
                )

    def _check_function(
        self,
        func: SemanticFunction | SemanticMethod,
        *,
        module: SemanticModule,
        known_shape_symbols: set[str],
        constant_names: set[str],
        owner: str,
        unit: str,
        unit_kind: str,
    ) -> None:
        self._check_metadata_blockers(
            getattr(func, "metadata", {}),
            owner=owner,
            item=func.name,
            unit=unit,
            unit_kind=unit_kind,
        )
        function_symbols = set(known_shape_symbols) | {arg.name for arg in func.arguments}
        self._check_bind_c_abi(func, module=module, owner=owner, unit=unit, unit_kind=unit_kind)
        for arg in func.arguments:
            if self._is_unsupported_polymorphic_argument(func, arg, module=module):
                self._add_blocker(
                    "fortran_polymorphic_policy_missing",
                    "Fortran class(...) arguments need an explicit dynamic-type and dispatch policy before they can be wrapped safely.",
                    {"owner": owner, "item": arg.name},
                    unit=unit,
                    unit_kind=unit_kind,
                )
            if self._is_unsupported_allocatable_output(arg):
                self._add_blocker(
                    "allocatable_scalar_replacement_unsupported",
                    "Allocatable scalar replacement needs explicit construction, ownership, and destruction policy before it can be wrapped safely.",
                    {
                        "owner": owner,
                        "item": arg.name,
                    },
                    unit=unit,
                    unit_kind=unit_kind,
                )
            if self._is_unsupported_pointer_output(arg):
                self._add_blocker(
                    "fortran_pointer_output_policy_missing",
                    "Fortran pointer output arguments need explicit ownership, lifetime, shape, contiguity, and deallocation policy before they can be wrapped safely.",
                    {
                        "owner": owner,
                        "item": arg.name,
                    },
                    unit=unit,
                    unit_kind=unit_kind,
                )
            else:
                self._check_ownership_policy(
                    arg.metadata.get(RESOLVED_OWNERSHIP_POLICY_METADATA),
                    owner=owner,
                    item=arg.name,
                    unit=unit,
                    unit_kind=unit_kind,
                )
            self._check_argument(
                arg,
                owner=f"{owner}.{arg.name}",
                module=module,
                known_shape_symbols=function_symbols,
                constant_names=constant_names,
                unit=unit,
                unit_kind=unit_kind,
            )
        if self._is_fortran_polymorphic(func.return_type):
            self._add_blocker(
                "fortran_polymorphic_policy_missing",
                "Fortran class(...) results need an explicit dynamic-type, allocation, and ownership policy before they can be wrapped safely.",
                {"owner": owner, "item": "return"},
                unit=unit,
                unit_kind=unit_kind,
            )
        self._check_ownership_policy(
            func.metadata.get(RESOLVED_RETURN_OWNERSHIP_POLICY_METADATA),
            owner=owner,
            item="return",
            unit=unit,
            unit_kind=unit_kind,
        )
        self._check_native_array_handle_policy(
            func.return_type,
            func.metadata.get(RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA),
            owner=f"{owner}.return",
            item="return",
            unit=unit,
            unit_kind=unit_kind,
        )
        self._check_type(
            func.return_type,
            owner=f"{owner}.return",
            item="return",
            module=module,
            known_shape_symbols=function_symbols,
            constant_names=constant_names,
            unit=unit,
            unit_kind=unit_kind,
        )

    def _check_bind_c_abi(
        self,
        func: SemanticFunction | SemanticMethod,
        *,
        module: SemanticModule,
        owner: str,
        unit: str,
        unit_kind: str,
    ) -> None:
        if not func.metadata.get("fortran_bind_c"):
            return
        for arg in func.arguments:
            semantic_type = arg.semantic_type
            if semantic_type.rank > 0:
                continue
            if self.index.is_bind_c_class(semantic_type.name, module):
                continue
            if self.index.is_wrapped_class(semantic_type.name, module):
                is_value = bool(getattr(arg.origin, "metadata", {}).get("value"))
                transfer = "by-value " if is_value else ""
                self._add_blocker(
                    "fortran_bind_c_derived_type_unsupported",
                    f"Fortran bind(C) {transfer}derived-type arguments must use a type declared bind(C); "
                    "x2py will not infer aggregate layout.",
                    {"owner": owner, "item": arg.name},
                    unit=unit,
                    unit_kind=unit_kind,
                )
                continue
            if not self._has_known_iso_c_kind(semantic_type):
                self._add_blocker(
                    "fortran_bind_c_abi_unsupported",
                    "Fortran bind(C) scalar declarations need a supported ISO C binding kind before wrapper generation.",
                    {"owner": owner, "item": arg.name},
                    unit=unit,
                    unit_kind=unit_kind,
                )
        if (
            func.return_type is not None
            and func.return_type.rank == 0
            and not self.index.is_bind_c_class(func.return_type.name, module)
            and not self._has_known_iso_c_kind(func.return_type)
        ):
            if self.index.is_wrapped_class(func.return_type.name, module):
                code = "fortran_bind_c_derived_type_unsupported"
                message = (
                    "Fortran bind(C) derived-type results must use a type declared bind(C); "
                    "x2py will not infer aggregate layout."
                )
            else:
                code = "fortran_bind_c_abi_unsupported"
                message = (
                    "Fortran bind(C) scalar declarations need a supported ISO C binding kind before wrapper generation."
                )
            self._add_blocker(
                code,
                message,
                {"owner": owner, "item": "return"},
                unit=unit,
                unit_kind=unit_kind,
            )

    def _check_argument(
        self,
        arg: SemanticArgument | SemanticVariable,
        *,
        owner: str,
        module: SemanticModule,
        known_shape_symbols: set[str],
        constant_names: set[str],
        unit: str,
        unit_kind: str,
    ) -> None:
        self._check_metadata_blockers(
            getattr(arg, "metadata", {}),
            owner=owner,
            item=arg.name,
            unit=unit,
            unit_kind=unit_kind,
        )
        self._check_native_array_handle_policy(
            arg.semantic_type,
            arg.metadata.get(RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA),
            owner=owner,
            item=arg.name,
            unit=unit,
            unit_kind=unit_kind,
        )
        self._check_type(
            arg.semantic_type,
            owner=owner,
            item=arg.name,
            module=module,
            known_shape_symbols=known_shape_symbols,
            constant_names=constant_names,
            unit=unit,
            unit_kind=unit_kind,
        )

    def _check_type(
        self,
        semantic_type: SemanticType | None,
        *,
        owner: str,
        item: str,
        module: SemanticModule,
        known_shape_symbols: set[str],
        constant_names: set[str],
        unit: str,
        unit_kind: str,
    ) -> None:
        if semantic_type is None:
            return

        self._check_metadata_blockers(
            getattr(semantic_type, "metadata", {}),
            owner=owner,
            item=item,
            unit=unit,
            unit_kind=unit_kind,
        )
        self._check_runtime_validation_policy(
            semantic_type,
            owner=owner,
            item=item,
            unit=unit,
            unit_kind=unit_kind,
        )
        if self._is_assumed_type(semantic_type):
            self._add_blocker(
                "fortran_assumed_type_policy_missing",
                "Fortran assumed-type type(*) arguments need an explicit dtype and descriptor policy.",
                {"owner": owner, "item": item},
                unit=unit,
                unit_kind=unit_kind,
            )
            return
        self._check_array_contract(
            semantic_type,
            owner=owner,
            item=item,
            unit=unit,
            unit_kind=unit_kind,
        )

        type_name = semantic_type.name
        if type_name in _CALLBACK_PLACEHOLDERS:
            self._add_callback_blocker(type_name, owner, item, unit=unit, unit_kind=unit_kind)
            return

        if semantic_type.storage is not None and semantic_type.storage.kind == "callback":
            self._check_prototype_reference(
                semantic_type,
                owner=owner,
                item=item,
                module=module,
                known_shape_symbols=known_shape_symbols,
                constant_names=constant_names,
                unit=unit,
                unit_kind=unit_kind,
            )
            return

        if not self.index.is_known_type(type_name, module) and not _is_external_type_ref(semantic_type):
            self._add_blocker(
                "unresolved_semantic_types",
                "Some semantic type references are not declared by the .pyi interface or its imports.",
                {"owner": owner, "item": item, "type": type_name},
                unit=unit,
                unit_kind=unit_kind,
            )

        self._check_shape_symbols(
            semantic_type,
            owner=owner,
            item=item,
            known_shape_symbols=known_shape_symbols,
            constant_names=constant_names,
            unit=unit,
            unit_kind=unit_kind,
        )

    def _check_runtime_validation_policy(
        self,
        semantic_type: SemanticType,
        *,
        owner: str,
        item: str,
        unit: str,
        unit_kind: str,
    ) -> None:
        constraints = sorted(
            {constraint.name for constraint in semantic_type.constraints if constraint.name != "Constant"}
        )
        if constraints:
            self._add_blocker(
                "fortran_runtime_constraints_unsupported",
                "Generic semantic constraints do not yet have Fortran wrapper runtime validators.",
                {
                    "owner": owner,
                    "item": item,
                    "constraints": constraints,
                },
                unit=unit,
                unit_kind=unit_kind,
            )
        if semantic_type.coercions:
            self._add_blocker(
                "fortran_runtime_coercions_unsupported",
                "Semantic coercions do not yet have Fortran wrapper conversion actions.",
                {
                    "owner": owner,
                    "item": item,
                    "coercions": [coercion.source_type for coercion in semantic_type.coercions],
                },
                unit=unit,
                unit_kind=unit_kind,
            )

    def _check_ownership_policy(
        self,
        decision,
        *,
        owner: str,
        item: str,
        unit: str,
        unit_kind: str,
    ) -> None:
        if decision is None:
            return
        if not decision.is_blocked:
            return
        self._add_blocker(
            "fortran_ownership_policy_blocked",
            "This value needs explicit ownership, transfer, lifetime, and destruction policy before it can be wrapped safely.",
            {
                "owner": owner,
                "item": item,
                "policy": decision.blocker or decision.reason,
            },
            unit=unit,
            unit_kind=unit_kind,
        )

    def _check_native_array_handle_policy(
        self,
        semantic_type: SemanticType | None,
        policy,
        *,
        owner: str,
        item: str,
        unit: str,
        unit_kind: str,
    ) -> None:
        if native_array_descriptor_kind(semantic_type) is None:
            return
        if policy is None:
            self._add_blocker(
                "native_array_handle_policy_missing",
                "Native array handles need completed descriptor ownership, lifetime, extraction, and operation policy before wrapper lowering.",
                {
                    "owner": owner,
                    "item": item,
                },
                unit=unit,
                unit_kind=unit_kind,
            )
            return
        self._check_pointer_c_descriptor_interop(policy, owner=owner, item=item, unit=unit, unit_kind=unit_kind)
        if not getattr(policy, "is_blocked", False):
            codegen_blocker = self._native_array_handle_codegen_blocker(policy)
            if codegen_blocker is None:
                return
            self._add_blocker(
                "native_array_handle_codegen_unsupported",
                "Native array handle policy is complete, but wrapper generation for this handle path is not implemented.",
                {
                    "owner": owner,
                    "item": item,
                    "policy": codegen_blocker,
                    "descriptor_kind": getattr(policy, "descriptor_kind", None),
                    "handle_kind": getattr(policy, "handle_kind", None),
                },
                unit=unit,
                unit_kind=unit_kind,
            )
            return
        self._add_blocker(
            "native_array_handle_policy_blocked",
            "Native array handle policy is incomplete or unsupported for wrapper lowering.",
            {
                "owner": owner,
                "item": item,
                "policy": getattr(policy, "blocker", None) or getattr(policy, "handle_kind", "unsupported"),
                "descriptor_kind": getattr(policy, "descriptor_kind", None),
                "handle_kind": getattr(policy, "handle_kind", None),
            },
            unit=unit,
            unit_kind=unit_kind,
        )

    def _check_pointer_c_descriptor_interop(
        self,
        policy,
        *,
        owner: str,
        item: str,
        unit: str,
        unit_kind: str,
    ) -> None:
        if (
            not getattr(policy, "requires_pointer_c_descriptor_interop", False)
            or _POINTER_C_DESCRIPTOR_INTEROP_AVAILABLE
        ):
            return
        self._add_blocker(
            "pointer_c_descriptor_interop_unavailable",
            "Pointer array descriptor-view extraction requires TS 29113 C descriptor interop, "
            "which is not implemented by the current wrapper generator.",
            {
                "owner": owner,
                "item": item,
                "descriptor_kind": getattr(policy, "descriptor_kind", None),
                "handle_kind": getattr(policy, "handle_kind", None),
                "descriptor_interop": getattr(policy, "descriptor_interop", None),
                "to_numpy": getattr(policy, "to_numpy", None),
                "descriptor_layout": "ts29113_required",
                "compiler_specific_layout": "rejected",
                "fallback": "readiness_failure",
            },
            unit=unit,
            unit_kind=unit_kind,
        )

    @staticmethod
    def _native_array_handle_codegen_blocker(_policy) -> str | None:
        return None

    def _check_array_contract(
        self,
        semantic_type: SemanticType,
        *,
        owner: str,
        item: str,
        unit: str,
        unit_kind: str,
    ) -> None:
        if semantic_type.rank <= 0:
            return
        if semantic_type.rank > _MAX_SUPPORTED_ARRAY_RANK:
            self._add_blocker(
                "fortran_array_rank_unsupported",
                f"Fortran wrappers support array ranks 1 through {_MAX_SUPPORTED_ARRAY_RANK}.",
                {
                    "owner": owner,
                    "item": item,
                    "rank": semantic_type.rank,
                    "max_rank": _MAX_SUPPORTED_ARRAY_RANK,
                },
                unit=unit,
                unit_kind=unit_kind,
            )
        if self._is_assumed_type(semantic_type):
            self._add_blocker(
                "fortran_assumed_type_policy_missing",
                "Fortran assumed-type type(*) arguments need an explicit dtype and descriptor policy.",
                {"owner": owner, "item": item},
                unit=unit,
                unit_kind=unit_kind,
            )
        if semantic_type.name not in _BUILTIN_TYPES and not _is_external_type_ref(semantic_type):
            self._add_blocker(
                "fortran_derived_type_array_policy_missing",
                "Fortran arrays of derived type values need explicit layout and ownership policy.",
                {"owner": owner, "item": item, "type": semantic_type.name},
                unit=unit,
                unit_kind=unit_kind,
            )

    @classmethod
    def _is_unsupported_allocatable_output(cls, argument: SemanticArgument) -> bool:
        semantic_type = argument.semantic_type
        if not (
            semantic_type is not None
            and semantic_type.rank == 0
            and semantic_type.metadata.get("fortran_allocatable")
            and cls._argument_uses_writable_storage(argument)
        ):
            return False
        scalar_name = semantic_type.dtype or semantic_type.name
        if scalar_name not in _BUILTIN_TYPES or scalar_name in {"String", "Void"}:
            return True
        decision = argument.metadata.get(RESOLVED_OWNERSHIP_POLICY_METADATA)
        return bool(decision is not None and decision.is_blocked)

    @staticmethod
    def _argument_uses_writable_storage(argument: SemanticArgument) -> bool:
        storage = argument.semantic_type.storage
        return bool(
            argument.semantic_type.ownership.mutable
            or (storage is not None and (storage.mutable or not storage.read_only))
            or argument.metadata.get(PROJECTED_OUTPUT_METADATA)
        )

    @classmethod
    def _is_unsupported_pointer_output(cls, argument: SemanticArgument) -> bool:
        if not cls._is_pointer(argument.semantic_type):
            return False
        decision = argument.metadata.get(RESOLVED_OWNERSHIP_POLICY_METADATA)
        if decision is None:
            return False
        return decision.is_blocked

    @staticmethod
    def _is_pointer_array(semantic_type: SemanticType | None) -> bool:
        if semantic_type is None or semantic_type.storage is None or semantic_type.storage.array is None:
            return False
        return semantic_type.storage.array.pointer

    @staticmethod
    def _is_pointer(semantic_type: SemanticType | None) -> bool:
        if semantic_type is None:
            return False
        storage = semantic_type.storage
        return bool(
            semantic_type.metadata.get("fortran_pointer")
            or (storage is not None and storage.array is not None and storage.array.pointer)
        )

    @staticmethod
    def _is_assumed_type(semantic_type: SemanticType | None) -> bool:
        if semantic_type is None:
            return False
        source_type = (semantic_type.origin.source_type or "").casefold().replace(" ", "")
        return "type(*)" in source_type or "class(*)" in source_type

    def _is_unsupported_polymorphic_argument(
        self,
        func: SemanticFunction | SemanticMethod,
        arg: SemanticArgument,
        *,
        module: SemanticModule,
    ) -> bool:
        if not self._is_fortran_polymorphic(arg.semantic_type):
            return False
        if isinstance(func, SemanticMethod) and not func.is_static and str(func.passed_object_name) == str(arg.name):
            return False
        if func.metadata.get("fortran_type_bound_target") and str(
            func.metadata.get("fortran_passed_object_name")
        ) == str(arg.name):
            return False
        return not self._is_supported_scalar_polymorphic_input_argument(arg, module=module)

    def _is_supported_scalar_polymorphic_input_argument(
        self,
        arg: SemanticArgument,
        *,
        module: SemanticModule,
    ) -> bool:
        semantic_type = arg.semantic_type
        if semantic_type is None or semantic_type.rank != 0:
            return False
        if self._argument_uses_writable_storage(arg):
            return False
        if semantic_type.metadata.get("fortran_allocatable"):
            return False
        if getattr(arg.origin, "metadata", {}).get("pointer"):
            return False
        return self.index.is_wrapped_class(semantic_type.name, module)

    @staticmethod
    def _is_fortran_polymorphic(semantic_type: SemanticType | None) -> bool:
        return bool(
            semantic_type is not None
            and semantic_type.metadata.get("fortran_polymorphic")
            and not _SemanticReadinessChecker._is_assumed_type(semantic_type)
        )

    @staticmethod
    def _has_known_iso_c_kind(semantic_type: SemanticType) -> bool:
        source_type = (semantic_type.origin.source_type or "").casefold()
        return any(token in source_type for token in _ISO_C_KIND_TOKENS)

    def _check_prototype_reference(
        self,
        semantic_type: SemanticType,
        *,
        owner: str,
        item: str,
        module: SemanticModule,
        known_shape_symbols: set[str],
        constant_names: set[str],
        unit: str,
        unit_kind: str,
    ) -> None:
        arguments = semantic_type.metadata.get("arguments")
        return_type = semantic_type.metadata.get("return")
        if not isinstance(arguments, list) or return_type is None:
            self._add_callback_blocker(semantic_type.name, owner, item, unit=unit, unit_kind=unit_kind)
            return

        for index, callback_arg in enumerate(arguments):
            self._check_type(
                callback_arg,
                owner=f"{owner}.callback_arg_{index}",
                item=f"{item}[{index}]",
                module=module,
                known_shape_symbols=known_shape_symbols,
                constant_names=constant_names,
                unit=unit,
                unit_kind=unit_kind,
            )
        self._check_type(
            return_type,
            owner=f"{owner}.callback_return",
            item=f"{item}.return",
            module=module,
            known_shape_symbols=known_shape_symbols,
            constant_names=constant_names,
            unit=unit,
            unit_kind=unit_kind,
        )

    def _check_shape_symbols(
        self,
        semantic_type: SemanticType,
        *,
        owner: str,
        item: str,
        known_shape_symbols: set[str],
        constant_names: set[str],
        unit: str,
        unit_kind: str,
    ) -> None:
        for expression in _shape_expressions(semantic_type):
            intrinsic_calls = _called_shape_intrinsics(expression)
            for symbol in sorted(_shape_symbols(expression)):
                if symbol in known_shape_symbols:
                    continue
                if symbol in constant_names:
                    self._add_blocker(
                        "missing_compile_time_values",
                        "Some compile-time constants are declared but do not have literal .pyi values.",
                        {"owner": owner, "item": item, "symbol": symbol, "expression": expression},
                        unit=unit,
                        unit_kind=unit_kind,
                    )
                    continue
                if symbol in intrinsic_calls:
                    continue
                self._add_blocker(
                    "unresolved_shape_symbols",
                    "Some shape expressions refer to symbols not supplied by the semantic interface.",
                    {"owner": owner, "item": item, "symbol": symbol, "expression": expression},
                    unit=unit,
                    unit_kind=unit_kind,
                )

    def _check_metadata_blockers(
        self,
        metadata: dict,
        *,
        owner: str,
        item: str,
        unit: str,
        unit_kind: str,
    ) -> None:
        blockers = metadata.get("readiness_blockers") if isinstance(metadata, dict) else None
        if not isinstance(blockers, list):
            return

        for blocker in blockers:
            if not isinstance(blocker, dict):
                continue
            code = str(blocker.get("code") or "semantic_readiness_blocker")
            message = str(blocker.get("message") or "Semantic metadata marks this item as not wrappable.")
            raw_items = blocker.get("items")
            if raw_items is None:
                raw_items = [blocker.get("item") or {}]
            if not isinstance(raw_items, list):
                raw_items = [raw_items]

            blocker_unit = str(blocker.get("unit") or unit)
            blocker_unit_kind = str(blocker.get("unit_kind") or unit_kind)
            for raw_item in raw_items:
                payload = dict(raw_item) if isinstance(raw_item, dict) else {"detail": raw_item}
                payload.setdefault("owner", owner)
                payload.setdefault("item", item)
                self._add_blocker(
                    code,
                    message,
                    payload,
                    unit=blocker_unit,
                    unit_kind=blocker_unit_kind,
                )

    def _add_callback_blocker(
        self,
        type_name: str,
        owner: str,
        item: str,
        *,
        unit: str,
        unit_kind: str,
    ) -> None:
        self._add_blocker(
            "callback_signature_incomplete",
            "Some callback or procedure arguments need a complete named prototype in the .pyi file.",
            {
                "owner": owner,
                "item": item,
                "type": type_name,
                "needs": [
                    "callback argument order",
                    "callback argument types",
                    "callback return type",
                ],
            },
            unit=unit,
            unit_kind=unit_kind,
        )

    def _add_blocker(
        self,
        code: str,
        message: str,
        item: dict,
        *,
        unit: str,
        unit_kind: str,
    ) -> None:
        blocker = self._blockers.setdefault(code, {"code": code, "message": message, "items": []})
        blocker["items"].append(item)

        unit_blocker = self._unit_blockers.setdefault(
            unit,
            {"unit": unit, "kind": unit_kind, "blockers": []},
        )
        for existing in unit_blocker["blockers"]:
            if existing["code"] == code:
                existing["items"].append(item)
                break
        else:
            unit_blocker["blockers"].append({"code": code, "message": message, "items": [item]})


class _SemanticTypeIndex:
    def __init__(self, modules: list[SemanticModule]):
        self.known_types = set(_BUILTIN_TYPES)
        self.wrapped_class_names: set[str] = set()
        self.bind_c_class_names: set[str] = set()
        self.imported_modules_by_module: dict[str, set[str]] = {}
        self.import_aliases_by_module: dict[str, set[str]] = {}

        for module in modules:
            for declaration in module.classes:
                if isinstance(declaration, SemanticClass):
                    names = _class_type_names(declaration, module_name=module.name)
                    self.known_types.update(names)
                    self.wrapped_class_names.update(names)
                    if declaration.metadata.get("fortran_bind_c"):
                        self.bind_c_class_names.update(names)
                else:
                    self.known_types.add(declaration.name)
                    self.known_types.add(f"{module.name}.{declaration.name}")
            imported_modules, import_aliases, imported_types = _import_index(module.imports)
            self.imported_modules_by_module[module.name] = imported_modules
            self.import_aliases_by_module[module.name] = import_aliases
            self.known_types.update(imported_types)

    def is_known_type(self, name: str, module: SemanticModule) -> bool:
        if name in self.known_types:
            return True
        if "." not in name:
            return False
        module_name = name.rsplit(".", 1)[0]
        first_part = name.split(".", 1)[0]
        imported_modules = self.imported_modules_by_module.get(module.name, set())
        import_aliases = self.import_aliases_by_module.get(module.name, set())
        return module_name in imported_modules or first_part in import_aliases

    def is_wrapped_class(self, name: str, module: SemanticModule) -> bool:
        if name in self.wrapped_class_names:
            return True
        qualified = f"{module.name}.{name}"
        return qualified in self.wrapped_class_names

    def is_bind_c_class(self, name: str, module: SemanticModule) -> bool:
        if name in self.bind_c_class_names:
            return True
        qualified = f"{module.name}.{name}"
        return qualified in self.bind_c_class_names


def _import_index(imports: list[str | SemanticImport]) -> tuple[set[str], set[str], set[str]]:
    imported_modules: set[str] = set()
    import_aliases: set[str] = set()
    imported_types: set[str] = set()

    for imp in imports:
        if isinstance(imp, str):
            module_name, _, alias = imp.partition(" as ")
            imported_modules.add(module_name.strip())
            if alias:
                import_aliases.add(alias.strip())
            continue

        imported_modules.add(imp.module)
        for item in imp.items:
            exported = item.target or item.source
            imported_types.add(exported)
            imported_types.add(f"{imp.module}.{item.source}")
            if item.target:
                imported_types.add(f"{imp.module}.{item.target}")

    return imported_modules, import_aliases, imported_types


def _iter_public_classes(cls: SemanticClass):
    for nested in cls.classes:
        if _is_public(nested):
            yield nested
            yield from _iter_public_classes(nested)


def _class_type_names(cls: SemanticClass, *, module_name: str, prefix: str = "") -> set[str]:
    qualified = f"{prefix}.{cls.name}" if prefix else cls.name
    names = {cls.name, qualified, f"{module_name}.{qualified}"}
    for nested in cls.classes:
        names.update(_class_type_names(nested, module_name=module_name, prefix=qualified))
    return names


def _constant_values(arguments: list[SemanticVariable]) -> dict[str, str]:
    return {
        arg.name: str(arg.default_value)
        for arg in arguments
        if _is_constant(arg.semantic_type) and arg.default_value is not None
    }


def _constant_names(arguments: list[SemanticVariable]) -> set[str]:
    return {arg.name for arg in arguments if _is_constant(arg.semantic_type)}


def _is_constant(semantic_type: SemanticType) -> bool:
    return any(constraint.name == "Constant" for constraint in semantic_type.constraints)


def _is_external_type_ref(semantic_type: SemanticType) -> bool:
    ref = semantic_type.metadata.get(EXTERNAL_TYPE_REF_METADATA)
    return (
        isinstance(ref, dict)
        and isinstance(ref.get("name"), str)
        and bool(ref["name"])
        and isinstance(ref.get("origin_module"), str)
        and bool(ref["origin_module"])
        and ref.get("representation") in {"opaque", "wrapped"}
    )


def _shape_expressions(semantic_type: SemanticType) -> list[str]:
    storage = semantic_type.storage
    array = storage.array if storage is not None else None
    shape_sources = [semantic_type.shape]
    if array is not None:
        shape_sources.append(array.shape)
    expressions = []
    for dimensions in shape_sources:
        axes = array.axes if array is not None and len(array.axes) == len(dimensions) else ()
        for index, dimension in enumerate(dimensions):
            axis = axes[index] if axes else None
            expression = _extent_expression(str(dimension), axis=axis)
            if expression is not None and expression not in expressions:
                expressions.append(expression)
    return expressions


def _extent_expression(dimension: str, *, axis: str | None) -> str | None:
    expression = dimension.strip()
    if axis == "strided" and expression.endswith(":Strided"):
        expression = expression[: -len("Strided")]
    return None if expression in _NON_EXTENT_DIMENSIONS else expression


def _iter_expression_values(value) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _iter_expression_values(item)
    elif isinstance(value, list | tuple):
        for item in value:
            yield from _iter_expression_values(item)


def _shape_symbols(expression: str) -> set[str]:
    return {match.group(0) for match in _IDENTIFIER_RE.finditer(expression)}


def _called_shape_intrinsics(expression: str) -> set[str]:
    intrinsics = set()
    for match in _IDENTIFIER_RE.finditer(expression):
        symbol = match.group(0)
        suffix = expression[match.end() :].lstrip()
        if symbol.casefold() in _SHAPE_INTRINSIC_CALLS and suffix.startswith("("):
            intrinsics.add(symbol)
    return intrinsics


def _is_public(node) -> bool:
    return getattr(node, "visibility", "public") != "private"
