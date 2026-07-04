class accumulator:
    def __init__(
        self,
        *,
        total: Float64 = 0.0
    ) -> None: ...

    total: Float64 = 0.0

    @private
    @bind("accumulator_add_integer")
    @native_call([Pass(), Addr(Arg(0))])
    def add_integer(
        self,
        value: Int32
    ) -> None: ...

    @private
    @bind("accumulator_add_real")
    @native_call([Pass(), Addr(Arg(0))])
    def add_real(
        self,
        value: Float64
    ) -> None: ...

    @overload("accumulator_add_integer")
    @native_call([Pass(), Addr(Arg(0))])
    def add(
        self,
        value: Int32
    ) -> None: ...

    @overload("accumulator_add_real")
    @native_call([Pass(), Addr(Arg(0))])
    def add(
        self,
        value: Float64
    ) -> None: ...

class sample:
    def __init__(
        self,
        *,
        value: Float64 = 0.0
    ) -> None: ...

    value: Float64 = 0.0

@private
@native_call([Addr(Arg(0))])
def convert_integer(
    value: Int32
) -> Int32: ...

@private
@native_call([Addr(Arg(0))])
def convert_real(
    value: Float64
) -> Float64: ...

@private
@native_call([Addr(Arg(0))])
def convert_complex(
    value: Complex128
) -> Complex128: ...

@private
@native_call([Addr(Arg(0))])
def summarize_scalar(
    value: Float64
) -> Float64: ...

@private
def summarize_vector(
    values: Float64[::]
) -> Float64: ...

@private
def inspect_accumulator(
    value: accumulator
) -> Float64: ...

@private
def inspect_sample(
    value: sample
) -> Float64: ...

@private
@native_call([Arg(0), Addr(Arg(1))])
def accumulator_add_integer(
    self: Annotated[accumulator, Polymorphic],
    value: Int32
) -> None: ...

@private
@native_call([Arg(0), Addr(Arg(1))])
def accumulator_add_real(
    self: Annotated[accumulator, Polymorphic],
    value: Float64
) -> None: ...

@overload("convert_integer")
@native_call([Addr(Arg(0))])
def convert(
    value: Int32
) -> Int32: ...

@overload("convert_real")
@native_call([Addr(Arg(0))])
def convert(
    value: Float64
) -> Float64: ...

@overload("convert_complex")
@native_call([Addr(Arg(0))])
def convert(
    value: Complex128
) -> Complex128: ...

@overload("summarize_scalar")
@native_call([Addr(Arg(0))])
def summarize(
    value: Float64
) -> Float64: ...

@overload("summarize_vector")
def summarize(
    values: Float64[::]
) -> Float64: ...

@overload("inspect_accumulator")
def inspect(
    value: accumulator
) -> Float64: ...

@overload("inspect_sample")
def inspect(
    value: sample
) -> Float64: ...
