"""
Module representing concepts that are only applicable to C code (e.g. ObjectAddress).
"""

from ..models.datatypes import (
    CharType,
    FixedSizeNumericType,
    Literal,
    StringType,
    attach_model_child,
    init_model_object,
    is_model_object,
    PrimitiveIntegerType,
    register_model_class,
    convert_to_literal,
)
from ..models.core import Function

__all__ = (
    "CMacro",
    "CNativeInt",
    "CStrStr",
    "CStringExpression",
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


def _is_string_literal(value):
    """Return whether is string literal."""
    return isinstance(value, Literal) and isinstance(value.dtype, StringType)


# ------------------------------------------------------------------------------
class CStringExpression:
    """
    Internal class used to hold a C string that has literals and C macros.

    Parameters
    ----------
    *args : str / Literal / CMacro / CStringExpression
            any number of arguments to be added to the expression
            note: they will get added in the order provided

    Example
    ------
    >>> expr = CStringExpression(
    ...     CMacro("m"),
    ...     CStringExpression(
    ...         convert_to_literal("the macro is: "),
    ...         CMacro("mc")
    ...     ),
    ...     convert_to_literal("."),
    ... )
    """

    __slots__ = ("_expression",)
    _attribute_nodes = ("_expression",)

    def __init__(self, *args):
        """Initialize one ``CStringExpression`` model instance."""
        self._expression = []
        init_model_object(self)
        for arg in args:
            self.append(arg)

    def __repr__(self):
        """Return the developer representation on ``CStringExpression``."""
        return "".join(repr(e) for e in self._expression)

    def __str__(self):
        """Return the generated text representation on ``CStringExpression``."""
        return "".join(str(e) for e in self._expression)

    def __add__(self, o):
        """
        return new CStringExpression that has `o` at the end

        Parameter
        ----------
        o : str / Literal / CMacro / CStringExpression
            the expression to add
        """
        if isinstance(o, str):
            o = convert_to_literal(o)
        if not (_is_string_literal(o) or isinstance(o, CMacro | CStringExpression)):
            raise TypeError(f"unsupported operand type(s) for +: '{self.__class__}' and '{type(o)}'")
        return CStringExpression(*self._expression, o)

    def __radd__(self, o):
        """Implement ``__radd__`` on ``CStringExpression``."""
        if _is_string_literal(o):
            return CStringExpression(o, self)
        return NotImplemented

    def __iadd__(self, o):
        """Implement ``__iadd__`` on ``CStringExpression``."""
        self.append(o)
        return self

    def append(self, o):
        """
        append the argument `o` to the end of the list _expression

        Parameter
        ---------
        o : str / Literal / CMacro / CStringExpression
            the expression to append
        """
        if isinstance(o, str):
            o = convert_to_literal(o)
        if not (_is_string_literal(o) or isinstance(o, CMacro | CStringExpression)):
            raise TypeError(f"unsupported operand type(s) for append: '{self.__class__}' and '{type(o)}'")
        self._expression += (o,)
        attach_model_child(self, o)

    def join(self, lst):
        """
        insert self between each element of the list `lst`

        Parameter
        ---------
        lst : list
            the list to insert self between its elements

        Example
        -------
        >>> a = [
        ...     CMacro("m"),
        ...     CStringExpression(convert_to_literal("the macro is: ")),
        ...     convert_to_literal("."),
        ... ]
        >>> b = CStringExpression("?").join(a)
        ...
        ... # is the same as:
        ...
        >>> b = CStringExpression(
        ...     CMacro("m"),
        ...     CStringExpression("?"),
        ...     CStringExpression(convert_to_literal("the macro is: ")),
                CStringExpression("?"),
        ...     convert_to_literal("."),
        ... )
        """
        result = CStringExpression()
        if not lst:
            return result
        result += lst[0]
        for elm in lst[1:]:
            result += self
            result += elm
        return result

    def get_flat_expression_list(self):
        """
        returns a list of string literals and CMacros after merging consecutive
        string literals
        """
        tmp_res = []
        for e in self.expression:
            if isinstance(e, CStringExpression):
                tmp_res.extend(e.get_flat_expression_list())
            else:
                tmp_res.append(e)
        if not tmp_res:
            return []
        result = [tmp_res[0]]
        for e in tmp_res[1:]:
            if _is_string_literal(e) and _is_string_literal(result[-1]):
                result[-1] += e
            else:
                result.append(e)
        return result

    @property
    def expression(self):
        """The list containing the literal strings and c macros"""
        return self._expression


# ------------------------------------------------------------------------------
class CMacro:
    """Represents a c macro"""

    __slots__ = ("_macro",)
    _attribute_nodes = ()

    def __init__(self, arg):
        """Initialize one ``CMacro`` model instance."""
        init_model_object(self)
        if not isinstance(arg, str):
            raise TypeError("arg must be of type str")
        self._macro = arg

    def __repr__(self):
        """Return the developer representation on ``CMacro``."""
        return str(self._macro)

    def __add__(self, o):
        """Implement ``__add__`` on ``CMacro``."""
        if _is_string_literal(o) or isinstance(o, CStringExpression):
            return CStringExpression(self, o)
        return NotImplemented

    def __radd__(self, o):
        """Implement ``__radd__`` on ``CMacro``."""
        if _is_string_literal(o):
            return CStringExpression(o, self)
        return NotImplemented

    @property
    def macro(self):
        """The string containing macro name"""
        return self._macro


# -------------------------------------------------------------------
#                         String functions
# -------------------------------------------------------------------
class CStrStr(Function):
    """
    A class which extracts a const char* from a literal string.

    A class which extracts a const char* from a literal string. This
    is useful for calling C functions which were not designed for
    STC.

    Parameters
    ----------
    arg : model object | CMacro
        The object which should be passed as a const char*.
    """

    __slots__ = ()
    _class_type = CharType()
    _shape = (None,)

    def __new__(cls, arg):
        """Create one normalized ``CStrStr`` model instance."""
        if isinstance(arg, CMacro):
            return arg
        return super().__new__(cls)

    def __init__(self, arg):
        """Initialize one ``CStrStr`` model instance."""
        super().__init__(arg)


for _model_cls in (ObjectAddress, PointerCast, CStringExpression, CMacro):
    register_model_class(_model_cls)

del _model_cls
