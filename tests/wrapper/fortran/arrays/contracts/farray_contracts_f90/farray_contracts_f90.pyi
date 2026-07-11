from x2py.contracts import Addr, Annotated, Arg, Flat, Float64, Int32, ORDER_F, Returns, native_call

@native_call([Addr(Arg(0)), Arg(1)])
def sum_assumed_size(
    n: Int32,
    values: Float64[Flat]
) -> Float64: ...

@native_call([Addr(Arg(0)), Arg(1)])
def scale_lower(
    n: Int32,
    values: Float64[n - 1 - 0 + 1]
) -> None: ...

def sum_in(
    values: Float64[::]
) -> Float64: ...

def bump_inout(
    values: Float64[::]
) -> None: ...

def fill_out(
    values: Float64[::]
) -> Returns["values", Float64[::]]: ...

def shift1(
    values: Float64[::],
    out: Float64[::]
) -> Returns["out", Float64[::]]: ...

def shift2(
    values: Annotated[Float64[::, ::], ORDER_F],
    out: Annotated[Float64[::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::], ORDER_F]]: ...

def shift3(
    values: Annotated[Float64[::, ::, ::], ORDER_F],
    out: Annotated[Float64[::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::], ORDER_F]]: ...

def shift4(
    values: Annotated[Float64[::, ::, ::, ::], ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::], ORDER_F]]: ...

def shift5(
    values: Annotated[Float64[::, ::, ::, ::, ::], ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::, ::], ORDER_F]]: ...

def shift6(
    values: Annotated[Float64[::, ::, ::, ::, ::, ::], ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::, ::, ::], ORDER_F]]: ...

def shift7(
    values: Annotated[Float64[::, ::, ::, ::, ::, ::, ::], ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::, ::, ::, ::], ORDER_F]]: ...

def shift8(
    values: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::], ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]]: ...

def shift9(
    values: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]]: ...

def shift10(
    values: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]]: ...

def shift11(
    values: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]]: ...

def shift12(
    values: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]]: ...

def shift13(
    values: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]]: ...

def shift14(
    values: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]]: ...

def shift15(
    values: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F],
    out: Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]
) -> Returns["out", Annotated[Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::], ORDER_F]]: ...
