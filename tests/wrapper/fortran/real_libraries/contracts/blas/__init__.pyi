@bind("CAXPY")
@external
def caxpy(
    N: Ptr(Int32),
    CA: Ptr(Complex64),
    CX: Complex64[Flat],
    INCX: Ptr(Int32),
    CY: Complex64[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("CCOPY")
@external
def ccopy(
    N: Ptr(Int32),
    CX: Complex64[Flat],
    INCX: Ptr(Int32),
    CY: Complex64[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("CDOTC")
@external
def cdotc(
    N: Ptr(Int32),
    CX: Complex64[Flat],
    INCX: Ptr(Int32),
    CY: Complex64[Flat],
    INCY: Ptr(Int32)
) -> Complex64: ...

@bind("CDOTU")
@external
def cdotu(
    N: Ptr(Int32),
    CX: Complex64[Flat],
    INCX: Ptr(Int32),
    CY: Complex64[Flat],
    INCY: Ptr(Int32)
) -> Complex64: ...

@bind("CGBMV")
@external
def cgbmv(
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex64[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Complex64),
    Y: Complex64[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("CGEMM")
@external
def cgemm(
    TRANSA: Ptr(Const(String[1])),
    TRANSB: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    BETA: Ptr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("CGEMMTR")
@external
def cgemmtr(
    UPLO: Ptr(Const(String[1])),
    TRANSA: Ptr(Const(String[1])),
    TRANSB: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    BETA: Ptr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("CGEMV")
@external
def cgemv(
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex64[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Complex64),
    Y: Complex64[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("CGERC")
@external
def cgerc(
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    X: Complex64[Flat],
    INCX: Ptr(Int32),
    Y: Complex64[Flat],
    INCY: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("CGERU")
@external
def cgeru(
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    X: Complex64[Flat],
    INCX: Ptr(Int32),
    Y: Complex64[Flat],
    INCY: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("CHBMV")
@external
def chbmv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex64[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Complex64),
    Y: Complex64[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("CHEMM")
@external
def chemm(
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    BETA: Ptr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("CHEMV")
@external
def chemv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex64[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Complex64),
    Y: Complex64[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("CHER")
@external
def cher(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Float32),
    X: Complex64[Flat],
    INCX: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("CHER2")
@external
def cher2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    X: Complex64[Flat],
    INCX: Ptr(Int32),
    Y: Complex64[Flat],
    INCY: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("CHER2K")
@external
def cher2k(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    BETA: Ptr(Float32),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("CHERK")
@external
def cherk(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Float32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    BETA: Ptr(Float32),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("CHPMV")
@external
def chpmv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    AP: Complex64[Flat],
    X: Complex64[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Complex64),
    Y: Complex64[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("CHPR")
@external
def chpr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Float32),
    X: Complex64[Flat],
    INCX: Ptr(Int32),
    AP: Complex64[Flat]
) -> None: ...

@bind("CHPR2")
@external
def chpr2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    X: Complex64[Flat],
    INCX: Ptr(Int32),
    Y: Complex64[Flat],
    INCY: Ptr(Int32),
    AP: Complex64[Flat]
) -> None: ...

@bind("CROTG")
@external
def crotg(
    a: Ptr(Complex64),
    b: Ptr(Complex64),
    c: Ptr(Float32),
    s: Ptr(Complex64)
) -> None: ...

@bind("CSCAL")
@external
def cscal(
    N: Ptr(Int32),
    CA: Ptr(Complex64),
    CX: Complex64[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("CSROT")
@external
def csrot(
    N: Ptr(Int32),
    CX: Complex64[Flat],
    INCX: Ptr(Int32),
    CY: Complex64[Flat],
    INCY: Ptr(Int32),
    C: Ptr(Float32),
    S: Ptr(Float32)
) -> None: ...

@bind("CSSCAL")
@external
def csscal(
    N: Ptr(Int32),
    SA: Ptr(Float32),
    CX: Complex64[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("CSWAP")
@external
def cswap(
    N: Ptr(Int32),
    CX: Complex64[Flat],
    INCX: Ptr(Int32),
    CY: Complex64[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("CSYMM")
@external
def csymm(
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    BETA: Ptr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("CSYR2K")
@external
def csyr2k(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    BETA: Ptr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("CSYRK")
@external
def csyrk(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    BETA: Ptr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("CTBMV")
@external
def ctbmv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex64[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("CTBSV")
@external
def ctbsv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex64[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("CTPMV")
@external
def ctpmv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    X: Complex64[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("CTPSV")
@external
def ctpsv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    X: Complex64[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("CTRMM")
@external
def ctrmm(
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANSA: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("CTRMV")
@external
def ctrmv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex64[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("CTRSM")
@external
def ctrsm(
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANSA: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("CTRSV")
@external
def ctrsv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex64[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("DASUM")
@external
def dasum(
    N: Ptr(Int32),
    DX: Float64[Flat],
    INCX: Ptr(Int32)
) -> Float64: ...

@bind("DAXPY")
@external
def daxpy(
    N: Ptr(Int32),
    DA: Ptr(Float64),
    DX: Float64[Flat],
    INCX: Ptr(Int32),
    DY: Float64[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("DCABS1")
@external
def dcabs1(
    Z: Ptr(Complex128)
) -> Float64: ...

@bind("DCOPY")
@external
def dcopy(
    N: Ptr(Int32),
    DX: Float64[Flat],
    INCX: Ptr(Int32),
    DY: Float64[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("DDOT")
@external
def ddot(
    N: Ptr(Int32),
    DX: Float64[Flat],
    INCX: Ptr(Int32),
    DY: Float64[Flat],
    INCY: Ptr(Int32)
) -> Float64: ...

@bind("DGBMV")
@external
def dgbmv(
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    ALPHA: Ptr(Float64),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Float64[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Float64),
    Y: Float64[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("DGEMM")
@external
def dgemm(
    TRANSA: Ptr(Const(String[1])),
    TRANSB: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Float64),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    BETA: Ptr(Float64),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("DGEMMTR")
@external
def dgemmtr(
    UPLO: Ptr(Const(String[1])),
    TRANSA: Ptr(Const(String[1])),
    TRANSB: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Float64),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    BETA: Ptr(Float64),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("DGEMV")
@external
def dgemv(
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Float64),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Float64[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Float64),
    Y: Float64[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("DGER")
@external
def dger(
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Float64),
    X: Float64[Flat],
    INCX: Ptr(Int32),
    Y: Float64[Flat],
    INCY: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("DNRM2")
@external
def dnrm2(
    n: Ptr(Int32),
    x: Float64[Flat],
    incx: Ptr(Int32)
) -> Float64: ...

@bind("DROT")
@external
def drot(
    N: Ptr(Int32),
    DX: Float64[Flat],
    INCX: Ptr(Int32),
    DY: Float64[Flat],
    INCY: Ptr(Int32),
    C: Ptr(Float64),
    S: Ptr(Float64)
) -> None: ...

@bind("DROTG")
@external
def drotg(
    a: Ptr(Float64),
    b: Ptr(Float64),
    c: Ptr(Float64),
    s: Ptr(Float64)
) -> None: ...

@bind("DROTM")
@external
def drotm(
    N: Ptr(Int32),
    DX: Float64[Flat],
    INCX: Ptr(Int32),
    DY: Float64[Flat],
    INCY: Ptr(Int32),
    DPARAM: Float64[5]
) -> None: ...

@bind("DROTMG")
@external
def drotmg(
    DD1: Ptr(Float64),
    DD2: Ptr(Float64),
    DX1: Ptr(Float64),
    DY1: Ptr(Float64),
    DPARAM: Float64[5]
) -> None: ...

@bind("DSBMV")
@external
def dsbmv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Float64),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Float64[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Float64),
    Y: Float64[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("DSCAL")
@external
def dscal(
    N: Ptr(Int32),
    DA: Ptr(Float64),
    DX: Float64[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("DSDOT")
@external
def dsdot(
    N: Ptr(Int32),
    SX: Float32[Flat],
    INCX: Ptr(Int32),
    SY: Float32[Flat],
    INCY: Ptr(Int32)
) -> Float64: ...

@bind("DSPMV")
@external
def dspmv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Float64),
    AP: Float64[Flat],
    X: Float64[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Float64),
    Y: Float64[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("DSPR")
@external
def dspr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Float64),
    X: Float64[Flat],
    INCX: Ptr(Int32),
    AP: Float64[Flat]
) -> None: ...

@bind("DSPR2")
@external
def dspr2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Float64),
    X: Float64[Flat],
    INCX: Ptr(Int32),
    Y: Float64[Flat],
    INCY: Ptr(Int32),
    AP: Float64[Flat]
) -> None: ...

@bind("DSWAP")
@external
def dswap(
    N: Ptr(Int32),
    DX: Float64[Flat],
    INCX: Ptr(Int32),
    DY: Float64[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("DSYMM")
@external
def dsymm(
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Float64),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    BETA: Ptr(Float64),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("DSYMV")
@external
def dsymv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Float64),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Float64[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Float64),
    Y: Float64[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("DSYR")
@external
def dsyr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Float64),
    X: Float64[Flat],
    INCX: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("DSYR2")
@external
def dsyr2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Float64),
    X: Float64[Flat],
    INCX: Ptr(Int32),
    Y: Float64[Flat],
    INCY: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("DSYR2K")
@external
def dsyr2k(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Float64),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    BETA: Ptr(Float64),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("DSYRK")
@external
def dsyrk(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Float64),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    BETA: Ptr(Float64),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("DTBMV")
@external
def dtbmv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Float64[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("DTBSV")
@external
def dtbsv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Float64[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("DTPMV")
@external
def dtpmv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    X: Float64[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("DTPSV")
@external
def dtpsv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    X: Float64[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("DTRMM")
@external
def dtrmm(
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANSA: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Float64),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("DTRMV")
@external
def dtrmv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Float64[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("DTRSM")
@external
def dtrsm(
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANSA: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Float64),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("DTRSV")
@external
def dtrsv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Float64[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("DZASUM")
@external
def dzasum(
    N: Ptr(Int32),
    ZX: Complex128[Flat],
    INCX: Ptr(Int32)
) -> Float64: ...

@bind("DZNRM2")
@external
def dznrm2(
    n: Ptr(Int32),
    x: Complex128[Flat],
    incx: Ptr(Int32)
) -> Float64: ...

@bind("ICAMAX")
@external
def icamax(
    N: Ptr(Int32),
    CX: Complex64[Flat],
    INCX: Ptr(Int32)
) -> Int32: ...

@bind("IDAMAX")
@external
def idamax(
    N: Ptr(Int32),
    DX: Float64[Flat],
    INCX: Ptr(Int32)
) -> Int32: ...

@bind("ISAMAX")
@external
def isamax(
    N: Ptr(Int32),
    SX: Float32[Flat],
    INCX: Ptr(Int32)
) -> Int32: ...

@bind("IZAMAX")
@external
def izamax(
    N: Ptr(Int32),
    ZX: Complex128[Flat],
    INCX: Ptr(Int32)
) -> Int32: ...

@bind("LSAME")
@external
def lsame(
    CA: Ptr(Const(String[1])),
    CB: Ptr(Const(String[1]))
) -> Bool: ...

@bind("SASUM")
@external
def sasum(
    N: Ptr(Int32),
    SX: Float32[Flat],
    INCX: Ptr(Int32)
) -> Float32: ...

@bind("SAXPY")
@external
def saxpy(
    N: Ptr(Int32),
    SA: Ptr(Float32),
    SX: Float32[Flat],
    INCX: Ptr(Int32),
    SY: Float32[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("SCABS1")
@external
def scabs1(
    Z: Ptr(Complex64)
) -> Float32: ...

@bind("SCASUM")
@external
def scasum(
    N: Ptr(Int32),
    CX: Complex64[Flat],
    INCX: Ptr(Int32)
) -> Float32: ...

@bind("SCNRM2")
@external
def scnrm2(
    n: Ptr(Int32),
    x: Complex64[Flat],
    incx: Ptr(Int32)
) -> Float32: ...

@bind("SCOPY")
@external
def scopy(
    N: Ptr(Int32),
    SX: Float32[Flat],
    INCX: Ptr(Int32),
    SY: Float32[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("SDOT")
@external
def sdot(
    N: Ptr(Int32),
    SX: Float32[Flat],
    INCX: Ptr(Int32),
    SY: Float32[Flat],
    INCY: Ptr(Int32)
) -> Float32: ...

@bind("SDSDOT")
@external
def sdsdot(
    N: Ptr(Int32),
    SB: Ptr(Float32),
    SX: Float32[Flat],
    INCX: Ptr(Int32),
    SY: Float32[Flat],
    INCY: Ptr(Int32)
) -> Float32: ...

@bind("SGBMV")
@external
def sgbmv(
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    ALPHA: Ptr(Float32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    X: Float32[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Float32),
    Y: Float32[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("SGEMM")
@external
def sgemm(
    TRANSA: Ptr(Const(String[1])),
    TRANSB: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Float32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    BETA: Ptr(Float32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("SGEMMTR")
@external
def sgemmtr(
    UPLO: Ptr(Const(String[1])),
    TRANSA: Ptr(Const(String[1])),
    TRANSB: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Float32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    BETA: Ptr(Float32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("SGEMV")
@external
def sgemv(
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Float32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    X: Float32[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Float32),
    Y: Float32[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("SGER")
@external
def sger(
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Float32),
    X: Float32[Flat],
    INCX: Ptr(Int32),
    Y: Float32[Flat],
    INCY: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("SNRM2")
@external
def snrm2(
    n: Ptr(Int32),
    x: Float32[Flat],
    incx: Ptr(Int32)
) -> Float32: ...

@bind("SROT")
@external
def srot(
    N: Ptr(Int32),
    SX: Float32[Flat],
    INCX: Ptr(Int32),
    SY: Float32[Flat],
    INCY: Ptr(Int32),
    C: Ptr(Float32),
    S: Ptr(Float32)
) -> None: ...

@bind("SROTG")
@external
def srotg(
    a: Ptr(Float32),
    b: Ptr(Float32),
    c: Ptr(Float32),
    s: Ptr(Float32)
) -> None: ...

@bind("SROTM")
@external
def srotm(
    N: Ptr(Int32),
    SX: Float32[Flat],
    INCX: Ptr(Int32),
    SY: Float32[Flat],
    INCY: Ptr(Int32),
    SPARAM: Float32[5]
) -> None: ...

@bind("SROTMG")
@external
def srotmg(
    SD1: Ptr(Float32),
    SD2: Ptr(Float32),
    SX1: Ptr(Float32),
    SY1: Ptr(Float32),
    SPARAM: Float32[5]
) -> None: ...

@bind("SSBMV")
@external
def ssbmv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Float32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    X: Float32[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Float32),
    Y: Float32[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("SSCAL")
@external
def sscal(
    N: Ptr(Int32),
    SA: Ptr(Float32),
    SX: Float32[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("SSPMV")
@external
def sspmv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Float32),
    AP: Float32[Flat],
    X: Float32[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Float32),
    Y: Float32[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("SSPR")
@external
def sspr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Float32),
    X: Float32[Flat],
    INCX: Ptr(Int32),
    AP: Float32[Flat]
) -> None: ...

@bind("SSPR2")
@external
def sspr2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Float32),
    X: Float32[Flat],
    INCX: Ptr(Int32),
    Y: Float32[Flat],
    INCY: Ptr(Int32),
    AP: Float32[Flat]
) -> None: ...

@bind("SSWAP")
@external
def sswap(
    N: Ptr(Int32),
    SX: Float32[Flat],
    INCX: Ptr(Int32),
    SY: Float32[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("SSYMM")
@external
def ssymm(
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Float32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    BETA: Ptr(Float32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("SSYMV")
@external
def ssymv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Float32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    X: Float32[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Float32),
    Y: Float32[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("SSYR")
@external
def ssyr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Float32),
    X: Float32[Flat],
    INCX: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("SSYR2")
@external
def ssyr2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Float32),
    X: Float32[Flat],
    INCX: Ptr(Int32),
    Y: Float32[Flat],
    INCY: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("SSYR2K")
@external
def ssyr2k(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Float32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    BETA: Ptr(Float32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("SSYRK")
@external
def ssyrk(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Float32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    BETA: Ptr(Float32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("STBMV")
@external
def stbmv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    X: Float32[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("STBSV")
@external
def stbsv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    X: Float32[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("STPMV")
@external
def stpmv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    X: Float32[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("STPSV")
@external
def stpsv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    X: Float32[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("STRMM")
@external
def strmm(
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANSA: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Float32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("STRMV")
@external
def strmv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    X: Float32[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("STRSM")
@external
def strsm(
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANSA: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Float32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("STRSV")
@external
def strsv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    X: Float32[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("XERBLA")
@external
def xerbla(
    SRNAME: Ptr(Const(String)),
    INFO: Ptr(Int32)
) -> None: ...

@bind("XERBLA_ARRAY")
@external
def xerbla_array(
    SRNAME_ARRAY: String[1][SRNAME_LEN],
    SRNAME_LEN: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZAXPY")
@external
def zaxpy(
    N: Ptr(Int32),
    ZA: Ptr(Complex128),
    ZX: Complex128[Flat],
    INCX: Ptr(Int32),
    ZY: Complex128[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("ZCOPY")
@external
def zcopy(
    N: Ptr(Int32),
    ZX: Complex128[Flat],
    INCX: Ptr(Int32),
    ZY: Complex128[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("ZDOTC")
@external
def zdotc(
    N: Ptr(Int32),
    ZX: Complex128[Flat],
    INCX: Ptr(Int32),
    ZY: Complex128[Flat],
    INCY: Ptr(Int32)
) -> Complex128: ...

@bind("ZDOTU")
@external
def zdotu(
    N: Ptr(Int32),
    ZX: Complex128[Flat],
    INCX: Ptr(Int32),
    ZY: Complex128[Flat],
    INCY: Ptr(Int32)
) -> Complex128: ...

@bind("ZDROT")
@external
def zdrot(
    N: Ptr(Int32),
    ZX: Complex128[Flat],
    INCX: Ptr(Int32),
    ZY: Complex128[Flat],
    INCY: Ptr(Int32),
    C: Ptr(Float64),
    S: Ptr(Float64)
) -> None: ...

@bind("ZDSCAL")
@external
def zdscal(
    N: Ptr(Int32),
    DA: Ptr(Float64),
    ZX: Complex128[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("ZGBMV")
@external
def zgbmv(
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex128[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Complex128),
    Y: Complex128[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("ZGEMM")
@external
def zgemm(
    TRANSA: Ptr(Const(String[1])),
    TRANSB: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    BETA: Ptr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("ZGEMMTR")
@external
def zgemmtr(
    UPLO: Ptr(Const(String[1])),
    TRANSA: Ptr(Const(String[1])),
    TRANSB: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    BETA: Ptr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("ZGEMV")
@external
def zgemv(
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex128[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Complex128),
    Y: Complex128[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("ZGERC")
@external
def zgerc(
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    X: Complex128[Flat],
    INCX: Ptr(Int32),
    Y: Complex128[Flat],
    INCY: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("ZGERU")
@external
def zgeru(
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    X: Complex128[Flat],
    INCX: Ptr(Int32),
    Y: Complex128[Flat],
    INCY: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("ZHBMV")
@external
def zhbmv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex128[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Complex128),
    Y: Complex128[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("ZHEMM")
@external
def zhemm(
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    BETA: Ptr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("ZHEMV")
@external
def zhemv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex128[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Complex128),
    Y: Complex128[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("ZHER")
@external
def zher(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Float64),
    X: Complex128[Flat],
    INCX: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("ZHER2")
@external
def zher2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    X: Complex128[Flat],
    INCX: Ptr(Int32),
    Y: Complex128[Flat],
    INCY: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("ZHER2K")
@external
def zher2k(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    BETA: Ptr(Float64),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("ZHERK")
@external
def zherk(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Float64),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    BETA: Ptr(Float64),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("ZHPMV")
@external
def zhpmv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    AP: Complex128[Flat],
    X: Complex128[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Complex128),
    Y: Complex128[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("ZHPR")
@external
def zhpr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Float64),
    X: Complex128[Flat],
    INCX: Ptr(Int32),
    AP: Complex128[Flat]
) -> None: ...

@bind("ZHPR2")
@external
def zhpr2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    X: Complex128[Flat],
    INCX: Ptr(Int32),
    Y: Complex128[Flat],
    INCY: Ptr(Int32),
    AP: Complex128[Flat]
) -> None: ...

@bind("ZROTG")
@external
def zrotg(
    a: Ptr(Complex128),
    b: Ptr(Complex128),
    c: Ptr(Float64),
    s: Ptr(Complex128)
) -> None: ...

@bind("ZSCAL")
@external
def zscal(
    N: Ptr(Int32),
    ZA: Ptr(Complex128),
    ZX: Complex128[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("ZSWAP")
@external
def zswap(
    N: Ptr(Int32),
    ZX: Complex128[Flat],
    INCX: Ptr(Int32),
    ZY: Complex128[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("ZSYMM")
@external
def zsymm(
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    BETA: Ptr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("ZSYR2K")
@external
def zsyr2k(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    BETA: Ptr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("ZSYRK")
@external
def zsyrk(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    BETA: Ptr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32)
) -> None: ...

@bind("ZTBMV")
@external
def ztbmv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex128[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("ZTBSV")
@external
def ztbsv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex128[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("ZTPMV")
@external
def ztpmv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    X: Complex128[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("ZTPSV")
@external
def ztpsv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    X: Complex128[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("ZTRMM")
@external
def ztrmm(
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANSA: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("ZTRMV")
@external
def ztrmv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex128[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("ZTRSM")
@external
def ztrsm(
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANSA: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("ZTRSV")
@external
def ztrsv(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex128[Flat],
    INCX: Ptr(Int32)
) -> None: ...
