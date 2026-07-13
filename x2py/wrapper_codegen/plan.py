"""Editable wrapper-plan records for the isolated wrapper-plan route."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from x2py.semantics.ownership import (
    AssignmentMode,
    CodegenAction,
    NativeBarrierAction,
    PythonBarrierAction,
    SetterAction,
)
from x2py.semantics.wrapper_policy import (
    ArgumentHandoffMode,
    BridgeDataAction,
    ModuleGetterAction,
    OptionalMode,
    PythonExceptionKind,
    WritebackPhase,
)
from x2py.stage_values import StageRecord


class DatatypeFamily(Enum):
    """Backend-relevant datatype family copied from semantic type facts."""

    BOOL = "bool"
    INTEGER = "integer"
    REAL = "real"
    COMPLEX = "complex"
    STRING = "string"


@dataclass
class BindingStatusErrorPlan(StageRecord):
    """Binding-owned post-call native status projection."""

    status_role: str
    message_role: str | None
    success: int
    exception_kind: PythonExceptionKind


@dataclass
class BindingModulePlan(StageRecord):
    """Binding-facing module facts."""

    owner_path: str


@dataclass
class BridgeModulePlan(StageRecord):
    """Bridge-facing module facts."""

    owner_path: str


@dataclass
class BindingModuleVariablePlan(StageRecord):
    """Python module-attribute behavior for one state value."""

    python_names: tuple[str, ...]
    getter_action: ModuleGetterAction
    setter_action: SetterAction
    initializer: Any
    constant_value: Any


@dataclass
class BridgeModuleVariablePlan(StageRecord):
    """Native module-variable access behavior selected by completed policy."""

    native_name: str
    native_module: str
    getter_action: ModuleGetterAction
    native_assignment: AssignmentMode
    descriptor_kind: str | None
    getter_role: str | None
    setter_role: str | None


@dataclass
class ModuleVariablePlan(StageRecord):
    """One concise shared module-variable plan."""

    owner_path: str
    symbol_name: str
    semantic_type_name: str
    datatype_family: DatatypeFamily
    binding: BindingModuleVariablePlan
    bridge: BridgeModuleVariablePlan


@dataclass
class BindingFunctionPlan(StageRecord):
    """Binding-facing function facts."""

    python_name: str
    hold_gil: bool
    status_error: BindingStatusErrorPlan | None


@dataclass
class BridgeFunctionPlan(StageRecord):
    """Bridge-facing function facts."""

    native_name: str
    external: bool
    native_module: str | None
    native_is_subroutine: bool


@dataclass
class BindingArgumentPlan(StageRecord):
    """Python input conversion and binding-to-bridge handoff facts."""

    python_name: str
    python_action: PythonBarrierAction
    handoff_role: str
    optional_mode: OptionalMode
    nullable: bool
    writable: bool
    descriptor_boundary: bool


@dataclass
class BridgeArgumentPlan(StageRecord):
    """Bridge ABI and native argument conversion facts."""

    native_name: str
    native_action: NativeBarrierAction
    handoff_mode: ArgumentHandoffMode
    data_action: BridgeDataAction
    copy_reason: str | None
    abi_position: int
    handoff_role: str
    optional_mode: OptionalMode
    presence_role: str | None


@dataclass
class BindingResultPlan(StageRecord):
    """Binding-facing result projection facts."""

    codegen_action: CodegenAction
    python_action: PythonBarrierAction
    python_result_role: str


@dataclass
class BridgeResultPlan(StageRecord):
    """Bridge-facing result production facts."""

    codegen_action: CodegenAction
    native_action: NativeBarrierAction
    data_action: BridgeDataAction
    copy_reason: str | None
    native_result_role: str
    native_name: str | None
    abi_position: int | None


@dataclass
class BindingLifecyclePlan(StageRecord):
    """Binding-owned lifecycle action facts."""

    source_role: str
    codegen_action: CodegenAction
    semantic_type_name: str
    datatype_family: DatatypeFamily
    result_position: int
    python_result_role: str | None


@dataclass
class BridgeLifecyclePlan(StageRecord):
    """Bridge-owned lifecycle action facts."""

    source_role: str


@dataclass
class NativeCallSlotPlan(StageRecord):
    """One native-call slot copied from completed policy."""

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
    bridge_data_action: BridgeDataAction
    bridge_copy_reason: str | None
    literal_type: str | None = None
    literal_value: Any = None
    result_position: int | None = None
    semantic_type_name: str | None = None
    datatype_family: DatatypeFamily | None = None
    character_length: int | None = None


@dataclass
class ArgumentTransferPlan(StageRecord):
    """One shared Python-to-native transfer with explicit backend views."""

    owner_path: str
    python_position: int
    native_position: int
    semantic_type_name: str
    datatype_family: DatatypeFamily
    binding: BindingArgumentPlan
    bridge: BridgeArgumentPlan
    native_call_slot: NativeCallSlotPlan


@dataclass
class ResultPlan(StageRecord):
    """One shared native-to-Python result with explicit backend views."""

    owner_path: str
    semantic_type_name: str
    datatype_family: DatatypeFamily
    source_kind: str
    result_position: int
    binding: BindingResultPlan
    bridge: BridgeResultPlan
    native_call_slot: NativeCallSlotPlan | None = None


@dataclass
class LifecycleActionPlan(StageRecord):
    """One ordered lifecycle action with explicit backend ownership."""

    owner_path: str
    phase: WritebackPhase
    source_role: str
    binding: BindingLifecyclePlan | None = None
    bridge: BridgeLifecyclePlan | None = None


@dataclass
class FunctionPlan(StageRecord):
    """Wrapper plan for one semantic function owner."""

    owner_path: str
    symbol_name: str
    binding: BindingFunctionPlan
    bridge: BridgeFunctionPlan
    arguments: tuple[ArgumentTransferPlan, ...]
    results: tuple[ResultPlan, ...]
    native_call_slots: tuple[NativeCallSlotPlan, ...]
    available_roles: tuple[str, ...]
    writeback_actions: tuple[LifecycleActionPlan, ...] = ()
    cleanup_actions: tuple[LifecycleActionPlan, ...] = ()
    release_actions: tuple[LifecycleActionPlan, ...] = ()


@dataclass
class NamespacePlan(StageRecord):
    """One Python namespace containing directly exported wrapper owners."""

    owner_path: str
    python_path: tuple[str, ...]
    functions: tuple[FunctionPlan, ...] = ()
    variables: tuple[ModuleVariablePlan, ...] = ()


@dataclass
class ModulePlan(StageRecord):
    """One shared generation-unit plan containing an explicit namespace tree."""

    owner_path: str
    binding: BindingModulePlan
    bridge: BridgeModulePlan
    namespaces: tuple[NamespacePlan, ...]


@dataclass
class WrapperPlanDiagnostic(StageRecord):
    """One owner-path diagnostic produced before backend generation."""

    owner_path: str
    code: str
    message: str


@dataclass
class WrapperPlanSupportBlocker(StageRecord):
    """One stable unsupported-owner reason for the wrapper-plan route."""

    owner_path: str
    reason: str


@dataclass
class WrapperPlanSupportReport(StageRecord):
    """Whole-generation-unit support report for route selection callers."""

    owner_path: str
    covered_lanes: tuple[str, ...] = ()
    blockers: tuple[WrapperPlanSupportBlocker, ...] = ()

    @property
    def supported(self) -> bool:
        """Return whether the whole generation unit is supported."""
        return not self.blockers
