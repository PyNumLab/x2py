def norm2(
    n: Int,
    x: Const(Float64[1])
) -> Float64: ...

def scale(
    n: Int,
    alpha: Float64,
    x: Float64[1]
) -> None: ...

@native_call([Arg(0), Ref(Arg(1)), Ref(Arg(2))])
def dot(
    n: Int,
    x: Const(Float64),
    y: Const(Float64)
) -> Float64: ...

def fill_identity3(
    a: Float64[3, 3]
) -> None: ...
