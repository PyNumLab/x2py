from __future__ import annotations

from .models import *


class PyiPrinter:
    """Emit Python stub text from semantic IR models.

    The printer centralizes formatting behavior in one object while the
    historical module-level functions delegate to a shared default instance.
    """

    def emit_semantic_type(self, t: SemanticType) -> str:
        s = t.name
        annotations = []

        for c in t.constraints:
            if c.arguments:
                args = ", ".join(map(repr, c.arguments))
                annotations.append(f"{c.name}({args})")
            else:
                annotations.append(c.name)

        if annotations:
            s += "[" + ", ".join(annotations) + "]"

        return s

    def emit_argument(self, arg: SemanticArgument) -> str:
        s = f"{arg.name}: {self.emit_semantic_type(arg.semantic_type)}"

        if arg.optional:
            s += " = ..."

        return s

    def emit_function(self, func: SemanticFunction) -> str:
        args = ",\n    ".join(
            self.emit_argument(a)
            for a in func.arguments
        )

        if func.return_type:
            ret = self.emit_semantic_type(func.return_type)
        else:
            ret = "None"

        return f'''
def {func.name}(
    {args}
) -> {ret}: ...
'''.strip()

    def emit_method(self, method: SemanticMethod) -> str:
        args = ["self"]
        args.extend(
            self.emit_argument(a)
            for a in method.arguments
        )

        arg_text = ",\n        ".join(args)

        if method.return_type:
            ret = self.emit_semantic_type(method.return_type)
        else:
            ret = "None"

        return f'''
    def {method.name}(
        {arg_text}
    ) -> {ret}: ...
'''.rstrip()

    def emit_class(self, cls: SemanticClass) -> str:
        bases = ""

        if cls.base_classes:
            bases = "(" + ", ".join(cls.base_classes) + ")"

        methods = "\n\n".join(
            self.emit_method(m)
            for m in cls.methods
        )

        if not methods:
            methods = "    pass"

        return f'''
class {cls.name}{bases}:
{methods}
'''.strip()

    def emit_module(self, module: SemanticModule) -> str:
        sections = []

        for imp in module.imports:
            sections.append(f"import {imp}")

        if module.imports:
            sections.append("")

        for cls in module.classes:
            sections.append(self.emit_class(cls))
            sections.append("")

        for func in module.functions:
            sections.append(self.emit_function(func))
            sections.append("")

        return "\n".join(sections)


_DEFAULT_PRINTER = PyiPrinter()


def emit_semantic_type(t: SemanticType) -> str:
    return _DEFAULT_PRINTER.emit_semantic_type(t)


def emit_argument(arg: SemanticArgument) -> str:
    return _DEFAULT_PRINTER.emit_argument(arg)


def emit_function(func: SemanticFunction) -> str:
    return _DEFAULT_PRINTER.emit_function(func)


def emit_method(method: SemanticMethod) -> str:
    return _DEFAULT_PRINTER.emit_method(method)


def emit_class(cls: SemanticClass) -> str:
    return _DEFAULT_PRINTER.emit_class(cls)


def emit_module(module: SemanticModule) -> str:
    return _DEFAULT_PRINTER.emit_module(module)


if __name__ == "__main__":
    pass
