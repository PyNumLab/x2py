"""Central ownership policy decisions for generated wrappers.

The wrapper generators still lower memory through the historical
``stack``/``heap``/``alias`` hints.  This module owns the higher-level policy
that decides who owns a value, how ownership crosses the Python/native
boundary, and which low-level hint the existing generators should use.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from enum import Enum
from typing import Any


OWNERSHIP_POLICY_METADATA = "ownership_policy"


class ObjectKind(str, Enum):
    SCALAR = "scalar"
    STRING = "string"
    NUMPY_ARRAY = "numpy_array"
    DERIVED_TYPE = "derived_type"
    MODULE_VARIABLE = "module_variable"
    DERIVED_FIELD = "derived_field"


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


class CodegenAction(str, Enum):
    DIRECT_VALUE = "direct_value"
    CALL_LOCAL_INPUT = "call_local_input"
    IN_PLACE_ARGUMENT = "in_place_argument"
    COPY_RETURN_ARRAY = "copy_return_array"
    SNAPSHOT_COPY_ARRAY = "snapshot_copy_array"
    BORROWED_VIEW = "borrowed_view"
    WRAPPER_INSTANCE = "wrapper_instance"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class OwnershipActionDispatcher:
    handlers: Mapping[CodegenAction, str]
    default_handler: str

    def handler_name(self, var: Any) -> tuple[OwnershipDecision, str]:
        decision = ownership_decision_for_codegen_variable(var)
        return decision, self.handlers.get(decision.codegen_action, self.default_handler)

    def dispatch(self, target: Any, var: Any, *args: Any, **kwargs: Any) -> Any:
        decision, handler_name = self.handler_name(var)
        handler = getattr(target, handler_name)
        return handler(var, decision, *args, **kwargs)


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
    TransferMode.COPY_RETURN: CodegenAction.COPY_RETURN_ARRAY,
    TransferMode.SNAPSHOT_COPY: CodegenAction.SNAPSHOT_COPY_ARRAY,
    TransferMode.BORROWED_VIEW: CodegenAction.BORROWED_VIEW,
    TransferMode.WRAPPER_INSTANCE: CodegenAction.WRAPPER_INSTANCE,
    TransferMode.BLOCKED: CodegenAction.BLOCKED,
}


@dataclass(frozen=True)
class OwnershipContext:
    location: str = "value"
    intent: str = "in"
    is_result: bool = False
    is_argument: bool = False
    is_field: bool = False
    is_module_variable: bool = False

    @classmethod
    def result(cls) -> OwnershipContext:
        return cls(location="result", intent="out", is_result=True)

    @classmethod
    def argument(cls, intent: str) -> OwnershipContext:
        return cls(location="argument", intent=str(intent).lower(), is_argument=True)

    @classmethod
    def field(cls) -> OwnershipContext:
        return cls(location="derived_field", intent="in", is_field=True)

    @classmethod
    def module_variable(cls) -> OwnershipContext:
        return cls(location="module_variable", intent="in", is_module_variable=True)


@dataclass(frozen=True)
class OwnershipDecision:
    kind: ObjectKind
    owner: OwnershipOwner
    transfer: TransferMode
    destruction: DestructionPolicy
    memory_handling: str = "stack"
    nullable: bool = False
    borrowed: bool = False
    mutates_native: bool = False
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

    @property
    def codegen_action(self) -> CodegenAction:
        return _CODEGEN_ACTION_BY_TRANSFER[self.transfer]


@dataclass(frozen=True)
class _StorageFacts:
    rank: int
    name: str
    allocatable: bool = False
    pointer: bool = False
    fortran_target: bool = False
    fortran_allocatable: bool = False
    is_ndarray: bool = False
    is_string: bool = False
    is_dotted: bool = False
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
            ObjectKind.MODULE_VARIABLE: self._module_variable_decision,
            ObjectKind.DERIVED_FIELD: self._derived_field_decision,
        }
        if handlers:
            self._handlers.update(handlers)

    def decide_semantic_type(self, semantic_type: Any, context: OwnershipContext) -> OwnershipDecision:
        facts = self._semantic_facts(semantic_type)
        return self._apply_overrides(self._decide(facts, context), facts)

    def decide_semantic_variable(
        self,
        variable: Any,
        context: OwnershipContext | None = None,
    ) -> OwnershipDecision:
        actual_context = context or self._semantic_variable_context(variable)
        return self.decide_semantic_type(variable.semantic_type, actual_context)

    def decide_semantic_function(self, function: Any, prefix: str = "") -> dict[str, OwnershipDecision]:
        name = f"{prefix}{function.name}"
        decisions = {
            f"{name}.{argument.name}": self.decide_semantic_variable(
                argument,
                OwnershipContext.argument(getattr(argument, "intent", "in")),
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

    def decide_codegen_variable(
        self,
        var: Any,
        context: OwnershipContext | None = None,
    ) -> OwnershipDecision:
        explicit = getattr(var, "ownership_decision", None)
        if isinstance(explicit, OwnershipDecision):
            return explicit
        facts = self._codegen_facts(var)
        actual_context = context or self._codegen_context(var)
        return self._apply_overrides(self._decide(facts, actual_context), facts)

    def memory_handling_for_semantic_type(self, semantic_type: Any, context: OwnershipContext) -> str:
        return self.decide_semantic_type(semantic_type, context).memory_handling

    def _decide(self, facts: _StorageFacts, context: OwnershipContext) -> OwnershipDecision:
        kind = self._kind(facts, context)
        return self._handlers[kind](facts, context)

    def _kind(self, facts: _StorageFacts, context: OwnershipContext) -> ObjectKind:
        if context.is_module_variable:
            return ObjectKind.MODULE_VARIABLE
        if context.is_field:
            return ObjectKind.DERIVED_FIELD
        if facts.rank > 0 or facts.is_ndarray:
            return ObjectKind.NUMPY_ARRAY
        if facts.is_string:
            return ObjectKind.STRING
        if facts.is_custom:
            return ObjectKind.DERIVED_TYPE
        return ObjectKind.SCALAR

    def _scalar_decision(self, facts: _StorageFacts, context: OwnershipContext) -> OwnershipDecision:
        if context.is_result or context.intent == "out":
            return OwnershipDecision(
                ObjectKind.SCALAR,
                OwnershipOwner.PYTHON,
                TransferMode.BY_VALUE,
                DestructionPolicy.PYTHON_REFCOUNT,
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

    def _string_decision(self, facts: _StorageFacts, context: OwnershipContext) -> OwnershipDecision:
        if context.is_result or context.intent == "out":
            return OwnershipDecision(
                ObjectKind.STRING,
                OwnershipOwner.PYTHON,
                TransferMode.COPY_RETURN,
                DestructionPolicy.PYTHON_REFCOUNT,
                reason="string output is copied into a Python string",
            )
        return self._scalar_decision(facts, context)

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
                memory_handling="heap",
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
                memory_handling="heap",
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
                memory_handling="heap",
                nullable=True,
                reason="allocatable array output is copied before native storage is released",
            )
        return OwnershipDecision(
            ObjectKind.NUMPY_ARRAY,
            OwnershipOwner.CALLER,
            TransferMode.CALL_LOCAL,
            DestructionPolicy.NONE,
            memory_handling="heap",
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
                memory_handling="alias",
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
                memory_handling="alias",
                nullable=True,
                reason="pointer array result is copied into Python-owned NumPy storage",
            )
        if context.intent in {"out", "inout"}:
            return OwnershipDecision(
                ObjectKind.NUMPY_ARRAY,
                OwnershipOwner.UNKNOWN,
                TransferMode.BLOCKED,
                DestructionPolicy.BLOCKED,
                memory_handling="alias",
                nullable=True,
                blocker=f"pointer array {context.intent} reassociation policy is unknown",
                reason="pointer array dummy reassociation needs explicit policy metadata",
            )
        return OwnershipDecision(
            ObjectKind.NUMPY_ARRAY,
            OwnershipOwner.CALLER,
            TransferMode.CALL_LOCAL,
            DestructionPolicy.NONE,
            memory_handling="alias",
            reason="pointer input is associated with caller storage only for the call",
        )

    def _derived_type_decision(self, facts: _StorageFacts, context: OwnershipContext) -> OwnershipDecision:
        if context.is_result or context.intent == "out":
            return OwnershipDecision(
                ObjectKind.DERIVED_TYPE,
                OwnershipOwner.WRAPPER,
                TransferMode.WRAPPER_INSTANCE,
                DestructionPolicy.WRAPPER_DEALLOC,
                reason="derived output is represented by a wrapper-owned native instance",
            )
        if context.intent == "inout":
            return OwnershipDecision(
                ObjectKind.DERIVED_TYPE,
                OwnershipOwner.WRAPPER,
                TransferMode.IN_PLACE,
                DestructionPolicy.WRAPPER_DEALLOC,
                mutates_native=True,
                reason="derived inout mutates the wrapper-owned native instance",
            )
        return OwnershipDecision(
            ObjectKind.DERIVED_TYPE,
            OwnershipOwner.WRAPPER,
            TransferMode.CALL_LOCAL,
            DestructionPolicy.NONE,
            reason="derived input is passed through its existing wrapper",
        )

    def _module_variable_decision(self, facts: _StorageFacts, context: OwnershipContext) -> OwnershipDecision:
        if facts.rank > 0 or facts.is_ndarray:
            if facts.pointer:
                return self._pointer_array_decision(facts, context)
            if facts.allocatable:
                return self._allocatable_array_decision(facts, context)
        return OwnershipDecision(
            ObjectKind.MODULE_VARIABLE,
            OwnershipOwner.NATIVE,
            TransferMode.BORROWED_VIEW,
            DestructionPolicy.NATIVE_OWNER,
            memory_handling="alias" if facts.rank > 0 else "stack",
            borrowed=True,
            reason="module variable storage is owned by native module state",
        )

    def _derived_field_decision(self, facts: _StorageFacts, context: OwnershipContext) -> OwnershipDecision:
        if facts.rank > 0 or facts.is_ndarray:
            if facts.pointer:
                return self._pointer_array_decision(facts, context)
            if facts.allocatable:
                return self._allocatable_array_decision(facts, context)
            return OwnershipDecision(
                ObjectKind.DERIVED_FIELD,
                OwnershipOwner.WRAPPER,
                TransferMode.BORROWED_VIEW,
                DestructionPolicy.WRAPPER_DEALLOC,
                borrowed=True,
                reason="array field storage is part of the containing wrapper instance",
            )
        return OwnershipDecision(
            ObjectKind.DERIVED_FIELD,
            OwnershipOwner.WRAPPER,
            TransferMode.BORROWED_VIEW,
            DestructionPolicy.WRAPPER_DEALLOC,
            borrowed=True,
            reason="field storage is part of the containing wrapper instance",
        )

    def _apply_overrides(self, decision: OwnershipDecision, facts: _StorageFacts) -> OwnershipDecision:
        metadata = facts.metadata or {}
        raw = metadata.get(OWNERSHIP_POLICY_METADATA)
        if not isinstance(raw, Mapping):
            return decision
        owner = self._enum_value(OwnershipOwner, raw.get("owner"), decision.owner)
        transfer = self._enum_value(TransferMode, raw.get("transfer"), decision.transfer)
        destruction = self._enum_value(DestructionPolicy, raw.get("destruction"), decision.destruction)
        memory_handling = self._memory_for_override(facts, transfer, decision.memory_handling)
        nullable = bool(raw.get("nullable", decision.nullable))
        borrowed = transfer is TransferMode.BORROWED_VIEW or bool(raw.get("borrowed", decision.borrowed))
        blocker = None if transfer is not TransferMode.BLOCKED else decision.blocker or "blocked by ownership policy"
        return replace(
            decision,
            owner=owner,
            transfer=transfer,
            destruction=destruction,
            memory_handling=memory_handling,
            nullable=nullable,
            borrowed=borrowed,
            blocker=blocker,
            reason=str(raw.get("reason", "explicit ownership policy metadata")),
        )

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
    def _memory_for_override(facts: _StorageFacts, transfer: TransferMode, default: str) -> str:
        if facts.pointer:
            return "alias"
        if facts.allocatable:
            return "heap"
        if transfer is TransferMode.BORROWED_VIEW and (facts.rank > 0 or facts.is_ndarray):
            return "alias"
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
            pointer=bool(getattr(array, "pointer", False)),
            fortran_target=bool(metadata.get("fortran_target")),
            fortran_allocatable=bool(metadata.get("fortran_allocatable")),
            is_string=is_string,
            is_custom=is_custom,
            metadata=metadata,
        )

    @staticmethod
    def _codegen_facts(var: Any) -> _StorageFacts:
        memory_handling = str(getattr(var, "memory_handling", "stack"))
        name = str(getattr(var, "name", ""))
        class_type = getattr(var, "class_type", None)
        class_name = type(class_type).__name__
        is_ndarray = bool(getattr(var, "is_ndarray", False))
        is_string = class_name == "StringType" or str(class_type) == "String"
        is_custom = class_name == "CustomDataType" or getattr(var, "cls_base", None) is not None
        return _StorageFacts(
            rank=int(getattr(var, "rank", 0) or 0),
            name=name,
            allocatable=memory_handling == "heap" and is_ndarray,
            pointer=memory_handling == "alias" and is_ndarray,
            is_ndarray=is_ndarray,
            is_string=is_string,
            is_dotted=type(var).__name__ == "DottedVariable",
            is_custom=is_custom,
            metadata={},
        )

    @staticmethod
    def _codegen_context(var: Any) -> OwnershipContext:
        if type(var).__name__ == "DottedVariable":
            return OwnershipContext.field()
        intent = str(getattr(var, "intent", "in")).lower()
        if intent == "out":
            return OwnershipContext.result()
        if bool(getattr(var, "is_argument", False)):
            return OwnershipContext.argument(intent)
        return OwnershipContext(location="value", intent=intent)

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


default_ownership_policy = OwnershipPolicyResolver()


def ownership_decision_for_codegen_variable(var: Any) -> OwnershipDecision:
    return default_ownership_policy.decide_codegen_variable(var)


def codegen_action_for_variable(var: Any) -> CodegenAction:
    return ownership_decision_for_codegen_variable(var).codegen_action
