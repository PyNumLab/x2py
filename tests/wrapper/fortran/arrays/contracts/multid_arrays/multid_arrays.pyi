from x2py.contracts import Addr, Arg, Float64, Int32, Returns, native_call

def scale2_contiguous(
    a: Float64[:, :],
    out: Float64[:, :]
) -> Returns["out", Float64[:, :]]: ...

def scale2_strided(
    a: Float64[::, ::],
    out: Float64[::, ::]
) -> Returns["out", Float64[::, ::]]: ...

def checksum2_strided(
    a: Float64[::, ::],
    checksum: Float64[1]
) -> Returns["checksum", Float64[1]]: ...

@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Arg(3)])
def scale2_explicit(
    rows: Int32,
    cols: Int32,
    a: Float64[rows, cols],
    out: Float64[rows, cols]
) -> Returns["out", Float64[rows, cols]]: ...

def shift3_contiguous(
    a: Float64[:, :, :],
    out: Float64[:, :, :]
) -> Returns["out", Float64[:, :, :]]: ...

def shift3_strided(
    a: Float64[::, ::, ::],
    out: Float64[::, ::, ::]
) -> Returns["out", Float64[::, ::, ::]]: ...

def checksum3_strided(
    a: Float64[::, ::, ::],
    checksum: Float64[1]
) -> Returns["checksum", Float64[1]]: ...
