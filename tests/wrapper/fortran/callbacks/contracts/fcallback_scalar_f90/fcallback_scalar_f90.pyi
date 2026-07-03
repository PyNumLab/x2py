@native_call([Arg(0), Addr(Arg(1))])
def apply_scalar(
    callback: Callable[[Addr(Const(Float64))], Float64],
    value: Const(Float64)
) -> Float64: ...

@native_call([Arg(0), Addr(Arg(1))])
def apply_explicit(
    callback: Callable[[Addr(Const(Float64))], Float64],
    value: Const(Float64)
) -> Float64: ...

@native_call([Arg(0), Addr(Arg(1))])
def call_notify(
    callback: Callable[[Addr(Const(Float64))], None],
    value: Const(Float64)
) -> None: ...
