def apply_scalar(
    callback: Callable[[Ptr(Const(Float64))], Float64],
    value: Ptr(Const(Float64))
) -> Float64: ...

def apply_explicit(
    callback: Callable[[Ptr(Const(Float64))], Float64],
    value: Ptr(Const(Float64))
) -> Float64: ...

def call_notify(
    callback: Callable[[Ptr(Const(Float64))], None],
    value: Ptr(Const(Float64))
) -> None: ...
