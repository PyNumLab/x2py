from __future__ import annotations

import ast
import re
from pathlib import Path

from .models import (
    ProjectionMapping,
    SemanticArgument,
    SemanticClass,
    SemanticConstraint,
    SemanticFunction,
    SemanticMethod,
    SemanticModule,
    SemanticType,
)


def load_pyi_file(path: str | Path, *, module_name: str | None = None, encoding: str = "utf-8") -> SemanticModule:
    pyi_path = Path(path)
    return parse_pyi_text(
        pyi_path.read_text(encoding=encoding),
        module_name=module_name or pyi_path.stem,
    )


def convert_pyi_to_ir(source: str, *, module_name: str = "<pyi>") -> SemanticModule:
    return parse_pyi_text(source, module_name=module_name)


def parse_pyi_text(source: str, *, module_name: str = "<pyi>") -> SemanticModule:
    return PyiToIRParser(module_name=module_name).parse(source)


class PyiToIRParser:
    """Parse the wrapper-oriented `.pyi` dialect emitted by `PyiPrinter`.

    The parser intentionally targets the generated, editable stub format rather
    than the full Python typing grammar. It validates input with Python's AST
    parser and interprets wrapper projection helpers such as `Returns["x", T]`.
    """

    def __init__(self, *, module_name: str):
        self.module_name = module_name
        self.lines: list[str] = []
        self.index = 0

    def parse(self, source: str) -> SemanticModule:
        ast.parse(source or "\n")
        self.lines = source.splitlines()
        self.index = 0
        module = SemanticModule(name=self.module_name)
        pending_visibility = "public"
        pending_projection: list[ProjectionMapping] = []

        while self.index < len(self.lines):
            line = self.lines[self.index]
            stripped = line.strip()
            if not stripped:
                self.index += 1
                continue
            if self._indent(line) != 0:
                raise ValueError(f"Unexpected indented top-level line: {line!r}")
            if stripped == "@private":
                pending_visibility = "private"
                self.index += 1
                continue
            if stripped.startswith("@call_map"):
                pending_projection = self._parse_call_map_decorator(stripped)
                self.index += 1
                continue
            if stripped.startswith("import "):
                module.imports.append(stripped.split(None, 1)[1].strip())
                self.index += 1
                continue
            if stripped.startswith("class "):
                cls, self.index = self._parse_class(self.index, visibility=pending_visibility)
                module.classes.append(cls)
                pending_visibility = "public"
                continue
            if stripped.startswith("def "):
                func, self.index = self._parse_function(
                    self.index,
                    visibility=pending_visibility,
                    projection=pending_projection,
                )
                module.functions.append(func)
                pending_visibility = "public"
                pending_projection = []
                continue
            if ":" in stripped:
                module.variables.append(self._parse_argument_line(stripped, default_intent="in"))
                pending_visibility = "public"
                self.index += 1
                continue
            raise ValueError(f"Unsupported .pyi line: {line!r}")

        return module

    def _parse_class(self, start: int, *, visibility: str) -> tuple[SemanticClass, int]:
        header = self.lines[start].strip()
        match = re.match(r"^class\s+(?P<name>\w+)(?:\((?P<bases>[^)]*)\))?:\s*$", header)
        if not match:
            raise ValueError(f"Unsupported class header: {header!r}")

        fields: list[SemanticArgument] = []
        methods: list[SemanticMethod] = []
        pending_visibility = "public"
        pending_projection: list[ProjectionMapping] = []
        index = start + 1
        while index < len(self.lines):
            line = self.lines[index]
            stripped = line.strip()
            if not stripped:
                index += 1
                continue
            if self._indent(line) == 0:
                break
            if stripped == "pass":
                index += 1
                continue
            if stripped == "@private":
                pending_visibility = "private"
                index += 1
                continue
            if stripped.startswith("@call_map"):
                pending_projection = self._parse_call_map_decorator(stripped)
                index += 1
                continue
            if stripped.startswith("def "):
                method, index = self._parse_method(
                    index,
                    visibility=pending_visibility,
                    projection=pending_projection,
                )
                methods.append(method)
                pending_visibility = "public"
                pending_projection = []
                continue
            if ":" in stripped:
                fields.append(self._parse_argument_line(stripped, default_intent="in"))
                index += 1
                continue
            raise ValueError(f"Unsupported class body line: {line!r}")

        bases = [base.strip() for base in (match.group("bases") or "").split(",") if base.strip()]
        return (
            SemanticClass(
                name=match.group("name"),
                native_name=match.group("name"),
                fields=fields,
                methods=methods,
                base_classes=bases,
                visibility=visibility,
            ),
            index,
        )

    def _parse_function(
        self,
        start: int,
        *,
        visibility: str,
        projection: list[ProjectionMapping] | None = None,
    ) -> tuple[SemanticFunction, int]:
        name, args, return_type, returned_args, index = self._parse_callable(start)
        semantic_args = [self._parse_argument_line(arg, default_intent="in") for arg in args]
        return_type, returned_args = self._apply_call_map_returns(return_type, returned_args, projection or [])
        self._apply_projected_returns(semantic_args, returned_args)
        self._apply_call_map_argument_names(semantic_args, projection or [])
        return (
            SemanticFunction(
                name=name,
                native_name=name,
                arguments=semantic_args,
                return_type=return_type,
                projection=projection or [],
                visibility=visibility,
            ),
            index,
        )

    def _parse_method(
        self,
        start: int,
        *,
        visibility: str,
        projection: list[ProjectionMapping] | None = None,
    ) -> tuple[SemanticMethod, int]:
        name, args, return_type, returned_args, index = self._parse_callable(start)
        args = args[1:] if args and args[0].strip() == "self" else args
        semantic_args = [self._parse_argument_line(arg, default_intent="in") for arg in args]
        return_type, returned_args = self._apply_call_map_returns(return_type, returned_args, projection or [])
        self._apply_projected_returns(semantic_args, returned_args)
        self._apply_call_map_argument_names(semantic_args, projection or [])
        return (
            SemanticMethod(
                name=name,
                native_name=name,
                arguments=semantic_args,
                return_type=return_type,
                projection=projection or [],
                visibility=visibility,
            ),
            index,
        )

    def _parse_callable(self, start: int) -> tuple[str, list[str], SemanticType | None, list[SemanticArgument], int]:
        first = self.lines[start].strip()
        single = re.match(r"^def\s+(?P<name>\w+)\((?P<args>.*)\)\s*->\s*(?P<ret>.+?):\s*\.\.\.\s*$", first)
        if single:
            return_type, returned_args = self._parse_return_projection(single.group("ret"))
            return (
                single.group("name"),
                self._split_argument_text(single.group("args")),
                return_type,
                returned_args,
                start + 1,
            )

        header = re.match(r"^def\s+(?P<name>\w+)\(\s*$", first)
        if not header:
            raise ValueError(f"Unsupported function header: {first!r}")

        args: list[str] = []
        index = start + 1
        while index < len(self.lines):
            stripped = self.lines[index].strip()
            close = re.match(r"^\)\s*->\s*(?P<ret>.+?):\s*\.\.\.\s*$", stripped)
            if close:
                return_type, returned_args = self._parse_return_projection(close.group("ret"))
                return header.group("name"), args, return_type, returned_args, index + 1
            if stripped:
                args.append(stripped.rstrip(","))
            index += 1
        raise ValueError(f"Unterminated callable starting at line {start + 1}")

    def _parse_argument_line(self, text: str, *, default_intent: str) -> SemanticArgument:
        text = text.rstrip(",").rstrip()
        split = self._split_annotation_line(text)
        if split is None:
            raise ValueError(f"Expected typed argument or variable line: {text!r}")

        raw_name, type_text = split
        name = self._parse_annotation_target(raw_name)
        optional = False
        if type_text.endswith("= ..."):
            optional = True
            type_text = type_text[:-5].rstrip()

        visibility, semantic_type, original_name = self._parse_visible_type(type_text)
        if original_name is not None:
            name = original_name
        intent = default_intent
        semantic_type.ownership.mutable = intent.lower() != "in"
        return SemanticArgument(
            name=name,
            semantic_type=semantic_type,
            intent=intent,
            optional=optional,
            visibility=visibility,
        )

    def _apply_projected_returns(
        self,
        semantic_args: list[SemanticArgument],
        returned_args: list[SemanticArgument],
    ) -> None:
        by_name = {arg.name: arg for arg in semantic_args}
        for returned in returned_args:
            existing = by_name.get(returned.name)
            if existing is None:
                returned.intent = "out"
                returned.semantic_type.ownership.mutable = True
                semantic_args.append(returned)
                continue
            existing.intent = "inout"
            existing.semantic_type.ownership.mutable = True

    def _apply_call_map_returns(
        self,
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
                    name=mapping.native_name,
                    semantic_type=return_type,
                    intent=mapping.intent,
                ),
            )
            return_type = None

        for returned in returned_args:
            position = returned.metadata.pop("return_position", None)
            mapping = output_by_result.get(position)
            if mapping is not None:
                returned.name = mapping.native_name
                returned.intent = mapping.intent
                returned.semantic_type.ownership.mutable = True
        return return_type, returned_args

    @staticmethod
    def _apply_call_map_argument_names(
        semantic_args: list[SemanticArgument],
        projection: list[ProjectionMapping],
    ) -> None:
        for mapping in projection:
            if mapping.python_position is None:
                continue
            if not 0 <= mapping.python_position < len(semantic_args):
                raise ValueError(f"call_map argument position is out of range: {mapping.python_position}")
            mapping.python_name = semantic_args[mapping.python_position].name

    def _parse_visible_type(self, type_text: str) -> tuple[str, SemanticType, str | None]:
        if type_text.startswith("private[") and type_text.endswith("]"):
            semantic_type, original_name = self._parse_semantic_type_annotation(type_text[len("private[") : -1])
            return "private", semantic_type, original_name
        semantic_type, original_name = self._parse_semantic_type_annotation(type_text)
        return "public", semantic_type, original_name

    def _parse_semantic_type_annotation(self, type_text: str) -> tuple[SemanticType, str | None]:
        type_text = type_text.strip()
        if type_text.startswith("Annotated[") and type_text.endswith("]"):
            name, inner = self._split_type_subscript(type_text)
            if name == "Annotated":
                items = self._split_top_level(inner)
                if not items:
                    raise ValueError(f"Annotated type is empty: {type_text!r}")
                semantic_type = self._parse_semantic_type(items[0])
                original_name = None
                for item in items[1:]:
                    parsed_name = self._parse_name_metadata(item)
                    if parsed_name is not None:
                        original_name = parsed_name
                return semantic_type, original_name
        return self._parse_semantic_type(type_text), None

    def _parse_semantic_type(self, type_text: str) -> SemanticType:
        type_text = type_text.strip()
        if type_text.startswith("Annotated[") and type_text.endswith("]"):
            semantic_type, _ = self._parse_semantic_type_annotation(type_text)
            return semantic_type
        if "[" not in type_text:
            return SemanticType(name=type_text, dtype=type_text)

        name, inner = self._split_type_subscript(type_text)
        constraints = [self._parse_constraint(token) for token in self._split_top_level(inner)]
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

    def _parse_constraint(self, token: str) -> SemanticConstraint:
        token = token.strip()
        expr = ast.parse(token, mode="eval").body
        if isinstance(expr, ast.Name):
            return SemanticConstraint(expr.id)
        if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name):
            return SemanticConstraint(
                name=expr.func.id,
                arguments=[ast.literal_eval(arg) for arg in expr.args],
            )
        raise ValueError(f"Unsupported semantic type constraint: {token!r}")

    def _parse_call_map_decorator(self, text: str) -> list[ProjectionMapping]:
        expr = ast.parse(text[1:], mode="eval").body
        if not isinstance(expr, ast.Call) or not isinstance(expr.func, ast.Name) or expr.func.id != "call_map":
            raise ValueError(f"Unsupported call map decorator: {text!r}")
        return [self._parse_native_arg_mapping(arg) for arg in expr.args]

    def _parse_native_arg_mapping(self, expr: ast.AST) -> ProjectionMapping:
        if not isinstance(expr, ast.Call) or not isinstance(expr.func, ast.Name) or expr.func.id != "NativeArg":
            raise ValueError("call_map expects NativeArg(...) entries")
        if len(expr.args) != 2:
            raise ValueError("NativeArg expects a native name and native position")
        native_name = str(ast.literal_eval(expr.args[0]))
        native_position = int(ast.literal_eval(expr.args[1]))
        keywords = {kw.arg: ast.literal_eval(kw.value) for kw in expr.keywords if kw.arg is not None}
        source = str(keywords.get("source", "arg"))
        position = keywords.get("position")
        result = keywords.get("result")
        return ProjectionMapping(
            native_name=native_name,
            native_position=native_position,
            python_position=int(position) if source == "arg" and position is not None else None,
            result_position=int(result if result is not None else position) if source == "return" and position is not None else (
                int(result) if result is not None else None
            ),
            intent=str(keywords.get("intent", "in")),
        )

    def _parse_return_projection(self, text: str) -> tuple[SemanticType | None, list[SemanticArgument]]:
        text = text.strip()
        if text == "None":
            return None, []
        return_type: SemanticType | None = None
        returned_args: list[SemanticArgument] = []
        plain_return_index = 0
        for item_index, item in enumerate(self._return_items(text)):
            returned = self._parse_returned_argument(item)
            if returned is not None:
                returned.metadata["return_position"] = item_index
                returned_args.append(returned)
            else:
                semantic_type = self._parse_semantic_type(item)
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

    def _return_items(self, text: str) -> list[str]:
        if text.startswith("tuple[") and text.endswith("]"):
            _, inner = self._split_type_subscript(text)
            return self._split_top_level(inner)
        return [text]

    def _parse_returned_argument(self, text: str) -> SemanticArgument | None:
        if not text.startswith("Returns["):
            return None
        name, inner = self._split_type_subscript(text)
        if name != "Returns":
            return None
        items = self._split_top_level(inner)
        if len(items) not in {2, 3}:
            raise ValueError(f"Returns expects a name and type: {text!r}")
        arg_name = ast.literal_eval(items[0])
        semantic_type = self._parse_semantic_type(items[1])
        semantic_type.ownership.mutable = True
        return SemanticArgument(
            name=str(arg_name),
            semantic_type=semantic_type,
            intent="out",
            optional=len(items) == 3 and items[2] == "Optional",
        )

    def _parse_name_metadata(self, text: str) -> str | None:
        expr = ast.parse(text, mode="eval").body
        if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name) and expr.func.id == "Name":
            if len(expr.args) != 1:
                raise ValueError(f"Name metadata expects one argument: {text!r}")
            return str(ast.literal_eval(expr.args[0]))
        return None

    def _split_argument_text(self, text: str) -> list[str]:
        if not text.strip():
            return []
        return self._split_top_level(text)

    def _split_type_subscript(self, text: str) -> tuple[str, str]:
        start = text.find("[")
        if start < 0 or not text.endswith("]"):
            raise ValueError(f"Unsupported type annotation: {text!r}")
        return text[:start].strip(), text[start + 1 : -1].strip()

    def _split_annotation_line(self, text: str) -> tuple[str, str] | None:
        depth = 0
        quote: str | None = None
        for i, char in enumerate(text):
            if quote:
                if char == quote:
                    quote = None
                continue
            if char in {"'", '"'}:
                quote = char
                continue
            if char in "([{":
                depth += 1
                continue
            if char in ")]}":
                depth -= 1
                continue
            if char == ":" and depth == 0:
                return text[:i].strip(), text[i + 1 :].strip()
        return None

    def _parse_annotation_target(self, text: str) -> str:
        if re.match(r"^[A-Za-z_]\w*$", text):
            return text
        expr = ast.parse(text, mode="eval").body
        if isinstance(expr, ast.Subscript) and isinstance(expr.value, ast.Name) and expr.value.id == "var":
            return str(ast.literal_eval(expr.slice))
        raise ValueError(f"Unsupported annotation target: {text!r}")

    def _split_top_level(self, text: str) -> list[str]:
        items: list[str] = []
        start = 0
        depth = 0
        quote: str | None = None
        for i, char in enumerate(text):
            if quote:
                if char == quote:
                    quote = None
                continue
            if char in {"'", '"'}:
                quote = char
                continue
            if char in "([{":
                depth += 1
                continue
            if char in ")]}":
                depth -= 1
                continue
            if char == "," and depth == 0:
                item = text[start:i].strip()
                if item:
                    items.append(item)
                start = i + 1
        item = text[start:].strip()
        if item:
            items.append(item)
        return items

    @staticmethod
    def _indent(line: str) -> int:
        return len(line) - len(line.lstrip(" "))
