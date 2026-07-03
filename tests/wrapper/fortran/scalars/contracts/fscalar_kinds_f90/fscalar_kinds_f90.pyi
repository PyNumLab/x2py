@native_call([Addr(Arg(0))])
def id_i8(
    value: Const(Int8)
) -> Int8: ...

@native_call([Addr(Arg(0))])
def id_i16(
    value: Const(Int16)
) -> Int16: ...

@native_call([Addr(Arg(0))])
def id_i32(
    value: Const(Int32)
) -> Int32: ...

@native_call([Addr(Arg(0))])
def id_i64(
    value: Const(Int64)
) -> Int64: ...

@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def copy_i16(
    n: Const(Int32),
    values: Const(Int16[n]),
    out: Int16[n]
) -> Returns["out", Int16[n]]: ...

@native_call([Addr(Arg(0))])
def not_flag(
    value: Const(Bool)
) -> Bool: ...

@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def invert_flags(
    n: Const(Int32),
    values: Const(Bool[n]),
    out: Bool[n]
) -> Returns["out", Bool[n]]: ...

@native_call([Addr(Arg(0))])
def id_r32(
    value: Const(Float32)
) -> Float32: ...

@native_call([Addr(Arg(0))])
def id_r64(
    value: Const(Float64)
) -> Float64: ...

@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def copy_r64(
    n: Const(Int32),
    values: Const(Float64[n]),
    out: Float64[n]
) -> Returns["out", Float64[n]]: ...

@native_call([Addr(Arg(0))])
def conj_c64(
    value: Const(Complex64)
) -> Complex64: ...

@native_call([Addr(Arg(0))])
def shift_c128(
    value: Const(Complex128)
) -> Complex128: ...

@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def copy_c128(
    n: Const(Int32),
    values: Const(Complex128[n]),
    out: Complex128[n]
) -> Returns["out", Complex128[n]]: ...

@native_call([Addr(Arg(0))])
def id_c_i32(
    value: Const(Int32)
) -> Int32: ...

@native_call([Addr(Arg(0))])
def id_c_float(
    value: Const(Float32)
) -> Float32: ...

@native_call([Addr(Arg(0))])
def id_c_double(
    value: Const(Float64)
) -> Float64: ...

@native_call([Addr(Arg(0))])
def conj_c_float_complex(
    value: Const(Complex64)
) -> Complex64: ...

@native_call([Addr(Arg(0))])
def conj_c_double_complex(
    value: Const(Complex128)
) -> Complex128: ...
