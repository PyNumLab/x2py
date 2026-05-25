def norm2(
    x: Annotated[Const(Float64[::Strided]), ArrayCategory('assumed_shape'), SourceDims(':')]
) -> Float64: ...

def scale(
    a: Ptr(Const(Float64)),
    x: Annotated[Float64[::Strided], ArrayCategory('assumed_shape'), SourceDims(':')]
) -> None: ...
