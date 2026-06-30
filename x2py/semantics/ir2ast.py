"""Convert x2py semantic IR nodes into codegen AST nodes."""

from __future__ import annotations

import ast
from dataclasses import replace
from itertools import product
import keyword
import numpy as np
import re

from x2py import SEMANTIC_DTYPE_TO_NUMPY_DTYPE
from x2py.codegen.models.core import (
    Add,
    AsName,
    ClassDef,
    Div,
    FunctionDef,
    FunctionAddress,
    FunctionDefArgument,
    FunctionDefResult,
    FunctionOverloadSet,
    Import,
    Minus,
    Module,
    Mul,
    UnarySub,
    Variable,
)
from x2py.codegen.models.datatypes import (
    CharType,
    DataTypeFactory,
    FinalType,
    NIL,
    NumpyNDArrayType,
    StringType,
    convert_to_literal,
    original_type_to_x2py_type,
)
from x2py.semantics import models
from x2py.semantics.models import (
    FORTRAN_GENERIC_NAME_METADATA,
    OVERLOAD_KIND_METADATA,
    PYI_NATIVE_PROJECTION_METADATA,
    PYI_PROJECTED_OUTPUT_METADATA,
    PYTHON_BOUND_POSITION_METADATA,
)


_SEMANTIC_ORDER_TO_NUMPY_ORDER = {
    "ORDER_C": "C",
    "ORDER_F": "F",
}
_MAX_SUPPORTED_ARRAY_RANK = 15
_ISO_C_KIND_TOKENS = frozenset(
    {
        "c_bool",
        "c_char",
        "c_double",
        "c_double_complex",
        "c_float",
        "c_float_complex",
        "c_int",
        "c_int16_t",
        "c_int32_t",
        "c_int64_t",
        "c_int8_t",
        "c_long_double",
        "c_long_double_complex",
        "c_long_long",
        "c_short",
        "c_signed_char",
        "c_size_t",
    }
)
_POLYMORPHIC_DISPATCH_VARIANT_METADATA = "fortran_polymorphic_dispatch_variant"


def _numpy_type(dtype: str):
    return getattr(np, dtype.removeprefix("numpy."))


def _codegen_type(dtype: str, custom_types: dict[str, object] | None = None):
    if custom_types and dtype in custom_types:
        return custom_types[dtype]
    if dtype == "String":
        return StringType()
    numpy_type = _numpy_type(SEMANTIC_DTYPE_TO_NUMPY_DTYPE[dtype])
    return original_type_to_x2py_type[numpy_type]


def _is_constant(semantic_type: models.SemanticType) -> bool:
    return any(constraint.name == "Constant" for constraint in semantic_type.constraints)


def _string_shape(semantic_type: models.SemanticType):
    length = semantic_type.metadata.get("fortran_character_length")
    if isinstance(length, str) and length.isdigit():
        return (convert_to_literal(int(length)),)
    return (None,)


def _array_contract(
    semantic_type: models.SemanticType,
) -> models.SemanticArrayContract | None:
    if semantic_type.storage is None:
        return None
    return semantic_type.storage.array


def _numpy_array_order(semantic_type: models.SemanticType, rank: int) -> str | None:
    if rank <= 1:
        return None
    contract = _array_contract(semantic_type)
    order = contract.order if contract is not None else None
    return _SEMANTIC_ORDER_TO_NUMPY_ORDER.get(order, "C")


def _array_allows_strides(semantic_type: models.SemanticType) -> bool:
    contract = _array_contract(semantic_type)
    return contract is None or contract.contiguous is not True


def _codegen_dimension_expression(text: str, scope):
    try:
        parsed = ast.parse(text, mode="eval").body
    except SyntaxError:
        return None
    return _codegen_expression_node(parsed, scope)


def _codegen_expression_node(node: ast.AST, scope):
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return convert_to_literal(node.value)
    if isinstance(node, ast.Name):
        return scope.find(node.id, "variables")
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        operand = _codegen_expression_node(node.operand, scope)
        return None if operand is None else UnarySub(operand)
    if isinstance(node, ast.BinOp):
        left = _codegen_expression_node(node.left, scope)
        right = _codegen_expression_node(node.right, scope)
        if left is None or right is None:
            return None
        operators = {
            ast.Add: Add,
            ast.Sub: Minus,
            ast.Mult: Mul,
            ast.Div: Div,
        }
        for ast_op, codegen_op in operators.items():
            if isinstance(node.op, ast_op):
                return codegen_op(left, right)
    return None


def _codegen_array_shape(semantic_type: models.SemanticType, scope) -> tuple[object | None, ...] | None:
    if semantic_type.rank <= 0:
        return None
    shape = list(semantic_type.shape)
    if not shape:
        contract = _array_contract(semantic_type)
        shape = list(contract.shape if contract is not None and contract.shape else [])
    if not shape:
        return None

    result = []
    for dimension in shape:
        text = str(dimension).strip()
        if text in {"", ":", "*"} or "Strided" in text:
            result.append(None)
        elif text.isdigit():
            result.append(convert_to_literal(int(text)))
        else:
            result.append(_codegen_dimension_expression(text, scope))
    return tuple(result)


def _class_type(semantic_class: models.SemanticClass):
    return DataTypeFactory(
        semantic_class.native_name or semantic_class.name,
        semantic_class.name,
    )()


def _iter_semantic_classes(classes: list[models.SemanticClass]):
    for semantic_class in classes:
        yield semantic_class
        yield from _iter_semantic_classes(semantic_class.classes)


def _semantic_class_lookup(classes: list[models.SemanticClass]) -> dict[str, models.SemanticClass]:
    return {semantic_class.name: semantic_class for semantic_class in _iter_semantic_classes(classes)}


def _semantic_class_order(classes: list[models.SemanticClass]) -> dict[str, int]:
    return {semantic_class.name: index for index, semantic_class in enumerate(_iter_semantic_classes(classes))}


def _semantic_class_descendants(classes: list[models.SemanticClass]) -> dict[str, tuple[str, ...]]:
    lookup = _semantic_class_lookup(classes)
    direct: dict[str, list[str]] = {name: [] for name in lookup}
    for semantic_class in lookup.values():
        for base_name in semantic_class.base_classes:
            if base_name in direct:
                direct[base_name].append(semantic_class.name)

    def collect(base_name: str) -> tuple[str, ...]:
        names = []
        for child_name in direct.get(base_name, ()):
            names.extend(collect(child_name))
            names.append(child_name)
        return tuple(dict.fromkeys(names))

    return {base_name: collect(base_name) for base_name in direct}


def _missing_completed_policy(owner: str) -> ValueError:
    return ValueError(
        f"{owner} is missing completed ownership policy; run complete_semantic_policies before ir2ast lowering"
    )


def _variable_ownership_decision(variable: models.SemanticVariable):
    decision = variable.metadata.get(models.RESOLVED_OWNERSHIP_POLICY_METADATA)
    if decision is None:
        raise _missing_completed_policy(f"Variable {variable.name!r}")
    return decision


def _function_return_ownership_decision(function: models.SemanticFunction):
    decision = function.metadata.get(models.RESOLVED_RETURN_OWNERSHIP_POLICY_METADATA)
    if decision is None:
        raise _missing_completed_policy(f"Function {function.name!r} result")
    return decision


def _type_ownership_decision(owner: str, semantic_type: models.SemanticType):
    decision = semantic_type.metadata.get(models.RESOLVED_OWNERSHIP_POLICY_METADATA)
    if decision is None:
        raise _missing_completed_policy(owner)
    return decision


def _passes_by_value(node: models.SemanticVariable) -> bool:
    return bool(
        getattr(node, "origin", None) is not None
        and isinstance(node.origin.metadata, dict)
        and node.origin.metadata.get("value")
    )


def _passed_object_position(node: models.SemanticFunction) -> int | None:
    if node.name == "__init__" and node.metadata.get(models.PYI_BIND_TARGET_METADATA):
        return None
    overload_kind = node.metadata.get(OVERLOAD_KIND_METADATA)
    if overload_kind in {"generic", "assignment", "named_operator", "comparison"}:
        position = node.metadata.get(PYTHON_BOUND_POSITION_METADATA)
        return position if isinstance(position, int) else None
    if not isinstance(node, models.SemanticMethod) or node.is_static:
        return None
    return node.passed_object_position if node.passed_object_position is not None else 0


def _codegen_function_arguments(declarations: list[Variable], passed_object_position: int | None):
    native_args = [
        FunctionDefArgument(
            item,
            value=NIL if item.is_optional else None,
            bound_argument=index == passed_object_position,
            bound_argument_position=index if index == passed_object_position else None,
        )
        for index, item in enumerate(declarations)
    ]
    if passed_object_position is None:
        return native_args
    return [
        native_args[passed_object_position],
        *native_args[:passed_object_position],
        *native_args[passed_object_position + 1 :],
    ]


def _callback_result_variable(
    semantic_type: models.SemanticType,
    name: str,
    scope,
    custom_types: dict[str, object] | None,
) -> Variable:
    ownership_decision = _type_ownership_decision(f"Callback result {name!r}", semantic_type)
    dtype = _codegen_type(semantic_type.dtype, custom_types)
    if semantic_type.rank > 0:
        dtype = NumpyNDArrayType.get_new(
            dtype,
            semantic_type.rank,
            order=_numpy_array_order(semantic_type, semantic_type.rank),
            allows_strides=_array_allows_strides(semantic_type),
        )
    shape = _codegen_array_shape(semantic_type, scope) if semantic_type.rank > 0 else None
    result = Variable(
        dtype,
        name,
        shape=shape,
        memory_handling=ownership_decision.storage_mode.value,
        intent="out",
        ownership_decision=ownership_decision,
    )
    scope.insert_variable(result, name=name)
    return result


def _codegen_callback_argument(
    node: models.SemanticArgument,
    scope,
    legacy: bool,
    *,
    custom_types: dict[str, object] | None,
    class_lookup: dict[str, models.SemanticClass] | None,
    class_descendants: dict[str, tuple[str, ...]] | None,
    class_order: dict[str, int] | None,
) -> FunctionAddress:
    metadata = node.semantic_type.metadata
    callback_arguments = metadata.get("callback_arguments")
    if callback_arguments is None:
        argument_types = metadata.get("arguments")
        if isinstance(argument_types, list):
            callback_arguments = [
                models.SemanticArgument(f"arg_{index}", semantic_type)
                for index, semantic_type in enumerate(argument_types)
            ]
    if not isinstance(callback_arguments, list):
        raise ValueError(f"Callback argument {node.name!r} is missing a complete callable argument contract")

    try:
        name = scope.get_expected_name(node.name)
    except RuntimeError:
        name = scope.get_new_public_name(
            node.name,
            object_type="argument",
            owner=f"callback argument {node.name}",
        )
    callback_scope = scope.new_child_scope(f"{name}_callback", "function")
    declarations = [
        semantic_ir_to_codegen_ast(
            item,
            callback_scope,
            legacy,
            custom_types=custom_types,
            class_lookup=class_lookup,
            class_descendants=class_descendants,
            class_order=class_order,
        )
        for item in callback_arguments
    ]
    result_type = metadata.get("return")
    result = (
        FunctionDefResult(
            _callback_result_variable(
                result_type,
                f"{name}_result",
                callback_scope,
                custom_types,
            )
        )
        if isinstance(result_type, models.SemanticType) and result_type.name != "None"
        else FunctionDefResult(NIL)
    )
    return FunctionAddress(
        name,
        [FunctionDefArgument(item) for item in declarations],
        result,
        is_optional=node.optional,
        is_argument=True,
        decorators={"x2py_callback": dict(metadata)},
        scope=callback_scope,
    )


def _pyi_bound_constructor_self(
    node: models.SemanticFunction,
    cls_base: ClassDef | None,
    func_scope,
) -> Variable | None:
    if cls_base is None or node.name != "__init__" or not node.metadata.get(models.PYI_BIND_TARGET_METADATA):
        return None
    self_policy = cls_base.decorators[models.RESOLVED_CLASS_SELF_POLICY_METADATA]
    self_var = Variable(
        cls_base.class_type,
        func_scope.get_new_name("self"),
        cls_base=cls_base,
        memory_handling=self_policy.boundary_storage_mode.value,
        ownership_decision=self_policy,
    )
    func_scope.insert_variable(self_var)
    return self_var


def _raise_for_unresolved_generic_targets(node: models.SemanticModule | models.SemanticClass) -> None:
    blockers = node.metadata.get("readiness_blockers", ())
    for blocker in blockers:
        if blocker.get("code") != "fortran_generic_target_unresolved":
            continue
        item = next(iter(blocker.get("items", ())), {})
        generic = item.get("generic", "<unnamed>")
        missing = item.get("missing_targets", ())
        if missing:
            targets = ", ".join(str(target) for target in missing)
            raise ValueError(f"Generic interface {generic!r} references missing specific procedure(s): {targets}")
        raise ValueError(f"Generic interface {generic!r} does not declare any specific procedures")


def _raise_for_unsupported_constructor_overloads(node: models.SemanticClass) -> None:
    if any(overload_set.name == "__init__" for overload_set in node.overload_sets):
        raise ValueError(
            "Constructor overload dispatch is not mapped to Python tp_init yet; "
            "use the generated field constructor until overloaded constructor lowering is implemented."
        )


def _raise_for_unsupported_fortran_module_features(node: models.SemanticModule) -> None:
    owners = [node, *node.variables, *node.functions]
    blocking_codes = {
        "fortran_generic_constructor_unsupported",
        models.MODULE_VARIABLE_INITIALIZER_UNSUPPORTED_BLOCKER,
    }
    for owner in owners:
        for blocker in owner.metadata.get("readiness_blockers", ()):
            if blocker.get("code") in blocking_codes:
                raise ValueError(str(blocker.get("message") or "Unsupported Fortran wrapper feature."))


def _is_allocatable_array(semantic_type: models.SemanticType | None) -> bool:
    return bool(
        semantic_type is not None
        and semantic_type.storage is not None
        and semantic_type.storage.array is not None
        and semantic_type.storage.array.allocatable
    )


def _is_allocatable_scalar(semantic_type: models.SemanticType | None) -> bool:
    return bool(
        semantic_type is not None and semantic_type.rank == 0 and semantic_type.metadata.get("fortran_allocatable")
    )


def _is_pointer_array(semantic_type: models.SemanticType | None) -> bool:
    return bool(
        semantic_type is not None
        and semantic_type.storage is not None
        and semantic_type.storage.array is not None
        and semantic_type.storage.array.pointer
    )


def _is_pointer(semantic_type: models.SemanticType | None) -> bool:
    if semantic_type is None:
        return False
    storage = semantic_type.storage
    return bool(
        semantic_type.metadata.get("fortran_pointer")
        or (storage is not None and storage.array is not None and storage.array.pointer)
    )


def _array_contract_category(semantic_type: models.SemanticType | None) -> str | None:
    contract = _array_contract(semantic_type) if semantic_type is not None else None
    return None if contract is None else contract.category


def _is_assumed_rank(semantic_type: models.SemanticType | None) -> bool:
    return _array_contract_category(semantic_type) == "assumed_rank"


def _is_assumed_type(semantic_type: models.SemanticType | None) -> bool:
    if semantic_type is None:
        return False
    source_type = (semantic_type.origin.source_type or "").casefold().replace(" ", "")
    return "type(*)" in source_type or "class(*)" in source_type


def _is_fortran_polymorphic(semantic_type: models.SemanticType | None) -> bool:
    return bool(
        semantic_type is not None
        and semantic_type.metadata.get("fortran_polymorphic")
        and not _is_assumed_type(semantic_type)
    )


def _is_supported_passed_object_polymorphic_arg(
    node: models.SemanticFunction,
    argument: models.SemanticArgument,
    *,
    cls_base: ClassDef | None = None,
    passed_object_position: int | None = None,
    argument_position: int | None = None,
) -> bool:
    if (
        isinstance(node, models.SemanticMethod)
        and not node.is_static
        and str(node.passed_object_name) == str(argument.name)
    ):
        return True
    if cls_base is not None and passed_object_position is not None and argument_position == passed_object_position:
        return True
    python_bound_position = node.metadata.get(PYTHON_BOUND_POSITION_METADATA)
    if python_bound_position is not None and argument_position == int(python_bound_position):
        return True
    return bool(
        node.metadata.get("fortran_type_bound_target")
        and str(node.metadata.get("fortran_passed_object_name")) == str(argument.name)
    )


def _is_scalar_polymorphic_input_dispatch_arg(
    argument: models.SemanticArgument,
    class_lookup: dict[str, models.SemanticClass],
) -> bool:
    semantic_type = argument.semantic_type
    if not _is_fortran_polymorphic(semantic_type):
        return False
    if semantic_type.rank != 0 or str(argument.intent).lower() != "in":
        return False
    if semantic_type.metadata.get("fortran_allocatable"):
        return False
    if getattr(argument.origin, "metadata", {}).get("pointer"):
        return False
    return semantic_type.name in class_lookup


def _semantic_class_depth(
    name: str,
    class_lookup: dict[str, models.SemanticClass],
    cache: dict[str, int],
) -> int:
    if name in cache:
        return cache[name]
    semantic_class = class_lookup.get(name)
    if semantic_class is None or not semantic_class.base_classes:
        cache[name] = 0
        return 0
    cache[name] = 1 + max(
        (_semantic_class_depth(base_name, class_lookup, cache) for base_name in semantic_class.base_classes),
        default=0,
    )
    return cache[name]


def _polymorphic_dispatch_class_names(
    semantic_type: models.SemanticType,
    class_lookup: dict[str, models.SemanticClass],
    class_descendants: dict[str, tuple[str, ...]],
    class_order: dict[str, int],
) -> tuple[str, ...]:
    base_name = semantic_type.name
    if base_name not in class_lookup:
        return ()
    depth_cache: dict[str, int] = {}
    descendants = sorted(
        class_descendants.get(base_name, ()),
        key=lambda name: (
            -_semantic_class_depth(name, class_lookup, depth_cache),
            class_order.get(name, 0),
        ),
    )
    return (*descendants, base_name)


def _polymorphic_dispatch_options(
    node: models.SemanticFunction,
    *,
    cls_base: ClassDef | None,
    passed_object_position: int | None,
    class_lookup: dict[str, models.SemanticClass],
    class_descendants: dict[str, tuple[str, ...]],
    class_order: dict[str, int],
) -> tuple[tuple[int, tuple[str, ...]], ...]:
    if node.metadata.get(_POLYMORPHIC_DISPATCH_VARIANT_METADATA):
        return ()

    options = []
    for index, argument in enumerate(node.arguments):
        if not _is_fortran_polymorphic(argument.semantic_type):
            continue
        if _is_supported_passed_object_polymorphic_arg(
            node,
            argument,
            cls_base=cls_base,
            passed_object_position=passed_object_position,
            argument_position=index,
        ):
            continue
        if not _is_scalar_polymorphic_input_dispatch_arg(argument, class_lookup):
            continue
        class_names = _polymorphic_dispatch_class_names(
            argument.semantic_type,
            class_lookup,
            class_descendants,
            class_order,
        )
        if class_names:
            options.append((index, class_names))
    return tuple(options)


def _dispatch_argument_for_class(argument: models.SemanticArgument, class_name: str) -> models.SemanticArgument:
    type_metadata = dict(argument.semantic_type.metadata)
    type_metadata.pop("fortran_polymorphic", None)
    type_metadata["fortran_polymorphic_dispatch_base"] = argument.semantic_type.name
    type_metadata["fortran_polymorphic_dispatch_type"] = class_name
    semantic_type = replace(
        argument.semantic_type,
        name=class_name,
        dtype=class_name,
        metadata=type_metadata,
    )
    return models.SemanticArgument(
        argument.name,
        semantic_type,
        intent=argument.intent,
        optional=argument.optional,
        visibility=argument.visibility,
        default_value=argument.default_value,
        metadata=dict(argument.metadata),
        origin=argument.origin,
    )


def _polymorphic_dispatch_variants(
    node: models.SemanticFunction,
    dispatch_options: tuple[tuple[int, tuple[str, ...]], ...],
) -> tuple[models.SemanticFunction, ...]:
    positions = tuple(position for position, _ in dispatch_options)
    class_options = tuple(class_names for _, class_names in dispatch_options)
    variants = []
    for selected_classes in product(*class_options):
        arguments = list(node.arguments)
        for position, class_name in zip(positions, selected_classes, strict=True):
            arguments[position] = _dispatch_argument_for_class(arguments[position], class_name)
        metadata = dict(node.metadata)
        metadata[_POLYMORPHIC_DISPATCH_VARIANT_METADATA] = True
        variants.append(replace(node, arguments=arguments, metadata=metadata))
    return tuple(variants)


def _is_derived_type_array(semantic_type: models.SemanticType | None) -> bool:
    return bool(
        semantic_type is not None
        and semantic_type.rank > 0
        and semantic_type.name not in SEMANTIC_DTYPE_TO_NUMPY_DTYPE
        and semantic_type.name != "String"
    )


def _raise_for_unsupported_array_contracts_in_type(
    owner: str,
    semantic_type: models.SemanticType | None,
) -> None:
    if semantic_type is None or semantic_type.rank <= 0:
        return
    if semantic_type.rank > _MAX_SUPPORTED_ARRAY_RANK:
        raise ValueError(
            f"{owner} has rank {semantic_type.rank}, but wrapper generation supports ranks "
            f"1 through {_MAX_SUPPORTED_ARRAY_RANK}"
        )
    if _is_assumed_type(semantic_type):
        raise ValueError(
            f"{owner} uses assumed-type type(*), which needs an explicit dtype and descriptor policy "
            "before wrapper generation"
        )
    if _is_derived_type_array(semantic_type):
        raise ValueError(
            f"{owner} is an array of derived type values, which needs explicit layout and ownership policy"
        )


def _raise_for_unsupported_array_contracts_in_function(node: models.SemanticFunction) -> None:
    for argument in node.arguments:
        _raise_for_unsupported_array_contracts_in_type(
            f"Function {node.name!r} argument {argument.name!r}",
            argument.semantic_type,
        )
    _raise_for_unsupported_array_contracts_in_type(f"Function {node.name!r} result", node.return_type)


def _raise_for_unsupported_array_contracts_in_class(node: models.SemanticClass) -> None:
    for field in node.fields:
        _raise_for_unsupported_array_contracts_in_type(
            f"Class {node.name!r} field {field.name!r}",
            field.semantic_type,
        )
    for method in node.methods:
        _raise_for_unsupported_array_contracts_in_function(method)


def _raise_for_unsupported_array_contracts(node: models.SemanticModule) -> None:
    for variable in node.variables:
        _raise_for_unsupported_array_contracts_in_type(
            f"Module variable {variable.name!r}",
            variable.semantic_type,
        )
    for function in node.functions:
        _raise_for_unsupported_array_contracts_in_function(function)
    for overload_set in node.overload_sets:
        for procedure in overload_set.procedures:
            _raise_for_unsupported_array_contracts_in_function(procedure)
    for semantic_class in node.classes:
        _raise_for_unsupported_array_contracts_in_class(semantic_class)


def _raise_for_unsupported_allocatable_module_variables(node: models.SemanticModule) -> None:
    for variable in node.variables:
        semantic_type = variable.semantic_type
        if _is_allocatable_array(semantic_type) and not semantic_type.metadata.get("fortran_target"):
            raise ValueError(
                f"Module variable {variable.name!r} is an allocatable array without the Fortran target attribute; "
                "borrowed zero-copy module views require target storage"
            )


def _raise_for_unsupported_pointer_outputs(node: models.SemanticFunction) -> None:
    for argument in node.arguments:
        decision = _variable_ownership_decision(argument)
        if _is_pointer(argument.semantic_type) and decision.is_blocked:
            raise ValueError(
                f"Function {node.name!r} has pointer {argument.intent} argument {argument.name!r}, "
                f"which cannot be wrapped safely: {decision.blocker or decision.reason}"
            )


def _raise_for_blocked_ownership_policy(
    owner: str,
    decision,
) -> None:
    if decision.is_blocked:
        raise ValueError(f"{owner} cannot be wrapped safely: {decision.blocker or decision.reason}")


def _raise_for_unsupported_assumed_type_contracts(node: models.SemanticFunction) -> None:
    for argument in node.arguments:
        if _is_assumed_type(argument.semantic_type):
            raise ValueError(
                f"Function {node.name!r} has assumed-type argument {argument.name!r}, "
                "which needs an explicit dtype and descriptor policy before wrapper generation"
            )
    if _is_assumed_type(node.return_type):
        raise ValueError(
            f"Function {node.name!r} has an assumed-type result, "
            "which needs an explicit dtype and descriptor policy before wrapper generation"
        )


def _raise_for_unsupported_polymorphic_contracts(
    node: models.SemanticFunction,
    *,
    cls_base: ClassDef | None = None,
    passed_object_position: int | None = None,
    dispatch_positions: set[int] | None = None,
) -> None:
    supported_dispatch_positions = set() if dispatch_positions is None else dispatch_positions
    for index, argument in enumerate(node.arguments):
        if not _is_fortran_polymorphic(argument.semantic_type):
            continue
        if index in supported_dispatch_positions:
            continue
        if not _is_supported_passed_object_polymorphic_arg(
            node,
            argument,
            cls_base=cls_base,
            passed_object_position=passed_object_position,
            argument_position=index,
        ):
            raise ValueError(
                f"Function {node.name!r} has polymorphic argument {argument.name!r}, "
                "which needs explicit dynamic-type and dispatch policy"
            )
    if _is_fortran_polymorphic(node.return_type):
        raise ValueError(
            f"Function {node.name!r} has a polymorphic result, "
            "which needs explicit dynamic-type, allocation, and ownership policy"
        )


def _raise_for_unsupported_allocatable_scalar_outputs(node: models.SemanticFunction) -> None:
    for argument in node.arguments:
        intent = str(argument.intent).lower()
        if _is_allocatable_scalar(argument.semantic_type) and intent in {"out", "inout"}:
            raise ValueError(
                f"Function {node.name!r} has allocatable scalar {intent} argument {argument.name!r}, "
                "which needs explicit construction, ownership, and destruction policy"
            )


def _is_scalar_integer_runtime_status(semantic_type: models.SemanticType) -> bool:
    if semantic_type.rank != 0:
        return False
    try:
        numpy_dtype = SEMANTIC_DTYPE_TO_NUMPY_DTYPE[semantic_type.dtype]
        return bool(np.issubdtype(np.dtype(_numpy_type(numpy_dtype)), np.integer))
    except (AttributeError, KeyError, TypeError):
        return False


def _raise_for_invalid_runtime_policy(node: models.SemanticFunction) -> None:
    policy = node.metadata.get(models.RUNTIME_STATUS_ERROR_METADATA)
    if policy is None:
        return
    if not isinstance(policy, dict):
        raise ValueError(f"Function {node.name!r} has invalid raises metadata")

    success = policy.get("success", 0)
    if not isinstance(success, int) or isinstance(success, bool):
        raise ValueError(f"Function {node.name!r} raises success value must be an integer")

    hidden_outputs = {argument.name: argument for argument in node.arguments if str(argument.intent).lower() == "out"}
    status_name = policy.get("status")
    status = hidden_outputs.get(status_name) if isinstance(status_name, str) else None
    if status is None:
        raise ValueError(f"Function {node.name!r} raises status target must name a hidden output")
    if not _is_scalar_integer_runtime_status(status.semantic_type):
        raise ValueError(
            f"Function {node.name!r} raises status target {status.name!r} must be a scalar integer hidden output"
        )

    message_name = policy.get("message")
    if message_name is None:
        return
    message = hidden_outputs.get(message_name) if isinstance(message_name, str) else None
    if message is None:
        raise ValueError(f"Function {node.name!r} raises message target must name a hidden output")
    if message.semantic_type.rank != 0 or message.semantic_type.name != "String":
        raise ValueError(
            f"Function {node.name!r} raises message target {message.name!r} must be a scalar string hidden output"
        )


def _is_bind_c_derived_type(
    semantic_type: models.SemanticType,
    class_lookup: dict[str, models.SemanticClass],
) -> bool:
    semantic_class = class_lookup.get(semantic_type.name)
    return semantic_class is not None and bool(semantic_class.metadata.get("fortran_bind_c"))


def _raise_for_unsupported_bind_c_abi(
    node: models.SemanticFunction,
    class_lookup: dict[str, models.SemanticClass],
) -> None:
    if not node.metadata.get("fortran_bind_c"):
        return
    for argument in node.arguments:
        semantic_type = argument.semantic_type
        if semantic_type.rank > 0:
            continue
        if _is_bind_c_derived_type(semantic_type, class_lookup):
            continue
        if semantic_type.name in class_lookup:
            is_value = bool(getattr(argument.origin, "metadata", {}).get("value"))
            transfer = "by-value " if is_value else ""
            raise ValueError(
                f"Function {node.name!r} has bind(C) {transfer}derived-type argument {argument.name!r} "
                "whose type is not declared bind(C); aggregate layout is not inferred"
            )
        if not _has_known_iso_c_kind(semantic_type):
            raise ValueError(
                f"Function {node.name!r} has bind(C) scalar argument {argument.name!r} "
                "without a supported ISO C binding kind"
            )
    if node.return_type is not None and node.return_type.rank == 0:
        if _is_bind_c_derived_type(node.return_type, class_lookup):
            return
        if node.return_type.name in class_lookup:
            raise ValueError(
                f"Function {node.name!r} has a bind(C) derived-type result whose type is not declared bind(C); "
                "aggregate layout is not inferred"
            )
        if not _has_known_iso_c_kind(node.return_type):
            raise ValueError(
                f"Function {node.name!r} has a bind(C) scalar result without a supported ISO C binding kind"
            )


def _raise_for_blocked_ownership_contracts_in_function(node: models.SemanticFunction) -> None:
    for argument in node.arguments:
        _raise_for_blocked_ownership_policy(
            f"Function {node.name!r} argument {argument.name!r}",
            _variable_ownership_decision(argument),
        )
    if node.return_type is not None:
        _raise_for_blocked_ownership_policy(
            f"Function {node.name!r} result",
            _function_return_ownership_decision(node),
        )


def _raise_for_blocked_ownership_contracts_in_class(node: models.SemanticClass) -> None:
    for field in node.fields:
        _raise_for_blocked_ownership_policy(
            f"Class {node.name!r} field {field.name!r}",
            _variable_ownership_decision(field),
        )


def _raise_for_blocked_ownership_contracts(node: models.SemanticModule) -> None:
    for variable in node.variables:
        _raise_for_blocked_ownership_policy(
            f"Module variable {variable.name!r}",
            _variable_ownership_decision(variable),
        )
    for semantic_class in node.classes:
        _raise_for_blocked_ownership_contracts_in_class(semantic_class)


def _is_public(node) -> bool:
    return getattr(node, "visibility", "public") != "private"


def _references_private_type(semantic_type: models.SemanticType | None, private_type_names: set[str]) -> bool:
    return bool(semantic_type is not None and semantic_type.name in private_type_names)


def _raise_if_private_type_exposed(
    owner: str,
    semantic_type: models.SemanticType | None,
    private_type_names: set[str],
) -> None:
    if _references_private_type(semantic_type, private_type_names):
        raise ValueError(f"{owner} exposes private derived type {semantic_type.name!r} in the Python wrapper API")


def _raise_for_private_type_exposure_in_function(
    node: models.SemanticFunction,
    private_type_names: set[str],
) -> None:
    if not _is_public(node):
        return
    for argument in node.arguments:
        _raise_if_private_type_exposed(
            f"Public function {node.name!r} argument {argument.name!r}",
            argument.semantic_type,
            private_type_names,
        )
    _raise_if_private_type_exposed(f"Public function {node.name!r} result", node.return_type, private_type_names)


def _raise_for_private_type_exposure_in_class(
    node: models.SemanticClass,
    private_type_names: set[str],
) -> None:
    if not _is_public(node):
        return
    for base_name in node.base_classes:
        if base_name in private_type_names:
            raise ValueError(f"Public type {node.name!r} extends private derived type {base_name!r}")
    for field in node.fields:
        if _is_public(field):
            _raise_if_private_type_exposed(
                f"Public type {node.name!r} field {field.name!r}",
                field.semantic_type,
                private_type_names,
            )
    for method in node.methods:
        _raise_for_private_type_exposure_in_function(method, private_type_names)
    for overload_set in node.overload_sets:
        if _is_public(overload_set):
            for procedure in overload_set.procedures:
                _raise_for_private_type_exposure_in_function(procedure, private_type_names)


def _raise_for_private_type_exposure(node: models.SemanticModule) -> None:
    private_type_names = {
        semantic_class.name for semantic_class in _iter_semantic_classes(node.classes) if not _is_public(semantic_class)
    }
    if not private_type_names:
        return
    for variable in node.variables:
        if _is_public(variable):
            _raise_if_private_type_exposed(
                f"Public module variable {variable.name!r}",
                variable.semantic_type,
                private_type_names,
            )
    for function in node.functions:
        _raise_for_private_type_exposure_in_function(function, private_type_names)
    for overload_set in node.overload_sets:
        if _is_public(overload_set):
            for procedure in overload_set.procedures:
                _raise_for_private_type_exposure_in_function(procedure, private_type_names)
    for semantic_class in node.classes:
        _raise_for_private_type_exposure_in_class(semantic_class, private_type_names)


def _has_known_iso_c_kind(semantic_type: models.SemanticType) -> bool:
    source_type = (semantic_type.origin.source_type or "").casefold()
    return any(token in source_type for token in _ISO_C_KIND_TOKENS)


def _convert_semantic_module(node, scope, legacy, custom_types):
    _raise_for_unresolved_generic_targets(node)
    _raise_for_unsupported_fortran_module_features(node)
    _raise_for_unsupported_allocatable_module_variables(node)
    _raise_for_unsupported_array_contracts(node)
    _raise_for_blocked_ownership_contracts(node)
    _raise_for_private_type_exposure(node)
    custom_types = dict(custom_types or {})
    class_lookup = _semantic_class_lookup(node.classes)
    class_descendants = _semantic_class_descendants(node.classes)
    class_order = _semantic_class_order(node.classes)
    for semantic_class in node.classes:
        custom_types.setdefault(semantic_class.name, _class_type(semantic_class))
        scope.insert_cls_construct(custom_types[semantic_class.name])

    class_items = [item for item in node.classes if _is_public(item)]
    classes = [
        semantic_ir_to_codegen_ast(
            item,
            scope,
            legacy,
            custom_types=custom_types,
            class_lookup=class_lookup,
            class_descendants=class_descendants,
            class_order=class_order,
        )
        for item in class_items
    ]
    funcs = []
    generated_overload_sets = []
    python_exports = {}
    native_imports = []
    overload_target_names = _pyi_overload_target_names(node)
    for item, converted in zip(class_items, classes, strict=True):
        python_exports[id(converted)] = _semantic_python_exports(item, converted, scope)
        if native_import := _pyi_native_import(item, converted):
            native_imports.append(native_import)
        native_imports.extend(_pyi_class_overload_native_imports(item, converted))
    for item in node.functions:
        converted = semantic_ir_to_codegen_ast(
            item,
            scope,
            legacy,
            custom_types=custom_types,
            class_lookup=class_lookup,
            class_descendants=class_descendants,
            class_order=class_order,
        )
        if isinstance(converted, FunctionOverloadSet):
            generated_overload_sets.append(converted)
        else:
            funcs.append(converted)
        python_exports[id(converted)] = _semantic_python_exports(item, converted, scope)
        if native_import := _pyi_native_import(item, converted, overload_target_names=overload_target_names):
            native_imports.append(native_import)
    overload_sets = [
        semantic_ir_to_codegen_ast(
            item,
            scope,
            legacy,
            custom_types=custom_types,
            class_lookup=class_lookup,
            class_descendants=class_descendants,
            class_order=class_order,
        )
        for item in node.overload_sets
    ]
    for item, converted in zip(node.overload_sets, overload_sets, strict=True):
        python_exports[id(converted)] = _semantic_python_exports(item, converted, scope)
        if native_import := _pyi_native_import(item, converted):
            native_imports.append(native_import)
    declarations = [
        semantic_ir_to_codegen_ast(item, scope, legacy, custom_types=custom_types) for item in node.variables
    ]
    for item, converted in zip(node.variables, declarations, strict=True):
        python_exports[id(converted)] = _semantic_python_exports(item, converted, scope)
        if native_import := _pyi_native_import(item, converted):
            native_imports.append(native_import)
    name = scope.get_new_public_name(node.name, object_type="module", owner=node.name)
    explicit_exports = node.metadata.get(models.PYTHON_EXPORTS_PREPARED_METADATA)
    imports = (
        native_imports
        if node.metadata.get(models.PYI_LOADED_METADATA)
        else [Import(module_name, target=()) for module_name in node.metadata.get("wrapper_native_modules", ())]
    )
    return Module(
        name,
        declarations,
        funcs,
        overload_sets=[*generated_overload_sets, *overload_sets],
        classes=classes,
        imports=imports,
        scope=scope,
        python_exports=python_exports if explicit_exports else None,
    )


def _semantic_python_exports(node, converted, scope) -> tuple[tuple[tuple[str, ...], str], ...]:
    if isinstance(node, models.ProcedureOverloadSet):
        metadata = node.procedures[0].metadata if node.procedures else {}
    else:
        metadata = node.metadata
    exports = metadata.get(models.PYTHON_EXPORTS_METADATA, ())
    if not exports:
        return ()
    public_name = str(scope.get_python_name(converted.name)) if any(item["name"] is None for item in exports) else ""
    return tuple(
        (tuple(item["namespace"]), public_name if item["name"] is None else str(item["name"])) for item in exports
    )


def _pyi_native_import(
    node,
    converted,
    *,
    overload_target_names: frozenset[str] = frozenset(),
    native_name_filter=None,
    preserve_native_alias: bool = False,
) -> Import | None:
    if isinstance(node, models.ProcedureOverloadSet):
        if not node.procedures:
            return None
        origin = node.procedures[0].origin
        native_names = _pyi_overload_native_names(node)
        if native_name_filter is not None:
            native_names = tuple(name for name in native_names if native_name_filter(name))
    else:
        origin = node.origin
        native_name = getattr(node, "native_name", None) or node.name
        if (
            isinstance(node, models.SemanticFunction)
            and node.visibility == "private"
            and {str(node.name), str(native_name)} & overload_target_names
        ):
            return None
        native_names = (str(native_name),)
    if origin.native_scope is None:
        return None
    if not native_names:
        return None
    targets = tuple(
        AsName(
            converted,
            str(native_name) if preserve_native_alias else str(converted.name),
            source_name=str(native_name),
        )
        for native_name in native_names
    )
    return Import(str(origin.native_scope), target=targets)


def _pyi_overload_native_names(node: models.ProcedureOverloadSet) -> tuple[str, ...]:
    names = {str(procedure.metadata.get(FORTRAN_GENERIC_NAME_METADATA, node.name)) for procedure in node.procedures}
    return tuple(sorted(names))


def _pyi_overload_target_names(node: models.SemanticModule) -> frozenset[str]:
    targets: set[str] = set()
    for overload_set in _iter_semantic_overload_sets(node):
        for procedure in overload_set.procedures:
            for value in (
                procedure.metadata.get(models.OVERLOAD_TARGET_METADATA),
                procedure.name,
                procedure.native_name,
            ):
                if value:
                    targets.add(str(value))
    return frozenset(targets)


def _iter_semantic_overload_sets(node: models.SemanticModule | models.SemanticClass):
    yield from node.overload_sets
    for semantic_class in node.classes:
        yield from _iter_semantic_overload_sets(semantic_class)


def _pyi_class_overload_native_imports(semantic_class: models.SemanticClass, converted: ClassDef) -> list[Import]:
    imports = []
    converted_by_name = {str(overload_set.name): overload_set for overload_set in converted.overload_sets}
    for overload_set in semantic_class.overload_sets:
        converted_overload = converted_by_name.get(str(overload_set.name))
        if converted_overload is None:
            continue
        native_import = _pyi_native_import(
            overload_set,
            converted_overload,
            native_name_filter=_is_importable_class_generic,
            preserve_native_alias=True,
        )
        if native_import is not None:
            imports.append(native_import)
    return imports


def _is_importable_class_generic(native_name: str) -> bool:
    compact = re.sub(r"\s+", "", native_name).casefold()
    return compact.startswith("operator(") or compact == "assignment(=)"


def _convert_procedure_overload_set(
    node, scope, legacy, custom_types, cls_base, class_lookup, class_descendants, class_order
):
    functions = []
    native_names = []
    for procedure in node.procedures:
        native_name = str(procedure.metadata.get(FORTRAN_GENERIC_NAME_METADATA, node.name))
        converted = semantic_ir_to_codegen_ast(
            procedure,
            scope,
            legacy,
            custom_types=custom_types,
            cls_base=cls_base,
            class_lookup=class_lookup,
            class_descendants=class_descendants,
            class_order=class_order,
        )
        if isinstance(converted, FunctionOverloadSet):
            functions.extend(converted.functions)
            native_names.extend([native_name] * len(converted.functions))
        else:
            functions.append(converted)
            native_names.append(native_name)
    name = scope.get_new_public_name(node.name, object_type="function", owner=f"generic {node.name}")
    overload_set = FunctionOverloadSet(str(name), functions, native_names=native_names)
    scope.insert_function(overload_set, name)
    return overload_set


def _convert_polymorphic_function(
    node,
    scope,
    legacy,
    dispatch_options,
    custom_types,
    cls_base,
    class_lookup,
    class_descendants,
    class_order,
):
    name = scope.get_new_name(node.name)
    variants = _polymorphic_dispatch_variants(node, dispatch_options)
    functions = [
        semantic_ir_to_codegen_ast(
            variant,
            scope,
            legacy,
            custom_types=custom_types,
            cls_base=cls_base,
            class_lookup=class_lookup,
            class_descendants=class_descendants,
            class_order=class_order,
            enable_polymorphic_dispatch=False,
        )
        for variant in variants
    ]
    native_name = node.native_name or node.name
    overload_set = FunctionOverloadSet(
        str(name),
        functions,
        native_name=native_name,
        native_names=(native_name,) * len(functions),
    )
    scope.insert_function(overload_set, name)
    return overload_set


def _semantic_function_result(node, func_scope, custom_types):
    if not node.return_type:
        return FunctionDefResult(NIL)
    return_dtype = _codegen_type(node.return_type.dtype, custom_types)
    if node.return_type.rank > 0:
        return_dtype = NumpyNDArrayType.get_new(
            return_dtype,
            node.return_type.rank,
            order=_numpy_array_order(node.return_type, node.return_type.rank),
            allows_strides=_array_allows_strides(node.return_type),
        )
    if isinstance(return_dtype, StringType):
        result_shape = _string_shape(node.return_type)
    elif node.return_type.rank > 0:
        result_shape = _codegen_array_shape(node.return_type, func_scope)
    else:
        result_shape = None
    result_ownership = _function_return_ownership_decision(node)
    result_var = Variable(
        return_dtype,
        node.name,
        shape=result_shape,
        memory_handling=result_ownership.storage_mode.value,
        intent="out",
        ownership_decision=result_ownership,
    )
    func_scope.insert_variable(result_var, name=node.name)
    return FunctionDefResult(result_var)


def _semantic_function_name(node, scope, native_name):
    if _is_public(node):
        return scope.get_new_public_name(
            native_name,
            python_name=node.name,
            object_type="function",
            owner=f"function {node.name}",
        )
    return scope.get_new_name(native_name, object_type="function")


def _semantic_function_decorators(node):
    decorators = {}
    if node.projection:
        decorators[PYI_NATIVE_PROJECTION_METADATA] = True
    if node.metadata.get(models.RUNTIME_HOLD_GIL_METADATA):
        decorators[models.RUNTIME_HOLD_GIL_METADATA] = True
    if isinstance(status_policy := node.metadata.get(models.RUNTIME_STATUS_ERROR_METADATA), dict):
        decorators[models.RUNTIME_STATUS_ERROR_METADATA] = dict(status_policy)
    return decorators


def _convert_semantic_function(
    node,
    scope,
    legacy,
    custom_types,
    cls_base,
    class_lookup,
    class_descendants,
    class_order,
    enable_polymorphic_dispatch,
):
    _raise_for_invalid_runtime_policy(node)
    _raise_for_unsupported_bind_c_abi(node, class_lookup or {})
    _raise_for_unsupported_allocatable_scalar_outputs(node)
    _raise_for_unsupported_pointer_outputs(node)
    _raise_for_blocked_ownership_contracts_in_function(node)
    _raise_for_unsupported_assumed_type_contracts(node)
    _raise_for_unsupported_array_contracts_in_function(node)
    passed_object_position = _passed_object_position(node)
    dispatch_options = (
        _polymorphic_dispatch_options(
            node,
            cls_base=cls_base,
            passed_object_position=passed_object_position,
            class_lookup=class_lookup or {},
            class_descendants=class_descendants or {},
            class_order=class_order or {},
        )
        if enable_polymorphic_dispatch
        else ()
    )
    _raise_for_unsupported_polymorphic_contracts(
        node,
        cls_base=cls_base,
        passed_object_position=passed_object_position,
        dispatch_positions={position for position, _ in dispatch_options},
    )
    if dispatch_options:
        return _convert_polymorphic_function(
            node,
            scope,
            legacy,
            dispatch_options,
            custom_types,
            cls_base,
            class_lookup,
            class_descendants,
            class_order,
        )
    func_scope = scope.new_child_scope(
        name=node.name,
        scope_type="function",
        public_namespace=scope.child_public_namespace("function", node.name),
    )
    constructor_self = _pyi_bound_constructor_self(node, cls_base, func_scope)
    declarations = [constructor_self] if constructor_self is not None else []
    declarations.extend(
        semantic_ir_to_codegen_ast(
            item,
            func_scope,
            legacy,
            custom_types=custom_types,
            cls_base=cls_base if constructor_self is None and index == passed_object_position else None,
            class_lookup=class_lookup,
            class_descendants=class_descendants,
            class_order=class_order,
        )
        for index, item in enumerate(node.arguments)
    )
    if constructor_self is not None:
        passed_object_position = 0
    result = _semantic_function_result(node, func_scope, custom_types)
    native_name = node.native_name or node.name
    name = _semantic_function_name(node, scope, native_name)
    func = FunctionDef(
        name,
        _codegen_function_arguments(declarations, passed_object_position),
        [],
        result,
        scope=func_scope,
        decorators=_semantic_function_decorators(node),
        is_external=legacy or (node.origin.source_language == "fortran" and node.origin.native_scope is None),
        is_private=node.visibility == "private",
        bind_c_external_name=(
            str(node.metadata.get("fortran_bind_c_name") or native_name)
            if node.metadata.get("fortran_bind_c")
            else None
        ),
        type_bound_name=_semantic_type_bound_name(node, cls_base),
    )
    scope._locals["functions"][name] = func
    return func


def _semantic_type_bound_name(node: models.SemanticFunction, cls_base: ClassDef | None) -> str | None:
    """Return the native type-bound binding name for a class method call."""
    if cls_base is None:
        return None
    name = str(node.name)
    if isinstance(node, models.SemanticMethod) and node.metadata.get(models.PYI_BIND_TARGET_METADATA):
        candidate = name[:-1] if name.endswith("_") else name
        if keyword.iskeyword(candidate):
            return candidate
    return name


def _convert_semantic_class(node, scope, legacy, custom_types, class_lookup, class_descendants, class_order):
    _raise_for_unresolved_generic_targets(node)
    _raise_for_unsupported_constructor_overloads(node)
    _raise_for_blocked_ownership_contracts_in_class(node)
    class_type = (custom_types or {}).get(node.name)
    if class_type is None:
        class_type = _class_type(node)
        if custom_types is not None:
            custom_types[node.name] = class_type
        scope.insert_cls_construct(class_type)

    if _is_public(node):
        name = scope.get_new_public_name(node.name, object_type="class", owner=f"type {node.name}")
    else:
        name = scope.get_new_name(node.name, object_type="class")
    class_scope = scope.new_child_scope(
        name=str(name),
        scope_type="class",
        public_namespace=scope.child_public_namespace("class", scope.get_python_name(name)),
    )
    attributes = [
        semantic_ir_to_codegen_ast(item, class_scope, legacy, custom_types=custom_types) for item in node.fields
    ]
    superclasses = tuple(
        cls for base_name in node.base_classes if (cls := scope.find(base_name, "classes")) is not None
    )
    decorators = {}
    if node.origin.metadata.get(models.PYI_SUPPRESS_DEFAULT_CONSTRUCTOR_METADATA):
        decorators[models.PYI_SUPPRESS_DEFAULT_CONSTRUCTOR_METADATA] = True
    decorators[models.RESOLVED_CLASS_INSTANCE_POLICY_METADATA] = node.metadata[
        models.RESOLVED_CLASS_INSTANCE_POLICY_METADATA
    ]
    decorators[models.RESOLVED_CLASS_SELF_POLICY_METADATA] = node.metadata[models.RESOLVED_CLASS_SELF_POLICY_METADATA]
    cls = ClassDef(
        name,
        attributes=attributes,
        methods=(),
        superclasses=superclasses,
        scope=class_scope,
        class_type=class_type,
        decorators=decorators,
    )
    scope.insert_class(cls)
    _populate_codegen_class_methods(
        cls,
        node,
        class_scope,
        legacy,
        custom_types,
        class_lookup,
        class_descendants,
        class_order,
    )
    return cls


def _populate_codegen_class_methods(
    cls, node, class_scope, legacy, custom_types, class_lookup, class_descendants, class_order
):
    for method in node.methods:
        converted_method = semantic_ir_to_codegen_ast(
            method,
            class_scope,
            legacy,
            custom_types=custom_types,
            cls_base=cls,
            class_lookup=class_lookup,
            class_descendants=class_descendants,
            class_order=class_order,
        )
        if isinstance(converted_method, FunctionOverloadSet):
            cls.add_new_overload_set(converted_method)
        else:
            cls.add_new_method(converted_method)
    for overload_set in node.overload_sets:
        cls.add_new_overload_set(
            semantic_ir_to_codegen_ast(
                overload_set,
                class_scope,
                legacy,
                custom_types=custom_types,
                cls_base=cls,
                class_lookup=class_lookup,
                class_descendants=class_descendants,
                class_order=class_order,
            )
        )


def _semantic_variable_type_and_shape(semantic_type, scope, custom_types):
    rank = semantic_type.rank
    dtype = _codegen_type(semantic_type.dtype, custom_types)
    if _is_constant(semantic_type):
        dtype = FinalType.get_new(dtype)
    if rank > 0:
        if isinstance(dtype, StringType):
            dtype = CharType()
        dtype = NumpyNDArrayType.get_new(
            dtype,
            rank,
            order=_numpy_array_order(semantic_type, rank),
            allows_strides=_array_allows_strides(semantic_type),
        )
    shape = (
        _string_shape(semantic_type) if isinstance(dtype, StringType) else _codegen_array_shape(semantic_type, scope)
    )
    return dtype, shape


def _fortran_array_category_and_source_shape(semantic_type):
    contract = _array_contract(semantic_type)
    if contract is None:
        return None, ()
    return contract.category, tuple(contract.source_shape)


def _semantic_variable_name(node, scope):
    try:
        return scope.get_expected_name(node.name)
    except RuntimeError:
        is_module_mutable = getattr(scope, "_scope_type", None) == "module" and not _is_constant(node.semantic_type)
        if isinstance(node, models.SemanticArgument):
            object_type = "argument"
        elif isinstance(node, models.SemanticField):
            object_type = "field"
        else:
            object_type = "variable"
        if _is_public(node) and not is_module_mutable:
            return scope.get_new_public_name(
                node.name,
                object_type=object_type,
                owner=f"{object_type} {node.name}",
            )
        return scope.get_new_name(node.name)


def _convert_semantic_variable(node, scope, custom_types, cls_base):
    semantic_type = node.semantic_type
    dtype, shape = _semantic_variable_type_and_shape(semantic_type, scope, custom_types)
    name = _semantic_variable_name(node, scope)
    ownership_decision = _variable_ownership_decision(node)
    default_value = (
        node.default_value
        if _is_constant(semantic_type)
        else node.metadata.get(models.RESOLVED_MODULE_VARIABLE_INITIALIZER_METADATA)
    )
    fortran_array_category, fortran_source_shape = _fortran_array_category_and_source_shape(semantic_type)
    var = Variable(
        dtype,
        name,
        shape=shape,
        memory_handling=ownership_decision.storage_mode.value,
        is_private=node.visibility == "private",
        is_target=bool(semantic_type.metadata.get("fortran_target")),
        is_optional=getattr(node, "optional", False),
        intent=getattr(node, "intent", "in"),
        passes_by_value=_passes_by_value(node),
        fortran_array_category=fortran_array_category,
        fortran_source_shape=fortran_source_shape,
        getter_ownership_decision=node.metadata.get(models.RESOLVED_GETTER_OWNERSHIP_POLICY_METADATA),
        ownership_decision=ownership_decision,
        setter_ownership_decision=node.metadata.get(models.RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA),
        projected_output=bool(node.metadata.get(PYI_PROJECTED_OUTPUT_METADATA)),
        assumed_rank=_is_assumed_rank(semantic_type),
        cls_base=cls_base,
        default_value=default_value,
    )
    scope.insert_variable(var, name=node.name)
    return var


def semantic_ir_to_codegen_ast(
    node,
    scope,
    legacy: bool = False,
    *,
    custom_types: dict[str, object] | None = None,
    cls_base: ClassDef | None = None,
    class_lookup: dict[str, models.SemanticClass] | None = None,
    class_descendants: dict[str, tuple[str, ...]] | None = None,
    class_order: dict[str, int] | None = None,
    enable_polymorphic_dispatch: bool = True,
):
    """Convert one semantic IR node into the current codegen AST representation."""

    if isinstance(node, models.SemanticModule):
        if node.metadata.get(models.PYI_LOADED_METADATA) and not node.metadata.get(
            models.PYI_NATIVE_CONTRACT_PREPARED_METADATA
        ):
            from .native_contract import prepare_pyi_native_contract

            prepare_pyi_native_contract([node])
        return _convert_semantic_module(node, scope, legacy, custom_types)

    if isinstance(node, models.ProcedureOverloadSet):
        return _convert_procedure_overload_set(
            node,
            scope,
            legacy,
            custom_types,
            cls_base,
            class_lookup,
            class_descendants,
            class_order,
        )

    if isinstance(node, models.SemanticFunction):
        return _convert_semantic_function(
            node,
            scope,
            legacy,
            custom_types,
            cls_base,
            class_lookup,
            class_descendants,
            class_order,
            enable_polymorphic_dispatch,
        )

    if isinstance(node, models.SemanticClass):
        return _convert_semantic_class(
            node,
            scope,
            legacy,
            custom_types,
            class_lookup,
            class_descendants,
            class_order,
        )

    if isinstance(node, models.SemanticArgument) and node.semantic_type.name == "Callable":
        return _codegen_callback_argument(
            node,
            scope,
            legacy,
            custom_types=custom_types,
            class_lookup=class_lookup,
            class_descendants=class_descendants,
            class_order=class_order,
        )

    if isinstance(node, models.SemanticVariable):
        return _convert_semantic_variable(node, scope, custom_types, cls_base)

    raise NotImplementedError(type(node))


ir_to_ast = semantic_ir_to_codegen_ast
