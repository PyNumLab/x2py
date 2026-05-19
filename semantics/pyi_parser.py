from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

from .models import (
    ProjectionMapping,
    SemanticArgument,
    SemanticClass,
    SemanticConstraint,
    SemanticFunction,
    SemanticImport,
    SemanticImportItem,
    SemanticMethod,
    SemanticModule,
    SemanticType,
)

__all__ = ("convert_pyi_to_ir", "load_pyi_file", "parse_pyi_text")


def load_pyi_file(path: str | Path, *, module_name: str | None = None, encoding: str = "utf-8") -> SemanticModule:
    pyi_path = Path(path)
    return parse_pyi_text(
        pyi_path.read_text(encoding=encoding),
        module_name=module_name or pyi_path.stem,
        filename=str(pyi_path),
    )


def convert_pyi_to_ir(source: str, *, module_name: str = "<pyi>") -> SemanticModule:
    return parse_pyi_text(source, module_name=module_name)


def parse_pyi_text(source: str, *, module_name: str = "<pyi>", filename: str = "<pyi>") -> SemanticModule:
    tree = ast.parse(source or "\n", filename=filename)
    return _PyiAstParser(module_name=module_name).parse(tree)


@dataclass
class _Decorators:
    visibility: str = "public"
    projection: list[ProjectionMapping] = field(default_factory=list)
    has_native_call: bool = False


class _PyiAstParser:
    def __init__(self, *, module_name: str):
        self.module = SemanticModule(name=module_name)

    def parse(self, tree: ast.Module) -> SemanticModule:
        _ModuleVisitor(self).visit(tree)
        return self.module

    def import_from(self, node: ast.ImportFrom) -> SemanticImport:
        module_name = "." * node.level + (node.module or "")
        return SemanticImport(
            module=module_name,
            items=[SemanticImportItem(source=alias.name, target=alias.asname) for alias in node.names],
        )

    def import_name(self, node: ast.Import) -> str:
        return ", ".join(
            f"{alias.name} as {alias.asname}" if alias.asname else alias.name
            for alias in node.names
        )

    def class_def(self, node: ast.ClassDef, *, visibility: str) -> SemanticClass:
        body = _ClassBodyVisitor(self)
        body.visit_body(node.body)

        return SemanticClass(
            name=node.name,
            native_name=node.name,
            fields=body.fields,
            methods=body.methods,
            base_classes=[ast.unparse(base) for base in node.bases],
            visibility=visibility,
        )

    def function_def(
        self,
        node: ast.FunctionDef,
        *,
        visibility: str,
        projection: list[ProjectionMapping] | None = None,
    ) -> SemanticFunction:
        semantic_args, return_type = self._callable_parts(node, projection=projection or [])
        return SemanticFunction(
            name=node.name,
            native_name=node.name,
            arguments=semantic_args,
            return_type=return_type,
            projection=projection or [],
            visibility=visibility,
        )

    def method_def(
        self,
        node: ast.FunctionDef,
        *,
        visibility: str,
        projection: list[ProjectionMapping] | None = None,
    ) -> SemanticMethod:
        semantic_args, return_type = self._callable_parts(
            node,
            projection=projection or [],
            drop_untyped_self=True,
        )
        return SemanticMethod(
            name=node.name,
            native_name=node.name,
            arguments=semantic_args,
            return_type=return_type,
            projection=projection or [],
            visibility=visibility,
        )

    def ann_assign(self, node: ast.AnnAssign, *, default_intent: str) -> SemanticArgument:
        name = self.annotation_target(node.target)
        visibility, semantic_type, original_name = self.visible_type(node.annotation)
        if original_name is not None:
            name = original_name
        semantic_type.ownership.mutable = default_intent.lower() != "in"
        return SemanticArgument(
            name=name,
            semantic_type=semantic_type,
            intent=default_intent,
            optional=self.default_marks_optional(node.value),
            visibility=visibility,
        )

    def decorators(self, nodes: list[ast.expr], *, context: str) -> _Decorators:
        parsed = _Decorators()
        for node in nodes:
            if self.matches_name(node, "private"):
                parsed.visibility = "private"
                continue
            if isinstance(node, ast.Call) and self.matches_name(node.func, "native_call"):
                parsed.has_native_call = True
                parsed.projection = self.native_call(node)
                continue
            raise ValueError(f"Unsupported {context} decorator: {ast.unparse(node)!r}")
        return parsed

    def native_call(self, node: ast.Call) -> list[ProjectionMapping]:
        if len(node.args) != 1 or node.keywords:
            raise ValueError("native_call expects a single list argument")
        entries = node.args[0]
        if not isinstance(entries, ast.List):
            raise ValueError("native_call expects a list of projection entries")
        return [
            self.native_projection_entry(entry, native_position)
            for native_position, entry in enumerate(entries.elts)
        ]

    def native_projection_entry(self, node: ast.AST, native_position: int) -> ProjectionMapping:
        if not isinstance(node, ast.Call):
            raise ValueError("native_call expects projection entry calls")
        if node.keywords:
            raise ValueError(f"{self.required_name(node.func)} expects positional arguments only")

        helper = self.required_name(node.func)
        if helper == "Arg":
            if len(node.args) != 1:
                raise ValueError("Arg expects one positional index")
            return ProjectionMapping(
                native_position=native_position,
                python_position=int(ast.literal_eval(node.args[0])),
            )
        if helper == "Return":
            if len(node.args) != 1:
                raise ValueError("Return expects one positional index")
            return ProjectionMapping(
                native_position=native_position,
                result_position=int(ast.literal_eval(node.args[0])),
                intent="out",
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
        if helper == "Shape":
            if len(node.args) != 2:
                raise ValueError("Shape expects a value reference and dimension")
            return ProjectionMapping(
                native_position=native_position,
                value_kind="shape",
                value={"value": self.native_value_ref(node.args[0]), "dim": int(ast.literal_eval(node.args[1]))},
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
        if not self.is_subscript_of(node, "Annotated"):
            return self.semantic_type(node), None

        items = self.subscript_items(node)
        if not items:
            raise ValueError(f"Annotated type is empty: {ast.unparse(node)!r}")

        original_name = None
        for item in items[1:]:
            parsed_name = self.name_metadata(item)
            if parsed_name is not None:
                original_name = parsed_name
        return self.semantic_type(items[0]), original_name

    def semantic_type(self, node: ast.expr) -> SemanticType:
        if self.is_subscript_of(node, "Annotated"):
            semantic_type, _ = self.semantic_type_annotation(node)
            return semantic_type
        if self.is_subscript_of(node, "Final"):
            items = self.subscript_items(node)
            if len(items) != 1:
                raise ValueError(f"Final expects exactly one type: {ast.unparse(node)!r}")
            semantic_type = self.semantic_type(items[0])
            if not any(constraint.name == "Constant" for constraint in semantic_type.constraints):
                semantic_type.constraints.append(SemanticConstraint("Constant"))
            return semantic_type

        name = self.type_name(node)
        if not isinstance(node, ast.Subscript):
            return SemanticType(name=name, dtype=name)

        constraints = [self.constraint(item) for item in self.subscript_items(node)]
        shape = []
        for constraint in constraints:
            if constraint.name == "Shape":
                shape = [str(arg) for arg in constraint.arguments]
                break
        return SemanticType(
            name=name,
            rank=len(shape),
            dtype=name,
            shape=shape,
            constraints=constraints,
        )

    def constraint(self, node: ast.expr) -> SemanticConstraint:
        if isinstance(node, ast.Name):
            return SemanticConstraint(node.id)
        if isinstance(node, ast.Call):
            return SemanticConstraint(
                name=self.required_name(node.func),
                arguments=[ast.literal_eval(arg) for arg in node.args],
            )
        raise ValueError(f"Unsupported semantic type constraint: {ast.unparse(node)!r}")

    def return_projection(self, node: ast.expr) -> tuple[SemanticType | None, list[SemanticArgument]]:
        if isinstance(node, ast.Constant) and node.value is None:
            return None, []

        return_type: SemanticType | None = None
        returned_args: list[SemanticArgument] = []
        plain_return_index = 0

        for item_index, item in enumerate(self.return_items(node)):
            returned = self.returned_argument(item)
            if returned is not None:
                returned.metadata["return_position"] = item_index
                returned_args.append(returned)
                continue

            semantic_type = self.semantic_type(item)
            if item_index == 0:
                return_type = semantic_type
            else:
                returned_args.append(
                    SemanticArgument(
                        name=f"__return_{plain_return_index}",
                        semantic_type=semantic_type,
                        intent="out",
                        metadata={"return_position": item_index},
                    )
                )
            plain_return_index += 1

        return return_type, returned_args

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

        args = list(zip(node.args.args, self._argument_defaults(node)))
        if drop_untyped_self and args and args[0][0].arg == "self" and args[0][0].annotation is None:
            args = args[1:]

        semantic_args = [self._callable_argument(arg, default) for arg, default in args]
        return_type, returned_args = self.return_projection(node.returns)
        return_type, returned_args = self._apply_native_call_returns(return_type, returned_args, projection)
        return_positions = self._return_positions_by_name(returned_args)
        self._apply_projected_returns(semantic_args, returned_args)
        self._apply_native_call_argument_names(semantic_args, return_positions, projection)
        return semantic_args, return_type

    def _callable_argument(self, arg: ast.arg, default: ast.expr | None) -> SemanticArgument:
        if arg.annotation is None:
            raise ValueError(f"Expected typed argument: {arg.arg!r}")
        visibility, semantic_type, original_name = self.visible_type(arg.annotation)
        semantic_type.ownership.mutable = False
        return SemanticArgument(
            name=original_name or arg.arg,
            semantic_type=semantic_type,
            intent="in",
            optional=self.default_marks_optional(default),
            visibility=visibility,
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
        if not (
            isinstance(body, ast.Expr)
            and isinstance(body.value, ast.Constant)
            and body.value.value is Ellipsis
        ):
            raise ValueError(f"Unsupported function header: {_node_text(node)!r}")

    @staticmethod
    def _apply_projected_returns(semantic_args: list[SemanticArgument], returned_args: list[SemanticArgument]) -> None:
        by_name = {arg.name: arg for arg in semantic_args}
        for returned in returned_args:
            existing = by_name.get(returned.name)
            if existing is None:
                returned.intent = "out"
                returned.semantic_type.ownership.mutable = True
                returned.metadata.pop("return_position", None)
                semantic_args.append(returned)
                continue
            existing.intent = "inout"
            existing.semantic_type.ownership.mutable = True

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
            return_type.ownership.mutable = True
            returned_args.insert(
                0,
                SemanticArgument(
                    name=mapping.native_name or f"__return_{mapping.result_position}",
                    semantic_type=return_type,
                    intent=mapping.intent,
                ),
            )
            return_type = None

        for returned in returned_args:
            position = returned.metadata.get("return_position")
            mapping = output_by_result.get(position)
            if mapping is not None:
                if mapping.native_name:
                    returned.name = mapping.native_name
                returned.intent = mapping.intent
                returned.semantic_type.ownership.mutable = True
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
            mapping.python_name = arg.name
            if not mapping.native_name:
                mapping.native_name = arg.name
            mapping.intent = arg.intent
            if arg.intent == "inout" and mapping.result_position is None:
                mapping.result_position = return_positions.get(arg.name)

    def return_items(self, node: ast.expr) -> list[ast.expr]:
        if self.is_subscript_of(node, "tuple") or self.is_subscript_of(node, "Tuple"):
            return self.subscript_items(node)
        return [node]


class _ClassBodyVisitor(ast.NodeVisitor):
    def __init__(self, parser: _PyiAstParser):
        self.parser = parser
        self.fields: list[SemanticArgument] = []
        self.methods: list[SemanticMethod] = []

    def visit_body(self, nodes: list[ast.stmt]) -> None:
        for node in nodes:
            self.visit(node)

    def visit_Pass(self, node: ast.Pass) -> None:
        return None

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self.fields.append(self.parser.ann_assign(node, default_intent="in"))

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        decorators = self.parser.decorators(node.decorator_list, context="class body")
        self.methods.append(
            self.parser.method_def(
                node,
                visibility=decorators.visibility,
                projection=decorators.projection,
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
        self.parser.module.imports.append(self.parser.import_from(node))

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self.parser.module.variables.append(self.parser.ann_assign(node, default_intent="in"))

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        decorators = self.parser.decorators(node.decorator_list, context="class")
        if decorators.has_native_call:
            raise ValueError(f"Unsupported class decorator: {ast.unparse(node.decorator_list[-1])!r}")
        self.parser.module.classes.append(self.parser.class_def(node, visibility=decorators.visibility))

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        decorators = self.parser.decorators(node.decorator_list, context=".pyi")
        self.parser.module.functions.append(
            self.parser.function_def(
                node,
                visibility=decorators.visibility,
                projection=decorators.projection,
            )
        )

    def generic_visit(self, node: ast.AST) -> None:
        raise ValueError(f"Unsupported .pyi node: {_node_text(node)!r}")


def _node_text(node: ast.AST) -> str:
    text = ast.unparse(node)
    return text.splitlines()[0] if text else type(node).__name__
