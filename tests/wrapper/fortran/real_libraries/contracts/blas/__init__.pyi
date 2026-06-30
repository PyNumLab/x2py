@bind("CAXPY")
@external
def caxpy(
    N: Ref(Int32),
    CA: Ref(Complex64),
    CX: Complex64[Flat],
    INCX: Ref(Int32),
    CY: Complex64[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("CCOPY")
@external
def ccopy(
    N: Ref(Int32),
    CX: Complex64[Flat],
    INCX: Ref(Int32),
    CY: Complex64[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("CDOTC")
@external
def cdotc(
    N: Ref(Int32),
    CX: Complex64[Flat],
    INCX: Ref(Int32),
    CY: Complex64[Flat],
    INCY: Ref(Int32)
) -> Complex64: ...

@bind("CDOTU")
@external
def cdotu(
    N: Ref(Int32),
    CX: Complex64[Flat],
    INCX: Ref(Int32),
    CY: Complex64[Flat],
    INCY: Ref(Int32)
) -> Complex64: ...

@bind("CGBMV")
@external
def cgbmv(
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    ALPHA: Ref(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex64[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Complex64),
    Y: Complex64[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("CGEMM")
@external
def cgemm(
    TRANSA: Ref(Const(String[1])),
    TRANSB: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    BETA: Ref(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("CGEMMTR")
@external
def cgemmtr(
    UPLO: Ref(Const(String[1])),
    TRANSA: Ref(Const(String[1])),
    TRANSB: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    BETA: Ref(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("CGEMV")
@external
def cgemv(
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex64[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Complex64),
    Y: Complex64[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("CGERC")
@external
def cgerc(
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Complex64),
    X: Complex64[Flat],
    INCX: Ref(Int32),
    Y: Complex64[Flat],
    INCY: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("CGERU")
@external
def cgeru(
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Complex64),
    X: Complex64[Flat],
    INCX: Ref(Int32),
    Y: Complex64[Flat],
    INCY: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("CHBMV")
@external
def chbmv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex64[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Complex64),
    Y: Complex64[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("CHEMM")
@external
def chemm(
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    BETA: Ref(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("CHEMV")
@external
def chemv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex64[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Complex64),
    Y: Complex64[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("CHER")
@external
def cher(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Float32),
    X: Complex64[Flat],
    INCX: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("CHER2")
@external
def cher2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Complex64),
    X: Complex64[Flat],
    INCX: Ref(Int32),
    Y: Complex64[Flat],
    INCY: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("CHER2K")
@external
def cher2k(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    BETA: Ref(Float32),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("CHERK")
@external
def cherk(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Float32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    BETA: Ref(Float32),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("CHPMV")
@external
def chpmv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Complex64),
    AP: Complex64[Flat],
    X: Complex64[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Complex64),
    Y: Complex64[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("CHPR")
@external
def chpr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Float32),
    X: Complex64[Flat],
    INCX: Ref(Int32),
    AP: Complex64[Flat]
) -> None: ...

@bind("CHPR2")
@external
def chpr2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Complex64),
    X: Complex64[Flat],
    INCX: Ref(Int32),
    Y: Complex64[Flat],
    INCY: Ref(Int32),
    AP: Complex64[Flat]
) -> None: ...

@bind("CROTG")
@external
def crotg(
    a: Ref(Complex64),
    b: Ref(Complex64),
    c: Ref(Float32),
    s: Ref(Complex64)
) -> None: ...

@bind("CSCAL")
@external
def cscal(
    N: Ref(Int32),
    CA: Ref(Complex64),
    CX: Complex64[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("CSROT")
@external
def csrot(
    N: Ref(Int32),
    CX: Complex64[Flat],
    INCX: Ref(Int32),
    CY: Complex64[Flat],
    INCY: Ref(Int32),
    C: Ref(Float32),
    S: Ref(Float32)
) -> None: ...

@bind("CSSCAL")
@external
def csscal(
    N: Ref(Int32),
    SA: Ref(Float32),
    CX: Complex64[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("CSWAP")
@external
def cswap(
    N: Ref(Int32),
    CX: Complex64[Flat],
    INCX: Ref(Int32),
    CY: Complex64[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("CSYMM")
@external
def csymm(
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    BETA: Ref(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("CSYR2K")
@external
def csyr2k(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32),
    BETA: Ref(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("CSYRK")
@external
def csyrk(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    BETA: Ref(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("CTBMV")
@external
def ctbmv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex64[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("CTBSV")
@external
def ctbsv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex64[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("CTPMV")
@external
def ctpmv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    X: Complex64[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("CTPSV")
@external
def ctpsv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex64[Flat],
    X: Complex64[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("CTRMM")
@external
def ctrmm(
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANSA: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("CTRMV")
@external
def ctrmv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex64[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("CTRSM")
@external
def ctrsm(
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANSA: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("CTRSV")
@external
def ctrsv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex64[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("DASUM")
@external
def dasum(
    N: Ref(Int32),
    DX: Float64[Flat],
    INCX: Ref(Int32)
) -> Float64: ...

@bind("DAXPY")
@external
def daxpy(
    N: Ref(Int32),
    DA: Ref(Float64),
    DX: Float64[Flat],
    INCX: Ref(Int32),
    DY: Float64[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("DCABS1")
@external
def dcabs1(
    Z: Ref(Complex128)
) -> Float64: ...

@bind("DCOPY")
@external
def dcopy(
    N: Ref(Int32),
    DX: Float64[Flat],
    INCX: Ref(Int32),
    DY: Float64[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("DDOT")
@external
def ddot(
    N: Ref(Int32),
    DX: Float64[Flat],
    INCX: Ref(Int32),
    DY: Float64[Flat],
    INCY: Ref(Int32)
) -> Float64: ...

@bind("DGBMV")
@external
def dgbmv(
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    ALPHA: Ref(Float64),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    X: Float64[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Float64),
    Y: Float64[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("DGEMM")
@external
def dgemm(
    TRANSA: Ref(Const(String[1])),
    TRANSB: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Float64),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    BETA: Ref(Float64),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("DGEMMTR")
@external
def dgemmtr(
    UPLO: Ref(Const(String[1])),
    TRANSA: Ref(Const(String[1])),
    TRANSB: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Float64),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    BETA: Ref(Float64),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("DGEMV")
@external
def dgemv(
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Float64),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    X: Float64[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Float64),
    Y: Float64[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("DGER")
@external
def dger(
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Float64),
    X: Float64[Flat],
    INCX: Ref(Int32),
    Y: Float64[Flat],
    INCY: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("DNRM2")
@external
def dnrm2(
    n: Ref(Int32),
    x: Float64[Flat],
    incx: Ref(Int32)
) -> Float64: ...

@bind("DROT")
@external
def drot(
    N: Ref(Int32),
    DX: Float64[Flat],
    INCX: Ref(Int32),
    DY: Float64[Flat],
    INCY: Ref(Int32),
    C: Ref(Float64),
    S: Ref(Float64)
) -> None: ...

@bind("DROTG")
@external
def drotg(
    a: Ref(Float64),
    b: Ref(Float64),
    c: Ref(Float64),
    s: Ref(Float64)
) -> None: ...

@bind("DROTM")
@external
def drotm(
    N: Ref(Int32),
    DX: Float64[Flat],
    INCX: Ref(Int32),
    DY: Float64[Flat],
    INCY: Ref(Int32),
    DPARAM: Float64[5]
) -> None: ...

@bind("DROTMG")
@external
def drotmg(
    DD1: Ref(Float64),
    DD2: Ref(Float64),
    DX1: Ref(Float64),
    DY1: Ref(Float64),
    DPARAM: Float64[5]
) -> None: ...

@bind("DSBMV")
@external
def dsbmv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Float64),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    X: Float64[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Float64),
    Y: Float64[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("DSCAL")
@external
def dscal(
    N: Ref(Int32),
    DA: Ref(Float64),
    DX: Float64[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("DSDOT")
@external
def dsdot(
    N: Ref(Int32),
    SX: Float32[Flat],
    INCX: Ref(Int32),
    SY: Float32[Flat],
    INCY: Ref(Int32)
) -> Float64: ...

@bind("DSPMV")
@external
def dspmv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Float64),
    AP: Float64[Flat],
    X: Float64[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Float64),
    Y: Float64[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("DSPR")
@external
def dspr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Float64),
    X: Float64[Flat],
    INCX: Ref(Int32),
    AP: Float64[Flat]
) -> None: ...

@bind("DSPR2")
@external
def dspr2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Float64),
    X: Float64[Flat],
    INCX: Ref(Int32),
    Y: Float64[Flat],
    INCY: Ref(Int32),
    AP: Float64[Flat]
) -> None: ...

@bind("DSWAP")
@external
def dswap(
    N: Ref(Int32),
    DX: Float64[Flat],
    INCX: Ref(Int32),
    DY: Float64[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("DSYMM")
@external
def dsymm(
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Float64),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    BETA: Ref(Float64),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("DSYMV")
@external
def dsymv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Float64),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    X: Float64[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Float64),
    Y: Float64[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("DSYR")
@external
def dsyr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Float64),
    X: Float64[Flat],
    INCX: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("DSYR2")
@external
def dsyr2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Float64),
    X: Float64[Flat],
    INCX: Ref(Int32),
    Y: Float64[Flat],
    INCY: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("DSYR2K")
@external
def dsyr2k(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Float64),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32),
    BETA: Ref(Float64),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("DSYRK")
@external
def dsyrk(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Float64),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    BETA: Ref(Float64),
    C: Float64[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("DTBMV")
@external
def dtbmv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    X: Float64[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("DTBSV")
@external
def dtbsv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    X: Float64[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("DTPMV")
@external
def dtpmv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    X: Float64[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("DTPSV")
@external
def dtpsv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float64[Flat],
    X: Float64[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("DTRMM")
@external
def dtrmm(
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANSA: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Float64),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("DTRMV")
@external
def dtrmv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    X: Float64[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("DTRSM")
@external
def dtrsm(
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANSA: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Float64),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    B: Float64[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("DTRSV")
@external
def dtrsv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float64[LDA, Flat],
    LDA: Ref(Int32),
    X: Float64[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("DZASUM")
@external
def dzasum(
    N: Ref(Int32),
    ZX: Complex128[Flat],
    INCX: Ref(Int32)
) -> Float64: ...

@bind("DZNRM2")
@external
def dznrm2(
    n: Ref(Int32),
    x: Complex128[Flat],
    incx: Ref(Int32)
) -> Float64: ...

@bind("ICAMAX")
@external
def icamax(
    N: Ref(Int32),
    CX: Complex64[Flat],
    INCX: Ref(Int32)
) -> Int32: ...

@bind("IDAMAX")
@external
def idamax(
    N: Ref(Int32),
    DX: Float64[Flat],
    INCX: Ref(Int32)
) -> Int32: ...

@bind("ISAMAX")
@external
def isamax(
    N: Ref(Int32),
    SX: Float32[Flat],
    INCX: Ref(Int32)
) -> Int32: ...

@bind("IZAMAX")
@external
def izamax(
    N: Ref(Int32),
    ZX: Complex128[Flat],
    INCX: Ref(Int32)
) -> Int32: ...

@bind("LSAME")
@external
def lsame(
    CA: Ref(Const(String[1])),
    CB: Ref(Const(String[1]))
) -> Bool: ...

@bind("SASUM")
@external
def sasum(
    N: Ref(Int32),
    SX: Float32[Flat],
    INCX: Ref(Int32)
) -> Float32: ...

@bind("SAXPY")
@external
def saxpy(
    N: Ref(Int32),
    SA: Ref(Float32),
    SX: Float32[Flat],
    INCX: Ref(Int32),
    SY: Float32[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("SCABS1")
@external
def scabs1(
    Z: Ref(Complex64)
) -> Float32: ...

@bind("SCASUM")
@external
def scasum(
    N: Ref(Int32),
    CX: Complex64[Flat],
    INCX: Ref(Int32)
) -> Float32: ...

@bind("SCNRM2")
@external
def scnrm2(
    n: Ref(Int32),
    x: Complex64[Flat],
    incx: Ref(Int32)
) -> Float32: ...

@bind("SCOPY")
@external
def scopy(
    N: Ref(Int32),
    SX: Float32[Flat],
    INCX: Ref(Int32),
    SY: Float32[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("SDOT")
@external
def sdot(
    N: Ref(Int32),
    SX: Float32[Flat],
    INCX: Ref(Int32),
    SY: Float32[Flat],
    INCY: Ref(Int32)
) -> Float32: ...

@bind("SDSDOT")
@external
def sdsdot(
    N: Ref(Int32),
    SB: Ref(Float32),
    SX: Float32[Flat],
    INCX: Ref(Int32),
    SY: Float32[Flat],
    INCY: Ref(Int32)
) -> Float32: ...

@bind("SGBMV")
@external
def sgbmv(
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    ALPHA: Ref(Float32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    X: Float32[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Float32),
    Y: Float32[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("SGEMM")
@external
def sgemm(
    TRANSA: Ref(Const(String[1])),
    TRANSB: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Float32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    BETA: Ref(Float32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("SGEMMTR")
@external
def sgemmtr(
    UPLO: Ref(Const(String[1])),
    TRANSA: Ref(Const(String[1])),
    TRANSB: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Float32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    BETA: Ref(Float32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("SGEMV")
@external
def sgemv(
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Float32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    X: Float32[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Float32),
    Y: Float32[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("SGER")
@external
def sger(
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Float32),
    X: Float32[Flat],
    INCX: Ref(Int32),
    Y: Float32[Flat],
    INCY: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("SNRM2")
@external
def snrm2(
    n: Ref(Int32),
    x: Float32[Flat],
    incx: Ref(Int32)
) -> Float32: ...

@bind("SROT")
@external
def srot(
    N: Ref(Int32),
    SX: Float32[Flat],
    INCX: Ref(Int32),
    SY: Float32[Flat],
    INCY: Ref(Int32),
    C: Ref(Float32),
    S: Ref(Float32)
) -> None: ...

@bind("SROTG")
@external
def srotg(
    a: Ref(Float32),
    b: Ref(Float32),
    c: Ref(Float32),
    s: Ref(Float32)
) -> None: ...

@bind("SROTM")
@external
def srotm(
    N: Ref(Int32),
    SX: Float32[Flat],
    INCX: Ref(Int32),
    SY: Float32[Flat],
    INCY: Ref(Int32),
    SPARAM: Float32[5]
) -> None: ...

@bind("SROTMG")
@external
def srotmg(
    SD1: Ref(Float32),
    SD2: Ref(Float32),
    SX1: Ref(Float32),
    SY1: Ref(Float32),
    SPARAM: Float32[5]
) -> None: ...

@bind("SSBMV")
@external
def ssbmv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Float32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    X: Float32[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Float32),
    Y: Float32[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("SSCAL")
@external
def sscal(
    N: Ref(Int32),
    SA: Ref(Float32),
    SX: Float32[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("SSPMV")
@external
def sspmv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Float32),
    AP: Float32[Flat],
    X: Float32[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Float32),
    Y: Float32[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("SSPR")
@external
def sspr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Float32),
    X: Float32[Flat],
    INCX: Ref(Int32),
    AP: Float32[Flat]
) -> None: ...

@bind("SSPR2")
@external
def sspr2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Float32),
    X: Float32[Flat],
    INCX: Ref(Int32),
    Y: Float32[Flat],
    INCY: Ref(Int32),
    AP: Float32[Flat]
) -> None: ...

@bind("SSWAP")
@external
def sswap(
    N: Ref(Int32),
    SX: Float32[Flat],
    INCX: Ref(Int32),
    SY: Float32[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("SSYMM")
@external
def ssymm(
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Float32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    BETA: Ref(Float32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("SSYMV")
@external
def ssymv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Float32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    X: Float32[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Float32),
    Y: Float32[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("SSYR")
@external
def ssyr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Float32),
    X: Float32[Flat],
    INCX: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("SSYR2")
@external
def ssyr2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Float32),
    X: Float32[Flat],
    INCX: Ref(Int32),
    Y: Float32[Flat],
    INCY: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("SSYR2K")
@external
def ssyr2k(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Float32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32),
    BETA: Ref(Float32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("SSYRK")
@external
def ssyrk(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Float32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    BETA: Ref(Float32),
    C: Float32[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("STBMV")
@external
def stbmv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    X: Float32[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("STBSV")
@external
def stbsv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    X: Float32[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("STPMV")
@external
def stpmv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    X: Float32[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("STPSV")
@external
def stpsv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Float32[Flat],
    X: Float32[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("STRMM")
@external
def strmm(
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANSA: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Float32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("STRMV")
@external
def strmv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    X: Float32[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("STRSM")
@external
def strsm(
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANSA: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Float32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    B: Float32[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("STRSV")
@external
def strsv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Float32[LDA, Flat],
    LDA: Ref(Int32),
    X: Float32[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("XERBLA")
@external
def xerbla(
    SRNAME: Ref(Const(String)),
    INFO: Ref(Int32)
) -> None: ...

@bind("XERBLA_ARRAY")
@external
def xerbla_array(
    SRNAME_ARRAY: String[1][SRNAME_LEN],
    SRNAME_LEN: Ref(Int32),
    INFO: Ref(Int32)
) -> None: ...

@bind("ZAXPY")
@external
def zaxpy(
    N: Ref(Int32),
    ZA: Ref(Complex128),
    ZX: Complex128[Flat],
    INCX: Ref(Int32),
    ZY: Complex128[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("ZCOPY")
@external
def zcopy(
    N: Ref(Int32),
    ZX: Complex128[Flat],
    INCX: Ref(Int32),
    ZY: Complex128[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("ZDOTC")
@external
def zdotc(
    N: Ref(Int32),
    ZX: Complex128[Flat],
    INCX: Ref(Int32),
    ZY: Complex128[Flat],
    INCY: Ref(Int32)
) -> Complex128: ...

@bind("ZDOTU")
@external
def zdotu(
    N: Ref(Int32),
    ZX: Complex128[Flat],
    INCX: Ref(Int32),
    ZY: Complex128[Flat],
    INCY: Ref(Int32)
) -> Complex128: ...

@bind("ZDROT")
@external
def zdrot(
    N: Ref(Int32),
    ZX: Complex128[Flat],
    INCX: Ref(Int32),
    ZY: Complex128[Flat],
    INCY: Ref(Int32),
    C: Ref(Float64),
    S: Ref(Float64)
) -> None: ...

@bind("ZDSCAL")
@external
def zdscal(
    N: Ref(Int32),
    DA: Ref(Float64),
    ZX: Complex128[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("ZGBMV")
@external
def zgbmv(
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    KL: Ref(Int32),
    KU: Ref(Int32),
    ALPHA: Ref(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex128[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Complex128),
    Y: Complex128[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("ZGEMM")
@external
def zgemm(
    TRANSA: Ref(Const(String[1])),
    TRANSB: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    BETA: Ref(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("ZGEMMTR")
@external
def zgemmtr(
    UPLO: Ref(Const(String[1])),
    TRANSA: Ref(Const(String[1])),
    TRANSB: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    BETA: Ref(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("ZGEMV")
@external
def zgemv(
    TRANS: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex128[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Complex128),
    Y: Complex128[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("ZGERC")
@external
def zgerc(
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Complex128),
    X: Complex128[Flat],
    INCX: Ref(Int32),
    Y: Complex128[Flat],
    INCY: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("ZGERU")
@external
def zgeru(
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Complex128),
    X: Complex128[Flat],
    INCX: Ref(Int32),
    Y: Complex128[Flat],
    INCY: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("ZHBMV")
@external
def zhbmv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex128[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Complex128),
    Y: Complex128[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("ZHEMM")
@external
def zhemm(
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    BETA: Ref(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("ZHEMV")
@external
def zhemv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex128[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Complex128),
    Y: Complex128[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("ZHER")
@external
def zher(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Float64),
    X: Complex128[Flat],
    INCX: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("ZHER2")
@external
def zher2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Complex128),
    X: Complex128[Flat],
    INCX: Ref(Int32),
    Y: Complex128[Flat],
    INCY: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32)
) -> None: ...

@bind("ZHER2K")
@external
def zher2k(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    BETA: Ref(Float64),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("ZHERK")
@external
def zherk(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Float64),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    BETA: Ref(Float64),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("ZHPMV")
@external
def zhpmv(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Complex128),
    AP: Complex128[Flat],
    X: Complex128[Flat],
    INCX: Ref(Int32),
    BETA: Ref(Complex128),
    Y: Complex128[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("ZHPR")
@external
def zhpr(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Float64),
    X: Complex128[Flat],
    INCX: Ref(Int32),
    AP: Complex128[Flat]
) -> None: ...

@bind("ZHPR2")
@external
def zhpr2(
    UPLO: Ref(Const(String[1])),
    N: Ref(Int32),
    ALPHA: Ref(Complex128),
    X: Complex128[Flat],
    INCX: Ref(Int32),
    Y: Complex128[Flat],
    INCY: Ref(Int32),
    AP: Complex128[Flat]
) -> None: ...

@bind("ZROTG")
@external
def zrotg(
    a: Ref(Complex128),
    b: Ref(Complex128),
    c: Ref(Float64),
    s: Ref(Complex128)
) -> None: ...

@bind("ZSCAL")
@external
def zscal(
    N: Ref(Int32),
    ZA: Ref(Complex128),
    ZX: Complex128[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("ZSWAP")
@external
def zswap(
    N: Ref(Int32),
    ZX: Complex128[Flat],
    INCX: Ref(Int32),
    ZY: Complex128[Flat],
    INCY: Ref(Int32)
) -> None: ...

@bind("ZSYMM")
@external
def zsymm(
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    BETA: Ref(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("ZSYR2K")
@external
def zsyr2k(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32),
    BETA: Ref(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("ZSYRK")
@external
def zsyrk(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    ALPHA: Ref(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    BETA: Ref(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ref(Int32)
) -> None: ...

@bind("ZTBMV")
@external
def ztbmv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex128[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("ZTBSV")
@external
def ztbsv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    K: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex128[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("ZTPMV")
@external
def ztpmv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    X: Complex128[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("ZTPSV")
@external
def ztpsv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    AP: Complex128[Flat],
    X: Complex128[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("ZTRMM")
@external
def ztrmm(
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANSA: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("ZTRMV")
@external
def ztrmv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex128[Flat],
    INCX: Ref(Int32)
) -> None: ...

@bind("ZTRSM")
@external
def ztrsm(
    SIDE: Ref(Const(String[1])),
    UPLO: Ref(Const(String[1])),
    TRANSA: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    M: Ref(Int32),
    N: Ref(Int32),
    ALPHA: Ref(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ref(Int32)
) -> None: ...

@bind("ZTRSV")
@external
def ztrsv(
    UPLO: Ref(Const(String[1])),
    TRANS: Ref(Const(String[1])),
    DIAG: Ref(Const(String[1])),
    N: Ref(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ref(Int32),
    X: Complex128[Flat],
    INCX: Ref(Int32)
) -> None: ...
