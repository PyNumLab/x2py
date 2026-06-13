"""
Module handling all Python builtin operators

PyccelOperator
├── PyccelUnaryOperator
│   ├── PyccelAssociativeParenthesis
│   ├── PyccelUnary
│   └── PyccelUnarySub
│
├── PyccelBinaryOperator
│   └── PyccelArithmeticOperator
│       ├── PyccelAdd
│       ├── PyccelMinus
│       ├── PyccelMul
│       ├── PyccelDiv
│       ├── PyccelMod
│       ├── PyccelFloorDiv
│       └── PyccelPow
│
├── PyccelBooleanOperator
│   ├── PyccelAnd
│   ├── PyccelOr
│   │
│   ├── PyccelUnaryBooleanOperator
│   │   └── PyccelNot
│   │
│   └── PyccelBinaryBooleanOperator
│       ├── PyccelIs
│       ├── PyccelIsNot
│       ├── PyccelIn
│       │
│       └── PyccelComparisonOperator
│           ├── PyccelEq
│           ├── PyccelNe
│           ├── PyccelLt
│           ├── PyccelLe
│           ├── PyccelGt
│           └── PyccelGe
│
└── IfTernaryOperator
"""


from .basic import TypedAstNode
from .datatypes import PythonNativeBool

def make_operator_class(name, base, op):
    return type(
        name,
        (base,),
        {
            "__slots__": (),
            "__module__": __name__,
            "op": op,
        }
    )

# ==============================================================================
class PyccelOperator(TypedAstNode):
    __slots__ = ("_args", "_shape", "_class_type")
    _attribute_nodes = ("_args",)
    op = None
    _DEFAULT = object()
    def __init__(self, *args, shape=_DEFAULT, class_type=_DEFAULT):
        self._args = tuple(args)

        self._shape = args[0]._shape if shape is self._DEFAULT else shape
        self._class_type = args[0]._class_type if class_type is self._DEFAULT else class_type

        super().__init__()

    @property
    def args(self):
        return self._args

    def __str__(self):
        return repr(self)

class PyccelUnaryOperator(PyccelOperator):
    __slots__ = ()

    def __repr__(self):
        return f"{self.op}{repr(self.args[0])}"

class PyccelBinaryOperator(PyccelOperator):
    __slots__ = ()

    def __repr__(self):
        return f"{repr(self.args[0])} {self.op} {repr(self.args[1])}"

class PyccelBooleanOperator(PyccelOperator):
    __slots__ = ()

    def __init__(self, *args):
        super().__init__(
            *args,
            shape=None,
            class_type=PythonNativeBool()
        )

    def __repr__(self):
        return f" {self.op} ".join(repr(a) for a in self.args)

class PyccelUnaryBooleanOperator(PyccelBooleanOperator, PyccelUnaryOperator):
    __slots__ = ()
    def __init__(self, arg):
        super().__init__(arg)

    def __repr__(self):
        return PyccelUnaryOperator.__repr__(self)

class PyccelBinaryBooleanOperator(PyccelBooleanOperator, PyccelBinaryOperator):
    __slots__ = ()

    def __init__(self, arg1, arg2):
        super().__init__(arg1, arg2)

class PyccelArithmeticOperator(PyccelBinaryOperator):
    __slots__ = ()

class PyccelComparisonOperator(PyccelBinaryBooleanOperator):
    __slots__ = ()

# ==============================================================================
PyccelUnary    = make_operator_class("PyccelUnary",    PyccelUnaryOperator, "+")
PyccelUnarySub = make_operator_class("PyccelUnarySub", PyccelUnaryOperator, "-")

PyccelNot      = make_operator_class("PyccelNot",    PyccelUnaryBooleanOperator, "not ")

PyccelPow      = make_operator_class("PyccelPow", PyccelArithmeticOperator, "**")
PyccelAdd      = make_operator_class("PyccelAdd", PyccelArithmeticOperator, "+")
PyccelMul      = make_operator_class("PyccelMul", PyccelArithmeticOperator, "*")
PyccelMinus    = make_operator_class("PyccelMinus", PyccelArithmeticOperator, "-")
PyccelDiv      = make_operator_class("PyccelDiv", PyccelArithmeticOperator, "/")
PyccelMod      = make_operator_class("PyccelMod", PyccelArithmeticOperator, "%")
PyccelFloorDiv = make_operator_class("PyccelFloorDiv", PyccelArithmeticOperator, "//")

PyccelEq = make_operator_class("PyccelEq", PyccelComparisonOperator, "==")
PyccelNe = make_operator_class("PyccelNe", PyccelComparisonOperator, "!=")
PyccelLt = make_operator_class("PyccelLt", PyccelComparisonOperator, "<")
PyccelLe = make_operator_class("PyccelLe", PyccelComparisonOperator, "<=")
PyccelGt = make_operator_class("PyccelGt", PyccelComparisonOperator, ">")
PyccelGe = make_operator_class("PyccelGe", PyccelComparisonOperator, ">=")

PyccelAnd   = make_operator_class("PyccelAnd",   PyccelBooleanOperator, "and")
PyccelOr    = make_operator_class("PyccelOr",    PyccelBooleanOperator, "or")
PyccelIs    = make_operator_class("PyccelIs",    PyccelBinaryBooleanOperator, "is")
PyccelIsNot = make_operator_class("PyccelIsNot", PyccelBinaryBooleanOperator, "is not")
PyccelIn    = make_operator_class("PyccelIn",    PyccelBinaryBooleanOperator, "in")
# ==============================================================================
class PyccelAssociativeParenthesis(PyccelUnaryOperator):
    __slots__ = ()

    def __repr__(self):
        return f"({repr(self.args[0])})"

class IfTernaryOperator(PyccelOperator):
    """
    Represent a ternary conditional operator in the code.

    Represent a ternary conditional operator in the code,
    of the form (a if cond else b).

    Parameters
    ----------
    cond : TypedAstNode
        The condition which determines which result is returned.
    value_true : TypedAstNode
        The value returned if the condition is true.
    value_false : TypedAstNode
        The value returned if the condition is false.

    Examples
    --------
    >>> from pyccel.ast.internals import PyccelSymbol
    >>> from pyccel.ast.core import Assign
    >>> from pyccel.ast.operators import IfTernaryOperator
    >>> n = PyccelSymbol('n')
    >>> x = 5 if n > 1 else 2
    >>> IfTernaryOperator(PyccelGt(n > 1),  5,  2)
    IfTernaryOperator(PyccelGt(n > 1),  5,  2)
    """

    __slots__ = ()

    def __init__(self, cond, value_true, value_false):
        super().__init__(
            cond,
            value_true,
            value_false,
            shape=value_true._shape,
            class_type=value_true._class_type
        )

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

