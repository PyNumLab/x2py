"""
Module describing the code-wrapping class : CToPythonWrapper
which creates an interface exposing C code to Python.
"""

import warnings

from ..bind_c import (
    BindCArrayVariable,
    BindCArrayType,
    BindCClassDef,
    BindCClassProperty,
    BindCFunctionDef,
    BindCModule,
    BindCModuleVariable,
    BindCPointer,
    BindCVariable,
)
from ..models.core import PythonTuple
from .c_concepts import (
    CNativeInt,
    CStrStr,
    ObjectAddress,
    PointerCast,
)
from ..models.core import (
    AliasAssign,
    Allocate,
    AsName,
    Assign,
    AugAssign,
    ClassDef,
    CommentBlock,
    Deallocate,
    Declare,
    FunctionAddress,
    FunctionCall,
    FunctionDef,
    FunctionDefArgument,
    FunctionDefResult,
    get_enclosing_class,
    If,
    IfSection,
    Import,
    is_in_overload_set,
    Module,
    Return,
)
from .cpython_api import (
    C_to_Python,
    Py_DECREF,
    Py_INCREF,
    Py_None,
    Py_ssize_t,
    PyArg_ParseTupleNode,
    PyArgKeywords,
    PyArgumentError,
    PyAttributeError,
    PyBuildValueNode,
    PyCapsule_Import,
    PyCapsule_New,
    PythonObjectType,
    PythonTypeObjectType,
    PyClassDef,
    PyErr_SetString,
    PyFunctionDef,
    PyGetSetDefElement,
    PyFunctionOverloadSet,
    PyList_Append,
    PyList_GetItem,
    PyList_New,
    PyList_SetItem,
    PyMemoryError,
    PyModInitFunc,
    PyModule,
    PyModule_AddObject,
    PyModule_Create,
    PyNotImplementedError,
    PyObject_TypeCheck,
    PySys_GetObject,
    PyTuple_Pack,
    PyType_Ready,
    PyTypeError,
    PyUnicode_AsUTF8,
    PyUnicode_AsUTF8AndSize,
    PyUnicode_Check,
    PyUnicode_FromString,
    WrapperCustomDataType,
    check_type_registry,
    py_to_c_registry,
)
from ..models.datatypes import (
    CharType,
    CustomDataType,
    DataTypeFactory,
    FinalType,
    FixedSizeNumericType,
    NumpyBoolType,
    PrimitiveComplexType,
    PrimitiveFloatingPointType,
    PrimitiveIntegerType,
    StringType,
    TupleType,
    VoidType,
    cast_to,
    NIL,
    convert_to_literal,
)
from ..models.core import Slice
from .numpy_cpython_api import (
    PyArray_DATA,
    PyArray_SetBaseObject,
    NumpyArrayObjectType,
    get_strides_and_shape_from_numpy_array,
    import_array,
    is_numpy_array,
    no_order_check,
    numpy_dtype_registry,
    numpy_flag_c_contig,
    numpy_flag_f_contig,
    pyarray_check,
    require_any_contiguous,
    require_c_contiguous,
    require_f_contiguous,
    to_pyarray,
)
from ..models.datatypes import (
    NumpyInt32Type,
    NumpyInt64Type,
    NumpyNDArrayType,
)
from ..models.core import (
    IfTernaryOperator,
    Eq,
    Is,
    IsNot,
    Lt,
    Ne,
    Not,
    Or,
)
from ..models.core import DottedVariable, IndexedElement, Variable
from ..scope import Scope

from .base import BindingGenerator

cpython_ndarray_imports = [
    Import("python_runtime_ndarrays", Module("python_runtime_ndarrays", (), ())),
    Import("ndarrays", Module("ndarrays", (), ())),
]

StackArrayClass = ClassDef("stack_array")

magic_binary_funcs = (
    "__add__",
    "__sub__",
    "__mul__",
    "__truediv__",
    "__pow__",
    "__lshift__",
    "__rshift__",
    "__and__",
    "__or__",
    "__iadd__",
    "__isub__",
    "__imul__",
    "__itruediv__",
    "__ipow__",
    "__ilshift__",
    "__irshift__",
    "__iand__",
    "__ior__",
    "__getitem__",
)
magic_unary_funcs = ("__pos__", "__neg__", "__invert__")
magic_comparison_funcs = ("__eq__", "__ne__", "__lt__", "__le__", "__gt__", "__ge__")
magic_overload_funcs = (*magic_binary_funcs, *magic_unary_funcs, *magic_comparison_funcs)


class CPythonBindingGenerator(BindingGenerator):
    """
    Class for creating a wrapper exposing C code to Python.

    A class which provides all necessary functions for wrapping different AST
    objects such that the resulting AST is Python-compatible.

    Parameters
    ----------
    sharedlib_dirpath : str
        The folder where the generated .so file will be located.
    verbose : int
        The level of verbosity.
    """

    target_language = "Python"
    start_language = "C"

    def __init__(self, sharedlib_dirpath, verbose):
        # A map used to find the Python-compatible Variable equivalent to an object in the AST
        self._python_object_map = {}
        # The object that should be returned to indicate an error
        self._error_exit_code = NIL

        self._sharedlib_dirpath = sharedlib_dirpath
        super().__init__(verbose)

    def _function_docstring(self, name, func, original_func=None):
        original_func = original_func or func
        visible_args = [arg for arg in func.arguments if not arg.bound_argument]
        result_vars = self._doc_python_result_vars(func, original_func)
        signature = f"{name}({', '.join(self._doc_argument_name(arg) for arg in visible_args)})"
        signature += f" -> {self._doc_result_summary(result_vars)}" if result_vars else " -> None"

        sections = [signature]
        user_doc = self._existing_docstring_text(getattr(original_func, "docstring", None))
        if user_doc:
            sections.extend(["", user_doc])

        if visible_args:
            sections.extend(["", "Parameters", "----------"])
            for arg in visible_args:
                sections.extend(self._argument_doc_lines(arg))

        sections.extend(["", "Returns", "-------"])
        if result_vars:
            for result in result_vars:
                sections.extend(self._variable_doc_lines(self._doc_original_var(result), result_name=True))
        else:
            sections.append("None")

        notes = self._result_notes(result_vars)
        if notes:
            sections.extend(["", "Notes", "-----", *notes])

        sections.extend(
            [
                "",
                "Raises",
                "------",
                "TypeError",
                "    If an argument has incompatible dtype, rank, shape, layout, or wrapped class.",
            ]
        )
        return CommentBlock("\n".join(sections))

    @staticmethod
    def _existing_docstring_text(docstring):
        if not docstring:
            return ""
        return "\n".join(str(line) for line in docstring.comments if str(line).strip())

    def _argument_doc_lines(self, arg):
        var = self._doc_original_var(arg.var)
        can_be_none = getattr(arg.var, "is_optional", False) or getattr(var, "is_optional", False)
        header = f"{self._doc_argument_name(arg)} : {self._type_doc(var, include_none=can_be_none)}"
        details = self._argument_detail_lines(var)
        if can_be_none:
            details.append("    May be omitted or passed as None.")
        if arg.has_default:
            details.append(f"    Default is {arg.value}.")
        return [header, *details]

    def _variable_doc_lines(self, var, *, result_name=False):
        name = str(var.name) if result_name else "result"
        header = f"{name} : {self._type_doc(var, include_none=self._may_return_none(var))}"
        return [header, *self._result_detail_lines(var)]

    def _argument_detail_lines(self, var):
        intent = getattr(var, "intent", "in")
        lines = self._value_detail_lines(var)
        lines.append(f"    Intent: {intent}")
        if intent == "out":
            lines.append("    Mutates: fills in-place")
            if getattr(var, "rank", 0):
                lines.append("    Initial contents are ignored.")
        elif intent == "inout":
            lines.append("    Mutates: yes")
        return lines

    def _result_detail_lines(self, var):
        lines = self._value_detail_lines(var)
        if self._is_pointer_snapshot_result(var):
            lines.append("    Ownership: Python-owned")
            lines.append("    Returns None when unassociated.")
        elif var.rank and var.memory_handling == "heap":
            lines.append("    Ownership: Python-owned")
            lines.append("    Returns None when unallocated.")
        elif var.rank and getattr(var, "intent", "in") == "out":
            lines.append("    Ownership: Python-owned")
        elif var.rank and var.memory_handling == "alias":
            lines.append("    Ownership: Native-owned")
        return lines

    def _borrowed_detail_lines(self, var, description):
        lines = self._value_detail_lines(var)
        if var.rank:
            lines.append(f"    Ownership: {description}")
            if self._may_return_none(var):
                lines.append("    Returns None when unallocated.")
        return lines

    def _result_notes(self, result_vars):
        notes = []
        if any(
            self._doc_original_var(var).rank and self._doc_original_var(var).memory_handling == "heap"
            for var in result_vars
        ):
            notes.extend(
                [
                    "Allocatable array outputs are copied into Python-owned NumPy arrays.",
                    "This copy adds overhead proportional to the returned array size.",
                ]
            )
        if any(self._is_pointer_snapshot_result(self._doc_original_var(var)) for var in result_vars):
            if notes:
                notes.append("")
            notes.extend(
                [
                    "Pointer array results are copied into Python-owned NumPy arrays.",
                    "Unassociated pointer results return None.",
                ]
            )
        if any(
            self._doc_original_var(var).rank
            and self._doc_original_var(var).memory_handling == "alias"
            and not self._is_pointer_snapshot_result(self._doc_original_var(var))
            for var in result_vars
        ):
            if notes:
                notes.append("")
            notes.extend(self._borrowed_view_notes())
        return notes

    @staticmethod
    def _borrowed_view_notes():
        return [
            "The returned NumPy array is a zero-copy view of native Fortran memory.",
            "",
            "If the corresponding allocatable variable is deallocated or",
            "reallocated on the native side, previously obtained views may",
            "become invalid.",
            "",
            "Use ``x.copy()`` to obtain an independent NumPy array.",
        ]

    def _value_detail_lines(self, var):
        lines = []
        if var.rank:
            shape_doc = self._shape_doc(var)
            if shape_doc:
                lines.append(f"    Shape: {shape_doc}")
            lines.append(f"    Rank: {var.rank}")
            layout_doc = self._layout_doc(var)
            if layout_doc:
                lines.append(f"    Layout: {layout_doc}")
        return lines

    @staticmethod
    def _type_doc(var, *, include_none=False, signature=False):
        if getattr(var, "is_ndarray", False):
            doc_type = f"ndarray[{CPythonBindingGenerator._dtype_doc(var)}]"
        else:
            doc_type = str(var.class_type).removeprefix("numpy.")
        if not include_none:
            return doc_type
        return f"{doc_type} | None" if signature else f"{doc_type} or None"

    @staticmethod
    def _dtype_doc(var):
        return str(var.dtype).removeprefix("numpy.")

    @staticmethod
    def _may_return_none(var):
        return bool(
            var.rank and (var.memory_handling == "heap" or CPythonBindingGenerator._is_pointer_snapshot_result(var))
        )

    @staticmethod
    def _is_pointer_snapshot_result(var):
        return bool(
            getattr(var, "rank", 0)
            and getattr(var, "memory_handling", None) == "alias"
            and not isinstance(var, DottedVariable)
            and getattr(var, "intent", "in") == "out"
        )

    @staticmethod
    def _shape_doc(var):
        shape = getattr(var, "alloc_shape", None)
        if not shape or all(dim is None for dim in shape):
            return None
        shape_parts = ["any" if dim is None else str(dim) for dim in shape]
        trailing_comma = "," if len(shape_parts) == 1 else ""
        return f"({', '.join(shape_parts)}{trailing_comma})"

    @staticmethod
    def _layout_doc(var):
        if getattr(var, "rank", 0) <= 1:
            return None
        order = getattr(var, "order", None)
        if order == "F":
            return "F-contiguous"
        if order == "C":
            return "C-contiguous"
        return "C-contiguous"

    @staticmethod
    def _doc_original_var(var):
        return getattr(var, "original_var", var)

    def _doc_argument_name(self, arg):
        return str(self._doc_original_var(arg.var).name)

    @staticmethod
    def _doc_result_vars(func):
        if func.results.var is NIL:
            return []
        return [
            var
            for var in func.scope.collect_all_tuple_elements(func.results.var)
            if isinstance(var, Variable) and var is not NIL
        ]

    def _doc_python_result_vars(self, func, original_func):
        result_vars = []
        if original_func.results.var is not NIL:
            result_vars.extend(self._doc_result_vars(original_func))
        result_vars.extend(
            arg.var
            for arg in original_func.arguments
            if not arg.bound_argument and getattr(arg.var, "intent", "in") == "out"
        )
        return result_vars or self._doc_result_vars(func)

    def _doc_result_summary(self, result_vars):
        parts = [
            self._type_doc(
                self._doc_original_var(var),
                include_none=self._may_return_none(self._doc_original_var(var)),
                signature=True,
            )
            for var in result_vars
        ]
        if len(parts) == 1:
            result_var = self._doc_original_var(result_vars[0])
            return self._type_doc(result_var, include_none=self._may_return_none(result_var), signature=True)
        return f"tuple[{', '.join(parts)}]"

    def _class_docstring(self, cls):
        lines = [str(cls.name), "", "Fields", "------"]
        if cls.attributes:
            for attribute in cls.attributes:
                attr_name, var = self._class_attribute_doc_target(attribute)
                lines.append(f"{attr_name} : {self._type_doc(var, include_none=self._may_return_none(var))}")
                lines.extend(self._borrowed_detail_lines(var, "Native-owned"))
        else:
            lines.append("None")
        lines.extend(["", "Methods", "-------"])
        public_methods = []
        for method in cls.methods:
            if not method.is_semantic or method.is_private:
                continue
            original = getattr(method, "original_function", method)
            py_name = str(original.scope.get_python_name(original.name))
            if py_name == "__del__":
                continue
            public_methods.append(py_name)
        if public_methods:
            lines.extend(public_methods)
        else:
            lines.append("None")
        return CommentBlock("\n".join(lines))

    def _class_attribute_doc_target(self, attribute):
        if isinstance(attribute, BindCClassProperty):
            original = attribute.getter.original_function
            if isinstance(original, DottedVariable):
                return attribute.python_name, self._doc_original_var(original)
            return attribute.python_name, self._doc_original_var(original.results.var)
        return str(attribute.name), self._doc_original_var(attribute)

    def _property_docstring(self, name, func):
        docstring = f"{name} : object" if func.results.var is NIL else self._attribute_docstring(name, func.results.var)
        user_doc = self._existing_docstring_text(getattr(func, "docstring", None))
        if user_doc:
            docstring += f"\n\nNotes\n-----\n{user_doc}"
        return docstring

    def _attribute_docstring(self, name, var):
        var = self._doc_original_var(var)
        lines = [
            f"{name} : {self._type_doc(var, include_none=self._may_return_none(var))}",
            *self._borrowed_detail_lines(var, "Native-owned"),
        ]
        if not var.rank:
            lines.append("    Assigning writes through the generated setter when available.")
        elif var.memory_handling in {"heap", "alias"}:
            lines.extend(["", "Notes", "-----", *self._borrowed_view_notes()])
        return "\n".join(lines)

    def _module_array_getter_docstring(self, name, var):
        var = self._doc_original_var(var)
        lines = [
            f"{name}() -> {self._type_doc(var, include_none=True, signature=True)}",
            "",
            "Returns",
            "-------",
            f"{var.name} : {self._type_doc(var, include_none=True)}",
            *self._borrowed_detail_lines(var, "Native-owned"),
            "",
            "Notes",
            "-----",
            *self._borrowed_view_notes(),
        ]
        return CommentBlock("\n".join(lines))

    def get_new_PyObject(self, name, dtype=None, is_temp=False):
        """
        Create new `PythonObjectType` `Variable` with the desired name.

        Create a new `Variable` with the datatype `PythonObjectType` and the desired name.
        A `PythonObjectType` datatype means that this variable can be accessed and
        manipulated from Python.

        Parameters
        ----------
        name : str
            The desired name.

        dtype : DataType, optional
            The datatype of the object which will be represented by this PyObject.
            This is not necessary unless a variable sis required which will describe
            a class.

        is_temp : bool, default=False
            Indicates if the Variable is temporary. A temporary variable may be ignored
            by the printer.

        Returns
        -------
        Variable
            The new variable.
        """
        if isinstance(dtype, CustomDataType):
            var = Variable(
                self._python_object_map[dtype],
                self.scope.get_new_name(name),
                memory_handling="alias",
                cls_base=self.scope.find(dtype.name, "classes", raise_if_missing=True),
                is_temp=is_temp,
            )
        else:
            var = Variable(
                PythonObjectType(),
                self.scope.get_new_name(name),
                memory_handling="alias",
                is_temp=is_temp,
            )
        self.scope.insert_variable(var)
        return var

    def _get_python_argument_variables(self, args):
        """
        Get a new set of `PythonObjectType` `Variable`s representing each of the arguments.

        Create a new `PythonObjectType` variable for each argument returned in Python.
        The results are saved to the `self._python_object_map` dictionary so they can be
        discovered later.

        Parameters
        ----------
        args : iterable of FunctionDefArguments
            The arguments of the function.

        Returns
        -------
        list of Variable
            Variables which will hold the arguments in Python.
        """
        orig_args = [getattr(a.var, "original_var", a.var) for a in args]
        is_bound = [getattr(a, "wrapping_bound_argument", a.bound_argument) for a in args]
        collect_args = [
            self.get_new_PyObject(o_a.name + "_obj", dtype=o_a.dtype if b else None)
            for a, b, o_a in zip(args, is_bound, orig_args, strict=False)
        ]
        self._python_object_map.update(dict(zip(args, collect_args, strict=False)))
        return collect_args

    def _unpack_python_args(self, args, class_base=None):
        """
        Unpack the arguments received from Python into the expected Python variables.

        Create the wrapper arguments of the current `FunctionDef` (`self`, `args`, `kwargs`).
        Get a new set of `PythonObjectType` `Variable`s representing each of the expected
        arguments. Add the code which unpacks the `args` and `kwargs` into individual
        `PythonObjectType`s for each of the expected arguments.

        Parameters
        ----------
        args : iterable of FunctionDefArguments
            The expected arguments of the function.

        class_base : DataType, optional
            The DataType of the class which the method belongs to. In the case of a method
            defined in a module this value is None.

        Returns
        -------
        func_args : list of Variable
            The arguments of the FunctionDef.

        body : list of codegen model object
            The code which unpacks the arguments.

        Examples
        --------
        >>> arg = Variable('int', 'x')
        >>> func_args = (FunctionDefArgument(arg),)
        >>> wrapper_args, body = self._unpack_python_args(func_args)
        >>> wrapper_args
        [Variable('self', dtype=PythonObjectType()), Variable('args', dtype=PythonObjectType()), Variable('kwargs', dtype=PythonObjectType())]
        >>> body
        [<x2py.codegen.bindings.cpython_api.PyArgKeywords object at 0x7f99ec128cc0>, <x2py.codegen.models.core.If object at 0x7f99ed3a5b20>]
        >>> CPythonCodePrinter('wrapper_file.c').doprint(expr)
        static char *kwlist[] = {
            "x",
            NULL
        };
        if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O", kwlist, &x_obj))
        {
            return NULL;
        }
        """
        has_bound_arg = class_base is not None
        bound_arg = args[0] if has_bound_arg else None
        args = args[int(has_bound_arg) :]
        # Create necessary variables
        func_args = [self.get_new_PyObject("self", class_base)] + [self.get_new_PyObject(n) for n in ("args", "kwargs")]
        arg_vars = self._get_python_argument_variables(args)
        keyword_list_name = self.scope.get_new_name("kwlist")

        if has_bound_arg:
            self._python_object_map[bound_arg] = func_args[0]

        # Create the list of argument names
        arg_names = ["" if a.is_posonly else getattr(a.var, "original_var", a.var).name for a in args]
        keyword_list = PyArgKeywords(keyword_list_name, arg_names)

        # Parse arguments
        parse_node = PyArg_ParseTupleNode(*func_args[1:], args, arg_vars, keyword_list)

        # Initialise optionals
        body = [
            AliasAssign(py_arg, Py_None)
            for func_def_arg, py_arg in zip(args, arg_vars, strict=False)
            if func_def_arg.has_default
        ]

        body.append(keyword_list)
        body.append(If(IfSection(Not(parse_node), [Return(self._error_exit_code)])))

        return func_args, body

    def _get_python_result_variables(self, results):
        """
        Get a new set of `PythonObjectType` `Variable`s representing each of the results.

        Create a new `PythonObjectType` variable for each result returned in Python.
        The results are saved to the `self._python_object_map` dictionary so they can be
        discovered later.

        Parameters
        ----------
        results : iterable of FunctionDefResults
            The results of the function.

        Returns
        -------
        list of Variable
            Variables which will hold the results in Python.
        """
        collect_results = [
            self.get_new_PyObject(
                r.var.name + "_obj",
                getattr(r, "original_function_result_variable", r.var).dtype,
            )
            for r in results
        ]
        self._python_object_map.update(dict(zip(results, collect_results, strict=False)))
        return collect_results

    def _get_type_check_condition(
        self,
        py_obj,
        arg,
        raise_error,
        body,
        allow_empty_arrays,
        *,
        native_scalar_check=None,
    ):
        """
        Get the condition which checks if an argument has the expected type.

        Using the C-compatible description of a function argument, determine whether the Python
        object (with datatype `PythonObjectType`) holds data which is compatible with the expected
        type. The check is returned along with any errors that may be raised depending upon the
        result and the value of `raise_error`.

        Parameters
        ----------
        py_obj : Variable
            The variable with datatype `PythonObjectType` where the arguments is stored in Python.

        arg : Variable
            The C-compatible variable which holds all the details about the expected type.

        raise_error : bool
            True if an error should be raised in case of an unexpected type, False otherwise.

        body : list
            A list describing code where the type check will occur. This allows any necessary code
            to be inserted into the code block. E.g. code which should be run before the condition
            can be checked.

        allow_empty_arrays : bool
            A boolean indicating whether empty arrays are authorised. This is necessary as STC
            does not handle empty arrays.

        Returns
        -------
        type_check_condition : FunctionCall | Variable
            The function call which checks if the argument has the expected type or the variable
            indicating if the argument has the expected type.

        error_code : tuple of codegen model object
            The code which raises any necessary errors.
        """
        rank = arg.rank
        error_code = ()
        dtype = arg.dtype
        if isinstance(dtype, CustomDataType):
            python_cls_base = self.scope.find(dtype.name, "classes", raise_if_missing=True)
            type_check_condition = PyObject_TypeCheck(py_obj, python_cls_base.type_object)
        elif isinstance(dtype, StringType):
            type_check_condition = Ne(PyUnicode_Check(py_obj), convert_to_literal(0))
        elif rank == 0:
            try:
                cast_function = check_type_registry[dtype]
            except KeyError:
                raise TypeError(f"Can't check the type of {dtype}") from None
            func = FunctionDef(
                name=cast_function,
                body=[],
                arguments=[FunctionDefArgument(Variable(PythonObjectType(), name="o", memory_handling="alias"))],
                results=FunctionDefResult(Variable(NumpyBoolType(), name="v")),
            )

            type_check_condition = func(py_obj)
            if native_scalar_check is not None:
                native_func = FunctionDef(
                    name=native_scalar_check,
                    body=[],
                    arguments=[FunctionDefArgument(Variable(PythonObjectType(), name="o", memory_handling="alias"))],
                    results=FunctionDefResult(Variable(NumpyBoolType(), name="v")),
                )
                type_check_condition = Or(type_check_condition, native_func(py_obj))
        elif isinstance(arg.class_type, NumpyNDArrayType):
            try:
                type_ref = numpy_dtype_registry[dtype]
            except KeyError:
                raise TypeError(f"Can't check the type of an array of {dtype}") from None

            # order/contiguity flag
            if not arg.class_type.allows_strides:
                if rank == 1:
                    flag = require_any_contiguous
                elif arg.order == "F":
                    flag = require_f_contiguous
                else:
                    flag = require_c_contiguous
            elif rank == 1:
                flag = no_order_check
            elif arg.order == "F":
                flag = numpy_flag_f_contig
            else:
                flag = numpy_flag_c_contig

            allow_empty = convert_to_literal(allow_empty_arrays)

            if raise_error:
                type_check_condition = pyarray_check(
                    CStrStr(convert_to_literal(arg.name)),
                    py_obj,
                    type_ref,
                    convert_to_literal(rank),
                    flag,
                    allow_empty,
                )
            else:
                type_check_condition = is_numpy_array(py_obj, type_ref, convert_to_literal(rank), flag, allow_empty)

        else:
            raise TypeError(f"Can't check the type of an array of {arg.class_type}")

        if raise_error and not isinstance(arg.class_type, NumpyNDArrayType):
            # No error code required for arrays as the error is raised inside pyarray_check
            python_error = PyArgumentError(
                PyTypeError,
                f"Expected an argument of type {arg.class_type} for argument {arg.name}. Received {{type(arg)}}",
                arg=py_obj,
            )
            error_code = (python_error,)

        return type_check_condition, error_code

    def _get_type_check_function(self, name, args, funcs, *, allow_native_scalars=False):
        """
        Determine the flags which allow correct function to be identified from the interface.

        Each function must be identifiable by a different integer value. This value is known
        as a flag. Different parts of the flag indicate the types of different arguments.
        Take for example the following function:
        ```python
        @types('int', 'int')
        @types('float', 'float')
        def f(a, b):
            pass
        ```
        The values 0 (int) and 1 (float) would indicate the type of the argument a. In order
        to preserve this information the values which indicate the type of the argument b
        must only change the part of the flag which does not contain this information. In other
        words `flag % n_types_a = flag_a`. Therefore the values 0 (int) and 2(float) indicate
        the type of the argument b.
        We then finally have the following four options:
          1. 0 = 0 + 0 => (int,int)
          2. 1 = 1 + 0 => (float,int)
          3. 2 = 0 + 2 => (int, float)
          4. 3 = 1 + 2 => (float, float)

        of which only the first and last flags indicate acceptable arguments.

        The function returns a dictionary whose keys are the functions and whose values are
        a list of the flags which would indicate the correct types.
        In the above example we would return `{func_0 : [0,0], func_1 : [1,2]}`.
        It also returns a FunctionDef which determines the index of the chosen function.

        Parameters
        ----------
        name : str
            The name of the function to be generated.

        args : iterable of Variable
            A list containing the variables of datatype `PythonObjectType` describing the
            arguments that were passed to the function from Python.

        funcs : list of FunctionDefs
            The functions in the FunctionOverloadSet.

        Returns
        -------
        func : FunctionDef
            The function which determines the key identifying the relevant function.

        argument_type_flags : dict
            A dictionary whose keys are the functions and whose values are the integer keys
            which indicate that the function should be chosen.
        """
        args = [a.clone(a.name, is_argument=True) for a in args]
        func_scope = self.scope.new_child_scope(name, "function")
        self.scope = func_scope
        orig_funcs = [getattr(func, "original_function", func) for func in funcs]
        type_indicator = Variable(NumpyInt64Type(), self.scope.get_new_name("type_indicator"))
        is_bind_c = isinstance(funcs[0], BindCFunctionDef)

        # Initialise the argument_type_flags
        argument_type_flags = dict.fromkeys(funcs, 0)

        # Initialise type_indicator
        body = [Assign(type_indicator, convert_to_literal(0))]

        step = 1
        for i, py_arg in enumerate(args):
            # Get the relevant typed arguments from the original functions
            interface_args = [func.arguments[i].var for func in orig_funcs]
            # Get a dictionary mapping each unique type key to an example argument
            type_to_example_arg = {a.class_type: a for a in interface_args}
            # Get a list of unique keys
            possible_types = list(type_to_example_arg.keys())
            native_scalar_checks = {}
            if allow_native_scalars:
                family_counts = {}
                for possible_type in possible_types:
                    if not isinstance(possible_type, FixedSizeNumericType):
                        continue
                    primitive_type = possible_type.primitive_type
                    family_counts[type(primitive_type)] = family_counts.get(type(primitive_type), 0) + 1
                native_check_names = {
                    PrimitiveIntegerType: "PyIs_NativeInt",
                    PrimitiveFloatingPointType: "PyIs_NativeFloat",
                    PrimitiveComplexType: "PyIs_NativeComplex",
                }
                for possible_type in possible_types:
                    if not isinstance(possible_type, FixedSizeNumericType):
                        continue
                    primitive_cls = type(possible_type.primitive_type)
                    if family_counts[primitive_cls] == 1 and primitive_cls in native_check_names:
                        native_scalar_checks[possible_type] = native_check_names[primitive_cls]

            n_possible_types = len(possible_types)
            if orig_funcs[0].arguments[i].has_default:
                # The default must have a type that can be deduced so this can be checked
                # in the wrapper of the implementation
                pass
            elif n_possible_types != 1:
                # Update argument_type_flags with the index of the type key
                for func, a in zip(funcs, interface_args, strict=False):
                    index = next(i for i, p_t in enumerate(possible_types) if p_t is a.class_type) * step
                    argument_type_flags[func] += index

                # Create the type checks and incrementation of the type_indicator
                if_blocks = []
                for index, t in enumerate(possible_types):
                    check_func_call, _ = self._get_type_check_condition(
                        py_arg,
                        type_to_example_arg[t],
                        False,
                        body,
                        allow_empty_arrays=is_bind_c,
                        native_scalar_check=native_scalar_checks.get(t),
                    )
                    if_blocks.append(
                        IfSection(
                            check_func_call,
                            [AugAssign(type_indicator, "+", convert_to_literal(index * step))],
                        )
                    )
                body.append(
                    If(
                        *if_blocks,
                        IfSection(
                            convert_to_literal(True),
                            [
                                PyArgumentError(
                                    PyTypeError,
                                    f"Unexpected type for argument {interface_args[0].name}. Received {{type(arg)}}",
                                    arg=py_arg,
                                ),
                                Return(convert_to_literal(-1)),
                            ],
                        ),
                    )
                )
            else:
                check_func_call, err_body = self._get_type_check_condition(
                    py_arg,
                    type_to_example_arg.popitem()[1],
                    True,
                    body,
                    allow_empty_arrays=is_bind_c,
                    native_scalar_check=next(iter(native_scalar_checks.values()), None),
                )
                err_body = (*err_body, Return(convert_to_literal(-1)))
                if_sec = IfSection(Not(check_func_call), err_body)
                body.append(If(if_sec))

            # Update the step to ensure unique indices for each argument
            step *= n_possible_types

        body.append(Return(type_indicator))

        self.exit_scope()

        docstring = CommentBlock(
            "Assess the types. Raise an error for unexpected types and calculate an integer\n"
            + "which indicates which function should be called."
        )

        # Build the function
        func = FunctionDef(
            name,
            [FunctionDefArgument(a) for a in args],
            body,
            FunctionDefResult(type_indicator),
            docstring=docstring,
            scope=func_scope,
        )

        return func, argument_type_flags

    def _get_untranslatable_function(self, name, scope, original_function, error_msg):
        """
        Create code for a function complaining about an object which cannot be wrapped.

        Certain functions are not handled in the wrapper (e.g. private),
        This creates a wrapper function which raises NotImplementedError
        exception and returns NULL.

        Parameters
        ----------
        name : str
            The name of the generated function.

        scope : Scope
            The scope of the generated function.

        original_function : FunctionDef
           The function we were trying to wrap.

        error_msg : str
            The message to be raised in the NotImplementedError.

        Returns
        -------
        PyFunctionDef
            The new function which raises the error.
        """
        current_scope = self.scope
        self.scope = scope
        func_args = [FunctionDefArgument(self.get_new_PyObject(n)) for n in ("self", "args", "kwargs")]
        if self._error_exit_code is NIL:
            func_results = FunctionDefResult(self.get_new_PyObject("result", is_temp=True))
        else:
            func_results = FunctionDefResult(
                self.scope.get_temporary_variable(self._error_exit_code.class_type, "result")
            )
        function = PyFunctionDef(
            name=name,
            arguments=func_args,
            results=func_results,
            body=[
                PyErr_SetString(PyNotImplementedError, CStrStr(convert_to_literal(error_msg))),
                Return(self._error_exit_code),
            ],
            scope=scope,
            original_function=original_function,
        )

        self.scope = current_scope

        self.scope.insert_function(function, self.scope.get_python_name(name))

        return function

    def _save_referenced_objects(self, func, func_args):
        """
        Save any arguments passed to the wrapper which are then stored in pointers.

        If arguments are saved into pointers (e.g. inside classes) then their reference
        counter must be incremented. This prevents them being deallocated if they go
        out of scope in Python. The class must then take care to decrement their
        reference counter when it is itself deallocated to prevent a memory leak.
        The attribute `FunctionDefArgument.persistent_target` indicates whether an
        argument is a target inside the function. When it is true then additional code
        is added to the wrapper body. This code increments the reference counter for
        the argument and adds the object to a list of objects whose reference counter
        must be decremented in the class destructor.

        Parameters
        ----------
        func : FunctionDef
            The function being wrapped.
        func_args : list[FunctionDefArgument] | list[Variable]
            The arguments passed by Python to the function (self, args, kwargs).

        Returns
        -------
        list
            A list of any expressions which should be added to the wrapper body to
            add references to the arguments.
        """
        body = []
        class_arg_var = func_args[0]
        if isinstance(class_arg_var, FunctionDefArgument):
            class_arg_var = class_arg_var.var
        class_scope = class_arg_var.cls_base.scope
        for a in func.arguments:
            if a.persistent_target:
                ref_attribute = class_scope.find("referenced_objects", "variables", raise_if_missing=True)
                ref_list = ref_attribute.clone(ref_attribute.name, new_class=DottedVariable, lhs=class_arg_var)
                python_arg = self._python_object_map[a]
                if not isinstance(python_arg.dtype, PythonObjectType):
                    python_arg = ObjectAddress(PointerCast(python_arg, PyList_Append.arguments[1].var))
                append_call = PyList_Append(ref_list, python_arg)
                body.extend(
                    [
                        If(
                            IfSection(
                                Eq(append_call, convert_to_literal(-1)),
                                [Return(self._error_exit_code)],
                            )
                        )
                    ]
                )
        return body

    def _incref_return_pointer(self, ref_obj, return_var, orig_var):
        """
        Get the code necessary to return an object which references another.

        Get the code necessary to return an object which references another Python object. This is necessary when
        wrapping functions (or getters) which return pointers (e.g. attributes of a class). For these objects the
        target must not be deallocated before the returned object is no longer needed. For arrays this is achieved
        using PyArray_SetBaseObject, to save the reference. For class instances the self instance is added to the
        list of referenced objects saved in the returned class.

        Parameters
        ----------
        ref_obj : Variable
            A variable representing the class instance which must not be deallocated too early.
        return_var : Variable
            The variable which will be returned from the function.
        orig_var : Variable
            The variable which will be returned from the function as it appeared in the original code.

        Returns
        -------
        list[model object]
            Any nodes which must be printed to increase reference counts.
        """
        if isinstance(orig_var.class_type, NumpyNDArrayType):
            save_ref_call = PyArray_SetBaseObject(
                ObjectAddress(PointerCast(return_var, PyArray_SetBaseObject.arguments[0].var)),
                ObjectAddress(PointerCast(ref_obj, PyArray_SetBaseObject.arguments[1].var)),
            )
            return [
                Py_INCREF(ref_obj),
                If(
                    IfSection(
                        Lt(save_ref_call, convert_to_literal(0, dtype=CNativeInt())),
                        [Return(self._error_exit_code)],
                    )
                ),
            ]
        if isinstance(orig_var.dtype, CustomDataType):
            ref_attribute = return_var.cls_base.scope.find("referenced_objects", "variables", raise_if_missing=True)
            ref_list = ref_attribute.clone(ref_attribute.name, new_class=DottedVariable, lhs=return_var)
            save_ref_call = PyList_Append(ref_list, ObjectAddress(PointerCast(ref_obj, ref_list)))
            return [
                If(
                    IfSection(
                        Lt(save_ref_call, convert_to_literal(0, dtype=CNativeInt())),
                        [Return(self._error_exit_code)],
                    )
                )
            ]
        if isinstance(orig_var.class_type, FixedSizeNumericType):
            return []
        raise NotImplementedError(
            f"Unsure how to preserve references for attribute of type {type(orig_var.class_type)}"
        )

    def _add_object_to_mod(self, module_var, obj, name, initialised):
        """
        Get code for adding an object to the module.

        This function creates the AST nodes necessary to add an object to
        the module. This includes the creation of the success check and
        the dereferencing of any objects used.

        Parameters
        ----------
        module_var : Variable
            The variable containing the PyObject* which describes the module.

        obj : Variable
            The variable containing the PyObject* which should be added to the module.

        name : str
            The name by which the object will be known in X2py.

        initialised : list[Variable]
            A list of the variables which have had their reference counter incremented
            and must therefore decrement their counter if an error is raised.

        Returns
        -------
        list[model object]
            The code which adds the object to the module.
        """
        add_expr = PyModule_AddObject(module_var, CStrStr(convert_to_literal(name)), obj)
        if_expr = If(
            IfSection(
                Lt(add_expr, convert_to_literal(0)),
                [Py_DECREF(i) for i in initialised] + [Return(self._error_exit_code)],
            )
        )
        initialised.append(obj)
        return [if_expr, Py_INCREF(obj)]

    def _build_module_init_function(self, expr, imports, module_def_name):
        """
        Build the function that will be called when the module is first imported.

        Build the function that will be called when the module is first imported.
        This function must call any initialisation function of the underlying
        module and must add any variables to the module variable.

        Parameters
        ----------
        expr : Module
            The module of interest.

        imports : list of Import
            A list of any imports that will appear in the PyModule.

        module_def_name : str
            The name of the structure which defined the module.

        Returns
        -------
        PyModInitFunc
            The initialisation function.
        """
        mod_name = self.scope.get_python_name(getattr(expr, "original_module", expr).name)
        # The name of the init function is compulsory for the wrapper to work
        func_name = f"PyInit_{mod_name}"
        # Initialise the scope
        func_scope = self.scope.new_child_scope(func_name, "function")
        self.scope = func_scope

        for v in expr.variables:
            func_scope.insert_symbol(v.name)

        n_classes = len(expr.classes)

        # Create necessary variables
        module_var = self.get_new_PyObject("mod")
        API_var_name = self.scope.get_new_name(f"Py{mod_name}_API", object_type="wrapper")
        API_var = Variable(
            NumpyNDArrayType.get_new(BindCPointer(), 1, None, raw=True),
            API_var_name,
            shape=(n_classes,),
            cls_base=StackArrayClass,
        )
        self.scope.insert_variable(API_var)
        capsule_obj = self.get_new_PyObject(self.scope.get_new_name("c_api_object"))

        body = [
            AliasAssign(module_var, PyModule_Create(module_def_name)),
            If(IfSection(Is(module_var, NIL), [Return(self._error_exit_code)])),
        ]

        initialised = [module_var]

        # Save classes to the module variable
        for i, c in enumerate(expr.classes):
            wrapped_class = self._python_object_map[c]
            type_object = wrapped_class.type_object

            API_elem = IndexedElement(API_var, i)
            body.append(Assign(API_elem, ObjectAddress(type_object)))

        ok_code = convert_to_literal(0)

        # Save Capsule describing types (needed for dependent modules)
        body.append(AliasAssign(capsule_obj, PyCapsule_New(API_var, mod_name)))
        body.extend(self._add_object_to_mod(module_var, capsule_obj, "_C_API", initialised))

        body.append(import_array())
        import_funcs = [i.source_module.import_func for i in imports if isinstance(i.source_module, PyModule)]
        for i_func in import_funcs:
            body.append(
                If(
                    IfSection(
                        Lt(i_func(), ok_code),
                        [Py_DECREF(i) for i in initialised] + [Return(self._error_exit_code)],
                    )
                )
            )

        # Call the initialisation function
        if expr.init_func:
            body.append(expr.init_func())

        # Save classes to the module variable
        for i, c in enumerate(expr.classes):
            wrapped_class = self._python_object_map[c]
            type_object = wrapped_class.type_object
            class_name = self.scope.get_python_name(wrapped_class.name)

            ready_type = PyType_Ready(type_object)
            if_expr = If(
                IfSection(
                    Lt(ready_type, convert_to_literal(0)),
                    [Py_DECREF(i) for i in initialised] + [Return(self._error_exit_code)],
                )
            )
            body.append(if_expr)

            body.extend(self._add_object_to_mod(module_var, type_object, class_name, initialised))

        # Save module variables to the module variable
        for v in expr.variables:
            if v.is_private:
                continue
            if isinstance(v, BindCArrayVariable) and v.memory_handling == "heap":
                continue
            body.extend(self._wrap(v))
            wrapped_var = self._python_object_map[v]
            var_name = self.scope.get_python_name(v.name)
            body.extend(self._add_object_to_mod(module_var, wrapped_var, var_name, initialised))

        body.append(Return(module_var))

        self.exit_scope()

        return PyModInitFunc(func_name, body, [API_var], func_scope)

    def _build_module_import_function(self, expr):
        """
        Build the function that will be called in order to use the module from another module.

        Build the function that will be called when the module is first imported.
        This function must import the capsule created in the module initialisation.
        In order for this to work from any folder the `sys.path` list is modified to include
        the folder where the file is located (currently this is done by temporarily modifying
        an element of the list as the stable C-Python API doesn't contain any functions for
        reducing the size of lists).
        See <https://docs.python.org/3/extending/extending.html>
        for more details.

        Parameters
        ----------
        expr : Module
            The module of interest.

        Returns
        -------
        API_var : Variable
            The variable which contains the data extracted from the capsule.

        import_func : FunctionDef
            The import function.
        """
        mod_name = self.scope.get_python_name(getattr(expr, "original_module", expr).name)
        # Initialise the scope
        func_name = self.scope.get_new_name("import")

        API_var_name = self.scope.insert_symbol(f"Py{mod_name}_API", "wrapper")
        API_var = Variable(
            NumpyNDArrayType.get_new(BindCPointer(), 1, None, raw=True),
            API_var_name,
            shape=(None,),
            cls_base=StackArrayClass,
            memory_handling="alias",
        )
        self.scope.insert_variable(API_var)

        func_scope = self.scope.new_child_scope(func_name, "function")
        self.scope = func_scope

        ok_code = convert_to_literal(0, dtype=CNativeInt())
        error_code = convert_to_literal(-1, dtype=CNativeInt())
        self._error_exit_code = error_code

        # Create variables to temporarily modify the Python path so the file will be discovered
        current_path = func_scope.get_temporary_variable(PythonObjectType(), "current_path", memory_handling="alias")
        stash_path = func_scope.get_temporary_variable(PythonObjectType(), "stash_path", memory_handling="alias")

        body = [
            AliasAssign(current_path, PySys_GetObject(CStrStr(convert_to_literal("path")))),
            AliasAssign(
                stash_path,
                PyList_GetItem(current_path, convert_to_literal(0, dtype=CNativeInt())),
            ),
            Py_INCREF(stash_path),
            If(
                IfSection(
                    Eq(
                        PyList_SetItem(
                            current_path,
                            convert_to_literal(0, dtype=CNativeInt()),
                            PyUnicode_FromString(CStrStr(convert_to_literal(self._sharedlib_dirpath))),
                        ),
                        convert_to_literal(-1),
                    ),
                    [Return(self._error_exit_code)],
                )
            ),
            AliasAssign(API_var, PyCapsule_Import(mod_name)),
            If(
                IfSection(
                    Eq(
                        PyList_SetItem(
                            current_path,
                            convert_to_literal(0, dtype=CNativeInt()),
                            stash_path,
                        ),
                        convert_to_literal(-1),
                    ),
                    [Return(self._error_exit_code)],
                )
            ),
            Return(IfTernaryOperator(IsNot(API_var, NIL), ok_code, error_code)),
        ]

        result = func_scope.get_temporary_variable(CNativeInt())
        self.exit_scope()
        self._error_exit_code = NIL
        import_func = FunctionDef(
            func_name,
            (),
            body,
            FunctionDefResult(result),
            is_static=True,
            scope=func_scope,
        )

        return API_var, import_func

    def _allocate_class_instance(self, class_var, scope, is_alias):
        """
        Get all expressions necessary to allocate a new class description.

        Get all expressions necessary to allocate a new class description, this includes allocating
        the object itself, creating the list of referenced_objects and saving the alias status.

        Parameters
        ----------
        class_var : Variable
            The variable where the class instance is stored.

        scope : Scope
            The scope of the class (containing the class attributes).

        is_alias : bool
            A boolean indicating if an alias is being stored.

        Returns
        -------
        list[model object]
            A list of expressions necessary to allocate a new class description.
        """
        # Get the list of referenced objects
        ref_attribute = scope.find("referenced_objects", "variables", raise_if_missing=True)
        ref_list = ref_attribute.clone(ref_attribute.name, new_class=DottedVariable, lhs=class_var)

        # Get alias attribute
        attribute = scope.find("is_alias", "variables", raise_if_missing=True)
        alias_bool = attribute.clone(attribute.name, new_class=DottedVariable, lhs=class_var)

        alias_val = convert_to_literal(True) if is_alias else convert_to_literal(False)

        return [
            Allocate(class_var, shape=None, status="unallocated"),
            AliasAssign(ref_list, PyList_New()),
            Assign(alias_bool, alias_val),
        ]

    def _get_class_allocator(self, class_dtype, func=None):
        """
        Create the allocator for the class.

        Create a function which will allocate the memory for the class instance. This
        is equivalent to the `__new__` function.

        Parameters
        ----------
        class_dtype : DataType
            The datatype of the class being translated.

        func : FunctionDef, optional
            The function which provides a new instance of the class.

        Returns
        -------
        PyFunctionDef
            A function that can be called to create the class instance.
        """
        if func:
            func_name = self.scope.get_new_name(f"{func.name}__wrapper", object_type="wrapper")
        else:
            func_name = self.scope.get_new_name(f"{class_dtype.name}__new__wrapper")
        func_scope = self.scope.new_child_scope(func_name, "function")
        self.scope = func_scope

        self_var = Variable(
            PythonTypeObjectType(),
            name=self.scope.get_new_name("self"),
            memory_handling="alias",
        )
        self.scope.insert_variable(self_var, "self")
        func_args = [self_var] + [self.get_new_PyObject(n) for n in ("args", "kwargs")]
        func_args = [FunctionDefArgument(a) for a in func_args]

        func_results = FunctionDefResult(self.get_new_PyObject("result", is_temp=True))

        # Get the results of the PyFunctionDef
        python_result_var = self.get_new_PyObject("result_obj", class_dtype)
        scope = python_result_var.cls_base.scope
        attribute = scope.find("instance", "variables", raise_if_missing=True)
        c_res = attribute.clone(attribute.name, new_class=DottedVariable, lhs=python_result_var)

        body = self._allocate_class_instance(python_result_var, scope, False)

        if func:
            body.append(AliasAssign(c_res, func()))
        else:
            result_name = self.scope.get_new_name("result")
            result = Variable(class_dtype, result_name)
            body.append(Allocate(c_res, shape=None, status="unallocated", like=result))

        body.append(Return(PointerCast(python_result_var, func_results.var)))

        self.exit_scope()

        return PyFunctionDef(
            func_name,
            func_args,
            body,
            func_results,
            scope=func_scope,
            original_function=None,
        )

    def _get_class_initialiser(self, init_function, cls_dtype):
        """
        Create the constructor for the class.

        Create a function which will initialise the class. This function creates
        the `__new__` function to allocate the memory which stores the class
        instance and calls the `__init__` function.

        Parameters
        ----------
        init_function : FunctionDef
            The `__init__` function in the translated class.

        cls_dtype : DataType
            The datatype of the class being translated.

        Returns
        -------
        new_function : PyFunctionDef
            A function that can be called to create the class instance.

        init_function : PyFunctionDef
            A function that can be called to create the class instance.
        """
        original_func = getattr(init_function, "original_function", init_function)
        func_name = self.scope.get_new_name(f"{cls_dtype.name}__init__wrapper")
        func_scope = self.scope.new_child_scope(func_name, "function")
        self.scope = func_scope
        self._error_exit_code = convert_to_literal(-1, dtype=CNativeInt())

        isinstance(init_function, BindCFunctionDef)

        # Handle un-wrappable functions
        if any(isinstance(a.var, FunctionAddress) for a in init_function.arguments):
            self.exit_scope()
            warnings.warn("Functions with functions as arguments will not be callable from Python", stacklevel=2)
            return self._get_untranslatable_function(
                func_name,
                func_scope,
                init_function,
                "Cannot pass a function as an argument",
            )

        # Add the variables to the expected symbols in the scope
        for a in init_function.arguments:
            a_var = a.var
            func_scope.insert_symbol(getattr(a_var, "original_var", a_var).name)

        # Get variables describing the arguments and results that are seen from Python
        python_args = init_function.arguments

        # Get the arguments of the PyFunctionDef
        func_args, body = self._unpack_python_args(python_args, cls_dtype)
        func_args = [FunctionDefArgument(a) for a in func_args]

        # Get the results of the PyFunctionDef
        python_result_variable = Variable(CNativeInt(), self.scope.get_new_name(), is_temp=True)

        # Get the code required to extract the C-compatible arguments from the Python arguments
        wrapped_args = [self._visit(a) for a in python_args]
        body += [line for arg in wrapped_args for line in arg["body"]]

        # Get the arguments and results which should be used to call the c-compatible function
        func_call_args = [ca for a in wrapped_args for ca in a["args"]]

        body.extend(self._save_referenced_objects(init_function, func_args))

        # Call the C-compatible function
        body.append(init_function(*func_call_args))

        # Pack the Python compatible results of the function into one argument.
        func_results = FunctionDefResult(python_result_variable)
        body.append(Return(convert_to_literal(0, dtype=CNativeInt())))

        self.exit_scope()
        for a in python_args:
            if not a.bound_argument:
                self._python_object_map.pop(a)

        function = PyFunctionDef(
            func_name,
            func_args,
            body,
            func_results,
            scope=func_scope,
            docstring=init_function.docstring,
            original_function=original_func,
        )

        self.scope.insert_function(function, func_scope.get_python_name(func_name))
        self._python_object_map[init_function] = function
        self._error_exit_code = NIL

        return function

    def _get_class_destructor(self, del_function, cls_dtype, wrapper_scope):
        """
        Create the destructor for the class.

        Create a function which will act as a destructor for the class. This
        function calls the `__del__` function and frees the memory allocated
        to store the class instance.

        Parameters
        ----------
        del_function : FunctionDef
            The `__del__` function in the translated class.

        cls_dtype : DataType
            The datatype of the class being translated.

        wrapper_scope : Scope
            The scope for the wrapped version of the class.

        Returns
        -------
        PyFunctionDef
            A function that can be called to destroy the class instance.
        """
        original_func = getattr(del_function, "original_function", del_function)
        func_name = self.scope.get_new_name(f"{cls_dtype.name}__del__wrapper")
        func_scope = self.scope.new_child_scope(func_name, "function")
        self.scope = func_scope

        # Add the variables to the expected symbols in the scope
        for a in del_function.arguments:
            func_scope.insert_symbol(a.var.name)
        func_arg = self.get_new_PyObject("self", cls_dtype)

        attribute = wrapper_scope.find("instance", "variables")
        c_obj = attribute.clone(attribute.name, new_class=DottedVariable, lhs=func_arg)

        attribute = wrapper_scope.find("is_alias", "variables")
        is_alias = attribute.clone(attribute.name, new_class=DottedVariable, lhs=func_arg)

        if isinstance(del_function, BindCFunctionDef):
            body = [del_function(c_obj)]
        else:
            body = [del_function(c_obj), Deallocate(c_obj)]
        body.append(AliasAssign(c_obj, NIL))
        body = [If(IfSection(Not(is_alias), body))]

        # Get the list of referenced objects
        ref_attribute = wrapper_scope.find("referenced_objects", "variables", raise_if_missing=True)
        ref_list = ref_attribute.clone(ref_attribute.name, new_class=DottedVariable, lhs=func_arg)

        body.extend([Py_DECREF(ref_list), Deallocate(func_arg)])

        self.exit_scope()

        function = PyFunctionDef(
            func_name,
            [FunctionDefArgument(func_arg)],
            body,
            scope=func_scope,
            original_function=original_func,
        )

        self.scope.insert_function(function, func_scope.get_python_name(func_name))
        self._python_object_map[del_function] = function

        return function

    def _get_array_parts(self, orig_var, collect_arg):
        """
        Get AST nodes describing the extraction of the data pointer, shape, and strides from a Python array object.

        Get AST nodes describing the extraction of the data pointer, shape, and strides from a Python array object.
        These nodes as well as the new objects can then be packed into a structure or passed directly to a function
        depending on the target language.

        Parameters
        ----------
        orig_var : Variable | IndexedElement
            An object representing the variable or an element of the variable from the
            FunctionDefArgument being wrapped.

        collect_arg : Variable
            A variable with type PythonObject* holding the Python argument from which the
            C-compatible argument should be collected.

        Returns
        -------
        dict[str, Any]
            A dictionary with the keys:
             - body : a list containing the AST nodes which extract the data pointer, shape, and strides.
             - data : a Variable describing a pointer in which the data is stored.
             - shape : a Variable describing a stack array in which the shape information is stored.
             - strides : a Variable describing a stack array in which the strides are stored.
        """
        pyarray_collect_arg = PointerCast(collect_arg, Variable(NumpyArrayObjectType(), "_", memory_handling="alias"))
        data_var = Variable(
            VoidType(),
            self.scope.get_new_name(orig_var.name + "_data"),
            memory_handling="alias",
        )
        base_shape_var = Variable(
            NumpyNDArrayType.get_new(NumpyInt64Type(), 1, None, raw=True),
            self.scope.get_new_name(orig_var.name + "_base_shape"),
            shape=(orig_var.rank,),
        )
        ubound_var = Variable(
            NumpyNDArrayType.get_new(NumpyInt64Type(), 1, None, raw=True),
            self.scope.get_new_name(orig_var.name + "_ubound"),
            shape=(orig_var.rank,),
        )
        stride_var = Variable(
            NumpyNDArrayType.get_new(NumpyInt64Type(), 1, None, raw=True),
            self.scope.get_new_name(orig_var.name + "_strides"),
            shape=(orig_var.rank,),
        )
        self.scope.insert_variable(data_var)
        self.scope.insert_variable(base_shape_var)
        self.scope.insert_variable(ubound_var)
        self.scope.insert_variable(stride_var)

        get_data = AliasAssign(data_var, PyArray_DATA(ObjectAddress(pyarray_collect_arg)))
        get_strides_and_shape = get_strides_and_shape_from_numpy_array(
            ObjectAddress(collect_arg),
            base_shape_var,
            ubound_var,
            stride_var,
            convert_to_literal(orig_var.order != "F"),
        )

        body = [get_data, get_strides_and_shape]

        return {
            "body": body,
            "data": data_var,
            "shape": base_shape_var,
            "ubounds": ubound_var,
            "strides": stride_var,
        }

    def _call_wrapped_function(self, func, args, results):
        """
        Call the wrapped function.

        Call the wrapped function. The call is either a FunctionCall, an Assign or
        an AliasAssign depending on the number of results and the return type.

        Parameters
        ----------
        func : FunctionDef
            The function being wrapped.
        args : iterable[model object]
            The arguments passed to the wrapped function.
        results : iterable[model object]
            The results returned from the wrapped function.

        Returns
        -------
        FunctionCall | Assign | AliasAssign
            An AST node describing the function call.
        """
        n_results = len(results)
        if n_results == 0:
            return func(*args)
        if isinstance(results, PythonTuple):
            return Assign(results, func(*args))
        if n_results == 1:
            res = results[0]
            func_call = func(*args)
            if func_call.is_alias:
                if isinstance(res, PointerCast):
                    res = res.obj
                if isinstance(res, ObjectAddress):
                    res = res.obj
                return AliasAssign(res, func_call)
            return Assign(res, func_call)
        return Assign(results, func(*args))

    def _project_python_return(self, func, original_func, native_py_results, native_owned_results):
        output_items = []
        output_owned = []
        native_index = 0

        if original_func.results.var is not NIL:
            output_items.append(native_py_results[native_index])
            output_owned.append(native_owned_results[native_index])
            native_index += 1

        visible_outputs = self._visible_output_argument_objects(func)
        for argument in original_func.arguments:
            orig_var = argument.var
            if argument.bound_argument or getattr(orig_var, "intent", "in") != "out":
                continue
            visible_object = visible_outputs.get(orig_var)
            if visible_object is not None:
                output_items.append(visible_object)
                output_owned.append(False)
            else:
                output_items.append(native_py_results[native_index])
                output_owned.append(native_owned_results[native_index])
                native_index += 1

        if not output_items:
            return {
                "body": [Py_INCREF(Py_None)],
                "result": Py_None,
                "owned_result": False,
            }
        if len(output_items) == 1:
            if not output_owned[0]:
                return {
                    "body": [Py_INCREF(output_items[0])],
                    "result": output_items[0],
                    "owned_result": False,
                }
            return {"body": [], "result": output_items[0], "owned_result": True}

        tuple_result = self.get_new_PyObject("result_obj")
        body = [AliasAssign(tuple_result, PyTuple_Pack(*(ObjectAddress(item) for item in output_items)))]
        body.append(If(IfSection(Is(tuple_result, NIL), [Return(self._error_exit_code)])))
        body.extend(Py_DECREF(item) for item, owned in zip(output_items, output_owned, strict=False) if owned)
        return {"body": body, "result": tuple_result, "owned_result": True}

    def _visible_output_argument_objects(self, func):
        outputs = {}
        for argument in func.arguments:
            var = argument.var
            orig_var = getattr(var, "original_var", var)
            if getattr(orig_var, "intent", "in") == "out":
                outputs[orig_var] = self._python_object_map[argument]
        return outputs

    def connect_pointer_targets(self, orig_var, python_res, funcdef, is_bind_c):
        """
        Get the code to connect pointers to their targets.

        Get the code to connect pointers to their targets. The connection is done via reference
        counting to ensure that the target is not cleaned by the garbage collector before the
        pointer.

        Parameters
        ----------
        orig_var : Variable
            The result of the function being wrapped.
        python_res : Variable
            The Python accessible result of the function being wrapped.
        funcdef : FunctionDef
            The function being wrapped.
        is_bind_c : bool
            True if the code is translated from a C-compatible language. False if the
            translated code is in C.

        Returns
        -------
        list
            Any nodes which must be printed to increase reference counts.
        """
        python_args = funcdef.arguments
        arg_targets = funcdef.result_pointer_map.get(orig_var, ())
        n_targets = len(arg_targets)
        if n_targets == 1:
            collect_arg = self._python_object_map[python_args[arg_targets[0]]]
            return self._incref_return_pointer(collect_arg, python_res, orig_var)
        if n_targets > 1:
            if isinstance(orig_var.class_type, NumpyNDArrayType):
                raise RuntimeError(
                    f"Can't determine the pointer target for the return object {orig_var}. "
                    "Please avoid calling this function to prevent accidental creation of dangling pointers."
                )
            body = []
            for t in arg_targets:
                collect_arg = self._python_object_map[python_args[t]]
                body.extend(self._incref_return_pointer(collect_arg, python_res, orig_var))
            return body
        return []

    # --------------------------------------------------------------------------------------------------------------------------------------------

    def _visit_Module(self, expr):
        """
        Build a `PyModule` from a `Module`.

        Create a `PyModule` which wraps a C-compatible `Module`.

        Parameters
        ----------
        expr : Module
            The module which can be called from C.

        Returns
        -------
        PyModule
            The module which can be called from Python.
        """
        # Define scope
        scope = expr.scope
        original_mod = getattr(expr, "original_module", expr)
        original_mod_name = original_mod.scope.get_python_name(original_mod.name)

        mod_scope = Scope(
            name=original_mod_name,
            used_symbols=scope.local_used_symbols.copy(),
            original_symbols=scope.python_names.copy(),
            scope_type="module",
        )
        self.scope = mod_scope

        imports = [self._visit(i) for i in getattr(expr, "original_module", expr).imports]
        imports = [i for i in imports if i]

        # Ensure all class types are declared
        for c in expr.classes:
            name = c.name
            python_name = c.scope.get_python_name(name)
            struct_name = self.scope.get_new_name(f"Py{python_name}Object")
            dtype = DataTypeFactory(
                struct_name,
                self.scope.get_python_name(struct_name),
                BaseClass=WrapperCustomDataType,
            )()

            type_name = self.scope.get_new_name(f"Py{python_name}Type")
            wrapped_class = PyClassDef(
                c,
                struct_name,
                type_name,
                self.scope.new_child_scope(name, "class"),
                docstring=self._class_docstring(c),
                class_type=dtype,
            )

            orig_cls_dtype = c.scope.parent_scope.cls_constructs[python_name]
            self._python_object_map[c] = wrapped_class
            self._python_object_map[orig_cls_dtype] = dtype

            self.scope.insert_class(wrapped_class, python_name)

        # Wrap classes
        classes = [self._visit(i) for i in expr.classes]

        # Wrap functions
        funcs_to_wrap = [f for f in expr.funcs if f not in (expr.init_func, expr.free_func)]
        funcs_to_wrap = [f for f in funcs_to_wrap if f.is_semantic and not f.is_private]

        # Add any functions removed by the Fortran printer
        removed_functions = getattr(expr, "removed_functions", None)
        if removed_functions:
            funcs_to_wrap.extend(removed_functions)

        funcs = [self._visit(f) for f in funcs_to_wrap]
        if isinstance(expr, BindCModule):
            funcs.extend(
                self._get_allocatable_module_array_getter(variable)
                for variable in expr.variable_wrappers
                if variable.memory_handling == "heap"
            )

        # Wrap interfaces
        interfaces = [self._visit(i) for i in expr.overload_sets]

        module_def_name = self.scope.get_new_name("module")
        init_func = self._build_module_init_function(expr, imports, module_def_name)

        API_var, import_func = self._build_module_import_function(expr)

        self.exit_scope()

        if not isinstance(expr, BindCModule):
            imports.append(Import(mod_scope.get_python_name(expr.name), expr))
        original_mod_name = mod_scope.get_python_name(original_mod.name)
        return PyModule(
            original_mod_name,
            [API_var],
            funcs,
            imports=imports,
            overload_sets=interfaces,
            classes=classes,
            scope=mod_scope,
            init_func=init_func,
            import_func=import_func,
            module_def_name=module_def_name,
        )

    def _visit_BindCModule(self, expr):
        """
        Build a `PyModule` from a `BindCModule`.

        Create a `PyModule` which wraps a C-compatible `BindCModule`. This function calls the
        more general `_visit_Module` however additional steps are required to ensure that the
        Fortran functions and variables are declared in C.

        Parameters
        ----------
        expr : Module
            The module which can be called from C.

        Returns
        -------
        PyModule
            The module which can be called from Python.
        """
        pymod = self._visit_Module(expr)

        # Add declarations for C-compatible variables
        decs = [
            Declare(v.clone(v.name.lower()), module_variable=True, external=True)
            for v in expr.variables
            if not v.is_private and isinstance(v, BindCModuleVariable)
        ]
        pymod.declarations = decs

        external_funcs = []
        # Add external functions for functions wrapping array variables
        for v in expr.variable_wrappers:
            f = v.wrapper_function
            external_funcs.append(FunctionDef(f.name, f.arguments, [], f.results, is_header=True, scope=f.scope))

        # Add external functions for normal functions
        external_funcs.extend(
            FunctionDef(
                f.name.lower(),
                f.arguments,
                [],
                f.results,
                is_header=True,
                scope=f.scope,
            )
            for f in expr.funcs
        )
        external_funcs.extend(
            FunctionDef(
                f.name.lower(),
                f.arguments,
                [],
                f.results,
                is_header=True,
                scope=f.scope,
            )
            for i in expr.overload_sets
            for f in i.functions
        )

        for c in expr.classes:
            m = c.new_func
            external_funcs.append(FunctionDef(m.name, m.arguments, [], m.results, is_header=True, scope=m.scope))
            for m in c.methods:
                external_funcs.append(
                    FunctionDef(
                        m.name,
                        m.arguments,
                        [],
                        m.results,
                        is_header=True,
                        scope=m.scope,
                    )
                )
            for i in c.overload_sets:
                for f in i.functions:
                    external_funcs.append(
                        FunctionDef(
                            f.name,
                            f.arguments,
                            [],
                            f.results,
                            is_header=True,
                            scope=f.scope,
                        )
                    )
            for a in c.attributes:
                for f in (a.getter, a.setter):
                    if f:
                        external_funcs.append(
                            FunctionDef(
                                f.name,
                                f.arguments,
                                [],
                                f.results,
                                is_header=True,
                                scope=f.scope,
                            )
                        )
        pymod.external_funcs = external_funcs

        return pymod

    def _visit_FunctionOverloadSet(self, expr):
        """
        Build a `PyFunctionOverloadSet` from an `FunctionOverloadSet`.

        Create a `PyFunctionOverloadSet` which wraps a C-compatible `FunctionOverloadSet`. The `PyFunctionOverloadSet`
        should take three arguments (`self`, `args`, and `kwargs`) and return a
        `PythonObjectType`. The arguments are unpacked into multiple `PythonObjectType`s
        which are passed to `PyFunctionDef`s describing each of the internal
        `FunctionDef` objects. The appropriate `PyFunctionDef` is chosen using an
        additional function which calculates an integer type_indicator.

        Parameters
        ----------
        expr : FunctionOverloadSet
            The interface which can be called from C.

        Returns
        -------
        PyFunctionOverloadSet
            The interface which can be called from Python.

        See Also
        --------
        CToPythonWrapper._get_type_check_function : The function which defines the calculation
            of the type_indicator.
        """
        # Initialise the scope
        func_name = self.scope.get_new_name(expr.name + "_wrapper", object_type="wrapper")
        func_scope = self.scope.new_child_scope(func_name, "function")
        self.scope = func_scope
        original_funcs = expr.functions
        example_func = original_funcs[0]
        class_base = get_enclosing_class(expr)
        has_bound_arg = bool(expr.arguments and expr.arguments[0].bound_argument)
        class_dtype = class_base.class_type if class_base and has_bound_arg else None
        is_magic = expr.name in magic_overload_funcs

        for f in original_funcs:
            self._visit(f)

        # Add the variables to the expected symbols in the scope
        for a in example_func.arguments:
            func_scope.insert_symbol(a.var.name)

        # Create necessary arguments
        python_args = example_func.arguments
        if is_magic:
            func_args = self._get_python_argument_variables(python_args)
            body = []
            if expr.name == "__pow__":
                modulo = self.get_new_PyObject("modulo")
                func_args.append(modulo)
                body.append(
                    If(
                        IfSection(
                            IsNot(modulo, Py_None),
                            [
                                PyErr_SetString(
                                    PyTypeError,
                                    CStrStr(convert_to_literal("pow() with a modulus is not supported")),
                                ),
                                Return(self._error_exit_code),
                            ],
                        )
                    )
                )
        else:
            func_args, body = self._unpack_python_args(python_args, class_dtype)

        # Get python arguments which will be passed to FunctionDefs
        python_arg_objs = [self._python_object_map[a] for a in python_args]
        if expr.native_name.casefold() == "assignment(=)" and len(python_arg_objs) == 2:
            body.append(
                If(
                    IfSection(
                        Is(python_arg_objs[0], python_arg_objs[1]),
                        [
                            Py_INCREF(Py_None),
                            Return(Py_None),
                        ],
                    )
                )
            )

        type_indicator = Variable(NumpyInt64Type(), self.scope.get_new_name("type_indicator"))
        self.scope.insert_variable(type_indicator)

        self.exit_scope()

        # Determine flags which indicate argument type
        type_check_name = self.scope.get_new_name(expr.name + "_type_check", object_type="wrapper")
        type_check_func, argument_type_flags = self._get_type_check_function(
            type_check_name,
            python_arg_objs,
            original_funcs,
            allow_native_scalars=is_magic,
        )

        self.scope = func_scope
        # Build the body of the function
        body.append(Assign(type_indicator, type_check_func(*python_arg_objs)))

        functions = []
        if_sections = []
        for func, index in argument_type_flags.items():
            # Add an IfSection calling the appropriate function if the type_indicator matches the index
            wrapped_func = self._python_object_map[func]
            if_sections.append(
                IfSection(
                    Eq(type_indicator, convert_to_literal(index)),
                    [Return(wrapped_func(*python_arg_objs))],
                )
            )
            functions.append(wrapped_func)
        if_sections.append(
            IfSection(
                Eq(type_indicator, convert_to_literal(-1)),
                [Return(self._error_exit_code)],
            )
        )
        if_sections.append(
            IfSection(
                convert_to_literal(True),
                [
                    PyErr_SetString(
                        PyTypeError,
                        CStrStr(convert_to_literal("Unexpected type combination")),
                    ),
                    Return(self._error_exit_code),
                ],
            )
        )
        body.append(If(*if_sections))
        result_var = self.get_new_PyObject("result", is_temp=True)
        self.exit_scope()

        dispatcher_func = FunctionDef(
            func_name,
            [FunctionDefArgument(a) for a in func_args],
            body,
            FunctionDefResult(result_var),
            scope=func_scope,
        )
        for a in python_args:
            self._python_object_map.pop(a)

        return PyFunctionOverloadSet(func_name, functions, dispatcher_func, type_check_func, expr)

    def _visit_FunctionDef(self, expr):
        """
        Build a `PyFunctionDef` from a `FunctionDef`.

        Create a `PyFunctionDef` which wraps a C-compatible `FunctionDef`.
        The `PyFunctionDef` should take three arguments (`self`, `args`,
        and `kwargs`) and return a `PythonObjectType`. If the function is
        called from an FunctionOverloadSet then the arguments are `PythonObjectType`s
        describing each of the arguments of the C-compatible function.

        Parameters
        ----------
        expr : FunctionDef
            The function which can be called from C.

        Returns
        -------
        PyFunctionDef
            The function which can be called from Python.
        """
        original_func = getattr(expr, "original_function", expr)
        func_name = self.scope.get_new_name(expr.name + "_wrapper", object_type="wrapper")
        func_scope = self.scope.new_child_scope(func_name, "function")
        self.scope = func_scope
        original_func_name = original_func.scope.get_python_name(original_func.name)

        class_base = get_enclosing_class(expr)
        has_bound_arg = bool(expr.arguments and expr.arguments[0].bound_argument)
        class_dtype = class_base.class_type if class_base and has_bound_arg else None

        is_bind_c_function_def = isinstance(expr, BindCFunctionDef)

        if expr.is_private:
            self.exit_scope()
            return self._get_untranslatable_function(
                func_name,
                func_scope,
                expr,
                "Private functions are not accessible from python",
            )

        # Handle un-wrappable functions
        if any(isinstance(a.var, FunctionAddress) for a in expr.arguments):
            self.exit_scope()
            warnings.warn("Functions with functions as arguments will not be callable from Python", stacklevel=2)
            return self._get_untranslatable_function(
                func_name, func_scope, expr, "Cannot pass a function as an argument"
            )

        # Add the variables to the expected symbols in the scope
        for a in expr.arguments:
            a_var = a.var
            func_scope.insert_symbol(getattr(a_var, "original_var", a_var).name)

        in_overload_set = is_in_overload_set(expr)

        # Get variables describing the arguments and results that are seen from Python
        python_args = expr.arguments
        python_results = expr.results

        # Get the arguments of the PyFunctionDef
        if "property" in original_func.decorators:
            func_args = [
                self.get_new_PyObject("self_obj", dtype=class_dtype),
                func_scope.get_temporary_variable(VoidType(), memory_handling="alias"),
            ]
            self._python_object_map[python_args[0]] = func_args[0]
            func_args = [FunctionDefArgument(a) for a in func_args]
            body = []
        else:
            if in_overload_set or original_func_name in magic_binary_funcs or original_func_name == "__len__":
                func_args = [FunctionDefArgument(a) for a in self._get_python_argument_variables(python_args)]
                body = []
            else:
                func_args, body = self._unpack_python_args(python_args, class_dtype)
                func_args = [FunctionDefArgument(a) for a in func_args]

        # Get the code required to extract the C-compatible arguments from the Python arguments
        wrapped_args = [self._visit(a) for a in python_args]
        body += [line for arg in wrapped_args for line in arg["body"]]

        # Get the code required to wrap the C-compatible results into Python objects
        # This function creates variables so it must be called before extracting them from the scope.
        if original_func_name in magic_binary_funcs and original_func_name.startswith("__i"):
            res = func_args[0].var.clone(self.scope.get_new_name(func_args[0].var.name), is_argument=False)
            wrapped_results = {"c_results": [], "py_result": res, "body": []}
            body.append(AliasAssign(res, func_args[0].var))
            body.append(Py_INCREF(res))
        else:
            wrapped_results = self._extract_FunctionDefResult(python_results.var, is_bind_c_function_def, expr)

        # Get the arguments and results which should be used to call the c-compatible function
        func_call_args = [ca for a in wrapped_args for ca in a["args"]]

        # Get the names of the results collected from the C-compatible function
        body.extend(wrapped_results.get("setup", ()))
        c_results = wrapped_results["c_results"]
        python_result_variable = wrapped_results["py_result"]

        if class_dtype:
            body.extend(self._save_referenced_objects(expr, func_args))

        # Call the C-compatible function
        body.append(self._call_wrapped_function(expr, func_call_args, c_results))

        # Deallocate the C equivalent of any array arguments
        # The C equivalent is the same variable that is passed to the function unless the target language is Fortran.
        # In this case known-size stack arrays are used which are automatically deallocated when they go out of scope.
        for a in python_args:
            orig_var = a.var
            if orig_var.is_ndarray:
                v = self.scope.find(orig_var.name, category="variables", raise_if_missing=True)
                if v.is_optional:
                    body.append(If(IfSection(IsNot(v, NIL), [Deallocate(v)])))
                else:
                    body.append(Deallocate(v))

        if original_func_name == "__len__":
            self.scope.remove_variable(python_result_variable)
            python_result_variable = c_results[0]
        elif original_func_name in magic_binary_funcs and original_func_name.startswith("__i"):
            body.extend(wrapped_results["body"])
        else:
            body.extend(wrapped_results["body"])
            native_py_results = wrapped_results.get(
                "py_results",
                [] if python_result_variable is Py_None else [python_result_variable],
            )
            native_owned_results = wrapped_results.get(
                "owned_py_results",
                [True] * len(native_py_results),
            )
            projected_return = self._project_python_return(
                expr,
                original_func,
                native_py_results,
                native_owned_results,
            )
            body.extend(projected_return["body"])
            python_result_variable = projected_return["result"]
        body.extend(ai for arg in wrapped_args for ai in arg["clean_up"])

        # Pack the Python compatible results of the function into one argument.
        if original_func_name == "__len__":
            res = cast_to(python_result_variable, Py_ssize_t())
            func_results = FunctionDefResult(Variable(Py_ssize_t(), self.scope.get_new_name(), is_temp=True))
        elif python_result_variable is Py_None:
            res = Py_None
            func_results = FunctionDefResult(self.get_new_PyObject("result", is_temp=True))
        else:
            res = python_result_variable
            func_results = FunctionDefResult(res)
        body.append(Return(res))

        self.exit_scope()
        for a in python_args:
            if not a.bound_argument:
                self._python_object_map.pop(a)

        function = PyFunctionDef(
            func_name,
            func_args,
            body,
            func_results,
            scope=func_scope,
            docstring=self._function_docstring(original_func_name, expr, original_func),
            original_function=original_func,
        )

        self.scope.insert_function(function, func_scope.get_python_name(func_name))
        self._python_object_map[expr] = function

        if "property" in original_func.decorators:
            python_name = original_func.scope.get_python_name(original_func.name)
            docstring = convert_to_literal(self._property_docstring(python_name, original_func))
            return PyGetSetDefElement(python_name, function, None, CStrStr(docstring))
        return function

    def _visit_FunctionDefArgument(self, expr):
        """
        Get the code which translates a Python `FunctionDefArgument` to a C-compatible `Variable`.

        Get the code necessary to transform a Variable passed as an argument in Python, from an object with
        datatype `PythonObjectType` to a Variable that can be used in C code.

        The relevant `PythonObjectType` is collected from `self._python_object_map`.

        The necessary steps are:
        - Create a variable to store the C-compatible result.
        - Initialise the variable to any provided default value.
        - Cast the Python object to the C object using utility functions.
        - Raise any useful errors (this is not necessary if the FunctionDef is in an interface as errors are
            raised while determining which function to call).

        Parameters
        ----------
        expr : FunctionDefArgument
            The argument of the C function.

        Returns
        -------
        dict[str, Any]
            A dictionary with the keys:
             - body : a list of model objects containing the code which translates the `PythonObjectType`
                        to a C-compatible variable.
             - args : a list of Variables which should be passed to call the function being wrapped.
        """
        collect_arg = self._python_object_map[expr]
        in_overload_set = is_in_overload_set(expr)
        is_bind_c_argument = isinstance(expr.var, BindCVariable)

        orig_var = getattr(expr.var, "original_var", expr.var)
        bound_argument = expr.bound_argument

        # Collect the function which casts from a Python object to a C object
        arg_extraction = self._extract_FunctionDefArgument(orig_var, collect_arg, bound_argument, is_bind_c_argument)

        body = []
        cast = arg_extraction["body"]
        arg_vars = arg_extraction["args"]

        # Initialise to any default value
        if expr.has_default:
            if "default_init" in arg_extraction:
                for i, line in enumerate(arg_extraction["default_init"]):
                    body.insert(i, line)
            else:
                assert len(arg_vars) == 1
                arg_var = arg_vars[0]
                default_val = expr.value
                if default_val is NIL:
                    body.insert(0, AliasAssign(arg_var, default_val))
                else:
                    body.insert(0, Assign(arg_var, default_val))

        # Create any necessary type checks and errors
        if expr.has_default:
            check_func, err = self._get_type_check_condition(
                collect_arg, orig_var, True, body, allow_empty_arrays=is_bind_c_argument
            )
            body.append(
                If(
                    IfSection(
                        IsNot(collect_arg, Py_None),
                        [
                            If(
                                IfSection(check_func, cast),
                                IfSection(convert_to_literal(True), [*err, Return(self._error_exit_code)]),
                            )
                        ],
                    )
                )
            )
        elif not (in_overload_set or bound_argument):
            check_func, err = self._get_type_check_condition(
                collect_arg, orig_var, True, body, allow_empty_arrays=is_bind_c_argument
            )
            body.append(If(IfSection(Not(check_func), [*err, Return(self._error_exit_code)])))
            body.extend(cast)
        else:
            body.extend(cast)

        return {
            "body": body,
            "args": arg_vars,
            "clean_up": arg_extraction.get("clean_up", ()),
        }

    def _visit_Variable(self, expr):
        """
        Get the code which translates a C-compatible module variable to an object with datatype `PythonObjectType`.

        Get the code which translates a C-compatible module variable to an object with datatype `PythonObjectType`.
        This new object is saved into self._python_object_map. The translation is achieved using utility
        functions.

        Parameters
        ----------
        expr : Variable
            The module variable.

        Returns
        -------
        list of codegen model object
            The code which translates the Variable to a Python-compatible variable.
        """

        # Create the resulting Variable with datatype `PythonObjectType`
        py_equiv = self.scope.get_temporary_variable(PythonObjectType(), memory_handling="alias")
        # Save the Variable so it can be located later
        self._python_object_map[expr] = py_equiv

        if isinstance(expr.class_type, NumpyNDArrayType):
            # Cast the C variable into a Python variable
            typenum = numpy_dtype_registry[expr.dtype]
            data_var = DottedVariable(VoidType(), "data", memory_handling="alias", lhs=expr)
            shape_var = DottedVariable(NumpyNDArrayType.get_new(NumpyInt32Type(), 1, None, raw=True), "shape", lhs=expr)
            release_memory = False
            return [
                AliasAssign(
                    py_equiv,
                    to_pyarray(
                        convert_to_literal(expr.rank),
                        typenum,
                        data_var,
                        shape_var,
                        convert_to_literal(expr.order != "F"),
                        convert_to_literal(release_memory),
                    ),
                )
            ]
        wrapper_function = C_to_Python(expr)
        return [AliasAssign(py_equiv, wrapper_function(expr))]

    def _visit_BindCArrayVariable(self, expr):
        """
        Get the code which translates a Fortran array module variable to an object with datatype `PythonObjectType`.

        Get the code which translates a Fortran array module variable to an object with datatype `PythonObjectType`
        which can be used as a Python module variable. This new object is saved into self._python_object_map.
        Fortran arrays are not compatible with C, but objects of type `BindCArrayVariable` contain wrapper
        functions which can be used to retrieve C-compatible variables.

        The necessary steps are:
        - Create the variables necessary to retrieve array objects from Fortran.
        - Call the bind c wrapper function to initialise these objects.
        - Pack the results into a C-compatible `ndarray`.
        - Use `self._visit_Variable` to get the object with datatype `PythonObjectType`.
        - Correct the key in self._python_object_map initialised by `self._wrap_Variable`.

        Parameters
        ----------
        expr : BindCArrayVariable
            The array module variable.

        Returns
        -------
        list of codegen model object
            The code which translates the Variable to a Python-compatible variable.
        """
        v = expr.original_variable

        typenum = numpy_dtype_registry[v.dtype]
        # Get pointer to store raw array data
        data_var = self.scope.get_temporary_variable(
            dtype_or_var=VoidType(), name=v.name + "_data", memory_handling="alias"
        )
        # Create variables to store the shape of the array
        shape_var = self.scope.get_temporary_variable(
            NumpyNDArrayType.get_new(NumpyInt32Type(), 1, None, raw=True),
            name=v.name + "_size",
            shape=(v.rank,),
        )
        shape = [IndexedElement(shape_var, i) for i in range(v.rank)]
        # Get the bind_c function which wraps a fortran array and returns c objects
        var_wrapper = expr.wrapper_function
        # Call bind_c function
        call = Assign(PythonTuple(ObjectAddress(data_var), *shape), var_wrapper())

        # Create the resulting Variable with datatype `PythonObjectType`
        py_equiv = self.get_new_PyObject(f"{v.name}_obj", dtype=v.dtype)
        self._python_object_map[expr] = py_equiv

        release_memory = False
        unallocated_guard = self._return_none_if_unallocated(data_var) if expr.memory_handling == "heap" else []
        # Save the ndarray to vars_to_wrap to be handled as if it came from C
        return [
            call,
            *unallocated_guard,
            AliasAssign(
                py_equiv,
                to_pyarray(
                    convert_to_literal(v.rank),
                    typenum,
                    data_var,
                    shape_var,
                    convert_to_literal(v.order != "F"),
                    convert_to_literal(release_memory),
                ),
            ),
        ]

    def _get_allocatable_module_array_getter(self, expr):
        python_name = f"get_{self.scope.get_python_name(expr.name)}"
        wrapper_name = self.scope.get_new_name(f"{python_name}_wrapper", object_type="wrapper")
        original_name = self.scope.get_new_name(python_name, object_type="function")
        original = FunctionDef(
            original_name,
            (),
            (),
            FunctionDefResult(expr),
            scope=self.scope,
        )
        func_scope = self.scope.new_child_scope(wrapper_name, "function")
        self.scope = func_scope

        func_args, body = self._unpack_python_args(())
        body.extend(self._visit_BindCArrayVariable(expr))
        py_result = self._python_object_map.pop(expr)
        body.append(Return(py_result))
        self.exit_scope()

        return PyFunctionDef(
            wrapper_name,
            [FunctionDefArgument(arg) for arg in func_args],
            body,
            FunctionDefResult(py_result),
            scope=func_scope,
            docstring=self._module_array_getter_docstring(python_name, expr),
            original_function=original,
        )

    def _return_none_if_unallocated(self, data_ptr, shape_vars=()):
        return [
            If(
                IfSection(
                    Is(data_ptr, NIL),
                    [
                        *self._raise_memory_error_if_shape_is_nonzero(shape_vars),
                        Py_INCREF(Py_None),
                        Return(Py_None),
                    ],
                )
            )
        ]

    def _set_none_if_unallocated(self, data_ptr, py_res, shape_vars):
        return If(
            IfSection(
                Is(data_ptr, NIL),
                [
                    *self._raise_memory_error_if_shape_is_nonzero(shape_vars),
                    Py_INCREF(Py_None),
                    AliasAssign(py_res, Py_None),
                ],
            )
        )

    def _raise_memory_error_if_shape_is_nonzero(self, shape_vars):
        condition = None
        for shape_var in shape_vars:
            axis_has_extent = Ne(shape_var, convert_to_literal(0))
            condition = axis_has_extent if condition is None else Or(condition, axis_has_extent)
        if condition is None:
            return []
        return [
            If(
                IfSection(
                    condition,
                    [
                        PyErr_SetString(
                            PyMemoryError,
                            CStrStr(convert_to_literal("Unable to allocate copy-return output array.")),
                        ),
                        Return(self._error_exit_code),
                    ],
                )
            )
        ]

    def _visit_DottedVariable(self, expr):
        """
        Create all objects necessary to expose a class attribute to C.

        Create the getter and setter functions which expose the class attribute
        to C. Return these objects in a PyGetSetDefElement.
        See <https://docs.python.org/3/extending/newtypes_tutorial.html#providing-finer-control-over-data-attributes>
        for more information about the necessary prototypes.

        Parameters
        ----------
        expr : DottedVariable
            The class attribute.

        Returns
        -------
        PyGetSetDefElement
            An object which contains the new getter and setter functions that should be
            described in the array of PyGetSetDef objects.
        """
        lhs = expr.lhs
        class_type = lhs.cls_base
        python_class_type = self.scope.find(
            self.scope.get_python_name(class_type.name),
            "classes",
            raise_if_missing=True,
        )
        class_scope = python_class_type.scope

        class_ptr_attrib = class_scope.find("instance", "variables", raise_if_missing=True)

        # ----------------------------------------------------------------------------------
        #                        Create getter
        # ----------------------------------------------------------------------------------
        getter_name = self.scope.get_new_name(f"{class_type.name}_{expr.name}_getter", object_type="wrapper")
        getter_scope = self.scope.new_child_scope(getter_name, "function")
        self.scope = getter_scope
        getter_args = [
            self.get_new_PyObject("self_obj", dtype=lhs.dtype),
            getter_scope.get_temporary_variable(VoidType(), memory_handling="alias"),
        ]
        self.scope.insert_symbol(expr.name)

        class_obj = Variable(lhs.dtype, self.scope.get_new_name("self"), memory_handling="alias")
        self.scope.insert_variable(class_obj, "self")

        attrib = expr.clone(expr.name, lhs=class_obj)
        # Cast the C variable into a Python variable
        result_wrapping = self._extract_FunctionDefResult(expr.clone(expr.name, new_class=Variable), False)
        res_wrapper = result_wrapping["body"]
        new_res_val = result_wrapping["c_results"][0]
        getter_result = result_wrapping["py_result"]
        setup = result_wrapping.get("setup", ())
        if new_res_val.rank > 0:
            body = [AliasAssign(new_res_val, attrib), *res_wrapper]
        elif isinstance(expr.dtype, CustomDataType):
            if isinstance(new_res_val, PointerCast):
                new_res_val = new_res_val.obj
            body = [AliasAssign(new_res_val, attrib), *res_wrapper]
        else:
            body = [Assign(new_res_val, attrib), *res_wrapper]

        body.extend(self._incref_return_pointer(getter_args[0], getter_result, expr))

        getter_body = [
            *setup,
            AliasAssign(
                class_obj,
                PointerCast(
                    class_ptr_attrib.clone(
                        class_ptr_attrib.name,
                        new_class=DottedVariable,
                        lhs=getter_args[0],
                    ),
                    cast_type=lhs,
                ),
            ),
            *body,
            Return(getter_result),
        ]
        self.exit_scope()

        args = [FunctionDefArgument(a) for a in getter_args]
        getter = PyFunctionDef(
            getter_name,
            args,
            getter_body,
            FunctionDefResult(getter_result),
            original_function=expr,
            scope=getter_scope,
        )

        # ----------------------------------------------------------------------------------
        #                        Create setter
        # ----------------------------------------------------------------------------------
        self._error_exit_code = convert_to_literal(-1, dtype=CNativeInt())
        setter_name = self.scope.get_new_name(f"{class_type.name}_{expr.name}_setter", object_type="wrapper")
        setter_scope = self.scope.new_child_scope(setter_name, "function")
        self.scope = setter_scope
        setter_args = [
            self.get_new_PyObject("self_obj", dtype=lhs.dtype),
            self.get_new_PyObject(f"{expr.name}_obj"),
            setter_scope.get_temporary_variable(VoidType(), memory_handling="alias"),
        ]
        setter_result = FunctionDefResult(setter_scope.get_temporary_variable(CNativeInt()))
        self.scope.insert_symbol(expr.name)
        new_set_val_arg = FunctionDefArgument(expr.clone(expr.name, new_class=Variable))
        self._python_object_map[new_set_val_arg] = setter_args[1]

        if isinstance(expr.class_type, FixedSizeNumericType) or expr.is_alias:
            class_obj = Variable(lhs.dtype, self.scope.get_new_name("self"), memory_handling="alias")
            self.scope.insert_variable(class_obj, "self")

            attrib = expr.clone(expr.name, lhs=class_obj)
            wrap_arg = self._visit(new_set_val_arg)
            arg_wrapper = wrap_arg["body"]
            new_set_val = wrap_arg["args"][0]

            if expr.memory_handling == "alias":
                update = AliasAssign(attrib, new_set_val)
            else:
                update = Assign(attrib, new_set_val)

            # Cast the C variable into a Python variable
            setter_body = [
                *arg_wrapper,
                AliasAssign(
                    class_obj,
                    PointerCast(
                        class_ptr_attrib.clone(
                            class_ptr_attrib.name,
                            new_class=DottedVariable,
                            lhs=setter_args[0],
                        ),
                        cast_type=lhs,
                    ),
                ),
                *self._incref_return_pointer(setter_args[1], setter_args[0], expr.lhs),
                update,
                Return(convert_to_literal(0, dtype=CNativeInt())),
            ]
        else:
            setter_body = [
                PyErr_SetString(
                    PyAttributeError,
                    CStrStr(convert_to_literal("Can't reallocate memory via Python interface.")),
                ),
                Return(self._error_exit_code),
            ]
        self.exit_scope()

        args = [FunctionDefArgument(a) for a in setter_args]
        setter = PyFunctionDef(
            setter_name,
            args,
            setter_body,
            setter_result,
            original_function=expr,
            scope=setter_scope,
        )
        self._error_exit_code = NIL
        self._python_object_map.pop(new_set_val_arg)
        # ----------------------------------------------------------------------------------

        python_name = class_type.scope.get_python_name(expr.name)
        return PyGetSetDefElement(
            python_name,
            getter,
            setter,
            CStrStr(convert_to_literal(self._attribute_docstring(python_name, expr))),
        )

    def _visit_BindCClassProperty(self, expr):
        """
        Create a PyGetSetDefElement to expose a class attribute/property to Python.

        Create getter and setter functions which are compatible with the expected prototype for
        `PyGetSetDef` and which call the getter and setter functions contained in the
        BindCClassProperty. The result is returned in a PyGetSetDefElement.
        See <https://docs.python.org/3/extending/newtypes_tutorial.html#providing-finer-control-over-data-attributes>
        for more information about the necessary prototypes.

        Parameters
        ----------
        expr : BindCClassProperty
            The object containing the getter and setter functions to be wrapped.

        Returns
        -------
        PyGetSetDefElement
            An object which contains the new getter and setter functions that should be
            described in the array of PyGetSetDef objects.
        """
        class_type = expr.class_type
        name = expr.python_name
        # ----------------------------------------------------------------------------------
        #                        Create getter
        # ----------------------------------------------------------------------------------
        getter_name = self.scope.get_new_name(f"{class_type.name}_{name}_getter", object_type="wrapper")
        getter_scope = self.scope.new_child_scope(getter_name, "function")
        self.scope = getter_scope

        get_val_arg = expr.getter.arguments[0]
        self.scope.insert_symbol(get_val_arg.var.original_var.name)
        get_val_result = expr.getter.results

        getter_args = [
            self.get_new_PyObject("self_obj", dtype=class_type),
            getter_scope.get_temporary_variable(VoidType(), memory_handling="alias"),
        ]

        self._python_object_map[get_val_arg] = getter_args[0]

        wrapped_args = self._visit(get_val_arg)
        arg_code = wrapped_args["body"]
        class_obj = wrapped_args["args"][0]

        # Cast the C variable into a Python variable
        get_val_result_var = getattr(get_val_result, "original_function_result_variable", get_val_result.var)
        result_wrapping = self._extract_FunctionDefResult(get_val_result_var, True, expr.getter)
        res_wrapper = result_wrapping["body"]
        c_results = result_wrapping["c_results"]
        getter_result = result_wrapping["py_result"]
        setup = result_wrapping.get("setup", ())

        call = self._call_wrapped_function(expr.getter, (class_obj,), c_results)

        if isinstance(expr.getter.original_function, DottedVariable):
            wrapped_var = expr.getter.original_function
            res_wrapper.extend(self._incref_return_pointer(getter_args[0], getter_result, wrapped_var))
        else:
            wrapped_var = expr.getter.original_function.results.var

        getter_body = [*setup, *arg_code, call, *res_wrapper, Return(getter_result)]
        self.exit_scope()

        args = [FunctionDefArgument(a) for a in getter_args]
        getter = PyFunctionDef(
            getter_name,
            args,
            getter_body,
            FunctionDefResult(getter_result),
            original_function=expr.getter,
            scope=getter_scope,
        )

        # ----------------------------------------------------------------------------------
        #                        Create setter
        # ----------------------------------------------------------------------------------
        if expr.setter:
            self._error_exit_code = convert_to_literal(-1, dtype=CNativeInt())
            setter_name = self.scope.get_new_name(f"{class_type.name}_{name}_setter", object_type="wrapper")
            setter_scope = self.scope.new_child_scope(setter_name, "function")
            self.scope = setter_scope

            original_args = expr.setter.arguments
            f_wrapped_args = expr.setter.arguments

            self_arg = original_args[0]
            set_val_arg = original_args[1]
            for a in f_wrapped_args:
                self.scope.insert_symbol(a.var.name)
            self.scope.insert_symbol(self_arg.var.original_var.name)
            self.scope.insert_symbol(set_val_arg.var.original_var.name)

            setter_args = [
                self.get_new_PyObject("self_obj", dtype=class_type),
                self.get_new_PyObject(f"{name}_obj"),
                setter_scope.get_temporary_variable(VoidType(), memory_handling="alias"),
            ]
            setter_result = FunctionDefResult(setter_scope.get_temporary_variable(CNativeInt()))

            self._python_object_map[self_arg] = setter_args[0]
            self._python_object_map[set_val_arg] = setter_args[1]

            if isinstance(wrapped_var.class_type, FixedSizeNumericType) or wrapped_var.is_alias:
                wrapped_args = [self._visit(a) for a in original_args]
                arg_code = [line for arg in wrapped_args for line in arg["body"]]
                func_call_args = [ca for a in wrapped_args for ca in a["args"]]

                setter_body = [
                    *arg_code,
                    expr.setter(*func_call_args),
                    *self._save_referenced_objects(expr.setter, setter_args),
                    Return(convert_to_literal(0, dtype=CNativeInt())),
                ]
            else:
                setter_body = [
                    PyErr_SetString(
                        PyAttributeError,
                        CStrStr(convert_to_literal("Can't reallocate memory via Python interface.")),
                    ),
                    Return(self._error_exit_code),
                ]
            self.exit_scope()

            args = [FunctionDefArgument(a) for a in setter_args]
            setter = PyFunctionDef(
                setter_name,
                args,
                setter_body,
                setter_result,
                original_function=expr,
                scope=setter_scope,
            )
        else:
            setter = None

        self._error_exit_code = NIL

        docstring = convert_to_literal(
            "\n".join(expr.docstring.comments)
            if expr.docstring
            else self._attribute_docstring(expr.python_name, wrapped_var)
        )
        return PyGetSetDefElement(expr.python_name, getter, setter, CStrStr(docstring))

    def _visit_ClassDef(self, expr):
        """
        Get the code which exposes a class definition to Python.

        Get the code which exposes a class definition to Python.

        Parameters
        ----------
        expr : ClassDef
            The class definition being wrapped.

        Returns
        -------
        PyClassDef
            The wrapped class definition.
        """
        name = expr.name
        python_name = expr.scope.get_python_name(name)

        bound_class = isinstance(expr, BindCClassDef)

        orig_cls_dtype = expr.scope.parent_scope.cls_constructs[python_name]
        wrapped_class = self._python_object_map[expr]

        orig_scope = expr.scope

        for f in expr.methods:
            if not f.is_semantic:
                continue
            orig_f = getattr(f, "original_function", f)
            name = orig_f.name
            python_name = orig_scope.get_python_name(name)
            if python_name == "__del__":
                wrapped_class.add_new_method(self._get_class_destructor(f, orig_cls_dtype, wrapped_class.scope))
            elif python_name == "__init__":
                wrapped_class.add_new_method(self._get_class_initialiser(f, orig_cls_dtype))
            elif python_name in (*magic_binary_funcs, "__len__"):
                wrapped_class.add_new_magic_method(self._visit(f))
            elif "property" in f.decorators:
                wrapped_class.add_property(self._visit(f))
            else:
                wrapped_class.add_new_method(self._visit(f))

        for i in expr.overload_sets:
            for f in i.functions:
                self._visit(f)
            wrapped_overload_set = self._visit(i)
            if i.name in magic_overload_funcs:
                wrapped_class.add_new_magic_method(wrapped_overload_set)
            else:
                wrapped_class.add_new_overload_set(wrapped_overload_set)

        if bound_class:
            wrapped_class.add_alloc_method(self._get_class_allocator(orig_cls_dtype, expr.new_func))
        else:
            wrapped_class.add_alloc_method(self._get_class_allocator(orig_cls_dtype))

        # Pseudo-self variable is useful for pre-defined attributes which are not DottedVariables
        pseudo_self = Variable(expr.class_type, "self", cls_base=expr)
        for a in expr.attributes:
            if isinstance(a.class_type, TupleType):
                raise NotImplementedError("Tuples cannot yet be exposed to Python.")

            if bound_class or not a.is_private:
                if isinstance(a, DottedVariable | BindCClassProperty):
                    wrapped_class.add_property(self._visit(a))
                else:
                    wrapped_class.add_property(self._visit(a.clone(a.name, new_class=DottedVariable, lhs=pseudo_self)))

        return wrapped_class

    def _visit_Import(self, expr):
        """
        Examine an Import statement and collect any relevant objects.

        Examine an Import statement used in the module being wrapped. If it imports a class
        from a module then a PyClassDef is added to the scope imports to ensure that its
        description is available for functions wishing to use this type for an argument
        or return value.

        Parameters
        ----------
        expr : Import
            The import found in the module being wrapped.

        Returns
        -------
        Import | None
            The import needed in the wrapper, or None if none is necessary.
        """
        # Imports do not use collision handling as there is not enough context available.
        # This should be fixed when stub files and proper pickling is added
        import_wrapper = False
        import_scope = None
        for as_name in expr.target:
            t = as_name.object
            if isinstance(t, ClassDef):
                if import_scope is None:
                    import_scope = Scope(
                        name=expr.source_module.name,
                        used_symbols=expr.source_module.scope.local_used_symbols.copy(),
                        original_symbols=expr.source_module.scope.python_names.copy(),
                        scope_type="module",
                    )
                name = t.scope.get_python_name(t.name)
                struct_name = import_scope.get_new_name(f"Py{name}Object")
                dtype = DataTypeFactory(struct_name, struct_name, BaseClass=WrapperCustomDataType)()
                type_name = import_scope.get_new_name(f"Py{name}Type")
                wrapped_class = PyClassDef(
                    t,
                    struct_name,
                    type_name,
                    Scope(name=name, scope_type="class"),
                    class_type=dtype,
                )
                self._python_object_map[t] = wrapped_class
                self._python_object_map[t.class_type] = dtype
                self.scope.imports["classes"][name] = wrapped_class
                import_wrapper = True

        if import_wrapper:
            wrapper_name = f"{expr.source}_wrapper"
            mod_spoof_scope = Scope(name=expr.source_module.name, scope_type="module")
            mod_import_func = FunctionDef(
                mod_spoof_scope.get_new_name("import"),
                (),
                (),
                FunctionDefResult(Variable(CNativeInt(), "_", is_temp=True)),
            )
            mod_spoof = PyModule(
                expr.source_module.name,
                (),
                (),
                scope=mod_spoof_scope,
                module_def_name=mod_spoof_scope.get_new_name("module"),
                import_func=mod_import_func,
            )
            return Import(wrapper_name, AsName(mod_spoof, expr.source), mod=mod_spoof)
        return None

    def _extract_FunctionDefArgument(self, orig_var, collect_arg, bound_argument, is_bind_c_argument, *, arg_var=None):
        """
        Extract the C-compatible FunctionDefArgument from the PythonObject.

        Extract the C-compatible FunctionDefArgument from the PythonObject.
        The C-compatible argument is extracted from collect_arg which holds a Python
        object into arg_var.

        The extraction is done by finding the appropriate function
        _extract_X_FunctionDefArgument for the object expr. X is the class type of the
        object expr. If this function does not exist then the method resolution order
        is used to search for other compatible _extract_X_FunctionDefArgument functions.
        If none are found then an error is raised.

        Parameters
        ----------
        orig_var : Variable | IndexedElement
            An object representing the variable or an element of the variable from the
            FunctionDefArgument being wrapped.

        collect_arg : Variable
            A variable with type PythonObject* holding the Python argument from which the
            C-compatible argument should be collected.

        bound_argument : bool
            True if the argument is the self argument of a class method. False otherwise.
            This should always be False for this function.

        is_bind_c_argument : bool
            True if the argument was defined in a BindCFunctionDef. False otherwise.

        arg_var : Variable | IndexedElement, optional
            A variable or an element of the variable representing the argument that
            will be passed to the low-level function call.

        Returns
        -------
        dict
            A dictionary describing the objects necessary to access the argument.
        """
        class_type = orig_var.class_type

        classes = type(class_type).__mro__
        for cls in classes:
            annotation_method = f"_extract_{cls.__name__}_FunctionDefArgument"
            if hasattr(self, annotation_method):
                return getattr(self, annotation_method)(
                    orig_var,
                    collect_arg,
                    bound_argument,
                    is_bind_c_argument,
                    arg_var=arg_var,
                )

        # Unknown object, we raise an error.
        raise NotImplementedError(f"Wrapping function arguments is not implemented for type {class_type}.")

    def _extract_FixedSizeType_FunctionDefArgument(
        self, orig_var, collect_arg, bound_argument, is_bind_c_argument, *, arg_var=None
    ):
        """
        Extract the C-compatible scalar FunctionDefArgument from the PythonObject.

        Extract the C-compatible scalar FunctionDefArgument from the PythonObject.
        The C-compatible argument is extracted from collect_arg which holds a Python
        object into arg_var.

        The extraction is done by calling a function from the C-Python API. These functions
        are indexed in the dictionary `py_to_c_registry`.

        Parameters
        ----------
        orig_var : Variable | IndexedElement
            An object representing the variable or an element of the variable from the
            FunctionDefArgument being wrapped.

        collect_arg : Variable
            A variable with type PythonObject* holding the Python argument from which the
            C-compatible argument should be collected.

        bound_argument : bool
            True if the argument is the self argument of a class method. False otherwise.
            This should always be False for this function.

        is_bind_c_argument : bool
            True if the argument was defined in a BindCFunctionDef. False otherwise.

        arg_var : Variable | IndexedElement
            A variable or an element of the variable representing the argument that
            will be passed to the low-level function call.

        Returns
        -------
        dict
            A dictionary describing the objects necessary to access the argument.
        """
        assert not bound_argument
        if arg_var is None:
            class_type = orig_var.class_type
            if isinstance(class_type, FinalType):
                class_type = class_type.underlying_type
            kwargs = {
                "new_class": Variable,
                "is_argument": False,
                "class_type": class_type,
            }
            if getattr(orig_var, "is_optional", False):
                kwargs["memory_handling"] = "alias"
            arg_var = orig_var.clone(
                self.scope.get_expected_name(orig_var.name),
                **kwargs,
            )
            self.scope.insert_variable(arg_var, orig_var.name)

        dtype = orig_var.dtype
        try:
            cast_function = py_to_c_registry[(dtype.primitive_type, dtype.precision)]
        except KeyError:
            raise TypeError(f"No Python-to-C cast registered for {dtype}") from None
        cast_func = FunctionDef(
            name=cast_function,
            body=[],
            arguments=[FunctionDefArgument(Variable(PythonObjectType(), name="o", memory_handling="alias"))],
            results=FunctionDefResult(Variable(dtype, name="v")),
        )

        body = [Assign(arg_var, cast_func(collect_arg))]

        if getattr(orig_var, "is_optional", False):
            memory_var = self.scope.get_temporary_variable(
                arg_var,
                name=arg_var.name + "_memory",
                is_optional=False,
                memory_handling="stack",
            )
            body.insert(0, AliasAssign(arg_var, memory_var))

        return {"body": body, "args": [arg_var]}

    def _extract_CustomDataType_FunctionDefArgument(
        self, orig_var, collect_arg, bound_argument, is_bind_c_argument, *, arg_var=None
    ):
        """
        Extract the C-compatible class FunctionDefArgument from the PythonObject.

        Extract the C-compatible class FunctionDefArgument from the PythonObject.
        The C-compatible argument is extracted from collect_arg which holds a Python
        object into arg_var.

        The extraction is done by accessing the pointer from the `instance` attribute of the
        X2py generated class definition.

        Parameters
        ----------
        orig_var : Variable | IndexedElement
            An object representing the variable or an element of the variable from the
            FunctionDefArgument being wrapped.

        collect_arg : Variable
            A variable with type PythonObject* holding the Python argument from which the
            C-compatible argument should be collected.

        bound_argument : bool
            True if the argument is the self argument of a class method. False otherwise.
            This should always be False for this function.

        is_bind_c_argument : bool
            True if the argument was defined in a BindCFunctionDef. False otherwise.

        arg_var : Variable | IndexedElement, optional
            A variable or an element of the variable representing the argument that
            will be passed to the low-level function call.

        Returns
        -------
        dict
            A dictionary describing the objects necessary to access the argument.
        """
        if arg_var is None:
            kwargs = {"is_argument": False}
            kwargs["memory_handling"] = "alias"
            if is_bind_c_argument:
                kwargs["class_type"] = VoidType()

            arg_var = orig_var.clone(
                self.scope.get_expected_name(orig_var.name),
                new_class=Variable,
                **kwargs,
            )
            self.scope.insert_variable(arg_var, orig_var.name)

        dtype = orig_var.dtype
        python_cls_base = self.scope.find(dtype.name, "classes", raise_if_missing=True)
        scope = python_cls_base.scope
        attribute = scope.find("instance", "variables", raise_if_missing=True)
        if bound_argument:
            cast_type = collect_arg
            cast = []
        else:
            cast_type = Variable(
                self._python_object_map[dtype],
                self.scope.get_new_name(collect_arg.name),
                memory_handling="alias",
                cls_base=self.scope.find(dtype.name, "classes", raise_if_missing=True),
            )
            self.scope.insert_variable(cast_type)
            cast = [AliasAssign(cast_type, PointerCast(collect_arg, cast_type))]
        c_res = attribute.clone(attribute.name, new_class=DottedVariable, lhs=cast_type)
        cast_c_res = PointerCast(c_res, orig_var)
        cast.append(AliasAssign(arg_var, cast_c_res))
        return {"body": cast, "args": [arg_var]}

    def _extract_NumpyNDArrayType_FunctionDefArgument(
        self, orig_var, collect_arg, bound_argument, is_bind_c_argument, *, arg_var=None
    ):
        """
        Extract the C-compatible NumPy array FunctionDefArgument from the PythonObject.

        Extract the C-compatible NumPy array FunctionDefArgument from the PythonObject.
        The C-compatible argument is extracted from collect_arg which holds a Python
        object into arg_var.

        The extraction is done by calling the function `pyarray_to_ndarray` from the stdlib.

        Parameters
        ----------
        orig_var : Variable | IndexedElement
            An object representing the variable or an element of the variable from the
            FunctionDefArgument being wrapped.

        collect_arg : Variable
            A variable with type PythonObject* holding the Python argument from which the
            C-compatible argument should be collected.

        bound_argument : bool
            True if the argument is the self argument of a class method. False otherwise.
            This should always be False for this function.

        is_bind_c_argument : bool
            True if the argument was defined in a BindCFunctionDef. False otherwise.

        arg_var : Variable | IndexedElement, optional
            A variable or an element of the variable representing the argument that
            will be passed to the low-level function call.

        Returns
        -------
        dict
            A dictionary describing the objects necessary to access the argument.
        """
        assert arg_var is None
        parts = self._get_array_parts(orig_var, collect_arg)
        body = parts["body"]
        shape = parts["shape"]
        strides = parts["strides"]
        ubounds = parts["ubounds"]
        shape_elems = [IndexedElement(shape, i) for i in range(orig_var.rank)]
        stride_elems = [IndexedElement(strides, i) for i in range(orig_var.rank)]
        ubound_elems = [IndexedElement(ubounds, i) for i in range(orig_var.rank)]
        args = [parts["data"], *shape_elems, *stride_elems]
        body.extend(self._array_shape_validation(orig_var, shape_elems))
        default_body = (
            [AliasAssign(parts["data"], NIL)]
            + [Assign(s, 0) for s in shape_elems]
            + [Assign(s, 0) for s in ubound_elems]
            + [Assign(s, 1) for s in stride_elems]
        )

        if is_bind_c_argument:
            rank = orig_var.rank
            allows_strides = orig_var.class_type.allows_strides
            arg_var = Variable(
                BindCArrayType.get_new(rank, allows_strides),
                self.scope.get_new_name(orig_var.name),
                shape=(convert_to_literal(rank * 3 + 1 if allows_strides else rank + 1),),
            )
            self.scope.insert_symbolic_alias(
                IndexedElement(arg_var, convert_to_literal(0)), ObjectAddress(parts["data"])
            )
            for i, s in enumerate(shape_elems):
                self.scope.insert_symbolic_alias(IndexedElement(arg_var, convert_to_literal(i + 1)), s)
            if allows_strides:
                for i, s in enumerate(ubound_elems):
                    self.scope.insert_symbolic_alias(IndexedElement(arg_var, convert_to_literal(i + rank + 1)), s)
                for i, s in enumerate(stride_elems):
                    self.scope.insert_symbolic_alias(IndexedElement(arg_var, convert_to_literal(i + 2 * rank + 1)), s)

            return {"body": body, "args": [arg_var], "default_init": default_body}

        class_type = orig_var.class_type
        if isinstance(class_type, FinalType):
            class_type = class_type.underlying_type
        arg_var = orig_var.clone(
            self.scope.get_new_name(orig_var.name),
            is_argument=False,
            is_optional=False,
            memory_handling="alias",
            new_class=Variable,
            class_type=class_type,
        )
        self.scope.insert_variable(arg_var)
        if orig_var.is_optional:
            sliced_arg_var = orig_var.clone(
                self.scope.get_new_name(orig_var.name),
                is_argument=False,
                is_optional=False,
                memory_handling="alias",
                new_class=Variable,
                class_type=class_type,
            )
            self.scope.insert_variable(sliced_arg_var)
        else:
            sliced_arg_var = orig_var.clone(
                self.scope.get_expected_name(orig_var.name),
                is_argument=False,
                is_optional=False,
                memory_handling="alias",
                new_class=Variable,
                class_type=class_type,
            )
            self.scope.insert_variable(sliced_arg_var, orig_var.name)

        body.append(Allocate(arg_var, shape=tuple(shape_elems), status="unallocated", like=args[0]))
        body.append(
            AliasAssign(
                sliced_arg_var,
                IndexedElement(
                    arg_var,
                    *[Slice(None, u, s) for s, u in zip(stride_elems, ubound_elems, strict=False)],
                ),
            )
        )

        collect_arg = sliced_arg_var
        if orig_var.is_optional:
            optional_arg_var = sliced_arg_var.clone(self.scope.get_expected_name(orig_var.name), is_optional=True)
            self.scope.insert_variable(optional_arg_var)
            body.append(AliasAssign(optional_arg_var, sliced_arg_var))
            default_body.append(AliasAssign(optional_arg_var, NIL))
            collect_arg = optional_arg_var
        return {"body": body, "args": [collect_arg], "default_init": default_body}

    def _array_shape_validation(self, orig_var, shape_elems):
        checks = []
        for axis, (actual, expected) in enumerate(zip(shape_elems, orig_var.alloc_shape or (), strict=False)):
            if expected is None:
                continue
            checks.append(
                If(
                    IfSection(
                        Ne(actual, expected),
                        [
                            PyErr_SetString(
                                PyTypeError,
                                CStrStr(
                                    convert_to_literal(
                                        f"Argument {orig_var.name} has incompatible shape at axis {axis}"
                                    )
                                ),
                            ),
                            Return(self._error_exit_code),
                        ],
                    )
                )
            )
        return checks

    def _extract_StringType_FunctionDefArgument(
        self, orig_var, collect_arg, bound_argument, is_bind_c_argument, *, arg_var=None
    ):
        """
        Extract the C-compatible string FunctionDefArgument from the PythonObject.

        Extract the C-compatible string FunctionDefArgument from the PythonObject.
        The C-compatible argument is extracted from collect_arg which holds a Python
        object into arg_var.

        The extraction is done by allocating an array and filling the elements with values
        extracted from the indexed Python tuple in collect_arg.

        Parameters
        ----------
        orig_var : Variable | IndexedElement
            An object representing the variable or an element of the variable from the
            FunctionDefArgument being wrapped.

        collect_arg : Variable
            A variable with type PythonObject* holding the Python argument from which the
            C-compatible argument should be collected.

        bound_argument : bool
            True if the argument is the self argument of a class method. False otherwise.
            This should always be False for this function.

        is_bind_c_argument : bool
            True if the argument was saved in a BindCFunctionDefArgument. False otherwise.

        arg_var : Variable | IndexedElement, optional
            A variable or an element of the variable representing the argument that
            will be passed to the low-level function call.

        Returns
        -------
        list[model object]
            A list of expressions which extract the argument from collect_arg into arg_var.
        """
        assert bound_argument is False

        if is_bind_c_argument:
            if arg_var is None:
                data_var = Variable(
                    FinalType.get_new(NumpyNDArrayType.get_new(CharType(), 1, None, raw=True)),
                    self.scope.get_expected_name(orig_var.name),
                    shape=(None,),
                    memory_handling="alias",
                )
                size_var = Variable(NumpyInt64Type(), self.scope.get_new_name(f"{data_var.name}_size"))
                arg_var = Variable(
                    BindCArrayType.get_new(1, False),
                    self.scope.get_new_name(orig_var.name),
                    shape=(convert_to_literal(2),),
                )
                self.scope.insert_variable(data_var, orig_var.name)
                self.scope.insert_variable(size_var)
                data_element = IndexedElement(arg_var, convert_to_literal(0))
                size_element = IndexedElement(arg_var, convert_to_literal(1))
                self.scope.insert_symbolic_alias(data_element, ObjectAddress(data_var))
                self.scope.insert_symbolic_alias(size_element, size_var)
            else:
                size_element = IndexedElement(arg_var, convert_to_literal(1))

            if getattr(orig_var, "is_optional", False):
                body = [
                    AliasAssign(
                        data_var,
                        PyUnicode_AsUTF8AndSize(
                            collect_arg,
                            ObjectAddress(self.scope.collect_tuple_element(size_element)),
                        ),
                    ),
                ]
            else:
                body = [
                    Assign(
                        orig_var,
                        PyUnicode_AsUTF8AndSize(
                            collect_arg,
                            ObjectAddress(self.scope.collect_tuple_element(size_element)),
                        ),
                    ),
                ]

            default_init = [AliasAssign(data_var, NIL), Assign(size_var, 0)]
        else:
            if arg_var is None:
                kwargs = {"new_class": Variable, "is_argument": False}
                if getattr(orig_var, "is_optional", False):
                    kwargs["memory_handling"] = "alias"
                arg_var = orig_var.clone(
                    self.scope.get_expected_name(orig_var.name),
                    **kwargs,
                )
                self.scope.insert_variable(arg_var, orig_var.name)

            body = [Assign(orig_var, cast_to(PyUnicode_AsUTF8(collect_arg), StringType()))]

            default_init = [AliasAssign(arg_var, NIL)]
            if getattr(orig_var, "is_optional", False):
                memory_var = self.scope.get_temporary_variable(
                    arg_var,
                    name=arg_var.name + "_memory",
                    is_optional=False,
                    memory_handling="stack",
                )
                body.insert(0, AliasAssign(arg_var, memory_var))

        return {"body": body, "args": [arg_var], "default_init": default_init}

    def _extract_FunctionDefResult(self, orig_var, is_bind_c, funcdef=None):
        """
        Get the code which translates a C-compatible `Variable` to a Python `FunctionDefResult`.

        Get the code necessary to transform a Variable returned from a C-compatible function written in
        Fortran to an object with datatype `PythonObjectType`.

        Parameters
        ----------
        orig_var : Variable | IndexedElement
            An object representing the variable or an element of the variable from the
            FunctionDefResult being wrapped.

        is_bind_c : bool
            True if the result comes from a C-binding from another language. False otherwise.

        funcdef : FunctionDef
            The function being wrapped.

        Returns
        -------
        dict[str, Any]
            A dictionary with the keys:
             - body : a list of model objects containing the code which translates the C-compatible variable
                        to a `PythonObjectType`.
             - c_results : a list of Variables which are returned from the function being wrapped.
             - py_result : the Variable returned to Python.
             - setup : An optional key containing a list of model objects with code which should be
                        run before calling the function being wrapped.
        """
        if orig_var is NIL:
            return {"c_results": [], "py_result": Py_None, "body": []}

        class_type = orig_var.original_var.class_type if isinstance(orig_var, BindCVariable) else orig_var.class_type

        classes = type(class_type).__mro__
        for cls in classes:
            annotation_method = f"_extract_{cls.__name__}_FunctionDefResult"
            if hasattr(self, annotation_method):
                return getattr(self, annotation_method)(orig_var, is_bind_c, funcdef)

        # Unknown object, we raise an error.
        raise NotImplementedError(f"Wrapping function results is not implemented for type {class_type}.")

    def _extract_CustomDataType_FunctionDefResult(self, wrapped_var, is_bind_c, funcdef):
        """
        Get the code which translates a `Variable` containing a class instance to a PyObject.

        Get the code which translates a `Variable` containing a class instance to a PyObject.

        Parameters
        ----------
        wrapped_var : Variable | IndexedElement
            An object representing the variable or an element of the variable from the
            FunctionDefResult being wrapped.
        is_bind_c : bool
            True if the result comes from a C-binding from another language. False otherwise.
        funcdef : FunctionDef
            The function being wrapped.

        Returns
        -------
        dict
            A dictionary describing the objects necessary to collect the result.
        """
        orig_var = getattr(wrapped_var, "original_var", wrapped_var)
        name = orig_var.name
        python_res = self.get_new_PyObject(f"{name}_obj", orig_var.dtype)
        setup = self._allocate_class_instance(python_res, python_res.cls_base.scope, orig_var.is_alias)
        if is_bind_c:
            c_res = orig_var.clone(
                self.scope.get_new_name(orig_var.name),
                is_argument=False,
                memory_handling="alias",
                new_class=Variable,
            )
            self.scope.insert_variable(c_res, orig_var.name)
            scope = python_res.cls_base.scope
            attribute = scope.find("instance", "variables", raise_if_missing=True)
            attrib_var = attribute.clone(attribute.name, new_class=DottedVariable, lhs=python_res)
            body = [AliasAssign(attrib_var, c_res)]
            result = ObjectAddress(c_res)
        else:
            scope = python_res.cls_base.scope
            attribute = scope.find("instance", "variables", raise_if_missing=True)
            c_res = attribute.clone(attribute.name, new_class=DottedVariable, lhs=python_res)
            setup.append(Allocate(c_res, shape=None, status="unallocated", like=orig_var))
            result = PointerCast(c_res, cast_type=orig_var)
            body = []

        if funcdef:
            body.extend(self.connect_pointer_targets(orig_var, python_res, funcdef, is_bind_c))

        return {
            "c_results": [result],
            "py_result": python_res,
            "body": body,
            "setup": setup,
        }

    def _extract_FixedSizeType_FunctionDefResult(self, orig_var, is_bind_c, funcdef):
        """
        Get the code which translates a `Variable` containing a scalar to a PyObject.

        Get the code which translates a `Variable` containing a scalar to a PyObject.

        Parameters
        ----------
        orig_var : Variable | IndexedElement
            An object representing the variable or an element of the variable from the
            FunctionDefResult being wrapped.
        is_bind_c : bool
            True if the result comes from a C-binding from another language. False otherwise.
        funcdef : FunctionDef
            The function being wrapped.

        Returns
        -------
        dict
            A dictionary describing the objects necessary to collect the result.
        """
        name = getattr(orig_var, "name", "tmp")
        py_res = self.get_new_PyObject(f"{name}_obj", orig_var.dtype)
        c_res = Variable(orig_var.class_type, self.scope.get_new_name(name))
        self.scope.insert_variable(c_res)

        body = [AliasAssign(py_res, FunctionCall(C_to_Python(c_res), [c_res]))]
        return {"c_results": [c_res], "py_result": py_res, "body": body}

    def _extract_NumpyNDArrayType_FunctionDefResult(self, orig_var, is_bind_c, funcdef):
        """
        Get the code which translates a `Variable` containing an array to a PyObject.

        Get the code which translates a `Variable` containing an array to a PyObject.

        Parameters
        ----------
        orig_var : Variable | IndexedElement
            An object representing the variable or an element of the variable from the
            FunctionDefResult being wrapped.
        is_bind_c : bool
            True if the result comes from a C-binding from another language. False otherwise.
        funcdef : FunctionDef
            The function being wrapped.

        Returns
        -------
        dict
            A dictionary describing the objects necessary to collect the result.
        """
        if is_bind_c:
            return self._extract_BindCArrayType_FunctionDefResult(orig_var, funcdef)
        name = self.scope.get_new_name(orig_var.name)
        py_res = self.get_new_PyObject(f"{name}_obj", orig_var.dtype)
        c_res = orig_var.clone(name, is_argument=False, memory_handling="alias")
        typenum = numpy_dtype_registry[orig_var.dtype]
        data_var = DottedVariable(VoidType(), "data", memory_handling="alias", lhs=c_res)
        shape_var = DottedVariable(NumpyNDArrayType.get_new(NumpyInt64Type(), 1, None, raw=True), "shape", lhs=c_res)
        release_memory = False
        if funcdef:
            arg_targets = funcdef.result_pointer_map.get(orig_var, ())
            release_memory = len(arg_targets) == 0 and not isinstance(orig_var, DottedVariable)
        body = [
            AliasAssign(
                py_res,
                to_pyarray(
                    convert_to_literal(orig_var.rank),
                    typenum,
                    data_var,
                    shape_var,
                    convert_to_literal(orig_var.order != "F"),
                    convert_to_literal(release_memory),
                ),
            )
        ]
        self.scope.insert_variable(c_res)
        c_result_vars = [c_res]

        if funcdef:
            body.extend(self.connect_pointer_targets(orig_var, py_res, funcdef, False))

        return {"c_results": c_result_vars, "py_result": py_res, "body": body}

    def _extract_BindCResultTupleType_FunctionDefResult(self, tuple_var, is_bind_c, funcdef):
        c_results = []
        py_results = []
        owned_py_results = []
        setup = []
        body = []
        assert funcdef is not None
        for index in range(len(tuple_var.class_type)):
            element = funcdef.scope.collect_tuple_element(IndexedElement(tuple_var, index))
            if isinstance(getattr(element, "class_type", None), BindCArrayType):
                result = self._extract_BindCArrayType_FunctionDefResult(element, funcdef, tuple_item=True)
            else:
                result = self._extract_FunctionDefResult(element, is_bind_c, funcdef)
            item_c_results = result["c_results"]
            if isinstance(item_c_results, PythonTuple):
                c_results.extend(item_c_results.args)
            else:
                c_results.extend(item_c_results)
            setup.extend(result.get("setup", ()))
            body.extend(result["body"])
            py_results.extend(result.get("py_results", [result["py_result"]]))
            owned_py_results.extend(result.get("owned_py_results", [True]))
        return {
            "c_results": PythonTuple(*c_results),
            "py_result": Py_None,
            "py_results": py_results,
            "owned_py_results": owned_py_results,
            "body": body,
            "setup": setup,
        }

    def _extract_BindCArrayType_FunctionDefResult(self, wrapped_var, funcdef, *, tuple_item=False):
        """
        Get the code which translates a `Variable` containing an array to a PyObject.

        Get the code which translates a `Variable` containing a BindCArray, which describes an
        array in Fortran, to a PyObject.

        Parameters
        ----------
        wrapped_var : Variable | IndexedElement
            An object representing the variable or an element of the variable from the
            FunctionDefResult being wrapped.
        funcdef : FunctionDef
            The function being wrapped.

        Returns
        -------
        dict
            A dictionary describing the objects necessary to collect the result.
        """
        orig_var = wrapped_var.original_var
        name = orig_var.name
        py_res = self.get_new_PyObject(f"{name}_obj", orig_var.dtype)
        # Result of calling the bind-c function
        data_var = Variable(VoidType(), self.scope.get_new_name(name + "_data"), memory_handling="alias")
        shape_var = Variable(
            NumpyNDArrayType.get_new(NumpyInt32Type(), 1, None, raw=True),
            self.scope.get_new_name(name + "_shape"),
            shape=(orig_var.rank,),
            memory_handling="alias",
        )
        typenum = numpy_dtype_registry[orig_var.dtype]
        # Save so we can find by iterating over func.results
        self.scope.insert_variable(data_var)
        self.scope.insert_variable(shape_var)

        release_memory = False
        if funcdef:
            arg_targets = funcdef.result_pointer_map.get(orig_var, ())
            release_memory = len(arg_targets) == 0 and not isinstance(orig_var, DottedVariable)

        array_to_python = AliasAssign(
            py_res,
            to_pyarray(
                convert_to_literal(orig_var.rank),
                typenum,
                data_var,
                shape_var,
                convert_to_literal(orig_var.order != "F"),
                convert_to_literal(release_memory),
            ),
        )
        shape_vars = [IndexedElement(shape_var, i) for i in range(orig_var.rank)]
        body = [array_to_python]
        if getattr(orig_var, "memory_handling", None) == "heap" or self._is_pointer_snapshot_result(orig_var):
            if tuple_item:
                body = [
                    self._set_none_if_unallocated(data_var, py_res, shape_vars),
                    If(IfSection(IsNot(data_var, NIL), [array_to_python])),
                ]
            else:
                body = [*self._return_none_if_unallocated(data_var, shape_vars), *body]

        c_result_vars = PythonTuple(ObjectAddress(data_var), *shape_vars)

        if funcdef:
            body.extend(self.connect_pointer_targets(orig_var, py_res, funcdef, True))

        return {
            "c_results": c_result_vars,
            "py_result": py_res,
            "py_results": [py_res],
            "owned_py_results": [True],
            "body": body,
        }

    def _extract_StringType_FunctionDefResult(self, wrapped_var, is_bind_c, funcdef):
        orig_var = getattr(wrapped_var, "original_var", wrapped_var)
        name = getattr(orig_var, "name", "tmp")
        py_res = self.get_new_PyObject(f"{name}_obj", orig_var.dtype)
        if is_bind_c:
            c_res = Variable(
                CharType(),
                self.scope.get_new_name(name + "_data"),
                memory_handling="alias",
            )
            self.scope.insert_variable(c_res)
            char_data = ObjectAddress(c_res)
            result = [char_data]
        else:
            c_res = Variable(StringType(), self.scope.get_new_name(name), memory_handling="heap")
            self.scope.insert_variable(c_res)
            char_data = CStrStr(c_res)
            result = [c_res]

        if is_bind_c:
            body = [
                If(
                    IfSection(
                        Is(c_res, NIL),
                        [
                            PyErr_SetString(
                                PyMemoryError,
                                CStrStr(convert_to_literal("Unable to allocate copy-return output string.")),
                            ),
                            Return(self._error_exit_code),
                        ],
                    )
                ),
                AliasAssign(py_res, PyBuildValueNode([char_data])),
            ]
            body.append(Deallocate(c_res))
        else:
            body = [AliasAssign(py_res, PyBuildValueNode([char_data]))]
        return {"c_results": result, "py_result": py_res, "body": body}
