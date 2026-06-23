"""
Module representing objects (functions/variables etc) required for the interface
between Python code and C code (using Python/C Api and x2py_runtime/python_runtime.c).
This file contains classes but also many FunctionDef/Variable instances representing
objects defined in Python.h.
"""

import re

from ..bind_c import BindCPointer
from .c_concepts import CNativeInt, ObjectAddress
from ..models.core import (
    ClassDef,
    Declare,
    FunctionDef,
    FunctionDefArgument,
    FunctionDefResult,
    FunctionOverloadSet,
    Module,
)
from ..models.datatypes import (
    CharType,
    CustomDataType,
    FixedSizeType,
    init_model_object,
    PrimitiveBooleanType,
    PrimitiveComplexType,
    PrimitiveFloatingPointType,
    PrimitiveIntegerType,
    NumpyBoolType,
    NumpyComplex128Type,
    NumpyFloat64Type,
    NumpyInt64Type,
    attach_model_child,
    detach_model_child,
    register_model_class,
    StringType,
    VoidType,
    NIL,
    convert_to_literal,
)
from ..models.core import Function
from ..models.core import Variable

__all__ = (
    # --------- CLASSES -----------
    "PyAllowThreadsBegin",
    "PyAllowThreadsEnd",
    "PyArgKeywords",
    "PyArg_ParseTupleNode",
    "PyArgumentError",
    # --------- CONSTANTS ----------
    "PyAttributeError",
    "PyBuildValueNode",
    "PyCallbackContextPop",
    "PyCallbackContextPush",
    "PyCallbackValidate",
    "PyCapsule_Import",
    "PyCapsule_New",
    "PyClassDef",
    # ----- C / PYTHON FUNCTIONS ---
    "PyDict_New",
    "PyDict_SetItem",
    "PyErr_Occurred",
    "PyErr_SetObject",
    "PyErr_SetString",
    "PyErr_WarnEx",
    "PyFunctionDef",
    "PyFunctionOverloadSet",
    "PyGetSetDefElement",
    "PyList_Append",
    "PyList_GetItem",
    "PyList_New",
    "PyList_SetItem",
    "PyMemoryError",
    "PyModInitFunc",
    "PyModule",
    "PyModule_AddObject",
    "PyModule_Create",
    "PyModule_SetPropertyType",
    "PyNotImplementedError",
    "PyObject_TypeCheck",
    "PyRuntimeError",
    "PyRuntimeWarning",
    "PySys_GetObject",
    "PyTuple_Pack",
    "PyTypeError",
    "PyType_Ready",
    "PyUnicode_AsUTF8",
    "PyUnicode_AsUTF8AndSize",
    "PyUnicode_Check",
    "PyUnicode_FromString",
    "Py_DECREF",
    "Py_False",
    "Py_INCREF",
    "Py_None",
    "Py_True",
    # --------- DATATYPES -----------
    "Py_ssize_t",
    "PythonClassType",
    "PythonObjectType",
    "PythonTypeObjectType",
    "WrapperCustomDataType",
    "c_memcpy",
    "c_memset",
    "c_strlen",
    "x2py_malloc",
)


# -------------------------------------------------------------------
#                        Python DataTypes
# -------------------------------------------------------------------
class PythonObjectType(FixedSizeType):
    """
    Datatype representing a `PyObject`.

    Datatype representing a `PyObject` which is the
    class used to hold Python objects in `Python.h`.
    """

    __slots__ = ()
    _name = "pyobject"


class PythonClassType(FixedSizeType):
    """
    Datatype representing a subclass of `PyObject`.

    Datatype representing a subclass of `PyObject`. This is the
    datatype of a class which is compatible with Python.
    """

    __slots__ = ()
    _name = "pyclasstype"


class PythonTypeObjectType(FixedSizeType):
    """
    Datatype representing a `PyTypeObject`.

    Datatype representing a `PyTypeObject` which is the
    class used to hold Python class objects in `Python.h`.
    """

    __slots__ = ()
    _name = "pytypeobject"


class PyCallbackValidate:
    """Validate that a Python argument is callable before entering native code."""

    __slots__ = ("callback", "error_exit", "python_object")
    _attribute_nodes = ("callback", "error_exit", "python_object")

    def __init__(self, callback, python_object, error_exit):
        """Initialize one ``PyCallbackValidate`` model instance."""
        self.callback = callback
        self.python_object = python_object
        self.error_exit = error_exit
        init_model_object(self)


class PyCallbackContextPush:
    """Install one call-scoped callback context immediately before a native call."""

    __slots__ = ("callback", "python_object")
    _attribute_nodes = ("callback", "python_object")

    def __init__(self, callback, python_object):
        """Initialize one ``PyCallbackContextPush`` model instance."""
        self.callback = callback
        self.python_object = python_object
        init_model_object(self)


class PyCallbackContextPop:
    """Restore the prior callback context after a native call returns."""

    __slots__ = ("callback",)
    _attribute_nodes = ("callback",)

    def __init__(self, callback):
        """Initialize one ``PyCallbackContextPop`` model instance."""
        self.callback = callback
        init_model_object(self)


class PyAllowThreadsBegin:
    """Release the CPython GIL before entering a callback-free native call."""

    __slots__ = ()

    def __init__(self):
        """Initialize one ``PyAllowThreadsBegin`` model instance."""
        init_model_object(self)


class PyAllowThreadsEnd:
    """Reacquire the CPython GIL after a callback-free native call returns."""

    __slots__ = ()

    def __init__(self):
        """Initialize one ``PyAllowThreadsEnd`` model instance."""
        init_model_object(self)


class WrapperCustomDataType(CustomDataType):
    """
    Datatype representing a subclass of `PyObject`.

    Datatype representing a subclass of `PyObject`. This is the
    datatype of a class which is compatible with Python.
    """

    __slots__ = ()
    _name = "pycustomclasstype"


class Py_ssize_t(FixedSizeType):
    """
    Class representing Python's Py_ssize_t type.

    Class representing Python's Py_ssize_t type.
    """

    __slots__ = ()
    _name = "int"
    _primitive_type = PrimitiveIntegerType()


# -------------------------------------------------------------------
#                  Parsing and Building Classes
# -------------------------------------------------------------------


# TODO: Is there an equivalent to static so this can be a static list of strings?
class PyArgKeywords:
    """
    Represents the list containing the names of all arguments to a function.
    This information allows the function to be called by keyword

    Parameters
    ----------
    name : str
        The name of the variable in which the list is stored
    arg_names : list of str
        A list of the names of the function arguments
    """

    __slots__ = ("_arg_names", "_name")
    _attribute_nodes = ()

    def __init__(self, name, arg_names):
        """Initialize one ``PyArgKeywords`` model instance."""
        self._name = name
        self._arg_names = arg_names
        init_model_object(self)

    @property
    def name(self):
        """The name of the variable in which the list of
        all arguments to the function is stored
        """
        return self._name

    @property
    def arg_names(self):
        """The names of the arguments to the function which are
        contained in the PyArgKeywords list
        """
        return self._arg_names


# -------------------------------------------------------------------
class PyArg_ParseTupleNode:
    """
    Represents a call to the function `PyArg_ParseTupleNode`.

    Represents a call to the function `PyArg_ParseTupleNode` from `Python.h`.
    This function collects the expected arguments from `self`, `args`, `kwargs`
    and packs them into variables with datatype `PythonObjectType`.

    Parameters
    ----------
    python_func_args : Variable
        Args provided to the function in Python.
    python_func_kwargs : Variable
        Kwargs provided to the function in Python.
    c_func_args : list of Variable
        List of expected arguments. This helps determine the expected output types.
    parse_args : list of Variable
        List of arguments into which the result will be collected.
    arg_names : list of str
        A list of the names of the function arguments.
    """

    __slots__ = ("_arg_names", "_flags", "_parse_args", "_pyarg", "_pykwarg")
    _attribute_nodes = ("_pyarg", "_pykwarg", "_parse_args", "_arg_names")

    def __init__(self, python_func_args, python_func_kwargs, c_func_args, parse_args, arg_names):
        """Initialize one ``PyArg_ParseTupleNode`` model instance."""
        if not isinstance(python_func_args, Variable):
            raise TypeError("Python func args should be a Variable")
        if not isinstance(python_func_kwargs, Variable):
            raise TypeError("Python func kwargs should be a Variable")
        if not isinstance(parse_args, list) and any(not isinstance(c, Variable) for c in parse_args):
            raise TypeError("Parse args should be a list of Variables")
        if not isinstance(arg_names, PyArgKeywords):
            raise TypeError("Parse args should be a list of Variables")

        self._flags = ""
        has_default = False
        has_keyword = False
        for a in c_func_args:
            if a.has_default and not has_default:
                self._flags += "|"
                has_default = True
            if a.is_kwonly and not has_keyword:
                self._flags += "$"
                has_keyword = True
            self._flags += "O"

        if any(a.is_vararg or a.is_kwarg for a in c_func_args):
            raise NotImplementedError(
                "Variadic arguments (*args, **kwargs) are not yet supported in the wrapper.",
            )

        self._pyarg = python_func_args
        self._pykwarg = python_func_kwargs
        self._parse_args = parse_args
        self._arg_names = arg_names
        init_model_object(self)

    @property
    def pyarg(self):
        """The  variable containing all positional arguments
        passed to the function
        """
        return self._pyarg

    @property
    def pykwarg(self):
        """The  variable containing all keyword arguments
        passed to the function
        """
        return self._pykwarg

    @property
    def flags(self):
        """
        The flags indicating the types of the objects.

        The flags indicating the types of the objects to be collected from
        the Python arguments passed to the function.
        """
        return self._flags

    @property
    def args(self):
        """The arguments into which the python args and kwargs
        are collected
        """
        return self._parse_args

    @property
    def arg_names(self):
        """The PyArgKeywords object which contains all the
        names of the function's arguments
        """
        return self._arg_names


# -------------------------------------------------------------------
class PyBuildValueNode(Function):
    """
    Represents a call to the function PyBuildValueNode.

    The function PyBuildValueNode can be found in Python.h.
    It describes the creation of a new Python object based
    on a format string. More details can be found in Python's
    docs.

    Parameters
    ----------
    result_args : list of Variable
        List of arguments which the result will be built from.
    """

    __slots__ = ("_flags", "_result_args")
    _attribute_nodes = ("_result_args",)
    _shape = None
    _class_type = PythonObjectType()

    def __init__(self, result_args=()):
        """Initialize one ``PyBuildValueNode`` model instance."""
        self._flags = ""
        self._result_args = result_args
        for i in result_args:
            if isinstance(i.dtype, WrapperCustomDataType):
                self._flags += "O"
            else:
                self._flags += pytype_parse_registry[i.dtype]
        super().__init__()

    @property
    def flags(self):
        """Handle flags on ``PyBuildValueNode``."""
        return self._flags

    @property
    def args(self):
        """Handle args on ``PyBuildValueNode``."""
        return self._result_args


# -------------------------------------------------------------------
class PyModule_AddObject(Function):
    """
    Represents a call to the PyModule_AddObject function.

    The PyModule_AddObject function can be found in Python.h.
    It adds a PythonObject to a module. More information about
    this function can be found in Python's documentation.

    Parameters
    ----------
    mod_name : str
                The name of the variable containing the module.
    name : str
                The name of the variable being added to the module.
    variable : Variable
                The variable containing the PythonObject.
    """

    __slots__ = ("_mod_name", "_name", "_var")
    _attribute_nodes = ("_name", "_var")
    _shape = None
    _class_type = NumpyInt64Type()

    def __init__(self, mod_name, name, variable):
        """Initialize one ``PyModule_AddObject`` model instance."""
        assert isinstance(name.dtype, CharType)
        if not isinstance(variable, Variable) or variable.dtype not in (
            PythonObjectType(),
            PythonClassType(),
        ):
            raise TypeError("Variable must be a PyObject Variable")
        self._mod_name = mod_name
        self._name = name
        self._var = ObjectAddress(variable)
        super().__init__()

    @property
    def mod_name(self):
        """The name of the variable containing the module"""
        return self._mod_name

    @property
    def name(self):
        """The name of the variable being added to the module"""
        return self._name

    @property
    def variable(self):
        """The variable containing the PythonObject"""
        return self._var


# -------------------------------------------------------------------
class PyModule_Create(Function):
    """
    Represents a call to the PyModule_Create function.

    The PyModule_Create function can be found in Python.h.
    It acts as a constructor for a module. More information about
    this function can be found in Python's documentation.
    See https://docs.python.org/3/c-api/module.html#c.PyModule_Create .

    Parameters
    ----------
    module_def_name : str
        The name of the structure which defined the module.
    """

    __slots__ = ("_module_def_name",)
    _attribute_nodes = ()
    _shape = None
    _class_type = PythonObjectType()

    def __init__(self, module_def_name):
        """Initialize one ``PyModule_Create`` model instance."""
        self._module_def_name = module_def_name
        super().__init__()

    @property
    def module_def_name(self):
        """
        Get the name of the structure which defined the module.

        Get the name of the structure which defined the module.
        """
        return self._module_def_name


class PyModule_SetPropertyType(Function):
    """Call a generated helper that installs module-variable attribute hooks."""

    __slots__ = ("_module", "_setup_name")
    _attribute_nodes = ("_module",)
    _shape = None
    _class_type = CNativeInt()

    def __init__(self, setup_name, module):
        self._setup_name = setup_name
        self._module = module
        super().__init__(module)

    @property
    def setup_name(self):
        """Return the generated setup helper name."""
        return self._setup_name

    @property
    def module(self):
        """Return the module object receiving the custom type."""
        return self._module


# -------------------------------------------------------------------
class PyCapsule_New(Function):
    """
    Represents a call to the function PyCapsule_New.

    The function PyCapsule_New can be found in Python.h. It describes
    the creation of a capsule. A capsule contains all information
    from a module which should be exposed to other modules that import
    this module.
    See https://docs.python.org/3/extending/extending.html#using-capsules
    for a tutorial involving capsules.
    See https://docs.python.org/3/c-api/capsule.html#c.PyCapsule_New
    for the API docstrings for this method.

    Parameters
    ----------
    API_var : Variable
        The variable which contains all elements of the API which should be exposed.

    module_name : str
        The name of the module being exposed.
    """

    __slots__ = ("_API_var", "_capsule_name")
    _attribute_nodes = ("_API_var",)
    _shape = None
    _class_type = PythonObjectType()

    def __init__(self, API_var, module_name):
        """Initialize one ``PyCapsule_New`` model instance."""
        self._capsule_name = f"{module_name}._C_API"
        self._API_var = API_var
        super().__init__()

    @property
    def capsule_name(self):
        """
        Get the name of the capsule being created.

        Get the name of the capsule being created.
        """
        return self._capsule_name

    @property
    def API_var(self):
        """
        Get the variable describing the API.

        Get the variable which contains all elements of the API which
        should be exposed.
        """
        return self._API_var


# -------------------------------------------------------------------
class PyCapsule_Import(Function):
    """
    Represents a call to the function PyCapsule_Import.

    The function PyCapsule_Import can be found in Python.h. It describes
    the initialisation of a capsule by importing the information from
    another module. A capsule contains all information from a module
    which should be exposed to other modules that import this module.
    See https://docs.python.org/3/extending/extending.html#using-capsules
    for a tutorial involving capsules.
    See https://docs.python.org/3/c-api/capsule.html#c.PyCapsule_Import
    for the API docstrings for this method.

    Parameters
    ----------
    module_name : str
        The name of the module being retrieved.
    """

    __slots__ = ("_capsule_name",)
    _attribute_nodes = ()
    _shape = None
    _class_type = BindCPointer()

    def __init__(self, module_name):
        """Initialize one ``PyCapsule_Import`` model instance."""
        self._capsule_name = f"{module_name}._C_API"
        super().__init__()

    @property
    def capsule_name(self):
        """
        Get the name of the capsule being retrieved.

        Get the name of the capsule being retrieved.
        """
        return self._capsule_name


# -------------------------------------------------------------------
class PyModule(Module):
    """
    Class to hold a module which is accessible from Python.

    Class to hold a module which is accessible from Python. This class
    adds external functions and external declarations to the basic
    Module. However its main utility is in order to differentiate
    itself such that a different `_print` function can be implemented
    to handle it.

    Parameters
    ----------
    name : str
        Name of the module.

    *args : tuple
        See Module.

    external_funcs : iterable of FunctionDef
        A list of external functions.

    declarations : iterable
        Any declarations of (external) variables which should be made in the module.

    init_func : FunctionDef, optional
        The function which is executed when a module is initialised.
        See: https://docs.python.org/3/c-api/module.html#multi-phase-initialization .

    import_func : FunctionDef, optional
        The function which allows types from this module to be imported in other
        modules.
        See: https://docs.python.org/3/extending/extending.html .

    module_def_name : str
        The name of the structure which defined the module.

    **kwargs : dict
        See Module.

    See Also
    --------
    Module : The super class from which the class inherits.
    """

    __slots__ = (
        "_declarations",
        "_external_funcs",
        "_import_func",
        "_module_def_name",
        "_module_properties",
        "_namespace_module_defs",
    )
    _attribute_nodes = (*Module._attribute_nodes, "_external_funcs", "_declarations", "_import_func")

    def __init__(
        self,
        name,
        *args,
        external_funcs=(),
        declarations=(),
        init_func=None,
        import_func,
        module_def_name,
        module_properties=None,
        namespace_module_defs=None,
        **kwargs,
    ):
        """Initialize one ``PyModule`` model instance."""
        self._external_funcs = external_funcs
        self._declarations = declarations
        self._module_def_name = module_def_name
        self._module_properties = dict(module_properties or {})
        self._namespace_module_defs = dict(namespace_module_defs or {})
        self._import_func = import_func
        super().__init__(name, *args, init_func=init_func, **kwargs)

    @property
    def external_funcs(self):
        """
        A list of external functions.

        The external functions which should be declared at the start of the module.
        This is useful for declaring the existence of Fortran functions whose
        definition and declaration is inaccessible from C.
        """
        return self._external_funcs

    @property
    def namespace_module_defs(self):
        """Return child namespace paths and their generated module definitions."""
        return self._namespace_module_defs

    @property
    def module_properties(self):
        """Return generated module-variable property descriptors by namespace."""
        return self._module_properties

    @external_funcs.setter
    def external_funcs(self, funcs):
        """Handle external funcs on ``PyModule``."""
        for f in self._external_funcs:
            detach_model_child(self, f)
        self._external_funcs = funcs
        for f in funcs:
            attach_model_child(self, f)

    @property
    def declarations(self):
        """
        All declarations that need printing in the module.

        All declarations that need printing in the module. This usually includes
        any variables coming from a non-C language for which compatibility with C
        exists.
        """
        return self._declarations

    @declarations.setter
    def declarations(self, decs):
        """Handle declarations on ``PyModule``."""
        for d in self._declarations:
            detach_model_child(self, d)
        self._declarations = decs
        for d in decs:
            attach_model_child(self, d)

    @property
    def import_func(self):
        """
        The function which allows types from this module to be imported in other modules.

        The function which allows types from this module to be imported in other modules.
        See https://docs.python.org/3/extending/extending.html to understand how this
        is done.
        """
        return self._import_func

    @property
    def module_def_name(self):
        """
        The name of the PyModuleDef object describing the module.

        The name of the PyModuleDef object describing the module and
        its contents for Python.
        """
        return self._module_def_name


# -------------------------------------------------------------------
class PyFunctionDef(FunctionDef):
    """
    Class to hold a FunctionDef which is accessible from Python.

    Contains the Python-compatible version of the function which is
    used for the wrapper.
    As compared to a normal FunctionDef, this version contains
    arguments for the shape of arrays. It should be generated by
    calling `codegen.wrapper.CToPythonWrapper.wrap`.

    Parameters
    ----------
    *args : list
        See FunctionDef.

    original_function : FunctionDef
        The function from which the Python-compatible version was created.

    **kwargs : dict
        See FunctionDef.

    See Also
    --------
    x2py.ast.core.FunctionDef
        The class from which BindCFunctionDef inherits which contains all
        details about the args and kwargs.
    """

    __slots__ = ("_original_function",)
    _attribute_nodes = (*FunctionDef._attribute_nodes, "_original_function")

    def __init__(self, *args, original_function, **kwargs):
        """Initialize one ``PyFunctionDef`` model instance."""
        self._original_function = original_function
        super().__init__(*args, **kwargs, is_static=True)

    @property
    def original_function(self):
        """
        The function which is wrapped by this PyFunctionDef.

        The original function which would be printed in pure C which is not
        compatible with Python.
        """
        return self._original_function


# -------------------------------------------------------------------
class PyFunctionOverloadSet(FunctionOverloadSet):
    """
    Class to hold an FunctionOverloadSet which is accessible from Python.

    A class which holds the Python-compatible FunctionOverloadSet. It contains functions for
    determining the type of the arguments passed to the FunctionOverloadSet and the functions
    called through the interface.

    Parameters
    ----------
    name : str
        The name of the interface. See FunctionOverloadSet.

    functions : iterable of FunctionDef
        The functions of the interface. See FunctionOverloadSet.

    dispatcher_func : FunctionDef
        The function which Python will call to access the interface.

    type_check_func : FunctionDef
        The helper function which will determine the types of the arguments passed.

    original_overload_set : FunctionOverloadSet
        The interface being wrapped.

    **kwargs : dict
        See FunctionOverloadSet.

    See Also
    --------
    FunctionOverloadSet : The super class.
    """

    __slots__ = ("_dispatcher_func", "_original_overload_set", "_type_check_func")
    _attribute_nodes = (
        *FunctionOverloadSet._attribute_nodes,
        "_dispatcher_func",
        "_type_check_func",
        "_original_overload_set",
    )

    def __init__(
        self,
        name,
        functions,
        dispatcher_func,
        type_check_func,
        original_overload_set,
        **kwargs,
    ):
        """Initialize one ``PyFunctionOverloadSet`` model instance."""
        self._dispatcher_func = dispatcher_func
        self._type_check_func = type_check_func
        self._original_overload_set = original_overload_set
        for f in functions:
            if not isinstance(f, PyFunctionDef):
                raise TypeError("PyFunctionOverloadSet functions should be instances of the class PyFunctionDef.")
        super().__init__(name, functions, False, **kwargs)

    @property
    def dispatcher_func(self):
        """
        The function which is exposed to Python.

        The function which receives the Python arguments `self`, `args`, and `kwargs` and calls
        the appropriate function.
        """
        return self._dispatcher_func

    @property
    def type_check_func(self):
        """
        The function which determines the types which were passed to the FunctionOverloadSet.

        The function which takes the arguments passed to the function and returns an integer
        indicating which function was called.
        """
        return self._type_check_func

    @property
    def original_function(self):
        """
        The FunctionOverloadSet which is wrapped by this PyFunctionOverloadSet.

        The original interface which would be printed in C.
        """
        return self._original_overload_set


# -------------------------------------------------------------------
class PyClassDef(ClassDef):
    """
    Class to hold a class definition which is accessible from Python.

    Class to hold a class definition which is accessible from Python.

    Parameters
    ----------
    original_class : ClassDef
        The original class being wrapped.

    struct_name : str
        The name of the structure which will hold the Python-compatible
        class definition.

    type_name : str
        The name of the instance of the Python-compatible class definition
        structure. This object is necessary to add the class to the module.

    scope : Scope
        The scope for the class contents.

    **kwargs : dict
        See ClassDef.

    See Also
    --------
    ClassDef
        The class from which PyClassDef inherits. This is also the object being
        wrapped.
    """

    __slots__ = (
        "_magic_methods",
        "_new_func",
        "_original_class",
        "_properties",
        "_struct_name",
        "_type_name",
        "_type_object",
    )
    _attribute_nodes = (*ClassDef._attribute_nodes, "_magic_methods")

    def __init__(self, original_class, struct_name, type_name, scope, **kwargs):
        """Initialize one ``PyClassDef`` model instance."""
        assert isinstance(original_class, ClassDef)
        self._original_class = original_class
        self._struct_name = struct_name
        self._type_name = type_name
        self._type_object = Variable(PythonClassType(), type_name)
        self._new_func = None
        self._properties = ()
        self._magic_methods = ()
        variables = [
            Variable(VoidType(), scope.get_new_name("instance"), memory_handling="alias"),
            Variable(
                PythonObjectType(),
                scope.get_new_name("referenced_objects"),
                memory_handling="alias",
            ),
            Variable(NumpyBoolType(), scope.get_new_name("is_alias")),
        ]
        scope.insert_variable(variables[0])
        scope.insert_variable(variables[1])
        scope.insert_variable(variables[2])
        super().__init__(original_class.name, variables, scope=scope, **kwargs)

    @property
    def struct_name(self):
        """
        The name of the structure which will hold the Python-compatible class definition.

        The name of the structure which will hold the Python-compatible class definition.
        """
        return self._struct_name

    @property
    def type_name(self):
        """
        The name of the Python-compatible class definition instance.

        The name of the instance of the Python-compatible class definition
        structure. This object is necessary to add the class to the module.
        """
        return self._type_name

    @property
    def type_object(self):
        """
        The Python-compatible class definition instance.

        The Variable describing the instance of the Python-compatible class definition
        structure. This object is necessary to add the class to the module.
        """
        return self._type_object

    @property
    def original_class(self):
        """
        The class which is wrapped by this PyClassDef.

        The original class which would be printed in pure C which is not
        compatible with Python.
        """
        return self._original_class

    def add_alloc_method(self, f):
        """
        Add the wrapper for `__new__` to the class definition.

        Add the wrapper for `__new__` which allocates the memory for the class instance.

        Parameters
        ----------
        f : PyFunctionDef
            The wrapper for the `__new__` function.
        """
        self._new_func = f

    @property
    def new_func(self):
        """
        Get the wrapper for `__new__`.

        Get the wrapper for `__new__` which allocates the memory for the class instance.
        """
        return self._new_func

    def add_property(self, p):
        """
        Add a class property which has been wrapped.

        Add a class property which has been wrapped.

        Parameters
        ----------
        p : model object
            The new wrapped property which is added to the class.
        """
        attach_model_child(self, p)
        self._properties += (p,)

    @property
    def properties(self):
        """
        Get all wrapped class properties.

        Get all wrapped class properties.
        """
        return self._properties

    def add_new_magic_method(self, method):
        """
        Add a new magic method to the current class.

        Add a new magic method to the current ClassDef.

        Parameters
        ----------
        method : FunctionDef
            The Method that will be added.
        """

        if not isinstance(method, PyFunctionDef | PyFunctionOverloadSet):
            raise TypeError("Method must be PyFunctionDef or PyFunctionOverloadSet")
        attach_model_child(self, method)
        self._magic_methods += (method,)

    @property
    def magic_methods(self):
        """
        Get the magic methods describing methods.

        Get the magic methods describing methods such as __add__.
        """
        return self._magic_methods


# -------------------------------------------------------------------


class PyGetSetDefElement:
    """
    A class representing a PyGetSetDef object.

    A class representing an element of the list of PyGetSetDef objects
    which are used to add attributes/properties to classes.
    See https://docs.python.org/3/c-api/structures.html#c.PyGetSetDef .

    Parameters
    ----------
    python_name : str
        The name of the attribute/property in the original Python code.
    getter : FunctionDef
        The function which collects the value of the class attribute.
    setter : FunctionDef
        The function which modifies the value of the class attribute.
    docstring : Literal
        The docstring of the property.
    """

    _attribute_nodes = ("_getter", "_setter", "_docstring")
    __slots__ = ("_docstring", "_getter", "_python_name", "_setter")

    def __init__(self, python_name, getter, setter, docstring):
        """Initialize one ``PyGetSetDefElement`` model instance."""
        assert isinstance(getter, PyFunctionDef)
        assert isinstance(setter, PyFunctionDef) or setter is None
        self._python_name = python_name
        self._getter = getter
        self._setter = setter
        self._docstring = docstring
        init_model_object(self)

    @property
    def python_name(self):
        """
        The name of the attribute/property in the original Python code.

        The name of the attribute/property in the original Python code.
        """
        return self._python_name

    @property
    def getter(self):
        """
        The BindCFunctionDef describing the getter function.

        The BindCFunctionDef describing the function which allows the user to collect
        the value of the property.
        """
        return self._getter

    @property
    def setter(self):
        """
        The BindCFunctionDef describing the setter function.

        The BindCFunctionDef describing the function which allows the user to modify
        the value of the property.
        """
        return self._setter

    @property
    def docstring(self):
        """
        The docstring of the property being wrapped.

        The docstring of the property being wrapped.
        """
        return self._docstring


# -------------------------------------------------------------------
class PyModInitFunc(FunctionDef):
    """
    A class representing the PyModInitFunc function def.

    A class representing the PyModInitFunc function def. This function returns the
    macro PyModInitFunc, takes no arguments and initialises a module.

    Parameters
    ----------
    name : str
        The name of the function.

    body : list[model object]
        The code executed in the function.

    static_vars : list[Variable]
        A list of variables which should be declared as static objects.

    scope : Scope
        The scope of the function.
    """

    __slots__ = ("_static_vars",)

    def __init__(self, name, body, static_vars, scope):
        """Initialize one ``PyModInitFunc`` model instance."""
        self._static_vars = static_vars
        super().__init__(name, (), body, scope=scope)

    @property
    def declarations(self):
        """
        Returns the declarations of the variables.

        Returns the declarations of the variables.
        """
        return [
            Declare(
                v,
                static=(v in self._static_vars),
                value=(NIL if isinstance(v.class_type, VoidType | BindCPointer) else None),
            )
            for v in self.scope.variables.values()
        ]


class PyTuple_Pack(Function):
    """
    A class representing a call to Python's PyTuple_Pack function.

    A class representing a call to Python's PyTuple_Pack function. A class
    is used instead of a FunctionDef as the number of arguments is variable.
    A PyTuple_Pack is described here:
    https://docs.python.org/3/c-api/tuple.html#c.PyTuple_Pack

    Parameters
    ----------
    *args : model object
        The arguments that should be packed into the tuple.
    """

    __slots__ = ()
    _class_type = PythonObjectType()
    _shape = None


class PyArgumentError:
    """
    Class to display errors related to arguments.

    Class to display errors related to arguments. This class helps
    format the arguments to display the type of the received argument.

    Parameters
    ----------
    error_type : Variable
        A Variable containing the error type to be raised. E.g. PyTypeError.
    error_msg : str
        The message to be displayed containing f-string style type indicators.
    **kwargs : dict[str, Variable]
        The arguments whose types will be printed.
    """

    __slots__ = ("_args", "_error_msg", "_error_type")
    _attribute_nodes = ("_args",)

    def __init__(self, error_type, error_msg: str, **kwargs):
        """Initialize one ``PyArgumentError`` model instance."""
        assert isinstance(error_type, Variable)
        assert isinstance(error_msg, str)
        args = []
        # Find all expressions of the style '{type(var_name)}' in the error message
        type_indicators = re.findall(r"{type\([a-zA-Z0-9_]+\)}", error_msg)
        # Save the error message, replacing type indicators with the format string
        self._error_msg = re.sub(r"{type\([a-zA-Z0-9_]+\)}", "%V", error_msg)
        # Find the relevant arguments for each type indicator
        for t in type_indicators:
            var_name = t.removeprefix("{type(").removesuffix(")}")
            args.append(ObjectAddress(kwargs[var_name]))

        self._args = tuple(args)
        self._error_type = error_type
        init_model_object(self)

    @property
    def error_type(self):
        """
        The error type that should be raised.

        The error type that should be raised.
        """
        return self._error_type

    @property
    def error_msg(self):
        """
        The error message that should be formatted.

        The error message that should be formatted.
        """
        return self._error_msg

    @property
    def args(self):
        """
        The arguments whose types are printed in the error message.

        The arguments whose types are printed in the error message.
        These arguments are displayed in the order they appear in
        the error message.
        """
        return self._args


# -------------------------------------------------------------------
#                      Python.h Constants
# -------------------------------------------------------------------

# Python.h object  representing Booleans True and False
Py_True = Variable(PythonObjectType(), "Py_True", memory_handling="alias")
Py_False = Variable(PythonObjectType(), "Py_False", memory_handling="alias")

# Python.h object representing None
Py_None = Variable(PythonObjectType(), "Py_None", memory_handling="alias")

# https://docs.python.org/3/c-api/refcounting.html#c.Py_INCREF
Py_INCREF = FunctionDef(
    name="Py_INCREF",
    body=[],
    arguments=[FunctionDefArgument(Variable(PythonObjectType(), name="o", memory_handling="alias"))],
)

# https://docs.python.org/3/c-api/refcounting.html#c.Py_DECREF
Py_DECREF = FunctionDef(
    name="Py_DECREF",
    body=[],
    arguments=[FunctionDefArgument(Variable(PythonObjectType(), name="o", memory_handling="alias"))],
)

# https://docs.python.org/3/c-api/type.html#c.PyType_Ready
PyType_Ready = FunctionDef(
    name="PyType_Ready",
    body=[],
    arguments=[FunctionDefArgument(Variable(PythonObjectType(), name="o", memory_handling="alias"))],
    results=FunctionDefResult(Variable(NumpyInt64Type(), "_")),
)

# https://docs.python.org/3/c-api/sys.html#PySys_GetObject
PySys_GetObject = FunctionDef(
    name="PySys_GetObject",
    body=[],
    arguments=[FunctionDefArgument(Variable(StringType(), name="_"))],
    results=FunctionDefResult(Variable(PythonObjectType(), name="o", memory_handling="alias")),
)

# https://docs.python.org/3/c-api/unicode.html#c.PyUnicode_FromString
PyUnicode_FromString = FunctionDef(
    name="PyUnicode_FromString",
    body=[],
    arguments=[FunctionDefArgument(Variable(StringType(), name="_"))],
    results=FunctionDefResult(Variable(PythonObjectType(), name="o", memory_handling="alias")),
)

# -------------------------------------------------------------------

# using the documentation of PyArg_ParseTuple() and Py_BuildValue https://docs.python.org/3/c-api/arg.html
pytype_parse_registry = {
    NumpyFloat64Type(): "d",
    NumpyComplex128Type(): "O",
    NumpyBoolType(): "p",
    StringType(): "s",
    CharType(): "s",
    PythonObjectType(): "O",
}

# -------------------------------------------------------------------
#                      python_runtime.h functions
# -------------------------------------------------------------------

# Functions definitions are defined in x2py/stdlib/x2py_runtime/python_runtime.c
py_to_c_registry = {
    (PrimitiveBooleanType(), -1): "PyBool_to_Bool",
    (PrimitiveIntegerType(), 1): "PyInt8_to_Int8",
    (PrimitiveIntegerType(), 2): "PyInt16_to_Int16",
    (PrimitiveIntegerType(), 4): "PyInt32_to_Int32",
    (PrimitiveIntegerType(), 8): "PyInt64_to_Int64",
    (PrimitiveFloatingPointType(), 4): "PyFloat_to_Float",
    (PrimitiveFloatingPointType(), 8): "PyDouble_to_Double",
    (PrimitiveComplexType(), 4): "PyComplex_to_Complex64",
    (PrimitiveComplexType(), 8): "PyComplex_to_Complex128",
}


def C_to_Python(c_object):
    """
    Create a FunctionDef responsible for casting scalar C results to Python.

    Creates a FunctionDef node which contains all the code necessary
    for casting a C object, whose characteristics match that of the object
    passed as an argument, to a PythonObject which can be used in Python code.

    Parameters
    ----------
    c_object : Variable
        The variable needed for the generation of the cast_function.

    Returns
    -------
    FunctionDef
        The function which casts the C object to Python.
    """
    assert c_object.rank == 0
    try:
        cast_function = c_to_py_registry[c_object.dtype]
    except KeyError:
        raise TypeError(f"No C-to-Python cast registered for {c_object.dtype}") from None
    memory_handling = "alias"

    return FunctionDef(
        name=cast_function,
        body=[],
        arguments=[
            FunctionDefArgument(
                c_object.clone(
                    "v",
                    is_argument=True,
                    memory_handling=memory_handling,
                    new_class=Variable,
                )
            )
        ],
        results=FunctionDefResult(Variable(PythonObjectType(), name="o", memory_handling="alias")),
    )


# Functions definitions are defined in x2py/stdlib/x2py_runtime/python_runtime.c
c_to_py_registry = {
    NumpyBoolType(): "Bool_to_PyBool",
    NumpyInt64Type(): "Int" + str(NumpyInt64Type().precision * 8) + "_to_PyLong",
    NumpyFloat64Type(): "Double_to_PyDouble",
    NumpyComplex128Type(): "Complex128_to_PyComplex",
}


# -------------------------------------------------------------------
#              errors and check functions
# -------------------------------------------------------------------

# https://docs.python.org/3/c-api/exceptions.html#c.PyErr_Occurred
PyErr_Occurred = FunctionDef(
    name="PyErr_Occurred",
    arguments=[],
    results=FunctionDefResult(Variable(PythonObjectType(), name="r", memory_handling="alias")),
    body=[],
)

PyErr_SetString = FunctionDef(
    name="PyErr_SetString",
    body=[],
    arguments=[
        FunctionDefArgument(Variable(PythonObjectType(), name="o")),
        FunctionDefArgument(Variable(CharType(), name="s", memory_handling="alias")),
    ],
)

PyErr_SetObject = FunctionDef(
    name="PyErr_SetObject",
    body=[],
    arguments=[
        FunctionDefArgument(Variable(PythonObjectType(), name="o")),
        FunctionDefArgument(Variable(PythonObjectType(), name="value", memory_handling="alias")),
    ],
)

PyErr_WarnEx = FunctionDef(
    name="PyErr_WarnEx",
    body=[],
    arguments=[
        FunctionDefArgument(Variable(PythonObjectType(), name="category")),
        FunctionDefArgument(Variable(CharType(), name="message", memory_handling="alias")),
        FunctionDefArgument(Variable(Py_ssize_t(), name="stack_level")),
    ],
    results=FunctionDefResult(Variable(CNativeInt(), name="status")),
)

PyNotImplementedError = Variable(PythonObjectType(), name="PyExc_NotImplementedError")
PyMemoryError = Variable(PythonObjectType(), name="PyExc_MemoryError")
PyTypeError = Variable(PythonObjectType(), name="PyExc_TypeError")
PyAttributeError = Variable(PythonObjectType(), name="PyExc_AttributeError")
PyRuntimeError = Variable(PythonObjectType(), name="PyExc_RuntimeError")
PyRuntimeWarning = Variable(PythonObjectType(), name="PyExc_RuntimeWarning")

PyObject_TypeCheck = FunctionDef(
    name="PyObject_TypeCheck",
    arguments=[
        FunctionDefArgument(Variable(PythonObjectType(), "o", memory_handling="alias")),
        FunctionDefArgument(Variable(PythonClassType(), "c_type", memory_handling="alias")),
    ],
    results=FunctionDefResult(Variable(NumpyBoolType(), "r")),
    body=[],
)

# -------------------------------------------------------------------
#                          List functions
# -------------------------------------------------------------------

# https://docs.python.org/3/c-api/list.html#c.PyList_New
PyList_New = FunctionDef(
    name="PyList_New",
    arguments=[FunctionDefArgument(Variable(NumpyInt64Type(), "size"), value=convert_to_literal(0))],
    results=FunctionDefResult(Variable(PythonObjectType(), "r", memory_handling="alias")),
    body=[],
)

# https://docs.python.org/3/c-api/list.html#c.PyList_Append
PyList_Append = FunctionDef(
    name="PyList_Append",
    arguments=[
        FunctionDefArgument(Variable(PythonObjectType(), "list", memory_handling="alias")),
        FunctionDefArgument(Variable(PythonObjectType(), "item", memory_handling="alias")),
    ],
    results=FunctionDefResult(Variable(CNativeInt(), "i")),
    body=[],
)

# https://docs.python.org/3/c-api/list.html#c.PyList_GetItem
PyList_GetItem = FunctionDef(
    name="PyList_GetItem",
    arguments=[
        FunctionDefArgument(Variable(PythonObjectType(), "list", memory_handling="alias")),
        FunctionDefArgument(Variable(NumpyInt64Type(), "i")),
    ],
    results=FunctionDefResult(Variable(PythonObjectType(), "item", memory_handling="alias")),
    body=[],
)

# https://docs.python.org/3/c-api/list.html#c.PyList_SetItem
PyList_SetItem = FunctionDef(
    name="PyList_SetItem",
    body=[],
    arguments=[
        FunctionDefArgument(Variable(PythonObjectType(), name="l", memory_handling="alias")),
        FunctionDefArgument(Variable(NumpyInt64Type(), name="i")),
        FunctionDefArgument(Variable(PythonObjectType(), name="new_item", memory_handling="alias")),
    ],
    results=FunctionDefResult(Variable(CNativeInt(), "i")),
)


# -------------------------------------------------------------------
#                         Dict functions
# -------------------------------------------------------------------


# https://docs.python.org/3/c-api/dict.html#c.PyDict_New
PyDict_New = FunctionDef(
    name="PyDict_New",
    arguments=[],
    results=FunctionDefResult(Variable(PythonObjectType(), "dict", memory_handling="alias")),
    body=[],
)

# https://docs.python.org/3/c-api/dict.html#c.PyDict_SetItem
PyDict_SetItem = FunctionDef(
    name="PyDict_SetItem",
    arguments=[
        FunctionDefArgument(Variable(PythonObjectType(), "dict", memory_handling="alias")),
        FunctionDefArgument(Variable(PythonObjectType(), "key", memory_handling="alias")),
        FunctionDefArgument(Variable(PythonObjectType(), "val", memory_handling="alias")),
    ],
    results=FunctionDefResult(Variable(NumpyInt64Type(), "i")),
    body=[],
)


# -------------------------------------------------------------------
#                         String functions
# -------------------------------------------------------------------
# https://docs.python.org/3/c-api/unicode.html#c.PyUnicode_AsUTF8
PyUnicode_AsUTF8 = FunctionDef(
    name="PyUnicode_AsUTF8",
    arguments=[FunctionDefArgument(Variable(PythonObjectType(), "unicode", memory_handling="alias"))],
    results=FunctionDefResult(Variable(CharType(), "str", memory_handling="alias")),
    body=[],
)

# https://docs.python.org/3/c-api/unicode.html#c.PyUnicode_AsUTF8AndSize
PyUnicode_AsUTF8AndSize = FunctionDef(
    name="PyUnicode_AsUTF8AndSize",
    arguments=[
        FunctionDefArgument(Variable(PythonObjectType(), "unicode", memory_handling="alias")),
        FunctionDefArgument(Variable(Py_ssize_t(), "size", memory_handling="alias")),
    ],
    results=FunctionDefResult(Variable(CharType(), "str", memory_handling="alias")),
    body=[],
)

# https://docs.python.org/3/c-api/unicode.html#c.PyUnicode_Check
PyUnicode_Check = FunctionDef(
    name="PyUnicode_Check",
    arguments=[FunctionDefArgument(Variable(PythonObjectType(), "str", memory_handling="alias"))],
    results=FunctionDefResult(Variable(CNativeInt(), "out")),
    body=[],
)

c_memcpy = FunctionDef(
    name="memcpy",
    arguments=[
        FunctionDefArgument(Variable(VoidType(), "dest", memory_handling="alias")),
        FunctionDefArgument(Variable(VoidType(), "src", memory_handling="alias")),
        FunctionDefArgument(Variable(NumpyInt64Type(), "n")),
    ],
    results=FunctionDefResult(NIL),
    body=[],
)

c_memset = FunctionDef(
    name="memset",
    arguments=[
        FunctionDefArgument(Variable(VoidType(), "s", memory_handling="alias")),
        FunctionDefArgument(Variable(CNativeInt(), "c")),
        FunctionDefArgument(Variable(NumpyInt64Type(), "n")),
    ],
    results=FunctionDefResult(NIL),
    body=[],
)

c_strlen = FunctionDef(
    name="strlen",
    arguments=[FunctionDefArgument(Variable(CharType(), "s", memory_handling="alias"))],
    results=FunctionDefResult(Variable(CNativeInt(), "n")),
    body=[],
)

x2py_malloc = FunctionDef(
    name="x2py_malloc",
    arguments=[FunctionDefArgument(Variable(NumpyInt64Type(), "size"))],
    results=FunctionDefResult(Variable(VoidType(), "ptr", memory_handling="alias")),
    body=[],
)

# Functions definitions are defined in x2py/stdlib/x2py_runtime/python_runtime.c
check_type_registry = {
    NumpyBoolType(): "PyIs_Bool",
    NumpyInt64Type(): "PyIs_NativeInt",
    NumpyFloat64Type(): "PyIs_NativeFloat",
    NumpyComplex128Type(): "PyIs_NativeComplex",
}


for _model_cls in (
    PyArgKeywords,
    PyArg_ParseTupleNode,
    PyGetSetDefElement,
    PyArgumentError,
):
    register_model_class(_model_cls)

del _model_cls
