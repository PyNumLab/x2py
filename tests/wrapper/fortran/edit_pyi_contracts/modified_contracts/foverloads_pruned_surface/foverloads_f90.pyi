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
def convert_integer(
    value: Addr(Const(Int32))
) -> Int32: ...

@private
def convert_real(
    value: Addr(Const(Float64))
) -> Float64: ...

@overload("convert_integer")
def convert(
    value: Addr(Const(Int32))
) -> Int32: ...

@overload("convert_real")
def convert(
    value: Addr(Const(Float64))
) -> Float64: ...
