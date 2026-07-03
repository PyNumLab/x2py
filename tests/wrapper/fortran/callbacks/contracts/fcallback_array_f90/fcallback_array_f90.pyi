@native_call([Arg(0), Addr(Arg(1)), Arg(2)])
def apply_reduce(
    callback: Callable[[Addr(Const(Int32)), Const(Float64[count])], Float64],
    count: Const(Int32),
    values: Const(Float64[count])
) -> Float64: ...

@native_call([Arg(0), Addr(Arg(1)), Arg(2), Arg(3)])
def apply_transform(
    callback: Callable[[Addr(Const(Int32)), Const(Float64[count])], Float64[count]],
    count: Const(Int32),
    values: Const(Float64[count]),
    output: Float64[count]
) -> Returns["output", Float64[count]]: ...
