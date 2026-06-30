"""Complete post-IR semantic policies before readiness or lowering."""

from __future__ import annotations

from collections.abc import Iterable

from x2py.ownership_policy import (
    OwnershipContext,
    SetterAction,
    default_ownership_policy,
    ownership_context_for_argument,
)
from x2py.semantics import models

__all__ = ("complete_semantic_policies",)


def complete_semantic_policies(
    semantic_ir: models.SemanticModule | Iterable[models.SemanticModule],
) -> list[models.SemanticModule]:
    """Complete policy decisions for semantic modules after parser-to-IR conversion.

    This is the shared post-IR boundary for policies that need full semantic
    context. It completes entry export reachability, ownership, transfer, destruction,
    mutability/writeback, projection, nullability, release, codegen action, and
    contract/boundary storage modes, getter behavior, native setter assignment,
    and Python setter exposure. Future policy passes must be added here instead
    of in readiness, lowering, bridges, or bindings.
    """

    modules = list(semantic_ir) if not isinstance(semantic_ir, models.SemanticModule) else [semantic_ir]
    for module in modules:
        _complete_entry_export_policy(module)
        _complete_ownership_policies(module)
    return modules


def _complete_entry_export_policy(module: models.SemanticModule) -> None:
    """Remove public declarations not reachable from an explicit entry export policy."""
    if not module.metadata.get(models.PYTHON_EXPORTS_PREPARED_METADATA):
        return
    module.variables = [variable for variable in module.variables if _is_entry_export_reachable(variable)]
    module.functions = [function for function in module.functions if _is_entry_export_reachable(function)]
    module.overload_sets = [
        overload_set for overload_set in module.overload_sets if _is_entry_export_reachable(overload_set)
    ]


def _is_entry_export_reachable(declaration: object) -> bool:
    if getattr(declaration, "visibility", "public") == "private":
        return True
    return bool(_entry_exports(declaration))


def _entry_exports(declaration: object) -> object:
    if isinstance(declaration, models.ProcedureOverloadSet):
        if not declaration.procedures:
            return ()
        return declaration.procedures[0].metadata.get(models.PYTHON_EXPORTS_METADATA, ())
    if isinstance(declaration, models.SemanticVariable | models.SemanticFunction | models.SemanticClass):
        return declaration.metadata.get(models.PYTHON_EXPORTS_METADATA, ())
    raise TypeError(f"Unsupported semantic declaration: {type(declaration).__name__}")


def _complete_ownership_policies(module: models.SemanticModule) -> models.SemanticModule:
    """Attach resolved ownership decisions to a full semantic module.

    Raw semantic types such as ``Float64[:]`` do not carry enough context to
    decide boundary behavior or storage. This pass runs after complete
    signatures are known and before ``ir2ast`` lowering.
    """

    for variable in module.variables:
        _complete_variable(variable, OwnershipContext.module_variable())
        _complete_accessor_policies(variable, OwnershipContext.module_variable())
        _complete_module_variable_initializer(variable)
    for semantic_class in module.classes:
        _complete_class(semantic_class)
    for function in module.functions:
        _complete_function(function)
    for overload_set in module.overload_sets:
        for procedure in overload_set.procedures:
            _complete_function(procedure)
    module.metadata[models.POLICY_COMPLETION_PREPARED_METADATA] = True
    return module


def _complete_class(semantic_class: models.SemanticClass) -> None:
    class_type = models.SemanticType(name=semantic_class.name, dtype=semantic_class.name)
    semantic_class.metadata[models.RESOLVED_CLASS_INSTANCE_POLICY_METADATA] = (
        default_ownership_policy.decide_semantic_type(class_type, OwnershipContext.result())
    )
    semantic_class.metadata[models.RESOLVED_CLASS_SELF_POLICY_METADATA] = default_ownership_policy.decide_semantic_type(
        class_type,
        OwnershipContext.argument("inout"),
    )
    for field in semantic_class.fields:
        _complete_variable(field, OwnershipContext.field())
        _complete_accessor_policies(field, OwnershipContext.field())
    for nested in semantic_class.classes:
        _complete_class(nested)
    for method in semantic_class.methods:
        _complete_function(method)
    for overload_set in semantic_class.overload_sets:
        for procedure in overload_set.procedures:
            _complete_function(procedure)


def _complete_function(function: models.SemanticFunction) -> None:
    for argument in function.arguments:
        _complete_variable(argument, ownership_context_for_argument(function, argument))
    if function.return_type is not None:
        decision = default_ownership_policy.decide_semantic_type(function.return_type, OwnershipContext.result())
        function.metadata[models.RESOLVED_RETURN_OWNERSHIP_POLICY_METADATA] = decision
    else:
        function.metadata.pop(models.RESOLVED_RETURN_OWNERSHIP_POLICY_METADATA, None)


def _complete_variable(variable: models.SemanticVariable, context: OwnershipContext) -> None:
    decision = default_ownership_policy.decide_semantic_variable(variable, context)
    variable.metadata[models.RESOLVED_OWNERSHIP_POLICY_METADATA] = decision
    _complete_callable_policy(variable.semantic_type)


def _complete_accessor_policies(variable: models.SemanticVariable, context: OwnershipContext) -> None:
    variable.metadata[models.RESOLVED_GETTER_OWNERSHIP_POLICY_METADATA] = (
        default_ownership_policy.decide_semantic_getter(variable, context)
    )
    variable.metadata[models.RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA] = (
        default_ownership_policy.decide_semantic_setter(variable, context)
    )


def _complete_module_variable_initializer(variable: models.SemanticVariable) -> None:
    variable.metadata.pop(models.RESOLVED_MODULE_VARIABLE_INITIALIZER_METADATA, None)
    _clear_readiness_blocker(variable, models.MODULE_VARIABLE_INITIALIZER_UNSUPPORTED_BLOCKER)
    if variable.default_value is None or _is_constant(variable):
        return
    setter = variable.metadata[models.RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA]
    if variable.semantic_type.rank != 0:
        _add_readiness_blocker(
            variable,
            models.MODULE_VARIABLE_INITIALIZER_UNSUPPORTED_BLOCKER,
            "Module variable initializers require scalar storage with a write-through native setter.",
            {
                "item": variable.name,
                "rank": variable.semantic_type.rank,
                "reason": "only scalar module variables support import-time native initialization",
            },
        )
        return
    if setter.setter_action is not SetterAction.WRITE_THROUGH:
        _add_readiness_blocker(
            variable,
            models.MODULE_VARIABLE_INITIALIZER_UNSUPPORTED_BLOCKER,
            "Module variable initializers require scalar storage with a write-through native setter.",
            {
                "item": variable.name,
                "setter_action": setter.setter_action.value,
                "reason": "completed setter policy does not expose write-through native assignment",
            },
        )
        return
    variable.metadata[models.RESOLVED_MODULE_VARIABLE_INITIALIZER_METADATA] = variable.default_value


def _clear_readiness_blocker(variable: models.SemanticVariable, code: str) -> None:
    blockers = variable.metadata.get("readiness_blockers")
    if not isinstance(blockers, list):
        return
    remaining = [blocker for blocker in blockers if not isinstance(blocker, dict) or blocker.get("code") != code]
    if remaining:
        variable.metadata["readiness_blockers"] = remaining
    else:
        variable.metadata.pop("readiness_blockers", None)


def _add_readiness_blocker(
    variable: models.SemanticVariable,
    code: str,
    message: str,
    item: dict[str, object],
) -> None:
    variable.metadata.setdefault("readiness_blockers", []).append(
        {
            "code": code,
            "message": message,
            "item": item,
        }
    )


def _is_constant(variable: models.SemanticVariable) -> bool:
    return any(constraint.name == "Constant" for constraint in variable.semantic_type.constraints)


def _complete_callable_policy(semantic_type: models.SemanticType) -> None:
    if semantic_type.name != "Callable":
        return

    callback_arguments = semantic_type.metadata.get("callback_arguments")
    if isinstance(callback_arguments, list):
        for argument in callback_arguments:
            if isinstance(argument, models.SemanticArgument):
                _complete_variable(argument, OwnershipContext.argument(argument.intent))

    return_type = semantic_type.metadata.get("return")
    if isinstance(return_type, models.SemanticType) and return_type.name != "None":
        decision = default_ownership_policy.decide_semantic_type(return_type, OwnershipContext.result())
        return_type.metadata[models.RESOLVED_OWNERSHIP_POLICY_METADATA] = decision
