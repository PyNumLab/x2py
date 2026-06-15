"""
Module describing the code-wrapping class : FortranToCWrapper
which creates an interface exposing Fortran code to C.
THIS CREATES BIND(C) FORTRAN FILE
"""

import re
import warnings
from functools import reduce

from ..bind_c import (
    C_NULL_CHAR,
    BindCArrayType,
    BindCArrayVariable,
    BindCClassDef,
    BindCClassProperty,
    BindCFunctionDef,
    BindCModule,
    BindCModuleVariable,
    BindCPointer,
    BindCSizeOf,
    BindCVariable,
    C_F_Pointer,
    CLocFunc,
    DeallocatePointer,
    FortranTransfer,
    c_malloc,
)
from ..models.core import (
    AliasAssign,
    Allocate,
    ArrayAllocated,
    ArrayShapeElement,
    ArraySize,
    AsName,
    Assign,
    EmptyNode,
    FunctionAddress,
    FunctionCallArgument,
    FunctionDef,
    FunctionDefArgument,
    FunctionDefResult,
    get_direct_overload_set,
    get_enclosing_module,
    If,
    IfSection,
    Import,
    FunctionOverloadSet,
    Pass,
)
from ..models.datatypes import (
    CharType,
    CustomDataType,
    FinalType,
    FixedSizeNumericType,
    NumpyInt64Type,
    TupleType,
    NIL,
    cast_to,
    convert_to_literal,
)
from ..models.core import Slice
from ..models.datatypes import NumpyInt32Type, NumpyNDArrayType, numpy_precision_map
from ..models.core import Add, IsNot, Mul
from ..models.core import DottedVariable, IndexedElement, Variable
from ..scope import Scope

from .base import BridgeGenerator


class FortranToCBridgeGenerator(BridgeGenerator):
    """
    Class for creating a wrapper exposing Fortran code to C.

    A class which provides all necessary functions for wrapping different AST
    objects such that the resulting AST is C-compatible. This new AST is
    printed as an intermediary layer.

    Parameters
    ----------
    sharedlib_dirpath : str
        The folder where the generated .so file will be located.
    verbose : int
        The level of verbosity.
    """

    target_language = "C"
    start_language = "Fortran"

    def __init__(self, sharedlib_dirpath, verbose):
        self._additional_exprs = []
        self._generator_names_dict = {}
        super().__init__(verbose)

    def _get_function_def_body(self, func, generated_args, results, handled=()):
        """
        Get the body of the bind c function definition.

        Get the body of the bind c function definition by inserting if blocks
        to check the presence of optional variables. Once we have ascertained
        the presence of the variables the original function is called. This
        code slices array variables to ensure the correct step.

        Parameters
        ----------
        func : FunctionDef
            The function which should be called.

        generated_args : list[dict]
            A list containing the dictionaries returned by _extract_FunctionDefArgument.

        results : list of Variables
            The Variables where the result of the function call will be saved.

        handled : tuple
            A list of all variables which have been handled (checked to see if they
            are present).

        Returns
        -------
        list
            A list of codegen nodes describing the body of the function.
        """
        next_optional_arg = next(
            (a for a in generated_args if a["c_arg"].var.original_var.is_optional and a not in handled),
            None,
        )
        if next_optional_arg:
            args = generated_args.copy()
            optional_var = next_optional_arg["c_arg"].var
            optional_var = getattr(optional_var, "new_var", optional_var)
            class_type = optional_var.class_type
            if isinstance(class_type, BindCArrayType):
                optional_var = self.scope.collect_tuple_element(IndexedElement(optional_var, convert_to_literal(0)))

            handled += (next_optional_arg,)
            true_section = IfSection(
                IsNot(optional_var, NIL),
                self._get_function_def_body(func, args, results, handled),
            )
            args.remove(next_optional_arg)
            false_section = IfSection(
                convert_to_literal(True), self._get_function_def_body(func, args, results, handled)
            )
            return [If(true_section, false_section)]
        args = [a["f_arg"] for a in generated_args]
        body = [line for a in generated_args for line in a["body"]]

        if isinstance(func, FunctionOverloadSet):
            selected = func.point(args)
            native_name = func.native_name_for(selected)
        else:
            selected = None
            native_name = ""
        if re.sub(r"\s+", "", native_name).casefold() == "assignment(=)":
            lhs, rhs = func.native_arguments(selected, args)
            return [*body, Assign(lhs.value, rhs.value)]

        if len(results) == 1:
            res = results[0]
            func_call = AliasAssign(res, func(*args)) if res.is_alias else Assign(res, func(*args))
        else:
            func_call = Assign(results, func(*args))
        return [*body, func_call]

    def _visit_Module(self, expr):
        """
        Create a BindCModule which is compatible with C.

        Create a BindCModule which provides an interface between C and the
        Module described by expr. This includes wrapping functions,
        interfaces, classes and module variables.

        Parameters
        ----------
        expr : x2py.ast.core.Module
            The module to be generated.

        Returns
        -------
        x2py.ast.bind_c.BindCModule
            The C-compatible module.
        """
        # Define scope
        scope = expr.scope
        mod_scope = Scope(
            name=f"bind_c_{expr.name}",
            used_symbols=scope.local_used_symbols.copy(),
            original_symbols=scope.python_names.copy(),
            scope_type="module",
        )
        name = mod_scope.get_new_name(f"bind_c_{expr.name}")
        self.scope = mod_scope

        # Wrap contents
        funcs_to_generate = [f for f in expr.funcs if f.is_semantic and not f.is_private]

        funcs = [self._visit(f) for f in funcs_to_generate]
        if expr.init_func:
            init_func = funcs[next(i for i, f in enumerate(funcs_to_generate) if f == expr.init_func)]
        else:
            init_func = None
        if expr.free_func:
            free_func = funcs[next(i for i, f in enumerate(funcs_to_generate) if f == expr.free_func)]
        else:
            free_func = None
        removed_functions = [f for f, w in zip(funcs_to_generate, funcs, strict=False) if isinstance(w, EmptyNode)]
        funcs = [f for f in funcs if not isinstance(f, EmptyNode)]
        interfaces = [self._visit(f) for f in expr.overload_sets]
        classes = [self._visit(f) for f in expr.classes]
        variables = [self._visit(v) for v in expr.variables if not v.is_private]
        variable_getters = [v for v in variables if isinstance(v, BindCArrayVariable)]
        # Import the module and its dependencies (in case they are used for argument types)
        if any(f.is_external for f in funcs_to_generate):
            imports = []
        else:
            imports = [Import(expr.name, target=expr, mod=expr), *expr.imports]

        # Ensure renamed datatypes are mapped to their new name
        self.scope.imports["cls_constructs"].update(expr.scope.imports["cls_constructs"])

        self._generator_names_dict[expr.name] = name

        self.exit_scope()

        return BindCModule(
            name,
            variables,
            funcs,
            variable_wrappers=variable_getters,
            init_func=init_func,
            free_func=free_func,
            overload_sets=interfaces,
            classes=classes,
            imports=imports,
            original_module=expr,
            scope=mod_scope,
            removed_functions=removed_functions,
        )

    def _visit_FunctionDef(self, expr):
        """
        Create a C-compatible function which executes the original function.

        Create a function which can be called from C which internally calls the original
        function. It does this by wrapping the arguments and the results and unrolling
        the body using self._get_function_def_body to ensure optional arguments are
        present before accessing them. With all this information a BindCFunctionDef is
        created which is C-compatible.

        Functions which cannot be wrapped raise a warning and return an EmptyNode. This
        is the case for functions with functions as arguments.

        Parameters
        ----------
        expr : FunctionDef
            The function to generate.

        Returns
        -------
        BindCFunctionDef
            The C-compatible function.
        """
        if expr.is_private or not expr.is_semantic:
            return EmptyNode()

        orig_name = expr.cls_name or expr.name
        name = self.scope.get_new_name(f"bind_c_{orig_name.lower()}")
        self._generator_names_dict[expr.name] = name
        self._additional_exprs = []

        if any(isinstance(a.var, FunctionAddress) for a in expr.arguments):
            warnings.warn("Functions with functions as arguments cannot be wrapped by x2py", stacklevel=2)
            return EmptyNode()

        # Create the scope
        func_scope = self.scope.new_child_scope(name, "function")
        self.scope = func_scope

        # Wrap the arguments and collect the expressions passed as the call argument.
        generated_args = [self._extract_FunctionDefArgument(a, expr) for a in expr.arguments]
        func_arguments = [a["c_arg"] for a in generated_args]
        call_arguments = [a["f_arg"] for a in generated_args]
        {fa: ca for ca, fa in zip(call_arguments, func_arguments, strict=False)}

        if expr.results.var is NIL:
            func_results = NIL
            func_call_results = []
        else:
            result = self._extract_FunctionDefResult(expr.results.var, expr.scope)
            self._additional_exprs.extend(result["body"])
            func_results = result["c_result"]
            func_call_results = self.scope.collect_all_tuple_elements(result["f_result"])

        overload_set = get_direct_overload_set(expr)

        if overload_set:
            body = self._get_function_def_body(overload_set, generated_args, func_call_results)
        else:
            body = self._get_function_def_body(expr, generated_args, func_call_results)

        body.extend(self._additional_exprs)
        self._additional_exprs.clear()

        if expr.scope.get_python_name(expr.name) == "__del__" and call_arguments:
            if expr.is_external:
                # If __del__ is not defined in the module then the del call is unnecessary
                body.pop()
            body.append(DeallocatePointer(call_arguments[0].value))

        self.exit_scope()

        imports = []
        if expr.is_external and expr.scope.get_python_name(expr.name) != "__del__":
            imports.append(Import(expr.name, target=(), mod=expr))

        func = BindCFunctionDef(
            name,
            func_arguments,
            body,
            FunctionDefResult(func_results),
            imports=imports,
            scope=func_scope,
            original_function=expr,
            docstring=expr.docstring,
            result_pointer_map=expr.result_pointer_map,
        )

        self.scope.insert_function(func, name)

        return func

    def _visit_FunctionOverloadSet(self, expr):
        """
        Create an interface containing only C-compatible functions.

        Create an interface containing only functions which can be called from C
        from an interface which is not necessarily C-compatible.

        Parameters
        ----------
        expr : x2py.ast.core.FunctionOverloadSet
            The interface to be wrapped.

        Returns
        -------
        x2py.ast.core.FunctionOverloadSet
            The C-compatible interface.
        """
        functions = [self._visit(f) for f in expr.functions if not isinstance(f, EmptyNode)]
        return FunctionOverloadSet(
            expr.name,
            functions,
            expr.is_argument,
            native_name=expr.native_name,
            native_names=expr.native_names,
        )

    def _extract_FunctionDefArgument(self, expr, func):
        """
        Extract the C-compatible FunctionDefArgument from the Fortran FunctionDefArgument.

        Extract the C-compatible FunctionDefArgument from the Fortran FunctionDefArgument.

        The extraction is done by finding the appropriate function
        _extract_X_FunctionDefArgument for the object expr. X is the class type of the
        variable stored in the object expr. If this function does not exist then the
        method resolution order is used to search for other compatible
        _extract_X_FunctionDefArgument functions. If none are found then an error is raised.

        Parameters
        ----------
        expr : FunctionDefArgument
            An object representing the FunctionDefArgument in the Fortran code which should
            be exposed to the C code.

        func : FunctionDef
            The function being wrapped.

        Returns
        -------
        dict
            A dictionary describing the objects necessary to access the argument.
        """
        var = expr.var
        class_type = var.class_type

        classes = type(class_type).__mro__
        for cls in classes:
            annotation_method = f"_extract_{cls.__name__}_FunctionDefArgument"
            if hasattr(self, annotation_method):
                func_def_argument_dict = getattr(self, annotation_method)(var, func)
                new_var = func_def_argument_dict["c_arg"]
                func_def_argument_dict["c_arg"] = FunctionDefArgument(
                    new_var,
                    value=expr.value,
                    posonly=expr.is_posonly,
                    kwonly=expr.is_kwonly,
                    annotation=expr.annotation,
                    bound_argument=expr.bound_argument,
                    bound_argument_position=expr.bound_argument_position,
                    persistent_target=expr.persistent_target,
                    is_vararg=expr.is_vararg,
                    is_kwarg=expr.is_kwarg,
                )

                if getattr(func, "is_external", False):
                    func_def_argument_dict["f_arg"] = FunctionCallArgument(func_def_argument_dict["f_arg"])
                else:
                    func_def_argument_dict["f_arg"] = FunctionCallArgument(
                        func_def_argument_dict["f_arg"], keyword=expr.name
                    )
                return func_def_argument_dict

        # Unknown object, we raise an error.
        raise NotImplementedError(f"Wrapping function arguments is not implemented for type {class_type}.")

    def _extract_FixedSizeNumericType_FunctionDefArgument(self, var, func):
        name = var.name
        self.scope.insert_symbol(name)
        collisionless_name = self.scope.get_expected_name(name)
        if var.is_optional:
            f_arg = var.clone(
                collisionless_name,
                new_class=Variable,
                is_argument=False,
                is_optional=False,
                memory_handling="alias",
            )
            new_var = Variable(
                BindCPointer(),
                self.scope.get_new_name(f"bound_{name}"),
                is_argument=True,
                is_optional=False,
                memory_handling="alias",
            )
            body = [C_F_Pointer(new_var, f_arg)]
        else:
            f_arg = var.clone(collisionless_name, new_class=Variable, is_argument=True)
            new_var = f_arg
            body = []
        self.scope.insert_variable(f_arg)
        return {"c_arg": BindCVariable(new_var, var), "f_arg": f_arg, "body": body}

    def _extract_CustomDataType_FunctionDefArgument(self, var, func):
        name = var.name
        self.scope.insert_symbol(name)
        collisionless_name = self.scope.get_expected_name(name)
        f_arg = var.clone(
            collisionless_name,
            new_class=Variable,
            is_argument=False,
            is_optional=False,
            memory_handling="alias",
        )
        new_var = Variable(
            BindCPointer(),
            self.scope.get_new_name(f"bound_{name}"),
            is_argument=True,
            is_optional=False,
            memory_handling="alias",
        )
        body = [C_F_Pointer(new_var, f_arg)]
        self.scope.insert_variable(f_arg)
        return {"c_arg": BindCVariable(new_var, var), "f_arg": f_arg, "body": body}

    def _extract_NumpyNDArrayType_FunctionDefArgument(self, var, func):
        name = var.name
        scope = self.scope
        scope.insert_symbol(name)
        collisionless_name = scope.get_expected_name(name)
        rank = var.rank
        order = var.order
        allows_strides = var.class_type.allows_strides
        bind_var = Variable(
            BindCPointer(),
            scope.get_new_name(f"bound_{name}"),
            is_argument=True,
            is_optional=False,
            memory_handling="alias",
        )
        arg_var = var.clone(
            collisionless_name,
            is_argument=False,
            is_optional=False,
            memory_handling="alias",
            new_class=Variable,
        )
        scope.insert_variable(arg_var)
        scope.insert_variable(bind_var)

        base_shape = [
            scope.get_temporary_variable(NumpyInt64Type(), name=f"{name}_base_shape_{i + 1}", is_argument=True)
            for i in range(rank)
        ]
        stride = (
            [
                scope.get_temporary_variable(NumpyInt64Type(), name=f"{name}_stride_{i + 1}", is_argument=True)
                for i in range(rank)
            ]
            if allows_strides
            else []
        )
        ubound = (
            [
                scope.get_temporary_variable(NumpyInt64Type(), name=f"{name}_ubound_{i + 1}", is_argument=True)
                for i in range(rank)
            ]
            if allows_strides
            else []
        )

        body = [C_F_Pointer(bind_var, arg_var, base_shape[::-1] if order == "C" else base_shape)]

        c_arg_var = Variable(
            BindCArrayType.get_new(rank, has_strides=allows_strides),
            scope.get_new_name(),
            is_argument=True,
            shape=(convert_to_literal(rank * 3 + 1 if allows_strides else rank + 1),),
        )

        scope.insert_symbolic_alias(IndexedElement(c_arg_var, convert_to_literal(0)), bind_var)
        for i, s in enumerate(base_shape):
            scope.insert_symbolic_alias(IndexedElement(c_arg_var, convert_to_literal(i + 1)), s)
        if allows_strides:
            for i, s in enumerate(ubound):
                scope.insert_symbolic_alias(IndexedElement(c_arg_var, convert_to_literal(i + rank + 1)), s)
            for i, s in enumerate(stride):
                scope.insert_symbolic_alias(IndexedElement(c_arg_var, convert_to_literal(i + 2 * rank + 1)), s)

            start = convert_to_literal(1)  # C_F_Pointer leads to default Fortran lbound
            indexes = [
                Slice(start, Add(stop, convert_to_literal(1)), step) for step, stop in zip(stride, ubound, strict=False)
            ]
            f_arg = IndexedElement(arg_var, *indexes)
        else:
            f_arg = arg_var

        return {"c_arg": BindCVariable(c_arg_var, var), "f_arg": f_arg, "body": body}

    def _extract_HomogeneousTupleType_FunctionDefArgument(self, var, func):
        name = var.name
        scope = self.scope
        scope.insert_symbol(name)
        collisionless_name = scope.get_expected_name(name)
        rank = var.rank
        bind_var = Variable(
            BindCPointer(),
            scope.get_new_name(f"bound_{name}"),
            is_argument=True,
            is_optional=False,
            memory_handling="alias",
        )
        arg_var = var.clone(
            collisionless_name,
            is_argument=False,
            is_optional=False,
            memory_handling="alias",
            new_class=Variable,
        )
        scope.insert_variable(arg_var)
        scope.insert_variable(bind_var)

        shape_var = scope.get_temporary_variable(NumpyInt64Type(), name=f"{name}_size", is_argument=True)

        body = [C_F_Pointer(bind_var, arg_var, (shape_var,))]

        c_arg_var = Variable(
            BindCArrayType.get_new(rank, has_strides=False),
            scope.get_new_name(),
            is_argument=True,
            shape=(convert_to_literal(rank + 1),),
        )

        scope.insert_symbolic_alias(IndexedElement(c_arg_var, convert_to_literal(0)), bind_var)
        scope.insert_symbolic_alias(IndexedElement(c_arg_var, convert_to_literal(1)), shape_var)

        return {"c_arg": BindCVariable(c_arg_var, var), "f_arg": arg_var, "body": body}

    def _extract_StringType_FunctionDefArgument(self, var, func):
        name = var.name
        scope = self.scope
        scope.insert_symbol(name)
        collisionless_name = scope.get_expected_name(name)
        rank = var.rank
        bind_var = Variable(
            FinalType.get_new(BindCPointer()),
            scope.get_new_name(f"bound_{name}"),
            is_argument=True,
            is_optional=False,
            memory_handling="alias",
        )
        shape_var = scope.get_temporary_variable(NumpyInt64Type(), name=f"{name}_size", is_argument=True)
        array_var = Variable(
            NumpyNDArrayType.get_new(CharType(), 1, None),
            scope.get_new_name(name),
            memory_handling="alias",
        )
        scope.insert_variable(bind_var)
        scope.insert_variable(array_var)

        fixed_len = var.alloc_shape[0]
        if fixed_len == 1:
            fixed_var = var.clone(
                scope.get_new_name(f"{name}_fixed"),
                is_argument=False,
                is_optional=False,
                memory_handling="stack",
                new_class=Variable,
            )
            scope.insert_variable(fixed_var)
            body = [
                C_F_Pointer(bind_var, array_var, (shape_var,)),
                Assign(fixed_var, FortranTransfer(array_var, fixed_var)),
            ]
            f_arg = fixed_var
        else:
            arg_var = var.clone(
                collisionless_name,
                is_argument=False,
                is_optional=False,
                memory_handling="stack",
                shape=(shape_var,),
                new_class=Variable,
            )
            scope.insert_variable(arg_var)
            body = [
                C_F_Pointer(bind_var, array_var, (shape_var,)),
                Assign(arg_var, FortranTransfer(array_var, arg_var)),
            ]
            if fixed_len is not None:
                fixed_var = var.clone(
                    scope.get_new_name(f"{name}_fixed"),
                    is_argument=False,
                    is_optional=False,
                    memory_handling="stack",
                    new_class=Variable,
                )
                scope.insert_variable(fixed_var)
                body.append(Assign(fixed_var, arg_var))
                f_arg = fixed_var
            else:
                f_arg = arg_var

        c_arg_var = Variable(
            BindCArrayType.get_new(rank, has_strides=False),
            scope.get_new_name(),
            is_argument=True,
            shape=(convert_to_literal(2),),
        )

        scope.insert_symbolic_alias(IndexedElement(c_arg_var, convert_to_literal(0)), bind_var)
        scope.insert_symbolic_alias(IndexedElement(c_arg_var, convert_to_literal(1)), shape_var)

        return {"c_arg": BindCVariable(c_arg_var, var), "f_arg": f_arg, "body": body}

    def _visit_Variable(self, expr):
        """
        Create all objects necessary to expose a module variable to C.

        Create and return the objects which must be printed in the wrapping
        module in order to expose the variable to C. In the case of scalar
        numerical values nothing needs to be done so an EmptyNode is returned.
        In the case of numerical arrays a C-compatible function must be created
        which returns the array. This is necessary because built-in Fortran
        arrays are not C-compatible. In the case of classes a C-compatible
        function is also created which returns a pointer to the class object.

        Parameters
        ----------
        expr : x2py.ast.variables.Variable
            The module variable.

        Returns
        -------
        codegen model object
            The AST object describing the code which must be printed in
            the wrapping module to expose the variable.
        """
        if isinstance(expr.class_type, FixedSizeNumericType):
            return expr.clone(expr.name, new_class=BindCModuleVariable)
        if isinstance(expr.class_type, NumpyNDArrayType):
            scope = self.scope
            func_name = scope.get_new_name("bind_c_" + expr.name.lower())
            func_scope = scope.new_child_scope(func_name, "function")
            mod = get_enclosing_module(expr)
            assert mod is not None
            import_mod = Import(mod.name, AsName(expr, expr.name), mod=mod)
            func_scope.imports["variables"][expr.name] = expr

            # Create the data pointer
            result = self._get_bind_c_array(expr.name, expr, expr.shape, pointer_target=True)
            func = BindCFunctionDef(
                name=func_name,
                body=result["body"],
                arguments=[],
                results=FunctionDefResult(result["c_result"]),
                imports=[import_mod],
                scope=func_scope,
                original_function=expr,
            )
            return expr.clone(
                expr.name,
                new_class=BindCArrayVariable,
                wrapper_function=func,
                original_variable=expr,
            )
        raise NotImplementedError(f"Objects of type {expr.class_type} cannot be wrapped yet")

    def _visit_DottedVariable(self, expr):
        """
        Create all objects necessary to expose a class attribute to C.

        Create the getter and setter functions which expose the class attribute
        to C. Return these objects in a BindCClassProperty.

        Parameters
        ----------
        expr : DottedVariable
            The class attribute.

        Returns
        -------
        BindCClassProperty
            An object containing the getter and setter functions which expose
            the class attribute to C.
        """
        lhs = expr.lhs
        class_dtype = lhs.dtype
        # ----------------------------------------------------------------------------------
        #                        Create getter
        # ----------------------------------------------------------------------------------
        getter_name = self.scope.get_new_name(f"{class_dtype.name}_{expr.name}_getter".lower())
        getter_scope = self.scope.new_child_scope(getter_name, "function")
        self.scope = getter_scope
        self.scope.insert_symbol(expr.name)
        getter_result_info = self._extract_FunctionDefResult(expr, lhs.cls_base.scope)
        getter_result = getter_result_info["c_result"]

        getter_arg_generator = self._extract_FunctionDefArgument(FunctionDefArgument(lhs, bound_argument=True), expr)
        self_obj = getter_arg_generator["f_arg"].value
        getter_arg = getter_arg_generator["c_arg"]

        getter_body = getter_arg_generator["body"]

        attrib = expr.clone(expr.name, lhs=self_obj)
        obj = self.scope.find(expr.name)
        # Cast the C variable into a Python variable
        if expr.rank > 0 and expr.memory_handling == "heap":
            unallocated_body = [
                Assign(getter_result_info["bind_var"], NIL),
                *[
                    Assign(shape_var, convert_to_literal(0, dtype=NumpyInt32Type()))
                    for shape_var in getter_result_info["shape_vars"]
                ],
            ]
            getter_body.append(
                If(
                    IfSection(
                        ArrayAllocated(attrib),
                        [AliasAssign(obj, attrib), *getter_result_info["body"]],
                    ),
                    IfSection(convert_to_literal(True), unallocated_body),
                )
            )
        elif expr.rank > 0 or isinstance(expr.dtype, CustomDataType):
            getter_body.append(AliasAssign(obj, attrib))
            getter_body.extend(getter_result_info["body"])
        else:
            getter_body.append(Assign(getter_result_info["f_result"], attrib))
            getter_body.extend(getter_result_info["body"])
        self._additional_exprs.clear()
        self.exit_scope()

        getter = BindCFunctionDef(
            getter_name,
            (getter_arg,),
            getter_body,
            FunctionDefResult(getter_result),
            original_function=expr,
            scope=getter_scope,
        )

        # ----------------------------------------------------------------------------------
        #                        Create setter
        # ----------------------------------------------------------------------------------
        setter_name = self.scope.get_new_name(f"{class_dtype.name}_{expr.name}_setter".lower())
        setter_scope = self.scope.new_child_scope(setter_name, "function")
        self.scope = setter_scope
        self.scope.insert_symbol(expr.name)

        setter_arg_generators = (
            self._extract_FunctionDefArgument(FunctionDefArgument(lhs, bound_argument=True), expr),
            self._extract_FunctionDefArgument(FunctionDefArgument(expr), expr),
        )
        setter_args = (setter_arg_generators[0]["c_arg"], setter_arg_generators[1]["c_arg"])
        if expr.is_alias:
            setter_args[1].persistent_target = True

        self_obj = setter_arg_generators[0]["f_arg"].value
        set_val = setter_arg_generators[1]["f_arg"].value

        setter_body = setter_arg_generators[0]["body"] + setter_arg_generators[1]["body"]

        attrib = expr.clone(expr.name, lhs=self_obj)
        # Cast the C variable into a Python variable
        if expr.memory_handling == "alias":
            setter_body.append(AliasAssign(attrib, set_val))
        else:
            setter_body.append(Assign(attrib, set_val))
        self.exit_scope()

        setter = BindCFunctionDef(
            setter_name,
            setter_args,
            setter_body,
            original_function=expr,
            scope=setter_scope,
        )
        return BindCClassProperty(lhs.cls_base.scope.get_python_name(expr.name), getter, setter, lhs.dtype)

    def _visit_ClassDef(self, expr):
        """
        Create all objects necessary to expose a class definition to C.

        Create all objects necessary to expose a class definition to C.

        Parameters
        ----------
        expr : ClassDef
            The class to be wrapped.

        Returns
        -------
        BindCClassDef
            The wrapped class.
        """
        name = expr.name
        func_name = self.scope.get_new_name(f"{name}_bind_c_alloc".lower())
        func_scope = self.scope.new_child_scope(func_name, "function")

        # Allocatable is not returned so it must appear in local scope
        local_var = Variable(
            expr.class_type,
            func_scope.get_new_name(f"{name}_obj"),
            cls_base=expr,
            memory_handling="alias",
        )
        func_scope.insert_variable(local_var)

        # Create the C-compatible data pointer
        bind_var = Variable(
            BindCPointer(),
            func_scope.get_new_name("bound_" + name),
            memory_handling="alias",
        )
        result = BindCVariable(bind_var, local_var)

        # Define the additional steps necessary to define and fill ptr_var
        alloc = Allocate(local_var, shape=None, status="unallocated")
        c_loc = CLocFunc(local_var, bind_var)
        body = [alloc, c_loc]

        new_method = BindCFunctionDef(
            func_name,
            [],
            body,
            FunctionDefResult(result),
            original_function=None,
            scope=func_scope,
        )

        methods = [self._visit(m) for m in expr.methods]
        methods = [m for m in methods if not isinstance(m, EmptyNode)]
        for i in expr.overload_sets:
            for f in i.functions:
                self._visit(f)
        interfaces = [self._visit(i) for i in expr.overload_sets]

        del_method = expr.methods_as_dict.get("__del__", None)
        if del_method is None:
            del_name = expr.scope.get_new_name("__del__")
            scope = expr.scope.new_child_scope("__del__", scope_type="function")
            scope.local_used_symbols["__del__"] = del_name
            scope.python_names[del_name] = "__del__"
            argument = FunctionDefArgument(
                Variable(expr.class_type, scope.get_new_name("self"), cls_base=expr),
                bound_argument=True,
            )
            scope.insert_variable(argument.var)
            del_method = FunctionDef(del_name, [argument], [Pass()], scope=scope, is_external=True)
            methods.append(self._visit(del_method))

        if any(isinstance(v.class_type, TupleType) for v in expr.attributes):
            raise NotImplementedError("Tuples cannot yet be exposed to Python.")

        properties_getters = [
            BindCClassProperty(
                expr.scope.get_python_name(m.original_function.name),
                m,
                None,
                expr.class_type,
                m.original_function.docstring,
            )
            for m in methods
            if "property" in m.original_function.decorators
        ]
        methods = [
            m for m in methods if m not in properties_getters if "property" not in m.original_function.decorators
        ]

        # Pseudo-self variable is useful for pre-defined attributes which are not DottedVariables
        pseudo_self = Variable(expr.class_type, "self", cls_base=expr)
        properties = [
            self._visit(
                v if isinstance(v, DottedVariable) else v.clone(v.name, new_class=DottedVariable, lhs=pseudo_self)
            )
            for v in expr.attributes
            if not v.is_private and not isinstance(v.class_type, TupleType)
        ]
        return BindCClassDef(
            expr,
            new_func=new_method,
            methods=methods,
            overload_sets=interfaces,
            attributes=properties_getters + properties,
            docstring=expr.docstring,
            class_type=expr.class_type,
        )

    def _extract_FunctionDefResult(self, orig_var, orig_func_scope):
        """
        Get the code and variables necessary to translate a `Variable` to a C-compatible Variable.

        Get the code and variables necessary to translate a `Variable` which is returned
        from a function to a `Variable` which can be called from C. A variable `local_var` is
        created. This variable can be retrieved using its name which matches the name of `orig_var`
        the variable that was originally returned. `local_var` should be used to retrieve the
        result of the function call. It will generally be a clone of the return variable but some
        properties (such as the memory handling) may be modified. A variable describing the
        object which should be returned from the BindCFunctionDef may also be created if necessary.
        Finally AST nodes are also created to describe any code which is needed to convert the
        `local_var` to the returned variable.

        Parameters
        ----------
        orig_var : Variable
            An object representing the variable or an element of the variable from the
            FunctionDefResult being wrapped.

        Returns
        -------
        dict
            A dictionary describing the objects necessary to collect the result:
            - c_result: The Variable which should be used in a FunctionDefResult from the wrapped
                    function.
            - body: The code which is needed to convert the local_var to the returned variable
                    saved in c_result.
            - f_result: The Variable which should be used in a FunctionCall to collect the results
                    from the Fortran function.
        """
        class_type = orig_var.class_type

        classes = type(class_type).__mro__
        for cls in classes:
            annotation_method = f"_extract_{cls.__name__}_FunctionDefResult"
            if hasattr(self, annotation_method):
                return getattr(self, annotation_method)(orig_var, orig_func_scope)

        # Unknown object, we raise an error.
        raise NotImplementedError(f"Wrapping function results is not implemented for type {class_type}.")

    def _extract_FixedSizeType_FunctionDefResult(self, orig_var, orig_func_scope):
        name = orig_var.name
        self.scope.insert_symbol(name)
        local_var = orig_var.clone(self.scope.get_expected_name(name), new_class=Variable)
        return {
            "body": [],
            "c_result": BindCVariable(local_var, orig_var),
            "f_result": local_var,
        }

    def _extract_CustomDataType_FunctionDefResult(self, orig_var, orig_func_scope):
        name = orig_var.name
        scope = self.scope
        scope.insert_symbol(name)
        memory_handling = "alias" if isinstance(orig_var, DottedVariable) else orig_var.memory_handling
        local_var = orig_var.clone(
            scope.get_expected_name(name),
            new_class=Variable,
            memory_handling=memory_handling,
        )
        # Allocatable is not returned so it must appear in local scope
        scope.insert_variable(local_var, name)

        # Create the C-compatible data pointer
        bind_var = Variable(BindCPointer(), scope.get_new_name("bound_" + name), memory_handling="alias")

        if isinstance(orig_var, DottedVariable) or orig_var.is_alias:
            ptr_var = orig_var
            body = [CLocFunc(ptr_var, bind_var)]
        else:
            # Create an array variable which can be passed to CLocFunc
            ptr_var = Variable(
                orig_var.class_type,
                scope.get_new_name(name + "_ptr"),
                memory_handling="alias",
            )
            scope.insert_variable(ptr_var)
            alloc = Allocate(ptr_var, shape=None, status="unallocated")
            copy = Assign(ptr_var, local_var)
            cloc = CLocFunc(ptr_var, bind_var)
            body = [alloc, copy, cloc]

        return {
            "body": body,
            "c_result": BindCVariable(bind_var, orig_var),
            "f_result": local_var,
        }

    def _extract_NumpyNDArrayType_FunctionDefResult(self, orig_var, orig_func_scope):
        name = orig_var.name
        scope = self.scope
        scope.insert_symbol(name)
        memory_handling = "alias" if isinstance(orig_var, DottedVariable) else orig_var.memory_handling

        shape = orig_var.shape if memory_handling == "stack" else None

        # Allocatable is not returned so it must appear in local scope
        local_var = orig_var.clone(
            scope.get_expected_name(name),
            new_class=Variable,
            memory_handling=memory_handling,
            shape=shape,
        )
        scope.insert_variable(local_var, name)

        if orig_var.is_alias or isinstance(orig_var, DottedVariable):
            result = self._get_bind_c_array(name, orig_var, local_var.shape, local_var)
        else:
            result = self._get_bind_c_array(name, orig_var, local_var.shape)

            result["body"].append(Assign(result["f_array"], local_var))

        result["f_result"] = local_var

        return result

    def _extract_HomogeneousTupleType_FunctionDefResult(self, orig_var, orig_func_scope):
        return self._extract_NumpyNDArrayType_FunctionDefResult(orig_var, orig_func_scope)

    def _extract_StringType_FunctionDefResult(self, orig_var, orig_func_scope):
        name = orig_var.name
        scope = self.scope
        scope.insert_symbol(name)
        memory_handling = "alias" if isinstance(orig_var, DottedVariable) else orig_var.memory_handling

        # Allocatable is not returned so it must appear in local scope
        local_var = orig_var.clone(
            scope.get_expected_name(name),
            new_class=Variable,
            memory_handling=memory_handling,
        )
        scope.insert_variable(local_var, name)

        # Create the C-compatible data pointer
        bind_var = Variable(BindCPointer(), scope.get_new_name("bound_" + name), memory_handling="alias")

        shape_var = Variable(NumpyInt32Type(), scope.get_new_name(f"{name}_len"))
        scope.insert_variable(shape_var)

        # Create an array variable which can be passed to CLocFunc
        ptr_var = Variable(
            NumpyNDArrayType.get_new(CharType(), 1, None),
            scope.get_new_name(name + "_ptr"),
            memory_handling="alias",
        )
        elem_var = Variable(CharType(), scope.get_new_name(name + "_elem"))
        scope.insert_variable(ptr_var)
        scope.insert_variable(elem_var)

        # Define the additional steps necessary to define and fill ptr_var
        body = [
            Assign(shape_var, Add(ArraySize(local_var), convert_to_literal(1))),
            Assign(bind_var, c_malloc(Mul(BindCSizeOf(elem_var), shape_var))),
            C_F_Pointer(bind_var, ptr_var, [shape_var]),
            Assign(ptr_var, FortranTransfer(local_var, ptr_var, shape_var)),
            Assign(IndexedElement(ptr_var, shape_var), C_NULL_CHAR()),
        ]

        return {
            "c_result": BindCVariable(bind_var, orig_var),
            "body": body,
            "f_array": ptr_var,
            "f_result": local_var,
        }

    def _get_bind_c_array(self, name, orig_var, shape, pointer_target=False):
        """
        Get all the objects necessary to return an array from the BindCFunctionDef.

        In the case of an array, C cannot represent the array natively. Rather it is
        stored in a pointer. This function therefore creates a variable to represent
        that pointer. Additionally information about the shape and strides of the array
        are necessary.  The assignment expressions which define the shapes and strides
        are then stored in `body` along with the allocation of the pointer. The
        Fortran-accessible array is returned so that it can be filled differently
        depending on what type is described by the array (e.g. if the array describes
        an array a simple copy is required, but if the array describes a set then the
        elements need to be added one by one.

        Parameters
        ----------
        name : str
            The stem of the names of the objects that should be created.

        orig_var : Variable
            An object representing the variable or an element of the variable from the
            FunctionDefResult being wrapped. This is used to obtain the dtype, rank
            and order of the array that should be created.

        shape : tuple[model object]
            A tuple describing the shape that the array should be allocated to.

        pointer_target : bool, default=False
            Indicates if the data in orig_var is a target of the pointer that will be
            created.

        Returns
        -------
        dict
            A dictionary describing the objects necessary to collect the result:
            - c_result: The Variable which should be used in a FunctionDefResult from the wrapped
                    function.
            - body: The code which is needed to convert the local_var to the returned variable
                    saved in c_result.
            - f_array: The Fortran-accessible array that will be returned. This is where the data
                    should be copied to.
        """
        dtype = orig_var.dtype
        rank = orig_var.rank
        order = orig_var.order
        scope = self.scope
        # Create the C-compatible data pointer
        bind_var = Variable(BindCPointer(), scope.get_new_name("bound_" + name), memory_handling="alias")

        shape_vars = [Variable(NumpyInt32Type(), scope.get_new_name(f"{name}_shape_{i + 1}")) for i in range(rank)]

        if pointer_target:
            f_array = orig_var
        else:
            # Create an array variable which can be passed to CLocFunc
            numpy_dtype = numpy_precision_map[(dtype.primitive_type, dtype.precision)]
            ptr_var = Variable(
                NumpyNDArrayType.get_new(numpy_dtype, rank, order),
                scope.get_new_name(name + "_ptr"),
                memory_handling="alias",
            )
            elem_var = Variable(dtype, scope.get_new_name(name + "_elem"))
            scope.insert_variable(ptr_var)
            scope.insert_variable(elem_var)
            f_array = ptr_var

        if shape is None:
            shape = tuple(ArrayShapeElement(f_array, convert_to_literal(i)) for i in range(rank))
        else:
            shape = tuple(
                ArrayShapeElement(f_array, convert_to_literal(i)) if dim is None else dim for i, dim in enumerate(shape)
            )

        body = [Assign(s_v, cast_to(s, NumpyInt32Type())) for s_v, s in zip(shape_vars, shape, strict=False)]

        if pointer_target:
            body.append(CLocFunc(orig_var, bind_var))
        else:
            size = reduce(Mul, [BindCSizeOf(elem_var), *shape_vars])
            body = [
                *body,
                Assign(bind_var, c_malloc(size)),
                C_F_Pointer(bind_var, ptr_var, shape_vars if order == "F" else shape_vars[::-1]),
            ]

        result_var = Variable(
            BindCArrayType.get_new(rank, has_strides=False),
            scope.get_new_name(),
            shape=(rank + 1,),
        )
        scope.insert_symbolic_alias(IndexedElement(result_var, convert_to_literal(0)), bind_var)
        for i, s in enumerate(shape_vars):
            scope.insert_symbolic_alias(IndexedElement(result_var, convert_to_literal(i + 1)), s)

        return {
            "c_result": BindCVariable(result_var, orig_var),
            "body": body,
            "f_array": f_array,
            "bind_var": bind_var,
            "shape_vars": shape_vars,
        }
