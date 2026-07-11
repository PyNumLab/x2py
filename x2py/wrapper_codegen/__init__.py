"""Isolated wrapper-plan generator infrastructure.

This package is intentionally disconnected from production wrapper selection
until the migration checklist reaches the route-integration phase.
"""

from __future__ import annotations

from .plan import (
    ActionHandlerPlan,
    ArgumentTransferPlan,
    BindingHandoffPlan,
    BridgeAbiPlan,
    BridgeAbiSlotPlan,
    FunctionPlan,
    HandlerRegistryPlan,
    LifecycleActionPlan,
    ModulePlan,
    NativeCallSlotPlan,
    ResultPlan,
    WrapperPlanDiagnostic,
    WrapperPlanSupportBlocker,
    WrapperPlanSupportReport,
)
from .planner import WrapperPlanner
from .renderer import WrapperPlanRenderer
from .support import WrapperPlanSupportAnalyzer
from .validator import WrapperPlanValidator
from .visitor import ClassVisitor, UnsupportedWrapperCodegenNodeError

__all__ = (
    "ActionHandlerPlan",
    "ArgumentTransferPlan",
    "BindingHandoffPlan",
    "BridgeAbiPlan",
    "BridgeAbiSlotPlan",
    "ClassVisitor",
    "FunctionPlan",
    "HandlerRegistryPlan",
    "LifecycleActionPlan",
    "ModulePlan",
    "NativeCallSlotPlan",
    "ResultPlan",
    "UnsupportedWrapperCodegenNodeError",
    "WrapperPlanDiagnostic",
    "WrapperPlanRenderer",
    "WrapperPlanSupportAnalyzer",
    "WrapperPlanSupportBlocker",
    "WrapperPlanSupportReport",
    "WrapperPlanValidator",
    "WrapperPlanner",
)
