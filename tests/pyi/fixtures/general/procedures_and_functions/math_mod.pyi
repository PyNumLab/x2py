def norm2(
    x: Const(Float64[::])
) -> Float64: ...

@native_call([Ref(Arg(0)), Arg(1)])
def scale(
    a: Const(Float64),
    x: Float64[::]
) -> None: ...
