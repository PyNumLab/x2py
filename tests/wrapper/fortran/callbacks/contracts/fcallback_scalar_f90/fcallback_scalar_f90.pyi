from x2py.contracts import Addr, Arg, Callable, Float64, In, native_call

@native_call([Arg(0), Addr(Arg(1))])
def apply_scalar(
    callback: Callable[[In(Float64)], Float64],
    value: Float64
) -> Float64: ...

@native_call([Arg(0), Addr(Arg(1))])
def apply_explicit(
    callback: Callable[[In(Float64)], Float64],
    value: Float64
) -> Float64: ...

@native_call([Arg(0), Addr(Arg(1))])
def call_notify(
    callback: Callable[[In(Float64)], None],
    value: Float64
) -> None: ...
