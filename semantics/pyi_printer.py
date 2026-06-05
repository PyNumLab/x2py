from __future__ import annotations

import ast
from collections.abc import Iterable
from copy import deepcopy
import json
import keyword
import re

from .models import (
    EXTERNAL_TYPE_REF_METADATA,
    ProjectionMapping,
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
        annotations = [self.emit_constraint(constraint) for constraint in semantic_type.constraints]
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

    def emit_data_member(self, arg: SemanticArgument) -> str:
        return self._emit_typed_name(self._annotation_target(arg.name), arg)

    def _emit_typed_name(
        self,
        name: str,
        arg: SemanticArgument,
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
        elif self._is_enum_constant(arg):
            enum_value = self._enum_default_value(arg)
            if enum_value is not None:
                text += f" = {enum_value}"
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
    def _is_enum_constant(arg: SemanticArgument) -> bool:
        return PyiPrinter._is_constant(arg.semantic_type) and bool(
            arg.semantic_type.metadata.get("semantic_enum") or arg.semantic_type.metadata.get("c_enum")
        )

    @staticmethod
    def _enum_default_value(arg: SemanticArgument) -> str | None:
        pyi_value = arg.metadata.get("pyi_default_value")
        if isinstance(pyi_value, str):
            return pyi_value
        if arg.origin.source_language == "c":
            return None
        return arg.default_value

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
        return self._emit_callable(
            name=method.name,
            arguments=[
                "self",
                *[self.emit_argument(arg) for arg in self._method_call_arguments(method)],
            ],
            return_type=return_type,
            decorator=decorator,
            def_indent="    ",
            parameter_indent="        ",
        ).rstrip()

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
        self._append_items(sections, module.variables, self.emit_data_member)
        self._append_items(sections, module.functions, self.emit_function)
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

        fields = "\n".join(f"    {self.emit_data_member(field)}" for field in cls.fields)
        if fields:
            body_parts.append(fields)

        methods = "\n\n".join(self.emit_method(method) for method in cls.methods)
        if methods:
            body_parts.append(methods)

        if not body_parts:
            return "    pass"
        return "\n\n".join(body_parts)

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
        if func.return_type:
            return self.emit_semantic_type(func.return_type)
        return "None"

    def _projected_argument_return(self, arg: SemanticArgument) -> str:
        if self._requires_named_return(arg):
            return self._named_return(arg)
        return self.emit_semantic_type(arg.semantic_type)

    def _requires_named_return(self, arg: SemanticArgument) -> bool:
        return getattr(arg, "intent", "in") == "inout"

    def _named_return(self, arg: SemanticArgument) -> str:
        optional = ", Optional" if arg.optional else ""
        return f'Returns["{arg.name}", {self.emit_semantic_type(arg.semantic_type)}{optional}]'

    def _decorators(self, func: SemanticFunction, *, indent: str = "") -> str:
        decorators = []
        if self._is_private(func):
            decorators.append(f"{indent}@private")
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
            return mapping.python_position != mapping.native_position
        if mapping.intent != "in":
            return mapping.python_position is None
        if mapping.result_position is not None:
            return True
        if mapping.python_position is None:
            return True
        return mapping.native_position is not None and mapping.python_position != mapping.native_position

    @staticmethod
    def _call_arguments(func: SemanticFunction) -> list[SemanticArgument]:
        return list(func.arguments)

    @staticmethod
    def _requires_intent_metadata(arg: SemanticArgument) -> bool:
        return getattr(arg, "intent", "in") == "out"

    @classmethod
    def _method_call_arguments(cls, method: SemanticMethod) -> list[SemanticArgument]:
        args = cls._call_arguments(method)
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
