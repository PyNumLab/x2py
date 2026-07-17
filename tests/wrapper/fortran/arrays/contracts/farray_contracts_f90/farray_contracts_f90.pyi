from x2py.contracts import Addr, Arg, Flat, Float64, Int32, Returns, native_call

@native_call([Addr(Arg(0)), Arg(1)])
def sum_assumed_size(
    n: Int32,
    values: Float64[Flat]
) -> Float64: ...

@native_call([Addr(Arg(0)), Arg(1)])
def scale_lower(
    n: Int32,
    values: Float64[n]
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
    values: Float64[::, ::],
    out: Float64[::, ::]
) -> Returns["out", Float64[::, ::]]: ...

def shift3(
    values: Float64[::, ::, ::],
    out: Float64[::, ::, ::]
) -> Returns["out", Float64[::, ::, ::]]: ...

def shift4(
    values: Float64[::, ::, ::, ::],
    out: Float64[::, ::, ::, ::]
) -> Returns["out", Float64[::, ::, ::, ::]]: ...

def shift5(
    values: Float64[::, ::, ::, ::, ::],
    out: Float64[::, ::, ::, ::, ::]
) -> Returns["out", Float64[::, ::, ::, ::, ::]]: ...

def shift6(
    values: Float64[::, ::, ::, ::, ::, ::],
    out: Float64[::, ::, ::, ::, ::, ::]
) -> Returns["out", Float64[::, ::, ::, ::, ::, ::]]: ...

def shift7(
    values: Float64[::, ::, ::, ::, ::, ::, ::],
    out: Float64[::, ::, ::, ::, ::, ::, ::]
) -> Returns["out", Float64[::, ::, ::, ::, ::, ::, ::]]: ...

def shift8(
    values: Float64[::, ::, ::, ::, ::, ::, ::, ::],
    out: Float64[::, ::, ::, ::, ::, ::, ::, ::]
) -> Returns["out", Float64[::, ::, ::, ::, ::, ::, ::, ::]]: ...

def shift9(
    values: Float64[::, ::, ::, ::, ::, ::, ::, ::, ::],
    out: Float64[::, ::, ::, ::, ::, ::, ::, ::, ::]
) -> Returns["out", Float64[::, ::, ::, ::, ::, ::, ::, ::, ::]]: ...

def shift10(
    values: Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::],
    out: Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::]
) -> Returns["out", Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::]]: ...

def shift11(
    values: Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::],
    out: Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::]
) -> Returns["out", Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::]]: ...

def shift12(
    values: Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::],
    out: Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::]
) -> Returns["out", Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::]]: ...

def shift13(
    values: Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::],
    out: Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::]
) -> Returns["out", Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::]]: ...

def shift14(
    values: Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::],
    out: Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::]
) -> Returns["out", Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::]]: ...

def shift15(
    values: Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::],
    out: Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::]
) -> Returns["out", Float64[::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::, ::]]: ...
