def apply_reduce(
    callback: Callable[[Ptr(Const(Int32)), Const(Float64[count])], Float64],
    count: Ptr(Const(Int32)),
    values: Const(Float64[count])
) -> Float64: ...

@native_call([Arg(0), Arg(1), Arg(2), Arg(3)])
def apply_transform(
    callback: Callable[[Ptr(Const(Int32)), Const(Float64[count])], Float64[count]],
    count: Ptr(Const(Int32)),
    values: Const(Float64[count]),
    output: Float64[count]
) -> Returns["output", Float64[count]]: ...
