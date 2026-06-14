from __future__ import annotations

import ast
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from .models import (
    EXTERNAL_TYPE_REF_METADATA,
    ProjectionMapping,
    SemanticArgument,
    SemanticArrayContract,
    SemanticClass,
    SemanticConstraint,
    SemanticEnum,
    SemanticEnumerator,
    SemanticField,
    SemanticFunction,
    SemanticImport,
    SemanticImportItem,
    SemanticMethod,
    SemanticModule,
    SemanticStorageContract,
    SemanticType,
    SemanticVariable,
    _iter_module_semantic_types,
)

__all__ = ("convert_pyi_to_ir", "load_pyi_file", "load_pyi_modules", "parse_pyi_text")


def load_pyi_file(path: str | Path, *, module_name: str | None = None, encoding: str = "utf-8") -> SemanticModule:
    pyi_path = Path(path)
    return parse_pyi_text(
        pyi_path.read_text(encoding=encoding),
        module_name=module_name or pyi_path.stem,
        filename=str(pyi_path),
    )


def load_pyi_modules(
    paths: str | Path | Iterable[str | Path],
    *,
    encoding: str = "utf-8",
) -> list[SemanticModule]:
    raw_paths = [paths] if isinstance(paths, str | Path) else list(paths)
    expanded: dict[Path, str | None] = {}
    for raw_path in raw_paths:
        path = Path(raw_path)
        if path.is_dir():
            for item in path.rglob("*.pyi"):
                if not item.is_file():
                    continue
                module_name = ".".join(item.relative_to(path).with_suffix("").parts)
                previous = expanded.get(item)
                if previous is not None and previous != module_name:
                    raise ValueError(f"Ambiguous module name for {item}: {previous!r} or {module_name!r}")
                expanded[item] = module_name
        else:
            expanded.setdefault(path, None)
    return _reconcile_external_type_refs(
        [
            load_pyi_file(path, module_name=module_name, encoding=encoding)
            for path, module_name in sorted(expanded.items())
        ]
    )


def convert_pyi_to_ir(source: str, *, module_name: str = "<pyi>") -> SemanticModule:
    return parse_pyi_text(source, module_name=module_name)


def parse_pyi_text(source: str, *, module_name: str = "<pyi>", filename: str = "<pyi>") -> SemanticModule:
    tree = ast.parse(source or "\n", filename=filename)
    module = _PyiAstParser(module_name=module_name).parse(tree)
    _annotate_imported_external_type_refs(module)
    return module


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
        self._link_enum_constants()
        return self.module

    def import_from(self, node: ast.ImportFrom) -> SemanticImport:
        module_name = "." * node.level + (node.module or "")
        return SemanticImport(
            module=module_name,
            items=[SemanticImportItem(source=alias.name, target=alias.asname) for alias in node.names],
        )

    def import_name(self, node: ast.Import) -> str:
        return ", ".join(f"{alias.name} as {alias.asname}" if alias.asname else alias.name for alias in node.names)

    def class_def(self, node: ast.ClassDef, *, visibility: str) -> SemanticClass:
        body = _ClassBodyVisitor(self)
        body.visit_body(node.body)
        base_classes = [ast.unparse(base) for base in node.bases]

        return SemanticClass(
            name=node.name,
            native_name=node.name,
            fields=body.fields,
            methods=body.methods,
            classes=body.classes,
            base_classes=base_classes,
            metadata=self._class_metadata(base_classes),
            visibility=visibility,
        )

    @staticmethod
    def _class_metadata(base_classes: list[str]) -> dict[str, object]:
        metadata: dict[str, object] = {}
        if "CStruct" in base_classes:
            metadata["c_kind"] = "struct"
        if "CUnion" in base_classes:
            metadata["c_kind"] = "union"
        if "CAnonymous" in base_classes:
            metadata["c_anonymous"] = True
        if "Opaque" in base_classes:
            metadata["representation"] = "opaque"
        return metadata

    def enum_def(self, node: ast.ClassDef, *, visibility: str) -> SemanticEnum:
        if len(node.bases) != 1 or not self.is_subscript_of(node.bases[0], "Enum"):
            raise ValueError(f"Enum declaration expects exactly one underlying type: {_node_text(node)!r}")
        if len(node.body) != 1 or not isinstance(node.body[0], ast.Pass):
            raise ValueError(f"Enum declarations keep enumerators at module scope: {_node_text(node)!r}")
        items = self.subscript_items(node.bases[0])
        if len(items) != 1:
            raise ValueError(f"Enum declaration expects exactly one underlying type: {_node_text(node)!r}")
        return SemanticEnum(
            name=node.name,
            native_name=node.name,
            underlying_type=self.semantic_type(items[0]),
            open=True,
            visibility=visibility,
        )

    def _link_enum_constants(self) -> None:
        by_name = {enum.name: enum for enum in self.module.enums}
        for index, variable in enumerate(list(self.module.variables)):
            enum = by_name.get(variable.semantic_type.name)
            if enum is None or not any(
                constraint.name == "Constant" for constraint in variable.semantic_type.constraints
            ):
                continue
            variable.semantic_type.metadata["semantic_enum"] = enum.name
            enumerator = (
                variable
                if isinstance(variable, SemanticEnumerator)
                else SemanticEnumerator(
                    name=variable.name,
                    semantic_type=variable.semantic_type,
                    visibility=variable.visibility,
                    default_value=variable.default_value,
                    metadata=variable.metadata,
                    origin=variable.origin,
                )
            )
            enum.enumerators.append(enumerator)
            self.module.variables[index] = enumerator

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

    def ann_assign(
        self,
        node: ast.AnnAssign,
        *,
        default_intent: str,
        binding_cls: type[SemanticVariable] = SemanticVariable,
    ) -> SemanticVariable:
        name = self.annotation_target(node.target)
        visibility, semantic_type, original_name = self.visible_type(node.annotation)
        if original_name is not None:
            name = original_name
        intent = self._pop_intent_metadata(semantic_type, default_intent)
        semantic_type.ownership.mutable = intent.lower() != "in"
        if semantic_type.storage is not None:
            semantic_type.storage.mutable = intent.lower() != "in"
        binding = binding_cls(
            name=name,
            semantic_type=semantic_type,
            visibility=visibility,
            default_value=self.assignment_default_value(node.value, semantic_type),
        )
        binding.intent = intent
        binding.optional = self.default_marks_optional(node.value)
        return binding

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
            self.native_projection_entry(entry, native_position) for native_position, entry in enumerate(entries.elts)
        ]

    def native_projection_entry(self, node: ast.AST, native_position: int) -> ProjectionMapping:
        shape_mapping = self.native_shape_projection_entry(node, native_position)
        if shape_mapping is not None:
            return shape_mapping
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

    def native_shape_projection_entry(
        self,
        node: ast.AST,
        native_position: int,
    ) -> ProjectionMapping | None:
        if not isinstance(node, ast.Subscript) or not isinstance(node.value, ast.Attribute):
            return None
        attribute = node.value.attr
        if attribute != "shape":
            return None
        return ProjectionMapping(
            native_position=native_position,
            value_kind="shape",
            value={
                "value": self.native_value_ref(node.value.value),
                "dim": int(ast.literal_eval(node.slice)),
            },
        )

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
        semantic_type = self.semantic_type(items[0])
        for item in items[1:]:
            parsed_name = self.name_metadata(item)
            if parsed_name is not None:
                original_name = parsed_name
                continue
            self.apply_annotation_metadata(semantic_type, item)
        return semantic_type, original_name

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
        if self.matches_name(node, "Callable") or self.is_subscript_of(node, "Callable"):
            return self.callable_type(node)
        if isinstance(node, ast.Call) and self.matches_name(node.func, "Const"):
            if len(node.args) != 1 or node.keywords:
                raise ValueError(f"Const type expects one argument: {ast.unparse(node)!r}")
            semantic_type = self.semantic_type(node.args[0])
            self._mark_storage_read_only(semantic_type)
            return semantic_type
        if isinstance(node, ast.Call) and self._is_ptr_call(node):
            if len(node.args) != 1 or node.keywords:
                raise ValueError(f"Ptr type expects one argument: {ast.unparse(node)!r}")
            pointer_depth = self._ptr_depth(node.func)
            pointee = self.semantic_type(node.args[0])
            read_only = pointee.storage.read_only if pointee.storage is not None else False
            pointee.storage = SemanticStorageContract(
                kind="reference" if pointer_depth == 1 else "pointer",
                read_only=read_only,
                mutable=not read_only,
                pointer_depth=pointer_depth,
            )
            pointee.ownership.mutable = not read_only
            return pointee

        name = self.type_name(node)
        if name == "Unknown":
            raise ValueError("Unknown semantic type is not allowed in .pyi annotations")
        if not isinstance(node, ast.Subscript):
            return SemanticType(name=name, dtype=name)

        if not self._is_array_subscript(node):
            raise ValueError(
                "Non-dimensional type subscriptions are not supported; "
                "use Final[...] for constants and Annotated[...] for constraints or array metadata"
            )
        return self.array_type(node)

    def array_type(self, node: ast.Subscript) -> SemanticType:
        if isinstance(node.value, ast.Subscript):
            semantic_type = self.array_type(node.value)
            selector = ", ".join(self.dimension_text(item) for item in self.subscript_items(node))
            semantic_type.metadata["rank_selector"] = selector
            if semantic_type.storage and semantic_type.storage.array:
                semantic_type.storage.array.metadata["rank_selector"] = selector
            return semantic_type

        name = self.type_name(node)
        dims = [self.dimension_text(item) for item in self.subscript_items(node)]
        rank = None if "..." in dims else len(dims)
        array = SemanticArrayContract(
            rank=rank,
            shape=list(dims),
            order="ORDER_C" if rank is not None and rank > 1 else None,
            axes=["strided" if "Strided" in dim else "dense" for dim in dims],
            contiguous=not any("Strided" in dim for dim in dims),
        )
        storage = SemanticStorageContract(kind="array", array=array)
        return SemanticType(
            name=name,
            rank=rank or 0,
            dtype=name,
            shape=list(dims) if rank is not None else [],
            constraints=[],
            storage=storage,
        )

    def apply_annotation_metadata(self, semantic_type: SemanticType, node: ast.expr) -> None:
        if isinstance(node, ast.Name):
            if not self._apply_metadata_name(semantic_type, node.id):
                self._append_constraint_metadata(semantic_type, node.id, [])
            return
        if isinstance(node, ast.Call):
            helper = self.required_name(node.func)
            if helper == "Intent":
                if len(node.args) != 1:
                    raise ValueError(f"Intent metadata expects one argument: {ast.unparse(node)!r}")
                semantic_type.metadata["_pyi_intent"] = str(ast.literal_eval(node.args[0]))
                return
            if helper == "FortranCharacterLength":
                if len(node.args) != 1:
                    raise ValueError(f"FortranCharacterLength metadata expects one argument: {ast.unparse(node)!r}")
                semantic_type.metadata["fortran_character_length"] = str(ast.literal_eval(node.args[0]))
                return
            if helper == "ArrayCategory":
                self._require_array_storage(semantic_type).category = str(ast.literal_eval(node.args[0]))
                return
            if helper == "SourceDims":
                values = [str(ast.literal_eval(arg)) for arg in node.args]
                array = self._require_array_storage(semantic_type)
                array.source_shape = values
                array.lower_bounds, array.upper_bounds = self._bounds_from_source_shape(values)
                return
            if helper == "SourceShape":
                raise ValueError("SourceShape metadata is not supported; use SourceDims")
            if helper == "LowerBounds":
                self._require_array_storage(semantic_type).lower_bounds = [
                    None if isinstance(arg, ast.Constant) and arg.value is None else str(ast.literal_eval(arg))
                    for arg in node.args
                ]
                return
            if helper == "UpperBounds":
                self._require_array_storage(semantic_type).upper_bounds = [
                    None if isinstance(arg, ast.Constant) and arg.value is None else str(ast.literal_eval(arg))
                    for arg in node.args
                ]
                return
            if node.keywords:
                raise ValueError(f"Constraint metadata expects positional arguments only: {ast.unparse(node)!r}")
            self._append_constraint_metadata(
                semantic_type,
                helper,
                [ast.literal_eval(arg) for arg in node.args],
            )
            return
        raise ValueError(f"Unsupported Annotated metadata: {ast.unparse(node)!r}")

    def _apply_metadata_name(self, semantic_type: SemanticType, name: str) -> bool:
        if name in {"ORDER_C", "ORDER_F", "ORDER_ANY"}:
            array = self._require_array_storage(semantic_type)
            array.order = name
            return True
        if name == "Allocatable":
            array = self._require_array_storage(semantic_type)
            array.allocatable = True
            return True
        if name == "Pointer":
            array = self._require_array_storage(semantic_type)
            array.pointer = True
            return True
        if name == "Contiguous":
            self._require_array_storage(semantic_type).contiguous = True
            return True
        if name == "FortranAllocatable":
            semantic_type.metadata["fortran_allocatable"] = True
            return True
        return False

    @staticmethod
    def _append_constraint_metadata(
        semantic_type: SemanticType,
        name: str,
        arguments: list[object],
    ) -> None:
        if name == "Constant":
            raise ValueError("Constant metadata is not supported; use Final[...]")
        if name == "Shape":
            raise ValueError("Shape metadata is not supported; put dimensions inside T[...]")
        semantic_type.constraints.append(SemanticConstraint(name=name, arguments=arguments))

    @staticmethod
    def _require_array_storage(semantic_type: SemanticType) -> SemanticArrayContract:
        if semantic_type.storage is None:
            semantic_type.storage = SemanticStorageContract(kind="array")
        if semantic_type.storage.array is None:
            semantic_type.storage.array = SemanticArrayContract(
                rank=semantic_type.rank,
                shape=list(semantic_type.shape),
            )
        return semantic_type.storage.array

    @staticmethod
    def _bounds_from_source_shape(shape: list[str]) -> tuple[list[str | None], list[str | None]]:
        lower_bounds: list[str | None] = []
        upper_bounds: list[str | None] = []
        for dim in shape:
            token = str(dim).strip()
            if ":" in token:
                lower, upper = token.split(":", 1)
                lower_text = lower.strip() or None
                lower_bounds.append(None if lower_text == "1" else lower_text)
                upper_bounds.append(upper.strip() or None)
            elif token == "*":
                lower_bounds.append(None)
                upper_bounds.append("*")
            else:
                lower_bounds.append(None)
                upper_bounds.append(None)
        return lower_bounds, upper_bounds

    @staticmethod
    def _mark_storage_read_only(semantic_type: SemanticType) -> None:
        if semantic_type.storage is None:
            semantic_type.storage = SemanticStorageContract(kind="value")
        semantic_type.storage.read_only = True
        semantic_type.storage.mutable = False
        semantic_type.ownership.mutable = False

    @staticmethod
    def _inferred_argument_intent(semantic_type: SemanticType) -> str:
        storage = semantic_type.storage
        if storage is None:
            return "in"
        if storage.kind in {"reference", "array", "pointer"} and not storage.read_only:
            return "inout"
        return "in"

    @staticmethod
    def _pop_intent_metadata(semantic_type: SemanticType, default: str) -> str:
        value = semantic_type.metadata.pop("_pyi_intent", None)
        return str(value).lower() if value is not None else default

    @staticmethod
    def _is_ptr_call(node: ast.Call) -> bool:
        return _PyiAstParser.matches_name(node.func, "Ptr") or (
            isinstance(node.func, ast.Subscript) and _PyiAstParser.matches_name(node.func.value, "Ptr")
        )

    @staticmethod
    def _ptr_depth(node: ast.AST) -> int:
        if isinstance(node, ast.Subscript):
            depth = int(ast.literal_eval(node.slice))
            if depth <= 1:
                raise ValueError("Ptr[1](...) is invalid; use Ptr(...)")
            return depth
        return 1

    def _is_array_subscript(self, node: ast.Subscript) -> bool:
        if isinstance(node.value, ast.Subscript):
            return self._is_array_subscript(node.value)
        items = self.subscript_items(node)
        if not items:
            return False
        if any(isinstance(item, ast.Slice | ast.Constant) for item in items):
            return True
        if any(
            isinstance(item, ast.Name) and item.id not in self._non_dimension_subscription_names() for item in items
        ):
            return True
        if any(
            isinstance(item, ast.Call) and self.required_name(item.func) in self._non_dimension_subscription_names()
            for item in items
        ):
            return False
        if any(isinstance(item, ast.Call) for item in items):
            return True
        return any(isinstance(item, ast.BinOp | ast.UnaryOp) for item in items)

    @staticmethod
    def _non_dimension_subscription_names() -> set[str]:
        return {
            "Allocatable",
            "Constant",
            "Contiguous",
            "Optional",
            "ORDER_ANY",
            "ORDER_C",
            "ORDER_F",
            "Pointer",
            "Shape",
        }

    def dimension_text(self, node: ast.expr) -> str:
        if isinstance(node, ast.Constant) and node.value is Ellipsis:
            return "..."
        if isinstance(node, ast.Slice):
            return self.slice_text(node)
        if isinstance(node, ast.Constant):
            return str(node.value)
        if isinstance(node, ast.Attribute | ast.Subscript):
            raise ValueError(f"Unsupported array dimension expression: {ast.unparse(node)!r}")
        return ast.unparse(node)

    def slice_text(self, node: ast.Slice) -> str:
        lower = "" if node.lower is None else ast.unparse(node.lower)
        upper = "" if node.upper is None else ast.unparse(node.upper)
        step = "" if node.step is None else ast.unparse(node.step)
        if step:
            return f"{lower}:{upper}:{step}"
        return f"{lower}:{upper}"

    def callable_type(self, node: ast.expr) -> SemanticType:
        if not isinstance(node, ast.Subscript):
            return SemanticType(name="Callable", dtype="Callable")

        items = self.subscript_items(node)
        if len(items) != 2:
            raise ValueError(f"Callable expects argument types and a return type: {ast.unparse(node)!r}")

        raw_args, raw_return = items
        if isinstance(raw_args, ast.Constant) and raw_args.value is Ellipsis:
            return SemanticType(
                name="Callable",
                dtype="Callable",
                metadata={"arguments": None, "return": self.semantic_type(raw_return)},
            )
        if not isinstance(raw_args, ast.List):
            raise ValueError(f"Callable arguments must be a list: {ast.unparse(node)!r}")

        return SemanticType(
            name="Callable",
            dtype="Callable",
            metadata={
                "arguments": [self.semantic_type(item) for item in raw_args.elts],
                "return": self.semantic_type(raw_return),
            },
        )

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
    def literal_default_value(node: ast.expr | None) -> str | None:
        if node is None or _PyiAstParser.default_marks_optional(node):
            return None
        return str(ast.literal_eval(node))

    @staticmethod
    def assignment_default_value(node: ast.expr | None, semantic_type: SemanticType) -> str | None:
        if node is None or _PyiAstParser.default_marks_optional(node):
            return None
        if any(constraint.name == "Constant" for constraint in semantic_type.constraints):
            return ast.unparse(node)
        return _PyiAstParser.literal_default_value(node)

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

        args = list(zip(node.args.args, self._argument_defaults(node), strict=False))
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
        intent = self._pop_intent_metadata(semantic_type, self._inferred_argument_intent(semantic_type))
        semantic_type.ownership.mutable = intent.lower() != "in"
        if semantic_type.storage is not None:
            semantic_type.storage.mutable = intent.lower() != "in"
        return SemanticArgument(
            name=original_name or arg.arg,
            semantic_type=semantic_type,
            intent=intent,
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
        if not (isinstance(body, ast.Expr) and isinstance(body.value, ast.Constant) and body.value.value is Ellipsis):
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
        self.fields: list[SemanticField] = []
        self.methods: list[SemanticMethod] = []
        self.classes: list[SemanticClass] = []

    def visit_body(self, nodes: list[ast.stmt]) -> None:
        for node in nodes:
            self.visit(node)

    def visit_Pass(self, node: ast.Pass) -> None:
        return None

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self.fields.append(self.parser.ann_assign(node, default_intent="in", binding_cls=SemanticField))

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        decorators = self.parser.decorators(node.decorator_list, context="class body")
        self.methods.append(
            self.parser.method_def(
                node,
                visibility=decorators.visibility,
                projection=decorators.projection,
            )
        )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        decorators = self.parser.decorators(node.decorator_list, context="class body")
        if decorators.has_native_call:
            raise ValueError(f"Unsupported class body decorator: {ast.unparse(node.decorator_list[-1])!r}")
        if len(node.bases) == 1 and self.parser.is_subscript_of(node.bases[0], "Enum"):
            raise ValueError(f"Nested enum declarations are not supported: {_node_text(node)!r}")
        self.classes.append(self.parser.class_def(node, visibility=decorators.visibility))

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
        if len(node.bases) == 1 and self.parser.is_subscript_of(node.bases[0], "Enum"):
            self.parser.module.classes.append(self.parser.enum_def(node, visibility=decorators.visibility))
        else:
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


def _annotate_imported_external_type_refs(module: SemanticModule) -> None:
    imported = _imported_type_refs(module)
    for semantic_type in _iter_module_semantic_types(module):
        imported_ref = imported.get(semantic_type.name)
        if imported_ref is None:
            continue
        origin_module, source_name, local_name = imported_ref
        semantic_type.metadata.setdefault(
            EXTERNAL_TYPE_REF_METADATA,
            {
                "name": source_name,
                "local_name": local_name,
                "origin_module": origin_module,
                "wrapped": False,
                "representation": "opaque",
            },
        )


def _imported_type_refs(module: SemanticModule) -> dict[str, tuple[str, str, str]]:
    imported: dict[str, tuple[str, str, str]] = {}
    for imp in module.imports:
        if isinstance(imp, SemanticImport):
            for item in imp.items:
                local_name = item.target or item.source
                imported[local_name] = (imp.module, item.source, local_name)
            continue
        for item in imp.split(","):
            module_name, _, alias = item.strip().partition(" as ")
            visible_name = alias or module_name
            imported[visible_name] = (module_name, visible_name, visible_name)

    for semantic_type in _iter_module_semantic_types(module):
        if "." not in semantic_type.name:
            continue
        module_name, type_name = semantic_type.name.rsplit(".", 1)
        visible_module = module_name.split(".", 1)[0]
        imported_module = imported.get(visible_module)
        if imported_module is not None:
            imported[semantic_type.name] = (imported_module[0], type_name, semantic_type.name)
    return imported


def _reconcile_external_type_refs(modules: list[SemanticModule]) -> list[SemanticModule]:
    definitions = {(module.name, declaration.name): declaration for module in modules for declaration in module.classes}
    for module in modules:
        for semantic_type in _iter_module_semantic_types(module):
            ref = semantic_type.metadata.get(EXTERNAL_TYPE_REF_METADATA)
            if not isinstance(ref, dict):
                continue
            declaration = definitions.get((ref.get("origin_module"), ref.get("name")))
            wrapped = declaration is not None and (
                not isinstance(declaration, SemanticClass) or "Opaque" not in declaration.base_classes
            )
            ref["wrapped"] = wrapped
            ref["representation"] = "wrapped" if wrapped else "opaque"
    return modules
