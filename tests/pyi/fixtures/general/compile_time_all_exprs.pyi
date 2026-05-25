a: Final[Int32]

b: Final[Int32]

c: Final[Int32]

p_add: Final[Int32]

p_sub: Final[Int32]

p_mul: Final[Int32]

p_div: Final[Int32]

p_pow: Final[Int32]

p_mix: Final[Int32]

def all_exprs(
    x1: Annotated[Int32[::Strided], ArrayCategory('assumed_shape'), SourceDims('1:p_add')],
    x2: Annotated[Int32[::Strided], ArrayCategory('assumed_shape'), SourceDims('1:p_sub')],
    x3: Annotated[Int32[::Strided], ArrayCategory('assumed_shape'), SourceDims('1:p_mul')],
    x4: Annotated[Int32[::Strided], ArrayCategory('assumed_shape'), SourceDims('1:p_div')],
    x5: Annotated[Int32[::Strided], ArrayCategory('assumed_shape'), SourceDims('1:p_pow')],
    x6: Annotated[Int32[::Strided], ArrayCategory('assumed_shape'), SourceDims('0:p_mix'), LowerBounds('0')],
    x7: Annotated[Int32[::Strided], ArrayCategory('assumed_shape'), SourceDims('1:-(-a + b)')],
    x8: Annotated[Int32[::Strided], ArrayCategory('assumed_shape'), SourceDims('1:(a+b)*(c+1)-1')],
    x9: Annotated[Int32[::Strided], ArrayCategory('assumed_shape'), SourceDims('1:(a-b)*(a-c)')]
) -> None: ...
