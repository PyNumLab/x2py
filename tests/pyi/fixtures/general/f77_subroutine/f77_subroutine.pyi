@external
def daxpy(
    n: Addr(Int32),
    a: Addr(Float64),
    x: Float64[n],
    y: Float64[n]
) -> None: ...
