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
        if getattr(arg, "visibility", "public") == "private":
            s += "  # private"

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

        decorator = "@private\n" if getattr(func, "visibility", "public") == "private" else ""
        return f'''
{decorator}def {func.name}(
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

        decorator = "    @private\n" if getattr(method, "visibility", "public") == "private" else ""
        return f'''
{decorator}    def {method.name}(
        {arg_text}
    ) -> {ret}: ...
'''.rstrip()

    def emit_class(self, cls: SemanticClass) -> str:
        bases = ""

        if cls.base_classes:
            bases = "(" + ", ".join(cls.base_classes) + ")"

        fields = "\n".join(
            f"    {self.emit_argument(field)}"
            for field in cls.fields
        )

        methods = "\n\n".join(
            self.emit_method(m)
            for m in cls.methods
        )

        body_parts = []
        if fields:
            body_parts.append(fields)
        if methods:
            body_parts.append(methods)

        body = "\n\n".join(body_parts)
        if not body:
            body = "    pass"

        decorator = "@private\n" if getattr(cls, "visibility", "public") == "private" else ""
        return f'''
{decorator}class {cls.name}{bases}:
{body}
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

        for var in module.variables:
            sections.append(self.emit_argument(var))
            sections.append("")

        for func in module.functions:
            sections.append(self.emit_function(func))
            sections.append("")

        return "\n".join(sections)


_DEFAULT_PRINTER = PyiPrinter()


def emit_module(module: SemanticModule) -> str:
    return _DEFAULT_PRINTER.emit_module(module)


if __name__ == "__main__":
    pass
