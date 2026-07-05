from x2py.contracts import Addr, Arg, Float64, native_call

def norm2(
    x: Float64[::]
) -> Float64: ...

@native_call([Addr(Arg(0)), Arg(1)])
def scale(
    a: Float64,
    x: Float64[::]
) -> None: ...
