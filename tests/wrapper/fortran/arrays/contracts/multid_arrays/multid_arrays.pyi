def scale2_contiguous(
    a: Annotated[Const(Float64[:, :]), ORDER_F],
    out: Annotated[Float64[:, :], ORDER_F]
) -> Returns["out", Annotated[Float64[:, :], ORDER_F]]: ...

def scale2_strided(
    a: Annotated[Const(Float64[::, ::]), ORDER_F],
    out: Annotated[Float64[::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::], ORDER_F]]: ...

def checksum2_strided(
    a: Annotated[Const(Float64[::, ::]), ORDER_F],
    checksum: Float64[1]
) -> Returns["checksum", Float64[1]]: ...

@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Arg(3)])
def scale2_explicit(
    rows: Const(Int32),
    cols: Const(Int32),
    a: Annotated[Const(Float64[rows, cols]), ORDER_F],
    out: Annotated[Float64[rows, cols], ORDER_F]
) -> Returns["out", Annotated[Float64[rows, cols], ORDER_F]]: ...

def shift3_contiguous(
    a: Annotated[Const(Float64[:, :, :]), ORDER_F],
    out: Annotated[Float64[:, :, :], ORDER_F]
) -> Returns["out", Annotated[Float64[:, :, :], ORDER_F]]: ...

def shift3_strided(
    a: Annotated[Const(Float64[::, ::, ::]), ORDER_F],
    out: Annotated[Float64[::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::], ORDER_F]]: ...

def checksum3_strided(
    a: Annotated[Const(Float64[::, ::, ::]), ORDER_F],
    checksum: Float64[1]
) -> Returns["checksum", Float64[1]]: ...
