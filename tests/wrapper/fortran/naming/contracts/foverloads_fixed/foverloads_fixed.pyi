@private
@native_call([Addr(Arg(0))])
def convert_integer(
    value: Const(Int32)
) -> Int32: ...

@private
@native_call([Addr(Arg(0))])
def convert_real(
    value: Const(Float64)
) -> Float64: ...

@overload("convert_integer")
@native_call([Addr(Arg(0))])
def convert(
    value: Const(Int32)
) -> Int32: ...

@overload("convert_real")
@native_call([Addr(Arg(0))])
def convert(
    value: Const(Float64)
) -> Float64: ...
