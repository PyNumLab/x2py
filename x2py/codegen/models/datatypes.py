# coding: utf-8
# pylint: disable=no-member, protected-access


"""
Classes and methods that handle supported datatypes in C/Fortran.
"""

from functools import cache, lru_cache
from types import GeneratorType
import numpy

from x2py.utilities.metaclasses import Singleton


dict_keys = type({}.keys())
dict_values = type({}.values())


def iterable(value):
    """Return whether a value is a supported model collection."""
    return isinstance(
        value, (list, tuple, dict_keys, dict_values, set, GeneratorType)
    )


_MODEL_CLASSES = set()
_MODEL_STATE = {}


def is_model_object(value):
    """Return whether ``value`` participates in codegen model relationships."""
    return id(value) in _MODEL_STATE or is_model_class(type(value))


def is_model_class(value):
    """Return whether ``value`` is a class for model relationship objects."""
    return isinstance(value, type) and any(c in _MODEL_CLASSES for c in value.__mro__)


def _model_state(obj):
    return _MODEL_STATE.setdefault(
        id(obj), {"parents": [], "scope": None}
    )


def _ignore_model_child(value):
    return (
        value is None
        or isinstance(value, type)
        or getattr(value, "_model_immutable", False)
    )


def init_model_object(obj, scope=None):
    """Initialize relationship bookkeeping for one codegen model object."""
    state = _MODEL_STATE[id(obj)] = {
        "parents": [],
        "scope": scope,
    }

    for attribute_name in getattr(type(obj), "_attribute_nodes", ()):
        child = getattr(obj, attribute_name)
        if _ignore_model_child(child):
            continue

        if isinstance(child, (int, float, complex, str, bool)):
            child = convert_to_literal(child)
            setattr(obj, attribute_name, child)
        elif iterable(child):
            size = len(child)
            child = tuple(
                item
                if not isinstance(item, (int, float, complex, str, bool))
                or _ignore_model_child(item)
                else convert_to_literal(item)
                for item in child
                if not iterable(item)
            )
            if len(child) != size:
                raise TypeError("model child cannot contain nested collections")
            setattr(obj, attribute_name, child)
        elif not is_model_object(child):
            raise TypeError(
                f"model child must be a model object or collection, not {type(child)}"
            )

        children = child if isinstance(child, tuple) else (child,)
        for item in children:
            if not _ignore_model_child(item) and is_model_object(item):
                attach_model_child(obj, item)

    return state


def attach_model_child(parent, child):
    """Record that ``child`` is directly contained by ``parent``."""
    _model_state(child)["parents"].append(parent)


def detach_model_child(parent, child):
    """Remove a direct containment link from ``parent`` to ``child``."""
    _model_state(child)["parents"].remove(parent)


def _find_direct_model_parent(obj, parent_type):
    """Return the first direct parent of ``obj`` with the requested type."""
    return next(
        (
            parent
            for parent in _model_state(obj)["parents"]
            if isinstance(parent, parent_type)
        ),
        None,
    )


def _find_model_parent(obj, parent_type, excluded_types=()):
    """Return the first matching parent reachable from ``obj``."""
    visited = set()

    def find(current):
        current_id = id(current)
        if current_id in visited:
            return None
        visited.add(current_id)

        parents = _model_state(current)["parents"]
        direct_parent = next(
            (
                parent
                for parent in parents
                if isinstance(parent, parent_type)
                and not isinstance(parent, excluded_types)
            ),
            None,
        )
        if direct_parent is not None:
            return direct_parent

        for parent in parents:
            if (
                _ignore_model_child(parent)
                or isinstance(parent, excluded_types)
                or not is_model_object(parent)
            ):
                continue
            result = find(parent)
            if result is not None:
                return result
        return None

    return find(obj)


def _has_model_descendant(obj, descendant_type, excluded_types=()):
    """Return whether ``obj`` contains a descendant with the requested type."""
    visited = set()

    def contains(current):
        current_id = id(current)
        if current_id in visited:
            return False
        visited.add(current_id)

        for attribute_name in getattr(type(current), "_attribute_nodes", ()):
            value = getattr(current, attribute_name)
            values = value if isinstance(value, tuple) else (value,)
            for item in values:
                if isinstance(item, excluded_types):
                    continue
                if isinstance(item, descendant_type):
                    return True
                if (
                    not _ignore_model_child(item)
                    and is_model_object(item)
                    and contains(item)
                ):
                    return True
        return False

    return contains(obj)


def _shape(obj):
    return obj._shape


def _rank(obj):
    return obj.class_type.rank


def _dtype(obj):
    return obj.class_type.datatype


def _order(obj):
    return obj.class_type.order


def _class_type(obj):
    return obj._class_type


def _static_type(cls):
    return cls._static_type


def _scope(obj):
    return _model_state(obj)["scope"]


def register_model_class(cls):
    """Register a codegen model class without changing its inheritance."""
    _MODEL_CLASSES.add(cls)
    if "shape" not in cls.__dict__:
        cls.shape = property(_shape)
    if "rank" not in cls.__dict__:
        cls.rank = property(_rank)
    if "dtype" not in cls.__dict__:
        cls.dtype = property(_dtype)
    if "order" not in cls.__dict__:
        cls.order = property(_order)
    if "class_type" not in cls.__dict__:
        cls.class_type = property(_class_type)
    if "static_type" not in cls.__dict__:
        cls.static_type = classmethod(_static_type)
    if "scope" not in cls.__dict__:
        cls.scope = property(_scope)
    return cls


__all__ = (
    # ------------ Super classes ------------
    "ContainerType",
    "FixedSizeType",
    "PrimitiveType",
    "Type",
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
    "attach_model_child",
    "convert_to_literal",
    "detach_model_child",
    "init_model_object",
    "is_model_class",
    "is_model_object",
    "iterable",
    "register_model_class",
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


class Type(metaclass=Singleton):
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
        Get the name of the x2py type.

        Get the name of the x2py type.
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
        new_type : Type
            The new basic type.

        Returns
        -------
        Type
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
    A class to get Type subclasses describing constant values.

    A class to get Type subclasses describing constant values.
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
        underlying_type : Type
            The type which is characterised as final.
        """
        assert isinstance(underlying_type, Type)
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


class FixedSizeType(Type):
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
        Type
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

        The precision in X2py is equivalent to the `kind` parameter in Fortran.
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


class ContainerType(Type):
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
        element_type : Type
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

        The precision in X2py is equivalent to the `kind` parameter in Fortran.
        """
        return self.element_type.precision

    @property
    def element_type(self):
        """
        The type of elements of the object.

        The Type describing an element of the container.
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
        Type
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
        Type
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

        The Type describing an element of the container.
        """
        return CharType()

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __hash__(self):
        return hash(self.__class__)

# ==============================================================================


class CustomDataType(Type):
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
        python_name,
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

x2py_type_to_original_type = {
    PythonNativeBool(): bool,
    PythonNativeInt(): int,
    PythonNativeFloat(): float,
    PythonNativeComplex(): complex,
}

original_type_to_x2py_type = {v: k for k, v in x2py_type_to_original_type.items()}


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
            return original_type_to_x2py_type[
                numpy.result_type(
                    x2py_type_to_original_type[self](),
                    x2py_type_to_original_type[other](),
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
        test_type = numpy.zeros(1, dtype=x2py_type_to_original_type[self.element_type])
        if isinstance(other, FixedSizeNumericType):
            comparison_type = x2py_type_to_original_type[other]()
        elif isinstance(other, NumpyNDArrayType):
            comparison_type = numpy.zeros(
                1, dtype=x2py_type_to_original_type[other.element_type]
            )
        else:
            return NotImplemented
        result_type = original_type_to_x2py_type[
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
        Type
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
        Type
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
        Type
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

x2py_type_to_original_type.update(numpy_type_to_original_type)
original_type_to_x2py_type.update(
    {v: k for k, v in numpy_type_to_original_type.items()}
)
original_type_to_x2py_type[numpy.bool_] = PythonNativeBool()

#======================================================================
class Literal:
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

    def __init__(self):
        init_model_object(self)

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
        if is_model_object(other):
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


class NilArgument:
    """
    Represents None when passed as an argument to an inline function.

    Represents the Python value None when passed as an argument
    to an inline function. This class is necessary as to avoid
    accidental substitution due to Singletons.
    """

    __slots__ = ()
    _attribute_nodes = ()

    def __init__(self):
        init_model_object(self)

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
    Convert a Python value to a x2py Literal.

    Convert a Python value to a x2py Literal.

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
    from .core import UnarySub  # Imported here to avoid circular import

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
            literal_val = UnarySub(LiteralInteger(-value, dtype))
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


def process_shape(is_scalar, shape):
    """Return ``None`` for scalars and keep the existing shape for arrays."""
    return None if is_scalar else shape


class _DataTypeFunction:
    """Small call-node base for datatype casting helpers."""

    __slots__ = ("_args",)
    _attribute_nodes = ("_args",)
    name = None

    def __init__(self, *args):
        self._args = tuple(args)
        init_model_object(self)

    @property
    def args(self):
        return self._args

    @property
    def is_elemental(self):
        return False

    @property
    def modified_args(self):
        return ()

    @property
    def is_indexable(self):
        return self.is_elemental

#========================================================================================================
class PythonComplexProperty(_DataTypeFunction):
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
    arg : model object
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
    arg : model object
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
    arg : model object
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
class PythonBool(_DataTypeFunction):
    """
    Represents a call to Python's native `bool()` function.

    Represents a call to Python's native `bool()` function which casts an
    argument to a boolean.

    Parameters
    ----------
    arg : model object
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
            from .core import And, IsNot
            return And(IsNot(arg, Nil()), bool_expr)
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
class PythonComplex(_DataTypeFunction):
    """
    Represents a call to Python's native `complex()` function.

    Represents a call to Python's native `complex()` function which casts an
    argument to a complex number.

    Parameters
    ----------
    arg0 : model object
        The first argument passed to the function (either a real or a complex).

    arg1 : model object, default=0
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
        if not is_model_object(arg1):
            arg1 = convert_to_literal(arg1)
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
class PythonFloat(_DataTypeFunction):
    """
    Represents a call to Python's native `float()` function.

    Represents a call to Python's native `float()` function which casts an
    argument to a floating point number.

    Parameters
    ----------
    arg : model object
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
class PythonInt(_DataTypeFunction):
    """
    Represents a call to Python's native `int()` function.

    Represents a call to Python's native `int()` function which casts an
    argument to an integer.

    Parameters
    ----------
    arg : model object
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


class PythonStr(_DataTypeFunction):
    """
    Represents a call to Python's `str` function.

    Represents a call to Python's `str` function which describes a string
    cast.

    Parameters
    ----------
    arg : model object
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


DtypePrecisionToCastFunction = {
    PythonNativeBool(): PythonBool,
    PythonNativeInt(): PythonInt,
    PythonNativeFloat(): PythonFloat,
    PythonNativeComplex(): PythonComplex,
}


#==============================================================================================
dtype_registry = typenames_to_dtypes
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

class NumpyResultType(_DataTypeFunction):
    """
    Class representing a call to the `numpy.result_type` function.

    A class representing a call to the NumPy function `result_type` which returns
    the datatype of an expression. This function can be used to access the `dtype`
    property of a NumPy array.

    Parameters
    ----------
    *arrays_and_dtypes : model object
        Any arrays and dtypes passed to the function (currently only accepts one array
        and no dtypes).
    """

    __slots__ = ("_class_type",)
    _shape = None
    name = "result_type"

    def __init__(self, *arrays_and_dtypes):
        from .core import X2pyFunctionDef
        types = [
            (
                a.cls_name.static_type()
                if isinstance(a, X2pyFunctionDef)
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
    dtype : X2pyFunctionDef, LiteralString, str
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
    from .core import X2pyFunctionDef
    if isinstance(dtype, NumpyResultType):
        dtype = dtype.dtype

    elif isinstance(dtype, X2pyFunctionDef):
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
    arg : model object
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
    arg : model object
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
    arg : model object
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
    arg : model object
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
    arg : model object
        The argument passed to the function.
    base : model object
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
    arg : model object
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
    arg : model object
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
    arg : model object
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
    arg : model object
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
    arg : model object
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
    arg : model object
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
    arg0 : model object
        The first argument passed to the function. Either the array/scalar being cast
        or the real part of the complex.
    arg1 : model object, optional
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
    arg0 : model object
        The argument passed to the function.

    arg1 : model object
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
    arg0 : model object
        The argument passed to the function.

    arg1 : model object
        Unused inherited argument.
    """

    __slots__ = ()
    _static_type = NumpyComplex128Type()
    name = "complex128"


for _model_cls in (Literal, NilArgument, _DataTypeFunction):
    register_model_class(_model_cls)

del _model_cls
