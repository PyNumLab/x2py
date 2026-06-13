"""Convert x2py semantic IR nodes into codegen AST nodes."""

from __future__ import annotations

import numpy as np

from x2py import SEMANTIC_DTYPE_TO_NUMPY_DTYPE
from x2py.codegen.models.core import (
    FunctionDef,
    FunctionDefArgument,
    FunctionDefResult,
    Module,
    Nil,
    Variable,
)
from x2py.codegen.models.datatypes import original_type_to_x2py_type, NumpyNDArrayType
from x2py.semantics import models


def _numpy_type(dtype: str):
    return getattr(np, dtype.removeprefix("numpy."))


def semantic_ir_to_codegen_ast(node, scope, legacy: bool = False):
    """Convert one semantic IR node into the current codegen AST representation."""

    if isinstance(node, models.SemanticModule):
        funcs = [semantic_ir_to_codegen_ast(item, scope, legacy) for item in node.functions]
        declarations = [semantic_ir_to_codegen_ast(item, scope, legacy) for item in node.variables]
        name = scope.get_new_name(node.name)
        return Module(name, declarations, funcs, scope=scope)

    if isinstance(node, models.SemanticFunction):
        func_scope = scope.new_child_scope(name=node.name, scope_type="function")
        declarations = [semantic_ir_to_codegen_ast(item, func_scope, legacy) for item in node.arguments]
        if node.return_type:
            return_dtype = node.return_type
            return_dtype = original_type_to_x2py_type[
                _numpy_type(SEMANTIC_DTYPE_TO_NUMPY_DTYPE[return_dtype.dtype])
            ]
            result_var = Variable(return_dtype, node.name)
            scope.insert_variable(result_var, name=node.name)
            result = FunctionDefResult(result_var)
        else:
            result = FunctionDefResult(Nil())

        args = [FunctionDefArgument(item) for item in declarations]
        name = scope.get_new_name(node.name)
        func = FunctionDef(name, args, [], result, scope=func_scope, is_external=legacy)
        scope._locals["functions"][name] = func
        return func

    if isinstance(node, models.SemanticVariable):
        dtype = node.semantic_type
        rank  = dtype.rank
        dtype = original_type_to_x2py_type[_numpy_type(SEMANTIC_DTYPE_TO_NUMPY_DTYPE[dtype.dtype])]
        if rank > 0:
            dtype = NumpyNDArrayType.get_new(dtype, rank, order='C')
        var = Variable(dtype, node.name)
        scope.insert_variable(var, name=node.name)
        return var

    raise NotImplementedError(type(node))


ir_to_ast = semantic_ir_to_codegen_ast
