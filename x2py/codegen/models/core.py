"""
Module containing the core X2py AST nodes which are used in the syntactic
and semantic stages of X2py, and are relevant to all target languages. These
include model objects representing variable assignment, code blocks, and memory
allocation. Relationship bookkeeping lives in standalone helper functions,
without a shared model base class.
"""

import inspect

from itertools import chain
from typing import ClassVar

from .datatypes import (
    CustomDataType,
    FinalType,
    Type,
    NumpyBoolType,
    NumpyInt32Type,
    TupleType,
    PrimitiveIntegerType,
    NumpyInt64Type,
    StringType,
    _find_direct_model_parent,
    _find_model_parent,
    attach_model_child,
    detach_model_child,
    init_model_object,
    is_model_class,
    is_model_object,
    register_model_class,
    iterable,
)
from .datatypes import (
    Literal,
    NIL,
    NumpyNDArrayType,
    convert_to_literal,
)
from .datatypes import GenericType

__all__ = (
    "Add",
    "AliasAssign",
    "Allocate",
    "And",
    "ArithmeticOperator",
    "ArrayAllocated",
    "ArrayAssociated",
    "ArrayContiguous",
    "ArrayLowerBound",
    "ArrayShapeElement",
    "ArraySize",
    "AsName",
    "Assign",
    "AugAssign",
    "BinaryBooleanOperator",
    "BinaryOperator",
    "BooleanOperator",
    "CaseSection",
    "ClassDef",
    "CodeBlock",
    "Comment",
    "CommentBlock",
    "ComparisonOperator",
    "Deallocate",
    "Declare",
    "Div",
    "DottedVariable",
    "EmptyNode",
    "Eq",
    "FortranCharacterLength",
    "Function",
    "FunctionAddress",
    "FunctionCall",
    "FunctionCallArgument",
    "FunctionDef",
    "FunctionDefArgument",
    "FunctionDefResult",
    "FunctionOverloadSet",
    "Ge",
    "Gt",
    "If",
    "IfSection",
    "IfTernaryOperator",
    "Import",
    "In",
    "IndexedElement",
    "Is",
    "IsNot",
    "Le",
    "Lt",
    "Minus",
    "Module",
    "ModuleHeader",
    "Mul",
    "Ne",
    "Not",
    "Nullify",
    "Operator",
    "Or",
    "Pass",
    "PythonTuple",
    "Return",
    "SelectCase",
    "SeparatorComment",
    "Slice",
    "Symbol",
    "UnaryBooleanOperator",
    "UnaryOperator",
    "UnarySub",
    "Variable",
    "get_direct_assignment",
    "get_direct_function_argument",
    "get_direct_module",
    "get_direct_overload_set",
    "get_enclosing_class",
    "get_enclosing_function",
    "get_enclosing_module",
    "is_in_overload_set",
)


def make_operator_class(name, base, op):
    return type(
        name,
        (base,),
        {
            "__slots__": (),
            "__module__": __name__,
            "op": op,
        },
    )


# ==============================================================================
class Operator:
    __slots__ = ("_args", "_class_type", "_shape")
    _attribute_nodes = ("_args",)
    op = None
    _DEFAULT = object()

    def __init__(self, *args, shape=_DEFAULT, class_type=_DEFAULT):
        self._args = tuple(args)

        self._shape = args[0]._shape if shape is self._DEFAULT else shape
        self._class_type = args[0]._class_type if class_type is self._DEFAULT else class_type

        init_model_object(self)

    @property
    def args(self):
        return self._args

    def __str__(self):
        return repr(self)


class UnaryOperator(Operator):
    __slots__ = ()

    def __repr__(self):
        return f"{self.op}{self.args[0]!r}"


class BinaryOperator(Operator):
    __slots__ = ()

    def __repr__(self):
        return f"{self.args[0]!r} {self.op} {self.args[1]!r}"


class BooleanOperator(Operator):
    __slots__ = ()

    def __init__(self, *args):
        super().__init__(*args, shape=None, class_type=NumpyBoolType())

    def __repr__(self):
        return f" {self.op} ".join(repr(a) for a in self.args)


class UnaryBooleanOperator(BooleanOperator, UnaryOperator):
    __slots__ = ()

    def __init__(self, arg):
        super().__init__(arg)

    def __repr__(self):
        return UnaryOperator.__repr__(self)


class BinaryBooleanOperator(BooleanOperator, BinaryOperator):
    __slots__ = ()

    def __init__(self, arg1, arg2):
        super().__init__(arg1, arg2)


class ArithmeticOperator(BinaryOperator):
    __slots__ = ()


class ComparisonOperator(BinaryBooleanOperator):
    __slots__ = ()


UnarySub = make_operator_class("UnarySub", UnaryOperator, "-")

Not = make_operator_class("Not", UnaryBooleanOperator, "not ")

Add = make_operator_class("Add", ArithmeticOperator, "+")
Mul = make_operator_class("Mul", ArithmeticOperator, "*")
Minus = make_operator_class("Minus", ArithmeticOperator, "-")
Div = make_operator_class("Div", ArithmeticOperator, "/")

Eq = make_operator_class("Eq", ComparisonOperator, "==")
Ne = make_operator_class("Ne", ComparisonOperator, "!=")
Lt = make_operator_class("Lt", ComparisonOperator, "<")
Le = make_operator_class("Le", ComparisonOperator, "<=")
Gt = make_operator_class("Gt", ComparisonOperator, ">")
Ge = make_operator_class("Ge", ComparisonOperator, ">=")

And = make_operator_class("And", BooleanOperator, "and")
Or = make_operator_class("Or", BooleanOperator, "or")
Is = make_operator_class("Is", BinaryBooleanOperator, "is")
IsNot = make_operator_class("IsNot", BinaryBooleanOperator, "is not")
In = make_operator_class("In", BinaryBooleanOperator, "in")


# ==============================================================================
class IfTernaryOperator(Operator):
    """
    Represent a ternary conditional operator in the code.

    Represent a ternary conditional operator in the code,
    of the form (a if cond else b).

    Parameters
    ----------
    cond : model object
        The condition which determines which result is returned.
    value_true : model object
        The value returned if the condition is true.
    value_false : model object
        The value returned if the condition is false.

    Examples
    --------
    >>> from x2py.ast.internals import Symbol
    >>> from x2py.ast.core import Assign
    >>> from x2py.ast.operators import IfTernaryOperator
    >>> n = Symbol('n')
    >>> x = 5 if n > 1 else 2
    >>> IfTernaryOperator(Gt(n > 1),  5,  2)
    IfTernaryOperator(Gt(n > 1),  5,  2)
    """

    __slots__ = ()

    def __init__(self, cond, value_true, value_false):
        super().__init__(cond, value_true, value_false, shape=value_true._shape, class_type=value_true._class_type)

    @property
    def cond(self):
        return self._args[0]

    @property
    def value_true(self):
        return self._args[1]

    @property
    def value_false(self):
        return self._args[2]

    def __str__(self):
        return f"(({self.value_true}) if ({self.cond}) else ({self.value_false})"


# ==============================================================================
class Symbol(str):
    """
    Class representing a symbol in the code.

    Symbolic placeholder for a Python variable, which has a name but no type yet.
    This is very generic, and it can also represent a function or a module.

    Parameters
    ----------
    name : str
        Name of the symbol.

    is_temp : bool
        Indicates if the symbol is a temporary object. This either means that the
        symbol represents an object originally named `_` in the code, or that the
        symbol represents an object created by X2py in order to assign a
        temporary object. This is sometimes necessary to facilitate the translation.

    Examples
    --------
    >>> from x2py.ast.internals import Symbol
    >>> x = Symbol('x')
    x
    """

    __slots__ = ("_is_temp",)
    _model_immutable = True

    def __new__(cls, name, is_temp=False):
        return super().__new__(cls, name)

    def __init__(self, name, is_temp=False):
        self._is_temp = is_temp
        init_model_object(self)

    @property
    def is_temp(self):
        """
        Indicates if this symbol represents a temporary variable created by X2py,
        and was not present in the original Python code [default value : False].
        """
        return self._is_temp


class Variable:
    """
    Represents a typed variable.

    Represents a variable in the code and stores all useful properties which allow
    for easy usage of this variable.

    Parameters
    ----------
    class_type : Type
        The Python type of the variable.

    name : str, list, DottedName
        The name of the variable represented. This can be either a string
        or a dotted name, when using a Class attribute.

    memory_handling : str, default: 'stack'
        'heap' is used for arrays, if we need to allocate memory on the heap.
        'stack' if memory should be allocated on the stack, represents stack arrays and scalars.
        'alias' if object allows access to memory stored in another variable.

    is_target : bool, default: False
        Indicates if object is pointed to by another variable.

    is_optional : bool, default: False
        Indicates if object is an optional argument of a function.

    is_private : bool, default: False
        Indicates if object is private within a Module.

    projected_output : bool, default: False
        True when a compact semantic contract projects this visible writable
        argument into Python returns without preserving source-level output syntax.

    passes_by_value : bool, default: False
        True when a native scalar dummy has Fortran ``value`` ABI.

    fortran_array_category : str, optional
        Native Fortran array category preserved as ABI metadata. Python
        extraction and native handoff policy comes from ``ownership_decision``.

    fortran_callback_access : str, optional
        Exact callback dummy declaration access for Fortran adapter signatures.

    fortran_character_length : object, optional
        Native Fortran character element length for character scalars and arrays.

    fortran_source_shape : tuple, optional
        Native Fortran source dimensions preserved for ABI-sensitive declarations.

    ownership_decision : object, default: None
        Central ownership policy decision preserved from semantic lowering.

    getter_ownership_decision : object, default: None
        Completed policy used when this field or module variable is read.

    setter_ownership_decision : object, default: None
        Completed policy used when this field is assigned through a generated setter.

    snapshot_field_action : object, default: None
        Completed copy action used when this field appears in a derived snapshot.

    native_array_handle_policy : object, default: None
        Completed policy for native allocatable or pointer array handle lowering.

    array_interop_policy : object, default: None
        Completed selector for ordinary data-buffer versus native descriptor array ABI.

    shape : tuple, default: None
        The shape of the array. A tuple whose elements indicate the number of elements along
        each of the dimensions of an array. The elements of the tuple should be None or model objects.

    cls_base : class, default: None
        Class base if variable is an object or an object member.

    is_argument : bool, default: False
        Indicates if object is the argument of a function.

    is_temp : bool, default: False
        Indicates if this symbol represents a temporary variable created by X2py,
        and was not present in the original Python code.

    Examples
    --------
    >>> from x2py.ast.datatypes import NumpyInt64Type, NumpyFloat64Type
    >>> from x2py.ast.core import Variable
    >>> Variable(NumpyInt64Type(), 'n')
    n
    >>> n = 4
    >>> Variable(NumpyFloat64Type(), 'x', shape=(n,2), memory_handling='heap')
    x
    >>> Variable(NumpyInt64Type(), DottedName('matrix', 'n_rows'))
    matrix.n_rows
    """

    __slots__ = (
        "_alloc_shape",
        "_array_interop_policy",
        "_assumed_rank",
        "_class_type",
        "_cls_base",
        "_default_value",
        "_fortran_array_category",
        "_fortran_callback_access",
        "_fortran_character_length",
        "_fortran_source_shape",
        "_getter_ownership_decision",
        "_is_argument",
        "_is_optional",
        "_is_private",
        "_is_target",
        "_is_temp",
        "_memory_handling",
        "_name",
        "_native_array_handle_policy",
        "_ownership_decision",
        "_passes_by_value",
        "_projected_output",
        "_setter_ownership_decision",
        "_shape",
        "_snapshot_field_action",
    )
    _attribute_nodes = ()

    def __init__(
        self,
        class_type,
        name,
        *,
        memory_handling="stack",
        is_target=False,
        is_optional=False,
        is_private=False,
        passes_by_value=False,
        fortran_array_category=None,
        fortran_callback_access=None,
        fortran_character_length=None,
        fortran_source_shape=None,
        getter_ownership_decision=None,
        ownership_decision=None,
        setter_ownership_decision=None,
        snapshot_field_action=None,
        native_array_handle_policy=None,
        array_interop_policy=None,
        projected_output=False,
        assumed_rank=False,
        shape=None,
        cls_base=None,
        default_value=None,
        is_argument=False,
        is_temp=False,
    ):
        init_model_object(self)

        # ------------ Variable Properties ---------------
        # if class attribute
        if isinstance(name, str):
            name = name.split(""".""")
            if len(name) == 1:
                name = Symbol(name[0])
            else:
                raise ValueError(name)

        assert isinstance(name, Symbol)
        self._name = name

        if memory_handling not in ("heap", "stack", "alias"):
            raise ValueError("memory_handling must be 'heap', 'stack' or 'alias'")
        self._memory_handling = memory_handling

        if not isinstance(is_target, bool):
            raise TypeError("is_target must be a boolean.")
        self.is_target = is_target

        if not isinstance(is_optional, bool):
            raise TypeError("is_optional must be a boolean.")
        self._is_optional = is_optional

        if not isinstance(is_private, bool):
            raise TypeError("is_private must be a boolean.")
        self._is_private = is_private

        if not isinstance(passes_by_value, bool):
            raise TypeError("passes_by_value must be a boolean.")
        self._passes_by_value = passes_by_value
        self._fortran_array_category = fortran_array_category
        if fortran_callback_access not in (None, "read", "write", "readwrite", "unspecified"):
            raise ValueError(
                "fortran_callback_access must be one of None, 'read', 'write', 'readwrite', or 'unspecified'"
            )
        self._fortran_callback_access = fortran_callback_access
        self._fortran_character_length = fortran_character_length
        self._fortran_source_shape = tuple(fortran_source_shape or ())
        self._getter_ownership_decision = getter_ownership_decision
        self._ownership_decision = ownership_decision
        self._setter_ownership_decision = setter_ownership_decision
        self._snapshot_field_action = snapshot_field_action
        self._native_array_handle_policy = native_array_handle_policy
        self._array_interop_policy = array_interop_policy
        if not isinstance(projected_output, bool):
            raise TypeError("projected_output must be a boolean.")
        self._projected_output = projected_output
        if not isinstance(assumed_rank, bool):
            raise TypeError("assumed_rank must be a boolean.")
        self._assumed_rank = assumed_rank
        self._cls_base = cls_base
        self._default_value = default_value
        self._is_argument = is_argument
        self._is_temp = is_temp

        # ------------ model object Properties ---------------
        assert isinstance(class_type, Type)
        rank = class_type.rank

        if rank == 0:
            assert shape is None

        elif shape is None:
            shape = tuple(None for i in range(class_type.container_rank))

        self._alloc_shape = shape
        self._class_type = class_type
        self._shape = self.process_shape(shape)

    def process_shape(self, shape):
        """
        Simplify the provided shape and ensure it has the expected format.

        The provided shape is the shape used to create the object, and it can
        be a long expression. In most cases where the shape is required the
        provided shape is inconvenient, or it might have become invalid. This
        function therefore replaces those expressions with calls to the function
        `ArrayShapeElement`.

        Parameters
        ----------
        shape : iterable of int
            The array shape to be simplified.

        Returns
        -------
        tuple
            The simplified array shape.
        """
        if self.rank == 0:
            return None
        if not hasattr(shape, "__iter__"):
            shape = [shape]

        new_shape = [None] * len(shape)
        for i, s in enumerate(shape):
            if isinstance(s, Literal) and isinstance(s.dtype.primitive_type, PrimitiveIntegerType):
                new_shape[i] = s
            elif isinstance(s, int):
                new_shape[i] = convert_to_literal(s)
            elif is_model_object(s):
                new_shape[i] = s
            elif s is not None:
                raise ValueError(s)
        return tuple(new_shape)

    @property
    def name(self):
        """Name of the variable"""
        return self._name

    @property
    def alloc_shape(self):
        """Shape of the variable at allocation

        The shape used in x2py is usually simplified to contain
        only Literals and ArraySizes but the shape for
        the allocation of x cannot be `Shape(x)`
        """
        return self._alloc_shape

    @property
    def memory_handling(self):
        """Indicates whether a Variable has a dynamic size"""
        return self._memory_handling

    @memory_handling.setter
    def memory_handling(self, memory_handling):
        if memory_handling not in ("heap", "stack", "alias"):
            raise ValueError("memory_handling must be 'heap', 'stack' or 'alias'")
        self._memory_handling = memory_handling

    @property
    def is_alias(self):
        """Indicates if variable is an alias"""
        return self.memory_handling == "alias"

    @property
    def on_heap(self):
        """Indicates if memory is allocated on the heap"""
        return self.memory_handling == "heap"

    @property
    def on_stack(self):
        """Indicates if memory is allocated on the stack"""
        return self.memory_handling == "stack"

    @property
    def is_stack_array(self):
        """Indicates if the variable is located on stack and is an array"""
        return self.on_stack and self.rank > 0

    @property
    def cls_base(self):
        """Class from which the Variable inherits"""
        return self._cls_base

    @property
    def default_value(self):
        """Source-level literal value associated with this variable, when any."""
        return self._default_value

    @property
    def is_temp(self):
        """
        Indicates if this symbol represents a temporary variable created by X2py,
                and was not present in the original Python code [default value : False].
        """
        return self._is_temp

    @property
    def is_target(self):
        """Indicates if the data in this Variable is
        shared with (pointed at by) another Variable
        """
        return self._is_target

    @is_target.setter
    def is_target(self, is_target):
        if not isinstance(is_target, bool):
            raise TypeError("is_target must be a boolean.")
        self._is_target = is_target

    @property
    def is_optional(self):
        """Indicates if the Variable is optional
        in this context
        """
        return self._is_optional

    @property
    def is_private(self):
        """Indicates if the Variable is private
        within the Module
        """
        return self._is_private

    @property
    def passes_by_value(self):
        """True when the native scalar dummy uses Fortran ``value`` ABI."""
        return self._passes_by_value

    @property
    def projected_output(self):
        """True when this visible writable argument is projected as a Python result."""
        return self._projected_output

    @property
    def fortran_array_category(self):
        """Native Fortran array category carried as ABI metadata."""
        return self._fortran_array_category

    @property
    def fortran_callback_access(self):
        """Exact callback dummy declaration access for Fortran adapter signatures."""
        return self._fortran_callback_access

    @property
    def fortran_character_length(self):
        """Native Fortran character element length, when this variable stores character data."""
        return self._fortran_character_length

    @property
    def fortran_source_shape(self):
        """Native Fortran source dimensions used by ABI-sensitive printers."""
        return self._fortran_source_shape

    @property
    def ownership_decision(self):
        """Central ownership policy decision for this variable."""
        return self._ownership_decision

    @property
    def getter_ownership_decision(self):
        """Completed policy used by a generated getter."""
        return self._getter_ownership_decision

    @property
    def setter_ownership_decision(self):
        """Completed ownership policy used by a generated field setter."""
        return self._setter_ownership_decision

    @property
    def snapshot_field_action(self):
        """Completed copy action used when this field appears in a snapshot."""
        return self._snapshot_field_action

    @property
    def native_array_handle_policy(self):
        """Completed policy for native allocatable or pointer array handles."""
        return self._native_array_handle_policy

    @property
    def array_interop_policy(self):
        """Completed selector for the generated array ABI lane."""
        return self._array_interop_policy

    @property
    def assumed_rank(self):
        """True when this array represents a Fortran ``dimension(..)`` dummy."""
        return self._assumed_rank

    @property
    def is_argument(self):
        """Indicates whether the Variable is
        a function argument in this context
        """
        return self._is_argument

    def declare_as_argument(self):
        """
        Indicate that the variable is used as an argument.

        This function is called by FunctionDefArgument to ensure that
        arguments are correctly flagged as such.
        """
        self._is_argument = True

    @property
    def is_ndarray(self):
        """
        User friendly method to check if the variable is a numpy.ndarray.

        User friendly method to check if the variable is an ndarray.
        """
        return isinstance(self.class_type, NumpyNDArrayType) and not self.class_type.raw

    @property
    def is_raw_array(self):
        """Whether the variable is represented directly as a C array or pointer."""
        return isinstance(self.class_type, NumpyNDArrayType) and self.class_type.raw

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f"{type(self).__name__}({self.name}, type={self.class_type!r})"

    def __hash__(self):
        return hash((type(self).__name__, self._name))

    def clone(self, name, new_class=None, **kwargs):
        """
        Create a clone of the current variable.

        Create a new Variable object of the chosen class
        with the provided name and options. All non-specified
        options will match the current instance.

        Parameters
        ----------
        name : str
            The name of the new Variable.
        new_class : type, optional
            The class type of the new Variable (e.g. DottedVariable).
            The default is the same class type.
        **kwargs : dict
            Dictionary containing any keyword-value
            pairs which are valid constructor keywords.

        Returns
        -------
        Variable
            The cloned variable.
        """

        cls = self.__class__ if new_class is None else new_class

        args = inspect.signature(Variable.__init__)
        new_kwargs = {k: getattr(self, "_" + k) for k in args.parameters if "_" + k in dir(self)}
        new_kwargs.update(kwargs)
        new_kwargs["name"] = name
        if "shape" not in kwargs:
            new_kwargs["shape"] = self.alloc_shape

        return cls(**new_kwargs)

    def rename(self, newname):
        """Forbidden method for renaming the variable"""
        # The name is part of the hash so it must never change
        raise RuntimeError("Cannot modify hash definition")

    @is_temp.setter
    def is_temp(self, is_temp):
        if not isinstance(is_temp, bool):
            raise TypeError("is_temp must be a boolean")
        if is_temp:
            raise ValueError("Variables cannot become temporary")
        self._is_temp = is_temp


class IndexedElement:
    """
    Represents an indexed object in the code.

    Represents an object which is a subset of a base object. The
    indexed object is retrieved by passing indices to the base
    object using the `[]` syntax.

    In the semantic stage, the base object is an array, tuple or
    list. This function then determines the new rank and shape of
    the data block.

    In the syntactic stage, this object is more versatile, it
    stores anything which is indexed using `[]` syntax. This can
    additionally include classes, maps, etc.

    Parameters
    ----------
    base : Variable | Symbol | DottedName
        The object being indexed.

    *indices : tuple of model object
        The values used to index the base.

    Examples
    --------
    >>> from x2py.ast.core import Variable, IndexedElement
    >>> from x2py.ast.datatypes import NumpyInt64Type
    >>> A = Variable(NumpyInt64Type(), 'A', shape=(2,3), rank=2)
    >>> i = Variable(NumpyInt64Type(), 'i')
    >>> j = Variable(NumpyInt64Type(), 'j')
    >>> IndexedElement(A, (i, j))
    IndexedElement(A, i, j)
    >>> IndexedElement(A, i, j) == A[i, j]
    True
    """

    __slots__ = ("_class_type", "_indices", "_is_slice", "_label", "_shape")
    _attribute_nodes = ("_label", "_indices", "_shape")

    def __init__(self, base, *indices):
        self._label = base
        self._shape = None

        rank = base.class_type.container_rank
        assert len(indices) <= rank

        if any(not isinstance(a, int | Slice) and not is_model_object(a) for a in indices):
            raise TypeError("Index is not of valid type")

        if len(indices) < rank:
            indices = indices + tuple([Slice(None, None)] * (rank - len(indices)))
            self._indices = tuple(convert_to_literal(a) if isinstance(a, int) else a for a in indices)
        else:
            self._indices = tuple(convert_to_literal(a) if isinstance(a, int) else a for a in indices)

        if isinstance(base.class_type, TupleType):
            assert (
                len(self._indices) == 1
                and isinstance(self._indices[0], Literal)
                and isinstance(self._indices[0].dtype.primitive_type, PrimitiveIntegerType)
            )
            self._class_type = base.class_type[self._indices[0]]
            self._is_slice = False
            self._shape = None
        else:
            self._class_type = base.class_type.element_type
            self._is_slice = False
            self._shape = (1,)

        init_model_object(self)

    @property
    def base(self):
        """The object which is indexed"""
        return self._label

    @property
    def indices(self):
        """A tuple of indices used to index the variable"""
        return self._indices

    def __str__(self):
        indices = ",".join(str(i) for i in self.indices)
        return f"{self.base}[{indices}]"

    def __repr__(self):
        indices = ",".join(repr(i) for i in self.indices)
        return f"{self.base!r}[{indices}]"

    def __hash__(self):
        return hash((self.base, self._indices))


class FortranCharacterLength:
    """Represent the Fortran ``len(value)`` intrinsic for character storage."""

    __slots__ = ("_arg", "_class_type", "_shape")
    _attribute_nodes = ("_arg",)

    def __init__(self, arg):
        self._arg = arg
        self._class_type = NumpyInt32Type()
        self._shape = None
        init_model_object(self)

    @property
    def arg(self):
        """The character scalar or array whose element length is requested."""
        return self._arg


class DottedVariable(Variable):
    """
    Class representing a dotted variable.

    Represents a dotted variable. This is usually
    a variable which is a member of a class

    E.g.
    a = AClass()
    a.b = 3

    In this case b is a DottedVariable where the lhs is a.

    Parameters
    ----------
    *args : tuple
        See x2py.ast.variable.Variable.

    lhs : Variable
        The Variable on the right of the '.'.

    **kwargs : dict
        See x2py.ast.variable.Variable.
    """

    __slots__ = ("_lhs",)
    _attribute_nodes = ("_lhs",)

    def __init__(self, *args, lhs, **kwargs):
        self._lhs = lhs
        super().__init__(*args, **kwargs)

    @property
    def lhs(self):
        """The object before the final dot in the
        dotted variable

        e.g. for the DottedVariable:
        a.b
        The lhs is a
        """
        return self._lhs

    def __hash__(self):
        return hash((type(self).__name__, self.name, self.lhs))

    def __str__(self):
        return str(self.lhs) + "." + str(self.name)

    def __repr__(self):
        lhs = repr(self.lhs)
        name = str(self.name)
        class_type = repr(self.class_type)
        classname = type(self).__name__
        return f"{classname}({lhs}.{name}, type={class_type})"


class AsName:
    """
    Represents a renaming of an object, used with Import.

    A class representing the renaming of an object such as a function or a
    variable. This usually occurs during an Import.

    Parameters
    ----------
    obj : model object or model type
        The variable, function, or module being renamed.
    local_alias : str
        Name of variable or function in this context.
    """

    __slots__ = ("_local_alias", "_obj", "_source_name")
    _attribute_nodes = ()

    def __init__(self, obj, local_alias, *, source_name=None):
        assert (is_model_object(obj) and not isinstance(obj, Symbol)) or is_model_class(obj)
        self._obj = obj
        self._local_alias = local_alias
        self._source_name = source_name
        init_model_object(self)

    @property
    def name(self):
        """The original name of the object"""
        if self._source_name is not None:
            return self._source_name
        obj = self._obj
        if isinstance(obj, str | Symbol):
            return obj
        return obj.name

    @property
    def local_alias(self):
        """
        The local_alias name of the object.

        The name used to identify the object in the local scope.
        """
        return self._local_alias

    @property
    def object(self):
        """The underlying object described by this AsName"""
        return self._obj

    def __repr__(self):
        return f"{self.object} as {self.local_alias}"

    def __eq__(self, string):
        if isinstance(string, str):
            return string == self.local_alias
        if isinstance(string, AsName):
            return string.local_alias == self.local_alias
        return self is string

    def __ne__(self, string):
        return not self == string

    def __hash__(self):
        return hash(self.local_alias)


class Assign:
    """
    Represents variable assignment for code generation.

    Class representing an assignment node, where the result of an expression
    (rhs: right hand side) is saved into a variable (lhs: left hand side).

    Parameters
    ----------
    lhs : model object
        In the syntactic stage:
           Object representing the lhs of the expression. These should be
           singular objects, such as one would use in writing code. Notable types
           include Symbol, and IndexedElement. Types that
           subclass these types are also supported.
        In the semantic stage:
           Variable or IndexedElement.

    rhs : model object
        In the syntactic stage:
          Object representing the rhs of the expression.
        In the semantic stage :
          model object with the same shape as the lhs.

    Examples
    --------
    >>> from x2py.ast.datatypes import NumpyInt64Type
    >>> from x2py.ast.internals import symbols
    >>> from x2py.ast.variable import Variable
    >>> from x2py.ast.core import Assign
    >>> x, y, z = symbols('x, y, z')
    >>> Assign(x, y)
    x := y
    >>> Assign(x, 0)
    x := 0
    >>> A = Variable(NumpyInt64Type(), 'A', rank = 2)
    >>> Assign(x, A)
    x := A
    >>> Assign(A[0,1], x)
    IndexedElement(A, 0, 1) := x
    """

    __slots__ = ("_lhs", "_rhs")
    _attribute_nodes = ("_lhs", "_rhs")

    def __init__(self, lhs, rhs):
        if isinstance(lhs, tuple | list):
            lhs = tuple(lhs)
        self._lhs = lhs
        self._rhs = rhs
        init_model_object(self)

    def __str__(self):
        return f"{self.lhs} := {self.rhs}"

    def __repr__(self):
        return f"{self.lhs!r} := {self.rhs!r}"

    @property
    def lhs(self):
        return self._lhs

    @property
    def rhs(self):
        return self._rhs

    @property
    def is_alias(self):
        """Returns True if the assignment is an alias."""

        # TODO to be improved when handling classes

        lhs = self.lhs
        rhs = self.rhs
        cond = isinstance(rhs, Variable) and rhs.rank > 0
        cond = cond or isinstance(rhs, IndexedElement)
        cond = cond and isinstance(lhs, Symbol)
        return cond or (isinstance(rhs, Variable) and rhs.is_alias)


# ------------------------------------------------------------------------------
class Allocate:
    """
    Represents memory allocation for code generation.

    Represents memory allocation (usually of an array) for code generation.
    This is relevant to low-level target languages, such as C or Fortran,
    where the programmer must take care of heap memory allocation.

    Parameters
    ----------
    variable : x2py.ast.core.Variable
        The typed variable (usually an array) that needs memory allocation.

    shape : int or iterable or None
        Shape of the array after allocation (None for scalars).

    status : str {'allocated'|'unallocated'|'unknown'}
        Variable allocation status at object creation.

    like : model object, optional
        A model object describing the amount of memory which must be allocated.
        In C this provides the size which will be passed to malloc. In Fortran
        this provides the source argument of the allocate function.

    alloc_type : str {'init'|'reserve'|'resize'}, optional
        Specifies the memory allocation strategy for containers with dynamic memory management.
        This parameter is relevant for any container type where memory allocation patterns
        need to be specified based on usage.

        - 'init' refers to direct allocation with predefined data (e.g., `x = [1, 2, 4]`).
        - 'reserve' refers to cases where the container will be appended to.
        - 'resize' refers to cases where the container is populated via indexed elements.
        - 'function' refers to cases where the container is allocated in a function. It is
                     still useful to have an allocate node in this case for easy determination
                     of where deallocations are needed.

    Notes
    -----
    An object of this class is immutable, although it contains a reference to a
    mutable Variable object.
    """

    __slots__ = ("_alloc_type", "_like", "_order", "_shape", "_status", "_variable")
    _attribute_nodes = ("_variable", "_like")

    # ...
    def __init__(self, variable, *, shape, status, like=None, alloc_type=None):
        if not isinstance(variable, Variable):
            raise TypeError(f"Can only allocate a 'Variable' object, got {type(variable)} instead")

        if variable.on_stack:
            # Variable may only be a pointer in the wrapper
            raise ValueError("Variable must be allocatable")

        if shape and not isinstance(shape, int | tuple | list):
            raise TypeError(f"Cannot understand 'shape' parameter of type '{type(shape)}'")

        assert variable.class_type.shape_is_compatible(shape)

        if not isinstance(status, str):
            raise TypeError(f"Cannot understand 'status' parameter of type '{type(status)}'")

        if status not in ("allocated", "unallocated", "unknown"):
            raise ValueError(f"Value of 'status' not allowed: '{status}'")

        assert alloc_type in (None, "init", "reserve", "resize", "function")
        assert alloc_type in (None, "function")

        self._variable = variable
        self._shape = shape
        self._order = variable.order
        self._status = status
        self._like = like
        self._alloc_type = alloc_type
        init_model_object(self)

    # ...

    @property
    def variable(self):
        """
        The variable to be allocated.

        The variable to be allocated.
        """
        return self._variable

    @property
    def shape(self):
        """
        The shape that the variable should be allocated to.

        The shape that the variable should be allocated to.
        """
        return self._shape

    @property
    def order(self):
        """
        The order that the variable will be allocated with.

        The order that the variable will be allocated with.
        """
        return self._order

    @property
    def status(self):
        """
        The allocation status of the variable before this allocation.

        The allocation status of the variable before this allocation.
        One of {'allocated'|'unallocated'|'unknown'}.
        """
        return self._status

    @property
    def like(self):
        """
        model object describing the amount of memory needed for the allocation.

        A model object describing the amount of memory which must be allocated.
        In C this provides the size which will be passed to malloc. In Fortran
        this provides the source argument of the allocate function.
        """
        return self._like

    @property
    def alloc_type(self):
        """
        Determines the allocation type for homogeneous containers.

        Returns a string that indicates the allocation type used for memory allocation.
        The value is either 'init' for containers initialized with predefined data,
        'reserve' for containers populated through appending, and 'resize' for containers
        populated through indexed element assignment.
        """
        return self._alloc_type

    def __str__(self):
        return f"Allocate({self.variable}, shape={self.shape}, order={self.order}, status={self.status})"

    def __eq__(self, other):
        if isinstance(other, Allocate):
            return (
                (self.variable is other.variable)
                and (self.shape == other.shape)
                and (self.order == other.order)
                and (self.status == other.status)
            )
        return False

    def __hash__(self):
        return hash((id(self.variable), self.shape, self.order, self.status))


# ------------------------------------------------------------------------------
class Nullify:
    """Fortran pointer nullification statement."""

    __slots__ = ("_variable",)
    _attribute_nodes = ("_variable",)

    def __init__(self, variable):
        if not isinstance(variable, Variable):
            raise TypeError(f"Can only nullify a 'Variable' object, got {type(variable)} instead")
        self._variable = variable
        init_model_object(self)

    @property
    def variable(self):
        return self._variable


# ------------------------------------------------------------------------------
class Deallocate:
    """
    Class representing memory deallocation.

    Represents memory deallocation (usually of an array) for code generation.
    This is relevant to low-level target languages, such as C or Fortran,
    where the programmer must take care of heap memory deallocation.

    Parameters
    ----------
    variable : x2py.ast.core.Variable
        The typed variable (usually an array) that needs memory deallocation.

    Notes
    -----
    An object of this class is immutable, although it contains a reference to a
    mutable Variable object.
    """

    __slots__ = ("_variable",)
    _attribute_nodes = ("_variable",)

    # ...
    def __init__(self, variable):
        if not isinstance(variable, Variable):
            raise TypeError(f"Can only allocate a 'Variable' object, got {type(variable)} instead")

        self._variable = variable
        init_model_object(self)

    # ...

    @property
    def variable(self):
        return self._variable

    def __eq__(self, other):
        if isinstance(other, Deallocate):
            return self.variable is other.variable
        return False

    def __hash__(self):
        return hash(id(self.variable))


# ------------------------------------------------------------------------------
class CodeBlock:
    """
    Represents a block of statements.

    Represents a list of statements for code generation. Each statement
    represents a line of code.

    Parameters
    ----------
    body : iterable
        The lines of code to be grouped together.

    unravelled : bool, default=False
        Indicates whether the loops in the code have already been unravelled.
        This is useful for printing in languages which don't support vector
        expressions.
    """

    __slots__ = ("_body", "_unravelled")
    _attribute_nodes = ("_body",)

    def __init__(self, body, unravelled=False):
        ls = []
        for i in body:
            if isinstance(i, CodeBlock):
                ls += i.body
            elif i is not None and not isinstance(i, EmptyNode):
                ls.append(i)
        if not isinstance(unravelled, bool):
            raise TypeError("unravelled must be a boolean")
        self._body = tuple(ls)
        self._unravelled = unravelled
        init_model_object(self)

    @property
    def body(self):
        return self._body

    @property
    def unravelled(self):
        """Indicates whether the vector syntax of python
        has been unravelled into for loops
        """
        return self._unravelled

    @property
    def lhs(self):
        return self.body[-1].lhs

    def __repr__(self):
        return f"CodeBlock({self.body})"


class AliasAssign:
    """
    Representing assignment of an alias to its local_alias.

    Represents aliasing for code generation. An alias is any statement of the
    form `lhs := rhs` where lhs is a pointer and rhs is a local_alias. In other words
    the contents of `lhs` will change if the contents of `rhs` are modified.

    Parameters
    ----------
    lhs : model object
        In the syntactic stage:
           Object representing the lhs of the expression. These should be
           singular objects, such as one would use in writing code. Notable types
           include Symbol, and IndexedElement. Types that
           subclass these types are also supported.
        In the semantic stage:
           Variable.

    rhs : Symbol | Variable, IndexedElement
        The local_alias of the assignment. A Symbol in the syntactic stage,
        a Variable or a Slice of an array in the semantic stage.

    Examples
    --------
    >>> from x2py.ast.internals import Symbol
    >>> from x2py.ast.core import AliasAssign
    >>> from x2py.ast.core import Variable
    >>> n = Variable(NumpyInt64Type(), 'n')
    >>> x = Variable(NumpyInt64Type(), 'x', rank=1, shape=[n])
    >>> y = Symbol('y')
    >>> AliasAssign(y, x)
    """

    __slots__ = ("_lhs", "_rhs")
    _attribute_nodes = ("_lhs", "_rhs")

    def __init__(self, lhs, rhs):
        if not lhs.is_alias:
            raise TypeError("lhs must be a pointer")

        if isinstance(rhs, FunctionCall) and not rhs.funcdef.results.var.is_alias:
            raise TypeError("A pointer cannot point to the address of a temporary variable")

        self._lhs = lhs
        self._rhs = rhs
        init_model_object(self)

    def __str__(self):
        return f"{self.lhs} := {self.rhs}"

    @property
    def lhs(self):
        return self._lhs

    @property
    def rhs(self):
        return self._rhs


class AugAssign(Assign):
    r"""
    Represents augmented variable assignment for code generation.

    Represents augmented variable assignment for code generation.
    Augmented variable assignment is an assignment which modifies the
    variable using its initial value rather than simply replacing the
    value; for example via an addition (`+=`).

    Parameters
    ----------
    lhs : Symbol | model object
        Object representing the lhs of the expression.
        In the syntactic stage this may be a Symbol, or an IndexedElement.
        In later stages the object should inherit from model object and be fully
        typed.

    op : str
        Operator (+, -, /, \*, %).

    rhs : model object
        Object representing the rhs of the expression.

    Examples
    --------
    >>> from x2py.ast.core import Variable
    >>> from x2py.ast.core import AugAssign
    >>> s = Variable(NumpyInt64Type(), 's')
    >>> t = Variable(NumpyInt64Type(), 't')
    >>> AugAssign(s, '+', 2 * t + 1)
    s += 1 + 2*t
    """

    __slots__ = ("_op",)
    _accepted_operators: ClassVar = {
        "+": Add,
    }

    def __init__(self, lhs, op, rhs):
        if op not in self._accepted_operators:
            raise TypeError("Unrecognized Operator")

        self._op = op

        super().__init__(lhs, rhs)

    def __repr__(self):
        return f"{self.lhs} {self.op}= {self.rhs}"

    @property
    def op(self):
        """
        Get the string describing the operator which modifies the lhs variable.

        Get the string describing the operator which modifies the lhs variable.
        """
        return self._op

    def to_basic_assign(self):
        """
        Convert the AugAssign to an Assign.

        Convert the AugAssign to an Assign.
        E.g. convert:
        a += b
        to:
        a = a + b

        Returns
        -------
        Assign
            An assignment equivalent to the AugAssign.
        """
        return Assign(self.lhs, self._accepted_operators[self._op](self.lhs, self.rhs))


class Module:
    """
    Represents a module in the code.

    The X2py node representing a Python module. A module consists of everything
    inside a given Python file.

    Parameters
    ----------
    name : str
        Name of the module.

    variables : list
        List of the variables that appear in the block.

    funcs : list
        A list of FunctionDef instances.

    init_func : FunctionDef, default: None
        The function which initialises the module (expressions in the
        python module which are executed on import).

    free_func : FunctionDef, default: None
        The function which frees any variables allocated in the module.

    overload_sets : list
        A list of FunctionOverloadSet instances.

    classes : list
        A list of ClassDef instances.

    imports : list, tuple
        List of needed imports.

    scope : Scope
        The scope of the module.

    is_external : bool
        Indicates if the Module's definition is found elsewhere.
        This is notably the case for gFTL extensions.

    Examples
    --------
    >>> from x2py.ast.variable import Variable
    >>> from x2py.ast.core import FunctionDefArgument, Assign, FunctionDefResult
    >>> from x2py.ast.core import ClassDef, FunctionDef, Module
    >>> from x2py.ast.operators import Add, Minus
    >>> from x2py.codegen.models.datatypes import convert_to_literal
    >>> x = Variable(NumpyFloat64Type(), 'x')
    >>> y = Variable(NumpyFloat64Type(), 'y')
    >>> z = Variable(NumpyFloat64Type(), 'z')
    >>> t = Variable(NumpyFloat64Type(), 't')
    >>> a = Variable(NumpyFloat64Type(), 'a')
    >>> b = Variable(NumpyFloat64Type(), 'b')
    >>> body = [Assign(z,Add(x,a))]
    >>> args = [FunctionDefArgument(arg) for arg in [x,y,a,b]]
    >>> results = [FunctionDefResult(res) for res in [z,t]]
    >>> translate = FunctionDef('translate', args, results, body)
    >>> attributes   = [x,y]
    >>> methods     = [translate]
    >>> Point = ClassDef('Point', attributes, methods)
    >>> incr = FunctionDef('incr', [FunctionDefArgument(x)], [FunctionDefResult(y)], [Assign(y,Add(x,convert_to_literal(1)))])
    >>> decr = FunctionDef('decr', [FunctionDefArgument(x)], [FunctionDefResult(y)], [Assign(y,Minus(x,convert_to_literal(1)))])
    >>> Module('my_module', [], [incr, decr], classes = [Point])
    Module(my_module, [], [FunctionDef(), FunctionDef()], [], [ClassDef(Point, (x, y), (FunctionDef(),), [public], (), [], [])], ())
    """

    __slots__ = (
        "_classes",
        "_free_func",
        "_funcs",
        "_imports",
        "_init_func",
        "_internal_dictionary",
        "_is_external",
        "_name",
        "_overload_sets",
        "_python_exports",
        "_variable_inits",
        "_variables",
    )
    _attribute_nodes = (
        "_variables",
        "_funcs",
        "_overload_sets",
        "_classes",
        "_imports",
        "_init_func",
        "_free_func",
        "_variable_inits",
    )

    def __init__(
        self,
        name,
        variables,
        funcs,
        init_func=None,
        free_func=None,
        overload_sets=(),
        classes=(),
        imports=(),
        scope=None,
        is_external=False,
        python_exports=None,
    ):
        if not isinstance(name, str):
            raise TypeError("name must be a string")

        if not iterable(variables):
            raise TypeError("variables must be an iterable")
        for i in variables:
            if not isinstance(i, Variable):
                raise TypeError("Only a Variable instance is allowed.")

        if not iterable(funcs):
            raise TypeError("funcs must be an iterable")

        for i in funcs:
            if not isinstance(i, FunctionDef):
                raise TypeError("Only a FunctionDef instance is allowed.")

        if not iterable(classes):
            raise TypeError("classes must be an iterable")
        for i in classes:
            if not isinstance(i, ClassDef):
                raise TypeError("Only a ClassDef instance is allowed.")

        if not iterable(overload_sets):
            raise TypeError("overload_sets must be an iterable")
        for i in overload_sets:
            if not isinstance(i, FunctionOverloadSet):
                raise TypeError("Only a FunctionOverloadSet instance is allowed.")

        NoneType = type(None)
        assert isinstance(init_func, NoneType | FunctionDef)

        if not isinstance(free_func, NoneType | FunctionDef):
            raise TypeError("free_func must be a FunctionDef")

        if not iterable(imports):
            raise TypeError("imports must be an iterable")
        imports = list(imports)
        for i in classes:
            imports += i.imports
        imports = dict.fromkeys(imports)  # for unicity and ordering
        imports = tuple(imports.keys())

        assert isinstance(is_external, bool)

        self._name = name
        self._variables = variables
        self._variable_inits = [None] * len(variables)
        self._funcs = funcs
        self._init_func = init_func
        self._free_func = free_func
        self._overload_sets = overload_sets
        self._classes = classes
        self._imports = imports
        self._is_external = is_external
        self._python_exports = None if python_exports is None else dict(python_exports)

        def get_name(o):
            """Get the syntactic/Python name of the object"""
            n = o.name
            return scope.get_python_name(n) if scope else n

        self._internal_dictionary = {get_name(v): v for v in variables}
        self._internal_dictionary.update({get_name(f): f for f in funcs})
        self._internal_dictionary.update({get_name(i): i for i in overload_sets})
        self._internal_dictionary.update({get_name(c): c for c in classes})

        import_mods = {
            i.source: [t.object for t in i.target if isinstance(t.object, Module)]
            for i in imports
            if isinstance(i, Import)
        }
        self._internal_dictionary.update({v: t[0] for v, t in import_mods.items() if t})

        init_model_object(self, scope=scope)

    @property
    def name(self):
        """Name of the module"""
        return self._name

    @property
    def variables(self):
        """Module global variables"""
        return self._variables

    @property
    def init_func(self):
        """The function which initialises the module (expressions in the
        python module which are executed on import)
        """
        return self._init_func

    @property
    def free_func(self):
        """The function which frees any variables allocated in the module"""
        return self._free_func

    @property
    def funcs(self):
        """Any functions defined in the module"""
        return self._funcs

    @property
    def overload_sets(self):
        """Any overload_sets defined in the module"""
        return self._overload_sets

    @property
    def classes(self):
        """Any classes defined in the module"""
        return self._classes

    @property
    def imports(self):
        """Any imports in the module"""
        return self._imports

    def get_python_exports(self, obj):
        """Return ``(namespace, name)`` locations exported for one object."""
        if self._python_exports is None:
            name = self.scope.get_python_name(obj.name) if self.scope else obj.name
            return (((), str(name)),)
        return self._python_exports.get(id(obj), ())

    @property
    def has_explicit_python_exports(self):
        """Whether export locations came from an entry `.pyi` contract."""
        return self._python_exports is not None

    @property
    def declarations(self):
        """
        Get the declarations of all variables in the module.

        Get the declarations of all variables in the module.
        """
        return [
            Declare(i, value=v, module_variable=True)
            for i, v in zip(self.variables, self._variable_inits, strict=False)
        ]

    @property
    def body(self):
        """Returns the functions, overload_sets and classes defined
        in the module
        """
        return self.overload_sets + self.funcs + self.classes

    def __getitem__(self, arg):
        assert isinstance(arg, str)
        args = arg.split(".")
        result = self._internal_dictionary[args[0]]
        for key in args[1:]:
            result = result[key]
        return result

    def __contains__(self, arg):
        assert isinstance(arg, str | Symbol)
        args = str(arg).split(".")
        current_pos = self._internal_dictionary
        key = args[0]
        result = key in self._internal_dictionary
        i = 1
        while i < len(args) and result:
            current_pos = current_pos[key]
            key = args[i]
            result = key in current_pos
            i += 1
        return result

    def keys(self):
        """Returns the names of all objects accessible directly in this module"""
        return self._internal_dictionary.keys()

    @property
    def is_external(self):
        """
        Indicate if the Module's definition is found elsewhere.

        This is notably the case for gFTL extensions.
        """
        return self._is_external


class ModuleHeader:
    """
    Represents the header file for a module.

    This class is simply a wrapper around a module. It is helpful to differentiate
    between headers and sources when printing.

    Parameters
    ----------
    module : Module
        The module described by the header.

    See Also
    --------
    Module : The module itself.

    Examples
    --------
    >>> from x2py.ast.variable import Variable
    >>> from x2py.ast.core import FunctionDefArgument, Assign, FunctionDefResult
    >>> from x2py.ast.core import ClassDef, FunctionDef, Module
    >>> from x2py.ast.operators import Add, Minus
    >>> from x2py.codegen.models.datatypes import convert_to_literal
    >>> x = Variable(NumpyFloat64Type(), 'x')
    >>> y = Variable(NumpyFloat64Type(), 'y')
    >>> z = Variable(NumpyFloat64Type(), 'z')
    >>> t = Variable(NumpyFloat64Type(), 't')
    >>> a = Variable(NumpyFloat64Type(), 'a')
    >>> b = Variable(NumpyFloat64Type(), 'b')
    >>> body = [Assign(z,Add(x,a))]
    >>> args = [FunctionDefArgument(arg) for arg in [x,y,a,b]]
    >>> results = [FunctionDefResult(res) for res in [z,t]]
    >>> translate = FunctionDef('translate', args, results, body)
    >>> attributes   = [x,y]
    >>> methods     = [translate]
    >>> Point = ClassDef('Point', attributes, methods)
    >>> incr = FunctionDef('incr', [FunctionDefArgument(x)], [FunctionDefResult(y)], [Assign(y,Add(x,convert_to_literal(1)))])
    >>> decr = FunctionDef('decr', [FunctionDefArgument(x)], [FunctionDefResult(y)], [Assign(y,Minus(x,convert_to_literal(1)))])
    >>> Module('my_module', [], [incr, decr], classes = [Point])
    >>> ModuleHeader(mod)
    Module(my_module, [], [FunctionDef(), FunctionDef()], [], [ClassDef(Point, (x, y), (FunctionDef(),), [public], (), [], [])], ())
    """

    __slots__ = ("_module",)
    _attribute_nodes = ("_module",)

    def __init__(self, module):
        if not isinstance(module, Module):
            raise TypeError("module must be a Module")

        self._module = module
        init_model_object(self)

    @property
    def module(self):
        return self._module


class FunctionCallArgument:
    """
    An argument passed in a function call.

    Class describing an argument passed to a function in a
    function call.

    Parameters
    ----------
    value : model object
        The expression passed as an argument.
    keyword : str, optional
        If the argument is passed by keyword then this
        is that keyword.
    """

    __slots__ = ("_keyword", "_value")
    _attribute_nodes = ("_value",)

    def __init__(self, value, keyword=None):
        self._value = value
        self._keyword = keyword
        init_model_object(self)

    @property
    def value(self):
        """The value passed as argument"""
        return self._value

    @property
    def keyword(self):
        """The keyword used to pass the argument"""
        return self._keyword

    @property
    def has_keyword(self):
        """Indicates whether the argument was passed by keyword"""
        return self._keyword is not None

    def __repr__(self):
        if self.has_keyword:
            return f"FunctionCallArgument({self.keyword} = {self.value!r})"
        return f"FunctionCallArgument({self.value!r})"

    def __str__(self):
        if self.has_keyword:
            return f"{self.keyword} = {self.value}"
        return f"{self.value}"


class FunctionDefArgument:
    """
    model object describing the argument of a function.

    An object describing the argument of a function described
    by a FunctionDef. This object stores all the information
    which describes an argument but is superfluous for a Variable.

    Parameters
    ----------
    name : Symbol, Variable, FunctionAddress
        The name of the argument.

    value : model object, optional
        The default value of the argument.

    posonly : bool, default: False
        Indicates if the argument must be passed by position.

    kwonly : bool, default: False
        Indicates if the argument must be passed by keyword.

    annotation : str, optional
        The type annotation describing the argument.

    bound_argument : bool, default: False
        Indicates if the argument is the passed object bound to a method call.

    bound_argument_position : int, optional
        The position of the passed-object dummy in the native procedure
        signature before wrapper normalization.

    persistent_target : bool, default: False
        Indicates if the object passed as this argument becomes a target.
        This argument will usually only be passed by the wrapper.

    is_vararg : bool, default: False
        Indicates if the argument represents a variadic argument.

    is_kwarg : bool, default: False
        Indicates if the argument represents a set of keyword arguments.

    See Also
    --------
    FunctionDef : The class where these objects will be stored.

    Examples
    --------
    >>> from x2py.ast.core import FunctionDefArgument
    >>> n = FunctionDefArgument('n')
    >>> n
    n
    """

    __slots__ = (
        "_annotation",
        "_bound_argument",
        "_bound_argument_position",
        "_is_kwarg",
        "_is_vararg",
        "_kwonly",
        "_name",
        "_persistent_target",
        "_posonly",
        "_value",
        "_var",
        "_writable",
    )
    _attribute_nodes = ("_value", "_var")

    def __init__(
        self,
        name,
        *,
        value=None,
        posonly=False,
        kwonly=False,
        annotation=None,
        bound_argument=False,
        bound_argument_position=None,
        persistent_target=False,
        is_vararg=False,
        is_kwarg=False,
    ):
        if isinstance(name, Variable | FunctionAddress):
            self._var = name
            self._name = name.name
        elif isinstance(name, Symbol):
            self._var = name
            self._name = name
        else:
            raise TypeError("Name must be a Symbol, Variable or FunctionAddress")
        if not isinstance(bound_argument, bool):
            raise TypeError("bound_argument must be a boolean")
        if bound_argument_position is not None and not isinstance(bound_argument_position, int):
            raise TypeError("bound_argument_position must be an integer or None")
        if bound_argument_position is not None and not bound_argument:
            raise ValueError("bound_argument_position requires bound_argument=True")
        self._value = value
        self._posonly = posonly
        self._kwonly = kwonly
        self._annotation = annotation
        self._persistent_target = persistent_target
        self._bound_argument = bound_argument
        self._bound_argument_position = bound_argument_position
        self._is_vararg = is_vararg
        self._is_kwarg = is_kwarg

        if isinstance(name, Variable):
            name.declare_as_argument()

        if isinstance(self.var, Variable):
            self._writable = (
                (self.var.rank > 0 or isinstance(self.var.class_type, CustomDataType))
                and not isinstance(self.var.class_type, FinalType)
                and not isinstance(self.var.class_type, TupleType)
            )
        else:
            # If var is not a Variable it is a FunctionAddress
            self._writable = False

        init_model_object(self)

    @property
    def name(self):
        """The name of the argument"""
        return self._name

    @property
    def var(self):
        """The variable representing the argument
        (available after the semantic treatment)
        """
        return self._var

    @property
    def is_posonly(self):
        """
        Indicates if the argument must be passed by position.

        Indicates if the argument must be passed by position.
        """
        return self._posonly

    @property
    def is_kwonly(self):
        """
        Indicates if the argument must be passed by keyword.

        Indicates if the argument must be passed by keyword.
        """
        return self._kwonly

    @property
    def annotation(self):
        """
        The argument annotation providing dtype information.

        The argument annotation providing dtype information.
        """
        return self._annotation

    @property
    def value(self):
        """The default value of the argument"""
        return self._value

    @property
    def has_default(self):
        """Indicates whether the argument has a default value
        (if not then it must be provided)
        """
        return self._value is not None

    @property
    def writable(self):
        """
        Indicates whether the argument may be modified by the function.

        True if the argument may be modified in the function. False if
        the argument remains constant in the function.
        """
        return self._writable

    def make_const(self):
        """
        Indicate that the argument does not change in the function.

        Indicate that the argument does not change in the function by
        modifying the writable flag.
        """
        self._writable = False

    @property
    def persistent_target(self):
        """
        Indicate if the object passed as this argument becomes a target.

        Indicate if the object passed as this argument becomes a pointer target after
        a call to the function associated with this argument. This may be the case
        in class methods.
        """
        return self._persistent_target

    @persistent_target.setter
    def persistent_target(self, persistent_target):
        self._persistent_target = persistent_target

    @property
    def bound_argument(self):
        """
        Indicate if the argument is bound to the function call.

        Indicate if the argument is bound to the function call. This is
        the case if the argument is the first argument of a method of a
        class.
        """
        return self._bound_argument

    @property
    def bound_argument_position(self):
        """Position of the passed-object dummy in the native signature."""
        return self._bound_argument_position

    @bound_argument.setter
    def bound_argument(self, bound):
        if not isinstance(bound, bool):
            raise TypeError("bound must be a boolean")
        self._bound_argument = bound

    def __str__(self):
        name = str(self.name)
        if self.is_vararg:
            name = f"*{name}"
        if self.is_kwarg:
            name = f"**{name}"

        if self.has_default:
            return f"{name}={self.value}"
        return name

    def __repr__(self):
        name = repr(self.name)
        if self.is_vararg:
            name = f"*{name}"
        if self.is_kwarg:
            name = f"**{name}"

        if self.has_default:
            return f"FunctionDefArgument({name}={self.value})"
        return f"FunctionDefArgument({name})"

    @property
    def is_vararg(self):
        """
        True if the argument represents a variadic argument.

        True if the argument represents a variadic argument.
        """
        return self._is_vararg

    @property
    def is_kwarg(self):
        """
        True if the argument represents a set of keyword arguments.

        True if the argument represents a set of keyword arguments.
        """
        return self._is_kwarg


class FunctionDefResult:
    """
    model object describing the result of a function.

    An object describing the result of a function described
    by a FunctionDef. This object stores all the information
    which describes an result but is superfluous for a Variable.

    Parameters
    ----------
    var : Variable
        The variable which represents the returned value.

    annotation : str, default: None
        The type annotation describing the argument.

    See Also
    --------
    FunctionDef : The class where these objects will be stored.

    Examples
    --------
    >>> from x2py.ast.core import FunctionDefResult
    >>> n = FunctionDefResult('n')
    >>> n
    n
    """

    __slots__ = ("_annotation", "_is_argument", "_var")
    _attribute_nodes = ("_var",)

    def __init__(self, var, *, annotation=None):
        self._var = var
        self._annotation = annotation

        if not isinstance(var, Variable) and var is not NIL:
            raise TypeError(f"Var must be a Variable not a {type(var)}")
        self._is_argument = getattr(var, "is_argument", False)

        init_model_object(self)

    @property
    def var(self):
        """
        The variable representing the result.

        The variable which represents the result. This variable is only
        available after the semantic stage.
        """
        return self._var

    @property
    def annotation(self):
        """
        The result annotation providing dtype information.

        The annotation which provides all information about the data
        types, rank, etc, necessary to fully define the result.
        """
        return self._annotation

    @property
    def is_argument(self):
        """
        Indicates if the result was declared as an argument.

        Indicates if the result of the function was initially declared
        as an argument of the same function. If this is the case then
        the result may be printed simply as a writable argument.
        """
        return self._is_argument

    def __len__(self):
        return 0 if self.var is None else 1

    def __repr__(self):
        return f"FunctionDefResult({self.var!r})"

    def __str__(self):
        return str(self.var)

    def __bool__(self):
        return self.var is not NIL


class FunctionCall:
    """
    Represents a function call in the code.

    A node which holds all information necessary to represent a function
    call in the code.

    Parameters
    ----------
    func : FunctionDef
        The function being called.

    args : list of FunctionCallArgument
        The arguments passed to the function.

    current_function : FunctionDef, default: None
        The function where the call takes place.
    """

    __slots__ = (
        "_arguments",
        "_class_type",
        "_func_name",
        "_funcdef",
        "_overload_set",
        "_overload_set_name",
        "_shape",
    )
    _attribute_nodes = ("_arguments", "_funcdef", "_overload_set")

    def __init__(self, func, args, current_function=None):
        for a in args:
            assert not isinstance(a, FunctionDefArgument)
        # Ensure all arguments are of type FunctionCallArgument
        args = [a if isinstance(a, FunctionCallArgument) else FunctionCallArgument(a) for a in args]

        # ...
        if not isinstance(func, FunctionDef | FunctionOverloadSet):
            raise TypeError("> expecting a FunctionDef or an FunctionOverloadSet")

        if isinstance(func, FunctionOverloadSet):
            self._overload_set = func
            self._overload_set_name = func.name
            func = func.point(args)
        else:
            self._overload_set = None

        name = func.name
        # ...
        if current_function == name:
            func.set_recursive()

        if not isinstance(args, tuple | list):
            raise TypeError("args must be a list or tuple")

        # add the missing argument in the case of optional arguments
        f_args = func.arguments
        if len(args) != len(f_args):
            # Collect dict of keywords and values (initialised as default)
            f_args_dict = {a.name: (a.name, a.value) if a.has_default else None for a in f_args}
            keyword_args = []
            for i, a in enumerate(args):
                if a.keyword is None:
                    # Replace default positional arguments with provided arguments
                    f_args_dict[f_args[i].name] = a
                else:
                    keyword_args = args[i:]
                    break

            for a in keyword_args:
                # Replace default arguments with provided keyword arguments
                f_args_dict[a.keyword] = a

            args = [
                (FunctionCallArgument(keyword=a[0], value=a[1]) if isinstance(a, tuple) else a)
                for a in f_args_dict.values()
            ]

        # Handle function as argument
        arg_vals = [None if a is None else a.value for a in args]
        args = [
            (
                FunctionCallArgument(
                    FunctionAddress(av.name, av.arguments, av.results, scope=av.scope),
                    keyword=a.keyword,
                )
                if isinstance(av, FunctionDef)
                else a
            )
            for a, av in zip(args, arg_vals, strict=False)
        ]

        if current_function == func.name and len(func.results) > 0 and not is_model_object(func.results):
            raise RuntimeError("Recursive functions with results must declare a result variable.")

        self._funcdef = func
        self._arguments = args
        self._func_name = func.name
        self._shape = func.results.var.shape
        self._class_type = func.results.var.class_type

        init_model_object(self)

    @property
    def args(self):
        """List of FunctionCallArguments provided to the function call
        (contains default values after semantic stage)
        """
        return self._arguments

    @property
    def funcdef(self):
        """The function called by this function call"""
        return self._funcdef

    @property
    def overload_set(self):
        """The interface called by this function call"""
        return self._overload_set

    @property
    def func_name(self):
        """The name of the function called by this function call"""
        return self._func_name

    @property
    def overload_set_name(self):
        """The name of the interface called by this function call"""
        return self._overload_set_name

    @property
    def is_alias(self):
        """
        Check if the result of the function call is an alias type.

        Check if the result of the function call is an alias type.
        """
        assert len(self._funcdef.results) == 1
        return self._funcdef.results.var.is_alias

    def __repr__(self):
        args = ", ".join(str(a) for a in self.args)
        return f"{self.func_name}({args})"


class Return:
    """
    Represents a return statement in a function in the code.

    Represents a return statement in a function in the code.

    Parameters
    ----------
    expr : model object
        The expression to return.

    stmt : model object
        Any assign statements in the case of expression return.
    """

    __slots__ = ("_expr", "_n_returns", "_stmt")
    _attribute_nodes = ("_expr", "_stmt")

    def __init__(self, expr, stmt=None):
        assert stmt is None or isinstance(stmt, CodeBlock)
        assert expr is None or is_model_object(expr) or isinstance(expr, Symbol)

        self._expr = expr
        self._stmt = stmt

        self._n_returns = 0 if expr is NIL else 1 if not hasattr(expr, "__iter__") else len(expr)

        init_model_object(self)

    @property
    def expr(self):
        return self._expr

    @property
    def stmt(self):
        return self._stmt

    def __repr__(self):
        code = repr(self.stmt) + ";" if self.stmt else ""
        return code + f"Return({self.expr!r})"


class FunctionDef:
    """
    Represents a function definition.

    model object containing all the information necessary to describe a function.
    This information should provide enough information to print a functionally
    equivalent function in any target language.

    Parameters
    ----------
    name : str
        The name of the function.

    arguments : iterable of FunctionDefArgument
        The arguments to the function.

    body : iterable
        The body of the function.

    results : FunctionDefResult, optional
        The direct outputs of the function.

    global_vars : list of Symbols
        Variables which will not be passed into the function.

    cls_name : str
        The alternative name of the function required for classes.

    is_static : bool
        True for static functions. Needed for iso_c_binding interface.

    imports : list, tuple
        A list of needed imports.

    decorators : dict
        A dictionary whose keys are the names of decorators and whose values
        contain their implementation.

    headers : list,tuple
        A list of headers describing the function.

    is_recursive : bool
        True for a function which calls itself.

    is_pure : bool
        True for a function without side effect.

    is_elemental : bool
        True for a function that is elemental.

    is_private : bool
        True for a function that is private.

    is_header : bool
        True for a function which has no body available.

    is_external : bool
        True for a function which cannot be explicitly imported or renamed.

    is_imported : bool, default : False
        True for a function that is imported.

    functions : list, tuple
        A list of functions defined within this function.

    overload_sets : list, tuple
        A list of overload_sets defined within this function.

    result_pointer_map : dict[FunctionDefResult, list[int]]
        A dictionary connecting any pointer results to the index of the possible target arguments.

    docstring : str
        The doc string of the function.

    bind_c_external_name : str, optional
        Existing Fortran ``bind(C, name=...)`` symbol that may be called
        directly when its ABI is safe.

    type_bound_name : str, optional
        Native Fortran type-bound binding name used when dispatching through a
        passed-object argument.

    scope : parser.scope.Scope
        The scope containing all objects scoped to the inside of this function.

    See Also
    --------
    FunctionDefArgument : The type used to store the arguments.

    Examples
    --------
    >>> from x2py.ast.variable import Variable
    >>> from x2py.ast.core import FunctionDefArgument, FunctionDefResult
    >>> from x2py.ast.core import Assign, FunctionDef
    >>> from x2py.ast.operators import Add
    >>> from x2py.codegen.models.datatypes import convert_to_literal
    >>> x = Variable(NumpyFloat64Type(), 'x')
    >>> y = Variable(NumpyFloat64Type(), 'y')
    >>> args        = [FunctionDefArgument(x)]
    >>> results     = [FunctionDefResult(y)]
    >>> body        = [Assign(y,Add(x,convert_to_literal(1)))]
    >>> FunctionDef('incr', args, results, body)
    FunctionDef(incr, (x,), (y,), [y := x + 1], [], [], None, False, function)

    One can also use parametrized argument, using FunctionDefArgument

    >>> from x2py.ast.core import Variable
    >>> from x2py.ast.core import Assign
    >>> from x2py.ast.core import FunctionDef
    >>> from x2py.ast.core import FunctionDefArgument
    >>> n = FunctionDefArgument('n', value=4)
    >>> x = Variable(NumpyFloat64Type(), 'x')
    >>> y = Variable(NumpyFloat64Type(), 'y')
    >>> args        = [x, n]
    >>> results     = [y]
    >>> body        = [Assign(y,x+n)]
    >>> FunctionDef('incr', args, results, body)
    FunctionDef(incr, (x, n=4), (y,), [y := 1 + x], [], [], None, False, function, [])
    """

    __slots__ = (
        "_arguments",
        "_bind_c_external_name",
        "_body",
        "_cls_name",
        "_decorators",
        "_docstring",
        "_functions",
        "_global_vars",
        "_headers",
        "_imports",
        "_is_elemental",
        "_is_external",
        "_is_header",
        "_is_imported",
        "_is_private",
        "_is_pure",
        "_is_recursive",
        "_is_semantic",
        "_is_static",
        "_name",
        "_overload_sets",
        "_result_pointer_map",
        "_results",
        "_type_bound_name",
    )

    _attribute_nodes = (
        "_arguments",
        "_results",
        "_body",
        "_global_vars",
        "_imports",
        "_functions",
        "_overload_sets",
    )

    def __init__(
        self,
        name,
        arguments,
        body,
        results=None,
        *,
        global_vars=(),
        cls_name=None,
        is_static=False,
        imports=(),
        decorators=None,
        headers=(),
        is_recursive=False,
        is_pure=False,
        is_elemental=False,
        is_private=False,
        is_header=False,
        is_external=False,
        is_imported=False,
        functions=(),
        overload_sets=(),
        result_pointer_map=None,
        docstring=None,
        bind_c_external_name=None,
        type_bound_name=None,
        scope=None,
    ):
        if result_pointer_map is None:
            result_pointer_map = {}
        if decorators is None:
            decorators = {}
        if isinstance(name, str):
            name = Symbol(name)
        elif isinstance(name, tuple | list):
            name_ = []
            for i in name:
                if isinstance(i, str):
                    name_.append(Symbol(i))
                else:
                    raise TypeError("Function name must be Symbol or string")
            name = tuple(name_)
        else:
            raise TypeError("Function name must be Symbol or string")

        # arguments

        if not iterable(arguments):
            raise TypeError("arguments must be an iterable")
        if not all(isinstance(a, FunctionDefArgument) for a in arguments):
            raise TypeError("arguments must be all be FunctionDefArguments")

        [a.var for a in arguments]

        # body

        if iterable(body):
            body = CodeBlock(body)
        assert isinstance(body, CodeBlock)

        # results
        if results is None:
            results = FunctionDefResult(NIL)
        assert isinstance(results, FunctionDefResult)

        if cls_name and not isinstance(cls_name, str):
            raise TypeError("cls_name must be a string")

        if not isinstance(is_static, bool):
            raise TypeError("Expecting a boolean for is_static attribute")

        if not iterable(imports):
            raise TypeError("imports must be an iterable")

        if not isinstance(decorators, dict):
            raise TypeError("decorators must be a dict")

        if not isinstance(is_pure, bool):
            raise TypeError("Expecting a boolean for pure")

        if not isinstance(is_elemental, bool):
            raise TypeError("Expecting a boolean for elemental")

        if not isinstance(is_private, bool):
            raise TypeError("Expecting a boolean for private")

        if not isinstance(is_header, bool):
            raise TypeError("Expecting a boolean for header")

        if functions:
            for i in functions:
                if not isinstance(i, FunctionDef):
                    raise TypeError("Expecting a FunctionDef")

        self._name = name
        self._arguments = arguments
        self._results = results
        self._body = body
        self._global_vars = global_vars
        self._cls_name = cls_name
        self._is_static = is_static
        self._imports = imports
        self._decorators = decorators
        self._headers = headers
        self._is_recursive = is_recursive
        self._is_pure = is_pure
        self._is_elemental = is_elemental
        self._is_private = is_private
        self._is_header = is_header
        self._is_external = is_external
        self._is_imported = is_imported
        self._functions = functions
        self._overload_sets = overload_sets
        self._result_pointer_map = result_pointer_map
        self._docstring = docstring
        self._bind_c_external_name = bind_c_external_name
        self._type_bound_name = type_bound_name
        init_model_object(self, scope=scope)
        self._is_semantic = True

    @property
    def name(self):
        """Name of the function"""
        return self._name

    @property
    def arguments(self):
        """List of variables which are the function arguments"""
        return self._arguments

    @property
    def results(self):
        """List of variables which are the function results"""
        return self._results

    @property
    def body(self):
        """
        CodeBlock containing all the statements in the function.

        Return a CodeBlock containing all the statements in the function.
        """
        return self._body

    @body.setter
    def body(self, body):
        if iterable(body):
            body = CodeBlock(body)
        elif not isinstance(body, CodeBlock):
            raise TypeError("body must be an iterable or a CodeBlock")
        detach_model_child(self, self._body)
        self._body = body
        attach_model_child(self, self._body)

    @property
    def local_vars(self):
        """
        List of variables defined in the function.

        A list of all variables which are local to the function. This
        includes arguments, results, and variables defined inside the
        function.
        """
        scope = self.scope
        local_vars = scope.variables.values()
        result_vars = [self.results.var]
        return tuple(
            local_var for local_var in local_vars if local_var not in result_vars and not local_var.is_argument
        )

    @property
    def global_vars(self):
        """List of global variables used in the function"""
        return self._global_vars

    @property
    def cls_name(self):
        """
        String containing an alternative name for the function if it is a class method.

        If a function is a class method then in some languages an alternative name is
        required. For example in Fortran a name is required for the definition of the
        class in the module. This name is different from the name of the method which
        is used when calling the function via the class variable.
        """
        return self._cls_name

    @cls_name.setter
    def cls_name(self, cls_name):
        self._cls_name = cls_name

    @property
    def type_bound_name(self):
        """Native Fortran binding name used for type-bound dispatch."""
        return self._type_bound_name

    @property
    def imports(self):
        """List of imports in the function"""
        return self._imports

    @property
    def decorators(self):
        """List of decorators applied to the function"""
        return self._decorators

    @property
    def headers(self):
        """List of headers applied to the function"""
        return self._headers

    @property
    def is_recursive(self):
        """Returns True if the function is recursive (i.e. calls itself)
        and False otherwise"""
        return self._is_recursive

    @property
    def is_pure(self):
        """Returns True if the function is marked as pure and False otherwise
        Pure functions must not have any side effects.
        In other words this means that the result must be the same no matter
        how many times the function is called
        e.g:
        >>> a = f()
        >>> a = f()

        gives the same result as
        >>> a = f()

        This is notably not true for I/O functions
        """
        return self._is_pure

    @property
    def is_elemental(self):
        """returns True if the function is marked as elemental and
        False otherwise
        An elemental function is a function with a single scalar operator
        and a scalar return value which can also be called on an array.
        When it is called on an array it returns the result of the function
        called elementwise on the array"""
        return self._is_elemental

    @property
    def is_private(self):
        """True if the function should not be exposed to
        other modules. This includes the wrapper module and
        means that the function cannot be used in an import
        or exposed to python"""
        return self._is_private

    @property
    def is_header(self):
        """True if the implementation of the function body
        is not provided False otherwise"""
        return self._is_header

    @property
    def is_external(self):
        """
        Indicates if the function is from an external library.

        Indicates if the function is from an external library which has no
        associated imports. Such functions must be declared locally to
        satisfy the compiler. For example this method returns True if the
        function is exposed through a pyi file and describes a method from
        a f77 module.
        """
        return self._is_external

    @is_external.setter
    def is_external(self, is_external):
        assert isinstance(is_external, bool)
        self._is_external = is_external

    @property
    def is_imported(self):
        """
        Indicates if the function was imported from another file.

        Indicates if the function was imported from another file.
        """
        return self._is_imported

    @property
    def is_inline(self):
        """True if the function should be printed inline"""
        return False

    @property
    def is_static(self):
        """
        Indicates if the function is static.

        Indicates if the function is static.
        """
        return self._is_static

    @property
    def is_semantic(self):
        """
        Indicates if the function was created with semantic information.

        Indicates if the function has been annotated with type descriptors
        in the semantic stage.
        """
        return self._is_semantic

    @property
    def functions(self):
        """List of functions within this function"""
        return self._functions

    @property
    def overload_sets(self):
        """List of overload_sets within this function"""
        return self._overload_sets

    @property
    def docstring(self):
        """
        The docstring of the function.

        The docstring of the function.
        """
        return self._docstring

    @property
    def bind_c_external_name(self):
        """Existing Fortran ``bind(C)`` external symbol for direct C calls."""
        return self._bind_c_external_name

    def set_recursive(self):
        """Mark the function as a recursive function"""
        self._is_recursive = True

    def clone(self, newname, **new_kwargs):
        """
        Create an almost identical FunctionDef with name `newname`.

        Create an almost identical FunctionDef with name `newname`.
        Additional parameters can be passed to alter the resulting
        FunctionDef.

        Parameters
        ----------
        newname : str
            New name for the FunctionDef.

        **new_kwargs : dict
            Any new keyword arguments to be passed to the new FunctionDef.

        Returns
        -------
        FunctionDef
            The clone of the function definition.
        """
        args, kwargs = self.__getnewargs_ex__()
        kwargs.update(new_kwargs)
        cls = type(self)

        args = (newname, *args[1:])
        return cls(*args, **kwargs)

    def __getnewargs_ex__(self):
        """
        This method returns the positional and keyword arguments used to create
        an instance of this class. This is used by clone and can be used for pickling.
        See https://docs.python.org/3/library/pickle.html#object.__getnewargs_ex__
        """
        args = (self._name, self._arguments, self._body)

        kwargs = {
            "results": self._results,
            "global_vars": self._global_vars,
            "cls_name": self._cls_name,
            "is_static": self._is_static,
            "imports": self._imports,
            "decorators": self._decorators,
            "headers": self._headers,
            "is_recursive": self._is_recursive,
            "is_pure": self._is_pure,
            "is_elemental": self._is_elemental,
            "is_private": self._is_private,
            "is_header": self._is_header,
            "functions": self._functions,
            "is_external": self._is_external,
            "is_imported": self._is_imported,
            "overload_sets": self._overload_sets,
            "docstring": self._docstring,
            "bind_c_external_name": self._bind_c_external_name,
            "type_bound_name": self._type_bound_name,
            "scope": self._scope,
        }
        return args, kwargs

    def __str__(self):
        args = ", ".join(str(a) for a in self.arguments)
        return f"{self.name}({args}) -> {self.results}"

    @property
    def result_pointer_map(self):
        """
        A dictionary connecting any pointer results to the index of the possible target arguments.

        A dictionary whose keys are FunctionDefResult objects and whose values are a list of
        integers. The integers specify the position of the argument which is a target of the
        FunctionDefResult.
        """
        return self._result_pointer_map

    def __call__(self, *args, **kwargs):
        arguments = [a if isinstance(a, FunctionCallArgument) else FunctionCallArgument(a) for a in args]
        arguments += [FunctionCallArgument(a, keyword=key) for key, a in kwargs.items()]
        return FunctionCall(self, arguments)


class FunctionOverloadSet:
    """
    Class representing an interface function.

    A class representing an interface function. An interface function represents
    a Python function which accepts multiple types. In low-level languages this
    is a collection of functions.

    Parameters
    ----------
    name : str
        The name of the interface function.

    functions : iterable
        The internal functions that can be accessed via the interface.

    is_argument : bool
        True if the interface is used for a function argument.

    is_imported : bool
        True if the interface is imported from another file.

    syntactic_node : FunctionDef, default: None
        The syntactic node that is not annotated.

    Examples
    --------
    >>> from x2py.ast.core import FunctionOverloadSet, FunctionDef
    >>> f = FunctionDef('F', [], [], [])
    >>> FunctionOverloadSet('I', [f])
    """

    __slots__ = (
        "_functions",
        "_is_argument",
        "_is_imported",
        "_name",
        "_native_name",
        "_native_names",
        "_syntactic_node",
    )
    _attribute_nodes = ("_functions",)

    def __init__(
        self,
        name,
        functions,
        is_argument=False,
        is_imported=False,
        native_name=None,
        native_names=None,
        syntactic_node=None,
    ):
        if not isinstance(name, str):
            raise TypeError("Expecting an str")

        assert iterable(functions)
        functions = tuple(functions)
        if not functions:
            raise ValueError(f"Function overload set {name!r} must contain at least one function")
        if not all(isinstance(function, FunctionDef) for function in functions):
            raise TypeError("Function overload set entries must be FunctionDef instances")
        if type(self) is FunctionOverloadSet:
            source_functions = tuple(getattr(function, "original_function", function) for function in functions)
            self._validate_dispatch_signatures(name, source_functions)

        self._name = name
        if native_names is None:
            native_names = (native_name or name,) * len(functions)
        else:
            native_names = tuple(native_names)
            if len(native_names) != len(functions):
                raise ValueError("Function overload set native names must align with its functions")
        self._native_names = native_names
        self._native_name = native_name or (native_names[0] if len(set(native_names)) == 1 else name)
        self._functions = functions
        self._is_argument = is_argument
        self._is_imported = is_imported
        self._syntactic_node = syntactic_node
        init_model_object(self)

    @property
    def name(self):
        """Name of the interface."""
        return self._name

    @property
    def native_name(self):
        """Native generic name used by the source-language bridge."""
        return self._native_name

    @property
    def native_names(self):
        """Native generic name for each concrete overload candidate."""
        return self._native_names

    def native_name_for(self, function):
        """Return the native generic name associated with one candidate."""
        return self._native_names[self._functions.index(function)]

    @property
    def functions(self):
        """ "Functions of the interface."""
        return self._functions

    @property
    def arguments(self):
        """Arguments shared by every overload as seen by the generated wrapper."""
        return self._functions[0].arguments

    @staticmethod
    def _dispatch_arguments(function, *, include_bound=False):
        arguments = list(function.arguments)
        if not include_bound and arguments and arguments[0].bound_argument:
            return arguments[1:]
        return arguments

    @classmethod
    def _validate_dispatch_signatures(cls, name, functions):
        call_shapes = []
        dispatch_keys = []
        for function in functions:
            arguments = cls._dispatch_arguments(function, include_bound=name.startswith("__"))
            call_shapes.append(
                tuple(
                    (
                        argument.has_default,
                        argument.is_kwonly,
                        argument.is_vararg,
                        argument.is_kwarg,
                    )
                    for argument in arguments
                )
            )
            dispatch_keys.append(tuple((argument.var.class_type, argument.var.rank) for argument in arguments))

        if any(shape != call_shapes[0] for shape in call_shapes[1:]):
            raise ValueError(f"Function overload set {name!r} has incompatible Python call signatures")
        seen = set()
        for function, key in zip(functions, dispatch_keys, strict=True):
            if key in seen:
                raise ValueError(f"Function overload set {name!r} has indistinguishable overload {function.name!s}")
            seen.add(key)

    @property
    def is_argument(self):
        """True if the interface is used for a function argument."""
        return self._is_argument

    @property
    def is_imported(self):
        """
        Indicates if the function was imported from another file.

        Indicates if the function was imported from another file.
        """
        return self._is_imported

    @property
    def syntactic_node(self):
        """
        The syntactic node that is not annotated.

        The syntactic node that is not annotated.
        """
        return self._syntactic_node

    @property
    def docstring(self):
        """
        The docstring of the function.

        The docstring of the interface function.
        """
        return self._functions[0].docstring

    @property
    def is_semantic(self):
        """
        Flag to check if the node is annotated.

        Flag to check if the node has been annotated with type descriptors
        in the semantic stage.
        """
        return self._functions[0].is_semantic

    @property
    def is_inline(self):
        """
        Flag to check if the node is inlined.

        Flag to check if the node is inlined.
        """
        return self._functions[0].is_inline

    @property
    def is_private(self):
        """
        Indicates if the interface function is private.

        Indicates if the interface function is private.
        """
        return self._functions[0].is_private

    def rename(self, newname):
        """
        Rename the FunctionOverloadSet name to a newname.

        Rename the FunctionOverloadSet name to a newname.

        Parameters
        ----------
        newname : str
            New name for the FunctionOverloadSet.
        """

        self._name = newname

    def clone(self, newname, **new_kwargs):
        """
        Create an almost identical FunctionOverloadSet with name `newname`.

        Create an almost identical FunctionOverloadSet with name `newname`.
        Additional parameters can be passed to alter the resulting
        FunctionDef.

        Parameters
        ----------
        newname : str
            New name for the FunctionOverloadSet.

        **new_kwargs : dict
            Any new keyword arguments to be passed to the new FunctionOverloadSet.

        Returns
        -------
        FunctionOverloadSet
            The clone of the interface.
        """

        args, kwargs = self.__getnewargs_ex__()
        kwargs.update(new_kwargs)
        cls = type(self)
        new_func = cls(*args, **kwargs)
        new_func.rename(newname)
        return new_func

    def __getnewargs_ex__(self):
        """
        This method returns the positional and keyword arguments used to create
        an instance of this class. This is used by clone and can be used for pickling.
        See https://docs.python.org/3/library/pickle.html#object.__getnewargs_ex__
        """
        args = (self._name, self._functions)

        kwargs = {
            "is_argument": self._is_argument,
            "is_imported": self._is_imported,
            "native_name": self._native_name,
            "native_names": self._native_names,
            "syntactic_node": self._syntactic_node,
        }
        return args, kwargs

    def point(self, args):
        """
        Return the actual function that will be called, depending on the passed arguments.

        From the arguments passed in the function call, determine which of the FunctionDef
        objects in the FunctionOverloadSet is actually called.

        Parameters
        ----------
        args : tuple[model object]
            The arguments passed in the function call.

        Returns
        -------
        FunctionDef
            The function definition which corresponds with the arguments.
        """

        def type_match(call_arg, func_arg):
            """
            Check that the types of the arguments in the function and the call match.
            """
            return call_arg.class_type == func_arg.class_type and (call_arg.rank == func_arg.rank)

        matches = []
        for function in self._functions:
            function_args = list(function.arguments)
            if len(args) != len(function_args):
                continue
            if all(
                type_match(call_arg.value, func_arg.var) for call_arg, func_arg in zip(args, function_args, strict=True)
            ):
                matches.append(function)

        if not matches:
            raise TypeError(f"Arguments types provided to {self.name} are incompatible")
        if len(matches) > 1:
            names = ", ".join(str(function.name) for function in matches)
            raise TypeError(f"Arguments provided to {self.name} match multiple overloads: {names}")
        return matches[0]

    @staticmethod
    def native_arguments(function, args):
        """Restore the native argument order after Python method binding."""
        native_args = list(args)
        if not function.arguments or not function.arguments[0].bound_argument:
            return native_args
        position = function.arguments[0].bound_argument_position
        if position in {None, 0}:
            return native_args
        bound_arg = native_args.pop(0)
        native_args.insert(position, bound_arg)
        return native_args

    def __call__(self, *args, **kwargs):
        arguments = [a if isinstance(a, FunctionCallArgument) else FunctionCallArgument(a) for a in args]
        arguments += [FunctionCallArgument(a, keyword=key) for key, a in kwargs.items()]
        return FunctionCall(self, arguments)


class FunctionAddress(FunctionDef):
    """
    Represents a function address.

    A function definition can have a FunctionAddress as an argument.

    Parameters
    ----------
    name : str
        The name of the function address.

    arguments : iterable
        The arguments to the function address.

    results : iterable
        The direct outputs of the function address.

    is_optional : bool
        If object is an optional argument of a function [Default value: False].

    is_kwonly : bool
        If object is an argument which can only be specified using its keyword.

    is_argument : bool
        If object is the argument of a function [Default value: False].

    memory_handling : str
        Must be 'heap', 'stack' or 'alias' [Default value: 'stack'].

    **kwargs : dict
        Any keyword arguments which should be passed to the super class FunctionDef.

    See Also
    --------
    FunctionDef
        The super class from which this object derives.

    Examples
    --------
    >>> from x2py.ast.core import Variable, FunctionAddress, FunctionDef
    >>> x = Variable(NumpyFloat64Type(), 'x')
    >>> y = Variable(NumpyFloat64Type(), 'y')
    >>> # a function definition can have a FunctionAddress as an argument
    >>> FunctionDef('g', [FunctionAddress('f', [x], [y])], [], [])
    """

    __slots__ = ("_is_argument", "_is_kwonly", "_is_optional", "_memory_handling")

    def __init__(
        self,
        name,
        arguments,
        results,
        is_optional=False,
        is_kwonly=False,
        is_argument=False,
        memory_handling="stack",
        **kwargs,
    ):
        super().__init__(name, arguments, body=[], results=results, **kwargs)
        if not isinstance(is_argument, bool):
            raise TypeError("Expecting a boolean for is_argument")

        if memory_handling not in ("heap", "alias", "stack"):
            raise TypeError("Expecting 'heap', 'stack', 'alias' or None for memory_handling")

        if not isinstance(is_kwonly, bool):
            raise TypeError("Expecting a boolean for kwonly")

        if not isinstance(is_optional, bool):
            raise TypeError("is_optional must be a boolean.")

        self._is_optional = is_optional
        self._is_kwonly = is_kwonly
        self._is_argument = is_argument
        self._memory_handling = memory_handling

    @property
    def name(self):
        return self._name

    @property
    def memory_handling(self):
        """Returns the memory handling of the instance of FunctionAddress"""
        return self._memory_handling

    @property
    def is_alias(self):
        """Indicates if the instance of FunctionAddress is an alias"""
        return self.memory_handling == "alias"

    @property
    def is_argument(self):
        return self._is_argument

    @property
    def is_kwonly(self):
        return self._is_kwonly

    @property
    def is_optional(self):
        return self._is_optional

    def __getnewargs_ex__(self):
        """
        This method returns the positional and keyword arguments used to create
        an instance of this class. This is used by clone and can be used for pickling.
        See https://docs.python.org/3/library/pickle.html#object.__getnewargs_ex__
        """
        args, kwargs = super().__getnewargs_ex__()
        args = args[:-1]  # Remove body argument
        kwargs["is_argument"] = self.is_argument
        kwargs["is_kwonly"] = self.is_kwonly
        kwargs["is_optional"] = self.is_optional
        kwargs["memory_handling"] = self.memory_handling
        return args, kwargs


class ClassDef:
    """
    Represents a class definition.

    Class representing a class definition in the code. It holds all objects
    which may be defined in a class including methods, overload_sets, attributes,
    etc. It also handles inheritance.

    Parameters
    ----------
    name : str
        The name of the class.

    attributes : iterable
        The attributes to the class.

    methods : iterable
        Class methods.

    imports : list, tuple
        A list of required imports.

    superclasses : iterable
        The definition of all classes from which this class inherits.

    overload_sets : iterable
        The interface methods.

    docstring : CommentBlock, optional
        The doc string of the class.

    scope : Scope
        The scope for the class contents.

    class_type : Type
        The data type associated with this class.

    decorators : dict
        A dictionary whose keys are the names of decorators and whose values
        contain their implementation.

    Examples
    --------
    >>> from x2py.ast.core import Variable, Assign
    >>> from x2py.ast.core import ClassDef, FunctionDef
    >>> x = Variable(NumpyFloat64Type(), 'x')
    >>> y = Variable(NumpyFloat64Type(), 'y')
    >>> z = Variable(NumpyFloat64Type(), 'z')
    >>> t = Variable(NumpyFloat64Type(), 't')
    >>> a = Variable(NumpyFloat64Type(), 'a')
    >>> b = Variable(NumpyFloat64Type(), 'b')
    >>> body = [Assign(y,x+a)]
    >>> translate = FunctionDef('translate', [x,y,a,b], [z,t], body)
    >>> attributes   = [x,y]
    >>> methods     = [translate]
    >>> ClassDef('Point', attributes, methods)
    ClassDef(Point, (x, y), (FunctionDef(translate, (x, y, a, b), (z, t), [y := a + x], [], [], None, False, function),), [public])
    """

    __slots__ = (
        "_attributes",
        "_class_type",
        "_decorators",
        "_docstring",
        "_imports",
        "_methods",
        "_name",
        "_overload_sets",
        "_superclasses",
    )
    _attribute_nodes = (
        "_attributes",
        "_methods",
        "_imports",
        "_overload_sets",
        "_docstring",
    )

    def __init__(
        self,
        name,
        attributes=(),
        methods=(),
        imports=(),
        superclasses=(),
        overload_sets=(),
        docstring=None,
        scope=None,
        class_type=None,
        decorators=(),
    ):
        # name

        if isinstance(name, str):
            name = Symbol(name)
        else:
            raise TypeError("Class name must be Symbol or string")

        # attributes

        if not iterable(attributes):
            raise TypeError("attributes must be an iterable")
        attributes = tuple(attributes)

        # methods

        if not iterable(methods):
            raise TypeError("methods must be an iterable")

        # imports

        if not iterable(imports):
            raise TypeError("imports must be an iterable")

        if not iterable(superclasses):
            raise TypeError("superclasses must be iterable")

        for s in superclasses:
            if not isinstance(s, ClassDef):
                raise TypeError("superclass item must be a ClassDef")

            if not isinstance(class_type, Type):
                raise TypeError("class_type must be a Type")

        if not iterable(overload_sets):
            raise TypeError("overload_sets must be iterable")

        imports = list(imports)
        for i in methods:
            imports += list(i.imports)

        imports = set(imports)  # for unicity
        imports = tuple(imports)

        methods = tuple(methods)

        # ...
        self._name = name
        self._attributes = attributes
        self._methods = methods
        self._imports = imports
        self._superclasses = superclasses
        self._overload_sets = overload_sets
        self._docstring = docstring
        self._class_type = class_type
        self._decorators = decorators

        init_model_object(self, scope=scope)

    @property
    def name(self):
        """
        The name of the class.

        The name of the class.
        """
        return self._name

    @property
    def class_type(self):
        """
        The Type of an object of the described class.

        The Type of an object of the described class.
        """
        return self._class_type

    @property
    def attributes(self):
        """
        The attributes of a class.

        Returns a tuple containing the attributes of a ClassDef.
        Each element within the tuple is of type Variable.
        """
        return self._attributes

    @property
    def methods(self):
        return self._methods

    @property
    def imports(self):
        return self._imports

    @property
    def superclasses(self):
        """
        Get the superclasses.

        Get the class definitions for the classes from which this class
        inherits.
        """
        return self._superclasses

    @property
    def overload_sets(self):
        return self._overload_sets

    @property
    def docstring(self):
        """
        The docstring of the class.

        The docstring of the class.
        """
        return self._docstring

    @property
    def decorators(self):
        """
        Dictionary mapping decorator names to descriptions.

        Dictionary mapping the names of decorators applied to the function
        to descriptions of the decorator annotation.
        """
        return self._decorators

    @property
    def methods_as_dict(self):
        """
        A dictionary containing all methods with Python names as keys.

        A dictionary containing all the methods in the class. The keys are the original
        Python names of the methods. The values are the methods themselves.
        """
        return {self.scope.get_python_name(m.name) if m.is_semantic else m.name: m for m in self.methods}

    def add_new_method(self, method):
        """
        Add a new method to the current class.

        Add a new method to the current ClassDef.

        Parameters
        ----------
        method : FunctionDef
            The Method that will be added.
        """

        if not isinstance(method, FunctionDef):
            raise TypeError("Method must be FunctionDef")

        attach_model_child(self, method)
        self._methods += (method,)

    def add_new_overload_set(self, overload_set):
        """
        Add a new interface to the current class.

        Add a new interface to the current ClassDef.

        Parameters
        ----------
        interface : FunctionDef
            The interface that will be added.
        """

        if not isinstance(overload_set, FunctionOverloadSet):
            raise TypeError("Argument 'overload_set' must be of type FunctionOverloadSet")
        attach_model_child(self, overload_set)
        self._overload_sets += (overload_set,)

    def get_method(self, name, raise_error_from=None):
        """
        Get the method `name` of the current class.

        Look through all methods and overload_sets of the current class to
        find a method called `name`. If this class inherits from another
        class, that class is also searched to ensure that the inherited
        methods are available.

        Parameters
        ----------
        name : str
            The name of the attribute we are looking for.

        raise_error_from : model object, optional
            If an error should be raised then this variable should contain
            the node that the error should be raised from. This allows the
            correct, line/column error information to be reported.

        Returns
        -------
        FunctionDef
            The definition of the method.

        Raises
        ------
        ValueError
            Raised if the method cannot be found.
        """

        if self.scope is not None:
            # Collect translated name from scope
            try:
                name = self.scope.get_expected_name(name)
            except RuntimeError as error:
                if raise_error_from:
                    raise AttributeError(f"Can't find method {name} in class {self.name}") from error
                return None

        try:
            method = next(i for i in chain(self.methods, self.overload_sets) if i.name == name)
        except StopIteration:
            method = None
            i = 0
            n_classes = len(self.superclasses)
            while method is None and i < n_classes:
                try:
                    method = self.superclasses[i].get_method(name, raise_error_from)
                except StopIteration:
                    method = None
                i += 1

        if method is None and raise_error_from:
            raise AttributeError(f"Can't find method {name} in class {self.name}")

        return method

    @property
    def is_iterable(self):
        """Returns True if the class has an iterator."""

        names = [str(m.name) for m in self.methods]
        if "__next__" in names and "__iter__" in names:
            return True
        if "__next__" in names:
            raise ValueError("ClassDef does not contain __iter__ method")
        if "__iter__" in names:
            raise ValueError("ClassDef does not contain __next__ method")
        return False

    @property
    def is_with_construct(self):
        """Returns True if the class is a with construct."""

        names = [str(m.name) for m in self.methods]
        if "__enter__" in names and "__exit__" in names:
            return True
        if "__enter__" in names:
            raise ValueError("ClassDef does not contain __exit__ method")
        if "__exit__" in names:
            raise ValueError("ClassDef does not contain __enter__ method")
        return False


class Import:
    """
    Represents inclusion of dependencies in the code.

    Represents the importation of targets from another source code. This is
    usually used to represent an import statement in the original code but
    it is also used to import language/library specific dependencies.

    Parameters
    ----------
    source : str, AsName
        The module from which we import.
    target : str, AsName, list, tuple
        Targets to import.
    ignore_at_print : bool
        Indicates whether the import should be printed.
    mod : Module
        The module describing the source.

    Examples
    --------
    >>> from x2py.ast.core import Import
    >>> Import('foo')
    import foo

    >>> Import('foo', 'bar')
    from foo import bar
    """

    __slots__ = ("_ignore_at_print", "_source", "_source_mod", "_target")
    _attribute_nodes = ()

    def __init__(self, source, target=None, ignore_at_print=False, mod=None):
        if source is not None:
            source = Import._format(source)

        self._source = source
        self._target = {}  # Dict is used as Python doesn't have an ordered set
        self._source_mod = mod
        self._ignore_at_print = ignore_at_print

        if mod is None and isinstance(target, Module):
            self._source_mod = target

        if target is None:
            raise KeyError("Missing argument 'target'")
        if not iterable(target):
            target = [target]

        else:
            for i in target:
                assert isinstance(i, AsName | Module)
                if isinstance(i, Module):
                    self._target[AsName(i, source)] = None
                else:
                    self._target[i] = None
        init_model_object(self)

    @staticmethod
    def _format(i):
        """
        Format a string passed to this file into a X2py object.

        Format a string passed to this file into a X2py object or confirm
        that it is already correctly formatted.

        Parameters
        ----------
        i : Any
            The object to be formatted.

        Returns
        -------
        Symbol | AsName
            The formatted object.

        Raises
        ------
        TypeError
            Raised if the input is not a string or one of the acceptable
            output types.
        """
        if isinstance(i, str):
            return Symbol(i)
        if isinstance(i, AsName | Symbol) or (isinstance(i, Literal) and isinstance(i.dtype, StringType)):
            return i
        raise TypeError(f"Expecting a string, Symbol, given {type(i)}")

    @property
    def target(self):
        """
        Get the objects that are being imported.

        Get the objects that are being imported.
        """
        return self._target.keys()

    @property
    def source(self):
        return self._source

    @property
    def ignore(self):
        return self._ignore_at_print

    @ignore.setter
    def ignore(self, to_ignore):
        if not isinstance(to_ignore, bool):
            raise TypeError("to_ignore must be a boolean.")
        self._ignore_at_print = to_ignore

    def __str__(self):
        source = str(self.source)
        if len(self.target) == 0:
            return f"import {source}"
        target = ", ".join([str(i) for i in self.target])
        return f"from {source} import {target}"

    def define_target(self, new_target):
        """
        Add an additional target to the imports.

        Add an additional target to the imports.
        I.e. if imp is an Import defined as:
        >>> from numpy import ones

        and we call imp.define_target('cos')
        then it becomes:
        >>> from numpy import ones, cos

        Parameters
        ----------
        new_target : str | AsName | iterable[str | AsName]
            The new import target.
        """

        if iterable(new_target):
            self._target.update(dict.fromkeys(new_target))
        else:
            self._target[new_target] = None

    @property
    def source_module(self):
        """The module describing the Import source"""
        return self._source_mod


# TODO: Should Declare have an optional init value for each var?


# ARA : issue-999 add is_external for external function exported through header files
class Declare:
    """
    Represents a variable declaration in the code.

    Represents a variable declaration in the translated code.

    Parameters
    ----------
    variable : Variable
        A single variable which should be declared.
    access : str, optional
        Read/write access used by language printers for declaration attributes.
    by_value : bool, default=False
        True when the declaration must include the Fortran ``value`` ABI attribute.
    value : model object, optional
        The initialisation value of the variable.
    static : bool, default=False
        True for a static declaration of an array.
    external : bool, default=False
        True for a function declared through a header.
    module_variable : bool, default=False
        True for a variable which belongs to a module.

    Examples
    --------
    >>> from x2py.ast.core import Declare, Variable
    >>> Declare(Variable(NumpyInt64Type(), 'n'))
    Declare(n)
    """

    __slots__ = (
        "_access",
        "_by_value",
        "_external",
        "_module_variable",
        "_static",
        "_value",
        "_variable",
    )
    _attribute_nodes = ("_variable", "_value")

    def __init__(
        self,
        variable,
        access=None,
        by_value=False,
        value=None,
        static=False,
        external=False,
        module_variable=False,
    ):
        if not isinstance(variable, Variable):
            raise TypeError(f"var must be of type Variable, given {variable}")

        if access not in (None, "read", "write", "readwrite", "unspecified"):
            raise ValueError("access must be one of None, 'read', 'write', 'readwrite', or 'unspecified'")

        if not isinstance(by_value, bool):
            raise TypeError("Expecting a boolean for by_value attribute")

        if not isinstance(static, bool):
            raise TypeError("Expecting a boolean for static attribute")

        if not isinstance(external, bool):
            raise TypeError("Expecting a boolean for external attribute")

        if not isinstance(module_variable, bool):
            raise TypeError("Expecting a boolean for module_variable attribute")

        self._variable = variable
        self._access = access
        self._by_value = by_value
        self._value = value
        self._static = static
        self._external = external
        self._module_variable = module_variable
        init_model_object(self)

    @property
    def variable(self):
        return self._variable

    @property
    def access(self):
        return self._access

    @property
    def by_value(self):
        return self._by_value

    @property
    def value(self):
        return self._value

    @property
    def static(self):
        return self._static

    @property
    def external(self):
        return self._external

    @property
    def module_variable(self):
        """Indicates whether the variable is scoped to
        a module
        """
        return self._module_variable

    def __repr__(self):
        return f"Declare({self.variable!r})"


class EmptyNode:
    """
    Represents an empty node in the abstract syntax tree (AST).
    When a subtree is removed from the AST, we replace it with an EmptyNode
    object that acts as a placeholder. Using an EmptyNode instead of None
    is more explicit and avoids confusion. Further, finding a None in the AST
    is signal of an internal bug.

    Parameters
    ----------
    text : str
       the comment line

    Examples
    --------
    >>> from x2py.ast.core import EmptyNode
    >>> EmptyNode()

    """

    __slots__ = ()
    _attribute_nodes = ()

    def __init__(self):
        init_model_object(self)

    def __str__(self):
        return ""


class Comment:
    """
    Represents a Comment in the code.

    Represents a Comment in the code.

    Parameters
    ----------
    text : str
       The comment line.

    Examples
    --------
    >>> from x2py.ast.core import Comment
    >>> Comment('this is a comment')
    # this is a comment
    """

    __slots__ = "_text"
    _attribute_nodes = ()

    def __init__(self, text):
        self._text = text
        init_model_object(self)

    @property
    def text(self):
        return self._text

    def __str__(self):
        return f"# {self.text}"


class SeparatorComment(Comment):
    """Represents a Separator Comment in the code.

    Parameters
    ----------
    mark : str
        marker

    Examples
    --------
    >>> from x2py.ast.core import SeparatorComment
    >>> SeparatorComment(n=40)
    # ........................................
    """

    __slots__ = ()

    def __init__(self, n):
        text = """.""" * n
        super().__init__(text)


class CommentBlock:
    """Represents a Block of Comments

    Parameters
    ----------
    txt : str

    """

    __slots__ = ("_comments", "_header")
    _attribute_nodes = ()

    def __init__(self, txt, header="CommentBlock"):
        if not isinstance(txt, str):
            raise TypeError("txt must be of type str")
        txt = txt.replace('"', "")
        txts = txt.split("\n")

        self._header = header
        self._comments = txts

        init_model_object(self)

    @property
    def comments(self):
        return self._comments

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, header):
        self._header = header


class Pass:
    """Basic class for pass instruction."""

    __slots__ = ()
    _attribute_nodes = ()

    def __init__(self):
        init_model_object(self)


class IfSection:
    """
    Represents one condition and code block in an if statement.

    Represents a condition and associated code block
    in an if statement in the code.

    Parameters
    ----------
    cond : model object
           A boolean expression indicating whether or not the block
           should be executed.
    body : CodeBlock
           The code to be executed if the condition is satisfied.

    Examples
    --------
    >>> from x2py.ast.internals import Symbol
    >>> from x2py.ast.core import Assign, IfSection, CodeBlock
    >>> n = Symbol('n')
    >>> IfSection((n>1), CodeBlock([Assign(n,n-1)]))
    IfSection((n>1), CodeBlock([Assign(n,n-1)]))
    """

    __slots__ = ("_block", "_condition")
    _attribute_nodes = ("_condition", "_block")

    def __init__(self, cond, body):
        assert cond.dtype is NumpyBoolType()

        if isinstance(body, list | tuple):
            body = CodeBlock(body)
        elif isinstance(body, CodeBlock):
            body = body
        else:
            raise TypeError("body is not iterable or CodeBlock")

        self._condition = cond
        self._block = body

        init_model_object(self)

    @property
    def condition(self):
        return self._condition

    @property
    def body(self):
        return self._block

    def __iter__(self):
        return iter((self.condition, self.body))

    def __str__(self):
        return f"IfSec({self.condition}, {self.body})"


class If:
    """
    Represents an if statement in the code.

    Represents an if statement in the code.

    Parameters
    ----------
    *args : IfSection
        All arguments are sections of the complete If block.

    Examples
    --------
    >>> from x2py.ast.internals import Symbol
    >>> from x2py.ast.core import Assign, If
    >>> n = Symbol('n')
    >>> i1 = IfSection((n>1), [Assign(n,n-1)])
    >>> i2 = IfSection(True, [Assign(n,n+1)])
    >>> If(i1, i2)
    If(IfSection((n>1), [Assign(n,n-1)]), IfSection(True, [Assign(n,n+1)]))
    """

    __slots__ = ("_blocks",)
    _attribute_nodes = ("_blocks",)

    # TODO add type check in the semantic stage

    def __init__(self, *args):
        if not all(isinstance(a, IfSection) for a in args):
            raise TypeError("An If must be composed of IfSections")

        self._blocks = args

        init_model_object(self)

    @property
    def blocks(self):
        """
        The IfSection blocks inside this if.

        The IfSection blocks inside this if.
        """
        return self._blocks

    def __str__(self):
        blocks = ",".join(str(b) for b in self.blocks)
        return f"If({blocks})"


class CaseSection:
    """Represents one section in a select-case statement."""

    __slots__ = ("_body", "_label")
    _attribute_nodes = ("_label", "_body")

    def __init__(self, label, body):
        if isinstance(body, list | tuple):
            body = CodeBlock(body)
        elif not isinstance(body, CodeBlock):
            raise TypeError("body is not iterable or CodeBlock")
        self._label = label
        self._body = body
        init_model_object(self)

    @property
    def label(self):
        return self._label

    @property
    def body(self):
        return self._body


class SelectCase:
    """Represents a Fortran-style select-case statement."""

    __slots__ = ("_expr", "_sections")
    _attribute_nodes = ("_expr", "_sections")

    def __init__(self, expr, *sections):
        if not sections or not all(isinstance(section, CaseSection) for section in sections):
            raise TypeError("SelectCase must contain CaseSection objects")
        self._expr = expr
        self._sections = sections
        init_model_object(self)

    @property
    def expr(self):
        return self._expr

    @property
    def sections(self):
        return self._sections


# ========================================================================================
class Function:
    """
    Abstract class for function calls translated to X2py objects.

    A subclass of this base class represents calls to a specific internal
    function of X2py, which may be simplified at a later stage, or made
    available in the target language when printing the generated code.

    Parameters
    ----------
    *args : iterable
        The arguments passed to the function call.
    """

    __slots__ = ("_args",)
    _attribute_nodes = ("_args",)
    name = None

    def __init__(self, *args):
        self._args = tuple(args)
        init_model_object(self)

    @property
    def args(self):
        """
        The arguments passed to the function.

        Tuple containing all the arguments passed to the function call.
        """
        return self._args

    @property
    def is_elemental(self):
        """
        Whether the function acts elementwise on an array argument.

        Boolean indicating whether the (scalar) function should be called
        elementwise on an array argument. Here we set the default to False.
        """
        return False


class ArraySize(Function):
    """
    Gets the total number of elements in an array.

    Class representing a call to a function which would return
    the total number of elements in a multi-dimensional array.

    Parameters
    ----------
    arg : model object
        An array of unknown size.
    """

    __slots__ = ()
    name = "size"

    _shape = None
    _class_type = NumpyInt64Type()

    def __init__(self, arg):
        super().__init__(arg)

    @property
    def arg(self):
        """
        Object whose size is investigated.

        The argument of the function call, i.e. the object whose size is
        investigated.
        """
        return self._args[0]

    def __str__(self):
        return f"Size({self.arg})"

    def __eq__(self, other):
        if isinstance(other, ArraySize):
            return self.arg == other.arg
        return False


class ArrayShapeElement(Function):
    """
    Gets the size of one array dimension.
    """

    __slots__ = ()
    name = "shape"

    _shape = None
    _class_type = NumpyInt64Type()

    def __init__(self, arg, index):
        super().__init__(arg, index)

    @property
    def arg(self):
        """Object whose shape is investigated."""
        return self._args[0]

    @property
    def index(self):
        """Zero-based dimension index."""
        return self._args[1]


class ArrayLowerBound(Function):
    """Gets the lower bound of one array dimension."""

    __slots__ = ()
    name = "lbound"

    _shape = None
    _class_type = NumpyInt64Type()

    def __init__(self, arg, index):
        super().__init__(arg, index)

    @property
    def arg(self):
        """Object whose lower bound is investigated."""
        return self._args[0]

    @property
    def index(self):
        """Zero-based dimension index."""
        return self._args[1]


class ArrayAllocated(Function):
    """
    Tests whether an allocatable array is allocated.
    """

    __slots__ = ()
    name = "allocated"

    _shape = None
    _class_type = NumpyBoolType()

    def __init__(self, arg):
        super().__init__(arg)

    @property
    def arg(self):
        """Object whose allocation status is investigated."""
        return self._args[0]


class ArrayAssociated(Function):
    """
    Tests whether a Fortran pointer array is associated.
    """

    __slots__ = ()
    name = "associated"

    _shape = None
    _class_type = NumpyBoolType()

    def __init__(self, arg):
        super().__init__(arg)

    @property
    def arg(self):
        """Object whose pointer association status is investigated."""
        return self._args[0]


class ArrayContiguous(Function):
    """Tests whether an array occupies contiguous native storage."""

    __slots__ = ()
    name = "is_contiguous"

    _shape = None
    _class_type = NumpyBoolType()

    def __init__(self, arg):
        super().__init__(arg)

    @property
    def arg(self):
        """Object whose storage contiguity is investigated."""
        return self._args[0]


class Slice:
    """
    Represents a slice in the code.

    An object of this class represents the slicing of a Numpy array along one of
    its dimensions. In most cases this corresponds to a Python slice in the user
    code, where it is represented by a `python.ast.Slice` object.

    In addition, at the wrapper and code generation stages, an integer index
    `i` used to create a view of a Numpy array is converted to an object
    `Slice(i, i+1, 1)`. This allows using C
    variadic arguments in the function `array_slicing` (in file
    x2py/stdlib/ndarrays/ndarrays.c).

    Parameters
    ----------
    start : Symbol or int
        Starting index.

    stop : Symbol or int
        Ending index.

    step : Symbol or int, default=None
        The step between indices.

    Examples
    --------
    >>> from x2py.ast.internals import Slice, symbols
    >>> start, end, step = symbols('start, stop, step')
    >>> Slice(start, stop)
    start : stop
    >>> Slice(None, stop)
     : stop
    >>> Slice(start, None)
    start :
    >>> Slice(start, stop, step)
    start : stop : step
    """

    __slots__ = ("_start", "_step", "_stop")
    _attribute_nodes = ("_start", "_stop", "_step")

    def __init__(self, start, stop, step=None):
        self._start = start
        self._stop = stop
        self._step = step
        init_model_object(self)

        assert start is None or isinstance(getattr(start.dtype, "primitive_type", None), PrimitiveIntegerType)
        assert stop is None or isinstance(getattr(stop.dtype, "primitive_type", None), PrimitiveIntegerType)
        assert step is None or isinstance(getattr(step.dtype, "primitive_type", None), PrimitiveIntegerType)

    @property
    def start(self):
        """Index where the slicing of the object starts"""
        return self._start

    @property
    def stop(self):
        """Index until which the slicing takes place"""
        return self._stop

    @property
    def step(self):
        """The difference between each index of the
        objects in the slice
        """
        return self._step

    def __str__(self):
        start = "" if self.start is None else str(self.start)
        stop = "" if self.stop is None else str(self.stop)
        return f"{start} : {stop} : {self.step}"


# =======================================================================================================
class PythonTuple:
    """
    Class representing a call to Python's native (,) function which creates tuples.

    Class representing a call to Python's native (,) function
    which initialises a literal tuple.

    Parameters
    ----------
    *args : tuple of model object
        The arguments passed to the tuple function.
    class_type : Type, optional
        The final type of the tuple. This is necessary to create a printable
        empty tuple. Otherwise it is not used.
    """

    __slots__ = ("_args", "_class_type", "_is_homogeneous", "_shape")
    _iterable = True
    _attribute_nodes = ("_args",)

    def __init__(self, *args, class_type=None):
        self._args = args
        init_model_object(self)

        self._is_homogeneous = True
        if len(args) == 0:
            self._class_type = GenericType
            self._shape = (convert_to_literal(0),)
            return

        self._shape = (convert_to_literal(len(args)),)
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


def get_direct_assignment(obj):
    """Return the assignment that directly consumes ``obj``, if present."""
    return _find_direct_model_parent(obj, (Assign, AliasAssign))


def get_direct_function_argument(obj):
    """Return the function argument that directly contains ``obj``, if present."""
    return _find_direct_model_parent(obj, FunctionDefArgument)


def get_direct_overload_set(obj):
    """Return the interface that directly contains ``obj``, if present."""
    return _find_direct_model_parent(obj, FunctionOverloadSet)


def get_direct_module(obj):
    """Return the module that directly contains ``obj``, if present."""
    return _find_direct_model_parent(obj, Module)


def get_enclosing_class(obj):
    """Return the first class containing ``obj``, if present."""
    return _find_model_parent(obj, ClassDef)


def get_enclosing_function(obj):
    """Return the first function containing ``obj``, if present."""
    return _find_model_parent(obj, FunctionDef)


def get_enclosing_module(obj):
    """Return the first module containing ``obj``, if present."""
    return _find_model_parent(obj, Module)


def is_in_overload_set(obj):
    """Return whether ``obj`` belongs to an interface outside a function call."""
    return _find_model_parent(obj, FunctionOverloadSet, excluded_types=(FunctionCall,)) is not None


for _model_cls in (
    Operator,
    Variable,
    IndexedElement,
    AsName,
    Assign,
    Allocate,
    Deallocate,
    CodeBlock,
    AliasAssign,
    Module,
    ModuleHeader,
    FunctionCallArgument,
    FunctionDefArgument,
    FunctionDefResult,
    FunctionCall,
    Return,
    FunctionDef,
    FunctionOverloadSet,
    ClassDef,
    Import,
    Declare,
    EmptyNode,
    Comment,
    CommentBlock,
    Pass,
    IfSection,
    If,
    Function,
    ArrayAllocated,
    ArrayAssociated,
    ArrayContiguous,
    ArrayLowerBound,
    ArrayShapeElement,
    FortranCharacterLength,
    Slice,
    PythonTuple,
):
    register_model_class(_model_cls)

del _model_cls
