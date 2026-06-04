def add1(
    n: Int,
    x: Float64[1]
) -> None: ...

def add1_strided(
    n: Int,
    x: Ptr(Float64),
    incx: Int
) -> None: ...
