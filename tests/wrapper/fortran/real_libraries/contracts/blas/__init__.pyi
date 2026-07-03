@bind("CAXPY")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5))])
def caxpy(
    N: Annotated[Int32, Intent('inout')],
    CA: Annotated[Complex64, Intent('inout')],
    CX: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    CY: Complex64[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CCOPY")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def ccopy(
    N: Annotated[Int32, Intent('inout')],
    CX: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    CY: Complex64[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CDOTC")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def cdotc(
    N: Annotated[Int32, Intent('inout')],
    CX: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    CY: Complex64[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> Complex64: ...

@bind("CDOTU")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def cdotu(
    N: Annotated[Int32, Intent('inout')],
    CX: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    CY: Complex64[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> Complex64: ...

@bind("CGBMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def cgbmv(
    TRANS: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    KL: Annotated[Int32, Intent('inout')],
    KU: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex64, Intent('inout')],
    A: Complex64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Complex64, Intent('inout')],
    Y: Complex64[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CGEMM")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def cgemm(
    TRANSA: Const(String[1]),
    TRANSB: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex64, Intent('inout')],
    A: Complex64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Complex64[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Complex64, Intent('inout')],
    C: Complex64[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CGEMMTR")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def cgemmtr(
    UPLO: Const(String[1]),
    TRANSA: Const(String[1]),
    TRANSB: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex64, Intent('inout')],
    A: Complex64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Complex64[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Complex64, Intent('inout')],
    C: Complex64[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CGEMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def cgemv(
    TRANS: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex64, Intent('inout')],
    A: Complex64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Complex64, Intent('inout')],
    Y: Complex64[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CGERC")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def cgerc(
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex64, Intent('inout')],
    X: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    Y: Complex64[Flat],
    INCY: Annotated[Int32, Intent('inout')],
    A: Complex64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CGERU")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def cgeru(
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex64, Intent('inout')],
    X: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    Y: Complex64[Flat],
    INCY: Annotated[Int32, Intent('inout')],
    A: Complex64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CHBMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def chbmv(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex64, Intent('inout')],
    A: Complex64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Complex64, Intent('inout')],
    Y: Complex64[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CHEMM")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def chemm(
    SIDE: Const(String[1]),
    UPLO: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex64, Intent('inout')],
    A: Complex64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Complex64[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Complex64, Intent('inout')],
    C: Complex64[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CHEMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Addr(Arg(9))])
def chemv(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex64, Intent('inout')],
    A: Complex64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Complex64, Intent('inout')],
    Y: Complex64[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CHER")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6))])
def cher(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float32, Intent('inout')],
    X: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    A: Complex64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CHER2")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def cher2(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex64, Intent('inout')],
    X: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    Y: Complex64[Flat],
    INCY: Annotated[Int32, Intent('inout')],
    A: Complex64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CHER2K")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def cher2k(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex64, Intent('inout')],
    A: Complex64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Complex64[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float32, Intent('inout')],
    C: Complex64[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CHERK")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Addr(Arg(9))])
def cherk(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float32, Intent('inout')],
    A: Complex64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float32, Intent('inout')],
    C: Complex64[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CHPMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Arg(4), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def chpmv(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex64, Intent('inout')],
    AP: Complex64[Flat],
    X: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Complex64, Intent('inout')],
    Y: Complex64[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CHPR")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5)])
def chpr(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float32, Intent('inout')],
    X: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    AP: Complex64[Flat]
) -> None: ...

@bind("CHPR2")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7)])
def chpr2(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex64, Intent('inout')],
    X: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    Y: Complex64[Flat],
    INCY: Annotated[Int32, Intent('inout')],
    AP: Complex64[Flat]
) -> None: ...

@bind("CROTG")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3))])
def crotg(
    a: Annotated[Complex64, Intent('inout')],
    b: Annotated[Complex64, Intent('inout')],
    c: Annotated[Float32, Intent('inout')],
    s: Annotated[Complex64, Intent('inout')]
) -> None: ...

@bind("CSCAL")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Addr(Arg(3))])
def cscal(
    N: Annotated[Int32, Intent('inout')],
    CA: Annotated[Complex64, Intent('inout')],
    CX: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CSROT")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6))])
def csrot(
    N: Annotated[Int32, Intent('inout')],
    CX: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    CY: Complex64[Flat],
    INCY: Annotated[Int32, Intent('inout')],
    C: Annotated[Float32, Intent('inout')],
    S: Annotated[Float32, Intent('inout')]
) -> None: ...

@bind("CSSCAL")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Addr(Arg(3))])
def csscal(
    N: Annotated[Int32, Intent('inout')],
    SA: Annotated[Float32, Intent('inout')],
    CX: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CSWAP")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def cswap(
    N: Annotated[Int32, Intent('inout')],
    CX: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    CY: Complex64[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CSYMM")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def csymm(
    SIDE: Const(String[1]),
    UPLO: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex64, Intent('inout')],
    A: Complex64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Complex64[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Complex64, Intent('inout')],
    C: Complex64[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CSYR2K")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def csyr2k(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex64, Intent('inout')],
    A: Complex64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Complex64[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Complex64, Intent('inout')],
    C: Complex64[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CSYRK")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Addr(Arg(9))])
def csyrk(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex64, Intent('inout')],
    A: Complex64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Complex64, Intent('inout')],
    C: Complex64[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CTBMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def ctbmv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    A: Complex64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CTBSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def ctbsv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    A: Complex64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CTPMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Arg(5), Addr(Arg(6))])
def ctpmv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    AP: Complex64[Flat],
    X: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CTPSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Arg(5), Addr(Arg(6))])
def ctpsv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    AP: Complex64[Flat],
    X: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CTRMM")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def ctrmm(
    SIDE: Const(String[1]),
    UPLO: Const(String[1]),
    TRANSA: Const(String[1]),
    DIAG: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex64, Intent('inout')],
    A: Complex64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Complex64[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CTRMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7))])
def ctrmv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    A: Complex64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CTRSM")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def ctrsm(
    SIDE: Const(String[1]),
    UPLO: Const(String[1]),
    TRANSA: Const(String[1]),
    DIAG: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex64, Intent('inout')],
    A: Complex64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Complex64[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("CTRSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7))])
def ctrsv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    A: Complex64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DASUM")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def dasum(
    N: Annotated[Int32, Intent('inout')],
    DX: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> Float64: ...

@bind("DAXPY")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5))])
def daxpy(
    N: Annotated[Int32, Intent('inout')],
    DA: Annotated[Float64, Intent('inout')],
    DX: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    DY: Float64[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DCABS1")
@external
@native_call([Addr(Arg(0))])
def dcabs1(
    Z: Annotated[Complex128, Intent('inout')]
) -> Float64: ...

@bind("DCOPY")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def dcopy(
    N: Annotated[Int32, Intent('inout')],
    DX: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    DY: Float64[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DDOT")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def ddot(
    N: Annotated[Int32, Intent('inout')],
    DX: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    DY: Float64[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> Float64: ...

@bind("DGBMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def dgbmv(
    TRANS: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    KL: Annotated[Int32, Intent('inout')],
    KU: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float64, Intent('inout')],
    A: Float64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float64, Intent('inout')],
    Y: Float64[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DGEMM")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def dgemm(
    TRANSA: Const(String[1]),
    TRANSB: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float64, Intent('inout')],
    A: Float64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Float64[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float64, Intent('inout')],
    C: Float64[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DGEMMTR")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def dgemmtr(
    UPLO: Const(String[1]),
    TRANSA: Const(String[1]),
    TRANSB: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float64, Intent('inout')],
    A: Float64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Float64[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float64, Intent('inout')],
    C: Float64[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DGEMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def dgemv(
    TRANS: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float64, Intent('inout')],
    A: Float64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float64, Intent('inout')],
    Y: Float64[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DGER")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def dger(
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float64, Intent('inout')],
    X: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    Y: Float64[Flat],
    INCY: Annotated[Int32, Intent('inout')],
    A: Float64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DNRM2")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def dnrm2(
    n: Annotated[Int32, Intent('inout')],
    x: Float64[Flat],
    incx: Annotated[Int32, Intent('inout')]
) -> Float64: ...

@bind("DROT")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6))])
def drot(
    N: Annotated[Int32, Intent('inout')],
    DX: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    DY: Float64[Flat],
    INCY: Annotated[Int32, Intent('inout')],
    C: Annotated[Float64, Intent('inout')],
    S: Annotated[Float64, Intent('inout')]
) -> None: ...

@bind("DROTG")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3))])
def drotg(
    a: Annotated[Float64, Intent('inout')],
    b: Annotated[Float64, Intent('inout')],
    c: Annotated[Float64, Intent('inout')],
    s: Annotated[Float64, Intent('inout')]
) -> None: ...

@bind("DROTM")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5)])
def drotm(
    N: Annotated[Int32, Intent('inout')],
    DX: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    DY: Float64[Flat],
    INCY: Annotated[Int32, Intent('inout')],
    DPARAM: Float64[5]
) -> None: ...

@bind("DROTMG")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Arg(4)])
def drotmg(
    DD1: Annotated[Float64, Intent('inout')],
    DD2: Annotated[Float64, Intent('inout')],
    DX1: Annotated[Float64, Intent('inout')],
    DY1: Annotated[Float64, Intent('inout')],
    DPARAM: Float64[5]
) -> None: ...

@bind("DSBMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def dsbmv(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float64, Intent('inout')],
    A: Float64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float64, Intent('inout')],
    Y: Float64[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DSCAL")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Addr(Arg(3))])
def dscal(
    N: Annotated[Int32, Intent('inout')],
    DA: Annotated[Float64, Intent('inout')],
    DX: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DSDOT")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def dsdot(
    N: Annotated[Int32, Intent('inout')],
    SX: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    SY: Float32[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> Float64: ...

@bind("DSPMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Arg(4), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def dspmv(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float64, Intent('inout')],
    AP: Float64[Flat],
    X: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float64, Intent('inout')],
    Y: Float64[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DSPR")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5)])
def dspr(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float64, Intent('inout')],
    X: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    AP: Float64[Flat]
) -> None: ...

@bind("DSPR2")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7)])
def dspr2(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float64, Intent('inout')],
    X: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    Y: Float64[Flat],
    INCY: Annotated[Int32, Intent('inout')],
    AP: Float64[Flat]
) -> None: ...

@bind("DSWAP")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def dswap(
    N: Annotated[Int32, Intent('inout')],
    DX: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    DY: Float64[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DSYMM")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def dsymm(
    SIDE: Const(String[1]),
    UPLO: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float64, Intent('inout')],
    A: Float64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Float64[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float64, Intent('inout')],
    C: Float64[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DSYMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Addr(Arg(9))])
def dsymv(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float64, Intent('inout')],
    A: Float64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float64, Intent('inout')],
    Y: Float64[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DSYR")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6))])
def dsyr(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float64, Intent('inout')],
    X: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    A: Float64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DSYR2")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def dsyr2(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float64, Intent('inout')],
    X: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    Y: Float64[Flat],
    INCY: Annotated[Int32, Intent('inout')],
    A: Float64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DSYR2K")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def dsyr2k(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float64, Intent('inout')],
    A: Float64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Float64[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float64, Intent('inout')],
    C: Float64[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DSYRK")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Addr(Arg(9))])
def dsyrk(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float64, Intent('inout')],
    A: Float64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float64, Intent('inout')],
    C: Float64[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DTBMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def dtbmv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    A: Float64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DTBSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def dtbsv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    A: Float64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DTPMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Arg(5), Addr(Arg(6))])
def dtpmv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    AP: Float64[Flat],
    X: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DTPSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Arg(5), Addr(Arg(6))])
def dtpsv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    AP: Float64[Flat],
    X: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DTRMM")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def dtrmm(
    SIDE: Const(String[1]),
    UPLO: Const(String[1]),
    TRANSA: Const(String[1]),
    DIAG: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float64, Intent('inout')],
    A: Float64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Float64[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DTRMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7))])
def dtrmv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    A: Float64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DTRSM")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def dtrsm(
    SIDE: Const(String[1]),
    UPLO: Const(String[1]),
    TRANSA: Const(String[1]),
    DIAG: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float64, Intent('inout')],
    A: Float64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Float64[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DTRSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7))])
def dtrsv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    A: Float64[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("DZASUM")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def dzasum(
    N: Annotated[Int32, Intent('inout')],
    ZX: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> Float64: ...

@bind("DZNRM2")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def dznrm2(
    n: Annotated[Int32, Intent('inout')],
    x: Complex128[Flat],
    incx: Annotated[Int32, Intent('inout')]
) -> Float64: ...

@bind("ICAMAX")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def icamax(
    N: Annotated[Int32, Intent('inout')],
    CX: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> Int32: ...

@bind("IDAMAX")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def idamax(
    N: Annotated[Int32, Intent('inout')],
    DX: Float64[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> Int32: ...

@bind("ISAMAX")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def isamax(
    N: Annotated[Int32, Intent('inout')],
    SX: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> Int32: ...

@bind("IZAMAX")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def izamax(
    N: Annotated[Int32, Intent('inout')],
    ZX: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> Int32: ...

@bind("LSAME")
@external
def lsame(
    CA: Const(String[1]),
    CB: Const(String[1])
) -> Bool: ...

@bind("SASUM")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def sasum(
    N: Annotated[Int32, Intent('inout')],
    SX: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> Float32: ...

@bind("SAXPY")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5))])
def saxpy(
    N: Annotated[Int32, Intent('inout')],
    SA: Annotated[Float32, Intent('inout')],
    SX: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    SY: Float32[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("SCABS1")
@external
@native_call([Addr(Arg(0))])
def scabs1(
    Z: Annotated[Complex64, Intent('inout')]
) -> Float32: ...

@bind("SCASUM")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def scasum(
    N: Annotated[Int32, Intent('inout')],
    CX: Complex64[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> Float32: ...

@bind("SCNRM2")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def scnrm2(
    n: Annotated[Int32, Intent('inout')],
    x: Complex64[Flat],
    incx: Annotated[Int32, Intent('inout')]
) -> Float32: ...

@bind("SCOPY")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def scopy(
    N: Annotated[Int32, Intent('inout')],
    SX: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    SY: Float32[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("SDOT")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def sdot(
    N: Annotated[Int32, Intent('inout')],
    SX: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    SY: Float32[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> Float32: ...

@bind("SDSDOT")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5))])
def sdsdot(
    N: Annotated[Int32, Intent('inout')],
    SB: Annotated[Float32, Intent('inout')],
    SX: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    SY: Float32[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> Float32: ...

@bind("SGBMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def sgbmv(
    TRANS: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    KL: Annotated[Int32, Intent('inout')],
    KU: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float32, Intent('inout')],
    A: Float32[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float32, Intent('inout')],
    Y: Float32[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("SGEMM")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def sgemm(
    TRANSA: Const(String[1]),
    TRANSB: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float32, Intent('inout')],
    A: Float32[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Float32[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float32, Intent('inout')],
    C: Float32[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("SGEMMTR")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def sgemmtr(
    UPLO: Const(String[1]),
    TRANSA: Const(String[1]),
    TRANSB: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float32, Intent('inout')],
    A: Float32[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Float32[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float32, Intent('inout')],
    C: Float32[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("SGEMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def sgemv(
    TRANS: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float32, Intent('inout')],
    A: Float32[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float32, Intent('inout')],
    Y: Float32[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("SGER")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def sger(
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float32, Intent('inout')],
    X: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    Y: Float32[Flat],
    INCY: Annotated[Int32, Intent('inout')],
    A: Float32[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("SNRM2")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2))])
def snrm2(
    n: Annotated[Int32, Intent('inout')],
    x: Float32[Flat],
    incx: Annotated[Int32, Intent('inout')]
) -> Float32: ...

@bind("SROT")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6))])
def srot(
    N: Annotated[Int32, Intent('inout')],
    SX: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    SY: Float32[Flat],
    INCY: Annotated[Int32, Intent('inout')],
    C: Annotated[Float32, Intent('inout')],
    S: Annotated[Float32, Intent('inout')]
) -> None: ...

@bind("SROTG")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3))])
def srotg(
    a: Annotated[Float32, Intent('inout')],
    b: Annotated[Float32, Intent('inout')],
    c: Annotated[Float32, Intent('inout')],
    s: Annotated[Float32, Intent('inout')]
) -> None: ...

@bind("SROTM")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5)])
def srotm(
    N: Annotated[Int32, Intent('inout')],
    SX: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    SY: Float32[Flat],
    INCY: Annotated[Int32, Intent('inout')],
    SPARAM: Float32[5]
) -> None: ...

@bind("SROTMG")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Arg(4)])
def srotmg(
    SD1: Annotated[Float32, Intent('inout')],
    SD2: Annotated[Float32, Intent('inout')],
    SX1: Annotated[Float32, Intent('inout')],
    SY1: Annotated[Float32, Intent('inout')],
    SPARAM: Float32[5]
) -> None: ...

@bind("SSBMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def ssbmv(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float32, Intent('inout')],
    A: Float32[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float32, Intent('inout')],
    Y: Float32[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("SSCAL")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Addr(Arg(3))])
def sscal(
    N: Annotated[Int32, Intent('inout')],
    SA: Annotated[Float32, Intent('inout')],
    SX: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("SSPMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Arg(4), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def sspmv(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float32, Intent('inout')],
    AP: Float32[Flat],
    X: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float32, Intent('inout')],
    Y: Float32[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("SSPR")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5)])
def sspr(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float32, Intent('inout')],
    X: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    AP: Float32[Flat]
) -> None: ...

@bind("SSPR2")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7)])
def sspr2(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float32, Intent('inout')],
    X: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    Y: Float32[Flat],
    INCY: Annotated[Int32, Intent('inout')],
    AP: Float32[Flat]
) -> None: ...

@bind("SSWAP")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def sswap(
    N: Annotated[Int32, Intent('inout')],
    SX: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    SY: Float32[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("SSYMM")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def ssymm(
    SIDE: Const(String[1]),
    UPLO: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float32, Intent('inout')],
    A: Float32[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Float32[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float32, Intent('inout')],
    C: Float32[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("SSYMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Addr(Arg(9))])
def ssymv(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float32, Intent('inout')],
    A: Float32[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float32, Intent('inout')],
    Y: Float32[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("SSYR")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6))])
def ssyr(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float32, Intent('inout')],
    X: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    A: Float32[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("SSYR2")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def ssyr2(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float32, Intent('inout')],
    X: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    Y: Float32[Flat],
    INCY: Annotated[Int32, Intent('inout')],
    A: Float32[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("SSYR2K")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def ssyr2k(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float32, Intent('inout')],
    A: Float32[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Float32[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float32, Intent('inout')],
    C: Float32[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("SSYRK")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Addr(Arg(9))])
def ssyrk(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float32, Intent('inout')],
    A: Float32[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float32, Intent('inout')],
    C: Float32[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("STBMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def stbmv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    A: Float32[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("STBSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def stbsv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    A: Float32[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("STPMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Arg(5), Addr(Arg(6))])
def stpmv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    AP: Float32[Flat],
    X: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("STPSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Arg(5), Addr(Arg(6))])
def stpsv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    AP: Float32[Flat],
    X: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("STRMM")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def strmm(
    SIDE: Const(String[1]),
    UPLO: Const(String[1]),
    TRANSA: Const(String[1]),
    DIAG: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float32, Intent('inout')],
    A: Float32[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Float32[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("STRMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7))])
def strmv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    A: Float32[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("STRSM")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def strsm(
    SIDE: Const(String[1]),
    UPLO: Const(String[1]),
    TRANSA: Const(String[1]),
    DIAG: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float32, Intent('inout')],
    A: Float32[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Float32[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("STRSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7))])
def strsv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    A: Float32[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Float32[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("XERBLA")
@external
@native_call([Arg(0), Addr(Arg(1))])
def xerbla(
    SRNAME: Const(String),
    INFO: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("XERBLA_ARRAY")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2))])
def xerbla_array(
    SRNAME_ARRAY: String[1][SRNAME_LEN],
    SRNAME_LEN: Annotated[Int32, Intent('inout')],
    INFO: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZAXPY")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5))])
def zaxpy(
    N: Annotated[Int32, Intent('inout')],
    ZA: Annotated[Complex128, Intent('inout')],
    ZX: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    ZY: Complex128[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZCOPY")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def zcopy(
    N: Annotated[Int32, Intent('inout')],
    ZX: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    ZY: Complex128[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZDOTC")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def zdotc(
    N: Annotated[Int32, Intent('inout')],
    ZX: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    ZY: Complex128[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> Complex128: ...

@bind("ZDOTU")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def zdotu(
    N: Annotated[Int32, Intent('inout')],
    ZX: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    ZY: Complex128[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> Complex128: ...

@bind("ZDROT")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6))])
def zdrot(
    N: Annotated[Int32, Intent('inout')],
    ZX: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    ZY: Complex128[Flat],
    INCY: Annotated[Int32, Intent('inout')],
    C: Annotated[Float64, Intent('inout')],
    S: Annotated[Float64, Intent('inout')]
) -> None: ...

@bind("ZDSCAL")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Addr(Arg(3))])
def zdscal(
    N: Annotated[Int32, Intent('inout')],
    DA: Annotated[Float64, Intent('inout')],
    ZX: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZGBMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def zgbmv(
    TRANS: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    KL: Annotated[Int32, Intent('inout')],
    KU: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex128, Intent('inout')],
    A: Complex128[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Complex128, Intent('inout')],
    Y: Complex128[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZGEMM")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def zgemm(
    TRANSA: Const(String[1]),
    TRANSB: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex128, Intent('inout')],
    A: Complex128[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Complex128[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Complex128, Intent('inout')],
    C: Complex128[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZGEMMTR")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Arg(8), Addr(Arg(9)), Addr(Arg(10)), Arg(11), Addr(Arg(12))])
def zgemmtr(
    UPLO: Const(String[1]),
    TRANSA: Const(String[1]),
    TRANSB: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex128, Intent('inout')],
    A: Complex128[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Complex128[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Complex128, Intent('inout')],
    C: Complex128[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZGEMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def zgemv(
    TRANS: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex128, Intent('inout')],
    A: Complex128[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Complex128, Intent('inout')],
    Y: Complex128[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZGERC")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def zgerc(
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex128, Intent('inout')],
    X: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    Y: Complex128[Flat],
    INCY: Annotated[Int32, Intent('inout')],
    A: Complex128[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZGERU")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def zgeru(
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex128, Intent('inout')],
    X: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    Y: Complex128[Flat],
    INCY: Annotated[Int32, Intent('inout')],
    A: Complex128[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZHBMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7)), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def zhbmv(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex128, Intent('inout')],
    A: Complex128[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Complex128, Intent('inout')],
    Y: Complex128[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZHEMM")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def zhemm(
    SIDE: Const(String[1]),
    UPLO: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex128, Intent('inout')],
    A: Complex128[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Complex128[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Complex128, Intent('inout')],
    C: Complex128[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZHEMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Addr(Arg(9))])
def zhemv(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex128, Intent('inout')],
    A: Complex128[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Complex128, Intent('inout')],
    Y: Complex128[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZHER")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6))])
def zher(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float64, Intent('inout')],
    X: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    A: Complex128[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZHER2")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def zher2(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex128, Intent('inout')],
    X: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    Y: Complex128[Flat],
    INCY: Annotated[Int32, Intent('inout')],
    A: Complex128[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZHER2K")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def zher2k(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex128, Intent('inout')],
    A: Complex128[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Complex128[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float64, Intent('inout')],
    C: Complex128[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZHERK")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Addr(Arg(9))])
def zherk(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float64, Intent('inout')],
    A: Complex128[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Float64, Intent('inout')],
    C: Complex128[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZHPMV")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Arg(4), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def zhpmv(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex128, Intent('inout')],
    AP: Complex128[Flat],
    X: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Complex128, Intent('inout')],
    Y: Complex128[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZHPR")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5)])
def zhpr(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Float64, Intent('inout')],
    X: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    AP: Complex128[Flat]
) -> None: ...

@bind("ZHPR2")
@external
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2)), Arg(3), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7)])
def zhpr2(
    UPLO: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex128, Intent('inout')],
    X: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    Y: Complex128[Flat],
    INCY: Annotated[Int32, Intent('inout')],
    AP: Complex128[Flat]
) -> None: ...

@bind("ZROTG")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Addr(Arg(2)), Addr(Arg(3))])
def zrotg(
    a: Annotated[Complex128, Intent('inout')],
    b: Annotated[Complex128, Intent('inout')],
    c: Annotated[Float64, Intent('inout')],
    s: Annotated[Complex128, Intent('inout')]
) -> None: ...

@bind("ZSCAL")
@external
@native_call([Addr(Arg(0)), Addr(Arg(1)), Arg(2), Addr(Arg(3))])
def zscal(
    N: Annotated[Int32, Intent('inout')],
    ZA: Annotated[Complex128, Intent('inout')],
    ZX: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZSWAP")
@external
@native_call([Addr(Arg(0)), Arg(1), Addr(Arg(2)), Arg(3), Addr(Arg(4))])
def zswap(
    N: Annotated[Int32, Intent('inout')],
    ZX: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')],
    ZY: Complex128[Flat],
    INCY: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZSYMM")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def zsymm(
    SIDE: Const(String[1]),
    UPLO: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex128, Intent('inout')],
    A: Complex128[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Complex128[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Complex128, Intent('inout')],
    C: Complex128[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZSYR2K")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Addr(Arg(9)), Arg(10), Addr(Arg(11))])
def zsyr2k(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex128, Intent('inout')],
    A: Complex128[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Complex128[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Complex128, Intent('inout')],
    C: Complex128[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZSYRK")
@external
@native_call([Arg(0), Arg(1), Addr(Arg(2)), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Addr(Arg(7)), Arg(8), Addr(Arg(9))])
def zsyrk(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex128, Intent('inout')],
    A: Complex128[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    BETA: Annotated[Complex128, Intent('inout')],
    C: Complex128[LDC, Flat],
    LDC: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZTBMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def ztbmv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    A: Complex128[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZTBSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Addr(Arg(4)), Arg(5), Addr(Arg(6)), Arg(7), Addr(Arg(8))])
def ztbsv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    K: Annotated[Int32, Intent('inout')],
    A: Complex128[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZTPMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Arg(5), Addr(Arg(6))])
def ztpmv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    AP: Complex128[Flat],
    X: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZTPSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Arg(5), Addr(Arg(6))])
def ztpsv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    AP: Complex128[Flat],
    X: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZTRMM")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def ztrmm(
    SIDE: Const(String[1]),
    UPLO: Const(String[1]),
    TRANSA: Const(String[1]),
    DIAG: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex128, Intent('inout')],
    A: Complex128[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Complex128[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZTRMV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7))])
def ztrmv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    A: Complex128[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZTRSM")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Addr(Arg(4)), Addr(Arg(5)), Addr(Arg(6)), Arg(7), Addr(Arg(8)), Arg(9), Addr(Arg(10))])
def ztrsm(
    SIDE: Const(String[1]),
    UPLO: Const(String[1]),
    TRANSA: Const(String[1]),
    DIAG: Const(String[1]),
    M: Annotated[Int32, Intent('inout')],
    N: Annotated[Int32, Intent('inout')],
    ALPHA: Annotated[Complex128, Intent('inout')],
    A: Complex128[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    B: Complex128[LDB, Flat],
    LDB: Annotated[Int32, Intent('inout')]
) -> None: ...

@bind("ZTRSV")
@external
@native_call([Arg(0), Arg(1), Arg(2), Addr(Arg(3)), Arg(4), Addr(Arg(5)), Arg(6), Addr(Arg(7))])
def ztrsv(
    UPLO: Const(String[1]),
    TRANS: Const(String[1]),
    DIAG: Const(String[1]),
    N: Annotated[Int32, Intent('inout')],
    A: Complex128[LDA, Flat],
    LDA: Annotated[Int32, Intent('inout')],
    X: Complex128[Flat],
    INCX: Annotated[Int32, Intent('inout')]
) -> None: ...
