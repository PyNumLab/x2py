def id_i8(
    value: Ptr(Const(Int8))
) -> Int8: ...

def id_i16(
    value: Ptr(Const(Int16))
) -> Int16: ...

def id_i32(
    value: Ptr(Const(Int32))
) -> Int32: ...

def id_i64(
    value: Ptr(Const(Int64))
) -> Int64: ...

@native_call([Arg(0), Arg(1), Arg(2)])
def copy_i16(
    n: Ptr(Const(Int32)),
    values: Const(Int16[n]),
    out: Int16[n]
) -> Returns["out", Int16[n]]: ...

def not_flag(
    value: Ptr(Const(Bool))
) -> Bool: ...

@native_call([Arg(0), Arg(1), Arg(2)])
def invert_flags(
    n: Ptr(Const(Int32)),
    values: Const(Bool[n]),
    out: Bool[n]
) -> Returns["out", Bool[n]]: ...

def id_r32(
    value: Ptr(Const(Float32))
) -> Float32: ...

def id_r64(
    value: Ptr(Const(Float64))
) -> Float64: ...

@native_call([Arg(0), Arg(1), Arg(2)])
def copy_r64(
    n: Ptr(Const(Int32)),
    values: Const(Float64[n]),
    out: Float64[n]
) -> Returns["out", Float64[n]]: ...

def conj_c64(
    value: Ptr(Const(Complex64))
) -> Complex64: ...

def shift_c128(
    value: Ptr(Const(Complex128))
) -> Complex128: ...

@native_call([Arg(0), Arg(1), Arg(2)])
def copy_c128(
    n: Ptr(Const(Int32)),
    values: Const(Complex128[n]),
    out: Complex128[n]
) -> Returns["out", Complex128[n]]: ...

def id_c_i32(
    value: Ptr(Const(Int32))
) -> Int32: ...

def id_c_float(
    value: Ptr(Const(Float32))
) -> Float32: ...

def id_c_double(
    value: Ptr(Const(Float64))
) -> Float64: ...

def conj_c_float_complex(
    value: Ptr(Const(Complex64))
) -> Complex64: ...

def conj_c_double_complex(
    value: Ptr(Const(Complex128))
) -> Complex128: ...
