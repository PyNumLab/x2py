# -*- coding: utf-8 -*-
"""Read wrapper-facing facts from user-provided `.pyi` files.

This module is intentionally narrower than the semantic `.pyi` parser. It is
used by wrap-readiness to answer one question: did the user provide enough
interface facts to clear parser-side blockers for imported types, constants,
and callback arguments?
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class PyiReadinessFunction:
    name: str
    arguments: dict[str, str] = field(default_factory=dict)
    return_annotation: str | None = None
    filename: str | None = None


@dataclass
class PyiReadinessContext:
    files: list[str] = field(default_factory=list)
    types: set[str] = field(default_factory=set)
    constants: dict[str, str] = field(default_factory=dict)
    functions: dict[str, PyiReadinessFunction] = field(default_factory=dict)
    callback_arguments: set[tuple[str, str]] = field(default_factory=set)

    def has_type(self, name: str | None) -> bool:
        if not name:
            return False
        return _canonical_type_name(name) in {item.lower() for item in self.types}

    def has_constant(self, name: str | None) -> bool:
        return bool(name) and name.lower() in self.constants

    def has_callback_argument(self, procedure: str | None, argument: str | None) -> bool:
        return bool(procedure and argument) and (procedure.lower(), argument.lower()) in self.callback_arguments

    def to_dict(self) -> dict:
        return {
            "files": list(self.files),
            "provided_types": sorted(self.types, key=str.lower),
            "provided_constants": dict(sorted(self.constants.items())),
            "provided_callbacks": [
                {"procedure": procedure, "argument": argument}
                for procedure, argument in sorted(self.callback_arguments)
            ],
        }


def load_pyi_readiness_context(paths: list[str | Path] | tuple[str | Path, ...] | None) -> PyiReadinessContext:
    context = PyiReadinessContext()
    for raw_path in paths or []:
        path = Path(raw_path)
        _merge_context(context, parse_pyi_readiness_text(path.read_text(encoding="utf-8"), filename=str(path)))
    return context


def parse_pyi_readiness_text(source: str, *, filename: str = "<pyi>") -> PyiReadinessContext:
    tree = ast.parse(source, filename=filename)
    visitor = _PyiReadinessVisitor(filename)
    visitor.visit(tree)
    return visitor.context


def _merge_context(target: PyiReadinessContext, source: PyiReadinessContext) -> None:
    target.files.extend(source.files)
    target.types.update(source.types)
    target.constants.update(source.constants)
    target.functions.update(source.functions)
    target.callback_arguments.update(source.callback_arguments)


def _canonical_type_name(name: str) -> str:
    text = name.strip()
    if "(" in text:
        text = text.split("(", 1)[0].strip()
    return text.lower()


def _annotation_text(node: ast.AST | None) -> str | None:
    if node is None:
        return None
    return ast.unparse(node)


def _qualified_tail(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _is_subscript_of(node: ast.AST | None, name: str) -> bool:
    return (
        isinstance(node, ast.Subscript)
        and (_qualified_tail(node.value) or "").lower() == name.lower()
    )


def _is_callable_annotation(node: ast.AST | None) -> bool:
    return _is_subscript_of(node, "Callable")


def _is_final_annotation(node: ast.AST | None) -> bool:
    return _is_subscript_of(node, "Final")


def _literal_value(node: ast.AST | None) -> str | None:
    if node is None:
        return None
    try:
        value = ast.literal_eval(node)
    except (ValueError, TypeError):
        return None
    if isinstance(value, bool):
        return ".true." if value else ".false."
    if isinstance(value, (int, float, str)):
        return str(value)
    return None


class _PyiReadinessVisitor(ast.NodeVisitor):
    def __init__(self, filename: str):
        self.filename = filename
        self.context = PyiReadinessContext(files=[filename])

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.context.types.add(node.name)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if not isinstance(node.target, ast.Name):
            return
        if not _is_final_annotation(node.annotation):
            return
        value = _literal_value(node.value)
        if value is None:
            return
        self.context.constants[node.target.id.lower()] = value

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        arguments: dict[str, str] = {}
        for arg in node.args.args:
            annotation = _annotation_text(arg.annotation)
            if annotation is None:
                continue
            arguments[arg.arg] = annotation
            if _is_callable_annotation(arg.annotation):
                self.context.callback_arguments.add((node.name.lower(), arg.arg.lower()))
        self.context.functions[node.name.lower()] = PyiReadinessFunction(
            name=node.name,
            arguments=arguments,
            return_annotation=_annotation_text(node.returns),
            filename=self.filename,
        )

