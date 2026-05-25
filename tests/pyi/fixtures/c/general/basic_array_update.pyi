def add1(
    n: Int32,
    x: Float64[1]
) -> None: ...

def add1_strided(
    n: Int32,
    x: Ptr(Float64),
    incx: Int32
) -> None: ...
