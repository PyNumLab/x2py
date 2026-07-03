from __future__ import annotations

import ast
from collections.abc import Iterable
from copy import deepcopy
import json
import keyword
import re

from x2py.naming import NamingPolicy
from x2py.ownership_policy import OWNERSHIP_POLICY_METADATA, POINTER_POLICY_FIELDS, POINTER_POLICY_METADATA
from x2py.numpy_types import SEMANTIC_DTYPE_TO_NUMPY_DTYPE
from x2py.semantics.models import (
    EXTERNAL_TYPE_REF_METADATA,
    FORTRAN_GENERIC_NAME_METADATA,
    OVERLOAD_KIND_METADATA,
    OVERLOAD_TARGET_METADATA,
    PYI_ADDRESS_ROLE_METADATA,
    PYI_ADDRESS_ROLE_PROJECTION,
    PYI_ADDRESS_ROLE_RAW,
    PYI_NATIVE_PROJECTION_METADATA,
    PYI_SCALAR_STORAGE_CATEGORY,
    PYI_BIND_TARGET_METADATA,
    PYI_USER_PRIVATE_METADATA,
    PYTHON_BOUND_POSITION_METADATA,
    PYTHON_METHOD_NAME_METADATA,
    PYTHON_STATIC_METADATA,
    PYTHON_VALUE_IMMUTABLE,
    PYTHON_VALUE_MUTABILITY_METADATA,
    RUNTIME_HOLD_GIL_METADATA,
    RUNTIME_STATUS_ERROR_METADATA,
    ProjectionMapping,
    ProcedureOverloadSet,
    SemanticArgument,
    SemanticArrayContract,
    SemanticClass,
    SemanticConstraint,
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
from x2py.visitor import ClassVisitor


class PyiPrinter(ClassVisitor):
    """Emit Python stub text from semantic IR models.

    The class follows the same reading order as ``FortranParser``: its public
    entrypoint comes first, semantic model visitors follow in model-flow order,
    and formatting helpers remain next to the visitor group that owns them.
    """

    # ------------------------------------------------------------------
    # Public entrypoints and state
    # ------------------------------------------------------------------

    def __init__(self, *, normalize_fortran_public_names: bool = False):
        """Configure whether source-generated Fortran contracts use Python public names."""
        self._normalize_fortran_public_names = normalize_fortran_public_names
        self._naming_policy = NamingPolicy()
        self._public_namespace: tuple[str, ...] = ()
        self._reserved_public_names: dict[tuple[tuple[str, ...], str, object], str] = {}
        self._semantic_class_names: set[str] = set()

    def emit(self, node) -> str:
        """Emit the supported semantic model passed by the caller."""
        if self._normalize_fortran_public_names and isinstance(node, SemanticModule):
            previous_policy = self._naming_policy
            previous_namespace = self._public_namespace
            previous_reserved = self._reserved_public_names
            self._naming_policy = NamingPolicy()
            self._public_namespace = ()
            self._reserved_public_names = {}
            try:
                return self._visit(node)
            finally:
                self._naming_policy = previous_policy
                self._public_namespace = previous_namespace
                self._reserved_public_names = previous_reserved
        return self._visit(node)

    @staticmethod
    def _visit_not_supported(node):
        """Reject semantic models that have no `.pyi` visitor."""
        raise TypeError(f"Unsupported semantic model for .pyi emission: {type(node)!r}")

    # ------------------------------------------------------------------
    # Model visitors
    # ------------------------------------------------------------------

    @staticmethod
    def _visit_SemanticConstraint(constraint: SemanticConstraint) -> str:
        """Emit constraint syntax."""
        if constraint.name == "Constant":
            raise ValueError("Constant constraints are emitted through Final[...] data declarations")
        if constraint.name == "Shape":
            raise ValueError("Shape constraints are not canonical; put dimensions inside T[...]")
        if not constraint.arguments:
            return constraint.name
        args = ", ".join(map(repr, constraint.arguments))
        return f"{constraint.name}({args})"

    def _visit_SemanticType(self, semantic_type: SemanticType) -> str:
        """Emit semantic type syntax."""
        if semantic_type.name == "Unknown" or semantic_type.dtype == "Unknown":
            raise ValueError("Cannot emit .pyi with unresolved semantic type 'Unknown'")
        if semantic_type.name == "Callable":
            text = self._emit_callable_type(semantic_type)
        elif semantic_type.storage is not None:
            text = self._emit_storage_type(semantic_type)
        else:
            text = self._semantic_base_type(semantic_type)
        annotations = [
            *self._semantic_annotation_metadata(semantic_type),
            *[self._visit(constraint) for constraint in semantic_type.constraints],
        ]
        if annotations:
            return self._annotated_type_text(text, annotations)
        return text

    def _visit_SemanticArgument(self, arg: SemanticArgument) -> str:
        """Emit argument syntax."""
        name = self._parameter_target(arg.name)
        return self._emit_typed_name(
            name,
            arg,
            original_name=arg.name if name != arg.name else None,
        )

    def _visit_SemanticVariable(self, arg: SemanticVariable) -> str:
        """Emit data member syntax."""
        return self._emit_data_member(arg)

    def _visit_SemanticFunction(self, func: SemanticFunction) -> str:
        """Emit function syntax."""
        return self._emit_function(func)

    def _emit_function(self, func: SemanticFunction, *, name_owner: object | None = None) -> str:
        """Emit function syntax with an optional shared overload-set public name."""
        return_type = self._projected_return_annotation(func)
        name = self._callable_name(func, owner=name_owner)
        decorator = self._decorators(func, emitted_name=name)
        return self._emit_callable(
            name=name,
            arguments=[self._emit_call_argument(func, arg) for arg in self._call_arguments(func)],
            return_type=return_type,
            decorator=decorator,
            def_indent="",
            parameter_indent="    ",
        )

    def _visit_SemanticMethod(self, method: SemanticMethod) -> str:
        """Emit method syntax."""
        return self._emit_method(method)

    def _emit_method(self, method: SemanticMethod, *, name_owner: object | None = None) -> str:
        """Emit method syntax with an optional shared overload-set public name."""
        return_type = self._projected_return_annotation(method)
        name = self._callable_name(method, owner=name_owner)
        decorator = self._decorators(method, indent="    ", emitted_name=name)
        arguments = [self._emit_call_argument(method, arg) for arg in self._method_call_arguments(method)]
        if not method.is_static:
            arguments.insert(0, "self")
        return self._emit_callable(
            name=name,
            arguments=arguments,
            return_type=return_type,
            decorator=decorator,
            def_indent="    ",
            parameter_indent="        ",
        ).rstrip()

    def _visit_ProcedureOverloadSet(self, overload_set: ProcedureOverloadSet, *, in_class: bool = False) -> str:
        """Emit overload set syntax."""
        definitions = []
        for procedure in overload_set.procedures:
            candidate = deepcopy(procedure)
            target = str(candidate.metadata.get(OVERLOAD_TARGET_METADATA) or candidate.native_name or candidate.name)
            if in_class:
                candidate = self._overload_method(overload_set, candidate)
                definition = self._emit_method(
                    candidate,
                    name_owner=("overload", overload_set.name, candidate.name),
                )
                indent = "    "
            else:
                candidate.name = overload_set.name
                definition = self._emit_function(
                    candidate,
                    name_owner=("overload", overload_set.name),
                )
                indent = ""
            generic = self._overload_generic_argument(candidate, overload_set.name)
            definitions.append(f'{indent}@overload("{target}"{generic})\n{definition}')
        return "\n\n".join(definitions)

    def _visit_SemanticClass(self, cls: SemanticClass) -> str:
        """Emit class syntax."""
        bases = f"({', '.join(cls.base_classes)})" if cls.base_classes else ""
        previous_namespace = self._public_namespace
        self._public_namespace = (*self._public_namespace, cls.name)
        try:
            body = self._class_body(cls)
        finally:
            self._public_namespace = previous_namespace
        decorators = []
        if self._is_private(cls):
            decorators.append("@private")
        native_type = self._native_type_decorator(cls)
        if native_type:
            decorators.append(native_type)
        decorator_text = "\n".join(decorators)
        if decorator_text:
            decorator_text += "\n"
        return f"""
{decorator_text}class {cls.name}{bases}:
{body}
""".strip()

    @staticmethod
    def _native_type_decorator(cls: SemanticClass) -> str:
        """Emit native derived-type metadata when the class needs it."""
        if cls.origin.source_language != "fortran" or cls.origin.source_kind != "derived_type":
            return ""
        attributes = tuple(str(item) for item in cls.metadata.get("fortran_type_attributes", ()))
        finalizers = tuple(str(item) for item in cls.metadata.get("fortran_final_procedures", ()))
        parts = []
        if attributes:
            parts.append(f"attributes={attributes!r}")
        if finalizers:
            parts.append(f"finalizers={finalizers!r}")
        return f"@native_type({', '.join(parts)})" if parts else ""

    def _visit_SemanticModule(self, module: SemanticModule) -> str:
        """Emit module syntax."""
        previous_class_names = self._semantic_class_names
        self._semantic_class_names = {
            str(cls.name)
            for cls in module.classes
            if cls.origin.source_language == "fortran" and cls.origin.source_kind == "derived_type"
        }
        sections: list[str] = []
        try:
            self._append_imports(sections, module)
            self._append_items(sections, self._contract_items(module.classes), self.emit)
            self._append_items(sections, self._contract_items(module.variables), self._emit_module_variable)
            overload_targets = self._module_overload_target_names(module)
            self._append_items(
                sections,
                self._contract_items(module.functions, keep_names=overload_targets),
                self._visit,
            )
            self._append_items(sections, module.overload_sets, self._visit)
            return "\n".join(sections)
        finally:
            self._semantic_class_names = previous_class_names

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _emit_storage_type(self, semantic_type: SemanticType) -> str:
        """Emit storage type syntax."""
        storage = semantic_type.storage
        base_type = self._semantic_base_type(semantic_type)
        if storage is None:
            return base_type
        if storage.kind == "value":
            if storage.read_only:
                return f"Const({base_type})"
            return base_type
        if storage.kind in {"reference", "pointer", "address"}:
            if self._is_normal_storage_address(semantic_type):
                return f"Const({base_type})" if storage.read_only else base_type
            target = self._address_target_type(semantic_type)
            if storage.read_only:
                target = f"Const({target})"
            if storage.pointer_depth > 1:
                return f"Addr[{storage.pointer_depth}]({target})"
            return f"Addr({target})"
        if storage.kind == "array":
            return self._emit_array_type(semantic_type)
        return base_type

    @staticmethod
    def _semantic_base_type(semantic_type: SemanticType) -> str:
        """Return the semantic dtype including fixed character length."""
        if semantic_type.name != "String":
            return semantic_type.name
        length = semantic_type.metadata.get("fortran_character_length")
        if length is None or str(length) in {"", ":", "*"}:
            return "String"
        return f"String[{length}]"

    def _is_normal_storage_address(self, semantic_type: SemanticType) -> bool:
        """Return whether address storage is hidden behind the normal Python object."""
        storage = semantic_type.storage
        return bool(
            semantic_type.rank == 0
            and storage is not None
            and storage.kind in {"reference", "address"}
            and storage.pointer_depth == 1
            and storage.metadata.get(PYI_ADDRESS_ROLE_METADATA) != PYI_ADDRESS_ROLE_RAW
            and (semantic_type.name == "String" or str(semantic_type.name) in self._semantic_class_names)
        )

    def _address_target_type(self, semantic_type: SemanticType) -> str:
        """Return the pointee type spelling for a raw address contract."""
        base_type = self._semantic_base_type(semantic_type)
        if semantic_type.rank <= 0:
            return base_type
        dimensions = semantic_type.shape
        if not dimensions:
            storage = semantic_type.storage
            array = storage.array if storage is not None else None
            dimensions = tuple(array.source_shape or array.shape) if array is not None else ()
        return f"{base_type}[{', '.join(str(dimension) for dimension in dimensions)}]"

    def _emit_array_type(self, semantic_type: SemanticType) -> str:
        """Emit array type syntax."""
        storage = semantic_type.storage
        array = storage.array if storage is not None else None
        if array is not None and array.category == PYI_SCALAR_STORAGE_CATEGORY:
            base = f"{self._semantic_base_type(semantic_type)}[()]"
            if storage is not None and storage.read_only:
                base = f"Const({base})"
            return base
        dimensions = self._array_dimensions(semantic_type, array)
        base = f"{self._semantic_base_type(semantic_type)}[{', '.join(dimensions)}]"
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
        """Handle array dimensions for the current generation context."""
        if array is not None and array.category == "assumed_size" and array.source_shape:
            shape = [PyiPrinter._assumed_size_array_dimension(dim) for dim in array.source_shape]
        else:
            shape = list(array.shape if array is not None and array.shape else semantic_type.shape)
        if not shape and semantic_type.rank > 0:
            shape = [":" for _ in range(semantic_type.rank)]
        return [PyiPrinter._printed_array_dimension(dim) for dim in shape]

    @staticmethod
    def _assumed_size_array_dimension(dimension: object) -> str:
        """Map assumed-size Fortran dimensions to the `.pyi` Flat marker."""
        text = str(dimension).strip()
        if text == "*":
            return "Flat"
        if ":" in text:
            _lower, upper = text.split(":", 1)
            if upper.strip() == "*":
                return "Flat"
        return text

    @staticmethod
    def _canonical_array_dimension(dimension: object) -> str:
        """Handle canonical array dimension for the current generation context."""
        text = str(dimension)
        try:
            return ast.unparse(ast.parse(text, mode="eval").body)
        except SyntaxError:
            return text

    @staticmethod
    def _printed_array_dimension(dimension: object) -> str:
        """Return the public `.pyi` spelling for an array dimension."""
        text = PyiPrinter._canonical_array_dimension(dimension)
        if text == "::Strided":
            return "::"
        if text.endswith(":Strided"):
            return text[: -len("Strided")]
        return text

    @staticmethod
    def _array_annotation_metadata(array: SemanticArrayContract | None) -> list[str]:
        """Handle array annotation metadata for the current generation context."""
        if array is None:
            return []
        metadata: list[str] = []
        if array.order in {"ORDER_F", "ORDER_ANY"} and not (
            array.category == "assumed_size" and array.order == "ORDER_F"
        ):
            metadata.append(array.order)
        if array.order == "ORDER_C" and PyiPrinter._is_c_order_flat_array(array):
            metadata.append("ORDER_C")
        if array.allocatable:
            metadata.append("Allocatable")
        if array.pointer:
            metadata.append("Pointer")
        if PyiPrinter._requires_source_dims_metadata(array):
            args = ", ".join(json.dumps(str(dim)) for dim in array.source_shape)
            metadata.append(f"SourceDims({args})")
        return metadata

    @staticmethod
    def _requires_source_dims_metadata(array: SemanticArrayContract) -> bool:
        """Return whether lower-bound assumed-size details need metadata."""
        if array.category != "assumed_size" or not array.source_shape:
            return False
        for dim in array.source_shape:
            text = str(dim).strip()
            if ":" not in text:
                continue
            lower, upper = text.split(":", 1)
            if upper.strip() == "*" and lower.strip() not in {"", "1"}:
                return True
        return False

    @staticmethod
    def _is_c_order_flat_array(array: SemanticArrayContract) -> bool:
        """Return whether an assumed-size contract uses leading Flat storage."""
        return (
            array.category == "assumed_size"
            and array.rank is not None
            and array.rank > 1
            and bool(array.source_shape)
            and PyiPrinter._assumed_size_array_dimension(array.source_shape[0]) == "Flat"
        )

    @staticmethod
    def _semantic_annotation_metadata(semantic_type: SemanticType) -> list[str]:
        """Handle semantic annotation metadata for the current generation context."""
        metadata: list[str] = []
        source_type = (semantic_type.origin.source_type or "").casefold().replace(" ", "")
        if source_type in {"type(*)", "class(*)"} or semantic_type.metadata.get("fortran_assumed_type"):
            metadata.append("AssumedType")
        if semantic_type.metadata.get("fortran_polymorphic"):
            metadata.append("Polymorphic")
        if semantic_type.metadata.get("fortran_allocatable"):
            metadata.append("FortranAllocatable")
        if semantic_type.metadata.get("aliased"):
            metadata.append("Aliased")
        if semantic_type.metadata.get(PYTHON_VALUE_MUTABILITY_METADATA) == PYTHON_VALUE_IMMUTABLE:
            metadata.append("Immutable")
        pointer_association = semantic_type.metadata.get("fortran_pointer_association")
        if pointer_association is not None:
            metadata.append(f"PointerAssociation({json.dumps(str(pointer_association))})")
        pointer_policy = semantic_type.metadata.get(POINTER_POLICY_METADATA)
        if isinstance(pointer_policy, dict):
            arguments = []
            for name in POINTER_POLICY_FIELDS:
                value = pointer_policy.get(name)
                if value is not None:
                    rendered = repr(value) if isinstance(value, bool) else json.dumps(str(value))
                    arguments.append(f"{name}={rendered}")
            metadata.append(f"PointerPolicy({', '.join(arguments)})")
        ownership_policy = semantic_type.metadata.get(OWNERSHIP_POLICY_METADATA)
        if isinstance(ownership_policy, dict):
            owner = ownership_policy.get("owner")
            transfer = ownership_policy.get("transfer")
            destruction = ownership_policy.get("destruction")
            if owner is not None:
                metadata.append(f"Ownership({json.dumps(str(owner))})")
            if transfer is not None:
                metadata.append(f"Transfer({json.dumps(str(transfer))})")
            if destruction is not None:
                metadata.append(f"Destruction({json.dumps(str(destruction))})")
        return metadata

    def _emit_callable_type(self, semantic_type: SemanticType) -> str:
        """Emit callable type syntax."""
        arguments = semantic_type.metadata.get("arguments")
        return_type = semantic_type.metadata.get("return")
        if isinstance(arguments, list) and return_type is not None:
            args = ", ".join(self._visit(arg) for arg in arguments)
            return f"Callable[[{args}], {self._visit(return_type)}]"
        if return_type is not None:
            return f"Callable[..., {self._visit(return_type)}]"
        return "Callable"

    def _emit_data_member(self, variable: SemanticVariable) -> str:
        """Emit a variable in class-field context rather than argument context."""
        name = self._data_member_name(variable)
        return self._emit_typed_name(
            self._annotation_target(name),
            variable,
            original_name=variable.name if name != variable.name else None,
        )

    def _emit_module_variable(self, arg: SemanticVariable) -> str:
        """Emit module variable syntax."""
        if self._is_allocatable_module_array(arg):
            name = self._module_variable_name(arg)
            type_text = f"{self._visit(arg.semantic_type)} | None"
            if name != arg.name:
                type_text = self._annotated_type_text(type_text, [f"Name({json.dumps(arg.name)})"])
            return f"{self._annotation_target(name)}: {type_text}"
        name = self._module_variable_name(arg)
        return self._emit_typed_name(
            self._annotation_target(name),
            arg,
            original_name=arg.name if name != arg.name else None,
        )

    @staticmethod
    def _is_allocatable_module_array(arg: SemanticVariable) -> bool:
        """Return whether is allocatable module array."""
        storage = arg.semantic_type.storage
        return bool(storage is not None and storage.array is not None and storage.array.allocatable)

    @staticmethod
    def _is_allocatable_array(semantic_type: SemanticType) -> bool:
        """Return whether is allocatable array."""
        storage = semantic_type.storage
        return bool(storage is not None and storage.array is not None and storage.array.allocatable)

    def _emit_typed_name(
        self,
        name: str,
        arg: SemanticVariable,
        *,
        original_name: str | None = None,
        omit_output_intent: bool = False,
    ) -> str:
        """Emit typed name syntax."""
        semantic_type = self._without_constant_constraint(arg.semantic_type)
        type_text = self._visit(semantic_type)
        annotation_metadata = []
        if original_name is not None:
            annotation_metadata.append(f"Name({json.dumps(original_name)})")
        if self._requires_intent_metadata(arg, omit_output_intent=omit_output_intent):
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
        else:
            default_value = self._pyi_default_value(arg)
            if default_value is not None:
                text += f" = {default_value}"
        return text

    def _emit_call_argument(self, func: SemanticFunction, arg: SemanticArgument) -> str:
        """Emit a callable argument with compact output metadata when possible."""
        name = self._parameter_target(arg.name)
        emitted_arg = self._projected_address_argument(func, arg)
        return self._emit_typed_name(
            name,
            emitted_arg,
            original_name=arg.name if name != arg.name else None,
            omit_output_intent=self._can_omit_visible_projected_output_intent(func, arg),
        )

    @classmethod
    def _projected_address_argument(
        cls,
        func: SemanticFunction,
        arg: SemanticArgument,
    ) -> SemanticArgument:
        """Return the Python-visible value form for projected scalar addresses."""
        if not cls._uses_address_projection(func, arg):
            return arg
        emitted_arg = deepcopy(arg)
        storage = arg.semantic_type.storage
        emitted_arg.semantic_type.storage = SemanticStorageContract(
            kind="value",
            read_only=bool(storage is not None and storage.read_only),
            mutable=not bool(storage is not None and storage.read_only),
        )
        emitted_arg.semantic_type.ownership.mutable = not bool(storage is not None and storage.read_only)
        return emitted_arg

    @classmethod
    def _uses_address_projection(cls, func: SemanticFunction, arg: SemanticArgument) -> bool:
        """Return whether `arg` is emitted as a value plus `Addr(Arg(...))`."""
        if not cls._is_scalar_address_projection(arg.semantic_type):
            return False
        return any(cls._mapping_projects_argument(mapping, arg) for mapping in func.projection)

    @staticmethod
    def _is_scalar_address_projection(semantic_type: SemanticType) -> bool:
        """Return whether semantic type is a Python-value scalar passed by native address."""
        storage = semantic_type.storage
        return bool(
            semantic_type.rank == 0
            and semantic_type.name != "String"
            and semantic_type.dtype in SEMANTIC_DTYPE_TO_NUMPY_DTYPE
            and storage is not None
            and (
                (
                    storage.kind == "address"
                    and storage.metadata.get(PYI_ADDRESS_ROLE_METADATA) == PYI_ADDRESS_ROLE_PROJECTION
                )
                or (storage.kind == "reference" and storage.read_only)
            )
            and storage.pointer_depth == 1
        )

    @staticmethod
    def _mapping_projects_argument(mapping: ProjectionMapping, arg: SemanticArgument) -> bool:
        """Return whether a projection mapping consumes `arg` as a Python argument."""
        return bool(
            mapping.native_position is not None
            and mapping.python_position is not None
            and (mapping.python_name or mapping.native_name) == arg.name
        )

    @staticmethod
    def _annotated_type_text(type_text: str, metadata: list[str]) -> str:
        """Handle annotated type text for the current generation context."""
        suffix = ", ".join(metadata)
        if type_text.startswith("Annotated[") and type_text.endswith("]"):
            return f"{type_text[:-1]}, {suffix}]"
        return f"Annotated[{type_text}, {suffix}]"

    @staticmethod
    def _is_constant(semantic_type: SemanticType) -> bool:
        """Return whether is constant."""
        return any(constraint.name == "Constant" for constraint in semantic_type.constraints)

    @staticmethod
    def _is_enum_constant(arg: SemanticVariable) -> bool:
        """Return whether is enum constant."""
        return PyiPrinter._is_constant(arg.semantic_type) and bool(
            arg.semantic_type.metadata.get("semantic_enum") or arg.semantic_type.metadata.get("c_enum")
        )

    @staticmethod
    def _enum_default_value(arg: SemanticVariable) -> str | None:
        """Handle enum default value for the current generation context."""
        pyi_value = arg.metadata.get("pyi_default_value")
        if isinstance(pyi_value, str):
            return pyi_value
        if arg.origin.source_language == "c":
            return None
        return arg.default_value

    @staticmethod
    def _pyi_default_value(arg: SemanticVariable) -> str | None:
        """Handle pyi default value for the current generation context."""
        if (self_value := arg.metadata.get("pyi_default_value")) and isinstance(self_value, str):
            return self_value
        if PyiPrinter._is_enum_constant(arg):
            return PyiPrinter._enum_default_value(arg)
        if (initializer := arg.metadata.get("fortran_initializer")) and (
            literal := PyiPrinter._fortran_literal_text(initializer)
        ):
            return literal
        return PyiPrinter._python_literal_text(arg.default_value)

    @staticmethod
    def _python_literal_text(value: str | None) -> str | None:
        """Handle python literal text for the current generation context."""
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        text = re.sub(r"\.true\.", "True", text, flags=re.IGNORECASE)
        text = re.sub(r"\.false\.", "False", text, flags=re.IGNORECASE)
        text = re.sub(r"(?<=\d)[dD](?=[+-]?\d)", "e", text)
        try:
            return ast.unparse(ast.parse(text, mode="eval").body)
        except SyntaxError:
            return None

    @staticmethod
    def _fortran_literal_text(value: str | None) -> str | None:
        """Return a Python literal spelling for literal Fortran initializer text."""
        text = PyiPrinter._python_literal_text(value)
        if text is None:
            return None
        try:
            ast.literal_eval(ast.parse(text, mode="eval").body)
        except (ValueError, SyntaxError):
            return None
        return text

    @staticmethod
    def _without_constant_constraint(semantic_type: SemanticType) -> SemanticType:
        """Handle without constant constraint for the current generation context."""
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

    @staticmethod
    def _overload_generic_argument(procedure: SemanticFunction, public_name: str) -> str:
        """Handle overload generic argument for the current generation context."""
        generic_name = str(procedure.metadata.get(FORTRAN_GENERIC_NAME_METADATA, ""))
        if procedure.metadata.get(OVERLOAD_KIND_METADATA) == "generic":
            return "" if generic_name == public_name else f', generic="{generic_name}"'
        if procedure.metadata.get(OVERLOAD_KIND_METADATA) not in {"operator", "comparison"}:
            return ""
        if re.sub(r"\s+", "", generic_name).casefold() not in {
            "operator(.eqv.)",
            "operator(.neqv.)",
        }:
            return ""
        return f', generic="{generic_name}"'

    @staticmethod
    def _overload_method(
        overload_set: ProcedureOverloadSet,
        procedure: SemanticFunction,
    ) -> SemanticMethod:
        """Handle overload method for the current generation context."""
        bound_position = procedure.metadata.get(PYTHON_BOUND_POSITION_METADATA)
        return SemanticMethod(
            name=str(procedure.metadata.get(PYTHON_METHOD_NAME_METADATA, overload_set.name)),
            native_name=procedure.native_name,
            arguments=procedure.arguments,
            return_type=procedure.return_type,
            locals=procedure.locals,
            contracts=procedure.contracts,
            projection=procedure.projection,
            metadata=procedure.metadata,
            visibility=procedure.visibility,
            origin=procedure.origin,
            is_static=bool(procedure.metadata.get(PYTHON_STATIC_METADATA)),
            passed_object_name=(procedure.arguments[bound_position].name if isinstance(bound_position, int) else None),
            passed_object_position=bound_position if isinstance(bound_position, int) else None,
        )

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
        """Emit callable syntax."""
        if not arguments:
            return f"{decorator}{def_indent}def {name}() -> {return_type}: ..."
        if arguments == ["self"]:
            return f"{decorator}{def_indent}def {name}(self) -> {return_type}: ..."

        args = (",\n" + parameter_indent).join(arguments)
        return f"{decorator}{def_indent}def {name}(\n{parameter_indent}{args}\n{def_indent}) -> {return_type}: ..."

    def _class_body(self, cls: SemanticClass) -> str:
        """Handle class body for the current generation context."""
        body_parts = []

        nested_classes = "\n\n".join(
            self._indent_block(self._visit(nested), "    ") for nested in self._contract_items(cls.classes)
        )
        if nested_classes:
            body_parts.append(nested_classes)

        constructor = self._class_constructor(cls)
        if constructor:
            body_parts.append(constructor)

        fields = "\n".join(f"    {self._emit_data_member(field)}" for field in self._contract_items(cls.fields))
        if fields:
            body_parts.append(fields)

        overload_targets = self._overload_target_names(cls.overload_sets)
        methods = "\n\n".join(
            self._visit(method) for method in self._contract_items(cls.methods, keep_names=overload_targets)
        )
        if methods:
            body_parts.append(methods)

        overload_sets = "\n\n".join(self._visit(overload_set, in_class=True) for overload_set in cls.overload_sets)
        if overload_sets:
            body_parts.append(overload_sets)

        if not body_parts:
            return "    pass"
        return "\n\n".join(body_parts)

    def _class_constructor(self, cls: SemanticClass) -> str:
        """Handle class constructor for the current generation context."""
        if cls.origin.source_language != "fortran":
            return ""
        arguments = [
            self._constructor_argument(field) for field in cls.fields if self._constructor_accepts_field(field)
        ]
        if not arguments and cls.fields:
            return "    def __init__(self) -> None: ..."
        if not arguments:
            return ""
        return self._emit_callable(
            name="__init__",
            arguments=["self", "*", *arguments],
            return_type="None",
            decorator="",
            def_indent="    ",
            parameter_indent="        ",
        ).rstrip()

    def _constructor_argument(self, field: SemanticVariable) -> str:
        """Handle constructor argument for the current generation context."""
        name = self._data_member_name(field)
        semantic_type = self._without_constant_constraint(field.semantic_type)
        type_text = self._visit(semantic_type)
        default_value = (
            self._fortran_literal_text(field.metadata.get("fortran_initializer"))
            or self._python_literal_text(field.default_value)
            or "..."
        )
        if name != field.name:
            type_text = self._annotated_type_text(type_text, [f"Name({json.dumps(field.name)})"])
        return f"{name}: {type_text} = {default_value}"

    @staticmethod
    def _constructor_accepts_field(field: SemanticVariable) -> bool:
        """Handle constructor accepts field for the current generation context."""
        semantic_type = field.semantic_type
        return (
            field.visibility == "public"
            and semantic_type.rank == 0
            and semantic_type.name != "String"
            and semantic_type.name in SEMANTIC_DTYPE_TO_NUMPY_DTYPE
        )

    @staticmethod
    def _indent_block(text: str, indent: str) -> str:
        """Handle indent block for the current generation context."""
        return "\n".join(f"{indent}{line}" if line else line for line in text.splitlines())

    def _append_imports(self, sections: list[str], module: SemanticModule) -> None:
        """Append imports."""
        imports = self._effective_imports(module)
        for imp in imports:
            sections.append(self._emit_import(imp))
        if imports:
            sections.append("")

    @staticmethod
    def _effective_imports(module: SemanticModule) -> list[str | SemanticImport]:
        """Handle effective imports for the current generation context."""
        imports = [imp for imp in module.imports if not PyiPrinter._is_source_kind_import(imp)]
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
    def _is_source_kind_import(imp: str | SemanticImport) -> bool:
        """Return whether an import only names a source-language kind module."""
        module = imp.module if isinstance(imp, SemanticImport) else str(imp).split()[0]
        return module.casefold().lstrip(".") in {"iso_c_binding", "iso_fortran_env"}

    @staticmethod
    def _has_overload_sets(module: SemanticModule) -> bool:
        """Return whether has overload sets."""

        def class_has_overloads(cls: SemanticClass) -> bool:
            return bool(cls.overload_sets) or any(class_has_overloads(nested) for nested in cls.classes)

        return bool(module.overload_sets) or any(
            class_has_overloads(cls) for cls in module.classes if isinstance(cls, SemanticClass)
        )

    @staticmethod
    def _emit_import(imp: str | SemanticImport) -> str:
        """Emit import syntax."""
        if isinstance(imp, str):
            return f"import {imp}"
        if not imp.items:
            return f"import {imp.module}"
        items = ", ".join(PyiPrinter._emit_import_item(item) for item in imp.items)
        return f"from {imp.module} import {items}"

    @staticmethod
    def _emit_import_item(item: SemanticImportItem) -> str:
        """Emit import item syntax."""
        if item.target and item.target != item.source:
            return f"{item.source} as {item.target}"
        return item.source

    def _append_items(self, sections: list[str], items: list, emit_item) -> None:
        """Append items."""
        for item in items:
            sections.append(emit_item(item))
            sections.append("")

    @classmethod
    def _contract_items(cls, items: Iterable, *, keep_names: set[str] | None = None) -> list:
        """Handle contract items for the current generation context."""
        keep_names = set() if keep_names is None else keep_names
        return [item for item in items if cls._should_emit_contract_item(item, keep_names=keep_names)]

    @staticmethod
    def _should_emit_contract_item(item, *, keep_names: set[str]) -> bool:
        """Handle should emit contract item for the current generation context."""
        if PyiPrinter._item_names(item) & keep_names:
            return True
        if not PyiPrinter._is_source_private(item):
            return True
        return PyiPrinter._is_user_private(item)

    @staticmethod
    def _item_names(item) -> set[str]:
        """Handle item names for the current generation context."""
        names = {value for value in (getattr(item, "name", None), getattr(item, "native_name", None)) if value}
        return {str(name) for name in names}

    @staticmethod
    def _overload_target_names(overload_sets: Iterable[ProcedureOverloadSet]) -> set[str]:
        """Handle overload target names for the current generation context."""
        targets: set[str] = set()
        for overload_set in overload_sets:
            for procedure in overload_set.procedures:
                target = procedure.metadata.get(OVERLOAD_TARGET_METADATA) or procedure.native_name or procedure.name
                if target:
                    targets.add(str(target))
                targets.update(PyiPrinter._item_names(procedure))
        return targets

    @classmethod
    def _module_overload_target_names(cls, module: SemanticModule) -> set[str]:
        """Handle module overload target names for the current generation context."""
        targets = cls._overload_target_names(module.overload_sets)
        for semantic_class in module.classes:
            targets.update(cls._class_overload_target_names(semantic_class))
        return targets

    @classmethod
    def _class_overload_target_names(cls, semantic_class: SemanticClass) -> set[str]:
        """Handle class overload target names for the current generation context."""
        targets = cls._overload_target_names(semantic_class.overload_sets)
        for nested in semantic_class.classes:
            targets.update(cls._class_overload_target_names(nested))
        return targets

    @staticmethod
    def _is_source_private(node) -> bool:
        """Return whether is source private."""
        if isinstance(node, SemanticMethod):
            attributes = {str(attr).casefold() for attr in getattr(node, "binding_attributes", ())}
            return "private" in attributes
        origin = getattr(node, "origin", None)
        return (
            getattr(node, "visibility", "public") == "private" and getattr(origin, "source_language", None) == "fortran"
        )

    @staticmethod
    def _is_user_private(node) -> bool:
        """Return whether is user private."""
        origin = getattr(node, "origin", None)
        metadata = getattr(origin, "metadata", {})
        return isinstance(metadata, dict) and bool(metadata.get(PYI_USER_PRIVATE_METADATA))

    def _projected_return_annotation(self, func: SemanticFunction) -> str:
        """Handle projected return annotation for the current generation context."""
        parts = []
        if func.return_type:
            parts.append(self._visit(func.return_type))
        parts.extend(
            self._projected_argument_return(arg, visible=visible)
            for _, arg, visible in sorted(
                self._projected_return_arguments(func),
                key=lambda item: item[0],
            )
        )
        if not parts:
            return "None"
        if len(parts) == 1:
            return parts[0]
        return f"tuple[{', '.join(parts)}]"

    @staticmethod
    def _projected_return_arguments(func: SemanticFunction) -> list[tuple[int, SemanticArgument, bool]]:
        """Handle projected return arguments for the current generation context."""
        by_name = {arg.name: arg for arg in func.arguments}
        returned = []
        for mapping in func.projection:
            if mapping.result_position is None:
                continue
            arg_name = mapping.python_name or mapping.native_name
            arg = by_name.get(arg_name)
            if arg is not None:
                returned.append(
                    (
                        mapping.result_position,
                        arg,
                        PyiPrinter._is_visible_projected_return(func, mapping),
                    )
                )
        return returned

    @staticmethod
    def _is_visible_projected_return(func: SemanticFunction, mapping: ProjectionMapping) -> bool:
        """Return whether a projected return should keep a named argument result."""
        if (
            isinstance(func, SemanticMethod)
            and not func.is_static
            and mapping.native_position == func.passed_object_position
        ):
            return False
        return mapping.python_position is not None

    def _projected_argument_return(self, arg: SemanticArgument, *, visible: bool) -> str:
        """Handle projected argument return for the current generation context."""
        if visible:
            return self._named_return(arg)
        return self._plain_projected_return(arg)

    def _named_return(self, arg: SemanticArgument) -> str:
        """Handle named return for the current generation context."""
        optional = ", Optional" if arg.optional or self._is_allocatable_array(arg.semantic_type) else ""
        semantic_type = self._visible_projected_type(arg.semantic_type)
        return f'Returns["{arg.name}", {self._visit(semantic_type)}{optional}]'

    @staticmethod
    def _visible_projected_type(semantic_type: SemanticType) -> SemanticType:
        """Return the Python-visible type for address-projected scalars."""
        storage = semantic_type.storage
        if (
            semantic_type.rank == 0
            and storage is not None
            and storage.kind == "address"
            and storage.metadata.get(PYI_ADDRESS_ROLE_METADATA) == PYI_ADDRESS_ROLE_PROJECTION
        ):
            visible = deepcopy(semantic_type)
            visible.storage = SemanticStorageContract(
                kind="value",
                read_only=storage.read_only,
                mutable=not storage.read_only,
            )
            return visible
        return semantic_type

    def _plain_projected_return(self, arg: SemanticArgument) -> str:
        """Handle plain projected return for the current generation context."""
        semantic_type = deepcopy(arg.semantic_type)
        storage = semantic_type.storage
        if (
            semantic_type.rank == 0
            and storage is not None
            and (storage.kind == "reference" or storage.kind == "address")
        ):
            semantic_type.storage = None
        type_text = self._visit(semantic_type)
        if arg.optional or self._is_allocatable_array(arg.semantic_type):
            return f"{type_text} | None"
        return type_text

    def _callable_name(self, func: SemanticFunction, *, owner: object | None = None) -> str:
        """Return the Python-visible callable name to write in the contract."""
        if (
            not self._normalize_fortran_public_names
            or func.name.startswith("__")
            or func.origin.source_language != "fortran"
        ):
            return func.name
        return self._public_name(
            func.name,
            category="method" if isinstance(func, SemanticMethod) else "function",
            owner=owner if owner is not None else func,
        )

    def _data_member_name(self, variable: SemanticVariable) -> str:
        """Return the Python-visible class data-member name."""
        if not self._normalize_fortran_public_names:
            return variable.name
        return self._public_name(variable.name, category="field", owner=variable)

    def _module_variable_name(self, variable: SemanticVariable) -> str:
        """Return the Python-visible module variable name."""
        if not self._normalize_fortran_public_names:
            return variable.name
        return self._public_name(variable.name, category="variable", owner=variable)

    def _public_name(self, raw_name: str, *, category: str, owner: object) -> str:
        """Reserve and return a normalized Python public name."""
        key = (self._public_namespace, category, self._public_owner_key(owner))
        reserved = self._reserved_public_names.get(key)
        if reserved is not None:
            return reserved
        public_name = self._naming_policy.reserve_public_name(
            self._public_namespace,
            raw_name,
            category=category,
            owner=raw_name,
        )
        self._reserved_public_names[key] = public_name
        return public_name

    @staticmethod
    def _public_owner_key(owner: object) -> object:
        """Return a stable cache key for one emitted public declaration."""
        if isinstance(owner, str | int | tuple):
            return owner
        return id(owner)

    def _decorators(self, func: SemanticFunction, *, indent: str = "", emitted_name: str | None = None) -> str:
        """Handle decorators for the current generation context."""
        decorators = []
        emitted_name = emitted_name or func.name
        if self._is_private(func):
            decorators.append(f"{indent}@private")
        if isinstance(func, SemanticMethod) and func.is_static:
            decorators.append(f"{indent}@staticmethod")
        bind_target = func.metadata.get(PYI_BIND_TARGET_METADATA)
        if bind_target is None and func.native_name and func.native_name != emitted_name:
            bind_target = func.native_name
        if bind_target and not func.metadata.get(OVERLOAD_TARGET_METADATA):
            decorators.append(f"{indent}@bind({json.dumps(str(bind_target))})")
        if (
            func.origin.source_language == "fortran"
            and func.origin.native_scope is None
            and not isinstance(func, SemanticMethod)
            and not func.metadata.get(OVERLOAD_TARGET_METADATA)
        ):
            decorators.append(f"{indent}@external")
        if self._requires_native_call(func):
            decorators.append(f"{indent}{self._native_call(self._pyi_projection(func))}")
        if isinstance(policy := func.metadata.get(RUNTIME_STATUS_ERROR_METADATA), dict):
            decorators.append(f"{indent}{self._raises(policy)}")
        if func.metadata.get(RUNTIME_HOLD_GIL_METADATA):
            decorators.append(f"{indent}@hold_gil")
        if not decorators:
            return ""
        return "\n".join(decorators) + "\n"

    @staticmethod
    def _pyi_projection(func: SemanticFunction) -> list[ProjectionMapping]:
        """Return projection metadata adjusted for bound instance methods."""
        if not isinstance(func, SemanticMethod) or func.is_static or func.passed_object_position is None:
            return PyiPrinter._with_address_projections(func, deepcopy(func.projection))
        passed_position = func.passed_object_position
        projected = deepcopy(func.projection)
        if not projected:
            projected = [
                ProjectionMapping(
                    python_name=argument.name,
                    native_name=argument.name,
                    native_position=index,
                    python_position=index,
                    intent=argument.intent,
                )
                for index, argument in enumerate(func.arguments)
            ]
        for mapping in projected:
            if mapping.python_position == passed_position:
                mapping.python_position = None
                mapping.value_kind = "pass"
                continue
            if mapping.python_position is not None and mapping.python_position > passed_position:
                old_position = mapping.python_position
                mapping.python_position -= 1
                PyiPrinter._shift_address_argument_value(mapping, old_position, mapping.python_position)
        return PyiPrinter._with_address_projections(func, projected)

    @staticmethod
    def _shift_address_argument_value(
        mapping: ProjectionMapping,
        old_position: int,
        new_position: int,
    ) -> None:
        """Keep `Addr(Arg(...))` value refs aligned with shifted method arguments."""
        if mapping.value_kind != "addr" or not isinstance(mapping.value, dict):
            return
        if mapping.value.get("kind") == "arg" and mapping.value.get("position") == old_position:
            mapping.value["position"] = new_position

    @staticmethod
    def _with_address_projections(
        func: SemanticFunction,
        projection: list[ProjectionMapping],
    ) -> list[ProjectionMapping]:
        """Mark scalar address mappings as explicit native address projections."""
        by_name = {arg.name: arg for arg in func.arguments}
        for mapping in projection:
            if mapping.value_kind:
                continue
            if mapping.python_position is None:
                continue
            arg = by_name.get(mapping.python_name or mapping.native_name)
            if arg is None:
                continue
            if not PyiPrinter._uses_address_projection(func, arg):
                continue
            mapping.value_kind = "addr"
            mapping.value = {"kind": "arg", "position": mapping.python_position}
        return projection

    @staticmethod
    def _raises(policy: dict[str, object]) -> str:
        """Handle raises for the current generation context."""
        status = policy.get("status")
        if not isinstance(status, str) or not status:
            raise ValueError("raises metadata requires a non-empty status output name")
        parts = [f"status={json.dumps(status)}"]
        message = policy.get("message")
        if message is not None:
            if not isinstance(message, str) or not message:
                raise ValueError("raises metadata message must be a non-empty output name")
            parts.append(f"message={json.dumps(message)}")
        success = policy.get("success", 0)
        if not isinstance(success, int) or isinstance(success, bool):
            raise ValueError("raises metadata success must be an integer")
        parts.append(f"success={success}")
        return f"@raises({', '.join(parts)})"

    def _native_call(self, projection: list[ProjectionMapping]) -> str:
        """Handle native call for the current generation context."""
        entries = ", ".join(
            self._native_projection_entry(mapping)
            for mapping in sorted(
                projection, key=lambda item: item.native_position if item.native_position is not None else -1
            )
        )
        return f"@native_call([{entries}])"

    @staticmethod
    def _native_projection_entry(mapping: ProjectionMapping) -> str:
        """Handle native projection entry for the current generation context."""
        if mapping.value_kind:
            return PyiPrinter._native_projection_value(mapping)
        if mapping.python_position is not None:
            return f"Arg({mapping.python_position})"
        if mapping.result_position is not None:
            if mapping.native_name:
                return f"Return({mapping.native_name!r}, {mapping.result_position})"
            return f"Return({mapping.result_position})"
        raise ValueError("native_call cannot represent a native-only projection entry")

    @staticmethod
    def _native_projection_value(mapping: ProjectionMapping) -> str:
        """Handle native projection value for the current generation context."""
        if mapping.value_kind == "addr":
            return f"Addr({PyiPrinter._native_value_ref(mapping.value)})"
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
        if mapping.value_kind == "pass":
            return "Pass()"
        raise ValueError(f"Unsupported native_call projection entry: {mapping.value_kind!r}")

    @staticmethod
    def _native_value_ref(value: dict[str, int | str]) -> str:
        """Handle native value ref for the current generation context."""
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
        """Return whether requires native call."""
        if func.metadata.get(PYI_NATIVE_PROJECTION_METADATA) and any(
            mapping.result_position is not None for mapping in func.projection
        ):
            return True
        if isinstance(func, SemanticMethod) and not func.is_static and func.passed_object_position not in {None, 0}:
            return True
        projection = PyiPrinter._with_address_projections(func, deepcopy(func.projection))
        return any(
            PyiPrinter._requires_explicit_projection_mapping(mapping)
            for mapping in projection
            if not PyiPrinter._is_assignment_passed_object_return(func, mapping)
        )

    @staticmethod
    def _is_assignment_passed_object_return(func: SemanticFunction, mapping: ProjectionMapping) -> bool:
        """Return whether mapping only records assignment returning the bound object."""
        return bool(
            func.metadata.get(OVERLOAD_KIND_METADATA) == "assignment"
            and isinstance(func, SemanticMethod)
            and not func.is_static
            and mapping.result_position is not None
            and mapping.native_position == func.passed_object_position
            and mapping.python_position == func.passed_object_position
        )

    @staticmethod
    def _requires_explicit_projection_mapping(mapping: ProjectionMapping) -> bool:
        """Return whether requires explicit projection mapping."""
        if mapping.value_kind:
            return True
        if mapping.intent == "inout":
            return mapping.python_position is None or mapping.python_position != mapping.native_position
        if mapping.intent == "out" and mapping.result_position is not None:
            return mapping.python_position is None or mapping.python_position != mapping.native_position
        if mapping.intent != "in":
            return mapping.python_position is None
        if mapping.result_position is not None:
            return True
        if mapping.python_position is None:
            return True
        return mapping.native_position is not None and mapping.python_position != mapping.native_position

    @staticmethod
    def _call_arguments(func: SemanticFunction) -> list[SemanticArgument]:
        """Handle call arguments for the current generation context."""
        hidden_names = {
            mapping.python_name or mapping.native_name
            for mapping in func.projection
            if mapping.native_position is not None and mapping.python_position is None
        }
        return [arg for arg in func.arguments if arg.name not in hidden_names]

    @staticmethod
    def _requires_intent_metadata(arg: SemanticVariable, *, omit_output_intent: bool = False) -> bool:
        """Return whether requires intent metadata."""
        return getattr(arg, "intent", "in") == "out" and not omit_output_intent

    @staticmethod
    def _can_omit_visible_projected_output_intent(func: SemanticFunction, arg: SemanticArgument) -> bool:
        """Return whether compact `.pyi` can omit behavior-neutral output intent."""
        if getattr(arg, "intent", "in") != "out":
            return False
        if not PyiPrinter._has_visible_projection_result(func, arg):
            return False
        return PyiPrinter._is_compact_visible_projection_storage(arg)

    @staticmethod
    def _has_visible_projection_result(func: SemanticFunction, arg: SemanticArgument) -> bool:
        """Return whether an argument is passed visibly and also projected as a result."""
        return any(
            (mapping.python_name or mapping.native_name) == arg.name
            and mapping.native_position is not None
            and mapping.python_position is not None
            and mapping.result_position is not None
            for mapping in func.projection
        )

    @staticmethod
    def _is_compact_visible_projection_storage(arg: SemanticArgument) -> bool:
        """Return whether storage can carry compact visible projection semantics."""
        storage = arg.semantic_type.storage
        array = storage.array if storage is not None else None
        if storage is None:
            return False
        if storage.kind == "array":
            return bool(array is not None and not array.allocatable and not array.pointer)
        return bool(
            storage.kind == "reference"
            and not storage.read_only
            and storage.pointer_depth == 1
            and arg.semantic_type.name not in SEMANTIC_DTYPE_TO_NUMPY_DTYPE
        )

    @classmethod
    def _method_call_arguments(cls, method: SemanticMethod) -> list[SemanticArgument]:
        """Handle method call arguments for the current generation context."""
        args = cls._call_arguments(method)
        if method.is_static:
            return args
        if method.passed_object_position is not None:
            return [arg for index, arg in enumerate(args) if index != method.passed_object_position]
        if args and args[0].name == "self":
            return args[1:]
        return args

    @staticmethod
    def _is_private(node) -> bool:
        """Return whether is private."""
        return getattr(node, "visibility", "public") == "private"

    @staticmethod
    def _annotation_target(name: str) -> str:
        """Handle annotation target for the current generation context."""
        if name.isidentifier() and not keyword.iskeyword(name):
            return name
        return f"var[{name!r}]"

    @staticmethod
    def _parameter_target(name: str) -> str:
        """Handle parameter target for the current generation context."""
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

    @staticmethod
    def _opaque_dependency_class(type_name: str, c_kind: str | None) -> SemanticClass:
        """Build the semantic placeholder for one missing opaque dependency."""
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

    @staticmethod
    def _module_list(modules: SemanticModule | Iterable[SemanticModule] | None) -> list[SemanticModule]:
        """Normalize one semantic module or an iterable to a list."""
        if modules is None:
            return []
        if isinstance(modules, SemanticModule):
            return [modules]
        return list(modules)


_DEFAULT_PRINTER = PyiPrinter()


def emit_module(module: SemanticModule, *, normalize_fortran_public_names: bool = False) -> str:
    """Emit one semantic module through the default stateless printer."""
    if normalize_fortran_public_names:
        return PyiPrinter(normalize_fortran_public_names=True).emit(module)
    return _DEFAULT_PRINTER.emit(module)


def opaque_dependency_modules(
    modules: SemanticModule | Iterable[SemanticModule],
    *,
    available_modules: Iterable[SemanticModule] | None = None,
) -> list[SemanticModule]:
    """Build missing opaque dependency modules required by emitted stubs."""
    source_modules = PyiPrinter._module_list(modules)
    known_modules = PyiPrinter._module_list(available_modules) if available_modules is not None else source_modules
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
            classes=[
                PyiPrinter._opaque_dependency_class(type_name, c_kind)
                for type_name, c_kind in sorted(type_kinds.items())
            ],
        )
        for module_name, type_kinds in sorted(dependencies.items())
    ]


def emit_module_stubs(
    modules: SemanticModule | Iterable[SemanticModule],
    *,
    available_modules: Iterable[SemanticModule] | None = None,
    normalize_fortran_public_names: bool = False,
) -> dict[str, str]:
    """Emit a mapping of module names to complete stub texts."""
    source_modules = PyiPrinter._module_list(modules)
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

    return {
        module_name: emit_module(
            module,
            normalize_fortran_public_names=normalize_fortran_public_names,
        ).strip()
        for module_name, module in emitted_modules.items()
    }
