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

@bind("DDOT")
@external
def ddot(
    N: Ptr(Int32),
    DX: Float64[Flat],
    INCX: Ptr(Int32),
    DY: Float64[Flat],
    INCY: Ptr(Int32)
) -> Float64: ...

@bind("DSCAL")
@external
def dscal(
    N: Ptr(Int32),
    DA: Ptr(Float64),
    DX: Float64[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("DLABAD")
@external
def dlabad(
    SMALL: Ptr(Float64),
    LARGE: Ptr(Float64)
) -> None: ...

@bind("DLAED5")
@external
def dlaed5(
    I: Ptr(Int32),
    D: Float64[2],
    Z: Float64[2],
    DELTA: Float64[2],
    RHO: Ptr(Float64),
    DLAM: Ptr(Float64)
) -> None: ...

@bind("DLAMRG")
@external
def dlamrg(
    N1: Ptr(Int32),
    N2: Ptr(Int32),
    A: Float64[Flat],
    DTRD1: Ptr(Int32),
    DTRD2: Ptr(Int32),
    INDEX: Int32[Flat]
) -> None: ...
