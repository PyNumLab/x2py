from .datatypes import (
    NumpyComplex64Type,
    NumpyComplex128Type,
    NumpyComplex256Type,
    NumpyFloat32Type,
    NumpyFloat64Type,
    NumpyFloat128Type,
    NumpyInt8Type,
    NumpyInt16Type,
    NumpyInt32Type,
    NumpyInt64Type,
    NumpyNDArrayType,
    NumpyNumericType,
    numpy_precision_map,
)

from .builtins import (
    DtypePrecisionToCastFunction,
    PythonBool,
    PythonComplex,
    PythonFloat,
    PythonImag,
    PythonInt,
    PythonReal,
)

from .datatypes import PrimitiveIntegerType, ContainerType, PythonNativeBool, GenericType, FixedSizeNumericType
from .datatypes import typenames_to_dtypes as dtype_registry
from .datatypes import LiteralString
from .core import PyccelFunction

from .core import PyccelFunctionDef
dtype_registry.update(
    {
        "int8": NumpyInt8Type(),
        "int16": NumpyInt16Type(),
        "int32": NumpyInt32Type(),
        "int64": NumpyInt64Type(),
        "i1": NumpyInt8Type(),
        "i2": NumpyInt16Type(),
        "i4": NumpyInt32Type(),
        "i8": NumpyInt64Type(),
        "float32": NumpyFloat32Type(),
        "float64": NumpyFloat64Type(),
        "float128": NumpyFloat128Type(),
        "f4": NumpyFloat32Type(),
        "f8": NumpyFloat64Type(),
        "complex64": NumpyComplex64Type(),
        "complex128": NumpyComplex128Type(),
        "complex256": NumpyComplex256Type(),
        "c8": NumpyComplex64Type(),
        "c16": NumpyComplex128Type(),
    }
)

class NumpyResultType(PyccelFunction):
    """
    Class representing a call to the `numpy.result_type` function.

    A class representing a call to the NumPy function `result_type` which returns
    the datatype of an expression. This function can be used to access the `dtype`
    property of a NumPy array.

    Parameters
    ----------
    *arrays_and_dtypes : TypedAstNode
        Any arrays and dtypes passed to the function (currently only accepts one array
        and no dtypes).
    """

    __slots__ = ("_class_type",)
    _shape = None
    name = "result_type"

    def __init__(self, *arrays_and_dtypes):
        types = [
            (
                a.cls_name.static_type()
                if isinstance(a, PyccelFunctionDef)
                else a.class_type
            )
            for a in arrays_and_dtypes
        ]
        self._class_type = sum(types, start=GenericType())
        if isinstance(self._class_type, ContainerType):
            self._class_type = self._class_type.element_type

        super().__init__(*arrays_and_dtypes)

def process_dtype(dtype):
    """
    Analyse a dtype passed to a NumPy array creation function.

    This function takes a dtype passed to a NumPy array creation function,
    processes it in different ways depending on its type, and finally extracts
    the corresponding type and precision from the `dtype_registry` dictionary.

    This function could be useful when working with numpy creation function
    having a dtype argument, like numpy.array, numpy.arrange, numpy.linspace...

    Parameters
    ----------
    dtype : PyccelFunctionDef, LiteralString, str
        The actual dtype passed to the NumPy function.

    Returns
    -------
    Datatype
        The Datatype corresponding to the passed dtype.
    int
        The precision corresponding to the passed dtype.

    Raises
    ------
    TypeError: In the case of unrecognized argument type.
    TypeError: In the case of passed string argument not recognized as valid dtype.
    """
    if isinstance(dtype, NumpyResultType):
        dtype = dtype.dtype

    elif isinstance(dtype, PyccelFunctionDef):
        dtype = dtype.cls_name.static_type()

    elif isinstance(dtype, (LiteralString, str)):
        try:
            dtype = dtype_registry[str(dtype)]
        except KeyError as e:
            raise TypeError(f"Unknown type of {dtype}.") from e

    if isinstance(dtype, (NumpyNumericType, PythonNativeBool, GenericType)):
        return dtype
    if isinstance(dtype, FixedSizeNumericType):
        return numpy_precision_map[(dtype.primitive_type, dtype.precision)]
    else:
        raise TypeError(f"Unknown type of {dtype}.")
# =======================================================================================
class NumpyFloat(PythonFloat):
    """
    Represents a call to `numpy.float()` function.

    Represents a call to the NumPy cast function `float`.

    Parameters
    ----------
    arg : TypedAstNode
        The argument passed to the function.
    """

    __slots__ = ("_shape", "_class_type")
    _static_type = NumpyFloat64Type()
    name = "float"

    def __init__(self, arg):
        self._shape = arg.shape
        rank = arg.rank
        order = arg.order
        self._class_type = NumpyNDArrayType.get_new(self.static_type(), rank, order)
        super().__init__(arg)

    @property
    def is_elemental(self):
        """
        Indicates whether the function can be applied elementwise.

        Indicates whether the function should be
        called elementwise for an array argument
        """
        return True


class NumpyFloat32(NumpyFloat):
    """
    Represents a call to numpy.float32() function.

    Represents a call to numpy.float32() function.

    Parameters
    ----------
    arg : TypedAstNode
        The argument passed to the function.
    """

    __slots__ = ()
    _static_type = NumpyFloat32Type()
    name = "float32"


class NumpyFloat64(NumpyFloat):
    """
    Represents a call to numpy.float64() function.

    Represents a call to numpy.float64() function.

    Parameters
    ----------
    arg : TypedAstNode
        The argument passed to the function.
    """

    __slots__ = ()
    _static_type = NumpyFloat64Type()
    name = "float64"

class NumpyBool(PythonBool):
    """
    Represents a call to `numpy.bool()` function.

    Represents a call to the NumPy cast function `bool`.

    Parameters
    ----------
    arg : TypedAstNode
        The argument passed to the function.
    """

    __slots__ = ("_shape", "_class_type")
    name = "bool"

    def __init__(self, arg):
        self._shape = arg.shape
        rank = arg.rank
        order = arg.order
        self._class_type = NumpyNDArrayType.get_new(self.static_type(), rank, order)
        super().__init__(arg)

    @property
    def is_elemental(self):
        """
        Indicates whether the function can be applied elementwise.

        Indicates whether the function should be
        called elementwise for an array argument
        """
        return True

class NumpyInt(PythonInt):
    """
    Represents a call to `numpy.int()` function.

    Represents a call to the NumPy cast function `int`.

    Parameters
    ----------
    arg : TypedAstNode
        The argument passed to the function.
    base : TypedAstNode
        The argument passed to the function to indicate the base in which
        the integer is expressed.
    """

    __slots__ = ("_shape", "_class_type")
    _static_type = numpy_precision_map[
        (PrimitiveIntegerType(), PythonInt._static_type.precision)
    ]
    name = "int"

    def __init__(self, arg=None, base=10):
        if base != 10:
            raise TypeError("numpy.int's base argument is not yet supported")
        self._shape = arg.shape
        rank = arg.rank
        order = arg.order
        self._class_type = NumpyNDArrayType.get_new(self.static_type(), rank, order)
        super().__init__(arg)

    @property
    def is_elemental(self):
        """
        Indicates whether the function can be applied elementwise.

        Indicates whether the function should be
        called elementwise for an array argument
        """
        return True


class NumpyInt8(NumpyInt):
    """
    Represents a call to numpy.int8() function.

    Represents a call to numpy.int8() function.

    Parameters
    ----------
    arg : TypedAstNode
        The argument passed to the function.
    """

    __slots__ = ()
    _static_type = NumpyInt8Type()
    name = "int8"


class NumpyInt16(NumpyInt):
    """
    Represents a call to numpy.int16() function.

    Represents a call to numpy.int16() function.

    Parameters
    ----------
    arg : TypedAstNode
        The argument passed to the function.
    """

    __slots__ = ()
    _static_type = NumpyInt16Type()
    name = "int16"


class NumpyInt32(NumpyInt):
    """
    Represents a call to numpy.int32() function.

    Represents a call to numpy.int32() function.

    Parameters
    ----------
    arg : TypedAstNode
        The argument passed to the function.
    """

    __slots__ = ()
    _static_type = NumpyInt32Type()
    name = "int32"


class NumpyInt64(NumpyInt):
    """
    Represents a call to numpy.int64() function.

    Represents a call to numpy.int64() function.

    Parameters
    ----------
    arg : TypedAstNode
        The argument passed to the function.
    """

    __slots__ = ()
    _static_type = NumpyInt64Type()
    name = "int64"


# ==============================================================================
class NumpyReal(PythonReal):
    """
    Represents a call to numpy.real for code generation.

    Represents a call to the NumPy function real.
    > a = 1+2j
    > np.real(a)
    1.0

    Parameters
    ----------
    arg : TypedAstNode
        The argument passed to the function.
    """

    __slots__ = ("_shape", "_class_type")
    name = "real"

    def __new__(cls, arg):
        if isinstance(arg.dtype, PythonNativeBool):
            if arg.rank:
                return NumpyInt(arg)
            else:
                return PythonInt(arg)
        else:
            return super().__new__(cls, arg)

    def __init__(self, arg):
        super().__init__(arg)
        rank = arg.rank
        order = arg.order
        dtype = process_dtype(arg.dtype.element_type)
        self._class_type = NumpyNDArrayType.get_new(dtype, rank, order)
        self._shape = process_shape(self.rank == 0, self.internal_var.shape)

    @property
    def is_elemental(self):
        """Indicates whether the function should be
        called elementwise for an array argument
        """
        return True


# ==============================================================================


class NumpyImag(PythonImag):
    """
    Represents a call to numpy.imag for code generation.

    Represents a call to the NumPy function imag.
    > a = 1+2j
    > np.imag(a)
    2.0

    Parameters
    ----------
    arg : TypedAstNode
        The argument passed to the function.
    """

    __slots__ = ("_shape", "_class_type")
    name = "imag"

    def __new__(cls, arg):

        if not isinstance(arg.dtype.primitive_type, PrimitiveComplexType):
            dtype = (
                PythonNativeInt()
                if isinstance(arg.dtype, PythonNativeBool)
                else arg.dtype
            )
            if arg.rank == 0:
                return convert_to_literal(0, dtype)
            dtype = DtypePrecisionToCastFunction[dtype].static_type()
            return NumpyZeros(arg.shape, dtype=dtype)
        return super().__new__(cls, arg)

    def __init__(self, arg):
        super().__init__(arg)
        rank = arg.rank
        order = arg.order
        dtype = process_dtype(arg.dtype.element_type)
        self._class_type = NumpyNDArrayType.get_new(dtype, rank, order)
        self._shape = process_shape(self.rank == 0, self.internal_var.shape)

    @property
    def is_elemental(self):
        """Indicates whether the function should be
        called elementwise for an array argument
        """
        return True


# =======================================================================================
class NumpyComplex(PythonComplex):
    """
    Represents a call to `numpy.complex()` function.

    Represents a call to the NumPy cast function `complex`.

    Parameters
    ----------
    arg0 : TypedAstNode
        The first argument passed to the function. Either the array/scalar being cast
        or the real part of the complex.
    arg1 : TypedAstNode, optional
        The second argument passed to the function. The imaginary part of the complex.
    """

    _real_cast = NumpyReal
    _imag_cast = NumpyImag
    __slots__ = ("_shape", "_class_type")
    _static_type = NumpyComplex128Type()
    name = "complex"

    def __init__(self, arg0, arg1=None):
        if arg1 is not None:
            raise NotImplementedError(
                "Use builtin complex function not deprecated np.complex"
            )
        self._shape = arg0.shape
        rank = arg0.rank
        order = arg0.order
        self._class_type = NumpyNDArrayType.get_new(self.static_type(), rank, order)
        super().__init__(arg0)

    @property
    def is_elemental(self):
        """
        Indicates whether the function can be applied elementwise.

        Indicates whether the function should be
        called elementwise for an array argument
        """
        return True


class NumpyComplex64(NumpyComplex):
    """
    Represents a call to numpy.complex64() function.

    Represents a call to numpy.complex64() function.

    Parameters
    ----------
    arg0 : TypedAstNode
        The argument passed to the function.

    arg1 : TypedAstNode
        Unused inherited argument.
    """

    __slots__ = ()
    _static_type = NumpyComplex64Type()
    name = "complex64"


class NumpyComplex128(NumpyComplex):
    """
    Represents a call to numpy.complex128() function.

    Represents a call to numpy.complex128() function.

    Parameters
    ----------
    arg0 : TypedAstNode
        The argument passed to the function.

    arg1 : TypedAstNode
        Unused inherited argument.
    """

    __slots__ = ()
    _static_type = NumpyComplex128Type()
    name = "complex128"
