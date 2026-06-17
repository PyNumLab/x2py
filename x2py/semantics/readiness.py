from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

from .models import (
    EXTERNAL_TYPE_REF_METADATA,
    SemanticArgument,
    SemanticClass,
    SemanticEnum,
    SemanticFunction,
    SemanticImport,
    SemanticMethod,
    SemanticModule,
    SemanticType,
    SemanticVariable,
)
from .pyi_parser import load_pyi_modules


__all__ = ("assess_pyi_wrap_readiness", "assess_semantic_wrap_readiness")


_BUILTIN_TYPES = frozenset(
    {
        "Any",
        "Bool",
        "Callable",
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


def assess_pyi_wrap_readiness(
    paths: str | Path | Iterable[str | Path],
    *,
    encoding: str = "utf-8",
) -> dict:
    """Load one or more edited .pyi files and assess semantic wrap-readiness."""
    raw_paths = [paths] if isinstance(paths, str | Path) else list(paths)
    expanded = _expand_pyi_paths(raw_paths)
    modules = load_pyi_modules(raw_paths, encoding=encoding)
    return assess_semantic_wrap_readiness(modules, source=[str(path) for path in expanded])


def assess_semantic_wrap_readiness(
    semantic_ir: SemanticModule | Iterable[SemanticModule],
    *,
    source: str | list[str] | None = None,
) -> dict:
    """Assess whether semantic IR is complete enough to drive wrapping.

    The parser is intentionally not consulted here. Once a user edits a .pyi
    interface, this semantic check treats that interface as the source of truth.
    """
    modules = list(semantic_ir) if not isinstance(semantic_ir, SemanticModule) else [semantic_ir]
    checker = _SemanticReadinessChecker(modules)
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
    def __init__(self, modules: list[SemanticModule]):
        self.modules = modules
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
            if self._is_allocatable_array(var.semantic_type) and not var.semantic_type.metadata.get("fortran_target"):
                self._add_blocker(
                    "allocatable_module_target_missing",
                    "Borrowed zero-copy module views require allocatable module arrays to have the Fortran target attribute.",
                    {
                        "owner": f"{module.name}.{var.name}",
                        "item": var.name,
                    },
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

        for enum in module.enums:
            if not _is_public(enum):
                continue
            self._check_enum(
                enum,
                module=module,
                known_shape_symbols=set(module_constants),
                constant_names=module_constant_names,
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

    def _check_enum(
        self,
        enum: SemanticEnum,
        *,
        module: SemanticModule,
        known_shape_symbols: set[str],
        constant_names: set[str],
    ) -> None:
        owner = f"{module.name}.{enum.name}"
        self._check_metadata_blockers(
            enum.metadata,
            owner=owner,
            item=enum.name,
            unit=owner,
            unit_kind="enum",
        )
        self._check_type(
            enum.underlying_type,
            owner=owner,
            item=enum.name,
            module=module,
            known_shape_symbols=known_shape_symbols,
            constant_names=constant_names,
            unit=owner,
            unit_kind="enum",
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
        for arg in func.arguments:
            if self._is_unsupported_allocatable_output(arg.semantic_type, arg.intent):
                self._add_blocker(
                    "allocatable_replacement_policy_missing",
                    "Allocatable inout arrays need a replacement policy before they can be wrapped safely.",
                    {
                        "owner": owner,
                        "item": arg.name,
                        "intent": arg.intent,
                    },
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

        type_name = semantic_type.name
        if type_name in _CALLBACK_PLACEHOLDERS:
            self._add_callback_blocker(type_name, owner, item, unit=unit, unit_kind=unit_kind)
            return

        if type_name == "Callable":
            self._check_callable_type(
                semantic_type,
                owner=owner,
                item=item,
                module=module,
                known_shape_symbols=known_shape_symbols,
                constant_names=constant_names,
                unit=unit,
                unit_kind=unit_kind,
            )

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

    @classmethod
    def _is_unsupported_allocatable_output(cls, semantic_type: SemanticType | None, intent: str) -> bool:
        return cls._is_allocatable_array(semantic_type) and str(intent).lower() == "inout"

    @staticmethod
    def _is_allocatable_array(semantic_type: SemanticType | None) -> bool:
        if semantic_type is None or semantic_type.storage is None or semantic_type.storage.array is None:
            return False
        return semantic_type.storage.array.allocatable

    def _check_callable_type(
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
            self._add_callback_blocker("Callable", owner, item, unit=unit, unit_kind=unit_kind)
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
            "Some callback or procedure arguments need complete Callable[[...], ...] metadata in the .pyi file.",
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
        self.imported_modules_by_module: dict[str, set[str]] = {}
        self.import_aliases_by_module: dict[str, set[str]] = {}

        for module in modules:
            for declaration in module.classes:
                if isinstance(declaration, SemanticClass):
                    self.known_types.update(_class_type_names(declaration, module_name=module.name))
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
    expressions = list(semantic_type.shape)
    storage = semantic_type.storage
    if storage is not None and storage.array is not None:
        expressions.extend(storage.array.shape)
    return expressions


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
    return {match.group(0) for match in _IDENTIFIER_RE.finditer(expression) if not match.group(0).isdigit()}


def _is_public(node) -> bool:
    return getattr(node, "visibility", "public") != "private"
