# coding: utf-8
# pylint: disable=no-member, protected-access

# ------------------------------------------------------------------------- #
# This file is part of Pyccel which is released under MIT License. See the  #
# LICENSE file or go to https://github.com/pyccel/pyccel/blob/devel/LICENSE #
# for full license details.                                                 #
# ------------------------------------------------------------------------- #

"""
Classes and methods that handle supported datatypes in C/Fortran.
"""

from functools import lru_cache

import numpy

from pyccel.utilities.metaclasses import Singleton

from .basic import iterable
from .basic import PyccelAstNode, TypedAstNode

__all__ = (
    # ------------ Super classes ------------
    "ContainerType",
    "FixedSizeType",
    "PrimitiveType",
    "PyccelType",
    # ------------ Primitive types ------------
    "PrimitiveBooleanType",
    "PrimitiveCharacterType",
    "PrimitiveComplexType",
    "PrimitiveFloatingPointType",
    "PrimitiveIntegerType",
    # ------------ Modifying types ------------
    "FinalType",
    # ------------ Fixed size types ------------
    "CharType",
    "FixedSizeNumericType",
    "GenericType",
    "PythonNativeBool",
    "PythonNativeComplex",
    "PythonNativeFloat",
    "PythonNativeInt",
    "PythonNativeNumericType",
    "SymbolicType",
    "TypeAlias",
    "VoidType",
    # ------------ Container types ------------
    "CustomDataType",
    "DictType",
    "HomogeneousContainerType",
    "HomogeneousListType",
    "HomogeneousSetType",
    "StringType",
    "TupleType",
    # ---------- Functions -------------------
    "DataTypeFactory",
    #---------------numpy types --------------
    "NumpyComplex64Type",
    "NumpyComplex128Type",
    "NumpyComplex256Type",
    "NumpyFloat32Type",
    "NumpyFloat64Type",
    "NumpyFloat128Type",
    "NumpyInt8Type",
    "NumpyInt16Type",
    "NumpyInt32Type",
    "NumpyInt64Type",
    "NumpyIntType",
    "NumpyNDArrayType",
    "NumpyNumericType",
    #-----------------literals-----------------
    "Literal",
    "LiteralComplex",
    "LiteralEllipsis",
    "LiteralFalse",
    "LiteralFloat",
    "LiteralImaginaryUnit",
    "LiteralInteger",
    "LiteralString",
    "LiteralTrue",
    "Nil",
    "NilArgument",
    "convert_to_literal",
)


# ==============================================================================
class PrimitiveType(metaclass=Singleton):
    """
    Base class representing types of datatypes.

    The base class representing the category of datatype to which a FixedSizeType
    may belong (e.g. integer, floating point).
    """

    __slots__ = ()
    _name = "__UNDEFINED__"

    def __init__(self):  # pylint: disable=useless-parent-delegation
        # This __init__ function is required so the Singleton can
        # always detect a signature
        super().__init__()

    def __str__(self):
        return self._name


class PrimitiveBooleanType(PrimitiveType):
    """
    Class representing a boolean datatype.

    Class representing a boolean datatype.
    """

    __slots__ = ()
    _name = "boolean"


class PrimitiveIntegerType(PrimitiveType):
    """
    Class representing an integer datatype.

    Class representing an integer datatype.
    """

    __slots__ = ()
    _name = "integer"


class PrimitiveFloatingPointType(PrimitiveType):
    """
    Class representing a floating point datatype.

    Class representing a floating point datatype.
    """

    __slots__ = ()
    _name = "floating point"


class PrimitiveComplexType(PrimitiveType):
    """
    Class representing a complex datatype.

    Class representing a complex datatype.
    """

    __slots__ = ()
    _name = "complex"


class PrimitiveCharacterType(PrimitiveType):
    """
    Class representing a character datatype.

    Class representing a character datatype.
    """

    __slots__ = ()
    _name = "character"


# ==============================================================================


class PyccelType(metaclass=Singleton):
    """
    Base class representing the type of an object.

    Base class representing the type of an object from which all
    types must inherit. A type must contain enough information to
    describe the declaration type in a low-level language.

    Types contain an addition operator. The operator indicates the type that
    is expected when calling an arithmetic operator on objects of these types.

    Where applicable, types also contain an and operator. The operator indicates the type that
    is expected when calling a bitwise comparison operator on objects of these types.

    A type also contains an attribute _name which can be useful to examine
    the type.
    """

    __slots__ = ()

    @property
    def name(self):
        """
        Get the name of the pyccel type.

        Get the name of the pyccel type.
        """
        return self._name

    def __init__(self):  # pylint: disable=useless-parent-delegation
        # This __init__ function is required so the Singleton can
        # always detect a signature
        super().__init__()

    def __str__(self):
        return self._name

    def switch_basic_type(self, new_type):
        """
        Change the basic type to the new type.

        Change the basic type to the new type. In the case of a FixedSizeType the
        switch will replace the type completely, directly returning the new type.
        In the case of a homogeneous container type, a new container type will be
        returned whose underlying elements are of the new type. This method is not
        implemented for inhomogeneous containers.

        Parameters
        ----------
        new_type : PyccelType
            The new basic type.

        Returns
        -------
        PyccelType
            The new type.
        """
        raise NotImplementedError(f"switch_basic_type not implemented for {type(self)}")

    def shape_is_compatible(self, shape):
        """
        Check if the provided shape is compatible with the datatype.

        Check if the provided shape is compatible with the format expected for
        this datatype.

        Parameters
        ----------
        shape : Any
            The proposed shape.

        Returns
        -------
        bool
            True if the shape is acceptable, False otherwise.
        """
        return shape is None


# ==============================================================================
class FinalType:
    """
    A class to get PyccelType subclasses describing constant values.

    A class to get PyccelType subclasses describing constant values.
    """

    __slots__ = ()

    @classmethod
    @lru_cache
    def get_new(cls, underlying_type):
        """
        Get the parameterised Final type.

        Get the parameterised Final type Final[underlying_type].

        Parameters
        ----------
        underlying_type : PyccelType
            The type which is characterised as final.
        """
        assert isinstance(underlying_type, PyccelType)
        if isinstance(underlying_type, FinalType):
            return underlying_type

        type_class = type(underlying_type)

        def __init__(self):
            self._underlying_type = underlying_type
            type(underlying_type).__init__(self)

        def __hash__(self):
            return type_class.__hash__(underlying_type)

        def __eq__(self, other):
            return type_class.__eq__(underlying_type, other)

        def get_underlying_type(self):
            """
            Get the type that is indicated as const.

            Get the type that is indicated as const.
            """
            return self._underlying_type

        return type(
            f"Final[{type_class.__name__}]",
            (
                FinalType,
                type_class,
            ),
            {
                "__init__": __init__,
                "__hash__": __hash__,
                "__eq__": __eq__,
                "underlying_type": property(get_underlying_type),
            },
        )()

    def __str__(self):
        return f"Final[{self._underlying_type}]"


# ==============================================================================


class FixedSizeType(PyccelType):
    """
    Base class representing a built-in scalar datatype.

    The base class representing a built-in scalar datatype which can be
    represented in memory. E.g. int32, int64.
    """

    __slots__ = ()

    @property
    def datatype(self):
        """
        The datatype of the object.

        The datatype of the object.
        """
        return self

    @property
    def primitive_type(self):
        """
        The datatype category of the object.

        The datatype category of the object (e.g. integer, floating point).
        """
        return self._primitive_type

    @property
    def rank(self):
        """
        Number of dimensions of the object.

        Number of dimensions of the object. If the object is a scalar then
        this is equal to 0.
        """
        return 0

    @property
    def order(self):
        """
        The data layout ordering in memory.

        Indicates whether the data is stored in row-major ('C') or column-major
        ('F') format. This is only relevant if rank > 1. When it is not relevant
        this function returns None.
        """
        return None

    def switch_basic_type(self, new_type):
        """
        Change the basic type to the new type.

        Change the basic type to the new type. In the case of a FixedSizeType the
        switch will replace the type completely, directly returning the new type.

        Parameters
        ----------
        new_type : FixedSizeType
            The new basic type.

        Returns
        -------
        PyccelType
            The new type.
        """
        assert isinstance(new_type, FixedSizeType)
        return new_type


class FixedSizeNumericType(FixedSizeType):
    """
    Base class representing a scalar numeric datatype.

    The base class representing a scalar numeric datatype which can be
    represented in memory. E.g. int32, int64.
    """

    __slots__ = ()

    @property
    def precision(self):
        """
        Precision of the datatype of the object.

        The precision of the datatype of the object. This number is related to the
        number of bytes that the datatype takes up in memory. For basic types the
        number is equivalent to the number of bytes in memory (e.g. `float64` has
        precision = 8 as it takes up 8 bytes), however for less simple types the
        connection is less trivial. For example `complex128` has precision = 8 as
        it is comprised of two `float64` objects (which have precision=8).
        It should be noted that this is not the convention chosen by NumPy (in NumPy
        a `complex128` is so named because `16*8=precision*bits_in_a_byte=128`).

        The precision in Pyccel is equivalent to the `kind` parameter in Fortran.
        """
        return self._precision


class PythonNativeNumericType(FixedSizeNumericType):
    """
    Base class representing a built-in scalar numeric datatype.

    Base class representing a built-in scalar numeric datatype.
    """

    __slots__ = ()


class PythonNativeBool(PythonNativeNumericType):
    """
    Class representing Python's native boolean type.

    Class representing Python's native boolean type.
    """

    __slots__ = ()
    _name = "bool"
    _primitive_type = PrimitiveBooleanType()
    _precision = -1

    @lru_cache
    def __add__(self, other):
        if isinstance(other, PythonNativeBool):
            return PythonNativeInt()
        elif isinstance(other, PythonNativeNumericType):
            return other
        else:
            return NotImplemented

    @lru_cache
    def __and__(self, other):
        if isinstance(other, PythonNativeBool):
            return PythonNativeBool()
        elif isinstance(other, PythonNativeNumericType):
            return other
        else:
            return NotImplemented


class PythonNativeInt(PythonNativeNumericType):
    """
    Class representing Python's native integer type.

    Class representing Python's native integer type.
    """

    __slots__ = ()
    _name = "int"
    _primitive_type = PrimitiveIntegerType()
    _precision = numpy.dtype(int).alignment

    @lru_cache
    def __add__(self, other):
        if isinstance(other, PythonNativeBool):
            return self
        elif isinstance(other, PythonNativeNumericType):
            return other
        else:
            return NotImplemented

    @lru_cache
    def __and__(self, other):
        if isinstance(other, PythonNativeNumericType):
            return self
        else:
            return NotImplemented


class PythonNativeFloat(PythonNativeNumericType):
    """
    Class representing Python's native floating point type.

    Class representing Python's native floating point type.
    """

    __slots__ = ()
    _name = "float"
    _primitive_type = PrimitiveFloatingPointType()
    _precision = 8

    @lru_cache
    def __add__(self, other):
        if isinstance(other, PythonNativeComplex):
            return other
        elif isinstance(other, PythonNativeNumericType):
            return self
        else:
            return NotImplemented


class PythonNativeComplex(PythonNativeNumericType):
    """
    Class representing Python's native complex type.

    Class representing Python's native complex type.
    """

    __slots__ = ("_element_type",)
    _name = "complex"
    _primitive_type = PrimitiveComplexType()
    _precision = 8

    @lru_cache
    def __add__(self, other):
        if isinstance(other, PythonNativeNumericType):
            return self
        else:
            return NotImplemented

    @property
    def element_type(self):
        """
        The type of an element of the complex.

        The type of an element of the complex. In other words, the type
        of the floats which comprise the complex type.
        """
        return PythonNativeFloat()


class VoidType(FixedSizeType):
    """
    Class representing a void datatype.

    Class representing a void datatype. This class is especially useful
    in the C-Python wrapper when a `void*` type is needed to collect
    pointers from Fortran.
    """

    __slots__ = ()
    _name = "void"
    _primitive_type = None


class GenericType(FixedSizeType):
    """
    Class representing a generic datatype.

    Class representing a generic datatype. This datatype is
    useful for describing the type of an empty container (list/tuple/etc)
    or an argument which can accept any type (e.g. MPI arguments).
    """

    __slots__ = ()
    _name = "Generic"
    _primitive_type = None

    @lru_cache
    def __add__(self, other):
        return other

    def __eq__(self, other):
        return True

    def __hash__(self):
        return hash(self.__class__)


class SymbolicType(FixedSizeType):
    """
    Class representing the datatype of a placeholder symbol.

    Class representing the datatype of a placeholder symbol. This type should
    be used for objects which will not appear in the generated code but are
    used to identify objects (e.g. Type aliases).
    """

    __slots__ = ()
    _name = "Symbolic"
    _primitive_type = None


class CharType(FixedSizeType):
    """
    Class representing a char type in C/Fortran.

    Class representing a char type in C/Fortran. This datatype is
    useful for describing strings.
    """

    __slots__ = ()
    _name = "char"
    _primitive_type = PrimitiveCharacterType()


# ==============================================================================
class TypeAlias(SymbolicType):
    """
    Class representing the type of a symbolic object describing a type descriptor.

    Class representing the type of a symbolic object describing a type descriptor.
    This type is equivalent to Python's built-in typing.TypeAlias.

    See Also
    --------
    typing.TypeAlias :
        See documentation of `typing.TypeAlias`: https://docs.python.org/3/library/typing.html#typing.TypeAlias .
    """

    __slots__ = ()
    _name = "TypeAlias"


# ==============================================================================


class ContainerType(PyccelType):
    """
    Base class representing a type which contains objects of other types.

    Base class representing a type which contains objects of other types.
    E.g. classes, arrays, etc.
    """

    __slots__ = ()

    def shape_is_compatible(self, shape):
        """
        Check if the provided shape is compatible with the datatype.

        Check if the provided shape is compatible with the format expected for
        this datatype.

        Parameters
        ----------
        shape : Any
            The proposed shape.

        Returns
        -------
        bool
            True if the shape is acceptable, False otherwise.
        """
        return isinstance(shape, tuple) and len(shape) == self.container_rank


# ==============================================================================


class TupleType:
    """
    Base class representing tuple datatypes.

    The class from which tuple datatypes must inherit.
    """

    __slots__ = ()
    _name = "tuple"


# ==============================================================================


class HomogeneousContainerType(ContainerType):
    """
    Base class representing a datatype which contains multiple elements of a given type.

    Base class representing a datatype which contains multiple elements of a given type.
    This is the case for objects such as arrays, lists, etc.
    """

    __slots__ = ()

    @classmethod
    def get_new(cls, element_type):
        """
        Get a new homogeneous container whose elements have the specified type.

        Get a new homogeneous container whose elements have the specified type.

        Parameters
        ----------
        element_type : PyccelType
            The type of the elements of the homogeneous container.
        """
        raise NotImplementedError(
            "Subclasses should implement a get_new method to create the parametrised sub-class."
        )

    @property
    def datatype(self):
        """
        The datatype of the object.

        The datatype of the object.
        """
        return self.element_type.datatype

    @property
    def primitive_type(self):
        """
        The datatype category of elements of the object.

        The datatype category of elements of the object (e.g. integer, floating point).
        """
        return self.element_type.primitive_type

    @property
    def precision(self):
        """
        Precision of the datatype of the object.

        The precision of the datatype of the object. This number is related to the
        number of bytes that the datatype takes up in memory. For basic types the
        number is equivalent to the number of bytes in memory (e.g. `float64` has
        precision = 8 as it takes up 8 bytes), however for less simple types the
        connection is less trivial. For example `complex128` has precision = 8 as
        it is comprised of two `float64` objects (which have precision=8).
        It should be noted that this is not the convention chosen by NumPy (in NumPy
        a `complex128` is so named because `16*8=precision*bits_in_a_byte=128`).

        The precision in Pyccel is equivalent to the `kind` parameter in Fortran.
        """
        return self.element_type.precision

    @property
    def element_type(self):
        """
        The type of elements of the object.

        The PyccelType describing an element of the container.
        """
        return self._element_type

    def __str__(self):
        return f"{self._name}[{self._element_type}]"

    def switch_basic_type(self, new_type):
        """
        Change the basic type to the new type.

        Change the basic type to the new type. In the case of a FixedSizeType the
        switch will replace the type completely, directly returning the new type.
        In the case of a homogeneous container type, a new container type will be
        returned whose underlying elements are of the new type. This method is not
        implemented for inhomogeneous containers.

        Parameters
        ----------
        new_type : FixedSizeType
            The new basic type.

        Returns
        -------
        PyccelType
            The new type.
        """
        assert isinstance(new_type, FixedSizeType)
        cls = type(self)
        return cls.get_new(self.element_type.switch_basic_type(new_type))

    def switch_rank(self, new_rank, new_order=None):
        """
        Get a type which is identical to this type in all aspects except the rank.

        Get a type which is identical to this type in all aspects except the rank.
        The order must be provided if the rank is increased from 1. This is never
        the case for 1D containers.

        Parameters
        ----------
        new_rank : int
            The rank of the new type.

        new_order : str, optional
            The order of the new type. For 1D containers this should not be provided.

        Returns
        -------
        PyccelType
            The new type.
        """
        assert new_order is None
        rank = self.rank
        assert new_rank < rank

        if new_rank == rank:
            return self
        elif rank - new_rank == self.container_rank:
            return self.element_type
        else:
            return self.element_type.switch_rank(new_rank - self.container_rank)

    @property
    def container_rank(self):
        """
        Number of dimensions of the container.

        Number of dimensions of the object described by the container. This is
        equal to the number of values required to index an element of this container.
        """
        return self._container_rank

    @property
    def rank(self):
        """
        Number of dimensions of the object.

        Number of dimensions of the object. If the object is a scalar then
        this is equal to 0.
        """
        return self.container_rank + self.element_type.rank

    @property
    def order(self):
        """
        The data layout ordering in memory.

        Indicates whether the data is stored in row-major ('C') or column-major
        ('F') format. This is only relevant if rank > 1. When it is not relevant
        this function returns None.
        """
        return self._order


class StringType(ContainerType):
    """
    Class representing Python's native string type.

    Class representing Python's native string type.
    """

    __slots__ = ()
    _name = "str"

    @property
    def datatype(self):
        """
        The datatype of the object.

        The datatype of the object.
        """
        return self

    def __str__(self):
        return "str"

    @property
    def primitive_type(self):
        """
        The datatype category of elements of the object.

        The datatype category of elements of the object (e.g. integer, floating point).
        """
        return self

    @property
    def rank(self):
        """
        Number of dimensions of the object.

        Number of dimensions of the object. If the object is a scalar then
        this is equal to 0.
        """
        return 1

    @property
    def container_rank(self):
        """
        Number of dimensions of the container.

        Number of dimensions of the object described by the container. This is
        equal to the number of values required to index an element of this container.
        """
        return 1

    @property
    def order(self):
        """
        The data layout ordering in memory.

        Indicates whether the data is stored in row-major ('C') or column-major
        ('F') format. This is only relevant if rank > 1. When it is not relevant
        this function returns None.
        """
        return None

    @property
    def element_type(self):
        """
        The type of elements of the object.

        The PyccelType describing an element of the container.
        """
        return CharType()

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __hash__(self):
        return hash(self.__class__)

# ==============================================================================


class CustomDataType(PyccelType):
    """
    Class from which user-defined types inherit.

    A general class for custom data types which is used as a
    base class when a user defines their own type using classes.
    """

    __slots__ = ()

    @property
    def datatype(self):
        """
        The datatype of the object.

        The datatype of the object.
        """
        return self

    @property
    def rank(self):
        """
        Number of dimensions of the object.

        Number of dimensions of the object. If the object is a scalar then
        this is equal to 0.
        """
        return 0

    @property
    def order(self):
        """
        The data layout ordering in memory.

        Indicates whether the data is stored in row-major ('C') or column-major
        ('F') format. This is only relevant if rank > 1. When it is not relevant
        this function returns None.
        """
        return None

# ==============================================================================


def DataTypeFactory(ll_name, python_name, argnames=(), *, BaseClass=CustomDataType):
    """
    Create a new data class.

    Create a new data class which sub-classes a DataType. This provides
    a new data type which can be used, for example, for class types.

    Parameters
    ----------
    ll_name : str
        The low-level name of the new class.

    python_name : str
        The original name of the new class matching the name used in Python.

    argnames : iterable[str]
        A list of all the arguments for the new class.
        This can be used to create classes which are parametrised by a type.

    BaseClass : type inheriting from DataType
        The class from which the new type will be sub-classed.

    Returns
    -------
    type
        A new DataType class.
    """

    def class_init_func(self, **kwargs):
        """
        The __init__ function for the new CustomDataType class.
        """
        for key, value in kwargs.items():
            # here, the argnames variable is the one passed to the
            # DataTypeFactory call
            if key not in argnames:
                raise TypeError(
                    f"Argument {key} not valid for {self.__class__.__name__}"
                )
            setattr(self, key, value)

        BaseClass.__init__(self)  # pylint: disable=unnecessary-dunder-call

    assert iterable(argnames)
    assert all(isinstance(a, str) for a in argnames)

    def class_name_func(self):
        """
        The name function for the new CustomDataType class.
        """
        if argnames:
            param = ", ".join(str(getattr(self, a)) for a in argnames)
            return f"{self._name}[{param}]"  # pylint: disable=protected-access
        else:
            return self._name  # pylint: disable=protected-access

    def low_level_name(self):
        """
        The low_level_name function for the new CustomDataType class.
        This describes the name that will be used in the low-level language.
        """
        return ll_name

    newclass = type(
        f"Pyccel{python_name}",
        (BaseClass,),
        {
            "__init__": class_init_func,
            "name": property(class_name_func),
            "_name": python_name,
            "low_level_name": property(low_level_name),
        },
    )

    return newclass


# ==============================================================================

pyccel_type_to_original_type = {
    PythonNativeBool(): bool,
    PythonNativeInt(): int,
    PythonNativeFloat(): float,
    PythonNativeComplex(): complex,
}

original_type_to_pyccel_type = {v: k for k, v in pyccel_type_to_original_type.items()}


#========================================================================================
primitive_type_precedence = [
    PrimitiveBooleanType(),
    PrimitiveIntegerType(),
    PrimitiveFloatingPointType(),
    PrimitiveComplexType(),
]

typenames_to_dtypes = {
    "float": PythonNativeFloat(),
    "double": PythonNativeFloat(),
    "complex": PythonNativeComplex(),
    "int": PythonNativeInt(),
    "bool": PythonNativeBool(),
    "b1": PythonNativeBool(),
    "void": VoidType(),
    "*": GenericType(),
    "str": StringType(),
}
# ==============================================================================


class NumpyNumericType(FixedSizeNumericType):
    """
    Base class representing a scalar numeric datatype defined in the numpy module.

    Base class representing a scalar numeric datatype defined in the numpy module.
    """

    __slots__ = ()

    @lru_cache
    def __add__(self, other):
        try:
            return original_type_to_pyccel_type[
                numpy.result_type(
                    pyccel_type_to_original_type[self](),
                    pyccel_type_to_original_type[other](),
                ).type
            ]
        except KeyError:
            return NotImplemented

    @lru_cache
    def __radd__(self, other):
        return self.__add__(other)

    def __eq__(self, other):
        if other is self:
            return True
        elif isinstance(other, NumpyNumericType):
            return False
        elif isinstance(other, FixedSizeNumericType):
            return (
                other.primitive_type == self.primitive_type
                and other.precision == self.precision
            )
        else:
            return NotImplemented

    def __hash__(self):
        return hash(f"numpy.{self}")


# ==============================================================================


class NumpyIntType(NumpyNumericType):
    """
    Super class representing NumPy's integer types.

    Super class representing NumPy's integer types.
    """

    __slots__ = ()
    _primitive_type = PrimitiveIntegerType()

    @lru_cache
    def __and__(self, other):
        if isinstance(other, PythonNativeBool):
            return self
        elif isinstance(other, FixedSizeNumericType):
            precision = max(self.precision, other.precision)
            return numpy_precision_map[(self._primitive_type, precision)]
        else:
            return NotImplemented

    @lru_cache
    def __rand__(self, other):
        if isinstance(other, PythonNativeBool):
            return self
        elif isinstance(other, FixedSizeNumericType):
            precision = max(self.precision, other.precision)
            return numpy_precision_map[(self._primitive_type, precision)]
        else:
            return NotImplemented


class NumpyInt8Type(NumpyIntType):
    """
    Class representing NumPy's int8 type.

    Class representing NumPy's int8 type.
    """

    __slots__ = ()
    _name = "numpy.int8"
    _precision = 1


class NumpyInt16Type(NumpyIntType):
    """
    Class representing NumPy's int16 type.

    Class representing NumPy's int16 type.
    """

    __slots__ = ()
    _name = "numpy.int16"
    _precision = 2


class NumpyInt32Type(NumpyIntType):
    """
    Class representing NumPy's int32 type.

    Class representing NumPy's int32 type.
    """

    __slots__ = ()
    _name = "numpy.int32"
    _precision = 4


class NumpyInt64Type(NumpyIntType):
    """
    Class representing NumPy's int64 type.

    Class representing NumPy's int64 type.
    """

    __slots__ = ()
    _name = "numpy.int64"
    _precision = 8


# ==============================================================================


class NumpyFloat32Type(NumpyNumericType):
    """
    Class representing NumPy's float32 type.

    Class representing NumPy's float32 type.
    """

    __slots__ = ()
    _name = "numpy.float32"
    _primitive_type = PrimitiveFloatingPointType()
    _precision = 4


class NumpyFloat64Type(NumpyNumericType):
    """
    Class representing NumPy's float64 type.

    Class representing NumPy's float64 type.
    """

    __slots__ = ()
    _name = "numpy.float64"
    _primitive_type = PrimitiveFloatingPointType()
    _precision = 8


class NumpyFloat128Type(NumpyNumericType):
    """
    Class representing NumPy's float128 type.

    Class representing NumPy's float128 type.
    """

    __slots__ = ()
    _name = "numpy.float128"
    _primitive_type = PrimitiveFloatingPointType()
    _precision = 16


# ==============================================================================


class NumpyComplex64Type(NumpyNumericType):
    """
    Class representing NumPy's complex64 type.

    Class representing NumPy's complex64 type.
    """

    __slots__ = ()
    _name = "numpy.complex64"
    _primitive_type = PrimitiveComplexType()
    _precision = 4

    @property
    def element_type(self):
        """
        The type of an element of the complex.

        The type of an element of the complex. In other words, the type
        of the floats which comprise the complex type.
        """
        return NumpyFloat32Type()


class NumpyComplex128Type(NumpyNumericType):
    """
    Class representing NumPy's complex128 type.

    Class representing NumPy's complex128 type.
    """

    __slots__ = ()
    _name = "numpy.complex128"
    _primitive_type = PrimitiveComplexType()
    _precision = 8

    @property
    def element_type(self):
        """
        The type of an element of the complex.

        The type of an element of the complex. In other words, the type
        of the floats which comprise the complex type.
        """
        return NumpyFloat64Type()


class NumpyComplex256Type(NumpyNumericType):
    """
    Class representing NumPy's complex256 type.

    Class representing NumPy's complex256 type.
    """

    __slots__ = ()
    _name = "numpy.complex256"
    _primitive_type = PrimitiveComplexType()
    _precision = 16

    @property
    def element_type(self):
        """
        The type of an element of the complex.

        The type of an element of the complex. In other words, the type
        of the floats which comprise the complex type.
        """
        return NumpyFloat128Type()


# ==============================================================================


class NumpyNDArrayType(HomogeneousContainerType):
    """
    Class representing the NumPy ND array type.

    Class representing the NumPy ND array type.
    """

    __slots__ = ("_element_type", "_container_rank", "_order")
    _name = "numpy.ndarray"

    @classmethod
    @lru_cache
    def get_new(cls, dtype, rank, order):
        """
        Get the parametrised NumPy ND array type.

        Get the parametrised NumPy ND array type.

        Parameters
        ----------
        dtype : NumpyNumericType | PythonNativeBool | GenericType
            The internal datatype of the object (GenericType is allowed for external
            libraries, e.g. MPI).
        rank : int
            The rank of the new NumPy array.
        order : str
            The order of the memory layout for the new NumPy array.
        """
        assert isinstance(rank, int)
        assert order in (None, "C", "F")
        assert rank < 2 or order is not None
        assert isinstance(
            dtype, (NumpyNumericType, PythonNativeBool, GenericType, CharType)
        )

        if rank == 0:
            return dtype

        def __init__(self):
            self._element_type = dtype
            self._container_rank = rank
            self._order = order
            super().__init__()

        name = f"Numpy{rank}DArrayType_{order}_{type(dtype).__name__}"
        return type(name, (NumpyNDArrayType,), {"__init__": __init__})()

    @lru_cache
    def __add__(self, other):
        test_type = numpy.zeros(1, dtype=pyccel_type_to_original_type[self.element_type])
        if isinstance(other, FixedSizeNumericType):
            comparison_type = pyccel_type_to_original_type[other]()
        elif isinstance(other, NumpyNDArrayType):
            comparison_type = numpy.zeros(
                1, dtype=pyccel_type_to_original_type[other.element_type]
            )
        else:
            return NotImplemented
        result_type = original_type_to_pyccel_type[
            numpy.result_type(test_type, comparison_type).type
        ]
        rank = max(other.rank, self.rank)
        if rank < 2:
            order = None
        else:
            other_f_contiguous = other.order in (None, "F")
            self_f_contiguous = self.order in (None, "F")
            order = "F" if other_f_contiguous and self_f_contiguous else "C"
        return NumpyNDArrayType.get_new(result_type, rank, order)

    @lru_cache
    def __radd__(self, other):
        return self.__add__(other)

    @lru_cache
    def __and__(self, other):
        elem_type = self.element_type
        if isinstance(other, FixedSizeNumericType):
            return self.switch_basic_type(elem_type & other)
        elif isinstance(other, NumpyNDArrayType):
            return self.switch_basic_type(elem_type & other.element_type)
        else:
            return NotImplemented

    @lru_cache
    def __rand__(self, other):
        return self.__and__(other)

    def switch_basic_type(self, new_type):
        """
        Change the basic type to the new type.

        Change the basic type to the new type. A new NumpyNDArrayType will be
        returned whose underlying elements are of the NumPy type which is
        equivalent to the new type (e.g. PythonNativeFloat may be replaced by
        numpy.float64).

        Parameters
        ----------
        new_type : FixedSizeNumericType
            The new basic type.

        Returns
        -------
        PyccelType
            The new type.
        """
        assert isinstance(new_type, FixedSizeNumericType)
        new_type = numpy_precision_map[(new_type.primitive_type, new_type.precision)]
        cls = type(self)
        return cls.get_new(
            self.element_type.switch_basic_type(new_type),
            self._container_rank,
            self._order,
        )

    def switch_rank(self, new_rank, new_order=None):
        """
        Get a type which is identical to this type in all aspects except the rank and/or order.

        Get a type which is identical to this type in all aspects except the rank and/or order.
        The order must be provided if the rank is increased from 1. Otherwise it defaults to the
        same order as the current type.

        Parameters
        ----------
        new_rank : int
            The rank of the new type.

        new_order : str, optional
            The order of the new type. This should be provided if the rank is increased from 1.

        Returns
        -------
        PyccelType
            The new type.
        """
        if new_rank == 0:
            return self.element_type
        else:
            new_order = (new_order or self._order) if new_rank > 1 else None
            return NumpyNDArrayType.get_new(self.element_type, new_rank, new_order)

    def swap_order(self):
        """
        Get a type which is identical to this type in all aspects except the order.

        Get a type which is identical to this type in all aspects except the order.
        In the case of a 1D array the final type will be the same as this type. Otherwise
        if the array is C-ordered the final type will be F-ordered, while if the array
        is F-ordered the final type will be C-ordered.

        Returns
        -------
        PyccelType
            The new type.
        """
        order = None if self._order is None else ("C" if self._order == "F" else "F")
        return NumpyNDArrayType.get_new(self.element_type, self._container_rank, order)

    @property
    def rank(self):
        """
        Number of dimensions of the object.

        Number of dimensions of the object. If the object is a scalar then
        this is equal to 0.
        """
        return self._container_rank

    @property
    def order(self):
        """
        The data layout ordering in memory.

        Indicates whether the data is stored in row-major ('C') or column-major
        ('F') format. This is only relevant if rank > 1. When it is not relevant
        this function returns None.
        """
        return self._order

    def __repr__(self):
        dims = ",".join(":" * self._container_rank)
        order_str = f"(order={self._order})" if self._order else ""
        return f"{self.element_type}[{dims}]{order_str}"

    def __hash__(self):
        return hash((self.element_type, self.rank, self.order))

    def __eq__(self, other):
        return (
            isinstance(other, NumpyNDArrayType)
            and self.element_type == other.element_type
            and self.rank == other.rank
            and self.order == other.order
        )


# ==============================================================================

numpy_precision_map = {
    (PrimitiveBooleanType(), -1): PythonNativeBool(),
    (PrimitiveIntegerType(), 1): NumpyInt8Type(),
    (PrimitiveIntegerType(), 2): NumpyInt16Type(),
    (PrimitiveIntegerType(), 4): NumpyInt32Type(),
    (PrimitiveIntegerType(), 8): NumpyInt64Type(),
    (PrimitiveFloatingPointType(), 4): NumpyFloat32Type(),
    (PrimitiveFloatingPointType(), 8): NumpyFloat64Type(),
    (PrimitiveFloatingPointType(), 16): NumpyFloat128Type(),
    (PrimitiveComplexType(), 4): NumpyComplex64Type(),
    (PrimitiveComplexType(), 8): NumpyComplex128Type(),
    (PrimitiveComplexType(), 16): NumpyComplex256Type(),
}

numpy_type_to_original_type = {
    NumpyInt8Type(): numpy.int8,
    NumpyInt16Type(): numpy.int16,
    NumpyInt32Type(): numpy.int32,
    NumpyInt64Type(): numpy.int64,
    NumpyFloat32Type(): numpy.float32,
    NumpyFloat64Type(): numpy.float64,
    NumpyComplex64Type(): numpy.complex64,
    NumpyComplex128Type(): numpy.complex128,
}

# Large types don't exist on all systems
if hasattr(numpy, "float128"):
    numpy_type_to_original_type.update(
        {
            NumpyFloat128Type(): numpy.float128,
            NumpyComplex256Type(): numpy.complex256,
        }
    )

pyccel_type_to_original_type.update(numpy_type_to_original_type)
original_type_to_pyccel_type.update(
    {v: k for k, v in numpy_type_to_original_type.items()}
)
original_type_to_pyccel_type[numpy.bool_] = PythonNativeBool()

NumpyInt = NumpyInt64Type()

#======================================================================
class Literal(TypedAstNode):
    """
    Class representing a literal value.

    Class representing a literal value. A literal is a value that is expressed
    as itself rather than as a variable or an expression, e.g. the number 3
    or the string "Hello".

    This class is abstract and should be implemented for each dtype
    """

    __slots__ = ()
    _attribute_nodes = ()
    _shape = None

    @property
    def python_value(self):
        """
        Get the Python literal represented by this instance.

        Get the Python literal represented by this instance.
        """

    def __repr__(self):
        return f"Literal({repr(self.python_value)})"

    def __str__(self):
        return str(self.python_value)

    def __eq__(self, other):
        if isinstance(other, TypedAstNode):
            return (
                isinstance(other, type(self))
                and self.python_value == other.python_value
            )
        else:
            return self.python_value == other

    def __hash__(self):
        return hash(self.python_value)


# ------------------------------------------------------------------------------
class LiteralTrue(Literal):
    """
    Class representing the Python value True.

    Class representing the Python value True.

    Parameters
    ----------
    dtype : FixedSizeType
        The exact type of the literal.
    """

    __slots__ = ("_class_type",)

    def __init__(self, dtype=PythonNativeBool()):
        self._class_type = dtype
        super().__init__()

    @property
    def python_value(self):
        """
        Get the Python literal represented by this instance.

        Get the Python literal represented by this instance.
        """
        return True


# ------------------------------------------------------------------------------
class LiteralFalse(Literal):
    """
    Class representing the Python value False.

    Class representing the Python value False.

    Parameters
    ----------
    dtype : FixedSizeType
        The exact type of the literal.
    """

    __slots__ = ("_class_type",)

    def __init__(self, dtype=PythonNativeBool()):
        self._class_type = dtype
        super().__init__()

    @property
    def python_value(self):
        """
        Get the Python literal represented by this instance.

        Get the Python literal represented by this instance.
        """
        return False


# ------------------------------------------------------------------------------
class LiteralInteger(Literal):
    """
    Class representing an integer literal in Python.

    Class representing an integer literal, such as 3, in Python.

    Parameters
    ----------
    value : int
        The Python literal.

    dtype : FixedSizeType
        The exact type of the literal.
    """

    __slots__ = ("_value", "_class_type")

    def __init__(self, value, dtype=PythonNativeInt()):
        if not isinstance(value, (int, numpy.integer)):
            raise TypeError("A LiteralInteger can only be created with an integer")
        self._value = int(value)
        self._class_type = dtype
        super().__init__()

    @property
    def python_value(self):
        """
        Get the Python literal represented by this instance.

        Get the Python literal represented by this instance.
        """
        return self._value

    def __index__(self):
        return self.python_value


# ------------------------------------------------------------------------------
class LiteralFloat(Literal):
    """
    Class representing a float literal in Python.

    Class representing a float literal, such as 3.5, in Python.

    Parameters
    ----------
    value : float
        The Python literal.

    dtype : FixedSizeType
        The exact type of the literal.
    """

    __slots__ = ("_value", "_class_type")

    def __init__(self, value, dtype=PythonNativeFloat()):
        if not isinstance(value, (int, float, LiteralFloat, numpy.integer, numpy.floating)):
            raise TypeError(
                "A LiteralFloat can only be created with an integer or a float"
            )
        if isinstance(value, LiteralFloat):
            self._value = value.python_value
        else:
            self._value = float(value)
        self._class_type = dtype
        super().__init__()

    @property
    def python_value(self):
        """
        Get the Python literal represented by this instance.

        Get the Python literal represented by this instance.
        """
        return self._value


# ------------------------------------------------------------------------------
class LiteralComplex(Literal):
    """
    Class representing a complex literal in Python.

    Class representing a complex literal, such as 3+2j, in Python.

    Parameters
    ----------
    real : float
        The real part of the Python literal.

    imag : float
        The imaginary part of the Python literal.

    dtype : FixedSizeType
        The exact type of the literal.
    """

    __slots__ = ("_real_part", "_imag_part", "_class_type")

    def __new__(cls, real, imag, dtype=PythonNativeComplex()):
        if cls is LiteralImaginaryUnit:
            return super().__new__(cls)
        real_part = cls._collect_python_val(real)
        imag_part = cls._collect_python_val(imag)
        if real_part == 0 and imag_part == 1:
            return LiteralImaginaryUnit()
        else:
            return super().__new__(cls)

    def __init__(self, real, imag, dtype=PythonNativeComplex()):
        self._real_part = LiteralFloat(
            self._collect_python_val(real), dtype=dtype.element_type
        )
        self._imag_part = LiteralFloat(
            self._collect_python_val(imag), dtype=dtype.element_type
        )
        self._class_type = dtype
        super().__init__()

    @staticmethod
    def _collect_python_val(arg):
        """
        Extract the Python value from the input argument.

        Extract the Python value from the input argument which can either
        be a literal or a Python variable. The input argument represents
        either the real or the imaginary part of the complex literal.

        Parameters
        ----------
        arg : Literal | int | float
            The Python value.

        Returns
        -------
        float
            The Python value of the argument.
        """
        if isinstance(arg, Literal):
            return float(arg.python_value)
        elif isinstance(arg, (int, float, numpy.integer, numpy.floating)):
            return float(arg)
        else:
            raise TypeError(
                f"LiteralComplex argument must be an int/float/LiteralInt/LiteralFloat not a {type(arg)}"
            )

    @property
    def real(self):
        """
        Return the real part of the complex literal.

        Return the real part of the complex literal.
        """
        return self._real_part

    @property
    def imag(self):
        """
        Return the imaginary part of the complex literal.

        Return the imaginary part of the complex literal.
        """
        return self._imag_part

    @property
    def python_value(self):
        """
        Get the Python literal represented by this instance.

        Get the Python literal represented by this instance.
        """
        return self.real.python_value + self.imag.python_value * 1j


# ------------------------------------------------------------------------------
class LiteralImaginaryUnit(LiteralComplex):
    """
    Class representing the Python value j.

    Class representing the imaginary unit j in Python.

    Parameters
    ----------
    real : float = 0
        The value of the real part. This argument is necessary to handle the
        inheritance but should not be provided explicitly.
    imag : float = 0
        The value of the real part. This argument is necessary to handle the
        inheritance but should not be provided explicitly.
    dtype : FixedSizeType
        The exact type of the literal.
    """

    __slots__ = ()

    def __new__(cls, real=0, imag=1, dtype=PythonNativeComplex()):
        return super().__new__(cls, 0, 1, dtype=dtype)

    def __init__(self, real=0, imag=1, dtype=PythonNativeComplex()):
        super().__init__(0, 1, dtype)

    @property
    def python_value(self):
        """
        Get the Python literal represented by this instance.

        Get the Python literal represented by this instance.
        """
        return 1j


# ------------------------------------------------------------------------------
class LiteralString(Literal):
    """
    Class representing a string literal in Python.

    Class representing a string literal, such as 'hello' in Python.

    Parameters
    ----------
    arg : str
        The Python literal.
    """

    __slots__ = ("_string",)
    _class_type = StringType()
    _shape = (None,)

    def __init__(self, arg):
        super().__init__()
        if not isinstance(arg, str):
            raise TypeError("arg must be of type str")
        self._string = arg

    def __repr__(self):
        return f"'{self.python_value}'"

    def __str__(self):
        return str(self.python_value)

    def __add__(self, o):
        if isinstance(o, LiteralString):
            return LiteralString(self._string + o._string)
        return NotImplemented

    @property
    def python_value(self):
        """
        Get the Python literal represented by this instance.

        Get the Python literal represented by this instance.
        """
        return self._string


# ------------------------------------------------------------------------------


class Nil(Literal, metaclass=Singleton):
    """
    Class representing a None object in the code.

    Class representing the Python value None in the code.
    """

    __slots__ = ()
    _attribute_nodes = ()
    _class_type = VoidType()

    def __str__(self):
        return "None"

    def __bool__(self):
        return False

    def __eq__(self, other):
        return isinstance(other, Nil)

    def __hash__(self):
        return hash("Nil") + hash(None)


# ------------------------------------------------------------------------------


class NilArgument(PyccelAstNode):
    """
    Represents None when passed as an argument to an inline function.

    Represents the Python value None when passed as an argument
    to an inline function. This class is necessary as to avoid
    accidental substitution due to Singletons.
    """

    __slots__ = ()
    _attribute_nodes = ()

    def __str__(self):
        return "Argument(None)"

    def __bool__(self):
        return False


# ------------------------------------------------------------------------------


class LiteralEllipsis(Literal, metaclass=Singleton):
    """
    Class representing an Ellipsis object in the code.

    Class representing the Python value Ellipsis in the code.
    """

    __slots__ = ()

    def __str__(self):
        return "..."

    @property
    def python_value(self):
        """
        Get the Python literal represented by this instance.

        Get the Python literal represented by this instance.
        """
        return ...


# ------------------------------------------------------------------------------


def convert_to_literal(value, dtype=None):
    """
    Convert a Python value to a pyccel Literal.

    Convert a Python value to a pyccel Literal.

    Parameters
    ----------
    value : int/float/complex/bool/str
        The Python value.
    dtype : DataType
        The datatype of the Python value.
        Default : Matches type of 'value'.

    Returns
    -------
    Literal
        The Python value 'value' expressed as a literal
        with the specified dtype.
    """
    from .operators import PyccelUnarySub  # Imported here to avoid circular import

    # Calculate the default datatype
    if dtype is None:
        if isinstance(value, bool):
            dtype = PythonNativeBool()
        elif isinstance(value, int):
            dtype = PythonNativeInt()
        elif isinstance(value, float):
            dtype = PythonNativeFloat()
        elif isinstance(value, complex):
            dtype = PythonNativeComplex()
        elif isinstance(value, str):
            dtype = StringType()
        else:
            raise TypeError(f"Unknown type of object {value}")

    # Resolve any datatypes which don't inherit from FixedSizeType
    if isinstance(dtype, StringType):
        return LiteralString(value)

    assert isinstance(dtype, FixedSizeNumericType)

    primitive_type = dtype.primitive_type
    if isinstance(primitive_type, PrimitiveIntegerType):
        if value >= 0:
            literal_val = LiteralInteger(value, dtype)
        else:
            literal_val = PyccelUnarySub(LiteralInteger(-value, dtype))
    elif isinstance(primitive_type, PrimitiveFloatingPointType):
        literal_val = LiteralFloat(value, dtype)
    elif isinstance(primitive_type, PrimitiveComplexType):
        literal_val = LiteralComplex(value.real, value.imag, dtype)
    elif isinstance(primitive_type, PrimitiveBooleanType):
        if value:
            literal_val = LiteralTrue(dtype)
        else:
            literal_val = LiteralFalse(dtype)
    else:
        raise TypeError(f"Unknown type {dtype}")

    return literal_val
