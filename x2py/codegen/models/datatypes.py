# pylint: disable=no-member, protected-access


"""
Classes and methods that handle supported datatypes in C/Fortran.
"""

from functools import lru_cache
from types import GeneratorType
import numpy

from x2py.utilities.metaclasses import Singleton


dict_keys = type({}.keys())
dict_values = type({}.values())


def iterable(value):
    """Return whether a value is a supported model collection."""
    return isinstance(value, list | tuple | dict_keys | dict_values | set | GeneratorType)


_MODEL_CLASSES = set()
_MODEL_STATE = {}


def is_model_object(value):
    """Return whether ``value`` participates in codegen model relationships."""
    return id(value) in _MODEL_STATE or is_model_class(type(value))


def is_model_class(value):
    """Return whether ``value`` is a class for model relationship objects."""
    return isinstance(value, type) and any(c in _MODEL_CLASSES for c in value.__mro__)


def _model_state(obj):
    return _MODEL_STATE.setdefault(id(obj), {"parents": [], "scope": None})


def _ignore_model_child(value):
    return value is None or isinstance(value, type) or getattr(value, "_model_immutable", False)


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

        if isinstance(child, int | float | complex | str | bool):
            child = convert_to_literal(child)
            setattr(obj, attribute_name, child)
        elif iterable(child):
            size = len(child)
            child = tuple(
                item
                if not isinstance(item, int | float | complex | str | bool) or _ignore_model_child(item)
                else convert_to_literal(item)
                for item in child
                if not iterable(item)
            )
            if len(child) != size:
                raise TypeError("model child cannot contain nested collections")
            setattr(obj, attribute_name, child)
        elif not is_model_object(child):
            raise TypeError(f"model child must be a model object or collection, not {type(child)}")

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
        (parent for parent in _model_state(obj)["parents"] if isinstance(parent, parent_type)),
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
                if isinstance(parent, parent_type) and not isinstance(parent, excluded_types)
            ),
            None,
        )
        if direct_parent is not None:
            return direct_parent

        for parent in parents:
            if _ignore_model_child(parent) or isinstance(parent, excluded_types) or not is_model_object(parent):
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
                if not _ignore_model_child(item) and is_model_object(item) and contains(item):
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
    "NIL",
    # ---------- Functions -------------------
    "Cast",
    # ------------ Fixed size types ------------
    "CharType",
    "ComplexPart",
    # ------------ Container types ------------
    "CustomDataType",
    "DataTypeFactory",
    # ------------ Modifying types ------------
    "FinalType",
    "FixedSizeNumericType",
    # ------------ Super classes ------------
    "FixedSizeType",
    "GenericType",
    # -----------------literals-----------------
    "Literal",
    # ---------------numpy types --------------
    "NumpyBoolType",
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
    # ------------ Primitive types ------------
    "PrimitiveBooleanType",
    "PrimitiveCharacterType",
    "PrimitiveComplexType",
    "PrimitiveFloatingPointType",
    "PrimitiveIntegerType",
    "PrimitiveType",
    "StringType",
    "SymbolicType",
    "TupleType",
    "Type",
    "VoidType",
    "attach_model_child",
    "cast_to",
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
        Array types override this method to keep the array container and switch
        the element type.

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
    useful for describing an argument which can accept any type (e.g. MPI arguments).
    """

    __slots__ = ()
    _name = "Generic"
    _primitive_type = None

    @lru_cache  # noqa: B019 - datatype instances are interned and process-lived.
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


class TupleType:
    """
    Base class representing tuple datatypes.

    The class from which tuple datatypes must inherit.
    """

    __slots__ = ()
    _name = "tuple"


# ==============================================================================


class StringType(Type):
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

    def shape_is_compatible(self, shape):
        """Check if the provided shape is compatible with a string."""
        return isinstance(shape, tuple) and len(shape) == self.container_rank

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
                raise TypeError(f"Argument {key} not valid for {self.__class__.__name__}")
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
        return self._name  # pylint: disable=protected-access

    def low_level_name(self):
        """
        The low_level_name function for the new CustomDataType class.
        This describes the name that will be used in the low-level language.
        """
        return ll_name

    return type(
        python_name,
        (BaseClass,),
        {
            "__init__": class_init_func,
            "name": property(class_name_func),
            "_name": python_name,
            "low_level_name": property(low_level_name),
        },
    )


# ========================================================================================
primitive_type_precedence = [
    PrimitiveBooleanType(),
    PrimitiveIntegerType(),
    PrimitiveFloatingPointType(),
    PrimitiveComplexType(),
]

# ==============================================================================


class NumpyNumericType(FixedSizeNumericType):
    """
    Base class representing a scalar numeric datatype defined in the numpy module.

    Base class representing a scalar numeric datatype defined in the numpy module.
    """

    __slots__ = ()

    @lru_cache  # noqa: B019 - datatype instances are interned and process-lived.
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

    @lru_cache  # noqa: B019 - datatype instances are interned and process-lived.
    def __radd__(self, other):
        return self.__add__(other)

    def __eq__(self, other):
        if other is self:
            return True
        if isinstance(other, NumpyNumericType):
            return False
        if isinstance(other, FixedSizeNumericType):
            return other.primitive_type == self.primitive_type and other.precision == self.precision
        return NotImplemented

    def __hash__(self):
        return hash(f"numpy.{self}")


# ==============================================================================


class NumpyBoolType(NumpyNumericType):
    """
    Class representing NumPy's bool_ type.

    Class representing NumPy's bool_ type.
    """

    __slots__ = ()
    _name = "numpy.bool_"
    _primitive_type = PrimitiveBooleanType()
    _precision = -1

    @lru_cache  # noqa: B019 - datatype instances are interned and process-lived.
    def __add__(self, other):
        if isinstance(other, NumpyBoolType):
            return NumpyInt64Type()
        if isinstance(other, NumpyNumericType):
            return other
        return NotImplemented

    @lru_cache  # noqa: B019 - datatype instances are interned and process-lived.
    def __and__(self, other):
        if isinstance(other, NumpyBoolType):
            return self
        if isinstance(other, NumpyNumericType):
            return other
        return NotImplemented

    @lru_cache  # noqa: B019 - datatype instances are interned and process-lived.
    def __rand__(self, other):
        return self.__and__(other)


# ==============================================================================


class NumpyIntType(NumpyNumericType):
    """
    Super class representing NumPy's integer types.

    Super class representing NumPy's integer types.
    """

    __slots__ = ()
    _primitive_type = PrimitiveIntegerType()

    @lru_cache  # noqa: B019 - datatype instances are interned and process-lived.
    def __and__(self, other):
        if isinstance(other, NumpyBoolType):
            return self
        if isinstance(other, FixedSizeNumericType):
            precision = max(self.precision, other.precision)
            return numpy_precision_map[(self._primitive_type, precision)]
        return NotImplemented

    @lru_cache  # noqa: B019 - datatype instances are interned and process-lived.
    def __rand__(self, other):
        if isinstance(other, NumpyBoolType):
            return self
        if isinstance(other, FixedSizeNumericType):
            precision = max(self.precision, other.precision)
            return numpy_precision_map[(self._primitive_type, precision)]
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


class NumpyNDArrayType(Type):
    """
    Class representing the NumPy ND array type.

    Class representing the NumPy ND array type.
    """

    __slots__ = (
        "_allows_strides",
        "_container_rank",
        "_element_type",
        "_order",
        "_raw",
    )
    _name = "numpy.ndarray"

    @classmethod
    @lru_cache
    def get_new(cls, dtype, rank, order, allows_strides=True, *, raw=False):
        """
        Get the parametrised NumPy ND array type.

        Get the parametrised NumPy ND array type.

        Parameters
        ----------
        dtype : NumpyNumericType | GenericType
            The internal datatype of the object (GenericType is allowed for external
            libraries, e.g. MPI).
        rank : int
            The rank of the new NumPy array.
        order : str
            The order of the memory layout for the new NumPy array.
        allows_strides : bool
            Whether non-contiguous strided views are valid for this array contract.
        raw : bool
            Whether the array is represented directly as a C array/pointer instead
            of the generated ndarray wrapper structure.
        """
        assert isinstance(rank, int)
        assert order in (None, "C", "F")
        assert rank < 2 or order is not None
        assert isinstance(allows_strides, bool)
        assert isinstance(raw, bool)
        if raw:
            assert isinstance(dtype, FixedSizeType)
        else:
            assert isinstance(dtype, NumpyNumericType | GenericType | CharType)

        if rank == 0:
            return dtype

        def __init__(self):
            self._element_type = dtype
            self._container_rank = rank
            self._order = order
            self._allows_strides = allows_strides
            self._raw = raw
            super().__init__()

        representation = "Raw" if raw else "Numpy"
        stride_suffix = "strided" if allows_strides else "contiguous"
        name = f"{representation}{rank}DArrayType_{order}_{stride_suffix}_{type(dtype).__name__}"
        return type(name, (NumpyNDArrayType,), {"__init__": __init__})()

    @property
    def datatype(self):
        """The scalar datatype stored in this ndarray."""
        return self.element_type.datatype

    @property
    def primitive_type(self):
        """The datatype category of elements in this ndarray."""
        return self.element_type.primitive_type

    @property
    def precision(self):
        """The precision of elements in this ndarray."""
        return self.element_type.precision

    @property
    def element_type(self):
        """The scalar type of elements in this ndarray."""
        return self._element_type

    @property
    def container_rank(self):
        """Number of indices required to select an ndarray element."""
        return self._container_rank

    def __str__(self):
        name = "raw_array" if self.raw else self._name
        return f"{name}[{self._element_type}]"

    def shape_is_compatible(self, shape):
        """Check if the provided shape is compatible with this ndarray."""
        return isinstance(shape, tuple) and len(shape) == self.container_rank

    @lru_cache  # noqa: B019 - datatype instances are interned and process-lived.
    def __add__(self, other):
        test_type = numpy.zeros(1, dtype=x2py_type_to_original_type[self.element_type])
        if isinstance(other, FixedSizeNumericType):
            comparison_type = x2py_type_to_original_type[other]()
        elif isinstance(other, NumpyNDArrayType):
            comparison_type = numpy.zeros(1, dtype=x2py_type_to_original_type[other.element_type])
        else:
            return NotImplemented
        result_type = original_type_to_x2py_type[numpy.result_type(test_type, comparison_type).type]
        rank = max(other.rank, self.rank)
        if rank < 2:
            order = None
        else:
            other_f_contiguous = other.order in (None, "F")
            self_f_contiguous = self.order in (None, "F")
            order = "F" if other_f_contiguous and self_f_contiguous else "C"
        allows_strides = getattr(self, "allows_strides", True) or getattr(other, "allows_strides", True)
        return NumpyNDArrayType.get_new(result_type, rank, order, allows_strides)

    @lru_cache  # noqa: B019 - datatype instances are interned and process-lived.
    def __radd__(self, other):
        return self.__add__(other)

    @lru_cache  # noqa: B019 - datatype instances are interned and process-lived.
    def __and__(self, other):
        elem_type = self.element_type
        if isinstance(other, FixedSizeNumericType):
            return self.switch_basic_type(elem_type & other)
        if isinstance(other, NumpyNDArrayType):
            return self.switch_basic_type(elem_type & other.element_type)
        return NotImplemented

    @lru_cache  # noqa: B019 - datatype instances are interned and process-lived.
    def __rand__(self, other):
        return self.__and__(other)

    def switch_basic_type(self, new_type):
        """
        Change the basic type to the new type.

        Change the basic type to the new type. A new NumpyNDArrayType will be
        returned whose underlying elements are of the NumPy type which is
        equivalent to the new type.

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
            self._allows_strides,
            raw=self.raw,
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
        new_order = (new_order or self._order) if new_rank > 1 else None
        return NumpyNDArrayType.get_new(
            self.element_type,
            new_rank,
            new_order,
            self._allows_strides,
            raw=self.raw,
        )

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
        return NumpyNDArrayType.get_new(
            self.element_type,
            self._container_rank,
            order,
            self._allows_strides,
            raw=self.raw,
        )

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

    @property
    def allows_strides(self):
        """Whether non-contiguous strided NumPy views are accepted."""
        return self._allows_strides

    @property
    def raw(self):
        """Whether this array uses a direct C array/pointer representation."""
        return self._raw

    def __repr__(self):
        dims = ",".join(":" * self._container_rank)
        order_str = f"(order={self._order})" if self._order else ""
        stride_str = "" if self._allows_strides else "(contiguous)"
        return f"{self.element_type}[{dims}]{order_str}{stride_str}"

    def __hash__(self):
        return hash((self.element_type, self.rank, self.order, self.allows_strides))

    def __eq__(self, other):
        return (
            isinstance(other, NumpyNDArrayType)
            and self.element_type == other.element_type
            and self.rank == other.rank
            and self.order == other.order
            and self.allows_strides == other.allows_strides
        )


# ==============================================================================

numpy_precision_map = {
    (PrimitiveBooleanType(), -1): NumpyBoolType(),
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
    NumpyBoolType(): numpy.bool_,
    NumpyInt8Type(): numpy.int8,
    NumpyInt16Type(): numpy.int16,
    NumpyInt32Type(): numpy.int32,
    NumpyInt64Type(): numpy.int64,
    NumpyFloat32Type(): numpy.float32,
    NumpyFloat64Type(): numpy.float64,
    NumpyComplex64Type(): numpy.complex64,
    NumpyComplex128Type(): numpy.complex128,
}

x2py_type_to_original_type = {
    NumpyBoolType(): numpy.bool_,
    NumpyInt64Type(): numpy.int64,
    NumpyFloat64Type(): numpy.float64,
    NumpyComplex128Type(): numpy.complex128,
}

original_type_to_x2py_type = {
    bool: NumpyBoolType(),
    int: NumpyInt64Type(),
    float: NumpyFloat64Type(),
    complex: NumpyComplex128Type(),
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
original_type_to_x2py_type.update({v: k for k, v in numpy_type_to_original_type.items()})

typenames_to_dtypes = {
    "float": NumpyFloat64Type(),
    "double": NumpyFloat64Type(),
    "complex": NumpyComplex128Type(),
    "int": NumpyInt64Type(),
    "bool": NumpyBoolType(),
    "b1": NumpyBoolType(),
    "void": VoidType(),
    "*": GenericType(),
    "str": StringType(),
}


# ======================================================================
class Literal:
    """A value expressed directly in generated code."""

    __slots__ = ("_class_type", "_shape", "_value")
    _attribute_nodes = ()

    def __init__(self, value, datatype):
        if not isinstance(datatype, Type):
            raise TypeError("datatype must be a codegen Type")

        if isinstance(datatype, StringType):
            if not isinstance(value, str):
                raise TypeError("string literals require a str value")
            self._value = value
            self._shape = (None,)
        elif isinstance(datatype, VoidType):
            if value is not None:
                raise TypeError("void literals require a None value")
            self._value = None
            self._shape = None
        elif isinstance(datatype, FixedSizeNumericType):
            primitive_type = datatype.primitive_type
            if isinstance(primitive_type, PrimitiveBooleanType):
                if not isinstance(value, bool | numpy.bool_):
                    raise TypeError("boolean literals require a bool value")
                self._value = bool(value)
            elif isinstance(primitive_type, PrimitiveIntegerType):
                if not isinstance(value, int | numpy.integer):
                    raise TypeError("integer literals require an integer value")
                self._value = int(value)
            elif isinstance(primitive_type, PrimitiveFloatingPointType):
                if not isinstance(value, int | float | numpy.integer | numpy.floating):
                    raise TypeError("floating-point literals require a real value")
                self._value = float(value)
            elif isinstance(primitive_type, PrimitiveComplexType):
                if not isinstance(value, int | float | complex | numpy.number):
                    raise TypeError("complex literals require a numeric value")
                self._value = complex(value)
            else:
                raise TypeError(f"Unsupported literal datatype {datatype}")
            self._shape = None
        else:
            raise TypeError(f"Unsupported literal datatype {datatype}")

        self._class_type = datatype
        init_model_object(self)

    @property
    def python_value(self):
        """Return the Python value represented by this literal."""
        return self._value

    def __repr__(self):
        return f"Literal({self.python_value!r}, {self.class_type!r})"

    def __str__(self):
        return str(self.python_value)

    def __eq__(self, other):
        if is_model_object(other):
            return (
                isinstance(other, Literal)
                and self.class_type == other.class_type
                and self.python_value == other.python_value
            )
        return self.python_value == other

    def __hash__(self):
        return hash((self.python_value, self.class_type))

    def __index__(self):
        if not isinstance(self.class_type.primitive_type, PrimitiveIntegerType):
            raise TypeError("only integer literals can be used as indices")
        return self.python_value

    def __add__(self, o):
        if isinstance(self.class_type, StringType) and isinstance(o, Literal) and isinstance(o.class_type, StringType):
            return Literal(self.python_value + o.python_value, StringType())
        return NotImplemented

    def __bool__(self):
        return self.python_value is not None


NIL = Literal(None, VoidType())


# ------------------------------------------------------------------------------


def convert_to_literal(value, dtype=None):
    """
    Convert a Python value to a x2py Literal.

    Convert a Python value to a x2py Literal.

    Parameters
    ----------
    value : int/float/complex/bool/str or NumPy scalar
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

    if isinstance(value, Literal):
        if dtype is None or dtype == value.dtype:
            return value
        value = value.python_value

    # Calculate the default datatype
    if dtype is None:
        if isinstance(value, numpy.generic):
            numpy_type = numpy.asarray(value).dtype.type
            try:
                dtype = original_type_to_x2py_type[numpy_type]
            except KeyError as e:
                raise TypeError(f"Unknown type of object {value}") from e
        elif isinstance(value, bool):
            dtype = NumpyBoolType()
        elif isinstance(value, int):
            dtype = NumpyInt64Type()
        elif isinstance(value, float):
            dtype = NumpyFloat64Type()
        elif isinstance(value, complex):
            dtype = NumpyComplex128Type()
        elif isinstance(value, str):
            dtype = StringType()
        else:
            raise TypeError(f"Unknown type of object {value}")

    # Resolve any datatypes which don't inherit from FixedSizeType
    if isinstance(dtype, StringType):
        return Literal(value, dtype)

    assert isinstance(dtype, FixedSizeNumericType)

    primitive_type = dtype.primitive_type
    if isinstance(primitive_type, PrimitiveIntegerType):
        literal_val = Literal(value, dtype) if value >= 0 else UnarySub(Literal(-value, dtype))
    elif isinstance(primitive_type, PrimitiveFloatingPointType | PrimitiveComplexType | PrimitiveBooleanType):
        literal_val = Literal(value, dtype)
    else:
        raise TypeError(f"Unknown type {dtype}")

    return literal_val


def _cast_result_type(arg, target_type):
    """Return the scalar or array datatype produced by a cast."""
    if arg.rank == 0:
        return target_type
    return NumpyNDArrayType.get_new(
        target_type,
        arg.rank,
        arg.order,
        getattr(arg.class_type, "allows_strides", True),
    )


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


class ComplexPart(_DataTypeFunction):
    """Access the real or imaginary component of a complex expression."""

    __slots__ = ("_class_type", "_part", "_shape")

    def __new__(cls, arg, part):
        if part not in ("real", "imag"):
            raise ValueError("part must be 'real' or 'imag'")
        if not isinstance(arg.dtype.primitive_type, PrimitiveComplexType):
            if part == "real":
                if isinstance(arg.dtype, NumpyBoolType):
                    return cast_to(arg, NumpyInt64Type())
                return arg
            if arg.rank > 0:
                raise NotImplementedError("imaginary-part access for non-complex arrays is not supported")
            return convert_to_literal(0, dtype=arg.dtype)
        return super().__new__(cls)

    def __init__(self, arg, part):
        self._part = part
        self._shape = arg.shape
        self._class_type = _cast_result_type(arg, arg.dtype.element_type)
        super().__init__(arg)

    @property
    def arg(self):
        return self._args[0]

    @property
    def part(self):
        return self._part

    def __str__(self):
        return f"ComplexPart({self.arg}, {self.part!r})"


class Cast(_DataTypeFunction):
    """A conversion of one model expression to a target datatype."""

    __slots__ = ("_class_type", "_shape")

    def __init__(self, arg, datatype):
        if not isinstance(datatype, Type):
            raise TypeError("datatype must be a codegen Type")
        if isinstance(datatype, StringType) and not isinstance(arg.class_type, StringType | CharType):
            raise NotImplementedError("Support for casting non-character types to strings is not available")
        self._shape = (None,) if isinstance(datatype, StringType) else arg.shape
        self._class_type = _cast_result_type(arg, datatype)
        super().__init__(arg)

    @property
    def arg(self):
        """Return the expression being converted."""
        return self._args[0]

    @property
    def is_elemental(self):
        return True

    def __str__(self):
        return f"Cast({self.arg}, {self.dtype})"


# ==============================================================================================
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
    dtype : X2pyFunctionDef, Literal, str
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

    if isinstance(dtype, X2pyFunctionDef):
        dtype = dtype.cls_name.static_type()

    elif isinstance(dtype, Literal) and isinstance(dtype.dtype, StringType):
        dtype = dtype.python_value

    if isinstance(dtype, str):
        try:
            dtype = dtype_registry[dtype]
        except KeyError as e:
            raise TypeError(f"Unknown type of {dtype}.") from e

    if isinstance(dtype, NumpyNumericType | GenericType):
        return dtype
    if isinstance(dtype, FixedSizeNumericType):
        return numpy_precision_map[(dtype.primitive_type, dtype.precision)]
    raise TypeError(f"Unknown type of {dtype}.")


def cast_to(arg, target_type):
    """Return ``arg`` cast to ``target_type`` using the codegen cast node."""
    if arg.class_type == target_type:
        return arg
    if isinstance(target_type, NumpyNDArrayType):
        target_type = target_type.element_type

    if isinstance(target_type, NumpyBoolType) and getattr(arg, "is_optional", False):
        from .core import And, IsNot

        return And(IsNot(arg, NIL), Cast(arg, target_type))
    return Cast(arg, target_type)


for _model_cls in (Literal, _DataTypeFunction):
    register_model_class(_model_cls)

del _model_cls
