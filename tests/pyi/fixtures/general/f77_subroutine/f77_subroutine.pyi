@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Arg(3)])
def daxpy(
    n: Annotated[Int32, Intent('inout')],
    a: Annotated[Float64, Intent('inout')],
    x: Float64[n],
    y: Float64[n]
) -> None: ...
