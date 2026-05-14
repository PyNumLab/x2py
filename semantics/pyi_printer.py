from .models import *

def emit_semantic_type(t: SemanticType) -> str:

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

def emit_argument(arg: SemanticArgument) -> str:

    s = f"{arg.name}: {emit_semantic_type(arg.semantic_type)}"

    if arg.optional:
        s += " = ..."

    return s

def emit_function(func: SemanticFunction) -> str:

    args = ",\n    ".join(
        emit_argument(a)
        for a in func.arguments
    )

    if func.return_type:
        ret = emit_semantic_type(func.return_type)
    else:
        ret = "None"

    return f'''
def {func.name}(
    {args}
) -> {ret}: ...
'''.strip()

def emit_method(method: SemanticMethod) -> str:

    args = ["self"]

    args.extend(
        emit_argument(a)
        for a in method.arguments
    )

    arg_text = ",\n        ".join(args)

    if method.return_type:
        ret = emit_semantic_type(method.return_type)
    else:
        ret = "None"

    return f'''
    def {method.name}(
        {arg_text}
    ) -> {ret}: ...
'''.rstrip()


def emit_class(cls: SemanticClass) -> str:

    bases = ""

    if cls.base_classes:
        bases = "(" + ", ".join(cls.base_classes) + ")"

    methods = "\n\n".join(
        emit_method(m)
        for m in cls.methods
    )

    if not methods:
        methods = "    pass"

    return f'''
class {cls.name}{bases}:
{methods}
'''.strip()

def emit_module(module: SemanticModule) -> str:

    sections = []

    for imp in module.imports:
        sections.append(f"import {imp}")

    if module.imports:
        sections.append("")

    for cls in module.classes:
        sections.append(emit_class(cls))
        sections.append("")

    for func in module.functions:
        sections.append(emit_function(func))
        sections.append("")

    return "\n".join(sections)

if __name__ == "__main__":
    pass
