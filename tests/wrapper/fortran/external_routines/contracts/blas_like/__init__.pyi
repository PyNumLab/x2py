@external
def daxpy_like(
    n: Ptr(Const(Int32)),
    alpha: Ptr(Const(Float64)),
    x: Const(Float64[n]),
    y: Float64[n]
) -> None: ...

@external
def ddot_like(
    n: Ptr(Const(Int32)),
    x: Const(Float64[n]),
    y: Const(Float64[n])
) -> Float64: ...
