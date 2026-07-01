from __future__ import annotations

import ast
import re
from collections.abc import Iterable
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path

from x2py.numpy_types import SEMANTIC_DTYPE_TO_NUMPY_DTYPE
from x2py.ownership_policy import OWNERSHIP_POLICY_METADATA, set_ownership_metadata, set_pointer_policy_metadata

from .models import (
    EXTERNAL_TYPE_REF_METADATA,
    FORTRAN_GENERIC_NAME_METADATA,
    OVERLOAD_KIND_METADATA,
    OVERLOAD_TARGET_METADATA,
    PYI_BIND_TARGET_METADATA,
    PYI_LOADED_METADATA,
    PYI_PROJECTED_OUTPUT_METADATA,
    PYTHON_BOUND_POSITION_METADATA,
    PYTHON_METHOD_NAME_METADATA,
    PYTHON_STATIC_METADATA,
    PYTHON_VALUE_IMMUTABLE,
    PYTHON_VALUE_MUTABILITY_METADATA,
    PYI_SUPPRESS_DEFAULT_CONSTRUCTOR_METADATA,
    PYI_USER_PRIVATE_METADATA,
    RUNTIME_HOLD_GIL_METADATA,
    RUNTIME_STATUS_ERROR_METADATA,
    ProjectionMapping,
    ProcedureOverloadSet,
    SemanticArgument,
    SemanticArrayContract,
    SemanticClass,
    SemanticConstraint,
    SemanticField,
    SemanticFunction,
    SemanticImport,
    SemanticImportItem,
    SemanticMethod,
    SemanticModule,
    SemanticOrigin,
    SemanticStorageContract,
    SemanticType,
    SemanticVariable,
    _iter_module_semantic_types,
)
from .pyi_parser import parse_pyi_text as parse_pyi_ast_text

__all__ = ("convert_pyi_to_ir", "load_pyi_file", "load_pyi_modules", "parse_pyi_text")


_PYI_OPTIONAL_RETURN_METADATA = "_pyi_optional_return"
_WRITABLE_INTENTS = {"out", "inout"}


def load_pyi_file(path: str | Path, *, module_name: str | None = None, encoding: str = "utf-8") -> SemanticModule:
    pyi_path = Path(path)
    try:
        return parse_pyi_text(
            pyi_path.read_text(encoding=encoding),
            module_name=module_name or pyi_path.stem,
            filename=str(pyi_path),
        )
    except ValueError as exc:
        raise ValueError(f"{pyi_path}: {exc}") from exc


def load_pyi_modules(
    paths: str | Path | Iterable[str | Path],
    *,
    encoding: str = "utf-8",
) -> list[SemanticModule]:
    raw_paths = [paths] if isinstance(paths, str | Path) else list(paths)
    expanded: dict[Path, str | None] = {}
    for raw_path in raw_paths:
        path = Path(raw_path)
        if path.is_dir():
            for item in path.rglob("*.pyi"):
                if not item.is_file():
                    continue
                module_name = ".".join(item.relative_to(path).with_suffix("").parts)
                previous = expanded.get(item)
                if previous is not None and previous != module_name:
                    raise ValueError(f"Ambiguous module name for {item}: {previous!r} or {module_name!r}")
                expanded[item] = module_name
        else:
            expanded.setdefault(path, None)
    return _reconcile_external_type_refs(
        [
            load_pyi_file(path, module_name=module_name, encoding=encoding)
            for path, module_name in sorted(expanded.items())
        ]
    )


def convert_pyi_to_ir(source: str, *, module_name: str = "<pyi>") -> SemanticModule:
    return parse_pyi_text(source, module_name=module_name)


def parse_pyi_text(source: str, *, module_name: str = "<pyi>", filename: str = "<pyi>") -> SemanticModule:
    tree = parse_pyi_ast_text(source, filename=filename)
    module = _PyiAstParser(module_name=module_name, source=source).parse(tree)
    _annotate_imported_external_type_refs(module)
    return module


@dataclass
class _Decorators:
    visibility: str = "public"
    projection: list[ProjectionMapping] = field(default_factory=list)
    has_native_call: bool = False
    overload_target: str | None = None
    overload_generic: str | None = None
    bind_target: str | None = None
    native_type: dict[str, object] | None = None
    external: bool = False
    is_static: bool = False
    hold_gil: bool = False
    error_status_policy: dict[str, object] | None = None


@dataclass
class _PendingOverload:
    owner: SemanticModule | SemanticClass
    declaration: SemanticFunction
    target: str
    generic_name: str | None = None


class _PyiAstParser:
    def __init__(self, *, module_name: str, source: str = ""):
        self.module = SemanticModule(name=module_name, metadata={PYI_LOADED_METADATA: True})
        self.source = source
        self._pending_overloads: list[_PendingOverload] = []

    def parse(self, tree: ast.Module) -> SemanticModule:
        _ModuleVisitor(self).visit(tree)
        self._resolve_overloads()
        self._restore_type_bound_targets()
        return self.module

    def import_from(self, node: ast.ImportFrom) -> SemanticImport:
        module_name = "." * node.level + (node.module or "")
        return SemanticImport(
            module=module_name,
            items=[SemanticImportItem(source=alias.name, target=alias.asname) for alias in node.names],
        )

    def import_name(self, node: ast.Import) -> str:
        return ", ".join(f"{alias.name} as {alias.asname}" if alias.asname else alias.name for alias in node.names)

    def class_def(
        self,
        node: ast.ClassDef,
        *,
        visibility: str,
        native_type: dict[str, object] | None = None,
    ) -> SemanticClass:
        body = _ClassBodyVisitor(self, class_name=node.name)
        body.visit_body(node.body)
        if body.constructor_from_fields and body.has_bound_constructor:
            raise ValueError("Direct constructor bindings replace the generated field constructor; remove one __init__")
        base_classes = [ast.unparse(base) for base in node.bases]
        origin = self._origin(
            source_language="fortran" if body.constructor_from_fields or native_type is not None else None,
            user_private=visibility == "private",
        )
        if not body.constructor_from_fields:
            origin.metadata[PYI_SUPPRESS_DEFAULT_CONSTRUCTOR_METADATA] = True

        metadata = self._class_metadata(base_classes)
        if native_type is not None:
            metadata["fortran_type_attributes"] = list(native_type.get("attributes", ()))
            finalizers = list(native_type.get("finalizers", ()))
            if finalizers:
                metadata["fortran_final_procedures"] = finalizers
        semantic_class = SemanticClass(
            name=node.name,
            native_name=node.name,
            fields=body.fields,
            methods=body.methods,
            classes=body.classes,
            base_classes=base_classes,
            metadata=metadata,
            visibility=visibility,
            origin=origin,
        )
        self._validate_bound_constructor_targets(semantic_class)
        self._pending_overloads.extend(
            _PendingOverload(semantic_class, declaration, target, generic_name)
            for declaration, target, generic_name in body.pending_overloads
        )
        return semantic_class

    @staticmethod
    def _validate_bound_constructor_targets(semantic_class: SemanticClass) -> None:
        for constructor in semantic_class.methods:
            target_name = constructor.metadata.get(PYI_BIND_TARGET_METADATA)
            if constructor.name != "__init__" or not isinstance(target_name, str):
                continue
            candidates = [
                method for method in semantic_class.methods if method is not constructor and method.name == target_name
            ]
            if not candidates:
                raise ValueError(f"Bound constructor references missing class method {target_name!r}")
            if len(candidates) > 1:
                raise ValueError(f"Bound constructor target {target_name!r} is ambiguous")
            target = candidates[0]
            target_arguments = list(target.arguments)
            if isinstance(target, SemanticMethod) and target.passed_object_position is not None:
                target_arguments.pop(target.passed_object_position)
            if constructor.arguments != target_arguments or constructor.return_type != target.return_type:
                raise ValueError(f"Bound constructor declaration is incompatible with class method {target_name!r}")
            constructor.native_name = target.native_name or target.name

    @staticmethod
    def _class_metadata(base_classes: list[str]) -> dict[str, object]:
        metadata: dict[str, object] = {}
        if "CStruct" in base_classes:
            metadata["c_kind"] = "struct"
        if "CUnion" in base_classes:
            metadata["c_kind"] = "union"
        if "CAnonymous" in base_classes:
            metadata["c_anonymous"] = True
        if "Opaque" in base_classes:
            metadata["representation"] = "opaque"
        return metadata

    @staticmethod
    def _origin(*, source_language: str | None = None, user_private: bool = False) -> SemanticOrigin:
        origin = SemanticOrigin(source_language=source_language)
        if user_private:
            origin.metadata[PYI_USER_PRIVATE_METADATA] = True
        return origin

    def function_def(
        self,
        node: ast.FunctionDef,
        *,
        visibility: str,
        projection: list[ProjectionMapping] | None = None,
        native_name: str | None = None,
        external: bool = False,
        hold_gil: bool = False,
        error_status_policy: dict[str, object] | None = None,
    ) -> SemanticFunction:
        semantic_args, return_type = self._callable_parts(node, projection=projection or [])
        metadata = {PYI_BIND_TARGET_METADATA: native_name} if native_name is not None else {}
        if hold_gil:
            metadata[RUNTIME_HOLD_GIL_METADATA] = True
        if error_status_policy is not None:
            metadata[RUNTIME_STATUS_ERROR_METADATA] = dict(error_status_policy)
        origin = self._origin(
            source_language="fortran" if external else None,
            user_private=visibility == "private",
        )
        if external:
            origin.source_kind = "function" if return_type is not None else "subroutine"
            origin.native_name = native_name or node.name
        return SemanticFunction(
            name=node.name,
            native_name=native_name or node.name,
            arguments=semantic_args,
            return_type=return_type,
            projection=projection or [],
            metadata=metadata,
            visibility=visibility,
            origin=origin,
        )

    def method_def(
        self,
        node: ast.FunctionDef,
        *,
        visibility: str,
        projection: list[ProjectionMapping] | None = None,
        is_static: bool = False,
        native_name: str | None = None,
        class_name: str,
        infer_passed_object: bool = True,
        hold_gil: bool = False,
        error_status_policy: dict[str, object] | None = None,
    ) -> SemanticMethod:
        semantic_args, return_type = self._callable_parts(
            node,
            projection=projection or [],
            drop_untyped_self=True,
        )
        metadata = {PYI_BIND_TARGET_METADATA: native_name} if native_name is not None else {}
        passed_object_name = None
        passed_object_position = None
        if infer_passed_object and not is_static and node.name != "__init__":
            pass_mappings = [mapping for mapping in projection or [] if mapping.value_kind == "pass"]
            if len(pass_mappings) > 1:
                raise ValueError("native_call may contain at most one Pass() entry")
            passed_object_position = pass_mappings[0].native_position if pass_mappings else 0
            if not isinstance(passed_object_position, int) or not 0 <= passed_object_position <= len(semantic_args):
                raise ValueError("native_call Pass() position is out of range")
            passed_object_name = "self"
            semantic_args.insert(
                passed_object_position,
                SemanticArgument(
                    passed_object_name,
                    SemanticType(
                        class_name,
                        dtype=class_name,
                        storage=SemanticStorageContract(kind="reference", mutable=True, pointer_depth=1),
                    ),
                    intent="inout",
                ),
            )
            self._restore_pass_projection(projection or [], passed_object_position)
        if hold_gil:
            metadata[RUNTIME_HOLD_GIL_METADATA] = True
        if error_status_policy is not None:
            metadata[RUNTIME_STATUS_ERROR_METADATA] = dict(error_status_policy)
        origin = self._origin(
            source_language=None,
            user_private=visibility == "private",
        )
        return SemanticMethod(
            name=node.name,
            native_name=native_name or node.name,
            arguments=semantic_args,
            return_type=return_type,
            projection=projection or [],
            metadata=metadata,
            visibility=visibility,
            origin=origin,
            is_static=is_static,
            passed_object_name=passed_object_name,
            passed_object_position=passed_object_position,
        )

    @staticmethod
    def _restore_pass_projection(projection: list[ProjectionMapping], passed_position: int) -> None:
        for mapping in projection:
            if mapping.value_kind == "pass":
                mapping.value_kind = None
                mapping.python_position = passed_position
                mapping.python_name = "self"
                mapping.native_name = mapping.native_name or "self"
                mapping.intent = "inout"
            elif mapping.python_position is not None and mapping.python_position >= passed_position:
                old_position = mapping.python_position
                mapping.python_position += 1
                _PyiAstParser._shift_pointer_argument_value(mapping, old_position, mapping.python_position)

    def ann_assign(
        self,
        node: ast.AnnAssign,
        *,
        default_intent: str,
        binding_cls: type[SemanticVariable] = SemanticVariable,
    ) -> SemanticVariable:
        name = self.annotation_target(node.target)
        visibility, semantic_type, original_name = self.visible_type(node.annotation)
        if original_name is not None:
            name = original_name
        intent = self._pop_intent_metadata(semantic_type, default_intent)
        semantic_type.ownership.mutable = intent.lower() != "in"
        if semantic_type.storage is not None:
            semantic_type.storage.mutable = intent.lower() != "in"
        self._validate_python_value_policy(semantic_type, intent=intent, owner=name)
        binding = binding_cls(
            name=name,
            semantic_type=semantic_type,
            visibility=visibility,
            default_value=self.assignment_default_value(node.value, semantic_type),
        )
        if visibility == "private":
            binding.origin.metadata[PYI_USER_PRIVATE_METADATA] = True
        binding.intent = intent
        binding.optional = self.default_marks_optional(node.value)
        return binding

    def decorators(self, nodes: list[ast.expr], *, context: str) -> _Decorators:
        parsed = _Decorators()
        for node in nodes:
            self._apply_decorator(parsed, node, context=context)
        if parsed.overload_target is not None and parsed.bind_target is not None:
            raise ValueError("bind cannot be combined with overload")
        return parsed

    def _apply_decorator(self, parsed: _Decorators, node: ast.expr, *, context: str) -> None:
        if self.matches_name(node, "private"):
            parsed.visibility = "private"
            return
        if self.matches_name(node, "staticmethod"):
            parsed.is_static = True
            return
        target = node.func if isinstance(node, ast.Call) else node
        handlers = {
            "overload": self._apply_overload_decorator,
            "bind": self._apply_bind_decorator,
            "external": self._apply_external_decorator,
            "hold_gil": self._apply_hold_gil_decorator,
            "native_call": self._apply_native_call_decorator,
            "native_type": self._apply_native_type_decorator,
            "raises": self._apply_raises_decorator,
        }
        handler = next((value for name, value in handlers.items() if self.matches_name(target, name)), None)
        if handler is None:
            raise ValueError(f"Unsupported {context} decorator: {ast.unparse(node)!r}")
        handler(parsed, node, context)

    def _apply_overload_decorator(self, parsed: _Decorators, node: ast.expr, context: str) -> None:
        if not isinstance(node, ast.Call):
            raise ValueError("overload expects one specific procedure name")
        if parsed.overload_target is not None:
            raise ValueError(f"Duplicate {context} overload decorator")
        if self.qualified_name(node.func) == ("typing", "overload"):
            raise ValueError('typing.overload is not supported; use x2py @overload("specific")')
        if len(node.args) != 1:
            raise ValueError("overload expects one specific procedure name")
        target = ast.literal_eval(node.args[0])
        if not isinstance(target, str) or not target:
            raise ValueError("overload expects a non-empty specific procedure name")
        if len(node.keywords) > 1 or any(keyword.arg != "generic" for keyword in node.keywords):
            raise ValueError("overload accepts only the optional generic keyword")
        if node.keywords:
            generic_name = ast.literal_eval(node.keywords[0].value)
            if not isinstance(generic_name, str) or not generic_name:
                raise ValueError("overload generic expects a non-empty Fortran generic name")
            parsed.overload_generic = generic_name
        parsed.overload_target = target

    @staticmethod
    def _required_string_decorator_argument(node: ast.expr, name: str) -> str:
        if not isinstance(node, ast.Call) or len(node.args) != 1 or node.keywords:
            raise ValueError(f"{name} expects one native symbol name")
        target = ast.literal_eval(node.args[0])
        if not isinstance(target, str) or not target:
            raise ValueError(f"{name} expects a non-empty native symbol name")
        return target

    def _apply_bind_decorator(self, parsed: _Decorators, node: ast.expr, context: str) -> None:
        if parsed.bind_target is not None:
            raise ValueError(f"Duplicate {context} bind decorator")
        parsed.bind_target = self._required_string_decorator_argument(node, "bind")

    @staticmethod
    def _apply_hold_gil_decorator(parsed: _Decorators, node: ast.expr, context: str) -> None:
        if isinstance(node, ast.Call):
            raise ValueError("hold_gil does not accept arguments")
        if parsed.hold_gil:
            raise ValueError(f"Duplicate {context} hold_gil decorator")
        parsed.hold_gil = True

    @staticmethod
    def _apply_external_decorator(parsed: _Decorators, node: ast.expr, context: str) -> None:
        if isinstance(node, ast.Call):
            raise ValueError("external does not accept arguments")
        if parsed.external:
            raise ValueError(f"Duplicate {context} external decorator")
        parsed.external = True

    @staticmethod
    def _apply_native_type_decorator(parsed: _Decorators, node: ast.expr, context: str) -> None:
        if parsed.native_type is not None:
            raise ValueError(f"Duplicate {context} native_type decorator")
        if not isinstance(node, ast.Call) or node.args:
            raise ValueError("native_type accepts keyword arguments only")
        allowed = {"attributes", "finalizers"}
        values: dict[str, object] = {}
        for keyword in node.keywords:
            if keyword.arg not in allowed:
                raise ValueError(f"native_type got unsupported keyword {keyword.arg!r}")
            if keyword.arg in values:
                raise ValueError(f"native_type repeats {keyword.arg!r}")
            value = ast.literal_eval(keyword.value)
            if not isinstance(value, tuple) or not all(isinstance(item, str) and item for item in value):
                raise ValueError(f"native_type {keyword.arg} must be a tuple of non-empty strings")
            values[keyword.arg] = value
        parsed.native_type = values

    def _apply_native_call_decorator(self, parsed: _Decorators, node: ast.expr, context: str) -> None:
        del context
        if not isinstance(node, ast.Call):
            raise ValueError("native_call expects a single list argument")
        parsed.has_native_call = True
        parsed.projection = self.native_call(node)

    def _apply_raises_decorator(self, parsed: _Decorators, node: ast.expr, context: str) -> None:
        if not isinstance(node, ast.Call):
            raise ValueError("raises expects keyword arguments")
        if parsed.error_status_policy is not None:
            raise ValueError(f"Duplicate {context} raises decorator")
        parsed.error_status_policy = self.error_status_policy(node)

    def native_call(self, node: ast.Call) -> list[ProjectionMapping]:
        if len(node.args) != 1 or node.keywords:
            raise ValueError("native_call expects a single list argument")
        entries = node.args[0]
        if not isinstance(entries, ast.List):
            raise ValueError("native_call expects a list of projection entries")
        return [
            self.native_projection_entry(entry, native_position) for native_position, entry in enumerate(entries.elts)
        ]

    @staticmethod
    def error_status_policy(node: ast.Call) -> dict[str, object]:
        if node.args:
            raise ValueError("raises accepts keyword arguments only")
        allowed = {"status", "message", "success"}
        values: dict[str, object] = {}
        for keyword in node.keywords:
            if keyword.arg is None:
                raise ValueError("raises does not accept ** expansion")
            if keyword.arg not in allowed:
                raise ValueError(f"raises got unsupported keyword {keyword.arg!r}")
            if keyword.arg in values:
                raise ValueError(f"raises repeats {keyword.arg!r}")
            values[keyword.arg] = ast.literal_eval(keyword.value)

        status = values.get("status")
        if not isinstance(status, str) or not status:
            raise ValueError("raises requires status=<non-empty output name>")

        message = values.get("message")
        if message is not None and (not isinstance(message, str) or not message):
            raise ValueError("raises message must be a non-empty output name")

        success = values.get("success", 0)
        if not isinstance(success, int) or isinstance(success, bool):
            raise ValueError("raises success must be an integer status value")

        policy = {"status": status, "success": success}
        if message is not None:
            policy["message"] = message
        return policy

    def _resolve_overloads(self) -> None:
        for pending in self._pending_overloads:
            target = self._resolve_overload_target(pending.owner, pending.target)
            candidate = self._validated_overload_candidate(
                pending.owner,
                pending.declaration,
                target,
                generic_name=pending.generic_name,
            )
            overload_sets = pending.owner.overload_sets
            overload_name = self._overload_set_name(pending.owner, pending.declaration.name)
            overload_set = next((item for item in overload_sets if item.name == overload_name), None)
            if overload_set is None:
                overload_set = ProcedureOverloadSet(overload_name)
                overload_sets.append(overload_set)
            if any(proc.metadata.get(OVERLOAD_TARGET_METADATA) == pending.target for proc in overload_set.procedures):
                raise ValueError(
                    f"Overload {pending.declaration.name!r} references specific procedure "
                    f"{pending.target!r} more than once"
                )
            overload_set.procedures.append(candidate)

    def _restore_type_bound_targets(self) -> None:
        """Mark module procedures referenced by type-bound method declarations."""

        by_name = {
            target: function
            for function in self.module.functions
            for target in {function.name, function.native_name}
            if target
        }
        for semantic_class in self._iter_classes(self.module.classes):
            for method in semantic_class.methods:
                if method.is_static or method.passed_object_position is None:
                    continue
                target = by_name.get(method.native_name or method.name)
                if target is None:
                    continue
                passed_position = method.passed_object_position
                if not 0 <= passed_position < len(target.arguments):
                    continue
                target.metadata["fortran_type_bound_target"] = True
                target.metadata["fortran_passed_object_name"] = target.arguments[passed_position].name
                target.metadata["fortran_passed_object_position"] = passed_position

    @classmethod
    def _iter_classes(cls, classes: list[SemanticClass]):
        for semantic_class in classes:
            yield semantic_class
            yield from cls._iter_classes(semantic_class.classes)

    @staticmethod
    def _overload_set_name(owner: SemanticModule | SemanticClass, declaration_name: str) -> str:
        if isinstance(owner, SemanticModule):
            return declaration_name
        return {
            "__radd__": "__add__",
            "__rsub__": "__sub__",
            "__rmul__": "__mul__",
            "__rtruediv__": "__truediv__",
            "__rpow__": "__pow__",
            "__rand__": "__and__",
            "__ror__": "__or__",
        }.get(declaration_name, declaration_name)

    def _resolve_overload_target(
        self,
        owner: SemanticModule | SemanticClass,
        target_name: str,
    ) -> SemanticFunction:
        candidates = [
            function for function in self.module.functions if target_name in {function.name, function.native_name}
        ]
        if isinstance(owner, SemanticClass) and not candidates:
            candidates = [method for method in owner.methods if target_name in {method.name, method.native_name}]
        if not candidates:
            raise ValueError(f"Overload references missing specific procedure {target_name!r}")
        if len(candidates) != 1:
            raise ValueError(f"Overload target {target_name!r} is ambiguous")
        return candidates[0]

    def _validated_overload_candidate(
        self,
        owner: SemanticModule | SemanticClass,
        declaration: SemanticFunction,
        target: SemanticFunction,
        *,
        generic_name: str | None,
    ) -> SemanticFunction:
        candidate = deepcopy(target)
        candidate.visibility = declaration.visibility
        candidate.metadata[OVERLOAD_TARGET_METADATA] = target.name
        for key in (RUNTIME_HOLD_GIL_METADATA, RUNTIME_STATUS_ERROR_METADATA):
            if key in declaration.metadata:
                candidate.metadata[key] = deepcopy(declaration.metadata[key])

        if isinstance(owner, SemanticModule):
            self._validate_overload_signature(declaration, candidate, list(candidate.arguments))
            candidate.metadata[FORTRAN_GENERIC_NAME_METADATA] = generic_name or declaration.name
            candidate.metadata[OVERLOAD_KIND_METADATA] = "generic"
            return candidate

        bound_position = self._class_overload_bound_position(owner, declaration, candidate)
        call_arguments = (
            list(candidate.arguments)
            if bound_position is None
            else [arg for index, arg in enumerate(candidate.arguments) if index != bound_position]
        )
        self._validate_overload_signature(declaration, candidate, call_arguments, bound_position=bound_position)
        kind, native_name = self._class_overload_identity(
            declaration.name,
            bound_position,
            generic_name=generic_name,
        )
        candidate.metadata[FORTRAN_GENERIC_NAME_METADATA] = native_name
        candidate.metadata[OVERLOAD_KIND_METADATA] = kind
        candidate.metadata[PYTHON_METHOD_NAME_METADATA] = declaration.name
        if bound_position is not None:
            candidate.metadata[PYTHON_BOUND_POSITION_METADATA] = bound_position
        if isinstance(declaration, SemanticMethod) and declaration.is_static:
            candidate.metadata[PYTHON_STATIC_METADATA] = True
        return candidate

    @staticmethod
    def _validate_overload_signature(
        declaration: SemanticFunction,
        target: SemanticFunction,
        call_arguments: list[SemanticArgument],
        *,
        bound_position: int | None = None,
    ) -> None:
        if declaration.arguments == call_arguments and (
            declaration.return_type == target.return_type
            or _PyiAstParser._matches_bound_projection_return(declaration, target, bound_position)
        ):
            return
        raise ValueError(
            f"Overload declaration {declaration.name!r} is incompatible with "
            f"specific procedure {target.native_name or target.name!r}"
        )

    @staticmethod
    def _matches_bound_projection_return(
        declaration: SemanticFunction,
        target: SemanticFunction,
        bound_position: int | None,
    ) -> bool:
        if bound_position is None or declaration.return_type is None:
            return False
        if not 0 <= bound_position < len(target.arguments):
            return False
        if not any(
            mapping.native_position == bound_position and mapping.result_position is not None
            for mapping in target.projection
        ):
            return False
        expected = deepcopy(target.arguments[bound_position].semantic_type)
        if expected.rank == 0 and expected.storage is not None and expected.storage.kind == "reference":
            expected.storage = None
        expected.ownership = deepcopy(declaration.return_type.ownership)
        return declaration.return_type == expected

    @staticmethod
    def _class_overload_bound_position(
        owner: SemanticClass,
        declaration: SemanticFunction,
        target: SemanticFunction,
    ) -> int | None:
        if isinstance(declaration, SemanticMethod) and declaration.is_static:
            return None
        remaining_names = [argument.name for argument in declaration.arguments]
        matching = [
            index
            for index, argument in enumerate(target.arguments)
            if argument.semantic_type.name.casefold() == owner.name.casefold()
            and [arg.name for pos, arg in enumerate(target.arguments) if pos != index] == remaining_names
        ]
        if len(matching) == 1:
            return matching[0]
        if not matching:
            raise ValueError(
                f"Overload declaration {declaration.name!r} cannot bind an argument of type {owner.name!r} "
                f"from specific procedure {target.native_name or target.name!r}"
            )
        raise ValueError(
            f"Overload declaration {declaration.name!r} has an ambiguous bound argument in "
            f"specific procedure {target.native_name or target.name!r}"
        )

    @staticmethod
    def _class_overload_identity(
        method_name: str,
        bound_position: int | None,
        *,
        generic_name: str | None,
    ) -> tuple[str, str]:
        direct_operators = {
            "__add__": "+",
            "__sub__": "-",
            "__mul__": "*",
            "__truediv__": "/",
            "__pow__": "**",
            "__and__": ".and.",
            "__or__": ".or.",
            "__invert__": ".not.",
            "__pos__": "+",
            "__neg__": "-",
            "__eq__": "==",
            "__ne__": "/=",
            "__lt__": "<",
            "__le__": "<=",
            "__gt__": ">",
            "__ge__": ">=",
        }
        reflected_operators = {
            "__radd__": "+",
            "__rsub__": "-",
            "__rmul__": "*",
            "__rtruediv__": "/",
            "__rpow__": "**",
            "__rand__": ".and.",
            "__ror__": ".or.",
        }
        if method_name in reflected_operators:
            if bound_position != 1:
                raise ValueError(f"{method_name} requires the wrapped object to be the second native operand")
            identity = ("operator", f"operator({reflected_operators[method_name]})")
            return _PyiAstParser._validated_generic_override(method_name, identity, generic_name)
        if method_name in direct_operators:
            token = direct_operators[method_name]
            if method_name in {"__lt__", "__le__", "__gt__", "__ge__"} and bound_position == 1:
                token = {"<": ">", "<=": ">=", ">": "<", ">=": "<="}[token]
            kind = (
                "comparison"
                if method_name in {"__eq__", "__ne__", "__lt__", "__le__", "__gt__", "__ge__"}
                else "operator"
            )
            identity = (kind, f"operator({token})")
            return _PyiAstParser._validated_generic_override(method_name, identity, generic_name)
        if method_name == "assign":
            identity = ("assignment", "assignment(=)")
            return _PyiAstParser._validated_generic_override(method_name, identity, generic_name)
        if method_name == "__init__":
            if generic_name is not None:
                raise ValueError("overload generic is not valid for constructor declarations")
            return "constructor", method_name
        reflected_named = method_name.startswith("r_operator_")
        if reflected_named or method_name.startswith("operator_"):
            prefix = "r_operator_" if reflected_named else "operator_"
            token = method_name.removeprefix(prefix)
            if not token or not token.isidentifier():
                raise ValueError(f"Invalid named operator method {method_name!r}")
            if reflected_named and bound_position != 1:
                raise ValueError(f"{method_name} requires the wrapped object to be the second native operand")
            identity = ("named_operator", f"operator(.{token}.)")
            return _PyiAstParser._validated_generic_override(method_name, identity, generic_name)
        if generic_name is not None:
            raise ValueError(f"overload generic is not valid for ordinary method {method_name!r}")
        return "generic", method_name

    @staticmethod
    def _validated_generic_override(
        method_name: str,
        identity: tuple[str, str],
        generic_name: str | None,
    ) -> tuple[str, str]:
        if generic_name is None:
            return identity
        compact = re.sub(r"\s+", "", generic_name).casefold()
        allowed_overrides = {
            "__eq__": {"operator(==)", "operator(.eq.)", "operator(.eqv.)"},
            "__ne__": {"operator(/=)", "operator(.ne.)", "operator(.neqv.)"},
        }
        if compact not in allowed_overrides.get(method_name, {identity[1].casefold()}):
            raise ValueError(f"overload generic {generic_name!r} is incompatible with method {method_name!r}")
        return identity[0], generic_name

    def native_projection_entry(self, node: ast.AST, native_position: int) -> ProjectionMapping:
        shape_mapping = self.native_shape_projection_entry(node, native_position)
        if shape_mapping is not None:
            return shape_mapping
        if not isinstance(node, ast.Call):
            raise ValueError("native_call expects projection entry calls")
        if node.keywords:
            raise ValueError(f"{self.required_name(node.func)} expects positional arguments only")

        if self._is_ref_call(node):
            return self.native_pointer_projection_entry(node, native_position)

        helper = self.required_name(node.func)
        if helper == "Arg":
            if len(node.args) != 1:
                raise ValueError("Arg expects one positional index")
            return ProjectionMapping(
                native_position=native_position,
                python_position=int(ast.literal_eval(node.args[0])),
            )
        if helper == "Return":
            if len(node.args) not in {1, 2}:
                raise ValueError("Return expects one positional index or a name and index")
            native_name = ""
            position_arg = node.args[0]
            if len(node.args) == 2:
                native_name = str(ast.literal_eval(node.args[0]))
                position_arg = node.args[1]
            return ProjectionMapping(
                native_name=native_name,
                native_position=native_position,
                result_position=int(ast.literal_eval(position_arg)),
                intent="out",
            )
        if helper == "Pass":
            if node.args:
                raise ValueError("Pass does not accept arguments")
            return ProjectionMapping(
                native_position=native_position,
                value_kind="pass",
            )
        if helper == "Const":
            if len(node.args) != 1:
                raise ValueError("Const expects one value")
            return ProjectionMapping(
                native_position=native_position,
                value_kind="const",
                value=ast.literal_eval(node.args[0]),
            )
        if helper == "Len":
            if len(node.args) != 1:
                raise ValueError("Len expects one value reference")
            return ProjectionMapping(
                native_position=native_position,
                value_kind="len",
                value=self.native_value_ref(node.args[0]),
            )
        if helper == "IsPresent":
            if len(node.args) != 1:
                raise ValueError("IsPresent expects one value reference")
            return ProjectionMapping(
                native_position=native_position,
                value_kind="is_present",
                value=self.native_value_ref(node.args[0]),
            )
        if helper == "Work":
            if len(node.args) != 1:
                raise ValueError("Work expects one workspace name")
            return ProjectionMapping(
                native_position=native_position,
                value_kind="work",
                value=str(ast.literal_eval(node.args[0])),
            )

        raise ValueError(f"Unsupported native_call projection entry: {helper}")

    def native_pointer_projection_entry(self, node: ast.Call, native_position: int) -> ProjectionMapping:
        if len(node.args) != 1:
            raise ValueError("Ref projection expects one Arg(...), Return(...), or Work(...) reference")
        if self._ref_depth(node.func) != 1:
            raise ValueError("native_call reference projection only supports Ref(...)")
        value = self.native_value_ref(node.args[0])
        mapping = ProjectionMapping(
            native_position=native_position,
            value_kind="ptr",
            value=value,
        )
        if value["kind"] == "arg":
            mapping.python_position = int(value["position"])
        elif value["kind"] == "return":
            mapping.result_position = int(value["position"])
            mapping.intent = "out"
        return mapping

    def native_shape_projection_entry(
        self,
        node: ast.AST,
        native_position: int,
    ) -> ProjectionMapping | None:
        if not isinstance(node, ast.Subscript) or not isinstance(node.value, ast.Attribute):
            return None
        attribute = node.value.attr
        if attribute != "shape":
            return None
        return ProjectionMapping(
            native_position=native_position,
            value_kind="shape",
            value={
                "value": self.native_value_ref(node.value.value),
                "dim": int(ast.literal_eval(node.slice)),
            },
        )

    def native_value_ref(self, node: ast.AST) -> dict[str, int | str]:
        if not isinstance(node, ast.Call):
            raise ValueError("Expected Arg(...), Return(...), or Work(...) value reference")
        if node.keywords or len(node.args) != 1:
            raise ValueError(f"{self.required_name(node.func)} value reference expects one positional argument")
        helper = self.required_name(node.func)
        if helper == "Arg":
            return {"kind": "arg", "position": int(ast.literal_eval(node.args[0]))}
        if helper == "Return":
            return {"kind": "return", "position": int(ast.literal_eval(node.args[0]))}
        if helper == "Work":
            return {"kind": "work", "name": str(ast.literal_eval(node.args[0]))}
        raise ValueError("Expected Arg(...), Return(...), or Work(...) value reference")

    def visible_type(self, node: ast.expr) -> tuple[str, SemanticType, str | None]:
        if self.is_subscript_of(node, "private"):
            semantic_type, original_name = self.semantic_type_annotation(self.subscript_slice(node))
            return "private", semantic_type, original_name
        semantic_type, original_name = self.semantic_type_annotation(node)
        return "public", semantic_type, original_name

    def semantic_type_annotation(self, node: ast.expr) -> tuple[SemanticType, str | None]:
        optional_item = self._optional_union_item(node)
        if optional_item is not None:
            semantic_type = self.semantic_type(optional_item)
            storage = semantic_type.storage
            if storage is not None and storage.array is not None and storage.array.allocatable:
                return semantic_type, None
        if not self.is_subscript_of(node, "Annotated"):
            return self.semantic_type(node), None

        items = self.subscript_items(node)
        if not items:
            raise ValueError(f"Annotated type is empty: {ast.unparse(node)!r}")

        original_name = None
        semantic_type = self.semantic_type(items[0])
        for item in items[1:]:
            parsed_name = self.name_metadata(item)
            if parsed_name is not None:
                original_name = parsed_name
                continue
            self.apply_annotation_metadata(semantic_type, item)
        return semantic_type, original_name

    def semantic_type(self, node: ast.expr) -> SemanticType:
        if self.is_subscript_of(node, "Annotated"):
            semantic_type, _ = self.semantic_type_annotation(node)
            return semantic_type
        if self.is_subscript_of(node, "Final"):
            return self._final_type(node)
        if self.matches_name(node, "Callable") or self.is_subscript_of(node, "Callable"):
            return self.callable_type(node)
        if isinstance(node, ast.Call) and self.matches_name(node.func, "Const"):
            return self._const_type(node)
        if isinstance(node, ast.Call) and self._is_ref_call(node):
            return self._pointer_type(node)

        if isinstance(node, ast.Subscript) and self.matches_name(node.value, "String"):
            return self._character_type(node)

        name = self.type_name(node)
        if name == "Unknown":
            raise ValueError("Unknown semantic type is not allowed in .pyi annotations")
        if not isinstance(node, ast.Subscript):
            return SemanticType(name=name, dtype=name)

        if not self._is_array_subscript(node):
            raise ValueError(
                "Non-dimensional type subscriptions are not supported; "
                "use Final[...] for constants and Annotated[...] for constraints or array metadata"
            )
        return self.array_type(node)

    def _final_type(self, node: ast.Subscript) -> SemanticType:
        items = self.subscript_items(node)
        if len(items) != 1:
            raise ValueError(f"Final expects exactly one type: {ast.unparse(node)!r}")
        semantic_type = self.semantic_type(items[0])
        if not any(constraint.name == "Constant" for constraint in semantic_type.constraints):
            semantic_type.constraints.append(SemanticConstraint("Constant"))
        return semantic_type

    def _const_type(self, node: ast.Call) -> SemanticType:
        if len(node.args) != 1 or node.keywords:
            raise ValueError(f"Const type expects one argument: {ast.unparse(node)!r}")
        semantic_type = self.semantic_type(node.args[0])
        self._mark_storage_read_only(semantic_type)
        return semantic_type

    def _pointer_type(self, node: ast.Call) -> SemanticType:
        if len(node.args) != 1 or node.keywords:
            raise ValueError(f"Ref type expects one argument: {ast.unparse(node)!r}")
        pointer_depth = self._ref_depth(node.func)
        pointee = self.semantic_type(node.args[0])
        read_only = pointee.storage.read_only if pointee.storage is not None else False
        pointee.storage = SemanticStorageContract(
            kind="reference" if pointer_depth == 1 else "pointer",
            read_only=read_only,
            mutable=not read_only,
            pointer_depth=pointer_depth,
        )
        pointee.ownership.mutable = not read_only
        return pointee

    def array_type(self, node: ast.Subscript) -> SemanticType:
        if isinstance(node.value, ast.Subscript):
            if self.matches_name(node.value.value, "String"):
                semantic_type = self._character_type(node.value)
                return self._array_type_from_dimensions(
                    semantic_type.name,
                    self.array_dimension_texts(node),
                    metadata=semantic_type.metadata,
                )
            semantic_type = self.array_type(node.value)
            selector = ", ".join(self.dimension_text(item) for item in self.subscript_items(node))
            semantic_type.metadata["rank_selector"] = selector
            if semantic_type.storage and semantic_type.storage.array:
                semantic_type.storage.array.metadata["rank_selector"] = selector
            return semantic_type

        return self._array_type_from_dimensions(
            self.type_name(node),
            self.array_dimension_texts(node),
        )

    def array_dimension_texts(self, node: ast.Subscript) -> list[str]:
        items = self.subscript_items(node)
        raw_items = self._source_dimension_items(node)
        if raw_items is None or len(raw_items) != len(items):
            return [self.dimension_text(item) for item in items]
        dimensions = []
        for raw_item, item in zip(raw_items, items, strict=True):
            if isinstance(item, ast.Slice) and self._is_empty_step_slice(raw_item):
                dimensions.append(self._strided_dimension_text(raw_item))
            else:
                dimensions.append(self.dimension_text(item))
        return dimensions

    def _source_dimension_items(self, node: ast.Subscript) -> list[str] | None:
        if not self.source:
            return None
        source = ast.get_source_segment(self.source, node.slice)
        if source is None:
            return None
        return self._split_top_level_dimensions(source)

    @staticmethod
    def _split_top_level_dimensions(source: str) -> list[str]:
        items = []
        start = 0
        depth = 0
        quote: str | None = None
        escape = False
        for index, char in enumerate(source):
            if quote is not None:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == quote:
                    quote = None
                continue
            if char in {"'", '"'}:
                quote = char
                continue
            if char in "([{":
                depth += 1
                continue
            if char in ")]}":
                depth = max(depth - 1, 0)
                continue
            if char == "," and depth == 0:
                items.append(source[start:index].strip())
                start = index + 1
        items.append(source[start:].strip())
        return items

    @staticmethod
    def _is_empty_step_slice(text: str) -> bool:
        parts = text.split(":")
        return len(parts) == 3 and parts[2].strip() == ""

    @staticmethod
    def _strided_dimension_text(text: str) -> str:
        lower, upper, _step = text.split(":", 2)
        return f"{lower.strip()}:{upper.strip()}:Strided"

    @staticmethod
    def _array_type_from_dimensions(
        name: str,
        dims: list[str],
        *,
        metadata: dict[str, object] | None = None,
    ) -> SemanticType:
        dims, category, source_shape, lower_bounds, upper_bounds = _PyiAstParser._flat_array_dimensions(dims)
        if dims == ["..."]:
            category = "assumed_rank"
            source_shape = [".."]

        rank = 1 if category == "assumed_rank" else len(dims)
        array = SemanticArrayContract(
            rank=rank,
            shape=list(dims),
            order=_PyiAstParser._array_order_for_dimensions(category, rank, source_shape),
            axes=["strided" if "Strided" in dim else "dense" for dim in dims],
            contiguous=not any("Strided" in dim for dim in dims),
            category=category,
            source_shape=source_shape,
            lower_bounds=lower_bounds,
            upper_bounds=upper_bounds,
        )
        storage = SemanticStorageContract(kind="array", array=array)
        return SemanticType(
            name=name,
            rank=rank or 0,
            dtype=name,
            shape=list(dims) if rank is not None else [],
            constraints=[],
            metadata=dict(metadata or {}),
            storage=storage,
        )

    @staticmethod
    def _flat_array_dimensions(
        dims: list[str],
    ) -> tuple[list[str], str | None, list[str], list[str | None], list[str | None]]:
        if "Flat" not in dims:
            source_shape = [] if any(dim in {":", "..."} or "Strided" in dim for dim in dims) else list(dims)
            lower_bounds, upper_bounds = _PyiAstParser._bounds_from_source_shape(source_shape)
            return dims, None, source_shape, lower_bounds, upper_bounds
        if dims.count("Flat") != 1 or "..." in dims or dims.index("Flat") not in {0, len(dims) - 1}:
            raise ValueError("Flat must appear exactly once at the first or final concrete array dimension")
        source_shape = ["*" if dim == "Flat" else dim for dim in dims]
        lower_bounds, upper_bounds = _PyiAstParser._bounds_from_source_shape(source_shape)
        return [":" if dim == "Flat" else dim for dim in dims], "assumed_size", source_shape, lower_bounds, upper_bounds

    @staticmethod
    def _array_order_for_dimensions(
        category: str | None,
        rank: int | None,
        source_shape: list[str],
    ) -> str | None:
        if rank is None or rank <= 1:
            return None
        if category == "assumed_size":
            return _PyiAstParser._flat_array_order(source_shape, rank)
        return "ORDER_C"

    @staticmethod
    def _flat_array_order(source_shape: list[str], rank: int | None) -> str | None:
        if rank is None or rank <= 1 or "*" not in source_shape:
            return None
        return "ORDER_C" if source_shape.index("*") == 0 else "ORDER_F"

    def _character_type(self, node: ast.Subscript) -> SemanticType:
        items = self.subscript_items(node)
        if (
            len(items) != 1
            or isinstance(items[0], ast.Slice)
            or (isinstance(items[0], ast.Constant) and items[0].value is Ellipsis)
        ):
            raise ValueError("Fixed character types use String[length]; use String for non-fixed length")
        length = self.dimension_text(items[0])
        return SemanticType(
            name="String",
            dtype="String",
            metadata={"fortran_character_length": length},
        )

    def apply_annotation_metadata(self, semantic_type: SemanticType, node: ast.expr) -> None:
        if isinstance(node, ast.Name):
            if not self._apply_metadata_name(semantic_type, node.id):
                self._append_constraint_metadata(semantic_type, node.id, [])
            return
        if isinstance(node, ast.Call):
            self._apply_annotation_metadata_call(semantic_type, node)
            return
        raise ValueError(f"Unsupported Annotated metadata: {ast.unparse(node)!r}")

    def _apply_annotation_metadata_call(self, semantic_type: SemanticType, node: ast.Call) -> None:
        helper = self.required_name(node.func)
        if helper == "Intent":
            self._apply_scalar_annotation_metadata(semantic_type, node, helper)
            return
        if helper in {"FortranType", "FortranCallback"}:
            raise ValueError(f"{helper} metadata is no longer part of the semantic .pyi contract")
        if helper == "PointerAssociation":
            self._apply_pointer_association_metadata(semantic_type, node)
            return
        if helper == "PointerPolicy":
            self._apply_pointer_policy_metadata(semantic_type, node)
            return
        if helper in {"Ownership", "Transfer", "Destruction"}:
            self._apply_ownership_annotation_metadata(semantic_type, node, helper)
            return
        if helper == "ArrayCategory":
            self._require_array_storage(semantic_type).category = str(ast.literal_eval(node.args[0]))
            return
        if helper == "SourceDims":
            values = [str(ast.literal_eval(arg)) for arg in node.args]
            array = self._require_array_storage(semantic_type)
            array.source_shape = values
            array.lower_bounds, array.upper_bounds = self._bounds_from_source_shape(values)
            return
        if helper == "SourceShape":
            raise ValueError("SourceShape metadata is not supported; use SourceDims")
        if helper in {"LowerBounds", "UpperBounds"}:
            bounds = [
                None if isinstance(arg, ast.Constant) and arg.value is None else str(ast.literal_eval(arg))
                for arg in node.args
            ]
            array = self._require_array_storage(semantic_type)
            if helper == "LowerBounds":
                array.lower_bounds = bounds
            else:
                array.upper_bounds = bounds
            return
        if node.keywords:
            raise ValueError(f"Constraint metadata expects positional arguments only: {ast.unparse(node)!r}")
        self._append_constraint_metadata(
            semantic_type,
            helper,
            [ast.literal_eval(arg) for arg in node.args],
        )

    @staticmethod
    def _require_single_metadata_argument(node: ast.Call, helper: str):
        if len(node.args) != 1 or node.keywords:
            raise ValueError(f"{helper} metadata expects one argument: {ast.unparse(node)!r}")
        return ast.literal_eval(node.args[0])

    def _apply_scalar_annotation_metadata(self, semantic_type: SemanticType, node: ast.Call, helper: str) -> None:
        semantic_type.metadata["_pyi_intent"] = str(self._require_single_metadata_argument(node, helper))

    def _apply_pointer_association_metadata(self, semantic_type: SemanticType, node: ast.Call) -> None:
        value = self._require_single_metadata_argument(node, "PointerAssociation")
        semantic_type.metadata["fortran_pointer_association"] = str(value)
        semantic_type.metadata["fortran_pointer"] = True

    @staticmethod
    def _apply_pointer_policy_metadata(semantic_type: SemanticType, node: ast.Call) -> None:
        if node.args:
            raise ValueError(f"PointerPolicy metadata accepts keyword arguments only: {ast.unparse(node)!r}")
        values = {}
        for keyword in node.keywords:
            if keyword.arg is None:
                raise ValueError("PointerPolicy metadata does not accept ** expansion")
            if keyword.arg in values:
                raise ValueError(f"PointerPolicy metadata repeats {keyword.arg!r}")
            values[keyword.arg] = ast.literal_eval(keyword.value)
        set_pointer_policy_metadata(semantic_type.metadata, **values)

    def _apply_ownership_annotation_metadata(self, semantic_type: SemanticType, node: ast.Call, helper: str) -> None:
        value = str(self._require_single_metadata_argument(node, helper))
        set_ownership_metadata(
            semantic_type.metadata,
            owner=value if helper == "Ownership" else None,
            transfer=value if helper == "Transfer" else None,
            destruction=value if helper == "Destruction" else None,
        )

    def _apply_metadata_name(self, semantic_type: SemanticType, name: str) -> bool:
        if name in {"ORDER_C", "ORDER_F", "ORDER_ANY"}:
            array = self._require_array_storage(semantic_type)
            expected_order = self._flat_array_order(array.source_shape, array.rank)
            if expected_order is not None and name != expected_order:
                raise ValueError(f"{name} conflicts with {expected_order} implied by Flat placement")
            array.order = name
            return True
        if name == "Allocatable":
            array = self._require_array_storage(semantic_type)
            array.allocatable = True
            return True
        if name == "Pointer":
            array = self._require_array_storage(semantic_type)
            array.pointer = True
            return True
        if name == "Contiguous":
            self._require_array_storage(semantic_type).contiguous = True
            return True
        if name == "Immutable":
            semantic_type.metadata[PYTHON_VALUE_MUTABILITY_METADATA] = PYTHON_VALUE_IMMUTABLE
            return True
        if name == "FortranAllocatable":
            semantic_type.metadata["fortran_allocatable"] = True
            return True
        if name == "FortranTarget":
            semantic_type.metadata["fortran_target"] = True
            return True
        if name == "AssumedType":
            semantic_type.metadata["fortran_assumed_type"] = True
            return True
        if name == "Polymorphic":
            semantic_type.metadata["fortran_polymorphic"] = True
            return True
        return False

    @staticmethod
    def _append_constraint_metadata(
        semantic_type: SemanticType,
        name: str,
        arguments: list[object],
    ) -> None:
        if name == "Constant":
            raise ValueError("Constant metadata is not supported; use Final[...]")
        if name == "Shape":
            raise ValueError("Shape metadata is not supported; put dimensions inside T[...]")
        semantic_type.constraints.append(SemanticConstraint(name=name, arguments=arguments))

    @staticmethod
    def _validate_python_value_policy(semantic_type: SemanticType, *, intent: str, owner: str) -> None:
        if semantic_type.metadata.get(PYTHON_VALUE_MUTABILITY_METADATA) != PYTHON_VALUE_IMMUTABLE:
            return
        if intent.lower() not in _WRITABLE_INTENTS:
            return
        policy = semantic_type.metadata.get(OWNERSHIP_POLICY_METADATA)
        transfer = policy.get("transfer") if isinstance(policy, dict) else None
        if transfer != "borrowed_view":
            return
        raise ValueError(
            f"Invalid .pyi contract for {owner}: Immutable values cannot request "
            'Transfer("borrowed_view") for writable native intent. Use a projected '
            "replacement return or remove Immutable."
        )

    @staticmethod
    def _require_array_storage(semantic_type: SemanticType) -> SemanticArrayContract:
        if semantic_type.storage is None:
            semantic_type.storage = SemanticStorageContract(kind="array")
        if semantic_type.storage.array is None:
            semantic_type.storage.array = SemanticArrayContract(
                rank=semantic_type.rank,
                shape=list(semantic_type.shape),
            )
        return semantic_type.storage.array

    @staticmethod
    def _bounds_from_source_shape(shape: list[str]) -> tuple[list[str | None], list[str | None]]:
        lower_bounds: list[str | None] = []
        upper_bounds: list[str | None] = []
        for dim in shape:
            token = str(dim).strip()
            if ":" in token:
                lower, upper = token.split(":", 1)
                lower_text = lower.strip() or None
                lower_bounds.append(None if lower_text == "1" else lower_text)
                upper_bounds.append(upper.strip() or None)
            elif token == "*":
                lower_bounds.append(None)
                upper_bounds.append("*")
            else:
                lower_bounds.append(None)
                upper_bounds.append(None)
        return lower_bounds, upper_bounds

    @staticmethod
    def _mark_storage_read_only(semantic_type: SemanticType) -> None:
        if semantic_type.storage is None:
            semantic_type.storage = SemanticStorageContract(kind="value")
        semantic_type.storage.read_only = True
        semantic_type.storage.mutable = False
        semantic_type.ownership.mutable = False

    @staticmethod
    def _inferred_argument_intent(semantic_type: SemanticType) -> str:
        storage = semantic_type.storage
        if storage is None:
            return "in"
        if storage.kind in {"reference", "array", "pointer", "callback"} and not storage.read_only:
            return "inout"
        return "in"

    @staticmethod
    def _pop_intent_metadata(semantic_type: SemanticType, default: str) -> str:
        value = semantic_type.metadata.pop("_pyi_intent", None)
        return str(value).lower() if value is not None else default

    @staticmethod
    def _is_ref_call(node: ast.Call) -> bool:
        return _PyiAstParser.matches_name(node.func, "Ref") or (
            isinstance(node.func, ast.Subscript) and _PyiAstParser.matches_name(node.func.value, "Ref")
        )

    @staticmethod
    def _ref_depth(node: ast.AST) -> int:
        if isinstance(node, ast.Subscript):
            depth = int(ast.literal_eval(node.slice))
            if depth <= 1:
                raise ValueError("Ref[1](...) is invalid; use Ref(...)")
            return depth
        return 1

    def _is_array_subscript(self, node: ast.Subscript) -> bool:
        if isinstance(node.value, ast.Subscript):
            return self._is_array_subscript(node.value)
        items = self.subscript_items(node)
        if not items:
            return False
        if any(isinstance(item, ast.Slice | ast.Constant) for item in items):
            return True
        if any(
            isinstance(item, ast.Name) and item.id not in self._non_dimension_subscription_names() for item in items
        ):
            return True
        if any(
            isinstance(item, ast.Call) and self.required_name(item.func) in self._non_dimension_subscription_names()
            for item in items
        ):
            return False
        if any(isinstance(item, ast.Call) for item in items):
            return True
        return any(isinstance(item, ast.BinOp | ast.UnaryOp) for item in items)

    @staticmethod
    def _non_dimension_subscription_names() -> set[str]:
        return {
            "Allocatable",
            "Constant",
            "Contiguous",
            "FortranTarget",
            "Immutable",
            "Ownership",
            "Optional",
            "ORDER_ANY",
            "ORDER_C",
            "ORDER_F",
            "Pointer",
            "PointerAssociation",
            "PointerPolicy",
            "Shape",
            "Transfer",
            "Destruction",
        }

    def dimension_text(self, node: ast.expr) -> str:
        if isinstance(node, ast.Constant) and node.value is Ellipsis:
            return "..."
        if isinstance(node, ast.Slice):
            return self.slice_text(node)
        if isinstance(node, ast.Constant):
            return str(node.value)
        if isinstance(node, ast.Attribute | ast.Subscript):
            raise ValueError(f"Unsupported array dimension expression: {ast.unparse(node)!r}")
        return ast.unparse(node)

    def slice_text(self, node: ast.Slice) -> str:
        lower = "" if node.lower is None else ast.unparse(node.lower)
        upper = "" if node.upper is None else ast.unparse(node.upper)
        step = "" if node.step is None else ast.unparse(node.step)
        if step:
            return f"{lower}:{upper}:{step}"
        return f"{lower}:{upper}"

    def callable_type(self, node: ast.expr) -> SemanticType:
        if not isinstance(node, ast.Subscript):
            return SemanticType(name="Callable", dtype="Callable")

        items = self.subscript_items(node)
        if len(items) != 2:
            raise ValueError(f"Callable expects argument types and a return type: {ast.unparse(node)!r}")

        raw_args, raw_return = items
        if isinstance(raw_args, ast.Constant) and raw_args.value is Ellipsis:
            return SemanticType(
                name="Callable",
                dtype="Callable",
                metadata=self._callback_metadata(None, self.semantic_type(raw_return)),
                storage=self._callback_storage(),
            )
        if not isinstance(raw_args, ast.List):
            raise ValueError(f"Callable arguments must be a list: {ast.unparse(node)!r}")

        argument_types = [self.semantic_type(item) for item in raw_args.elts]
        return_type = self.semantic_type(raw_return)
        metadata = self._callback_metadata(argument_types, return_type)
        metadata["callback_arguments"] = self._callback_arguments(argument_types, return_type)
        return SemanticType(
            name="Callable",
            dtype="Callable",
            metadata=metadata,
            storage=self._callback_storage(),
        )

    @classmethod
    def _callback_arguments(
        cls,
        argument_types: list[SemanticType],
        return_type: SemanticType,
    ) -> list[SemanticArgument]:
        shape_names = cls._callback_shape_names([*argument_types, return_type])
        used_names: set[str] = set()
        arguments = []
        for index, semantic_type in enumerate(argument_types):
            name = f"arg_{index}"
            if cls._is_dimension_scalar_callback_type(semantic_type):
                inferred_name = next((item for item in shape_names if item not in used_names), None)
                if inferred_name is not None:
                    name = inferred_name
                    used_names.add(inferred_name)
            arguments.append(SemanticArgument(name, semantic_type))
        return arguments

    @classmethod
    def _callback_shape_names(cls, semantic_types: list[SemanticType]) -> list[str]:
        names = []
        for semantic_type in semantic_types:
            for dimension in cls._semantic_shape_dimensions(semantic_type):
                for name in re.findall(r"\b[A-Za-z_]\w*\b", str(dimension)):
                    if name not in cls._non_dimension_subscription_names() and name not in names:
                        names.append(name)
        return names

    @staticmethod
    def _semantic_shape_dimensions(semantic_type: SemanticType) -> list[str]:
        if semantic_type.shape:
            return list(semantic_type.shape)
        storage = semantic_type.storage
        if storage is not None and storage.array is not None:
            return list(storage.array.shape)
        return []

    @staticmethod
    def _is_dimension_scalar_callback_type(semantic_type: SemanticType) -> bool:
        return semantic_type.rank == 0 and str(semantic_type.name).startswith("Int")

    @staticmethod
    def _callback_metadata(arguments: list[SemanticType] | None, return_type: SemanticType) -> dict[str, object]:
        return {
            "arguments": arguments,
            "return": return_type,
            "fortran_callback_kind": "subroutine" if return_type.name == "None" else "function",
            "callback_lifetime": "call",
            "callback_thread": "entering_thread",
            "callback_exception": "print_traceback_and_abort",
        }

    @staticmethod
    def _callback_storage() -> SemanticStorageContract:
        return SemanticStorageContract(
            kind="callback",
            ownership="borrowed",
            calling_convention="fortran_dummy_procedure",
        )

    def return_projection(
        self,
        node: ast.expr,
        *,
        optional_return_positions: set[int] | None = None,
    ) -> tuple[SemanticType | None, list[SemanticArgument]]:
        if isinstance(node, ast.Constant) and node.value is None:
            return None, []

        return_type: SemanticType | None = None
        returned_args: list[SemanticArgument] = []
        plain_return_index = 0
        optional_positions = optional_return_positions or set()

        for item_index, item in enumerate(self.return_items(node)):
            returned = self.returned_argument(item)
            if returned is not None:
                returned.metadata["return_position"] = item_index
                returned_args.append(returned)
                continue

            semantic_type, optional = self._return_item_type(
                item,
                unwrap_optional=item_index in optional_positions,
            )
            if item_index == 0:
                if optional:
                    semantic_type.metadata[_PYI_OPTIONAL_RETURN_METADATA] = True
                return_type = semantic_type
            else:
                returned_args.append(
                    SemanticArgument(
                        name=f"__return_{plain_return_index}",
                        semantic_type=semantic_type,
                        intent="out",
                        optional=optional,
                        metadata={"return_position": item_index},
                    )
                )
            plain_return_index += 1

        return return_type, returned_args

    def _return_item_type(self, node: ast.expr, *, unwrap_optional: bool) -> tuple[SemanticType, bool]:
        if not unwrap_optional:
            return self.semantic_type(node), False
        optional_node = self._optional_union_item(node)
        if optional_node is None:
            return self.semantic_type(node), False
        return self.semantic_type(optional_node), True

    @staticmethod
    def _optional_union_item(node: ast.expr) -> ast.expr | None:
        if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.BitOr):
            return None
        left_none = isinstance(node.left, ast.Constant) and node.left.value is None
        right_none = isinstance(node.right, ast.Constant) and node.right.value is None
        if left_none == right_none:
            return None
        return node.right if left_none else node.left

    def returned_argument(self, node: ast.expr) -> SemanticArgument | None:
        if not self.is_subscript_of(node, "Returns"):
            return None
        items = self.subscript_items(node)
        if len(items) not in {2, 3}:
            raise ValueError(f"Returns expects a name and type: {ast.unparse(node)!r}")

        semantic_type = self.semantic_type(items[1])
        semantic_type.ownership.mutable = True
        return SemanticArgument(
            name=str(ast.literal_eval(items[0])),
            semantic_type=semantic_type,
            intent="out",
            optional=len(items) == 3 and isinstance(items[2], ast.Name) and items[2].id == "Optional",
        )

    @staticmethod
    def name_metadata(node: ast.expr) -> str | None:
        if isinstance(node, ast.Call) and _PyiAstParser.matches_name(node.func, "Name"):
            if len(node.args) != 1:
                raise ValueError(f"Name metadata expects one argument: {ast.unparse(node)!r}")
            return str(ast.literal_eval(node.args[0]))
        return None

    @staticmethod
    def annotation_target(node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and node.value.id == "var":
            return str(ast.literal_eval(node.slice))
        raise ValueError(f"Unsupported annotation target: {ast.unparse(node)!r}")

    @staticmethod
    def default_marks_optional(node: ast.expr | None) -> bool:
        return isinstance(node, ast.Constant) and node.value in {Ellipsis, None}

    @staticmethod
    def literal_default_value(node: ast.expr | None) -> str | None:
        if node is None or _PyiAstParser.default_marks_optional(node):
            return None
        try:
            ast.literal_eval(node)
        except (ValueError, SyntaxError):
            raise ValueError(f"Mutable defaults must be literal values: {ast.unparse(node)!r}") from None
        return ast.unparse(node)

    @staticmethod
    def assignment_default_value(node: ast.expr | None, semantic_type: SemanticType) -> str | None:
        if node is None or _PyiAstParser.default_marks_optional(node):
            return None
        if any(constraint.name == "Constant" for constraint in semantic_type.constraints):
            return ast.unparse(node)
        return _PyiAstParser.literal_default_value(node)

    @staticmethod
    def qualified_name(node: ast.AST) -> tuple[str, ...] | None:
        if isinstance(node, ast.Name):
            return (node.id,)
        if isinstance(node, ast.Attribute):
            parent = _PyiAstParser.qualified_name(node.value)
            if parent is None:
                return None
            return (*parent, node.attr)
        return None

    @staticmethod
    def matches_name(node: ast.AST, name: str) -> bool:
        qualified = _PyiAstParser.qualified_name(node)
        return qualified is not None and qualified[-1] == name

    @staticmethod
    def required_name(node: ast.AST) -> str:
        qualified = _PyiAstParser.qualified_name(node)
        if qualified is None:
            raise ValueError(f"Expected named helper: {ast.unparse(node)!r}")
        return qualified[-1]

    @staticmethod
    def is_subscript_of(node: ast.AST, name: str) -> bool:
        return isinstance(node, ast.Subscript) and _PyiAstParser.matches_name(node.value, name)

    @staticmethod
    def subscript_slice(node: ast.AST) -> ast.expr:
        if not isinstance(node, ast.Subscript):
            raise ValueError(f"Unsupported type annotation: {ast.unparse(node)!r}")
        return node.slice

    def subscript_items(self, node: ast.AST) -> list[ast.expr]:
        value = self.subscript_slice(node)
        if isinstance(value, ast.Tuple):
            return list(value.elts)
        return [value]

    @staticmethod
    def type_name(node: ast.AST) -> str:
        if isinstance(node, ast.Subscript):
            return ast.unparse(node.value)
        return ast.unparse(node)

    def _callable_parts(
        self,
        node: ast.FunctionDef,
        *,
        projection: list[ProjectionMapping],
        drop_untyped_self: bool = False,
    ) -> tuple[list[SemanticArgument], SemanticType | None]:
        self._validate_stub_callable(node)
        if node.returns is None:
            if getattr(node, "end_lineno", node.lineno) != node.lineno:
                raise ValueError(f"Unterminated callable starting at line {node.lineno}")
            raise ValueError(f"Unsupported function header: {_node_text(node)!r}")
        if node.args.vararg or node.args.kwarg or node.args.kwonlyargs or node.args.posonlyargs:
            raise ValueError(f"Unsupported function header: {_node_text(node)!r}")

        args = list(zip(node.args.args, self._argument_defaults(node), strict=False))
        if drop_untyped_self and args and args[0][0].arg == "self":
            args = args[1:]

        semantic_args = [self._callable_argument(arg, default) for arg, default in args]
        visible_args = list(semantic_args)
        optional_return_positions = {
            mapping.result_position
            for mapping in projection
            if mapping.result_position is not None and mapping.python_position is None
        }
        return_type, returned_args = self.return_projection(
            node.returns,
            optional_return_positions=optional_return_positions,
        )
        return_type, returned_args = self._apply_native_call_returns(return_type, returned_args, projection)
        return_positions = self._return_positions_by_name(returned_args)
        self._apply_projected_returns(semantic_args, returned_args)
        self._apply_native_call_argument_names(visible_args, return_positions, projection)
        return semantic_args, return_type

    def _callable_argument(self, arg: ast.arg, default: ast.expr | None) -> SemanticArgument:
        if arg.annotation is None:
            raise ValueError(f"Expected typed argument: {arg.arg!r}")
        visibility, semantic_type, original_name = self.visible_type(arg.annotation)
        intent = self._pop_intent_metadata(semantic_type, self._inferred_argument_intent(semantic_type))
        semantic_type.ownership.mutable = intent.lower() != "in"
        if semantic_type.storage is not None:
            semantic_type.storage.mutable = intent.lower() != "in"
        self._validate_python_value_policy(semantic_type, intent=intent, owner=arg.arg)
        return SemanticArgument(
            name=original_name or arg.arg,
            semantic_type=semantic_type,
            intent=intent,
            optional=self.default_marks_optional(default),
            visibility=visibility,
            origin=self._origin(user_private=visibility == "private"),
        )

    @staticmethod
    def _argument_defaults(node: ast.FunctionDef) -> list[ast.expr | None]:
        defaults: list[ast.expr | None] = [None] * (len(node.args.args) - len(node.args.defaults))
        defaults.extend(node.args.defaults)
        return defaults

    @staticmethod
    def _validate_stub_callable(node: ast.FunctionDef) -> None:
        if len(node.body) != 1:
            raise ValueError(f"Unsupported function header: {_node_text(node)!r}")
        body = node.body[0]
        if not (isinstance(body, ast.Expr) and isinstance(body.value, ast.Constant) and body.value.value is Ellipsis):
            raise ValueError(f"Unsupported function header: {_node_text(node)!r}")

    @staticmethod
    def _apply_projected_returns(semantic_args: list[SemanticArgument], returned_args: list[SemanticArgument]) -> None:
        by_name = {arg.name: arg for arg in semantic_args}
        for returned in returned_args:
            existing = by_name.get(returned.name)
            if existing is None:
                returned.intent = "out"
                returned.semantic_type.ownership.mutable = True
                returned.metadata[PYI_PROJECTED_OUTPUT_METADATA] = True
                returned.metadata.pop("return_position", None)
                native_position = returned.metadata.pop("native_position", None)
                if isinstance(native_position, int) and 0 <= native_position <= len(semantic_args):
                    semantic_args.insert(native_position, returned)
                else:
                    semantic_args.append(returned)
                continue
            if existing.intent != "out":
                existing.intent = "inout"
            immutable_replacement = (
                existing.semantic_type.metadata.get(PYTHON_VALUE_MUTABILITY_METADATA) == PYTHON_VALUE_IMMUTABLE
            )
            if immutable_replacement or _PyiAstParser._is_visible_storage_projection(existing):
                existing.metadata[PYI_PROJECTED_OUTPUT_METADATA] = True
            existing.semantic_type.ownership.mutable = True

    @staticmethod
    def _is_visible_storage_projection(argument: SemanticArgument) -> bool:
        storage = argument.semantic_type.storage
        array = storage.array if storage is not None else None
        if storage is None:
            return False
        if storage.kind == "array":
            return bool(array is not None and not array.allocatable and not array.pointer)
        return bool(
            storage.kind == "reference"
            and not storage.read_only
            and storage.pointer_depth == 1
            and argument.semantic_type.name not in SEMANTIC_DTYPE_TO_NUMPY_DTYPE
        )

    @staticmethod
    def _apply_native_call_returns(
        return_type: SemanticType | None,
        returned_args: list[SemanticArgument],
        projection: list[ProjectionMapping],
    ) -> tuple[SemanticType | None, list[SemanticArgument]]:
        output_by_result = {
            mapping.result_position: mapping
            for mapping in projection
            if mapping.result_position is not None and mapping.python_position is None
        }
        if return_type is not None and 0 in output_by_result:
            mapping = output_by_result[0]
            if mapping.native_name and not mapping.python_name:
                mapping.python_name = mapping.native_name
            return_type.ownership.mutable = True
            if return_type.rank == 0 and return_type.storage is None:
                return_type.storage = SemanticStorageContract(kind="reference", mutable=True, pointer_depth=1)
            returned_args.insert(
                0,
                SemanticArgument(
                    name=mapping.native_name or f"__return_{mapping.result_position}",
                    semantic_type=return_type,
                    intent=mapping.intent,
                    optional=bool(return_type.metadata.pop(_PYI_OPTIONAL_RETURN_METADATA, False)),
                    metadata={"native_position": mapping.native_position},
                ),
            )
            return_type = None

        for returned in returned_args:
            position = returned.metadata.get("return_position")
            mapping = output_by_result.get(position)
            if mapping is not None:
                if mapping.native_name and not mapping.python_name:
                    mapping.python_name = mapping.native_name
                if mapping.native_name:
                    returned.name = mapping.native_name
                returned.intent = mapping.intent
                returned.semantic_type.ownership.mutable = True
                returned.metadata["native_position"] = mapping.native_position
        return return_type, returned_args

    @staticmethod
    def _return_positions_by_name(returned_args: list[SemanticArgument]) -> dict[str, int | None]:
        return {returned.name: returned.metadata.get("return_position") for returned in returned_args}

    @staticmethod
    def _apply_native_call_argument_names(
        semantic_args: list[SemanticArgument],
        return_positions: dict[str, int | None],
        projection: list[ProjectionMapping],
    ) -> None:
        for mapping in projection:
            if mapping.python_position is None:
                continue
            if not 0 <= mapping.python_position < len(semantic_args):
                raise ValueError(f"native_call argument position is out of range: {mapping.python_position}")
            arg = semantic_args[mapping.python_position]
            if mapping.value_kind == "ptr":
                _PyiAstParser._apply_pointer_argument_projection(arg)
            mapping.python_name = arg.name
            if not mapping.native_name:
                mapping.native_name = arg.name
            mapping.intent = arg.intent
            if arg.intent in {"out", "inout"} and mapping.result_position is None:
                mapping.result_position = return_positions.get(arg.name)

    @staticmethod
    def _apply_pointer_argument_projection(arg: SemanticArgument) -> None:
        semantic_type = arg.semantic_type
        if semantic_type.rank != 0:
            raise ValueError(f"Ref(Arg(...)) projection for {arg.name!r} requires a scalar argument")
        storage = semantic_type.storage
        read_only = str(arg.intent).lower() == "in" or bool(storage is not None and storage.read_only)
        semantic_type.storage = SemanticStorageContract(
            kind="reference",
            read_only=read_only,
            mutable=not read_only,
            pointer_depth=1,
        )
        semantic_type.ownership.mutable = not read_only

    @staticmethod
    def _shift_pointer_argument_value(
        mapping: ProjectionMapping,
        old_position: int,
        new_position: int,
    ) -> None:
        if mapping.value_kind != "ptr" or not isinstance(mapping.value, dict):
            return
        if mapping.value.get("kind") == "arg" and mapping.value.get("position") == old_position:
            mapping.value["position"] = new_position

    def return_items(self, node: ast.expr) -> list[ast.expr]:
        if self.is_subscript_of(node, "tuple") or self.is_subscript_of(node, "Tuple"):
            return self.subscript_items(node)
        return [node]


class _ClassBodyVisitor(ast.NodeVisitor):
    def __init__(self, parser: _PyiAstParser, *, class_name: str):
        self.parser = parser
        self.class_name = class_name
        self.fields: list[SemanticField] = []
        self.methods: list[SemanticMethod] = []
        self.pending_overloads: list[tuple[SemanticMethod, str, str | None]] = []
        self.classes: list[SemanticClass] = []
        self.constructor_from_fields = False
        self.has_bound_constructor = False

    def visit_body(self, nodes: list[ast.stmt]) -> None:
        for node in nodes:
            self.visit(node)

    def visit_Pass(self, node: ast.Pass) -> None:
        return None

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self.fields.append(self.parser.ann_assign(node, default_intent="in", binding_cls=SemanticField))

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        decorators = self.parser.decorators(node.decorator_list, context="class body")
        if decorators.external:
            raise ValueError("external is not valid for a class method")
        if decorators.native_type is not None:
            raise ValueError("native_type is only valid for classes")
        if not node.decorator_list and self._is_generated_constructor(node):
            self.constructor_from_fields = True
            return
        if node.name == "__init__" and decorators.bind_target is None and decorators.overload_target is None:
            raise ValueError('Non-generated __init__ declarations must use @bind("specific_name")')
        if (
            node.name == "__init__"
            and decorators.bind_target is not None
            and node.args.args
            and node.args.args[0].arg == "self"
            and node.args.args[0].annotation is not None
        ):
            raise ValueError("Bound constructor declarations omit the native self argument")
        method = self.parser.method_def(
            node,
            visibility=decorators.visibility,
            projection=decorators.projection,
            is_static=decorators.is_static,
            native_name=decorators.bind_target,
            class_name=self.class_name,
            infer_passed_object=decorators.overload_target is None,
            hold_gil=decorators.hold_gil,
            error_status_policy=decorators.error_status_policy,
        )
        if node.name == "__init__" and decorators.bind_target is not None:
            self.has_bound_constructor = True
        if decorators.overload_target is not None:
            self.pending_overloads.append((method, decorators.overload_target, decorators.overload_generic))
        else:
            self.methods.append(method)

    @staticmethod
    def _is_generated_constructor(node: ast.FunctionDef) -> bool:
        args = node.args
        if (
            node.name == "__init__"
            and len(args.args) == 1
            and args.args[0].arg == "self"
            and args.args[0].annotation is None
            and not args.defaults
            and not args.kwonlyargs
            and not args.vararg
            and not args.kwarg
            and not args.posonlyargs
        ):
            return True
        return (
            node.name == "__init__"
            and len(args.args) == 1
            and args.args[0].arg == "self"
            and args.args[0].annotation is None
            and not args.defaults
            and bool(args.kwonlyargs)
            and all(default is not None for default in args.kw_defaults)
            and not args.vararg
            and not args.kwarg
            and not args.posonlyargs
        )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        decorators = self.parser.decorators(node.decorator_list, context="class body")
        if (
            decorators.has_native_call
            or decorators.bind_target is not None
            or decorators.hold_gil
            or decorators.error_status_policy is not None
            or decorators.external
        ):
            raise ValueError(f"Unsupported class body decorator: {ast.unparse(node.decorator_list[-1])!r}")
        if len(node.bases) == 1 and self.parser.is_subscript_of(node.bases[0], "Enum"):
            raise ValueError(
                f"Enum declarations are not supported; use Final[...] integer constants: {_node_text(node)!r}"
            )
        self.classes.append(
            self.parser.class_def(
                node,
                visibility=decorators.visibility,
                native_type=decorators.native_type,
            )
        )

    def generic_visit(self, node: ast.AST) -> None:
        raise ValueError(f"Unsupported class body node: {_node_text(node)!r}")


class _ModuleVisitor(ast.NodeVisitor):
    def __init__(self, parser: _PyiAstParser):
        self.parser = parser

    def visit_Module(self, node: ast.Module) -> None:
        for item in node.body:
            self.visit(item)

    def visit_Import(self, node: ast.Import) -> None:
        self.parser.module.imports.append(self.parser.import_name(node))

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        semantic_import = self.parser.import_from(node)
        if semantic_import.module == "typing" and any(item.source == "overload" for item in semantic_import.items):
            raise ValueError('typing.overload is not supported; use x2py @overload("specific")')
        self.parser.module.imports.append(semantic_import)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self.parser.module.variables.append(self.parser.ann_assign(node, default_intent="in"))

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        decorators = self.parser.decorators(node.decorator_list, context="class")
        if (
            decorators.has_native_call
            or decorators.bind_target is not None
            or decorators.hold_gil
            or decorators.error_status_policy is not None
            or decorators.external
        ):
            raise ValueError(f"Unsupported class decorator: {ast.unparse(node.decorator_list[-1])!r}")
        if len(node.bases) == 1 and self.parser.is_subscript_of(node.bases[0], "Enum"):
            raise ValueError(
                f"Enum declarations are not supported; use Final[...] integer constants: {_node_text(node)!r}"
            )
        self.parser.module.classes.append(
            self.parser.class_def(
                node,
                visibility=decorators.visibility,
                native_type=decorators.native_type,
            )
        )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        decorators = self.parser.decorators(node.decorator_list, context=".pyi")
        if decorators.native_type is not None:
            raise ValueError("native_type is only valid for classes")
        function = self.parser.function_def(
            node,
            visibility=decorators.visibility,
            projection=decorators.projection,
            native_name=decorators.bind_target,
            external=decorators.external,
            hold_gil=decorators.hold_gil,
            error_status_policy=decorators.error_status_policy,
        )
        if decorators.overload_target is not None:
            self.parser._pending_overloads.append(
                _PendingOverload(
                    self.parser.module,
                    function,
                    decorators.overload_target,
                    decorators.overload_generic,
                )
            )
        else:
            self.parser.module.functions.append(function)

    def generic_visit(self, node: ast.AST) -> None:
        raise ValueError(f"Unsupported .pyi node: {_node_text(node)!r}")


def _node_text(node: ast.AST) -> str:
    text = ast.unparse(node)
    return text.splitlines()[0] if text else type(node).__name__


def _annotate_imported_external_type_refs(module: SemanticModule) -> None:
    imported = _imported_type_refs(module)
    for semantic_type in _iter_module_semantic_types(module):
        imported_ref = imported.get(semantic_type.name)
        if imported_ref is None:
            continue
        origin_module, source_name, local_name = imported_ref
        semantic_type.metadata.setdefault(
            EXTERNAL_TYPE_REF_METADATA,
            {
                "name": source_name,
                "local_name": local_name,
                "origin_module": origin_module,
                "wrapped": False,
                "representation": "opaque",
            },
        )


def _imported_type_refs(module: SemanticModule) -> dict[str, tuple[str, str, str]]:
    imported: dict[str, tuple[str, str, str]] = {}
    for imp in module.imports:
        if isinstance(imp, SemanticImport):
            for item in imp.items:
                local_name = item.target or item.source
                imported[local_name] = (imp.module, item.source, local_name)
            continue
        for item in imp.split(","):
            module_name, _, alias = item.strip().partition(" as ")
            visible_name = alias or module_name
            imported[visible_name] = (module_name, visible_name, visible_name)

    for semantic_type in _iter_module_semantic_types(module):
        if "." not in semantic_type.name:
            continue
        module_name, type_name = semantic_type.name.rsplit(".", 1)
        visible_module = module_name.split(".", 1)[0]
        imported_module = imported.get(visible_module)
        if imported_module is not None:
            imported[semantic_type.name] = (imported_module[0], type_name, semantic_type.name)
    return imported


def _reconcile_external_type_refs(modules: list[SemanticModule]) -> list[SemanticModule]:
    definitions = {(module.name, declaration.name): declaration for module in modules for declaration in module.classes}
    for module in modules:
        for semantic_type in _iter_module_semantic_types(module):
            ref = semantic_type.metadata.get(EXTERNAL_TYPE_REF_METADATA)
            if not isinstance(ref, dict):
                continue
            declaration = definitions.get((ref.get("origin_module"), ref.get("name")))
            wrapped = declaration is not None and (
                not isinstance(declaration, SemanticClass) or "Opaque" not in declaration.base_classes
            )
            ref["wrapped"] = wrapped
            ref["representation"] = "wrapped" if wrapped else "opaque"
    return modules
