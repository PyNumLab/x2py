from __future__ import annotations

import keyword
import re

from .models import (
    SemanticArgument,
    SemanticClass,
    SemanticConstraint,
    SemanticFunction,
    SemanticMethod,
    SemanticModule,
    SemanticType,
)


class PyiPrinter:
    """Emit Python stub text from semantic IR models.

    The printer is a lightweight visitor. `emit()` dispatches by semantic model
    type, while the `emit_*` methods remain explicit compatibility entrypoints.
    """

    def __init__(self, *, roundtrip: bool = False):
        self.roundtrip = roundtrip

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
        type_text = self.emit_semantic_type(arg.semantic_type)
        if original_name is not None:
            type_text = f'Annotated[{type_text}, Name("{original_name}")]'
        if getattr(arg, "visibility", "public") == "private":
            type_text = f"private[{type_text}]"

        text = f"{name}: {type_text}"
        if arg.optional:
            text += " = ..."
        return text

    def emit_function(self, func: SemanticFunction) -> str:
        return_type = self._projected_return_annotation(func)
        decorator = "@private\n" if self._is_private(func) else ""
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
        decorator = "    @private\n" if self._is_private(method) else ""
        return self._emit_callable(
            name=method.name,
            arguments=["self", *[self.emit_argument(arg) for arg in self._call_arguments(method)]],
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
            sections.append(f"import {imp}")
        if module.imports:
            sections.append("")

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
            self._projected_argument_return(arg, func, returned_args)
            for arg in returned_args
        )

        if not returns:
            return "None"
        if len(returns) == 1:
            return returns[0]
        return "tuple[" + ", ".join(returns) + "]"

    def _projected_argument_return(
        self,
        arg: SemanticArgument,
        func: SemanticFunction,
        returned_args: list[SemanticArgument],
    ) -> str:
        if self._requires_named_return(arg, func, returned_args):
            return self._named_return(arg)
        return self.emit_semantic_type(arg.semantic_type)

    def _requires_named_return(
        self,
        arg: SemanticArgument,
        func: SemanticFunction,
        returned_args: list[SemanticArgument],
    ) -> bool:
        if self.roundtrip:
            return True
        if getattr(arg, "intent", "in") == "inout":
            return True
        if arg.optional:
            return True
        if func.return_type is not None:
            return True
        return len(returned_args) != 1

    def _named_return(self, arg: SemanticArgument) -> str:
        optional = ", Optional" if arg.optional else ""
        return f'Returns["{arg.name}", {self.emit_semantic_type(arg.semantic_type)}{optional}]'

    @staticmethod
    def _call_arguments(func: SemanticFunction) -> list[SemanticArgument]:
        return [
            arg
            for arg in func.arguments
            if getattr(arg, "intent", "in") != "out"
        ]

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
_ROUNDTRIP_PRINTER = PyiPrinter(roundtrip=True)


def emit_module(module: SemanticModule, *, roundtrip: bool = False) -> str:
    printer = _ROUNDTRIP_PRINTER if roundtrip else _DEFAULT_PRINTER
    return printer.emit_module(module)


if __name__ == "__main__":
    pass
