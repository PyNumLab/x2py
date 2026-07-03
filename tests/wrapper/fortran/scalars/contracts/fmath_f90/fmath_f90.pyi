@bind("SQUARE_R4")
def square_r4(
    X: Addr(Float32)
) -> Float32: ...

@bind("SQUARE_R8")
def square_r8(
    X: Addr(Float64)
) -> Float64: ...

@bind("SQUARE_I4")
def square_i4(
    X: Addr(Int32)
) -> Int32: ...

@bind("SQUARE_C4")
def square_c4(
    Z: Addr(Complex64)
) -> Complex64: ...

@bind("SQUARE_C8")
def square_c8(
    Z: Addr(Complex128)
) -> Complex128: ...

@bind("CUBE_R4")
def cube_r4(
    X: Addr(Float32)
) -> Float32: ...

@bind("CUBE_R8")
def cube_r8(
    X: Addr(Float64)
) -> Float64: ...

@bind("CUBE_I4")
def cube_i4(
    X: Addr(Int32)
) -> Int32: ...

@bind("ADD_R4")
def add_r4(
    X: Addr(Float32),
    Y: Addr(Float32)
) -> Float32: ...

@bind("ADD_R8")
def add_r8(
    X: Addr(Float64),
    Y: Addr(Float64)
) -> Float64: ...

@bind("ADD_I4")
def add_i4(
    X: Addr(Int32),
    Y: Addr(Int32)
) -> Int32: ...

@bind("ADD_C4")
def add_c4(
    X: Addr(Complex64),
    Y: Addr(Complex64)
) -> Complex64: ...

@bind("ADD_C8")
def add_c8(
    X: Addr(Complex128),
    Y: Addr(Complex128)
) -> Complex128: ...

@bind("SUB_R4")
def sub_r4(
    X: Addr(Float32),
    Y: Addr(Float32)
) -> Float32: ...

@bind("SUB_R8")
def sub_r8(
    X: Addr(Float64),
    Y: Addr(Float64)
) -> Float64: ...

@bind("SUB_I4")
def sub_i4(
    X: Addr(Int32),
    Y: Addr(Int32)
) -> Int32: ...

@bind("MUL_R4")
def mul_r4(
    X: Addr(Float32),
    Y: Addr(Float32)
) -> Float32: ...

@bind("MUL_R8")
def mul_r8(
    X: Addr(Float64),
    Y: Addr(Float64)
) -> Float64: ...

@bind("MUL_I4")
def mul_i4(
    X: Addr(Int32),
    Y: Addr(Int32)
) -> Int32: ...

@bind("DIV_R4")
def div_r4(
    X: Addr(Float32),
    Y: Addr(Float32)
) -> Float32: ...

@bind("DIV_R8")
def div_r8(
    X: Addr(Float64),
    Y: Addr(Float64)
) -> Float64: ...

@bind("POW_R4")
def pow_r4(
    X: Addr(Float32),
    Y: Addr(Float32)
) -> Float32: ...

@bind("POW_R8")
def pow_r8(
    X: Addr(Float64),
    Y: Addr(Float64)
) -> Float64: ...

@bind("ABS_R4")
def abs_r4(
    X: Addr(Float32)
) -> Float32: ...

@bind("ABS_R8")
def abs_r8(
    X: Addr(Float64)
) -> Float64: ...

@bind("ABS_I4")
def abs_i4(
    X: Addr(Int32)
) -> Int32: ...

@bind("NEG_R4")
def neg_r4(
    X: Addr(Float32)
) -> Float32: ...

@bind("NEG_R8")
def neg_r8(
    X: Addr(Float64)
) -> Float64: ...

@bind("NEG_I4")
def neg_i4(
    X: Addr(Int32)
) -> Int32: ...

@bind("SIN_R4")
def sin_r4(
    X: Addr(Float32)
) -> Float32: ...

@bind("SIN_R8")
def sin_r8(
    X: Addr(Float64)
) -> Float64: ...

@bind("COS_R4")
def cos_r4(
    X: Addr(Float32)
) -> Float32: ...

@bind("COS_R8")
def cos_r8(
    X: Addr(Float64)
) -> Float64: ...

@bind("TAN_R4")
def tan_r4(
    X: Addr(Float32)
) -> Float32: ...

@bind("TAN_R8")
def tan_r8(
    X: Addr(Float64)
) -> Float64: ...

@bind("ASIN_R4")
def asin_r4(
    X: Addr(Float32)
) -> Float32: ...

@bind("ASIN_R8")
def asin_r8(
    X: Addr(Float64)
) -> Float64: ...

@bind("ACOS_R4")
def acos_r4(
    X: Addr(Float32)
) -> Float32: ...

@bind("ACOS_R8")
def acos_r8(
    X: Addr(Float64)
) -> Float64: ...

@bind("ATAN_R4")
def atan_r4(
    X: Addr(Float32)
) -> Float32: ...

@bind("ATAN_R8")
def atan_r8(
    X: Addr(Float64)
) -> Float64: ...

@bind("ATAN2_R4")
def atan2_r4(
    Y: Addr(Float32),
    X: Addr(Float32)
) -> Float32: ...

@bind("ATAN2_R8")
def atan2_r8(
    Y: Addr(Float64),
    X: Addr(Float64)
) -> Float64: ...

@bind("EXP_R4")
def exp_r4(
    X: Addr(Float32)
) -> Float32: ...

@bind("EXP_R8")
def exp_r8(
    X: Addr(Float64)
) -> Float64: ...

@bind("LOG_R4")
def log_r4(
    X: Addr(Float32)
) -> Float32: ...

@bind("LOG_R8")
def log_r8(
    X: Addr(Float64)
) -> Float64: ...

@bind("LOG10_R4")
def log10_r4(
    X: Addr(Float32)
) -> Float32: ...

@bind("LOG10_R8")
def log10_r8(
    X: Addr(Float64)
) -> Float64: ...

@bind("SQRT_R4")
def sqrt_r4(
    X: Addr(Float32)
) -> Float32: ...

@bind("SQRT_R8")
def sqrt_r8(
    X: Addr(Float64)
) -> Float64: ...

@bind("HYPOT_R4")
def hypot_r4(
    X: Addr(Float32),
    Y: Addr(Float32)
) -> Float32: ...

@bind("HYPOT_R8")
def hypot_r8(
    X: Addr(Float64),
    Y: Addr(Float64)
) -> Float64: ...

@bind("MIN_R4")
def min_r4(
    X: Addr(Float32),
    Y: Addr(Float32)
) -> Float32: ...

@bind("MIN_R8")
def min_r8(
    X: Addr(Float64),
    Y: Addr(Float64)
) -> Float64: ...

@bind("MIN_I4")
def min_i4(
    X: Addr(Int32),
    Y: Addr(Int32)
) -> Int32: ...

@bind("MAX_R4")
def max_r4(
    X: Addr(Float32),
    Y: Addr(Float32)
) -> Float32: ...

@bind("MAX_R8")
def max_r8(
    X: Addr(Float64),
    Y: Addr(Float64)
) -> Float64: ...

@bind("MAX_I4")
def max_i4(
    X: Addr(Int32),
    Y: Addr(Int32)
) -> Int32: ...

@bind("SIGN_R4")
def sign_r4(
    X: Addr(Float32),
    Y: Addr(Float32)
) -> Float32: ...

@bind("SIGN_R8")
def sign_r8(
    X: Addr(Float64),
    Y: Addr(Float64)
) -> Float64: ...

@bind("MOD_I4")
def mod_i4(
    X: Addr(Int32),
    Y: Addr(Int32)
) -> Int32: ...

@bind("MOD_R4")
def mod_r4(
    X: Addr(Float32),
    Y: Addr(Float32)
) -> Float32: ...

@bind("MOD_R8")
def mod_r8(
    X: Addr(Float64),
    Y: Addr(Float64)
) -> Float64: ...

@bind("DEG2RAD_R4")
def deg2rad_r4(
    X: Addr(Float32)
) -> Float32: ...

@bind("DEG2RAD_R8")
def deg2rad_r8(
    X: Addr(Float64)
) -> Float64: ...

@bind("RAD2DEG_R4")
def rad2deg_r4(
    X: Addr(Float32)
) -> Float32: ...

@bind("RAD2DEG_R8")
def rad2deg_r8(
    X: Addr(Float64)
) -> Float64: ...

@bind("DIST2_R4")
def dist2_r4(
    X: Addr(Float32),
    Y: Addr(Float32)
) -> Float32: ...

@bind("DIST2_R8")
def dist2_r8(
    X: Addr(Float64),
    Y: Addr(Float64)
) -> Float64: ...

@bind("DOT2_R4")
def dot2_r4(
    X1: Addr(Float32),
    X2: Addr(Float32),
    Y1: Addr(Float32),
    Y2: Addr(Float32)
) -> Float32: ...

@bind("DOT2_R8")
def dot2_r8(
    X1: Addr(Float64),
    X2: Addr(Float64),
    Y1: Addr(Float64),
    Y2: Addr(Float64)
) -> Float64: ...

@bind("DOT3_R4")
def dot3_r4(
    X1: Addr(Float32),
    X2: Addr(Float32),
    X3: Addr(Float32),
    Y1: Addr(Float32),
    Y2: Addr(Float32),
    Y3: Addr(Float32)
) -> Float32: ...

@bind("DOT3_R8")
def dot3_r8(
    X1: Addr(Float64),
    X2: Addr(Float64),
    X3: Addr(Float64),
    Y1: Addr(Float64),
    Y2: Addr(Float64),
    Y3: Addr(Float64)
) -> Float64: ...

@bind("CONJ_C4")
def conj_c4(
    Z: Addr(Complex64)
) -> Complex64: ...

@bind("CONJ_C8")
def conj_c8(
    Z: Addr(Complex128)
) -> Complex128: ...

@bind("REAL_C4")
def real_c4(
    Z: Addr(Complex64)
) -> Float32: ...

@bind("REAL_C8")
def real_c8(
    Z: Addr(Complex128)
) -> Float64: ...

@bind("AIMAG_C4")
def aimag_c4(
    Z: Addr(Complex64)
) -> Float32: ...

@bind("AIMAG_C8")
def aimag_c8(
    Z: Addr(Complex128)
) -> Float64: ...

@bind("ABS_C4")
def abs_c4(
    Z: Addr(Complex64)
) -> Float32: ...

@bind("ABS_C8")
def abs_c8(
    Z: Addr(Complex128)
) -> Float64: ...

@bind("IS_POSITIVE_R4")
def is_positive_r4(
    X: Addr(Float32)
) -> Bool: ...

@bind("IS_POSITIVE_R8")
def is_positive_r8(
    X: Addr(Float64)
) -> Bool: ...

@bind("IS_EVEN_I4")
def is_even_i4(
    X: Addr(Int32)
) -> Bool: ...
