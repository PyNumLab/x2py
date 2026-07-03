@bind("CAXPY")
@external
def caxpy(
    N: Addr(Int32),
    CA: Addr(Complex64),
    CX: Complex64[Flat],
    INCX: Addr(Int32),
    CY: Complex64[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("CCOPY")
@external
def ccopy(
    N: Addr(Int32),
    CX: Complex64[Flat],
    INCX: Addr(Int32),
    CY: Complex64[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("CDOTC")
@external
def cdotc(
    N: Addr(Int32),
    CX: Complex64[Flat],
    INCX: Addr(Int32),
    CY: Complex64[Flat],
    INCY: Addr(Int32)
) -> Complex64: ...

@bind("CDOTU")
@external
def cdotu(
    N: Addr(Int32),
    CX: Complex64[Flat],
    INCX: Addr(Int32),
    CY: Complex64[Flat],
    INCY: Addr(Int32)
) -> Complex64: ...

@bind("CGBMV")
@external
def cgbmv(
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    ALPHA: Addr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex64[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Complex64),
    Y: Complex64[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("CGEMM")
@external
def cgemm(
    TRANSA: Addr(Const(String[1])),
    TRANSB: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    BETA: Addr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("CGEMMTR")
@external
def cgemmtr(
    UPLO: Addr(Const(String[1])),
    TRANSA: Addr(Const(String[1])),
    TRANSB: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    BETA: Addr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("CGEMV")
@external
def cgemv(
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex64[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Complex64),
    Y: Complex64[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("CGERC")
@external
def cgerc(
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Complex64),
    X: Complex64[Flat],
    INCX: Addr(Int32),
    Y: Complex64[Flat],
    INCY: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("CGERU")
@external
def cgeru(
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Complex64),
    X: Complex64[Flat],
    INCX: Addr(Int32),
    Y: Complex64[Flat],
    INCY: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("CHBMV")
@external
def chbmv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex64[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Complex64),
    Y: Complex64[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("CHEMM")
@external
def chemm(
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    BETA: Addr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("CHEMV")
@external
def chemv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex64[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Complex64),
    Y: Complex64[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("CHER")
@external
def cher(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Float32),
    X: Complex64[Flat],
    INCX: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("CHER2")
@external
def cher2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Complex64),
    X: Complex64[Flat],
    INCX: Addr(Int32),
    Y: Complex64[Flat],
    INCY: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("CHER2K")
@external
def cher2k(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    BETA: Addr(Float32),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("CHERK")
@external
def cherk(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Float32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    BETA: Addr(Float32),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("CHPMV")
@external
def chpmv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Complex64),
    AP: Complex64[Flat],
    X: Complex64[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Complex64),
    Y: Complex64[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("CHPR")
@external
def chpr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Float32),
    X: Complex64[Flat],
    INCX: Addr(Int32),
    AP: Complex64[Flat]
) -> None: ...

@bind("CHPR2")
@external
def chpr2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Complex64),
    X: Complex64[Flat],
    INCX: Addr(Int32),
    Y: Complex64[Flat],
    INCY: Addr(Int32),
    AP: Complex64[Flat]
) -> None: ...

@bind("CROTG")
@external
def crotg(
    a: Addr(Complex64),
    b: Addr(Complex64),
    c: Addr(Float32),
    s: Addr(Complex64)
) -> None: ...

@bind("CSCAL")
@external
def cscal(
    N: Addr(Int32),
    CA: Addr(Complex64),
    CX: Complex64[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("CSROT")
@external
def csrot(
    N: Addr(Int32),
    CX: Complex64[Flat],
    INCX: Addr(Int32),
    CY: Complex64[Flat],
    INCY: Addr(Int32),
    C: Addr(Float32),
    S: Addr(Float32)
) -> None: ...

@bind("CSSCAL")
@external
def csscal(
    N: Addr(Int32),
    SA: Addr(Float32),
    CX: Complex64[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("CSWAP")
@external
def cswap(
    N: Addr(Int32),
    CX: Complex64[Flat],
    INCX: Addr(Int32),
    CY: Complex64[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("CSYMM")
@external
def csymm(
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    BETA: Addr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("CSYR2K")
@external
def csyr2k(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32),
    BETA: Addr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("CSYRK")
@external
def csyrk(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    BETA: Addr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("CTBMV")
@external
def ctbmv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex64[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("CTBSV")
@external
def ctbsv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex64[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("CTPMV")
@external
def ctpmv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    X: Complex64[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("CTPSV")
@external
def ctpsv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex64[Flat],
    X: Complex64[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("CTRMM")
@external
def ctrmm(
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANSA: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("CTRMV")
@external
def ctrmv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex64[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("CTRSM")
@external
def ctrsm(
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANSA: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("CTRSV")
@external
def ctrsv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex64[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("DASUM")
@external
def dasum(
    N: Addr(Int32),
    DX: Float64[Flat],
    INCX: Addr(Int32)
) -> Float64: ...

@bind("DAXPY")
@external
def daxpy(
    N: Addr(Int32),
    DA: Addr(Float64),
    DX: Float64[Flat],
    INCX: Addr(Int32),
    DY: Float64[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("DCABS1")
@external
def dcabs1(
    Z: Addr(Complex128)
) -> Float64: ...

@bind("DCOPY")
@external
def dcopy(
    N: Addr(Int32),
    DX: Float64[Flat],
    INCX: Addr(Int32),
    DY: Float64[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("DDOT")
@external
def ddot(
    N: Addr(Int32),
    DX: Float64[Flat],
    INCX: Addr(Int32),
    DY: Float64[Flat],
    INCY: Addr(Int32)
) -> Float64: ...

@bind("DGBMV")
@external
def dgbmv(
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    ALPHA: Addr(Float64),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    X: Float64[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Float64),
    Y: Float64[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("DGEMM")
@external
def dgemm(
    TRANSA: Addr(Const(String[1])),
    TRANSB: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Float64),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    BETA: Addr(Float64),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("DGEMMTR")
@external
def dgemmtr(
    UPLO: Addr(Const(String[1])),
    TRANSA: Addr(Const(String[1])),
    TRANSB: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Float64),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    BETA: Addr(Float64),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("DGEMV")
@external
def dgemv(
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Float64),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    X: Float64[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Float64),
    Y: Float64[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("DGER")
@external
def dger(
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Float64),
    X: Float64[Flat],
    INCX: Addr(Int32),
    Y: Float64[Flat],
    INCY: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("DNRM2")
@external
def dnrm2(
    n: Addr(Int32),
    x: Float64[Flat],
    incx: Addr(Int32)
) -> Float64: ...

@bind("DROT")
@external
def drot(
    N: Addr(Int32),
    DX: Float64[Flat],
    INCX: Addr(Int32),
    DY: Float64[Flat],
    INCY: Addr(Int32),
    C: Addr(Float64),
    S: Addr(Float64)
) -> None: ...

@bind("DROTG")
@external
def drotg(
    a: Addr(Float64),
    b: Addr(Float64),
    c: Addr(Float64),
    s: Addr(Float64)
) -> None: ...

@bind("DROTM")
@external
def drotm(
    N: Addr(Int32),
    DX: Float64[Flat],
    INCX: Addr(Int32),
    DY: Float64[Flat],
    INCY: Addr(Int32),
    DPARAM: Float64[5]
) -> None: ...

@bind("DROTMG")
@external
def drotmg(
    DD1: Addr(Float64),
    DD2: Addr(Float64),
    DX1: Addr(Float64),
    DY1: Addr(Float64),
    DPARAM: Float64[5]
) -> None: ...

@bind("DSBMV")
@external
def dsbmv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Float64),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    X: Float64[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Float64),
    Y: Float64[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("DSCAL")
@external
def dscal(
    N: Addr(Int32),
    DA: Addr(Float64),
    DX: Float64[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("DSDOT")
@external
def dsdot(
    N: Addr(Int32),
    SX: Float32[Flat],
    INCX: Addr(Int32),
    SY: Float32[Flat],
    INCY: Addr(Int32)
) -> Float64: ...

@bind("DSPMV")
@external
def dspmv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Float64),
    AP: Float64[Flat],
    X: Float64[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Float64),
    Y: Float64[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("DSPR")
@external
def dspr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Float64),
    X: Float64[Flat],
    INCX: Addr(Int32),
    AP: Float64[Flat]
) -> None: ...

@bind("DSPR2")
@external
def dspr2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Float64),
    X: Float64[Flat],
    INCX: Addr(Int32),
    Y: Float64[Flat],
    INCY: Addr(Int32),
    AP: Float64[Flat]
) -> None: ...

@bind("DSWAP")
@external
def dswap(
    N: Addr(Int32),
    DX: Float64[Flat],
    INCX: Addr(Int32),
    DY: Float64[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("DSYMM")
@external
def dsymm(
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Float64),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    BETA: Addr(Float64),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("DSYMV")
@external
def dsymv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Float64),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    X: Float64[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Float64),
    Y: Float64[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("DSYR")
@external
def dsyr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Float64),
    X: Float64[Flat],
    INCX: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("DSYR2")
@external
def dsyr2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Float64),
    X: Float64[Flat],
    INCX: Addr(Int32),
    Y: Float64[Flat],
    INCY: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("DSYR2K")
@external
def dsyr2k(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Float64),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32),
    BETA: Addr(Float64),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("DSYRK")
@external
def dsyrk(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Float64),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    BETA: Addr(Float64),
    C: Float64[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("DTBMV")
@external
def dtbmv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    X: Float64[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("DTBSV")
@external
def dtbsv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    X: Float64[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("DTPMV")
@external
def dtpmv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    X: Float64[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("DTPSV")
@external
def dtpsv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float64[Flat],
    X: Float64[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("DTRMM")
@external
def dtrmm(
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANSA: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Float64),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("DTRMV")
@external
def dtrmv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    X: Float64[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("DTRSM")
@external
def dtrsm(
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANSA: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Float64),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    B: Float64[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("DTRSV")
@external
def dtrsv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float64[LDA, Flat],
    LDA: Addr(Int32),
    X: Float64[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("DZASUM")
@external
def dzasum(
    N: Addr(Int32),
    ZX: Complex128[Flat],
    INCX: Addr(Int32)
) -> Float64: ...

@bind("DZNRM2")
@external
def dznrm2(
    n: Addr(Int32),
    x: Complex128[Flat],
    incx: Addr(Int32)
) -> Float64: ...

@bind("ICAMAX")
@external
def icamax(
    N: Addr(Int32),
    CX: Complex64[Flat],
    INCX: Addr(Int32)
) -> Int32: ...

@bind("IDAMAX")
@external
def idamax(
    N: Addr(Int32),
    DX: Float64[Flat],
    INCX: Addr(Int32)
) -> Int32: ...

@bind("ISAMAX")
@external
def isamax(
    N: Addr(Int32),
    SX: Float32[Flat],
    INCX: Addr(Int32)
) -> Int32: ...

@bind("IZAMAX")
@external
def izamax(
    N: Addr(Int32),
    ZX: Complex128[Flat],
    INCX: Addr(Int32)
) -> Int32: ...

@bind("LSAME")
@external
def lsame(
    CA: Addr(Const(String[1])),
    CB: Addr(Const(String[1]))
) -> Bool: ...

@bind("SASUM")
@external
def sasum(
    N: Addr(Int32),
    SX: Float32[Flat],
    INCX: Addr(Int32)
) -> Float32: ...

@bind("SAXPY")
@external
def saxpy(
    N: Addr(Int32),
    SA: Addr(Float32),
    SX: Float32[Flat],
    INCX: Addr(Int32),
    SY: Float32[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("SCABS1")
@external
def scabs1(
    Z: Addr(Complex64)
) -> Float32: ...

@bind("SCASUM")
@external
def scasum(
    N: Addr(Int32),
    CX: Complex64[Flat],
    INCX: Addr(Int32)
) -> Float32: ...

@bind("SCNRM2")
@external
def scnrm2(
    n: Addr(Int32),
    x: Complex64[Flat],
    incx: Addr(Int32)
) -> Float32: ...

@bind("SCOPY")
@external
def scopy(
    N: Addr(Int32),
    SX: Float32[Flat],
    INCX: Addr(Int32),
    SY: Float32[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("SDOT")
@external
def sdot(
    N: Addr(Int32),
    SX: Float32[Flat],
    INCX: Addr(Int32),
    SY: Float32[Flat],
    INCY: Addr(Int32)
) -> Float32: ...

@bind("SDSDOT")
@external
def sdsdot(
    N: Addr(Int32),
    SB: Addr(Float32),
    SX: Float32[Flat],
    INCX: Addr(Int32),
    SY: Float32[Flat],
    INCY: Addr(Int32)
) -> Float32: ...

@bind("SGBMV")
@external
def sgbmv(
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    ALPHA: Addr(Float32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    X: Float32[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Float32),
    Y: Float32[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("SGEMM")
@external
def sgemm(
    TRANSA: Addr(Const(String[1])),
    TRANSB: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Float32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    BETA: Addr(Float32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("SGEMMTR")
@external
def sgemmtr(
    UPLO: Addr(Const(String[1])),
    TRANSA: Addr(Const(String[1])),
    TRANSB: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Float32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    BETA: Addr(Float32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("SGEMV")
@external
def sgemv(
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Float32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    X: Float32[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Float32),
    Y: Float32[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("SGER")
@external
def sger(
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Float32),
    X: Float32[Flat],
    INCX: Addr(Int32),
    Y: Float32[Flat],
    INCY: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("SNRM2")
@external
def snrm2(
    n: Addr(Int32),
    x: Float32[Flat],
    incx: Addr(Int32)
) -> Float32: ...

@bind("SROT")
@external
def srot(
    N: Addr(Int32),
    SX: Float32[Flat],
    INCX: Addr(Int32),
    SY: Float32[Flat],
    INCY: Addr(Int32),
    C: Addr(Float32),
    S: Addr(Float32)
) -> None: ...

@bind("SROTG")
@external
def srotg(
    a: Addr(Float32),
    b: Addr(Float32),
    c: Addr(Float32),
    s: Addr(Float32)
) -> None: ...

@bind("SROTM")
@external
def srotm(
    N: Addr(Int32),
    SX: Float32[Flat],
    INCX: Addr(Int32),
    SY: Float32[Flat],
    INCY: Addr(Int32),
    SPARAM: Float32[5]
) -> None: ...

@bind("SROTMG")
@external
def srotmg(
    SD1: Addr(Float32),
    SD2: Addr(Float32),
    SX1: Addr(Float32),
    SY1: Addr(Float32),
    SPARAM: Float32[5]
) -> None: ...

@bind("SSBMV")
@external
def ssbmv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Float32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    X: Float32[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Float32),
    Y: Float32[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("SSCAL")
@external
def sscal(
    N: Addr(Int32),
    SA: Addr(Float32),
    SX: Float32[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("SSPMV")
@external
def sspmv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Float32),
    AP: Float32[Flat],
    X: Float32[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Float32),
    Y: Float32[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("SSPR")
@external
def sspr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Float32),
    X: Float32[Flat],
    INCX: Addr(Int32),
    AP: Float32[Flat]
) -> None: ...

@bind("SSPR2")
@external
def sspr2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Float32),
    X: Float32[Flat],
    INCX: Addr(Int32),
    Y: Float32[Flat],
    INCY: Addr(Int32),
    AP: Float32[Flat]
) -> None: ...

@bind("SSWAP")
@external
def sswap(
    N: Addr(Int32),
    SX: Float32[Flat],
    INCX: Addr(Int32),
    SY: Float32[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("SSYMM")
@external
def ssymm(
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Float32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    BETA: Addr(Float32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("SSYMV")
@external
def ssymv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Float32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    X: Float32[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Float32),
    Y: Float32[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("SSYR")
@external
def ssyr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Float32),
    X: Float32[Flat],
    INCX: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("SSYR2")
@external
def ssyr2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Float32),
    X: Float32[Flat],
    INCX: Addr(Int32),
    Y: Float32[Flat],
    INCY: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("SSYR2K")
@external
def ssyr2k(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Float32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32),
    BETA: Addr(Float32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("SSYRK")
@external
def ssyrk(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Float32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    BETA: Addr(Float32),
    C: Float32[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("STBMV")
@external
def stbmv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    X: Float32[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("STBSV")
@external
def stbsv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    X: Float32[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("STPMV")
@external
def stpmv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    X: Float32[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("STPSV")
@external
def stpsv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Float32[Flat],
    X: Float32[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("STRMM")
@external
def strmm(
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANSA: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Float32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("STRMV")
@external
def strmv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    X: Float32[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("STRSM")
@external
def strsm(
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANSA: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Float32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    B: Float32[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("STRSV")
@external
def strsv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Float32[LDA, Flat],
    LDA: Addr(Int32),
    X: Float32[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("XERBLA")
@external
def xerbla(
    SRNAME: Addr(Const(String)),
    INFO: Addr(Int32)
) -> None: ...

@bind("XERBLA_ARRAY")
@external
def xerbla_array(
    SRNAME_ARRAY: String[1][SRNAME_LEN],
    SRNAME_LEN: Addr(Int32),
    INFO: Addr(Int32)
) -> None: ...

@bind("ZAXPY")
@external
def zaxpy(
    N: Addr(Int32),
    ZA: Addr(Complex128),
    ZX: Complex128[Flat],
    INCX: Addr(Int32),
    ZY: Complex128[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("ZCOPY")
@external
def zcopy(
    N: Addr(Int32),
    ZX: Complex128[Flat],
    INCX: Addr(Int32),
    ZY: Complex128[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("ZDOTC")
@external
def zdotc(
    N: Addr(Int32),
    ZX: Complex128[Flat],
    INCX: Addr(Int32),
    ZY: Complex128[Flat],
    INCY: Addr(Int32)
) -> Complex128: ...

@bind("ZDOTU")
@external
def zdotu(
    N: Addr(Int32),
    ZX: Complex128[Flat],
    INCX: Addr(Int32),
    ZY: Complex128[Flat],
    INCY: Addr(Int32)
) -> Complex128: ...

@bind("ZDROT")
@external
def zdrot(
    N: Addr(Int32),
    ZX: Complex128[Flat],
    INCX: Addr(Int32),
    ZY: Complex128[Flat],
    INCY: Addr(Int32),
    C: Addr(Float64),
    S: Addr(Float64)
) -> None: ...

@bind("ZDSCAL")
@external
def zdscal(
    N: Addr(Int32),
    DA: Addr(Float64),
    ZX: Complex128[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("ZGBMV")
@external
def zgbmv(
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    KL: Addr(Int32),
    KU: Addr(Int32),
    ALPHA: Addr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex128[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Complex128),
    Y: Complex128[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("ZGEMM")
@external
def zgemm(
    TRANSA: Addr(Const(String[1])),
    TRANSB: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    BETA: Addr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("ZGEMMTR")
@external
def zgemmtr(
    UPLO: Addr(Const(String[1])),
    TRANSA: Addr(Const(String[1])),
    TRANSB: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    BETA: Addr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("ZGEMV")
@external
def zgemv(
    TRANS: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex128[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Complex128),
    Y: Complex128[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("ZGERC")
@external
def zgerc(
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Complex128),
    X: Complex128[Flat],
    INCX: Addr(Int32),
    Y: Complex128[Flat],
    INCY: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("ZGERU")
@external
def zgeru(
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Complex128),
    X: Complex128[Flat],
    INCX: Addr(Int32),
    Y: Complex128[Flat],
    INCY: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("ZHBMV")
@external
def zhbmv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex128[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Complex128),
    Y: Complex128[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("ZHEMM")
@external
def zhemm(
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    BETA: Addr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("ZHEMV")
@external
def zhemv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex128[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Complex128),
    Y: Complex128[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("ZHER")
@external
def zher(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Float64),
    X: Complex128[Flat],
    INCX: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("ZHER2")
@external
def zher2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Complex128),
    X: Complex128[Flat],
    INCX: Addr(Int32),
    Y: Complex128[Flat],
    INCY: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32)
) -> None: ...

@bind("ZHER2K")
@external
def zher2k(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    BETA: Addr(Float64),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("ZHERK")
@external
def zherk(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Float64),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    BETA: Addr(Float64),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("ZHPMV")
@external
def zhpmv(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Complex128),
    AP: Complex128[Flat],
    X: Complex128[Flat],
    INCX: Addr(Int32),
    BETA: Addr(Complex128),
    Y: Complex128[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("ZHPR")
@external
def zhpr(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Float64),
    X: Complex128[Flat],
    INCX: Addr(Int32),
    AP: Complex128[Flat]
) -> None: ...

@bind("ZHPR2")
@external
def zhpr2(
    UPLO: Addr(Const(String[1])),
    N: Addr(Int32),
    ALPHA: Addr(Complex128),
    X: Complex128[Flat],
    INCX: Addr(Int32),
    Y: Complex128[Flat],
    INCY: Addr(Int32),
    AP: Complex128[Flat]
) -> None: ...

@bind("ZROTG")
@external
def zrotg(
    a: Addr(Complex128),
    b: Addr(Complex128),
    c: Addr(Float64),
    s: Addr(Complex128)
) -> None: ...

@bind("ZSCAL")
@external
def zscal(
    N: Addr(Int32),
    ZA: Addr(Complex128),
    ZX: Complex128[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("ZSWAP")
@external
def zswap(
    N: Addr(Int32),
    ZX: Complex128[Flat],
    INCX: Addr(Int32),
    ZY: Complex128[Flat],
    INCY: Addr(Int32)
) -> None: ...

@bind("ZSYMM")
@external
def zsymm(
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    BETA: Addr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("ZSYR2K")
@external
def zsyr2k(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32),
    BETA: Addr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("ZSYRK")
@external
def zsyrk(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    ALPHA: Addr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    BETA: Addr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Addr(Int32)
) -> None: ...

@bind("ZTBMV")
@external
def ztbmv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex128[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("ZTBSV")
@external
def ztbsv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    K: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex128[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("ZTPMV")
@external
def ztpmv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    X: Complex128[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("ZTPSV")
@external
def ztpsv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    AP: Complex128[Flat],
    X: Complex128[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("ZTRMM")
@external
def ztrmm(
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANSA: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("ZTRMV")
@external
def ztrmv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex128[Flat],
    INCX: Addr(Int32)
) -> None: ...

@bind("ZTRSM")
@external
def ztrsm(
    SIDE: Addr(Const(String[1])),
    UPLO: Addr(Const(String[1])),
    TRANSA: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    M: Addr(Int32),
    N: Addr(Int32),
    ALPHA: Addr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Addr(Int32)
) -> None: ...

@bind("ZTRSV")
@external
def ztrsv(
    UPLO: Addr(Const(String[1])),
    TRANS: Addr(Const(String[1])),
    DIAG: Addr(Const(String[1])),
    N: Addr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Addr(Int32),
    X: Complex128[Flat],
    INCX: Addr(Int32)
) -> None: ...
