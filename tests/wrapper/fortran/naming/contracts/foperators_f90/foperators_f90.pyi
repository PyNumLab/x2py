class vector:
    def __init__(
        self,
        *,
        value: Float64 = 0.0
    ) -> None: ...

    value: Float64 = 0.0

    @overload("add_vectors")
    def __add__(
        self,
        right: Ref(Const(vector))
    ) -> vector: ...

    @overload("add_vector_integer")
    @native_call([Pass(), Ref(Arg(0))])
    def __add__(
        self,
        right: Const(Int32)
    ) -> vector: ...

    @overload("add_vector_real")
    @native_call([Pass(), Ref(Arg(0))])
    def __add__(
        self,
        right: Const(Float64)
    ) -> vector: ...

    @overload("add_real_vector")
    @native_call([Ref(Arg(0)), Pass()])
    def __radd__(
        self,
        left: Const(Float64)
    ) -> vector: ...

    @overload("add_vector_array")
    def __add__(
        self,
        right: Const(Float64[::])
    ) -> vector: ...

    @overload("add_vector_offset")
    def __add__(
        self,
        right: Ref(Const(offset))
    ) -> vector: ...

    @overload("positive_vector")
    def __pos__(self) -> vector: ...

    @overload("subtract_vector_real")
    @native_call([Pass(), Ref(Arg(0))])
    def __sub__(
        self,
        right: Const(Float64)
    ) -> vector: ...

    @overload("subtract_real_vector")
    @native_call([Ref(Arg(0)), Pass()])
    def __rsub__(
        self,
        left: Const(Float64)
    ) -> vector: ...

    @overload("negative_vector")
    def __neg__(self) -> vector: ...

    @overload("multiply_vector_real")
    @native_call([Pass(), Ref(Arg(0))])
    def __mul__(
        self,
        right: Const(Float64)
    ) -> vector: ...

    @overload("divide_vector_real")
    @native_call([Pass(), Ref(Arg(0))])
    def __truediv__(
        self,
        right: Const(Float64)
    ) -> vector: ...

    @overload("power_vector_integer")
    @native_call([Pass(), Ref(Arg(0))])
    def __pow__(
        self,
        right: Const(Int32)
    ) -> vector: ...

    @overload("equal_vectors")
    def __eq__(
        self,
        right: Ref(Const(vector))
    ) -> Bool: ...

    @overload("equivalent_vector_offset", generic="operator(.eqv.)")
    def __eq__(
        self,
        right: Ref(Const(offset))
    ) -> Bool: ...

    @overload("not_equal_vectors")
    def __ne__(
        self,
        right: Ref(Const(vector))
    ) -> Bool: ...

    @overload("not_equivalent_vector_integer", generic="operator(.neqv.)")
    @native_call([Pass(), Ref(Arg(0))])
    def __ne__(
        self,
        right: Const(Int32)
    ) -> Bool: ...

    @overload("less_vectors")
    def __lt__(
        self,
        right: Ref(Const(vector))
    ) -> Bool: ...

    @overload("less_vector_real")
    @native_call([Pass(), Ref(Arg(0))])
    def __lt__(
        self,
        right: Const(Float64)
    ) -> Bool: ...

    @overload("less_real_vector")
    @native_call([Ref(Arg(0)), Pass()])
    def __gt__(
        self,
        left: Const(Float64)
    ) -> Bool: ...

    @overload("greater_vectors")
    def __gt__(
        self,
        right: Ref(Const(vector))
    ) -> Bool: ...

    @overload("less_equal_vectors")
    def __le__(
        self,
        right: Ref(Const(vector))
    ) -> Bool: ...

    @overload("greater_equal_vectors")
    def __ge__(
        self,
        right: Ref(Const(vector))
    ) -> Bool: ...

    @overload("and_vectors")
    def __and__(
        self,
        right: Ref(Const(vector))
    ) -> Bool: ...

    @overload("or_vectors")
    def __or__(
        self,
        right: Ref(Const(vector))
    ) -> Bool: ...

    @overload("not_vector")
    def __invert__(self) -> Bool: ...

    @overload("dot_vectors")
    def operator_dot(
        self,
        right: Ref(Const(vector))
    ) -> Float64: ...

    @overload("shift_real_vector")
    @native_call([Ref(Arg(0)), Pass()])
    def r_operator_shift(
        self,
        left: Const(Float64)
    ) -> vector: ...

    @overload("assign_vector_integer")
    @native_call([Pass(), Ref(Arg(0))])
    def assign(
        self,
        right: Const(Int32)
    ) -> vector: ...

    @overload("assign_vector_real")
    @native_call([Pass(), Ref(Arg(0))])
    def assign(
        self,
        right: Const(Float64)
    ) -> vector: ...

class offset:
    def __init__(
        self,
        *,
        value: Float64 = 0.0
    ) -> None: ...

    value: Float64 = 0.0

    @overload("add_vector_offset")
    @native_call([Arg(0), Pass()])
    def __radd__(
        self,
        left: Ref(Const(vector))
    ) -> vector: ...

    @overload("equivalent_vector_offset", generic="operator(.eqv.)")
    @native_call([Arg(0), Pass()])
    def __eq__(
        self,
        left: Ref(Const(vector))
    ) -> Bool: ...

class counter:
    def __init__(
        self,
        *,
        value: Int32 = 0
    ) -> None: ...

    value: Int32 = 0

    @private
    @bind("counter_add_integer")
    @native_call([Pass(), Ref(Arg(0))])
    def add_integer(
        self,
        right: Const(Int32)
    ) -> counter: ...

    @overload("counter_add_integer")
    @native_call([Pass(), Ref(Arg(0))])
    def __add__(
        self,
        right: Const(Int32)
    ) -> counter: ...

@private
@native_call([Ref(Arg(0))])
def convert_integer(
    value: Const(Int32)
) -> Int32: ...

@private
@native_call([Ref(Arg(0))])
def convert_real(
    value: Const(Float64)
) -> Float64: ...

@private
def add_vectors(
    left: Ref(Const(vector)),
    right: Ref(Const(vector))
) -> vector: ...

@private
@native_call([Arg(0), Ref(Arg(1))])
def add_vector_integer(
    left: Ref(Const(vector)),
    right: Const(Int32)
) -> vector: ...

@private
@native_call([Arg(0), Ref(Arg(1))])
def add_vector_real(
    left: Ref(Const(vector)),
    right: Const(Float64)
) -> vector: ...

@private
@native_call([Ref(Arg(0)), Arg(1)])
def add_real_vector(
    left: Const(Float64),
    right: Ref(Const(vector))
) -> vector: ...

@private
def add_vector_array(
    left: Ref(Const(vector)),
    right: Const(Float64[::])
) -> vector: ...

@private
def add_vector_offset(
    left: Ref(Const(vector)),
    right: Ref(Const(offset))
) -> vector: ...

@private
def positive_vector(
    value: Ref(Const(vector))
) -> vector: ...

@private
@native_call([Arg(0), Ref(Arg(1))])
def subtract_vector_real(
    left: Ref(Const(vector)),
    right: Const(Float64)
) -> vector: ...

@private
@native_call([Ref(Arg(0)), Arg(1)])
def subtract_real_vector(
    left: Const(Float64),
    right: Ref(Const(vector))
) -> vector: ...

@private
def negative_vector(
    value: Ref(Const(vector))
) -> vector: ...

@private
@native_call([Arg(0), Ref(Arg(1))])
def multiply_vector_real(
    left: Ref(Const(vector)),
    right: Const(Float64)
) -> vector: ...

@private
@native_call([Arg(0), Ref(Arg(1))])
def divide_vector_real(
    left: Ref(Const(vector)),
    right: Const(Float64)
) -> vector: ...

@private
@native_call([Arg(0), Ref(Arg(1))])
def power_vector_integer(
    left: Ref(Const(vector)),
    right: Const(Int32)
) -> vector: ...

@private
def equal_vectors(
    left: Ref(Const(vector)),
    right: Ref(Const(vector))
) -> Bool: ...

@private
def not_equal_vectors(
    left: Ref(Const(vector)),
    right: Ref(Const(vector))
) -> Bool: ...

@private
def less_vectors(
    left: Ref(Const(vector)),
    right: Ref(Const(vector))
) -> Bool: ...

@private
@native_call([Arg(0), Ref(Arg(1))])
def less_vector_real(
    left: Ref(Const(vector)),
    right: Const(Float64)
) -> Bool: ...

@private
@native_call([Ref(Arg(0)), Arg(1)])
def less_real_vector(
    left: Const(Float64),
    right: Ref(Const(vector))
) -> Bool: ...

@private
def less_equal_vectors(
    left: Ref(Const(vector)),
    right: Ref(Const(vector))
) -> Bool: ...

@private
def greater_vectors(
    left: Ref(Const(vector)),
    right: Ref(Const(vector))
) -> Bool: ...

@private
def greater_equal_vectors(
    left: Ref(Const(vector)),
    right: Ref(Const(vector))
) -> Bool: ...

@private
def and_vectors(
    left: Ref(Const(vector)),
    right: Ref(Const(vector))
) -> Bool: ...

@private
def or_vectors(
    left: Ref(Const(vector)),
    right: Ref(Const(vector))
) -> Bool: ...

@private
def not_vector(
    value: Ref(Const(vector))
) -> Bool: ...

@private
def equivalent_vector_offset(
    left: Ref(Const(vector)),
    right: Ref(Const(offset))
) -> Bool: ...

@private
@native_call([Arg(0), Ref(Arg(1))])
def not_equivalent_vector_integer(
    left: Ref(Const(vector)),
    right: Const(Int32)
) -> Bool: ...

@private
def dot_vectors(
    left: Ref(Const(vector)),
    right: Ref(Const(vector))
) -> Float64: ...

@private
@native_call([Ref(Arg(0)), Arg(1)])
def shift_real_vector(
    left: Const(Float64),
    right: Ref(Const(vector))
) -> vector: ...

@private
@native_call([Arg(0), Ref(Arg(1))])
def assign_vector_integer(
    left: Ref(vector),
    right: Const(Int32)
) -> Returns["left", Ref(vector)]: ...

@private
@native_call([Arg(0), Ref(Arg(1))])
def assign_vector_real(
    left: Ref(vector),
    right: Const(Float64)
) -> Returns["left", Ref(vector)]: ...

@private
@native_call([Arg(0), Ref(Arg(1))])
def counter_add_integer(
    self: Annotated[Ref(Const(counter)), Polymorphic],
    right: Const(Int32)
) -> counter: ...

@overload("convert_integer")
@native_call([Ref(Arg(0))])
def convert(
    value: Const(Int32)
) -> Int32: ...

@overload("convert_real")
@native_call([Ref(Arg(0))])
def convert(
    value: Const(Float64)
) -> Float64: ...
