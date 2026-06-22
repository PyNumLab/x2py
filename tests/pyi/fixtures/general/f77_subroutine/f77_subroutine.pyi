@external
def daxpy(
    n: Ptr(Int32),
    a: Ptr(Float64),
    x: Float64[n],
    y: Float64[n]
) -> None: ...
