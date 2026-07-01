@native_call([Ref(Arg(0)), Arg(1)])
def sum_assumed_size(
    n: Const(Int32),
    values: Const(Float64[Flat])
) -> Float64: ...

@native_call([Ref(Arg(0)), Arg(1)])
def scale_lower(
    n: Const(Int32),
    values: Float64[n - 1 - 0 + 1]
) -> None: ...

def sum_in(
    values: Const(Float64[::])
) -> Float64: ...

def bump_inout(
    values: Float64[::]
) -> None: ...

@native_call([Arg(0)])
def fill_out(
    values: Float64[::]
) -> Returns["values", Float64[::]]: ...

@native_call([Arg(0), Arg(1)])
def shift1(
    values: Const(Float64[::]),
    out: Float64[::]
) -> Returns["out", Float64[::]]: ...

@native_call([Arg(0), Arg(1)])
def shift2(
    values: Annotated[Const(Float64[::, ::]), ORDER_F],
    out: Annotated[Float64[::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::], ORDER_F]]: ...

@native_call([Arg(0), Arg(1)])
def shift3(
    values: Annotated[Const(Float64[::, ::, ::]), ORDER_F],
    out: Annotated[Float64[::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::], ORDER_F]]: ...

@native_call([Arg(0), Arg(1)])
def shift4(
    values: Annotated[Const(Float64[::, ::, ::, ::]), ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::], ORDER_F]]: ...

@native_call([Arg(0), Arg(1)])
def shift5(
    values: Annotated[Const(Float64[::, ::, ::, ::, ::]), ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::, ::], ORDER_F]]: ...

@native_call([Arg(0), Arg(1)])
def shift6(
    values: Annotated[Const(Float64[::, ::, ::, ::, ::, ::]), ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::, ::, ::], ORDER_F]]: ...

@native_call([Arg(0), Arg(1)])
def shift7(
    values: Annotated[Const(Float64[::, ::, ::, ::, ::, ::, ::]), ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::, ::, ::, ::], ORDER_F]]: ...

@native_call([Arg(0), Arg(1)])
def shift8(
    values: Annotated[Const(Float64[::, ::, ::, ::, ::, ::, ::, ::]), ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]]: ...

@native_call([Arg(0), Arg(1)])
def shift9(
    values: Annotated[Const(Float64[::, ::, ::, ::, ::, ::, ::, ::, ::]), ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]]: ...

@native_call([Arg(0), Arg(1)])
def shift10(
    values: Annotated[Const(Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::]), ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]]: ...

@native_call([Arg(0), Arg(1)])
def shift11(
    values: Annotated[Const(Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::]), ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]]: ...

@native_call([Arg(0), Arg(1)])
def shift12(
    values: Annotated[Const(Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::]), ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]]: ...

@native_call([Arg(0), Arg(1)])
def shift13(
    values: Annotated[Const(Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::]), ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]]: ...

@native_call([Arg(0), Arg(1)])
def shift14(
    values: Annotated[Const(Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::]), ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]]: ...

@native_call([Arg(0), Arg(1)])
def shift15(
    values: Annotated[Const(Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::]), ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]]: ...
