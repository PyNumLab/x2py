"""
Module describing the code-wrapping class : FortranToCWrapper
which creates an interface exposing Fortran code to C.
THIS CREATES BIND(C) FORTRAN FILE
"""

import re
from dataclasses import replace
from functools import reduce
from typing import ClassVar

from x2py.ownership_policy import (
    AssignmentMode,
    CodegenAction,
    DestructionPolicy,
    NativeBarrierAction,
    NativeBarrierDispatcher,
    ObjectKind,
    OwnershipDecision,
    OwnershipOwner,
    PolicyActionDispatcher,
    PythonBarrierAction,
    SetterAction,
    SetterActionDispatcher,
    StorageMode,
    TransferMode,
    ownership_decision_for_codegen_variable,
)
from x2py.semantics.models import (
    INTERNAL_MODULE_VARIABLE_ACCESS_METADATA,
    INTERNAL_MODULE_VARIABLE_NAME_METADATA,
    INTERNAL_NATIVE_ARRAY_HANDLE_OPERATION_METADATA,
    INTERNAL_NATIVE_ARRAY_HANDLE_OWNER_CLASS_METADATA,
    RESOLVED_CLASS_INSTANCE_POLICY_METADATA,
    RESOLVED_CLASS_SELF_POLICY_METADATA,
    RUNTIME_HOLD_GIL_METADATA,
    RUNTIME_RETAIN_RESULT_OWNER_METADATA,
)
from x2py.semantics.native_array_handles import (
    ArrayInteropPolicy,
    ArrayInteropPolicyDispatcher,
    NativeArrayHandlePolicyDispatcher,
)

from ..bind_c import (
    C_NULL_CHAR,
    BindCArrayType,
    BindCArrayVariable,
    BindCClassDef,
    BindCClassProperty,
    BindCFunctionDef,
    BindCModule,
    BindCModuleConstant,
    BindCNativeArrayDescriptorType,
    BindCNativeArrayHandleProperty,
    BindCNativeArrayHandleVariable,
    BindCPointer,
    BindCResultTupleType,
    BindCScalarDescriptorType,
    BindCScalarModuleVariable,
    BindCSizeOf,
    BindCVariable,
    C_F_Pointer,
    CLocFunc,
    DeallocatePointer,
    FortranTransfer,
    c_malloc,
    native_array_descriptor_argument_type,
)
from ..models.core import (
    AliasAssign,
    Allocate,
    ArrayAllocated,
    ArrayAssociated,
    ArrayContiguous,
    ArrayLowerBound,
    ArrayShapeElement,
    ArraySize,
    AsName,
    Assign,
    CaseSection,
    Deallocate,
    EmptyNode,
    FortranCharacterLength,
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
    Nullify,
    Pass,
    Return,
    SelectCase,
)
from ..models.datatypes import (
    CharType,
    CustomDataType,
    FinalType,
    FixedSizeNumericType,
    NumpyBoolType,
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

from ..generator import BridgeGenerator

_MAX_SUPPORTED_ASSUMED_RANK = 15


class FortranToCBridgeGenerator(BridgeGenerator):
    """Create a C-compatible bridge AST for a Fortran module.

    The class follows the same reading order as ``FortranParser``:

    - public generation entrypoint inherited from ``BridgeGenerator``;
    - module, function, variable, and class visitors;
    - argument conversion helpers;
    - result conversion helpers;
    - shared predicates and low-level builders.

    Contract-value conversion dispatches only from the completed post-IR object
    kind and codegen action. Model-node dispatch remains exclusively owned by
    ``_visit``.

    Parameters
    ----------
    sharedlib_dirpath : str
        The folder where the generated .so file will be located.
    verbose : int
        The level of verbosity.
    """

    target_language = "C"
    start_language = "Fortran"
    _NATIVE_BARRIER_DISPATCHER = NativeBarrierDispatcher(
        {
            NativeBarrierAction.PASS_VALUE: "_convert_native_value_argument",
            NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS: "_convert_native_call_local_address_argument",
            NativeBarrierAction.PASS_STORAGE_ADDRESS: "_convert_native_storage_address_argument",
            NativeBarrierAction.PASS_RAW_ADDRESS: "_convert_native_raw_address_argument",
            NativeBarrierAction.PASS_ARRAY_DESCRIPTOR: "_convert_native_array_descriptor_argument",
            NativeBarrierAction.PASS_WRAPPER_ADDRESS: "_convert_native_wrapper_address_argument",
        }
    )
    _RESULT_POLICY_DISPATCHER = PolicyActionDispatcher(
        {
            (ObjectKind.SCALAR, CodegenAction.DIRECT_VALUE): "_convert_scalar_result",
            (ObjectKind.SCALAR, CodegenAction.HIDDEN_OUTPUT): "_convert_scalar_result",
            (ObjectKind.SCALAR, CodegenAction.COPY_IN_OUT): "_convert_scalar_result",
            (ObjectKind.SCALAR, CodegenAction.IN_PLACE_ARGUMENT): "_convert_scalar_result",
            (ObjectKind.SCALAR, CodegenAction.IDENTITY_OUTPUT): "_convert_scalar_result",
            (ObjectKind.SCALAR, CodegenAction.SNAPSHOT_COPY): "_convert_snapshot_scalar_result",
            (ObjectKind.SCALAR, CodegenAction.BORROWED_VIEW): "_convert_scalar_result",
            (ObjectKind.STRING, CodegenAction.COPY_OUT): "_convert_string_result",
            (ObjectKind.STRING, CodegenAction.HIDDEN_OUTPUT): "_convert_string_result",
            (ObjectKind.STRING, CodegenAction.COPY_IN_OUT): "_convert_string_result",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.COPY_OUT): "_convert_array_result",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.HIDDEN_OUTPUT): "_convert_array_result",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.COPY_IN_OUT): "_convert_array_result",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.SNAPSHOT_COPY): "_convert_array_result",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.BORROWED_VIEW): "_convert_array_result",
            (ObjectKind.DERIVED_TYPE, CodegenAction.WRAPPER_INSTANCE): "_convert_owned_custom_type_result",
            (ObjectKind.DERIVED_TYPE, CodegenAction.HIDDEN_OUTPUT): "_convert_owned_custom_type_result",
            (ObjectKind.DERIVED_TYPE, CodegenAction.SNAPSHOT_COPY): "_convert_owned_custom_type_result",
            (ObjectKind.DERIVED_TYPE, CodegenAction.BORROWED_VIEW): "_convert_borrowed_custom_type_result",
        }
    )
    _FUNCTION_ARGUMENT_POLICY_DISPATCHER = PolicyActionDispatcher(
        {
            (ObjectKind.SCALAR, CodegenAction.DIRECT_VALUE): "_convert_visible_function_argument",
            (ObjectKind.SCALAR, CodegenAction.CALL_LOCAL_INPUT): "_convert_visible_function_argument",
            (ObjectKind.SCALAR, CodegenAction.IN_PLACE_ARGUMENT): "_convert_visible_function_argument",
            (ObjectKind.SCALAR, CodegenAction.IDENTITY_OUTPUT): "_convert_visible_function_argument",
            (ObjectKind.SCALAR, CodegenAction.COPY_IN_OUT): "_convert_replacement_function_argument",
            (ObjectKind.SCALAR, CodegenAction.HIDDEN_OUTPUT): "_convert_hidden_function_argument",
            (ObjectKind.STRING, CodegenAction.CALL_LOCAL_INPUT): "_convert_visible_function_argument",
            (ObjectKind.STRING, CodegenAction.IN_PLACE_ARGUMENT): "_convert_visible_function_argument",
            (ObjectKind.STRING, CodegenAction.IDENTITY_OUTPUT): "_convert_visible_function_argument",
            (ObjectKind.STRING, CodegenAction.COPY_IN_OUT): "_convert_replacement_function_argument",
            (ObjectKind.STRING, CodegenAction.HIDDEN_OUTPUT): "_convert_hidden_function_argument",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.CALL_LOCAL_INPUT): "_convert_visible_function_argument",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.IN_PLACE_ARGUMENT): "_convert_visible_function_argument",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.IDENTITY_OUTPUT): "_convert_visible_function_argument",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.COPY_IN_OUT): "_convert_replacement_function_argument",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.HIDDEN_OUTPUT): "_convert_hidden_function_argument",
            (ObjectKind.DERIVED_TYPE, CodegenAction.CALL_LOCAL_INPUT): "_convert_visible_function_argument",
            (ObjectKind.DERIVED_TYPE, CodegenAction.IN_PLACE_ARGUMENT): "_convert_visible_function_argument",
            (ObjectKind.DERIVED_TYPE, CodegenAction.IDENTITY_OUTPUT): "_convert_visible_function_argument",
            (ObjectKind.DERIVED_TYPE, CodegenAction.HIDDEN_OUTPUT): "_convert_hidden_function_argument",
        }
    )
    _REPLACEMENT_RESULT_DISPATCHER = PolicyActionDispatcher(
        {
            (ObjectKind.SCALAR, CodegenAction.COPY_IN_OUT): "_build_scalar_replacement_result",
            (ObjectKind.STRING, CodegenAction.COPY_IN_OUT): "_build_string_replacement_result",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.COPY_IN_OUT): "_build_array_replacement_result",
        }
    )
    _NDARRAY_RESULT_DISPATCHER = PolicyActionDispatcher(
        {
            (ObjectKind.NUMPY_ARRAY, CodegenAction.SNAPSHOT_COPY): "_build_snapshot_copy_array_result",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.BORROWED_VIEW): "_build_borrowed_array_result",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.COPY_OUT): "_build_copy_return_array_result",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.COPY_IN_OUT): "_build_copy_return_array_result",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.HIDDEN_OUTPUT): "_build_copy_return_array_result",
        }
    )
    _ALLOCATABLE_RESULT_HELPER_DISPATCHER = PolicyActionDispatcher(
        {
            (ObjectKind.NUMPY_ARRAY, CodegenAction.COPY_OUT): "_uses_heap_allocatable_result_helper",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.HIDDEN_OUTPUT): "_skips_allocatable_result_helper",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.COPY_IN_OUT): "_skips_allocatable_result_helper",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.SNAPSHOT_COPY): "_skips_allocatable_result_helper",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.BORROWED_VIEW): "_skips_allocatable_result_helper",
        }
    )
    _FIELD_ASSIGNMENT_BY_POLICY: ClassVar[dict[AssignmentMode, type]] = {
        AssignmentMode.VALUE_COPY: Assign,
        AssignmentMode.ALIAS: AliasAssign,
    }
    _FIELD_SETTER_POLICY_DISPATCHER = SetterActionDispatcher(
        {
            SetterAction.WRITE_THROUGH: "_build_field_setter",
            SetterAction.REJECT_REPLACEMENT: "_skip_field_setter",
            SetterAction.OMIT: "_skip_field_setter",
        }
    )
    _FIELD_GETTER_POLICY_DISPATCHER = PolicyActionDispatcher(
        {
            (ObjectKind.SCALAR, CodegenAction.DIRECT_VALUE): "_append_value_field_getter",
            (ObjectKind.SCALAR, CodegenAction.SNAPSHOT_COPY): "_append_nullable_scalar_field_getter",
            (ObjectKind.STRING, CodegenAction.COPY_OUT): "_append_value_field_getter",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.BORROWED_VIEW): "_append_borrowed_array_field_getter",
            (ObjectKind.DERIVED_TYPE, CodegenAction.BORROWED_VIEW): "_append_alias_field_getter",
        }
    )
    _MODULE_VARIABLE_POLICY_DISPATCHER = PolicyActionDispatcher(
        {
            (ObjectKind.SCALAR, CodegenAction.DIRECT_VALUE): "_literal_module_constant",
            (ObjectKind.SCALAR, CodegenAction.BORROWED_VIEW): "_scalar_module_variable",
            (ObjectKind.SCALAR, CodegenAction.SNAPSHOT_COPY): "_scalar_module_variable",
            (ObjectKind.STRING, CodegenAction.DIRECT_VALUE): "_literal_module_constant",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.BORROWED_VIEW): "_array_module_variable",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.SNAPSHOT_COPY): "_array_module_variable",
            (ObjectKind.DERIVED_TYPE, CodegenAction.WRAPPER_INSTANCE): "_copied_derived_module_constant",
            (ObjectKind.DERIVED_TYPE, CodegenAction.SNAPSHOT_COPY): "_snapshot_derived_module_variable",
            (ObjectKind.DERIVED_TYPE, CodegenAction.BORROWED_VIEW): "_derived_module_variable",
        }
    )
    _MODULE_ARRAY_GETTER_POLICY_DISPATCHER = PolicyActionDispatcher(
        {
            (ObjectKind.NUMPY_ARRAY, CodegenAction.BORROWED_VIEW): "_borrowed_module_array_getter_result",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.SNAPSHOT_COPY): "_snapshot_module_array_getter_result",
        }
    )
    _NATIVE_ARRAY_HANDLE_DISPATCHER = NativeArrayHandlePolicyDispatcher(
        {
            ("allocatable", "argument_descriptor"): "_bridge_allocatable_descriptor_argument",
            ("allocatable", "borrowed_field_descriptor"): "_bridge_borrowed_native_array_field_handle",
            ("allocatable", "borrowed_module_descriptor"): "_bridge_borrowed_native_array_module_handle",
            ("allocatable", "optional_absent_handle"): "_bridge_optional_native_array_handle",
            ("allocatable", "owned_result_descriptor"): "_bridge_owned_allocatable_result_handle",
            ("pointer", "argument_descriptor"): "_bridge_pointer_descriptor_argument",
            ("pointer", "borrowed_field_descriptor"): "_bridge_borrowed_native_array_field_handle",
            ("pointer", "borrowed_module_descriptor"): "_bridge_borrowed_native_array_module_handle",
            ("pointer", "optional_absent_handle"): "_bridge_optional_native_array_handle",
        }
    )
    _ARRAY_INTEROP_POLICY_DISPATCHER = ArrayInteropPolicyDispatcher(
        {
            ("argument", "data_buffer"): "_bridge_data_buffer_argument",
            ("argument", "descriptor"): "_bridge_descriptor_argument",
            ("module_variable", "data_buffer"): "_bridge_data_buffer_module_variable",
            ("module_variable", "descriptor"): "_bridge_descriptor_module_variable",
            ("result", "data_buffer"): "_bridge_data_buffer_result",
            ("result", "descriptor"): "_bridge_descriptor_result",
        }
    )
    _COPY_RETURN_ARRAY_BY_STORAGE: ClassVar[dict[StorageMode, str]] = {
        StorageMode.STACK: "_build_stack_copy_return_array_result",
        StorageMode.HEAP: "_build_heap_copy_return_array_result",
    }
    _CALLBACK_ARGUMENT_POLICY_DISPATCHER = PolicyActionDispatcher(
        {
            (ObjectKind.SCALAR, CodegenAction.DIRECT_VALUE): "_convert_callback_scalar_argument",
            (ObjectKind.SCALAR, CodegenAction.CALL_LOCAL_INPUT): "_convert_callback_scalar_argument",
            (ObjectKind.SCALAR, CodegenAction.IN_PLACE_ARGUMENT): "_convert_callback_scalar_storage_writable_argument",
            (ObjectKind.SCALAR, CodegenAction.IDENTITY_OUTPUT): "_convert_callback_scalar_storage_output_argument",
            (ObjectKind.STRING, CodegenAction.CALL_LOCAL_INPUT): "_convert_callback_string_input_argument",
            (ObjectKind.STRING, CodegenAction.IN_PLACE_ARGUMENT): "_convert_callback_string_storage_writable_argument",
            (ObjectKind.STRING, CodegenAction.IDENTITY_OUTPUT): "_convert_callback_string_storage_output_argument",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.CALL_LOCAL_INPUT): "_convert_callback_array_input_argument",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.IN_PLACE_ARGUMENT): "_convert_callback_array_writable_argument",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.IDENTITY_OUTPUT): "_convert_callback_array_output_argument",
            (ObjectKind.DERIVED_TYPE, CodegenAction.CALL_LOCAL_INPUT): "_convert_callback_derived_input_argument",
            (ObjectKind.DERIVED_TYPE, CodegenAction.IN_PLACE_ARGUMENT): "_convert_callback_derived_writable_argument",
            (ObjectKind.DERIVED_TYPE, CodegenAction.IDENTITY_OUTPUT): "_convert_callback_derived_output_argument",
        }
    )
    _CALLBACK_RESULT_POLICY_DISPATCHER = PolicyActionDispatcher(
        {
            (ObjectKind.SCALAR, CodegenAction.DIRECT_VALUE): "_convert_callback_scalar_result",
            (ObjectKind.NUMPY_ARRAY, CodegenAction.COPY_OUT): "_convert_callback_array_result",
            (ObjectKind.DERIVED_TYPE, CodegenAction.WRAPPER_INSTANCE): "_convert_callback_derived_result",
        }
    )

    # ------------------------------------------------------------------
    # Public entrypoints and state
    # ------------------------------------------------------------------

    def __init__(self, sharedlib_dirpath, verbose):
        """Initialize state collected while building one bridge module."""
        self._additional_exprs = []
        self._additional_functions = []
        self._generator_names_dict = {}
        super().__init__(verbose)

    # ------------------------------------------------------------------
    # Model visitors
    # ------------------------------------------------------------------

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
            naming_policy=scope.naming_policy,
            public_namespace=scope.public_namespace,
            symbol_language=self.start_language,
            scope_type="module",
        )
        name = mod_scope.get_new_name(f"bind_c_{expr.name}")
        self.scope = mod_scope

        # Wrap contents
        funcs_to_generate = [f for f in expr.funcs if f.is_semantic and not f.is_private]

        wrapped_funcs = [self._visit(f) for f in funcs_to_generate]
        init_func = self._wrapped_special_function(expr.init_func, funcs_to_generate, wrapped_funcs)
        free_func = self._wrapped_special_function(expr.free_func, funcs_to_generate, wrapped_funcs)
        removed_functions = [
            f for f, wrapped in zip(funcs_to_generate, wrapped_funcs, strict=False) if isinstance(wrapped, EmptyNode)
        ]
        python_exports = self._wrapped_python_exports(expr, funcs_to_generate, wrapped_funcs)
        funcs = [f for f in wrapped_funcs if not isinstance(f, EmptyNode)]
        interfaces = self._wrapped_interfaces(expr, python_exports)
        classes = [self._visit(f) for f in expr.classes]
        self._extend_python_exports(python_exports, expr, expr.classes, classes)
        variables, variable_accessor_funcs, variable_sources = self._wrapped_module_variables(expr.variables)
        self._extend_variable_python_exports(
            python_exports,
            expr,
            variables,
            variable_accessor_funcs,
            variable_sources,
        )
        funcs.extend(variable_accessor_funcs)
        variable_getters = [v for v in variables if isinstance(v, BindCArrayVariable | BindCNativeArrayHandleVariable)]
        # Import the module and its dependencies (in case they are used for argument types)
        imports = self._module_imports(expr, funcs_to_generate)

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
            python_exports=python_exports,
        )

    @staticmethod
    def _wrapped_python_exports(expr, source_functions, wrapped_functions):
        """Map wrapped functions to their explicit Python export paths."""
        if not expr.has_explicit_python_exports:
            return None
        return {
            id(wrapped): expr.get_python_exports(source)
            for source, wrapped in zip(source_functions, wrapped_functions, strict=True)
            if not isinstance(wrapped, EmptyNode)
        }

    def _wrapped_interfaces(self, expr, python_exports):
        """Wrap overload sets and attach explicit Python export metadata."""
        interfaces = []
        for item in expr.overload_sets:
            wrapped = self._visit(item)
            if isinstance(wrapped, EmptyNode):
                continue
            interfaces.append(wrapped)
            if python_exports is not None:
                python_exports[id(wrapped)] = expr.get_python_exports(item)
        return interfaces

    @staticmethod
    def _extend_python_exports(python_exports, expr, sources, wrapped_objects):
        """Add source-to-wrapper export mappings when explicit exports exist."""
        if python_exports is None:
            return
        python_exports.update(
            {
                id(wrapped): expr.get_python_exports(source)
                for source, wrapped in zip(sources, wrapped_objects, strict=True)
            }
        )

    def _extend_variable_python_exports(
        self,
        python_exports,
        expr,
        variables,
        accessor_functions,
        variable_sources,
    ):
        """Attach module-variable and accessor export paths to wrapped objects."""
        if python_exports is None:
            return
        accessor_ids = {id(function) for function in accessor_functions}
        for wrapped in (*variables, *accessor_functions):
            exports = expr.get_python_exports(variable_sources[id(wrapped)])
            if id(wrapped) in accessor_ids:
                source_name = wrapped.original_function.name
                exports = tuple((namespace, str(self.scope.get_python_name(source_name))) for namespace, _ in exports)
            python_exports[id(wrapped)] = exports

    @staticmethod
    def _wrapped_special_function(original, source_functions, wrapped_functions):
        """Return the wrapper corresponding to an optional special function."""
        if original is None:
            return None
        index = next(index for index, function in enumerate(source_functions) if function == original)
        return wrapped_functions[index]

    def _wrapped_module_variables(self, module_variables):
        """Split wrapped module variables into storage and accessor functions."""
        variables = []
        accessors = []
        sources = {}
        for item in module_variables:
            if item.is_private:
                continue
            variable = self._visit(item)
            if isinstance(variable, BindCScalarModuleVariable):
                wrapped_accessors = tuple(
                    function
                    for function in (variable.getter_function, variable.setter_function)
                    if function is not None
                )
                accessors.extend(wrapped_accessors)
                sources.update({id(function): item for function in wrapped_accessors})
            else:
                variables.append(variable)
                sources[id(variable)] = item
        return variables, accessors, sources

    @staticmethod
    def _module_imports(module, wrapped_functions):
        """Select imports required by a generated bridge module."""
        if module.imports:
            return list(module.imports)
        if any(function.is_external for function in wrapped_functions):
            return []
        return [Import(module.name, target=module, mod=module)]

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

        if self._can_call_existing_bind_c_directly(expr):
            return self._direct_bind_c_function(expr)

        orig_name = expr.cls_name or expr.name
        name = self.scope.get_new_name(f"bind_c_{orig_name.lower()}")
        self._generator_names_dict[expr.name] = name
        self._additional_exprs = []
        self._additional_functions = []

        # Create the scope
        func_scope = self.scope.new_child_scope(name, "function")
        self.scope = func_scope

        # Wrap the arguments and collect the expressions passed as the call argument.
        generated_args, projected_argument_results = self._convert_function_arguments(expr)

        func_arguments = [a["c_arg"] for a in generated_args if a["c_arg"] is not None]
        call_arguments = [a["f_arg"] for a in generated_args]

        result_infos, func_call_results = self._convert_function_result(expr)
        result_infos.extend(projected_argument_results)
        func_results = self._function_result_value(result_infos)

        overload_set = get_direct_overload_set(expr)

        call_target = overload_set or expr
        body = self._get_function_def_body(call_target, generated_args, func_call_results)

        body.extend(self._additional_exprs)
        self._additional_exprs.clear()
        additional_functions = self._additional_functions
        self._additional_functions = []

        self._append_destructor_cleanup(expr, call_arguments, body)

        self.exit_scope()

        imports = self._function_imports(expr)

        func = BindCFunctionDef(
            name,
            func_arguments,
            body,
            FunctionDefResult(func_results),
            imports=imports,
            functions=additional_functions,
            scope=func_scope,
            original_function=expr,
            docstring=expr.docstring,
            result_pointer_map=expr.result_pointer_map,
        )

        self.scope.insert_function(func, name)

        return func

    def _convert_function_arguments(self, function):
        """Convert every function argument and collect projected results."""
        generated_args = []
        projected_results = []
        for argument in function.arguments:
            generated_arg, projected_result = self._convert_function_argument(argument, function)
            generated_args.append(generated_arg)
            if projected_result is not None:
                projected_results.append(projected_result)
        return generated_args, projected_results

    def _convert_function_argument(self, argument, function):
        """Convert one function argument and its optional projected result."""
        if isinstance(argument.var, FunctionAddress):
            return self._convert_argument(argument, function), None
        return self._FUNCTION_ARGUMENT_POLICY_DISPATCHER.dispatch(
            self,
            argument.var,
            argument,
            function,
        )

    def _convert_visible_function_argument(self, _var, _decision, argument, function):
        """Convert an ordinary Python-visible native argument."""
        generated = self._convert_argument(argument, function)
        return generated, None

    def _convert_replacement_function_argument(self, _var, _decision, argument, function):
        """Convert one visible argument and collect its replacement result."""
        generated = self._convert_argument(argument, function)
        result = self._REPLACEMENT_RESULT_DISPATCHER.dispatch(self, argument.var, generated)
        self._additional_exprs.extend(result["body"])
        return generated, result

    def _convert_hidden_function_argument(self, _var, _decision, argument, function):
        """Create native output storage for a Python-hidden argument."""
        if argument.bound_argument:
            raise ValueError(f"Bound argument {argument.var.name!r} cannot be a hidden output")
        result = self._convert_result(argument.var, function.scope)
        self._additional_exprs.extend(result["body"])
        generated = {
            "c_arg": None,
            "f_arg": FunctionCallArgument(result["f_result"], keyword=argument.var.name),
            "body": [],
        }
        return generated, result

    def _convert_function_result(self, function):
        """Convert the explicit function result into bridge result metadata."""
        if function.results.var is NIL:
            return [], []
        result = self._convert_result(function.results.var, function.scope)
        self._additional_exprs.extend(result["body"])
        call_results = self.scope.collect_all_tuple_elements(result["f_result"])
        return [result], call_results

    def _function_result_value(self, result_infos):
        """Build the C-visible result value for converted result metadata."""
        if not result_infos:
            return NIL
        if len(result_infos) == 1:
            return result_infos[0]["c_result"]
        return self._pack_function_results(result_infos)

    @staticmethod
    def _append_destructor_cleanup(function, call_arguments, body) -> None:
        """Append pointer cleanup required by a wrapped destructor."""
        if function.scope.get_python_name(function.name) != "__del__" or not call_arguments:
            return
        if function.is_external:
            body.pop()
        body.append(DeallocatePointer(call_arguments[0].value))

    def _function_imports(self, function):
        """Return direct imports required to call an external function."""
        return []

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
        functions = [wrapped for item in expr.functions if not isinstance(wrapped := self._visit(item), EmptyNode)]
        if not functions:
            return EmptyNode()
        return FunctionOverloadSet(
            expr.name,
            functions,
            expr.is_argument,
            native_name=expr.native_name,
            native_names=expr.native_names,
        )

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
        if expr.array_interop_policy is not None:
            return self._ARRAY_INTEROP_POLICY_DISPATCHER.dispatch(
                self,
                expr,
                expr.array_interop_policy,
                "module_variable",
            )
        return self._MODULE_VARIABLE_POLICY_DISPATCHER.dispatch(self, expr)

    def _bridge_data_buffer_module_variable(self, subject, _policy):
        """Expose an ordinary array module variable through the data-buffer ABI."""
        return self._MODULE_VARIABLE_POLICY_DISPATCHER.dispatch(self, subject)

    def _bridge_descriptor_module_variable(self, subject, policy):
        """Expose a native array handle module variable through descriptor ABI."""
        self._validate_descriptor_array_interop_policy(subject, policy)
        return self._NATIVE_ARRAY_HANDLE_DISPATCHER.dispatch(
            self,
            subject,
            subject.native_array_handle_policy,
        )

    def _array_module_variable(self, expr, decision):
        """Build a borrowed module-array accessor from completed policy."""
        getter_policy = expr.getter_ownership_decision
        if getter_policy is None:
            raise ValueError(f"Module variable {expr.name!r} is missing completed getter policy")
        scope = self.scope
        func_name = scope.get_new_name("bind_c_" + expr.name.lower())
        func_scope = scope.new_child_scope(func_name, "function")
        mod = get_enclosing_module(expr)
        assert mod is not None
        func_scope.imports["variables"][expr.name] = expr
        self.scope = func_scope
        getter_value = expr.clone(
            expr.name,
            ownership_decision=getter_policy,
            memory_handling=getter_policy.storage_mode.value,
        )
        result = self._MODULE_ARRAY_GETTER_POLICY_DISPATCHER.dispatch_decision(
            self,
            getter_value,
            getter_policy,
            expr,
        )
        if decision.nullable:
            unallocated_body = [
                Assign(result["bind_var"], NIL),
                *[
                    Assign(shape_var, convert_to_literal(0, dtype=NumpyInt32Type()))
                    for shape_var in result["shape_vars"]
                ],
            ]
            result["body"] = [
                If(
                    IfSection(ArrayAllocated(expr), result["body"]),
                    IfSection(convert_to_literal(True), unallocated_body),
                )
            ]
        self.exit_scope()
        func = BindCFunctionDef(
            name=func_name,
            body=result["body"],
            arguments=[],
            results=FunctionDefResult(result["c_result"]),
            imports=self._module_variable_imports(expr),
            scope=func_scope,
            original_function=expr,
        )
        return expr.clone(
            expr.name,
            new_class=BindCArrayVariable,
            wrapper_function=func,
            original_variable=expr,
        )

    def _native_array_module_handle(self, subject, policy):
        """Build the Bind-C model for a borrowed native-array module handle."""
        return subject.clone(
            subject.name,
            new_class=BindCNativeArrayHandleVariable,
            operation_functions=self._native_array_module_handle_operations(subject, policy),
            native_array_handle_policy=policy,
            original_variable=subject,
        )

    def _native_array_field_handle(self, subject, policy):
        """Build generated parent-bound operations for a native-array field handle."""
        owner_class = subject.lhs.cls_base
        if owner_class is None:
            raise ValueError(f"Native array field {subject.name!r} has no containing wrapper class")
        return BindCNativeArrayHandleProperty(
            owner_class.scope.get_python_name(subject.name),
            class_type=subject.lhs.dtype,
            operation_functions=self._native_array_field_handle_operations(subject, policy),
            original_variable=subject,
            owner_class=owner_class,
            native_array_handle_policy=policy,
        )

    def _native_array_field_handle_operations(self, subject, policy):
        """Generate private parent-bound operations for one descriptor field."""
        operations = [
            ("shape", self._native_array_field_shape_operation(subject, policy)),
            ("array_actual", self._native_array_field_pointer_operation(subject, policy, "array_actual")),
            (
                "descriptor",
                self._native_array_field_descriptor_view_operation(subject, policy, "descriptor")
                if policy.descriptor_kind == "pointer"
                else self._native_array_field_pointer_operation(subject, policy, "descriptor"),
            ),
            (
                self._native_array_state_operation_name(policy),
                self._native_array_field_state_operation(subject, policy),
            ),
            (
                "native_byte_order",
                self._native_array_field_constant_bool_operation(subject, policy, "native_byte_order"),
            ),
            ("aligned", self._native_array_field_constant_bool_operation(subject, policy, "aligned")),
            ("writeable", self._native_array_field_constant_bool_operation(subject, policy, "writeable")),
        ]
        if policy.to_numpy != "unsupported":
            operation = (
                self._native_array_field_descriptor_view_operation(subject, policy, "to_numpy")
                if policy.requires_pointer_c_descriptor_interop
                else self._native_array_field_to_numpy_operation(subject, policy)
            )
            operations.append(("to_numpy", operation))
        if policy.descriptor_kind == "allocatable":
            if policy.allows("deallocate"):
                operations.append(("deallocate", self._native_array_field_deallocate_operation(subject, policy)))
            if policy.allows("resize"):
                operations.append(("resize", self._native_array_field_allocatable_resize_operation(subject, policy)))
        elif policy.allows("nullify"):
            operations.append(("contiguous", self._native_array_field_contiguous_operation(subject, policy)))
            operations.append(("nullify", self._native_array_field_nullify_operation(subject, policy)))
            if policy.allows("allocate"):
                operations.append(("allocate", self._native_array_field_pointer_allocate_operation(subject, policy)))
            if policy.allows("deallocate"):
                operations.append(
                    ("deallocate", self._native_array_field_pointer_deallocate_operation(subject, policy))
                )
            if policy.allows("resize"):
                operations.append(("resize", self._native_array_field_pointer_resize_operation(subject, policy)))
        return tuple(operations)

    def _native_array_field_operation_context(self, subject, operation):
        """Enter one parent-bound field operation and expose ``parent%field``."""
        outer_scope = self.scope
        owner_class = subject.lhs.cls_base
        class_scope = owner_class.scope
        original_name = class_scope.get_new_name(f"__x2py_{subject.name}_{operation}", object_type="wrapper")
        func_name = outer_scope.get_new_name(
            f"bind_c_{owner_class.name}_{subject.name}_{operation}",
            object_type="wrapper",
        )
        func_scope = outer_scope.new_child_scope(func_name, "function")
        self.scope = func_scope
        parent_argument = FunctionDefArgument(subject.lhs.clone(subject.lhs.name), bound_argument=True)
        converted_parent = self._convert_argument(parent_argument, subject)
        parent = converted_parent["f_arg"].value
        field = subject.clone(subject.name, lhs=parent)
        return {
            "outer_scope": outer_scope,
            "class_scope": class_scope,
            "owner_class": owner_class,
            "original_name": original_name,
            "func_name": func_name,
            "func_scope": func_scope,
            "arguments": [converted_parent["c_arg"]],
            "body": list(converted_parent["body"]),
            "field": field,
        }

    def _finish_native_array_field_operation(
        self,
        subject,
        operation,
        context,
        result,
        *,
        original_arguments=(),
    ):
        """Leave a parent-bound operation scope and create its Bind-C function."""
        self.exit_scope()
        original_result = result.original_var if isinstance(result, BindCVariable) else result
        if original_result is not NIL:
            original_result = original_result.clone(
                f"{subject.name}_{operation}_value",
                new_class=Variable,
                is_argument=False,
                is_optional=False,
            )
        self._copy_native_array_module_original_result_aliases(
            context["func_scope"],
            context["class_scope"],
            result,
            original_result,
        )
        original_parent = subject.lhs.clone(subject.lhs.name)
        original_function = FunctionDef(
            context["original_name"],
            [FunctionDefArgument(original_parent, bound_argument=True), *original_arguments],
            [],
            FunctionDefResult(original_result),
            scope=context["class_scope"],
            decorators={
                RUNTIME_HOLD_GIL_METADATA: True,
                INTERNAL_NATIVE_ARRAY_HANDLE_OPERATION_METADATA: True,
                INTERNAL_NATIVE_ARRAY_HANDLE_OWNER_CLASS_METADATA: context["owner_class"],
                RUNTIME_RETAIN_RESULT_OWNER_METADATA: operation == "to_numpy",
            },
            is_private=True,
        )
        return BindCFunctionDef(
            context["func_name"],
            context["arguments"],
            context["body"],
            FunctionDefResult(result),
            scope=context["func_scope"],
            original_function=original_function,
        )

    def _native_array_field_shape_operation(self, subject, policy):
        """Return current extents for a descriptor field."""
        context = self._native_array_field_operation_context(subject, "shape")
        result, shape_vars = self._native_array_shape_operation_result(subject)
        context["body"].extend(
            Assign(shape_var, ArrayShapeElement(context["field"], convert_to_literal(index)))
            for index, shape_var in enumerate(shape_vars)
        )
        return self._finish_native_array_field_operation(subject, "shape", context, result)

    def _native_array_field_pointer_operation(self, subject, policy, operation):
        """Return the current data address for an allocated or associated field."""
        context = self._native_array_field_operation_context(subject, operation)
        result = self._native_array_module_scalar_result(
            BindCPointer(),
            self.scope.get_new_name(f"{subject.name}_{operation}"),
        )
        context["body"].extend(
            [
                Assign(result, NIL),
                If(
                    IfSection(
                        self._native_array_present_expr(context["field"], policy),
                        [CLocFunc(context["field"], result)],
                    )
                ),
            ]
        )
        return self._finish_native_array_field_operation(subject, operation, context, result)

    def _native_array_field_null_pointer_operation(self, subject, policy, operation):
        """Return an explicit null pointer for an unavailable descriptor operation."""
        context = self._native_array_field_operation_context(subject, operation)
        result = self._native_array_module_scalar_result(
            BindCPointer(),
            self.scope.get_new_name(f"{subject.name}_{operation}"),
        )
        context["body"].append(Assign(result, NIL))
        return self._finish_native_array_field_operation(subject, operation, context, result)

    def _native_array_field_descriptor_view_operation(self, subject, policy, operation):
        """Associate a standard output descriptor with ``parent%field``."""
        context = self._native_array_field_operation_context(subject, operation)
        argument, descriptor = self._native_array_descriptor_output_argument(subject, policy)
        context["arguments"].append(argument)
        context["body"].append(AliasAssign(descriptor, context["field"]))
        return self._finish_native_array_field_operation(subject, operation, context, NIL)

    def _native_array_field_state_operation(self, subject, policy):
        """Return allocated or associated state for a descriptor field."""
        operation = self._native_array_state_operation_name(policy)
        context = self._native_array_field_operation_context(subject, operation)
        result = self._native_array_module_scalar_result(
            NumpyBoolType(),
            self.scope.get_new_name(f"{subject.name}_{operation}"),
        )
        context["body"].append(Assign(result, self._native_array_present_expr(context["field"], policy)))
        return self._finish_native_array_field_operation(subject, operation, context, result)

    def _native_array_field_contiguous_operation(self, subject, policy):
        """Return whether the current pointer field target is contiguous."""
        context = self._native_array_field_operation_context(subject, "contiguous")
        result = self._native_array_module_scalar_result(
            NumpyBoolType(),
            self.scope.get_new_name(f"{subject.name}_contiguous"),
        )
        context["body"].append(Assign(result, ArrayContiguous(context["field"])))
        return self._finish_native_array_field_operation(subject, "contiguous", context, result)

    def _native_array_field_constant_bool_operation(self, subject, policy, operation):
        """Return one completed constant array-storage fact for a field."""
        context = self._native_array_field_operation_context(subject, operation)
        result = self._native_array_module_scalar_result(
            NumpyBoolType(),
            self.scope.get_new_name(f"{subject.name}_{operation}"),
        )
        context["body"].append(Assign(result, convert_to_literal(True, dtype=NumpyBoolType())))
        return self._finish_native_array_field_operation(subject, operation, context, result)

    def _native_array_field_to_numpy_operation(self, subject, policy):
        """Expose a descriptor field through the completed array extraction policy."""
        context = self._native_array_field_operation_context(subject, "to_numpy")
        getter_policy = subject.getter_ownership_decision
        if getter_policy is None:
            raise ValueError(f"Native array field {subject.name!r} is missing completed getter policy")
        data_subject = subject.clone(
            subject.name,
            new_class=Variable,
            ownership_decision=getter_policy,
            memory_handling=getter_policy.storage_mode.value,
            native_array_handle_policy=None,
            array_interop_policy=ArrayInteropPolicy(
                abi="data_buffer",
                owner=f"field {subject.name} extraction",
            ),
        )
        local_var = data_subject.clone(
            self.scope.get_new_name(subject.name),
            new_class=Variable,
            is_argument=False,
            is_optional=False,
            memory_handling=getter_policy.boundary_storage_mode.value,
        )
        self.scope.insert_variable(local_var)
        result = self._build_borrowed_array_result(data_subject, getter_policy, subject.name, local_var)
        context["body"].extend([AliasAssign(local_var, context["field"]), *result["body"]])
        return self._finish_native_array_field_operation(subject, "to_numpy", context, result["c_result"])

    def _native_array_field_deallocate_operation(self, subject, policy):
        """Deallocate an allocatable descriptor field."""
        context = self._native_array_field_operation_context(subject, "deallocate")
        context["body"].append(If(IfSection(ArrayAllocated(context["field"]), [Deallocate(context["field"])])))
        return self._finish_native_array_field_operation(subject, "deallocate", context, NIL)

    def _native_array_field_allocatable_resize_operation(self, subject, policy):
        """Resize an allocatable descriptor field."""
        context = self._native_array_field_operation_context(subject, "resize")
        arguments, original_arguments, shape = self._native_array_field_shape_arguments(subject, context)
        context["arguments"].extend(arguments)
        context["body"].append(Allocate(context["field"], shape=shape, status="unknown"))
        return self._finish_native_array_field_operation(
            subject,
            "resize",
            context,
            NIL,
            original_arguments=original_arguments,
        )

    def _native_array_field_nullify_operation(self, subject, policy):
        """Nullify a pointer descriptor field."""
        context = self._native_array_field_operation_context(subject, "nullify")
        context["body"].append(Nullify(context["field"]))
        return self._finish_native_array_field_operation(subject, "nullify", context, NIL)

    def _native_array_field_pointer_allocate_operation(self, subject, policy):
        """Allocate target storage through a policy-enabled pointer field."""
        context = self._native_array_field_operation_context(subject, "allocate")
        arguments, original_arguments, shape = self._native_array_field_shape_arguments(subject, context)
        context["arguments"].extend(arguments)
        context["body"].append(Allocate(context["field"], shape=shape, status="unallocated"))
        return self._finish_native_array_field_operation(
            subject,
            "allocate",
            context,
            NIL,
            original_arguments=original_arguments,
        )

    def _native_array_field_pointer_deallocate_operation(self, subject, policy):
        """Deallocate target storage through a policy-enabled pointer field."""
        context = self._native_array_field_operation_context(subject, "deallocate")
        context["body"].append(If(IfSection(ArrayAssociated(context["field"]), [Deallocate(context["field"])])))
        return self._finish_native_array_field_operation(subject, "deallocate", context, NIL)

    def _native_array_field_pointer_resize_operation(self, subject, policy):
        """Replace target storage through a policy-enabled pointer field."""
        context = self._native_array_field_operation_context(subject, "resize")
        arguments, original_arguments, shape = self._native_array_field_shape_arguments(subject, context)
        context["arguments"].extend(arguments)
        context["body"].extend(
            [
                If(IfSection(ArrayAssociated(context["field"]), [Deallocate(context["field"])])),
                Allocate(context["field"], shape=shape, status="unallocated"),
            ]
        )
        return self._finish_native_array_field_operation(
            subject,
            "resize",
            context,
            NIL,
            original_arguments=original_arguments,
        )

    def _native_array_field_shape_arguments(self, subject, context):
        """Return scalar extent arguments following the bound parent argument."""
        arguments = []
        original_arguments = []
        shape = []
        for index in range(subject.rank):
            name = f"extent_{index + 1}"
            original = self._native_array_module_scalar_argument(NumpyInt64Type(), name)
            converted = self._build_numeric_argument(
                original,
                ownership_decision_for_codegen_variable(original),
                needs_pointer_bridge=False,
                direct_memory_handling=StorageMode.STACK.value,
            )
            arguments.append(FunctionDefArgument(converted["c_arg"]))
            original_arguments.append(FunctionDefArgument(original))
            shape.append(converted["f_arg"])
        return arguments, original_arguments, tuple(shape)

    def _native_array_module_handle_operations(self, subject, policy):
        """Generate private module-storage operations for a runtime handle."""
        operations = [
            ("shape", self._native_array_module_shape_operation(subject, policy)),
            ("array_actual", self._native_array_module_array_actual_operation(subject, policy)),
            (
                "descriptor",
                self._native_array_module_descriptor_view_operation(subject, policy, "descriptor")
                if policy.descriptor_kind == "pointer"
                else self._native_array_module_array_actual_operation(subject, policy, "descriptor"),
            ),
            (
                self._native_array_state_operation_name(policy),
                self._native_array_module_state_operation(subject, policy),
            ),
            (
                "native_byte_order",
                self._native_array_module_constant_bool_operation(subject, policy, "native_byte_order"),
            ),
            ("aligned", self._native_array_module_constant_bool_operation(subject, policy, "aligned")),
            ("writeable", self._native_array_module_constant_bool_operation(subject, policy, "writeable")),
        ]
        if policy.to_numpy != "unsupported":
            if policy.requires_pointer_c_descriptor_interop:
                operation = self._native_array_module_descriptor_view_operation(subject, policy, "to_numpy")
            else:
                operation = self._native_array_module_to_numpy_operation(subject, policy)
            operations.append(("to_numpy", operation))
        if policy.descriptor_kind == "allocatable":
            if policy.allows("deallocate"):
                operations.append(("deallocate", self._native_array_module_deallocate_operation(subject, policy)))
            if policy.allows("resize"):
                operations.append(("resize", self._native_array_module_allocatable_resize_operation(subject, policy)))
        elif policy.allows("nullify"):
            operations.append(("contiguous", self._native_array_module_contiguous_operation(subject, policy)))
            operations.append(("nullify", self._native_array_module_nullify_operation(subject, policy)))
            if policy.allows("allocate"):
                operations.append(("allocate", self._native_array_module_pointer_allocate_operation(subject, policy)))
            if policy.allows("deallocate"):
                operations.append(
                    ("deallocate", self._native_array_module_pointer_deallocate_operation(subject, policy))
                )
            if policy.allows("resize"):
                operations.append(("resize", self._native_array_module_pointer_resize_operation(subject, policy)))
        return tuple(operations)

    @staticmethod
    def _native_array_state_operation_name(policy):
        """Return the runtime state operation name for one descriptor kind."""
        return "allocated" if policy.descriptor_kind == "allocatable" else "associated"

    @staticmethod
    def _native_array_module_scalar_result(class_type, name):
        """Return a scalar helper result with completed by-value ownership policy."""
        return Variable(
            class_type,
            name,
            ownership_decision=OwnershipDecision(
                ObjectKind.SCALAR,
                OwnershipOwner.PYTHON,
                TransferMode.BY_VALUE,
                DestructionPolicy.PYTHON_REFCOUNT,
                boundary_storage_mode=StorageMode.STACK,
                codegen_action=CodegenAction.DIRECT_VALUE,
                python_barrier_action=PythonBarrierAction.NONE,
                native_barrier_action=NativeBarrierAction.NONE,
                reason="generated native-array handle helper returns a scalar Python value",
            ),
        )

    @staticmethod
    def _native_array_module_scalar_argument(class_type, name):
        """Return a scalar helper argument with completed by-value ownership policy."""
        return Variable(
            class_type,
            name,
            is_argument=True,
            ownership_decision=OwnershipDecision(
                ObjectKind.SCALAR,
                OwnershipOwner.CALLER,
                TransferMode.BY_VALUE,
                DestructionPolicy.CALLER,
                boundary_storage_mode=StorageMode.STACK,
                codegen_action=CodegenAction.DIRECT_VALUE,
                python_barrier_action=PythonBarrierAction.SCALAR_VALUE,
                native_barrier_action=NativeBarrierAction.PASS_VALUE,
                reason="generated native-array handle helper consumes a scalar Python value",
            ),
        )

    def _native_array_module_shape_operation(self, subject, policy):
        """Return a generated operation that reports current native extents."""
        outer_scope, original_name, func_name, func_scope = self._native_array_module_operation_context(
            subject,
            "shape",
        )
        result_var, shape_vars = self._native_array_shape_operation_result(subject)
        body = [
            Assign(shape_var, ArrayShapeElement(subject, convert_to_literal(index)))
            for index, shape_var in enumerate(shape_vars)
        ]
        return self._finish_native_array_module_operation(
            subject,
            "shape",
            original_name,
            func_name,
            func_scope,
            outer_scope,
            [],
            body,
            result_var,
        )

    def _native_array_shape_operation_result(self, subject):
        """Return the result variable and extent fields for a generated shape operation."""
        scope = self.scope
        if subject.rank == 1:
            result = self._native_array_module_scalar_result(
                NumpyInt64Type(),
                scope.get_new_name(f"{subject.name}_extent_1"),
            )
            return result, (result,)
        result_type = BindCResultTupleType.get_new(tuple(NumpyInt64Type() for _ in range(subject.rank)))
        result = Variable(
            result_type,
            scope.get_new_name(f"{subject.name}_shape"),
            shape=(convert_to_literal(subject.rank),),
        )
        shape_vars = tuple(
            self._native_array_module_scalar_result(
                NumpyInt64Type(),
                scope.get_new_name(f"{subject.name}_extent_{index + 1}"),
            )
            for index in range(subject.rank)
        )
        for index, shape_var in enumerate(shape_vars):
            scope.insert_symbolic_alias(IndexedElement(result, convert_to_literal(index)), shape_var)
        return result, shape_vars

    def _native_array_module_array_actual_operation(self, subject, policy, operation="array_actual"):
        """Return a generated operation that reports a native array data address."""
        outer_scope, original_name, func_name, func_scope = self._native_array_module_operation_context(
            subject,
            operation,
        )
        result = self._native_array_module_scalar_result(
            BindCPointer(),
            self.scope.get_new_name(f"{subject.name}_{operation}"),
        )
        body = [Assign(result, NIL)]
        address_source = self._native_array_module_address_source(subject)
        if address_source is not None:
            body.append(
                If(IfSection(self._native_array_present_expr(subject, policy), [CLocFunc(address_source, result)]))
            )
        return self._finish_native_array_module_operation(
            subject,
            operation,
            original_name,
            func_name,
            func_scope,
            outer_scope,
            [],
            body,
            result,
        )

    @staticmethod
    def _native_array_module_address_source(subject):
        """Return the Fortran expression that may be passed to ``c_loc`` for array data."""
        if subject.is_alias or subject.is_target:
            return subject
        return None

    def _native_array_module_null_pointer_operation(self, subject, policy, operation):
        """Return a generated operation that explicitly reports unavailable native handoff."""
        outer_scope, original_name, func_name, func_scope = self._native_array_module_operation_context(
            subject,
            operation,
        )
        result = self._native_array_module_scalar_result(
            BindCPointer(),
            self.scope.get_new_name(f"{subject.name}_{operation}"),
        )
        return self._finish_native_array_module_operation(
            subject,
            operation,
            original_name,
            func_name,
            func_scope,
            outer_scope,
            [],
            [Assign(result, NIL)],
            result,
        )

    def _native_array_module_descriptor_view_operation(self, subject, policy, operation):
        """Associate a standard output descriptor with a pointer module target."""
        outer_scope, original_name, func_name, func_scope = self._native_array_module_operation_context(
            subject,
            operation,
        )
        argument, descriptor = self._native_array_descriptor_output_argument(subject, policy)
        return self._finish_native_array_module_operation(
            subject,
            operation,
            original_name,
            func_name,
            func_scope,
            outer_scope,
            [argument],
            [AliasAssign(descriptor, subject)],
            NIL,
        )

    def _native_array_descriptor_output_argument(self, subject, policy):
        """Create one TS 29113 pointer output dummy hidden from Python."""
        descriptor_type = BindCNativeArrayDescriptorType.get_new()
        output_decision = OwnershipDecision(
            ObjectKind.NUMPY_ARRAY,
            OwnershipOwner.CALLER,
            TransferMode.IN_PLACE,
            DestructionPolicy.CALLER,
            storage_mode=StorageMode.ALIAS,
            boundary_storage_mode=StorageMode.ALIAS,
            codegen_action=CodegenAction.HIDDEN_OUTPUT,
            mutates_native=True,
            reason="generated pointer descriptor-view operation writes a caller-established C descriptor",
        )
        descriptor_tuple = Variable(
            descriptor_type,
            self.scope.get_new_name(f"{subject.name}_descriptor_output"),
            is_argument=True,
            shape=(convert_to_literal(1),),
            ownership_decision=output_decision,
        )
        descriptor = subject.clone(
            self.scope.get_new_name(f"{subject.name}_descriptor"),
            new_class=Variable,
            is_argument=True,
            is_optional=False,
            memory_handling=StorageMode.ALIAS.value,
            ownership_decision=output_decision,
            native_array_handle_policy=replace(policy, handle_kind="argument_descriptor"),
        )
        self.scope.insert_symbolic_alias(IndexedElement(descriptor_tuple, convert_to_literal(0)), descriptor)
        return FunctionDefArgument(BindCVariable(descriptor_tuple, subject)), descriptor

    def _native_array_module_state_operation(self, subject, policy):
        """Return a generated operation that reports allocated/associated state."""
        operation = self._native_array_state_operation_name(policy)
        outer_scope, original_name, func_name, func_scope = self._native_array_module_operation_context(
            subject,
            operation,
        )
        result = self._native_array_module_scalar_result(
            NumpyBoolType(),
            self.scope.get_new_name(f"{subject.name}_state"),
        )
        body = [Assign(result, self._native_array_present_expr(subject, policy))]
        return self._finish_native_array_module_operation(
            subject,
            operation,
            original_name,
            func_name,
            func_scope,
            outer_scope,
            [],
            body,
            result,
        )

    def _native_array_module_contiguous_operation(self, subject, policy):
        """Return whether the current pointer module target is contiguous."""
        outer_scope, original_name, func_name, func_scope = self._native_array_module_operation_context(
            subject,
            "contiguous",
        )
        result = self._native_array_module_scalar_result(
            NumpyBoolType(),
            self.scope.get_new_name(f"{subject.name}_contiguous"),
        )
        return self._finish_native_array_module_operation(
            subject,
            "contiguous",
            original_name,
            func_name,
            func_scope,
            outer_scope,
            [],
            [Assign(result, ArrayContiguous(subject))],
            result,
        )

    @staticmethod
    def _native_array_present_expr(subject, policy):
        """Return the descriptor-kind-specific Fortran presence expression."""
        if policy.descriptor_kind == "allocatable":
            return ArrayAllocated(subject)
        return ArrayAssociated(subject)

    def _native_array_module_constant_bool_operation(self, subject, policy, operation):
        """Return a generated operation that reports a constant native-storage fact."""
        outer_scope, original_name, func_name, func_scope = self._native_array_module_operation_context(
            subject,
            operation,
        )
        result = self._native_array_module_scalar_result(
            NumpyBoolType(),
            self.scope.get_new_name(f"{subject.name}_{operation}"),
        )
        body = [Assign(result, convert_to_literal(True, dtype=NumpyBoolType()))]
        return self._finish_native_array_module_operation(
            subject,
            operation,
            original_name,
            func_name,
            func_scope,
            outer_scope,
            [],
            body,
            result,
        )

    def _native_array_module_to_numpy_operation(self, subject, policy):
        """Return a generated operation that extracts the module array through the data-buffer ABI."""
        data_subject = self._native_array_data_module_variable(subject)
        getter_policy = data_subject.getter_ownership_decision
        if getter_policy is None:
            raise ValueError(f"Module variable {subject.name!r} is missing completed getter policy")
        scope = self.scope
        original_name = self._generated_module_function_name(f"__x2py_{subject.name}_to_numpy")
        func_name = scope.get_new_name(f"bind_c_{original_name.lower()}")
        func_scope = scope.new_child_scope(func_name, "function")
        self.scope = func_scope
        func_scope.imports["variables"][subject.name] = subject
        getter_value = data_subject.clone(
            subject.name,
            ownership_decision=getter_policy,
            memory_handling=getter_policy.storage_mode.value,
        )
        result = self._MODULE_ARRAY_GETTER_POLICY_DISPATCHER.dispatch_decision(
            self,
            getter_value,
            getter_policy,
            data_subject,
        )
        if getter_policy.nullable:
            empty_body = [
                Assign(result["bind_var"], NIL),
                *[
                    Assign(shape_var, convert_to_literal(0, dtype=NumpyInt32Type()))
                    for shape_var in result["shape_vars"]
                ],
            ]
            result["body"] = [
                If(
                    IfSection(self._native_array_present_expr(subject, policy), result["body"]),
                    IfSection(convert_to_literal(True), empty_body),
                )
            ]
        self.exit_scope()
        return BindCFunctionDef(
            func_name,
            [],
            result["body"],
            FunctionDefResult(result["c_result"]),
            imports=self._module_variable_imports(subject),
            scope=func_scope,
            original_function=self._native_array_module_original_function(
                subject,
                original_name,
                access="to_numpy",
                result_var=data_subject,
                scope=scope,
            ),
        )

    @staticmethod
    def _native_array_data_module_variable(subject):
        """Return the ordinary array-data view of a native-array handle variable."""
        return subject.clone(
            subject.name,
            new_class=Variable,
            native_array_handle_policy=None,
            array_interop_policy=ArrayInteropPolicy(
                abi="data_buffer",
                owner=f"variable {subject.name}",
            ),
        )

    def _native_array_module_deallocate_operation(self, subject, policy):
        """Return a generated operation that deallocates an allocatable module array."""
        outer_scope, original_name, func_name, func_scope = self._native_array_module_operation_context(
            subject,
            "deallocate",
        )
        body = [If(IfSection(ArrayAllocated(subject), [Deallocate(subject)]))]
        return self._finish_native_array_module_operation(
            subject,
            "deallocate",
            original_name,
            func_name,
            func_scope,
            outer_scope,
            [],
            body,
            NIL,
        )

    def _native_array_module_allocatable_resize_operation(self, subject, policy):
        """Return a generated operation that resizes an allocatable module array."""
        (
            outer_scope,
            original_name,
            func_name,
            func_scope,
        ) = self._native_array_module_operation_context(subject, "resize")
        arguments, original_arguments, shape = self._native_array_module_shape_arguments(subject)
        body = [Allocate(subject, shape=shape, status="unknown")]
        return self._finish_native_array_module_operation(
            subject,
            "resize",
            original_name,
            func_name,
            func_scope,
            outer_scope,
            arguments,
            body,
            NIL,
            original_arguments=original_arguments,
        )

    def _native_array_module_nullify_operation(self, subject, policy):
        """Return a generated operation that nullifies a pointer module array."""
        outer_scope, original_name, func_name, func_scope = self._native_array_module_operation_context(
            subject,
            "nullify",
        )
        return self._finish_native_array_module_operation(
            subject,
            "nullify",
            original_name,
            func_name,
            func_scope,
            outer_scope,
            [],
            [Nullify(subject)],
            NIL,
        )

    def _native_array_module_pointer_allocate_operation(self, subject, policy):
        """Return a generated operation that allocates storage through a pointer module variable."""
        (
            outer_scope,
            original_name,
            func_name,
            func_scope,
        ) = self._native_array_module_operation_context(subject, "allocate")
        arguments, original_arguments, shape = self._native_array_module_shape_arguments(subject)
        body = [Allocate(subject, shape=shape, status="unallocated")]
        return self._finish_native_array_module_operation(
            subject,
            "allocate",
            original_name,
            func_name,
            func_scope,
            outer_scope,
            arguments,
            body,
            NIL,
            original_arguments=original_arguments,
        )

    def _native_array_module_pointer_deallocate_operation(self, subject, policy):
        """Return a generated operation that deallocates storage through a pointer module variable."""
        (
            outer_scope,
            original_name,
            func_name,
            func_scope,
        ) = self._native_array_module_operation_context(subject, "deallocate")
        body = [If(IfSection(ArrayAssociated(subject), [DeallocatePointer(subject)]))]
        return self._finish_native_array_module_operation(
            subject,
            "deallocate",
            original_name,
            func_name,
            func_scope,
            outer_scope,
            [],
            body,
            NIL,
        )

    def _native_array_module_pointer_resize_operation(self, subject, policy):
        """Return a generated operation that reallocates storage through a pointer module variable."""
        (
            outer_scope,
            original_name,
            func_name,
            func_scope,
        ) = self._native_array_module_operation_context(subject, "resize")
        arguments, original_arguments, shape = self._native_array_module_shape_arguments(subject)
        body = [
            If(IfSection(ArrayAssociated(subject), [DeallocatePointer(subject)])),
            Allocate(subject, shape=shape, status="unallocated"),
        ]
        return self._finish_native_array_module_operation(
            subject,
            "resize",
            original_name,
            func_name,
            func_scope,
            outer_scope,
            arguments,
            body,
            NIL,
            original_arguments=original_arguments,
        )

    def _native_array_module_shape_arguments(self, subject):
        """Return scalar extent arguments for generated shape-changing operations."""
        arguments = []
        original_arguments = []
        shape = []
        for index in range(subject.rank):
            name = f"extent_{index + 1}"
            original = self._native_array_module_scalar_argument(NumpyInt64Type(), name)
            converted = self._build_numeric_argument(
                original,
                ownership_decision_for_codegen_variable(original),
                needs_pointer_bridge=False,
                direct_memory_handling=StorageMode.STACK.value,
            )
            arguments.append(FunctionDefArgument(converted["c_arg"]))
            original_arguments.append(FunctionDefArgument(original))
            shape.append(converted["f_arg"])
        return arguments, original_arguments, tuple(shape)

    def _native_array_module_operation_context(self, subject, operation):
        """Enter the function scope for one generated module-handle operation."""
        scope = self.scope
        if scope is None:
            raise ValueError(f"Native array module handle {subject.name!r} needs an active generation scope")
        self.scope = scope
        original_name = self._generated_module_function_name(f"__x2py_{subject.name}_{operation}")
        func_name = scope.get_new_name(f"bind_c_{original_name.lower()}")
        func_scope = scope.new_child_scope(func_name, "function")
        self.scope = func_scope
        func_scope.imports["variables"][subject.name] = subject
        return scope, original_name, func_name, func_scope

    def _finish_native_array_module_operation(
        self,
        subject,
        operation,
        original_name,
        func_name,
        func_scope,
        outer_scope,
        arguments,
        body,
        result,
        *,
        original_arguments=(),
    ):
        """Leave an operation scope and create its private Bind-C function."""
        self.exit_scope()
        original_result = self._native_array_module_original_result(subject, operation, result)
        self._copy_native_array_module_original_result_aliases(
            func_scope,
            outer_scope,
            result,
            original_result,
        )
        original_function = self._native_array_module_original_function(
            subject,
            original_name,
            access=operation,
            result_var=original_result,
            arguments=original_arguments,
            scope=outer_scope,
        )
        return BindCFunctionDef(
            func_name,
            arguments,
            body,
            FunctionDefResult(result),
            imports=self._module_variable_imports(subject),
            scope=func_scope,
            original_function=original_function,
        )

    @staticmethod
    def _copy_native_array_module_original_result_aliases(func_scope, original_scope, result, original_result):
        """Copy tuple result aliases onto generated operation metadata."""
        if (
            result is NIL
            or original_result is NIL
            or not isinstance(getattr(result, "class_type", None), BindCResultTupleType)
        ):
            return
        for index, alias in enumerate(func_scope.collect_all_tuple_elements(result)):
            original_scope.insert_symbolic_alias(
                IndexedElement(original_result, convert_to_literal(index)),
                alias,
            )

    @staticmethod
    def _native_array_module_original_result(subject, operation, result):
        """Return the Python-visible result variable for operation wrapper generation."""
        if result is NIL:
            return NIL
        if operation == "to_numpy":
            return result
        return result.clone(f"{subject.name}_{operation}_value", new_class=Variable)

    @staticmethod
    def _native_array_module_original_function(subject, name, *, access, result_var, arguments=(), scope):
        """Return private source metadata for a generated module-handle operation."""
        return FunctionDef(
            name,
            list(arguments),
            [],
            FunctionDefResult(result_var),
            scope=scope,
            decorators={
                RUNTIME_HOLD_GIL_METADATA: True,
                INTERNAL_MODULE_VARIABLE_NAME_METADATA: subject.name,
                INTERNAL_MODULE_VARIABLE_ACCESS_METADATA: access,
                INTERNAL_NATIVE_ARRAY_HANDLE_OPERATION_METADATA: True,
            },
        )

    def _bridge_borrowed_native_array_module_handle(self, subject, policy):
        """Expose completed borrowed module storage as a generated runtime handle."""
        return self._native_array_module_handle(subject, policy)

    def _bridge_borrowed_native_array_field_handle(self, subject, policy):
        """Expose completed borrowed field storage as a generated runtime handle."""
        return self._native_array_field_handle(subject, policy)

    def _bridge_allocatable_descriptor_argument(self, subject, policy, *args):
        """Pass an allocatable TS29113 descriptor through the bind(C) wrapper."""
        return self._bridge_native_array_descriptor_argument(subject, policy, *args)

    def _bridge_owned_allocatable_result_handle(self, subject, policy, *args):
        """Return bridge-local data for transfer into persistent CFI owner storage."""
        name = subject.name
        scope = self.scope
        scope.insert_symbol(name)
        local_var = subject.clone(
            scope.get_expected_name(name),
            new_class=Variable,
            memory_handling=StorageMode.HEAP.value,
            shape=None,
            is_argument=False,
            is_optional=False,
        )
        scope.insert_variable(local_var, name)
        decision = ownership_decision_for_codegen_variable(subject)
        result = self._build_heap_copy_return_array_result(subject, decision, name, local_var)
        result["f_result"] = local_var
        return result

    def _bridge_pointer_descriptor_argument(self, subject, policy, *args):
        """Pass a pointer TS29113 descriptor through the bind(C) wrapper."""
        return self._bridge_native_array_descriptor_argument(subject, policy, *args)

    def _bridge_optional_native_array_handle(self, subject, policy, *args):
        """Pass an optional TS29113 descriptor through the bind(C) wrapper."""
        return self._bridge_native_array_descriptor_argument(subject, policy, *args)

    def _bridge_native_array_descriptor_argument(self, subject, policy, expr, func):
        """Build the Bind-C descriptor pointer tuple selected by completed policy."""
        descriptor_type = self._native_array_descriptor_argument_type(policy)
        scope = self.scope
        name = subject.name
        scope.insert_symbol(name)
        descriptor_tuple = Variable(
            descriptor_type,
            scope.get_new_name(f"{name}_descriptor_arg"),
            is_argument=True,
            shape=(convert_to_literal(len(descriptor_type)),),
        )
        descriptor_dummy = subject.clone(
            scope.get_expected_name(name),
            new_class=Variable,
            is_argument=True,
            is_optional=policy.optional_absent,
            memory_handling=StorageMode.ALIAS.value if policy.descriptor_kind == "pointer" else StorageMode.HEAP.value,
        )
        scope.insert_symbolic_alias(IndexedElement(descriptor_tuple, convert_to_literal(0)), descriptor_dummy)
        presence_var = None
        if descriptor_type.has_presence:
            presence_var = Variable(
                BindCPointer(),
                scope.get_new_name(f"{name}_present"),
                is_argument=True,
                is_optional=False,
                memory_handling=StorageMode.ALIAS.value,
            )
            scope.insert_symbolic_alias(IndexedElement(descriptor_tuple, convert_to_literal(1)), presence_var)
        return {
            "c_arg": self._native_array_descriptor_function_argument(expr, descriptor_tuple, subject),
            "f_arg": self._native_array_descriptor_call_argument(expr, func, descriptor_dummy),
            "body": [],
            "optional_presence_var": presence_var,
        }

    @staticmethod
    def _native_array_descriptor_function_argument(expr, descriptor_tuple, subject):
        """Wrap the generated descriptor tuple as the C-visible function argument."""
        return FunctionDefArgument(
            BindCVariable(descriptor_tuple, subject),
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

    def _native_array_descriptor_call_argument(self, expr, func, descriptor_dummy):
        """Return the native call argument for the descriptor dummy."""
        if self._uses_positional_native_call(func):
            return FunctionCallArgument(descriptor_dummy)
        return FunctionCallArgument(descriptor_dummy, keyword=self._native_argument_keyword(func, expr))

    @staticmethod
    def _native_array_descriptor_argument_type(policy):
        """Return the Bind-C tuple shape selected for a handle descriptor argument."""
        return native_array_descriptor_argument_type(policy)

    @staticmethod
    def _validate_descriptor_array_interop_policy(subject, policy) -> None:
        """Require descriptor ABI dispatch to carry completed native handle policy."""
        handle_policy = subject.native_array_handle_policy
        if handle_policy is None:
            raise ValueError(f"Descriptor array interop for {subject.name!r} is missing completed handle policy")
        if policy.descriptor_kind != handle_policy.descriptor_kind or policy.handle_kind != handle_policy.handle_kind:
            raise ValueError(
                f"Descriptor array interop for {subject.name!r} disagrees with completed handle policy: "
                f"{policy.descriptor_kind}/{policy.handle_kind} != "
                f"{handle_policy.descriptor_kind}/{handle_policy.handle_kind}"
            )

    def _borrowed_module_array_getter_result(self, getter_value, _decision, expr):
        """Build a borrowed module-array getter result."""
        return self._get_bind_c_array(expr.name, getter_value, expr.shape, pointer_target=True)

    def _snapshot_module_array_getter_result(self, getter_value, _decision, expr):
        """Build a copied module-array getter result."""
        return self._get_allocatable_snapshot_bind_c_array(expr.name, getter_value, expr)

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
        if expr.array_interop_policy is not None and expr.array_interop_policy.is_descriptor:
            self._validate_descriptor_array_interop_policy(expr, expr.array_interop_policy)
            return self._NATIVE_ARRAY_HANDLE_DISPATCHER.dispatch(
                self,
                expr,
                expr.native_array_handle_policy,
            )

        lhs = expr.lhs
        getter_policy = expr.getter_ownership_decision
        setter_policy = expr.setter_ownership_decision
        if getter_policy is None or setter_policy is None:
            raise ValueError(f"Field {expr.name!r} is missing completed accessor policy")
        class_dtype = lhs.dtype
        # ----------------------------------------------------------------------------------
        #                        Create getter
        # ----------------------------------------------------------------------------------
        getter_name = self.scope.get_new_name(f"{class_dtype.name}_{expr.name}_getter".lower())
        getter_scope = self.scope.new_child_scope(getter_name, "function")
        self.scope = getter_scope
        self.scope.insert_symbol(expr.name)
        getter_value = expr.clone(
            expr.name,
            lhs=expr.lhs,
            ownership_decision=getter_policy,
            memory_handling=getter_policy.storage_mode.value,
        )
        getter_result_info = self._convert_result(getter_value, lhs.cls_base.scope)
        getter_result = getter_result_info["c_result"]

        getter_arg_generator = self._convert_argument(FunctionDefArgument(lhs, bound_argument=True), expr)
        self_obj = getter_arg_generator["f_arg"].value
        getter_arg = getter_arg_generator["c_arg"]

        getter_body = getter_arg_generator["body"]

        attrib = expr.clone(expr.name, lhs=self_obj)
        obj = self.scope.find(expr.name)
        self._FIELD_GETTER_POLICY_DISPATCHER.dispatch_decision(
            self,
            expr,
            getter_policy,
            attrib,
            obj,
            getter_result_info,
            getter_body,
        )
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

        setter = self._FIELD_SETTER_POLICY_DISPATCHER.dispatch(self, expr, setter_policy, lhs)
        return BindCClassProperty(
            lhs.cls_base.scope.get_python_name(expr.name),
            getter,
            setter,
            lhs.dtype,
            getter_policy=getter_policy,
            setter_policy=setter_policy,
        )

    @staticmethod
    def _skip_field_setter(_expr, _setter_policy, _lhs):
        """Omit native setter emission when policy exposes no write-through path."""

    @staticmethod
    def _append_value_field_getter(_expr, _getter_policy, attrib, _obj, getter_result_info, getter_body):
        """Copy a scalar-like field getter value into the C-visible result."""
        getter_body.append(Assign(getter_result_info["f_result"], attrib))
        getter_body.extend(getter_result_info["body"])

    @staticmethod
    def _append_alias_field_getter(_expr, _getter_policy, attrib, obj, getter_result_info, getter_body):
        """Alias a borrowed field getter target before result conversion."""
        getter_body.append(AliasAssign(obj, attrib))
        getter_body.extend(getter_result_info["body"])

    def _append_borrowed_array_field_getter(self, expr, getter_policy, attrib, obj, getter_result_info, getter_body):
        """Alias a borrowed array field and handle nullable allocatable storage."""
        if not getter_policy.nullable:
            self._append_alias_field_getter(expr, getter_policy, attrib, obj, getter_result_info, getter_body)
            return
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

    def _append_nullable_scalar_field_getter(self, _expr, getter_policy, attrib, _obj, getter_result_info, getter_body):
        """Copy a nullable scalar descriptor field through a C data pointer."""
        getter_body.append(
            self._nullable_scalar_snapshot_if(
                attrib,
                self._nullable_scalar_status_func(getter_policy),
                getter_result_info["bind_var"],
                getter_result_info["copy_var"],
                getter_result_info["size_var"],
            )
        )

    def _build_field_setter(self, expr, setter_policy, lhs):
        """Build one field setter from completed storage and setter policies."""
        setter_name = self.scope.get_new_name(f"{lhs.dtype.name}_{expr.name}_setter".lower())
        setter_scope = self.scope.new_child_scope(setter_name, "function")
        self.scope = setter_scope
        self.scope.insert_symbol(expr.name)
        setter_value = expr.clone(
            expr.name,
            lhs=expr.lhs,
            memory_handling=setter_policy.storage_mode.value,
            ownership_decision=setter_policy,
        )

        setter_arg_generators = (
            self._convert_argument(FunctionDefArgument(lhs, bound_argument=True), expr),
            self._convert_argument(FunctionDefArgument(setter_value), expr),
        )
        setter_args = (setter_arg_generators[0]["c_arg"], setter_arg_generators[1]["c_arg"])
        setter_args[1].persistent_target = setter_policy.assignment_mode is AssignmentMode.ALIAS

        self_obj = setter_arg_generators[0]["f_arg"].value
        set_val = setter_arg_generators[1]["f_arg"].value

        setter_body = setter_arg_generators[0]["body"] + setter_arg_generators[1]["body"]

        attrib = expr.clone(expr.name, lhs=self_obj)
        try:
            assignment = self._FIELD_ASSIGNMENT_BY_POLICY[setter_policy.assignment_mode]
        except KeyError:
            raise ValueError(
                f"No field setter assignment for completed policy {setter_policy.assignment_mode.value!r}"
            ) from None
        setter_body.append(assignment(attrib, set_val))
        self.exit_scope()

        return BindCFunctionDef(
            setter_name,
            setter_args,
            setter_body,
            original_function=expr,
            scope=setter_scope,
        )

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
        instance_policy = expr.decorators[RESOLVED_CLASS_INSTANCE_POLICY_METADATA]
        self_policy = expr.decorators[RESOLVED_CLASS_SELF_POLICY_METADATA]
        func_name = self.scope.get_new_name(f"{name}_bind_c_alloc".lower())
        func_scope = self.scope.new_child_scope(func_name, "function")

        # Allocatable is not returned so it must appear in local scope
        local_var = Variable(
            expr.class_type,
            func_scope.get_new_name(f"{name}_obj"),
            cls_base=expr,
            memory_handling=instance_policy.boundary_storage_mode.value,
            ownership_decision=instance_policy,
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
                Variable(
                    expr.class_type,
                    scope.get_new_name("self"),
                    cls_base=expr,
                    memory_handling=self_policy.boundary_storage_mode.value,
                    ownership_decision=self_policy,
                ),
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
        pseudo_self = Variable(
            expr.class_type,
            "self",
            cls_base=expr,
            memory_handling=self_policy.boundary_storage_mode.value,
            ownership_decision=self_policy,
        )
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
            decorators=expr.decorators,
            superclasses=expr.superclasses,
        )

    # ------------------------------------------------------------------
    # Datatype conversion
    # ------------------------------------------------------------------

    def _convert_argument(self, expr, func):
        """
        Extract the C-compatible FunctionDefArgument from the Fortran FunctionDefArgument.

        Extract the C-compatible FunctionDefArgument from the Fortran FunctionDefArgument.

        The explicit datatype dispatch table selects the conversion helper.

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
        if isinstance(var, FunctionAddress):
            return self._convert_callback_argument(expr, func)
        if var.array_interop_policy is not None:
            return self._ARRAY_INTEROP_POLICY_DISPATCHER.dispatch(
                self,
                var,
                var.array_interop_policy,
                "argument",
                expr,
                func,
            )
        return self._bridge_non_array_argument(var, expr, func)

    def _bridge_data_buffer_argument(self, subject, _policy, expr, func):
        """Convert an ordinary array argument through the data-buffer ABI."""
        return self._bridge_non_array_argument(subject, expr, func)

    def _bridge_descriptor_argument(self, subject, policy, expr, func):
        """Convert a native array handle argument through descriptor ABI."""
        self._validate_descriptor_array_interop_policy(subject, policy)
        return self._NATIVE_ARRAY_HANDLE_DISPATCHER.dispatch(
            self,
            subject,
            subject.native_array_handle_policy,
            expr,
            func,
        )

    def _bridge_non_array_argument(self, var, expr, func):
        """Convert a function argument without native descriptor-handle routing."""
        func_def_argument_dict = self._NATIVE_BARRIER_DISPATCHER.dispatch(self, var, func)
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

        if self._uses_positional_native_call(func):
            func_def_argument_dict["f_arg"] = FunctionCallArgument(func_def_argument_dict["f_arg"])
        else:
            func_def_argument_dict["f_arg"] = FunctionCallArgument(
                func_def_argument_dict["f_arg"],
                keyword=self._native_argument_keyword(func, expr),
            )
        return func_def_argument_dict

    def _convert_callback_argument(self, expr, func):
        """Lower one immediate-call dummy procedure to a C callback plus a Fortran adapter."""
        callback = expr.var
        if callback.is_optional:
            raise ValueError(f"Optional callback argument {callback.name!s} is not supported")

        callback_name = str(callback.name)
        c_name = self.scope.get_new_name(f"bound_{callback_name}")
        adapter_name = self.scope.get_new_name(f"adapt_{callback_name}")
        c_scope = self.scope.new_child_scope(f"{c_name}_interface", "function")
        adapter_scope = self.scope.new_child_scope(adapter_name, "function")

        c_arguments = []
        adapter_arguments = []
        adapter_call_arguments = []
        adapter_body = []
        adapter_post_body = []
        abi_arguments = []

        for argument in callback.arguments:
            native_var = argument.var
            adapter_var = native_var.clone(
                str(native_var.name),
                new_class=Variable,
                is_argument=True,
                is_target=False,
                memory_handling="stack",
            )
            adapter_scope.insert_variable(adapter_var, name=str(native_var.name))
            adapter_arguments.append(FunctionDefArgument(adapter_var))
            converted = self._convert_callback_abi_argument(
                callback_name,
                native_var,
                adapter_var,
                c_scope,
                adapter_scope,
            )
            c_arguments.extend(converted["c_arguments"])
            adapter_call_arguments.extend(converted["call_arguments"])
            adapter_body.extend(converted["body"])
            adapter_post_body.extend(converted["post_body"])
            abi_arguments.append(converted["abi"])

        native_result = callback.results.var
        abi_result = {"kind": "none", "native": NIL}
        if native_result is NIL:
            c_result = FunctionDefResult(NIL)
            adapter_result = FunctionDefResult(NIL)
        else:
            adapter_result_var = native_result.clone(
                adapter_scope.get_new_name(f"{callback_name}_result"),
                new_class=Variable,
                is_argument=False,
                is_target=native_result.rank > 0 or isinstance(native_result.class_type, CustomDataType),
            )
            adapter_scope.insert_variable(adapter_result_var)
            adapter_result = FunctionDefResult(adapter_result_var)
            converted_result = self._CALLBACK_RESULT_POLICY_DISPATCHER.dispatch(
                self,
                native_result,
                callback_name,
                c_scope,
                adapter_result_var,
            )
            c_result = converted_result["c_result"]
            abi_result = converted_result["abi"]

        c_callback = FunctionAddress(
            c_name,
            c_arguments,
            c_result,
            is_argument=True,
            decorators={
                "x2py_callback_abi": {
                    "native": callback,
                    "arguments": abi_arguments,
                    "result": abi_result,
                }
            },
            scope=c_scope,
        )

        callback_call = c_callback(*adapter_call_arguments)
        if native_result is NIL:
            adapter_body.append(callback_call)
            adapter_body.extend(adapter_post_body)
        elif abi_result["kind"] == "scalar":
            adapter_body.append(Assign(adapter_result.var, callback_call))
            adapter_body.extend(adapter_post_body)
        else:
            result_pointer = Variable(
                BindCPointer(),
                adapter_scope.get_new_name(f"{callback_name}_result_data"),
                memory_handling="stack",
            )
            adapter_scope.insert_variable(result_pointer)
            adapter_body.append(Assign(result_pointer, callback_call))
            adapter_body.extend(adapter_post_body)
            result_view = adapter_result.var.clone(
                adapter_scope.get_new_name(f"{callback_name}_result_view"),
                new_class=Variable,
                is_argument=False,
                memory_handling="alias",
                is_target=False,
            )
            adapter_scope.insert_variable(result_view)
            shape = adapter_result.var.alloc_shape if adapter_result.var.rank > 0 else None
            adapter_body.append(C_F_Pointer(result_pointer, result_view, shape))
            adapter_body.append(Assign(adapter_result.var, result_view))

        adapter = FunctionDef(
            adapter_name,
            adapter_arguments,
            adapter_body,
            adapter_result,
            decorators={"x2py_callback_adapter": callback},
            scope=adapter_scope,
        )
        self._additional_functions.append(adapter)
        f_arg = (
            FunctionCallArgument(adapter)
            if self._uses_positional_native_call(func)
            else FunctionCallArgument(adapter, keyword=self._native_argument_keyword(func, expr))
        )
        return {
            "c_arg": FunctionDefArgument(c_callback),
            "f_arg": f_arg,
            "body": [],
        }

    @staticmethod
    def _uses_positional_native_call(func) -> bool:
        """Return whether the native call should avoid Fortran keywords."""

        return (
            getattr(func, "is_external", False)
            or any(isinstance(argument.var, FunctionAddress) for argument in getattr(func, "arguments", ()))
        ) and not FortranToCBridgeGenerator._has_optional_arguments(func)

    @staticmethod
    def _native_argument_keyword(func, expr):
        """Return the original native keyword for a generated argument."""

        if getattr(func, "scope", None) is None:
            return expr.name
        try:
            return func.scope.get_python_name(expr.name)
        except RuntimeError:
            return expr.name

    def _convert_callback_abi_argument(self, callback_name, native_var, adapter_var, c_scope, adapter_scope):
        """Dispatch one callback argument to its ABI converter."""
        return self._CALLBACK_ARGUMENT_POLICY_DISPATCHER.dispatch(
            self,
            native_var,
            callback_name,
            adapter_var,
            c_scope,
            adapter_scope,
        )

    @staticmethod
    def _convert_callback_scalar_result(native_result, decision, callback_name, c_scope, _adapter_result):
        """Build the C ABI result for a scalar callback result."""
        c_result_var = native_result.clone(
            c_scope.get_new_name(f"{callback_name}_result"),
            new_class=Variable,
            is_argument=False,
            memory_handling=decision.boundary_storage_mode.value,
        )
        c_scope.insert_variable(c_result_var)
        return {
            "c_result": FunctionDefResult(c_result_var),
            "abi": {"kind": "scalar", "native": native_result, "abi": c_result_var},
        }

    def _convert_callback_array_result(self, native_result, decision, callback_name, c_scope, adapter_result):
        """Build the pointer ABI for an array callback result."""
        if any(item is None for item in adapter_result.alloc_shape):
            raise ValueError(f"Callback {callback_name!r} array result must have an explicit shape")
        return self._convert_callback_pointer_result(
            native_result,
            decision,
            callback_name,
            c_scope,
            kind="array",
        )

    def _convert_callback_derived_result(self, native_result, decision, callback_name, c_scope, _adapter_result):
        """Build the pointer ABI for a derived callback result."""
        return self._convert_callback_pointer_result(
            native_result,
            decision,
            callback_name,
            c_scope,
            kind="derived",
        )

    @staticmethod
    def _convert_callback_pointer_result(native_result, _decision, callback_name, c_scope, *, kind):
        """Represent an array or derived callback result with one C pointer."""
        c_result_var = Variable(
            BindCPointer(),
            c_scope.get_new_name(f"{callback_name}_result_data"),
            memory_handling="stack",
        )
        c_scope.insert_variable(c_result_var)
        return {
            "c_result": FunctionDefResult(c_result_var),
            "abi": {"kind": kind, "native": native_result, "abi": c_result_var},
        }

    def _convert_callback_scalar_argument(
        self,
        native_var,
        decision,
        callback_name,
        adapter_var,
        c_scope,
        adapter_scope,
    ):
        """Convert a scalar callback argument to its interoperable ABI."""
        if decision.python_barrier_action is PythonBarrierAction.SCALAR_STORAGE:
            return self._convert_callback_scalar_storage_argument(
                native_var,
                decision,
                callback_name,
                adapter_var,
                c_scope,
                adapter_scope,
                copy_in=True,
                copy_out=False,
            )
        c_var = native_var.clone(
            str(native_var.name),
            new_class=Variable,
            is_argument=True,
            memory_handling="stack",
            passes_by_value=True,
        )
        c_scope.insert_variable(c_var, name=str(native_var.name))
        return {
            "c_arguments": [FunctionDefArgument(c_var)],
            "call_arguments": [cast_to(adapter_var, c_var.dtype)],
            "body": [],
            "post_body": [],
            "abi": {"kind": "scalar", "native": native_var, "abi": (c_var,)},
        }

    def _convert_callback_scalar_storage_writable_argument(
        self, native_var, decision, callback_name, adapter_var, c_scope, adapter_scope
    ):
        """Expose a writable scalar callback dummy as rank-0 NumPy storage."""
        return self._convert_callback_scalar_storage_argument(
            native_var,
            decision,
            callback_name,
            adapter_var,
            c_scope,
            adapter_scope,
            copy_in=True,
            copy_out=True,
        )

    def _convert_callback_scalar_storage_output_argument(
        self, native_var, decision, callback_name, adapter_var, c_scope, adapter_scope
    ):
        """Expose a scalar callback output dummy as rank-0 NumPy storage."""
        return self._convert_callback_scalar_storage_argument(
            native_var,
            decision,
            callback_name,
            adapter_var,
            c_scope,
            adapter_scope,
            copy_in=False,
            copy_out=True,
        )

    def _convert_callback_scalar_storage_argument(
        self,
        native_var,
        _decision,
        _callback_name,
        adapter_var,
        c_scope,
        adapter_scope,
        *,
        copy_in,
        copy_out,
    ):
        """Convert a scalar callback argument to pointer-backed Python storage."""
        data = Variable(
            BindCPointer(),
            c_scope.get_new_name(f"{native_var.name}_data"),
            is_argument=True,
            memory_handling="stack",
        )
        c_scope.insert_variable(data)
        data_value, callback_storage = self._callback_pointer_storage(native_var, adapter_var, adapter_scope)
        body = []
        post_body = []
        if copy_in:
            body.append(Assign(callback_storage, adapter_var))
        body.append(CLocFunc(callback_storage, data_value))
        if copy_out:
            post_body.append(Assign(adapter_var, callback_storage))
        return {
            "c_arguments": [FunctionDefArgument(data)],
            "call_arguments": [data_value],
            "body": body,
            "post_body": post_body,
            "abi": {"kind": "scalar_storage", "native": native_var, "abi": (data,)},
        }

    def _convert_callback_string_input_argument(
        self, native_var, decision, callback_name, adapter_var, c_scope, adapter_scope
    ):
        """Expose a read-only character callback dummy as a Python string."""
        return self._convert_callback_string_argument(
            native_var,
            decision,
            callback_name,
            adapter_var,
            c_scope,
            adapter_scope,
            kind="string",
            copy_in=True,
            copy_out=False,
        )

    def _convert_callback_string_storage_writable_argument(
        self, native_var, decision, callback_name, adapter_var, c_scope, adapter_scope
    ):
        """Expose a writable character callback dummy as rank-0 bytes storage."""
        return self._convert_callback_string_argument(
            native_var,
            decision,
            callback_name,
            adapter_var,
            c_scope,
            adapter_scope,
            kind="string_storage",
            copy_in=True,
            copy_out=True,
        )

    def _convert_callback_string_storage_output_argument(
        self, native_var, decision, callback_name, adapter_var, c_scope, adapter_scope
    ):
        """Expose a character callback output dummy as rank-0 bytes storage."""
        return self._convert_callback_string_argument(
            native_var,
            decision,
            callback_name,
            adapter_var,
            c_scope,
            adapter_scope,
            kind="string_storage",
            copy_in=False,
            copy_out=True,
        )

    def _convert_callback_string_argument(
        self,
        native_var,
        _decision,
        _callback_name,
        adapter_var,
        c_scope,
        adapter_scope,
        *,
        kind,
        copy_in,
        copy_out,
    ):
        """Convert a fixed-length character callback argument to pointer ABI data."""
        fixed_len = self._callback_string_length(native_var)
        data = Variable(
            BindCPointer(),
            c_scope.get_new_name(f"{native_var.name}_data"),
            is_argument=True,
            memory_handling="stack",
        )
        length = Variable(
            NumpyInt64Type(),
            c_scope.get_new_name(f"{native_var.name}_length"),
            is_argument=True,
            passes_by_value=True,
        )
        c_scope.insert_variable(data)
        c_scope.insert_variable(length)
        data_value, callback_storage = self._callback_pointer_storage(native_var, adapter_var, adapter_scope)
        body = []
        post_body = []
        if copy_in:
            body.append(Assign(callback_storage, adapter_var))
        body.append(CLocFunc(callback_storage, data_value))
        if copy_out:
            post_body.append(Assign(adapter_var, callback_storage))
        return {
            "c_arguments": [FunctionDefArgument(data), FunctionDefArgument(length)],
            "call_arguments": [
                data_value,
                cast_to(FortranCharacterLength(callback_storage), NumpyInt64Type()),
            ],
            "body": body,
            "post_body": post_body,
            "abi": {"kind": kind, "native": native_var, "abi": (data, length), "length": fixed_len},
        }

    @staticmethod
    def _callback_string_length(native_var):
        """Return a fixed callback character length for diagnostics and ABI metadata."""
        if native_var.fortran_character_length not in (None, "*", ":"):
            return native_var.fortran_character_length
        if native_var.alloc_shape and native_var.alloc_shape[0] is not None:
            return native_var.alloc_shape[0]
        raise ValueError(f"Callback string argument {native_var.name!r} requires a fixed character length")

    def _convert_callback_array_input_argument(
        self, native_var, decision, callback_name, adapter_var, c_scope, adapter_scope
    ):
        """Copy an array callback input into adapter-visible pointer storage."""
        return self._convert_callback_pointer_argument(
            native_var,
            decision,
            callback_name,
            adapter_var,
            c_scope,
            adapter_scope,
            is_array=True,
            copy_in=True,
            copy_out=False,
        )

    def _convert_callback_array_writable_argument(
        self, native_var, decision, callback_name, adapter_var, c_scope, adapter_scope
    ):
        """Copy an array callback argument into and out of pointer storage."""
        return self._convert_callback_pointer_argument(
            native_var,
            decision,
            callback_name,
            adapter_var,
            c_scope,
            adapter_scope,
            is_array=True,
            copy_in=True,
            copy_out=True,
        )

    def _convert_callback_array_output_argument(
        self, native_var, decision, callback_name, adapter_var, c_scope, adapter_scope
    ):
        """Copy an array callback output from adapter pointer storage."""
        return self._convert_callback_pointer_argument(
            native_var,
            decision,
            callback_name,
            adapter_var,
            c_scope,
            adapter_scope,
            is_array=True,
            copy_in=False,
            copy_out=True,
        )

    def _convert_callback_derived_input_argument(
        self, native_var, decision, callback_name, adapter_var, c_scope, adapter_scope
    ):
        """Copy a derived callback input into adapter-visible pointer storage."""
        return self._convert_callback_pointer_argument(
            native_var,
            decision,
            callback_name,
            adapter_var,
            c_scope,
            adapter_scope,
            is_array=False,
            copy_in=True,
            copy_out=False,
        )

    def _convert_callback_derived_writable_argument(
        self, native_var, decision, callback_name, adapter_var, c_scope, adapter_scope
    ):
        """Copy a derived callback argument into and out of pointer storage."""
        return self._convert_callback_pointer_argument(
            native_var,
            decision,
            callback_name,
            adapter_var,
            c_scope,
            adapter_scope,
            is_array=False,
            copy_in=True,
            copy_out=True,
        )

    def _convert_callback_derived_output_argument(
        self, native_var, decision, callback_name, adapter_var, c_scope, adapter_scope
    ):
        """Copy a derived callback output from adapter pointer storage."""
        return self._convert_callback_pointer_argument(
            native_var,
            decision,
            callback_name,
            adapter_var,
            c_scope,
            adapter_scope,
            is_array=False,
            copy_in=False,
            copy_out=True,
        )

    @staticmethod
    def _callback_pointer_storage(native_var, adapter_var, adapter_scope):
        """Create adapter-side pointer storage for a callback argument."""
        data_value = Variable(
            BindCPointer(),
            adapter_scope.get_new_name(f"{native_var.name}_data"),
            memory_handling="stack",
        )
        adapter_scope.insert_variable(data_value)
        callback_storage = adapter_var.clone(
            adapter_scope.get_new_name(f"{native_var.name}_callback_storage"),
            new_class=Variable,
            is_argument=False,
            is_target=True,
            memory_handling="stack",
        )
        adapter_scope.insert_variable(callback_storage)
        return data_value, callback_storage

    def _convert_callback_pointer_argument(
        self,
        native_var,
        _decision,
        _callback_name,
        adapter_var,
        c_scope,
        adapter_scope,
        *,
        is_array,
        copy_in,
        copy_out,
    ):
        """Convert an array or derived callback argument to pointer ABI data."""
        data = Variable(
            BindCPointer(),
            c_scope.get_new_name(f"{native_var.name}_data"),
            is_argument=True,
            memory_handling="stack",
        )
        c_scope.insert_variable(data)
        dimensions = self._callback_array_dimensions(native_var, c_scope) if is_array else []
        data_value, callback_storage = self._callback_pointer_storage(native_var, adapter_var, adapter_scope)
        body = []
        post_body = []
        if copy_in:
            body.append(Assign(callback_storage, adapter_var))
        body.append(CLocFunc(callback_storage, data_value))
        if copy_out:
            post_body.append(Assign(adapter_var, callback_storage))
        shape_arguments = [
            ArrayShapeElement(callback_storage, convert_to_literal(index)) for index in range(native_var.rank)
        ]
        return {
            "c_arguments": [FunctionDefArgument(item) for item in (data, *dimensions)],
            "call_arguments": [data_value, *shape_arguments],
            "body": body,
            "post_body": post_body,
            "abi": {
                "kind": "array" if is_array else "derived",
                "native": native_var,
                "abi": (data, *dimensions),
            },
        }

    @staticmethod
    def _callback_array_dimensions(native_var, c_scope):
        """Create C ABI dimension arguments for a callback array."""
        dimensions = [
            Variable(
                NumpyInt64Type(),
                c_scope.get_new_name(f"{native_var.name}_shape_{index + 1}"),
                is_argument=True,
                passes_by_value=True,
            )
            for index in range(native_var.rank)
        ]
        for dimension in dimensions:
            c_scope.insert_variable(dimension)
        return dimensions

    def _convert_native_value_argument(self, var, decision, func):
        """Pass a C-visible scalar value through the native call boundary."""
        if decision.kind is not ObjectKind.SCALAR:
            raise ValueError(f"Native value barrier only supports scalar arguments, got {decision.kind.value}")
        return self._build_numeric_argument(
            var,
            decision,
            needs_pointer_bridge=var.is_optional,
            direct_memory_handling=var.memory_handling,
        )

    def _convert_native_call_local_address_argument(self, var, decision, func):
        """Pass the address of bridge-owned call-local native storage."""
        if decision.kind is ObjectKind.STRING:
            return self._build_string_argument(
                var, decision, copy_back=decision.codegen_action is CodegenAction.COPY_IN_OUT
            )
        if decision.kind is ObjectKind.SCALAR and decision.codegen_action is CodegenAction.COPY_IN_OUT:
            return self._convert_native_scalar_replacement_argument(var, decision, func)
        if decision.kind is not ObjectKind.SCALAR:
            raise ValueError(
                f"Native call-local address barrier only supports scalar or string arguments, got {decision.kind.value}"
            )
        if (
            decision.codegen_action is CodegenAction.CALL_LOCAL_INPUT
            and decision.descriptor_boundary
            and decision.boundary_storage_mode in {StorageMode.HEAP, StorageMode.ALIAS}
        ):
            return self._convert_native_scalar_descriptor_input_argument(var, decision)
        return self._build_numeric_argument(
            var,
            decision,
            needs_pointer_bridge=var.is_optional,
            direct_memory_handling=StorageMode.STACK.value,
        )

    def _convert_native_scalar_descriptor_input_argument(self, var, decision):
        """Build a nullable call-local descriptor from a scalar C pointer."""
        name = var.name
        scope = self.scope
        scope.insert_symbol(name)
        bind_var = Variable(
            BindCPointer(),
            scope.get_new_name(f"bound_{name}"),
            is_argument=True,
            is_optional=False,
            memory_handling=StorageMode.ALIAS.value,
        )
        presence_var = None
        if self._uses_optional_scalar_descriptor_presence(var, decision):
            presence_var = Variable(
                BindCPointer(),
                scope.get_new_name(f"bound_{name}_present"),
                is_argument=True,
                is_optional=False,
                memory_handling=StorageMode.ALIAS.value,
            )
        input_var = var.clone(
            scope.get_new_name(f"{name}_input"),
            new_class=Variable,
            is_argument=False,
            is_optional=False,
            memory_handling=StorageMode.ALIAS.value,
        )
        descriptor_var = var.clone(
            scope.get_new_name(f"{name}_descriptor"),
            new_class=Variable,
            is_argument=False,
            is_optional=False,
            memory_handling=decision.boundary_storage_mode.value,
        )
        scope.insert_variable(bind_var)
        if presence_var is not None:
            scope.insert_variable(presence_var)
        scope.insert_variable(input_var)
        scope.insert_variable(descriptor_var)
        body = [C_F_Pointer(bind_var, input_var)]
        if decision.boundary_storage_mode is StorageMode.HEAP:
            body.append(If(IfSection(ArrayAssociated(input_var), [Assign(descriptor_var, input_var)])))
        else:
            body.append(AliasAssign(descriptor_var, input_var))
        if presence_var is not None:
            c_arg_var = Variable(
                BindCScalarDescriptorType(),
                scope.get_new_name(f"{name}_descriptor_input"),
                is_argument=True,
                shape=(convert_to_literal(2),),
            )
            scope.insert_symbolic_alias(IndexedElement(c_arg_var, convert_to_literal(0)), bind_var)
            scope.insert_symbolic_alias(IndexedElement(c_arg_var, convert_to_literal(1)), presence_var)
            return {
                "c_arg": BindCVariable(c_arg_var, var),
                "f_arg": descriptor_var,
                "body": body,
                "optional_presence_var": presence_var,
            }
        return {
            "c_arg": BindCVariable(bind_var, var),
            "f_arg": descriptor_var,
            "body": body,
        }

    @staticmethod
    def _uses_optional_scalar_descriptor_presence(var, decision):
        """Return whether a scalar descriptor needs supplied-vs-None tracking."""
        return bool(
            var.is_optional
            and decision.kind is ObjectKind.SCALAR
            and decision.descriptor_boundary
            and decision.nullable
        )

    def _convert_native_storage_address_argument(self, var, decision, func):
        """Pass caller/Python-backed storage through the native call boundary."""
        if decision.kind is ObjectKind.STRING:
            return self._build_string_storage_argument(var, decision)
        if decision.kind is not ObjectKind.SCALAR:
            raise ValueError(
                f"Native storage-address barrier only supports scalar arguments, got {decision.kind.value}"
            )
        return self._build_numeric_argument(
            var,
            decision,
            needs_pointer_bridge=True,
            direct_memory_handling=var.memory_handling,
        )

    def _convert_native_raw_address_argument(self, var, decision, func):
        """Pass a caller-supplied raw address through the native call boundary."""
        if decision.kind is ObjectKind.STRING:
            return self._convert_raw_string_argument(var, decision)
        if decision.kind is ObjectKind.NUMPY_ARRAY:
            return self._convert_raw_array_argument(var)
        if decision.kind is not ObjectKind.SCALAR:
            raise ValueError(f"Native raw-address barrier does not support {decision.kind.value} arguments")
        return self._build_numeric_argument(
            var,
            decision,
            needs_pointer_bridge=True,
            direct_memory_handling=var.memory_handling,
        )

    def _build_numeric_argument(self, var, decision, *, needs_pointer_bridge, direct_memory_handling):
        """Build the numeric bridge representation selected by policy dispatch."""
        name = var.name
        self.scope.insert_symbol(name)
        collisionless_name = self.scope.get_expected_name(name)
        if needs_pointer_bridge:
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
            f_arg = var.clone(
                collisionless_name,
                new_class=Variable,
                is_argument=True,
                memory_handling=direct_memory_handling,
            )
            new_var = f_arg
            body = []
        self.scope.insert_variable(f_arg)
        return {"c_arg": BindCVariable(new_var, var), "f_arg": f_arg, "body": body}

    def _convert_native_scalar_replacement_argument(self, var, decision, func):
        """Copy an immutable Python scalar into mutable native call storage."""
        if decision.descriptor_boundary:
            return self._convert_native_scalar_descriptor_input_argument(var, decision)
        name = var.name
        scope = self.scope
        scope.insert_symbol(name)
        input_var = var.clone(
            scope.get_expected_name(name),
            new_class=Variable,
            is_argument=True,
            is_optional=False,
            memory_handling=StorageMode.STACK.value,
        )
        local_var = var.clone(
            scope.get_new_name(f"{name}_mutable"),
            new_class=Variable,
            is_argument=False,
            is_optional=False,
            memory_handling=decision.boundary_storage_mode.value,
        )
        scope.insert_variable(input_var)
        scope.insert_variable(local_var)
        return {
            "c_arg": BindCVariable(input_var, var),
            "f_arg": local_var,
            "body": [Assign(local_var, input_var)],
        }

    def _convert_native_wrapper_address_argument(self, var, decision, func):
        """Pass a generated wrapper's native address through the native boundary."""
        name = var.name
        self.scope.insert_symbol(name)
        collisionless_name = self.scope.get_expected_name(name)
        f_arg = var.clone(
            collisionless_name,
            new_class=Variable,
            is_argument=False,
            is_optional=False,
            memory_handling=decision.boundary_storage_mode.value,
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

    def _convert_native_array_descriptor_argument(self, var, decision, func):
        """Pass a packed array descriptor through the native call boundary."""
        if decision.codegen_action is CodegenAction.COPY_IN_OUT:
            return self._convert_native_array_replacement_argument(var, decision, func)
        return self._convert_native_array_storage_argument(var, decision, func)

    def _convert_native_array_replacement_argument(self, var, decision, func):
        """Copy an immutable Python array into mutable native call storage."""
        name = var.name
        scope = self.scope
        scope.insert_symbol(name)
        rank = var.rank
        has_itemsize = self._is_character_array(var)
        base_shape = [
            scope.get_temporary_variable(
                NumpyInt64Type(),
                name=f"{name}_base_shape_{index + 1}",
                is_argument=True,
            )
            for index in range(rank)
        ]
        itemsize_var = (
            scope.get_temporary_variable(NumpyInt64Type(), name=f"{name}_itemsize", is_argument=True)
            if has_itemsize
            else None
        )
        bind_var = Variable(
            BindCPointer(),
            scope.get_new_name(f"bound_{name}"),
            is_argument=True,
            is_optional=False,
            memory_handling=StorageMode.ALIAS.value,
        )
        input_var = var.clone(
            scope.get_new_name(f"{name}_input"),
            is_argument=False,
            is_optional=False,
            memory_handling=StorageMode.ALIAS.value,
            new_class=Variable,
            fortran_character_length=itemsize_var if has_itemsize else var.fortran_character_length,
        )
        local_var = var.clone(
            scope.get_expected_name(name),
            is_argument=False,
            is_optional=False,
            memory_handling=decision.storage_mode.value,
            shape=tuple(base_shape),
            new_class=Variable,
        )
        for item in (bind_var, input_var, local_var):
            scope.insert_variable(item)

        prepare_local = []
        if decision.storage_mode is StorageMode.HEAP:
            alloc_var = (
                local_var.clone(local_var.name, new_class=Variable, fortran_character_length=itemsize_var)
                if has_itemsize
                else local_var
            )
            prepare_local.append(Allocate(alloc_var, shape=tuple(base_shape), status="unallocated"))
        prepare_local.append(Assign(local_var, input_var))
        pointer_shape = base_shape[::-1] if var.order == "C" else base_shape
        body = [
            If(
                IfSection(
                    IsNot(bind_var, NIL),
                    [C_F_Pointer(bind_var, input_var, pointer_shape), *prepare_local],
                )
            )
        ]
        descriptor_offset = 2 if has_itemsize else 1
        c_arg_var = Variable(
            BindCArrayType.get_new(rank, has_strides=False, has_itemsize=has_itemsize),
            scope.get_new_name(),
            is_argument=True,
            shape=(convert_to_literal(rank + descriptor_offset),),
        )
        scope.insert_symbolic_alias(IndexedElement(c_arg_var, convert_to_literal(0)), bind_var)
        if itemsize_var is not None:
            scope.insert_symbolic_alias(IndexedElement(c_arg_var, convert_to_literal(1)), itemsize_var)
        for index, shape_var in enumerate(base_shape):
            scope.insert_symbolic_alias(
                IndexedElement(c_arg_var, convert_to_literal(index + descriptor_offset)),
                shape_var,
            )
        return {"c_arg": BindCVariable(c_arg_var, var), "f_arg": local_var, "body": body}

    def _convert_native_array_storage_argument(self, var, decision, func):
        """Convert array argument for the current wrapper."""
        name = var.name
        scope = self.scope
        scope.insert_symbol(name)
        collisionless_name = scope.get_expected_name(name)
        rank = var.rank
        order = var.order
        allows_strides = var.class_type.allows_strides
        has_itemsize = self._is_character_array(var)
        bind_var = Variable(
            BindCPointer(),
            scope.get_new_name(f"bound_{name}"),
            is_argument=True,
            is_optional=False,
            memory_handling="alias",
        )

        if self._is_assumed_rank_array(var):
            return self._convert_assumed_rank_array_argument(var, collisionless_name, bind_var)

        base_shape = [
            scope.get_temporary_variable(NumpyInt64Type(), name=f"{name}_base_shape_{i + 1}", is_argument=True)
            for i in range(rank)
        ]
        itemsize_var = (
            scope.get_temporary_variable(NumpyInt64Type(), name=f"{name}_itemsize", is_argument=True)
            if has_itemsize
            else None
        )
        arg_var = var.clone(
            collisionless_name,
            is_argument=False,
            is_optional=False,
            memory_handling="alias",
            new_class=Variable,
            fortran_character_length=itemsize_var if has_itemsize else var.fortran_character_length,
        )
        pointer_shape = base_shape[::-1] if order == "C" else base_shape
        scope.insert_variable(arg_var)
        scope.insert_variable(bind_var)

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

        body = [C_F_Pointer(bind_var, arg_var, pointer_shape)]
        descriptor_offset = 2 if has_itemsize else 1

        c_arg_var = Variable(
            BindCArrayType.get_new(rank, has_strides=allows_strides, has_itemsize=has_itemsize),
            scope.get_new_name(),
            is_argument=True,
            shape=(convert_to_literal(rank * 3 + descriptor_offset if allows_strides else rank + descriptor_offset),),
        )

        scope.insert_symbolic_alias(IndexedElement(c_arg_var, convert_to_literal(0)), bind_var)
        if itemsize_var is not None:
            scope.insert_symbolic_alias(IndexedElement(c_arg_var, convert_to_literal(1)), itemsize_var)
        for i, s in enumerate(base_shape):
            scope.insert_symbolic_alias(IndexedElement(c_arg_var, convert_to_literal(i + descriptor_offset)), s)
        if allows_strides:
            for i, s in enumerate(ubound):
                scope.insert_symbolic_alias(
                    IndexedElement(c_arg_var, convert_to_literal(i + rank + descriptor_offset)), s
                )
            for i, s in enumerate(stride):
                scope.insert_symbolic_alias(
                    IndexedElement(c_arg_var, convert_to_literal(i + 2 * rank + descriptor_offset)),
                    s,
                )

            start = convert_to_literal(1)  # C_F_Pointer leads to default Fortran lbound
            indexes = [
                Slice(start, Add(stop, convert_to_literal(1)), step) for step, stop in zip(stride, ubound, strict=False)
            ]
            f_arg = IndexedElement(arg_var, *indexes)
        else:
            f_arg = arg_var

        return {"c_arg": BindCVariable(c_arg_var, var), "f_arg": f_arg, "body": body}

    def _convert_raw_array_argument(self, var):
        """Associate a caller-supplied raw data address with a Fortran array pointer."""
        name = var.name
        scope = self.scope
        scope.insert_symbol(name)
        collisionless_name = scope.get_expected_name(name)
        shape = self._raw_array_pointer_shape(var)
        pointer_shape = shape[::-1] if var.order == "C" else shape
        bind_var = Variable(
            BindCPointer(),
            scope.get_new_name(f"bound_{name}"),
            is_argument=True,
            is_optional=False,
            memory_handling="alias",
        )
        f_arg = var.clone(
            collisionless_name,
            is_argument=False,
            is_optional=False,
            memory_handling="alias",
            new_class=Variable,
        )
        scope.insert_variable(bind_var)
        scope.insert_variable(f_arg)
        return {
            "c_arg": BindCVariable(bind_var, var),
            "f_arg": f_arg,
            "body": [C_F_Pointer(bind_var, f_arg, pointer_shape)],
        }

    @staticmethod
    def _raw_array_pointer_shape(var):
        """Return the fixed or visible extents needed to associate a raw pointer."""
        shape = tuple(var.alloc_shape or ())
        if len(shape) != var.rank or any(item is None for item in shape):
            raise ValueError(
                f"Raw array address argument {var.name!r} requires a fixed or visible extent for every axis"
            )
        return list(shape)

    def _convert_assumed_rank_array_argument(self, var, collisionless_name, bind_var):
        """Convert assumed rank array argument for the current wrapper."""
        name = var.name
        scope = self.scope
        rank = _MAX_SUPPORTED_ASSUMED_RANK
        allows_strides = var.class_type.allows_strides
        scope.insert_variable(bind_var)
        rank_var = scope.get_temporary_variable(NumpyInt64Type(), name=f"{name}_rank", is_argument=True)
        shape_vars = [
            scope.get_temporary_variable(NumpyInt64Type(), name=f"{name}_base_shape_{i + 1}", is_argument=True)
            for i in range(rank)
        ]
        ubound_vars = (
            [
                scope.get_temporary_variable(NumpyInt64Type(), name=f"{name}_ubound_{i + 1}", is_argument=True)
                for i in range(rank)
            ]
            if allows_strides
            else []
        )
        stride_vars = (
            [
                scope.get_temporary_variable(NumpyInt64Type(), name=f"{name}_stride_{i + 1}", is_argument=True)
                for i in range(rank)
            ]
            if allows_strides
            else []
        )
        rank_vars = {}
        for actual_rank in range(1, rank + 1):
            rank_type = var.class_type.switch_rank(actual_rank, "F")
            rank_vars[actual_rank] = Variable(
                rank_type,
                scope.get_new_name(f"{collisionless_name}_rank{actual_rank}"),
                is_argument=False,
                is_optional=False,
                memory_handling="alias",
            )
            scope.insert_variable(rank_vars[actual_rank])

        descriptor_type = BindCArrayType.get_new(rank, has_strides=allows_strides, has_rank=True)
        c_arg_var = Variable(
            descriptor_type,
            scope.get_new_name(),
            is_argument=True,
            shape=(convert_to_literal(len(descriptor_type)),),
        )
        scope.insert_symbolic_alias(IndexedElement(c_arg_var, convert_to_literal(0)), bind_var)
        scope.insert_symbolic_alias(IndexedElement(c_arg_var, convert_to_literal(1)), rank_var)
        offset = 2
        for i, s in enumerate(shape_vars):
            scope.insert_symbolic_alias(IndexedElement(c_arg_var, convert_to_literal(i + offset)), s)
        if allows_strides:
            for i, s in enumerate(ubound_vars):
                scope.insert_symbolic_alias(IndexedElement(c_arg_var, convert_to_literal(i + rank + offset)), s)
            for i, s in enumerate(stride_vars):
                scope.insert_symbolic_alias(IndexedElement(c_arg_var, convert_to_literal(i + 2 * rank + offset)), s)

        placeholder = var.clone(
            collisionless_name,
            is_argument=False,
            is_optional=False,
            memory_handling="alias",
            new_class=Variable,
        )
        return {
            "c_arg": BindCVariable(c_arg_var, var),
            "f_arg": placeholder,
            "body": [],
            "assumed_rank": {
                "allows_strides": allows_strides,
                "bind_var": bind_var,
                "rank_var": rank_var,
                "rank_vars": rank_vars,
                "shape_vars": shape_vars,
                "stride_vars": stride_vars,
                "ubound_vars": ubound_vars,
            },
        }

    def _convert_raw_string_argument(self, var, decision):
        """Associate a caller-supplied raw character address with fixed string storage."""
        name = var.name
        scope = self.scope
        scope.insert_symbol(name)
        fixed_len = var.alloc_shape[0]
        if fixed_len is None:
            raise ValueError(f"Raw string address argument {name!r} requires a fixed String[n] length")
        bind_var = Variable(
            BindCPointer(),
            scope.get_new_name(f"bound_{name}"),
            is_argument=True,
            is_optional=False,
            memory_handling="alias",
        )
        array_var = Variable(
            NumpyNDArrayType.get_new(CharType(), 1, None),
            scope.get_new_name(name),
            memory_handling="alias",
        )
        f_arg = var.clone(
            scope.get_expected_name(name),
            is_argument=False,
            is_optional=False,
            memory_handling="stack",
            new_class=Variable,
        )
        scope.insert_variable(bind_var)
        scope.insert_variable(array_var)
        scope.insert_variable(f_arg)
        body = [
            C_F_Pointer(bind_var, array_var, (fixed_len,)),
            Assign(f_arg, FortranTransfer(array_var, f_arg)),
        ]
        post_body = []
        if decision.mutates_native:
            raw_slice = IndexedElement(array_var, Slice(None, Add(fixed_len, convert_to_literal(1))))
            post_body = [Assign(raw_slice, FortranTransfer(f_arg, raw_slice, fixed_len))]
        return {
            "c_arg": BindCVariable(bind_var, var),
            "f_arg": f_arg,
            "body": body,
            "post_body": post_body,
        }

    def _build_string_storage_argument(self, var, decision):
        """Associate caller-provided rank-0 NumPy bytes storage with fixed string storage."""
        name = var.name
        scope = self.scope
        scope.insert_symbol(name)
        fixed_len = var.alloc_shape[0]
        if fixed_len is None:
            raise ValueError(f"String storage argument {name!r} requires a fixed String[n] length")
        bind_var = Variable(
            BindCPointer(),
            scope.get_new_name(f"bound_{name}"),
            is_argument=True,
            is_optional=False,
            memory_handling="alias",
        )
        array_var = Variable(
            NumpyNDArrayType.get_new(CharType(), 1, None),
            scope.get_new_name(name),
            memory_handling="alias",
        )
        f_arg = var.clone(
            scope.get_expected_name(name),
            is_argument=False,
            is_optional=False,
            memory_handling="stack",
            new_class=Variable,
        )
        scope.insert_variable(bind_var)
        scope.insert_variable(array_var)
        scope.insert_variable(f_arg)
        body = [
            C_F_Pointer(bind_var, array_var, (fixed_len,)),
            Assign(f_arg, FortranTransfer(array_var, f_arg)),
        ]
        post_body = []
        if decision.mutates_native:
            storage_slice = IndexedElement(array_var, Slice(None, Add(fixed_len, convert_to_literal(1))))
            post_body = [Assign(storage_slice, FortranTransfer(f_arg, storage_slice, fixed_len))]
        return {
            "c_arg": BindCVariable(bind_var, var),
            "f_arg": f_arg,
            "body": body,
            "post_body": post_body,
        }

    def _build_string_argument(self, var, decision, *, copy_back):
        """Build string argument storage selected by strict policy dispatch."""
        name = var.name
        scope = self.scope
        scope.insert_symbol(name)
        collisionless_name = scope.get_expected_name(name)
        rank = var.rank
        pointer_type = BindCPointer() if decision.mutates_native else FinalType.get_new(BindCPointer())
        bind_var = Variable(
            pointer_type,
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
        has_fixed_length = fixed_len is not None
        buffer_extent = Add(fixed_len if has_fixed_length else shape_var, convert_to_literal(1))
        pointer_extent = buffer_extent if copy_back else fixed_len if has_fixed_length else buffer_extent
        if has_fixed_length:
            fixed_var = var.clone(
                collisionless_name,
                is_argument=False,
                is_optional=False,
                memory_handling="stack",
                new_class=Variable,
            )
            scope.insert_variable(fixed_var)
            body = [
                C_F_Pointer(bind_var, array_var, (pointer_extent,)),
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
                C_F_Pointer(bind_var, array_var, (buffer_extent,)),
                Assign(arg_var, FortranTransfer(array_var, arg_var)),
            ]
            f_arg = arg_var

        post_body = []
        absent_body = []
        result_bind_var = None
        if copy_back:
            result_bind_var = Variable(
                BindCPointer(),
                scope.get_new_name(f"returned_{name}"),
                memory_handling="alias",
                ownership_decision=var.ownership_decision,
            )
            payload_slice = IndexedElement(array_var, Slice(None, buffer_extent))
            post_body = [
                Assign(payload_slice, FortranTransfer(f_arg, payload_slice, shape_var)),
                Assign(IndexedElement(array_var, buffer_extent), C_NULL_CHAR()),
                Assign(result_bind_var, bind_var),
            ]
            if var.is_optional:
                absent_body = [Assign(result_bind_var, NIL)]

        c_arg_var = Variable(
            BindCArrayType.get_new(rank, has_strides=False),
            scope.get_new_name(),
            is_argument=True,
            shape=(convert_to_literal(2),),
        )

        scope.insert_symbolic_alias(IndexedElement(c_arg_var, convert_to_literal(0)), bind_var)
        scope.insert_symbolic_alias(IndexedElement(c_arg_var, convert_to_literal(1)), shape_var)

        return {
            "c_arg": BindCVariable(c_arg_var, var),
            "f_arg": f_arg,
            "body": body,
            "post_body": post_body,
            "absent_body": absent_body,
            "bind_var": bind_var,
            "result_bind_var": result_bind_var,
        }

    def _convert_result(self, orig_var, orig_func_scope):
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
        if orig_var.array_interop_policy is not None:
            return self._ARRAY_INTEROP_POLICY_DISPATCHER.dispatch(
                self,
                orig_var,
                orig_var.array_interop_policy,
                "result",
                orig_func_scope,
            )
        return self._bridge_non_array_result(orig_var, orig_func_scope)

    def _bridge_data_buffer_result(self, subject, _policy, orig_func_scope):
        """Convert an ordinary array result through the data-buffer ABI."""
        return self._bridge_non_array_result(subject, orig_func_scope)

    def _bridge_descriptor_result(self, subject, policy, orig_func_scope):
        """Convert a native array handle result through descriptor ABI."""
        self._validate_descriptor_array_interop_policy(subject, policy)
        return self._NATIVE_ARRAY_HANDLE_DISPATCHER.dispatch(
            self,
            subject,
            subject.native_array_handle_policy,
            orig_func_scope,
        )

    def _bridge_non_array_result(self, orig_var, orig_func_scope):
        """Convert a function result without native descriptor-handle routing."""
        return self._RESULT_POLICY_DISPATCHER.dispatch(self, orig_var, orig_func_scope)

    def _convert_scalar_result(self, orig_var, decision, orig_func_scope):
        """Convert scalar result for the current wrapper."""
        if decision.descriptor_boundary and decision.nullable:
            return self._build_snapshot_copy_scalar_result(
                orig_var,
                self._nullable_scalar_status_func_for_storage(decision.boundary_storage_mode),
                source_storage_mode=decision.boundary_storage_mode,
            )
        name = orig_var.name
        self.scope.insert_symbol(name)
        local_var = orig_var.clone(
            self.scope.get_expected_name(name),
            new_class=Variable,
            is_argument=False,
            is_optional=False,
            memory_handling=(
                StorageMode.STACK.value
                if decision.native_barrier_action is NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS
                else orig_var.memory_handling
            ),
        )
        return {
            "body": [],
            "c_result": BindCVariable(local_var, orig_var),
            "f_result": local_var,
        }

    def _convert_snapshot_scalar_result(self, orig_var, decision, orig_func_scope):
        """Copy a pointer scalar result into detached Python-visible storage."""
        return self._build_snapshot_copy_scalar_result(
            orig_var,
            self._nullable_scalar_status_func(decision),
            source_storage_mode=decision.storage_mode,
        )

    def _convert_owned_custom_type_result(self, orig_var, decision, orig_func_scope):
        """Convert an owned custom result through native value storage."""
        return self._convert_custom_type_result(
            orig_var,
            decision,
            orig_func_scope,
            decision.storage_mode,
            borrowed=False,
        )

    def _convert_borrowed_custom_type_result(self, orig_var, decision, orig_func_scope):
        """Convert a borrowed custom result through alias boundary storage."""
        return self._convert_custom_type_result(
            orig_var,
            decision,
            orig_func_scope,
            decision.boundary_storage_mode,
            borrowed=True,
        )

    def _convert_custom_type_result(
        self,
        orig_var,
        decision,
        orig_func_scope,
        local_storage_mode,
        *,
        borrowed,
    ):
        """Build the concrete custom result representation selected by policy."""
        name = orig_var.name
        scope = self.scope
        scope.insert_symbol(name)
        memory_handling = local_storage_mode.value
        local_var = orig_var.clone(
            scope.get_expected_name(name),
            new_class=Variable,
            memory_handling=memory_handling,
            is_argument=False,
            is_optional=False,
        )
        # Allocatable is not returned so it must appear in local scope
        scope.insert_variable(local_var, name)

        # Create the C-compatible data pointer
        bind_var = Variable(BindCPointer(), scope.get_new_name("bound_" + name), memory_handling="alias")

        if borrowed:
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

    def _convert_array_result(self, orig_var, decision, orig_func_scope):
        """Convert array result for the current wrapper."""
        name = orig_var.name
        scope = self.scope
        scope.insert_symbol(name)
        memory_handling = decision.boundary_storage_mode.value

        shape = orig_var.shape if memory_handling == "stack" else None

        # Allocatable is not returned so it must appear in local scope
        local_var = orig_var.clone(
            scope.get_expected_name(name),
            new_class=Variable,
            memory_handling=memory_handling,
            shape=shape,
            is_argument=False,
            is_optional=False,
        )
        scope.insert_variable(local_var, name)

        result = self._NDARRAY_RESULT_DISPATCHER.dispatch(
            self,
            orig_var,
            name,
            local_var,
        )

        result["f_result"] = local_var

        return result

    def _convert_string_result(self, orig_var, decision, orig_func_scope):
        """Convert string result for the current wrapper."""
        name = orig_var.name
        scope = self.scope
        scope.insert_symbol(name)
        memory_handling = decision.boundary_storage_mode.value

        # Allocatable is not returned so it must appear in local scope
        local_var = orig_var.clone(
            scope.get_expected_name(name),
            new_class=Variable,
            memory_handling=memory_handling,
            is_argument=False,
            is_optional=False,
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
            If(
                IfSection(
                    IsNot(bind_var, NIL),
                    [
                        C_F_Pointer(bind_var, ptr_var, [shape_var]),
                        Assign(ptr_var, FortranTransfer(local_var, ptr_var, shape_var)),
                        Assign(IndexedElement(ptr_var, shape_var), C_NULL_CHAR()),
                    ],
                )
            ),
        ]

        return {
            "c_result": BindCVariable(bind_var, orig_var),
            "body": body,
            "f_array": ptr_var,
            "f_result": local_var,
        }

    # ------------------------------------------------------------------
    # Node builders
    # ------------------------------------------------------------------

    def _build_snapshot_copy_scalar_result(
        self,
        orig_var,
        status_func=None,
        source_expr=None,
        source_storage_mode=None,
    ):
        """Build snapshot copy scalar result nodes."""
        name = orig_var.name
        scope = self.scope
        local_storage = source_storage_mode or StorageMode.ALIAS
        if source_expr is None:
            scope.insert_symbol(name)
            source_expr = orig_var.clone(
                scope.get_expected_name(name),
                new_class=Variable,
                is_argument=False,
                memory_handling=local_storage.value,
                is_optional=False,
            )
            scope.insert_variable(source_expr)
        bind_var = Variable(BindCPointer(), scope.get_new_name(f"bound_{name}"), memory_handling="alias")
        copy_var = orig_var.clone(
            scope.get_new_name(f"{name}_copy"),
            new_class=Variable,
            is_argument=False,
            memory_handling="alias",
            is_optional=False,
        )
        size_var = orig_var.clone(
            scope.get_new_name(f"{name}_element"),
            new_class=Variable,
            is_argument=False,
            memory_handling="stack",
            is_optional=False,
        )
        for variable in (copy_var, size_var):
            scope.insert_variable(variable)
        status = status_func or ArrayAssociated
        body = [self._nullable_scalar_snapshot_if(source_expr, status, bind_var, copy_var, size_var)]
        return {
            "body": body,
            "c_result": BindCVariable(bind_var, orig_var),
            "f_result": source_expr,
            "bind_var": bind_var,
            "copy_var": copy_var,
            "size_var": size_var,
        }

    @staticmethod
    def _nullable_scalar_snapshot_if(source_expr, status_func, bind_var, copy_var, size_var):
        """Build a nullable scalar snapshot branch from a completed descriptor policy."""
        copy_body = [
            Assign(bind_var, c_malloc(BindCSizeOf(size_var))),
            If(
                IfSection(
                    IsNot(bind_var, NIL),
                    [C_F_Pointer(bind_var, copy_var), Assign(copy_var, source_expr)],
                )
            ),
        ]
        return If(
            IfSection(status_func(source_expr), copy_body),
            IfSection(convert_to_literal(True), [Assign(bind_var, NIL)]),
        )

    @staticmethod
    def _nullable_scalar_status_func(decision):
        """Return the native descriptor presence check selected by completed policy."""
        return FortranToCBridgeGenerator._nullable_scalar_status_func_for_storage(decision.storage_mode)

    @staticmethod
    def _nullable_scalar_status_func_for_storage(storage_mode):
        """Return the presence check for one completed descriptor storage mode."""
        if storage_mode is StorageMode.HEAP:
            return ArrayAllocated
        if storage_mode is StorageMode.ALIAS:
            return ArrayAssociated
        value = getattr(storage_mode, "value", storage_mode)
        raise ValueError(f"Nullable scalar snapshot requires heap or alias storage, got {value}")

    def _build_snapshot_copy_array_result(self, orig_var, _decision, name, local_var):
        """Build snapshot copy array result nodes."""
        return self._get_pointer_snapshot_bind_c_array(name, orig_var, local_var)

    def _build_borrowed_array_result(self, orig_var, _decision, name, local_var):
        """Build borrowed array result nodes."""
        return self._get_bind_c_array(name, orig_var, local_var.shape, local_var, source_var=local_var)

    def _build_copy_return_array_result(self, orig_var, decision, name, local_var):
        """Dispatch copy-return emission from completed boundary storage."""
        try:
            handler_name = self._COPY_RETURN_ARRAY_BY_STORAGE[decision.boundary_storage_mode]
        except KeyError:
            raise ValueError(
                f"No array copy-return handler for completed storage {decision.boundary_storage_mode.value!r}"
            ) from None
        return getattr(self, handler_name)(orig_var, decision, name, local_var)

    def _build_stack_copy_return_array_result(self, orig_var, _decision, name, local_var):
        """Copy a fixed-shape native result into Python-owned storage."""
        result = self._get_bind_c_array(name, orig_var, local_var.shape, source_var=local_var)
        result["body"].append(self._array_result_copy_section(result, local_var))
        return result

    def _build_heap_copy_return_array_result(self, orig_var, _decision, name, local_var):
        """Copy an allocated native result and release its native storage."""
        copy_shape = tuple(ArrayShapeElement(local_var, convert_to_literal(index)) for index in range(local_var.rank))
        result = self._get_bind_c_array(name, orig_var, copy_shape, source_var=local_var)
        result["body"].append(self._array_result_copy_section(result, local_var))
        allocated_body = [*result["body"], Deallocate(local_var)]
        unallocated_body = [
            Assign(result["bind_var"], NIL),
            *[Assign(shape_var, convert_to_literal(0, dtype=NumpyInt32Type())) for shape_var in result["shape_vars"]],
        ]
        result["body"] = [
            If(
                IfSection(ArrayAllocated(local_var), allocated_body),
                IfSection(convert_to_literal(True), unallocated_body),
            )
        ]
        return result

    def _build_scalar_replacement_result(self, orig_var, decision, generated_arg):
        """Return the mutable native scalar temporary as a replacement value."""
        local_var = generated_arg["f_arg"].value
        if decision.descriptor_boundary and decision.nullable:
            return self._build_snapshot_copy_scalar_result(
                orig_var,
                self._nullable_scalar_status_func_for_storage(decision.boundary_storage_mode),
                source_expr=local_var,
                source_storage_mode=decision.boundary_storage_mode,
            )
        return {
            "c_result": BindCVariable(local_var, orig_var),
            "body": [],
            "f_result": local_var,
        }

    def _build_array_replacement_result(self, orig_var, decision, generated_arg):
        """Copy a mutable native array temporary into Python-owned result storage."""
        local_var = generated_arg["f_arg"].value
        result_shape = (
            tuple(ArrayShapeElement(local_var, convert_to_literal(index)) for index in range(local_var.rank))
            if decision.storage_mode is StorageMode.HEAP
            else local_var.shape
        )
        result = self._get_bind_c_array(
            orig_var.name,
            orig_var,
            result_shape,
            source_var=local_var,
        )
        result["body"].append(self._array_result_copy_section(result, local_var))
        if decision.storage_mode is StorageMode.HEAP:
            allocated_body = [*result["body"], Deallocate(local_var)]
            unallocated_body = [
                Assign(result["bind_var"], NIL),
                *[
                    Assign(shape_var, convert_to_literal(0, dtype=NumpyInt32Type()))
                    for shape_var in result["shape_vars"]
                ],
            ]
            result["body"] = [
                If(
                    IfSection(ArrayAllocated(local_var), allocated_body),
                    IfSection(convert_to_literal(True), unallocated_body),
                )
            ]
        result["f_result"] = local_var
        return result

    @staticmethod
    def _build_string_replacement_result(orig_var, decision, generated_arg):
        """Build string replacement result nodes."""
        return {
            "c_result": BindCVariable(generated_arg["result_bind_var"], orig_var),
            "body": [],
            "f_result": generated_arg["f_arg"].value,
        }

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _array_result_copy_section(self, result, source_var):
        """Copy a native array into the returned C-compatible result buffer."""
        if self._is_character_array(source_var):
            copy_expr = FortranTransfer(source_var, result["f_array"], result["byte_count"])
        else:
            copy_expr = source_var
        return If(IfSection(IsNot(result["bind_var"], NIL), [Assign(result["f_array"], copy_expr)]))

    @staticmethod
    def _is_character_array(var):
        """Return whether ``var`` stores fixed-width character array elements."""
        return isinstance(var.class_type, NumpyNDArrayType) and isinstance(var.dtype, CharType)

    @staticmethod
    def _has_optional_arguments(func: FunctionDef) -> bool:
        """Return whether has optional arguments."""
        return any(getattr(argument.var, "is_optional", False) for argument in func.arguments)

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
            A list containing the dictionaries returned by _convert_argument.

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
        optional_block = self._optional_argument_presence_block(func, generated_args, results, handled)
        if optional_block is not None:
            return optional_block
        return self._get_required_function_def_body(func, generated_args, results)

    def _optional_argument_presence_block(self, func, generated_args, results, handled):
        """Build the next optional-argument presence branch, if any remains."""
        next_optional_arg = self._next_optional_generated_arg(generated_args, handled)
        if next_optional_arg is None:
            return None

        args = generated_args.copy()
        optional_var = self._optional_presence_var(next_optional_arg)
        handled += (next_optional_arg,)
        true_section = IfSection(
            IsNot(optional_var, NIL),
            self._get_function_def_body(func, args, results, handled),
        )
        args.remove(next_optional_arg)
        false_section = IfSection(
            convert_to_literal(True),
            [
                *next_optional_arg.get("absent_body", ()),
                *self._get_function_def_body(func, args, results, handled),
            ],
        )
        return [If(true_section, false_section)]

    @staticmethod
    def _next_optional_generated_arg(generated_args, handled):
        """Return the next generated optional argument that has not been branched."""
        for generated_arg in generated_args:
            if generated_arg["c_arg"] is None or generated_arg in handled:
                continue
            original_var = getattr(generated_arg["c_arg"].var, "original_var", generated_arg["c_arg"].var)
            if getattr(original_var, "is_optional", False):
                return generated_arg
        return None

    def _optional_presence_var(self, generated_arg):
        """Return the C-side value used to test optional argument presence."""
        optional_var = generated_arg.get("optional_presence_var") or generated_arg["c_arg"].var
        optional_var = getattr(optional_var, "new_var", optional_var)
        if isinstance(optional_var.class_type, BindCArrayType):
            return self.scope.collect_tuple_element(IndexedElement(optional_var, convert_to_literal(0)))
        return optional_var

    def _get_required_function_def_body(self, func, generated_args, results):
        """Build the body once all optional arguments have been resolved."""
        args = [a["f_arg"] for a in generated_args]
        body = [line for a in generated_args for line in a["body"]]
        post_body = [line for a in generated_args for line in a.get("post_body", ())]

        selected, native_name, args = self._selected_native_call_args(func, args)
        if re.sub(r"\s+", "", native_name).casefold() == "assignment(=)":
            lhs, rhs = func.native_arguments(selected, args)
            return [*body, Assign(lhs.value, rhs.value), *post_body]

        if getattr(func, "is_external", False):
            args = self._positional_native_arguments(args)

        selected_func = selected or func
        if len(results) == 1 and self._uses_allocatable_function_result_helper(selected_func, results[0]):
            helper = self._allocatable_function_result_helper(results[0])
            self._additional_functions.append(helper)
            return [*body, helper(func(*args), results[0]), *post_body]

        if any(arg.get("assumed_rank") for arg in generated_args):
            return [*body, *self._assumed_rank_dispatch(func, generated_args, results), *post_body]

        return [*body, *self._native_call_body(func, args, results), *post_body]

    @staticmethod
    def _selected_native_call_args(func, args):
        """Resolve overload calls and normalize their native argument order."""
        if not isinstance(func, FunctionOverloadSet):
            return None, "", args
        selected = func.point(args)
        native_name = func.native_name_for(selected)
        return selected, native_name, FortranToCBridgeGenerator._positional_native_arguments(args)

    @staticmethod
    def _positional_native_arguments(args):
        """Return native call arguments without generated bridge keywords."""
        return [FunctionCallArgument(arg.value) for arg in args]

    @staticmethod
    def _native_call_body(func, args, results):
        """Handle native call body for the current generation context."""
        if len(results) == 1:
            res = results[0]
            func_call = AliasAssign(res, func(*args)) if res.is_alias else Assign(res, func(*args))
        else:
            func_call = Assign(results, func(*args))
        return [func_call]

    def _assumed_rank_dispatch(self, func, generated_args, results):
        """Handle assumed rank dispatch for the current generation context."""
        dispatch_args = [arg for arg in generated_args if arg.get("assumed_rank")]
        return self._assumed_rank_dispatch_level(func, generated_args, results, dispatch_args, {}, 0)

    def _assumed_rank_dispatch_level(self, func, generated_args, results, dispatch_args, replacements, index):
        """Handle assumed rank dispatch level for the current generation context."""
        if index == len(dispatch_args):
            args = [
                self._replacement_function_argument(arg["f_arg"], replacements[arg["f_arg"].value])
                if arg.get("assumed_rank")
                else arg["f_arg"]
                for arg in generated_args
            ]
            return self._native_call_body(func, args, results)

        dispatch_arg = dispatch_args[index]
        info = dispatch_arg["assumed_rank"]
        sections = []
        for rank in range(1, _MAX_SUPPORTED_ASSUMED_RANK + 1):
            rank_var = info["rank_vars"][rank]
            f_arg = self._assumed_rank_argument_view(info, rank_var, rank)
            replacements[dispatch_arg["f_arg"].value] = f_arg
            nested_body = self._assumed_rank_dispatch_level(
                func,
                generated_args,
                results,
                dispatch_args,
                replacements,
                index + 1,
            )
            del replacements[dispatch_arg["f_arg"].value]
            sections.append(
                CaseSection(
                    convert_to_literal(rank, dtype=NumpyInt64Type()),
                    [
                        C_F_Pointer(info["bind_var"], rank_var, info["shape_vars"][:rank]),
                        *nested_body,
                    ],
                )
            )
        sections.append(CaseSection(None, [Return(None)]))
        return [SelectCase(info["rank_var"], *sections)]

    @staticmethod
    def _replacement_function_argument(original, value):
        """Handle replacement function argument for the current generation context."""
        return FunctionCallArgument(value, keyword=original.keyword)

    @staticmethod
    def _assumed_rank_argument_view(info, rank_var, rank):
        """Handle assumed rank argument view for the current generation context."""
        if not info["allows_strides"]:
            return rank_var
        start = convert_to_literal(1)
        indexes = [
            Slice(start, Add(stop, convert_to_literal(1)), step)
            for step, stop in zip(info["stride_vars"][:rank], info["ubound_vars"][:rank], strict=False)
        ]
        return IndexedElement(rank_var, *indexes)

    @classmethod
    def _uses_allocatable_function_result_helper(cls, func, result):
        """Return whether uses allocatable function result helper."""
        func_result = getattr(getattr(func, "results", None), "var", NIL)
        result_decision = ownership_decision_for_codegen_variable(result)
        func_result_decision = ownership_decision_for_codegen_variable(func_result) if func_result is not NIL else None
        if (
            result_decision.kind is ObjectKind.SCALAR
            and result_decision.codegen_action is CodegenAction.SNAPSHOT_COPY
            and result_decision.storage_mode is StorageMode.HEAP
            and func_result_decision is not None
        ):
            return (
                func_result_decision.kind is ObjectKind.SCALAR
                and func_result_decision.codegen_action is CodegenAction.SNAPSHOT_COPY
                and func_result_decision.storage_mode is StorageMode.HEAP
            )
        return (
            result.is_ndarray
            and cls._is_allocatable_copy_return_result(result)
            and func_result is not NIL
            and getattr(func_result, "is_ndarray", False)
            and cls._is_allocatable_copy_return_result(func_result)
        )

    def _allocatable_function_result_helper(self, result):
        """Handle allocatable function result helper for the current generation context."""
        helper_name = self.scope.get_new_name(f"x2py_collect_{result.name}")
        helper_scope = self.scope.new_child_scope(helper_name, "function")
        value = result.clone(
            helper_scope.get_new_name(f"{result.name}_value"),
            new_class=Variable,
            is_argument=False,
            is_optional=False,
        )
        target = result.clone(
            helper_scope.get_new_name(f"{result.name}_target"),
            new_class=Variable,
            is_argument=False,
            is_optional=False,
        )
        value_arg = FunctionDefArgument(value)
        value_arg.make_const()
        target_arg = FunctionDefArgument(target)
        return FunctionDef(
            helper_name,
            [value_arg, target_arg],
            [If(IfSection(ArrayAllocated(value), [Assign(target, value)]))],
            scope=helper_scope,
        )

    def _direct_bind_c_function(self, expr):
        """Handle direct bind c function for the current generation context."""
        external_name = expr.bind_c_external_name
        func = BindCFunctionDef(
            external_name,
            expr.arguments,
            [],
            expr.results,
            is_header=True,
            scope=expr.scope,
            original_function=expr,
            docstring=expr.docstring,
            result_pointer_map=expr.result_pointer_map,
            bind_c_external_name=external_name,
        )
        self.scope.insert_symbol(external_name, object_type="function")
        self.scope.insert_function(func, external_name)
        return func

    @classmethod
    def _can_call_existing_bind_c_directly(cls, expr):
        """Return whether can call existing bind c directly."""
        if not expr.bind_c_external_name or expr.is_private or not expr.is_semantic:
            return False
        if expr.is_external or cls._has_optional_arguments(expr):
            return False
        if any(argument.bound_argument for argument in expr.arguments):
            return False
        if not cls._is_direct_bind_c_result(expr.results.var):
            return False
        return all(cls._is_direct_bind_c_argument(argument.var) for argument in expr.arguments)

    @staticmethod
    def _is_direct_bind_c_result(var):
        """Return whether is direct bind c result."""
        if var is NIL:
            return True
        return var.rank == 0 and isinstance(var.class_type, FixedSizeNumericType)

    @staticmethod
    def _is_direct_bind_c_argument(var):
        """Return whether is direct bind c argument."""
        return (
            var.rank == 0
            and var.memory_handling == "stack"
            and getattr(var, "passes_by_value", False)
            and isinstance(var.class_type, FixedSizeNumericType)
        )

    @staticmethod
    def _is_allocatable_copy_return_result(var):
        """Return whether is allocatable copy return result."""
        decision = ownership_decision_for_codegen_variable(var)
        return FortranToCBridgeGenerator._ALLOCATABLE_RESULT_HELPER_DISPATCHER.dispatch_decision(
            FortranToCBridgeGenerator, var, decision
        )

    @staticmethod
    def _uses_heap_allocatable_result_helper(var, decision):
        """Return whether a copy-return array result needs allocatable helper collection."""
        return decision.storage_mode is StorageMode.HEAP

    @staticmethod
    def _skips_allocatable_result_helper(_var, _decision):
        """Return whether a non-copy-return array result skips allocatable helper collection."""
        return False

    @staticmethod
    def _is_assumed_rank_array(var):
        """Return whether is assumed rank array."""
        return bool(getattr(var, "assumed_rank", False) and var.is_ndarray)

    def _pack_function_results(self, result_infos):
        """Handle pack function results for the current generation context."""
        result_type = BindCResultTupleType.get_new(tuple(info["c_result"].class_type for info in result_infos))
        result_var = Variable(
            result_type,
            self.scope.get_new_name("results"),
            shape=(convert_to_literal(len(result_infos)),),
            is_temp=True,
        )
        for index, info in enumerate(result_infos):
            self.scope.insert_symbolic_alias(IndexedElement(result_var, convert_to_literal(index)), info["c_result"])
        return result_var

    @staticmethod
    def _module_variable_imports(expr):
        """Handle module variable imports for the current generation context."""
        mod = get_enclosing_module(expr)
        assert mod is not None
        if mod.imports:
            return []
        return [Import(mod.name, AsName(expr, expr.name), mod=mod)]

    def _generated_module_function_name(self, public_name: str):
        """Handle generated module function name for the current generation context."""
        return self.scope.get_new_public_name(
            public_name,
            object_type="function",
            owner=f"module variable accessor {public_name}",
        )

    def _scalar_module_variable(self, expr, _decision):
        """Handle scalar module variable for the current generation context."""
        getter = self._scalar_module_getter(expr)
        setter = (
            self._scalar_module_setter(expr)
            if expr.setter_ownership_decision.setter_action is SetterAction.WRITE_THROUGH
            else None
        )
        return expr.clone(
            expr.name,
            new_class=BindCScalarModuleVariable,
            getter_function=getter,
            setter_function=setter,
        )

    @staticmethod
    def _literal_module_constant(expr, _decision):
        """Expose one literal scalar or string constant without native storage."""
        return expr.clone(expr.name, new_class=BindCModuleConstant)

    def _copied_derived_module_constant(self, expr, decision):
        """Expose one derived constant through a wrapper-owned value copy."""
        if decision.transfer is not TransferMode.WRAPPER_INSTANCE:
            raise ValueError(f"Derived module constant {expr.name!r} is missing completed copy policy")
        if expr.setter_ownership_decision.setter_action is not SetterAction.OMIT:
            raise ValueError(f"Derived module constant {expr.name!r} unexpectedly exposes a setter")
        return expr.clone(
            expr.name,
            new_class=BindCScalarModuleVariable,
            getter_function=self._derived_module_copy_getter(expr),
            setter_function=None,
        )

    def _derived_module_variable(self, expr, decision):
        """Expose one addressable native module object through a borrowed wrapper."""
        if decision.boundary_storage_mode is not StorageMode.ALIAS:
            raise ValueError(f"Derived module variable {expr.name!r} is missing completed Aliased storage")
        if expr.setter_ownership_decision.setter_action is not SetterAction.REJECT_REPLACEMENT:
            raise ValueError(f"Derived module variable {expr.name!r} unexpectedly exposes replacement")
        return expr.clone(
            expr.name,
            new_class=BindCScalarModuleVariable,
            getter_function=self._derived_module_getter(expr),
            setter_function=None,
        )

    def _snapshot_derived_module_variable(self, expr, decision):
        """Expose one native module object through a detached snapshot getter."""
        if decision.boundary_storage_mode is StorageMode.ALIAS:
            raise ValueError(f"Derived module snapshot {expr.name!r} unexpectedly uses alias boundary storage")
        if expr.setter_ownership_decision.setter_action is not SetterAction.REJECT_REPLACEMENT:
            raise ValueError(f"Derived module snapshot {expr.name!r} unexpectedly exposes replacement")
        return expr.clone(
            expr.name,
            new_class=BindCScalarModuleVariable,
            getter_function=self._derived_module_copy_getter(expr),
            setter_function=None,
        )

    def _derived_module_copy_getter(self, expr):
        """Return a pointer to an owned copy of a derived module value."""
        getter_policy = expr.getter_ownership_decision
        if getter_policy is None:
            raise ValueError(f"Module variable {expr.name!r} is missing completed getter policy")
        value_type = expr.class_type.underlying_type if isinstance(expr.class_type, FinalType) else expr.class_type
        scope = self.scope
        public_name = f"get_{expr.name}"
        original_name = self._generated_module_function_name(public_name)
        func_name = scope.get_new_name("bind_c_" + public_name.lower())
        func_scope = scope.new_child_scope(func_name, "function")
        self.scope = func_scope
        source_value = expr.clone(
            expr.name,
            class_type=value_type,
            is_argument=False,
            is_optional=False,
            memory_handling=getter_policy.storage_mode.value,
            ownership_decision=getter_policy,
            new_class=Variable,
        )
        local_var = expr.clone(
            f"{expr.name}_snapshot",
            class_type=value_type,
            is_argument=False,
            is_optional=False,
            memory_handling=getter_policy.storage_mode.value,
            ownership_decision=getter_policy,
            new_class=Variable,
        )
        pointer_var = Variable(
            value_type,
            func_scope.get_new_name(f"{expr.name}_snapshot_ptr"),
            memory_handling="alias",
        )
        bind_var = Variable(BindCPointer(), func_scope.get_new_name(f"bound_{expr.name}"), memory_handling="alias")
        for variable in (local_var, pointer_var):
            func_scope.insert_variable(variable, name=str(variable.name))
        func_scope.imports["variables"][expr.name] = expr
        self.exit_scope()

        original_result = expr.clone(
            f"{expr.name}_value",
            class_type=value_type,
            is_argument=False,
            is_optional=False,
            memory_handling=getter_policy.storage_mode.value,
            ownership_decision=getter_policy,
            new_class=Variable,
        )
        original_function = FunctionDef(
            original_name,
            [],
            [],
            FunctionDefResult(original_result),
            scope=scope,
            decorators={
                RUNTIME_HOLD_GIL_METADATA: True,
                INTERNAL_MODULE_VARIABLE_NAME_METADATA: expr.name,
                INTERNAL_MODULE_VARIABLE_ACCESS_METADATA: "get",
            },
        )
        return BindCFunctionDef(
            func_name,
            [],
            [
                Assign(local_var, source_value),
                Allocate(pointer_var, shape=None, status="unallocated"),
                Assign(pointer_var, local_var),
                CLocFunc(pointer_var, bind_var),
            ],
            FunctionDefResult(BindCVariable(bind_var, local_var)),
            imports=self._module_variable_imports(expr),
            scope=func_scope,
            original_function=original_function,
        )

    def _derived_module_getter(self, expr):
        """Return the C address of an Aliased derived module object."""
        getter_policy = expr.getter_ownership_decision
        if getter_policy is None:
            raise ValueError(f"Module variable {expr.name!r} is missing completed getter policy")
        scope = self.scope
        public_name = f"get_{expr.name}"
        original_name = self._generated_module_function_name(public_name)
        func_name = scope.get_new_name("bind_c_" + public_name.lower())
        func_scope = scope.new_child_scope(func_name, "function")
        self.scope = func_scope
        getter_value = expr.clone(
            expr.name,
            is_argument=False,
            is_optional=False,
            memory_handling=getter_policy.boundary_storage_mode.value,
            ownership_decision=getter_policy,
            new_class=Variable,
        )
        bind_var = Variable(BindCPointer(), func_scope.get_new_name(f"bound_{expr.name}"), memory_handling="alias")
        func_scope.imports["variables"][expr.name] = expr
        self.exit_scope()

        original_result = expr.clone(
            f"{expr.name}_value",
            is_argument=False,
            is_optional=False,
            memory_handling=getter_policy.boundary_storage_mode.value,
            ownership_decision=getter_policy,
            new_class=Variable,
        )
        original_function = FunctionDef(
            original_name,
            [],
            [],
            FunctionDefResult(original_result),
            scope=scope,
            decorators={
                RUNTIME_HOLD_GIL_METADATA: True,
                INTERNAL_MODULE_VARIABLE_NAME_METADATA: expr.name,
                INTERNAL_MODULE_VARIABLE_ACCESS_METADATA: "get",
            },
        )
        return BindCFunctionDef(
            func_name,
            [],
            [CLocFunc(getter_value, bind_var)],
            FunctionDefResult(BindCVariable(bind_var, getter_value)),
            imports=self._module_variable_imports(expr),
            scope=func_scope,
            original_function=original_function,
        )

    def _scalar_module_getter(self, expr):
        """Handle scalar module getter for the current generation context."""
        getter_policy = expr.getter_ownership_decision
        if getter_policy is None:
            raise ValueError(f"Module variable {expr.name!r} is missing completed getter policy")
        scope = self.scope
        public_name = f"get_{expr.name}"
        original_name = self._generated_module_function_name(public_name)
        func_name = scope.get_new_name("bind_c_" + public_name.lower())
        func_scope = scope.new_child_scope(func_name, "function")
        self.scope = func_scope
        func_scope.imports["variables"][expr.name] = expr
        if getter_policy.codegen_action is CodegenAction.SNAPSHOT_COPY:
            source_value = expr.clone(
                expr.name,
                is_argument=False,
                is_optional=False,
                memory_handling=getter_policy.storage_mode.value,
                ownership_decision=getter_policy,
                new_class=Variable,
            )
            result_info = self._build_snapshot_copy_scalar_result(
                expr,
                self._nullable_scalar_status_func(getter_policy),
                source_expr=source_value,
            )
            body = result_info["body"]
            result = result_info["c_result"]
        else:
            result = expr.clone(
                func_scope.get_new_name(f"{expr.name}_value"),
                is_argument=False,
                is_optional=False,
                memory_handling=getter_policy.storage_mode.value,
                ownership_decision=getter_policy,
                new_class=Variable,
            )
            func_scope.insert_variable(result)
            body = [Assign(result, expr)]
        self.exit_scope()
        original_result = expr.clone(
            f"{expr.name}_value",
            is_argument=False,
            is_optional=False,
            memory_handling=getter_policy.storage_mode.value,
            ownership_decision=getter_policy,
            new_class=Variable,
        )
        original_function = FunctionDef(
            original_name,
            [],
            [],
            FunctionDefResult(original_result),
            scope=scope,
            decorators={
                RUNTIME_HOLD_GIL_METADATA: True,
                INTERNAL_MODULE_VARIABLE_NAME_METADATA: expr.name,
                INTERNAL_MODULE_VARIABLE_ACCESS_METADATA: "get",
            },
        )
        return BindCFunctionDef(
            func_name,
            [],
            body,
            FunctionDefResult(result),
            imports=self._module_variable_imports(expr),
            scope=func_scope,
            original_function=original_function,
        )

    def _scalar_module_setter(self, expr):
        """Handle scalar module setter for the current generation context."""
        setter_policy = expr.setter_ownership_decision
        if setter_policy is None:
            raise ValueError(f"Module variable {expr.name!r} is missing completed setter policy")
        scope = self.scope
        public_name = f"set_{expr.name}"
        original_name = self._generated_module_function_name(public_name)
        func_name = scope.get_new_name("bind_c_" + public_name.lower())
        func_scope = scope.new_child_scope(func_name, "function")
        self.scope = func_scope
        value = expr.clone(
            func_scope.get_new_name("value"),
            is_argument=True,
            is_optional=False,
            memory_handling=setter_policy.storage_mode.value,
            ownership_decision=setter_policy,
            new_class=Variable,
        )
        func_scope.insert_variable(value)
        func_scope.imports["variables"][expr.name] = expr
        body = [Assign(expr, value)]
        self.exit_scope()
        original_value = expr.clone(
            "value",
            is_argument=True,
            is_optional=False,
            memory_handling=setter_policy.storage_mode.value,
            ownership_decision=setter_policy,
            new_class=Variable,
        )
        original_function = FunctionDef(
            original_name,
            [FunctionDefArgument(original_value)],
            [],
            FunctionDefResult(NIL),
            scope=scope,
            decorators={
                RUNTIME_HOLD_GIL_METADATA: True,
                INTERNAL_MODULE_VARIABLE_NAME_METADATA: expr.name,
                INTERNAL_MODULE_VARIABLE_ACCESS_METADATA: "set",
            },
        )
        return BindCFunctionDef(
            func_name,
            [FunctionDefArgument(value)],
            body,
            FunctionDefResult(NIL),
            imports=self._module_variable_imports(expr),
            scope=func_scope,
            original_function=original_function,
        )

    def _get_pointer_snapshot_bind_c_array(self, name, orig_var, pointer_var):
        """Return a snapshot-copy bind C array for descriptor-backed storage."""
        dtype = orig_var.dtype
        rank = orig_var.rank
        order = orig_var.order
        scope = self.scope

        bind_var = Variable(BindCPointer(), scope.get_new_name("bound_" + name), memory_handling="alias")
        shape_vars = [Variable(NumpyInt32Type(), scope.get_new_name(f"{name}_shape_{i + 1}")) for i in range(rank)]

        numpy_dtype = numpy_precision_map[(dtype.primitive_type, dtype.precision)]
        ptr_var = Variable(
            NumpyNDArrayType.get_new(numpy_dtype, rank, order),
            scope.get_new_name(name + "_ptr"),
            memory_handling="alias",
        )
        elem_var = Variable(dtype, scope.get_new_name(name + "_elem"))
        scope.insert_variable(ptr_var)
        scope.insert_variable(elem_var)

        shape_assignments = [
            Assign(
                shape_var,
                cast_to(ArrayShapeElement(pointer_var, convert_to_literal(index)), NumpyInt32Type()),
            )
            for index, shape_var in enumerate(shape_vars)
        ]
        size = reduce(Mul, [BindCSizeOf(elem_var), *shape_vars])
        copy_body = [
            *shape_assignments,
            Assign(bind_var, c_malloc(size)),
            If(
                IfSection(
                    IsNot(bind_var, NIL),
                    [
                        C_F_Pointer(bind_var, ptr_var, shape_vars if order == "F" else shape_vars[::-1]),
                        Assign(ptr_var, pointer_var),
                    ],
                )
            ),
        ]
        unassociated_body = [
            Assign(bind_var, NIL),
            *[Assign(shape_var, convert_to_literal(0, dtype=NumpyInt32Type())) for shape_var in shape_vars],
        ]
        body = [
            If(
                IfSection(ArrayAssociated(pointer_var), copy_body),
                IfSection(convert_to_literal(True), unassociated_body),
            )
        ]

        result_var = Variable(
            BindCArrayType.get_new(rank, has_strides=False),
            scope.get_new_name(),
            shape=(rank + 1,),
        )
        c_result = BindCVariable(result_var, orig_var)
        for descriptor in (result_var, c_result):
            scope.insert_symbolic_alias(IndexedElement(descriptor, convert_to_literal(0)), bind_var)
            for index, shape_var in enumerate(shape_vars):
                scope.insert_symbolic_alias(IndexedElement(descriptor, convert_to_literal(index + 1)), shape_var)

        return {
            "c_result": c_result,
            "body": body,
            "f_array": ptr_var,
            "bind_var": bind_var,
            "shape_vars": shape_vars,
        }

    def _get_allocatable_snapshot_bind_c_array(self, name, orig_var, source_var):
        """Return a Python-owned snapshot of allocatable module storage."""
        dtype = orig_var.dtype
        rank = orig_var.rank
        order = orig_var.order
        scope = self.scope

        bind_var = Variable(BindCPointer(), scope.get_new_name("bound_" + name), memory_handling="alias")
        shape_vars = [Variable(NumpyInt32Type(), scope.get_new_name(f"{name}_shape_{i + 1}")) for i in range(rank)]

        numpy_dtype = numpy_precision_map[(dtype.primitive_type, dtype.precision)]
        ptr_var = Variable(
            NumpyNDArrayType.get_new(numpy_dtype, rank, order),
            scope.get_new_name(name + "_ptr"),
            memory_handling="alias",
        )
        elem_var = Variable(dtype, scope.get_new_name(name + "_elem"))
        scope.insert_variable(ptr_var)
        scope.insert_variable(elem_var)

        shape_assignments = [
            Assign(
                shape_var,
                cast_to(ArrayShapeElement(source_var, convert_to_literal(index)), NumpyInt32Type()),
            )
            for index, shape_var in enumerate(shape_vars)
        ]
        size = reduce(Mul, [BindCSizeOf(elem_var), *shape_vars])
        copy_body = [
            *shape_assignments,
            Assign(bind_var, c_malloc(size)),
            If(
                IfSection(
                    IsNot(bind_var, NIL),
                    [
                        C_F_Pointer(bind_var, ptr_var, shape_vars if order == "F" else shape_vars[::-1]),
                        Assign(ptr_var, source_var),
                    ],
                )
            ),
        ]
        unallocated_body = [
            Assign(bind_var, NIL),
            *[Assign(shape_var, convert_to_literal(0, dtype=NumpyInt32Type())) for shape_var in shape_vars],
        ]
        body = [
            If(
                IfSection(ArrayAllocated(source_var), copy_body),
                IfSection(convert_to_literal(True), unallocated_body),
            )
        ]

        result_var = Variable(
            BindCArrayType.get_new(rank, has_strides=False),
            scope.get_new_name(),
            shape=(rank + 1,),
        )
        c_result = BindCVariable(result_var, orig_var)
        for descriptor in (result_var, c_result):
            scope.insert_symbolic_alias(IndexedElement(descriptor, convert_to_literal(0)), bind_var)
            for index, shape_var in enumerate(shape_vars):
                scope.insert_symbolic_alias(IndexedElement(descriptor, convert_to_literal(index + 1)), shape_var)

        return {
            "c_result": c_result,
            "body": body,
            "f_array": ptr_var,
            "bind_var": bind_var,
            "shape_vars": shape_vars,
        }

    def _get_bind_c_array(self, name, orig_var, shape, pointer_target=False, source_var=None):
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
        rank = orig_var.rank
        scope = self.scope
        has_itemsize = self._is_character_array(orig_var)
        # Create the C-compatible data pointer
        bind_var = Variable(BindCPointer(), scope.get_new_name("bound_" + name), memory_handling="alias")
        itemsize_var = Variable(NumpyInt64Type(), scope.get_new_name(f"{name}_itemsize")) if has_itemsize else None
        shape_vars = [Variable(NumpyInt32Type(), scope.get_new_name(f"{name}_shape_{i + 1}")) for i in range(rank)]
        f_array, elem_var = self._bind_c_array_result_storage(name, orig_var, pointer_target, has_itemsize)
        shape = self._bind_c_array_result_shape(f_array, rank, shape)
        body = [Assign(s_v, cast_to(s, NumpyInt32Type())) for s_v, s in zip(shape_vars, shape, strict=False)]
        body.extend(self._bind_c_array_itemsize_body(itemsize_var, source_var, pointer_target, orig_var))
        byte_count = reduce(Mul, [itemsize_var, *shape_vars]) if itemsize_var is not None else None
        body.extend(
            self._bind_c_array_pointer_body(
                orig_var,
                bind_var,
                elem_var,
                shape_vars,
                byte_count,
                pointer_target,
                f_array,
            )
        )
        _result_var, c_result = self._bind_c_array_result_descriptor(
            rank,
            has_itemsize,
            bind_var,
            itemsize_var,
            shape_vars,
            orig_var,
        )

        return {
            "c_result": c_result,
            "body": body,
            "f_array": f_array,
            "bind_var": bind_var,
            "byte_count": byte_count,
            "itemsize_var": itemsize_var,
            "shape_vars": shape_vars,
        }

    def _bind_c_array_result_storage(self, name, orig_var, pointer_target, has_itemsize):
        """Create the Fortran-side array storage used for bind-C array results."""
        if pointer_target:
            return orig_var, None
        dtype = orig_var.dtype
        rank = orig_var.rank
        order = orig_var.order
        numpy_dtype = dtype if has_itemsize else numpy_precision_map[(dtype.primitive_type, dtype.precision)]
        ptr_rank = 1 if has_itemsize else rank
        ptr_var = Variable(
            NumpyNDArrayType.get_new(numpy_dtype, ptr_rank, order),
            self.scope.get_new_name(name + "_ptr"),
            memory_handling="alias",
            fortran_character_length=1 if has_itemsize else None,
        )
        elem_var = Variable(dtype, self.scope.get_new_name(name + "_elem"))
        self.scope.insert_variable(ptr_var)
        self.scope.insert_variable(elem_var)
        return ptr_var, elem_var

    @staticmethod
    def _bind_c_array_result_shape(f_array, rank, shape):
        """Fill unspecified bind-C result dimensions from the emitted Fortran array."""
        if shape is None:
            return tuple(ArrayShapeElement(f_array, convert_to_literal(index)) for index in range(rank))
        return tuple(
            ArrayShapeElement(f_array, convert_to_literal(index)) if dim is None else dim
            for index, dim in enumerate(shape)
        )

    @staticmethod
    def _bind_c_array_itemsize_body(itemsize_var, source_var, pointer_target, orig_var):
        """Return itemsize assignment nodes for fixed-width character array results."""
        if itemsize_var is None:
            return []
        length_source = source_var
        if length_source is None and isinstance(pointer_target, Variable):
            length_source = pointer_target
        if length_source is None:
            length_source = orig_var
        return [Assign(itemsize_var, cast_to(FortranCharacterLength(length_source), NumpyInt64Type()))]

    def _bind_c_array_pointer_body(self, orig_var, bind_var, elem_var, shape_vars, byte_count, pointer_target, f_array):
        """Create pointer association or allocation nodes for a bind-C result."""
        if pointer_target:
            return [CLocFunc(self._bind_c_array_pointer_source(orig_var), bind_var)]
        pointer_shape = (
            [byte_count] if byte_count is not None else self._bind_c_array_pointer_shape(orig_var, shape_vars)
        )
        size_terms = (
            [BindCSizeOf(elem_var), byte_count] if byte_count is not None else [BindCSizeOf(elem_var), *shape_vars]
        )
        return [
            Assign(bind_var, c_malloc(reduce(Mul, size_terms))),
            If(IfSection(IsNot(bind_var, NIL), [C_F_Pointer(bind_var, f_array, pointer_shape)])),
        ]

    @staticmethod
    def _bind_c_array_pointer_shape(orig_var, shape_vars):
        """Return pointer shape respecting Fortran or C-oriented storage."""
        return shape_vars if orig_var.order == "F" else shape_vars[::-1]

    @staticmethod
    def _bind_c_array_pointer_source(orig_var):
        """Return the addressable source for borrowed bind-C result arrays."""
        if ownership_decision_for_codegen_variable(orig_var).storage_mode is StorageMode.HEAP:
            return IndexedElement(
                orig_var,
                *(ArrayLowerBound(orig_var, convert_to_literal(index)) for index in range(orig_var.rank)),
            )
        return orig_var

    def _bind_c_array_result_descriptor(self, rank, has_itemsize, bind_var, itemsize_var, shape_vars, orig_var):
        """Create and alias the bind-C array result descriptor."""
        descriptor_offset = 2 if has_itemsize else 1
        result_var = Variable(
            BindCArrayType.get_new(rank, has_strides=False, has_itemsize=has_itemsize),
            self.scope.get_new_name(),
            shape=(rank + descriptor_offset,),
        )
        c_result = BindCVariable(result_var, orig_var)
        for descriptor in (result_var, c_result):
            self.scope.insert_symbolic_alias(IndexedElement(descriptor, convert_to_literal(0)), bind_var)
            if itemsize_var is not None:
                self.scope.insert_symbolic_alias(IndexedElement(descriptor, convert_to_literal(1)), itemsize_var)
            for i, s in enumerate(shape_vars):
                self.scope.insert_symbolic_alias(
                    IndexedElement(descriptor, convert_to_literal(i + descriptor_offset)), s
                )
        return result_var, c_result
