"""
Module describing all elements of the AST needed to represent elements which appear in a Fortran-C binding
file.
"""

from functools import cache

from .models.core import (
    ClassDef,
    Deallocate,
    FunctionDef,
    FunctionDefArgument,
    FunctionDefResult,
    Module,
    Function,
)
from .models.datatypes import (
    FixedSizeType,
    init_model_object,
    NumpyInt64Type,
    register_model_class,
    StringType,
    Type,
    TupleType,
    convert_to_literal,
)
from .models.core import Variable

__all__ = (
    "C_NULL_CHAR",
    "BindCArrayType",
    "BindCArrayVariable",
    "BindCClassDef",
    "BindCClassProperty",
    "BindCFunctionDef",
    "BindCModule",
    "BindCModuleConstant",
    "BindCModuleVariable",
    "BindCPointer",
    "BindCResultTupleType",
    "BindCScalarModuleVariable",
    "BindCSizeOf",
    "BindCVariable",
    "CLocFunc",
    "C_F_Pointer",
    "DeallocatePointer",
    "FortranTransfer",
    "c_malloc",
)

# =======================================================================================
#                                    Datatypes
# =======================================================================================


class BindCPointer(FixedSizeType):
    """
    Datatype representing a C pointer in Fortran.

    Datatype representing a C pointer in Fortran. This data type is defined
    in the iso_c_binding module.
    """

    __slots__ = ()
    _name = "bindcpointer"


class BindCArrayType(Type, TupleType):
    """
    Datatype for a tuple containing all the information necessary to describe an array.

    Datatype for a tuple containing a pointer to array data and integers describing their
    shape and strides.
    """

    __slots__ = ("_array_rank", "_element_types", "_has_itemsize", "_has_rank", "_has_strides")
    _name = "BindCArrayType"

    @classmethod
    def get_new(cls, rank, has_strides, has_rank=False, has_itemsize=False):
        """
        Get the parametrised BindCArrayType subclass.

        Get the parametrised BindCArrayType subclass.

        Parameters
        ----------
        rank : int
            The rank of the array being described.
        has_strides : bool
            Indicates whether strides are used to describe the array.
        has_rank : bool
            Indicates whether the descriptor carries a runtime rank field.
        has_itemsize : bool
            Indicates whether the descriptor carries a fixed-width character
            element byte length.
        """
        if not isinstance(rank, int):
            raise TypeError("rank must be an integer")
        if rank < 1:
            raise ValueError("rank must be positive")
        if not isinstance(has_strides, bool):
            raise TypeError("has_strides must be a boolean")
        if not isinstance(has_rank, bool):
            raise TypeError("has_rank must be a boolean")
        if not isinstance(has_itemsize, bool):
            raise TypeError("has_itemsize must be a boolean")
        return cls._get_new(rank, has_strides, has_rank, has_itemsize)

    @classmethod
    @cache
    def _get_new(cls, rank, has_strides, has_rank, has_itemsize):
        rank_types = (NumpyInt64Type(),) if has_rank else ()
        itemsize_types = (NumpyInt64Type(),) if has_itemsize else ()
        shape_types = (NumpyInt64Type(),) * rank
        ubound_types = (NumpyInt64Type(),) * rank * has_strides
        stride_types = (NumpyInt64Type(),) * rank * has_strides
        element_types = (BindCPointer(), *rank_types, *itemsize_types, *shape_types, *ubound_types, *stride_types)

        def __init__(self):
            self._array_rank = rank
            self._has_strides = has_strides
            self._has_rank = has_rank
            self._has_itemsize = has_itemsize
            self._element_types = element_types
            Type.__init__(self)

        name = f"BindCArray{rank}DType"
        if has_rank:
            name += "_ranked"
        if has_itemsize:
            name += "_itemsize"
        if has_strides:
            name += "_strided"
        return type(name, (BindCArrayType,), {"__init__": __init__})()

    @property
    def array_rank(self):
        """Rank of the array described by this packed argument."""
        return self._array_rank

    @property
    def has_strides(self):
        """Whether upper bounds and strides are present in the packed argument."""
        return self._has_strides

    @property
    def has_rank(self):
        """Whether a runtime rank field is present in the packed argument."""
        return self._has_rank

    @property
    def has_itemsize(self):
        """Whether a fixed-width character itemsize field is present."""
        return self._has_itemsize

    @property
    def element_types(self):
        """Types of the pointer, shape, upper-bound, and stride fields."""
        return self._element_types

    @property
    def container_rank(self):
        """Rank of the packed descriptor itself."""
        return 1

    @property
    def rank(self):
        """Rank of the packed descriptor itself."""
        return 1

    @property
    def order(self):
        """Memory order is not applicable to the packed descriptor."""
        return None

    @property
    def datatype(self):
        """The descriptor is heterogeneous, so its datatype is the descriptor itself."""
        return self

    def shape_is_compatible(self, shape):
        """Return whether ``shape`` has one entry with the descriptor field count."""
        return isinstance(shape, tuple) and len(shape) == 1 and shape[0] == len(self)

    def __getitem__(self, index):
        return self._element_types[index]

    def __len__(self):
        return len(self._element_types)

    def __iter__(self):
        return iter(self._element_types)


class BindCResultTupleType(Type, TupleType):
    """Datatype for a heterogeneous set of C-compatible function outputs."""

    __slots__ = ("_element_types",)
    _name = "BindCResultTupleType"

    @classmethod
    def get_new(cls, element_types):
        element_types = tuple(element_types)
        if len(element_types) < 2:
            raise ValueError("Bind-C result tuples require at least two elements")
        return cls._get_new(element_types)

    @classmethod
    @cache
    def _get_new(cls, element_types):
        def __init__(self):
            self._element_types = element_types
            Type.__init__(self)

        name = f"BindCResultTuple{len(element_types)}Type"
        return type(name, (BindCResultTupleType,), {"__init__": __init__})()

    @property
    def element_types(self):
        """Types of the packed C-compatible result fields."""
        return self._element_types

    @property
    def container_rank(self):
        """Rank of the packed result descriptor itself."""
        return 1

    @property
    def rank(self):
        """Rank of the packed result descriptor itself."""
        return 1

    @property
    def order(self):
        """Memory order is not applicable to the packed result descriptor."""
        return None

    @property
    def datatype(self):
        """The descriptor is heterogeneous, so its datatype is the descriptor itself."""
        return self

    def shape_is_compatible(self, shape):
        """Return whether ``shape`` has one entry with the descriptor field count."""
        return isinstance(shape, tuple) and len(shape) == 1 and shape[0] == len(self)

    def __getitem__(self, index):
        return self._element_types[index]

    def __len__(self):
        return len(self._element_types)

    def __iter__(self):
        return iter(self._element_types)


# =======================================================================================
#                                   Wrapper classes
# =======================================================================================


class BindCFunctionDef(FunctionDef):
    """
    Represents the definition of a C-compatible function.

    Contains the C-compatible version of the function which is
    used for the wrapper.
    As compared to a normal FunctionDef, this version contains
    arguments for the shape of arrays. It should be generated by
    calling `codegen.wrapper.FortranToCWrapper.wrap`.

    Parameters
    ----------
    *args : list
        See FunctionDef.

    original_function : FunctionDef
        The function from which the C-compatible version was created.

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
        self._original_function = original_function
        super().__init__(*args, **kwargs)
        assert all(isinstance(a, FunctionDefArgument) for a in self._arguments)

    @property
    def original_function(self):
        """
        The function which is wrapped by this BindCFunctionDef.

        The original function which would be printed in pure Fortran which is not
        compatible with C.
        """
        return self._original_function

    def rename(self, newname):
        """
        Rename the FunctionDef name->newname.

        Rename the FunctionDef name->newname.

        Parameters
        ----------
        newname : str
            New name for the FunctionDef.
        """
        self._name = newname


# =======================================================================================


class BindCVariable(Variable):
    """
    A wrapper linking the new C-compatible variable to the original variable.

    A wrapper linking the new C-compatible variable to the variable that is accessible
    via this information. This object is a variable which mimics the new variable so
    it can be used in some of the same contexts but the underlying variables should be
    extracted before manipulating them.

    Parameters
    ----------
    new_var : Variable
        The new C-compatible variable.
    original_var : Variable
        The original variable in the target language.
    """

    __slots__ = ("_new_var", "_original_var")
    _attribute_nodes = (*Variable._attribute_nodes, "_new_var", "_original_var")

    def __init__(self, new_var, original_var):
        self._new_var = new_var
        self._original_var = original_var
        super().__init__(
            new_var.class_type,
            new_var.name,
            memory_handling=new_var.memory_handling,
            is_optional=new_var.is_optional,
            shape=new_var.shape,
            ownership_decision=getattr(new_var, "ownership_decision", None)
            or getattr(original_var, "ownership_decision", None),
        )

    @property
    def new_var(self):
        """
        The new C-compatible variable.

        The new C-compatible variable.
        """
        return self._new_var

    @property
    def original_var(self):
        """
        The original variable in the target language.

        The original variable from the target language that was wrapped.
        """
        return self._original_var


# =======================================================================================
class BindCModule(Module):
    """
    Represents a Module which only contains functions compatible with C.

    Represents a Module which provides the C-Fortran interface to another module.
    Both functions and module variables are wrapped in order to be compatible with
    C.

    Parameters
    ----------
    *args : tuple
        See `x2py.ast.core.Module`.

    original_module : Module
        The Module being wrapped.

    variable_wrappers : list of BindCFunctionDef
        A list containing all the functions which expose module variables to C.

    removed_functions : list of FunctionDef
        A list of any functions which weren't translated to BindCFunctionDef
        objects (e.g. private functions).

    **kwargs : dict
        See `x2py.ast.core.Module`.

    See Also
    --------
    x2py.ast.core.Module
        The class from which BindCModule inherits which contains all details
        about the args and kwargs.
    """

    __slots__ = ("_orig_mod", "_removed_functions", "_variable_wrappers")
    _attribute_nodes = (
        *Module._attribute_nodes,
        "_orig_mod",
        "_variable_wrappers",
        "_removed_functions",
    )

    def __init__(
        self,
        *args,
        original_module,
        variable_wrappers=(),
        removed_functions=None,
        **kwargs,
    ):
        self._orig_mod = original_module
        self._variable_wrappers = variable_wrappers
        self._removed_functions = removed_functions
        super().__init__(*args, **kwargs)

    @property
    def original_module(self):
        """
        The module which was wrapped.

        The original module for which this object provides the C-Fortran interface.
        """
        return self._orig_mod

    @property
    def variable_wrappers(self):
        """
        Get the wrappers which expose module variables to C.

        Get a list containing all the BindCFunctionDefs which expose module variables to C.
        """
        return self._variable_wrappers

    @property
    def removed_functions(self):
        """
        Get the functions which weren't translated to BindCFunctionDef objects.

        Get a list of the functions which weren't translated to BindCFunctionDef objects.
        This includes private functions and objects for which wrapper support is lacking.
        """
        return self._removed_functions

    @property
    def declarations(self):
        """
        Get the declarations of all module variables.

        In the case of a BindCModule no variables should be declared. Plain variables
        are used directly from the original module and more complex variables require
        wrapper functions.
        """
        return ()


# =======================================================================================


class BindCModuleVariable(Variable):
    """
    A class which wraps a compatible variable from Fortran to make it available in C.

    A class which wraps a compatible module variable from Fortran to make it available
    in C. A compatible variable is a variable which can be exposed to C simply using
    iso_c_binding (i.e. no wrapper function is required).

    Parameters
    ----------
    *args : tuple
        See Variable.

    **kwargs : dict
        See Variable.

    See Also
    --------
    Variable : The super class.
    """

    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BindCModuleConstant(Variable):
    """
    A Python-exported constant that has no mutable native storage.
    """

    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BindCScalarModuleVariable(Variable):
    """
    Generated getter and setter wrappers for a scalar module variable.
    """

    __slots__ = ("_getter_function", "_setter_function")
    _attribute_nodes = ("_getter_function", "_setter_function")

    def __init__(self, *args, getter_function, setter_function, **kwargs):
        self._getter_function = getter_function
        self._setter_function = setter_function
        super().__init__(*args, **kwargs)

    @property
    def getter_function(self):
        """Generated native getter for this module variable."""
        return self._getter_function

    @property
    def setter_function(self):
        """Generated native setter for this module variable."""
        return self._setter_function


# =======================================================================================


class BindCArrayVariable(Variable):
    """
    A class which wraps an array from Fortran to make it available in C.

    A class which wraps an array from Fortran to make it available in C.

    Parameters
    ----------
    *args : tuple
        See Variable.

    wrapper_function : FunctionDef
        The function which can be used to access the array.

    original_variable : Variable
        The original variable in the Fortran code.

    **kwargs : dict
        See Variable.

    See Also
    --------
    Variable : The super class.
    """

    __slots__ = ("_original_variable", "_wrapper_function")
    _attribute_nodes = ("_wrapper_function", "_original_variable")

    def __init__(self, *args, wrapper_function, original_variable, **kwargs):
        self._original_variable = original_variable
        self._wrapper_function = wrapper_function
        super().__init__(*args, **kwargs)

    @property
    def original_variable(self):
        """
        The original variable in the Fortran code.

        The original variable in the Fortran code. This is important in
        order to access the correct type and other details about the
        Variable.
        """
        return self._original_variable

    @property
    def wrapper_function(self):
        """
        The function which can be used to access the array.

        The function which can be used to access the array. The function
        must return the pointer to the raw data and information about
        the shape.
        """
        return self._wrapper_function


# =======================================================================================


class BindCClassProperty:
    """
    A class which wraps a class attribute.

    A class which wraps a class attribute to make it accessible
    from C. In the future this class will also be used to handle properties of
    classes (i.e. functions marked with the `@property` decorator).

    Parameters
    ----------
    python_name : str
        The name of the attribute/property in the original Python code.
    getter : FunctionDef
        The function which collects the value of the class attribute.
    setter : FunctionDef
        The function which modifies the value of the class attribute.
    class_type : Variable
        The type of the class to which the attribute belongs.
    docstring : Literal, optional
        The docstring of the property.
    getter_policy : object, optional
        Completed policy for the getter result.
    setter_policy : object, optional
        Completed policy for setter availability and conversion.
    """

    __slots__ = (
        "_class_type",
        "_docstring",
        "_getter",
        "_getter_policy",
        "_python_name",
        "_setter",
        "_setter_policy",
    )
    _attribute_nodes = ("_getter", "_setter")

    def __init__(
        self,
        python_name,
        getter,
        setter,
        class_type,
        docstring=None,
        *,
        getter_policy=None,
        setter_policy=None,
    ):
        assert isinstance(getter, BindCFunctionDef)
        assert isinstance(setter, BindCFunctionDef) or setter is None
        self._python_name = python_name
        self._getter = getter
        self._setter = setter
        self._getter_policy = getter_policy
        self._setter_policy = setter_policy
        self._class_type = class_type
        self._docstring = docstring
        init_model_object(self)

    @property
    def getter(self):
        """
        The BindCFunctionDef describing the getter function.

        The BindCFunctionDef describing the function which allows the user to collect
        the value of the property.
        """
        return self._getter

    @property
    def getter_policy(self):
        """Return the completed policy for reading this property."""
        return self._getter_policy

    @property
    def setter(self):
        """
        The BindCFunctionDef describing the setter function.

        The BindCFunctionDef describing the function which allows the user to modify
        the value of the property.
        """
        return self._setter

    @property
    def setter_policy(self):
        """Return the completed policy for writing this property."""
        return self._setter_policy

    @property
    def class_type(self):
        """
        The type of the class to which the attribute belongs.

        The type of the class to which the attribute belongs.
        """
        return self._class_type

    @property
    def python_name(self):
        """
        The name of the attribute/property in the original Python code.

        The name of the attribute/property in the original Python code.
        """
        return self._python_name

    @property
    def docstring(self):
        """
        The docstring of the property being wrapped.

        The docstring of the property being wrapped.
        """
        return self._docstring


# =======================================================================================


class BindCClassDef(ClassDef):
    """
    Represents a class which is compatible with C.

    Represents a class which is compatible with C. This means that it stores
    C-compatible versions of class methods and getters and setters for class
    variables.

    Parameters
    ----------
    original_class : ClassDef
        The class being wrapped.

    new_func : BindCFunctionDef
        The function which provides a new instance of the class.

    **kwargs : dict
        See ClassDef.
    """

    __slots__ = ("_new_func", "_original_class")

    def __init__(self, original_class, new_func, **kwargs):
        self._original_class = original_class
        self._new_func = new_func
        super().__init__(original_class.name, scope=original_class.scope, **kwargs)

    @property
    def new_func(self):
        """
        Get the wrapper for `__new__`.

        Get the wrapper for `__new__` which allocates the memory for the class instance.
        """
        return self._new_func


# =======================================================================================
#                                   Utility functions
# =======================================================================================


class CLocFunc:
    """
    Creates a C-compatible pointer to the argument.

    Class representing the iso_c_binding function cloc which returns a valid
    C pointer to the location where an object can be found.

    Parameters
    ----------
    argument : Variable
        The object which should be pointed to.

    result : Variable of dtype BindCPointer
        The variable where the C-compatible pointer should be stored.
    """

    __slots__ = ("_arg", "_result")
    _attribute_nodes = ()

    def __init__(self, argument, result):
        self._arg = argument
        self._result = result
        assert result.dtype is BindCPointer()
        init_model_object(self)

    @property
    def arg(self):
        """
        Pointer target.

        Object which will be pointed at by the result pointer.
        """
        return self._arg

    @property
    def result(self):
        """
        The variable where the C-compatible pointer should be stored.

        The variable where the C-compatible pointer of dtype BindCPointer
        should be stored.
        """
        return self._result


# =======================================================================================


class C_F_Pointer:
    """
    Creates a Fortran array pointer from a C pointer and size information.

    Represents the iso_c_binding function C_F_Pointer which takes a pointer
    to an object in C (with dtype BindCPointer) and a list of sizes and returns
    a Fortran array pointer.

    Parameters
    ----------
    c_expr : Variable of dtype BindCPointer
        The Variable containing the C pointer.

    f_expr : Variable
        The Variable containing the resulting array.

    shape : list of Variables
        A list describing the Variables which dictate the size of the array in each dimension.
    """

    __slots__ = ("_c_expr", "_f_expr", "_shape")
    _attribute_nodes = ("_c_expr", "_f_expr", "_shape")

    def __init__(self, c_expr, f_expr, shape=None):
        self._c_expr = c_expr
        self._f_expr = f_expr
        self._shape = shape
        init_model_object(self)

    @property
    def c_pointer(self):
        """
        The Variable containing the C pointer.

        The Variable of dtype BindCPointer which contains the C pointer.
        """
        return self._c_expr

    @property
    def f_array(self):
        """
        The Variable containing the resulting array.

        The Variable where the array pointer will be stored.
        """
        return self._f_expr

    @property
    def shape(self):
        """
        A list of the sizes of the array in each dimension.

        A list describing the Variables which are passed as arguments, in order to
        determine the size of the array in each dimension.
        """
        return self._shape


class DeallocatePointer(Deallocate):
    """
    Represents memory deallocation for memory only stored in a pointer.

    Represents memory deallocation for memory only stored in a pointer. Usually
    `deallocate` is not called on pointers so as not to delete the target values
    however this capability is necessary in the wrapper.

    Parameters
    ----------
    variable : x2py.ast.core.Variable
        The typed variable (usually an array) that needs memory deallocation.
    """

    __slots__ = ()


class BindCSizeOf(Function):
    """
    Represents a call to a function which can calculate the size of an object in bits.

    Represents a call to a function which can calculate the size of an object in bits.

    Parameters
    ----------
    element : model object
        The object whose type should be determined.
    """

    __slots__ = ()
    _class_type = NumpyInt64Type()
    _shape = None

    def __init__(self, element):
        super().__init__(element)


class FortranTransfer(Function):
    """Represent the Fortran ``transfer(source, mold[, size])`` intrinsic."""

    __slots__ = ("_class_type", "_shape")

    def __init__(self, source, mold, size=None):
        self._class_type = mold.class_type
        self._shape = mold.shape
        args = (source, mold) if size is None else (source, mold, size)
        super().__init__(*args)

    @property
    def source(self):
        return self.args[0]

    @property
    def mold(self):
        return self.args[1]

    @property
    def size(self):
        return self.args[2] if len(self.args) == 3 else None


class C_NULL_CHAR:
    """
    A class representing the C_NULL_CHAR character from the iso_c_binding module.

    A class representing the C_NULL_CHAR character from the iso_c_binding module.
    This object should be appended to strings before returning them from Fortran
    to C.
    """

    __slots__ = ()
    _class_type = StringType()
    _shape = (convert_to_literal(1),)
    _attribute_nodes = ()

    def __init__(self):
        init_model_object(self)


c_malloc = FunctionDef(
    "c_malloc",
    (FunctionDefArgument(Variable(NumpyInt64Type(), "size")),),
    (),
    FunctionDefResult(Variable(BindCPointer(), "ptr")),
)


for _model_cls in (
    BindCClassProperty,
    CLocFunc,
    C_F_Pointer,
    C_NULL_CHAR,
    FortranTransfer,
):
    register_model_class(_model_cls)

del _model_cls
