"""Isolated wrapper-plan generator infrastructure.

This package is intentionally disconnected from production wrapper selection
until the migration checklist reaches the route-integration phase.
"""

from __future__ import annotations

from .assembly import BackendSourceAssembly, RenderedBackendSources
from .names import FunctionEmissionContext, ModuleEmissionContext, NameAllocator
from .nodes import (
    ApiReference,
    BackendScalarType,
    CDeclaration,
    CExpressionStatement,
    CFunction,
    CFunctionPrototype,
    CHeader,
    CInclude,
    CModule,
    CParameter,
    CReturn,
    CodeExpression,
    FortranAssignment,
    FortranCall,
    FortranDeclaration,
    FortranFunction,
    FortranModule,
    FortranParameter,
    FortranUse,
)
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
from .source_printers import CSourcePrinter, FortranSourcePrinter
from .support import WrapperPlanSupportAnalyzer
from .validator import WrapperPlanValidator
from .visitor import ClassVisitor, UnsupportedWrapperCodegenNodeError

__all__ = (
    "ActionHandlerPlan",
    "ApiReference",
    "ArgumentTransferPlan",
    "BackendScalarType",
    "BackendSourceAssembly",
    "BindingHandoffPlan",
    "BridgeAbiPlan",
    "BridgeAbiSlotPlan",
    "CDeclaration",
    "CExpressionStatement",
    "CFunction",
    "CFunctionPrototype",
    "CHeader",
    "CInclude",
    "CModule",
    "CParameter",
    "CReturn",
    "CSourcePrinter",
    "ClassVisitor",
    "CodeExpression",
    "FortranAssignment",
    "FortranCall",
    "FortranDeclaration",
    "FortranFunction",
    "FortranModule",
    "FortranParameter",
    "FortranSourcePrinter",
    "FortranUse",
    "FunctionEmissionContext",
    "FunctionPlan",
    "HandlerRegistryPlan",
    "LifecycleActionPlan",
    "ModuleEmissionContext",
    "ModulePlan",
    "NameAllocator",
    "NativeCallSlotPlan",
    "RenderedBackendSources",
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
