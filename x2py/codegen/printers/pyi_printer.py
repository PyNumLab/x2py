from __future__ import annotations

import ast
from collections.abc import Iterable
from copy import deepcopy
import json
import keyword
import re

from x2py.ownership_policy import OWNERSHIP_POLICY_METADATA, POINTER_POLICY_FIELDS, POINTER_POLICY_METADATA
from x2py.numpy_types import SEMANTIC_DTYPE_TO_NUMPY_DTYPE
from x2py.semantics.models import (
    EXTERNAL_TYPE_REF_METADATA,
    FORTRAN_GENERIC_NAME_METADATA,
    MODULE_VARIABLE_GETTER_METADATA,
    OVERLOAD_KIND_METADATA,
    OVERLOAD_TARGET_METADATA,
    PYTHON_BOUND_POSITION_METADATA,
    PYTHON_METHOD_NAME_METADATA,
    PYTHON_STATIC_METADATA,
    ProjectionMapping,
    ProcedureOverloadSet,
    SemanticArgument,
    SemanticArrayContract,
    SemanticClass,
    SemanticConstraint,
    SemanticEnum,
    SemanticFunction,
    SemanticImport,
    SemanticImportItem,
    SemanticMethod,
    SemanticModule,
    SemanticType,
    SemanticVariable,
    _iter_module_semantic_types,
)


class PyiPrinter:
    """Emit Python stub text from semantic IR models.

    The printer is a lightweight visitor. `emit()` dispatches by semantic model
    type, while the `emit_*` methods remain explicit compatibility entrypoints.
    """

    def emit(self, node) -> str:
        if isinstance(node, SemanticModule):
            return self.emit_module(node)
        if isinstance(node, ProcedureOverloadSet):
            return self.emit_overload_set(node)
        if isinstance(node, SemanticClass):
            return self.emit_class(node)
        if isinstance(node, SemanticEnum):
            return self.emit_enum(node)
        if isinstance(node, SemanticMethod):
            return self.emit_method(node)
        if isinstance(node, SemanticFunction):
            return self.emit_function(node)
        if isinstance(node, SemanticArgument):
            return self.emit_argument(node)
        if isinstance(node, SemanticVariable):
            return self.emit_data_member(node)
        if isinstance(node, SemanticType):
            return self.emit_semantic_type(node)
        if isinstance(node, SemanticConstraint):
            return self.emit_constraint(node)
        raise TypeError(f"Unsupported semantic model for .pyi emission: {type(node)!r}")

    @staticmethod
    def emit_constraint(constraint: SemanticConstraint) -> str:
        if constraint.name == "Constant":
            raise ValueError("Constant constraints are emitted through Final[...] data declarations")
        if constraint.name == "Shape":
            raise ValueError("Shape constraints are not canonical; put dimensions inside T[...]")
        if not constraint.arguments:
            return constraint.name
        args = ", ".join(map(repr, constraint.arguments))
        return f"{constraint.name}({args})"

    def emit_semantic_type(self, semantic_type: SemanticType) -> str:
        if semantic_type.name == "Unknown" or semantic_type.dtype == "Unknown":
            raise ValueError("Cannot emit .pyi with unresolved semantic type 'Unknown'")
        if semantic_type.name == "Callable":
            text = self._emit_callable_type(semantic_type)
        elif semantic_type.storage is not None:
            text = self._emit_storage_type(semantic_type)
        else:
            text = semantic_type.name
        annotations = [
            *self._semantic_annotation_metadata(semantic_type),
            *[self.emit_constraint(constraint) for constraint in semantic_type.constraints],
        ]
        if annotations:
            return self._annotated_type_text(text, annotations)
        return text

    def _emit_storage_type(self, semantic_type: SemanticType) -> str:
        storage = semantic_type.storage
        if storage is None:
            return semantic_type.name
        if storage.kind == "value":
            if storage.read_only:
                return f"Const({semantic_type.name})"
            return semantic_type.name
        if storage.kind in {"reference", "pointer"}:
            target = semantic_type.name
            if storage.read_only:
                target = f"Const({target})"
            if storage.pointer_depth > 1:
                return f"Ptr[{storage.pointer_depth}]({target})"
            return f"Ptr({target})"
        if storage.kind == "array":
            return self._emit_array_type(semantic_type)
        return semantic_type.name

    def _emit_array_type(self, semantic_type: SemanticType) -> str:
        storage = semantic_type.storage
        array = storage.array if storage is not None else None
        dimensions = self._array_dimensions(semantic_type, array)
        base = f"{semantic_type.name}[{', '.join(dimensions)}]"
        if storage is not None and storage.read_only:
            base = f"Const({base})"

        metadata = self._array_annotation_metadata(array)
        if metadata:
            return f"Annotated[{base}, {', '.join(metadata)}]"
        return base

    @staticmethod
    def _array_dimensions(
        semantic_type: SemanticType,
        array: SemanticArrayContract | None,
    ) -> list[str]:
        shape = list(array.shape if array is not None and array.shape else semantic_type.shape)
        if not shape and semantic_type.rank > 0:
            shape = [":" for _ in range(semantic_type.rank)]
        return [PyiPrinter._canonical_array_dimension(dim) for dim in shape]

    @staticmethod
    def _canonical_array_dimension(dimension: object) -> str:
        text = str(dimension)
        try:
            return ast.unparse(ast.parse(text, mode="eval").body)
        except SyntaxError:
            return text

    @staticmethod
    def _array_annotation_metadata(array: SemanticArrayContract | None) -> list[str]:
        if array is None:
            return []
        metadata: list[str] = []
        if array.order in {"ORDER_F", "ORDER_ANY"}:
            metadata.append(array.order)
        if array.allocatable:
            metadata.append("Allocatable")
        if array.pointer:
            metadata.append("Pointer")
        return metadata

    @staticmethod
    def _semantic_annotation_metadata(semantic_type: SemanticType) -> list[str]:
        metadata: list[str] = []
        character_length = semantic_type.metadata.get("fortran_character_length")
        if character_length is not None:
            metadata.append(f"FortranCharacterLength({json.dumps(str(character_length))})")
        if semantic_type.metadata.get("fortran_allocatable"):
            metadata.append("FortranAllocatable")
        if semantic_type.metadata.get("fortran_target"):
            metadata.append("FortranTarget")
        pointer_association = semantic_type.metadata.get("fortran_pointer_association")
        if pointer_association is not None:
            metadata.append(f"PointerAssociation({json.dumps(str(pointer_association))})")
        pointer_policy = semantic_type.metadata.get(POINTER_POLICY_METADATA)
        if isinstance(pointer_policy, dict):
            arguments = []
            for name in POINTER_POLICY_FIELDS:
                value = pointer_policy.get(name)
                if value is not None:
                    rendered = repr(value) if isinstance(value, bool) else json.dumps(str(value))
                    arguments.append(f"{name}={rendered}")
            metadata.append(f"PointerPolicy({', '.join(arguments)})")
        ownership_policy = semantic_type.metadata.get(OWNERSHIP_POLICY_METADATA)
        if isinstance(ownership_policy, dict):
            owner = ownership_policy.get("owner")
            transfer = ownership_policy.get("transfer")
            destruction = ownership_policy.get("destruction")
            if owner is not None:
                metadata.append(f"Ownership({json.dumps(str(owner))})")
            if transfer is not None:
                metadata.append(f"Transfer({json.dumps(str(transfer))})")
            if destruction is not None:
                metadata.append(f"Destruction({json.dumps(str(destruction))})")
        return metadata

    def _emit_callable_type(self, semantic_type: SemanticType) -> str:
        arguments = semantic_type.metadata.get("arguments")
        return_type = semantic_type.metadata.get("return")
        if isinstance(arguments, list) and return_type is not None:
            args = ", ".join(self.emit_semantic_type(arg) for arg in arguments)
            return f"Callable[[{args}], {self.emit_semantic_type(return_type)}]"
        if return_type is not None:
            return f"Callable[..., {self.emit_semantic_type(return_type)}]"
        return "Callable"

    def emit_argument(self, arg: SemanticArgument) -> str:
        name = self._parameter_target(arg.name)
        return self._emit_typed_name(
            name,
            arg,
            original_name=arg.name if name != arg.name else None,
        )

    def emit_data_member(self, arg: SemanticVariable) -> str:
        return self._emit_typed_name(self._annotation_target(arg.name), arg)

    def emit_module_variable(self, arg: SemanticVariable) -> str:
        if self._is_constant(arg.semantic_type):
            return self._emit_typed_name(self._annotation_target(arg.name), arg)
        if self._is_allocatable_module_array(arg):
            return self.emit_module_variable_getter(arg)
        if self._is_scalar_module_variable(arg):
            return self.emit_scalar_module_variable_accessors(arg)
        return self._emit_typed_name(self._annotation_target(arg.name), arg)

    def emit_scalar_module_variable_accessors(self, arg: SemanticVariable) -> str:
        type_text = self.emit_semantic_type(arg.semantic_type)
        getter_name = str(arg.metadata.get(MODULE_VARIABLE_GETTER_METADATA) or f"get_{arg.name}")
        setter_name = str(arg.metadata.get("module_variable_setter") or f"set_{arg.name}")
        return "\n".join(
            (
                f"def {getter_name}() -> {type_text}: ...",
                "",
                f"def {setter_name}(value: {type_text}) -> None: ...",
            )
        )

    def emit_module_variable_getter(self, arg: SemanticVariable) -> str:
        getter_name = str(arg.metadata.get(MODULE_VARIABLE_GETTER_METADATA) or f"get_{arg.name}")
        return_type = f"{self.emit_semantic_type(arg.semantic_type)} | None"
        return f'@module_variable("{arg.name}")\ndef {getter_name}() -> {return_type}: ...'

    @staticmethod
    def _is_allocatable_module_array(arg: SemanticVariable) -> bool:
        storage = arg.semantic_type.storage
        return bool(
            storage is not None
            and storage.array is not None
            and storage.array.allocatable
            and arg.metadata.get(MODULE_VARIABLE_GETTER_METADATA) is not False
        )

    @staticmethod
    def _is_scalar_module_variable(arg: SemanticVariable) -> bool:
        return (
            arg.origin.source_language == "fortran"
            and arg.visibility == "public"
            and arg.semantic_type.rank == 0
            and arg.semantic_type.name != "String"
            and arg.semantic_type.name in SEMANTIC_DTYPE_TO_NUMPY_DTYPE
        )

    @staticmethod
    def _is_allocatable_array(semantic_type: SemanticType) -> bool:
        storage = semantic_type.storage
        return bool(storage is not None and storage.array is not None and storage.array.allocatable)

    def _emit_typed_name(
        self,
        name: str,
        arg: SemanticVariable,
        *,
        original_name: str | None = None,
    ) -> str:
        semantic_type = self._without_constant_constraint(arg.semantic_type)
        type_text = self.emit_semantic_type(semantic_type)
        annotation_metadata = []
        if original_name is not None:
            annotation_metadata.append(f"Name({json.dumps(original_name)})")
        if self._requires_intent_metadata(arg):
            annotation_metadata.append(f"Intent({arg.intent!r})")
        if annotation_metadata:
            type_text = self._annotated_type_text(type_text, annotation_metadata)
        if self._is_constant(arg.semantic_type):
            type_text = f"Final[{type_text}]"
        if getattr(arg, "visibility", "public") == "private":
            type_text = f"private[{type_text}]"

        text = f"{name}: {type_text}"
        if arg.optional:
            text += " = ..."
        else:
            default_value = self._pyi_default_value(arg)
            if default_value is not None:
                text += f" = {default_value}"
        return text

    @staticmethod
    def _annotated_type_text(type_text: str, metadata: list[str]) -> str:
        suffix = ", ".join(metadata)
        if type_text.startswith("Annotated[") and type_text.endswith("]"):
            return f"{type_text[:-1]}, {suffix}]"
        return f"Annotated[{type_text}, {suffix}]"

    @staticmethod
    def _is_constant(semantic_type: SemanticType) -> bool:
        return any(constraint.name == "Constant" for constraint in semantic_type.constraints)

    @staticmethod
    def _is_enum_constant(arg: SemanticVariable) -> bool:
        return PyiPrinter._is_constant(arg.semantic_type) and bool(
            arg.semantic_type.metadata.get("semantic_enum") or arg.semantic_type.metadata.get("c_enum")
        )

    @staticmethod
    def _enum_default_value(arg: SemanticVariable) -> str | None:
        pyi_value = arg.metadata.get("pyi_default_value")
        if isinstance(pyi_value, str):
            return pyi_value
        if arg.origin.source_language == "c":
            return None
        return arg.default_value

    @staticmethod
    def _pyi_default_value(arg: SemanticVariable) -> str | None:
        if (self_value := arg.metadata.get("pyi_default_value")) and isinstance(self_value, str):
            return self_value
        if PyiPrinter._is_enum_constant(arg):
            return PyiPrinter._enum_default_value(arg)
        if initializer := arg.metadata.get("fortran_initializer"):
            return PyiPrinter._python_literal_text(initializer) or PyiPrinter._python_literal_text(arg.default_value)
        return PyiPrinter._python_literal_text(arg.default_value)

    @staticmethod
    def _python_literal_text(value: str | None) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        text = re.sub(r"\.true\.", "True", text, flags=re.IGNORECASE)
        text = re.sub(r"\.false\.", "False", text, flags=re.IGNORECASE)
        text = re.sub(r"(?<=\d)[dD](?=[+-]?\d)", "e", text)
        try:
            return ast.unparse(ast.parse(text, mode="eval").body)
        except SyntaxError:
            return None

    @staticmethod
    def _without_constant_constraint(semantic_type: SemanticType) -> SemanticType:
        if not PyiPrinter._is_constant(semantic_type):
            return semantic_type
        return SemanticType(
            name=semantic_type.name,
            rank=semantic_type.rank,
            dtype=semantic_type.dtype,
            shape=list(semantic_type.shape),
            constraints=[constraint for constraint in semantic_type.constraints if constraint.name != "Constant"],
            coercions=list(semantic_type.coercions),
            ownership=semantic_type.ownership,
            metadata=dict(semantic_type.metadata),
            storage=semantic_type.storage,
            origin=semantic_type.origin,
        )

    def emit_function(self, func: SemanticFunction) -> str:
        return_type = self._projected_return_annotation(func)
        decorator = self._decorators(func)
        return self._emit_callable(
            name=func.name,
            arguments=[self.emit_argument(arg) for arg in self._call_arguments(func)],
            return_type=return_type,
            decorator=decorator,
            def_indent="",
            parameter_indent="    ",
        )

    def emit_method(self, method: SemanticMethod) -> str:
        return_type = self._projected_return_annotation(method)
        decorator = self._decorators(method, indent="    ")
        arguments = [self.emit_argument(arg) for arg in self._method_call_arguments(method)]
        if not method.is_static:
            arguments.insert(0, "self")
        return self._emit_callable(
            name=method.name,
            arguments=arguments,
            return_type=return_type,
            decorator=decorator,
            def_indent="    ",
            parameter_indent="        ",
        ).rstrip()

    def emit_overload_set(self, overload_set: ProcedureOverloadSet, *, in_class: bool = False) -> str:
        definitions = []
        for procedure in overload_set.procedures:
            candidate = deepcopy(procedure)
            target = str(candidate.metadata.get(OVERLOAD_TARGET_METADATA) or candidate.native_name or candidate.name)
            if in_class:
                candidate = self._overload_method(overload_set, candidate)
                definition = self.emit_method(candidate)
                indent = "    "
            else:
                candidate.name = overload_set.name
                definition = self.emit_function(candidate)
                indent = ""
            generic = self._overload_generic_argument(candidate)
            definitions.append(f'{indent}@overload("{target}"{generic})\n{definition}')
        return "\n\n".join(definitions)

    @staticmethod
    def _overload_generic_argument(procedure: SemanticFunction) -> str:
        if procedure.metadata.get(OVERLOAD_KIND_METADATA) not in {"operator", "comparison"}:
            return ""
        generic_name = str(procedure.metadata.get(FORTRAN_GENERIC_NAME_METADATA, ""))
        if re.sub(r"\s+", "", generic_name).casefold() not in {
            "operator(.eqv.)",
            "operator(.neqv.)",
        }:
            return ""
        return f', generic="{generic_name}"'

    @staticmethod
    def _overload_method(
        overload_set: ProcedureOverloadSet,
        procedure: SemanticFunction,
    ) -> SemanticMethod:
        bound_position = procedure.metadata.get(PYTHON_BOUND_POSITION_METADATA)
        return SemanticMethod(
            name=str(procedure.metadata.get(PYTHON_METHOD_NAME_METADATA, overload_set.name)),
            native_name=procedure.native_name,
            arguments=procedure.arguments,
            return_type=procedure.return_type,
            locals=procedure.locals,
            contracts=procedure.contracts,
            projection=procedure.projection,
            metadata=procedure.metadata,
            visibility=procedure.visibility,
            origin=procedure.origin,
            is_static=bool(procedure.metadata.get(PYTHON_STATIC_METADATA)),
            passed_object_name=(procedure.arguments[bound_position].name if isinstance(bound_position, int) else None),
            passed_object_position=bound_position if isinstance(bound_position, int) else None,
        )

    def emit_class(self, cls: SemanticClass) -> str:
        bases = f"({', '.join(cls.base_classes)})" if cls.base_classes else ""
        body = self._class_body(cls)
        decorator = "@private\n" if self._is_private(cls) else ""
        return f"""
{decorator}class {cls.name}{bases}:
{body}
""".strip()

    def emit_enum(self, enum: SemanticEnum) -> str:
        decorator = "@private\n" if self._is_private(enum) else ""
        underlying = self.emit_semantic_type(enum.underlying_type)
        return f"{decorator}class {enum.name}(Enum[{underlying}]):\n    pass"

    def emit_module(self, module: SemanticModule) -> str:
        sections: list[str] = []
        self._append_imports(sections, module)
        self._append_items(sections, module.classes, self.emit)
        self._append_items(sections, module.variables, self.emit_module_variable)
        self._append_items(sections, module.functions, self.emit_function)
        self._append_items(sections, module.overload_sets, self.emit_overload_set)
        return "\n".join(sections)

    def _emit_callable(
        self,
        *,
        name: str,
        arguments: list[str],
        return_type: str,
        decorator: str,
        def_indent: str,
        parameter_indent: str,
    ) -> str:
        if not arguments:
            return f"{decorator}{def_indent}def {name}() -> {return_type}: ..."
        if arguments == ["self"]:
            return f"{decorator}{def_indent}def {name}(self) -> {return_type}: ..."

        args = (",\n" + parameter_indent).join(arguments)
        return f"{decorator}{def_indent}def {name}(\n{parameter_indent}{args}\n{def_indent}) -> {return_type}: ..."

    def _class_body(self, cls: SemanticClass) -> str:
        body_parts = []

        nested_classes = "\n\n".join(self._indent_block(self.emit_class(nested), "    ") for nested in cls.classes)
        if nested_classes:
            body_parts.append(nested_classes)

        constructor = self._class_constructor(cls)
        if constructor:
            body_parts.append(constructor)

        fields = "\n".join(f"    {self.emit_data_member(field)}" for field in cls.fields)
        if fields:
            body_parts.append(fields)

        methods = "\n\n".join(self.emit_method(method) for method in cls.methods)
        if methods:
            body_parts.append(methods)

        overload_sets = "\n\n".join(
            self.emit_overload_set(overload_set, in_class=True) for overload_set in cls.overload_sets
        )
        if overload_sets:
            body_parts.append(overload_sets)

        if not body_parts:
            return "    pass"
        return "\n\n".join(body_parts)

    def _class_constructor(self, cls: SemanticClass) -> str:
        if cls.origin.source_language != "fortran":
            return ""
        arguments = [
            self._constructor_argument(field) for field in cls.fields if self._constructor_accepts_field(field)
        ]
        if not arguments:
            return ""
        return self._emit_callable(
            name="__init__",
            arguments=["self", "*", *arguments],
            return_type="None",
            decorator="",
            def_indent="    ",
            parameter_indent="        ",
        ).rstrip()

    def _constructor_argument(self, field: SemanticVariable) -> str:
        name = self._parameter_target(field.name)
        semantic_type = self._without_constant_constraint(field.semantic_type)
        type_text = self.emit_semantic_type(semantic_type)
        initializer = field.metadata.get("fortran_initializer")
        default_value = (
            self._python_literal_text(initializer) or self._python_literal_text(field.default_value) or "..."
        )
        if name != field.name:
            type_text = self._annotated_type_text(type_text, [f"Name({json.dumps(field.name)})"])
        return f"{name}: {type_text} = {default_value}"

    @staticmethod
    def _constructor_accepts_field(field: SemanticVariable) -> bool:
        semantic_type = field.semantic_type
        return (
            field.visibility == "public"
            and semantic_type.rank == 0
            and semantic_type.name != "String"
            and semantic_type.name in SEMANTIC_DTYPE_TO_NUMPY_DTYPE
        )

    @staticmethod
    def _indent_block(text: str, indent: str) -> str:
        return "\n".join(f"{indent}{line}" if line else line for line in text.splitlines())

    def _append_imports(self, sections: list[str], module: SemanticModule) -> None:
        imports = self._effective_imports(module)
        for imp in imports:
            sections.append(self._emit_import(imp))
        if imports:
            sections.append("")

    @staticmethod
    def _effective_imports(module: SemanticModule) -> list[str | SemanticImport]:
        imports = list(module.imports)
        imported_items = {
            (imp.module, item.source, item.target or item.source)
            for imp in imports
            if isinstance(imp, SemanticImport)
            for item in imp.items
        }
        synthetic: dict[str, list[SemanticImportItem]] = {}
        for semantic_type in _iter_module_semantic_types(module):
            ref = semantic_type.metadata.get(EXTERNAL_TYPE_REF_METADATA)
            if not isinstance(ref, dict):
                continue
            origin_module = ref.get("origin_module")
            source_name = ref.get("name")
            local_name = ref.get("local_name") or source_name
            if not all(isinstance(value, str) and value for value in (origin_module, source_name, local_name)):
                continue
            key = (origin_module, source_name, local_name)
            if key in imported_items:
                continue
            synthetic.setdefault(origin_module, []).append(
                SemanticImportItem(
                    source=source_name,
                    target=local_name if local_name != source_name else None,
                )
            )
            imported_items.add(key)
        imports.extend(
            SemanticImport(
                module=module_name,
                items=sorted(items, key=lambda item: (item.source, item.target or "")),
            )
            for module_name, items in sorted(synthetic.items())
        )
        return imports

    @staticmethod
    def _has_overload_sets(module: SemanticModule) -> bool:
        def class_has_overloads(cls: SemanticClass) -> bool:
            return bool(cls.overload_sets) or any(class_has_overloads(nested) for nested in cls.classes)

        return bool(module.overload_sets) or any(
            class_has_overloads(cls) for cls in module.classes if isinstance(cls, SemanticClass)
        )

    @staticmethod
    def _emit_import(imp: str | SemanticImport) -> str:
        if isinstance(imp, str):
            return f"import {imp}"
        if not imp.items:
            return f"import {imp.module}"
        items = ", ".join(PyiPrinter._emit_import_item(item) for item in imp.items)
        return f"from {imp.module} import {items}"

    @staticmethod
    def _emit_import_item(item: SemanticImportItem) -> str:
        if item.target and item.target != item.source:
            return f"{item.source} as {item.target}"
        return item.source

    def _append_items(self, sections: list[str], items: list, emit_item) -> None:
        for item in items:
            sections.append(emit_item(item))
            sections.append("")

    def _projected_return_annotation(self, func: SemanticFunction) -> str:
        parts = []
        if func.return_type:
            parts.append(self.emit_semantic_type(func.return_type))
        parts.extend(
            self._projected_argument_return(arg, visible=visible)
            for _, arg, visible in sorted(
                self._projected_return_arguments(func),
                key=lambda item: item[0],
            )
        )
        if not parts:
            return "None"
        if len(parts) == 1:
            return parts[0]
        return f"tuple[{', '.join(parts)}]"

    @staticmethod
    def _projected_return_arguments(func: SemanticFunction) -> list[tuple[int, SemanticArgument, bool]]:
        if func.metadata.get(OVERLOAD_KIND_METADATA) == "assignment":
            return []
        by_name = {arg.name: arg for arg in func.arguments}
        returned = []
        for mapping in func.projection:
            if mapping.result_position is None:
                continue
            arg_name = mapping.python_name or mapping.native_name
            arg = by_name.get(arg_name)
            if arg is not None:
                returned.append((mapping.result_position, arg, mapping.python_position is not None))
        return returned

    def _projected_argument_return(self, arg: SemanticArgument, *, visible: bool) -> str:
        if visible:
            return self._named_return(arg)
        return self._plain_projected_return(arg)

    def _named_return(self, arg: SemanticArgument) -> str:
        optional = ", Optional" if arg.optional or self._is_allocatable_array(arg.semantic_type) else ""
        return f'Returns["{arg.name}", {self.emit_semantic_type(arg.semantic_type)}{optional}]'

    def _plain_projected_return(self, arg: SemanticArgument) -> str:
        type_text = self.emit_semantic_type(arg.semantic_type)
        if arg.optional or self._is_allocatable_array(arg.semantic_type):
            return f"{type_text} | None"
        return type_text

    def _decorators(self, func: SemanticFunction, *, indent: str = "") -> str:
        decorators = []
        if self._is_private(func):
            decorators.append(f"{indent}@private")
        if isinstance(func, SemanticMethod) and func.is_static:
            decorators.append(f"{indent}@staticmethod")
        if self._requires_native_call(func):
            decorators.append(f"{indent}{self._native_call(func.projection)}")
        if not decorators:
            return ""
        return "\n".join(decorators) + "\n"

    def _native_call(self, projection: list[ProjectionMapping]) -> str:
        entries = ", ".join(
            self._native_projection_entry(mapping)
            for mapping in sorted(
                projection, key=lambda item: item.native_position if item.native_position is not None else -1
            )
        )
        return f"@native_call([{entries}])"

    @staticmethod
    def _native_projection_entry(mapping: ProjectionMapping) -> str:
        if mapping.value_kind:
            return PyiPrinter._native_projection_value(mapping)
        if mapping.python_position is not None:
            return f"Arg({mapping.python_position})"
        if mapping.result_position is not None:
            if mapping.native_name:
                return f"Return({mapping.native_name!r}, {mapping.result_position})"
            return f"Return({mapping.result_position})"
        raise ValueError("native_call cannot represent a native-only projection entry")

    @staticmethod
    def _native_projection_value(mapping: ProjectionMapping) -> str:
        if mapping.value_kind == "const":
            return f"Const({mapping.value!r})"
        if mapping.value_kind == "len":
            return f"Len({PyiPrinter._native_value_ref(mapping.value)})"
        if mapping.value_kind == "shape":
            return f"{PyiPrinter._native_value_ref(mapping.value['value'])}.shape[{mapping.value['dim']}]"
        if mapping.value_kind == "is_present":
            return f"IsPresent({PyiPrinter._native_value_ref(mapping.value)})"
        if mapping.value_kind == "work":
            return f"Work({mapping.value!r})"
        raise ValueError(f"Unsupported native_call projection entry: {mapping.value_kind!r}")

    @staticmethod
    def _native_value_ref(value: dict[str, int | str]) -> str:
        kind = value.get("kind")
        if kind == "arg":
            return f"Arg({value['position']})"
        if kind == "return":
            return f"Return({value['position']})"
        if kind == "work":
            return f"Work({value['name']!r})"
        raise ValueError(f"Unsupported native_call value reference: {kind!r}")

    @staticmethod
    def _requires_native_call(func: SemanticFunction) -> bool:
        return any(PyiPrinter._requires_explicit_projection_mapping(mapping) for mapping in func.projection)

    @staticmethod
    def _requires_explicit_projection_mapping(mapping: ProjectionMapping) -> bool:
        if mapping.intent == "inout":
            return mapping.result_position is not None or mapping.python_position != mapping.native_position
        if mapping.intent == "out" and mapping.result_position is not None:
            return True
        if mapping.intent != "in":
            return mapping.python_position is None
        if mapping.result_position is not None:
            return True
        if mapping.python_position is None:
            return True
        return mapping.native_position is not None and mapping.python_position != mapping.native_position

    @staticmethod
    def _call_arguments(func: SemanticFunction) -> list[SemanticArgument]:
        hidden_names = {
            mapping.python_name or mapping.native_name
            for mapping in func.projection
            if mapping.native_position is not None and mapping.python_position is None
        }
        return [arg for arg in func.arguments if arg.name not in hidden_names]

    @staticmethod
    def _requires_intent_metadata(arg: SemanticVariable) -> bool:
        return getattr(arg, "intent", "in") == "out"

    @classmethod
    def _method_call_arguments(cls, method: SemanticMethod) -> list[SemanticArgument]:
        args = cls._call_arguments(method)
        if method.is_static:
            return args
        if method.passed_object_position is not None:
            return [arg for index, arg in enumerate(args) if index != method.passed_object_position]
        if args and args[0].name == "self":
            return args[1:]
        return args

    @staticmethod
    def _is_private(node) -> bool:
        return getattr(node, "visibility", "public") == "private"

    @staticmethod
    def _annotation_target(name: str) -> str:
        if name.isidentifier() and not keyword.iskeyword(name):
            return name
        return f"var[{name!r}]"

    @staticmethod
    def _parameter_target(name: str) -> str:
        if name.isidentifier() and not keyword.iskeyword(name):
            return name
        if name.isidentifier():
            return f"{name}_"
        target = re.sub(r"\W+", "_", name).strip("_") or "arg"
        if target[:1].isdigit():
            target = f"arg_{target}"
        if keyword.iskeyword(target):
            target = f"{target}_"
        return target


_DEFAULT_PRINTER = PyiPrinter()


def emit_module(module: SemanticModule) -> str:
    return _DEFAULT_PRINTER.emit_module(module)


def opaque_dependency_modules(
    modules: SemanticModule | Iterable[SemanticModule],
    *,
    available_modules: Iterable[SemanticModule] | None = None,
) -> list[SemanticModule]:
    source_modules = _module_list(modules)
    known_modules = _module_list(available_modules) if available_modules is not None else source_modules
    known_classes = {
        (module.name, cls.name) for module in known_modules for cls in module.classes if isinstance(cls, SemanticClass)
    }
    dependencies: dict[str, dict[str, str | None]] = {}
    for module in source_modules:
        for semantic_type in _iter_module_semantic_types(module):
            ref = semantic_type.metadata.get(EXTERNAL_TYPE_REF_METADATA)
            if not isinstance(ref, dict) or ref.get("representation") != "opaque":
                continue
            origin_module = ref.get("origin_module")
            type_name = ref.get("name")
            if not isinstance(origin_module, str) or not isinstance(type_name, str):
                continue
            if (origin_module, type_name) in known_classes:
                continue
            c_kind = semantic_type.metadata.get("c_kind")
            dependencies.setdefault(origin_module, {}).setdefault(
                type_name,
                c_kind if c_kind in {"struct", "union"} else None,
            )
    return [
        SemanticModule(
            name=module_name,
            classes=[_opaque_dependency_class(type_name, c_kind) for type_name, c_kind in sorted(type_kinds.items())],
        )
        for module_name, type_kinds in sorted(dependencies.items())
    ]


def _opaque_dependency_class(type_name: str, c_kind: str | None) -> SemanticClass:
    base_classes: list[str] = []
    metadata: dict[str, object] = {"representation": "opaque"}
    if c_kind == "struct":
        base_classes.append("CStruct")
        metadata["c_kind"] = "struct"
    elif c_kind == "union":
        base_classes.append("CUnion")
        metadata["c_kind"] = "union"
    base_classes.append("Opaque")
    return SemanticClass(
        name=type_name,
        native_name=type_name,
        base_classes=base_classes,
        metadata=metadata,
    )


def emit_module_stubs(
    modules: SemanticModule | Iterable[SemanticModule],
    *,
    available_modules: Iterable[SemanticModule] | None = None,
) -> dict[str, str]:
    source_modules = _module_list(modules)
    emitted_modules: dict[str, SemanticModule] = {}
    for module in source_modules:
        if module.name in emitted_modules:
            raise ValueError(f"Cannot emit duplicate semantic module '{module.name}'")
        emitted_modules[module.name] = deepcopy(module)

    for dependency in opaque_dependency_modules(
        source_modules,
        available_modules=available_modules,
    ):
        target = emitted_modules.setdefault(dependency.name, SemanticModule(name=dependency.name))
        existing = {cls.name for cls in target.classes}
        target.classes.extend(cls for cls in dependency.classes if cls.name not in existing)

    return {module_name: emit_module(module).strip() for module_name, module in emitted_modules.items()}


def _module_list(modules: SemanticModule | Iterable[SemanticModule] | None) -> list[SemanticModule]:
    if modules is None:
        return []
    if isinstance(modules, SemanticModule):
        return [modules]
    return list(modules)


if __name__ == "__main__":
    pass
