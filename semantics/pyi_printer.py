from __future__ import annotations

import keyword
import re

from .models import (
    SemanticArgument,
    SemanticClass,
    SemanticConstraint,
    SemanticFunction,
    SemanticImport,
    SemanticImportItem,
    SemanticMethod,
    SemanticModule,
    SemanticType,
    ProjectionMapping,
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

    def emit_constraint(self, constraint: SemanticConstraint) -> str:
        if not constraint.arguments:
            return constraint.name
        args = ", ".join(map(repr, constraint.arguments))
        return f"{constraint.name}({args})"

    def emit_semantic_type(self, semantic_type: SemanticType) -> str:
        if semantic_type.name == "Unknown" or semantic_type.dtype == "Unknown":
            raise ValueError("Cannot emit .pyi with unresolved semantic type 'Unknown'")
        text = semantic_type.name
        annotations = [self.emit_constraint(c) for c in semantic_type.constraints]
        if annotations:
            text += "[" + ", ".join(annotations) + "]"
        return text

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
        if original_name is not None:
            type_text = f'Annotated[{type_text}, Name("{original_name}")]'
        if self._is_constant(arg.semantic_type):
            type_text = f"Final[{type_text}]"
        if getattr(arg, "visibility", "public") == "private":
            type_text = f"private[{type_text}]"

        text = f"{name}: {type_text}"
        if arg.optional:
            text += " = ..."
        return text

    @staticmethod
    def _is_constant(semantic_type: SemanticType) -> bool:
        return any(constraint.name == "Constant" for constraint in semantic_type.constraints)

    @staticmethod
    def _without_constant_constraint(semantic_type: SemanticType) -> SemanticType:
        if not PyiPrinter._is_constant(semantic_type):
            return semantic_type
        return SemanticType(
            name=semantic_type.name,
            rank=semantic_type.rank,
            dtype=semantic_type.dtype,
            shape=list(semantic_type.shape),
            constraints=[
                constraint
                for constraint in semantic_type.constraints
                if constraint.name != "Constant"
            ],
            coercions=list(semantic_type.coercions),
            ownership=semantic_type.ownership,
            metadata=dict(semantic_type.metadata),
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

    def emit_module(self, module: SemanticModule) -> str:
        sections: list[str] = []
        self._append_imports(sections, module)
        self._append_items(sections, module.classes, self.emit_class)
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
        return (
            f"{decorator}{def_indent}def {name}(\n"
            f"{parameter_indent}{args}\n"
            f"{def_indent}) -> {return_type}: ..."
        )

    def _class_body(self, cls: SemanticClass) -> str:
        body_parts = []

        fields = "\n".join(f"    {self.emit_data_member(field)}" for field in cls.fields)
        if fields:
            body_parts.append(fields)

        methods = "\n\n".join(self.emit_method(method) for method in cls.methods)
        if methods:
            body_parts.append(methods)

        if not body_parts:
            return "    pass"
        return "\n\n".join(body_parts)

    def _append_imports(self, sections: list[str], module: SemanticModule) -> None:
        for imp in module.imports:
            sections.append(self._emit_import(imp))
        if module.imports:
            sections.append("")

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
        returns = []
        if func.return_type:
            returns.append(self.emit_semantic_type(func.return_type))

        returned_args = [
            arg
            for arg in func.arguments
            if getattr(arg, "intent", "in") in {"out", "inout"}
        ]
        returns.extend(
            self._projected_argument_return(arg)
            for arg in returned_args
        )

        if not returns:
            return "None"
        if len(returns) == 1:
            return returns[0]
        return "tuple[" + ", ".join(returns) + "]"

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
            for mapping in sorted(projection, key=lambda item: item.native_position if item.native_position is not None else -1)
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
            return f"Shape({PyiPrinter._native_value_ref(mapping.value['value'])}, {mapping.value['dim']})"
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
        return [
            arg
            for arg in func.arguments
            if getattr(arg, "intent", "in") != "out"
        ]

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


if __name__ == "__main__":
    pass
