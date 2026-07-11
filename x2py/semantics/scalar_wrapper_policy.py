"""Completed first-lane scalar wrapper policy records."""

from __future__ import annotations

from dataclasses import dataclass

from x2py.types.numpy import SEMANTIC_SCALAR_TYPE_NAMES
from x2py.semantics import models
from x2py.semantics.metadata import BIND_TARGET_METADATA
from x2py.semantics.ownership import (
    CodegenAction,
    NativeBarrierAction,
    ObjectKind,
    OwnershipDecision,
    PythonBarrierAction,
    StorageMode,
)


@dataclass(frozen=True)
class ScalarWrapperArgumentPolicy:
    """Completed scalar wrapper policy for one Python-visible argument."""

    owner_path: str
    name: str
    python_name: str
    native_name: str
    python_position: int
    native_position: int
    semantic_type_name: str
    rank: int
    optional: bool
    ownership: OwnershipDecision
    codegen_action: CodegenAction
    python_barrier_action: PythonBarrierAction
    native_barrier_action: NativeBarrierAction
    storage_mode: StorageMode
    boundary_storage_mode: StorageMode
    projects_result: bool
    python_visible: bool


@dataclass(frozen=True)
class ScalarWrapperResultPolicy:
    """Completed scalar wrapper policy for one native scalar result."""

    owner_path: str
    semantic_type_name: str
    rank: int
    ownership: OwnershipDecision
    codegen_action: CodegenAction
    python_barrier_action: PythonBarrierAction
    native_barrier_action: NativeBarrierAction
    storage_mode: StorageMode
    boundary_storage_mode: StorageMode


@dataclass(frozen=True)
class ScalarWrapperNativeCallSlotPolicy:
    """Completed native-call slot for first-lane scalar wrapper planning."""

    owner_path: str
    native_position: int
    source_kind: str
    python_position: int | None
    python_name: str | None
    native_name: str
    value_kind: str
    native_barrier_action: NativeBarrierAction
    codegen_action: CodegenAction


@dataclass(frozen=True)
class ScalarWrapperFunctionPolicy:
    """Completed first-lane scalar wrapper policy for one semantic function."""

    owner_path: str
    python_name: str
    native_name: str
    external: bool
    bind_target: str | None
    supported: bool
    arguments: tuple[ScalarWrapperArgumentPolicy, ...] = ()
    result: ScalarWrapperResultPolicy | None = None
    native_call_slots: tuple[ScalarWrapperNativeCallSlotPolicy, ...] = ()
    blockers: tuple[str, ...] = ()
    writeback_actions: tuple[str, ...] = ()
    cleanup_actions: tuple[str, ...] = ()
    release_actions: tuple[str, ...] = ()


def completed_scalar_wrapper_policy(function: models.SemanticFunction) -> ScalarWrapperFunctionPolicy:
    """Return a completed scalar wrapper policy or fail before planning."""

    policy = function.metadata.get(models.RESOLVED_SCALAR_WRAPPER_POLICY_METADATA)
    if not isinstance(policy, ScalarWrapperFunctionPolicy):
        raise ValueError(
            f"Semantic function {function.name!r} is missing completed scalar wrapper policy; "
            "run complete_semantic_policies before wrapper planning"
        )
    if not policy.supported:
        details = "; ".join(policy.blockers) or "unsupported first-lane scalar wrapper policy"
        raise ValueError(f"Semantic function {policy.owner_path!r} has blocked scalar wrapper policy: {details}")
    return policy


def build_scalar_wrapper_function_policy(
    function: models.SemanticFunction,
    *,
    owner_path: str,
) -> ScalarWrapperFunctionPolicy:
    """Build a typed scalar-wrapper policy from completed post-IR decisions."""

    argument_native_positions, native_call_slots, slot_blockers = _native_call_slot_policies(function, owner_path)
    arguments, argument_blockers = _argument_policies(function, owner_path, argument_native_positions)
    result, result_blockers = _result_policy(function, owner_path)
    blockers = (
        _function_shape_blockers(function)
        + argument_blockers
        + result_blockers
        + slot_blockers
        + _lifecycle_blockers(arguments)
    )
    return ScalarWrapperFunctionPolicy(
        owner_path=owner_path,
        python_name=function.name,
        native_name=_native_name(function),
        external=_is_external(function),
        bind_target=_bind_target(function),
        supported=not blockers,
        arguments=tuple(arguments),
        result=result,
        native_call_slots=tuple(native_call_slots),
        blockers=tuple(blockers),
    )


def _argument_policies(
    function: models.SemanticFunction,
    owner_path: str,
    argument_native_positions: dict[int, int],
) -> tuple[list[ScalarWrapperArgumentPolicy], tuple[str, ...]]:
    policies: list[ScalarWrapperArgumentPolicy] = []
    blockers: list[str] = []
    for python_position, argument in enumerate(function.arguments):
        decision = _ownership_decision(argument, models.RESOLVED_OWNERSHIP_POLICY_METADATA)
        if decision is None:
            blockers.append(f"argument {argument.name!r} is missing completed ownership policy")
            continue
        blockers.extend(_argument_blockers(argument, decision))
        native_position = argument_native_positions.get(python_position)
        if native_position is None:
            blockers.append(f"argument {argument.name!r} has no completed native-call slot")
            native_position = -1
        policies.append(
            ScalarWrapperArgumentPolicy(
                owner_path=f"{owner_path}.{argument.name}",
                name=argument.name,
                python_name=argument.name,
                native_name=_argument_native_name(function, python_position, argument),
                python_position=python_position,
                native_position=native_position,
                semantic_type_name=argument.semantic_type.name,
                rank=int(argument.semantic_type.rank or 0),
                optional=argument.optional,
                ownership=decision,
                codegen_action=decision.codegen_action,
                python_barrier_action=decision.python_barrier_action,
                native_barrier_action=decision.native_barrier_action,
                storage_mode=decision.storage_mode,
                boundary_storage_mode=decision.boundary_storage_mode or decision.storage_mode,
                projects_result=decision.projects_result,
                python_visible=decision.python_visible,
            )
        )
    return policies, tuple(blockers)


def _result_policy(
    function: models.SemanticFunction,
    owner_path: str,
) -> tuple[ScalarWrapperResultPolicy | None, tuple[str, ...]]:
    if function.return_type is None:
        return None, ("first scalar lane requires one scalar result",)
    decision = function.metadata.get(models.RESOLVED_RETURN_OWNERSHIP_POLICY_METADATA)
    if not isinstance(decision, OwnershipDecision):
        return None, ("function result is missing completed ownership policy",)
    blockers = _result_blockers(function.return_type, decision)
    return (
        ScalarWrapperResultPolicy(
            owner_path=f"{owner_path}.return",
            semantic_type_name=function.return_type.name,
            rank=int(function.return_type.rank or 0),
            ownership=decision,
            codegen_action=decision.codegen_action,
            python_barrier_action=decision.python_barrier_action,
            native_barrier_action=decision.native_barrier_action,
            storage_mode=decision.storage_mode,
            boundary_storage_mode=decision.boundary_storage_mode or decision.storage_mode,
        ),
        tuple(blockers),
    )


def _native_call_slot_policies(
    function: models.SemanticFunction,
    owner_path: str,
) -> tuple[dict[int, int], tuple[ScalarWrapperNativeCallSlotPolicy, ...], tuple[str, ...]]:
    if function.projection:
        return _projected_native_call_slot_policies(function, owner_path)
    return _implicit_native_call_slot_policies(function, owner_path)


def _projected_native_call_slot_policies(
    function: models.SemanticFunction,
    owner_path: str,
) -> tuple[dict[int, int], tuple[ScalarWrapperNativeCallSlotPolicy, ...], tuple[str, ...]]:
    slots: list[ScalarWrapperNativeCallSlotPolicy] = []
    blockers: list[str] = []
    positions: dict[int, int] = {}
    for mapping in sorted(
        function.projection, key=lambda item: item.native_position if item.native_position is not None else -1
    ):
        native_position = mapping.native_position
        python_position = mapping.python_position
        if not isinstance(native_position, int):
            blockers.append("native-call projection is missing a native position")
            continue
        if mapping.result_position is not None or python_position is None:
            blockers.append(f"native-call slot {native_position} is not a first-lane Python argument projection")
            continue
        if not 0 <= python_position < len(function.arguments):
            blockers.append(f"native-call slot {native_position} references argument position {python_position}")
            continue
        argument = function.arguments[python_position]
        decision = _ownership_decision(argument, models.RESOLVED_OWNERSHIP_POLICY_METADATA)
        if decision is None:
            blockers.append(f"native-call slot {native_position} references argument without completed policy")
            continue
        value_kind = mapping.value_kind or "arg"
        if value_kind not in {"addr", "arg"}:
            blockers.append(f"native-call slot {native_position} uses unsupported scalar value kind {value_kind!r}")
        if python_position in positions:
            blockers.append(f"argument {argument.name!r} appears in more than one native-call slot")
        positions[python_position] = native_position
        slots.append(
            ScalarWrapperNativeCallSlotPolicy(
                owner_path=f"{owner_path}.{argument.name}",
                native_position=native_position,
                source_kind="projection",
                python_position=python_position,
                python_name=mapping.python_name or argument.name,
                native_name=mapping.native_name or argument.name,
                value_kind=value_kind,
                native_barrier_action=decision.native_barrier_action,
                codegen_action=decision.codegen_action,
            )
        )
    blockers.extend(_native_position_blockers(slot.native_position for slot in slots))
    return positions, tuple(slots), tuple(blockers)


def _implicit_native_call_slot_policies(
    function: models.SemanticFunction,
    owner_path: str,
) -> tuple[dict[int, int], tuple[ScalarWrapperNativeCallSlotPolicy, ...], tuple[str, ...]]:
    slots: list[ScalarWrapperNativeCallSlotPolicy] = []
    positions: dict[int, int] = {}
    blockers: list[str] = []
    for position, argument in enumerate(function.arguments):
        decision = _ownership_decision(argument, models.RESOLVED_OWNERSHIP_POLICY_METADATA)
        if decision is None:
            blockers.append(f"implicit native-call slot {position} references argument without completed policy")
            continue
        positions[position] = position
        slots.append(
            ScalarWrapperNativeCallSlotPolicy(
                owner_path=f"{owner_path}.{argument.name}",
                native_position=position,
                source_kind="implicit",
                python_position=position,
                python_name=argument.name,
                native_name=argument.name,
                value_kind="arg",
                native_barrier_action=decision.native_barrier_action,
                codegen_action=decision.codegen_action,
            )
        )
    return positions, tuple(slots), tuple(blockers)


def _argument_blockers(argument: models.SemanticArgument, decision: OwnershipDecision) -> tuple[str, ...]:
    blockers: list[str] = []
    if decision.is_blocked:
        blockers.append(
            f"argument {argument.name!r} has blocked ownership policy: {decision.blocker or decision.reason}"
        )
    if not _is_first_lane_scalar_type(argument.semantic_type):
        blockers.append(f"argument {argument.name!r} is not a first-lane primitive scalar")
    if argument.optional:
        blockers.append(f"argument {argument.name!r} is optional")
    if not decision.python_visible:
        blockers.append(f"argument {argument.name!r} is not Python-visible")
    if decision.kind is not ObjectKind.SCALAR:
        blockers.append(f"argument {argument.name!r} policy kind is {decision.kind.value}, not scalar")
    if decision.python_barrier_action is not PythonBarrierAction.SCALAR_VALUE:
        blockers.append(
            f"argument {argument.name!r} Python action is {decision.python_barrier_action.value}, not scalar_value"
        )
    if decision.native_barrier_action not in {
        NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS,
        NativeBarrierAction.PASS_VALUE,
    }:
        blockers.append(
            f"argument {argument.name!r} native action is {decision.native_barrier_action.value}, "
            "not pass_call_local_address or pass_value"
        )
    if decision.projects_result:
        blockers.append(f"argument {argument.name!r} projects a result")
    return tuple(blockers)


def _result_blockers(semantic_type: models.SemanticType, decision: OwnershipDecision) -> tuple[str, ...]:
    blockers: list[str] = []
    if decision.is_blocked:
        blockers.append(f"result has blocked ownership policy: {decision.blocker or decision.reason}")
    if not _is_first_lane_scalar_type(semantic_type):
        blockers.append("result is not a first-lane primitive scalar")
    if decision.kind is not ObjectKind.SCALAR:
        blockers.append(f"result policy kind is {decision.kind.value}, not scalar")
    if decision.codegen_action is not CodegenAction.DIRECT_VALUE:
        blockers.append(f"result codegen action is {decision.codegen_action.value}, not direct_value")
    if decision.python_barrier_action is not PythonBarrierAction.NONE:
        blockers.append(f"result Python action is {decision.python_barrier_action.value}, not none")
    if decision.native_barrier_action is not NativeBarrierAction.NONE:
        blockers.append(f"result native action is {decision.native_barrier_action.value}, not none")
    return tuple(blockers)


def _function_shape_blockers(function: models.SemanticFunction) -> tuple[str, ...]:
    blockers: list[str] = []
    if function.visibility != "public":
        blockers.append("function is not public")
    if isinstance(function, models.SemanticMethod):
        blockers.append("methods are outside the first scalar lane")
    if function.locals:
        blockers.append("function locals are outside the first scalar lane")
    if function.contracts:
        blockers.append("function contracts are outside the first scalar lane")
    return tuple(blockers)


def _lifecycle_blockers(arguments: list[ScalarWrapperArgumentPolicy]) -> tuple[str, ...]:
    blockers: list[str] = []
    for argument in arguments:
        if argument.projects_result:
            blockers.append(f"argument {argument.name!r} requires writeback/result lifecycle policy")
    return tuple(blockers)


def _native_position_blockers(native_positions: object) -> tuple[str, ...]:
    positions = tuple(native_positions)
    if sorted(positions) != list(range(len(positions))):
        return ("native-call slots must cover each native position exactly once in order",)
    return ()


def _ownership_decision(owner: object, metadata_key: str) -> OwnershipDecision | None:
    decision = getattr(owner, "metadata", {}).get(metadata_key)
    return decision if isinstance(decision, OwnershipDecision) else None


def _is_first_lane_scalar_type(semantic_type: models.SemanticType) -> bool:
    scalar_name = semantic_type.dtype or semantic_type.name
    return bool(
        int(semantic_type.rank or 0) == 0
        and semantic_type.name != "String"
        and scalar_name in SEMANTIC_SCALAR_TYPE_NAMES
    )


def _native_name(function: models.SemanticFunction) -> str:
    return str(function.native_name or function.origin.native_name or function.name)


def _bind_target(function: models.SemanticFunction) -> str | None:
    target = function.metadata.get(BIND_TARGET_METADATA)
    return str(target) if target is not None else None


def _is_external(function: models.SemanticFunction) -> bool:
    return bool(function.origin.source_language == "fortran" and function.origin.native_scope is None)


def _argument_native_name(
    function: models.SemanticFunction,
    python_position: int,
    argument: models.SemanticArgument,
) -> str:
    for mapping in function.projection:
        if mapping.python_position == python_position:
            return mapping.native_name or argument.name
    return argument.name
