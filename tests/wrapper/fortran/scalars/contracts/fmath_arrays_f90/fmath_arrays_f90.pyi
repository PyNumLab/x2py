@bind("SQUARE_R4_CONTIGUOUS")
def square_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("SQUARE_R8_CONTIGUOUS")
def square_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("SQUARE_I4_CONTIGUOUS")
def square_i4_contiguous(
    N: Ptr(Int32),
    X: Int32[:],
    R: Int32[:]
) -> None: ...

@bind("SQUARE_C4_CONTIGUOUS")
def square_c4_contiguous(
    N: Ptr(Int32),
    Z: Complex64[:],
    R: Complex64[:]
) -> None: ...

@bind("SQUARE_C8_CONTIGUOUS")
def square_c8_contiguous(
    N: Ptr(Int32),
    Z: Complex128[:],
    R: Complex128[:]
) -> None: ...

@bind("CUBE_R4_CONTIGUOUS")
def cube_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("CUBE_R8_CONTIGUOUS")
def cube_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("CUBE_I4_CONTIGUOUS")
def cube_i4_contiguous(
    N: Ptr(Int32),
    X: Int32[:],
    R: Int32[:]
) -> None: ...

@bind("ADD_R4_CONTIGUOUS")
def add_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    Y: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("ADD_R8_CONTIGUOUS")
def add_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    Y: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("ADD_I4_CONTIGUOUS")
def add_i4_contiguous(
    N: Ptr(Int32),
    X: Int32[:],
    Y: Int32[:],
    R: Int32[:]
) -> None: ...

@bind("ADD_C4_CONTIGUOUS")
def add_c4_contiguous(
    N: Ptr(Int32),
    X: Complex64[:],
    Y: Complex64[:],
    R: Complex64[:]
) -> None: ...

@bind("ADD_C8_CONTIGUOUS")
def add_c8_contiguous(
    N: Ptr(Int32),
    X: Complex128[:],
    Y: Complex128[:],
    R: Complex128[:]
) -> None: ...

@bind("SUB_R4_CONTIGUOUS")
def sub_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    Y: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("SUB_R8_CONTIGUOUS")
def sub_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    Y: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("SUB_I4_CONTIGUOUS")
def sub_i4_contiguous(
    N: Ptr(Int32),
    X: Int32[:],
    Y: Int32[:],
    R: Int32[:]
) -> None: ...

@bind("MUL_R4_CONTIGUOUS")
def mul_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    Y: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("MUL_R8_CONTIGUOUS")
def mul_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    Y: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("MUL_I4_CONTIGUOUS")
def mul_i4_contiguous(
    N: Ptr(Int32),
    X: Int32[:],
    Y: Int32[:],
    R: Int32[:]
) -> None: ...

@bind("DIV_R4_CONTIGUOUS")
def div_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    Y: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("DIV_R8_CONTIGUOUS")
def div_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    Y: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("POW_R4_CONTIGUOUS")
def pow_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    Y: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("POW_R8_CONTIGUOUS")
def pow_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    Y: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("ABS_R4_CONTIGUOUS")
def abs_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("ABS_R8_CONTIGUOUS")
def abs_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("ABS_I4_CONTIGUOUS")
def abs_i4_contiguous(
    N: Ptr(Int32),
    X: Int32[:],
    R: Int32[:]
) -> None: ...

@bind("NEG_R4_CONTIGUOUS")
def neg_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("NEG_R8_CONTIGUOUS")
def neg_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("NEG_I4_CONTIGUOUS")
def neg_i4_contiguous(
    N: Ptr(Int32),
    X: Int32[:],
    R: Int32[:]
) -> None: ...

@bind("SIN_R4_CONTIGUOUS")
def sin_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("SIN_R8_CONTIGUOUS")
def sin_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("COS_R4_CONTIGUOUS")
def cos_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("COS_R8_CONTIGUOUS")
def cos_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("TAN_R4_CONTIGUOUS")
def tan_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("TAN_R8_CONTIGUOUS")
def tan_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("ASIN_R4_CONTIGUOUS")
def asin_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("ASIN_R8_CONTIGUOUS")
def asin_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("ACOS_R4_CONTIGUOUS")
def acos_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("ACOS_R8_CONTIGUOUS")
def acos_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("ATAN_R4_CONTIGUOUS")
def atan_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("ATAN_R8_CONTIGUOUS")
def atan_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("ATAN2_R4_CONTIGUOUS")
def atan2_r4_contiguous(
    N: Ptr(Int32),
    Y: Float32[:],
    X: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("ATAN2_R8_CONTIGUOUS")
def atan2_r8_contiguous(
    N: Ptr(Int32),
    Y: Float64[:],
    X: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("EXP_R4_CONTIGUOUS")
def exp_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("EXP_R8_CONTIGUOUS")
def exp_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("LOG_R4_CONTIGUOUS")
def log_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("LOG_R8_CONTIGUOUS")
def log_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("LOG10_R4_CONTIGUOUS")
def log10_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("LOG10_R8_CONTIGUOUS")
def log10_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("SQRT_R4_CONTIGUOUS")
def sqrt_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("SQRT_R8_CONTIGUOUS")
def sqrt_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("HYPOT_R4_CONTIGUOUS")
def hypot_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    Y: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("HYPOT_R8_CONTIGUOUS")
def hypot_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    Y: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("MIN_R4_CONTIGUOUS")
def min_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    Y: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("MIN_R8_CONTIGUOUS")
def min_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    Y: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("MIN_I4_CONTIGUOUS")
def min_i4_contiguous(
    N: Ptr(Int32),
    X: Int32[:],
    Y: Int32[:],
    R: Int32[:]
) -> None: ...

@bind("MAX_R4_CONTIGUOUS")
def max_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    Y: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("MAX_R8_CONTIGUOUS")
def max_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    Y: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("MAX_I4_CONTIGUOUS")
def max_i4_contiguous(
    N: Ptr(Int32),
    X: Int32[:],
    Y: Int32[:],
    R: Int32[:]
) -> None: ...

@bind("SIGN_R4_CONTIGUOUS")
def sign_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    Y: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("SIGN_R8_CONTIGUOUS")
def sign_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    Y: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("MOD_I4_CONTIGUOUS")
def mod_i4_contiguous(
    N: Ptr(Int32),
    X: Int32[:],
    Y: Int32[:],
    R: Int32[:]
) -> None: ...

@bind("MOD_R4_CONTIGUOUS")
def mod_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    Y: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("MOD_R8_CONTIGUOUS")
def mod_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    Y: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("DEG2RAD_R4_CONTIGUOUS")
def deg2rad_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("DEG2RAD_R8_CONTIGUOUS")
def deg2rad_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("RAD2DEG_R4_CONTIGUOUS")
def rad2deg_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("RAD2DEG_R8_CONTIGUOUS")
def rad2deg_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("DIST2_R4_CONTIGUOUS")
def dist2_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    Y: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("DIST2_R8_CONTIGUOUS")
def dist2_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    Y: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("DOT2_R4_CONTIGUOUS")
def dot2_r4_contiguous(
    N: Ptr(Int32),
    X1: Float32[:],
    X2: Float32[:],
    Y1: Float32[:],
    Y2: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("DOT2_R8_CONTIGUOUS")
def dot2_r8_contiguous(
    N: Ptr(Int32),
    X1: Float64[:],
    X2: Float64[:],
    Y1: Float64[:],
    Y2: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("DOT3_R4_CONTIGUOUS")
def dot3_r4_contiguous(
    N: Ptr(Int32),
    X1: Float32[:],
    X2: Float32[:],
    X3: Float32[:],
    Y1: Float32[:],
    Y2: Float32[:],
    Y3: Float32[:],
    R: Float32[:]
) -> None: ...

@bind("DOT3_R8_CONTIGUOUS")
def dot3_r8_contiguous(
    N: Ptr(Int32),
    X1: Float64[:],
    X2: Float64[:],
    X3: Float64[:],
    Y1: Float64[:],
    Y2: Float64[:],
    Y3: Float64[:],
    R: Float64[:]
) -> None: ...

@bind("CONJ_C4_CONTIGUOUS")
def conj_c4_contiguous(
    N: Ptr(Int32),
    Z: Complex64[:],
    R: Complex64[:]
) -> None: ...

@bind("CONJ_C8_CONTIGUOUS")
def conj_c8_contiguous(
    N: Ptr(Int32),
    Z: Complex128[:],
    R: Complex128[:]
) -> None: ...

@bind("REAL_C4_CONTIGUOUS")
def real_c4_contiguous(
    N: Ptr(Int32),
    Z: Complex64[:],
    R: Float32[:]
) -> None: ...

@bind("REAL_C8_CONTIGUOUS")
def real_c8_contiguous(
    N: Ptr(Int32),
    Z: Complex128[:],
    R: Float64[:]
) -> None: ...

@bind("AIMAG_C4_CONTIGUOUS")
def aimag_c4_contiguous(
    N: Ptr(Int32),
    Z: Complex64[:],
    R: Float32[:]
) -> None: ...

@bind("AIMAG_C8_CONTIGUOUS")
def aimag_c8_contiguous(
    N: Ptr(Int32),
    Z: Complex128[:],
    R: Float64[:]
) -> None: ...

@bind("ABS_C4_CONTIGUOUS")
def abs_c4_contiguous(
    N: Ptr(Int32),
    Z: Complex64[:],
    R: Float32[:]
) -> None: ...

@bind("ABS_C8_CONTIGUOUS")
def abs_c8_contiguous(
    N: Ptr(Int32),
    Z: Complex128[:],
    R: Float64[:]
) -> None: ...

@bind("IS_POSITIVE_R4_CONTIGUOUS")
def is_positive_r4_contiguous(
    N: Ptr(Int32),
    X: Float32[:],
    R: Bool[:]
) -> None: ...

@bind("IS_POSITIVE_R8_CONTIGUOUS")
def is_positive_r8_contiguous(
    N: Ptr(Int32),
    X: Float64[:],
    R: Bool[:]
) -> None: ...

@bind("IS_EVEN_I4_CONTIGUOUS")
def is_even_i4_contiguous(
    N: Ptr(Int32),
    X: Int32[:],
    R: Bool[:]
) -> None: ...

@bind("SQUARE_R4_STRIDED")
def square_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("SQUARE_R8_STRIDED")
def square_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("SQUARE_I4_STRIDED")
def square_i4_strided(
    N: Ptr(Int32),
    X: Int32[::Strided],
    R: Int32[::Strided]
) -> None: ...

@bind("SQUARE_C4_STRIDED")
def square_c4_strided(
    N: Ptr(Int32),
    Z: Complex64[::Strided],
    R: Complex64[::Strided]
) -> None: ...

@bind("SQUARE_C8_STRIDED")
def square_c8_strided(
    N: Ptr(Int32),
    Z: Complex128[::Strided],
    R: Complex128[::Strided]
) -> None: ...

@bind("CUBE_R4_STRIDED")
def cube_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("CUBE_R8_STRIDED")
def cube_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("CUBE_I4_STRIDED")
def cube_i4_strided(
    N: Ptr(Int32),
    X: Int32[::Strided],
    R: Int32[::Strided]
) -> None: ...

@bind("ADD_R4_STRIDED")
def add_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    Y: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("ADD_R8_STRIDED")
def add_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    Y: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("ADD_I4_STRIDED")
def add_i4_strided(
    N: Ptr(Int32),
    X: Int32[::Strided],
    Y: Int32[::Strided],
    R: Int32[::Strided]
) -> None: ...

@bind("ADD_C4_STRIDED")
def add_c4_strided(
    N: Ptr(Int32),
    X: Complex64[::Strided],
    Y: Complex64[::Strided],
    R: Complex64[::Strided]
) -> None: ...

@bind("ADD_C8_STRIDED")
def add_c8_strided(
    N: Ptr(Int32),
    X: Complex128[::Strided],
    Y: Complex128[::Strided],
    R: Complex128[::Strided]
) -> None: ...

@bind("SUB_R4_STRIDED")
def sub_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    Y: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("SUB_R8_STRIDED")
def sub_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    Y: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("SUB_I4_STRIDED")
def sub_i4_strided(
    N: Ptr(Int32),
    X: Int32[::Strided],
    Y: Int32[::Strided],
    R: Int32[::Strided]
) -> None: ...

@bind("MUL_R4_STRIDED")
def mul_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    Y: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("MUL_R8_STRIDED")
def mul_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    Y: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("MUL_I4_STRIDED")
def mul_i4_strided(
    N: Ptr(Int32),
    X: Int32[::Strided],
    Y: Int32[::Strided],
    R: Int32[::Strided]
) -> None: ...

@bind("DIV_R4_STRIDED")
def div_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    Y: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("DIV_R8_STRIDED")
def div_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    Y: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("POW_R4_STRIDED")
def pow_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    Y: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("POW_R8_STRIDED")
def pow_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    Y: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("ABS_R4_STRIDED")
def abs_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("ABS_R8_STRIDED")
def abs_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("ABS_I4_STRIDED")
def abs_i4_strided(
    N: Ptr(Int32),
    X: Int32[::Strided],
    R: Int32[::Strided]
) -> None: ...

@bind("NEG_R4_STRIDED")
def neg_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("NEG_R8_STRIDED")
def neg_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("NEG_I4_STRIDED")
def neg_i4_strided(
    N: Ptr(Int32),
    X: Int32[::Strided],
    R: Int32[::Strided]
) -> None: ...

@bind("SIN_R4_STRIDED")
def sin_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("SIN_R8_STRIDED")
def sin_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("COS_R4_STRIDED")
def cos_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("COS_R8_STRIDED")
def cos_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("TAN_R4_STRIDED")
def tan_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("TAN_R8_STRIDED")
def tan_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("ASIN_R4_STRIDED")
def asin_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("ASIN_R8_STRIDED")
def asin_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("ACOS_R4_STRIDED")
def acos_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("ACOS_R8_STRIDED")
def acos_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("ATAN_R4_STRIDED")
def atan_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("ATAN_R8_STRIDED")
def atan_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("ATAN2_R4_STRIDED")
def atan2_r4_strided(
    N: Ptr(Int32),
    Y: Float32[::Strided],
    X: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("ATAN2_R8_STRIDED")
def atan2_r8_strided(
    N: Ptr(Int32),
    Y: Float64[::Strided],
    X: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("EXP_R4_STRIDED")
def exp_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("EXP_R8_STRIDED")
def exp_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("LOG_R4_STRIDED")
def log_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("LOG_R8_STRIDED")
def log_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("LOG10_R4_STRIDED")
def log10_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("LOG10_R8_STRIDED")
def log10_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("SQRT_R4_STRIDED")
def sqrt_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("SQRT_R8_STRIDED")
def sqrt_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("HYPOT_R4_STRIDED")
def hypot_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    Y: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("HYPOT_R8_STRIDED")
def hypot_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    Y: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("MIN_R4_STRIDED")
def min_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    Y: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("MIN_R8_STRIDED")
def min_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    Y: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("MIN_I4_STRIDED")
def min_i4_strided(
    N: Ptr(Int32),
    X: Int32[::Strided],
    Y: Int32[::Strided],
    R: Int32[::Strided]
) -> None: ...

@bind("MAX_R4_STRIDED")
def max_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    Y: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("MAX_R8_STRIDED")
def max_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    Y: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("MAX_I4_STRIDED")
def max_i4_strided(
    N: Ptr(Int32),
    X: Int32[::Strided],
    Y: Int32[::Strided],
    R: Int32[::Strided]
) -> None: ...

@bind("SIGN_R4_STRIDED")
def sign_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    Y: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("SIGN_R8_STRIDED")
def sign_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    Y: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("MOD_I4_STRIDED")
def mod_i4_strided(
    N: Ptr(Int32),
    X: Int32[::Strided],
    Y: Int32[::Strided],
    R: Int32[::Strided]
) -> None: ...

@bind("MOD_R4_STRIDED")
def mod_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    Y: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("MOD_R8_STRIDED")
def mod_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    Y: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("DEG2RAD_R4_STRIDED")
def deg2rad_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("DEG2RAD_R8_STRIDED")
def deg2rad_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("RAD2DEG_R4_STRIDED")
def rad2deg_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("RAD2DEG_R8_STRIDED")
def rad2deg_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("DIST2_R4_STRIDED")
def dist2_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    Y: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("DIST2_R8_STRIDED")
def dist2_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    Y: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("DOT2_R4_STRIDED")
def dot2_r4_strided(
    N: Ptr(Int32),
    X1: Float32[::Strided],
    X2: Float32[::Strided],
    Y1: Float32[::Strided],
    Y2: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("DOT2_R8_STRIDED")
def dot2_r8_strided(
    N: Ptr(Int32),
    X1: Float64[::Strided],
    X2: Float64[::Strided],
    Y1: Float64[::Strided],
    Y2: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("DOT3_R4_STRIDED")
def dot3_r4_strided(
    N: Ptr(Int32),
    X1: Float32[::Strided],
    X2: Float32[::Strided],
    X3: Float32[::Strided],
    Y1: Float32[::Strided],
    Y2: Float32[::Strided],
    Y3: Float32[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("DOT3_R8_STRIDED")
def dot3_r8_strided(
    N: Ptr(Int32),
    X1: Float64[::Strided],
    X2: Float64[::Strided],
    X3: Float64[::Strided],
    Y1: Float64[::Strided],
    Y2: Float64[::Strided],
    Y3: Float64[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("CONJ_C4_STRIDED")
def conj_c4_strided(
    N: Ptr(Int32),
    Z: Complex64[::Strided],
    R: Complex64[::Strided]
) -> None: ...

@bind("CONJ_C8_STRIDED")
def conj_c8_strided(
    N: Ptr(Int32),
    Z: Complex128[::Strided],
    R: Complex128[::Strided]
) -> None: ...

@bind("REAL_C4_STRIDED")
def real_c4_strided(
    N: Ptr(Int32),
    Z: Complex64[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("REAL_C8_STRIDED")
def real_c8_strided(
    N: Ptr(Int32),
    Z: Complex128[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("AIMAG_C4_STRIDED")
def aimag_c4_strided(
    N: Ptr(Int32),
    Z: Complex64[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("AIMAG_C8_STRIDED")
def aimag_c8_strided(
    N: Ptr(Int32),
    Z: Complex128[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("ABS_C4_STRIDED")
def abs_c4_strided(
    N: Ptr(Int32),
    Z: Complex64[::Strided],
    R: Float32[::Strided]
) -> None: ...

@bind("ABS_C8_STRIDED")
def abs_c8_strided(
    N: Ptr(Int32),
    Z: Complex128[::Strided],
    R: Float64[::Strided]
) -> None: ...

@bind("IS_POSITIVE_R4_STRIDED")
def is_positive_r4_strided(
    N: Ptr(Int32),
    X: Float32[::Strided],
    R: Bool[::Strided]
) -> None: ...

@bind("IS_POSITIVE_R8_STRIDED")
def is_positive_r8_strided(
    N: Ptr(Int32),
    X: Float64[::Strided],
    R: Bool[::Strided]
) -> None: ...

@bind("IS_EVEN_I4_STRIDED")
def is_even_i4_strided(
    N: Ptr(Int32),
    X: Int32[::Strided],
    R: Bool[::Strided]
) -> None: ...
