from x2py.contracts import Addr, Arg, Bool, Complex128, Complex64, Flat, Float32, Float64, Int32, String, bind, external, native_call

@bind("CAXPY")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5))])
def caxpy(
    N: Int32,
    CA: Complex64,
    CX: Complex64[Flat],
    INCX: Int32,
    CY: Complex64[Flat],
    INCY: Int32
) -> None: ...

@bind("CCOPY")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def ccopy(
    N: Int32,
    CX: Complex64[Flat],
    INCX: Int32,
    CY: Complex64[Flat],
    INCY: Int32
) -> None: ...

@bind("CDOTC")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def cdotc(
    N: Int32,
    CX: Complex64[Flat],
    INCX: Int32,
    CY: Complex64[Flat],
    INCY: Int32
) -> Complex64: ...

@bind("CDOTU")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def cdotu(
    N: Int32,
    CX: Complex64[Flat],
    INCX: Int32,
    CY: Complex64[Flat],
    INCY: Int32
) -> Complex64: ...

@bind("CGBMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def cgbmv(
    TRANS: String[1],
    M: Int32,
    N: Int32,
    KL: Int32,
    KU: Int32,
    ALPHA: Complex64,
    A: Complex64[LDA, Flat],
    LDA: Int32,
    X: Complex64[Flat],
    INCX: Int32,
    BETA: Complex64,
    Y: Complex64[Flat],
    INCY: Int32
) -> None: ...

@bind("CGEMM")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def cgemm(
    TRANSA: String[1],
    TRANSB: String[1],
    M: Int32,
    N: Int32,
    K: Int32,
    ALPHA: Complex64,
    A: Complex64[LDA, Flat],
    LDA: Int32,
    B: Complex64[LDB, Flat],
    LDB: Int32,
    BETA: Complex64,
    C: Complex64[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("CGEMMTR")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def cgemmtr(
    UPLO: String[1],
    TRANSA: String[1],
    TRANSB: String[1],
    N: Int32,
    K: Int32,
    ALPHA: Complex64,
    A: Complex64[LDA, Flat],
    LDA: Int32,
    B: Complex64[LDB, Flat],
    LDB: Int32,
    BETA: Complex64,
    C: Complex64[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("CGEMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def cgemv(
    TRANS: String[1],
    M: Int32,
    N: Int32,
    ALPHA: Complex64,
    A: Complex64[LDA, Flat],
    LDA: Int32,
    X: Complex64[Flat],
    INCX: Int32,
    BETA: Complex64,
    Y: Complex64[Flat],
    INCY: Int32
) -> None: ...

@bind("CGERC")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def cgerc(
    M: Int32,
    N: Int32,
    ALPHA: Complex64,
    X: Complex64[Flat],
    INCX: Int32,
    Y: Complex64[Flat],
    INCY: Int32,
    A: Complex64[LDA, Flat],
    LDA: Int32
) -> None: ...

@bind("CGERU")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def cgeru(
    M: Int32,
    N: Int32,
    ALPHA: Complex64,
    X: Complex64[Flat],
    INCX: Int32,
    Y: Complex64[Flat],
    INCY: Int32,
    A: Complex64[LDA, Flat],
    LDA: Int32
) -> None: ...

@bind("CHBMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def chbmv(
    UPLO: String[1],
    N: Int32,
    K: Int32,
    ALPHA: Complex64,
    A: Complex64[LDA, Flat],
    LDA: Int32,
    X: Complex64[Flat],
    INCX: Int32,
    BETA: Complex64,
    Y: Complex64[Flat],
    INCY: Int32
) -> None: ...

@bind("CHEMM")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def chemm(
    SIDE: String[1],
    UPLO: String[1],
    M: Int32,
    N: Int32,
    ALPHA: Complex64,
    A: Complex64[LDA, Flat],
    LDA: Int32,
    B: Complex64[LDB, Flat],
    LDB: Int32,
    BETA: Complex64,
    C: Complex64[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("CHEMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Addr(Arg(9))])
def chemv(
    UPLO: String[1],
    N: Int32,
    ALPHA: Complex64,
    A: Complex64[LDA, Flat],
    LDA: Int32,
    X: Complex64[Flat],
    INCX: Int32,
    BETA: Complex64,
    Y: Complex64[Flat],
    INCY: Int32
) -> None: ...

@bind("CHER")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6))])
def cher(
    UPLO: String[1],
    N: Int32,
    ALPHA: Float32,
    X: Complex64[Flat],
    INCX: Int32,
    A: Complex64[LDA, Flat],
    LDA: Int32
) -> None: ...

@bind("CHER2")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def cher2(
    UPLO: String[1],
    N: Int32,
    ALPHA: Complex64,
    X: Complex64[Flat],
    INCX: Int32,
    Y: Complex64[Flat],
    INCY: Int32,
    A: Complex64[LDA, Flat],
    LDA: Int32
) -> None: ...

@bind("CHER2K")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def cher2k(
    UPLO: String[1],
    TRANS: String[1],
    N: Int32,
    K: Int32,
    ALPHA: Complex64,
    A: Complex64[LDA, Flat],
    LDA: Int32,
    B: Complex64[LDB, Flat],
    LDB: Int32,
    BETA: Float32,
    C: Complex64[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("CHERK")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Addr(Arg(9))])
def cherk(
    UPLO: String[1],
    TRANS: String[1],
    N: Int32,
    K: Int32,
    ALPHA: Float32,
    A: Complex64[LDA, Flat],
    LDA: Int32,
    BETA: Float32,
    C: Complex64[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("CHPMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Arg(4), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def chpmv(
    UPLO: String[1],
    N: Int32,
    ALPHA: Complex64,
    AP: Complex64[Flat],
    X: Complex64[Flat],
    INCX: Int32,
    BETA: Complex64,
    Y: Complex64[Flat],
    INCY: Int32
) -> None: ...

@bind("CHPR")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5)])
def chpr(
    UPLO: String[1],
    N: Int32,
    ALPHA: Float32,
    X: Complex64[Flat],
    INCX: Int32,
    AP: Complex64[Flat]
) -> None: ...

@bind("CHPR2")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7)])
def chpr2(
    UPLO: String[1],
    N: Int32,
    ALPHA: Complex64,
    X: Complex64[Flat],
    INCX: Int32,
    Y: Complex64[Flat],
    INCY: Int32,
    AP: Complex64[Flat]
) -> None: ...

@bind("CROTG")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3))])
def crotg(
    a: Complex64,
    b: Complex64,
    c: Float32,
    s: Complex64
) -> None: ...

@bind("CSCAL")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Addr(Arg(3))])
def cscal(
    N: Int32,
    CA: Complex64,
    CX: Complex64[Flat],
    INCX: Int32
) -> None: ...

@bind("CSROT")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6))])
def csrot(
    N: Int32,
    CX: Complex64[Flat],
    INCX: Int32,
    CY: Complex64[Flat],
    INCY: Int32,
    C: Float32,
    S: Float32
) -> None: ...

@bind("CSSCAL")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Addr(Arg(3))])
def csscal(
    N: Int32,
    SA: Float32,
    CX: Complex64[Flat],
    INCX: Int32
) -> None: ...

@bind("CSWAP")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def cswap(
    N: Int32,
    CX: Complex64[Flat],
    INCX: Int32,
    CY: Complex64[Flat],
    INCY: Int32
) -> None: ...

@bind("CSYMM")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def csymm(
    SIDE: String[1],
    UPLO: String[1],
    M: Int32,
    N: Int32,
    ALPHA: Complex64,
    A: Complex64[LDA, Flat],
    LDA: Int32,
    B: Complex64[LDB, Flat],
    LDB: Int32,
    BETA: Complex64,
    C: Complex64[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("CSYR2K")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def csyr2k(
    UPLO: String[1],
    TRANS: String[1],
    N: Int32,
    K: Int32,
    ALPHA: Complex64,
    A: Complex64[LDA, Flat],
    LDA: Int32,
    B: Complex64[LDB, Flat],
    LDB: Int32,
    BETA: Complex64,
    C: Complex64[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("CSYRK")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Addr(Arg(9))])
def csyrk(
    UPLO: String[1],
    TRANS: String[1],
    N: Int32,
    K: Int32,
    ALPHA: Complex64,
    A: Complex64[LDA, Flat],
    LDA: Int32,
    BETA: Complex64,
    C: Complex64[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("CTBMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def ctbmv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    K: Int32,
    A: Complex64[LDA, Flat],
    LDA: Int32,
    X: Complex64[Flat],
    INCX: Int32
) -> None: ...

@bind("CTBSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def ctbsv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    K: Int32,
    A: Complex64[LDA, Flat],
    LDA: Int32,
    X: Complex64[Flat],
    INCX: Int32
) -> None: ...

@bind("CTPMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Arg(5), Addr(Arg(6))])
def ctpmv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    AP: Complex64[Flat],
    X: Complex64[Flat],
    INCX: Int32
) -> None: ...

@bind("CTPSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Arg(5), Addr(Arg(6))])
def ctpsv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    AP: Complex64[Flat],
    X: Complex64[Flat],
    INCX: Int32
) -> None: ...

@bind("CTRMM")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def ctrmm(
    SIDE: String[1],
    UPLO: String[1],
    TRANSA: String[1],
    DIAG: String[1],
    M: Int32,
    N: Int32,
    ALPHA: Complex64,
    A: Complex64[LDA, Flat],
    LDA: Int32,
    B: Complex64[LDB, Flat],
    LDB: Int32
) -> None: ...

@bind("CTRMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7))])
def ctrmv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    A: Complex64[LDA, Flat],
    LDA: Int32,
    X: Complex64[Flat],
    INCX: Int32
) -> None: ...

@bind("CTRSM")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def ctrsm(
    SIDE: String[1],
    UPLO: String[1],
    TRANSA: String[1],
    DIAG: String[1],
    M: Int32,
    N: Int32,
    ALPHA: Complex64,
    A: Complex64[LDA, Flat],
    LDA: Int32,
    B: Complex64[LDB, Flat],
    LDB: Int32
) -> None: ...

@bind("CTRSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7))])
def ctrsv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    A: Complex64[LDA, Flat],
    LDA: Int32,
    X: Complex64[Flat],
    INCX: Int32
) -> None: ...

@bind("DASUM")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def dasum(
    N: Int32,
    DX: Float64[Flat],
    INCX: Int32
) -> Float64: ...

@bind("DAXPY")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5))])
def daxpy(
    N: Int32,
    DA: Float64,
    DX: Float64[Flat],
    INCX: Int32,
    DY: Float64[Flat],
    INCY: Int32
) -> None: ...

@bind("DCABS1")
@external
@native_call([Addr(Arg(0))])
def dcabs1(
    Z: Complex128
) -> Float64: ...

@bind("DCOPY")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def dcopy(
    N: Int32,
    DX: Float64[Flat],
    INCX: Int32,
    DY: Float64[Flat],
    INCY: Int32
) -> None: ...

@bind("DDOT")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def ddot(
    N: Int32,
    DX: Float64[Flat],
    INCX: Int32,
    DY: Float64[Flat],
    INCY: Int32
) -> Float64: ...

@bind("DGBMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def dgbmv(
    TRANS: String[1],
    M: Int32,
    N: Int32,
    KL: Int32,
    KU: Int32,
    ALPHA: Float64,
    A: Float64[LDA, Flat],
    LDA: Int32,
    X: Float64[Flat],
    INCX: Int32,
    BETA: Float64,
    Y: Float64[Flat],
    INCY: Int32
) -> None: ...

@bind("DGEMM")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def dgemm(
    TRANSA: String[1],
    TRANSB: String[1],
    M: Int32,
    N: Int32,
    K: Int32,
    ALPHA: Float64,
    A: Float64[LDA, Flat],
    LDA: Int32,
    B: Float64[LDB, Flat],
    LDB: Int32,
    BETA: Float64,
    C: Float64[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("DGEMMTR")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def dgemmtr(
    UPLO: String[1],
    TRANSA: String[1],
    TRANSB: String[1],
    N: Int32,
    K: Int32,
    ALPHA: Float64,
    A: Float64[LDA, Flat],
    LDA: Int32,
    B: Float64[LDB, Flat],
    LDB: Int32,
    BETA: Float64,
    C: Float64[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("DGEMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def dgemv(
    TRANS: String[1],
    M: Int32,
    N: Int32,
    ALPHA: Float64,
    A: Float64[LDA, Flat],
    LDA: Int32,
    X: Float64[Flat],
    INCX: Int32,
    BETA: Float64,
    Y: Float64[Flat],
    INCY: Int32
) -> None: ...

@bind("DGER")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def dger(
    M: Int32,
    N: Int32,
    ALPHA: Float64,
    X: Float64[Flat],
    INCX: Int32,
    Y: Float64[Flat],
    INCY: Int32,
    A: Float64[LDA, Flat],
    LDA: Int32
) -> None: ...

@bind("DNRM2")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def dnrm2(
    n: Int32,
    x: Float64[Flat],
    incx: Int32
) -> Float64: ...

@bind("DROT")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6))])
def drot(
    N: Int32,
    DX: Float64[Flat],
    INCX: Int32,
    DY: Float64[Flat],
    INCY: Int32,
    C: Float64,
    S: Float64
) -> None: ...

@bind("DROTG")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3))])
def drotg(
    a: Float64,
    b: Float64,
    c: Float64,
    s: Float64
) -> None: ...

@bind("DROTM")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5)])
def drotm(
    N: Int32,
    DX: Float64[Flat],
    INCX: Int32,
    DY: Float64[Flat],
    INCY: Int32,
    DPARAM: Float64[5]
) -> None: ...

@bind("DROTMG")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Arg(4)])
def drotmg(
    DD1: Float64,
    DD2: Float64,
    DX1: Float64,
    DY1: Float64,
    DPARAM: Float64[5]
) -> None: ...

@bind("DSBMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def dsbmv(
    UPLO: String[1],
    N: Int32,
    K: Int32,
    ALPHA: Float64,
    A: Float64[LDA, Flat],
    LDA: Int32,
    X: Float64[Flat],
    INCX: Int32,
    BETA: Float64,
    Y: Float64[Flat],
    INCY: Int32
) -> None: ...

@bind("DSCAL")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Addr(Arg(3))])
def dscal(
    N: Int32,
    DA: Float64,
    DX: Float64[Flat],
    INCX: Int32
) -> None: ...

@bind("DSDOT")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def dsdot(
    N: Int32,
    SX: Float32[Flat],
    INCX: Int32,
    SY: Float32[Flat],
    INCY: Int32
) -> Float64: ...

@bind("DSPMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Arg(4), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def dspmv(
    UPLO: String[1],
    N: Int32,
    ALPHA: Float64,
    AP: Float64[Flat],
    X: Float64[Flat],
    INCX: Int32,
    BETA: Float64,
    Y: Float64[Flat],
    INCY: Int32
) -> None: ...

@bind("DSPR")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5)])
def dspr(
    UPLO: String[1],
    N: Int32,
    ALPHA: Float64,
    X: Float64[Flat],
    INCX: Int32,
    AP: Float64[Flat]
) -> None: ...

@bind("DSPR2")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7)])
def dspr2(
    UPLO: String[1],
    N: Int32,
    ALPHA: Float64,
    X: Float64[Flat],
    INCX: Int32,
    Y: Float64[Flat],
    INCY: Int32,
    AP: Float64[Flat]
) -> None: ...

@bind("DSWAP")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def dswap(
    N: Int32,
    DX: Float64[Flat],
    INCX: Int32,
    DY: Float64[Flat],
    INCY: Int32
) -> None: ...

@bind("DSYMM")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def dsymm(
    SIDE: String[1],
    UPLO: String[1],
    M: Int32,
    N: Int32,
    ALPHA: Float64,
    A: Float64[LDA, Flat],
    LDA: Int32,
    B: Float64[LDB, Flat],
    LDB: Int32,
    BETA: Float64,
    C: Float64[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("DSYMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Addr(Arg(9))])
def dsymv(
    UPLO: String[1],
    N: Int32,
    ALPHA: Float64,
    A: Float64[LDA, Flat],
    LDA: Int32,
    X: Float64[Flat],
    INCX: Int32,
    BETA: Float64,
    Y: Float64[Flat],
    INCY: Int32
) -> None: ...

@bind("DSYR")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6))])
def dsyr(
    UPLO: String[1],
    N: Int32,
    ALPHA: Float64,
    X: Float64[Flat],
    INCX: Int32,
    A: Float64[LDA, Flat],
    LDA: Int32
) -> None: ...

@bind("DSYR2")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def dsyr2(
    UPLO: String[1],
    N: Int32,
    ALPHA: Float64,
    X: Float64[Flat],
    INCX: Int32,
    Y: Float64[Flat],
    INCY: Int32,
    A: Float64[LDA, Flat],
    LDA: Int32
) -> None: ...

@bind("DSYR2K")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def dsyr2k(
    UPLO: String[1],
    TRANS: String[1],
    N: Int32,
    K: Int32,
    ALPHA: Float64,
    A: Float64[LDA, Flat],
    LDA: Int32,
    B: Float64[LDB, Flat],
    LDB: Int32,
    BETA: Float64,
    C: Float64[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("DSYRK")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Addr(Arg(9))])
def dsyrk(
    UPLO: String[1],
    TRANS: String[1],
    N: Int32,
    K: Int32,
    ALPHA: Float64,
    A: Float64[LDA, Flat],
    LDA: Int32,
    BETA: Float64,
    C: Float64[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("DTBMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def dtbmv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    K: Int32,
    A: Float64[LDA, Flat],
    LDA: Int32,
    X: Float64[Flat],
    INCX: Int32
) -> None: ...

@bind("DTBSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def dtbsv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    K: Int32,
    A: Float64[LDA, Flat],
    LDA: Int32,
    X: Float64[Flat],
    INCX: Int32
) -> None: ...

@bind("DTPMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Arg(5), Addr(Arg(6))])
def dtpmv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    AP: Float64[Flat],
    X: Float64[Flat],
    INCX: Int32
) -> None: ...

@bind("DTPSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Arg(5), Addr(Arg(6))])
def dtpsv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    AP: Float64[Flat],
    X: Float64[Flat],
    INCX: Int32
) -> None: ...

@bind("DTRMM")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def dtrmm(
    SIDE: String[1],
    UPLO: String[1],
    TRANSA: String[1],
    DIAG: String[1],
    M: Int32,
    N: Int32,
    ALPHA: Float64,
    A: Float64[LDA, Flat],
    LDA: Int32,
    B: Float64[LDB, Flat],
    LDB: Int32
) -> None: ...

@bind("DTRMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7))])
def dtrmv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    A: Float64[LDA, Flat],
    LDA: Int32,
    X: Float64[Flat],
    INCX: Int32
) -> None: ...

@bind("DTRSM")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def dtrsm(
    SIDE: String[1],
    UPLO: String[1],
    TRANSA: String[1],
    DIAG: String[1],
    M: Int32,
    N: Int32,
    ALPHA: Float64,
    A: Float64[LDA, Flat],
    LDA: Int32,
    B: Float64[LDB, Flat],
    LDB: Int32
) -> None: ...

@bind("DTRSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7))])
def dtrsv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    A: Float64[LDA, Flat],
    LDA: Int32,
    X: Float64[Flat],
    INCX: Int32
) -> None: ...

@bind("DZASUM")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def dzasum(
    N: Int32,
    ZX: Complex128[Flat],
    INCX: Int32
) -> Float64: ...

@bind("DZNRM2")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def dznrm2(
    n: Int32,
    x: Complex128[Flat],
    incx: Int32
) -> Float64: ...

@bind("ICAMAX")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def icamax(
    N: Int32,
    CX: Complex64[Flat],
    INCX: Int32
) -> Int32: ...

@bind("IDAMAX")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def idamax(
    N: Int32,
    DX: Float64[Flat],
    INCX: Int32
) -> Int32: ...

@bind("ISAMAX")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def isamax(
    N: Int32,
    SX: Float32[Flat],
    INCX: Int32
) -> Int32: ...

@bind("IZAMAX")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def izamax(
    N: Int32,
    ZX: Complex128[Flat],
    INCX: Int32
) -> Int32: ...

@bind("LSAME")
@external
def lsame(
    CA: String[1],
    CB: String[1]
) -> Bool: ...

@bind("SASUM")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def sasum(
    N: Int32,
    SX: Float32[Flat],
    INCX: Int32
) -> Float32: ...

@bind("SAXPY")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5))])
def saxpy(
    N: Int32,
    SA: Float32,
    SX: Float32[Flat],
    INCX: Int32,
    SY: Float32[Flat],
    INCY: Int32
) -> None: ...

@bind("SCABS1")
@external
@native_call([Addr(Arg(0))])
def scabs1(
    Z: Complex64
) -> Float32: ...

@bind("SCASUM")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def scasum(
    N: Int32,
    CX: Complex64[Flat],
    INCX: Int32
) -> Float32: ...

@bind("SCNRM2")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def scnrm2(
    n: Int32,
    x: Complex64[Flat],
    incx: Int32
) -> Float32: ...

@bind("SCOPY")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def scopy(
    N: Int32,
    SX: Float32[Flat],
    INCX: Int32,
    SY: Float32[Flat],
    INCY: Int32
) -> None: ...

@bind("SDOT")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def sdot(
    N: Int32,
    SX: Float32[Flat],
    INCX: Int32,
    SY: Float32[Flat],
    INCY: Int32
) -> Float32: ...

@bind("SDSDOT")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5))])
def sdsdot(
    N: Int32,
    SB: Float32,
    SX: Float32[Flat],
    INCX: Int32,
    SY: Float32[Flat],
    INCY: Int32
) -> Float32: ...

@bind("SGBMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def sgbmv(
    TRANS: String[1],
    M: Int32,
    N: Int32,
    KL: Int32,
    KU: Int32,
    ALPHA: Float32,
    A: Float32[LDA, Flat],
    LDA: Int32,
    X: Float32[Flat],
    INCX: Int32,
    BETA: Float32,
    Y: Float32[Flat],
    INCY: Int32
) -> None: ...

@bind("SGEMM")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def sgemm(
    TRANSA: String[1],
    TRANSB: String[1],
    M: Int32,
    N: Int32,
    K: Int32,
    ALPHA: Float32,
    A: Float32[LDA, Flat],
    LDA: Int32,
    B: Float32[LDB, Flat],
    LDB: Int32,
    BETA: Float32,
    C: Float32[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("SGEMMTR")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def sgemmtr(
    UPLO: String[1],
    TRANSA: String[1],
    TRANSB: String[1],
    N: Int32,
    K: Int32,
    ALPHA: Float32,
    A: Float32[LDA, Flat],
    LDA: Int32,
    B: Float32[LDB, Flat],
    LDB: Int32,
    BETA: Float32,
    C: Float32[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("SGEMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def sgemv(
    TRANS: String[1],
    M: Int32,
    N: Int32,
    ALPHA: Float32,
    A: Float32[LDA, Flat],
    LDA: Int32,
    X: Float32[Flat],
    INCX: Int32,
    BETA: Float32,
    Y: Float32[Flat],
    INCY: Int32
) -> None: ...

@bind("SGER")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def sger(
    M: Int32,
    N: Int32,
    ALPHA: Float32,
    X: Float32[Flat],
    INCX: Int32,
    Y: Float32[Flat],
    INCY: Int32,
    A: Float32[LDA, Flat],
    LDA: Int32
) -> None: ...

@bind("SNRM2")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def snrm2(
    n: Int32,
    x: Float32[Flat],
    incx: Int32
) -> Float32: ...

@bind("SROT")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6))])
def srot(
    N: Int32,
    SX: Float32[Flat],
    INCX: Int32,
    SY: Float32[Flat],
    INCY: Int32,
    C: Float32,
    S: Float32
) -> None: ...

@bind("SROTG")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3))])
def srotg(
    a: Float32,
    b: Float32,
    c: Float32,
    s: Float32
) -> None: ...

@bind("SROTM")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5)])
def srotm(
    N: Int32,
    SX: Float32[Flat],
    INCX: Int32,
    SY: Float32[Flat],
    INCY: Int32,
    SPARAM: Float32[5]
) -> None: ...

@bind("SROTMG")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Arg(4)])
def srotmg(
    SD1: Float32,
    SD2: Float32,
    SX1: Float32,
    SY1: Float32,
    SPARAM: Float32[5]
) -> None: ...

@bind("SSBMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def ssbmv(
    UPLO: String[1],
    N: Int32,
    K: Int32,
    ALPHA: Float32,
    A: Float32[LDA, Flat],
    LDA: Int32,
    X: Float32[Flat],
    INCX: Int32,
    BETA: Float32,
    Y: Float32[Flat],
    INCY: Int32
) -> None: ...

@bind("SSCAL")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Addr(Arg(3))])
def sscal(
    N: Int32,
    SA: Float32,
    SX: Float32[Flat],
    INCX: Int32
) -> None: ...

@bind("SSPMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Arg(4), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def sspmv(
    UPLO: String[1],
    N: Int32,
    ALPHA: Float32,
    AP: Float32[Flat],
    X: Float32[Flat],
    INCX: Int32,
    BETA: Float32,
    Y: Float32[Flat],
    INCY: Int32
) -> None: ...

@bind("SSPR")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5)])
def sspr(
    UPLO: String[1],
    N: Int32,
    ALPHA: Float32,
    X: Float32[Flat],
    INCX: Int32,
    AP: Float32[Flat]
) -> None: ...

@bind("SSPR2")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7)])
def sspr2(
    UPLO: String[1],
    N: Int32,
    ALPHA: Float32,
    X: Float32[Flat],
    INCX: Int32,
    Y: Float32[Flat],
    INCY: Int32,
    AP: Float32[Flat]
) -> None: ...

@bind("SSWAP")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def sswap(
    N: Int32,
    SX: Float32[Flat],
    INCX: Int32,
    SY: Float32[Flat],
    INCY: Int32
) -> None: ...

@bind("SSYMM")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def ssymm(
    SIDE: String[1],
    UPLO: String[1],
    M: Int32,
    N: Int32,
    ALPHA: Float32,
    A: Float32[LDA, Flat],
    LDA: Int32,
    B: Float32[LDB, Flat],
    LDB: Int32,
    BETA: Float32,
    C: Float32[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("SSYMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Addr(Arg(9))])
def ssymv(
    UPLO: String[1],
    N: Int32,
    ALPHA: Float32,
    A: Float32[LDA, Flat],
    LDA: Int32,
    X: Float32[Flat],
    INCX: Int32,
    BETA: Float32,
    Y: Float32[Flat],
    INCY: Int32
) -> None: ...

@bind("SSYR")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6))])
def ssyr(
    UPLO: String[1],
    N: Int32,
    ALPHA: Float32,
    X: Float32[Flat],
    INCX: Int32,
    A: Float32[LDA, Flat],
    LDA: Int32
) -> None: ...

@bind("SSYR2")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def ssyr2(
    UPLO: String[1],
    N: Int32,
    ALPHA: Float32,
    X: Float32[Flat],
    INCX: Int32,
    Y: Float32[Flat],
    INCY: Int32,
    A: Float32[LDA, Flat],
    LDA: Int32
) -> None: ...

@bind("SSYR2K")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def ssyr2k(
    UPLO: String[1],
    TRANS: String[1],
    N: Int32,
    K: Int32,
    ALPHA: Float32,
    A: Float32[LDA, Flat],
    LDA: Int32,
    B: Float32[LDB, Flat],
    LDB: Int32,
    BETA: Float32,
    C: Float32[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("SSYRK")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Addr(Arg(9))])
def ssyrk(
    UPLO: String[1],
    TRANS: String[1],
    N: Int32,
    K: Int32,
    ALPHA: Float32,
    A: Float32[LDA, Flat],
    LDA: Int32,
    BETA: Float32,
    C: Float32[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("STBMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def stbmv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    K: Int32,
    A: Float32[LDA, Flat],
    LDA: Int32,
    X: Float32[Flat],
    INCX: Int32
) -> None: ...

@bind("STBSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def stbsv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    K: Int32,
    A: Float32[LDA, Flat],
    LDA: Int32,
    X: Float32[Flat],
    INCX: Int32
) -> None: ...

@bind("STPMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Arg(5), Addr(Arg(6))])
def stpmv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    AP: Float32[Flat],
    X: Float32[Flat],
    INCX: Int32
) -> None: ...

@bind("STPSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Arg(5), Addr(Arg(6))])
def stpsv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    AP: Float32[Flat],
    X: Float32[Flat],
    INCX: Int32
) -> None: ...

@bind("STRMM")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def strmm(
    SIDE: String[1],
    UPLO: String[1],
    TRANSA: String[1],
    DIAG: String[1],
    M: Int32,
    N: Int32,
    ALPHA: Float32,
    A: Float32[LDA, Flat],
    LDA: Int32,
    B: Float32[LDB, Flat],
    LDB: Int32
) -> None: ...

@bind("STRMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7))])
def strmv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    A: Float32[LDA, Flat],
    LDA: Int32,
    X: Float32[Flat],
    INCX: Int32
) -> None: ...

@bind("STRSM")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def strsm(
    SIDE: String[1],
    UPLO: String[1],
    TRANSA: String[1],
    DIAG: String[1],
    M: Int32,
    N: Int32,
    ALPHA: Float32,
    A: Float32[LDA, Flat],
    LDA: Int32,
    B: Float32[LDB, Flat],
    LDB: Int32
) -> None: ...

@bind("STRSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7))])
def strsv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    A: Float32[LDA, Flat],
    LDA: Int32,
    X: Float32[Flat],
    INCX: Int32
) -> None: ...

@bind("XERBLA")
@external
@native_call([Arg(0), Addr(Arg(1))])
def xerbla(
    SRNAME: String,
    INFO: Int32
) -> None: ...

@bind("XERBLA_ARRAY")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2))])
def xerbla_array(
    SRNAME_ARRAY: String[1][SRNAME_LEN],
    SRNAME_LEN: Int32,
    INFO: Int32
) -> None: ...

@bind("ZAXPY")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5))])
def zaxpy(
    N: Int32,
    ZA: Complex128,
    ZX: Complex128[Flat],
    INCX: Int32,
    ZY: Complex128[Flat],
    INCY: Int32
) -> None: ...

@bind("ZCOPY")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def zcopy(
    N: Int32,
    ZX: Complex128[Flat],
    INCX: Int32,
    ZY: Complex128[Flat],
    INCY: Int32
) -> None: ...

@bind("ZDOTC")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def zdotc(
    N: Int32,
    ZX: Complex128[Flat],
    INCX: Int32,
    ZY: Complex128[Flat],
    INCY: Int32
) -> Complex128: ...

@bind("ZDOTU")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def zdotu(
    N: Int32,
    ZX: Complex128[Flat],
    INCX: Int32,
    ZY: Complex128[Flat],
    INCY: Int32
) -> Complex128: ...

@bind("ZDROT")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6))])
def zdrot(
    N: Int32,
    ZX: Complex128[Flat],
    INCX: Int32,
    ZY: Complex128[Flat],
    INCY: Int32,
    C: Float64,
    S: Float64
) -> None: ...

@bind("ZDSCAL")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Addr(Arg(3))])
def zdscal(
    N: Int32,
    DA: Float64,
    ZX: Complex128[Flat],
    INCX: Int32
) -> None: ...

@bind("ZGBMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def zgbmv(
    TRANS: String[1],
    M: Int32,
    N: Int32,
    KL: Int32,
    KU: Int32,
    ALPHA: Complex128,
    A: Complex128[LDA, Flat],
    LDA: Int32,
    X: Complex128[Flat],
    INCX: Int32,
    BETA: Complex128,
    Y: Complex128[Flat],
    INCY: Int32
) -> None: ...

@bind("ZGEMM")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def zgemm(
    TRANSA: String[1],
    TRANSB: String[1],
    M: Int32,
    N: Int32,
    K: Int32,
    ALPHA: Complex128,
    A: Complex128[LDA, Flat],
    LDA: Int32,
    B: Complex128[LDB, Flat],
    LDB: Int32,
    BETA: Complex128,
    C: Complex128[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("ZGEMMTR")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def zgemmtr(
    UPLO: String[1],
    TRANSA: String[1],
    TRANSB: String[1],
    N: Int32,
    K: Int32,
    ALPHA: Complex128,
    A: Complex128[LDA, Flat],
    LDA: Int32,
    B: Complex128[LDB, Flat],
    LDB: Int32,
    BETA: Complex128,
    C: Complex128[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("ZGEMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def zgemv(
    TRANS: String[1],
    M: Int32,
    N: Int32,
    ALPHA: Complex128,
    A: Complex128[LDA, Flat],
    LDA: Int32,
    X: Complex128[Flat],
    INCX: Int32,
    BETA: Complex128,
    Y: Complex128[Flat],
    INCY: Int32
) -> None: ...

@bind("ZGERC")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def zgerc(
    M: Int32,
    N: Int32,
    ALPHA: Complex128,
    X: Complex128[Flat],
    INCX: Int32,
    Y: Complex128[Flat],
    INCY: Int32,
    A: Complex128[LDA, Flat],
    LDA: Int32
) -> None: ...

@bind("ZGERU")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def zgeru(
    M: Int32,
    N: Int32,
    ALPHA: Complex128,
    X: Complex128[Flat],
    INCX: Int32,
    Y: Complex128[Flat],
    INCY: Int32,
    A: Complex128[LDA, Flat],
    LDA: Int32
) -> None: ...

@bind("ZHBMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def zhbmv(
    UPLO: String[1],
    N: Int32,
    K: Int32,
    ALPHA: Complex128,
    A: Complex128[LDA, Flat],
    LDA: Int32,
    X: Complex128[Flat],
    INCX: Int32,
    BETA: Complex128,
    Y: Complex128[Flat],
    INCY: Int32
) -> None: ...

@bind("ZHEMM")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def zhemm(
    SIDE: String[1],
    UPLO: String[1],
    M: Int32,
    N: Int32,
    ALPHA: Complex128,
    A: Complex128[LDA, Flat],
    LDA: Int32,
    B: Complex128[LDB, Flat],
    LDB: Int32,
    BETA: Complex128,
    C: Complex128[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("ZHEMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Addr(Arg(9))])
def zhemv(
    UPLO: String[1],
    N: Int32,
    ALPHA: Complex128,
    A: Complex128[LDA, Flat],
    LDA: Int32,
    X: Complex128[Flat],
    INCX: Int32,
    BETA: Complex128,
    Y: Complex128[Flat],
    INCY: Int32
) -> None: ...

@bind("ZHER")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6))])
def zher(
    UPLO: String[1],
    N: Int32,
    ALPHA: Float64,
    X: Complex128[Flat],
    INCX: Int32,
    A: Complex128[LDA, Flat],
    LDA: Int32
) -> None: ...

@bind("ZHER2")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def zher2(
    UPLO: String[1],
    N: Int32,
    ALPHA: Complex128,
    X: Complex128[Flat],
    INCX: Int32,
    Y: Complex128[Flat],
    INCY: Int32,
    A: Complex128[LDA, Flat],
    LDA: Int32
) -> None: ...

@bind("ZHER2K")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def zher2k(
    UPLO: String[1],
    TRANS: String[1],
    N: Int32,
    K: Int32,
    ALPHA: Complex128,
    A: Complex128[LDA, Flat],
    LDA: Int32,
    B: Complex128[LDB, Flat],
    LDB: Int32,
    BETA: Float64,
    C: Complex128[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("ZHERK")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Addr(Arg(9))])
def zherk(
    UPLO: String[1],
    TRANS: String[1],
    N: Int32,
    K: Int32,
    ALPHA: Float64,
    A: Complex128[LDA, Flat],
    LDA: Int32,
    BETA: Float64,
    C: Complex128[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("ZHPMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Arg(4), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def zhpmv(
    UPLO: String[1],
    N: Int32,
    ALPHA: Complex128,
    AP: Complex128[Flat],
    X: Complex128[Flat],
    INCX: Int32,
    BETA: Complex128,
    Y: Complex128[Flat],
    INCY: Int32
) -> None: ...

@bind("ZHPR")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5)])
def zhpr(
    UPLO: String[1],
    N: Int32,
    ALPHA: Float64,
    X: Complex128[Flat],
    INCX: Int32,
    AP: Complex128[Flat]
) -> None: ...

@bind("ZHPR2")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7)])
def zhpr2(
    UPLO: String[1],
    N: Int32,
    ALPHA: Complex128,
    X: Complex128[Flat],
    INCX: Int32,
    Y: Complex128[Flat],
    INCY: Int32,
    AP: Complex128[Flat]
) -> None: ...

@bind("ZROTG")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3))])
def zrotg(
    a: Complex128,
    b: Complex128,
    c: Float64,
    s: Complex128
) -> None: ...

@bind("ZSCAL")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Addr(Arg(3))])
def zscal(
    N: Int32,
    ZA: Complex128,
    ZX: Complex128[Flat],
    INCX: Int32
) -> None: ...

@bind("ZSWAP")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def zswap(
    N: Int32,
    ZX: Complex128[Flat],
    INCX: Int32,
    ZY: Complex128[Flat],
    INCY: Int32
) -> None: ...

@bind("ZSYMM")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def zsymm(
    SIDE: String[1],
    UPLO: String[1],
    M: Int32,
    N: Int32,
    ALPHA: Complex128,
    A: Complex128[LDA, Flat],
    LDA: Int32,
    B: Complex128[LDB, Flat],
    LDB: Int32,
    BETA: Complex128,
    C: Complex128[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("ZSYR2K")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def zsyr2k(
    UPLO: String[1],
    TRANS: String[1],
    N: Int32,
    K: Int32,
    ALPHA: Complex128,
    A: Complex128[LDA, Flat],
    LDA: Int32,
    B: Complex128[LDB, Flat],
    LDB: Int32,
    BETA: Complex128,
    C: Complex128[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("ZSYRK")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Addr(Arg(9))])
def zsyrk(
    UPLO: String[1],
    TRANS: String[1],
    N: Int32,
    K: Int32,
    ALPHA: Complex128,
    A: Complex128[LDA, Flat],
    LDA: Int32,
    BETA: Complex128,
    C: Complex128[LDC, Flat],
    LDC: Int32
) -> None: ...

@bind("ZTBMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def ztbmv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    K: Int32,
    A: Complex128[LDA, Flat],
    LDA: Int32,
    X: Complex128[Flat],
    INCX: Int32
) -> None: ...

@bind("ZTBSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def ztbsv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    K: Int32,
    A: Complex128[LDA, Flat],
    LDA: Int32,
    X: Complex128[Flat],
    INCX: Int32
) -> None: ...

@bind("ZTPMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Arg(5), Addr(Arg(6))])
def ztpmv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    AP: Complex128[Flat],
    X: Complex128[Flat],
    INCX: Int32
) -> None: ...

@bind("ZTPSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Arg(5), Addr(Arg(6))])
def ztpsv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    AP: Complex128[Flat],
    X: Complex128[Flat],
    INCX: Int32
) -> None: ...

@bind("ZTRMM")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def ztrmm(
    SIDE: String[1],
    UPLO: String[1],
    TRANSA: String[1],
    DIAG: String[1],
    M: Int32,
    N: Int32,
    ALPHA: Complex128,
    A: Complex128[LDA, Flat],
    LDA: Int32,
    B: Complex128[LDB, Flat],
    LDB: Int32
) -> None: ...

@bind("ZTRMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7))])
def ztrmv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    A: Complex128[LDA, Flat],
    LDA: Int32,
    X: Complex128[Flat],
    INCX: Int32
) -> None: ...

@bind("ZTRSM")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def ztrsm(
    SIDE: String[1],
    UPLO: String[1],
    TRANSA: String[1],
    DIAG: String[1],
    M: Int32,
    N: Int32,
    ALPHA: Complex128,
    A: Complex128[LDA, Flat],
    LDA: Int32,
    B: Complex128[LDB, Flat],
    LDB: Int32
) -> None: ...

@bind("ZTRSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7))])
def ztrsv(
    UPLO: String[1],
    TRANS: String[1],
    DIAG: String[1],
    N: Int32,
    A: Complex128[LDA, Flat],
    LDA: Int32,
    X: Complex128[Flat],
    INCX: Int32
) -> None: ...
