"""Convert x2py semantic IR nodes into codegen AST nodes."""

from __future__ import annotations

import numpy as np

from x2py import SEMANTIC_DTYPE_TO_NUMPY_DTYPE
from x2py.codegen.models.core import (
    ClassDef,
    FunctionDef,
    FunctionDefArgument,
    FunctionDefResult,
    FunctionOverloadSet,
    Module,
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
        elif text.isidentifier():
            result.append(scope.find(text, "variables"))
        else:
            result.append(None)
    return tuple(result)


def _class_type(semantic_class: models.SemanticClass):
    return DataTypeFactory(
        semantic_class.native_name or semantic_class.name,
        semantic_class.name,
    )()


def _memory_handling(semantic_type: models.SemanticType) -> str:
    if semantic_type.storage is not None and semantic_type.storage.array is not None:
        if semantic_type.storage.array.pointer:
            return "alias"
        if semantic_type.storage.array.allocatable:
            return "heap"
    return "stack"


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


def _is_pointer_array(semantic_type: models.SemanticType | None) -> bool:
    return bool(
        semantic_type is not None
        and semantic_type.storage is not None
        and semantic_type.storage.array is not None
        and semantic_type.storage.array.pointer
    )


def _raise_for_unsupported_allocatable_module_variables(node: models.SemanticModule) -> None:
    for variable in node.variables:
        semantic_type = variable.semantic_type
        if _is_allocatable_array(semantic_type) and not semantic_type.metadata.get("fortran_target"):
            raise ValueError(
                f"Module variable {variable.name!r} is an allocatable array without the Fortran target attribute; "
                "borrowed zero-copy module views require target storage"
            )


def _raise_for_unsupported_allocatable_outputs(node: models.SemanticFunction) -> None:
    for argument in node.arguments:
        if _is_allocatable_array(argument.semantic_type) and str(argument.intent).lower() == "inout":
            raise ValueError(
                f"Function {node.name!r} has allocatable inout argument {argument.name!r}, "
                "which needs a replacement policy"
            )


def _raise_for_unsupported_pointer_outputs(node: models.SemanticFunction) -> None:
    for argument in node.arguments:
        intent = str(argument.intent).lower()
        if _is_pointer_array(argument.semantic_type) and intent in {"out", "inout"}:
            raise ValueError(
                f"Function {node.name!r} has pointer {intent} argument {argument.name!r}, "
                "which needs explicit pointer ownership, lifetime, shape, contiguity, and deallocation policy"
            )


def semantic_ir_to_codegen_ast(
    node,
    scope,
    legacy: bool = False,
    *,
    custom_types: dict[str, object] | None = None,
    cls_base: ClassDef | None = None,
):
    """Convert one semantic IR node into the current codegen AST representation."""

    if isinstance(node, models.SemanticModule):
        _raise_for_unresolved_generic_targets(node)
        _raise_for_unsupported_allocatable_module_variables(node)
        custom_types = dict(custom_types or {})
        for semantic_class in node.classes:
            custom_types.setdefault(semantic_class.name, _class_type(semantic_class))
            scope.insert_cls_construct(custom_types[semantic_class.name])

        classes = [
            semantic_ir_to_codegen_ast(
                item,
                scope,
                legacy,
                custom_types=custom_types,
            )
            for item in node.classes
        ]
        funcs = [
            semantic_ir_to_codegen_ast(
                item,
                scope,
                legacy,
                custom_types=custom_types,
            )
            for item in node.functions
        ]
        overload_sets = [
            semantic_ir_to_codegen_ast(
                item,
                scope,
                legacy,
                custom_types=custom_types,
            )
            for item in node.overload_sets
        ]
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
        functions = [
            semantic_ir_to_codegen_ast(
                procedure,
                scope,
                legacy,
                custom_types=custom_types,
                cls_base=cls_base,
            )
            for procedure in node.procedures
        ]
        name = scope.get_new_name(node.name)
        native_names = tuple(
            str(procedure.metadata.get(FORTRAN_GENERIC_NAME_METADATA, node.name)) for procedure in node.procedures
        )
        overload_set = FunctionOverloadSet(str(name), functions, native_names=native_names)
        scope.insert_function(overload_set, name)
        return overload_set

    if isinstance(node, models.SemanticFunction):
        _raise_for_unsupported_allocatable_outputs(node)
        _raise_for_unsupported_pointer_outputs(node)
        func_scope = scope.new_child_scope(name=node.name, scope_type="function")
        passed_object_position = _passed_object_position(node)
        declarations = [
            semantic_ir_to_codegen_ast(
                item,
                func_scope,
                legacy,
                custom_types=custom_types,
                cls_base=cls_base if index == passed_object_position else None,
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
            result_shape = _string_shape(node.return_type) if isinstance(return_dtype, StringType) else None
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
            cls.add_new_method(
                semantic_ir_to_codegen_ast(
                    method,
                    class_scope,
                    legacy,
                    custom_types=custom_types,
                    cls_base=cls,
                )
            )
        for overload_set in node.overload_sets:
            cls.add_new_overload_set(
                semantic_ir_to_codegen_ast(
                    overload_set,
                    class_scope,
                    legacy,
                    custom_types=custom_types,
                    cls_base=cls,
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
            cls_base=cls_base,
        )
        scope.insert_variable(var, name=node.name)
        return var

    raise NotImplementedError(type(node))


ir_to_ast = semantic_ir_to_codegen_ast
