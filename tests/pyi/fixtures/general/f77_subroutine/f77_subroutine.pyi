@external
def daxpy(
    n: Ref(Int32),
    a: Ref(Float64),
    x: Float64[n],
    y: Float64[n]
) -> None: ...
