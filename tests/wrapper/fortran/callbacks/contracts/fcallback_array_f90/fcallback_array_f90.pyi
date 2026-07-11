from x2py.contracts import Addr, Arg, Callable, Float64, In, Int32, Returns, native_call

@native_call([Arg(0), Addr(Arg(1)), Arg(2)])
def apply_reduce(
    callback: Callable[[In(Int32), In(Float64[count])], Float64],
    count: Int32,
    values: Float64[count]
) -> Float64: ...

@native_call([Arg(0), Addr(Arg(1)), Arg(2), Arg(3)])
def apply_transform(
    callback: Callable[[In(Int32), In(Float64[count])], Float64[count]],
    count: Int32,
    values: Float64[count],
    output: Float64[count]
) -> Returns["output", Float64[count]]: ...
