@native_call([Arg(0), Ref(Arg(1))])
def apply_scalar(
    callback: Callable[[Ref(Const(Float64))], Float64],
    value: Const(Float64)
) -> Float64: ...

@native_call([Arg(0), Ref(Arg(1))])
def apply_explicit(
    callback: Callable[[Ref(Const(Float64))], Float64],
    value: Const(Float64)
) -> Float64: ...

@native_call([Arg(0), Ref(Arg(1))])
def call_notify(
    callback: Callable[[Ref(Const(Float64))], None],
    value: Const(Float64)
) -> None: ...
