# Intentional difference: remove class sample, remove accumulator.add, and
# remove the complex overload candidate while leaving the integer/real generic.
class accumulator:
    def __init__(
        self,
        *,
        total: Float64 = 0.0
    ) -> None: ...

    total: Float64 = 0.0

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
