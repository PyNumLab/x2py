n0: Final[Int32]

n1: Final[Int32]

def use_expr(
    x: Annotated[Int32[::Strided], ArrayCategory('assumed_shape'), SourceDims('0:n1-1'), LowerBounds('0')],
    y: Annotated[Float64[::Strided], ArrayCategory('assumed_shape'), SourceDims('1:n0*2')]
) -> None: ...
