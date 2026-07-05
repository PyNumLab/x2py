from x2py.contracts import Addr, Arg, Bool, Complex128, Complex64, Float32, Float64, Int32, bind, external, native_call

@bind("SQUARE_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def square_r4(
    N: Int32,
    X: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("SQUARE_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def square_r8(
    N: Int32,
    X: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("SQUARE_I4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def square_i4(
    N: Int32,
    X: Int32[N],
    R: Int32[N]
) -> None: ...

@bind("SQUARE_C4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def square_c4(
    N: Int32,
    Z: Complex64[N],
    R: Complex64[N]
) -> None: ...

@bind("SQUARE_C8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def square_c8(
    N: Int32,
    Z: Complex128[N],
    R: Complex128[N]
) -> None: ...

@bind("CUBE_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def cube_r4(
    N: Int32,
    X: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("CUBE_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def cube_r8(
    N: Int32,
    X: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("CUBE_I4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def cube_i4(
    N: Int32,
    X: Int32[N],
    R: Int32[N]
) -> None: ...

@bind("ADD_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def add_r4(
    N: Int32,
    X: Float32[N],
    Y: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("ADD_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def add_r8(
    N: Int32,
    X: Float64[N],
    Y: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("ADD_I4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def add_i4(
    N: Int32,
    X: Int32[N],
    Y: Int32[N],
    R: Int32[N]
) -> None: ...

@bind("ADD_C4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def add_c4(
    N: Int32,
    X: Complex64[N],
    Y: Complex64[N],
    R: Complex64[N]
) -> None: ...

@bind("ADD_C8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def add_c8(
    N: Int32,
    X: Complex128[N],
    Y: Complex128[N],
    R: Complex128[N]
) -> None: ...

@bind("SUB_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def sub_r4(
    N: Int32,
    X: Float32[N],
    Y: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("SUB_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def sub_r8(
    N: Int32,
    X: Float64[N],
    Y: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("SUB_I4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def sub_i4(
    N: Int32,
    X: Int32[N],
    Y: Int32[N],
    R: Int32[N]
) -> None: ...

@bind("MUL_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def mul_r4(
    N: Int32,
    X: Float32[N],
    Y: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("MUL_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def mul_r8(
    N: Int32,
    X: Float64[N],
    Y: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("MUL_I4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def mul_i4(
    N: Int32,
    X: Int32[N],
    Y: Int32[N],
    R: Int32[N]
) -> None: ...

@bind("DIV_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def div_r4(
    N: Int32,
    X: Float32[N],
    Y: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("DIV_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def div_r8(
    N: Int32,
    X: Float64[N],
    Y: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("POW_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def pow_r4(
    N: Int32,
    X: Float32[N],
    Y: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("POW_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def pow_r8(
    N: Int32,
    X: Float64[N],
    Y: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("ABS_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def abs_r4(
    N: Int32,
    X: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("ABS_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def abs_r8(
    N: Int32,
    X: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("ABS_I4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def abs_i4(
    N: Int32,
    X: Int32[N],
    R: Int32[N]
) -> None: ...

@bind("NEG_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def neg_r4(
    N: Int32,
    X: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("NEG_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def neg_r8(
    N: Int32,
    X: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("NEG_I4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def neg_i4(
    N: Int32,
    X: Int32[N],
    R: Int32[N]
) -> None: ...

@bind("SIN_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def sin_r4(
    N: Int32,
    X: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("SIN_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def sin_r8(
    N: Int32,
    X: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("COS_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def cos_r4(
    N: Int32,
    X: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("COS_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def cos_r8(
    N: Int32,
    X: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("TAN_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def tan_r4(
    N: Int32,
    X: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("TAN_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def tan_r8(
    N: Int32,
    X: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("ASIN_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def asin_r4(
    N: Int32,
    X: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("ASIN_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def asin_r8(
    N: Int32,
    X: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("ACOS_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def acos_r4(
    N: Int32,
    X: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("ACOS_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def acos_r8(
    N: Int32,
    X: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("ATAN_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def atan_r4(
    N: Int32,
    X: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("ATAN_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def atan_r8(
    N: Int32,
    X: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("ATAN2_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def atan2_r4(
    N: Int32,
    Y: Float32[N],
    X: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("ATAN2_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def atan2_r8(
    N: Int32,
    Y: Float64[N],
    X: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("EXP_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def exp_r4(
    N: Int32,
    X: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("EXP_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def exp_r8(
    N: Int32,
    X: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("LOG_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def log_r4(
    N: Int32,
    X: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("LOG_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def log_r8(
    N: Int32,
    X: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("LOG10_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def log10_r4(
    N: Int32,
    X: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("LOG10_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def log10_r8(
    N: Int32,
    X: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("SQRT_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def sqrt_r4(
    N: Int32,
    X: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("SQRT_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def sqrt_r8(
    N: Int32,
    X: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("HYPOT_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def hypot_r4(
    N: Int32,
    X: Float32[N],
    Y: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("HYPOT_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def hypot_r8(
    N: Int32,
    X: Float64[N],
    Y: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("MIN_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def min_r4(
    N: Int32,
    X: Float32[N],
    Y: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("MIN_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def min_r8(
    N: Int32,
    X: Float64[N],
    Y: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("MIN_I4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def min_i4(
    N: Int32,
    X: Int32[N],
    Y: Int32[N],
    R: Int32[N]
) -> None: ...

@bind("MAX_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def max_r4(
    N: Int32,
    X: Float32[N],
    Y: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("MAX_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def max_r8(
    N: Int32,
    X: Float64[N],
    Y: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("MAX_I4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def max_i4(
    N: Int32,
    X: Int32[N],
    Y: Int32[N],
    R: Int32[N]
) -> None: ...

@bind("SIGN_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def sign_r4(
    N: Int32,
    X: Float32[N],
    Y: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("SIGN_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def sign_r8(
    N: Int32,
    X: Float64[N],
    Y: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("MOD_I4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def mod_i4(
    N: Int32,
    X: Int32[N],
    Y: Int32[N],
    R: Int32[N]
) -> None: ...

@bind("MOD_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def mod_r4(
    N: Int32,
    X: Float32[N],
    Y: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("MOD_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def mod_r8(
    N: Int32,
    X: Float64[N],
    Y: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("DEG2RAD_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def deg2rad_r4(
    N: Int32,
    X: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("DEG2RAD_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def deg2rad_r8(
    N: Int32,
    X: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("RAD2DEG_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def rad2deg_r4(
    N: Int32,
    X: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("RAD2DEG_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def rad2deg_r8(
    N: Int32,
    X: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("DIST2_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def dist2_r4(
    N: Int32,
    X: Float32[N],
    Y: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("DIST2_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3)])
def dist2_r8(
    N: Int32,
    X: Float64[N],
    Y: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("DOT2_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5)])
def dot2_r4(
    N: Int32,
    X1: Float32[N],
    X2: Float32[N],
    Y1: Float32[N],
    Y2: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("DOT2_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5)])
def dot2_r8(
    N: Int32,
    X1: Float64[N],
    X2: Float64[N],
    Y1: Float64[N],
    Y2: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("DOT3_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7)])
def dot3_r4(
    N: Int32,
    X1: Float32[N],
    X2: Float32[N],
    X3: Float32[N],
    Y1: Float32[N],
    Y2: Float32[N],
    Y3: Float32[N],
    R: Float32[N]
) -> None: ...

@bind("DOT3_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7)])
def dot3_r8(
    N: Int32,
    X1: Float64[N],
    X2: Float64[N],
    X3: Float64[N],
    Y1: Float64[N],
    Y2: Float64[N],
    Y3: Float64[N],
    R: Float64[N]
) -> None: ...

@bind("CONJ_C4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def conj_c4(
    N: Int32,
    Z: Complex64[N],
    R: Complex64[N]
) -> None: ...

@bind("CONJ_C8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def conj_c8(
    N: Int32,
    Z: Complex128[N],
    R: Complex128[N]
) -> None: ...

@bind("REAL_C4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def real_c4(
    N: Int32,
    Z: Complex64[N],
    R: Float32[N]
) -> None: ...

@bind("REAL_C8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def real_c8(
    N: Int32,
    Z: Complex128[N],
    R: Float64[N]
) -> None: ...

@bind("AIMAG_C4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def aimag_c4(
    N: Int32,
    Z: Complex64[N],
    R: Float32[N]
) -> None: ...

@bind("AIMAG_C8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def aimag_c8(
    N: Int32,
    Z: Complex128[N],
    R: Float64[N]
) -> None: ...

@bind("ABS_C4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def abs_c4(
    N: Int32,
    Z: Complex64[N],
    R: Float32[N]
) -> None: ...

@bind("ABS_C8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def abs_c8(
    N: Int32,
    Z: Complex128[N],
    R: Float64[N]
) -> None: ...

@bind("IS_POSITIVE_R4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def is_positive_r4(
    N: Int32,
    X: Float32[N],
    R: Bool[N]
) -> None: ...

@bind("IS_POSITIVE_R8")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def is_positive_r8(
    N: Int32,
    X: Float64[N],
    R: Bool[N]
) -> None: ...

@bind("IS_EVEN_I4")
@external
@native_call([Addr(Arg(0)), Arg(1), Arg(2)])
def is_even_i4(
    N: Int32,
    X: Int32[N],
    R: Bool[N]
) -> None: ...
