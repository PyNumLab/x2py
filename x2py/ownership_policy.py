"""Complete wrapper boundary and storage policy before codegen lowering.

This module decides ownership, transfer, destruction, writeback, projection,
nullability, release responsibility, codegen action, and both contract-value
and boundary ``stack``/``heap``/``alias`` storage modes. Bridge and binding
generators consume these decisions through strict dispatch and do not
reconstruct policy from codegen datatypes.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from enum import Enum
from typing import Any


OWNERSHIP_POLICY_METADATA = "ownership_policy"
POINTER_POLICY_METADATA = "pointer_policy"
POINTER_POLICY_FIELDS = (
    "nullable",
    "transfer",
    "target_owner",
    "lifetime",
    "deallocation",
    "shape_source",
    "contiguity",
    "reassociation",
    "aliasing",
    "mutability",
)
PYTHON_VALUE_MUTABILITY_METADATA = "python_value_mutability"
PYTHON_VALUE_IMMUTABLE = "immutable"
PYI_PROJECTED_OUTPUT_METADATA = "pyi_projected_output"


class ObjectKind(str, Enum):
    SCALAR = "scalar"
    STRING = "string"
    NUMPY_ARRAY = "numpy_array"
    DERIVED_TYPE = "derived_type"


class OwnershipOwner(str, Enum):
    PYTHON = "python"
    CALLER = "caller"
    NATIVE = "native"
    WRAPPER = "wrapper"
    TEMPORARY = "temporary"
    UNKNOWN = "unknown"


class TransferMode(str, Enum):
    BY_VALUE = "by_value"
    IN_PLACE = "in_place"
    COPY_RETURN = "copy_return"
    SNAPSHOT_COPY = "snapshot_copy"
    BORROWED_VIEW = "borrowed_view"
    CALL_LOCAL = "call_local"
    WRAPPER_INSTANCE = "wrapper_instance"
    BLOCKED = "blocked"


class DestructionPolicy(str, Enum):
    PYTHON_REFCOUNT = "python_refcount"
    CALLER = "caller"
    WRAPPER_DEALLOC = "wrapper_dealloc"
    NATIVE_OWNER = "native_owner"
    CALL_LOCAL = "call_local"
    NONE = "none"
    BLOCKED = "blocked"


class StorageMode(str, Enum):
    STACK = "stack"
    HEAP = "heap"
    ALIAS = "alias"


class CodegenAction(str, Enum):
    DIRECT_VALUE = "direct_value"
    CALL_LOCAL_INPUT = "call_local_input"
    IN_PLACE_ARGUMENT = "in_place_argument"
    IDENTITY_OUTPUT = "identity_output"
    HIDDEN_OUTPUT = "hidden_output"
    COPY_IN_OUT = "copy_in_out"
    COPY_OUT = "copy_out"
    SNAPSHOT_COPY = "snapshot_copy"
    BORROWED_VIEW = "borrowed_view"
    WRAPPER_INSTANCE = "wrapper_instance"
    BLOCKED = "blocked"


class AssignmentMode(str, Enum):
    NONE = "none"
    VALUE_COPY = "value_copy"
    ALIAS = "alias"


class SetterAction(str, Enum):
    WRITE_THROUGH = "write_through"
    REJECT_REPLACEMENT = "reject_replacement"
    OMIT = "omit"


@dataclass(frozen=True)
class PolicyActionDispatcher:
    handlers: Mapping[tuple[ObjectKind, CodegenAction], str]

    def handler_name_for_decision(self, decision: OwnershipDecision, name: str) -> str:
        key = (decision.kind, decision.codegen_action)
        try:
            return self.handlers[key]
        except KeyError:
            raise ValueError(
                f"No policy codegen handler for {name!r}: {decision.kind.value}/{decision.codegen_action.value}"
            ) from None

    def handler_name(self, var: Any) -> tuple[OwnershipDecision, str]:
        decision = ownership_decision_for_codegen_variable(var)
        name = str(getattr(var, "name", type(var).__name__))
        return decision, self.handler_name_for_decision(decision, name)

    def dispatch(self, target: Any, var: Any, *args: Any, **kwargs: Any) -> Any:
        decision, handler_name = self.handler_name(var)
        handler = getattr(target, handler_name)
        return handler(var, decision, *args, **kwargs)

    def dispatch_decision(
        self,
        target: Any,
        subject: Any,
        decision: OwnershipDecision,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Dispatch an accessor or nested policy stored beside its subject."""
        name = str(getattr(subject, "name", getattr(subject, "python_name", type(subject).__name__)))
        handler = getattr(target, self.handler_name_for_decision(decision, name))
        return handler(subject, decision, *args, **kwargs)


@dataclass(frozen=True)
class PolicyProjectionDispatcher:
    handlers: Mapping[tuple[ObjectKind, CodegenAction, bool], str]

    def handler_name_for_decision(self, decision: OwnershipDecision, name: str) -> str:
        key = (decision.kind, decision.codegen_action, decision.projects_result)
        try:
            return self.handlers[key]
        except KeyError:
            raise ValueError(
                f"No projection handler for {name!r}: "
                f"{decision.kind.value}/{decision.codegen_action.value}/projects_result={decision.projects_result}"
            ) from None

    def dispatch(self, target: Any, var: Any, *args: Any, **kwargs: Any) -> Any:
        decision = ownership_decision_for_codegen_variable(var)
        name = str(getattr(var, "name", type(var).__name__))
        handler = getattr(target, self.handler_name_for_decision(decision, name))
        return handler(var, decision, *args, **kwargs)


@dataclass(frozen=True)
class SetterActionDispatcher:
    handlers: Mapping[SetterAction, str]

    def dispatch(self, target: Any, subject: Any, decision: OwnershipDecision, *args: Any) -> Any:
        try:
            handler_name = self.handlers[decision.setter_action]
        except KeyError:
            name = str(getattr(subject, "name", getattr(subject, "python_name", type(subject).__name__)))
            raise ValueError(f"No setter handler for {name!r}: {decision.setter_action.value}") from None
        return getattr(target, handler_name)(subject, decision, *args)


@dataclass(frozen=True)
class DestructionPolicyDispatcher:
    handlers: Mapping[DestructionPolicy, str]

    def dispatch(self, target: Any, subject: Any, decision: OwnershipDecision, *args: Any) -> Any:
        try:
            handler_name = self.handlers[decision.destruction]
        except KeyError:
            name = str(getattr(subject, "name", getattr(subject, "python_name", type(subject).__name__)))
            raise ValueError(f"No release handler for {name!r}: {decision.destruction.value}") from None
        return getattr(target, handler_name)(subject, decision, *args)


_STANDARD_SCALAR_TYPES = frozenset(
    {
        "Bool",
        "Byte",
        "CEnum",
        "Char",
        "Complex64",
        "Complex128",
        "Float16",
        "Float32",
        "Float64",
        "Float128",
        "Int",
        "Int8",
        "Int16",
        "Int32",
        "Int64",
        "UInt",
        "UInt8",
        "UInt16",
        "UInt32",
        "UInt64",
        "Void",
    }
)

_OWNER_LABELS = {
    OwnershipOwner.PYTHON: "Python-owned",
    OwnershipOwner.CALLER: "Caller-owned",
    OwnershipOwner.NATIVE: "Native-owned",
    OwnershipOwner.WRAPPER: "Wrapper-owned",
    OwnershipOwner.TEMPORARY: "Temporary",
    OwnershipOwner.UNKNOWN: "Unknown owner",
}

_CODEGEN_ACTION_BY_TRANSFER = {
    TransferMode.BY_VALUE: CodegenAction.DIRECT_VALUE,
    TransferMode.CALL_LOCAL: CodegenAction.CALL_LOCAL_INPUT,
    TransferMode.IN_PLACE: CodegenAction.IN_PLACE_ARGUMENT,
    TransferMode.COPY_RETURN: CodegenAction.COPY_OUT,
    TransferMode.SNAPSHOT_COPY: CodegenAction.SNAPSHOT_COPY,
    TransferMode.BORROWED_VIEW: CodegenAction.BORROWED_VIEW,
    TransferMode.WRAPPER_INSTANCE: CodegenAction.WRAPPER_INSTANCE,
    TransferMode.BLOCKED: CodegenAction.BLOCKED,
}

_VALID_DESTRUCTION_BY_OWNER_TRANSFER = {
    (OwnershipOwner.PYTHON, TransferMode.BY_VALUE): frozenset({DestructionPolicy.PYTHON_REFCOUNT}),
    (OwnershipOwner.PYTHON, TransferMode.COPY_RETURN): frozenset({DestructionPolicy.PYTHON_REFCOUNT}),
    (OwnershipOwner.PYTHON, TransferMode.SNAPSHOT_COPY): frozenset({DestructionPolicy.PYTHON_REFCOUNT}),
    (OwnershipOwner.CALLER, TransferMode.CALL_LOCAL): frozenset({DestructionPolicy.NONE, DestructionPolicy.CALL_LOCAL}),
    (OwnershipOwner.CALLER, TransferMode.IN_PLACE): frozenset({DestructionPolicy.CALLER}),
    (OwnershipOwner.NATIVE, TransferMode.BORROWED_VIEW): frozenset({DestructionPolicy.NATIVE_OWNER}),
    (OwnershipOwner.WRAPPER, TransferMode.CALL_LOCAL): frozenset({DestructionPolicy.NONE}),
    (OwnershipOwner.WRAPPER, TransferMode.IN_PLACE): frozenset({DestructionPolicy.WRAPPER_DEALLOC}),
    (OwnershipOwner.WRAPPER, TransferMode.BORROWED_VIEW): frozenset({DestructionPolicy.WRAPPER_DEALLOC}),
    (OwnershipOwner.WRAPPER, TransferMode.WRAPPER_INSTANCE): frozenset({DestructionPolicy.WRAPPER_DEALLOC}),
    (OwnershipOwner.TEMPORARY, TransferMode.CALL_LOCAL): frozenset({DestructionPolicy.CALL_LOCAL}),
}


@dataclass(frozen=True)
class OwnershipContext:
    location: str = "value"
    intent: str = "in"
    is_result: bool = False
    is_argument: bool = False
    is_field: bool = False
    is_module_variable: bool = False
    projects_result: bool = False
    python_visible: bool = True

    @classmethod
    def result(cls) -> OwnershipContext:
        return cls(location="result", intent="out", is_result=True)

    @classmethod
    def argument(
        cls,
        intent: str,
        *,
        projects_result: bool = False,
        python_visible: bool = True,
    ) -> OwnershipContext:
        return cls(
            location="argument",
            intent=str(intent).lower(),
            is_argument=True,
            projects_result=projects_result,
            python_visible=python_visible,
        )

    @classmethod
    def field(cls) -> OwnershipContext:
        return cls(location="derived_field", intent="in", is_field=True)

    @classmethod
    def module_variable(cls) -> OwnershipContext:
        return cls(location="module_variable", intent="in", is_module_variable=True)


def ownership_context_for_argument(function: Any, argument: Any) -> OwnershipContext:
    """Build full-signature policy context for one semantic argument."""
    projection = tuple(getattr(function, "projection", ()))
    argument_name = str(getattr(argument, "name", "")).casefold()
    mapping = next(
        (item for item in projection if str(getattr(item, "native_name", "")).casefold() == argument_name),
        None,
    )
    metadata = getattr(argument, "metadata", {}) or {}
    projects_result = bool(metadata.get(PYI_PROJECTED_OUTPUT_METADATA))
    projects_result |= mapping is not None and getattr(mapping, "result_position", None) is not None
    python_visible = mapping is None or getattr(mapping, "python_position", None) is not None
    return OwnershipContext.argument(
        getattr(argument, "intent", "in"),
        projects_result=projects_result,
        python_visible=python_visible,
    )


@dataclass(frozen=True)
class OwnershipDecision:
    kind: ObjectKind
    owner: OwnershipOwner
    transfer: TransferMode
    destruction: DestructionPolicy
    storage_mode: StorageMode = StorageMode.STACK
    boundary_storage_mode: StorageMode | None = None
    codegen_action: CodegenAction = CodegenAction.BLOCKED
    nullable: bool = False
    borrowed: bool = False
    mutates_native: bool = False
    projects_result: bool = False
    python_visible: bool = True
    assignment_mode: AssignmentMode = AssignmentMode.NONE
    setter_action: SetterAction = SetterAction.OMIT
    blocker: str | None = None
    reason: str = ""

    @property
    def owner_label(self) -> str:
        return _OWNER_LABELS[self.owner]

    @property
    def is_blocked(self) -> bool:
        return self.transfer is TransferMode.BLOCKED or self.destruction is DestructionPolicy.BLOCKED

    @property
    def is_copy_return(self) -> bool:
        return self.transfer in {TransferMode.COPY_RETURN, TransferMode.SNAPSHOT_COPY}


@dataclass(frozen=True)
class _StorageFacts:
    rank: int
    name: str
    allocatable: bool = False
    pointer: bool = False
    is_ndarray: bool = False
    is_string: bool = False
    is_custom: bool = False
    metadata: Mapping[str, Any] | None = None


Handler = Callable[[_StorageFacts, OwnershipContext], OwnershipDecision]


class OwnershipPolicyResolver:
    """Resolve ownership for semantic types and codegen variables."""

    def __init__(self, handlers: Mapping[ObjectKind, Handler] | None = None):
        self._handlers: dict[ObjectKind, Handler] = {
            ObjectKind.SCALAR: self._scalar_decision,
            ObjectKind.STRING: self._string_decision,
            ObjectKind.NUMPY_ARRAY: self._array_decision,
            ObjectKind.DERIVED_TYPE: self._derived_type_decision,
        }
        if handlers:
            self._handlers.update(handlers)

    def decide_semantic_type(self, semantic_type: Any, context: OwnershipContext) -> OwnershipDecision:
        facts = self._semantic_facts(semantic_type)
        decision = self._apply_overrides(self._decide(facts, context), facts)
        decision = self._validate_pointer_decision(decision, facts, context)
        decision = self._complete_immutable_policy(decision, facts, context)
        decision = self._validate_result_projection(decision, context)
        decision = self._validate_policy_combination(decision)
        return replace(
            decision,
            boundary_storage_mode=decision.boundary_storage_mode or decision.storage_mode,
            codegen_action=self._codegen_action(decision, context),
            projects_result=context.projects_result,
            python_visible=context.python_visible,
        )

    def decide_semantic_variable(
        self,
        variable: Any,
        context: OwnershipContext | None = None,
    ) -> OwnershipDecision:
        actual_context = context or self._semantic_variable_context(variable)
        return self.decide_semantic_type(variable.semantic_type, actual_context)

    def decide_semantic_getter(
        self,
        variable: Any,
        context: OwnershipContext,
    ) -> OwnershipDecision:
        """Decide the value exposed by a field or module-variable getter."""
        storage = self.decide_semantic_variable(variable, context)
        if storage.is_blocked or storage.kind in {ObjectKind.NUMPY_ARRAY, ObjectKind.DERIVED_TYPE}:
            return storage
        return self.decide_semantic_type(variable.semantic_type, OwnershipContext.result())

    def decide_semantic_setter(
        self,
        variable: Any,
        context: OwnershipContext,
    ) -> OwnershipDecision:
        """Decide setter availability and its incoming value conversion."""
        storage = self.decide_semantic_variable(variable, context)
        if storage.is_blocked:
            return replace(
                storage,
                assignment_mode=AssignmentMode.NONE,
                setter_action=SetterAction.OMIT,
            )
        incoming = self.decide_semantic_type(variable.semantic_type, OwnershipContext.argument("in"))
        return replace(
            incoming,
            assignment_mode=(
                AssignmentMode.ALIAS if storage.storage_mode is StorageMode.ALIAS else AssignmentMode.VALUE_COPY
            ),
            setter_action=self._setter_action(storage, incoming),
        )

    @staticmethod
    def _setter_action(storage: OwnershipDecision, incoming: OwnershipDecision) -> SetterAction:
        """Select Python property setter exposure from completed storage and input policy."""
        if storage.kind is ObjectKind.SCALAR:
            return SetterAction.WRITE_THROUGH
        if storage.kind is ObjectKind.DERIVED_TYPE and incoming.transfer is TransferMode.CALL_LOCAL:
            return SetterAction.WRITE_THROUGH
        return SetterAction.REJECT_REPLACEMENT

    def decide_semantic_function(self, function: Any, prefix: str = "") -> dict[str, OwnershipDecision]:
        name = f"{prefix}{function.name}"
        decisions = {
            f"{name}.{argument.name}": self.decide_semantic_variable(
                argument,
                ownership_context_for_argument(function, argument),
            )
            for argument in getattr(function, "arguments", ())
        }
        return_type = getattr(function, "return_type", None)
        if return_type is not None:
            decisions[f"{name}.return"] = self.decide_semantic_type(return_type, OwnershipContext.result())
        return decisions

    def decide_semantic_class(self, semantic_class: Any, prefix: str = "") -> dict[str, OwnershipDecision]:
        name = f"{prefix}{semantic_class.name}"
        decisions = {
            f"{name}.{field.name}": self.decide_semantic_variable(field, OwnershipContext.field())
            for field in getattr(semantic_class, "fields", ())
        }
        for nested in getattr(semantic_class, "classes", ()):
            decisions.update(self.decide_semantic_class(nested, prefix=f"{name}."))
        for method in getattr(semantic_class, "methods", ()):
            decisions.update(self.decide_semantic_function(method, prefix=f"{name}."))
        return decisions

    def decide_semantic_module(self, module: Any) -> dict[str, OwnershipDecision]:
        name = str(getattr(module, "name", "module"))
        decisions = {
            f"{name}.{variable.name}": self.decide_semantic_variable(
                variable,
                OwnershipContext.module_variable(),
            )
            for variable in getattr(module, "variables", ())
        }
        for semantic_class in getattr(module, "classes", ()):
            decisions.update(self.decide_semantic_class(semantic_class, prefix=f"{name}."))
        for function in getattr(module, "functions", ()):
            decisions.update(self.decide_semantic_function(function, prefix=f"{name}."))
        for overload_set in getattr(module, "overload_sets", ()):
            overload_name = f"{name}.{overload_set.name}"
            for procedure in getattr(overload_set, "procedures", ()):
                decisions.update(self.decide_semantic_function(procedure, prefix=f"{overload_name}."))
        return decisions

    def _decide(self, facts: _StorageFacts, context: OwnershipContext) -> OwnershipDecision:
        if context.is_module_variable:
            return self._module_variable_decision(facts, context)
        if context.is_field:
            return self._derived_field_decision(facts, context)
        kind = self._kind(facts, context)
        return self._handlers[kind](facts, context)

    def _kind(self, facts: _StorageFacts, context: OwnershipContext) -> ObjectKind:
        if facts.rank > 0 or facts.is_ndarray:
            return ObjectKind.NUMPY_ARRAY
        if facts.is_string:
            return ObjectKind.STRING
        if facts.is_custom:
            return ObjectKind.DERIVED_TYPE
        return ObjectKind.SCALAR

    def _scalar_decision(self, facts: _StorageFacts, context: OwnershipContext) -> OwnershipDecision:
        if facts.pointer:
            return self._pointer_scalar_decision(facts, context)
        if context.is_result:
            return OwnershipDecision(
                ObjectKind.SCALAR,
                OwnershipOwner.PYTHON,
                TransferMode.BY_VALUE,
                DestructionPolicy.PYTHON_REFCOUNT,
                reason="scalar output is returned as a Python value",
            )
        if context.intent == "out":
            if not context.projects_result:
                return OwnershipDecision(
                    ObjectKind.SCALAR,
                    OwnershipOwner.CALLER,
                    TransferMode.IN_PLACE,
                    DestructionPolicy.CALLER,
                    mutates_native=True,
                    reason="identity scalar output writes caller-provided storage",
                )
            return OwnershipDecision(
                ObjectKind.SCALAR,
                OwnershipOwner.PYTHON,
                TransferMode.BY_VALUE,
                DestructionPolicy.PYTHON_REFCOUNT,
                mutates_native=True,
                reason="scalar output is returned as a Python value",
            )
        if context.intent == "inout":
            return OwnershipDecision(
                ObjectKind.SCALAR,
                OwnershipOwner.CALLER,
                TransferMode.IN_PLACE,
                DestructionPolicy.CALLER,
                mutates_native=True,
                reason="scalar inout updates caller-visible storage",
            )
        return OwnershipDecision(
            ObjectKind.SCALAR,
            OwnershipOwner.CALLER,
            TransferMode.CALL_LOCAL,
            DestructionPolicy.NONE,
            reason="scalar input is converted for the call only",
        )

    @staticmethod
    def _pointer_scalar_decision(facts: _StorageFacts, context: OwnershipContext) -> OwnershipDecision:
        if context.is_result:
            return OwnershipDecision(
                ObjectKind.SCALAR,
                OwnershipOwner.PYTHON,
                TransferMode.SNAPSHOT_COPY,
                DestructionPolicy.PYTHON_REFCOUNT,
                storage_mode=StorageMode.ALIAS,
                nullable=True,
                reason="pointer scalar result is copied into a detached Python value",
            )
        if context.is_field or context.is_module_variable or context.intent in {"out", "inout"}:
            return OwnershipDecision(
                ObjectKind.SCALAR,
                OwnershipOwner.UNKNOWN,
                TransferMode.BLOCKED,
                DestructionPolicy.BLOCKED,
                storage_mode=StorageMode.ALIAS,
                nullable=True,
                blocker=f"pointer scalar {context.location} owner, lifetime, and reassociation policy are unknown",
                reason="pointer scalar output needs explicit policy metadata",
            )
        return OwnershipDecision(
            ObjectKind.SCALAR,
            OwnershipOwner.CALLER,
            TransferMode.CALL_LOCAL,
            DestructionPolicy.CALL_LOCAL,
            storage_mode=StorageMode.ALIAS,
            reason="pointer scalar input is associated with a wrapper temporary only for the call",
        )

    def _string_decision(self, facts: _StorageFacts, context: OwnershipContext) -> OwnershipDecision:
        if context.is_result:
            return OwnershipDecision(
                ObjectKind.STRING,
                OwnershipOwner.PYTHON,
                TransferMode.COPY_RETURN,
                DestructionPolicy.PYTHON_REFCOUNT,
                reason="string output is copied into a Python string",
            )
        if context.intent == "out":
            if not context.projects_result:
                return OwnershipDecision(
                    ObjectKind.STRING,
                    OwnershipOwner.TEMPORARY,
                    TransferMode.CALL_LOCAL,
                    DestructionPolicy.CALL_LOCAL,
                    mutates_native=True,
                    reason="identity string output uses temporary storage and discards native mutation",
                )
            return OwnershipDecision(
                ObjectKind.STRING,
                OwnershipOwner.PYTHON,
                TransferMode.COPY_RETURN,
                DestructionPolicy.PYTHON_REFCOUNT,
                mutates_native=True,
                reason="string output is copied into a Python string",
            )
        if context.intent == "inout":
            if not context.projects_result:
                return OwnershipDecision(
                    ObjectKind.STRING,
                    OwnershipOwner.TEMPORARY,
                    TransferMode.CALL_LOCAL,
                    DestructionPolicy.CALL_LOCAL,
                    mutates_native=True,
                    reason="string inout uses a mutable call-local copy and discards native mutation",
                )
            return OwnershipDecision(
                ObjectKind.STRING,
                OwnershipOwner.PYTHON,
                TransferMode.COPY_RETURN,
                DestructionPolicy.PYTHON_REFCOUNT,
                mutates_native=True,
                reason="immutable Python strings use copy-in/copy-out replacement for inout",
            )
        return OwnershipDecision(
            ObjectKind.STRING,
            OwnershipOwner.CALLER,
            TransferMode.CALL_LOCAL,
            DestructionPolicy.NONE,
            reason="string input is converted for the call only",
        )

    def _array_decision(self, facts: _StorageFacts, context: OwnershipContext) -> OwnershipDecision:
        if facts.pointer:
            return self._pointer_array_decision(facts, context)
        if facts.allocatable:
            return self._allocatable_array_decision(facts, context)
        if context.is_result:
            return OwnershipDecision(
                ObjectKind.NUMPY_ARRAY,
                OwnershipOwner.PYTHON,
                TransferMode.COPY_RETURN,
                DestructionPolicy.PYTHON_REFCOUNT,
                reason="array result is returned as Python-owned NumPy storage",
            )
        if context.intent in {"out", "inout"}:
            return OwnershipDecision(
                ObjectKind.NUMPY_ARRAY,
                OwnershipOwner.CALLER,
                TransferMode.IN_PLACE,
                DestructionPolicy.CALLER,
                mutates_native=True,
                reason="explicit-shape array output mutates caller storage",
            )
        return OwnershipDecision(
            ObjectKind.NUMPY_ARRAY,
            OwnershipOwner.CALLER,
            TransferMode.CALL_LOCAL,
            DestructionPolicy.NONE,
            reason="array input is borrowed for the duration of the call",
        )

    def _allocatable_array_decision(self, facts: _StorageFacts, context: OwnershipContext) -> OwnershipDecision:
        if context.is_field:
            return OwnershipDecision(
                ObjectKind.NUMPY_ARRAY,
                OwnershipOwner.WRAPPER,
                TransferMode.BORROWED_VIEW,
                DestructionPolicy.WRAPPER_DEALLOC,
                storage_mode=StorageMode.HEAP,
                boundary_storage_mode=StorageMode.ALIAS,
                nullable=True,
                borrowed=True,
                reason="allocatable field storage is owned by the containing wrapper instance",
            )
        if context.is_module_variable:
            return OwnershipDecision(
                ObjectKind.NUMPY_ARRAY,
                OwnershipOwner.NATIVE,
                TransferMode.BORROWED_VIEW,
                DestructionPolicy.NATIVE_OWNER,
                storage_mode=StorageMode.HEAP,
                boundary_storage_mode=StorageMode.ALIAS,
                nullable=True,
                borrowed=True,
                reason="allocatable module storage is owned by the Fortran module",
            )
        if context.is_result or context.intent in {"out", "inout"}:
            return OwnershipDecision(
                ObjectKind.NUMPY_ARRAY,
                OwnershipOwner.PYTHON,
                TransferMode.COPY_RETURN,
                DestructionPolicy.PYTHON_REFCOUNT,
                storage_mode=StorageMode.HEAP,
                nullable=True,
                reason="allocatable array output is copied before native storage is released",
            )
        return OwnershipDecision(
            ObjectKind.NUMPY_ARRAY,
            OwnershipOwner.CALLER,
            TransferMode.CALL_LOCAL,
            DestructionPolicy.NONE,
            storage_mode=StorageMode.HEAP,
            nullable=True,
            reason="allocatable array input is associated only for the call",
        )

    def _pointer_array_decision(self, facts: _StorageFacts, context: OwnershipContext) -> OwnershipDecision:
        if context.is_field or context.is_module_variable:
            return OwnershipDecision(
                ObjectKind.NUMPY_ARRAY,
                OwnershipOwner.UNKNOWN,
                TransferMode.BLOCKED,
                DestructionPolicy.BLOCKED,
                storage_mode=StorageMode.ALIAS,
                nullable=True,
                blocker="pointer array owner, lifetime, shape, and release policy are unknown",
                reason="persistent pointer arrays need explicit policy metadata",
            )
        if context.is_result:
            return OwnershipDecision(
                ObjectKind.NUMPY_ARRAY,
                OwnershipOwner.PYTHON,
                TransferMode.SNAPSHOT_COPY,
                DestructionPolicy.PYTHON_REFCOUNT,
                storage_mode=StorageMode.ALIAS,
                nullable=True,
                reason="pointer array result is copied into Python-owned NumPy storage",
            )
        if context.intent in {"out", "inout"}:
            return OwnershipDecision(
                ObjectKind.NUMPY_ARRAY,
                OwnershipOwner.UNKNOWN,
                TransferMode.BLOCKED,
                DestructionPolicy.BLOCKED,
                storage_mode=StorageMode.ALIAS,
                nullable=True,
                blocker=f"pointer array {context.intent} reassociation policy is unknown",
                reason="pointer array dummy reassociation needs explicit policy metadata",
            )
        return OwnershipDecision(
            ObjectKind.NUMPY_ARRAY,
            OwnershipOwner.CALLER,
            TransferMode.CALL_LOCAL,
            DestructionPolicy.NONE,
            storage_mode=StorageMode.ALIAS,
            reason="pointer input is associated with caller storage only for the call",
        )

    def _derived_type_decision(self, facts: _StorageFacts, context: OwnershipContext) -> OwnershipDecision:
        if context.is_result or (context.intent == "out" and context.projects_result and not context.python_visible):
            return OwnershipDecision(
                ObjectKind.DERIVED_TYPE,
                OwnershipOwner.WRAPPER,
                TransferMode.WRAPPER_INSTANCE,
                DestructionPolicy.WRAPPER_DEALLOC,
                storage_mode=StorageMode.STACK,
                boundary_storage_mode=StorageMode.ALIAS,
                reason="derived output is represented by a wrapper-owned native instance",
            )
        if context.intent == "out":
            return OwnershipDecision(
                ObjectKind.DERIVED_TYPE,
                OwnershipOwner.WRAPPER,
                TransferMode.IN_PLACE,
                DestructionPolicy.WRAPPER_DEALLOC,
                storage_mode=StorageMode.ALIAS,
                mutates_native=True,
                reason="identity derived output mutates the supplied wrapper instance",
            )
        if context.intent == "inout":
            return OwnershipDecision(
                ObjectKind.DERIVED_TYPE,
                OwnershipOwner.WRAPPER,
                TransferMode.IN_PLACE,
                DestructionPolicy.WRAPPER_DEALLOC,
                storage_mode=StorageMode.ALIAS,
                mutates_native=True,
                reason="derived inout mutates the wrapper-owned native instance",
            )
        return OwnershipDecision(
            ObjectKind.DERIVED_TYPE,
            OwnershipOwner.WRAPPER,
            TransferMode.CALL_LOCAL,
            DestructionPolicy.NONE,
            storage_mode=StorageMode.ALIAS,
            reason="derived input is passed through its existing wrapper",
        )

    def _module_variable_decision(self, facts: _StorageFacts, context: OwnershipContext) -> OwnershipDecision:
        if facts.pointer and facts.rank == 0:
            return self._pointer_scalar_decision(facts, context)
        if facts.rank > 0 or facts.is_ndarray:
            if facts.pointer:
                return self._pointer_array_decision(facts, context)
            if facts.allocatable:
                return self._allocatable_array_decision(facts, context)
        return OwnershipDecision(
            self._kind(facts, OwnershipContext()),
            OwnershipOwner.NATIVE,
            TransferMode.BORROWED_VIEW,
            DestructionPolicy.NATIVE_OWNER,
            storage_mode=StorageMode.ALIAS if facts.rank > 0 else StorageMode.STACK,
            borrowed=True,
            reason="module variable storage is owned by native module state",
        )

    def _derived_field_decision(self, facts: _StorageFacts, context: OwnershipContext) -> OwnershipDecision:
        if facts.pointer and facts.rank == 0:
            return self._pointer_scalar_decision(facts, context)
        if facts.rank > 0 or facts.is_ndarray:
            if facts.pointer:
                return self._pointer_array_decision(facts, context)
            if facts.allocatable:
                return self._allocatable_array_decision(facts, context)
            return OwnershipDecision(
                ObjectKind.NUMPY_ARRAY,
                OwnershipOwner.WRAPPER,
                TransferMode.BORROWED_VIEW,
                DestructionPolicy.WRAPPER_DEALLOC,
                storage_mode=StorageMode.STACK,
                boundary_storage_mode=StorageMode.ALIAS,
                borrowed=True,
                reason="array field storage is part of the containing wrapper instance",
            )
        return OwnershipDecision(
            self._kind(facts, OwnershipContext()),
            OwnershipOwner.WRAPPER,
            TransferMode.BORROWED_VIEW,
            DestructionPolicy.WRAPPER_DEALLOC,
            storage_mode=StorageMode.STACK,
            boundary_storage_mode=StorageMode.ALIAS if facts.is_custom else StorageMode.STACK,
            borrowed=True,
            reason="field storage is part of the containing wrapper instance",
        )

    def _apply_overrides(self, decision: OwnershipDecision, facts: _StorageFacts) -> OwnershipDecision:
        metadata = facts.metadata or {}
        raw = metadata.get(OWNERSHIP_POLICY_METADATA)
        pointer_policy = metadata.get(POINTER_POLICY_METADATA)
        if facts.pointer and isinstance(pointer_policy, Mapping):
            raw = {**(raw if isinstance(raw, Mapping) else {}), **pointer_policy}
        if not isinstance(raw, Mapping):
            return decision
        owner = self._enum_value(OwnershipOwner, raw.get("owner"), decision.owner)
        transfer = self._enum_value(TransferMode, raw.get("transfer"), decision.transfer)
        if facts.pointer and transfer is TransferMode.BORROWED_VIEW:
            return replace(
                decision,
                owner=OwnershipOwner.UNKNOWN,
                transfer=TransferMode.BLOCKED,
                destruction=DestructionPolicy.BLOCKED,
                storage_mode=StorageMode.ALIAS,
                nullable=bool(raw.get("nullable", True)),
                borrowed=False,
                blocker="borrowed pointer views need native-owner retention and stale-view invalidation",
                reason="borrowed pointer views are not implemented",
            )
        destruction = self._enum_value(DestructionPolicy, raw.get("destruction"), decision.destruction)
        storage_mode = self._storage_for_override(facts, transfer, decision.storage_mode)
        nullable = bool(raw.get("nullable", decision.nullable))
        borrowed = transfer is TransferMode.BORROWED_VIEW or bool(raw.get("borrowed", decision.borrowed))
        blocker = None if transfer is not TransferMode.BLOCKED else decision.blocker or "blocked by ownership policy"
        return replace(
            decision,
            owner=owner,
            transfer=transfer,
            destruction=destruction,
            storage_mode=storage_mode,
            nullable=nullable,
            borrowed=borrowed,
            blocker=blocker,
            reason=str(raw.get("reason", "explicit ownership policy metadata")),
        )

    @staticmethod
    def _validate_pointer_decision(
        decision: OwnershipDecision,
        facts: _StorageFacts,
        context: OwnershipContext,
    ) -> OwnershipDecision:
        if not facts.pointer or decision.is_blocked:
            return decision
        blocker = None
        if context.is_argument and context.intent in {"out", "inout"}:
            blocker = "pointer output and reassociation code generation is not implemented"
        elif facts.rank > 0 and (context.is_field or context.is_module_variable):
            blocker = "pointer array field and module snapshot accessors are not implemented"
        elif facts.rank == 0 and (context.is_field or context.is_module_variable):
            blocker = "scalar pointer field and module accessors are not implemented"
        elif context.is_result and decision.transfer is not TransferMode.SNAPSHOT_COPY:
            blocker = "pointer results currently require snapshot_copy transfer"
        elif context.is_argument and context.intent == "in" and decision.transfer is not TransferMode.CALL_LOCAL:
            blocker = "pointer input arguments currently require call_local transfer"
        if blocker is None:
            return decision
        return replace(
            decision,
            owner=OwnershipOwner.UNKNOWN,
            transfer=TransferMode.BLOCKED,
            destruction=DestructionPolicy.BLOCKED,
            borrowed=False,
            blocker=blocker,
            reason="requested pointer policy is not implemented by code generation",
        )

    @staticmethod
    def _complete_immutable_policy(
        decision: OwnershipDecision,
        facts: _StorageFacts,
        context: OwnershipContext,
    ) -> OwnershipDecision:
        metadata = facts.metadata or {}
        if metadata.get(PYTHON_VALUE_MUTABILITY_METADATA) != PYTHON_VALUE_IMMUTABLE:
            return decision
        if not context.is_argument or context.intent not in {"out", "inout"} or decision.is_blocked:
            return decision

        if facts.is_custom:
            if context.intent == "out" and context.projects_result:
                return replace(
                    decision,
                    owner=OwnershipOwner.WRAPPER,
                    transfer=TransferMode.WRAPPER_INSTANCE,
                    destruction=DestructionPolicy.WRAPPER_DEALLOC,
                    storage_mode=StorageMode.STACK,
                    boundary_storage_mode=StorageMode.ALIAS,
                    borrowed=False,
                    mutates_native=True,
                    reason="immutable derived output uses a new wrapper-owned native instance",
                )
            return replace(
                decision,
                owner=OwnershipOwner.UNKNOWN,
                transfer=TransferMode.BLOCKED,
                destruction=DestructionPolicy.BLOCKED,
                borrowed=False,
                blocker="immutable derived inout replacement is not implemented",
                reason="derived replacement needs an explicit native copy/finalization policy",
            )

        raw_policy = metadata.get(OWNERSHIP_POLICY_METADATA)
        explicit_transfer = raw_policy.get("transfer") if isinstance(raw_policy, Mapping) else None
        if explicit_transfer is None and context.projects_result:
            decision = replace(
                decision,
                owner=OwnershipOwner.PYTHON,
                transfer=TransferMode.COPY_RETURN,
                destruction=DestructionPolicy.PYTHON_REFCOUNT,
                borrowed=False,
                mutates_native=True,
                reason="immutable writable value uses a mutable native temporary and replacement return",
            )

        if decision.transfer is TransferMode.COPY_RETURN and context.projects_result:
            return replace(
                decision,
                owner=OwnershipOwner.PYTHON,
                destruction=DestructionPolicy.PYTHON_REFCOUNT,
                borrowed=False,
                mutates_native=True,
            )
        if decision.transfer is TransferMode.CALL_LOCAL:
            return replace(
                decision,
                owner=OwnershipOwner.TEMPORARY,
                destruction=DestructionPolicy.CALL_LOCAL,
                borrowed=False,
                mutates_native=True,
                reason="immutable writable value uses a call-local copy and discards native mutation",
            )

        return replace(
            decision,
            owner=OwnershipOwner.UNKNOWN,
            transfer=TransferMode.BLOCKED,
            destruction=DestructionPolicy.BLOCKED,
            borrowed=False,
            blocker=(
                "immutable writable values require a projected copy_return replacement "
                "or explicit call_local discarded mutation"
            ),
            reason="immutable writeback policy is incomplete or contradictory",
        )

    @staticmethod
    def _validate_result_projection(
        decision: OwnershipDecision,
        context: OwnershipContext,
    ) -> OwnershipDecision:
        if (
            decision.is_blocked
            or not context.is_argument
            or decision.transfer is not TransferMode.COPY_RETURN
            or context.projects_result
        ):
            return decision
        return replace(
            decision,
            owner=OwnershipOwner.UNKNOWN,
            transfer=TransferMode.BLOCKED,
            destruction=DestructionPolicy.BLOCKED,
            borrowed=False,
            blocker="copy_return argument policy requires an explicit projected result",
            reason="argument replacement has no Python result projection",
        )

    @staticmethod
    def _validate_policy_combination(decision: OwnershipDecision) -> OwnershipDecision:
        """Reject owner, transfer, and destruction triples with no implemented lifetime."""
        if decision.is_blocked:
            return replace(
                decision,
                owner=OwnershipOwner.UNKNOWN,
                transfer=TransferMode.BLOCKED,
                destruction=DestructionPolicy.BLOCKED,
                borrowed=False,
                blocker=decision.blocker or "blocked by ownership policy",
            )

        allowed = _VALID_DESTRUCTION_BY_OWNER_TRANSFER.get((decision.owner, decision.transfer))
        if allowed is not None and decision.destruction in allowed:
            return decision

        expected = (
            "no supported destruction policy"
            if allowed is None
            else "expected " + " or ".join(sorted(policy.value for policy in allowed))
        )
        triple = f"{decision.owner.value}/{decision.transfer.value}/{decision.destruction.value}"
        return replace(
            decision,
            owner=OwnershipOwner.UNKNOWN,
            transfer=TransferMode.BLOCKED,
            destruction=DestructionPolicy.BLOCKED,
            borrowed=False,
            blocker=f"ownership policy {triple} is contradictory or unsupported; {expected}",
            reason="ownership, boundary transfer, and release responsibility must form a supported triple",
        )

    @staticmethod
    def _codegen_action(decision: OwnershipDecision, context: OwnershipContext) -> CodegenAction:
        if decision.is_blocked:
            return CodegenAction.BLOCKED
        if context.is_argument and context.intent == "out":
            if not context.projects_result:
                return CodegenAction.IDENTITY_OUTPUT
            if context.python_visible and decision.transfer is TransferMode.IN_PLACE:
                return CodegenAction.IDENTITY_OUTPUT
            return CodegenAction.HIDDEN_OUTPUT
        if context.is_argument and context.intent == "inout" and decision.transfer is TransferMode.COPY_RETURN:
            return CodegenAction.COPY_IN_OUT
        return _CODEGEN_ACTION_BY_TRANSFER[decision.transfer]

    @staticmethod
    def _enum_value(enum_type: type[Enum], value: object, default: Any) -> Any:
        if value is None:
            return default
        try:
            return enum_type(str(value))
        except ValueError as exc:
            allowed = ", ".join(item.value for item in enum_type)
            raise ValueError(f"Unsupported ownership policy value {value!r}; expected one of: {allowed}") from exc

    @staticmethod
    def _storage_for_override(
        facts: _StorageFacts,
        transfer: TransferMode,
        default: StorageMode,
    ) -> StorageMode:
        if facts.pointer:
            return StorageMode.ALIAS
        if facts.allocatable:
            return StorageMode.HEAP
        if transfer is TransferMode.BORROWED_VIEW and (facts.rank > 0 or facts.is_ndarray):
            return StorageMode.ALIAS
        return default

    @staticmethod
    def _semantic_facts(semantic_type: Any) -> _StorageFacts:
        metadata = getattr(semantic_type, "metadata", {}) or {}
        storage = getattr(semantic_type, "storage", None)
        array = getattr(storage, "array", None) if storage is not None else None
        name = str(getattr(semantic_type, "name", ""))
        rank = int(getattr(semantic_type, "rank", 0) or 0)
        is_string = name == "String"
        is_custom = rank == 0 and not is_string and name not in _STANDARD_SCALAR_TYPES
        return _StorageFacts(
            rank=rank,
            name=name,
            allocatable=bool(getattr(array, "allocatable", False)),
            pointer=bool(getattr(array, "pointer", False) or metadata.get("fortran_pointer")),
            is_string=is_string,
            is_custom=is_custom,
            metadata=metadata,
        )

    @staticmethod
    def _semantic_variable_context(variable: Any) -> OwnershipContext:
        class_name = type(variable).__name__
        if class_name == "SemanticField":
            return OwnershipContext.field()
        if class_name == "SemanticArgument":
            return OwnershipContext.argument(getattr(variable, "intent", "in"))
        return OwnershipContext(location="value", intent=getattr(variable, "intent", "in"))


def set_ownership_metadata(
    metadata: dict[str, Any],
    *,
    owner: str | None = None,
    transfer: str | None = None,
    destruction: str | None = None,
) -> None:
    policy = metadata.setdefault(OWNERSHIP_POLICY_METADATA, {})
    if not isinstance(policy, dict):
        raise ValueError(f"{OWNERSHIP_POLICY_METADATA!r} metadata must be a dictionary")
    if owner is not None:
        policy["owner"] = OwnershipOwner(owner).value
    if transfer is not None:
        policy["transfer"] = TransferMode(transfer).value
    if destruction is not None:
        policy["destruction"] = DestructionPolicy(destruction).value


def set_pointer_policy_metadata(metadata: dict[str, Any], **policy_values: Any) -> None:
    """Store a complete semantic pointer policy after validating its shape."""
    missing = [name for name in POINTER_POLICY_FIELDS if name not in policy_values]
    extra = [name for name in policy_values if name not in POINTER_POLICY_FIELDS]
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing: {', '.join(missing)}")
        if extra:
            details.append(f"unexpected: {', '.join(extra)}")
        raise ValueError(f"PointerPolicy requires exactly {', '.join(POINTER_POLICY_FIELDS)} ({'; '.join(details)})")
    if not isinstance(policy_values["nullable"], bool):
        raise ValueError("PointerPolicy nullable must be a boolean")
    for name in POINTER_POLICY_FIELDS[1:]:
        if not isinstance(policy_values[name], str) or not policy_values[name]:
            raise ValueError(f"PointerPolicy {name} must be a non-empty string")
    TransferMode(policy_values["transfer"])
    metadata[POINTER_POLICY_METADATA] = dict(policy_values)
    metadata["fortran_pointer"] = True


default_ownership_policy = OwnershipPolicyResolver()


def ownership_decision_for_codegen_variable(var: Any) -> OwnershipDecision:
    decision = getattr(var, "ownership_decision", None)
    if decision is None:
        name = getattr(var, "name", type(var).__name__)
        raise ValueError(
            f"Codegen variable {name!r} is missing completed ownership policy; "
            "run complete_semantic_policies before ir2ast lowering"
        )
    return decision


def codegen_action_for_variable(var: Any) -> CodegenAction:
    return ownership_decision_for_codegen_variable(var).codegen_action
