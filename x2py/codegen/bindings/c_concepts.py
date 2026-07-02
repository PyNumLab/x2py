"""
Module representing concepts that are only applicable to C code (e.g. ObjectAddress).
"""

from ..models.datatypes import (
    CharType,
    FixedSizeNumericType,
    init_model_object,
    is_model_object,
    PrimitiveIntegerType,
    register_model_class,
)
from ..models.core import Function

__all__ = (
    "CNativeInt",
    "CStrStr",
    "ObjectAddress",
    "PointerCast",
)

# ------------------------------------------------------------------------------


class CNativeInt(FixedSizeNumericType):
    """
    Class representing C's native integer type.

    Class representing C's native integer type.
    """

    __slots__ = ()
    _name = "int"
    _primitive_type = PrimitiveIntegerType()
    _precision = None


# ------------------------------------------------------------------------------
class ObjectAddress:
    """
    Class representing the address of an object.

    Class representing the address of an object. In most situations it will not be
    necessary to use this object explicitly. E.g. if you assign a pointer to a
    target then the pointer will be printed using `AliasAssign`. However for the
    `_visit_AliasAssign` function to print neatly, this class will be used.

    Parameters
    ----------
    obj : model object
        The object whose address should be printed.

    Examples
    --------
    >>> CCodePrinter._visit(ObjectAddress(Variable(NumpyInt64Type(),'a')))
    '&a'
    >>> CCodePrinter._visit(ObjectAddress(Variable(NumpyInt64Type(),'a', memory_handling='alias')))
    'a'
    """

    __slots__ = ("_class_type", "_obj", "_shape")
    _attribute_nodes = ("_obj",)

    def __init__(self, obj):
        """Initialize one ``ObjectAddress`` model instance."""
        if not is_model_object(obj):
            raise TypeError("object must be a model object")
        self._obj = obj
        self._shape = obj.shape
        self._class_type = obj.class_type
        init_model_object(self)

    @property
    def obj(self):
        """The object whose address is of interest"""
        return self._obj

    @property
    def is_alias(self):
        """
        Indicate that an ObjectAddress uses alias memory handling.

        Indicate that an ObjectAddress uses alias memory handling.
        """
        return True


# ------------------------------------------------------------------------------
class PointerCast:
    """
    A class which represents the casting of one pointer to another.

    A class which represents the casting of one pointer to another in C code.
    This is useful for storing addresses in a void pointer.
    Using this class is not strictly necessary to produce correct C code,
    but avoids compiler warnings about the implicit conversion of pointers.

    Parameters
    ----------
    obj : Variable
        The pointer being cast.
    cast_type : model object
        A model object describing the object resulting from the cast.
    """

    __slots__ = ("_cast_type", "_class_type", "_obj", "_shape")
    _attribute_nodes = ("_obj",)

    def __init__(self, obj, cast_type):
        """Initialize one ``PointerCast`` model instance."""
        if not is_model_object(obj):
            raise TypeError("object must be a model object")
        assert getattr(obj, "is_alias", False)
        self._obj = obj
        self._shape = cast_type.shape
        self._class_type = cast_type.class_type
        self._cast_type = cast_type
        init_model_object(self)

    @property
    def obj(self):
        """
        The object whose address is of interest.

        The object whose address is of interest.
        """
        return self._obj

    @property
    def cast_type(self):
        """
        Get the model object which describes the object resulting from the cast.

        Get the model object which describes the object resulting from the cast.
        """
        return self._cast_type

    @property
    def is_argument(self):
        """
        Indicates whether the variable is an argument.

        Indicates whether the variable is an argument.
        """
        return self._obj.is_argument


class CStrStr(Function):
    """
    A class which extracts a const char* from a literal string.

    A class which extracts a const char* from a literal string. This
    is useful for calling C functions which were not designed for
    STC.

    Parameters
    ----------
    arg : model object
        The object which should be passed as a const char*.
    """

    __slots__ = ()
    _class_type = CharType()
    _shape = (None,)

    def __init__(self, arg):
        """Initialize one ``CStrStr`` model instance."""
        super().__init__(arg)


for _model_cls in (ObjectAddress, PointerCast):
    register_model_class(_model_cls)

del _model_cls
