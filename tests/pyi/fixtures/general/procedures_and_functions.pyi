def norm2(
    x: Const(Float64[::Strided])
) -> Float64: ...

def scale(
    a: Ptr(Const(Float64)),
    x: Float64[::Strided]
) -> None: ...
