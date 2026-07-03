def add1(
    n: Int,
    x: Float64[1]
) -> None: ...

@native_call([Arg(0), Addr(Arg(1)), Arg(2)])
def add1_strided(
    n: Int,
    x: Annotated[Float64, Intent('inout')],
    incx: Int
) -> None: ...
