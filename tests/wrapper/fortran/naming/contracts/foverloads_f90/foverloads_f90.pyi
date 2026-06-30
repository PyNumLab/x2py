class accumulator:
    def __init__(
        self,
        *,
        total: Float64 = 0.0
    ) -> None: ...

    total: Float64 = 0.0

    @private
    @bind("accumulator_add_integer")
    @native_call([Pass(), Ref(Arg(0))])
    def add_integer(
        self,
        value: Const(Int32)
    ) -> None: ...

    @private
    @bind("accumulator_add_real")
    @native_call([Pass(), Ref(Arg(0))])
    def add_real(
        self,
        value: Const(Float64)
    ) -> None: ...

    @overload("accumulator_add_integer")
    @native_call([Pass(), Ref(Arg(0))])
    def add(
        self,
        value: Const(Int32)
    ) -> None: ...

    @overload("accumulator_add_real")
    @native_call([Pass(), Ref(Arg(0))])
    def add(
        self,
        value: Const(Float64)
    ) -> None: ...

class sample:
    def __init__(
        self,
        *,
        value: Float64 = 0.0
    ) -> None: ...

    value: Float64 = 0.0

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
@native_call([Ref(Arg(0))])
def convert_complex(
    value: Const(Complex128)
) -> Complex128: ...

@private
@native_call([Ref(Arg(0))])
def summarize_scalar(
    value: Const(Float64)
) -> Float64: ...

@private
def summarize_vector(
    values: Const(Float64[::Strided])
) -> Float64: ...

@private
def inspect_accumulator(
    value: Ref(Const(accumulator))
) -> Float64: ...

@private
def inspect_sample(
    value: Ref(Const(sample))
) -> Float64: ...

@private
@native_call([Arg(0), Ref(Arg(1))])
def accumulator_add_integer(
    self: Annotated[Ref(accumulator), Polymorphic],
    value: Const(Int32)
) -> None: ...

@private
@native_call([Arg(0), Ref(Arg(1))])
def accumulator_add_real(
    self: Annotated[Ref(accumulator), Polymorphic],
    value: Const(Float64)
) -> None: ...

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

@overload("convert_complex")
@native_call([Ref(Arg(0))])
def convert(
    value: Const(Complex128)
) -> Complex128: ...

@overload("summarize_scalar")
@native_call([Ref(Arg(0))])
def summarize(
    value: Const(Float64)
) -> Float64: ...

@overload("summarize_vector")
def summarize(
    values: Const(Float64[::Strided])
) -> Float64: ...

@overload("inspect_accumulator")
def inspect(
    value: Ref(Const(accumulator))
) -> Float64: ...

@overload("inspect_sample")
def inspect(
    value: Ref(Const(sample))
) -> Float64: ...
