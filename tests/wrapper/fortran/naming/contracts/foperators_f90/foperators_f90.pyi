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
        right: Ptr(Const(vector))
    ) -> vector: ...

    @overload("add_vector_integer")
    def __add__(
        self,
        right: Ptr(Const(Int32))
    ) -> vector: ...

    @overload("add_vector_real")
    def __add__(
        self,
        right: Ptr(Const(Float64))
    ) -> vector: ...

    @overload("add_real_vector")
    @native_call([Arg(0), Pass()])
    def __radd__(
        self,
        left: Ptr(Const(Float64))
    ) -> vector: ...

    @overload("add_vector_array")
    def __add__(
        self,
        right: Const(Float64[::Strided])
    ) -> vector: ...

    @overload("add_vector_offset")
    def __add__(
        self,
        right: Ptr(Const(offset))
    ) -> vector: ...

    @overload("positive_vector")
    def __pos__(self) -> vector: ...

    @overload("subtract_vector_real")
    def __sub__(
        self,
        right: Ptr(Const(Float64))
    ) -> vector: ...

    @overload("subtract_real_vector")
    @native_call([Arg(0), Pass()])
    def __rsub__(
        self,
        left: Ptr(Const(Float64))
    ) -> vector: ...

    @overload("negative_vector")
    def __neg__(self) -> vector: ...

    @overload("multiply_vector_real")
    def __mul__(
        self,
        right: Ptr(Const(Float64))
    ) -> vector: ...

    @overload("divide_vector_real")
    def __truediv__(
        self,
        right: Ptr(Const(Float64))
    ) -> vector: ...

    @overload("power_vector_integer")
    def __pow__(
        self,
        right: Ptr(Const(Int32))
    ) -> vector: ...

    @overload("equal_vectors")
    def __eq__(
        self,
        right: Ptr(Const(vector))
    ) -> Bool: ...

    @overload("equivalent_vector_offset", generic="operator(.eqv.)")
    def __eq__(
        self,
        right: Ptr(Const(offset))
    ) -> Bool: ...

    @overload("not_equal_vectors")
    def __ne__(
        self,
        right: Ptr(Const(vector))
    ) -> Bool: ...

    @overload("not_equivalent_vector_integer", generic="operator(.neqv.)")
    def __ne__(
        self,
        right: Ptr(Const(Int32))
    ) -> Bool: ...

    @overload("less_vectors")
    def __lt__(
        self,
        right: Ptr(Const(vector))
    ) -> Bool: ...

    @overload("less_vector_real")
    def __lt__(
        self,
        right: Ptr(Const(Float64))
    ) -> Bool: ...

    @overload("less_real_vector")
    @native_call([Arg(0), Pass()])
    def __gt__(
        self,
        left: Ptr(Const(Float64))
    ) -> Bool: ...

    @overload("greater_vectors")
    def __gt__(
        self,
        right: Ptr(Const(vector))
    ) -> Bool: ...

    @overload("less_equal_vectors")
    def __le__(
        self,
        right: Ptr(Const(vector))
    ) -> Bool: ...

    @overload("greater_equal_vectors")
    def __ge__(
        self,
        right: Ptr(Const(vector))
    ) -> Bool: ...

    @overload("and_vectors")
    def __and__(
        self,
        right: Ptr(Const(vector))
    ) -> Bool: ...

    @overload("or_vectors")
    def __or__(
        self,
        right: Ptr(Const(vector))
    ) -> Bool: ...

    @overload("not_vector")
    def __invert__(self) -> Bool: ...

    @overload("dot_vectors")
    def operator_dot(
        self,
        right: Ptr(Const(vector))
    ) -> Float64: ...

    @overload("shift_real_vector")
    @native_call([Arg(0), Pass()])
    def r_operator_shift(
        self,
        left: Ptr(Const(Float64))
    ) -> vector: ...

    @overload("assign_vector_integer")
    def assign(
        self,
        right: Ptr(Const(Int32))
    ) -> vector: ...

    @overload("assign_vector_real")
    def assign(
        self,
        right: Ptr(Const(Float64))
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
        left: Ptr(Const(vector))
    ) -> vector: ...

    @overload("equivalent_vector_offset", generic="operator(.eqv.)")
    @native_call([Arg(0), Pass()])
    def __eq__(
        self,
        left: Ptr(Const(vector))
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
    def add_integer(
        self,
        right: Ptr(Const(Int32))
    ) -> counter: ...

    @overload("counter_add_integer")
    def __add__(
        self,
        right: Ptr(Const(Int32))
    ) -> counter: ...

@private
def convert_integer(
    value: Ptr(Const(Int32))
) -> Int32: ...

@private
def convert_real(
    value: Ptr(Const(Float64))
) -> Float64: ...

@private
def add_vectors(
    left: Ptr(Const(vector)),
    right: Ptr(Const(vector))
) -> vector: ...

@private
def add_vector_integer(
    left: Ptr(Const(vector)),
    right: Ptr(Const(Int32))
) -> vector: ...

@private
def add_vector_real(
    left: Ptr(Const(vector)),
    right: Ptr(Const(Float64))
) -> vector: ...

@private
def add_real_vector(
    left: Ptr(Const(Float64)),
    right: Ptr(Const(vector))
) -> vector: ...

@private
def add_vector_array(
    left: Ptr(Const(vector)),
    right: Const(Float64[::Strided])
) -> vector: ...

@private
def add_vector_offset(
    left: Ptr(Const(vector)),
    right: Ptr(Const(offset))
) -> vector: ...

@private
def positive_vector(
    value: Ptr(Const(vector))
) -> vector: ...

@private
def subtract_vector_real(
    left: Ptr(Const(vector)),
    right: Ptr(Const(Float64))
) -> vector: ...

@private
def subtract_real_vector(
    left: Ptr(Const(Float64)),
    right: Ptr(Const(vector))
) -> vector: ...

@private
def negative_vector(
    value: Ptr(Const(vector))
) -> vector: ...

@private
def multiply_vector_real(
    left: Ptr(Const(vector)),
    right: Ptr(Const(Float64))
) -> vector: ...

@private
def divide_vector_real(
    left: Ptr(Const(vector)),
    right: Ptr(Const(Float64))
) -> vector: ...

@private
def power_vector_integer(
    left: Ptr(Const(vector)),
    right: Ptr(Const(Int32))
) -> vector: ...

@private
def equal_vectors(
    left: Ptr(Const(vector)),
    right: Ptr(Const(vector))
) -> Bool: ...

@private
def not_equal_vectors(
    left: Ptr(Const(vector)),
    right: Ptr(Const(vector))
) -> Bool: ...

@private
def less_vectors(
    left: Ptr(Const(vector)),
    right: Ptr(Const(vector))
) -> Bool: ...

@private
def less_vector_real(
    left: Ptr(Const(vector)),
    right: Ptr(Const(Float64))
) -> Bool: ...

@private
def less_real_vector(
    left: Ptr(Const(Float64)),
    right: Ptr(Const(vector))
) -> Bool: ...

@private
def less_equal_vectors(
    left: Ptr(Const(vector)),
    right: Ptr(Const(vector))
) -> Bool: ...

@private
def greater_vectors(
    left: Ptr(Const(vector)),
    right: Ptr(Const(vector))
) -> Bool: ...

@private
def greater_equal_vectors(
    left: Ptr(Const(vector)),
    right: Ptr(Const(vector))
) -> Bool: ...

@private
def and_vectors(
    left: Ptr(Const(vector)),
    right: Ptr(Const(vector))
) -> Bool: ...

@private
def or_vectors(
    left: Ptr(Const(vector)),
    right: Ptr(Const(vector))
) -> Bool: ...

@private
def not_vector(
    value: Ptr(Const(vector))
) -> Bool: ...

@private
def equivalent_vector_offset(
    left: Ptr(Const(vector)),
    right: Ptr(Const(offset))
) -> Bool: ...

@private
def not_equivalent_vector_integer(
    left: Ptr(Const(vector)),
    right: Ptr(Const(Int32))
) -> Bool: ...

@private
def dot_vectors(
    left: Ptr(Const(vector)),
    right: Ptr(Const(vector))
) -> Float64: ...

@private
def shift_real_vector(
    left: Ptr(Const(Float64)),
    right: Ptr(Const(vector))
) -> vector: ...

@private
@native_call([Arg(0), Arg(1)])
def assign_vector_integer(
    left: Ptr(vector),
    right: Ptr(Const(Int32))
) -> Returns["left", Ptr(vector)]: ...

@private
@native_call([Arg(0), Arg(1)])
def assign_vector_real(
    left: Ptr(vector),
    right: Ptr(Const(Float64))
) -> Returns["left", Ptr(vector)]: ...

@private
def counter_add_integer(
    self: Annotated[Ptr(Const(counter)), Polymorphic],
    right: Ptr(Const(Int32))
) -> counter: ...

@overload("convert_integer")
def convert(
    value: Ptr(Const(Int32))
) -> Int32: ...

@overload("convert_real")
def convert(
    value: Ptr(Const(Float64))
) -> Float64: ...
