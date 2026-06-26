class accumulator:
    def __init__(
        self,
        *,
        total: Float64 = 0.0
    ) -> None: ...

    total: Float64 = 0.0

    @private
    @bind("accumulator_add_integer")
    def add_integer(
        self,
        value: Ptr(Const(Int32))
    ) -> None: ...

    @private
    @bind("accumulator_add_real")
    def add_real(
        self,
        value: Ptr(Const(Float64))
    ) -> None: ...

    @overload("accumulator_add_integer")
    def add(
        self,
        value: Ptr(Const(Int32))
    ) -> None: ...

    @overload("accumulator_add_real")
    def add(
        self,
        value: Ptr(Const(Float64))
    ) -> None: ...

class sample:
    def __init__(
        self,
        *,
        value: Float64 = 0.0
    ) -> None: ...

    value: Float64 = 0.0

@private
def convert_integer(
    value: Ptr(Const(Int32))
) -> Int32: ...

@private
def convert_real(
    value: Ptr(Const(Float64))
) -> Float64: ...

@private
def convert_complex(
    value: Ptr(Const(Complex128))
) -> Complex128: ...

@private
def summarize_scalar(
    value: Ptr(Const(Float64))
) -> Float64: ...

@private
def summarize_vector(
    values: Const(Float64[::Strided])
) -> Float64: ...

@private
def inspect_accumulator(
    value: Ptr(Const(accumulator))
) -> Float64: ...

@private
def inspect_sample(
    value: Ptr(Const(sample))
) -> Float64: ...

@private
def accumulator_add_integer(
    self: Annotated[Ptr(accumulator), Polymorphic],
    value: Ptr(Const(Int32))
) -> None: ...

@private
def accumulator_add_real(
    self: Annotated[Ptr(accumulator), Polymorphic],
    value: Ptr(Const(Float64))
) -> None: ...

@overload("convert_integer")
def convert(
    value: Ptr(Const(Int32))
) -> Int32: ...

@overload("convert_real")
def convert(
    value: Ptr(Const(Float64))
) -> Float64: ...

@overload("convert_complex")
def convert(
    value: Ptr(Const(Complex128))
) -> Complex128: ...

@overload("summarize_scalar")
def summarize(
    value: Ptr(Const(Float64))
) -> Float64: ...

@overload("summarize_vector")
def summarize(
    values: Const(Float64[::Strided])
) -> Float64: ...

@overload("inspect_accumulator")
def inspect(
    value: Ptr(Const(accumulator))
) -> Float64: ...

@overload("inspect_sample")
def inspect(
    value: Ptr(Const(sample))
) -> Float64: ...
