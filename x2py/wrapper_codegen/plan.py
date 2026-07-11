"""Frozen wrapper-plan records for the isolated wrapper-plan route."""

from __future__ import annotations

from dataclasses import dataclass

from x2py.semantics.ownership import CodegenAction, NativeBarrierAction, PythonBarrierAction


@dataclass(frozen=True)
class ActionHandlerPlan:
    """One completed semantic action mapped to one implementation handler."""

    action: CodegenAction | NativeBarrierAction | PythonBarrierAction
    handler_name: str


@dataclass(frozen=True)
class HandlerRegistryPlan:
    """Handler names keyed by existing completed semantic action values."""

    python_action_handlers: tuple[ActionHandlerPlan, ...]
    native_action_handlers: tuple[ActionHandlerPlan, ...]
    result_action_handlers: tuple[ActionHandlerPlan, ...]


@dataclass(frozen=True)
class BindingHandoffPlan:
    """Symbolic handoff produced by the binding layer for bridge consumption."""

    owner_path: str
    produced_role: str
    consumed_role: str
    python_action: PythonBarrierAction
    handler_name: str


@dataclass(frozen=True)
class BridgeAbiSlotPlan:
    """One deterministic bridge ABI slot for an argument transfer."""

    owner_path: str
    index: int
    symbolic_role: str
    native_action: NativeBarrierAction
    handler_name: str


@dataclass(frozen=True)
class BridgeAbiPlan:
    """Bridge ABI slot collection for one function."""

    owner_path: str
    slots: tuple[BridgeAbiSlotPlan, ...]


@dataclass(frozen=True)
class NativeCallSlotPlan:
    """Native-call slot copied from completed scalar policy."""

    owner_path: str
    native_position: int
    source_kind: str
    python_position: int | None
    python_name: str | None
    native_name: str
    value_kind: str
    symbolic_role: str
    native_action: NativeBarrierAction
    codegen_action: CodegenAction


@dataclass(frozen=True)
class ArgumentTransferPlan:
    """Single Python-to-native transfer plan for one argument."""

    owner_path: str
    python_name: str
    native_name: str
    python_position: int
    native_position: int
    semantic_type_name: str
    python_action: PythonBarrierAction
    native_action: NativeBarrierAction
    codegen_action: CodegenAction
    binding_handoff: BindingHandoffPlan
    bridge_abi_slot: BridgeAbiSlotPlan | None
    native_call_slot: NativeCallSlotPlan | None


@dataclass(frozen=True)
class ResultPlan:
    """Symbolic result conversion plan for one function result."""

    owner_path: str
    semantic_type_name: str
    codegen_action: CodegenAction
    python_action: PythonBarrierAction
    native_action: NativeBarrierAction
    native_result_role: str
    python_result_role: str
    handler_name: str


@dataclass(frozen=True)
class LifecycleActionPlan:
    """Symbolic lifecycle action that consumes a previously available role."""

    owner_path: str
    phase: str
    source_role: str
    handler_name: str


@dataclass(frozen=True)
class FunctionPlan:
    """Wrapper plan for one semantic function owner."""

    owner_path: str
    python_name: str
    native_name: str
    external: bool
    bind_target: str | None
    arguments: tuple[ArgumentTransferPlan, ...]
    result: ResultPlan | None
    bridge_abi: BridgeAbiPlan
    available_roles: tuple[str, ...]
    writeback_actions: tuple[LifecycleActionPlan, ...] = ()
    cleanup_actions: tuple[LifecycleActionPlan, ...] = ()
    release_actions: tuple[LifecycleActionPlan, ...] = ()


@dataclass(frozen=True)
class ModulePlan:
    """Wrapper plan for one generation unit."""

    owner_path: str
    functions: tuple[FunctionPlan, ...]
    handler_registry: HandlerRegistryPlan


@dataclass(frozen=True)
class WrapperPlanDiagnostic:
    """One owner-path diagnostic produced before backend emission."""

    owner_path: str
    code: str
    message: str


@dataclass(frozen=True)
class WrapperPlanSupportBlocker:
    """One stable unsupported-owner reason for the wrapper-plan route."""

    owner_path: str
    reason: str


@dataclass(frozen=True)
class WrapperPlanSupportReport:
    """Whole-generation-unit support report for route selection callers."""

    owner_path: str
    blockers: tuple[WrapperPlanSupportBlocker, ...] = ()

    @property
    def supported(self) -> bool:
        """Return whether the whole generation unit is supported."""
        return not self.blockers
