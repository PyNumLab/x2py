"""Convert x2py semantic IR nodes into codegen AST nodes."""

from __future__ import annotations

import ast
from dataclasses import replace
from itertools import product
import numpy as np

from x2py import SEMANTIC_DTYPE_TO_NUMPY_DTYPE
from x2py.codegen.models.core import (
    Add,
    ClassDef,
    Div,
    FunctionDef,
    FunctionDefArgument,
    FunctionDefResult,
    FunctionOverloadSet,
    Minus,
    Module,
    Mul,
    UnarySub,
    Variable,
)
from x2py.codegen.models.datatypes import (
    DataTypeFactory,
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


def _memory_handling(semantic_type: models.SemanticType) -> str:
    if semantic_type.storage is not None and semantic_type.storage.array is not None:
        if semantic_type.storage.array.pointer:
            return "alias"
        if semantic_type.storage.array.allocatable:
            return "heap"
    return "stack"


def _passes_by_value(node: models.SemanticVariable) -> bool:
    return bool(
        getattr(node, "origin", None) is not None
        and isinstance(node.origin.metadata, dict)
        and node.origin.metadata.get("value")
    )


def _passed_object_position(node: models.SemanticFunction) -> int | None:
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


def _is_character_array(semantic_type: models.SemanticType | None) -> bool:
    return bool(semantic_type is not None and semantic_type.rank > 0 and semantic_type.name == "String")


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
    if _is_character_array(semantic_type):
        raise ValueError(f"{owner} is an array of character values, which is not supported by wrapper generation")
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
        intent = str(argument.intent).lower()
        if _is_pointer_array(argument.semantic_type) and intent in {"out", "inout"}:
            raise ValueError(
                f"Function {node.name!r} has pointer {intent} argument {argument.name!r}, "
                "which needs explicit pointer ownership, lifetime, shape, contiguity, and deallocation policy"
            )


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


def _raise_for_unsupported_bind_c_abi(node: models.SemanticFunction) -> None:
    if not node.metadata.get("fortran_bind_c"):
        return
    for argument in node.arguments:
        semantic_type = argument.semantic_type
        if semantic_type.rank > 0:
            continue
        if not _has_known_iso_c_kind(semantic_type):
            raise ValueError(
                f"Function {node.name!r} has bind(C) scalar argument {argument.name!r} "
                "without a supported ISO C binding kind"
            )
    if node.return_type is not None and node.return_type.rank == 0 and not _has_known_iso_c_kind(node.return_type):
        raise ValueError(f"Function {node.name!r} has a bind(C) scalar result without a supported ISO C binding kind")


def _has_known_iso_c_kind(semantic_type: models.SemanticType) -> bool:
    source_type = (semantic_type.origin.source_type or "").casefold()
    return any(token in source_type for token in _ISO_C_KIND_TOKENS)


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
        _raise_for_unresolved_generic_targets(node)
        _raise_for_unsupported_allocatable_module_variables(node)
        _raise_for_unsupported_array_contracts(node)
        custom_types = dict(custom_types or {})
        class_lookup = _semantic_class_lookup(node.classes)
        class_descendants = _semantic_class_descendants(node.classes)
        class_order = _semantic_class_order(node.classes)
        for semantic_class in node.classes:
            custom_types.setdefault(semantic_class.name, _class_type(semantic_class))
            scope.insert_cls_construct(custom_types[semantic_class.name])

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
            for item in node.classes
        ]
        funcs = []
        generated_overload_sets = []
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
        overload_sets = [*generated_overload_sets, *overload_sets]
        declarations = [
            semantic_ir_to_codegen_ast(
                item,
                scope,
                legacy,
                custom_types=custom_types,
            )
            for item in node.variables
        ]
        name = scope.get_new_name(node.name)
        return Module(name, declarations, funcs, overload_sets=overload_sets, classes=classes, scope=scope)

    if isinstance(node, models.ProcedureOverloadSet):
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
        name = scope.get_new_name(node.name)
        overload_set = FunctionOverloadSet(str(name), functions, native_names=native_names)
        scope.insert_function(overload_set, name)
        return overload_set

    if isinstance(node, models.SemanticFunction):
        _raise_for_unsupported_bind_c_abi(node)
        _raise_for_unsupported_allocatable_scalar_outputs(node)
        _raise_for_unsupported_pointer_outputs(node)
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
        func_scope = scope.new_child_scope(name=node.name, scope_type="function")
        declarations = [
            semantic_ir_to_codegen_ast(
                item,
                func_scope,
                legacy,
                custom_types=custom_types,
                cls_base=cls_base if index == passed_object_position else None,
                class_lookup=class_lookup,
                class_descendants=class_descendants,
                class_order=class_order,
            )
            for index, item in enumerate(node.arguments)
        ]
        if node.return_type:
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
            result_memory = _memory_handling(node.return_type)
            result_var = Variable(
                return_dtype,
                node.name,
                shape=result_shape,
                memory_handling=result_memory,
                intent="out",
            )
            func_scope.insert_variable(result_var, name=node.name)
            result = FunctionDefResult(result_var)
        else:
            result = FunctionDefResult(NIL)

        args = _codegen_function_arguments(declarations, passed_object_position)
        native_name = node.native_name or node.name
        name = scope.get_new_name(native_name)
        if native_name != node.name:
            scope.python_names[name] = node.name
        func = FunctionDef(
            name,
            args,
            [],
            result,
            scope=func_scope,
            is_external=legacy,
            is_private=node.visibility == "private",
            bind_c_external_name=(
                str(node.metadata.get("fortran_bind_c_name") or native_name)
                if node.metadata.get("fortran_bind_c")
                else None
            ),
        )
        scope._locals["functions"][name] = func
        return func

    if isinstance(node, models.SemanticClass):
        _raise_for_unresolved_generic_targets(node)
        class_type = (custom_types or {}).get(node.name)
        if class_type is None:
            class_type = _class_type(node)
            if custom_types is not None:
                custom_types[node.name] = class_type
            scope.insert_cls_construct(class_type)

        name = scope.get_new_name(node.name, object_type="class")
        class_scope = scope.new_child_scope(name=str(name), scope_type="class")
        attributes = [
            semantic_ir_to_codegen_ast(
                item,
                class_scope,
                legacy,
                custom_types=custom_types,
            )
            for item in node.fields
        ]
        superclasses = tuple(
            cls for base_name in node.base_classes if (cls := scope.find(base_name, "classes")) is not None
        )
        cls = ClassDef(
            name,
            attributes=attributes,
            methods=(),
            superclasses=superclasses,
            scope=class_scope,
            class_type=class_type,
        )
        scope.insert_class(cls)
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
        return cls

    if isinstance(node, models.SemanticVariable):
        semantic_type = node.semantic_type
        rank = semantic_type.rank
        dtype = _codegen_type(semantic_type.dtype, custom_types)
        if rank > 0:
            dtype = NumpyNDArrayType.get_new(
                dtype,
                rank,
                order=_numpy_array_order(semantic_type, rank),
                allows_strides=_array_allows_strides(semantic_type),
            )
        if isinstance(dtype, StringType):
            shape = _string_shape(semantic_type)
        else:
            shape = _codegen_array_shape(semantic_type, scope)
        try:
            name = scope.get_expected_name(node.name)
        except RuntimeError:
            name = scope.get_new_name(node.name)
        var = Variable(
            dtype,
            name,
            shape=shape,
            memory_handling=_memory_handling(semantic_type),
            is_private=node.visibility == "private",
            is_target=bool(semantic_type.metadata.get("fortran_target")),
            is_optional=getattr(node, "optional", False),
            intent=getattr(node, "intent", "in"),
            passes_by_value=_passes_by_value(node),
            assumed_rank=_is_assumed_rank(semantic_type),
            cls_base=cls_base,
        )
        scope.insert_variable(var, name=node.name)
        return var

    raise NotImplementedError(type(node))


ir_to_ast = semantic_ir_to_codegen_ast
