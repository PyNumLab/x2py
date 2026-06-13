# ------------------------------------------------------------------------- #
# This file is part of Pyccel which is released under MIT License. See the  #
# LICENSE file or go to https://github.com/pyccel/pyccel/blob/devel/LICENSE #
# for full license details.                                                 #
# ------------------------------------------------------------------------- #
"""
Module containing the core Pyccel AST nodes which are used in the syntactic
and semantic stages of Pyccel, and are relevant to all target languages. These
include nodes representing variable assignment, code blocks, and memory
allocation. All of these nodes inherit from `PyccelAstNode` either directly or
through the subclasses `TypedAstNode` and `ScopedAstNode`, all of which are
defined in `pyccel.ast.core.basic`.
"""
import inspect

from itertools import chain
from functools import lru_cache

from .basic import Immutable, PyccelAstNode, ScopedAstNode, TypedAstNode, iterable
from .datatypes import (
    CustomDataType,
    FinalType,
    PyccelType,
    PythonNativeBool,
    SymbolicType,
    TupleType,
    PrimitiveIntegerType,
    PythonNativeInt,
    CharType,
    ContainerType,
    StringType,
)
from .datatypes import (
    LiteralInteger,
    LiteralFalse,
    LiteralString,
    LiteralTrue,
    Nil,
    NilArgument,
    LiteralEllipsis,
    NumpyNDArrayType,
)
from .operators import (
    PyccelAdd,
    PyccelAssociativeParenthesis,
    PyccelDiv,
    PyccelFloorDiv,
    PyccelIs,
    PyccelMinus,
    PyccelMod,
    PyccelMul,
    PyccelOperator,
)

__all__ = (
    "DottedVariable",
    "IndexedElement",
    "Variable",
    "AliasAssign",
    "Allocate",
    "AsName",
    "Assign",
    "AugAssign",
    "ClassDef",
    "CodeBlock",
    "Comment",
    "CommentBlock",
    "Deallocate",
    "Declare",
    "EmptyNode",
    "For",
    "FunctionAddress",
    "FunctionCall",
    "FunctionCallArgument",
    "FunctionDef",
    "FunctionDefArgument",
    "FunctionDefResult",
    "If",
    "IfSection",
    "Import",
    "Interface",
    "Module",
    "ModuleHeader",
    "Pass",
    "Program",
    "PyccelFunctionDef",
    "Return",
    "SeparatorComment",
    "ManagedMemory",
    "MemoryHandlerType",
    "UnpackManagedMemory",
    "PyccelArrayShapeElement",
    "PyccelArraySize",
    "PyccelFunction",
    "PyccelSymbol",
    "Slice",
)

# ==============================================================================
class PyccelSymbol(str, Immutable):
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
        symbol represents an object created by Pyccel in order to assign a
        temporary object. This is sometimes necessary to facilitate the translation.

    Examples
    --------
    >>> from pyccel.ast.internals import PyccelSymbol
    >>> x = PyccelSymbol('x')
    x
    """

    __slots__ = ("_is_temp",)

    def __new__(cls, name, is_temp=False):
        return super().__new__(cls, name)

    def __init__(self, name, is_temp=False):
        self._is_temp = is_temp
        super().__init__()

    @property
    def is_temp(self):
        """
        Indicates if this symbol represents a temporary variable created by Pyccel,
        and was not present in the original Python code [default value : False].
        """
        return self._is_temp

class Variable(TypedAstNode):
    """
    Represents a typed variable.

    Represents a variable in the code and stores all useful properties which allow
    for easy usage of this variable.

    Parameters
    ----------
    class_type : PyccelType
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

    shape : tuple, default: None
        The shape of the array. A tuple whose elements indicate the number of elements along
        each of the dimensions of an array. The elements of the tuple should be None or TypedAstNodes.

    cls_base : class, default: None
        Class base if variable is an object or an object member.

    is_argument : bool, default: False
        Indicates if object is the argument of a function.

    is_temp : bool, default: False
        Indicates if this symbol represents a temporary variable created by Pyccel,
        and was not present in the original Python code.

    allows_negative_indexes : bool, default: False
        Indicates if non-literal negative indexes should be correctly handled when indexing this
        variable. The default is False for performance reasons.

    Examples
    --------
    >>> from pyccel.ast.datatypes import PythonNativeInt, PythonNativeFloat
    >>> from pyccel.ast.core import Variable
    >>> Variable(PythonNativeInt(), 'n')
    n
    >>> n = 4
    >>> Variable(PythonNativeFloat(), 'x', shape=(n,2), memory_handling='heap')
    x
    >>> Variable(PythonNativeInt(), DottedName('matrix', 'n_rows'))
    matrix.n_rows
    """

    __slots__ = (
        "_name",
        "_alloc_shape",
        "_memory_handling",
        "_is_target",
        "_is_optional",
        "_cls_base",
        "_is_argument",
        "_is_temp",
        "_shape",
        "_is_private",
        "_class_type",
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
        shape=None,
        cls_base=None,
        is_argument=False,
        is_temp=False,
        allows_negative_indexes=False,
    ):
        super().__init__()

        # ------------ Variable Properties ---------------
        # if class attribute
        if isinstance(name, str):
            name = name.split(""".""")
            if len(name) == 1:
                name = PyccelSymbol(name[0])
            else:
                raise ValueError(name)

        assert isinstance(name, PyccelSymbol)
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

        self._cls_base = cls_base
        self._is_argument = is_argument
        self._is_temp = is_temp

        # ------------ TypedAstNode Properties ---------------
        assert isinstance(class_type, PyccelType)
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
        `PyccelArrayShapeElement`.

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
        elif not hasattr(shape, "__iter__"):
            shape = [shape]

        new_shape = [None]*len(shape)
        for i, s in enumerate(shape):
            if isinstance(s, LiteralInteger):
                new_shape[i] = s
            elif isinstance(s, int):
                new_shape[i] = LiteralInteger(s)
            elif isinstance(s, TypedAstNode):
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

        The shape used in pyccel is usually simplified to contain
        only Literals and PyccelArraySizes but the shape for
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
    def is_temp(self):
        """
        Indicates if this symbol represents a temporary variable created by Pyccel,
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
        return isinstance(self.class_type, NumpyNDArrayType)

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f"{type(self).__name__}({self.name}, type={repr(self.class_type)})"

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

        if new_class is None:
            cls = self.__class__
        else:
            cls = new_class

        args = inspect.signature(Variable.__init__)
        new_kwargs = {
            k: getattr(self, "_" + k)
            for k in args.parameters.keys()
            if "_" + k in dir(self)
        }
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
        elif is_temp:
            raise ValueError("Variables cannot become temporary")
        self._is_temp = is_temp

class IndexedElement(TypedAstNode):
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
    base : Variable | PyccelSymbol | DottedName
        The object being indexed.

    *indices : tuple of TypedAstNode
        The values used to index the base.

    Examples
    --------
    >>> from pyccel.ast.core import Variable, IndexedElement
    >>> from pyccel.ast.datatypes import PythonNativeInt
    >>> A = Variable(PythonNativeInt(), 'A', shape=(2,3), rank=2)
    >>> i = Variable(PythonNativeInt(), 'i')
    >>> j = Variable(PythonNativeInt(), 'j')
    >>> IndexedElement(A, (i, j))
    IndexedElement(A, i, j)
    >>> IndexedElement(A, i, j) == A[i, j]
    True
    """

    __slots__ = ("_label", "_indices", "_shape", "_class_type", "_is_slice")
    _attribute_nodes = ("_label", "_indices", "_shape")

    def __init__(self, base, *indices):

        self._label = base
        self._shape = None

        shape = base.shape
        rank = base.class_type.container_rank
        assert len(indices) <= rank

        if any(
            not isinstance(a, (int, TypedAstNode, Slice, LiteralEllipsis))
            for a in indices
        ):
            raise
            errors.report(
                "Index is not of valid type", symbol=indices, severity="fatal"
            )

        if len(indices) == 1 and isinstance(indices[0], LiteralEllipsis):
            self._indices = tuple(
                LiteralInteger(a) if isinstance(a, int) else a for a in indices
            )
            indices = [Slice(None, None)] * rank
        # Add empty slices to fully index the object
        elif len(indices) < rank:
            indices = indices + tuple([Slice(None, None)] * (rank - len(indices)))
            self._indices = tuple(
                LiteralInteger(a) if isinstance(a, int) else a for a in indices
            )
        else:
            self._indices = tuple(
                LiteralInteger(a) if isinstance(a, int) else a for a in indices
            )

        self._class_type = base.class_type.element_type
        self._is_slice   = False
        self._shape      = (1,)

        super().__init__()

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
        return f"{repr(self.base)}[{indices}]"

    @property
    def is_slice(self):
        """
        Indicates whether this instance represents a slice.

        Indicates whether this instance represents a slice or an element.
        """
        return self._is_slice

    def __hash__(self):
        return hash((self.base, self._indices))

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
        See pyccel.ast.variable.Variable.

    lhs : Variable
        The Variable on the right of the '.'.

    **kwargs : dict
        See pyccel.ast.variable.Variable.
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

class AsName(PyccelAstNode):
    """
    Represents a renaming of an object, used with Import.

    A class representing the renaming of an object such as a function or a
    variable. This usually occurs during an Import.

    Parameters
    ----------
    obj : PyccelAstNode or PyccelAstNodeType
        The variable, function, or module being renamed.
    local_alias : str
        Name of variable or function in this context.

    Examples
    --------
    >>> from pyccel.ast.core import AsName, FunctionDef
    >>> from pyccel.ast.numpyext import NumpyFull
    >>> func = FunctionDef('old', (), (), ())
    >>> AsName(func, 'new')
    old as new
    >>> AsName(NumpyFull, 'fill_func')
    full as fill_func
    """

    __slots__ = ("_obj", "_local_alias")
    _attribute_nodes = ()

    def __init__(self, obj, local_alias):
        assert (
                isinstance(obj, PyccelAstNode) and not isinstance(obj, PyccelSymbol)
            ) or (isinstance(obj, type) and issubclass(obj, PyccelAstNode))
        self._obj = obj
        self._local_alias = local_alias
        super().__init__()

    @property
    def name(self):
        """The original name of the object"""
        obj = self._obj
        if isinstance(obj, (str, PyccelSymbol)):
            return obj
        else:
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
        elif isinstance(string, AsName):
            return string.local_alias == self.local_alias
        else:
            return self is string

    def __ne__(self, string):
        return not self == string

    def __hash__(self):
        return hash(self.local_alias)

class Assign(PyccelAstNode):
    """
    Represents variable assignment for code generation.

    Class representing an assignment node, where the result of an expression
    (rhs: right hand side) is saved into a variable (lhs: left hand side).

    Parameters
    ----------
    lhs : TypedAstNode
        In the syntactic stage:
           Object representing the lhs of the expression. These should be
           singular objects, such as one would use in writing code. Notable types
           include PyccelSymbol, and IndexedElement. Types that
           subclass these types are also supported.
        In the semantic stage:
           Variable or IndexedElement.

    rhs : TypedAstNode
        In the syntactic stage:
          Object representing the rhs of the expression.
        In the semantic stage :
          TypedAstNode with the same shape as the lhs.

    Examples
    --------
    >>> from pyccel.ast.datatypes import PythonNativeInt
    >>> from pyccel.ast.internals import symbols
    >>> from pyccel.ast.variable import Variable
    >>> from pyccel.ast.core import Assign
    >>> x, y, z = symbols('x, y, z')
    >>> Assign(x, y)
    x := y
    >>> Assign(x, 0)
    x := 0
    >>> A = Variable(PythonNativeInt(), 'A', rank = 2)
    >>> Assign(x, A)
    x := A
    >>> Assign(A[0,1], x)
    IndexedElement(A, 0, 1) := x
    """

    __slots__ = ("_lhs", "_rhs")
    _attribute_nodes = ("_lhs", "_rhs")

    def __init__(self, lhs, rhs):
        if isinstance(lhs, (tuple, list)):
            lhs = tuple(lhs)
        self._lhs = lhs
        self._rhs = rhs
        super().__init__()

    def __str__(self):
        return f"{self.lhs} := {self.rhs}"

    def __repr__(self):
        return f"{repr(self.lhs)} := {repr(self.rhs)}"

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
        cond = cond and isinstance(lhs, PyccelSymbol)
        cond = cond or isinstance(rhs, Variable) and rhs.is_alias
        return cond


# ------------------------------------------------------------------------------
class Allocate(PyccelAstNode):
    """
    Represents memory allocation for code generation.

    Represents memory allocation (usually of an array) for code generation.
    This is relevant to low-level target languages, such as C or Fortran,
    where the programmer must take care of heap memory allocation.

    Parameters
    ----------
    variable : pyccel.ast.core.Variable
        The typed variable (usually an array) that needs memory allocation.

    shape : int or iterable or None
        Shape of the array after allocation (None for scalars).

    status : str {'allocated'|'unallocated'|'unknown'}
        Variable allocation status at object creation.

    like : TypedAstNode, optional
        A TypedAstNode describing the amount of memory which must be allocated.
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

    __slots__ = ("_variable", "_shape", "_order", "_status", "_like", "_alloc_type")
    _attribute_nodes = ("_variable", "_like")

    # ...
    def __init__(self, variable, *, shape, status, like=None, alloc_type=None):

        if not isinstance(variable, Variable):
            raise TypeError(
                f"Can only allocate a 'Variable' object, got {type(variable)} instead"
            )

        if variable.on_stack:
            # Variable may only be a pointer in the wrapper
            raise ValueError("Variable must be allocatable")

        if shape and not isinstance(shape, (int, tuple, list)):
            raise TypeError(
                f"Cannot understand 'shape' parameter of type '{type(shape)}'"
            )

        assert variable.class_type.shape_is_compatible(shape)

        if not isinstance(status, str):
            raise TypeError(
                f"Cannot understand 'status' parameter of type '{type(status)}'"
            )

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
        super().__init__()

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
        TypedAstNode describing the amount of memory needed for the allocation.

        A TypedAstNode describing the amount of memory which must be allocated.
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
        else:
            return False

    def __hash__(self):
        return hash((id(self.variable), self.shape, self.order, self.status))


# ------------------------------------------------------------------------------
class Deallocate(PyccelAstNode):
    """
    Class representing memory deallocation.

    Represents memory deallocation (usually of an array) for code generation.
    This is relevant to low-level target languages, such as C or Fortran,
    where the programmer must take care of heap memory deallocation.

    Parameters
    ----------
    variable : pyccel.ast.core.Variable
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
            raise TypeError(
                f"Can only allocate a 'Variable' object, got {type(variable)} instead"
            )

        self._variable = variable
        super().__init__()

    # ...

    @property
    def variable(self):
        return self._variable

    def __eq__(self, other):
        if isinstance(other, Deallocate):
            return self.variable is other.variable
        else:
            return False

    def __hash__(self):
        return hash(id(self.variable))


# ------------------------------------------------------------------------------
class CodeBlock(PyccelAstNode):
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
        super().__init__()

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

    def insert2body(self, *obj, back=True):
        """Insert object(s) to the body of the codeblock
        The object(s) are inserted at the back by default but
        can be inserted at the front by setting back to False
        """
        _ = [o.set_current_user_node(self) for o in obj]
        if back:
            self._body = tuple([*self.body, *obj])
        else:
            self._body = tuple([*obj, *self.body])

    def __repr__(self):
        return f"CodeBlock({self.body})"


class AliasAssign(PyccelAstNode):
    """
    Representing assignment of an alias to its local_alias.

    Represents aliasing for code generation. An alias is any statement of the
    form `lhs := rhs` where lhs is a pointer and rhs is a local_alias. In other words
    the contents of `lhs` will change if the contents of `rhs` are modified.

    Parameters
    ----------
    lhs : TypedAstNode
        In the syntactic stage:
           Object representing the lhs of the expression. These should be
           singular objects, such as one would use in writing code. Notable types
           include PyccelSymbol, and IndexedElement. Types that
           subclass these types are also supported.
        In the semantic stage:
           Variable.

    rhs : PyccelSymbol | Variable, IndexedElement
        The local_alias of the assignment. A PyccelSymbol in the syntactic stage,
        a Variable or a Slice of an array in the semantic stage.

    Examples
    --------
    >>> from pyccel.ast.internals import PyccelSymbol
    >>> from pyccel.ast.core import AliasAssign
    >>> from pyccel.ast.core import Variable
    >>> n = Variable(PythonNativeInt(), 'n')
    >>> x = Variable(PythonNativeInt(), 'x', rank=1, shape=[n])
    >>> y = PyccelSymbol('y')
    >>> AliasAssign(y, x)
    """

    __slots__ = ("_lhs", "_rhs")
    _attribute_nodes = ("_lhs", "_rhs")

    def __init__(self, lhs, rhs):
        if not lhs.is_alias:
            raise TypeError("lhs must be a pointer")

        if isinstance(rhs, FunctionCall) and not rhs.funcdef.results.var.is_alias:
            raise TypeError(
                "A pointer cannot point to the address of a temporary variable"
            )

        self._lhs = lhs
        self._rhs = rhs
        super().__init__()

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
    lhs : PyccelSymbol | TypedAstNode
        Object representing the lhs of the expression.
        In the syntactic stage this may be a PyccelSymbol, or an IndexedElement.
        In later stages the object should inherit from TypedAstNode and be fully
        typed.

    op : str
        Operator (+, -, /, \*, %).

    rhs : TypedAstNode
        Object representing the rhs of the expression.

    Examples
    --------
    >>> from pyccel.ast.core import Variable
    >>> from pyccel.ast.core import AugAssign
    >>> s = Variable(PythonNativeInt(), 's')
    >>> t = Variable(PythonNativeInt(), 't')
    >>> AugAssign(s, '+', 2 * t + 1)
    s += 1 + 2*t
    """

    __slots__ = ("_op",)
    _accepted_operators = {
        "+": PyccelAdd,
    }

    def __init__(self, lhs, op, rhs):

        if op not in self._accepted_operators.keys():
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

    @property
    def pyccel_operator(self):
        """
        Get the PyccelOperator which modifies the lhs variable.

        Get the PyccelOperator which modifies the lhs variable.
        """
        return self._accepted_operators[self._op]

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

class Module(ScopedAstNode):
    """
    Represents a module in the code.

    The Pyccel node representing a Python module. A module consists of everything
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

    program : Program/CodeBlock
        CodeBlock containing any expressions which are only executed
        when the module is executed directly.

    interfaces : list
        A list of Interface instances.

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
    >>> from pyccel.ast.variable import Variable
    >>> from pyccel.ast.core import FunctionDefArgument, Assign, FunctionDefResult
    >>> from pyccel.ast.core import ClassDef, FunctionDef, Module
    >>> from pyccel.ast.operators import PyccelAdd, PyccelMinus
    >>> from pyccel.ast.literals import LiteralInteger
    >>> x = Variable(PythonNativeFloat(), 'x')
    >>> y = Variable(PythonNativeFloat(), 'y')
    >>> z = Variable(PythonNativeFloat(), 'z')
    >>> t = Variable(PythonNativeFloat(), 't')
    >>> a = Variable(PythonNativeFloat(), 'a')
    >>> b = Variable(PythonNativeFloat(), 'b')
    >>> body = [Assign(z,PyccelAdd(x,a))]
    >>> args = [FunctionDefArgument(arg) for arg in [x,y,a,b]]
    >>> results = [FunctionDefResult(res) for res in [z,t]]
    >>> translate = FunctionDef('translate', args, results, body)
    >>> attributes   = [x,y]
    >>> methods     = [translate]
    >>> Point = ClassDef('Point', attributes, methods)
    >>> incr = FunctionDef('incr', [FunctionDefArgument(x)], [FunctionDefResult(y)], [Assign(y,PyccelAdd(x,LiteralInteger(1)))])
    >>> decr = FunctionDef('decr', [FunctionDefArgument(x)], [FunctionDefResult(y)], [Assign(y,PyccelMinus(x,LiteralInteger(1)))])
    >>> Module('my_module', [], [incr, decr], classes = [Point])
    Module(my_module, [], [FunctionDef(), FunctionDef()], [], [ClassDef(Point, (x, y), (FunctionDef(),), [public], (), [], [])], ())
    """

    __slots__ = (
        "_name",
        "_variables",
        "_funcs",
        "_interfaces",
        "_classes",
        "_imports",
        "_init_func",
        "_free_func",
        "_program",
        "_variable_inits",
        "_internal_dictionary",
        "_is_external",
    )
    _attribute_nodes = (
        "_variables",
        "_funcs",
        "_interfaces",
        "_classes",
        "_imports",
        "_init_func",
        "_free_func",
        "_program",
        "_variable_inits",
    )

    def __init__(
        self,
        name,
        variables,
        funcs,
        init_func=None,
        free_func=None,
        program=None,
        interfaces=(),
        classes=(),
        imports=(),
        scope=None,
        is_external=False,
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

        if not iterable(interfaces):
            raise TypeError("interfaces must be an iterable")
        for i in interfaces:
            if not isinstance(i, Interface):
                raise TypeError("Only a Interface instance is allowed.")

        NoneType = type(None)
        assert isinstance(init_func, (NoneType, FunctionDef))

        if not isinstance(free_func, (NoneType, FunctionDef)):
            raise TypeError("free_func must be a FunctionDef")

        if not isinstance(program, (NoneType, Program, CodeBlock)):
            raise TypeError(
                "program must be a Program (or a CodeBlock at the syntactic stage)"
            )

        if not iterable(imports):
            raise TypeError("imports must be an iterable")
        imports = list(imports)
        for i in classes:
            imports += i.imports
        imports = {i: None for i in imports}  # for unicity and ordering
        imports = tuple(imports.keys())

        assert isinstance(is_external, bool)

        self._name = name
        self._variables = variables
        self._variable_inits = [None] * len(variables)
        self._funcs = funcs
        self._init_func = init_func
        self._free_func = free_func
        self._program = program
        self._interfaces = interfaces
        self._classes = classes
        self._imports = imports
        self._is_external = is_external

        def get_name(o):
            """Get the syntactic/Python name of the object"""
            n = o.name
            return scope.get_python_name(n) if scope else n

        self._internal_dictionary = {get_name(v): v for v in variables}
        self._internal_dictionary.update({get_name(f): f for f in funcs})
        self._internal_dictionary.update({get_name(i): i for i in interfaces})
        self._internal_dictionary.update({get_name(c): c for c in classes})

        import_mods = {
            i.source: [t.object for t in i.target if isinstance(t.object, Module)]
            for i in imports
            if isinstance(i, Import)
        }
        self._internal_dictionary.update(
            {v: t[0] for v, t in import_mods.items() if t}
        )

        super().__init__(scope)

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
    def program(self):
        """CodeBlock or Program containing any expressions which are only executed
        when the module is executed directly
        """
        return self._program

    @program.setter
    def program(self, prog):
        assert self._program is None
        self._program = prog
        self._program.set_current_user_node(self)

    @property
    def funcs(self):
        """Any functions defined in the module"""
        return self._funcs

    @property
    def interfaces(self):
        """Any interfaces defined in the module"""
        return self._interfaces

    @property
    def classes(self):
        """Any classes defined in the module"""
        return self._classes

    @property
    def imports(self):
        """Any imports in the module"""
        return self._imports

    @property
    def declarations(self):
        """
        Get the declarations of all variables in the module.

        Get the declarations of all variables in the module.
        """
        return [
            Declare(i, value=v, module_variable=True)
            for i, v in zip(self.variables, self._variable_inits)
        ]

    @property
    def body(self):
        """Returns the functions, interfaces and classes defined
        in the module
        """
        return self.interfaces + self.funcs + self.classes

    def __getitem__(self, arg):
        assert isinstance(arg, str)
        args = arg.split(".")
        result = self._internal_dictionary[args[0]]
        for key in args[1:]:
            result = result[key]
        return result

    def __contains__(self, arg):
        assert isinstance(arg, (str, PyccelSymbol))
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


class ModuleHeader(PyccelAstNode):
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
    >>> from pyccel.ast.variable import Variable
    >>> from pyccel.ast.core import FunctionDefArgument, Assign, FunctionDefResult
    >>> from pyccel.ast.core import ClassDef, FunctionDef, Module
    >>> from pyccel.ast.operators import PyccelAdd, PyccelMinus
    >>> from pyccel.ast.literals import LiteralInteger
    >>> x = Variable(PythonNativeFloat(), 'x')
    >>> y = Variable(PythonNativeFloat(), 'y')
    >>> z = Variable(PythonNativeFloat(), 'z')
    >>> t = Variable(PythonNativeFloat(), 't')
    >>> a = Variable(PythonNativeFloat(), 'a')
    >>> b = Variable(PythonNativeFloat(), 'b')
    >>> body = [Assign(z,PyccelAdd(x,a))]
    >>> args = [FunctionDefArgument(arg) for arg in [x,y,a,b]]
    >>> results = [FunctionDefResult(res) for res in [z,t]]
    >>> translate = FunctionDef('translate', args, results, body)
    >>> attributes   = [x,y]
    >>> methods     = [translate]
    >>> Point = ClassDef('Point', attributes, methods)
    >>> incr = FunctionDef('incr', [FunctionDefArgument(x)], [FunctionDefResult(y)], [Assign(y,PyccelAdd(x,LiteralInteger(1)))])
    >>> decr = FunctionDef('decr', [FunctionDefArgument(x)], [FunctionDefResult(y)], [Assign(y,PyccelMinus(x,LiteralInteger(1)))])
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
        super().__init__()

    @property
    def module(self):
        return self._module


class Program(ScopedAstNode):
    """
    Represents a Program in the code.

    A class representing a program in the code. A program is a set of statements
    that are executed when the module is run directly. In Python these statements
    are located in an `if __name__ == '__main__':` block.

    Parameters
    ----------
    name : str
        The name used to identify the program (this is used for printing in Fortran).

    variables : tuple[Variable]
        An iterable object containing the variables that appear in the program.

    body : CodeBlock
        An CodeBlock containing the statements in the body of the program.

    imports : tuple[Import]
        An iterable object containing the imports used by the program.

    scope : Scope
        The scope of the program.
    """

    __slots__ = ("_name", "_variables", "_body", "_imports")
    _attribute_nodes = ("_variables", "_body", "_imports")

    def __init__(self, name, variables, body, imports=(), scope=None):

        if not isinstance(name, str):
            raise TypeError("name must be a string")

        if not iterable(variables):
            raise TypeError("variables must be an iterable")

        for i in variables:
            if not isinstance(i, Variable):
                raise TypeError("Only a Variable instance is allowed.")

        assert isinstance(body, CodeBlock)

        if not iterable(imports):
            raise TypeError("imports must be an iterable")

        imports = {i: None for i in imports}  # for unicity and ordering
        imports = tuple(imports.keys())

        self._name = name
        self._variables = tuple(variables)
        self._body = body
        self._imports = tuple(imports)
        super().__init__(scope)

    @property
    def name(self):
        """Name of the executable"""
        return self._name

    @property
    def variables(self):
        """Variables contained within the program"""
        return self._variables

    @property
    def body(self):
        """Statements in the program"""
        return self._body

    @property
    def imports(self):
        """Imports imported in the program"""
        return self._imports

    def remove_import(self, name):
        """Remove an import with the given source name from the list
        of imports
        """
        self._imports = tuple(i for i in self.imports if i.source != name)


# ==============================================================================


class For(ScopedAstNode):
    """
    Represents a 'for-loop' in the code.

    Expressions are of the form:
        "for target in iter:
            body..."

    Parameters
    ----------
    target : Variable
        Variable representing the iterator.
    iter_obj : Iterable
        Iterable object. Multiple iterators are supported but these are
        translated to a range object in the Iterable class.
    body : list[PyccelAstNode]
        List of statements representing the body of the For statement.
    scope : Scope
        The scope for the loop.

    Examples
    --------
    >>> from pyccel.ast.variable import Variable
    >>> from pyccel.ast.core import Assign, For
    >>> from pyccel.ast.internals import symbols
    >>> i,b,e,s,x = symbols('i,b,e,s,x')
    >>> A = Variable(PythonNativeInt(), 'A', rank = 2)
    >>> For(i, (b,e,s), [Assign(x, i), Assign(A[0, 1], x)])
    For(i, (b, e, s), (x := i, IndexedElement(A, 0, 1) := x))
    """

    __slots__ = ("_target", "_iterable", "_body", "_end_annotation")
    _attribute_nodes = ("_target", "_iterable", "_body")

    def __init__(self, target, iter_obj, body, scope=None):
        assert iterable(iter_obj)
        assert iterable(target)

        if iterable(body):
            body = CodeBlock(body)
        elif not isinstance(body, CodeBlock):
            raise TypeError("body must be an iterable or a Codeblock")

        self._target = target
        self._iterable = tuple(iter_obj)
        self._body = body
        self._end_annotation = None
        super().__init__(scope)

    @property
    def end_annotation(self):
        return self._end_annotation

    @end_annotation.setter
    def end_annotation(self, expr):
        self._end_annotation = expr

    @property
    def target(self):
        return self._target

    @property
    def iterable(self):
        return self._iterable

    @property
    def body(self):
        return self._body

    @property
    def local_vars(self):
        """List of variables defined in the loop"""
        return tuple(self.scope.variables.values())

    def insert2body(self, stmt):
        stmt.set_current_user_node(self)
        self.body.insert2body(stmt)


class FunctionCallArgument(PyccelAstNode):
    """
    An argument passed in a function call.

    Class describing an argument passed to a function in a
    function call.

    Parameters
    ----------
    value : TypedAstNode
        The expression passed as an argument.
    keyword : str, optional
        If the argument is passed by keyword then this
        is that keyword.
    """

    __slots__ = ("_value", "_keyword")
    _attribute_nodes = ("_value",)

    def __init__(self, value, keyword=None):
        self._value = value
        self._keyword = keyword
        super().__init__()

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
            return f"FunctionCallArgument({self.keyword} = {repr(self.value)})"
        else:
            return f"FunctionCallArgument({repr(self.value)})"

    def __str__(self):
        if self.has_keyword:
            return f"{self.keyword} = {self.value}"
        else:
            return f"{self.value}"


class FunctionDefArgument(TypedAstNode):
    """
    Node describing the argument of a function.

    An object describing the argument of a function described
    by a FunctionDef. This object stores all the information
    which describes an argument but is superfluous for a Variable.

    Parameters
    ----------
    name : PyccelSymbol, Variable, FunctionAddress
        The name of the argument.

    value : TypedAstNode, optional
        The default value of the argument.

    posonly : bool, default: False
        Indicates if the argument must be passed by position.

    kwonly : bool, default: False
        Indicates if the argument must be passed by keyword.

    annotation : str, optional
        The type annotation describing the argument.

    bound_argument : bool, default: False
        Indicates if the argument is bound to the function call. This is
        the case if the argument is the first argument of a method of a
        class.

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
    >>> from pyccel.ast.core import FunctionDefArgument
    >>> n = FunctionDefArgument('n')
    >>> n
    n
    """

    __slots__ = (
        "_name",
        "_var",
        "_posonly",
        "_kwonly",
        "_annotation",
        "_value",
        "_inout",
        "_persistent_target",
        "_bound_argument",
        "_is_vararg",
        "_is_kwarg",
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
        persistent_target=False,
        is_vararg=False,
        is_kwarg=False,
    ):
        if isinstance(name, (Variable, FunctionAddress)):
            self._var = name
            self._name = name.name
        elif isinstance(name, PyccelSymbol):
            self._var = name
            self._name = name
        else:
            raise TypeError("Name must be a PyccelSymbol, Variable or FunctionAddress")
        if not isinstance(bound_argument, bool):
            raise TypeError("bound_argument must be a boolean")
        self._value = value
        self._posonly = posonly
        self._kwonly = kwonly
        self._annotation = annotation
        self._persistent_target = persistent_target
        self._bound_argument = bound_argument
        self._is_vararg = is_vararg
        self._is_kwarg = is_kwarg

        if isinstance(name, Variable):
            name.declare_as_argument()

        if isinstance(self.var, Variable):
            self._inout = (
                (
                    self.var.rank > 0
                    or isinstance(self.var.class_type, CustomDataType)
                )
                and not isinstance(self.var.class_type, FinalType)
                and not isinstance(self.var.class_type, TupleType)
            )
        else:
            # If var is not a Variable it is a FunctionAddress
            self._inout = False

        super().__init__()

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
    def default_call_arg(self):
        """The FunctionCallArgument which is passed to FunctionCall
        if no value is provided for this argument
        """
        return (
            FunctionCallArgument(self.value, keyword=self.name)
            if self.has_default
            else None
        )

    @property
    def has_default(self):
        """Indicates whether the argument has a default value
        (if not then it must be provided)
        """
        return self._value is not None

    @property
    def inout(self):
        """
        Indicates whether the argument may be modified by the function.

        True if the argument may be modified in the function. False if
        the argument remains constant in the function.
        """
        return self._inout

    def make_const(self):
        """
        Indicate that the argument does not change in the function.

        Indicate that the argument does not change in the function by
        modifying the inout flag.
        """
        self._inout = False

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
        else:
            return name

    def __repr__(self):
        name = repr(self.name)
        if self.is_vararg:
            name = f"*{name}"
        if self.is_kwarg:
            name = f"**{name}"

        if self.has_default:
            return f"FunctionDefArgument({name}={self.value})"
        else:
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


class FunctionDefResult(TypedAstNode):
    """
    Node describing the result of a function.

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
    >>> from pyccel.ast.core import FunctionDefResult
    >>> n = FunctionDefResult('n')
    >>> n
    n
    """

    __slots__ = ("_var", "_is_argument", "_annotation")
    _attribute_nodes = ("_var",)

    def __init__(self, var, *, annotation=None):
        self._var = var
        self._annotation = annotation

        if not isinstance(var, (Variable, Nil)):
            raise TypeError(f"Var must be a Variable not a {type(var)}")
        else:
            self._is_argument = getattr(var, "is_argument", False)

        super().__init__()

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
        the result may be printed simply as an inout argument.
        """
        return self._is_argument

    def __len__(self):
        return (
            0
            if self.var is None
            else 1
        )

    def __repr__(self):
        return f"FunctionDefResult({repr(self.var)})"

    def __str__(self):
        return str(self.var)

    def __bool__(self):
        return self.var is not Nil()


class FunctionCall(TypedAstNode):
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
        "_funcdef",
        "_interface",
        "_func_name",
        "_interface_name",
        "_shape",
        "_class_type",
    )
    _attribute_nodes = ("_arguments", "_funcdef", "_interface")

    def __init__(self, func, args, current_function=None):

        for a in args:
            assert not isinstance(a, FunctionDefArgument)
        # Ensure all arguments are of type FunctionCallArgument
        args = [
            a if isinstance(a, FunctionCallArgument) else FunctionCallArgument(a)
            for a in args
        ]

        # ...
        if not isinstance(func, (FunctionDef, Interface)):
            raise TypeError("> expecting a FunctionDef or an Interface")

        if isinstance(func, Interface):
            self._interface = func
            self._interface_name = func.name
            func = func.point(args)
        else:
            self._interface = None

        name = func.name
        # ...
        if current_function == name:
            func.set_recursive()

        if not isinstance(args, (tuple, list)):
            raise TypeError("args must be a list or tuple")

        # add the missing argument in the case of optional arguments
        f_args = func.arguments
        if not len(args) == len(f_args):
            # Collect dict of keywords and values (initialised as default)
            f_args_dict = {
                a.name: (a.name, a.value) if a.has_default else None for a in f_args
            }
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
                (
                    FunctionCallArgument(keyword=a[0], value=a[1])
                    if isinstance(a, tuple)
                    else a
                )
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
            for a, av in zip(args, arg_vals)
        ]

        if current_function == func.name:
            if len(func.results) > 0 and not isinstance(func.results, TypedAstNode):
                raise
                errors.report(RECURSIVE_RESULTS_REQUIRED, symbol=func, severity="fatal")

        self._funcdef = func
        self._arguments = args
        self._func_name = func.name
        self._shape = func.results.var.shape
        self._class_type = func.results.var.class_type

        super().__init__()

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
    def interface(self):
        """The interface called by this function call"""
        return self._interface

    @property
    def func_name(self):
        """The name of the function called by this function call"""
        return self._func_name

    @property
    def interface_name(self):
        """The name of the interface called by this function call"""
        return self._interface_name

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

    @classmethod
    def _ignore(cls, c):
        """Indicates if a node should be ignored when recursing"""
        return c is None or isinstance(c, (FunctionDef, *cls._ignored_types))


class Return(PyccelAstNode):
    """
    Represents a return statement in a function in the code.

    Represents a return statement in a function in the code.

    Parameters
    ----------
    expr : TypedAstNode
        The expression to return.

    stmt : PyccelAstNode
        Any assign statements in the case of expression return.
    """

    __slots__ = ("_expr", "_stmt", "_n_returns")
    _attribute_nodes = ("_expr", "_stmt")

    def __init__(self, expr, stmt=None):

        assert stmt is None or isinstance(stmt, CodeBlock)
        assert expr is None or isinstance(
            expr, (TypedAstNode, PyccelSymbol)
        )

        self._expr = expr
        self._stmt = stmt

        self._n_returns = (
            0
            if isinstance(expr, Nil)
            else 1 if not hasattr(expr, "__iter__") else len(expr)
        )

        super().__init__()

    @property
    def expr(self):
        return self._expr

    @property
    def stmt(self):
        return self._stmt

    @property
    def n_explicit_results(self):
        """
        The number of variables explicitly returned.

        The number of variables explicitly returned.
        """
        return self._n_returns

    def __repr__(self):
        if self.stmt:
            code = repr(self.stmt) + ";"
        else:
            code = ""
        return code + f"Return({repr(self.expr)})"


class FunctionDef(ScopedAstNode):
    """
    Represents a function definition.

    Node containing all the information necessary to describe a function.
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

    interfaces : list, tuple
        A list of interfaces defined within this function.

    result_pointer_map : dict[FunctionDefResult, list[int]]
        A dictionary connecting any pointer results to the index of the possible target arguments.

    docstring : str
        The doc string of the function.

    scope : parser.scope.Scope
        The scope containing all objects scoped to the inside of this function.

    See Also
    --------
    FunctionDefArgument : The type used to store the arguments.

    Examples
    --------
    >>> from pyccel.ast.variable import Variable
    >>> from pyccel.ast.core import FunctionDefArgument, FunctionDefResult
    >>> from pyccel.ast.core import Assign, FunctionDef
    >>> from pyccel.ast.operators import PyccelAdd
    >>> from pyccel.ast.literals import LiteralInteger
    >>> x = Variable(PythonNativeFloat(), 'x')
    >>> y = Variable(PythonNativeFloat(), 'y')
    >>> args        = [FunctionDefArgument(x)]
    >>> results     = [FunctionDefResult(y)]
    >>> body        = [Assign(y,PyccelAdd(x,LiteralInteger(1)))]
    >>> FunctionDef('incr', args, results, body)
    FunctionDef(incr, (x,), (y,), [y := x + 1], [], [], None, False, function)

    One can also use parametrized argument, using FunctionDefArgument

    >>> from pyccel.ast.core import Variable
    >>> from pyccel.ast.core import Assign
    >>> from pyccel.ast.core import FunctionDef
    >>> from pyccel.ast.core import FunctionDefArgument
    >>> n = FunctionDefArgument('n', value=4)
    >>> x = Variable(PythonNativeFloat(), 'x')
    >>> y = Variable(PythonNativeFloat(), 'y')
    >>> args        = [x, n]
    >>> results     = [y]
    >>> body        = [Assign(y,x+n)]
    >>> FunctionDef('incr', args, results, body)
    FunctionDef(incr, (x, n=4), (y,), [y := 1 + x], [], [], None, False, function, [])
    """

    __slots__ = (
        "_name",
        "_arguments",
        "_results",
        "_body",
        "_global_vars",
        "_cls_name",
        "_is_static",
        "_imports",
        "_decorators",
        "_headers",
        "_is_recursive",
        "_is_pure",
        "_is_elemental",
        "_is_private",
        "_is_header",
        "_functions",
        "_interfaces",
        "_docstring",
        "_is_external",
        "_result_pointer_map",
        "_is_imported",
        "_is_semantic",
    )

    _attribute_nodes = (
        "_arguments",
        "_results",
        "_body",
        "_global_vars",
        "_imports",
        "_functions",
        "_interfaces",
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
        decorators={},
        headers=(),
        is_recursive=False,
        is_pure=False,
        is_elemental=False,
        is_private=False,
        is_header=False,
        is_external=False,
        is_imported=False,
        functions=(),
        interfaces=(),
        result_pointer_map={},
        docstring=None,
        scope=None,
    ):

        if isinstance(name, str):
            name = PyccelSymbol(name)
        elif isinstance(name, (tuple, list)):
            name_ = []
            for i in name:
                if isinstance(i, str):
                    name_.append(PyccelSymbol(i))
                else:
                    raise TypeError("Function name must be PyccelSymbol or string")
            name = tuple(name_)
        else:
            raise TypeError("Function name must be PyccelSymbol or string")

        # arguments

        if not iterable(arguments):
            raise TypeError("arguments must be an iterable")
        if not all(isinstance(a, FunctionDefArgument) for a in arguments):
            raise TypeError("arguments must be all be FunctionDefArguments")

        arg_vars = [a.var for a in arguments]

        # body

        if iterable(body):
            body = CodeBlock(body)
        assert isinstance(body, CodeBlock)

        # results
        if results is None:
            results = FunctionDefResult(Nil())
        assert isinstance(results, FunctionDefResult)

        if cls_name:

            if not isinstance(cls_name, str):
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
        self._interfaces = interfaces
        self._result_pointer_map = result_pointer_map
        self._docstring = docstring
        super().__init__(scope)
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
        self._body.remove_user_node(self)
        self._body = body
        self._body.set_current_user_node(self)

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
        tuple_result_vars = [self.results.var]
        return tuple(
            l for l in local_vars if l not in result_vars and not l.is_argument
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
    def interfaces(self):
        """List of interfaces within this function"""
        return self._interfaces

    @property
    def docstring(self):
        """
        The docstring of the function.

        The docstring of the function.
        """
        return self._docstring

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

        args = (newname,) + args[1:]
        new_func = cls(*args, **kwargs)
        return new_func

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
            "interfaces": self._interfaces,
            "docstring": self._docstring,
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
        arguments = [
            a if isinstance(a, FunctionCallArgument) else FunctionCallArgument(a)
            for a in args
        ]
        arguments += [FunctionCallArgument(a, keyword=key) for key, a in kwargs.items()]
        return FunctionCall(self, arguments)

class PyccelFunctionDef(FunctionDef):
    """
    Class used for storing `PyccelFunction` objects in a FunctionDef.

    Class inheriting from `FunctionDef` which can store a pointer
    to a class type defined by pyccel for treating internal functions.
    This is useful for importing builtin functions and for defining
    classes which have `PyccelFunction` objects as attributes or methods.

    Parameters
    ----------
    name : str
        The name of the function.

    func_class : type inheriting from PyccelFunction / TypedAstNode
        The class which should be instantiated upon a FunctionCall
        to this FunctionDef object.

    decorators : dictionary
        A dictionary whose keys are the names of decorators and whose values
        contain their implementation.

    argument_description : dict, optional
        A dictionary containing all arguments and their default values. This
        is useful in order to reuse types with similar functionalities but
        different default values.
    """

    __slots__ = ("_argument_description",)
    class_type = SymbolicType()

    def __init__(self, name, func_class, *, decorators={}, argument_description={}):
        assert isinstance(func_class, type) and issubclass(
            func_class, (PyccelFunction, TypedAstNode)
        )
        assert isinstance(argument_description, dict)
        arguments = ()
        body = ()
        super().__init__(name, arguments, body, decorators=decorators)
        self._cls_name = func_class
        self._argument_description = argument_description

    @property
    def argument_description(self):
        """
        Get a description of the arguments.

        Return a dictionary whose keys are the arguments with default values
        and whose values are the default values for the function described by
        the `PyccelFunctionDef`
        """
        return self._argument_description

    def __call__(self, *args, **kwargs):
        return self._cls_name(*args, **kwargs)


class Interface(PyccelAstNode):
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
    >>> from pyccel.ast.core import Interface, FunctionDef
    >>> f = FunctionDef('F', [], [], [])
    >>> Interface('I', [f])
    """

    __slots__ = (
        "_name",
        "_functions",
        "_is_argument",
        "_is_imported",
        "_syntactic_node",
    )
    _attribute_nodes = ("_functions",)

    def __init__(
        self,
        name,
        functions,
        is_argument=False,
        is_imported=False,
        syntactic_node=None,
    ):

        if not isinstance(name, str):
            raise TypeError("Expecting an str")

        assert iterable(functions)

        self._name = name
        self._functions = tuple(functions)
        self._is_argument = is_argument
        self._is_imported = is_imported
        self._syntactic_node = syntactic_node
        super().__init__()

    @property
    def name(self):
        """Name of the interface."""
        return self._name

    @property
    def functions(self):
        """ "Functions of the interface."""
        return self._functions

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
        Rename the Interface name to a newname.

        Rename the Interface name to a newname.

        Parameters
        ----------
        newname : str
            New name for the Interface.
        """

        self._name = newname

    def clone(self, newname, **new_kwargs):
        """
        Create an almost identical Interface with name `newname`.

        Create an almost identical Interface with name `newname`.
        Additional parameters can be passed to alter the resulting
        FunctionDef.

        Parameters
        ----------
        newname : str
            New name for the Interface.

        **new_kwargs : dict
            Any new keyword arguments to be passed to the new Interface.

        Returns
        -------
        Interface
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
            "syntactic_node": self._syntactic_node,
        }
        return args, kwargs

    def point(self, args):
        """
        Return the actual function that will be called, depending on the passed arguments.

        From the arguments passed in the function call, determine which of the FunctionDef
        objects in the Interface is actually called.

        Parameters
        ----------
        args : tuple[TypedAstNode]
            The arguments passed in the function call.

        Returns
        -------
        FunctionDef
            The function definition which corresponds with the arguments.
        """
        fs_args = [[j for j in i.arguments] for i in self._functions]

        def type_match(call_arg, func_arg):
            """
            Check that the types of the arguments in the function and the call match.
            """
            return call_arg.class_type == func_arg.class_type and (
                call_arg.rank == func_arg.rank
            )

        j = -1
        for i in fs_args:
            j += 1
            found = True
            for x, y in enumerate(args):
                func_arg = i[x].var
                call_arg = y.value
                found = found and type_match(call_arg, func_arg)
            if found:
                break

        if not found:
            raise
            errors.report(
                f"Arguments types provided to {self.name} are incompatible",
                severity="fatal",
            )
        return self._functions[j]

    def __call__(self, *args, **kwargs):
        arguments = [
            a if isinstance(a, FunctionCallArgument) else FunctionCallArgument(a)
            for a in args
        ]
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
    >>> from pyccel.ast.core import Variable, FunctionAddress, FunctionDef
    >>> x = Variable(PythonNativeFloat(), 'x')
    >>> y = Variable(PythonNativeFloat(), 'y')
    >>> # a function definition can have a FunctionAddress as an argument
    >>> FunctionDef('g', [FunctionAddress('f', [x], [y])], [], [])
    """

    __slots__ = ("_is_optional", "_is_kwonly", "_is_argument", "_memory_handling")

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
            raise TypeError(
                "Expecting 'heap', 'stack', 'alias' or None for memory_handling"
            )

        if not isinstance(is_kwonly, bool):
            raise TypeError("Expecting a boolean for kwonly")

        elif not isinstance(is_optional, bool):
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


class ClassDef(ScopedAstNode):
    """
    Represents a class definition.

    Class representing a class definition in the code. It holds all objects
    which may be defined in a class including methods, interfaces, attributes,
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

    interfaces : iterable
        The interface methods.

    docstring : CommentBlock, optional
        The doc string of the class.

    scope : Scope
        The scope for the class contents.

    class_type : PyccelType
        The data type associated with this class.

    decorators : dict
        A dictionary whose keys are the names of decorators and whose values
        contain their implementation.

    Examples
    --------
    >>> from pyccel.ast.core import Variable, Assign
    >>> from pyccel.ast.core import ClassDef, FunctionDef
    >>> x = Variable(PythonNativeFloat(), 'x')
    >>> y = Variable(PythonNativeFloat(), 'y')
    >>> z = Variable(PythonNativeFloat(), 'z')
    >>> t = Variable(PythonNativeFloat(), 't')
    >>> a = Variable(PythonNativeFloat(), 'a')
    >>> b = Variable(PythonNativeFloat(), 'b')
    >>> body = [Assign(y,x+a)]
    >>> translate = FunctionDef('translate', [x,y,a,b], [z,t], body)
    >>> attributes   = [x,y]
    >>> methods     = [translate]
    >>> ClassDef('Point', attributes, methods)
    ClassDef(Point, (x, y), (FunctionDef(translate, (x, y, a, b), (z, t), [y := a + x], [], [], None, False, function),), [public])
    """

    __slots__ = (
        "_name",
        "_attributes",
        "_methods",
        "_class_type",
        "_imports",
        "_superclasses",
        "_interfaces",
        "_docstring",
        "_decorators",
    )
    _attribute_nodes = (
        "_attributes",
        "_methods",
        "_imports",
        "_interfaces",
        "_docstring",
    )

    def __init__(
        self,
        name,
        attributes=(),
        methods=(),
        imports=(),
        superclasses=(),
        interfaces=(),
        docstring=None,
        scope=None,
        class_type=None,
        decorators=(),
    ):

        # name

        if isinstance(name, str):
            name = PyccelSymbol(name)
        else:
            raise TypeError("Class name must be PyccelSymbol or string")

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

            if not isinstance(class_type, PyccelType):
                raise TypeError("class_type must be a PyccelType")

        if not iterable(interfaces):
            raise TypeError("interfaces must be iterable")

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
        self._interfaces = interfaces
        self._docstring = docstring
        self._class_type = class_type
        self._decorators = decorators

        super().__init__(scope=scope)

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
        The PyccelType of an object of the described class.

        The PyccelType of an object of the described class.
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
    def interfaces(self):
        return self._interfaces

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
        return {
            self._scope.get_python_name(m.name) if m.is_semantic else m.name: m
            for m in self.methods
        }

    @property
    def attributes_as_dict(self):
        """Returns a dictionary that contains all attributes, where the key is the
        attribute's name."""

        d_attributes = {}
        for i in self.attributes:
            d_attributes[i.name] = i
        return d_attributes

    def add_new_attribute(self, attr):
        """
        Add a new attribute to the current class.

        Add a new attribute to the current ClassDef.

        Parameters
        ----------
        attr : Variable
            The Variable that will be added.
        """

        if not isinstance(attr, Variable):
            raise TypeError("Attributes must be Variables")
        assert attr not in self._attributes
        attr.set_current_user_node(self)
        self._attributes += (attr,)

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

        method.set_current_user_node(self)
        self._methods += (method,)

    def add_new_interface(self, interface):
        """
        Add a new interface to the current class.

        Add a new interface to the current ClassDef.

        Parameters
        ----------
        interface : FunctionDef
            The interface that will be added.
        """

        if not isinstance(interface, Interface):
            raise TypeError("Argument 'interface' must be of type Interface")
        interface.set_current_user_node(self)
        self._interfaces += (interface,)

    def update_method(self, syntactic_method, semantic_method):
        """
        Replace a syntactic_method with its semantic equivalent.

        Replace a syntactic_method with its semantic equivalent.

        Parameters
        ----------
        syntactic_method : FunctionDef
            The method that has already been added to the class.
        semantic_method : FunctionDef
            The method that will replace the syntactic_method.
        """
        assert isinstance(semantic_method, FunctionDef)
        assert syntactic_method in self._methods
        assert semantic_method.is_semantic
        syntactic_method.remove_user_node(self)
        semantic_method.set_current_user_node(self)
        self._methods = tuple(m for m in self._methods if m is not syntactic_method) + (
            semantic_method,
        )

    def update_interface(self, syntactic_interface, semantic_interface):
        """
        Replace an existing interface with a new interface.

        Replace an existing interface with a new semantic interface.
        When translating a .py file this will always be an operation which
        replaces a syntactic interface with its semantic equivalent.
        The syntactic interface is inserted into the class at its creation
        to ensure that the method can be located when it is called, but
        it is only treated on the first call (or once the rest of the
        enlosing Module has been translated) to ensure that all global
        variables that it may use have been declared. When the method
        is visited to create the semantic version, this method is called
        to update the stored interface.

        When translating a .pyi file, an additional case is seen due to
        the use of the `@overload` decorator. When this decorator is used
        each `FunctionDef` in the `Interface` is visited individually.
        When the first implementation is visited, the syntactic interface
        will be replaced by the semantic interface, but when subsequent
        implementations are visited, the syntactic interface will already
        have been removed, rather it is the previous semantic interface
        (identified by its name) which will be replaced.

        Parameters
        ----------
        syntactic_interface : FunctionDef
            The syntactic interface that should be removed from the class.
            In the case of a .pyi file this interface may not appear in
            the class any more.
        semantic_interface : FunctionDef
            The new interface that should appear in the class.
        """
        assert isinstance(semantic_interface, Interface)
        assert semantic_interface.is_semantic
        if syntactic_interface in self._methods:
            syntactic_interface.remove_user_node(self)
        semantic_interface.set_current_user_node(self)
        self._methods = tuple(m for m in self._methods if m is not syntactic_interface)
        self._interfaces = tuple(
            m
            for m in self._interfaces
            if m is not syntactic_interface and m.name != semantic_interface.name
        ) + (semantic_interface,)

    def get_method(self, name, raise_error_from=None):
        """
        Get the method `name` of the current class.

        Look through all methods and interfaces of the current class to
        find a method called `name`. If this class inherits from another
        class, that class is also searched to ensure that the inherited
        methods are available.

        Parameters
        ----------
        name : str
            The name of the attribute we are looking for.

        raise_error_from : PyccelAstNode, optional
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
            except RuntimeError:
                if raise_error_from:
                    raise
                    errors.report(
                        f"Can't find method {name} in class {self.name}",
                        severity="fatal",
                        symbol=raise_error_from,
                    )
                else:
                    return None

        try:
            method = next(
                i for i in chain(self.methods, self.interfaces) if i.name == name
            )
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
            raise
            errors.report(
                f"Can't find method {name} in class {self.name}",
                severity="fatal",
                symbol=raise_error_from,
            )

        return method

    @property
    def is_iterable(self):
        """Returns True if the class has an iterator."""

        names = [str(m.name) for m in self.methods]
        if "__next__" in names and "__iter__" in names:
            return True
        elif "__next__" in names:
            raise ValueError("ClassDef does not contain __iter__ method")
        elif "__iter__" in names:
            raise ValueError("ClassDef does not contain __next__ method")
        else:
            return False

    @property
    def is_with_construct(self):
        """Returns True if the class is a with construct."""

        names = [str(m.name) for m in self.methods]
        if "__enter__" in names and "__exit__" in names:
            return True
        elif "__enter__" in names:
            raise ValueError("ClassDef does not contain __exit__ method")
        elif "__exit__" in names:
            raise ValueError("ClassDef does not contain __enter__ method")
        else:
            return False

    @property
    def hide(self):
        """
        Indicate whether the class should be hidden.

        Indicate whether the class should be hidden. A hidden class does
        not appear in the printed code.
        """
        return self.is_iterable or self.is_with_construct


class Import(PyccelAstNode):
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
    >>> from pyccel.ast.core import Import
    >>> Import('foo')
    import foo

    >>> Import('foo', 'bar')
    from foo import bar
    """

    __slots__ = ("_source", "_target", "_ignore_at_print", "_source_mod")
    _attribute_nodes = ()

    def __init__(self, source, target=None, ignore_at_print=False, mod=None):

        if not source is None:
            source = Import._format(source)

        self._source = source
        self._target = {}  # Dict is used as Python doesn't have an ordered set
        self._source_mod = mod
        self._ignore_at_print = ignore_at_print

        if mod is None and isinstance(target, Module):
            self._source_mod = target

        if target is None:
            raise KeyError("Missing argument 'target'")
        elif not iterable(target):
            target = [target]

        else:
            for i in target:
                assert isinstance(i, (AsName, Module))
                if isinstance(i, Module):
                    self._target[AsName(i, source)] = None
                else:
                    self._target[i] = None
        super().__init__()

    @staticmethod
    def _format(i):
        """
        Format a string passed to this file into a Pyccel object.

        Format a string passed to this file into a Pyccel object or confirm
        that it is already correctly formatted.

        Parameters
        ----------
        i : Any
            The object to be formatted.

        Returns
        -------
        PyccelSymbol | AsName
            The formatted object.

        Raises
        ------
        TypeError
            Raised if the input is not a string or one of the acceptable
            output types.
        """
        if isinstance(i, str):
            return PyccelSymbol(i)
        if isinstance(i, (AsName, PyccelSymbol, LiteralString)):
            return i
        else:
            raise TypeError(
                f"Expecting a string, PyccelSymbol, given {type(i)}"
            )

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
        else:
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
            self._target.update({t: None for t in new_target})
        else:
            self._target[new_target] = None

    def remove_target(self, target_to_remove):
        """
        Remove a target from the imports.

        Remove a target from the imports.
        I.e., if `imp` is an Import defined as:
        >>> from numpy import ones, cos

        and we call `imp.remove_target('cos')`
        then it becomes:
        >>> from numpy import ones

        Parameters
        ----------
        target_to_remove : str | AsName | iterable[str | AsName]
            The import target(s) to remove.
        """

        if iterable(target_to_remove):
            for t in target_to_remove:
                self._target.pop(t, None)
        else:
            self._target.pop(target_to_remove, None)

    def find_module_target(self, new_target):
        """
        Find the specified target amongst the targets of the Import.

        Find the specified target amongst the targets of the Import.

        Parameters
        ----------
        new_target : str
            The name of the target that has been imported.

        Returns
        -------
        str
            The name of the target in the local scope or None if the
            target is not found.
        """
        for t in self._target:
            if isinstance(t, AsName) and new_target == t.name:
                return t.local_alias
            elif new_target == t:
                return t
        return None

    @property
    def source_module(self):
        """The module describing the Import source"""
        return self._source_mod


# TODO: Should Declare have an optional init value for each var?


# ARA : issue-999 add is_external for external function exported through header files
class Declare(PyccelAstNode):
    """
    Represents a variable declaration in the code.

    Represents a variable declaration in the translated code.

    Parameters
    ----------
    variable : Variable
        A single variable which should be declared.
    intent : str, optional
        One among {'in', 'out', 'inout'}.
    value : TypedAstNode, optional
        The initialisation value of the variable.
    static : bool, default=False
        True for a static declaration of an array.
    external : bool, default=False
        True for a function declared through a header.
    module_variable : bool, default=False
        True for a variable which belongs to a module.

    Examples
    --------
    >>> from pyccel.ast.core import Declare, Variable
    >>> Declare(Variable(PythonNativeInt(), 'n'))
    Declare(n, None)
    >>> Declare(Variable(PythonNativeFloat(), 'x'), intent='out')
    Declare(x, out)
    """

    __slots__ = (
        "_variable",
        "_intent",
        "_value",
        "_static",
        "_external",
        "_module_variable",
    )
    _attribute_nodes = ("_variable", "_value")

    def __init__(
        self,
        variable,
        intent=None,
        value=None,
        static=False,
        external=False,
        module_variable=False,
    ):
        if not isinstance(variable, Variable):
            raise TypeError(f"var must be of type Variable, given {variable}")

        if intent:
            if not intent in ["in", "out", "inout"]:
                raise ValueError("intent must be one among {'in', 'out', 'inout'}")

        if not isinstance(static, bool):
            raise TypeError("Expecting a boolean for static attribute")

        if not isinstance(external, bool):
            raise TypeError("Expecting a boolean for external attribute")

        if not isinstance(module_variable, bool):
            raise TypeError("Expecting a boolean for module_variable attribute")

        self._variable = variable
        self._intent = intent
        self._value = value
        self._static = static
        self._external = external
        self._module_variable = module_variable
        super().__init__()

    @property
    def variable(self):
        return self._variable

    @property
    def intent(self):
        return self._intent

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
        return f"Declare({repr(self.variable)})"

class EmptyNode(PyccelAstNode):
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
    >>> from pyccel.ast.core import EmptyNode
    >>> EmptyNode()

    """

    __slots__ = ()
    _attribute_nodes = ()

    def __str__(self):
        return ""


class Comment(PyccelAstNode):
    """
    Represents a Comment in the code.

    Represents a Comment in the code.

    Parameters
    ----------
    text : str
       The comment line.

    Examples
    --------
    >>> from pyccel.ast.core import Comment
    >>> Comment('this is a comment')
    # this is a comment
    """

    __slots__ = "_text"
    _attribute_nodes = ()

    def __init__(self, text):
        self._text = text
        super().__init__()

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
    >>> from pyccel.ast.core import SeparatorComment
    >>> SeparatorComment(n=40)
    # ........................................
    """

    __slots__ = ()

    def __init__(self, n):
        text = """.""" * n
        super().__init__(text)

class CommentBlock(PyccelAstNode):
    """Represents a Block of Comments

    Parameters
    ----------
    txt : str

    """

    __slots__ = ("_header", "_comments")
    _attribute_nodes = ()

    def __init__(self, txt, header="CommentBlock"):
        if not isinstance(txt, str):
            raise TypeError("txt must be of type str")
        txt = txt.replace('"', "")
        txts = txt.split("\n")

        self._header = header
        self._comments = txts

        super().__init__()

    @property
    def comments(self):
        return self._comments

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, header):
        self._header = header


class Pass(PyccelAstNode):
    """Basic class for pass instruction."""

    __slots__ = ()
    _attribute_nodes = ()


class IfSection(PyccelAstNode):
    """
    Represents one condition and code block in an if statement.

    Represents a condition and associated code block
    in an if statement in the code.

    Parameters
    ----------
    cond : TypedAstNode
           A boolean expression indicating whether or not the block
           should be executed.
    body : CodeBlock
           The code to be executed if the condition is satisfied.

    Examples
    --------
    >>> from pyccel.ast.internals import PyccelSymbol
    >>> from pyccel.ast.core import Assign, IfSection, CodeBlock
    >>> n = PyccelSymbol('n')
    >>> IfSection((n>1), CodeBlock([Assign(n,n-1)]))
    IfSection((n>1), CodeBlock([Assign(n,n-1)]))
    """

    __slots__ = ("_condition", "_block")
    _attribute_nodes = ("_condition", "_block")

    def __init__(self, cond, body):

        assert cond.dtype is PythonNativeBool()

        if isinstance(body, (list, tuple)):
            body = CodeBlock(body)
        elif isinstance(body, CodeBlock):
            body = body
        else:
            raise TypeError("body is not iterable or CodeBlock")

        self._condition = cond
        self._block = body

        super().__init__()

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


class If(PyccelAstNode):
    """
    Represents an if statement in the code.

    Represents an if statement in the code.

    Parameters
    ----------
    *args : IfSection
        All arguments are sections of the complete If block.

    Examples
    --------
    >>> from pyccel.ast.internals import PyccelSymbol
    >>> from pyccel.ast.core import Assign, If
    >>> n = PyccelSymbol('n')
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

        super().__init__()

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

# ------------------------------------------------------------------------------
class MemoryHandlerType(PyccelType):
    """
    The type of an object which can hold a pointer and manage its memory.

    The type of an object which can hold a pointer and manage its memory by
    choosing whether or not to deallocate. This class may be used notably
    for list elements and dictionary values.
    """

    __slots__ = ("_element_type",)

    @classmethod
    @lru_cache
    def get_new(cls, element_type):
        """
        Get the parametrised MemoryHandlerType.

        Get the subclass of MemoryHandlerType describing the type of an
        object which can hold a pointer and manage its memory.

        Parameters
        ----------
        element_type : PyccelType
            The type of the element whose memory is being managed.
        """

        def __init__(self):
            self._element_type = element_type
            PyccelType.__init__(self)

        return type(
            f"MemoryHandlerType[{type(element_type)}]",
            (MemoryHandlerType,),
            {"__init__": __init__},
        )()

    @property
    def element_type(self):
        """
        The type of the element whose memory is being managed.

        The type of the element whose memory is being managed.
        """
        return self._element_type

    @property
    def container_rank(self):
        """
        Number of dimensions of the memory handler object.

        Number of dimensions of the memory handler object.
        This is the number of indices that can be used to
        directly index the object.
        """
        return 0

    @property
    def rank(self):
        """
        Number of dimensions of the object.

        Number of dimensions of the object. This is equal to the
        number of dimensions of the element whose memory is being
        managed.
        """
        return self._element_type.rank

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
        return shape == (() if self.rank else None)

    def __str__(self):
        return f"MemoryHandler[{self._element_type}]"

# ------------------------------------------------------------------------------
class UnpackManagedMemory(PyccelAstNode):
    """
    Assign a pointer to a managed memory block.

    A class representing the operation whereby an object whose memory is managed
    by a MemoryHandlerType is assigned as the target of a pointer.

    Parameters
    ----------
    out_ptr : Variable
        The variable which will point at this memory block.
    managed_object : TypedAstNode
        The object whose memory is being managed.
    mem_var : Variable
        The variable responsible for managing the memory.
    """

    _attribute_nodes = ("_managed_object", "_mem_var", "_out_ptr")
    __slots__ = ("_managed_object", "_mem_var", "_out_ptr")

    def __init__(self, out_ptr, managed_object, mem_var):
        assert isinstance(out_ptr, Variable)
        assert isinstance(managed_object, TypedAstNode)
        assert isinstance(mem_var, Variable)
        self._managed_object = managed_object
        self._mem_var = mem_var
        self._out_ptr = out_ptr
        super().__init__()

    @property
    def out_ptr(self):
        """
        Get the variable which will point at the managed memory block.

        Get the variable which will point at the managed memory block.
        """
        return self._out_ptr

    @property
    def managed_object(self):
        """
        Get the object whose memory is being managed.

        Get the object whose memory is being managed.
        """
        return self._managed_object

    @property
    def memory_handler_var(self):
        """
        Get the variable responsible for managing the memory.

        Get the variable responsible for managing the memory.
        """
        return self._mem_var


# ------------------------------------------------------------------------------
class ManagedMemory(PyccelAstNode):
    """
    A class which links a variable to the variable which manages its memory.

    A class which links a variable to the variable which manages its memory.
    This class does not need to appear in the AST description of the file.
    Simply creating an instance will add it to the AST tree which will ensure
    that it is found when examining the variable.

    Parameters
    ----------
    var : Variable
        The variable whose memory is being managed.
    mem_var : Variable
        The variable responsible for managing the memory.
    """

    __slots__ = ("_var", "_mem_var")
    _attribute_nodes = ("_var", "_mem_var")

    def __init__(self, var, mem_var):
        assert isinstance(var, Variable)
        assert isinstance(mem_var, Variable)
        assert isinstance(mem_var.class_type, MemoryHandlerType)
        self._var = var
        self._mem_var = mem_var
        super().__init__()

    @property
    def var(self):
        """
        Get the variable whose memory is being managed.

        Get the variable whose memory is being managed.
        """
        return self._var

    @property
    def mem_var(self):
        """
        Get the variable responsible for managing the memory.

        Get the variable responsible for managing the memory.
        """
        return self._mem_var

#========================================================================================
class PyccelFunction(TypedAstNode):
    """
    Abstract class for function calls translated to Pyccel objects.

    A subclass of this base class represents calls to a specific internal
    function of Pyccel, which may be simplified at a later stage, or made
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
        super().__init__()

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

    @property
    def modified_args(self):
        """
        Return a tuple of all the arguments which may be modified by this function.

        Return a tuple of all the arguments which may be modified by this function.
        This is notably useful in order to determine the constness of arguments.
        """
        return ()

    @property
    def is_indexable(self):
        """
        Indicate whether the expression can be indexed.

        Indicate whether the expression can be indexed to get an element without
        calculating the entire result. E.g `cos(x)[i]` is equivalent to `cos(x[i])`
        but `func_call(x)[i]` is not equivalent to `func_call(x[i])`.
        """
        return self.is_elemental


class PyccelArraySize(PyccelFunction):
    """
    Gets the total number of elements in an array.

    Class representing a call to a function which would return
    the total number of elements in a multi-dimensional array.

    Parameters
    ----------
    arg : TypedAstNode
        An array of unknown size.
    """

    __slots__ = ()
    name = "size"

    _shape = None
    _class_type = PythonNativeInt()

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
        if isinstance(other, PyccelArraySize):
            return self.arg == other.arg
        else:
            return False


class Slice(PyccelAstNode):
    """
    Represents a slice in the code.

    An object of this class represents the slicing of a Numpy array along one of
    its dimensions. In most cases this corresponds to a Python slice in the user
    code, where it is represented by a `python.ast.Slice` object.

    In addition, at the wrapper and code generation stages, an integer index
    `i` used to create a view of a Numpy array is converted to an object
    `Slice(i, i+1, 1)`. This allows using C
    variadic arguments in the function `array_slicing` (in file
    pyccel/stdlib/ndarrays/ndarrays.c).

    Parameters
    ----------
    start : PyccelSymbol or int
        Starting index.

    stop : PyccelSymbol or int
        Ending index.

    step : PyccelSymbol or int, default=None
        The step between indices.

    Examples
    --------
    >>> from pyccel.ast.internals import Slice, symbols
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

    __slots__ = ("_start", "_stop", "_step")
    _attribute_nodes = ("_start", "_stop", "_step")

    def __init__(self, start, stop, step=None):
        self._start = start
        self._stop = stop
        self._step = step
        super().__init__()

        assert start is None or isinstance(
            getattr(start.dtype, "primitive_type", None), PrimitiveIntegerType
        )
        assert stop is None or isinstance(
            getattr(stop.dtype, "primitive_type", None), PrimitiveIntegerType
        )
        assert step is None or isinstance(
            getattr(step.dtype, "primitive_type", None), PrimitiveIntegerType
        )

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
        if self.start is None:
            start = ""
        else:
            start = str(self.start)
        if self.stop is None:
            stop = ""
        else:
            stop = str(self.stop)
        return f"{start} : {stop} : {self.step}"
