"""
Module representing concepts that are only applicable to C code (e.g. ObjectAddress).
"""

from functools import cache

from ..models.datatypes import (
    CharType,
    convert_to_literal,
    FixedSizeType,
    FixedSizeNumericType,
    init_model_object,
    is_model_object,
    PrimitiveIntegerType,
    register_model_class,
    Type,
)
from ..models.core import Function

__all__ = (
    "CFIDescriptorAllocate",
    "CFIDescriptorDeallocate",
    "CFIDescriptorDimField",
    "CFIDescriptorEstablish",
    "CFIDescriptorField",
    "CFIDescriptorStorageSize",
    "CFIDescriptorStorageType",
    "CFIDescriptorType",
    "CFIDimensionType",
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
class CFIDescriptorType(FixedSizeType):
    """TS 29113 ``CFI_cdesc_t`` descriptor record."""

    __slots__ = ()
    _name = "CFI_cdesc_t"


class CFIDescriptorStorageType(Type):
    """Rank-specific storage emitted with the standard ``CFI_CDESC_T`` macro."""

    __slots__ = ("_rank",)
    _name = "CFI_CDESC_T"

    @classmethod
    def get_new(cls, rank):
        """Return cached descriptor storage for one non-negative rank."""
        rank = int(rank)
        if rank < 0:
            raise ValueError("CFI descriptor storage rank must be non-negative")
        return cls._get_new(rank)

    @classmethod
    @cache
    def _get_new(cls, rank):
        def __init__(self):
            self._rank = rank
            Type.__init__(self)

        return type(f"CFIDescriptorStorage{rank}DType", (CFIDescriptorStorageType,), {"__init__": __init__})()

    @property
    def rank(self):
        """Descriptor storage is a scalar C object."""
        return 0

    @property
    def descriptor_rank(self):
        """Descriptor rank reserved by this storage type."""
        return self._rank

    @property
    def container_rank(self):
        """Descriptor storage is a scalar C object."""
        return 0

    @property
    def order(self):
        """Descriptor storage has no array order."""
        return None

    @property
    def datatype(self):
        """Descriptor storage is its own datatype."""
        return self


class CFIDimensionType(FixedSizeType):
    """TS 29113 ``CFI_dim_t`` dimension record."""

    __slots__ = ()
    _name = "CFI_dim_t"


class CFIDescriptorField:
    """Typed field access on a ``CFI_cdesc_t*`` descriptor pointer."""

    __slots__ = ("_class_type", "_field", "_owner", "_shape")
    _attribute_nodes = ("_owner",)

    def __init__(self, owner, field, dtype):
        """Initialize one descriptor field expression."""
        if not is_model_object(owner):
            raise TypeError("owner must be a model object")
        if not isinstance(field, str) or not field:
            raise TypeError("field must be a non-empty string")
        if not isinstance(dtype, Type):
            raise TypeError("dtype must be a codegen Type")
        self._owner = owner
        self._field = field
        self._class_type = dtype
        self._shape = None
        init_model_object(self)

    @property
    def owner(self):
        """Descriptor pointer whose field is read."""
        return self._owner

    @property
    def field(self):
        """Descriptor field name."""
        return self._field


class CFIDescriptorDimField:
    """Typed field access on ``CFI_cdesc_t.dim[index]``."""

    __slots__ = ("_class_type", "_field", "_index", "_owner", "_shape")
    _attribute_nodes = ("_owner", "_index")

    def __init__(self, owner, index, field, dtype):
        """Initialize one descriptor dimension field expression."""
        if not is_model_object(owner):
            raise TypeError("owner must be a model object")
        if isinstance(index, int):
            index = convert_to_literal(index)
        if not is_model_object(index):
            raise TypeError("index must be an integer or model object")
        if not isinstance(field, str) or not field:
            raise TypeError("field must be a non-empty string")
        if not isinstance(dtype, Type):
            raise TypeError("dtype must be a codegen Type")
        self._owner = owner
        self._index = index
        self._field = field
        self._class_type = dtype
        self._shape = None
        init_model_object(self)

    @property
    def owner(self):
        """Descriptor pointer whose dimension field is read."""
        return self._owner

    @property
    def index(self):
        """Zero-based descriptor dimension index."""
        return self._index

    @property
    def field(self):
        """Descriptor dimension field name."""
        return self._field


class CFIDescriptorEstablish:
    """Standard ``CFI_establish`` call for an initially disassociated pointer."""

    __slots__ = (
        "_attribute",
        "_base_address",
        "_class_type",
        "_descriptor",
        "_element_length",
        "_element_type",
        "_extents",
        "_rank",
        "_shape",
    )
    _attribute_nodes = ("_base_address", "_descriptor", "_element_length", "_extents")

    def __init__(
        self,
        descriptor,
        element_type,
        rank,
        *,
        base_address=None,
        attribute="pointer",
        element_length=None,
        extents=(),
    ):
        if not is_model_object(descriptor):
            raise TypeError("descriptor must be a model object")
        if not isinstance(element_type, Type):
            raise TypeError("element_type must be a codegen Type")
        rank = int(rank)
        if rank < 0:
            raise ValueError("CFI descriptor rank must be non-negative")
        if attribute not in {"allocatable", "other", "pointer"}:
            raise ValueError("CFI descriptor attribute must be allocatable, other, or pointer")
        extents = tuple(extents)
        if extents and len(extents) != rank:
            raise ValueError("CFI descriptor extents must match the declared rank")
        self._descriptor = descriptor
        self._element_type = element_type
        self._rank = rank
        self._base_address = base_address
        self._attribute = attribute
        self._element_length = element_length
        self._extents = extents
        self._class_type = CNativeInt()
        self._shape = None
        init_model_object(self)

    @property
    def descriptor(self):
        """Pointer to the descriptor record being established."""
        return self._descriptor

    @property
    def element_type(self):
        """Declared array element type."""
        return self._element_type

    @property
    def rank(self):
        """Declared descriptor rank."""
        return self._rank

    @property
    def base_address(self):
        """Optional native data address used to establish the descriptor."""
        return self._base_address

    @property
    def attribute(self):
        """Standard CFI descriptor attribute spelling."""
        return self._attribute

    @property
    def element_length(self):
        """Optional runtime element length expression."""
        return self._element_length

    @property
    def extents(self):
        """Runtime extent expressions used for an associated descriptor."""
        return self._extents


class CFIDescriptorAllocate:
    """Standard ``CFI_allocate`` call for persistent allocatable storage."""

    __slots__ = ("_class_type", "_descriptor", "_element_length", "_lower_bounds", "_shape", "_upper_bounds")
    _attribute_nodes = ("_descriptor", "_element_length", "_lower_bounds", "_upper_bounds")

    def __init__(self, descriptor, lower_bounds, upper_bounds, element_length):
        lower_bounds = tuple(lower_bounds)
        upper_bounds = tuple(upper_bounds)
        if not is_model_object(descriptor):
            raise TypeError("descriptor must be a model object")
        if len(lower_bounds) != len(upper_bounds):
            raise ValueError("CFI allocation lower and upper bounds must have equal rank")
        if not all(is_model_object(bound) for bound in (*lower_bounds, *upper_bounds)):
            raise TypeError("CFI allocation bounds must be model objects")
        if not is_model_object(element_length):
            raise TypeError("CFI allocation element length must be a model object")
        self._descriptor = descriptor
        self._lower_bounds = lower_bounds
        self._upper_bounds = upper_bounds
        self._element_length = element_length
        self._class_type = CNativeInt()
        self._shape = None
        init_model_object(self)

    @property
    def descriptor(self):
        return self._descriptor

    @property
    def lower_bounds(self):
        return self._lower_bounds

    @property
    def upper_bounds(self):
        return self._upper_bounds

    @property
    def element_length(self):
        return self._element_length


class CFIDescriptorDeallocate:
    """Standard ``CFI_deallocate`` call for persistent allocatable storage."""

    __slots__ = ("_class_type", "_descriptor", "_shape")
    _attribute_nodes = ("_descriptor",)

    def __init__(self, descriptor):
        if not is_model_object(descriptor):
            raise TypeError("descriptor must be a model object")
        self._descriptor = descriptor
        self._class_type = CNativeInt()
        self._shape = None
        init_model_object(self)

    @property
    def descriptor(self):
        return self._descriptor


class CFIDescriptorStorageSize:
    """Size in bytes of rank-specific ``CFI_CDESC_T`` storage."""

    __slots__ = ("_class_type", "_rank", "_shape")
    _attribute_nodes = ()

    def __init__(self, rank):
        rank = int(rank)
        if rank < 0:
            raise ValueError("CFI descriptor storage rank must be non-negative")
        self._rank = rank
        self._class_type = CNativeInt()
        self._shape = None
        init_model_object(self)

    @property
    def rank(self):
        return self._rank


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


for _model_cls in (
    CFIDescriptorAllocate,
    CFIDescriptorDeallocate,
    CFIDescriptorField,
    CFIDescriptorDimField,
    CFIDescriptorEstablish,
    CFIDescriptorStorageSize,
    ObjectAddress,
    PointerCast,
):
    register_model_class(_model_cls)

del _model_cls
