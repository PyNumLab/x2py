@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Arg(3)])
def daxpy_like(
    n: Const(Int32),
    alpha: Const(Float64),
    x: Const(Float64[n]),
    y: Float64[n]
) -> None: ...

@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def ddot_like(
    n: Const(Int32),
    x: Const(Float64[n]),
    y: Const(Float64[n])
) -> Float64: ...
