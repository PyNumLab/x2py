# coding: utf-8
# ------------------------------------------------------------------------- #
# This file is part of Pyccel which is released under MIT License. See the  #
# LICENSE file or go to https://github.com/pyccel/pyccel/blob/devel/LICENSE #
# for full license details.                                                 #
# ------------------------------------------------------------------------- #
"""
The Python interpreter has a number of built-in functions and types that are
always available.

In this module we implement some of them in alphabetical order.

"""

from .basic import PyccelAstNode, TypedAstNode
from .datatypes import (
    CharType,
    FixedSizeNumericType,
    GenericType,
    PrimitiveBooleanType,
    PrimitiveComplexType,
    PythonNativeBool,
    PythonNativeComplex,
    PythonNativeFloat,
    PythonNativeInt,
    StringType,
    SymbolicType,
    TupleType,
    TypeAlias,
    VoidType,
    original_type_to_pyccel_type,
)
from .core import PyccelFunction, Slice
from .datatypes import (
    Literal,
    LiteralComplex,
    LiteralFloat,
    LiteralImaginaryUnit,
    LiteralInteger,
    LiteralString,
    Nil,
    convert_to_literal,
)
from .operators import (
    PyccelAdd,
    PyccelAnd,
    PyccelIsNot,
    PyccelMinus,
    PyccelMul,
    PyccelNot,
    PyccelUnarySub,
)

__all__ = (
    "PythonAbs",
    "PythonBool",
    "PythonComplex",
    "PythonComplexProperty",
    "PythonFloat",
    "PythonImag",
    "PythonInt",
    "PythonLen",
    "PythonRange",
    "PythonReal",
    "PythonStr",
    "PythonTuple",
    "PythonType",
)
# ==============================================================================
class PythonComplexProperty(PyccelFunction):
    """
    Represents a call to the .real or .imag property.

    Represents a call to a property of a complex number. The relevant properties
    are the `.real` and `.imag` properties.

    e.g:
    >>> a = 1+2j
    >>> a.real
    1.0

    Parameters
    ----------
    arg : TypedAstNode
        The object which the property is called from.
    """

    __slots__ = ()
    _shape = None
    _class_type = PythonNativeFloat()

    def __init__(self, arg):
        super().__init__(arg)

    @property
    def internal_var(self):
        """Return the variable on which the function was called"""
        return self._args[0]


# ==============================================================================
class PythonReal(PythonComplexProperty):
    """
    Represents a call to the .real property.

    e.g:
    >>> a = 1+2j
    >>> a.real
    1.0

    Parameters
    ----------
    arg : TypedAstNode
        The object which the property is called from.
    """

    __slots__ = ()
    name = "real"

    def __new__(cls, arg):
        if isinstance(arg.dtype, PythonNativeBool):
            return PythonInt(arg)
        elif not isinstance(arg.dtype.primitive_type, PrimitiveComplexType):
            return arg
        else:
            return super().__new__(cls)

    def __str__(self):
        return f"Real({self.internal_var})"


# ==============================================================================
class PythonImag(PythonComplexProperty):
    """
    Represents a call to the .imag property.

    Represents a call to the .imag property of an object with a complex type.
    e.g:
    >>> a = 1+2j
    >>> a.imag
    1.0

    Parameters
    ----------
    arg : TypedAstNode
        The object on which the property is called.
    """

    __slots__ = ()
    name = "imag"

    def __new__(cls, arg):
        if not isinstance(arg.dtype.primitive_type, PrimitiveComplexType):
            return convert_to_literal(0, dtype=arg.dtype)
        else:
            return super().__new__(cls)

    def __str__(self):
        return f"Imag({self.internal_var})"

# ==============================================================================
class PythonBool(PyccelFunction):
    """
    Represents a call to Python's native `bool()` function.

    Represents a call to Python's native `bool()` function which casts an
    argument to a boolean.

    Parameters
    ----------
    arg : TypedAstNode
        The argument passed to the function.
    """

    __slots__ = ()
    name = "bool"
    _static_type = PythonNativeBool()
    _shape = None
    _class_type = PythonNativeBool()

    def __new__(cls, arg):
        if getattr(arg, "is_optional", None):
            bool_expr = super().__new__(cls)
            bool_expr.__init__(arg)
            return PyccelAnd(PyccelIsNot(arg, Nil()), bool_expr)
        else:
            return super().__new__(cls)

    @property
    def arg(self):
        """
        Get the argument which was passed to the function.

        Get the argument which was passed to the function.
        """
        return self._args[0]

    def __str__(self):
        return f"Bool({self.arg})"


# ==============================================================================
class PythonComplex(PyccelFunction):
    """
    Represents a call to Python's native `complex()` function.

    Represents a call to Python's native `complex()` function which casts an
    argument to a complex number.

    Parameters
    ----------
    arg0 : TypedAstNode
        The first argument passed to the function (either a real or a complex).

    arg1 : TypedAstNode, default=0
        The second argument passed to the function (the imaginary part).
    """

    __slots__ = ("_real_part", "_imag_part", "_internal_var", "_is_cast")
    name = "complex"

    _static_type = PythonNativeComplex()
    _shape = None
    _class_type = PythonNativeComplex()
    _real_cast = PythonReal
    _imag_cast = PythonImag
    _attribute_nodes = ("_real_part", "_imag_part", "_internal_var")

    def __new__(cls, arg0, arg1=0.):
        return super().__new__(cls)

    def __init__(self, arg0, arg1=0.):
        self._is_cast = arg1.python_value == 0.

        self._internal_var = None
        self._real_part = self._real_cast(arg0)
        self._imag_part = self._real_cast(arg1)
        super().__init__()

    @property
    def is_cast(self):
        """Indicates if the function is casting or assembling a complex"""
        return self._is_cast

    @property
    def real(self):
        """Returns the real part of the complex"""
        return self._real_part

    @property
    def imag(self):
        """Returns the imaginary part of the complex"""
        return self._imag_part

    @property
    def internal_var(self):
        """
        When the complex call is a cast, returns the variable being cast.

        When the complex call is a cast, returns the variable being cast.
        This property should only be used when handling a cast.
        """
        assert self._is_cast
        return self._internal_var

    def __str__(self):
        return f"complex({self.real}, {self.imag})"

# ==============================================================================
class PythonFloat(PyccelFunction):
    """
    Represents a call to Python's native `float()` function.

    Represents a call to Python's native `float()` function which casts an
    argument to a floating point number.

    Parameters
    ----------
    arg : TypedAstNode
        The argument passed to the function.
    """

    __slots__ = ()
    name = "float"
    _static_type = PythonNativeFloat()
    _shape = None
    _class_type = PythonNativeFloat()

    def __new__(cls, arg):
        return super().__new__(cls)

    def __init__(self, arg):
        super().__init__(arg)

    @property
    def arg(self):
        """
        Get the argument which was passed to the function.

        Get the argument which was passed to the function.
        """
        return self._args[0]

    def __str__(self):
        return f"float({self.arg})"

# ==============================================================================
class PythonInt(PyccelFunction):
    """
    Represents a call to Python's native `int()` function.

    Represents a call to Python's native `int()` function which casts an
    argument to an integer.

    Parameters
    ----------
    arg : TypedAstNode
        The argument passed to the function.
    """

    __slots__ = ()
    name = "int"
    _static_type = PythonNativeInt()
    _shape = None
    _class_type = PythonNativeInt()

    def __new__(cls, arg):
        return super().__new__(cls)

    def __init__(self, arg):
        super().__init__(arg)

    @property
    def arg(self):
        """
        Get the argument which was passed to the function.

        Get the argument which was passed to the function.
        """
        return self._args[0]


# ==============================================================================
class PythonTuple(TypedAstNode):
    """
    Class representing a call to Python's native (,) function which creates tuples.

    Class representing a call to Python's native (,) function
    which initialises a literal tuple.

    Parameters
    ----------
    *args : tuple of TypedAstNode
        The arguments passed to the tuple function.
    prefer_inhomogeneous : bool, default=False
        A boolean that can be used to ensure that the tuple is stocked as an
        inhomogeneous object even if it could be homogeneous.
    class_type : PyccelType, optional
        The final type of the tuple. This is necessary to create a printable
        empty tuple. Otherwise it is not used.
    """

    __slots__ = ("_args", "_is_homogeneous", "_shape", "_class_type")
    _iterable = True
    _attribute_nodes = ("_args",)

    def __init__(self, *args, prefer_inhomogeneous=False, class_type=None):
        self._args = args
        super().__init__()

        self._is_homogeneous = True
        if len(args) == 0:
            self._class_type = GenericType
            self._shape = (LiteralInteger(0),)
            return

        self._shape = (LiteralInteger(len(args)),)
        self._class_type = args[0]._class_type

    def __len__(self):
        return len(self._args)

    def __str__(self):
        args = ", ".join(str(a) for a in self)
        return f"({args})"

    def __repr__(self):
        args = ", ".join(str(a) for a in self)
        return f"PythonTuple({args})"

    @property
    def is_homogeneous(self):
        """
        Indicates whether the tuple is homogeneous or inhomogeneous.

        Indicates whether all elements of the tuple have the same dtype,
        rank, etc (homogenous) or if these values can vary (inhomogeneous).
        """
        return self._is_homogeneous

    @property
    def args(self):
        """
        Arguments of the tuple.

        The arguments that were used to initialise the tuple.
        """
        return self._args

# ==============================================================================
class PythonRange(TypedAstNode):
    """
    Class representing a range.

    Class representing a call to the built-in Python function `range`. This function
    is parametrised by an interval (described by a start element and a stop element)
    and a step. The step describes the number of elements between subsequent elements
    in the range.

    Parameters
    ----------
    *args : tuple of TypedAstNodes
        The arguments passed to the range.
        If one argument is passed then it represents the end of the interval.
        If two arguments are passed then they represent the start and end of the interval.
        If three arguments are passed then they represent the start, end and step of the interval.
    """

    __slots__ = ("_start", "_stop", "_step")
    _attribute_nodes = ("_start", "_stop", "_step")
    name = "range"

    def __init__(self, *args):
        # Define default values
        n = len(args)

        if n == 1:
            self._start = LiteralInteger(0)
            self._stop = args[0]
            self._step = LiteralInteger(1)
        elif n == 2:
            self._start = args[0]
            self._stop = args[1]
            self._step = LiteralInteger(1)
        elif n == 3:
            self._start = args[0]
            self._stop = args[1]
            self._step = args[2]
        else:
            raise ValueError("Range has at most 3 arguments")
        assert self._stop is not None

        super().__init__(0)

    @property
    def start(self):
        """
        Get the start of the interval.

        Get the start of the interval which the range iterates over.
        """
        return self._start

    @property
    def stop(self):
        """
        Get the end of the interval.

        Get the end of the interval which the range iterates over. The
        interval does not include this value.
        """
        return self._stop

    @property
    def step(self):
        """
        Get the step between subsequent elements in the range.

        Get the step between subsequent elements in the range.
        """
        return self._step

    def get_range(self):
        """
        Get this range.

        Get this range. This method is used to allow this class to be handled
        like other iterables which can be converted to PythonRange objects.

        Returns
        -------
        PythonRange
            This object.
        """
        return self

    def get_python_iterable_item(self):
        """
        Get the item of the iterable that will be saved to the loop targets.

        Returns an element of the range indexed with the iterators
        previously provided via the set_loop_counters method
        (useful to determine the dtype etc of the loop iterator).

        Returns
        -------
        list[TypedAstNode]
            A list of objects that should be assigned to variables.
        """
        return self._indices

    def get_assign_targets(self):
        """
        Get objects that should be assigned to variables to use the range.

        This method is used to allow this class to be handled like other iterables
        which can be converted to PythonRange objects.

        Returns
        -------
        list[TypedAstNode]
            An empty list.
        """
        return []

# ==============================================================================
class PythonStr(PyccelFunction):
    """
    Represents a call to Python's `str` function.

    Represents a call to Python's `str` function which describes a string
    cast.

    Parameters
    ----------
    arg : TypedAstNode
        The argument that is cast to a string.
    """

    __slots__ = ("_shape",)
    _static_type = StringType()
    _class_type = StringType()
    name = "str"

    def __new__(cls, arg):
        if isinstance(arg, LiteralString):
            return arg
        else:
            return super().__new__(cls)

    def __init__(self, arg):
        if not isinstance(arg.class_type, (StringType, CharType)):
            raise NotImplementedError(
                "Support for casting non-character types to strings is not yet available"
            )
        self._shape = (None,)
        super().__init__(arg)


# ==============================================================================

DtypePrecisionToCastFunction = {
    PythonNativeBool(): PythonBool,
    PythonNativeInt(): PythonInt,
    PythonNativeFloat(): PythonFloat,
    PythonNativeComplex(): PythonComplex,
}

# ==============================================================================
