from . import LA_CONSTANTS
from . import LA_XISNAN

@bind("CBBCSD")
@external
def cbbcsd(
    JOBU1: Ptr(Const(String[1])),
    JOBU2: Ptr(Const(String[1])),
    JOBV1T: Ptr(Const(String[1])),
    JOBV2T: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    U1: Complex64[LDU1, Flat],
    LDU1: Ptr(Int32),
    U2: Complex64[LDU2, Flat],
    LDU2: Ptr(Int32),
    V1T: Complex64[LDV1T, Flat],
    LDV1T: Ptr(Int32),
    V2T: Complex64[LDV2T, Flat],
    LDV2T: Ptr(Int32),
    B11D: Float32[Flat],
    B11E: Float32[Flat],
    B12D: Float32[Flat],
    B12E: Float32[Flat],
    B21D: Float32[Flat],
    B21E: Float32[Flat],
    B22D: Float32[Flat],
    B22E: Float32[Flat],
    RWORK: Float32[Flat],
    LRWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CBDSQR")
@external
def cbdsqr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NCVT: Ptr(Int32),
    NRU: Ptr(Int32),
    NCC: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VT: Complex64[LDVT, Flat],
    LDVT: Ptr(Int32),
    U: Complex64[LDU, Flat],
    LDU: Ptr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGBBRD")
@external
def cgbbrd(
    VECT: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    NCC: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Int32),
    PT: Complex64[LDPT, Flat],
    LDPT: Ptr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGBCON")
@external
def cgbcon(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    IPIV: Int32[Flat],
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGBEQU")
@external
def cgbequ(
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ptr(Float32),
    COLCND: Ptr(Float32),
    AMAX: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGBEQUB")
@external
def cgbequb(
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ptr(Float32),
    COLCND: Ptr(Float32),
    AMAX: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGBRFS")
@external
def cgbrfs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGBRFSX")
@external
def cgbrfsx(
    TRANS: Ptr(Const(String[1])),
    EQUED: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    R: Float32[Flat],
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGBSV")
@external
def cgbsv(
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGBSVX")
@external
def cgbsvx(
    FACT: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    EQUED: Ptr(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGBSVXX")
@external
def cgbsvxx(
    FACT: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    EQUED: Ptr(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    RPVGRW: Ptr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGBTF2")
@external
def cgbtf2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGBTRF")
@external
def cgbtrf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGBTRS")
@external
def cgbtrs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEBAK")
@external
def cgebak(
    JOB: Ptr(Const(String[1])),
    SIDE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    SCALE: Float32[Flat],
    M: Ptr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEBAL")
@external
def cgebal(
    JOB: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    SCALE: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEBD2")
@external
def cgebd2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAUQ: Complex64[Flat],
    TAUP: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEBRD")
@external
def cgebrd(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAUQ: Complex64[Flat],
    TAUP: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGECON")
@external
def cgecon(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEDMD")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7), Arg(8), Arg(9), Arg(10), Arg(11), Arg(12), Return('K', 0), Arg(13), Arg(14), Arg(15), Arg(16), Arg(17), Arg(18), Arg(19), Arg(20), Arg(21), Arg(22), Arg(23), Arg(24), Arg(25), Arg(26), Arg(27), Arg(28), Return('INFO', 10)])
def cgedmd(
    JOBS: Ptr(Const(String[1])),
    JOBZ: Ptr(Const(String[1])),
    JOBR: Ptr(Const(String[1])),
    JOBF: Ptr(Const(String[1])),
    WHTSVD: Ptr(Const(Int32)),
    M: Ptr(Const(Int32)),
    N: Ptr(Const(Int32)),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Const(Int32)),
    Y: Complex64[LDY, Flat],
    LDY: Ptr(Const(Int32)),
    NRNK: Ptr(Const(Int32)),
    TOL: Ptr(Const(Float32)),
    EIGS: Complex64[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Const(Int32)),
    RES: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    W: Complex64[LDW, Flat],
    LDW: Ptr(Const(Int32)),
    S: Complex64[LDS, Flat],
    LDS: Ptr(Const(Int32)),
    ZWORK: Complex64[Flat],
    LZWORK: Ptr(Const(Int32)),
    RWORK: Float32[Flat],
    LRWORK: Ptr(Const(Int32)),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Const(Int32))
) -> tuple[Int32, Returns["EIGS", Complex64[Flat]], Returns["Z", Complex64[LDZ, Flat]], Returns["RES", Float32[Flat]], Returns["B", Complex64[LDB, Flat]], Returns["W", Complex64[LDW, Flat]], Returns["S", Complex64[LDS, Flat]], Returns["ZWORK", Complex64[Flat]], Returns["RWORK", Float32[Flat]], Returns["IWORK", Int32[Flat]], Int32]: ...

@bind("CGEDMDQ")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7), Arg(8), Arg(9), Arg(10), Arg(11), Arg(12), Arg(13), Arg(14), Arg(15), Arg(16), Return('K', 2), Arg(17), Arg(18), Arg(19), Arg(20), Arg(21), Arg(22), Arg(23), Arg(24), Arg(25), Arg(26), Arg(27), Arg(28), Arg(29), Arg(30), Arg(31), Arg(32), Return('INFO', 12)])
def cgedmdq(
    JOBS: Ptr(Const(String[1])),
    JOBZ: Ptr(Const(String[1])),
    JOBR: Ptr(Const(String[1])),
    JOBQ: Ptr(Const(String[1])),
    JOBT: Ptr(Const(String[1])),
    JOBF: Ptr(Const(String[1])),
    WHTSVD: Ptr(Const(Int32)),
    M: Ptr(Const(Int32)),
    N: Ptr(Const(Int32)),
    F: Complex64[LDF, Flat],
    LDF: Ptr(Const(Int32)),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Const(Int32)),
    Y: Complex64[LDY, Flat],
    LDY: Ptr(Const(Int32)),
    NRNK: Ptr(Const(Int32)),
    TOL: Ptr(Const(Float32)),
    EIGS: Complex64[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Const(Int32)),
    RES: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    V: Complex64[LDV, Flat],
    LDV: Ptr(Const(Int32)),
    S: Complex64[LDS, Flat],
    LDS: Ptr(Const(Int32)),
    ZWORK: Complex64[Flat],
    LZWORK: Ptr(Const(Int32)),
    WORK: Float32[Flat],
    LWORK: Ptr(Const(Int32)),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Const(Int32))
) -> tuple[Returns["X", Complex64[LDX, Flat]], Returns["Y", Complex64[LDY, Flat]], Int32, Returns["EIGS", Complex64[Flat]], Returns["Z", Complex64[LDZ, Flat]], Returns["RES", Float32[Flat]], Returns["B", Complex64[LDB, Flat]], Returns["V", Complex64[LDV, Flat]], Returns["S", Complex64[LDS, Flat]], Returns["ZWORK", Complex64[Flat]], Returns["WORK", Float32[Flat]], Returns["IWORK", Int32[Flat]], Int32]: ...

@bind("CGEEQU")
@external
def cgeequ(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ptr(Float32),
    COLCND: Ptr(Float32),
    AMAX: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEEQUB")
@external
def cgeequb(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ptr(Float32),
    COLCND: Ptr(Float32),
    AMAX: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEES")
@external
def cgees(
    JOBVS: Ptr(Const(String[1])),
    SORT: Ptr(Const(String[1])),
    SELECT: Ptr(Bool),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    SDIM: Ptr(Int32),
    W: Complex64[Flat],
    VS: Complex64[LDVS, Flat],
    LDVS: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEESX")
@external
def cgeesx(
    JOBVS: Ptr(Const(String[1])),
    SORT: Ptr(Const(String[1])),
    SELECT: Ptr(Bool),
    SENSE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    SDIM: Ptr(Int32),
    W: Complex64[Flat],
    VS: Complex64[LDVS, Flat],
    LDVS: Ptr(Int32),
    RCONDE: Ptr(Float32),
    RCONDV: Ptr(Float32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEEV")
@external
def cgeev(
    JOBVL: Ptr(Const(String[1])),
    JOBVR: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    W: Complex64[Flat],
    VL: Complex64[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEEVX")
@external
def cgeevx(
    BALANC: Ptr(Const(String[1])),
    JOBVL: Ptr(Const(String[1])),
    JOBVR: Ptr(Const(String[1])),
    SENSE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    W: Complex64[Flat],
    VL: Complex64[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    SCALE: Float32[Flat],
    ABNRM: Ptr(Float32),
    RCONDE: Float32[Flat],
    RCONDV: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEHD2")
@external
def cgehd2(
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEHRD")
@external
def cgehrd(
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEJSV")
@external
def cgejsv(
    JOBA: Ptr(Const(String[1])),
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    JOBR: Ptr(Const(String[1])),
    JOBT: Ptr(Const(String[1])),
    JOBP: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    SVA: Float32[N],
    U: Complex64[LDU, Flat],
    LDU: Ptr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ptr(Int32),
    CWORK: Complex64[LWORK],
    LWORK: Ptr(Int32),
    RWORK: Float32[LRWORK],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGELQ")
@external
def cgelq(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex64[Flat],
    TSIZE: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGELQ2")
@external
def cgelq2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGELQF")
@external
def cgelqf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGELQT")
@external
def cgelqt(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGELQT3")
@external
def cgelqt3(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGELS")
@external
def cgels(
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGELSD")
@external
def cgelsd(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    S: Float32[Flat],
    RCOND: Ptr(Float32),
    RANK: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGELSS")
@external
def cgelss(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    S: Float32[Flat],
    RCOND: Ptr(Float32),
    RANK: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGELST")
@external
def cgelst(
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGELSY")
@external
def cgelsy(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    JPVT: Int32[Flat],
    RCOND: Ptr(Float32),
    RANK: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEMLQ")
@external
def cgemlq(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex64[Flat],
    TSIZE: Ptr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEMLQT")
@external
def cgemlqt(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    MB: Ptr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEMQR")
@external
def cgemqr(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex64[Flat],
    TSIZE: Ptr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEMQRT")
@external
def cgemqrt(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    NB: Ptr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEQL2")
@external
def cgeql2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEQLF")
@external
def cgeqlf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEQP3")
@external
def cgeqp3(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    JPVT: Int32[Flat],
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEQP3RK")
@external
def cgeqp3rk(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    KMAX: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    RELTOL: Ptr(Float32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    K: Ptr(Int32),
    MAXC2NRMK: Ptr(Float32),
    RELMAXC2NRMK: Ptr(Float32),
    JPIV: Int32[Flat],
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEQR")
@external
def cgeqr(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex64[Flat],
    TSIZE: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEQR2")
@external
def cgeqr2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEQR2P")
@external
def cgeqr2p(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEQRF")
@external
def cgeqrf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEQRFP")
@external
def cgeqrfp(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEQRT")
@external
def cgeqrt(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEQRT2")
@external
def cgeqrt2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGEQRT3")
@external
def cgeqrt3(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGERFS")
@external
def cgerfs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGERFSX")
@external
def cgerfsx(
    TRANS: Ptr(Const(String[1])),
    EQUED: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    R: Float32[Flat],
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGERQ2")
@external
def cgerq2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGERQF")
@external
def cgerqf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGESC2")
@external
def cgesc2(
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    RHS: Complex64[Flat],
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    SCALE: Ptr(Float32)
) -> None: ...

@bind("CGESDD")
@external
def cgesdd(
    JOBZ: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float32[Flat],
    U: Complex64[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Complex64[LDVT, Flat],
    LDVT: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGESV")
@external
def cgesv(
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGESVD")
@external
def cgesvd(
    JOBU: Ptr(Const(String[1])),
    JOBVT: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float32[Flat],
    U: Complex64[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Complex64[LDVT, Flat],
    LDVT: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGESVDQ")
@external
def cgesvdq(
    JOBA: Ptr(Const(String[1])),
    JOBP: Ptr(Const(String[1])),
    JOBR: Ptr(Const(String[1])),
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float32[Flat],
    U: Complex64[LDU, Flat],
    LDU: Ptr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ptr(Int32),
    NUMRANK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    CWORK: Complex64[Flat],
    LCWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGESVDX")
@external
def cgesvdx(
    JOBU: Ptr(Const(String[1])),
    JOBVT: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    NS: Ptr(Int32),
    S: Float32[Flat],
    U: Complex64[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Complex64[LDVT, Flat],
    LDVT: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGESVJ")
@external
def cgesvj(
    JOBA: Ptr(Const(String[1])),
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    SVA: Float32[N],
    MV: Ptr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ptr(Int32),
    CWORK: Complex64[LWORK],
    LWORK: Ptr(Int32),
    RWORK: Float32[LRWORK],
    LRWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGESVX")
@external
def cgesvx(
    FACT: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    EQUED: Ptr(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGESVXX")
@external
def cgesvxx(
    FACT: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    EQUED: Ptr(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    RPVGRW: Ptr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGETC2")
@external
def cgetc2(
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGETF2")
@external
def cgetf2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGETRF")
@external
def cgetrf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGETRF2")
@external
def cgetrf2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGETRI")
@external
def cgetri(
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGETRS")
@external
def cgetrs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGETSLS")
@external
def cgetsls(
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGETSQRHRT")
@external
def cgetsqrhrt(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB1: Ptr(Int32),
    NB1: Ptr(Int32),
    NB2: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGGBAK")
@external
def cggbak(
    JOB: Ptr(Const(String[1])),
    SIDE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    LSCALE: Float32[Flat],
    RSCALE: Float32[Flat],
    M: Ptr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGGBAL")
@external
def cggbal(
    JOB: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    LSCALE: Float32[Flat],
    RSCALE: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGGES")
@external
def cgges(
    JOBVSL: Ptr(Const(String[1])),
    JOBVSR: Ptr(Const(String[1])),
    SORT: Ptr(Const(String[1])),
    SELCTG: Ptr(Bool),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    SDIM: Ptr(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    VSL: Complex64[LDVSL, Flat],
    LDVSL: Ptr(Int32),
    VSR: Complex64[LDVSR, Flat],
    LDVSR: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGGES3")
@external
def cgges3(
    JOBVSL: Ptr(Const(String[1])),
    JOBVSR: Ptr(Const(String[1])),
    SORT: Ptr(Const(String[1])),
    SELCTG: Ptr(Bool),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    SDIM: Ptr(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    VSL: Complex64[LDVSL, Flat],
    LDVSL: Ptr(Int32),
    VSR: Complex64[LDVSR, Flat],
    LDVSR: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGGESX")
@external
def cggesx(
    JOBVSL: Ptr(Const(String[1])),
    JOBVSR: Ptr(Const(String[1])),
    SORT: Ptr(Const(String[1])),
    SELCTG: Ptr(Bool),
    SENSE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    SDIM: Ptr(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    VSL: Complex64[LDVSL, Flat],
    LDVSL: Ptr(Int32),
    VSR: Complex64[LDVSR, Flat],
    LDVSR: Ptr(Int32),
    RCONDE: Float32[2],
    RCONDV: Float32[2],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGGEV")
@external
def cggev(
    JOBVL: Ptr(Const(String[1])),
    JOBVR: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    VL: Complex64[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGGEV3")
@external
def cggev3(
    JOBVL: Ptr(Const(String[1])),
    JOBVR: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    VL: Complex64[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGGEVX")
@external
def cggevx(
    BALANC: Ptr(Const(String[1])),
    JOBVL: Ptr(Const(String[1])),
    JOBVR: Ptr(Const(String[1])),
    SENSE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    VL: Complex64[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    LSCALE: Float32[Flat],
    RSCALE: Float32[Flat],
    ABNRM: Ptr(Float32),
    BBNRM: Ptr(Float32),
    RCONDE: Float32[Flat],
    RCONDV: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGGGLM")
@external
def cggglm(
    N: Ptr(Int32),
    M: Ptr(Int32),
    P: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    D: Complex64[Flat],
    X: Complex64[Flat],
    Y: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGGHD3")
@external
def cgghd3(
    COMPQ: Ptr(Const(String[1])),
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGGHRD")
@external
def cgghrd(
    COMPQ: Ptr(Const(String[1])),
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGGLSE")
@external
def cgglse(
    M: Ptr(Int32),
    N: Ptr(Int32),
    P: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    C: Complex64[Flat],
    D: Complex64[Flat],
    X: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGGQRF")
@external
def cggqrf(
    N: Ptr(Int32),
    M: Ptr(Int32),
    P: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAUA: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    TAUB: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGGRQF")
@external
def cggrqf(
    M: Ptr(Int32),
    P: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAUA: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    TAUB: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGGSVD3")
@external
def cggsvd3(
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    JOBQ: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    P: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    ALPHA: Float32[Flat],
    BETA: Float32[Flat],
    U: Complex64[LDU, Flat],
    LDU: Ptr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ptr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGGSVP3")
@external
def cggsvp3(
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    JOBQ: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    TOLA: Ptr(Float32),
    TOLB: Ptr(Float32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    U: Complex64[LDU, Flat],
    LDU: Ptr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ptr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Int32),
    IWORK: Int32[Flat],
    RWORK: Float32[Flat],
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGSVJ0")
@external
def cgsvj0(
    JOBV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    D: Complex64[N],
    SVA: Float32[N],
    MV: Ptr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ptr(Int32),
    EPS: Ptr(Float32),
    SFMIN: Ptr(Float32),
    TOL: Ptr(Float32),
    NSWEEP: Ptr(Int32),
    WORK: Complex64[LWORK],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGSVJ1")
@external
def cgsvj1(
    JOBV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    N1: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    D: Complex64[N],
    SVA: Float32[N],
    MV: Ptr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ptr(Int32),
    EPS: Ptr(Float32),
    SFMIN: Ptr(Float32),
    TOL: Ptr(Float32),
    NSWEEP: Ptr(Int32),
    WORK: Complex64[LWORK],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGTCON")
@external
def cgtcon(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    DU2: Complex64[Flat],
    IPIV: Int32[Flat],
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGTRFS")
@external
def cgtrfs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    DLF: Complex64[Flat],
    DF: Complex64[Flat],
    DUF: Complex64[Flat],
    DU2: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGTSV")
@external
def cgtsv(
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGTSVX")
@external
def cgtsvx(
    FACT: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    DLF: Complex64[Flat],
    DF: Complex64[Flat],
    DUF: Complex64[Flat],
    DU2: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGTTRF")
@external
def cgttrf(
    N: Ptr(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    DU2: Complex64[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGTTRS")
@external
def cgttrs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    DU2: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CGTTS2")
@external
def cgtts2(
    ITRANS: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    DU2: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("CHB2ST_KERNELS")
@external
def chb2st_kernels(
    UPLO: Ptr(Const(String[1])),
    WANTZ: Ptr(Bool),
    TTYPE: Ptr(Int32),
    ST: Ptr(Int32),
    ED: Ptr(Int32),
    SWEEP: Ptr(Int32),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    IB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    V: Complex64[Flat],
    TAU: Complex64[Flat],
    LDVT: Ptr(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CHBEV")
@external
def chbev(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHBEV_2STAGE")
@external
def chbev_2stage(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHBEVD")
@external
def chbevd(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHBEVD_2STAGE")
@external
def chbevd_2stage(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHBEVX")
@external
def chbevx(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHBEVX_2STAGE")
@external
def chbevx_2stage(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHBGST")
@external
def chbgst(
    VECT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KA: Ptr(Int32),
    KB: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    BB: Complex64[LDBB, Flat],
    LDBB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHBGV")
@external
def chbgv(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KA: Ptr(Int32),
    KB: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    BB: Complex64[LDBB, Flat],
    LDBB: Ptr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHBGVD")
@external
def chbgvd(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KA: Ptr(Int32),
    KB: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    BB: Complex64[LDBB, Flat],
    LDBB: Ptr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHBGVX")
@external
def chbgvx(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KA: Ptr(Int32),
    KB: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    BB: Complex64[LDBB, Flat],
    LDBB: Ptr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHBTRD")
@external
def chbtrd(
    VECT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Int32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHECON")
@external
def checon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHECON_3")
@external
def checon_3(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHECON_ROOK")
@external
def checon_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHEEQUB")
@external
def cheequb(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float32[Flat],
    SCOND: Ptr(Float32),
    AMAX: Ptr(Float32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHEEV")
@external
def cheev(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    W: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHEEV_2STAGE")
@external
def cheev_2stage(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    W: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHEEVD")
@external
def cheevd(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    W: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHEEVD_2STAGE")
@external
def cheevd_2stage(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    W: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHEEVR")
@external
def cheevr(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHEEVR_2STAGE")
@external
def cheevr_2stage(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHEEVX")
@external
def cheevx(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHEEVX_2STAGE")
@external
def cheevx_2stage(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHEGS2")
@external
def chegs2(
    ITYPE: Ptr(Int32),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHEGST")
@external
def chegst(
    ITYPE: Ptr(Int32),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHEGV")
@external
def chegv(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    W: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHEGV_2STAGE")
@external
def chegv_2stage(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    W: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHEGVD")
@external
def chegvd(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    W: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHEGVX")
@external
def chegvx(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHERFS")
@external
def cherfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHERFSX")
@external
def cherfsx(
    UPLO: Ptr(Const(String[1])),
    EQUED: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHESV")
@external
def chesv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHESV_AA")
@external
def chesv_aa(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHESV_AA_2STAGE")
@external
def chesv_aa_2stage(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TB: Complex64[Flat],
    LTB: Ptr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHESV_RK")
@external
def chesv_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHESV_ROOK")
@external
def chesv_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHESVX")
@external
def chesvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHESVXX")
@external
def chesvxx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    EQUED: Ptr(Const(String[1])),
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    RPVGRW: Ptr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHESWAPR")
@external
def cheswapr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Complex64[LDA, N], ORDER_F],
    LDA: Ptr(Int32),
    I1: Ptr(Int32),
    I2: Ptr(Int32)
) -> None: ...

@bind("CHETD2")
@external
def chetd2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETF2")
@external
def chetf2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETF2_RK")
@external
def chetf2_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETF2_ROOK")
@external
def chetf2_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETRD")
@external
def chetrd(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETRD_2STAGE")
@external
def chetrd_2stage(
    VECT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Complex64[Flat],
    HOUS2: Complex64[Flat],
    LHOUS2: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETRD_HB2ST")
@external
def chetrd_hb2st(
    STAGE1: Ptr(Const(String[1])),
    VECT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    HOUS: Complex64[Flat],
    LHOUS: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETRD_HE2HB")
@external
def chetrd_he2hb(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETRF")
@external
def chetrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETRF_AA")
@external
def chetrf_aa(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETRF_AA_2STAGE")
@external
def chetrf_aa_2stage(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TB: Complex64[Flat],
    LTB: Ptr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETRF_RK")
@external
def chetrf_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETRF_ROOK")
@external
def chetrf_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETRI")
@external
def chetri(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETRI2")
@external
def chetri2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETRI2X")
@external
def chetri2x(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[N + NB + 1, Flat],
    NB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETRI_3")
@external
def chetri_3(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETRI_3X")
@external
def chetri_3x(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[N + NB + 1, Flat],
    NB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETRI_ROOK")
@external
def chetri_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETRS")
@external
def chetrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETRS2")
@external
def chetrs2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETRS_3")
@external
def chetrs_3(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETRS_AA")
@external
def chetrs_aa(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETRS_AA_2STAGE")
@external
def chetrs_aa_2stage(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TB: Complex64[Flat],
    LTB: Ptr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHETRS_ROOK")
@external
def chetrs_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHFRK")
@external
def chfrk(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Float32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    BETA: Ptr(Float32),
    C: Complex64[Flat]
) -> None: ...

@bind("CHGEQZ")
@external
def chgeqz(
    JOB: Ptr(Const(String[1])),
    COMPQ: Ptr(Const(String[1])),
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    H: Complex64[LDH, Flat],
    LDH: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHLA_TRANSTYPE")
@external
def chla_transtype(
    TRANS: Ptr(Int32)
) -> String[1]: ...

@bind("CHPCON")
@external
def chpcon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHPEV")
@external
def chpev(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHPEVD")
@external
def chpevd(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHPEVX")
@external
def chpevx(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHPGST")
@external
def chpgst(
    ITYPE: Ptr(Int32),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    BP: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHPGV")
@external
def chpgv(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    BP: Complex64[Flat],
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHPGVD")
@external
def chpgvd(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    BP: Complex64[Flat],
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHPGVX")
@external
def chpgvx(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    BP: Complex64[Flat],
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHPRFS")
@external
def chprfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex64[Flat],
    AFP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHPSV")
@external
def chpsv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHPSVX")
@external
def chpsvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex64[Flat],
    AFP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHPTRD")
@external
def chptrd(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHPTRF")
@external
def chptrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHPTRI")
@external
def chptri(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHPTRS")
@external
def chptrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHSEIN")
@external
def chsein(
    SIDE: Ptr(Const(String[1])),
    EIGSRC: Ptr(Const(String[1])),
    INITV: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    H: Complex64[LDH, Flat],
    LDH: Ptr(Int32),
    W: Complex64[Flat],
    VL: Complex64[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Ptr(Int32),
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    IFAILL: Int32[Flat],
    IFAILR: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CHSEQR")
@external
def chseqr(
    JOB: Ptr(Const(String[1])),
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    H: Complex64[LDH, Flat],
    LDH: Ptr(Int32),
    W: Complex64[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLA_GBAMV")
@external
def cla_gbamv(
    TRANS: Ptr(Int32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    ALPHA: Ptr(Float32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    X: Complex64[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Float32),
    Y: Float32[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("CLA_GBRCOND_C")
@external
def cla_gbrcond_c(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    C: Float32[Flat],
    CAPPLY: Ptr(Bool),
    INFO: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_GBRCOND_X")
@external
def cla_gbrcond_x(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    X: Complex64[Flat],
    INFO: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_GBRFSX_EXTENDED")
@external
def cla_gbrfsx_extended(
    PREC_TYPE: Ptr(Int32),
    TRANS_TYPE: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ptr(Bool),
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    Y: Complex64[LDY, Flat],
    LDY: Ptr(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    RES: Complex64[Flat],
    AYB: Float32[Flat],
    DY: Complex64[Flat],
    Y_TAIL: Complex64[Flat],
    RCOND: Ptr(Float32),
    ITHRESH: Ptr(Int32),
    RTHRESH: Ptr(Float32),
    DZ_UB: Ptr(Float32),
    IGNORE_CWISE: Ptr(Bool),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLA_GBRPVGRW")
@external
def cla_gbrpvgrw(
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NCOLS: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Ptr(Int32)
) -> Float32: ...

@bind("CLA_GEAMV")
@external
def cla_geamv(
    TRANS: Ptr(Int32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Float32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex64[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Float32),
    Y: Float32[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("CLA_GERCOND_C")
@external
def cla_gercond_c(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    C: Float32[Flat],
    CAPPLY: Ptr(Bool),
    INFO: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_GERCOND_X")
@external
def cla_gercond_x(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    X: Complex64[Flat],
    INFO: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_GERFSX_EXTENDED")
@external
def cla_gerfsx_extended(
    PREC_TYPE: Ptr(Int32),
    TRANS_TYPE: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ptr(Bool),
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    Y: Complex64[LDY, Flat],
    LDY: Ptr(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Ptr(Int32),
    ERRS_N: Float32[NRHS, Flat],
    ERRS_C: Float32[NRHS, Flat],
    RES: Complex64[Flat],
    AYB: Float32[Flat],
    DY: Complex64[Flat],
    Y_TAIL: Complex64[Flat],
    RCOND: Ptr(Float32),
    ITHRESH: Ptr(Int32),
    RTHRESH: Ptr(Float32),
    DZ_UB: Ptr(Float32),
    IGNORE_CWISE: Ptr(Bool),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLA_GERPVGRW")
@external
def cla_gerpvgrw(
    N: Ptr(Int32),
    NCOLS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32)
) -> Float32: ...

@bind("CLA_HEAMV")
@external
def cla_heamv(
    UPLO: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Float32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex64[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Float32),
    Y: Float32[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("CLA_HERCOND_C")
@external
def cla_hercond_c(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    C: Float32[Flat],
    CAPPLY: Ptr(Bool),
    INFO: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_HERCOND_X")
@external
def cla_hercond_x(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    X: Complex64[Flat],
    INFO: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_HERFSX_EXTENDED")
@external
def cla_herfsx_extended(
    PREC_TYPE: Ptr(Int32),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ptr(Bool),
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    Y: Complex64[LDY, Flat],
    LDY: Ptr(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    RES: Complex64[Flat],
    AYB: Float32[Flat],
    DY: Complex64[Flat],
    Y_TAIL: Complex64[Flat],
    RCOND: Ptr(Float32),
    ITHRESH: Ptr(Int32),
    RTHRESH: Ptr(Float32),
    DZ_UB: Ptr(Float32),
    IGNORE_CWISE: Ptr(Bool),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLA_HERPVGRW")
@external
def cla_herpvgrw(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    INFO: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_LIN_BERR")
@external
def cla_lin_berr(
    N: Ptr(Int32),
    NZ: Ptr(Int32),
    NRHS: Ptr(Int32),
    RES: Annotated[Complex64[N, NRHS], ORDER_F],
    AYB: Annotated[Float32[N, NRHS], ORDER_F],
    BERR: Float32[NRHS]
) -> None: ...

@bind("CLA_PORCOND_C")
@external
def cla_porcond_c(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    C: Float32[Flat],
    CAPPLY: Ptr(Bool),
    INFO: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_PORCOND_X")
@external
def cla_porcond_x(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    X: Complex64[Flat],
    INFO: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_PORFSX_EXTENDED")
@external
def cla_porfsx_extended(
    PREC_TYPE: Ptr(Int32),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    COLEQU: Ptr(Bool),
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    Y: Complex64[LDY, Flat],
    LDY: Ptr(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    RES: Complex64[Flat],
    AYB: Float32[Flat],
    DY: Complex64[Flat],
    Y_TAIL: Complex64[Flat],
    RCOND: Ptr(Float32),
    ITHRESH: Ptr(Int32),
    RTHRESH: Ptr(Float32),
    DZ_UB: Ptr(Float32),
    IGNORE_CWISE: Ptr(Bool),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLA_PORPVGRW")
@external
def cla_porpvgrw(
    UPLO: Ptr(Const(String[1])),
    NCOLS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_SYAMV")
@external
def cla_syamv(
    UPLO: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Float32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex64[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Float32),
    Y: Float32[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("CLA_SYRCOND_C")
@external
def cla_syrcond_c(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    C: Float32[Flat],
    CAPPLY: Ptr(Bool),
    INFO: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_SYRCOND_X")
@external
def cla_syrcond_x(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    X: Complex64[Flat],
    INFO: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_SYRFSX_EXTENDED")
@external
def cla_syrfsx_extended(
    PREC_TYPE: Ptr(Int32),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ptr(Bool),
    C: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    Y: Complex64[LDY, Flat],
    LDY: Ptr(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    RES: Complex64[Flat],
    AYB: Float32[Flat],
    DY: Complex64[Flat],
    Y_TAIL: Complex64[Flat],
    RCOND: Ptr(Float32),
    ITHRESH: Ptr(Int32),
    RTHRESH: Ptr(Float32),
    DZ_UB: Ptr(Float32),
    IGNORE_CWISE: Ptr(Bool),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLA_SYRPVGRW")
@external
def cla_syrpvgrw(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    INFO: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLA_WWADDW")
@external
def cla_wwaddw(
    N: Ptr(Int32),
    X: Complex64[Flat],
    Y: Complex64[Flat],
    W: Complex64[Flat]
) -> None: ...

@bind("CLABRD")
@external
def clabrd(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAUQ: Complex64[Flat],
    TAUP: Complex64[Flat],
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    Y: Complex64[LDY, Flat],
    LDY: Ptr(Int32)
) -> None: ...

@bind("CLACGV")
@external
def clacgv(
    N: Ptr(Int32),
    X: Complex64[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("CLACN2")
@external
def clacn2(
    N: Ptr(Int32),
    V: Complex64[Flat],
    X: Complex64[Flat],
    EST: Ptr(Float32),
    KASE: Ptr(Int32),
    ISAVE: Int32[3]
) -> None: ...

@bind("CLACON")
@external
def clacon(
    N: Ptr(Int32),
    V: Complex64[N],
    X: Complex64[N],
    EST: Ptr(Float32),
    KASE: Ptr(Int32)
) -> None: ...

@bind("CLACP2")
@external
def clacp2(
    UPLO: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("CLACPY")
@external
def clacpy(
    UPLO: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("CLACRM")
@external
def clacrm(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    RWORK: Float32[Flat]
) -> None: ...

@bind("CLACRT")
@external
def clacrt(
    N: Ptr(Int32),
    CX: Complex64[Flat],
    INCX: Ptr(Int32),
    CY: Complex64[Flat],
    INCY: Ptr(Int32),
    C: Ptr(Complex64),
    S: Ptr(Complex64)
) -> None: ...

@bind("CLADIV")
@external
def cladiv(
    X: Ptr(Complex64),
    Y: Ptr(Complex64)
) -> Complex64: ...

@bind("CLAED0")
@external
def claed0(
    QSIZ: Ptr(Int32),
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Int32),
    QSTORE: Complex64[LDQS, Flat],
    LDQS: Ptr(Int32),
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLAED7")
@external
def claed7(
    N: Ptr(Int32),
    CUTPNT: Ptr(Int32),
    QSIZ: Ptr(Int32),
    TLVLS: Ptr(Int32),
    CURLVL: Ptr(Int32),
    CURPBM: Ptr(Int32),
    D: Float32[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Int32),
    RHO: Ptr(Float32),
    INDXQ: Int32[Flat],
    QSTORE: Float32[Flat],
    QPTR: Int32[Flat],
    PRMPTR: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float32[2, Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLAED8")
@external
def claed8(
    K: Ptr(Int32),
    N: Ptr(Int32),
    QSIZ: Ptr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Int32),
    D: Float32[Flat],
    RHO: Ptr(Float32),
    CUTPNT: Ptr(Int32),
    Z: Float32[Flat],
    DLAMBDA: Float32[Flat],
    Q2: Complex64[LDQ2, Flat],
    LDQ2: Ptr(Int32),
    W: Float32[Flat],
    INDXP: Int32[Flat],
    INDX: Int32[Flat],
    INDXQ: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Ptr(Int32),
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float32[2, Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLAEIN")
@external
def claein(
    RIGHTV: Ptr(Bool),
    NOINIT: Ptr(Bool),
    N: Ptr(Int32),
    H: Complex64[LDH, Flat],
    LDH: Ptr(Int32),
    W: Ptr(Complex64),
    V: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    RWORK: Float32[Flat],
    EPS3: Ptr(Float32),
    SMLNUM: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLAESY")
@external
def claesy(
    A: Ptr(Complex64),
    B: Ptr(Complex64),
    C: Ptr(Complex64),
    RT1: Ptr(Complex64),
    RT2: Ptr(Complex64),
    EVSCAL: Ptr(Complex64),
    CS1: Ptr(Complex64),
    SN1: Ptr(Complex64)
) -> None: ...

@bind("CLAEV2")
@external
def claev2(
    A: Ptr(Complex64),
    B: Ptr(Complex64),
    C: Ptr(Complex64),
    RT1: Ptr(Float32),
    RT2: Ptr(Float32),
    CS1: Ptr(Float32),
    SN1: Ptr(Complex64)
) -> None: ...

@bind("CLAG2Z")
@external
def clag2z(
    M: Ptr(Int32),
    N: Ptr(Int32),
    SA: Complex64[LDSA, Flat],
    LDSA: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLAGS2")
@external
def clags2(
    UPPER: Ptr(Bool),
    A1: Ptr(Float32),
    A2: Ptr(Complex64),
    A3: Ptr(Float32),
    B1: Ptr(Float32),
    B2: Ptr(Complex64),
    B3: Ptr(Float32),
    CSU: Ptr(Float32),
    SNU: Ptr(Complex64),
    CSV: Ptr(Float32),
    SNV: Ptr(Complex64),
    CSQ: Ptr(Float32),
    SNQ: Ptr(Complex64)
) -> None: ...

@bind("CLAGTM")
@external
def clagtm(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    ALPHA: Ptr(Float32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat],
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    BETA: Ptr(Float32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("CLAHEF")
@external
def clahef(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    KB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    W: Complex64[LDW, Flat],
    LDW: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLAHEF_AA")
@external
def clahef_aa(
    UPLO: Ptr(Const(String[1])),
    J1: Ptr(Int32),
    M: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    H: Complex64[LDH, Flat],
    LDH: Ptr(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLAHEF_RK")
@external
def clahef_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    KB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    W: Complex64[LDW, Flat],
    LDW: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLAHEF_ROOK")
@external
def clahef_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    KB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    W: Complex64[LDW, Flat],
    LDW: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLAHQR")
@external
def clahqr(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    H: Complex64[LDH, Flat],
    LDH: Ptr(Int32),
    W: Complex64[Flat],
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLAHR2")
@external
def clahr2(
    N: Ptr(Int32),
    K: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[NB],
    T: Annotated[Complex64[LDT, NB], ORDER_F],
    LDT: Ptr(Int32),
    Y: Annotated[Complex64[LDY, NB], ORDER_F],
    LDY: Ptr(Int32)
) -> None: ...

@bind("CLAIC1")
@external
def claic1(
    JOB: Ptr(Int32),
    J: Ptr(Int32),
    X: Complex64[J],
    SEST: Ptr(Float32),
    W: Complex64[J],
    GAMMA: Ptr(Complex64),
    SESTPR: Ptr(Float32),
    S: Ptr(Complex64),
    C: Ptr(Complex64)
) -> None: ...

@bind("CLALS0")
@external
def clals0(
    ICOMPQ: Ptr(Int32),
    NL: Ptr(Int32),
    NR: Ptr(Int32),
    SQRE: Ptr(Int32),
    NRHS: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    BX: Complex64[LDBX, Flat],
    LDBX: Ptr(Int32),
    PERM: Int32[Flat],
    GIVPTR: Ptr(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ptr(Int32),
    GIVNUM: Float32[LDGNUM, Flat],
    LDGNUM: Ptr(Int32),
    POLES: Float32[LDGNUM, Flat],
    DIFL: Float32[Flat],
    DIFR: Float32[LDGNUM, Flat],
    Z: Float32[Flat],
    K: Ptr(Int32),
    C: Ptr(Float32),
    S: Ptr(Float32),
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLALSA")
@external
def clalsa(
    ICOMPQ: Ptr(Int32),
    SMLSIZ: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    BX: Complex64[LDBX, Flat],
    LDBX: Ptr(Int32),
    U: Float32[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Float32[LDU, Flat],
    K: Int32[Flat],
    DIFL: Float32[LDU, Flat],
    DIFR: Float32[LDU, Flat],
    Z: Float32[LDU, Flat],
    POLES: Float32[LDU, Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ptr(Int32),
    PERM: Int32[LDGCOL, Flat],
    GIVNUM: Float32[LDU, Flat],
    C: Float32[Flat],
    S: Float32[Flat],
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLALSD")
@external
def clalsd(
    UPLO: Ptr(Const(String[1])),
    SMLSIZ: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    RCOND: Ptr(Float32),
    RANK: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLAMSWLQ")
@external
def clamswlq(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLAMTSQR")
@external
def clamtsqr(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLANGB")
@external
def clangb(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANGE")
@external
def clange(
    NORM: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANGT")
@external
def clangt(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    DL: Complex64[Flat],
    D: Complex64[Flat],
    DU: Complex64[Flat]
) -> Float32: ...

@bind("CLANHB")
@external
def clanhb(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANHE")
@external
def clanhe(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANHF")
@external
def clanhf(
    NORM: Ptr(Const(String[1])),
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Complex64[Flat], SourceDims("0:*")],
    WORK: Annotated[Float32[Flat], SourceDims("0:*")]
) -> Float32: ...

@bind("CLANHP")
@external
def clanhp(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANHS")
@external
def clanhs(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANHT")
@external
def clanht(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Complex64[Flat]
) -> Float32: ...

@bind("CLANSB")
@external
def clansb(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANSP")
@external
def clansp(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANSY")
@external
def clansy(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANTB")
@external
def clantb(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANTP")
@external
def clantp(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLANTR")
@external
def clantr(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("CLAPLL")
@external
def clapll(
    N: Ptr(Int32),
    X: Complex64[Flat],
    INCX: Ptr(Int32),
    Y: Complex64[Flat],
    INCY: Ptr(Int32),
    SSMIN: Ptr(Float32)
) -> None: ...

@bind("CLAPMR")
@external
def clapmr(
    FORWRD: Ptr(Bool),
    M: Ptr(Int32),
    N: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("CLAPMT")
@external
def clapmt(
    FORWRD: Ptr(Bool),
    M: Ptr(Int32),
    N: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("CLAQGB")
@external
def claqgb(
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ptr(Float32),
    COLCND: Ptr(Float32),
    AMAX: Ptr(Float32),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("CLAQGE")
@external
def claqge(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ptr(Float32),
    COLCND: Ptr(Float32),
    AMAX: Ptr(Float32),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("CLAQHB")
@external
def claqhb(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    S: Float32[Flat],
    SCOND: Ptr(Float32),
    AMAX: Ptr(Float32),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("CLAQHE")
@external
def claqhe(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float32[Flat],
    SCOND: Ptr(Float32),
    AMAX: Ptr(Float32),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("CLAQHP")
@external
def claqhp(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    S: Float32[Flat],
    SCOND: Ptr(Float32),
    AMAX: Ptr(Float32),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("CLAQP2")
@external
def claqp2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    OFFSET: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    JPVT: Int32[Flat],
    TAU: Complex64[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLAQP2RK")
@external
def claqp2rk(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    IOFFSET: Ptr(Int32),
    KMAX: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    RELTOL: Ptr(Float32),
    KP1: Ptr(Int32),
    MAXC2NRM: Ptr(Float32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    K: Ptr(Int32),
    MAXC2NRMK: Ptr(Float32),
    RELMAXC2NRMK: Ptr(Float32),
    JPIV: Int32[Flat],
    TAU: Complex64[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLAQP3RK")
@external
def claqp3rk(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    IOFFSET: Ptr(Int32),
    NB: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    RELTOL: Ptr(Float32),
    KP1: Ptr(Int32),
    MAXC2NRM: Ptr(Float32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    DONE: Ptr(Bool),
    KB: Ptr(Int32),
    MAXC2NRMK: Ptr(Float32),
    RELMAXC2NRMK: Ptr(Float32),
    JPIV: Int32[Flat],
    TAU: Complex64[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    AUXV: Complex64[Flat],
    F: Complex64[LDF, Flat],
    LDF: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLAQPS")
@external
def claqps(
    M: Ptr(Int32),
    N: Ptr(Int32),
    OFFSET: Ptr(Int32),
    NB: Ptr(Int32),
    KB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    JPVT: Int32[Flat],
    TAU: Complex64[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    AUXV: Complex64[Flat],
    F: Complex64[LDF, Flat],
    LDF: Ptr(Int32)
) -> None: ...

@bind("CLAQR0")
@external
def claqr0(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    H: Complex64[LDH, Flat],
    LDH: Ptr(Int32),
    W: Complex64[Flat],
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLAQR1")
@external
def claqr1(
    N: Ptr(Int32),
    H: Complex64[LDH, Flat],
    LDH: Ptr(Int32),
    S1: Ptr(Complex64),
    S2: Ptr(Complex64),
    V: Complex64[Flat]
) -> None: ...

@bind("CLAQR2")
@external
def claqr2(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    KTOP: Ptr(Int32),
    KBOT: Ptr(Int32),
    NW: Ptr(Int32),
    H: Complex64[LDH, Flat],
    LDH: Ptr(Int32),
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    NS: Ptr(Int32),
    ND: Ptr(Int32),
    SH: Complex64[Flat],
    V: Complex64[LDV, Flat],
    LDV: Ptr(Int32),
    NH: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    NV: Ptr(Int32),
    WV: Complex64[LDWV, Flat],
    LDWV: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32)
) -> None: ...

@bind("CLAQR3")
@external
def claqr3(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    KTOP: Ptr(Int32),
    KBOT: Ptr(Int32),
    NW: Ptr(Int32),
    H: Complex64[LDH, Flat],
    LDH: Ptr(Int32),
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    NS: Ptr(Int32),
    ND: Ptr(Int32),
    SH: Complex64[Flat],
    V: Complex64[LDV, Flat],
    LDV: Ptr(Int32),
    NH: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    NV: Ptr(Int32),
    WV: Complex64[LDWV, Flat],
    LDWV: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32)
) -> None: ...

@bind("CLAQR4")
@external
def claqr4(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    H: Complex64[LDH, Flat],
    LDH: Ptr(Int32),
    W: Complex64[Flat],
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLAQR5")
@external
def claqr5(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    KACC22: Ptr(Int32),
    N: Ptr(Int32),
    KTOP: Ptr(Int32),
    KBOT: Ptr(Int32),
    NSHFTS: Ptr(Int32),
    S: Complex64[Flat],
    H: Complex64[LDH, Flat],
    LDH: Ptr(Int32),
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ptr(Int32),
    U: Complex64[LDU, Flat],
    LDU: Ptr(Int32),
    NV: Ptr(Int32),
    WV: Complex64[LDWV, Flat],
    LDWV: Ptr(Int32),
    NH: Ptr(Int32),
    WH: Complex64[LDWH, Flat],
    LDWH: Ptr(Int32)
) -> None: ...

@bind("CLAQSB")
@external
def claqsb(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    S: Float32[Flat],
    SCOND: Ptr(Float32),
    AMAX: Ptr(Float32),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("CLAQSP")
@external
def claqsp(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    S: Float32[Flat],
    SCOND: Ptr(Float32),
    AMAX: Ptr(Float32),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("CLAQSY")
@external
def claqsy(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float32[Flat],
    SCOND: Ptr(Float32),
    AMAX: Ptr(Float32),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("CLAQZ0")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7), Arg(8), Arg(9), Arg(10), Arg(11), Arg(12), Arg(13), Arg(14), Arg(15), Arg(16), Arg(17), Arg(18), Arg(19), Return('INFO', 1)])
def claqz0(
    WANTS: Ptr(Const(String[1])),
    WANTQ: Ptr(Const(String[1])),
    WANTZ: Ptr(Const(String[1])),
    N: Ptr(Const(Int32)),
    ILO: Ptr(Const(Int32)),
    IHI: Ptr(Const(Int32)),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Const(Int32)),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Const(Int32)),
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Const(Int32)),
    WORK: Complex64[Flat],
    LWORK: Ptr(Const(Int32)),
    RWORK: Float32[Flat],
    REC: Ptr(Const(Int32))
) -> tuple[Returns["RWORK", Float32[Flat]], Int32]: ...

@bind("CLAQZ1")
@external
def claqz1(
    ILQ: Ptr(Const(Bool)),
    ILZ: Ptr(Const(Bool)),
    K: Ptr(Const(Int32)),
    ISTARTM: Ptr(Const(Int32)),
    ISTOPM: Ptr(Const(Int32)),
    IHI: Ptr(Const(Int32)),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Const(Int32)),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    NQ: Ptr(Const(Int32)),
    QSTART: Ptr(Const(Int32)),
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Const(Int32)),
    NZ: Ptr(Const(Int32)),
    ZSTART: Ptr(Const(Int32)),
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Const(Int32))
) -> None: ...

@bind("CLAQZ2")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7), Arg(8), Arg(9), Arg(10), Arg(11), Arg(12), Arg(13), Arg(14), Return('NS', 0), Return('ND', 1), Arg(15), Arg(16), Arg(17), Arg(18), Arg(19), Arg(20), Arg(21), Arg(22), Arg(23), Arg(24), Return('INFO', 2)])
def claqz2(
    ILSCHUR: Ptr(Const(Bool)),
    ILQ: Ptr(Const(Bool)),
    ILZ: Ptr(Const(Bool)),
    N: Ptr(Const(Int32)),
    ILO: Ptr(Const(Int32)),
    IHI: Ptr(Const(Int32)),
    NW: Ptr(Const(Int32)),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Const(Int32)),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Const(Int32)),
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Const(Int32)),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    QC: Complex64[LDQC, Flat],
    LDQC: Ptr(Const(Int32)),
    ZC: Complex64[LDZC, Flat],
    LDZC: Ptr(Const(Int32)),
    WORK: Complex64[Flat],
    LWORK: Ptr(Const(Int32)),
    RWORK: Float32[Flat],
    REC: Ptr(Const(Int32))
) -> tuple[Int32, Int32, Int32]: ...

@bind("CLAQZ3")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7), Arg(8), Arg(9), Arg(10), Arg(11), Arg(12), Arg(13), Arg(14), Arg(15), Arg(16), Arg(17), Arg(18), Arg(19), Arg(20), Arg(21), Arg(22), Arg(23), Return('INFO', 0)])
def claqz3(
    ILSCHUR: Ptr(Const(Bool)),
    ILQ: Ptr(Const(Bool)),
    ILZ: Ptr(Const(Bool)),
    N: Ptr(Const(Int32)),
    ILO: Ptr(Const(Int32)),
    IHI: Ptr(Const(Int32)),
    NSHIFTS: Ptr(Const(Int32)),
    NBLOCK_DESIRED: Ptr(Const(Int32)),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    A: Complex64[LDA, Flat],
    LDA: Ptr(Const(Int32)),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Const(Int32)),
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Const(Int32)),
    QC: Complex64[LDQC, Flat],
    LDQC: Ptr(Const(Int32)),
    ZC: Complex64[LDZC, Flat],
    LDZC: Ptr(Const(Int32)),
    WORK: Complex64[Flat],
    LWORK: Ptr(Const(Int32))
) -> Int32: ...

@bind("CLAR1V")
@external
def clar1v(
    N: Ptr(Int32),
    B1: Ptr(Int32),
    BN: Ptr(Int32),
    LAMBDA: Ptr(Float32),
    D: Float32[Flat],
    L: Float32[Flat],
    LD: Float32[Flat],
    LLD: Float32[Flat],
    PIVMIN: Ptr(Float32),
    GAPTOL: Ptr(Float32),
    Z: Complex64[Flat],
    WANTNC: Ptr(Bool),
    NEGCNT: Ptr(Int32),
    ZTZ: Ptr(Float32),
    MINGMA: Ptr(Float32),
    R: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    NRMINV: Ptr(Float32),
    RESID: Ptr(Float32),
    RQCORR: Ptr(Float32),
    WORK: Float32[Flat]
) -> None: ...

@bind("CLAR2V")
@external
def clar2v(
    N: Ptr(Int32),
    X: Complex64[Flat],
    Y: Complex64[Flat],
    Z: Complex64[Flat],
    INCX: Ptr(Int32),
    C: Float32[Flat],
    S: Complex64[Flat],
    INCC: Ptr(Int32)
) -> None: ...

@bind("CLARCM")
@external
def clarcm(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    RWORK: Float32[Flat]
) -> None: ...

@bind("CLARF")
@external
def clarf(
    SIDE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    V: Complex64[Flat],
    INCV: Ptr(Int32),
    TAU: Ptr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLARF1F")
@external
def clarf1f(
    SIDE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    V: Complex64[Flat],
    INCV: Ptr(Int32),
    TAU: Ptr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLARF1L")
@external
def clarf1l(
    SIDE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    V: Complex64[Flat],
    INCV: Ptr(Int32),
    TAU: Ptr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLARFB")
@external
def clarfb(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIRECT: Ptr(Const(String[1])),
    STOREV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[LDWORK, Flat],
    LDWORK: Ptr(Int32)
) -> None: ...

@bind("CLARFB_GETT")
@external
def clarfb_gett(
    IDENT: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex64[LDWORK, Flat],
    LDWORK: Ptr(Int32)
) -> None: ...

@bind("CLARFG")
@external
def clarfg(
    N: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    X: Complex64[Flat],
    INCX: Ptr(Int32),
    TAU: Ptr(Complex64)
) -> None: ...

@bind("CLARFGP")
@external
def clarfgp(
    N: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    X: Complex64[Flat],
    INCX: Ptr(Int32),
    TAU: Ptr(Complex64)
) -> None: ...

@bind("CLARFT")
@external
def clarft(
    DIRECT: Ptr(Const(String[1])),
    STOREV: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ptr(Int32),
    TAU: Complex64[Flat],
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32)
) -> None: ...

@bind("CLARFX")
@external
def clarfx(
    SIDE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    V: Complex64[Flat],
    TAU: Ptr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLARFY")
@external
def clarfy(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    V: Complex64[Flat],
    INCV: Ptr(Int32),
    TAU: Ptr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLARGV")
@external
def clargv(
    N: Ptr(Int32),
    X: Complex64[Flat],
    INCX: Ptr(Int32),
    Y: Complex64[Flat],
    INCY: Ptr(Int32),
    C: Float32[Flat],
    INCC: Ptr(Int32)
) -> None: ...

@bind("CLARNV")
@external
def clarnv(
    IDIST: Ptr(Int32),
    ISEED: Int32[4],
    N: Ptr(Int32),
    X: Complex64[Flat]
) -> None: ...

@bind("CLARRV")
@external
def clarrv(
    N: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    D: Float32[Flat],
    L: Float32[Flat],
    PIVMIN: Ptr(Float32),
    ISPLIT: Int32[Flat],
    M: Ptr(Int32),
    DOL: Ptr(Int32),
    DOU: Ptr(Int32),
    MINRGP: Ptr(Float32),
    RTOL1: Ptr(Float32),
    RTOL2: Ptr(Float32),
    W: Float32[Flat],
    WERR: Float32[Flat],
    WGAP: Float32[Flat],
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    GERS: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLARSCL2")
@external
def clarscl2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    D: Float32[Flat],
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32)
) -> None: ...

@bind("CLARTG")
@external
def clartg(
    f: Ptr(Complex64),
    g: Ptr(Complex64),
    c: Ptr(Float32),
    s: Ptr(Complex64),
    r: Ptr(Complex64)
) -> None: ...

@bind("CLARTV")
@external
def clartv(
    N: Ptr(Int32),
    X: Complex64[Flat],
    INCX: Ptr(Int32),
    Y: Complex64[Flat],
    INCY: Ptr(Int32),
    C: Float32[Flat],
    S: Complex64[Flat],
    INCC: Ptr(Int32)
) -> None: ...

@bind("CLARZ")
@external
def clarz(
    SIDE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    V: Complex64[Flat],
    INCV: Ptr(Int32),
    TAU: Ptr(Complex64),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLARZB")
@external
def clarzb(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIRECT: Ptr(Const(String[1])),
    STOREV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[LDWORK, Flat],
    LDWORK: Ptr(Int32)
) -> None: ...

@bind("CLARZT")
@external
def clarzt(
    DIRECT: Ptr(Const(String[1])),
    STOREV: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ptr(Int32),
    TAU: Complex64[Flat],
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32)
) -> None: ...

@bind("CLASCL")
@external
def clascl(
    TYPE: Ptr(Const(String[1])),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    CFROM: Ptr(Float32),
    CTO: Ptr(Float32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLASCL2")
@external
def clascl2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    D: Float32[Flat],
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32)
) -> None: ...

@bind("CLASET")
@external
def claset(
    UPLO: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    BETA: Ptr(Complex64),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("CLASR")
@external
def clasr(
    SIDE: Ptr(Const(String[1])),
    PIVOT: Ptr(Const(String[1])),
    DIRECT: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    C: Float32[Flat],
    S: Float32[Flat],
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("CLASSQ")
@external
def classq(
    n: Ptr(Int32),
    x: Complex64[Flat],
    incx: Ptr(Int32),
    scale: Ptr(Float32),
    sumsq: Ptr(Float32)
) -> None: ...

@bind("CLASWLQ")
@external
def claswlq(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLASWP")
@external
def claswp(
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    K1: Ptr(Int32),
    K2: Ptr(Int32),
    IPIV: Int32[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("CLASYF")
@external
def clasyf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    KB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    W: Complex64[LDW, Flat],
    LDW: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLASYF_AA")
@external
def clasyf_aa(
    UPLO: Ptr(Const(String[1])),
    J1: Ptr(Int32),
    M: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    H: Complex64[LDH, Flat],
    LDH: Ptr(Int32),
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLASYF_RK")
@external
def clasyf_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    KB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    W: Complex64[LDW, Flat],
    LDW: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLASYF_ROOK")
@external
def clasyf_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    KB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    W: Complex64[LDW, Flat],
    LDW: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLATBS")
@external
def clatbs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    NORMIN: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    X: Complex64[Flat],
    SCALE: Ptr(Float32),
    CNORM: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLATDF")
@external
def clatdf(
    IJOB: Ptr(Int32),
    N: Ptr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    RHS: Complex64[Flat],
    RDSUM: Ptr(Float32),
    RDSCAL: Ptr(Float32),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat]
) -> None: ...

@bind("CLATPS")
@external
def clatps(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    NORMIN: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    X: Complex64[Flat],
    SCALE: Ptr(Float32),
    CNORM: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLATRD")
@external
def clatrd(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float32[Flat],
    TAU: Complex64[Flat],
    W: Complex64[LDW, Flat],
    LDW: Ptr(Int32)
) -> None: ...

@bind("CLATRS")
@external
def clatrs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    NORMIN: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex64[Flat],
    SCALE: Ptr(Float32),
    CNORM: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLATRS3")
@external
def clatrs3(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    NORMIN: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    SCALE: Float32[Flat],
    CNORM: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLATRZ")
@external
def clatrz(
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat]
) -> None: ...

@bind("CLATSQR")
@external
def clatsqr(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLAUNHR_COL_GETRFNP")
@external
def claunhr_col_getrfnp(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    D: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLAUNHR_COL_GETRFNP2")
@external
def claunhr_col_getrfnp2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    D: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLAUU2")
@external
def clauu2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CLAUUM")
@external
def clauum(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPBCON")
@external
def cpbcon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPBEQU")
@external
def cpbequ(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    S: Float32[Flat],
    SCOND: Ptr(Float32),
    AMAX: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPBRFS")
@external
def cpbrfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPBSTF")
@external
def cpbstf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPBSV")
@external
def cpbsv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPBSVX")
@external
def cpbsvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Complex64[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    EQUED: Ptr(Const(String[1])),
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPBTF2")
@external
def cpbtf2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPBTRF")
@external
def cpbtrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPBTRS")
@external
def cpbtrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPFTRF")
@external
def cpftrf(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Complex64[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPFTRI")
@external
def cpftri(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Complex64[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPFTRS")
@external
def cpftrs(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Annotated[Complex64[Flat], SourceDims("0:*")],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPOCON")
@external
def cpocon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPOEQU")
@external
def cpoequ(
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float32[Flat],
    SCOND: Ptr(Float32),
    AMAX: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPOEQUB")
@external
def cpoequb(
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float32[Flat],
    SCOND: Ptr(Float32),
    AMAX: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPORFS")
@external
def cporfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPORFSX")
@external
def cporfsx(
    UPLO: Ptr(Const(String[1])),
    EQUED: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPOSV")
@external
def cposv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPOSVX")
@external
def cposvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    EQUED: Ptr(Const(String[1])),
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPOSVXX")
@external
def cposvxx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    EQUED: Ptr(Const(String[1])),
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    RPVGRW: Ptr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPOTF2")
@external
def cpotf2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPOTRF")
@external
def cpotrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPOTRF2")
@external
def cpotrf2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPOTRI")
@external
def cpotri(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPOTRS")
@external
def cpotrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPPCON")
@external
def cppcon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPPEQU")
@external
def cppequ(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    S: Float32[Flat],
    SCOND: Ptr(Float32),
    AMAX: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPPRFS")
@external
def cpprfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex64[Flat],
    AFP: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPPSV")
@external
def cppsv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPPSVX")
@external
def cppsvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex64[Flat],
    AFP: Complex64[Flat],
    EQUED: Ptr(Const(String[1])),
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPPTRF")
@external
def cpptrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPPTRI")
@external
def cpptri(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPPTRS")
@external
def cpptrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPSTF2")
@external
def cpstf2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    PIV: Int32[N],
    RANK: Ptr(Int32),
    TOL: Ptr(Float32),
    WORK: Float32[2 * N],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPSTRF")
@external
def cpstrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    PIV: Int32[N],
    RANK: Ptr(Int32),
    TOL: Ptr(Float32),
    WORK: Float32[2 * N],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPTCON")
@external
def cptcon(
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Complex64[Flat],
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPTEQR")
@external
def cpteqr(
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPTRFS")
@external
def cptrfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float32[Flat],
    E: Complex64[Flat],
    DF: Float32[Flat],
    EF: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPTSV")
@external
def cptsv(
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float32[Flat],
    E: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPTSVX")
@external
def cptsvx(
    FACT: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float32[Flat],
    E: Complex64[Flat],
    DF: Float32[Flat],
    EF: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPTTRF")
@external
def cpttrf(
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPTTRS")
@external
def cpttrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float32[Flat],
    E: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CPTTS2")
@external
def cptts2(
    IUPLO: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float32[Flat],
    E: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("CROT")
@external
def crot(
    N: Ptr(Int32),
    CX: Complex64[Flat],
    INCX: Ptr(Int32),
    CY: Complex64[Flat],
    INCY: Ptr(Int32),
    C: Ptr(Float32),
    S: Ptr(Complex64)
) -> None: ...

@bind("CRSCL")
@external
def crscl(
    N: Ptr(Int32),
    A: Ptr(Complex64),
    X: Complex64[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("CSPCON")
@external
def cspcon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSPMV")
@external
def cspmv(
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

@bind("CSPR")
@external
def cspr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    X: Complex64[Flat],
    INCX: Ptr(Int32),
    AP: Complex64[Flat]
) -> None: ...

@bind("CSPRFS")
@external
def csprfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex64[Flat],
    AFP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSPSV")
@external
def cspsv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSPSVX")
@external
def cspsvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex64[Flat],
    AFP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSPTRF")
@external
def csptrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSPTRI")
@external
def csptri(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSPTRS")
@external
def csptrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSRSCL")
@external
def csrscl(
    N: Ptr(Int32),
    SA: Ptr(Float32),
    SX: Complex64[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("CSTEDC")
@external
def cstedc(
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSTEGR")
@external
def cstegr(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSTEIN")
@external
def cstein(
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    M: Ptr(Int32),
    W: Float32[Flat],
    IBLOCK: Int32[Flat],
    ISPLIT: Int32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSTEMR")
@external
def cstemr(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    NZC: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    TRYRAC: Ptr(Bool),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSTEQR")
@external
def csteqr(
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYCON")
@external
def csycon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYCON_3")
@external
def csycon_3(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYCON_ROOK")
@external
def csycon_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYCONV")
@external
def csyconv(
    UPLO: Ptr(Const(String[1])),
    WAY: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    E: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYCONVF")
@external
def csyconvf(
    UPLO: Ptr(Const(String[1])),
    WAY: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYCONVF_ROOK")
@external
def csyconvf_rook(
    UPLO: Ptr(Const(String[1])),
    WAY: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYEQUB")
@external
def csyequb(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float32[Flat],
    SCOND: Ptr(Float32),
    AMAX: Ptr(Float32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYMV")
@external
def csymv(
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

@bind("CSYR")
@external
def csyr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    X: Complex64[Flat],
    INCX: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("CSYRFS")
@external
def csyrfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYRFSX")
@external
def csyrfsx(
    UPLO: Ptr(Const(String[1])),
    EQUED: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYSV")
@external
def csysv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYSV_AA")
@external
def csysv_aa(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYSV_AA_2STAGE")
@external
def csysv_aa_2stage(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TB: Complex64[Flat],
    LTB: Ptr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYSV_RK")
@external
def csysv_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYSV_ROOK")
@external
def csysv_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYSVX")
@external
def csysvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYSVXX")
@external
def csysvxx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    EQUED: Ptr(Const(String[1])),
    S: Float32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    RPVGRW: Ptr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYSWAPR")
@external
def csyswapr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Complex64[LDA, N], ORDER_F],
    LDA: Ptr(Int32),
    I1: Ptr(Int32),
    I2: Ptr(Int32)
) -> None: ...

@bind("CSYTF2")
@external
def csytf2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYTF2_RK")
@external
def csytf2_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYTF2_ROOK")
@external
def csytf2_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYTRF")
@external
def csytrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYTRF_AA")
@external
def csytrf_aa(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYTRF_AA_2STAGE")
@external
def csytrf_aa_2stage(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TB: Complex64[Flat],
    LTB: Ptr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYTRF_RK")
@external
def csytrf_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYTRF_ROOK")
@external
def csytrf_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYTRI")
@external
def csytri(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYTRI2")
@external
def csytri2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYTRI2X")
@external
def csytri2x(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[N + NB + 1, Flat],
    NB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYTRI_3")
@external
def csytri_3(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYTRI_3X")
@external
def csytri_3x(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    WORK: Complex64[N + NB + 1, Flat],
    NB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYTRI_ROOK")
@external
def csytri_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYTRS")
@external
def csytrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYTRS2")
@external
def csytrs2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYTRS_3")
@external
def csytrs_3(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex64[Flat],
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYTRS_AA")
@external
def csytrs_aa(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYTRS_AA_2STAGE")
@external
def csytrs_aa_2stage(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TB: Complex64[Flat],
    LTB: Ptr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CSYTRS_ROOK")
@external
def csytrs_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTBCON")
@external
def ctbcon(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    RCOND: Ptr(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTBRFS")
@external
def ctbrfs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTBTRS")
@external
def ctbtrs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex64[LDAB, Flat],
    LDAB: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTFSM")
@external
def ctfsm(
    TRANSR: Ptr(Const(String[1])),
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex64),
    A: Annotated[Complex64[Flat], SourceDims("0:*")],
    B: Annotated[Complex64[0:LDB-1, Flat], SourceDims("0:LDB-1", "0:*")],
    LDB: Ptr(Int32)
) -> None: ...

@bind("CTFTRI")
@external
def ctftri(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Complex64[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTFTTP")
@external
def ctfttp(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ARF: Annotated[Complex64[Flat], SourceDims("0:*")],
    AP: Annotated[Complex64[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTFTTR")
@external
def ctfttr(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ARF: Annotated[Complex64[Flat], SourceDims("0:*")],
    A: Annotated[Complex64[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTGEVC")
@external
def ctgevc(
    SIDE: Ptr(Const(String[1])),
    HOWMNY: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    S: Complex64[LDS, Flat],
    LDS: Ptr(Int32),
    P: Complex64[LDP, Flat],
    LDP: Ptr(Int32),
    VL: Complex64[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Ptr(Int32),
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTGEX2")
@external
def ctgex2(
    WANTQ: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    J1: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTGEXC")
@external
def ctgexc(
    WANTQ: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    IFST: Ptr(Int32),
    ILST: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTGSEN")
@external
def ctgsen(
    IJOB: Ptr(Int32),
    WANTQ: Ptr(Bool),
    WANTZ: Ptr(Bool),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    ALPHA: Complex64[Flat],
    BETA: Complex64[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Complex64[LDZ, Flat],
    LDZ: Ptr(Int32),
    M: Ptr(Int32),
    PL: Ptr(Float32),
    PR: Ptr(Float32),
    DIF: Float32[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTGSJA")
@external
def ctgsja(
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    JOBQ: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    TOLA: Ptr(Float32),
    TOLB: Ptr(Float32),
    ALPHA: Float32[Flat],
    BETA: Float32[Flat],
    U: Complex64[LDU, Flat],
    LDU: Ptr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ptr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Int32),
    WORK: Complex64[Flat],
    NCYCLE: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTGSNA")
@external
def ctgsna(
    JOB: Ptr(Const(String[1])),
    HOWMNY: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    VL: Complex64[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Ptr(Int32),
    S: Float32[Flat],
    DIF: Float32[Flat],
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTGSY2")
@external
def ctgsy2(
    TRANS: Ptr(Const(String[1])),
    IJOB: Ptr(Int32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    D: Complex64[LDD, Flat],
    LDD: Ptr(Int32),
    E: Complex64[LDE, Flat],
    LDE: Ptr(Int32),
    F: Complex64[LDF, Flat],
    LDF: Ptr(Int32),
    SCALE: Ptr(Float32),
    RDSUM: Ptr(Float32),
    RDSCAL: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTGSYL")
@external
def ctgsyl(
    TRANS: Ptr(Const(String[1])),
    IJOB: Ptr(Int32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    D: Complex64[LDD, Flat],
    LDD: Ptr(Int32),
    E: Complex64[LDE, Flat],
    LDE: Ptr(Int32),
    F: Complex64[LDF, Flat],
    LDF: Ptr(Int32),
    SCALE: Ptr(Float32),
    DIF: Ptr(Float32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTPCON")
@external
def ctpcon(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    RCOND: Ptr(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTPLQT")
@external
def ctplqt(
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    MB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTPLQT2")
@external
def ctplqt2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTPMLQT")
@external
def ctpmlqt(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    MB: Ptr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTPMQRT")
@external
def ctpmqrt(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    NB: Ptr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTPQRT")
@external
def ctpqrt(
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTPQRT2")
@external
def ctpqrt2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTPRFB")
@external
def ctprfb(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIRECT: Ptr(Const(String[1])),
    STOREV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    V: Complex64[LDV, Flat],
    LDV: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex64[LDWORK, Flat],
    LDWORK: Ptr(Int32)
) -> None: ...

@bind("CTPRFS")
@external
def ctprfs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTPTRI")
@external
def ctptri(
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTPTRS")
@external
def ctptrs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex64[Flat],
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTPTTF")
@external
def ctpttf(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Annotated[Complex64[Flat], SourceDims("0:*")],
    ARF: Annotated[Complex64[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTPTTR")
@external
def ctpttr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTRCON")
@external
def ctrcon(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    RCOND: Ptr(Float32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTREVC")
@external
def ctrevc(
    SIDE: Ptr(Const(String[1])),
    HOWMNY: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    VL: Complex64[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Ptr(Int32),
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTREVC3")
@external
def ctrevc3(
    SIDE: Ptr(Const(String[1])),
    HOWMNY: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    VL: Complex64[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Ptr(Int32),
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTREXC")
@external
def ctrexc(
    COMPQ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Int32),
    IFST: Ptr(Int32),
    ILST: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTRRFS")
@external
def ctrrfs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Complex64[Flat],
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTRSEN")
@external
def ctrsen(
    JOB: Ptr(Const(String[1])),
    COMPQ: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Int32),
    W: Complex64[Flat],
    M: Ptr(Int32),
    S: Ptr(Float32),
    SEP: Ptr(Float32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTRSNA")
@external
def ctrsna(
    JOB: Ptr(Const(String[1])),
    HOWMNY: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    VL: Complex64[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Complex64[LDVR, Flat],
    LDVR: Ptr(Int32),
    S: Float32[Flat],
    SEP: Float32[Flat],
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Complex64[LDWORK, Flat],
    LDWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTRSYL")
@external
def ctrsyl(
    TRANA: Ptr(Const(String[1])),
    TRANB: Ptr(Const(String[1])),
    ISGN: Ptr(Int32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    SCALE: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTRSYL3")
@external
def ctrsyl3(
    TRANA: Ptr(Const(String[1])),
    TRANB: Ptr(Const(String[1])),
    ISGN: Ptr(Int32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    SCALE: Ptr(Float32),
    SWORK: Float32[LDSWORK, Flat],
    LDSWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTRTI2")
@external
def ctrti2(
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTRTRI")
@external
def ctrtri(
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTRTRS")
@external
def ctrtrs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTRTTF")
@external
def ctrttf(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Complex64[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Ptr(Int32),
    ARF: Annotated[Complex64[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTRTTP")
@external
def ctrttp(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    AP: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CTZRZF")
@external
def ctzrzf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNBDB")
@external
def cunbdb(
    TRANS: Ptr(Const(String[1])),
    SIGNS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Complex64[LDX11, Flat],
    LDX11: Ptr(Int32),
    X12: Complex64[LDX12, Flat],
    LDX12: Ptr(Int32),
    X21: Complex64[LDX21, Flat],
    LDX21: Ptr(Int32),
    X22: Complex64[LDX22, Flat],
    LDX22: Ptr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Complex64[Flat],
    TAUP2: Complex64[Flat],
    TAUQ1: Complex64[Flat],
    TAUQ2: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNBDB1")
@external
def cunbdb1(
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Complex64[LDX11, Flat],
    LDX11: Ptr(Int32),
    X21: Complex64[LDX21, Flat],
    LDX21: Ptr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Complex64[Flat],
    TAUP2: Complex64[Flat],
    TAUQ1: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNBDB2")
@external
def cunbdb2(
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Complex64[LDX11, Flat],
    LDX11: Ptr(Int32),
    X21: Complex64[LDX21, Flat],
    LDX21: Ptr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Complex64[Flat],
    TAUP2: Complex64[Flat],
    TAUQ1: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNBDB3")
@external
def cunbdb3(
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Complex64[LDX11, Flat],
    LDX11: Ptr(Int32),
    X21: Complex64[LDX21, Flat],
    LDX21: Ptr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Complex64[Flat],
    TAUP2: Complex64[Flat],
    TAUQ1: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNBDB4")
@external
def cunbdb4(
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Complex64[LDX11, Flat],
    LDX11: Ptr(Int32),
    X21: Complex64[LDX21, Flat],
    LDX21: Ptr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Complex64[Flat],
    TAUP2: Complex64[Flat],
    TAUQ1: Complex64[Flat],
    PHANTOM: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNBDB5")
@external
def cunbdb5(
    M1: Ptr(Int32),
    M2: Ptr(Int32),
    N: Ptr(Int32),
    X1: Complex64[Flat],
    INCX1: Ptr(Int32),
    X2: Complex64[Flat],
    INCX2: Ptr(Int32),
    Q1: Complex64[LDQ1, Flat],
    LDQ1: Ptr(Int32),
    Q2: Complex64[LDQ2, Flat],
    LDQ2: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNBDB6")
@external
def cunbdb6(
    M1: Ptr(Int32),
    M2: Ptr(Int32),
    N: Ptr(Int32),
    X1: Complex64[Flat],
    INCX1: Ptr(Int32),
    X2: Complex64[Flat],
    INCX2: Ptr(Int32),
    Q1: Complex64[LDQ1, Flat],
    LDQ1: Ptr(Int32),
    Q2: Complex64[LDQ2, Flat],
    LDQ2: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNCSD")
@external
def cuncsd(
    JOBU1: Ptr(Const(String[1])),
    JOBU2: Ptr(Const(String[1])),
    JOBV1T: Ptr(Const(String[1])),
    JOBV2T: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    SIGNS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Complex64[LDX11, Flat],
    LDX11: Ptr(Int32),
    X12: Complex64[LDX12, Flat],
    LDX12: Ptr(Int32),
    X21: Complex64[LDX21, Flat],
    LDX21: Ptr(Int32),
    X22: Complex64[LDX22, Flat],
    LDX22: Ptr(Int32),
    THETA: Float32[Flat],
    U1: Complex64[LDU1, Flat],
    LDU1: Ptr(Int32),
    U2: Complex64[LDU2, Flat],
    LDU2: Ptr(Int32),
    V1T: Complex64[LDV1T, Flat],
    LDV1T: Ptr(Int32),
    V2T: Complex64[LDV2T, Flat],
    LDV2T: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNCSD2BY1")
@external
def cuncsd2by1(
    JOBU1: Ptr(Const(String[1])),
    JOBU2: Ptr(Const(String[1])),
    JOBV1T: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Complex64[LDX11, Flat],
    LDX11: Ptr(Int32),
    X21: Complex64[LDX21, Flat],
    LDX21: Ptr(Int32),
    THETA: Float32[Flat],
    U1: Complex64[LDU1, Flat],
    LDU1: Ptr(Int32),
    U2: Complex64[LDU2, Flat],
    LDU2: Ptr(Int32),
    V1T: Complex64[LDV1T, Flat],
    LDV1T: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNG2L")
@external
def cung2l(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNG2R")
@external
def cung2r(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNGBR")
@external
def cungbr(
    VECT: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNGHR")
@external
def cunghr(
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNGL2")
@external
def cungl2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNGLQ")
@external
def cunglq(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNGQL")
@external
def cungql(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNGQR")
@external
def cungqr(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNGR2")
@external
def cungr2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNGRQ")
@external
def cungrq(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNGTR")
@external
def cungtr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNGTSQR")
@external
def cungtsqr(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNGTSQR_ROW")
@external
def cungtsqr_row(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNHR_COL")
@external
def cunhr_col(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex64[LDT, Flat],
    LDT: Ptr(Int32),
    D: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNM22")
@external
def cunm22(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    N1: Ptr(Int32),
    N2: Ptr(Int32),
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Int32),
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNM2L")
@external
def cunm2l(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNM2R")
@external
def cunm2r(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNMBR")
@external
def cunmbr(
    VECT: Ptr(Const(String[1])),
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNMHR")
@external
def cunmhr(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNML2")
@external
def cunml2(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNMLQ")
@external
def cunmlq(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNMQL")
@external
def cunmql(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNMQR")
@external
def cunmqr(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNMR2")
@external
def cunmr2(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNMR3")
@external
def cunmr3(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNMRQ")
@external
def cunmrq(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNMRZ")
@external
def cunmrz(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUNMTR")
@external
def cunmtr(
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUPGTR")
@external
def cupgtr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    TAU: Complex64[Flat],
    Q: Complex64[LDQ, Flat],
    LDQ: Ptr(Int32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("CUPMTR")
@external
def cupmtr(
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    AP: Complex64[Flat],
    TAU: Complex64[Flat],
    C: Complex64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DBBCSD")
@external
def dbbcsd(
    JOBU1: Ptr(Const(String[1])),
    JOBU2: Ptr(Const(String[1])),
    JOBV1T: Ptr(Const(String[1])),
    JOBV2T: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    U1: Float64[LDU1, Flat],
    LDU1: Ptr(Int32),
    U2: Float64[LDU2, Flat],
    LDU2: Ptr(Int32),
    V1T: Float64[LDV1T, Flat],
    LDV1T: Ptr(Int32),
    V2T: Float64[LDV2T, Flat],
    LDV2T: Ptr(Int32),
    B11D: Float64[Flat],
    B11E: Float64[Flat],
    B12D: Float64[Flat],
    B12E: Float64[Flat],
    B21D: Float64[Flat],
    B21E: Float64[Flat],
    B22D: Float64[Flat],
    B22E: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DBDSDC")
@external
def dbdsdc(
    UPLO: Ptr(Const(String[1])),
    COMPQ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Ptr(Int32),
    Q: Float64[Flat],
    IQ: Int32[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DBDSQR")
@external
def dbdsqr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NCVT: Ptr(Int32),
    NRU: Ptr(Int32),
    NCC: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VT: Float64[LDVT, Flat],
    LDVT: Ptr(Int32),
    U: Float64[LDU, Flat],
    LDU: Ptr(Int32),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DBDSVDX")
@external
def dbdsvdx(
    UPLO: Ptr(Const(String[1])),
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    NS: Ptr(Int32),
    S: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DDISNA")
@external
def ddisna(
    JOB: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    D: Float64[Flat],
    SEP: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGBBRD")
@external
def dgbbrd(
    VECT: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    NCC: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    PT: Float64[LDPT, Flat],
    LDPT: Ptr(Int32),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGBCON")
@external
def dgbcon(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    IPIV: Int32[Flat],
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGBEQU")
@external
def dgbequ(
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ptr(Float64),
    COLCND: Ptr(Float64),
    AMAX: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGBEQUB")
@external
def dgbequb(
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ptr(Float64),
    COLCND: Ptr(Float64),
    AMAX: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGBRFS")
@external
def dgbrfs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGBRFSX")
@external
def dgbrfsx(
    TRANS: Ptr(Const(String[1])),
    EQUED: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    R: Float64[Flat],
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGBSV")
@external
def dgbsv(
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGBSVX")
@external
def dgbsvx(
    FACT: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    EQUED: Ptr(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGBSVXX")
@external
def dgbsvxx(
    FACT: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    EQUED: Ptr(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    RPVGRW: Ptr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGBTF2")
@external
def dgbtf2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGBTRF")
@external
def dgbtrf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGBTRS")
@external
def dgbtrs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEBAK")
@external
def dgebak(
    JOB: Ptr(Const(String[1])),
    SIDE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    SCALE: Float64[Flat],
    M: Ptr(Int32),
    V: Float64[LDV, Flat],
    LDV: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEBAL")
@external
def dgebal(
    JOB: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    SCALE: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEBD2")
@external
def dgebd2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAUQ: Float64[Flat],
    TAUP: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEBRD")
@external
def dgebrd(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAUQ: Float64[Flat],
    TAUP: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGECON")
@external
def dgecon(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEDMD")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7), Arg(8), Arg(9), Arg(10), Arg(11), Arg(12), Return('K', 0), Arg(13), Arg(14), Arg(15), Arg(16), Arg(17), Arg(18), Arg(19), Arg(20), Arg(21), Arg(22), Arg(23), Arg(24), Arg(25), Arg(26), Arg(27), Return('INFO', 10)])
def dgedmd(
    JOBS: Ptr(Const(String[1])),
    JOBZ: Ptr(Const(String[1])),
    JOBR: Ptr(Const(String[1])),
    JOBF: Ptr(Const(String[1])),
    WHTSVD: Ptr(Const(Int32)),
    M: Ptr(Const(Int32)),
    N: Ptr(Const(Int32)),
    X: Float64[LDX, Flat],
    LDX: Ptr(Const(Int32)),
    Y: Float64[LDY, Flat],
    LDY: Ptr(Const(Int32)),
    NRNK: Ptr(Const(Int32)),
    TOL: Ptr(Const(Float64)),
    REIG: Float64[Flat],
    IMEIG: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Const(Int32)),
    RES: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    W: Float64[LDW, Flat],
    LDW: Ptr(Const(Int32)),
    S: Float64[LDS, Flat],
    LDS: Ptr(Const(Int32)),
    WORK: Float64[Flat],
    LWORK: Ptr(Const(Int32)),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Const(Int32))
) -> tuple[Int32, Returns["REIG", Float64[Flat]], Returns["IMEIG", Float64[Flat]], Returns["Z", Float64[LDZ, Flat]], Returns["RES", Float64[Flat]], Returns["B", Float64[LDB, Flat]], Returns["W", Float64[LDW, Flat]], Returns["S", Float64[LDS, Flat]], Returns["WORK", Float64[Flat]], Returns["IWORK", Int32[Flat]], Int32]: ...

@bind("DGEDMDQ")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7), Arg(8), Arg(9), Arg(10), Arg(11), Arg(12), Arg(13), Arg(14), Arg(15), Arg(16), Return('K', 2), Arg(17), Arg(18), Arg(19), Arg(20), Arg(21), Arg(22), Arg(23), Arg(24), Arg(25), Arg(26), Arg(27), Arg(28), Arg(29), Arg(30), Arg(31), Return('INFO', 12)])
def dgedmdq(
    JOBS: Ptr(Const(String[1])),
    JOBZ: Ptr(Const(String[1])),
    JOBR: Ptr(Const(String[1])),
    JOBQ: Ptr(Const(String[1])),
    JOBT: Ptr(Const(String[1])),
    JOBF: Ptr(Const(String[1])),
    WHTSVD: Ptr(Const(Int32)),
    M: Ptr(Const(Int32)),
    N: Ptr(Const(Int32)),
    F: Float64[LDF, Flat],
    LDF: Ptr(Const(Int32)),
    X: Float64[LDX, Flat],
    LDX: Ptr(Const(Int32)),
    Y: Float64[LDY, Flat],
    LDY: Ptr(Const(Int32)),
    NRNK: Ptr(Const(Int32)),
    TOL: Ptr(Const(Float64)),
    REIG: Float64[Flat],
    IMEIG: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Const(Int32)),
    RES: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    V: Float64[LDV, Flat],
    LDV: Ptr(Const(Int32)),
    S: Float64[LDS, Flat],
    LDS: Ptr(Const(Int32)),
    WORK: Float64[Flat],
    LWORK: Ptr(Const(Int32)),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Const(Int32))
) -> tuple[Returns["X", Float64[LDX, Flat]], Returns["Y", Float64[LDY, Flat]], Int32, Returns["REIG", Float64[Flat]], Returns["IMEIG", Float64[Flat]], Returns["Z", Float64[LDZ, Flat]], Returns["RES", Float64[Flat]], Returns["B", Float64[LDB, Flat]], Returns["V", Float64[LDV, Flat]], Returns["S", Float64[LDS, Flat]], Returns["WORK", Float64[Flat]], Returns["IWORK", Int32[Flat]], Int32]: ...

@bind("DGEEQU")
@external
def dgeequ(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ptr(Float64),
    COLCND: Ptr(Float64),
    AMAX: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEEQUB")
@external
def dgeequb(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ptr(Float64),
    COLCND: Ptr(Float64),
    AMAX: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEES")
@external
def dgees(
    JOBVS: Ptr(Const(String[1])),
    SORT: Ptr(Const(String[1])),
    SELECT: Ptr(Bool),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    SDIM: Ptr(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    VS: Float64[LDVS, Flat],
    LDVS: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEESX")
@external
def dgeesx(
    JOBVS: Ptr(Const(String[1])),
    SORT: Ptr(Const(String[1])),
    SELECT: Ptr(Bool),
    SENSE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    SDIM: Ptr(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    VS: Float64[LDVS, Flat],
    LDVS: Ptr(Int32),
    RCONDE: Ptr(Float64),
    RCONDV: Ptr(Float64),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEEV")
@external
def dgeev(
    JOBVL: Ptr(Const(String[1])),
    JOBVR: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    VL: Float64[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEEVX")
@external
def dgeevx(
    BALANC: Ptr(Const(String[1])),
    JOBVL: Ptr(Const(String[1])),
    JOBVR: Ptr(Const(String[1])),
    SENSE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    VL: Float64[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    SCALE: Float64[Flat],
    ABNRM: Ptr(Float64),
    RCONDE: Float64[Flat],
    RCONDV: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEHD2")
@external
def dgehd2(
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEHRD")
@external
def dgehrd(
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEJSV")
@external
def dgejsv(
    JOBA: Ptr(Const(String[1])),
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    JOBR: Ptr(Const(String[1])),
    JOBT: Ptr(Const(String[1])),
    JOBP: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    SVA: Float64[N],
    U: Float64[LDU, Flat],
    LDU: Ptr(Int32),
    V: Float64[LDV, Flat],
    LDV: Ptr(Int32),
    WORK: Float64[LWORK],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGELQ")
@external
def dgelq(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float64[Flat],
    TSIZE: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGELQ2")
@external
def dgelq2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGELQF")
@external
def dgelqf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGELQT")
@external
def dgelqt(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGELQT3")
@external
def dgelqt3(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGELS")
@external
def dgels(
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGELSD")
@external
def dgelsd(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    S: Float64[Flat],
    RCOND: Ptr(Float64),
    RANK: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGELSS")
@external
def dgelss(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    S: Float64[Flat],
    RCOND: Ptr(Float64),
    RANK: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGELST")
@external
def dgelst(
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGELSY")
@external
def dgelsy(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    JPVT: Int32[Flat],
    RCOND: Ptr(Float64),
    RANK: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEMLQ")
@external
def dgemlq(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float64[Flat],
    TSIZE: Ptr(Int32),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEMLQT")
@external
def dgemlqt(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    MB: Ptr(Int32),
    V: Float64[LDV, Flat],
    LDV: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEMQR")
@external
def dgemqr(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float64[Flat],
    TSIZE: Ptr(Int32),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEMQRT")
@external
def dgemqrt(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    NB: Ptr(Int32),
    V: Float64[LDV, Flat],
    LDV: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEQL2")
@external
def dgeql2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEQLF")
@external
def dgeqlf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEQP3")
@external
def dgeqp3(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    JPVT: Int32[Flat],
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEQP3RK")
@external
def dgeqp3rk(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    KMAX: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    RELTOL: Ptr(Float64),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    K: Ptr(Int32),
    MAXC2NRMK: Ptr(Float64),
    RELMAXC2NRMK: Ptr(Float64),
    JPIV: Int32[Flat],
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEQR")
@external
def dgeqr(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float64[Flat],
    TSIZE: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEQR2")
@external
def dgeqr2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEQR2P")
@external
def dgeqr2p(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEQRF")
@external
def dgeqrf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEQRFP")
@external
def dgeqrfp(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEQRT")
@external
def dgeqrt(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEQRT2")
@external
def dgeqrt2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGEQRT3")
@external
def dgeqrt3(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGERFS")
@external
def dgerfs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGERFSX")
@external
def dgerfsx(
    TRANS: Ptr(Const(String[1])),
    EQUED: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    R: Float64[Flat],
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGERQ2")
@external
def dgerq2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGERQF")
@external
def dgerqf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGESC2")
@external
def dgesc2(
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    RHS: Float64[Flat],
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    SCALE: Ptr(Float64)
) -> None: ...

@bind("DGESDD")
@external
def dgesdd(
    JOBZ: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGESV")
@external
def dgesv(
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGESVD")
@external
def dgesvd(
    JOBU: Ptr(Const(String[1])),
    JOBVT: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGESVDQ")
@external
def dgesvdq(
    JOBA: Ptr(Const(String[1])),
    JOBP: Ptr(Const(String[1])),
    JOBR: Ptr(Const(String[1])),
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Ptr(Int32),
    V: Float64[LDV, Flat],
    LDV: Ptr(Int32),
    NUMRANK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGESVDX")
@external
def dgesvdx(
    JOBU: Ptr(Const(String[1])),
    JOBVT: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    NS: Ptr(Int32),
    S: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGESVJ")
@external
def dgesvj(
    JOBA: Ptr(Const(String[1])),
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    SVA: Float64[N],
    MV: Ptr(Int32),
    V: Float64[LDV, Flat],
    LDV: Ptr(Int32),
    WORK: Float64[LWORK],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGESVX")
@external
def dgesvx(
    FACT: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    EQUED: Ptr(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGESVXX")
@external
def dgesvxx(
    FACT: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    EQUED: Ptr(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    RPVGRW: Ptr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGETC2")
@external
def dgetc2(
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGETF2")
@external
def dgetf2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGETRF")
@external
def dgetrf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGETRF2")
@external
def dgetrf2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGETRI")
@external
def dgetri(
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGETRS")
@external
def dgetrs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGETSLS")
@external
def dgetsls(
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGETSQRHRT")
@external
def dgetsqrhrt(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB1: Ptr(Int32),
    NB1: Ptr(Int32),
    NB2: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGGBAK")
@external
def dggbak(
    JOB: Ptr(Const(String[1])),
    SIDE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    LSCALE: Float64[Flat],
    RSCALE: Float64[Flat],
    M: Ptr(Int32),
    V: Float64[LDV, Flat],
    LDV: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGGBAL")
@external
def dggbal(
    JOB: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    LSCALE: Float64[Flat],
    RSCALE: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGGES")
@external
def dgges(
    JOBVSL: Ptr(Const(String[1])),
    JOBVSR: Ptr(Const(String[1])),
    SORT: Ptr(Const(String[1])),
    SELCTG: Ptr(Bool),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    SDIM: Ptr(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    VSL: Float64[LDVSL, Flat],
    LDVSL: Ptr(Int32),
    VSR: Float64[LDVSR, Flat],
    LDVSR: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGGES3")
@external
def dgges3(
    JOBVSL: Ptr(Const(String[1])),
    JOBVSR: Ptr(Const(String[1])),
    SORT: Ptr(Const(String[1])),
    SELCTG: Ptr(Bool),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    SDIM: Ptr(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    VSL: Float64[LDVSL, Flat],
    LDVSL: Ptr(Int32),
    VSR: Float64[LDVSR, Flat],
    LDVSR: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGGESX")
@external
def dggesx(
    JOBVSL: Ptr(Const(String[1])),
    JOBVSR: Ptr(Const(String[1])),
    SORT: Ptr(Const(String[1])),
    SELCTG: Ptr(Bool),
    SENSE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    SDIM: Ptr(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    VSL: Float64[LDVSL, Flat],
    LDVSL: Ptr(Int32),
    VSR: Float64[LDVSR, Flat],
    LDVSR: Ptr(Int32),
    RCONDE: Float64[2],
    RCONDV: Float64[2],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGGEV")
@external
def dggev(
    JOBVL: Ptr(Const(String[1])),
    JOBVR: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    VL: Float64[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGGEV3")
@external
def dggev3(
    JOBVL: Ptr(Const(String[1])),
    JOBVR: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    VL: Float64[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGGEVX")
@external
def dggevx(
    BALANC: Ptr(Const(String[1])),
    JOBVL: Ptr(Const(String[1])),
    JOBVR: Ptr(Const(String[1])),
    SENSE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    VL: Float64[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    LSCALE: Float64[Flat],
    RSCALE: Float64[Flat],
    ABNRM: Ptr(Float64),
    BBNRM: Ptr(Float64),
    RCONDE: Float64[Flat],
    RCONDV: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGGGLM")
@external
def dggglm(
    N: Ptr(Int32),
    M: Ptr(Int32),
    P: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    D: Float64[Flat],
    X: Float64[Flat],
    Y: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGGHD3")
@external
def dgghd3(
    COMPQ: Ptr(Const(String[1])),
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGGHRD")
@external
def dgghrd(
    COMPQ: Ptr(Const(String[1])),
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGGLSE")
@external
def dgglse(
    M: Ptr(Int32),
    N: Ptr(Int32),
    P: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    C: Float64[Flat],
    D: Float64[Flat],
    X: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGGQRF")
@external
def dggqrf(
    N: Ptr(Int32),
    M: Ptr(Int32),
    P: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAUA: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    TAUB: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGGRQF")
@external
def dggrqf(
    M: Ptr(Int32),
    P: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAUA: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    TAUB: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGGSVD3")
@external
def dggsvd3(
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    JOBQ: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    P: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    ALPHA: Float64[Flat],
    BETA: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Ptr(Int32),
    V: Float64[LDV, Flat],
    LDV: Ptr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGGSVP3")
@external
def dggsvp3(
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    JOBQ: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    TOLA: Ptr(Float64),
    TOLB: Ptr(Float64),
    K: Ptr(Int32),
    L: Ptr(Int32),
    U: Float64[LDU, Flat],
    LDU: Ptr(Int32),
    V: Float64[LDV, Flat],
    LDV: Ptr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    IWORK: Int32[Flat],
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGSVJ0")
@external
def dgsvj0(
    JOBV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float64[N],
    SVA: Float64[N],
    MV: Ptr(Int32),
    V: Float64[LDV, Flat],
    LDV: Ptr(Int32),
    EPS: Ptr(Float64),
    SFMIN: Ptr(Float64),
    TOL: Ptr(Float64),
    NSWEEP: Ptr(Int32),
    WORK: Float64[LWORK],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGSVJ1")
@external
def dgsvj1(
    JOBV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    N1: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float64[N],
    SVA: Float64[N],
    MV: Ptr(Int32),
    V: Float64[LDV, Flat],
    LDV: Ptr(Int32),
    EPS: Ptr(Float64),
    SFMIN: Ptr(Float64),
    TOL: Ptr(Float64),
    NSWEEP: Ptr(Int32),
    WORK: Float64[LWORK],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGTCON")
@external
def dgtcon(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    DU2: Float64[Flat],
    IPIV: Int32[Flat],
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGTRFS")
@external
def dgtrfs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    DLF: Float64[Flat],
    DF: Float64[Flat],
    DUF: Float64[Flat],
    DU2: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGTSV")
@external
def dgtsv(
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGTSVX")
@external
def dgtsvx(
    FACT: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    DLF: Float64[Flat],
    DF: Float64[Flat],
    DUF: Float64[Flat],
    DU2: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGTTRF")
@external
def dgttrf(
    N: Ptr(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    DU2: Float64[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGTTRS")
@external
def dgttrs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    DU2: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DGTTS2")
@external
def dgtts2(
    ITRANS: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    DU2: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("DHGEQZ")
@external
def dhgeqz(
    JOB: Ptr(Const(String[1])),
    COMPQ: Ptr(Const(String[1])),
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    H: Float64[LDH, Flat],
    LDH: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DHSEIN")
@external
def dhsein(
    SIDE: Ptr(Const(String[1])),
    EIGSRC: Ptr(Const(String[1])),
    INITV: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    H: Float64[LDH, Flat],
    LDH: Ptr(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    VL: Float64[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Ptr(Int32),
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Float64[Flat],
    IFAILL: Int32[Flat],
    IFAILR: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DHSEQR")
@external
def dhseqr(
    JOB: Ptr(Const(String[1])),
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    H: Float64[LDH, Flat],
    LDH: Ptr(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DISNAN")
@external
def disnan(
    DIN: Ptr(Const(Float64))
) -> Bool: ...

@bind("DLA_GBAMV")
@external
def dla_gbamv(
    TRANS: Ptr(Int32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    ALPHA: Ptr(Float64),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    X: Float64[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Float64),
    Y: Float64[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("DLA_GBRCOND")
@external
def dla_gbrcond(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    CMODE: Ptr(Int32),
    C: Float64[Flat],
    INFO: Ptr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat]
) -> Float64: ...

@bind("DLA_GBRFSX_EXTENDED")
@external
def dla_gbrfsx_extended(
    PREC_TYPE: Ptr(Int32),
    TRANS_TYPE: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ptr(Bool),
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    Y: Float64[LDY, Flat],
    LDY: Ptr(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    RES: Float64[Flat],
    AYB: Float64[Flat],
    DY: Float64[Flat],
    Y_TAIL: Float64[Flat],
    RCOND: Ptr(Float64),
    ITHRESH: Ptr(Int32),
    RTHRESH: Ptr(Float64),
    DZ_UB: Ptr(Float64),
    IGNORE_CWISE: Ptr(Bool),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLA_GBRPVGRW")
@external
def dla_gbrpvgrw(
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NCOLS: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Ptr(Int32)
) -> Float64: ...

@bind("DLA_GEAMV")
@external
def dla_geamv(
    TRANS: Ptr(Int32),
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

@bind("DLA_GERCOND")
@external
def dla_gercond(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    CMODE: Ptr(Int32),
    C: Float64[Flat],
    INFO: Ptr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat]
) -> Float64: ...

@bind("DLA_GERFSX_EXTENDED")
@external
def dla_gerfsx_extended(
    PREC_TYPE: Ptr(Int32),
    TRANS_TYPE: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ptr(Bool),
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    Y: Float64[LDY, Flat],
    LDY: Ptr(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Ptr(Int32),
    ERRS_N: Float64[NRHS, Flat],
    ERRS_C: Float64[NRHS, Flat],
    RES: Float64[Flat],
    AYB: Float64[Flat],
    DY: Float64[Flat],
    Y_TAIL: Float64[Flat],
    RCOND: Ptr(Float64),
    ITHRESH: Ptr(Int32),
    RTHRESH: Ptr(Float64),
    DZ_UB: Ptr(Float64),
    IGNORE_CWISE: Ptr(Bool),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLA_GERPVGRW")
@external
def dla_gerpvgrw(
    N: Ptr(Int32),
    NCOLS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ptr(Int32)
) -> Float64: ...

@bind("DLA_LIN_BERR")
@external
def dla_lin_berr(
    N: Ptr(Int32),
    NZ: Ptr(Int32),
    NRHS: Ptr(Int32),
    RES: Annotated[Float64[N, NRHS], ORDER_F],
    AYB: Annotated[Float64[N, NRHS], ORDER_F],
    BERR: Float64[NRHS]
) -> None: ...

@bind("DLA_PORCOND")
@external
def dla_porcond(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ptr(Int32),
    CMODE: Ptr(Int32),
    C: Float64[Flat],
    INFO: Ptr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat]
) -> Float64: ...

@bind("DLA_PORFSX_EXTENDED")
@external
def dla_porfsx_extended(
    PREC_TYPE: Ptr(Int32),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ptr(Int32),
    COLEQU: Ptr(Bool),
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    Y: Float64[LDY, Flat],
    LDY: Ptr(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    RES: Float64[Flat],
    AYB: Float64[Flat],
    DY: Float64[Flat],
    Y_TAIL: Float64[Flat],
    RCOND: Ptr(Float64),
    ITHRESH: Ptr(Int32),
    RTHRESH: Ptr(Float64),
    DZ_UB: Ptr(Float64),
    IGNORE_CWISE: Ptr(Bool),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLA_PORPVGRW")
@external
def dla_porpvgrw(
    UPLO: Ptr(Const(String[1])),
    NCOLS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ptr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLA_SYAMV")
@external
def dla_syamv(
    UPLO: Ptr(Int32),
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

@bind("DLA_SYRCOND")
@external
def dla_syrcond(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    CMODE: Ptr(Int32),
    C: Float64[Flat],
    INFO: Ptr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat]
) -> Float64: ...

@bind("DLA_SYRFSX_EXTENDED")
@external
def dla_syrfsx_extended(
    PREC_TYPE: Ptr(Int32),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ptr(Bool),
    C: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    Y: Float64[LDY, Flat],
    LDY: Ptr(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    RES: Float64[Flat],
    AYB: Float64[Flat],
    DY: Float64[Flat],
    Y_TAIL: Float64[Flat],
    RCOND: Ptr(Float64),
    ITHRESH: Ptr(Int32),
    RTHRESH: Ptr(Float64),
    DZ_UB: Ptr(Float64),
    IGNORE_CWISE: Ptr(Bool),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLA_SYRPVGRW")
@external
def dla_syrpvgrw(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    INFO: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLA_WWADDW")
@external
def dla_wwaddw(
    N: Ptr(Int32),
    X: Float64[Flat],
    Y: Float64[Flat],
    W: Float64[Flat]
) -> None: ...

@bind("DLABAD")
@external
def dlabad(
    SMALL: Ptr(Float64),
    LARGE: Ptr(Float64)
) -> None: ...

@bind("DLABRD")
@external
def dlabrd(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAUQ: Float64[Flat],
    TAUP: Float64[Flat],
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    Y: Float64[LDY, Flat],
    LDY: Ptr(Int32)
) -> None: ...

@bind("DLACN2")
@external
def dlacn2(
    N: Ptr(Int32),
    V: Float64[Flat],
    X: Float64[Flat],
    ISGN: Int32[Flat],
    EST: Ptr(Float64),
    KASE: Ptr(Int32),
    ISAVE: Int32[3]
) -> None: ...

@bind("DLACON")
@external
def dlacon(
    N: Ptr(Int32),
    V: Float64[Flat],
    X: Float64[Flat],
    ISGN: Int32[Flat],
    EST: Ptr(Float64),
    KASE: Ptr(Int32)
) -> None: ...

@bind("DLACPY")
@external
def dlacpy(
    UPLO: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("DLADIV")
@external
def dladiv(
    A: Ptr(Float64),
    B: Ptr(Float64),
    C: Ptr(Float64),
    D: Ptr(Float64),
    P: Ptr(Float64),
    Q: Ptr(Float64)
) -> None: ...

@bind("DLADIV1")
@external
def dladiv1(
    A: Ptr(Float64),
    B: Ptr(Float64),
    C: Ptr(Float64),
    D: Ptr(Float64),
    P: Ptr(Float64),
    Q: Ptr(Float64)
) -> None: ...

@bind("DLADIV2")
@external
def dladiv2(
    A: Ptr(Float64),
    B: Ptr(Float64),
    C: Ptr(Float64),
    D: Ptr(Float64),
    R: Ptr(Float64),
    T: Ptr(Float64)
) -> Float64: ...

@bind("DLAE2")
@external
def dlae2(
    A: Ptr(Float64),
    B: Ptr(Float64),
    C: Ptr(Float64),
    RT1: Ptr(Float64),
    RT2: Ptr(Float64)
) -> None: ...

@bind("DLAEBZ")
@external
def dlaebz(
    IJOB: Ptr(Int32),
    NITMAX: Ptr(Int32),
    N: Ptr(Int32),
    MMAX: Ptr(Int32),
    MINP: Ptr(Int32),
    NBMIN: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    RELTOL: Ptr(Float64),
    PIVMIN: Ptr(Float64),
    D: Float64[Flat],
    E: Float64[Flat],
    E2: Float64[Flat],
    NVAL: Int32[Flat],
    AB: Float64[MMAX, Flat],
    C: Float64[Flat],
    MOUT: Ptr(Int32),
    NAB: Int32[MMAX, Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAED0")
@external
def dlaed0(
    ICOMPQ: Ptr(Int32),
    QSIZ: Ptr(Int32),
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    QSTORE: Float64[LDQS, Flat],
    LDQS: Ptr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAED1")
@external
def dlaed1(
    N: Ptr(Int32),
    D: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    INDXQ: Int32[Flat],
    RHO: Ptr(Float64),
    CUTPNT: Ptr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAED2")
@external
def dlaed2(
    K: Ptr(Int32),
    N: Ptr(Int32),
    N1: Ptr(Int32),
    D: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    INDXQ: Int32[Flat],
    RHO: Ptr(Float64),
    Z: Float64[Flat],
    DLAMBDA: Float64[Flat],
    W: Float64[Flat],
    Q2: Float64[Flat],
    INDX: Int32[Flat],
    INDXC: Int32[Flat],
    INDXP: Int32[Flat],
    COLTYP: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAED3")
@external
def dlaed3(
    K: Ptr(Int32),
    N: Ptr(Int32),
    N1: Ptr(Int32),
    D: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    RHO: Ptr(Float64),
    DLAMBDA: Float64[Flat],
    Q2: Float64[Flat],
    INDX: Int32[Flat],
    CTOT: Int32[Flat],
    W: Float64[Flat],
    S: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAED4")
@external
def dlaed4(
    N: Ptr(Int32),
    I: Ptr(Int32),
    D: Float64[Flat],
    Z: Float64[Flat],
    DELTA: Float64[Flat],
    RHO: Ptr(Float64),
    DLAM: Ptr(Float64),
    INFO: Ptr(Int32)
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

@bind("DLAED6")
@external
def dlaed6(
    KNITER: Ptr(Int32),
    ORGATI: Ptr(Bool),
    RHO: Ptr(Float64),
    D: Float64[3],
    Z: Float64[3],
    FINIT: Ptr(Float64),
    TAU: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAED7")
@external
def dlaed7(
    ICOMPQ: Ptr(Int32),
    N: Ptr(Int32),
    QSIZ: Ptr(Int32),
    TLVLS: Ptr(Int32),
    CURLVL: Ptr(Int32),
    CURPBM: Ptr(Int32),
    D: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    INDXQ: Int32[Flat],
    RHO: Ptr(Float64),
    CUTPNT: Ptr(Int32),
    QSTORE: Float64[Flat],
    QPTR: Int32[Flat],
    PRMPTR: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float64[2, Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAED8")
@external
def dlaed8(
    ICOMPQ: Ptr(Int32),
    K: Ptr(Int32),
    N: Ptr(Int32),
    QSIZ: Ptr(Int32),
    D: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    INDXQ: Int32[Flat],
    RHO: Ptr(Float64),
    CUTPNT: Ptr(Int32),
    Z: Float64[Flat],
    DLAMBDA: Float64[Flat],
    Q2: Float64[LDQ2, Flat],
    LDQ2: Ptr(Int32),
    W: Float64[Flat],
    PERM: Int32[Flat],
    GIVPTR: Ptr(Int32),
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float64[2, Flat],
    INDXP: Int32[Flat],
    INDX: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAED9")
@external
def dlaed9(
    K: Ptr(Int32),
    KSTART: Ptr(Int32),
    KSTOP: Ptr(Int32),
    N: Ptr(Int32),
    D: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    RHO: Ptr(Float64),
    DLAMBDA: Float64[Flat],
    W: Float64[Flat],
    S: Float64[LDS, Flat],
    LDS: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAEDA")
@external
def dlaeda(
    N: Ptr(Int32),
    TLVLS: Ptr(Int32),
    CURLVL: Ptr(Int32),
    CURPBM: Ptr(Int32),
    PRMPTR: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float64[2, Flat],
    Q: Float64[Flat],
    QPTR: Int32[Flat],
    Z: Float64[Flat],
    ZTEMP: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAEIN")
@external
def dlaein(
    RIGHTV: Ptr(Bool),
    NOINIT: Ptr(Bool),
    N: Ptr(Int32),
    H: Float64[LDH, Flat],
    LDH: Ptr(Int32),
    WR: Ptr(Float64),
    WI: Ptr(Float64),
    VR: Float64[Flat],
    VI: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float64[Flat],
    EPS3: Ptr(Float64),
    SMLNUM: Ptr(Float64),
    BIGNUM: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAEV2")
@external
def dlaev2(
    A: Ptr(Float64),
    B: Ptr(Float64),
    C: Ptr(Float64),
    RT1: Ptr(Float64),
    RT2: Ptr(Float64),
    CS1: Ptr(Float64),
    SN1: Ptr(Float64)
) -> None: ...

@bind("DLAEXC")
@external
def dlaexc(
    WANTQ: Ptr(Bool),
    N: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    J1: Ptr(Int32),
    N1: Ptr(Int32),
    N2: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAG2")
@external
def dlag2(
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    SAFMIN: Ptr(Float64),
    SCALE1: Ptr(Float64),
    SCALE2: Ptr(Float64),
    WR1: Ptr(Float64),
    WR2: Ptr(Float64),
    WI: Ptr(Float64)
) -> None: ...

@bind("DLAG2S")
@external
def dlag2s(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    SA: Float32[LDSA, Flat],
    LDSA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAGS2")
@external
def dlags2(
    UPPER: Ptr(Bool),
    A1: Ptr(Float64),
    A2: Ptr(Float64),
    A3: Ptr(Float64),
    B1: Ptr(Float64),
    B2: Ptr(Float64),
    B3: Ptr(Float64),
    CSU: Ptr(Float64),
    SNU: Ptr(Float64),
    CSV: Ptr(Float64),
    SNV: Ptr(Float64),
    CSQ: Ptr(Float64),
    SNQ: Ptr(Float64)
) -> None: ...

@bind("DLAGTF")
@external
def dlagtf(
    N: Ptr(Int32),
    A: Float64[Flat],
    LAMBDA: Ptr(Float64),
    B: Float64[Flat],
    C: Float64[Flat],
    TOL: Ptr(Float64),
    D: Float64[Flat],
    IN: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAGTM")
@external
def dlagtm(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    ALPHA: Ptr(Float64),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat],
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    BETA: Ptr(Float64),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("DLAGTS")
@external
def dlagts(
    JOB: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[Flat],
    B: Float64[Flat],
    C: Float64[Flat],
    D: Float64[Flat],
    IN: Int32[Flat],
    Y: Float64[Flat],
    TOL: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAGV2")
@external
def dlagv2(
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    ALPHAR: Float64[2],
    ALPHAI: Float64[2],
    BETA: Float64[2],
    CSL: Ptr(Float64),
    SNL: Ptr(Float64),
    CSR: Ptr(Float64),
    SNR: Ptr(Float64)
) -> None: ...

@bind("DLAHQR")
@external
def dlahqr(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    H: Float64[LDH, Flat],
    LDH: Ptr(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAHR2")
@external
def dlahr2(
    N: Ptr(Int32),
    K: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[NB],
    T: Annotated[Float64[LDT, NB], ORDER_F],
    LDT: Ptr(Int32),
    Y: Annotated[Float64[LDY, NB], ORDER_F],
    LDY: Ptr(Int32)
) -> None: ...

@bind("DLAIC1")
@external
def dlaic1(
    JOB: Ptr(Int32),
    J: Ptr(Int32),
    X: Float64[J],
    SEST: Ptr(Float64),
    W: Float64[J],
    GAMMA: Ptr(Float64),
    SESTPR: Ptr(Float64),
    S: Ptr(Float64),
    C: Ptr(Float64)
) -> None: ...

@bind("DLAISNAN")
@external
def dlaisnan(
    DIN1: Ptr(Const(Float64)),
    DIN2: Ptr(Const(Float64))
) -> Bool: ...

@bind("DLALN2")
@external
def dlaln2(
    LTRANS: Ptr(Bool),
    NA: Ptr(Int32),
    NW: Ptr(Int32),
    SMIN: Ptr(Float64),
    CA: Ptr(Float64),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    D1: Ptr(Float64),
    D2: Ptr(Float64),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    WR: Ptr(Float64),
    WI: Ptr(Float64),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    SCALE: Ptr(Float64),
    XNORM: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLALS0")
@external
def dlals0(
    ICOMPQ: Ptr(Int32),
    NL: Ptr(Int32),
    NR: Ptr(Int32),
    SQRE: Ptr(Int32),
    NRHS: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    BX: Float64[LDBX, Flat],
    LDBX: Ptr(Int32),
    PERM: Int32[Flat],
    GIVPTR: Ptr(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ptr(Int32),
    GIVNUM: Float64[LDGNUM, Flat],
    LDGNUM: Ptr(Int32),
    POLES: Float64[LDGNUM, Flat],
    DIFL: Float64[Flat],
    DIFR: Float64[LDGNUM, Flat],
    Z: Float64[Flat],
    K: Ptr(Int32),
    C: Ptr(Float64),
    S: Ptr(Float64),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLALSA")
@external
def dlalsa(
    ICOMPQ: Ptr(Int32),
    SMLSIZ: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    BX: Float64[LDBX, Flat],
    LDBX: Ptr(Int32),
    U: Float64[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Float64[LDU, Flat],
    K: Int32[Flat],
    DIFL: Float64[LDU, Flat],
    DIFR: Float64[LDU, Flat],
    Z: Float64[LDU, Flat],
    POLES: Float64[LDU, Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ptr(Int32),
    PERM: Int32[LDGCOL, Flat],
    GIVNUM: Float64[LDU, Flat],
    C: Float64[Flat],
    S: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLALSD")
@external
def dlalsd(
    UPLO: Ptr(Const(String[1])),
    SMLSIZ: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    RCOND: Ptr(Float64),
    RANK: Ptr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
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

@bind("DLAMSWLQ")
@external
def dlamswlq(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAMTSQR")
@external
def dlamtsqr(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLANEG")
@external
def dlaneg(
    N: Ptr(Int32),
    D: Float64[Flat],
    LLD: Float64[Flat],
    SIGMA: Ptr(Float64),
    PIVMIN: Ptr(Float64),
    R: Ptr(Int32)
) -> Int32: ...

@bind("DLANGB")
@external
def dlangb(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANGE")
@external
def dlange(
    NORM: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANGT")
@external
def dlangt(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    DL: Float64[Flat],
    D: Float64[Flat],
    DU: Float64[Flat]
) -> Float64: ...

@bind("DLANHS")
@external
def dlanhs(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANSB")
@external
def dlansb(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANSF")
@external
def dlansf(
    NORM: Ptr(Const(String[1])),
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Float64[Flat], SourceDims("0:*")],
    WORK: Annotated[Float64[Flat], SourceDims("0:*")]
) -> Float64: ...

@bind("DLANSP")
@external
def dlansp(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANST")
@external
def dlanst(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat]
) -> Float64: ...

@bind("DLANSY")
@external
def dlansy(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANTB")
@external
def dlantb(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANTP")
@external
def dlantp(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANTR")
@external
def dlantr(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("DLANV2")
@external
def dlanv2(
    A: Ptr(Float64),
    B: Ptr(Float64),
    C: Ptr(Float64),
    D: Ptr(Float64),
    RT1R: Ptr(Float64),
    RT1I: Ptr(Float64),
    RT2R: Ptr(Float64),
    RT2I: Ptr(Float64),
    CS: Ptr(Float64),
    SN: Ptr(Float64)
) -> None: ...

@bind("DLAORHR_COL_GETRFNP")
@external
def dlaorhr_col_getrfnp(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAORHR_COL_GETRFNP2")
@external
def dlaorhr_col_getrfnp2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAPLL")
@external
def dlapll(
    N: Ptr(Int32),
    X: Float64[Flat],
    INCX: Ptr(Int32),
    Y: Float64[Flat],
    INCY: Ptr(Int32),
    SSMIN: Ptr(Float64)
) -> None: ...

@bind("DLAPMR")
@external
def dlapmr(
    FORWRD: Ptr(Bool),
    M: Ptr(Int32),
    N: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("DLAPMT")
@external
def dlapmt(
    FORWRD: Ptr(Bool),
    M: Ptr(Int32),
    N: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("DLAPY2")
@external
def dlapy2(
    X: Ptr(Float64),
    Y: Ptr(Float64)
) -> Float64: ...

@bind("DLAPY3")
@external
def dlapy3(
    X: Ptr(Float64),
    Y: Ptr(Float64),
    Z: Ptr(Float64)
) -> Float64: ...

@bind("DLAQGB")
@external
def dlaqgb(
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ptr(Float64),
    COLCND: Ptr(Float64),
    AMAX: Ptr(Float64),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("DLAQGE")
@external
def dlaqge(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ptr(Float64),
    COLCND: Ptr(Float64),
    AMAX: Ptr(Float64),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("DLAQP2")
@external
def dlaqp2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    OFFSET: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    JPVT: Int32[Flat],
    TAU: Float64[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    WORK: Float64[Flat]
) -> None: ...

@bind("DLAQP2RK")
@external
def dlaqp2rk(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    IOFFSET: Ptr(Int32),
    KMAX: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    RELTOL: Ptr(Float64),
    KP1: Ptr(Int32),
    MAXC2NRM: Ptr(Float64),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    K: Ptr(Int32),
    MAXC2NRMK: Ptr(Float64),
    RELMAXC2NRMK: Ptr(Float64),
    JPIV: Int32[Flat],
    TAU: Float64[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAQP3RK")
@external
def dlaqp3rk(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    IOFFSET: Ptr(Int32),
    NB: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    RELTOL: Ptr(Float64),
    KP1: Ptr(Int32),
    MAXC2NRM: Ptr(Float64),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    DONE: Ptr(Bool),
    KB: Ptr(Int32),
    MAXC2NRMK: Ptr(Float64),
    RELMAXC2NRMK: Ptr(Float64),
    JPIV: Int32[Flat],
    TAU: Float64[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    AUXV: Float64[Flat],
    F: Float64[LDF, Flat],
    LDF: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAQPS")
@external
def dlaqps(
    M: Ptr(Int32),
    N: Ptr(Int32),
    OFFSET: Ptr(Int32),
    NB: Ptr(Int32),
    KB: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    JPVT: Int32[Flat],
    TAU: Float64[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    AUXV: Float64[Flat],
    F: Float64[LDF, Flat],
    LDF: Ptr(Int32)
) -> None: ...

@bind("DLAQR0")
@external
def dlaqr0(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    H: Float64[LDH, Flat],
    LDH: Ptr(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAQR1")
@external
def dlaqr1(
    N: Ptr(Int32),
    H: Float64[LDH, Flat],
    LDH: Ptr(Int32),
    SR1: Ptr(Float64),
    SI1: Ptr(Float64),
    SR2: Ptr(Float64),
    SI2: Ptr(Float64),
    V: Float64[Flat]
) -> None: ...

@bind("DLAQR2")
@external
def dlaqr2(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    KTOP: Ptr(Int32),
    KBOT: Ptr(Int32),
    NW: Ptr(Int32),
    H: Float64[LDH, Flat],
    LDH: Ptr(Int32),
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    NS: Ptr(Int32),
    ND: Ptr(Int32),
    SR: Float64[Flat],
    SI: Float64[Flat],
    V: Float64[LDV, Flat],
    LDV: Ptr(Int32),
    NH: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    NV: Ptr(Int32),
    WV: Float64[LDWV, Flat],
    LDWV: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32)
) -> None: ...

@bind("DLAQR3")
@external
def dlaqr3(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    KTOP: Ptr(Int32),
    KBOT: Ptr(Int32),
    NW: Ptr(Int32),
    H: Float64[LDH, Flat],
    LDH: Ptr(Int32),
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    NS: Ptr(Int32),
    ND: Ptr(Int32),
    SR: Float64[Flat],
    SI: Float64[Flat],
    V: Float64[LDV, Flat],
    LDV: Ptr(Int32),
    NH: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    NV: Ptr(Int32),
    WV: Float64[LDWV, Flat],
    LDWV: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32)
) -> None: ...

@bind("DLAQR4")
@external
def dlaqr4(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    H: Float64[LDH, Flat],
    LDH: Ptr(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAQR5")
@external
def dlaqr5(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    KACC22: Ptr(Int32),
    N: Ptr(Int32),
    KTOP: Ptr(Int32),
    KBOT: Ptr(Int32),
    NSHFTS: Ptr(Int32),
    SR: Float64[Flat],
    SI: Float64[Flat],
    H: Float64[LDH, Flat],
    LDH: Ptr(Int32),
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    V: Float64[LDV, Flat],
    LDV: Ptr(Int32),
    U: Float64[LDU, Flat],
    LDU: Ptr(Int32),
    NV: Ptr(Int32),
    WV: Float64[LDWV, Flat],
    LDWV: Ptr(Int32),
    NH: Ptr(Int32),
    WH: Float64[LDWH, Flat],
    LDWH: Ptr(Int32)
) -> None: ...

@bind("DLAQSB")
@external
def dlaqsb(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    S: Float64[Flat],
    SCOND: Ptr(Float64),
    AMAX: Ptr(Float64),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("DLAQSP")
@external
def dlaqsp(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    S: Float64[Flat],
    SCOND: Ptr(Float64),
    AMAX: Ptr(Float64),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("DLAQSY")
@external
def dlaqsy(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float64[Flat],
    SCOND: Ptr(Float64),
    AMAX: Ptr(Float64),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("DLAQTR")
@external
def dlaqtr(
    LTRAN: Ptr(Bool),
    LREAL: Ptr(Bool),
    N: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    B: Float64[Flat],
    W: Ptr(Float64),
    SCALE: Ptr(Float64),
    X: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAQZ0")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7), Arg(8), Arg(9), Arg(10), Arg(11), Arg(12), Arg(13), Arg(14), Arg(15), Arg(16), Arg(17), Arg(18), Arg(19), Return('INFO', 0)])
def dlaqz0(
    WANTS: Ptr(Const(String[1])),
    WANTQ: Ptr(Const(String[1])),
    WANTZ: Ptr(Const(String[1])),
    N: Ptr(Const(Int32)),
    ILO: Ptr(Const(Int32)),
    IHI: Ptr(Const(Int32)),
    A: Float64[LDA, Flat],
    LDA: Ptr(Const(Int32)),
    B: Float64[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Const(Int32)),
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Const(Int32)),
    WORK: Float64[Flat],
    LWORK: Ptr(Const(Int32)),
    REC: Ptr(Const(Int32))
) -> Int32: ...

@bind("DLAQZ1")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7), Arg(8), Arg(9)])
def dlaqz1(
    A: Const(Float64[LDA, Flat]),
    LDA: Ptr(Const(Int32)),
    B: Const(Float64[LDB, Flat]),
    LDB: Ptr(Const(Int32)),
    SR1: Ptr(Const(Float64)),
    SR2: Ptr(Const(Float64)),
    SI: Ptr(Const(Float64)),
    BETA1: Ptr(Const(Float64)),
    BETA2: Ptr(Const(Float64)),
    V: Float64[Flat]
) -> Returns["V", Float64[Flat]]: ...

@bind("DLAQZ2")
@external
def dlaqz2(
    ILQ: Ptr(Const(Bool)),
    ILZ: Ptr(Const(Bool)),
    K: Ptr(Const(Int32)),
    ISTARTM: Ptr(Const(Int32)),
    ISTOPM: Ptr(Const(Int32)),
    IHI: Ptr(Const(Int32)),
    A: Float64[LDA, Flat],
    LDA: Ptr(Const(Int32)),
    B: Float64[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    NQ: Ptr(Const(Int32)),
    QSTART: Ptr(Const(Int32)),
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Const(Int32)),
    NZ: Ptr(Const(Int32)),
    ZSTART: Ptr(Const(Int32)),
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Const(Int32))
) -> None: ...

@bind("DLAQZ3")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7), Arg(8), Arg(9), Arg(10), Arg(11), Arg(12), Arg(13), Arg(14), Return('NS', 0), Return('ND', 1), Arg(15), Arg(16), Arg(17), Arg(18), Arg(19), Arg(20), Arg(21), Arg(22), Arg(23), Arg(24), Return('INFO', 2)])
def dlaqz3(
    ILSCHUR: Ptr(Const(Bool)),
    ILQ: Ptr(Const(Bool)),
    ILZ: Ptr(Const(Bool)),
    N: Ptr(Const(Int32)),
    ILO: Ptr(Const(Int32)),
    IHI: Ptr(Const(Int32)),
    NW: Ptr(Const(Int32)),
    A: Float64[LDA, Flat],
    LDA: Ptr(Const(Int32)),
    B: Float64[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Const(Int32)),
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Const(Int32)),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    QC: Float64[LDQC, Flat],
    LDQC: Ptr(Const(Int32)),
    ZC: Float64[LDZC, Flat],
    LDZC: Ptr(Const(Int32)),
    WORK: Float64[Flat],
    LWORK: Ptr(Const(Int32)),
    REC: Ptr(Const(Int32))
) -> tuple[Int32, Int32, Int32]: ...

@bind("DLAQZ4")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7), Arg(8), Arg(9), Arg(10), Arg(11), Arg(12), Arg(13), Arg(14), Arg(15), Arg(16), Arg(17), Arg(18), Arg(19), Arg(20), Arg(21), Arg(22), Arg(23), Arg(24), Return('INFO', 0)])
def dlaqz4(
    ILSCHUR: Ptr(Const(Bool)),
    ILQ: Ptr(Const(Bool)),
    ILZ: Ptr(Const(Bool)),
    N: Ptr(Const(Int32)),
    ILO: Ptr(Const(Int32)),
    IHI: Ptr(Const(Int32)),
    NSHIFTS: Ptr(Const(Int32)),
    NBLOCK_DESIRED: Ptr(Const(Int32)),
    SR: Float64[Flat],
    SI: Float64[Flat],
    SS: Float64[Flat],
    A: Float64[LDA, Flat],
    LDA: Ptr(Const(Int32)),
    B: Float64[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Const(Int32)),
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Const(Int32)),
    QC: Float64[LDQC, Flat],
    LDQC: Ptr(Const(Int32)),
    ZC: Float64[LDZC, Flat],
    LDZC: Ptr(Const(Int32)),
    WORK: Float64[Flat],
    LWORK: Ptr(Const(Int32))
) -> Int32: ...

@bind("DLAR1V")
@external
def dlar1v(
    N: Ptr(Int32),
    B1: Ptr(Int32),
    BN: Ptr(Int32),
    LAMBDA: Ptr(Float64),
    D: Float64[Flat],
    L: Float64[Flat],
    LD: Float64[Flat],
    LLD: Float64[Flat],
    PIVMIN: Ptr(Float64),
    GAPTOL: Ptr(Float64),
    Z: Float64[Flat],
    WANTNC: Ptr(Bool),
    NEGCNT: Ptr(Int32),
    ZTZ: Ptr(Float64),
    MINGMA: Ptr(Float64),
    R: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    NRMINV: Ptr(Float64),
    RESID: Ptr(Float64),
    RQCORR: Ptr(Float64),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLAR2V")
@external
def dlar2v(
    N: Ptr(Int32),
    X: Float64[Flat],
    Y: Float64[Flat],
    Z: Float64[Flat],
    INCX: Ptr(Int32),
    C: Float64[Flat],
    S: Float64[Flat],
    INCC: Ptr(Int32)
) -> None: ...

@bind("DLARF")
@external
def dlarf(
    SIDE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    V: Float64[Flat],
    INCV: Ptr(Int32),
    TAU: Ptr(Float64),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLARF1F")
@external
def dlarf1f(
    SIDE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    V: Float64[Flat],
    INCV: Ptr(Int32),
    TAU: Ptr(Float64),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLARF1L")
@external
def dlarf1l(
    SIDE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    V: Float64[Flat],
    INCV: Ptr(Int32),
    TAU: Ptr(Float64),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLARFB")
@external
def dlarfb(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIRECT: Ptr(Const(String[1])),
    STOREV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    V: Float64[LDV, Flat],
    LDV: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[LDWORK, Flat],
    LDWORK: Ptr(Int32)
) -> None: ...

@bind("DLARFB_GETT")
@external
def dlarfb_gett(
    IDENT: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float64[LDWORK, Flat],
    LDWORK: Ptr(Int32)
) -> None: ...

@bind("DLARFG")
@external
def dlarfg(
    N: Ptr(Int32),
    ALPHA: Ptr(Float64),
    X: Float64[Flat],
    INCX: Ptr(Int32),
    TAU: Ptr(Float64)
) -> None: ...

@bind("DLARFGP")
@external
def dlarfgp(
    N: Ptr(Int32),
    ALPHA: Ptr(Float64),
    X: Float64[Flat],
    INCX: Ptr(Int32),
    TAU: Ptr(Float64)
) -> None: ...

@bind("DLARFT")
@external
def dlarft(
    DIRECT: Ptr(Const(String[1])),
    STOREV: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    V: Float64[LDV, Flat],
    LDV: Ptr(Int32),
    TAU: Float64[Flat],
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32)
) -> None: ...

@bind("DLARFX")
@external
def dlarfx(
    SIDE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    V: Float64[Flat],
    TAU: Ptr(Float64),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLARFY")
@external
def dlarfy(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    V: Float64[Flat],
    INCV: Ptr(Int32),
    TAU: Ptr(Float64),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLARGV")
@external
def dlargv(
    N: Ptr(Int32),
    X: Float64[Flat],
    INCX: Ptr(Int32),
    Y: Float64[Flat],
    INCY: Ptr(Int32),
    C: Float64[Flat],
    INCC: Ptr(Int32)
) -> None: ...

@bind("DLARMM")
@external
def dlarmm(
    ANORM: Ptr(Float64),
    BNORM: Ptr(Float64),
    CNORM: Ptr(Float64)
) -> Float64: ...

@bind("DLARNV")
@external
def dlarnv(
    IDIST: Ptr(Int32),
    ISEED: Int32[4],
    N: Ptr(Int32),
    X: Float64[Flat]
) -> None: ...

@bind("DLARRA")
@external
def dlarra(
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    E2: Float64[Flat],
    SPLTOL: Ptr(Float64),
    TNRM: Ptr(Float64),
    NSPLIT: Ptr(Int32),
    ISPLIT: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLARRB")
@external
def dlarrb(
    N: Ptr(Int32),
    D: Float64[Flat],
    LLD: Float64[Flat],
    IFIRST: Ptr(Int32),
    ILAST: Ptr(Int32),
    RTOL1: Ptr(Float64),
    RTOL2: Ptr(Float64),
    OFFSET: Ptr(Int32),
    W: Float64[Flat],
    WGAP: Float64[Flat],
    WERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    PIVMIN: Ptr(Float64),
    SPDIAM: Ptr(Float64),
    TWIST: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLARRC")
@external
def dlarrc(
    JOBT: Ptr(Const(String[1])),
    N: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    D: Float64[Flat],
    E: Float64[Flat],
    PIVMIN: Ptr(Float64),
    EIGCNT: Ptr(Int32),
    LCNT: Ptr(Int32),
    RCNT: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLARRD")
@external
def dlarrd(
    RANGE: Ptr(Const(String[1])),
    ORDER: Ptr(Const(String[1])),
    N: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    GERS: Float64[Flat],
    RELTOL: Ptr(Float64),
    D: Float64[Flat],
    E: Float64[Flat],
    E2: Float64[Flat],
    PIVMIN: Ptr(Float64),
    NSPLIT: Ptr(Int32),
    ISPLIT: Int32[Flat],
    M: Ptr(Int32),
    W: Float64[Flat],
    WERR: Float64[Flat],
    WL: Ptr(Float64),
    WU: Ptr(Float64),
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLARRE")
@external
def dlarre(
    RANGE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    E2: Float64[Flat],
    RTOL1: Ptr(Float64),
    RTOL2: Ptr(Float64),
    SPLTOL: Ptr(Float64),
    NSPLIT: Ptr(Int32),
    ISPLIT: Int32[Flat],
    M: Ptr(Int32),
    W: Float64[Flat],
    WERR: Float64[Flat],
    WGAP: Float64[Flat],
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    GERS: Float64[Flat],
    PIVMIN: Ptr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLARRF")
@external
def dlarrf(
    N: Ptr(Int32),
    D: Float64[Flat],
    L: Float64[Flat],
    LD: Float64[Flat],
    CLSTRT: Ptr(Int32),
    CLEND: Ptr(Int32),
    W: Float64[Flat],
    WGAP: Float64[Flat],
    WERR: Float64[Flat],
    SPDIAM: Ptr(Float64),
    CLGAPL: Ptr(Float64),
    CLGAPR: Ptr(Float64),
    PIVMIN: Ptr(Float64),
    SIGMA: Ptr(Float64),
    DPLUS: Float64[Flat],
    LPLUS: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLARRJ")
@external
def dlarrj(
    N: Ptr(Int32),
    D: Float64[Flat],
    E2: Float64[Flat],
    IFIRST: Ptr(Int32),
    ILAST: Ptr(Int32),
    RTOL: Ptr(Float64),
    OFFSET: Ptr(Int32),
    W: Float64[Flat],
    WERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    PIVMIN: Ptr(Float64),
    SPDIAM: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLARRK")
@external
def dlarrk(
    N: Ptr(Int32),
    IW: Ptr(Int32),
    GL: Ptr(Float64),
    GU: Ptr(Float64),
    D: Float64[Flat],
    E2: Float64[Flat],
    PIVMIN: Ptr(Float64),
    RELTOL: Ptr(Float64),
    W: Ptr(Float64),
    WERR: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLARRR")
@external
def dlarrr(
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLARRV")
@external
def dlarrv(
    N: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    D: Float64[Flat],
    L: Float64[Flat],
    PIVMIN: Ptr(Float64),
    ISPLIT: Int32[Flat],
    M: Ptr(Int32),
    DOL: Ptr(Int32),
    DOU: Ptr(Int32),
    MINRGP: Ptr(Float64),
    RTOL1: Ptr(Float64),
    RTOL2: Ptr(Float64),
    W: Float64[Flat],
    WERR: Float64[Flat],
    WGAP: Float64[Flat],
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    GERS: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLARSCL2")
@external
def dlarscl2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    D: Float64[Flat],
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32)
) -> None: ...

@bind("DLARTG")
@external
def dlartg(
    f: Ptr(Float64),
    g: Ptr(Float64),
    c: Ptr(Float64),
    s: Ptr(Float64),
    r: Ptr(Float64)
) -> None: ...

@bind("DLARTGP")
@external
def dlartgp(
    F: Ptr(Float64),
    G: Ptr(Float64),
    CS: Ptr(Float64),
    SN: Ptr(Float64),
    R: Ptr(Float64)
) -> None: ...

@bind("DLARTGS")
@external
def dlartgs(
    X: Ptr(Float64),
    Y: Ptr(Float64),
    SIGMA: Ptr(Float64),
    CS: Ptr(Float64),
    SN: Ptr(Float64)
) -> None: ...

@bind("DLARTV")
@external
def dlartv(
    N: Ptr(Int32),
    X: Float64[Flat],
    INCX: Ptr(Int32),
    Y: Float64[Flat],
    INCY: Ptr(Int32),
    C: Float64[Flat],
    S: Float64[Flat],
    INCC: Ptr(Int32)
) -> None: ...

@bind("DLARUV")
@external
def dlaruv(
    ISEED: Int32[4],
    N: Ptr(Int32),
    X: Float64[N]
) -> None: ...

@bind("DLARZ")
@external
def dlarz(
    SIDE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    V: Float64[Flat],
    INCV: Ptr(Int32),
    TAU: Ptr(Float64),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLARZB")
@external
def dlarzb(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIRECT: Ptr(Const(String[1])),
    STOREV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    V: Float64[LDV, Flat],
    LDV: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[LDWORK, Flat],
    LDWORK: Ptr(Int32)
) -> None: ...

@bind("DLARZT")
@external
def dlarzt(
    DIRECT: Ptr(Const(String[1])),
    STOREV: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    V: Float64[LDV, Flat],
    LDV: Ptr(Int32),
    TAU: Float64[Flat],
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32)
) -> None: ...

@bind("DLAS2")
@external
def dlas2(
    F: Ptr(Float64),
    G: Ptr(Float64),
    H: Ptr(Float64),
    SSMIN: Ptr(Float64),
    SSMAX: Ptr(Float64)
) -> None: ...

@bind("DLASCL")
@external
def dlascl(
    TYPE: Ptr(Const(String[1])),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    CFROM: Ptr(Float64),
    CTO: Ptr(Float64),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLASCL2")
@external
def dlascl2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    D: Float64[Flat],
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32)
) -> None: ...

@bind("DLASD0")
@external
def dlasd0(
    N: Ptr(Int32),
    SQRE: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Ptr(Int32),
    SMLSIZ: Ptr(Int32),
    IWORK: Int32[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLASD1")
@external
def dlasd1(
    NL: Ptr(Int32),
    NR: Ptr(Int32),
    SQRE: Ptr(Int32),
    D: Float64[Flat],
    ALPHA: Ptr(Float64),
    BETA: Ptr(Float64),
    U: Float64[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Ptr(Int32),
    IDXQ: Int32[Flat],
    IWORK: Int32[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLASD2")
@external
def dlasd2(
    NL: Ptr(Int32),
    NR: Ptr(Int32),
    SQRE: Ptr(Int32),
    K: Ptr(Int32),
    D: Float64[Flat],
    Z: Float64[Flat],
    ALPHA: Ptr(Float64),
    BETA: Ptr(Float64),
    U: Float64[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Ptr(Int32),
    DSIGMA: Float64[Flat],
    U2: Float64[LDU2, Flat],
    LDU2: Ptr(Int32),
    VT2: Float64[LDVT2, Flat],
    LDVT2: Ptr(Int32),
    IDXP: Int32[Flat],
    IDX: Int32[Flat],
    IDXC: Int32[Flat],
    IDXQ: Int32[Flat],
    COLTYP: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLASD3")
@external
def dlasd3(
    NL: Ptr(Int32),
    NR: Ptr(Int32),
    SQRE: Ptr(Int32),
    K: Ptr(Int32),
    D: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    DSIGMA: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Ptr(Int32),
    U2: Float64[LDU2, Flat],
    LDU2: Ptr(Int32),
    VT: Float64[LDVT, Flat],
    LDVT: Ptr(Int32),
    VT2: Float64[LDVT2, Flat],
    LDVT2: Ptr(Int32),
    IDXC: Int32[Flat],
    CTOT: Int32[Flat],
    Z: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLASD4")
@external
def dlasd4(
    N: Ptr(Int32),
    I: Ptr(Int32),
    D: Float64[Flat],
    Z: Float64[Flat],
    DELTA: Float64[Flat],
    RHO: Ptr(Float64),
    SIGMA: Ptr(Float64),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLASD5")
@external
def dlasd5(
    I: Ptr(Int32),
    D: Float64[2],
    Z: Float64[2],
    DELTA: Float64[2],
    RHO: Ptr(Float64),
    DSIGMA: Ptr(Float64),
    WORK: Float64[2]
) -> None: ...

@bind("DLASD6")
@external
def dlasd6(
    ICOMPQ: Ptr(Int32),
    NL: Ptr(Int32),
    NR: Ptr(Int32),
    SQRE: Ptr(Int32),
    D: Float64[Flat],
    VF: Float64[Flat],
    VL: Float64[Flat],
    ALPHA: Ptr(Float64),
    BETA: Ptr(Float64),
    IDXQ: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Ptr(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ptr(Int32),
    GIVNUM: Float64[LDGNUM, Flat],
    LDGNUM: Ptr(Int32),
    POLES: Float64[LDGNUM, Flat],
    DIFL: Float64[Flat],
    DIFR: Float64[Flat],
    Z: Float64[Flat],
    K: Ptr(Int32),
    C: Ptr(Float64),
    S: Ptr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLASD7")
@external
def dlasd7(
    ICOMPQ: Ptr(Int32),
    NL: Ptr(Int32),
    NR: Ptr(Int32),
    SQRE: Ptr(Int32),
    K: Ptr(Int32),
    D: Float64[Flat],
    Z: Float64[Flat],
    ZW: Float64[Flat],
    VF: Float64[Flat],
    VFW: Float64[Flat],
    VL: Float64[Flat],
    VLW: Float64[Flat],
    ALPHA: Ptr(Float64),
    BETA: Ptr(Float64),
    DSIGMA: Float64[Flat],
    IDX: Int32[Flat],
    IDXP: Int32[Flat],
    IDXQ: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Ptr(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ptr(Int32),
    GIVNUM: Float64[LDGNUM, Flat],
    LDGNUM: Ptr(Int32),
    C: Ptr(Float64),
    S: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLASD8")
@external
def dlasd8(
    ICOMPQ: Ptr(Int32),
    K: Ptr(Int32),
    D: Float64[Flat],
    Z: Float64[Flat],
    VF: Float64[Flat],
    VL: Float64[Flat],
    DIFL: Float64[Flat],
    DIFR: Float64[LDDIFR, Flat],
    LDDIFR: Ptr(Int32),
    DSIGMA: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLASDA")
@external
def dlasda(
    ICOMPQ: Ptr(Int32),
    SMLSIZ: Ptr(Int32),
    N: Ptr(Int32),
    SQRE: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Float64[LDU, Flat],
    K: Int32[Flat],
    DIFL: Float64[LDU, Flat],
    DIFR: Float64[LDU, Flat],
    Z: Float64[LDU, Flat],
    POLES: Float64[LDU, Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ptr(Int32),
    PERM: Int32[LDGCOL, Flat],
    GIVNUM: Float64[LDU, Flat],
    C: Float64[Flat],
    S: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLASDQ")
@external
def dlasdq(
    UPLO: Ptr(Const(String[1])),
    SQRE: Ptr(Int32),
    N: Ptr(Int32),
    NCVT: Ptr(Int32),
    NRU: Ptr(Int32),
    NCC: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VT: Float64[LDVT, Flat],
    LDVT: Ptr(Int32),
    U: Float64[LDU, Flat],
    LDU: Ptr(Int32),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLASDT")
@external
def dlasdt(
    N: Ptr(Int32),
    LVL: Ptr(Int32),
    ND: Ptr(Int32),
    INODE: Int32[Flat],
    NDIML: Int32[Flat],
    NDIMR: Int32[Flat],
    MSUB: Ptr(Int32)
) -> None: ...

@bind("DLASET")
@external
def dlaset(
    UPLO: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Float64),
    BETA: Ptr(Float64),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("DLASQ1")
@external
def dlasq1(
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLASQ2")
@external
def dlasq2(
    N: Ptr(Int32),
    Z: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLASQ3")
@external
def dlasq3(
    I0: Ptr(Int32),
    N0: Ptr(Int32),
    Z: Float64[Flat],
    PP: Ptr(Int32),
    DMIN: Ptr(Float64),
    SIGMA: Ptr(Float64),
    DESIG: Ptr(Float64),
    QMAX: Ptr(Float64),
    NFAIL: Ptr(Int32),
    ITER: Ptr(Int32),
    NDIV: Ptr(Int32),
    IEEE: Ptr(Bool),
    TTYPE: Ptr(Int32),
    DMIN1: Ptr(Float64),
    DMIN2: Ptr(Float64),
    DN: Ptr(Float64),
    DN1: Ptr(Float64),
    DN2: Ptr(Float64),
    G: Ptr(Float64),
    TAU: Ptr(Float64)
) -> None: ...

@bind("DLASQ4")
@external
def dlasq4(
    I0: Ptr(Int32),
    N0: Ptr(Int32),
    Z: Float64[Flat],
    PP: Ptr(Int32),
    N0IN: Ptr(Int32),
    DMIN: Ptr(Float64),
    DMIN1: Ptr(Float64),
    DMIN2: Ptr(Float64),
    DN: Ptr(Float64),
    DN1: Ptr(Float64),
    DN2: Ptr(Float64),
    TAU: Ptr(Float64),
    TTYPE: Ptr(Int32),
    G: Ptr(Float64)
) -> None: ...

@bind("DLASQ5")
@external
def dlasq5(
    I0: Ptr(Int32),
    N0: Ptr(Int32),
    Z: Float64[Flat],
    PP: Ptr(Int32),
    TAU: Ptr(Float64),
    SIGMA: Ptr(Float64),
    DMIN: Ptr(Float64),
    DMIN1: Ptr(Float64),
    DMIN2: Ptr(Float64),
    DN: Ptr(Float64),
    DNM1: Ptr(Float64),
    DNM2: Ptr(Float64),
    IEEE: Ptr(Bool),
    EPS: Ptr(Float64)
) -> None: ...

@bind("DLASQ6")
@external
def dlasq6(
    I0: Ptr(Int32),
    N0: Ptr(Int32),
    Z: Float64[Flat],
    PP: Ptr(Int32),
    DMIN: Ptr(Float64),
    DMIN1: Ptr(Float64),
    DMIN2: Ptr(Float64),
    DN: Ptr(Float64),
    DNM1: Ptr(Float64),
    DNM2: Ptr(Float64)
) -> None: ...

@bind("DLASR")
@external
def dlasr(
    SIDE: Ptr(Const(String[1])),
    PIVOT: Ptr(Const(String[1])),
    DIRECT: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    C: Float64[Flat],
    S: Float64[Flat],
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("DLASRT")
@external
def dlasrt(
    ID: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLASSQ")
@external
def dlassq(
    n: Ptr(Int32),
    x: Float64[Flat],
    incx: Ptr(Int32),
    scale: Ptr(Float64),
    sumsq: Ptr(Float64)
) -> None: ...

@bind("DLASV2")
@external
def dlasv2(
    F: Ptr(Float64),
    G: Ptr(Float64),
    H: Ptr(Float64),
    SSMIN: Ptr(Float64),
    SSMAX: Ptr(Float64),
    SNR: Ptr(Float64),
    CSR: Ptr(Float64),
    SNL: Ptr(Float64),
    CSL: Ptr(Float64)
) -> None: ...

@bind("DLASWLQ")
@external
def dlaswlq(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLASWP")
@external
def dlaswp(
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    K1: Ptr(Int32),
    K2: Ptr(Int32),
    IPIV: Int32[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("DLASY2")
@external
def dlasy2(
    LTRANL: Ptr(Bool),
    LTRANR: Ptr(Bool),
    ISGN: Ptr(Int32),
    N1: Ptr(Int32),
    N2: Ptr(Int32),
    TL: Float64[LDTL, Flat],
    LDTL: Ptr(Int32),
    TR: Float64[LDTR, Flat],
    LDTR: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    SCALE: Ptr(Float64),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    XNORM: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLASYF")
@external
def dlasyf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    KB: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    W: Float64[LDW, Flat],
    LDW: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLASYF_AA")
@external
def dlasyf_aa(
    UPLO: Ptr(Const(String[1])),
    J1: Ptr(Int32),
    M: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    H: Float64[LDH, Flat],
    LDH: Ptr(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DLASYF_RK")
@external
def dlasyf_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    KB: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    W: Float64[LDW, Flat],
    LDW: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLASYF_ROOK")
@external
def dlasyf_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    KB: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    W: Float64[LDW, Flat],
    LDW: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAT2S")
@external
def dlat2s(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    SA: Float32[LDSA, Flat],
    LDSA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLATBS")
@external
def dlatbs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    NORMIN: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    X: Float64[Flat],
    SCALE: Ptr(Float64),
    CNORM: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLATDF")
@external
def dlatdf(
    IJOB: Ptr(Int32),
    N: Ptr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    RHS: Float64[Flat],
    RDSUM: Ptr(Float64),
    RDSCAL: Ptr(Float64),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat]
) -> None: ...

@bind("DLATPS")
@external
def dlatps(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    NORMIN: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    X: Float64[Flat],
    SCALE: Ptr(Float64),
    CNORM: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLATRD")
@external
def dlatrd(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float64[Flat],
    TAU: Float64[Flat],
    W: Float64[LDW, Flat],
    LDW: Ptr(Int32)
) -> None: ...

@bind("DLATRS")
@external
def dlatrs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    NORMIN: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Float64[Flat],
    SCALE: Ptr(Float64),
    CNORM: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLATRS3")
@external
def dlatrs3(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    NORMIN: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    SCALE: Float64[Flat],
    CNORM: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLATRZ")
@external
def dlatrz(
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat]
) -> None: ...

@bind("DLATSQR")
@external
def dlatsqr(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAUU2")
@external
def dlauu2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DLAUUM")
@external
def dlauum(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DOPGTR")
@external
def dopgtr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    TAU: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DOPMTR")
@external
def dopmtr(
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    AP: Float64[Flat],
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORBDB")
@external
def dorbdb(
    TRANS: Ptr(Const(String[1])),
    SIGNS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Float64[LDX11, Flat],
    LDX11: Ptr(Int32),
    X12: Float64[LDX12, Flat],
    LDX12: Ptr(Int32),
    X21: Float64[LDX21, Flat],
    LDX21: Ptr(Int32),
    X22: Float64[LDX22, Flat],
    LDX22: Ptr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Float64[Flat],
    TAUP2: Float64[Flat],
    TAUQ1: Float64[Flat],
    TAUQ2: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORBDB1")
@external
def dorbdb1(
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Float64[LDX11, Flat],
    LDX11: Ptr(Int32),
    X21: Float64[LDX21, Flat],
    LDX21: Ptr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Float64[Flat],
    TAUP2: Float64[Flat],
    TAUQ1: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORBDB2")
@external
def dorbdb2(
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Float64[LDX11, Flat],
    LDX11: Ptr(Int32),
    X21: Float64[LDX21, Flat],
    LDX21: Ptr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Float64[Flat],
    TAUP2: Float64[Flat],
    TAUQ1: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORBDB3")
@external
def dorbdb3(
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Float64[LDX11, Flat],
    LDX11: Ptr(Int32),
    X21: Float64[LDX21, Flat],
    LDX21: Ptr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Float64[Flat],
    TAUP2: Float64[Flat],
    TAUQ1: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORBDB4")
@external
def dorbdb4(
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Float64[LDX11, Flat],
    LDX11: Ptr(Int32),
    X21: Float64[LDX21, Flat],
    LDX21: Ptr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Float64[Flat],
    TAUP2: Float64[Flat],
    TAUQ1: Float64[Flat],
    PHANTOM: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORBDB5")
@external
def dorbdb5(
    M1: Ptr(Int32),
    M2: Ptr(Int32),
    N: Ptr(Int32),
    X1: Float64[Flat],
    INCX1: Ptr(Int32),
    X2: Float64[Flat],
    INCX2: Ptr(Int32),
    Q1: Float64[LDQ1, Flat],
    LDQ1: Ptr(Int32),
    Q2: Float64[LDQ2, Flat],
    LDQ2: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORBDB6")
@external
def dorbdb6(
    M1: Ptr(Int32),
    M2: Ptr(Int32),
    N: Ptr(Int32),
    X1: Float64[Flat],
    INCX1: Ptr(Int32),
    X2: Float64[Flat],
    INCX2: Ptr(Int32),
    Q1: Float64[LDQ1, Flat],
    LDQ1: Ptr(Int32),
    Q2: Float64[LDQ2, Flat],
    LDQ2: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORCSD")
@external
def dorcsd(
    JOBU1: Ptr(Const(String[1])),
    JOBU2: Ptr(Const(String[1])),
    JOBV1T: Ptr(Const(String[1])),
    JOBV2T: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    SIGNS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Float64[LDX11, Flat],
    LDX11: Ptr(Int32),
    X12: Float64[LDX12, Flat],
    LDX12: Ptr(Int32),
    X21: Float64[LDX21, Flat],
    LDX21: Ptr(Int32),
    X22: Float64[LDX22, Flat],
    LDX22: Ptr(Int32),
    THETA: Float64[Flat],
    U1: Float64[LDU1, Flat],
    LDU1: Ptr(Int32),
    U2: Float64[LDU2, Flat],
    LDU2: Ptr(Int32),
    V1T: Float64[LDV1T, Flat],
    LDV1T: Ptr(Int32),
    V2T: Float64[LDV2T, Flat],
    LDV2T: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORCSD2BY1")
@external
def dorcsd2by1(
    JOBU1: Ptr(Const(String[1])),
    JOBU2: Ptr(Const(String[1])),
    JOBV1T: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Float64[LDX11, Flat],
    LDX11: Ptr(Int32),
    X21: Float64[LDX21, Flat],
    LDX21: Ptr(Int32),
    THETA: Float64[Flat],
    U1: Float64[LDU1, Flat],
    LDU1: Ptr(Int32),
    U2: Float64[LDU2, Flat],
    LDU2: Ptr(Int32),
    V1T: Float64[LDV1T, Flat],
    LDV1T: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORG2L")
@external
def dorg2l(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORG2R")
@external
def dorg2r(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORGBR")
@external
def dorgbr(
    VECT: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORGHR")
@external
def dorghr(
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORGL2")
@external
def dorgl2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORGLQ")
@external
def dorglq(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORGQL")
@external
def dorgql(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORGQR")
@external
def dorgqr(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORGR2")
@external
def dorgr2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORGRQ")
@external
def dorgrq(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORGTR")
@external
def dorgtr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORGTSQR")
@external
def dorgtsqr(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORGTSQR_ROW")
@external
def dorgtsqr_row(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORHR_COL")
@external
def dorhr_col(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    D: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORM22")
@external
def dorm22(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    N1: Ptr(Int32),
    N2: Ptr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORM2L")
@external
def dorm2l(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORM2R")
@external
def dorm2r(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORMBR")
@external
def dormbr(
    VECT: Ptr(Const(String[1])),
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORMHR")
@external
def dormhr(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORML2")
@external
def dorml2(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORMLQ")
@external
def dormlq(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORMQL")
@external
def dormql(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORMQR")
@external
def dormqr(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORMR2")
@external
def dormr2(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORMR3")
@external
def dormr3(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORMRQ")
@external
def dormrq(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORMRZ")
@external
def dormrz(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DORMTR")
@external
def dormtr(
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPBCON")
@external
def dpbcon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPBEQU")
@external
def dpbequ(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    S: Float64[Flat],
    SCOND: Ptr(Float64),
    AMAX: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPBRFS")
@external
def dpbrfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPBSTF")
@external
def dpbstf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPBSV")
@external
def dpbsv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPBSVX")
@external
def dpbsvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Float64[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    EQUED: Ptr(Const(String[1])),
    S: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPBTF2")
@external
def dpbtf2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPBTRF")
@external
def dpbtrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPBTRS")
@external
def dpbtrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPFTRF")
@external
def dpftrf(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Float64[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPFTRI")
@external
def dpftri(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Float64[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPFTRS")
@external
def dpftrs(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Annotated[Float64[Flat], SourceDims("0:*")],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPOCON")
@external
def dpocon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPOEQU")
@external
def dpoequ(
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float64[Flat],
    SCOND: Ptr(Float64),
    AMAX: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPOEQUB")
@external
def dpoequb(
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float64[Flat],
    SCOND: Ptr(Float64),
    AMAX: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPORFS")
@external
def dporfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPORFSX")
@external
def dporfsx(
    UPLO: Ptr(Const(String[1])),
    EQUED: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ptr(Int32),
    S: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPOSV")
@external
def dposv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPOSVX")
@external
def dposvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ptr(Int32),
    EQUED: Ptr(Const(String[1])),
    S: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPOSVXX")
@external
def dposvxx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ptr(Int32),
    EQUED: Ptr(Const(String[1])),
    S: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    RPVGRW: Ptr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPOTF2")
@external
def dpotf2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPOTRF")
@external
def dpotrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPOTRF2")
@external
def dpotrf2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPOTRI")
@external
def dpotri(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPOTRS")
@external
def dpotrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPPCON")
@external
def dppcon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPPEQU")
@external
def dppequ(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    S: Float64[Flat],
    SCOND: Ptr(Float64),
    AMAX: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPPRFS")
@external
def dpprfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Float64[Flat],
    AFP: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPPSV")
@external
def dppsv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPPSVX")
@external
def dppsvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Float64[Flat],
    AFP: Float64[Flat],
    EQUED: Ptr(Const(String[1])),
    S: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPPTRF")
@external
def dpptrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPPTRI")
@external
def dpptri(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPPTRS")
@external
def dpptrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPSTF2")
@external
def dpstf2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    PIV: Int32[N],
    RANK: Ptr(Int32),
    TOL: Ptr(Float64),
    WORK: Float64[2 * N],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPSTRF")
@external
def dpstrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    PIV: Int32[N],
    RANK: Ptr(Int32),
    TOL: Ptr(Float64),
    WORK: Float64[2 * N],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPTCON")
@external
def dptcon(
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPTEQR")
@external
def dpteqr(
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPTRFS")
@external
def dptrfs(
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    DF: Float64[Flat],
    EF: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPTSV")
@external
def dptsv(
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPTSVX")
@external
def dptsvx(
    FACT: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    DF: Float64[Flat],
    EF: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPTTRF")
@external
def dpttrf(
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPTTRS")
@external
def dpttrs(
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DPTTS2")
@external
def dptts2(
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("DRSCL")
@external
def drscl(
    N: Ptr(Int32),
    SA: Ptr(Float64),
    SX: Float64[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("DSB2ST_KERNELS")
@external
def dsb2st_kernels(
    UPLO: Ptr(Const(String[1])),
    WANTZ: Ptr(Bool),
    TTYPE: Ptr(Int32),
    ST: Ptr(Int32),
    ED: Ptr(Int32),
    SWEEP: Ptr(Int32),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    IB: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    V: Float64[Flat],
    TAU: Float64[Flat],
    LDVT: Ptr(Int32),
    WORK: Float64[Flat]
) -> None: ...

@bind("DSBEV")
@external
def dsbev(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSBEV_2STAGE")
@external
def dsbev_2stage(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSBEVD")
@external
def dsbevd(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSBEVD_2STAGE")
@external
def dsbevd_2stage(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSBEVX")
@external
def dsbevx(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSBEVX_2STAGE")
@external
def dsbevx_2stage(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSBGST")
@external
def dsbgst(
    VECT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KA: Ptr(Int32),
    KB: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    BB: Float64[LDBB, Flat],
    LDBB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSBGV")
@external
def dsbgv(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KA: Ptr(Int32),
    KB: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    BB: Float64[LDBB, Flat],
    LDBB: Ptr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSBGVD")
@external
def dsbgvd(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KA: Ptr(Int32),
    KB: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    BB: Float64[LDBB, Flat],
    LDBB: Ptr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSBGVX")
@external
def dsbgvx(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KA: Ptr(Int32),
    KB: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    BB: Float64[LDBB, Flat],
    LDBB: Ptr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSBTRD")
@external
def dsbtrd(
    VECT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSFRK")
@external
def dsfrk(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Float64),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    BETA: Ptr(Float64),
    C: Float64[Flat]
) -> None: ...

@bind("DSGESV")
@external
def dsgesv(
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    WORK: Float64[N, Flat],
    SWORK: Float32[Flat],
    ITER: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSPCON")
@external
def dspcon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    IPIV: Int32[Flat],
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSPEV")
@external
def dspev(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSPEVD")
@external
def dspevd(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSPEVX")
@external
def dspevx(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSPGST")
@external
def dspgst(
    ITYPE: Ptr(Int32),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    BP: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSPGV")
@external
def dspgv(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    BP: Float64[Flat],
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSPGVD")
@external
def dspgvd(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    BP: Float64[Flat],
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSPGVX")
@external
def dspgvx(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    BP: Float64[Flat],
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSPOSV")
@external
def dsposv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    WORK: Float64[N, Flat],
    SWORK: Float32[Flat],
    ITER: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSPRFS")
@external
def dsprfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Float64[Flat],
    AFP: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSPSV")
@external
def dspsv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSPSVX")
@external
def dspsvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Float64[Flat],
    AFP: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSPTRD")
@external
def dsptrd(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSPTRF")
@external
def dsptrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSPTRI")
@external
def dsptri(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSPTRS")
@external
def dsptrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSTEBZ")
@external
def dstebz(
    RANGE: Ptr(Const(String[1])),
    ORDER: Ptr(Const(String[1])),
    N: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    D: Float64[Flat],
    E: Float64[Flat],
    M: Ptr(Int32),
    NSPLIT: Ptr(Int32),
    W: Float64[Flat],
    IBLOCK: Int32[Flat],
    ISPLIT: Int32[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSTEDC")
@external
def dstedc(
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSTEGR")
@external
def dstegr(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSTEIN")
@external
def dstein(
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    M: Ptr(Int32),
    W: Float64[Flat],
    IBLOCK: Int32[Flat],
    ISPLIT: Int32[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSTEMR")
@external
def dstemr(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    NZC: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    TRYRAC: Ptr(Bool),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSTEQR")
@external
def dsteqr(
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSTERF")
@external
def dsterf(
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSTEV")
@external
def dstev(
    JOBZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSTEVD")
@external
def dstevd(
    JOBZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSTEVR")
@external
def dstevr(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSTEVX")
@external
def dstevx(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYCON")
@external
def dsycon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYCON_3")
@external
def dsycon_3(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYCON_ROOK")
@external
def dsycon_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYCONV")
@external
def dsyconv(
    UPLO: Ptr(Const(String[1])),
    WAY: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    E: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYCONVF")
@external
def dsyconvf(
    UPLO: Ptr(Const(String[1])),
    WAY: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYCONVF_ROOK")
@external
def dsyconvf_rook(
    UPLO: Ptr(Const(String[1])),
    WAY: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYEQUB")
@external
def dsyequb(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float64[Flat],
    SCOND: Ptr(Float64),
    AMAX: Ptr(Float64),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYEV")
@external
def dsyev(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    W: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYEV_2STAGE")
@external
def dsyev_2stage(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    W: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYEVD")
@external
def dsyevd(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    W: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYEVD_2STAGE")
@external
def dsyevd_2stage(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    W: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYEVR")
@external
def dsyevr(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYEVR_2STAGE")
@external
def dsyevr_2stage(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYEVX")
@external
def dsyevx(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYEVX_2STAGE")
@external
def dsyevx_2stage(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYGS2")
@external
def dsygs2(
    ITYPE: Ptr(Int32),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYGST")
@external
def dsygst(
    ITYPE: Ptr(Int32),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYGV")
@external
def dsygv(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    W: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYGV_2STAGE")
@external
def dsygv_2stage(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    W: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYGVD")
@external
def dsygvd(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    W: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYGVX")
@external
def dsygvx(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYRFS")
@external
def dsyrfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYRFSX")
@external
def dsyrfsx(
    UPLO: Ptr(Const(String[1])),
    EQUED: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    S: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYSV")
@external
def dsysv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYSV_AA")
@external
def dsysv_aa(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYSV_AA_2STAGE")
@external
def dsysv_aa_2stage(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TB: Float64[Flat],
    LTB: Ptr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYSV_RK")
@external
def dsysv_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYSV_ROOK")
@external
def dsysv_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYSVX")
@external
def dsysvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYSVXX")
@external
def dsysvxx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float64[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    EQUED: Ptr(Const(String[1])),
    S: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    RPVGRW: Ptr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYSWAPR")
@external
def dsyswapr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    I1: Ptr(Int32),
    I2: Ptr(Int32)
) -> None: ...

@bind("DSYTD2")
@external
def dsytd2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTF2")
@external
def dsytf2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTF2_RK")
@external
def dsytf2_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTF2_ROOK")
@external
def dsytf2_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTRD")
@external
def dsytrd(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTRD_2STAGE")
@external
def dsytrd_2stage(
    VECT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Float64[Flat],
    HOUS2: Float64[Flat],
    LHOUS2: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTRD_SB2ST")
@external
def dsytrd_sb2st(
    STAGE1: Ptr(Const(String[1])),
    VECT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    HOUS: Float64[Flat],
    LHOUS: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTRD_SY2SB")
@external
def dsytrd_sy2sb(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTRF")
@external
def dsytrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTRF_AA")
@external
def dsytrf_aa(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTRF_AA_2STAGE")
@external
def dsytrf_aa_2stage(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TB: Float64[Flat],
    LTB: Ptr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTRF_RK")
@external
def dsytrf_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTRF_ROOK")
@external
def dsytrf_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTRI")
@external
def dsytri(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTRI2")
@external
def dsytri2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTRI2X")
@external
def dsytri2x(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[N + NB + 1, Flat],
    NB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTRI_3")
@external
def dsytri_3(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTRI_3X")
@external
def dsytri_3x(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    WORK: Float64[N + NB + 1, Flat],
    NB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTRI_ROOK")
@external
def dsytri_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTRS")
@external
def dsytrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTRS2")
@external
def dsytrs2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTRS_3")
@external
def dsytrs_3(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float64[Flat],
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTRS_AA")
@external
def dsytrs_aa(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTRS_AA_2STAGE")
@external
def dsytrs_aa_2stage(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TB: Float64[Flat],
    LTB: Ptr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DSYTRS_ROOK")
@external
def dsytrs_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTBCON")
@external
def dtbcon(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    RCOND: Ptr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTBRFS")
@external
def dtbrfs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTBTRS")
@external
def dtbtrs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float64[LDAB, Flat],
    LDAB: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTFSM")
@external
def dtfsm(
    TRANSR: Ptr(Const(String[1])),
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Float64),
    A: Annotated[Float64[Flat], SourceDims("0:*")],
    B: Annotated[Float64[0:LDB-1, Flat], SourceDims("0:LDB-1", "0:*")],
    LDB: Ptr(Int32)
) -> None: ...

@bind("DTFTRI")
@external
def dtftri(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Float64[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTFTTP")
@external
def dtfttp(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ARF: Annotated[Float64[Flat], SourceDims("0:*")],
    AP: Annotated[Float64[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTFTTR")
@external
def dtfttr(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ARF: Annotated[Float64[Flat], SourceDims("0:*")],
    A: Annotated[Float64[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTGEVC")
@external
def dtgevc(
    SIDE: Ptr(Const(String[1])),
    HOWMNY: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    S: Float64[LDS, Flat],
    LDS: Ptr(Int32),
    P: Float64[LDP, Flat],
    LDP: Ptr(Int32),
    VL: Float64[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Ptr(Int32),
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTGEX2")
@external
def dtgex2(
    WANTQ: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    J1: Ptr(Int32),
    N1: Ptr(Int32),
    N2: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTGEXC")
@external
def dtgexc(
    WANTQ: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    IFST: Ptr(Int32),
    ILST: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTGSEN")
@external
def dtgsen(
    IJOB: Ptr(Int32),
    WANTQ: Ptr(Bool),
    WANTZ: Ptr(Bool),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    ALPHAR: Float64[Flat],
    ALPHAI: Float64[Flat],
    BETA: Float64[Flat],
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Float64[LDZ, Flat],
    LDZ: Ptr(Int32),
    M: Ptr(Int32),
    PL: Ptr(Float64),
    PR: Ptr(Float64),
    DIF: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTGSJA")
@external
def dtgsja(
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    JOBQ: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    TOLA: Ptr(Float64),
    TOLB: Ptr(Float64),
    ALPHA: Float64[Flat],
    BETA: Float64[Flat],
    U: Float64[LDU, Flat],
    LDU: Ptr(Int32),
    V: Float64[LDV, Flat],
    LDV: Ptr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    WORK: Float64[Flat],
    NCYCLE: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTGSNA")
@external
def dtgsna(
    JOB: Ptr(Const(String[1])),
    HOWMNY: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    VL: Float64[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Ptr(Int32),
    S: Float64[Flat],
    DIF: Float64[Flat],
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTGSY2")
@external
def dtgsy2(
    TRANS: Ptr(Const(String[1])),
    IJOB: Ptr(Int32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    D: Float64[LDD, Flat],
    LDD: Ptr(Int32),
    E: Float64[LDE, Flat],
    LDE: Ptr(Int32),
    F: Float64[LDF, Flat],
    LDF: Ptr(Int32),
    SCALE: Ptr(Float64),
    RDSUM: Ptr(Float64),
    RDSCAL: Ptr(Float64),
    IWORK: Int32[Flat],
    PQ: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTGSYL")
@external
def dtgsyl(
    TRANS: Ptr(Const(String[1])),
    IJOB: Ptr(Int32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    D: Float64[LDD, Flat],
    LDD: Ptr(Int32),
    E: Float64[LDE, Flat],
    LDE: Ptr(Int32),
    F: Float64[LDF, Flat],
    LDF: Ptr(Int32),
    SCALE: Ptr(Float64),
    DIF: Ptr(Float64),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTPCON")
@external
def dtpcon(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    RCOND: Ptr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTPLQT")
@external
def dtplqt(
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    MB: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTPLQT2")
@external
def dtplqt2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTPMLQT")
@external
def dtpmlqt(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    MB: Ptr(Int32),
    V: Float64[LDV, Flat],
    LDV: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTPMQRT")
@external
def dtpmqrt(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    NB: Ptr(Int32),
    V: Float64[LDV, Flat],
    LDV: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTPQRT")
@external
def dtpqrt(
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTPQRT2")
@external
def dtpqrt2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTPRFB")
@external
def dtprfb(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIRECT: Ptr(Const(String[1])),
    STOREV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    V: Float64[LDV, Flat],
    LDV: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float64[LDWORK, Flat],
    LDWORK: Ptr(Int32)
) -> None: ...

@bind("DTPRFS")
@external
def dtprfs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTPTRI")
@external
def dtptri(
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTPTRS")
@external
def dtptrs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Float64[Flat],
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTPTTF")
@external
def dtpttf(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Annotated[Float64[Flat], SourceDims("0:*")],
    ARF: Annotated[Float64[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTPTTR")
@external
def dtpttr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float64[Flat],
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTRCON")
@external
def dtrcon(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    RCOND: Ptr(Float64),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTREVC")
@external
def dtrevc(
    SIDE: Ptr(Const(String[1])),
    HOWMNY: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    VL: Float64[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Ptr(Int32),
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTREVC3")
@external
def dtrevc3(
    SIDE: Ptr(Const(String[1])),
    HOWMNY: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    VL: Float64[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Ptr(Int32),
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTREXC")
@external
def dtrexc(
    COMPQ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    IFST: Ptr(Int32),
    ILST: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTRRFS")
@external
def dtrrfs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float64[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTRSEN")
@external
def dtrsen(
    JOB: Ptr(Const(String[1])),
    COMPQ: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    Q: Float64[LDQ, Flat],
    LDQ: Ptr(Int32),
    WR: Float64[Flat],
    WI: Float64[Flat],
    M: Ptr(Int32),
    S: Ptr(Float64),
    SEP: Ptr(Float64),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTRSNA")
@external
def dtrsna(
    JOB: Ptr(Const(String[1])),
    HOWMNY: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    T: Float64[LDT, Flat],
    LDT: Ptr(Int32),
    VL: Float64[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Float64[LDVR, Flat],
    LDVR: Ptr(Int32),
    S: Float64[Flat],
    SEP: Float64[Flat],
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Float64[LDWORK, Flat],
    LDWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTRSYL")
@external
def dtrsyl(
    TRANA: Ptr(Const(String[1])),
    TRANB: Ptr(Const(String[1])),
    ISGN: Ptr(Int32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    SCALE: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTRSYL3")
@external
def dtrsyl3(
    TRANA: Ptr(Const(String[1])),
    TRANB: Ptr(Const(String[1])),
    ISGN: Ptr(Int32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    C: Float64[LDC, Flat],
    LDC: Ptr(Int32),
    SCALE: Ptr(Float64),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    SWORK: Float64[LDSWORK, Flat],
    LDSWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTRTI2")
@external
def dtrti2(
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTRTRI")
@external
def dtrtri(
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTRTRS")
@external
def dtrtrs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTRTTF")
@external
def dtrttf(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Float64[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Ptr(Int32),
    ARF: Annotated[Float64[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTRTTP")
@external
def dtrttp(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    AP: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("DTZRZF")
@external
def dtzrzf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("DZSUM1")
@external
def dzsum1(
    N: Ptr(Int32),
    CX: Complex128[Flat],
    INCX: Ptr(Int32)
) -> Float64: ...

@bind("ICMAX1")
@external
def icmax1(
    N: Ptr(Int32),
    CX: Complex64[Flat],
    INCX: Ptr(Int32)
) -> Int32: ...

@bind("IEEECK")
@external
def ieeeck(
    ISPEC: Ptr(Int32),
    ZERO: Ptr(Float32),
    ONE: Ptr(Float32)
) -> Int32: ...

@bind("ILACLC")
@external
def ilaclc(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32)
) -> Int32: ...

@bind("ILACLR")
@external
def ilaclr(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex64[LDA, Flat],
    LDA: Ptr(Int32)
) -> Int32: ...

@bind("ILADIAG")
@external
def iladiag(
    DIAG: Ptr(Const(String[1]))
) -> Int32: ...

@bind("ILADLC")
@external
def iladlc(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32)
) -> Int32: ...

@bind("ILADLR")
@external
def iladlr(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32)
) -> Int32: ...

@bind("ILAENV")
@external
def ilaenv(
    ISPEC: Ptr(Int32),
    NAME: Ptr(Const(String)),
    OPTS: Ptr(Const(String)),
    N1: Ptr(Int32),
    N2: Ptr(Int32),
    N3: Ptr(Int32),
    N4: Ptr(Int32)
) -> Int32: ...

@bind("ILAENV2STAGE")
@external
def ilaenv2stage(
    ISPEC: Ptr(Int32),
    NAME: Ptr(Const(String)),
    OPTS: Ptr(Const(String)),
    N1: Ptr(Int32),
    N2: Ptr(Int32),
    N3: Ptr(Int32),
    N4: Ptr(Int32)
) -> Int32: ...

@bind("ILAPREC")
@external
def ilaprec(
    PREC: Ptr(Const(String[1]))
) -> Int32: ...

@bind("ILASLC")
@external
def ilaslc(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32)
) -> Int32: ...

@bind("ILASLR")
@external
def ilaslr(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32)
) -> Int32: ...

@bind("ILATRANS")
@external
def ilatrans(
    TRANS: Ptr(Const(String[1]))
) -> Int32: ...

@bind("ILAUPLO")
@external
def ilauplo(
    UPLO: Ptr(Const(String[1]))
) -> Int32: ...

@bind("ILAZLC")
@external
def ilazlc(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32)
) -> Int32: ...

@bind("ILAZLR")
@external
def ilazlr(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32)
) -> Int32: ...

@bind("IPARAM2STAGE")
@external
def iparam2stage(
    ISPEC: Ptr(Int32),
    NAME: Ptr(Const(String)),
    OPTS: Ptr(Const(String)),
    NI: Ptr(Int32),
    NBI: Ptr(Int32),
    IBI: Ptr(Int32),
    NXI: Ptr(Int32)
) -> Int32: ...

@bind("IPARMQ")
@external
def iparmq(
    ISPEC: Ptr(Int32),
    NAME: String[1][Flat],
    OPTS: String[1][Flat],
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    LWORK: Ptr(Int32)
) -> Int32: ...

@bind("IZMAX1")
@external
def izmax1(
    N: Ptr(Int32),
    ZX: Complex128[Flat],
    INCX: Ptr(Int32)
) -> Int32: ...

@bind("LSAMEN")
@external
def lsamen(
    N: Ptr(Int32),
    CA: Ptr(Const(String)),
    CB: Ptr(Const(String))
) -> Bool: ...

@bind("SBBCSD")
@external
def sbbcsd(
    JOBU1: Ptr(Const(String[1])),
    JOBU2: Ptr(Const(String[1])),
    JOBV1T: Ptr(Const(String[1])),
    JOBV2T: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    U1: Float32[LDU1, Flat],
    LDU1: Ptr(Int32),
    U2: Float32[LDU2, Flat],
    LDU2: Ptr(Int32),
    V1T: Float32[LDV1T, Flat],
    LDV1T: Ptr(Int32),
    V2T: Float32[LDV2T, Flat],
    LDV2T: Ptr(Int32),
    B11D: Float32[Flat],
    B11E: Float32[Flat],
    B12D: Float32[Flat],
    B12E: Float32[Flat],
    B21D: Float32[Flat],
    B21E: Float32[Flat],
    B22D: Float32[Flat],
    B22E: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SBDSDC")
@external
def sbdsdc(
    UPLO: Ptr(Const(String[1])),
    COMPQ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Ptr(Int32),
    Q: Float32[Flat],
    IQ: Int32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SBDSQR")
@external
def sbdsqr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NCVT: Ptr(Int32),
    NRU: Ptr(Int32),
    NCC: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VT: Float32[LDVT, Flat],
    LDVT: Ptr(Int32),
    U: Float32[LDU, Flat],
    LDU: Ptr(Int32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SBDSVDX")
@external
def sbdsvdx(
    UPLO: Ptr(Const(String[1])),
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    NS: Ptr(Int32),
    S: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SCSUM1")
@external
def scsum1(
    N: Ptr(Int32),
    CX: Complex64[Flat],
    INCX: Ptr(Int32)
) -> Float32: ...

@bind("SDISNA")
@external
def sdisna(
    JOB: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    D: Float32[Flat],
    SEP: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGBBRD")
@external
def sgbbrd(
    VECT: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    NCC: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    PT: Float32[LDPT, Flat],
    LDPT: Ptr(Int32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGBCON")
@external
def sgbcon(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    IPIV: Int32[Flat],
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGBEQU")
@external
def sgbequ(
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ptr(Float32),
    COLCND: Ptr(Float32),
    AMAX: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGBEQUB")
@external
def sgbequb(
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ptr(Float32),
    COLCND: Ptr(Float32),
    AMAX: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGBRFS")
@external
def sgbrfs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGBRFSX")
@external
def sgbrfsx(
    TRANS: Ptr(Const(String[1])),
    EQUED: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    R: Float32[Flat],
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGBSV")
@external
def sgbsv(
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGBSVX")
@external
def sgbsvx(
    FACT: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    EQUED: Ptr(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGBSVXX")
@external
def sgbsvxx(
    FACT: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    EQUED: Ptr(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    RPVGRW: Ptr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGBTF2")
@external
def sgbtf2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGBTRF")
@external
def sgbtrf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGBTRS")
@external
def sgbtrs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEBAK")
@external
def sgebak(
    JOB: Ptr(Const(String[1])),
    SIDE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    SCALE: Float32[Flat],
    M: Ptr(Int32),
    V: Float32[LDV, Flat],
    LDV: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEBAL")
@external
def sgebal(
    JOB: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    SCALE: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEBD2")
@external
def sgebd2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAUQ: Float32[Flat],
    TAUP: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEBRD")
@external
def sgebrd(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAUQ: Float32[Flat],
    TAUP: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGECON")
@external
def sgecon(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEDMD")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7), Arg(8), Arg(9), Arg(10), Arg(11), Arg(12), Return('K', 0), Arg(13), Arg(14), Arg(15), Arg(16), Arg(17), Arg(18), Arg(19), Arg(20), Arg(21), Arg(22), Arg(23), Arg(24), Arg(25), Arg(26), Arg(27), Return('INFO', 10)])
def sgedmd(
    JOBS: Ptr(Const(String[1])),
    JOBZ: Ptr(Const(String[1])),
    JOBR: Ptr(Const(String[1])),
    JOBF: Ptr(Const(String[1])),
    WHTSVD: Ptr(Const(Int32)),
    M: Ptr(Const(Int32)),
    N: Ptr(Const(Int32)),
    X: Float32[LDX, Flat],
    LDX: Ptr(Const(Int32)),
    Y: Float32[LDY, Flat],
    LDY: Ptr(Const(Int32)),
    NRNK: Ptr(Const(Int32)),
    TOL: Ptr(Const(Float32)),
    REIG: Float32[Flat],
    IMEIG: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Const(Int32)),
    RES: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    W: Float32[LDW, Flat],
    LDW: Ptr(Const(Int32)),
    S: Float32[LDS, Flat],
    LDS: Ptr(Const(Int32)),
    WORK: Float32[Flat],
    LWORK: Ptr(Const(Int32)),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Const(Int32))
) -> tuple[Int32, Returns["REIG", Float32[Flat]], Returns["IMEIG", Float32[Flat]], Returns["Z", Float32[LDZ, Flat]], Returns["RES", Float32[Flat]], Returns["B", Float32[LDB, Flat]], Returns["W", Float32[LDW, Flat]], Returns["S", Float32[LDS, Flat]], Returns["WORK", Float32[Flat]], Returns["IWORK", Int32[Flat]], Int32]: ...

@bind("SGEDMDQ")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7), Arg(8), Arg(9), Arg(10), Arg(11), Arg(12), Arg(13), Arg(14), Arg(15), Arg(16), Return('K', 2), Arg(17), Arg(18), Arg(19), Arg(20), Arg(21), Arg(22), Arg(23), Arg(24), Arg(25), Arg(26), Arg(27), Arg(28), Arg(29), Arg(30), Arg(31), Return('INFO', 12)])
def sgedmdq(
    JOBS: Ptr(Const(String[1])),
    JOBZ: Ptr(Const(String[1])),
    JOBR: Ptr(Const(String[1])),
    JOBQ: Ptr(Const(String[1])),
    JOBT: Ptr(Const(String[1])),
    JOBF: Ptr(Const(String[1])),
    WHTSVD: Ptr(Const(Int32)),
    M: Ptr(Const(Int32)),
    N: Ptr(Const(Int32)),
    F: Float32[LDF, Flat],
    LDF: Ptr(Const(Int32)),
    X: Float32[LDX, Flat],
    LDX: Ptr(Const(Int32)),
    Y: Float32[LDY, Flat],
    LDY: Ptr(Const(Int32)),
    NRNK: Ptr(Const(Int32)),
    TOL: Ptr(Const(Float32)),
    REIG: Float32[Flat],
    IMEIG: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Const(Int32)),
    RES: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    V: Float32[LDV, Flat],
    LDV: Ptr(Const(Int32)),
    S: Float32[LDS, Flat],
    LDS: Ptr(Const(Int32)),
    WORK: Float32[Flat],
    LWORK: Ptr(Const(Int32)),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Const(Int32))
) -> tuple[Returns["X", Float32[LDX, Flat]], Returns["Y", Float32[LDY, Flat]], Int32, Returns["REIG", Float32[Flat]], Returns["IMEIG", Float32[Flat]], Returns["Z", Float32[LDZ, Flat]], Returns["RES", Float32[Flat]], Returns["B", Float32[LDB, Flat]], Returns["V", Float32[LDV, Flat]], Returns["S", Float32[LDS, Flat]], Returns["WORK", Float32[Flat]], Returns["IWORK", Int32[Flat]], Int32]: ...

@bind("SGEEQU")
@external
def sgeequ(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ptr(Float32),
    COLCND: Ptr(Float32),
    AMAX: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEEQUB")
@external
def sgeequb(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ptr(Float32),
    COLCND: Ptr(Float32),
    AMAX: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEES")
@external
def sgees(
    JOBVS: Ptr(Const(String[1])),
    SORT: Ptr(Const(String[1])),
    SELECT: Ptr(Bool),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    SDIM: Ptr(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    VS: Float32[LDVS, Flat],
    LDVS: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEESX")
@external
def sgeesx(
    JOBVS: Ptr(Const(String[1])),
    SORT: Ptr(Const(String[1])),
    SELECT: Ptr(Bool),
    SENSE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    SDIM: Ptr(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    VS: Float32[LDVS, Flat],
    LDVS: Ptr(Int32),
    RCONDE: Ptr(Float32),
    RCONDV: Ptr(Float32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEEV")
@external
def sgeev(
    JOBVL: Ptr(Const(String[1])),
    JOBVR: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    VL: Float32[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEEVX")
@external
def sgeevx(
    BALANC: Ptr(Const(String[1])),
    JOBVL: Ptr(Const(String[1])),
    JOBVR: Ptr(Const(String[1])),
    SENSE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    VL: Float32[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    SCALE: Float32[Flat],
    ABNRM: Ptr(Float32),
    RCONDE: Float32[Flat],
    RCONDV: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEHD2")
@external
def sgehd2(
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEHRD")
@external
def sgehrd(
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEJSV")
@external
def sgejsv(
    JOBA: Ptr(Const(String[1])),
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    JOBR: Ptr(Const(String[1])),
    JOBT: Ptr(Const(String[1])),
    JOBP: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    SVA: Float32[N],
    U: Float32[LDU, Flat],
    LDU: Ptr(Int32),
    V: Float32[LDV, Flat],
    LDV: Ptr(Int32),
    WORK: Float32[LWORK],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGELQ")
@external
def sgelq(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float32[Flat],
    TSIZE: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGELQ2")
@external
def sgelq2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGELQF")
@external
def sgelqf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGELQT")
@external
def sgelqt(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGELQT3")
@external
def sgelqt3(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGELS")
@external
def sgels(
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGELSD")
@external
def sgelsd(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    S: Float32[Flat],
    RCOND: Ptr(Float32),
    RANK: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGELSS")
@external
def sgelss(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    S: Float32[Flat],
    RCOND: Ptr(Float32),
    RANK: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGELST")
@external
def sgelst(
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGELSY")
@external
def sgelsy(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    JPVT: Int32[Flat],
    RCOND: Ptr(Float32),
    RANK: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEMLQ")
@external
def sgemlq(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float32[Flat],
    TSIZE: Ptr(Int32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEMLQT")
@external
def sgemlqt(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    MB: Ptr(Int32),
    V: Float32[LDV, Flat],
    LDV: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEMQR")
@external
def sgemqr(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float32[Flat],
    TSIZE: Ptr(Int32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEMQRT")
@external
def sgemqrt(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    NB: Ptr(Int32),
    V: Float32[LDV, Flat],
    LDV: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEQL2")
@external
def sgeql2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEQLF")
@external
def sgeqlf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEQP3")
@external
def sgeqp3(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    JPVT: Int32[Flat],
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEQP3RK")
@external
def sgeqp3rk(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    KMAX: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    RELTOL: Ptr(Float32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    K: Ptr(Int32),
    MAXC2NRMK: Ptr(Float32),
    RELMAXC2NRMK: Ptr(Float32),
    JPIV: Int32[Flat],
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEQR")
@external
def sgeqr(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float32[Flat],
    TSIZE: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEQR2")
@external
def sgeqr2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEQR2P")
@external
def sgeqr2p(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEQRF")
@external
def sgeqrf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEQRFP")
@external
def sgeqrfp(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEQRT")
@external
def sgeqrt(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEQRT2")
@external
def sgeqrt2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGEQRT3")
@external
def sgeqrt3(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGERFS")
@external
def sgerfs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGERFSX")
@external
def sgerfsx(
    TRANS: Ptr(Const(String[1])),
    EQUED: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    R: Float32[Flat],
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGERQ2")
@external
def sgerq2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGERQF")
@external
def sgerqf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGESC2")
@external
def sgesc2(
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    RHS: Float32[Flat],
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    SCALE: Ptr(Float32)
) -> None: ...

@bind("SGESDD")
@external
def sgesdd(
    JOBZ: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGESV")
@external
def sgesv(
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGESVD")
@external
def sgesvd(
    JOBU: Ptr(Const(String[1])),
    JOBVT: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGESVDQ")
@external
def sgesvdq(
    JOBA: Ptr(Const(String[1])),
    JOBP: Ptr(Const(String[1])),
    JOBR: Ptr(Const(String[1])),
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Ptr(Int32),
    V: Float32[LDV, Flat],
    LDV: Ptr(Int32),
    NUMRANK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float32[Flat],
    LRWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGESVDX")
@external
def sgesvdx(
    JOBU: Ptr(Const(String[1])),
    JOBVT: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    NS: Ptr(Int32),
    S: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGESVJ")
@external
def sgesvj(
    JOBA: Ptr(Const(String[1])),
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    SVA: Float32[N],
    MV: Ptr(Int32),
    V: Float32[LDV, Flat],
    LDV: Ptr(Int32),
    WORK: Float32[LWORK],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGESVX")
@external
def sgesvx(
    FACT: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    EQUED: Ptr(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGESVXX")
@external
def sgesvxx(
    FACT: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    EQUED: Ptr(Const(String[1])),
    R: Float32[Flat],
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    RPVGRW: Ptr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGETC2")
@external
def sgetc2(
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGETF2")
@external
def sgetf2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGETRF")
@external
def sgetrf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGETRF2")
@external
def sgetrf2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGETRI")
@external
def sgetri(
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGETRS")
@external
def sgetrs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGETSLS")
@external
def sgetsls(
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGETSQRHRT")
@external
def sgetsqrhrt(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB1: Ptr(Int32),
    NB1: Ptr(Int32),
    NB2: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGGBAK")
@external
def sggbak(
    JOB: Ptr(Const(String[1])),
    SIDE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    LSCALE: Float32[Flat],
    RSCALE: Float32[Flat],
    M: Ptr(Int32),
    V: Float32[LDV, Flat],
    LDV: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGGBAL")
@external
def sggbal(
    JOB: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    LSCALE: Float32[Flat],
    RSCALE: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGGES")
@external
def sgges(
    JOBVSL: Ptr(Const(String[1])),
    JOBVSR: Ptr(Const(String[1])),
    SORT: Ptr(Const(String[1])),
    SELCTG: Ptr(Bool),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    SDIM: Ptr(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    VSL: Float32[LDVSL, Flat],
    LDVSL: Ptr(Int32),
    VSR: Float32[LDVSR, Flat],
    LDVSR: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGGES3")
@external
def sgges3(
    JOBVSL: Ptr(Const(String[1])),
    JOBVSR: Ptr(Const(String[1])),
    SORT: Ptr(Const(String[1])),
    SELCTG: Ptr(Bool),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    SDIM: Ptr(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    VSL: Float32[LDVSL, Flat],
    LDVSL: Ptr(Int32),
    VSR: Float32[LDVSR, Flat],
    LDVSR: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGGESX")
@external
def sggesx(
    JOBVSL: Ptr(Const(String[1])),
    JOBVSR: Ptr(Const(String[1])),
    SORT: Ptr(Const(String[1])),
    SELCTG: Ptr(Bool),
    SENSE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    SDIM: Ptr(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    VSL: Float32[LDVSL, Flat],
    LDVSL: Ptr(Int32),
    VSR: Float32[LDVSR, Flat],
    LDVSR: Ptr(Int32),
    RCONDE: Float32[2],
    RCONDV: Float32[2],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGGEV")
@external
def sggev(
    JOBVL: Ptr(Const(String[1])),
    JOBVR: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    VL: Float32[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGGEV3")
@external
def sggev3(
    JOBVL: Ptr(Const(String[1])),
    JOBVR: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    VL: Float32[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGGEVX")
@external
def sggevx(
    BALANC: Ptr(Const(String[1])),
    JOBVL: Ptr(Const(String[1])),
    JOBVR: Ptr(Const(String[1])),
    SENSE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    VL: Float32[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    LSCALE: Float32[Flat],
    RSCALE: Float32[Flat],
    ABNRM: Ptr(Float32),
    BBNRM: Ptr(Float32),
    RCONDE: Float32[Flat],
    RCONDV: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGGGLM")
@external
def sggglm(
    N: Ptr(Int32),
    M: Ptr(Int32),
    P: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    D: Float32[Flat],
    X: Float32[Flat],
    Y: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGGHD3")
@external
def sgghd3(
    COMPQ: Ptr(Const(String[1])),
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGGHRD")
@external
def sgghrd(
    COMPQ: Ptr(Const(String[1])),
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGGLSE")
@external
def sgglse(
    M: Ptr(Int32),
    N: Ptr(Int32),
    P: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    C: Float32[Flat],
    D: Float32[Flat],
    X: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGGQRF")
@external
def sggqrf(
    N: Ptr(Int32),
    M: Ptr(Int32),
    P: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAUA: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    TAUB: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGGRQF")
@external
def sggrqf(
    M: Ptr(Int32),
    P: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAUA: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    TAUB: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGGSVD3")
@external
def sggsvd3(
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    JOBQ: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    P: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    ALPHA: Float32[Flat],
    BETA: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Ptr(Int32),
    V: Float32[LDV, Flat],
    LDV: Ptr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGGSVP3")
@external
def sggsvp3(
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    JOBQ: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    TOLA: Ptr(Float32),
    TOLB: Ptr(Float32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    U: Float32[LDU, Flat],
    LDU: Ptr(Int32),
    V: Float32[LDV, Flat],
    LDV: Ptr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    IWORK: Int32[Flat],
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGSVJ0")
@external
def sgsvj0(
    JOBV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float32[N],
    SVA: Float32[N],
    MV: Ptr(Int32),
    V: Float32[LDV, Flat],
    LDV: Ptr(Int32),
    EPS: Ptr(Float32),
    SFMIN: Ptr(Float32),
    TOL: Ptr(Float32),
    NSWEEP: Ptr(Int32),
    WORK: Float32[LWORK],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGSVJ1")
@external
def sgsvj1(
    JOBV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    N1: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float32[N],
    SVA: Float32[N],
    MV: Ptr(Int32),
    V: Float32[LDV, Flat],
    LDV: Ptr(Int32),
    EPS: Ptr(Float32),
    SFMIN: Ptr(Float32),
    TOL: Ptr(Float32),
    NSWEEP: Ptr(Int32),
    WORK: Float32[LWORK],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGTCON")
@external
def sgtcon(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    DU2: Float32[Flat],
    IPIV: Int32[Flat],
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGTRFS")
@external
def sgtrfs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    DLF: Float32[Flat],
    DF: Float32[Flat],
    DUF: Float32[Flat],
    DU2: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGTSV")
@external
def sgtsv(
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGTSVX")
@external
def sgtsvx(
    FACT: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    DLF: Float32[Flat],
    DF: Float32[Flat],
    DUF: Float32[Flat],
    DU2: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGTTRF")
@external
def sgttrf(
    N: Ptr(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    DU2: Float32[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGTTRS")
@external
def sgttrs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    DU2: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SGTTS2")
@external
def sgtts2(
    ITRANS: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    DU2: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("SHGEQZ")
@external
def shgeqz(
    JOB: Ptr(Const(String[1])),
    COMPQ: Ptr(Const(String[1])),
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    H: Float32[LDH, Flat],
    LDH: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SHSEIN")
@external
def shsein(
    SIDE: Ptr(Const(String[1])),
    EIGSRC: Ptr(Const(String[1])),
    INITV: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    H: Float32[LDH, Flat],
    LDH: Ptr(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    VL: Float32[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Ptr(Int32),
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Float32[Flat],
    IFAILL: Int32[Flat],
    IFAILR: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SHSEQR")
@external
def shseqr(
    JOB: Ptr(Const(String[1])),
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    H: Float32[LDH, Flat],
    LDH: Ptr(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SISNAN")
@external
def sisnan(
    SIN: Ptr(Const(Float32))
) -> Bool: ...

@bind("SLA_GBAMV")
@external
def sla_gbamv(
    TRANS: Ptr(Int32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    ALPHA: Ptr(Float32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    X: Float32[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Float32),
    Y: Float32[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("SLA_GBRCOND")
@external
def sla_gbrcond(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    CMODE: Ptr(Int32),
    C: Float32[Flat],
    INFO: Ptr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat]
) -> Float32: ...

@bind("SLA_GBRFSX_EXTENDED")
@external
def sla_gbrfsx_extended(
    PREC_TYPE: Ptr(Int32),
    TRANS_TYPE: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ptr(Bool),
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    Y: Float32[LDY, Flat],
    LDY: Ptr(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    RES: Float32[Flat],
    AYB: Float32[Flat],
    DY: Float32[Flat],
    Y_TAIL: Float32[Flat],
    RCOND: Ptr(Float32),
    ITHRESH: Ptr(Int32),
    RTHRESH: Ptr(Float32),
    DZ_UB: Ptr(Float32),
    IGNORE_CWISE: Ptr(Bool),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLA_GBRPVGRW")
@external
def sla_gbrpvgrw(
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NCOLS: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Ptr(Int32)
) -> Float32: ...

@bind("SLA_GEAMV")
@external
def sla_geamv(
    TRANS: Ptr(Int32),
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

@bind("SLA_GERCOND")
@external
def sla_gercond(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    CMODE: Ptr(Int32),
    C: Float32[Flat],
    INFO: Ptr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat]
) -> Float32: ...

@bind("SLA_GERFSX_EXTENDED")
@external
def sla_gerfsx_extended(
    PREC_TYPE: Ptr(Int32),
    TRANS_TYPE: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ptr(Bool),
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    Y: Float32[LDY, Flat],
    LDY: Ptr(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Ptr(Int32),
    ERRS_N: Float32[NRHS, Flat],
    ERRS_C: Float32[NRHS, Flat],
    RES: Float32[Flat],
    AYB: Float32[Flat],
    DY: Float32[Flat],
    Y_TAIL: Float32[Flat],
    RCOND: Ptr(Float32),
    ITHRESH: Ptr(Int32),
    RTHRESH: Ptr(Float32),
    DZ_UB: Ptr(Float32),
    IGNORE_CWISE: Ptr(Bool),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLA_GERPVGRW")
@external
def sla_gerpvgrw(
    N: Ptr(Int32),
    NCOLS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ptr(Int32)
) -> Float32: ...

@bind("SLA_LIN_BERR")
@external
def sla_lin_berr(
    N: Ptr(Int32),
    NZ: Ptr(Int32),
    NRHS: Ptr(Int32),
    RES: Annotated[Float32[N, NRHS], ORDER_F],
    AYB: Annotated[Float32[N, NRHS], ORDER_F],
    BERR: Float32[NRHS]
) -> None: ...

@bind("SLA_PORCOND")
@external
def sla_porcond(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ptr(Int32),
    CMODE: Ptr(Int32),
    C: Float32[Flat],
    INFO: Ptr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat]
) -> Float32: ...

@bind("SLA_PORFSX_EXTENDED")
@external
def sla_porfsx_extended(
    PREC_TYPE: Ptr(Int32),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ptr(Int32),
    COLEQU: Ptr(Bool),
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    Y: Float32[LDY, Flat],
    LDY: Ptr(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    RES: Float32[Flat],
    AYB: Float32[Flat],
    DY: Float32[Flat],
    Y_TAIL: Float32[Flat],
    RCOND: Ptr(Float32),
    ITHRESH: Ptr(Int32),
    RTHRESH: Ptr(Float32),
    DZ_UB: Ptr(Float32),
    IGNORE_CWISE: Ptr(Bool),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLA_PORPVGRW")
@external
def sla_porpvgrw(
    UPLO: Ptr(Const(String[1])),
    NCOLS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ptr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLA_SYAMV")
@external
def sla_syamv(
    UPLO: Ptr(Int32),
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

@bind("SLA_SYRCOND")
@external
def sla_syrcond(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    CMODE: Ptr(Int32),
    C: Float32[Flat],
    INFO: Ptr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat]
) -> Float32: ...

@bind("SLA_SYRFSX_EXTENDED")
@external
def sla_syrfsx_extended(
    PREC_TYPE: Ptr(Int32),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ptr(Bool),
    C: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    Y: Float32[LDY, Flat],
    LDY: Ptr(Int32),
    BERR_OUT: Float32[Flat],
    N_NORMS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    RES: Float32[Flat],
    AYB: Float32[Flat],
    DY: Float32[Flat],
    Y_TAIL: Float32[Flat],
    RCOND: Ptr(Float32),
    ITHRESH: Ptr(Int32),
    RTHRESH: Ptr(Float32),
    DZ_UB: Ptr(Float32),
    IGNORE_CWISE: Ptr(Bool),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLA_SYRPVGRW")
@external
def sla_syrpvgrw(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    INFO: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLA_WWADDW")
@external
def sla_wwaddw(
    N: Ptr(Int32),
    X: Float32[Flat],
    Y: Float32[Flat],
    W: Float32[Flat]
) -> None: ...

@bind("SLABAD")
@external
def slabad(
    SMALL: Ptr(Float32),
    LARGE: Ptr(Float32)
) -> None: ...

@bind("SLABRD")
@external
def slabrd(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAUQ: Float32[Flat],
    TAUP: Float32[Flat],
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    Y: Float32[LDY, Flat],
    LDY: Ptr(Int32)
) -> None: ...

@bind("SLACN2")
@external
def slacn2(
    N: Ptr(Int32),
    V: Float32[Flat],
    X: Float32[Flat],
    ISGN: Int32[Flat],
    EST: Ptr(Float32),
    KASE: Ptr(Int32),
    ISAVE: Int32[3]
) -> None: ...

@bind("SLACON")
@external
def slacon(
    N: Ptr(Int32),
    V: Float32[Flat],
    X: Float32[Flat],
    ISGN: Int32[Flat],
    EST: Ptr(Float32),
    KASE: Ptr(Int32)
) -> None: ...

@bind("SLACPY")
@external
def slacpy(
    UPLO: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("SLADIV")
@external
def sladiv(
    A: Ptr(Float32),
    B: Ptr(Float32),
    C: Ptr(Float32),
    D: Ptr(Float32),
    P: Ptr(Float32),
    Q: Ptr(Float32)
) -> None: ...

@bind("SLADIV1")
@external
def sladiv1(
    A: Ptr(Float32),
    B: Ptr(Float32),
    C: Ptr(Float32),
    D: Ptr(Float32),
    P: Ptr(Float32),
    Q: Ptr(Float32)
) -> None: ...

@bind("SLADIV2")
@external
def sladiv2(
    A: Ptr(Float32),
    B: Ptr(Float32),
    C: Ptr(Float32),
    D: Ptr(Float32),
    R: Ptr(Float32),
    T: Ptr(Float32)
) -> Float32: ...

@bind("SLAE2")
@external
def slae2(
    A: Ptr(Float32),
    B: Ptr(Float32),
    C: Ptr(Float32),
    RT1: Ptr(Float32),
    RT2: Ptr(Float32)
) -> None: ...

@bind("SLAEBZ")
@external
def slaebz(
    IJOB: Ptr(Int32),
    NITMAX: Ptr(Int32),
    N: Ptr(Int32),
    MMAX: Ptr(Int32),
    MINP: Ptr(Int32),
    NBMIN: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    RELTOL: Ptr(Float32),
    PIVMIN: Ptr(Float32),
    D: Float32[Flat],
    E: Float32[Flat],
    E2: Float32[Flat],
    NVAL: Int32[Flat],
    AB: Float32[MMAX, Flat],
    C: Float32[Flat],
    MOUT: Ptr(Int32),
    NAB: Int32[MMAX, Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAED0")
@external
def slaed0(
    ICOMPQ: Ptr(Int32),
    QSIZ: Ptr(Int32),
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    QSTORE: Float32[LDQS, Flat],
    LDQS: Ptr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAED1")
@external
def slaed1(
    N: Ptr(Int32),
    D: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    INDXQ: Int32[Flat],
    RHO: Ptr(Float32),
    CUTPNT: Ptr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAED2")
@external
def slaed2(
    K: Ptr(Int32),
    N: Ptr(Int32),
    N1: Ptr(Int32),
    D: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    INDXQ: Int32[Flat],
    RHO: Ptr(Float32),
    Z: Float32[Flat],
    DLAMBDA: Float32[Flat],
    W: Float32[Flat],
    Q2: Float32[Flat],
    INDX: Int32[Flat],
    INDXC: Int32[Flat],
    INDXP: Int32[Flat],
    COLTYP: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAED3")
@external
def slaed3(
    K: Ptr(Int32),
    N: Ptr(Int32),
    N1: Ptr(Int32),
    D: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    RHO: Ptr(Float32),
    DLAMBDA: Float32[Flat],
    Q2: Float32[Flat],
    INDX: Int32[Flat],
    CTOT: Int32[Flat],
    W: Float32[Flat],
    S: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAED4")
@external
def slaed4(
    N: Ptr(Int32),
    I: Ptr(Int32),
    D: Float32[Flat],
    Z: Float32[Flat],
    DELTA: Float32[Flat],
    RHO: Ptr(Float32),
    DLAM: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAED5")
@external
def slaed5(
    I: Ptr(Int32),
    D: Float32[2],
    Z: Float32[2],
    DELTA: Float32[2],
    RHO: Ptr(Float32),
    DLAM: Ptr(Float32)
) -> None: ...

@bind("SLAED6")
@external
def slaed6(
    KNITER: Ptr(Int32),
    ORGATI: Ptr(Bool),
    RHO: Ptr(Float32),
    D: Float32[3],
    Z: Float32[3],
    FINIT: Ptr(Float32),
    TAU: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAED7")
@external
def slaed7(
    ICOMPQ: Ptr(Int32),
    N: Ptr(Int32),
    QSIZ: Ptr(Int32),
    TLVLS: Ptr(Int32),
    CURLVL: Ptr(Int32),
    CURPBM: Ptr(Int32),
    D: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    INDXQ: Int32[Flat],
    RHO: Ptr(Float32),
    CUTPNT: Ptr(Int32),
    QSTORE: Float32[Flat],
    QPTR: Int32[Flat],
    PRMPTR: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float32[2, Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAED8")
@external
def slaed8(
    ICOMPQ: Ptr(Int32),
    K: Ptr(Int32),
    N: Ptr(Int32),
    QSIZ: Ptr(Int32),
    D: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    INDXQ: Int32[Flat],
    RHO: Ptr(Float32),
    CUTPNT: Ptr(Int32),
    Z: Float32[Flat],
    DLAMBDA: Float32[Flat],
    Q2: Float32[LDQ2, Flat],
    LDQ2: Ptr(Int32),
    W: Float32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Ptr(Int32),
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float32[2, Flat],
    INDXP: Int32[Flat],
    INDX: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAED9")
@external
def slaed9(
    K: Ptr(Int32),
    KSTART: Ptr(Int32),
    KSTOP: Ptr(Int32),
    N: Ptr(Int32),
    D: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    RHO: Ptr(Float32),
    DLAMBDA: Float32[Flat],
    W: Float32[Flat],
    S: Float32[LDS, Flat],
    LDS: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAEDA")
@external
def slaeda(
    N: Ptr(Int32),
    TLVLS: Ptr(Int32),
    CURLVL: Ptr(Int32),
    CURPBM: Ptr(Int32),
    PRMPTR: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float32[2, Flat],
    Q: Float32[Flat],
    QPTR: Int32[Flat],
    Z: Float32[Flat],
    ZTEMP: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAEIN")
@external
def slaein(
    RIGHTV: Ptr(Bool),
    NOINIT: Ptr(Bool),
    N: Ptr(Int32),
    H: Float32[LDH, Flat],
    LDH: Ptr(Int32),
    WR: Ptr(Float32),
    WI: Ptr(Float32),
    VR: Float32[Flat],
    VI: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float32[Flat],
    EPS3: Ptr(Float32),
    SMLNUM: Ptr(Float32),
    BIGNUM: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAEV2")
@external
def slaev2(
    A: Ptr(Float32),
    B: Ptr(Float32),
    C: Ptr(Float32),
    RT1: Ptr(Float32),
    RT2: Ptr(Float32),
    CS1: Ptr(Float32),
    SN1: Ptr(Float32)
) -> None: ...

@bind("SLAEXC")
@external
def slaexc(
    WANTQ: Ptr(Bool),
    N: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    J1: Ptr(Int32),
    N1: Ptr(Int32),
    N2: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAG2")
@external
def slag2(
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    SAFMIN: Ptr(Float32),
    SCALE1: Ptr(Float32),
    SCALE2: Ptr(Float32),
    WR1: Ptr(Float32),
    WR2: Ptr(Float32),
    WI: Ptr(Float32)
) -> None: ...

@bind("SLAG2D")
@external
def slag2d(
    M: Ptr(Int32),
    N: Ptr(Int32),
    SA: Float32[LDSA, Flat],
    LDSA: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAGS2")
@external
def slags2(
    UPPER: Ptr(Bool),
    A1: Ptr(Float32),
    A2: Ptr(Float32),
    A3: Ptr(Float32),
    B1: Ptr(Float32),
    B2: Ptr(Float32),
    B3: Ptr(Float32),
    CSU: Ptr(Float32),
    SNU: Ptr(Float32),
    CSV: Ptr(Float32),
    SNV: Ptr(Float32),
    CSQ: Ptr(Float32),
    SNQ: Ptr(Float32)
) -> None: ...

@bind("SLAGTF")
@external
def slagtf(
    N: Ptr(Int32),
    A: Float32[Flat],
    LAMBDA: Ptr(Float32),
    B: Float32[Flat],
    C: Float32[Flat],
    TOL: Ptr(Float32),
    D: Float32[Flat],
    IN: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAGTM")
@external
def slagtm(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    ALPHA: Ptr(Float32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat],
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    BETA: Ptr(Float32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("SLAGTS")
@external
def slagts(
    JOB: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[Flat],
    B: Float32[Flat],
    C: Float32[Flat],
    D: Float32[Flat],
    IN: Int32[Flat],
    Y: Float32[Flat],
    TOL: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAGV2")
@external
def slagv2(
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    ALPHAR: Float32[2],
    ALPHAI: Float32[2],
    BETA: Float32[2],
    CSL: Ptr(Float32),
    SNL: Ptr(Float32),
    CSR: Ptr(Float32),
    SNR: Ptr(Float32)
) -> None: ...

@bind("SLAHQR")
@external
def slahqr(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    H: Float32[LDH, Flat],
    LDH: Ptr(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAHR2")
@external
def slahr2(
    N: Ptr(Int32),
    K: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[NB],
    T: Annotated[Float32[LDT, NB], ORDER_F],
    LDT: Ptr(Int32),
    Y: Annotated[Float32[LDY, NB], ORDER_F],
    LDY: Ptr(Int32)
) -> None: ...

@bind("SLAIC1")
@external
def slaic1(
    JOB: Ptr(Int32),
    J: Ptr(Int32),
    X: Float32[J],
    SEST: Ptr(Float32),
    W: Float32[J],
    GAMMA: Ptr(Float32),
    SESTPR: Ptr(Float32),
    S: Ptr(Float32),
    C: Ptr(Float32)
) -> None: ...

@bind("SLAISNAN")
@external
def slaisnan(
    SIN1: Ptr(Const(Float32)),
    SIN2: Ptr(Const(Float32))
) -> Bool: ...

@bind("SLALN2")
@external
def slaln2(
    LTRANS: Ptr(Bool),
    NA: Ptr(Int32),
    NW: Ptr(Int32),
    SMIN: Ptr(Float32),
    CA: Ptr(Float32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    D1: Ptr(Float32),
    D2: Ptr(Float32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    WR: Ptr(Float32),
    WI: Ptr(Float32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    SCALE: Ptr(Float32),
    XNORM: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLALS0")
@external
def slals0(
    ICOMPQ: Ptr(Int32),
    NL: Ptr(Int32),
    NR: Ptr(Int32),
    SQRE: Ptr(Int32),
    NRHS: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    BX: Float32[LDBX, Flat],
    LDBX: Ptr(Int32),
    PERM: Int32[Flat],
    GIVPTR: Ptr(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ptr(Int32),
    GIVNUM: Float32[LDGNUM, Flat],
    LDGNUM: Ptr(Int32),
    POLES: Float32[LDGNUM, Flat],
    DIFL: Float32[Flat],
    DIFR: Float32[LDGNUM, Flat],
    Z: Float32[Flat],
    K: Ptr(Int32),
    C: Ptr(Float32),
    S: Ptr(Float32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLALSA")
@external
def slalsa(
    ICOMPQ: Ptr(Int32),
    SMLSIZ: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    BX: Float32[LDBX, Flat],
    LDBX: Ptr(Int32),
    U: Float32[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Float32[LDU, Flat],
    K: Int32[Flat],
    DIFL: Float32[LDU, Flat],
    DIFR: Float32[LDU, Flat],
    Z: Float32[LDU, Flat],
    POLES: Float32[LDU, Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ptr(Int32),
    PERM: Int32[LDGCOL, Flat],
    GIVNUM: Float32[LDU, Flat],
    C: Float32[Flat],
    S: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLALSD")
@external
def slalsd(
    UPLO: Ptr(Const(String[1])),
    SMLSIZ: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    RCOND: Ptr(Float32),
    RANK: Ptr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAMRG")
@external
def slamrg(
    N1: Ptr(Int32),
    N2: Ptr(Int32),
    A: Float32[Flat],
    STRD1: Ptr(Int32),
    STRD2: Ptr(Int32),
    INDEX: Int32[Flat]
) -> None: ...

@bind("SLAMSWLQ")
@external
def slamswlq(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAMTSQR")
@external
def slamtsqr(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLANEG")
@external
def slaneg(
    N: Ptr(Int32),
    D: Float32[Flat],
    LLD: Float32[Flat],
    SIGMA: Ptr(Float32),
    PIVMIN: Ptr(Float32),
    R: Ptr(Int32)
) -> Int32: ...

@bind("SLANGB")
@external
def slangb(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANGE")
@external
def slange(
    NORM: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANGT")
@external
def slangt(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    DL: Float32[Flat],
    D: Float32[Flat],
    DU: Float32[Flat]
) -> Float32: ...

@bind("SLANHS")
@external
def slanhs(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANSB")
@external
def slansb(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANSF")
@external
def slansf(
    NORM: Ptr(Const(String[1])),
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Float32[Flat], SourceDims("0:*")],
    WORK: Annotated[Float32[Flat], SourceDims("0:*")]
) -> Float32: ...

@bind("SLANSP")
@external
def slansp(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANST")
@external
def slanst(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat]
) -> Float32: ...

@bind("SLANSY")
@external
def slansy(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANTB")
@external
def slantb(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANTP")
@external
def slantp(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANTR")
@external
def slantr(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    WORK: Float32[Flat]
) -> Float32: ...

@bind("SLANV2")
@external
def slanv2(
    A: Ptr(Float32),
    B: Ptr(Float32),
    C: Ptr(Float32),
    D: Ptr(Float32),
    RT1R: Ptr(Float32),
    RT1I: Ptr(Float32),
    RT2R: Ptr(Float32),
    RT2I: Ptr(Float32),
    CS: Ptr(Float32),
    SN: Ptr(Float32)
) -> None: ...

@bind("SLAORHR_COL_GETRFNP")
@external
def slaorhr_col_getrfnp(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAORHR_COL_GETRFNP2")
@external
def slaorhr_col_getrfnp2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAPLL")
@external
def slapll(
    N: Ptr(Int32),
    X: Float32[Flat],
    INCX: Ptr(Int32),
    Y: Float32[Flat],
    INCY: Ptr(Int32),
    SSMIN: Ptr(Float32)
) -> None: ...

@bind("SLAPMR")
@external
def slapmr(
    FORWRD: Ptr(Bool),
    M: Ptr(Int32),
    N: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("SLAPMT")
@external
def slapmt(
    FORWRD: Ptr(Bool),
    M: Ptr(Int32),
    N: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("SLAPY2")
@external
def slapy2(
    X: Ptr(Float32),
    Y: Ptr(Float32)
) -> Float32: ...

@bind("SLAPY3")
@external
def slapy3(
    X: Ptr(Float32),
    Y: Ptr(Float32),
    Z: Ptr(Float32)
) -> Float32: ...

@bind("SLAQGB")
@external
def slaqgb(
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ptr(Float32),
    COLCND: Ptr(Float32),
    AMAX: Ptr(Float32),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("SLAQGE")
@external
def slaqge(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    R: Float32[Flat],
    C: Float32[Flat],
    ROWCND: Ptr(Float32),
    COLCND: Ptr(Float32),
    AMAX: Ptr(Float32),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("SLAQP2")
@external
def slaqp2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    OFFSET: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    JPVT: Int32[Flat],
    TAU: Float32[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    WORK: Float32[Flat]
) -> None: ...

@bind("SLAQP2RK")
@external
def slaqp2rk(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    IOFFSET: Ptr(Int32),
    KMAX: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    RELTOL: Ptr(Float32),
    KP1: Ptr(Int32),
    MAXC2NRM: Ptr(Float32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    K: Ptr(Int32),
    MAXC2NRMK: Ptr(Float32),
    RELMAXC2NRMK: Ptr(Float32),
    JPIV: Int32[Flat],
    TAU: Float32[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAQP3RK")
@external
def slaqp3rk(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    IOFFSET: Ptr(Int32),
    NB: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    RELTOL: Ptr(Float32),
    KP1: Ptr(Int32),
    MAXC2NRM: Ptr(Float32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    DONE: Ptr(Bool),
    KB: Ptr(Int32),
    MAXC2NRMK: Ptr(Float32),
    RELMAXC2NRMK: Ptr(Float32),
    JPIV: Int32[Flat],
    TAU: Float32[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    AUXV: Float32[Flat],
    F: Float32[LDF, Flat],
    LDF: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAQPS")
@external
def slaqps(
    M: Ptr(Int32),
    N: Ptr(Int32),
    OFFSET: Ptr(Int32),
    NB: Ptr(Int32),
    KB: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    JPVT: Int32[Flat],
    TAU: Float32[Flat],
    VN1: Float32[Flat],
    VN2: Float32[Flat],
    AUXV: Float32[Flat],
    F: Float32[LDF, Flat],
    LDF: Ptr(Int32)
) -> None: ...

@bind("SLAQR0")
@external
def slaqr0(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    H: Float32[LDH, Flat],
    LDH: Ptr(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAQR1")
@external
def slaqr1(
    N: Ptr(Int32),
    H: Float32[LDH, Flat],
    LDH: Ptr(Int32),
    SR1: Ptr(Float32),
    SI1: Ptr(Float32),
    SR2: Ptr(Float32),
    SI2: Ptr(Float32),
    V: Float32[Flat]
) -> None: ...

@bind("SLAQR2")
@external
def slaqr2(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    KTOP: Ptr(Int32),
    KBOT: Ptr(Int32),
    NW: Ptr(Int32),
    H: Float32[LDH, Flat],
    LDH: Ptr(Int32),
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    NS: Ptr(Int32),
    ND: Ptr(Int32),
    SR: Float32[Flat],
    SI: Float32[Flat],
    V: Float32[LDV, Flat],
    LDV: Ptr(Int32),
    NH: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    NV: Ptr(Int32),
    WV: Float32[LDWV, Flat],
    LDWV: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32)
) -> None: ...

@bind("SLAQR3")
@external
def slaqr3(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    KTOP: Ptr(Int32),
    KBOT: Ptr(Int32),
    NW: Ptr(Int32),
    H: Float32[LDH, Flat],
    LDH: Ptr(Int32),
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    NS: Ptr(Int32),
    ND: Ptr(Int32),
    SR: Float32[Flat],
    SI: Float32[Flat],
    V: Float32[LDV, Flat],
    LDV: Ptr(Int32),
    NH: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    NV: Ptr(Int32),
    WV: Float32[LDWV, Flat],
    LDWV: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32)
) -> None: ...

@bind("SLAQR4")
@external
def slaqr4(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    H: Float32[LDH, Flat],
    LDH: Ptr(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAQR5")
@external
def slaqr5(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    KACC22: Ptr(Int32),
    N: Ptr(Int32),
    KTOP: Ptr(Int32),
    KBOT: Ptr(Int32),
    NSHFTS: Ptr(Int32),
    SR: Float32[Flat],
    SI: Float32[Flat],
    H: Float32[LDH, Flat],
    LDH: Ptr(Int32),
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    V: Float32[LDV, Flat],
    LDV: Ptr(Int32),
    U: Float32[LDU, Flat],
    LDU: Ptr(Int32),
    NV: Ptr(Int32),
    WV: Float32[LDWV, Flat],
    LDWV: Ptr(Int32),
    NH: Ptr(Int32),
    WH: Float32[LDWH, Flat],
    LDWH: Ptr(Int32)
) -> None: ...

@bind("SLAQSB")
@external
def slaqsb(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    S: Float32[Flat],
    SCOND: Ptr(Float32),
    AMAX: Ptr(Float32),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("SLAQSP")
@external
def slaqsp(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    S: Float32[Flat],
    SCOND: Ptr(Float32),
    AMAX: Ptr(Float32),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("SLAQSY")
@external
def slaqsy(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float32[Flat],
    SCOND: Ptr(Float32),
    AMAX: Ptr(Float32),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("SLAQTR")
@external
def slaqtr(
    LTRAN: Ptr(Bool),
    LREAL: Ptr(Bool),
    N: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    B: Float32[Flat],
    W: Ptr(Float32),
    SCALE: Ptr(Float32),
    X: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAQZ0")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7), Arg(8), Arg(9), Arg(10), Arg(11), Arg(12), Arg(13), Arg(14), Arg(15), Arg(16), Arg(17), Arg(18), Arg(19), Return('INFO', 0)])
def slaqz0(
    WANTS: Ptr(Const(String[1])),
    WANTQ: Ptr(Const(String[1])),
    WANTZ: Ptr(Const(String[1])),
    N: Ptr(Const(Int32)),
    ILO: Ptr(Const(Int32)),
    IHI: Ptr(Const(Int32)),
    A: Float32[LDA, Flat],
    LDA: Ptr(Const(Int32)),
    B: Float32[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Const(Int32)),
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Const(Int32)),
    WORK: Float32[Flat],
    LWORK: Ptr(Const(Int32)),
    REC: Ptr(Const(Int32))
) -> Int32: ...

@bind("SLAQZ1")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7), Arg(8), Arg(9)])
def slaqz1(
    A: Const(Float32[LDA, Flat]),
    LDA: Ptr(Const(Int32)),
    B: Const(Float32[LDB, Flat]),
    LDB: Ptr(Const(Int32)),
    SR1: Ptr(Const(Float32)),
    SR2: Ptr(Const(Float32)),
    SI: Ptr(Const(Float32)),
    BETA1: Ptr(Const(Float32)),
    BETA2: Ptr(Const(Float32)),
    V: Float32[Flat]
) -> Returns["V", Float32[Flat]]: ...

@bind("SLAQZ2")
@external
def slaqz2(
    ILQ: Ptr(Const(Bool)),
    ILZ: Ptr(Const(Bool)),
    K: Ptr(Const(Int32)),
    ISTARTM: Ptr(Const(Int32)),
    ISTOPM: Ptr(Const(Int32)),
    IHI: Ptr(Const(Int32)),
    A: Float32[LDA, Flat],
    LDA: Ptr(Const(Int32)),
    B: Float32[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    NQ: Ptr(Const(Int32)),
    QSTART: Ptr(Const(Int32)),
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Const(Int32)),
    NZ: Ptr(Const(Int32)),
    ZSTART: Ptr(Const(Int32)),
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Const(Int32))
) -> None: ...

@bind("SLAQZ3")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7), Arg(8), Arg(9), Arg(10), Arg(11), Arg(12), Arg(13), Arg(14), Return('NS', 0), Return('ND', 1), Arg(15), Arg(16), Arg(17), Arg(18), Arg(19), Arg(20), Arg(21), Arg(22), Arg(23), Arg(24), Return('INFO', 2)])
def slaqz3(
    ILSCHUR: Ptr(Const(Bool)),
    ILQ: Ptr(Const(Bool)),
    ILZ: Ptr(Const(Bool)),
    N: Ptr(Const(Int32)),
    ILO: Ptr(Const(Int32)),
    IHI: Ptr(Const(Int32)),
    NW: Ptr(Const(Int32)),
    A: Float32[LDA, Flat],
    LDA: Ptr(Const(Int32)),
    B: Float32[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Const(Int32)),
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Const(Int32)),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    QC: Float32[LDQC, Flat],
    LDQC: Ptr(Const(Int32)),
    ZC: Float32[LDZC, Flat],
    LDZC: Ptr(Const(Int32)),
    WORK: Float32[Flat],
    LWORK: Ptr(Const(Int32)),
    REC: Ptr(Const(Int32))
) -> tuple[Int32, Int32, Int32]: ...

@bind("SLAQZ4")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7), Arg(8), Arg(9), Arg(10), Arg(11), Arg(12), Arg(13), Arg(14), Arg(15), Arg(16), Arg(17), Arg(18), Arg(19), Arg(20), Arg(21), Arg(22), Arg(23), Arg(24), Return('INFO', 0)])
def slaqz4(
    ILSCHUR: Ptr(Const(Bool)),
    ILQ: Ptr(Const(Bool)),
    ILZ: Ptr(Const(Bool)),
    N: Ptr(Const(Int32)),
    ILO: Ptr(Const(Int32)),
    IHI: Ptr(Const(Int32)),
    NSHIFTS: Ptr(Const(Int32)),
    NBLOCK_DESIRED: Ptr(Const(Int32)),
    SR: Float32[Flat],
    SI: Float32[Flat],
    SS: Float32[Flat],
    A: Float32[LDA, Flat],
    LDA: Ptr(Const(Int32)),
    B: Float32[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Const(Int32)),
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Const(Int32)),
    QC: Float32[LDQC, Flat],
    LDQC: Ptr(Const(Int32)),
    ZC: Float32[LDZC, Flat],
    LDZC: Ptr(Const(Int32)),
    WORK: Float32[Flat],
    LWORK: Ptr(Const(Int32))
) -> Int32: ...

@bind("SLAR1V")
@external
def slar1v(
    N: Ptr(Int32),
    B1: Ptr(Int32),
    BN: Ptr(Int32),
    LAMBDA: Ptr(Float32),
    D: Float32[Flat],
    L: Float32[Flat],
    LD: Float32[Flat],
    LLD: Float32[Flat],
    PIVMIN: Ptr(Float32),
    GAPTOL: Ptr(Float32),
    Z: Float32[Flat],
    WANTNC: Ptr(Bool),
    NEGCNT: Ptr(Int32),
    ZTZ: Ptr(Float32),
    MINGMA: Ptr(Float32),
    R: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    NRMINV: Ptr(Float32),
    RESID: Ptr(Float32),
    RQCORR: Ptr(Float32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLAR2V")
@external
def slar2v(
    N: Ptr(Int32),
    X: Float32[Flat],
    Y: Float32[Flat],
    Z: Float32[Flat],
    INCX: Ptr(Int32),
    C: Float32[Flat],
    S: Float32[Flat],
    INCC: Ptr(Int32)
) -> None: ...

@bind("SLARF")
@external
def slarf(
    SIDE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    V: Float32[Flat],
    INCV: Ptr(Int32),
    TAU: Ptr(Float32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLARF1F")
@external
def slarf1f(
    SIDE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    V: Float32[Flat],
    INCV: Ptr(Int32),
    TAU: Ptr(Float32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLARF1L")
@external
def slarf1l(
    SIDE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    V: Float32[Flat],
    INCV: Ptr(Int32),
    TAU: Ptr(Float32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLARFB")
@external
def slarfb(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIRECT: Ptr(Const(String[1])),
    STOREV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    V: Float32[LDV, Flat],
    LDV: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[LDWORK, Flat],
    LDWORK: Ptr(Int32)
) -> None: ...

@bind("SLARFB_GETT")
@external
def slarfb_gett(
    IDENT: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float32[LDWORK, Flat],
    LDWORK: Ptr(Int32)
) -> None: ...

@bind("SLARFG")
@external
def slarfg(
    N: Ptr(Int32),
    ALPHA: Ptr(Float32),
    X: Float32[Flat],
    INCX: Ptr(Int32),
    TAU: Ptr(Float32)
) -> None: ...

@bind("SLARFGP")
@external
def slarfgp(
    N: Ptr(Int32),
    ALPHA: Ptr(Float32),
    X: Float32[Flat],
    INCX: Ptr(Int32),
    TAU: Ptr(Float32)
) -> None: ...

@bind("SLARFT")
@external
def slarft(
    DIRECT: Ptr(Const(String[1])),
    STOREV: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    V: Float32[LDV, Flat],
    LDV: Ptr(Int32),
    TAU: Float32[Flat],
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32)
) -> None: ...

@bind("SLARFX")
@external
def slarfx(
    SIDE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    V: Float32[Flat],
    TAU: Ptr(Float32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLARFY")
@external
def slarfy(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    V: Float32[Flat],
    INCV: Ptr(Int32),
    TAU: Ptr(Float32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLARGV")
@external
def slargv(
    N: Ptr(Int32),
    X: Float32[Flat],
    INCX: Ptr(Int32),
    Y: Float32[Flat],
    INCY: Ptr(Int32),
    C: Float32[Flat],
    INCC: Ptr(Int32)
) -> None: ...

@bind("SLARMM")
@external
def slarmm(
    ANORM: Ptr(Float32),
    BNORM: Ptr(Float32),
    CNORM: Ptr(Float32)
) -> Float32: ...

@bind("SLARNV")
@external
def slarnv(
    IDIST: Ptr(Int32),
    ISEED: Int32[4],
    N: Ptr(Int32),
    X: Float32[Flat]
) -> None: ...

@bind("SLARRA")
@external
def slarra(
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    E2: Float32[Flat],
    SPLTOL: Ptr(Float32),
    TNRM: Ptr(Float32),
    NSPLIT: Ptr(Int32),
    ISPLIT: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLARRB")
@external
def slarrb(
    N: Ptr(Int32),
    D: Float32[Flat],
    LLD: Float32[Flat],
    IFIRST: Ptr(Int32),
    ILAST: Ptr(Int32),
    RTOL1: Ptr(Float32),
    RTOL2: Ptr(Float32),
    OFFSET: Ptr(Int32),
    W: Float32[Flat],
    WGAP: Float32[Flat],
    WERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    PIVMIN: Ptr(Float32),
    SPDIAM: Ptr(Float32),
    TWIST: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLARRC")
@external
def slarrc(
    JOBT: Ptr(Const(String[1])),
    N: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    D: Float32[Flat],
    E: Float32[Flat],
    PIVMIN: Ptr(Float32),
    EIGCNT: Ptr(Int32),
    LCNT: Ptr(Int32),
    RCNT: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLARRD")
@external
def slarrd(
    RANGE: Ptr(Const(String[1])),
    ORDER: Ptr(Const(String[1])),
    N: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    GERS: Float32[Flat],
    RELTOL: Ptr(Float32),
    D: Float32[Flat],
    E: Float32[Flat],
    E2: Float32[Flat],
    PIVMIN: Ptr(Float32),
    NSPLIT: Ptr(Int32),
    ISPLIT: Int32[Flat],
    M: Ptr(Int32),
    W: Float32[Flat],
    WERR: Float32[Flat],
    WL: Ptr(Float32),
    WU: Ptr(Float32),
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLARRE")
@external
def slarre(
    RANGE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    E2: Float32[Flat],
    RTOL1: Ptr(Float32),
    RTOL2: Ptr(Float32),
    SPLTOL: Ptr(Float32),
    NSPLIT: Ptr(Int32),
    ISPLIT: Int32[Flat],
    M: Ptr(Int32),
    W: Float32[Flat],
    WERR: Float32[Flat],
    WGAP: Float32[Flat],
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    GERS: Float32[Flat],
    PIVMIN: Ptr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLARRF")
@external
def slarrf(
    N: Ptr(Int32),
    D: Float32[Flat],
    L: Float32[Flat],
    LD: Float32[Flat],
    CLSTRT: Ptr(Int32),
    CLEND: Ptr(Int32),
    W: Float32[Flat],
    WGAP: Float32[Flat],
    WERR: Float32[Flat],
    SPDIAM: Ptr(Float32),
    CLGAPL: Ptr(Float32),
    CLGAPR: Ptr(Float32),
    PIVMIN: Ptr(Float32),
    SIGMA: Ptr(Float32),
    DPLUS: Float32[Flat],
    LPLUS: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLARRJ")
@external
def slarrj(
    N: Ptr(Int32),
    D: Float32[Flat],
    E2: Float32[Flat],
    IFIRST: Ptr(Int32),
    ILAST: Ptr(Int32),
    RTOL: Ptr(Float32),
    OFFSET: Ptr(Int32),
    W: Float32[Flat],
    WERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    PIVMIN: Ptr(Float32),
    SPDIAM: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLARRK")
@external
def slarrk(
    N: Ptr(Int32),
    IW: Ptr(Int32),
    GL: Ptr(Float32),
    GU: Ptr(Float32),
    D: Float32[Flat],
    E2: Float32[Flat],
    PIVMIN: Ptr(Float32),
    RELTOL: Ptr(Float32),
    W: Ptr(Float32),
    WERR: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLARRR")
@external
def slarrr(
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLARRV")
@external
def slarrv(
    N: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    D: Float32[Flat],
    L: Float32[Flat],
    PIVMIN: Ptr(Float32),
    ISPLIT: Int32[Flat],
    M: Ptr(Int32),
    DOL: Ptr(Int32),
    DOU: Ptr(Int32),
    MINRGP: Ptr(Float32),
    RTOL1: Ptr(Float32),
    RTOL2: Ptr(Float32),
    W: Float32[Flat],
    WERR: Float32[Flat],
    WGAP: Float32[Flat],
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    GERS: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLARSCL2")
@external
def slarscl2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    D: Float32[Flat],
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32)
) -> None: ...

@bind("SLARTG")
@external
def slartg(
    f: Ptr(Float32),
    g: Ptr(Float32),
    c: Ptr(Float32),
    s: Ptr(Float32),
    r: Ptr(Float32)
) -> None: ...

@bind("SLARTGP")
@external
def slartgp(
    F: Ptr(Float32),
    G: Ptr(Float32),
    CS: Ptr(Float32),
    SN: Ptr(Float32),
    R: Ptr(Float32)
) -> None: ...

@bind("SLARTGS")
@external
def slartgs(
    X: Ptr(Float32),
    Y: Ptr(Float32),
    SIGMA: Ptr(Float32),
    CS: Ptr(Float32),
    SN: Ptr(Float32)
) -> None: ...

@bind("SLARTV")
@external
def slartv(
    N: Ptr(Int32),
    X: Float32[Flat],
    INCX: Ptr(Int32),
    Y: Float32[Flat],
    INCY: Ptr(Int32),
    C: Float32[Flat],
    S: Float32[Flat],
    INCC: Ptr(Int32)
) -> None: ...

@bind("SLARUV")
@external
def slaruv(
    ISEED: Int32[4],
    N: Ptr(Int32),
    X: Float32[N]
) -> None: ...

@bind("SLARZ")
@external
def slarz(
    SIDE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    V: Float32[Flat],
    INCV: Ptr(Int32),
    TAU: Ptr(Float32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLARZB")
@external
def slarzb(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIRECT: Ptr(Const(String[1])),
    STOREV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    V: Float32[LDV, Flat],
    LDV: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[LDWORK, Flat],
    LDWORK: Ptr(Int32)
) -> None: ...

@bind("SLARZT")
@external
def slarzt(
    DIRECT: Ptr(Const(String[1])),
    STOREV: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    V: Float32[LDV, Flat],
    LDV: Ptr(Int32),
    TAU: Float32[Flat],
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32)
) -> None: ...

@bind("SLAS2")
@external
def slas2(
    F: Ptr(Float32),
    G: Ptr(Float32),
    H: Ptr(Float32),
    SSMIN: Ptr(Float32),
    SSMAX: Ptr(Float32)
) -> None: ...

@bind("SLASCL")
@external
def slascl(
    TYPE: Ptr(Const(String[1])),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    CFROM: Ptr(Float32),
    CTO: Ptr(Float32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLASCL2")
@external
def slascl2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    D: Float32[Flat],
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32)
) -> None: ...

@bind("SLASD0")
@external
def slasd0(
    N: Ptr(Int32),
    SQRE: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Ptr(Int32),
    SMLSIZ: Ptr(Int32),
    IWORK: Int32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLASD1")
@external
def slasd1(
    NL: Ptr(Int32),
    NR: Ptr(Int32),
    SQRE: Ptr(Int32),
    D: Float32[Flat],
    ALPHA: Ptr(Float32),
    BETA: Ptr(Float32),
    U: Float32[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Ptr(Int32),
    IDXQ: Int32[Flat],
    IWORK: Int32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLASD2")
@external
def slasd2(
    NL: Ptr(Int32),
    NR: Ptr(Int32),
    SQRE: Ptr(Int32),
    K: Ptr(Int32),
    D: Float32[Flat],
    Z: Float32[Flat],
    ALPHA: Ptr(Float32),
    BETA: Ptr(Float32),
    U: Float32[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Ptr(Int32),
    DSIGMA: Float32[Flat],
    U2: Float32[LDU2, Flat],
    LDU2: Ptr(Int32),
    VT2: Float32[LDVT2, Flat],
    LDVT2: Ptr(Int32),
    IDXP: Int32[Flat],
    IDX: Int32[Flat],
    IDXC: Int32[Flat],
    IDXQ: Int32[Flat],
    COLTYP: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLASD3")
@external
def slasd3(
    NL: Ptr(Int32),
    NR: Ptr(Int32),
    SQRE: Ptr(Int32),
    K: Ptr(Int32),
    D: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    DSIGMA: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Ptr(Int32),
    U2: Float32[LDU2, Flat],
    LDU2: Ptr(Int32),
    VT: Float32[LDVT, Flat],
    LDVT: Ptr(Int32),
    VT2: Float32[LDVT2, Flat],
    LDVT2: Ptr(Int32),
    IDXC: Int32[Flat],
    CTOT: Int32[Flat],
    Z: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLASD4")
@external
def slasd4(
    N: Ptr(Int32),
    I: Ptr(Int32),
    D: Float32[Flat],
    Z: Float32[Flat],
    DELTA: Float32[Flat],
    RHO: Ptr(Float32),
    SIGMA: Ptr(Float32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLASD5")
@external
def slasd5(
    I: Ptr(Int32),
    D: Float32[2],
    Z: Float32[2],
    DELTA: Float32[2],
    RHO: Ptr(Float32),
    DSIGMA: Ptr(Float32),
    WORK: Float32[2]
) -> None: ...

@bind("SLASD6")
@external
def slasd6(
    ICOMPQ: Ptr(Int32),
    NL: Ptr(Int32),
    NR: Ptr(Int32),
    SQRE: Ptr(Int32),
    D: Float32[Flat],
    VF: Float32[Flat],
    VL: Float32[Flat],
    ALPHA: Ptr(Float32),
    BETA: Ptr(Float32),
    IDXQ: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Ptr(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ptr(Int32),
    GIVNUM: Float32[LDGNUM, Flat],
    LDGNUM: Ptr(Int32),
    POLES: Float32[LDGNUM, Flat],
    DIFL: Float32[Flat],
    DIFR: Float32[Flat],
    Z: Float32[Flat],
    K: Ptr(Int32),
    C: Ptr(Float32),
    S: Ptr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLASD7")
@external
def slasd7(
    ICOMPQ: Ptr(Int32),
    NL: Ptr(Int32),
    NR: Ptr(Int32),
    SQRE: Ptr(Int32),
    K: Ptr(Int32),
    D: Float32[Flat],
    Z: Float32[Flat],
    ZW: Float32[Flat],
    VF: Float32[Flat],
    VFW: Float32[Flat],
    VL: Float32[Flat],
    VLW: Float32[Flat],
    ALPHA: Ptr(Float32),
    BETA: Ptr(Float32),
    DSIGMA: Float32[Flat],
    IDX: Int32[Flat],
    IDXP: Int32[Flat],
    IDXQ: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Ptr(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ptr(Int32),
    GIVNUM: Float32[LDGNUM, Flat],
    LDGNUM: Ptr(Int32),
    C: Ptr(Float32),
    S: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLASD8")
@external
def slasd8(
    ICOMPQ: Ptr(Int32),
    K: Ptr(Int32),
    D: Float32[Flat],
    Z: Float32[Flat],
    VF: Float32[Flat],
    VL: Float32[Flat],
    DIFL: Float32[Flat],
    DIFR: Float32[LDDIFR, Flat],
    LDDIFR: Ptr(Int32),
    DSIGMA: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLASDA")
@external
def slasda(
    ICOMPQ: Ptr(Int32),
    SMLSIZ: Ptr(Int32),
    N: Ptr(Int32),
    SQRE: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Float32[LDU, Flat],
    K: Int32[Flat],
    DIFL: Float32[LDU, Flat],
    DIFR: Float32[LDU, Flat],
    Z: Float32[LDU, Flat],
    POLES: Float32[LDU, Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ptr(Int32),
    PERM: Int32[LDGCOL, Flat],
    GIVNUM: Float32[LDU, Flat],
    C: Float32[Flat],
    S: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLASDQ")
@external
def slasdq(
    UPLO: Ptr(Const(String[1])),
    SQRE: Ptr(Int32),
    N: Ptr(Int32),
    NCVT: Ptr(Int32),
    NRU: Ptr(Int32),
    NCC: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VT: Float32[LDVT, Flat],
    LDVT: Ptr(Int32),
    U: Float32[LDU, Flat],
    LDU: Ptr(Int32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLASDT")
@external
def slasdt(
    N: Ptr(Int32),
    LVL: Ptr(Int32),
    ND: Ptr(Int32),
    INODE: Int32[Flat],
    NDIML: Int32[Flat],
    NDIMR: Int32[Flat],
    MSUB: Ptr(Int32)
) -> None: ...

@bind("SLASET")
@external
def slaset(
    UPLO: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Float32),
    BETA: Ptr(Float32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("SLASQ1")
@external
def slasq1(
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLASQ2")
@external
def slasq2(
    N: Ptr(Int32),
    Z: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLASQ3")
@external
def slasq3(
    I0: Ptr(Int32),
    N0: Ptr(Int32),
    Z: Float32[Flat],
    PP: Ptr(Int32),
    DMIN: Ptr(Float32),
    SIGMA: Ptr(Float32),
    DESIG: Ptr(Float32),
    QMAX: Ptr(Float32),
    NFAIL: Ptr(Int32),
    ITER: Ptr(Int32),
    NDIV: Ptr(Int32),
    IEEE: Ptr(Bool),
    TTYPE: Ptr(Int32),
    DMIN1: Ptr(Float32),
    DMIN2: Ptr(Float32),
    DN: Ptr(Float32),
    DN1: Ptr(Float32),
    DN2: Ptr(Float32),
    G: Ptr(Float32),
    TAU: Ptr(Float32)
) -> None: ...

@bind("SLASQ4")
@external
def slasq4(
    I0: Ptr(Int32),
    N0: Ptr(Int32),
    Z: Float32[Flat],
    PP: Ptr(Int32),
    N0IN: Ptr(Int32),
    DMIN: Ptr(Float32),
    DMIN1: Ptr(Float32),
    DMIN2: Ptr(Float32),
    DN: Ptr(Float32),
    DN1: Ptr(Float32),
    DN2: Ptr(Float32),
    TAU: Ptr(Float32),
    TTYPE: Ptr(Int32),
    G: Ptr(Float32)
) -> None: ...

@bind("SLASQ5")
@external
def slasq5(
    I0: Ptr(Int32),
    N0: Ptr(Int32),
    Z: Float32[Flat],
    PP: Ptr(Int32),
    TAU: Ptr(Float32),
    SIGMA: Ptr(Float32),
    DMIN: Ptr(Float32),
    DMIN1: Ptr(Float32),
    DMIN2: Ptr(Float32),
    DN: Ptr(Float32),
    DNM1: Ptr(Float32),
    DNM2: Ptr(Float32),
    IEEE: Ptr(Bool),
    EPS: Ptr(Float32)
) -> None: ...

@bind("SLASQ6")
@external
def slasq6(
    I0: Ptr(Int32),
    N0: Ptr(Int32),
    Z: Float32[Flat],
    PP: Ptr(Int32),
    DMIN: Ptr(Float32),
    DMIN1: Ptr(Float32),
    DMIN2: Ptr(Float32),
    DN: Ptr(Float32),
    DNM1: Ptr(Float32),
    DNM2: Ptr(Float32)
) -> None: ...

@bind("SLASR")
@external
def slasr(
    SIDE: Ptr(Const(String[1])),
    PIVOT: Ptr(Const(String[1])),
    DIRECT: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    C: Float32[Flat],
    S: Float32[Flat],
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("SLASRT")
@external
def slasrt(
    ID: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLASSQ")
@external
def slassq(
    n: Ptr(Int32),
    x: Float32[Flat],
    incx: Ptr(Int32),
    scale: Ptr(Float32),
    sumsq: Ptr(Float32)
) -> None: ...

@bind("SLASV2")
@external
def slasv2(
    F: Ptr(Float32),
    G: Ptr(Float32),
    H: Ptr(Float32),
    SSMIN: Ptr(Float32),
    SSMAX: Ptr(Float32),
    SNR: Ptr(Float32),
    CSR: Ptr(Float32),
    SNL: Ptr(Float32),
    CSL: Ptr(Float32)
) -> None: ...

@bind("SLASWLQ")
@external
def slaswlq(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLASWP")
@external
def slaswp(
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    K1: Ptr(Int32),
    K2: Ptr(Int32),
    IPIV: Int32[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("SLASY2")
@external
def slasy2(
    LTRANL: Ptr(Bool),
    LTRANR: Ptr(Bool),
    ISGN: Ptr(Int32),
    N1: Ptr(Int32),
    N2: Ptr(Int32),
    TL: Float32[LDTL, Flat],
    LDTL: Ptr(Int32),
    TR: Float32[LDTR, Flat],
    LDTR: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    SCALE: Ptr(Float32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    XNORM: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLASYF")
@external
def slasyf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    KB: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    W: Float32[LDW, Flat],
    LDW: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLASYF_AA")
@external
def slasyf_aa(
    UPLO: Ptr(Const(String[1])),
    J1: Ptr(Int32),
    M: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    H: Float32[LDH, Flat],
    LDH: Ptr(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SLASYF_RK")
@external
def slasyf_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    KB: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    W: Float32[LDW, Flat],
    LDW: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLASYF_ROOK")
@external
def slasyf_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    KB: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    W: Float32[LDW, Flat],
    LDW: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLATBS")
@external
def slatbs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    NORMIN: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    X: Float32[Flat],
    SCALE: Ptr(Float32),
    CNORM: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLATDF")
@external
def slatdf(
    IJOB: Ptr(Int32),
    N: Ptr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    RHS: Float32[Flat],
    RDSUM: Ptr(Float32),
    RDSCAL: Ptr(Float32),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat]
) -> None: ...

@bind("SLATPS")
@external
def slatps(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    NORMIN: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    X: Float32[Flat],
    SCALE: Ptr(Float32),
    CNORM: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLATRD")
@external
def slatrd(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float32[Flat],
    TAU: Float32[Flat],
    W: Float32[LDW, Flat],
    LDW: Ptr(Int32)
) -> None: ...

@bind("SLATRS")
@external
def slatrs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    NORMIN: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    X: Float32[Flat],
    SCALE: Ptr(Float32),
    CNORM: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLATRS3")
@external
def slatrs3(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    NORMIN: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    SCALE: Float32[Flat],
    CNORM: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLATRZ")
@external
def slatrz(
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat]
) -> None: ...

@bind("SLATSQR")
@external
def slatsqr(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAUU2")
@external
def slauu2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SLAUUM")
@external
def slauum(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SOPGTR")
@external
def sopgtr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    TAU: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SOPMTR")
@external
def sopmtr(
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    AP: Float32[Flat],
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORBDB")
@external
def sorbdb(
    TRANS: Ptr(Const(String[1])),
    SIGNS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Float32[LDX11, Flat],
    LDX11: Ptr(Int32),
    X12: Float32[LDX12, Flat],
    LDX12: Ptr(Int32),
    X21: Float32[LDX21, Flat],
    LDX21: Ptr(Int32),
    X22: Float32[LDX22, Flat],
    LDX22: Ptr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Float32[Flat],
    TAUP2: Float32[Flat],
    TAUQ1: Float32[Flat],
    TAUQ2: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORBDB1")
@external
def sorbdb1(
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Float32[LDX11, Flat],
    LDX11: Ptr(Int32),
    X21: Float32[LDX21, Flat],
    LDX21: Ptr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Float32[Flat],
    TAUP2: Float32[Flat],
    TAUQ1: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORBDB2")
@external
def sorbdb2(
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Float32[LDX11, Flat],
    LDX11: Ptr(Int32),
    X21: Float32[LDX21, Flat],
    LDX21: Ptr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Float32[Flat],
    TAUP2: Float32[Flat],
    TAUQ1: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORBDB3")
@external
def sorbdb3(
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Float32[LDX11, Flat],
    LDX11: Ptr(Int32),
    X21: Float32[LDX21, Flat],
    LDX21: Ptr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Float32[Flat],
    TAUP2: Float32[Flat],
    TAUQ1: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORBDB4")
@external
def sorbdb4(
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Float32[LDX11, Flat],
    LDX11: Ptr(Int32),
    X21: Float32[LDX21, Flat],
    LDX21: Ptr(Int32),
    THETA: Float32[Flat],
    PHI: Float32[Flat],
    TAUP1: Float32[Flat],
    TAUP2: Float32[Flat],
    TAUQ1: Float32[Flat],
    PHANTOM: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORBDB5")
@external
def sorbdb5(
    M1: Ptr(Int32),
    M2: Ptr(Int32),
    N: Ptr(Int32),
    X1: Float32[Flat],
    INCX1: Ptr(Int32),
    X2: Float32[Flat],
    INCX2: Ptr(Int32),
    Q1: Float32[LDQ1, Flat],
    LDQ1: Ptr(Int32),
    Q2: Float32[LDQ2, Flat],
    LDQ2: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORBDB6")
@external
def sorbdb6(
    M1: Ptr(Int32),
    M2: Ptr(Int32),
    N: Ptr(Int32),
    X1: Float32[Flat],
    INCX1: Ptr(Int32),
    X2: Float32[Flat],
    INCX2: Ptr(Int32),
    Q1: Float32[LDQ1, Flat],
    LDQ1: Ptr(Int32),
    Q2: Float32[LDQ2, Flat],
    LDQ2: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORCSD")
@external
def sorcsd(
    JOBU1: Ptr(Const(String[1])),
    JOBU2: Ptr(Const(String[1])),
    JOBV1T: Ptr(Const(String[1])),
    JOBV2T: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    SIGNS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Float32[LDX11, Flat],
    LDX11: Ptr(Int32),
    X12: Float32[LDX12, Flat],
    LDX12: Ptr(Int32),
    X21: Float32[LDX21, Flat],
    LDX21: Ptr(Int32),
    X22: Float32[LDX22, Flat],
    LDX22: Ptr(Int32),
    THETA: Float32[Flat],
    U1: Float32[LDU1, Flat],
    LDU1: Ptr(Int32),
    U2: Float32[LDU2, Flat],
    LDU2: Ptr(Int32),
    V1T: Float32[LDV1T, Flat],
    LDV1T: Ptr(Int32),
    V2T: Float32[LDV2T, Flat],
    LDV2T: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORCSD2BY1")
@external
def sorcsd2by1(
    JOBU1: Ptr(Const(String[1])),
    JOBU2: Ptr(Const(String[1])),
    JOBV1T: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Float32[LDX11, Flat],
    LDX11: Ptr(Int32),
    X21: Float32[LDX21, Flat],
    LDX21: Ptr(Int32),
    THETA: Float32[Flat],
    U1: Float32[LDU1, Flat],
    LDU1: Ptr(Int32),
    U2: Float32[LDU2, Flat],
    LDU2: Ptr(Int32),
    V1T: Float32[LDV1T, Flat],
    LDV1T: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORG2L")
@external
def sorg2l(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORG2R")
@external
def sorg2r(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORGBR")
@external
def sorgbr(
    VECT: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORGHR")
@external
def sorghr(
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORGL2")
@external
def sorgl2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORGLQ")
@external
def sorglq(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORGQL")
@external
def sorgql(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORGQR")
@external
def sorgqr(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORGR2")
@external
def sorgr2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORGRQ")
@external
def sorgrq(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORGTR")
@external
def sorgtr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORGTSQR")
@external
def sorgtsqr(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORGTSQR_ROW")
@external
def sorgtsqr_row(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORHR_COL")
@external
def sorhr_col(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    D: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORM22")
@external
def sorm22(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    N1: Ptr(Int32),
    N2: Ptr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORM2L")
@external
def sorm2l(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORM2R")
@external
def sorm2r(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORMBR")
@external
def sormbr(
    VECT: Ptr(Const(String[1])),
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORMHR")
@external
def sormhr(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORML2")
@external
def sorml2(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORMLQ")
@external
def sormlq(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORMQL")
@external
def sormql(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORMQR")
@external
def sormqr(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORMR2")
@external
def sormr2(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORMR3")
@external
def sormr3(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORMRQ")
@external
def sormrq(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORMRZ")
@external
def sormrz(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SORMTR")
@external
def sormtr(
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPBCON")
@external
def spbcon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPBEQU")
@external
def spbequ(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    S: Float32[Flat],
    SCOND: Ptr(Float32),
    AMAX: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPBRFS")
@external
def spbrfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPBSTF")
@external
def spbstf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPBSV")
@external
def spbsv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPBSVX")
@external
def spbsvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Float32[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    EQUED: Ptr(Const(String[1])),
    S: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPBTF2")
@external
def spbtf2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPBTRF")
@external
def spbtrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPBTRS")
@external
def spbtrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPFTRF")
@external
def spftrf(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Float32[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPFTRI")
@external
def spftri(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Float32[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPFTRS")
@external
def spftrs(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Annotated[Float32[Flat], SourceDims("0:*")],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPOCON")
@external
def spocon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPOEQU")
@external
def spoequ(
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float32[Flat],
    SCOND: Ptr(Float32),
    AMAX: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPOEQUB")
@external
def spoequb(
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float32[Flat],
    SCOND: Ptr(Float32),
    AMAX: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPORFS")
@external
def sporfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPORFSX")
@external
def sporfsx(
    UPLO: Ptr(Const(String[1])),
    EQUED: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ptr(Int32),
    S: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPOSV")
@external
def sposv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPOSVX")
@external
def sposvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ptr(Int32),
    EQUED: Ptr(Const(String[1])),
    S: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPOSVXX")
@external
def sposvxx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ptr(Int32),
    EQUED: Ptr(Const(String[1])),
    S: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    RPVGRW: Ptr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPOTF2")
@external
def spotf2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPOTRF")
@external
def spotrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPOTRF2")
@external
def spotrf2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPOTRI")
@external
def spotri(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPOTRS")
@external
def spotrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPPCON")
@external
def sppcon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPPEQU")
@external
def sppequ(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    S: Float32[Flat],
    SCOND: Ptr(Float32),
    AMAX: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPPRFS")
@external
def spprfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Float32[Flat],
    AFP: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPPSV")
@external
def sppsv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPPSVX")
@external
def sppsvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Float32[Flat],
    AFP: Float32[Flat],
    EQUED: Ptr(Const(String[1])),
    S: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPPTRF")
@external
def spptrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPPTRI")
@external
def spptri(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPPTRS")
@external
def spptrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPSTF2")
@external
def spstf2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    PIV: Int32[N],
    RANK: Ptr(Int32),
    TOL: Ptr(Float32),
    WORK: Float32[2 * N],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPSTRF")
@external
def spstrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    PIV: Int32[N],
    RANK: Ptr(Int32),
    TOL: Ptr(Float32),
    WORK: Float32[2 * N],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPTCON")
@external
def sptcon(
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPTEQR")
@external
def spteqr(
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPTRFS")
@external
def sptrfs(
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    DF: Float32[Flat],
    EF: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPTSV")
@external
def sptsv(
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPTSVX")
@external
def sptsvx(
    FACT: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    DF: Float32[Flat],
    EF: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPTTRF")
@external
def spttrf(
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPTTRS")
@external
def spttrs(
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SPTTS2")
@external
def sptts2(
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("SRSCL")
@external
def srscl(
    N: Ptr(Int32),
    SA: Ptr(Float32),
    SX: Float32[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("SSB2ST_KERNELS")
@external
def ssb2st_kernels(
    UPLO: Ptr(Const(String[1])),
    WANTZ: Ptr(Bool),
    TTYPE: Ptr(Int32),
    ST: Ptr(Int32),
    ED: Ptr(Int32),
    SWEEP: Ptr(Int32),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    IB: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    V: Float32[Flat],
    TAU: Float32[Flat],
    LDVT: Ptr(Int32),
    WORK: Float32[Flat]
) -> None: ...

@bind("SSBEV")
@external
def ssbev(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSBEV_2STAGE")
@external
def ssbev_2stage(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSBEVD")
@external
def ssbevd(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSBEVD_2STAGE")
@external
def ssbevd_2stage(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSBEVX")
@external
def ssbevx(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSBEVX_2STAGE")
@external
def ssbevx_2stage(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSBGST")
@external
def ssbgst(
    VECT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KA: Ptr(Int32),
    KB: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    BB: Float32[LDBB, Flat],
    LDBB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSBGV")
@external
def ssbgv(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KA: Ptr(Int32),
    KB: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    BB: Float32[LDBB, Flat],
    LDBB: Ptr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSBGVD")
@external
def ssbgvd(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KA: Ptr(Int32),
    KB: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    BB: Float32[LDBB, Flat],
    LDBB: Ptr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSBGVX")
@external
def ssbgvx(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KA: Ptr(Int32),
    KB: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    BB: Float32[LDBB, Flat],
    LDBB: Ptr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSBTRD")
@external
def ssbtrd(
    VECT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSFRK")
@external
def ssfrk(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Float32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    BETA: Ptr(Float32),
    C: Float32[Flat]
) -> None: ...

@bind("SSPCON")
@external
def sspcon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    IPIV: Int32[Flat],
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSPEV")
@external
def sspev(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSPEVD")
@external
def sspevd(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSPEVX")
@external
def sspevx(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSPGST")
@external
def sspgst(
    ITYPE: Ptr(Int32),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    BP: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSPGV")
@external
def sspgv(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    BP: Float32[Flat],
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSPGVD")
@external
def sspgvd(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    BP: Float32[Flat],
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSPGVX")
@external
def sspgvx(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    BP: Float32[Flat],
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSPRFS")
@external
def ssprfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Float32[Flat],
    AFP: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSPSV")
@external
def sspsv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSPSVX")
@external
def sspsvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Float32[Flat],
    AFP: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSPTRD")
@external
def ssptrd(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSPTRF")
@external
def ssptrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSPTRI")
@external
def ssptri(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSPTRS")
@external
def ssptrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSTEBZ")
@external
def sstebz(
    RANGE: Ptr(Const(String[1])),
    ORDER: Ptr(Const(String[1])),
    N: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    D: Float32[Flat],
    E: Float32[Flat],
    M: Ptr(Int32),
    NSPLIT: Ptr(Int32),
    W: Float32[Flat],
    IBLOCK: Int32[Flat],
    ISPLIT: Int32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSTEDC")
@external
def sstedc(
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSTEGR")
@external
def sstegr(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSTEIN")
@external
def sstein(
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    M: Ptr(Int32),
    W: Float32[Flat],
    IBLOCK: Int32[Flat],
    ISPLIT: Int32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSTEMR")
@external
def sstemr(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    NZC: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    TRYRAC: Ptr(Bool),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSTEQR")
@external
def ssteqr(
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSTERF")
@external
def ssterf(
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSTEV")
@external
def sstev(
    JOBZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSTEVD")
@external
def sstevd(
    JOBZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSTEVR")
@external
def sstevr(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSTEVX")
@external
def sstevx(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYCON")
@external
def ssycon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYCON_3")
@external
def ssycon_3(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYCON_ROOK")
@external
def ssycon_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    ANORM: Ptr(Float32),
    RCOND: Ptr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYCONV")
@external
def ssyconv(
    UPLO: Ptr(Const(String[1])),
    WAY: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    E: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYCONVF")
@external
def ssyconvf(
    UPLO: Ptr(Const(String[1])),
    WAY: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYCONVF_ROOK")
@external
def ssyconvf_rook(
    UPLO: Ptr(Const(String[1])),
    WAY: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYEQUB")
@external
def ssyequb(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float32[Flat],
    SCOND: Ptr(Float32),
    AMAX: Ptr(Float32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYEV")
@external
def ssyev(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    W: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYEV_2STAGE")
@external
def ssyev_2stage(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    W: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYEVD")
@external
def ssyevd(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    W: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYEVD_2STAGE")
@external
def ssyevd_2stage(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    W: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYEVR")
@external
def ssyevr(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYEVR_2STAGE")
@external
def ssyevr_2stage(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYEVX")
@external
def ssyevx(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYEVX_2STAGE")
@external
def ssyevx_2stage(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYGS2")
@external
def ssygs2(
    ITYPE: Ptr(Int32),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYGST")
@external
def ssygst(
    ITYPE: Ptr(Int32),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYGV")
@external
def ssygv(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    W: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYGV_2STAGE")
@external
def ssygv_2stage(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    W: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYGVD")
@external
def ssygvd(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    W: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYGVX")
@external
def ssygvx(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    VL: Ptr(Float32),
    VU: Ptr(Float32),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float32),
    M: Ptr(Int32),
    W: Float32[Flat],
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYRFS")
@external
def ssyrfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYRFSX")
@external
def ssyrfsx(
    UPLO: Ptr(Const(String[1])),
    EQUED: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    S: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYSV")
@external
def ssysv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYSV_AA")
@external
def ssysv_aa(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYSV_AA_2STAGE")
@external
def ssysv_aa_2stage(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TB: Float32[Flat],
    LTB: Ptr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYSV_RK")
@external
def ssysv_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYSV_ROOK")
@external
def ssysv_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYSVX")
@external
def ssysvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYSVXX")
@external
def ssysvxx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Float32[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    EQUED: Ptr(Const(String[1])),
    S: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float32),
    RPVGRW: Ptr(Float32),
    BERR: Float32[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float32[NRHS, Flat],
    ERR_BNDS_COMP: Float32[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYSWAPR")
@external
def ssyswapr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    I1: Ptr(Int32),
    I2: Ptr(Int32)
) -> None: ...

@bind("SSYTD2")
@external
def ssytd2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTF2")
@external
def ssytf2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTF2_RK")
@external
def ssytf2_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTF2_ROOK")
@external
def ssytf2_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTRD")
@external
def ssytrd(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTRD_2STAGE")
@external
def ssytrd_2stage(
    VECT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    TAU: Float32[Flat],
    HOUS2: Float32[Flat],
    LHOUS2: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTRD_SB2ST")
@external
def ssytrd_sb2st(
    STAGE1: Ptr(Const(String[1])),
    VECT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    D: Float32[Flat],
    E: Float32[Flat],
    HOUS: Float32[Flat],
    LHOUS: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTRD_SY2SB")
@external
def ssytrd_sy2sb(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTRF")
@external
def ssytrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTRF_AA")
@external
def ssytrf_aa(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTRF_AA_2STAGE")
@external
def ssytrf_aa_2stage(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TB: Float32[Flat],
    LTB: Ptr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTRF_RK")
@external
def ssytrf_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTRF_ROOK")
@external
def ssytrf_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTRI")
@external
def ssytri(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTRI2")
@external
def ssytri2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTRI2X")
@external
def ssytri2x(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[N + NB + 1, Flat],
    NB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTRI_3")
@external
def ssytri_3(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTRI_3X")
@external
def ssytri_3x(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    WORK: Float32[N + NB + 1, Flat],
    NB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTRI_ROOK")
@external
def ssytri_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTRS")
@external
def ssytrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTRS2")
@external
def ssytrs2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTRS_3")
@external
def ssytrs_3(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float32[Flat],
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTRS_AA")
@external
def ssytrs_aa(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTRS_AA_2STAGE")
@external
def ssytrs_aa_2stage(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TB: Float32[Flat],
    LTB: Ptr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("SSYTRS_ROOK")
@external
def ssytrs_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("STBCON")
@external
def stbcon(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    RCOND: Ptr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("STBRFS")
@external
def stbrfs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("STBTRS")
@external
def stbtrs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Float32[LDAB, Flat],
    LDAB: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("STFSM")
@external
def stfsm(
    TRANSR: Ptr(Const(String[1])),
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Float32),
    A: Annotated[Float32[Flat], SourceDims("0:*")],
    B: Annotated[Float32[0:LDB-1, Flat], SourceDims("0:LDB-1", "0:*")],
    LDB: Ptr(Int32)
) -> None: ...

@bind("STFTRI")
@external
def stftri(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Float32[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("STFTTP")
@external
def stfttp(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ARF: Annotated[Float32[Flat], SourceDims("0:*")],
    AP: Annotated[Float32[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("STFTTR")
@external
def stfttr(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ARF: Annotated[Float32[Flat], SourceDims("0:*")],
    A: Annotated[Float32[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("STGEVC")
@external
def stgevc(
    SIDE: Ptr(Const(String[1])),
    HOWMNY: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    S: Float32[LDS, Flat],
    LDS: Ptr(Int32),
    P: Float32[LDP, Flat],
    LDP: Ptr(Int32),
    VL: Float32[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Ptr(Int32),
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("STGEX2")
@external
def stgex2(
    WANTQ: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    J1: Ptr(Int32),
    N1: Ptr(Int32),
    N2: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("STGEXC")
@external
def stgexc(
    WANTQ: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    IFST: Ptr(Int32),
    ILST: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("STGSEN")
@external
def stgsen(
    IJOB: Ptr(Int32),
    WANTQ: Ptr(Bool),
    WANTZ: Ptr(Bool),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    ALPHAR: Float32[Flat],
    ALPHAI: Float32[Flat],
    BETA: Float32[Flat],
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Float32[LDZ, Flat],
    LDZ: Ptr(Int32),
    M: Ptr(Int32),
    PL: Ptr(Float32),
    PR: Ptr(Float32),
    DIF: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("STGSJA")
@external
def stgsja(
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    JOBQ: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    TOLA: Ptr(Float32),
    TOLB: Ptr(Float32),
    ALPHA: Float32[Flat],
    BETA: Float32[Flat],
    U: Float32[LDU, Flat],
    LDU: Ptr(Int32),
    V: Float32[LDV, Flat],
    LDV: Ptr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    WORK: Float32[Flat],
    NCYCLE: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("STGSNA")
@external
def stgsna(
    JOB: Ptr(Const(String[1])),
    HOWMNY: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    VL: Float32[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Ptr(Int32),
    S: Float32[Flat],
    DIF: Float32[Flat],
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("STGSY2")
@external
def stgsy2(
    TRANS: Ptr(Const(String[1])),
    IJOB: Ptr(Int32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    D: Float32[LDD, Flat],
    LDD: Ptr(Int32),
    E: Float32[LDE, Flat],
    LDE: Ptr(Int32),
    F: Float32[LDF, Flat],
    LDF: Ptr(Int32),
    SCALE: Ptr(Float32),
    RDSUM: Ptr(Float32),
    RDSCAL: Ptr(Float32),
    IWORK: Int32[Flat],
    PQ: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("STGSYL")
@external
def stgsyl(
    TRANS: Ptr(Const(String[1])),
    IJOB: Ptr(Int32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    D: Float32[LDD, Flat],
    LDD: Ptr(Int32),
    E: Float32[LDE, Flat],
    LDE: Ptr(Int32),
    F: Float32[LDF, Flat],
    LDF: Ptr(Int32),
    SCALE: Ptr(Float32),
    DIF: Ptr(Float32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("STPCON")
@external
def stpcon(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    RCOND: Ptr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("STPLQT")
@external
def stplqt(
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    MB: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("STPLQT2")
@external
def stplqt2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("STPMLQT")
@external
def stpmlqt(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    MB: Ptr(Int32),
    V: Float32[LDV, Flat],
    LDV: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("STPMQRT")
@external
def stpmqrt(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    NB: Ptr(Int32),
    V: Float32[LDV, Flat],
    LDV: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("STPQRT")
@external
def stpqrt(
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    NB: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("STPQRT2")
@external
def stpqrt2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("STPRFB")
@external
def stprfb(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIRECT: Ptr(Const(String[1])),
    STOREV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    V: Float32[LDV, Flat],
    LDV: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Float32[LDWORK, Flat],
    LDWORK: Ptr(Int32)
) -> None: ...

@bind("STPRFS")
@external
def stprfs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("STPTRI")
@external
def stptri(
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("STPTRS")
@external
def stptrs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Float32[Flat],
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("STPTTF")
@external
def stpttf(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Annotated[Float32[Flat], SourceDims("0:*")],
    ARF: Annotated[Float32[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("STPTTR")
@external
def stpttr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Float32[Flat],
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("STRCON")
@external
def strcon(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    RCOND: Ptr(Float32),
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("STREVC")
@external
def strevc(
    SIDE: Ptr(Const(String[1])),
    HOWMNY: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    VL: Float32[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Ptr(Int32),
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("STREVC3")
@external
def strevc3(
    SIDE: Ptr(Const(String[1])),
    HOWMNY: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    VL: Float32[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Ptr(Int32),
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("STREXC")
@external
def strexc(
    COMPQ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    IFST: Ptr(Int32),
    ILST: Ptr(Int32),
    WORK: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("STRRFS")
@external
def strrfs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    X: Float32[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float32[Flat],
    BERR: Float32[Flat],
    WORK: Float32[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("STRSEN")
@external
def strsen(
    JOB: Ptr(Const(String[1])),
    COMPQ: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    Q: Float32[LDQ, Flat],
    LDQ: Ptr(Int32),
    WR: Float32[Flat],
    WI: Float32[Flat],
    M: Ptr(Int32),
    S: Ptr(Float32),
    SEP: Ptr(Float32),
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("STRSNA")
@external
def strsna(
    JOB: Ptr(Const(String[1])),
    HOWMNY: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    T: Float32[LDT, Flat],
    LDT: Ptr(Int32),
    VL: Float32[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Float32[LDVR, Flat],
    LDVR: Ptr(Int32),
    S: Float32[Flat],
    SEP: Float32[Flat],
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Float32[LDWORK, Flat],
    LDWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("STRSYL")
@external
def strsyl(
    TRANA: Ptr(Const(String[1])),
    TRANB: Ptr(Const(String[1])),
    ISGN: Ptr(Int32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    SCALE: Ptr(Float32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("STRSYL3")
@external
def strsyl3(
    TRANA: Ptr(Const(String[1])),
    TRANB: Ptr(Const(String[1])),
    ISGN: Ptr(Int32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    C: Float32[LDC, Flat],
    LDC: Ptr(Int32),
    SCALE: Ptr(Float32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    SWORK: Float32[LDSWORK, Flat],
    LDSWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("STRTI2")
@external
def strti2(
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("STRTRI")
@external
def strtri(
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("STRTRS")
@external
def strtrs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float32[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("STRTTF")
@external
def strttf(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Float32[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Ptr(Int32),
    ARF: Annotated[Float32[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("STRTTP")
@external
def strttp(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    AP: Float32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("STZRZF")
@external
def stzrzf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float32[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Float32[Flat],
    WORK: Float32[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
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

@bind("ZBBCSD")
@external
def zbbcsd(
    JOBU1: Ptr(Const(String[1])),
    JOBU2: Ptr(Const(String[1])),
    JOBV1T: Ptr(Const(String[1])),
    JOBV2T: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    U1: Complex128[LDU1, Flat],
    LDU1: Ptr(Int32),
    U2: Complex128[LDU2, Flat],
    LDU2: Ptr(Int32),
    V1T: Complex128[LDV1T, Flat],
    LDV1T: Ptr(Int32),
    V2T: Complex128[LDV2T, Flat],
    LDV2T: Ptr(Int32),
    B11D: Float64[Flat],
    B11E: Float64[Flat],
    B12D: Float64[Flat],
    B12E: Float64[Flat],
    B21D: Float64[Flat],
    B21E: Float64[Flat],
    B22D: Float64[Flat],
    B22E: Float64[Flat],
    RWORK: Float64[Flat],
    LRWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZBDSQR")
@external
def zbdsqr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NCVT: Ptr(Int32),
    NRU: Ptr(Int32),
    NCC: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VT: Complex128[LDVT, Flat],
    LDVT: Ptr(Int32),
    U: Complex128[LDU, Flat],
    LDU: Ptr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZCGESV")
@external
def zcgesv(
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    WORK: Complex128[N, Flat],
    SWORK: Complex64[Flat],
    RWORK: Float64[Flat],
    ITER: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZCPOSV")
@external
def zcposv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    WORK: Complex128[N, Flat],
    SWORK: Complex64[Flat],
    RWORK: Float64[Flat],
    ITER: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZDRSCL")
@external
def zdrscl(
    N: Ptr(Int32),
    SA: Ptr(Float64),
    SX: Complex128[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("ZGBBRD")
@external
def zgbbrd(
    VECT: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    NCC: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Int32),
    PT: Complex128[LDPT, Flat],
    LDPT: Ptr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGBCON")
@external
def zgbcon(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    IPIV: Int32[Flat],
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGBEQU")
@external
def zgbequ(
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ptr(Float64),
    COLCND: Ptr(Float64),
    AMAX: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGBEQUB")
@external
def zgbequb(
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ptr(Float64),
    COLCND: Ptr(Float64),
    AMAX: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGBRFS")
@external
def zgbrfs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGBRFSX")
@external
def zgbrfsx(
    TRANS: Ptr(Const(String[1])),
    EQUED: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    R: Float64[Flat],
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGBSV")
@external
def zgbsv(
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGBSVX")
@external
def zgbsvx(
    FACT: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    EQUED: Ptr(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGBSVXX")
@external
def zgbsvxx(
    FACT: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    EQUED: Ptr(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    RPVGRW: Ptr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGBTF2")
@external
def zgbtf2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGBTRF")
@external
def zgbtrf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGBTRS")
@external
def zgbtrs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEBAK")
@external
def zgebak(
    JOB: Ptr(Const(String[1])),
    SIDE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    SCALE: Float64[Flat],
    M: Ptr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEBAL")
@external
def zgebal(
    JOB: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    SCALE: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEBD2")
@external
def zgebd2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAUQ: Complex128[Flat],
    TAUP: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEBRD")
@external
def zgebrd(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAUQ: Complex128[Flat],
    TAUP: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGECON")
@external
def zgecon(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEDMD")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7), Arg(8), Arg(9), Arg(10), Arg(11), Arg(12), Return('K', 0), Arg(13), Arg(14), Arg(15), Arg(16), Arg(17), Arg(18), Arg(19), Arg(20), Arg(21), Arg(22), Arg(23), Arg(24), Arg(25), Arg(26), Arg(27), Arg(28), Return('INFO', 10)])
def zgedmd(
    JOBS: Ptr(Const(String[1])),
    JOBZ: Ptr(Const(String[1])),
    JOBR: Ptr(Const(String[1])),
    JOBF: Ptr(Const(String[1])),
    WHTSVD: Ptr(Const(Int32)),
    M: Ptr(Const(Int32)),
    N: Ptr(Const(Int32)),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Const(Int32)),
    Y: Complex128[LDY, Flat],
    LDY: Ptr(Const(Int32)),
    NRNK: Ptr(Const(Int32)),
    TOL: Ptr(Const(Float64)),
    EIGS: Complex128[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Const(Int32)),
    RES: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    W: Complex128[LDW, Flat],
    LDW: Ptr(Const(Int32)),
    S: Complex128[LDS, Flat],
    LDS: Ptr(Const(Int32)),
    ZWORK: Complex128[Flat],
    LZWORK: Ptr(Const(Int32)),
    RWORK: Float64[Flat],
    LRWORK: Ptr(Const(Int32)),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Const(Int32))
) -> tuple[Int32, Returns["EIGS", Complex128[Flat]], Returns["Z", Complex128[LDZ, Flat]], Returns["RES", Float64[Flat]], Returns["B", Complex128[LDB, Flat]], Returns["W", Complex128[LDW, Flat]], Returns["S", Complex128[LDS, Flat]], Returns["ZWORK", Complex128[Flat]], Returns["RWORK", Float64[Flat]], Returns["IWORK", Int32[Flat]], Int32]: ...

@bind("ZGEDMDQ")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7), Arg(8), Arg(9), Arg(10), Arg(11), Arg(12), Arg(13), Arg(14), Arg(15), Arg(16), Return('K', 2), Arg(17), Arg(18), Arg(19), Arg(20), Arg(21), Arg(22), Arg(23), Arg(24), Arg(25), Arg(26), Arg(27), Arg(28), Arg(29), Arg(30), Arg(31), Arg(32), Return('INFO', 12)])
def zgedmdq(
    JOBS: Ptr(Const(String[1])),
    JOBZ: Ptr(Const(String[1])),
    JOBR: Ptr(Const(String[1])),
    JOBQ: Ptr(Const(String[1])),
    JOBT: Ptr(Const(String[1])),
    JOBF: Ptr(Const(String[1])),
    WHTSVD: Ptr(Const(Int32)),
    M: Ptr(Const(Int32)),
    N: Ptr(Const(Int32)),
    F: Complex128[LDF, Flat],
    LDF: Ptr(Const(Int32)),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Const(Int32)),
    Y: Complex128[LDY, Flat],
    LDY: Ptr(Const(Int32)),
    NRNK: Ptr(Const(Int32)),
    TOL: Ptr(Const(Float64)),
    EIGS: Complex128[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Const(Int32)),
    RES: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    V: Complex128[LDV, Flat],
    LDV: Ptr(Const(Int32)),
    S: Complex128[LDS, Flat],
    LDS: Ptr(Const(Int32)),
    ZWORK: Complex128[Flat],
    LZWORK: Ptr(Const(Int32)),
    WORK: Float64[Flat],
    LWORK: Ptr(Const(Int32)),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Const(Int32))
) -> tuple[Returns["X", Complex128[LDX, Flat]], Returns["Y", Complex128[LDY, Flat]], Int32, Returns["EIGS", Complex128[Flat]], Returns["Z", Complex128[LDZ, Flat]], Returns["RES", Float64[Flat]], Returns["B", Complex128[LDB, Flat]], Returns["V", Complex128[LDV, Flat]], Returns["S", Complex128[LDS, Flat]], Returns["ZWORK", Complex128[Flat]], Returns["WORK", Float64[Flat]], Returns["IWORK", Int32[Flat]], Int32]: ...

@bind("ZGEEQU")
@external
def zgeequ(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ptr(Float64),
    COLCND: Ptr(Float64),
    AMAX: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEEQUB")
@external
def zgeequb(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ptr(Float64),
    COLCND: Ptr(Float64),
    AMAX: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEES")
@external
def zgees(
    JOBVS: Ptr(Const(String[1])),
    SORT: Ptr(Const(String[1])),
    SELECT: Ptr(Bool),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    SDIM: Ptr(Int32),
    W: Complex128[Flat],
    VS: Complex128[LDVS, Flat],
    LDVS: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEESX")
@external
def zgeesx(
    JOBVS: Ptr(Const(String[1])),
    SORT: Ptr(Const(String[1])),
    SELECT: Ptr(Bool),
    SENSE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    SDIM: Ptr(Int32),
    W: Complex128[Flat],
    VS: Complex128[LDVS, Flat],
    LDVS: Ptr(Int32),
    RCONDE: Ptr(Float64),
    RCONDV: Ptr(Float64),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEEV")
@external
def zgeev(
    JOBVL: Ptr(Const(String[1])),
    JOBVR: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    W: Complex128[Flat],
    VL: Complex128[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEEVX")
@external
def zgeevx(
    BALANC: Ptr(Const(String[1])),
    JOBVL: Ptr(Const(String[1])),
    JOBVR: Ptr(Const(String[1])),
    SENSE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    W: Complex128[Flat],
    VL: Complex128[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    SCALE: Float64[Flat],
    ABNRM: Ptr(Float64),
    RCONDE: Float64[Flat],
    RCONDV: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEHD2")
@external
def zgehd2(
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEHRD")
@external
def zgehrd(
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEJSV")
@external
def zgejsv(
    JOBA: Ptr(Const(String[1])),
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    JOBR: Ptr(Const(String[1])),
    JOBT: Ptr(Const(String[1])),
    JOBP: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    SVA: Float64[N],
    U: Complex128[LDU, Flat],
    LDU: Ptr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ptr(Int32),
    CWORK: Complex128[LWORK],
    LWORK: Ptr(Int32),
    RWORK: Float64[LRWORK],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGELQ")
@external
def zgelq(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex128[Flat],
    TSIZE: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGELQ2")
@external
def zgelq2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGELQF")
@external
def zgelqf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGELQT")
@external
def zgelqt(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGELQT3")
@external
def zgelqt3(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGELS")
@external
def zgels(
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGELSD")
@external
def zgelsd(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    S: Float64[Flat],
    RCOND: Ptr(Float64),
    RANK: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGELSS")
@external
def zgelss(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    S: Float64[Flat],
    RCOND: Ptr(Float64),
    RANK: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGELST")
@external
def zgelst(
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGELSY")
@external
def zgelsy(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    JPVT: Int32[Flat],
    RCOND: Ptr(Float64),
    RANK: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEMLQ")
@external
def zgemlq(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex128[Flat],
    TSIZE: Ptr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEMLQT")
@external
def zgemlqt(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    MB: Ptr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEMQR")
@external
def zgemqr(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex128[Flat],
    TSIZE: Ptr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEMQRT")
@external
def zgemqrt(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    NB: Ptr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEQL2")
@external
def zgeql2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEQLF")
@external
def zgeqlf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEQP3")
@external
def zgeqp3(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    JPVT: Int32[Flat],
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEQP3RK")
@external
def zgeqp3rk(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    KMAX: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    RELTOL: Ptr(Float64),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    K: Ptr(Int32),
    MAXC2NRMK: Ptr(Float64),
    RELMAXC2NRMK: Ptr(Float64),
    JPIV: Int32[Flat],
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEQR")
@external
def zgeqr(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex128[Flat],
    TSIZE: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEQR2")
@external
def zgeqr2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEQR2P")
@external
def zgeqr2p(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEQRF")
@external
def zgeqrf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEQRFP")
@external
def zgeqrfp(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEQRT")
@external
def zgeqrt(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEQRT2")
@external
def zgeqrt2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGEQRT3")
@external
def zgeqrt3(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGERFS")
@external
def zgerfs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGERFSX")
@external
def zgerfsx(
    TRANS: Ptr(Const(String[1])),
    EQUED: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    R: Float64[Flat],
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGERQ2")
@external
def zgerq2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGERQF")
@external
def zgerqf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGESC2")
@external
def zgesc2(
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    RHS: Complex128[Flat],
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    SCALE: Ptr(Float64)
) -> None: ...

@bind("ZGESDD")
@external
def zgesdd(
    JOBZ: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float64[Flat],
    U: Complex128[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Complex128[LDVT, Flat],
    LDVT: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGESV")
@external
def zgesv(
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGESVD")
@external
def zgesvd(
    JOBU: Ptr(Const(String[1])),
    JOBVT: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float64[Flat],
    U: Complex128[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Complex128[LDVT, Flat],
    LDVT: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGESVDQ")
@external
def zgesvdq(
    JOBA: Ptr(Const(String[1])),
    JOBP: Ptr(Const(String[1])),
    JOBR: Ptr(Const(String[1])),
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float64[Flat],
    U: Complex128[LDU, Flat],
    LDU: Ptr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ptr(Int32),
    NUMRANK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    CWORK: Complex128[Flat],
    LCWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGESVDX")
@external
def zgesvdx(
    JOBU: Ptr(Const(String[1])),
    JOBVT: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    NS: Ptr(Int32),
    S: Float64[Flat],
    U: Complex128[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Complex128[LDVT, Flat],
    LDVT: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGESVJ")
@external
def zgesvj(
    JOBA: Ptr(Const(String[1])),
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    SVA: Float64[N],
    MV: Ptr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ptr(Int32),
    CWORK: Complex128[LWORK],
    LWORK: Ptr(Int32),
    RWORK: Float64[LRWORK],
    LRWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGESVX")
@external
def zgesvx(
    FACT: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    EQUED: Ptr(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGESVXX")
@external
def zgesvxx(
    FACT: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    EQUED: Ptr(Const(String[1])),
    R: Float64[Flat],
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    RPVGRW: Ptr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGETC2")
@external
def zgetc2(
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGETF2")
@external
def zgetf2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGETRF")
@external
def zgetrf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGETRF2")
@external
def zgetrf2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGETRI")
@external
def zgetri(
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGETRS")
@external
def zgetrs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGETSLS")
@external
def zgetsls(
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGETSQRHRT")
@external
def zgetsqrhrt(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB1: Ptr(Int32),
    NB1: Ptr(Int32),
    NB2: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGGBAK")
@external
def zggbak(
    JOB: Ptr(Const(String[1])),
    SIDE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    LSCALE: Float64[Flat],
    RSCALE: Float64[Flat],
    M: Ptr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGGBAL")
@external
def zggbal(
    JOB: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    LSCALE: Float64[Flat],
    RSCALE: Float64[Flat],
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGGES")
@external
def zgges(
    JOBVSL: Ptr(Const(String[1])),
    JOBVSR: Ptr(Const(String[1])),
    SORT: Ptr(Const(String[1])),
    SELCTG: Ptr(Bool),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    SDIM: Ptr(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    VSL: Complex128[LDVSL, Flat],
    LDVSL: Ptr(Int32),
    VSR: Complex128[LDVSR, Flat],
    LDVSR: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGGES3")
@external
def zgges3(
    JOBVSL: Ptr(Const(String[1])),
    JOBVSR: Ptr(Const(String[1])),
    SORT: Ptr(Const(String[1])),
    SELCTG: Ptr(Bool),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    SDIM: Ptr(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    VSL: Complex128[LDVSL, Flat],
    LDVSL: Ptr(Int32),
    VSR: Complex128[LDVSR, Flat],
    LDVSR: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGGESX")
@external
def zggesx(
    JOBVSL: Ptr(Const(String[1])),
    JOBVSR: Ptr(Const(String[1])),
    SORT: Ptr(Const(String[1])),
    SELCTG: Ptr(Bool),
    SENSE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    SDIM: Ptr(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    VSL: Complex128[LDVSL, Flat],
    LDVSL: Ptr(Int32),
    VSR: Complex128[LDVSR, Flat],
    LDVSR: Ptr(Int32),
    RCONDE: Float64[2],
    RCONDV: Float64[2],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGGEV")
@external
def zggev(
    JOBVL: Ptr(Const(String[1])),
    JOBVR: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    VL: Complex128[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGGEV3")
@external
def zggev3(
    JOBVL: Ptr(Const(String[1])),
    JOBVR: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    VL: Complex128[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGGEVX")
@external
def zggevx(
    BALANC: Ptr(Const(String[1])),
    JOBVL: Ptr(Const(String[1])),
    JOBVR: Ptr(Const(String[1])),
    SENSE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    VL: Complex128[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    LSCALE: Float64[Flat],
    RSCALE: Float64[Flat],
    ABNRM: Ptr(Float64),
    BBNRM: Ptr(Float64),
    RCONDE: Float64[Flat],
    RCONDV: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    BWORK: Bool[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGGGLM")
@external
def zggglm(
    N: Ptr(Int32),
    M: Ptr(Int32),
    P: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    D: Complex128[Flat],
    X: Complex128[Flat],
    Y: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGGHD3")
@external
def zgghd3(
    COMPQ: Ptr(Const(String[1])),
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGGHRD")
@external
def zgghrd(
    COMPQ: Ptr(Const(String[1])),
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGGLSE")
@external
def zgglse(
    M: Ptr(Int32),
    N: Ptr(Int32),
    P: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    C: Complex128[Flat],
    D: Complex128[Flat],
    X: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGGQRF")
@external
def zggqrf(
    N: Ptr(Int32),
    M: Ptr(Int32),
    P: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAUA: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    TAUB: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGGRQF")
@external
def zggrqf(
    M: Ptr(Int32),
    P: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAUA: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    TAUB: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGGSVD3")
@external
def zggsvd3(
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    JOBQ: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    P: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    ALPHA: Float64[Flat],
    BETA: Float64[Flat],
    U: Complex128[LDU, Flat],
    LDU: Ptr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ptr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGGSVP3")
@external
def zggsvp3(
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    JOBQ: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    TOLA: Ptr(Float64),
    TOLB: Ptr(Float64),
    K: Ptr(Int32),
    L: Ptr(Int32),
    U: Complex128[LDU, Flat],
    LDU: Ptr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ptr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Int32),
    IWORK: Int32[Flat],
    RWORK: Float64[Flat],
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGSVJ0")
@external
def zgsvj0(
    JOBV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    D: Complex128[N],
    SVA: Float64[N],
    MV: Ptr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ptr(Int32),
    EPS: Ptr(Float64),
    SFMIN: Ptr(Float64),
    TOL: Ptr(Float64),
    NSWEEP: Ptr(Int32),
    WORK: Complex128[LWORK],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGSVJ1")
@external
def zgsvj1(
    JOBV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    N1: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    D: Complex128[N],
    SVA: Float64[N],
    MV: Ptr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ptr(Int32),
    EPS: Ptr(Float64),
    SFMIN: Ptr(Float64),
    TOL: Ptr(Float64),
    NSWEEP: Ptr(Int32),
    WORK: Complex128[LWORK],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGTCON")
@external
def zgtcon(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    DU2: Complex128[Flat],
    IPIV: Int32[Flat],
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGTRFS")
@external
def zgtrfs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    DLF: Complex128[Flat],
    DF: Complex128[Flat],
    DUF: Complex128[Flat],
    DU2: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGTSV")
@external
def zgtsv(
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGTSVX")
@external
def zgtsvx(
    FACT: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    DLF: Complex128[Flat],
    DF: Complex128[Flat],
    DUF: Complex128[Flat],
    DU2: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGTTRF")
@external
def zgttrf(
    N: Ptr(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    DU2: Complex128[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGTTRS")
@external
def zgttrs(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    DU2: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZGTTS2")
@external
def zgtts2(
    ITRANS: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    DU2: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("ZHB2ST_KERNELS")
@external
def zhb2st_kernels(
    UPLO: Ptr(Const(String[1])),
    WANTZ: Ptr(Bool),
    TTYPE: Ptr(Int32),
    ST: Ptr(Int32),
    ED: Ptr(Int32),
    SWEEP: Ptr(Int32),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    IB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    V: Complex128[Flat],
    TAU: Complex128[Flat],
    LDVT: Ptr(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZHBEV")
@external
def zhbev(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHBEV_2STAGE")
@external
def zhbev_2stage(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHBEVD")
@external
def zhbevd(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHBEVD_2STAGE")
@external
def zhbevd_2stage(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHBEVX")
@external
def zhbevx(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHBEVX_2STAGE")
@external
def zhbevx_2stage(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHBGST")
@external
def zhbgst(
    VECT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KA: Ptr(Int32),
    KB: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    BB: Complex128[LDBB, Flat],
    LDBB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHBGV")
@external
def zhbgv(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KA: Ptr(Int32),
    KB: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    BB: Complex128[LDBB, Flat],
    LDBB: Ptr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHBGVD")
@external
def zhbgvd(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KA: Ptr(Int32),
    KB: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    BB: Complex128[LDBB, Flat],
    LDBB: Ptr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHBGVX")
@external
def zhbgvx(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KA: Ptr(Int32),
    KB: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    BB: Complex128[LDBB, Flat],
    LDBB: Ptr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHBTRD")
@external
def zhbtrd(
    VECT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Int32),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHECON")
@external
def zhecon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHECON_3")
@external
def zhecon_3(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHECON_ROOK")
@external
def zhecon_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHEEQUB")
@external
def zheequb(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float64[Flat],
    SCOND: Ptr(Float64),
    AMAX: Ptr(Float64),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHEEV")
@external
def zheev(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    W: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHEEV_2STAGE")
@external
def zheev_2stage(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    W: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHEEVD")
@external
def zheevd(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    W: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHEEVD_2STAGE")
@external
def zheevd_2stage(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    W: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHEEVR")
@external
def zheevr(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHEEVR_2STAGE")
@external
def zheevr_2stage(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHEEVX")
@external
def zheevx(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHEEVX_2STAGE")
@external
def zheevx_2stage(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHEGS2")
@external
def zhegs2(
    ITYPE: Ptr(Int32),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHEGST")
@external
def zhegst(
    ITYPE: Ptr(Int32),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHEGV")
@external
def zhegv(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    W: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHEGV_2STAGE")
@external
def zhegv_2stage(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    W: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHEGVD")
@external
def zhegvd(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    W: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHEGVX")
@external
def zhegvx(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHERFS")
@external
def zherfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHERFSX")
@external
def zherfsx(
    UPLO: Ptr(Const(String[1])),
    EQUED: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHESV")
@external
def zhesv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHESV_AA")
@external
def zhesv_aa(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHESV_AA_2STAGE")
@external
def zhesv_aa_2stage(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TB: Complex128[Flat],
    LTB: Ptr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHESV_RK")
@external
def zhesv_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHESV_ROOK")
@external
def zhesv_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHESVX")
@external
def zhesvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHESVXX")
@external
def zhesvxx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    EQUED: Ptr(Const(String[1])),
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    RPVGRW: Ptr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHESWAPR")
@external
def zheswapr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Complex128[LDA, N], ORDER_F],
    LDA: Ptr(Int32),
    I1: Ptr(Int32),
    I2: Ptr(Int32)
) -> None: ...

@bind("ZHETD2")
@external
def zhetd2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETF2")
@external
def zhetf2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETF2_RK")
@external
def zhetf2_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETF2_ROOK")
@external
def zhetf2_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETRD")
@external
def zhetrd(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETRD_2STAGE")
@external
def zhetrd_2stage(
    VECT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Complex128[Flat],
    HOUS2: Complex128[Flat],
    LHOUS2: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETRD_HB2ST")
@external
def zhetrd_hb2st(
    STAGE1: Ptr(Const(String[1])),
    VECT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    HOUS: Complex128[Flat],
    LHOUS: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETRD_HE2HB")
@external
def zhetrd_he2hb(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETRF")
@external
def zhetrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETRF_AA")
@external
def zhetrf_aa(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETRF_AA_2STAGE")
@external
def zhetrf_aa_2stage(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TB: Complex128[Flat],
    LTB: Ptr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETRF_RK")
@external
def zhetrf_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETRF_ROOK")
@external
def zhetrf_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETRI")
@external
def zhetri(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETRI2")
@external
def zhetri2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETRI2X")
@external
def zhetri2x(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[N + NB + 1, Flat],
    NB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETRI_3")
@external
def zhetri_3(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETRI_3X")
@external
def zhetri_3x(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[N + NB + 1, Flat],
    NB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETRI_ROOK")
@external
def zhetri_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETRS")
@external
def zhetrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETRS2")
@external
def zhetrs2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETRS_3")
@external
def zhetrs_3(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETRS_AA")
@external
def zhetrs_aa(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETRS_AA_2STAGE")
@external
def zhetrs_aa_2stage(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TB: Complex128[Flat],
    LTB: Ptr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHETRS_ROOK")
@external
def zhetrs_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHFRK")
@external
def zhfrk(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    ALPHA: Ptr(Float64),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    BETA: Ptr(Float64),
    C: Complex128[Flat]
) -> None: ...

@bind("ZHGEQZ")
@external
def zhgeqz(
    JOB: Ptr(Const(String[1])),
    COMPQ: Ptr(Const(String[1])),
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    H: Complex128[LDH, Flat],
    LDH: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHPCON")
@external
def zhpcon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHPEV")
@external
def zhpev(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHPEVD")
@external
def zhpevd(
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHPEVX")
@external
def zhpevx(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHPGST")
@external
def zhpgst(
    ITYPE: Ptr(Int32),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    BP: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHPGV")
@external
def zhpgv(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    BP: Complex128[Flat],
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHPGVD")
@external
def zhpgvd(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    BP: Complex128[Flat],
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHPGVX")
@external
def zhpgvx(
    ITYPE: Ptr(Int32),
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    BP: Complex128[Flat],
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHPRFS")
@external
def zhprfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex128[Flat],
    AFP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHPSV")
@external
def zhpsv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHPSVX")
@external
def zhpsvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex128[Flat],
    AFP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHPTRD")
@external
def zhptrd(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    D: Float64[Flat],
    E: Float64[Flat],
    TAU: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHPTRF")
@external
def zhptrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHPTRI")
@external
def zhptri(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHPTRS")
@external
def zhptrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHSEIN")
@external
def zhsein(
    SIDE: Ptr(Const(String[1])),
    EIGSRC: Ptr(Const(String[1])),
    INITV: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    H: Complex128[LDH, Flat],
    LDH: Ptr(Int32),
    W: Complex128[Flat],
    VL: Complex128[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Ptr(Int32),
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    IFAILL: Int32[Flat],
    IFAILR: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZHSEQR")
@external
def zhseqr(
    JOB: Ptr(Const(String[1])),
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    H: Complex128[LDH, Flat],
    LDH: Ptr(Int32),
    W: Complex128[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLA_GBAMV")
@external
def zla_gbamv(
    TRANS: Ptr(Int32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    ALPHA: Ptr(Float64),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    X: Complex128[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Float64),
    Y: Float64[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("ZLA_GBRCOND_C")
@external
def zla_gbrcond_c(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    C: Float64[Flat],
    CAPPLY: Ptr(Bool),
    INFO: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_GBRCOND_X")
@external
def zla_gbrcond_x(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    X: Complex128[Flat],
    INFO: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_GBRFSX_EXTENDED")
@external
def zla_gbrfsx_extended(
    PREC_TYPE: Ptr(Int32),
    TRANS_TYPE: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ptr(Bool),
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    Y: Complex128[LDY, Flat],
    LDY: Ptr(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    RES: Complex128[Flat],
    AYB: Float64[Flat],
    DY: Complex128[Flat],
    Y_TAIL: Complex128[Flat],
    RCOND: Ptr(Float64),
    ITHRESH: Ptr(Int32),
    RTHRESH: Ptr(Float64),
    DZ_UB: Ptr(Float64),
    IGNORE_CWISE: Ptr(Bool),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLA_GBRPVGRW")
@external
def zla_gbrpvgrw(
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    NCOLS: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Ptr(Int32)
) -> Float64: ...

@bind("ZLA_GEAMV")
@external
def zla_geamv(
    TRANS: Ptr(Int32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Float64),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex128[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Float64),
    Y: Float64[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("ZLA_GERCOND_C")
@external
def zla_gercond_c(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    C: Float64[Flat],
    CAPPLY: Ptr(Bool),
    INFO: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_GERCOND_X")
@external
def zla_gercond_x(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    X: Complex128[Flat],
    INFO: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_GERFSX_EXTENDED")
@external
def zla_gerfsx_extended(
    PREC_TYPE: Ptr(Int32),
    TRANS_TYPE: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ptr(Bool),
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    Y: Complex128[LDY, Flat],
    LDY: Ptr(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Ptr(Int32),
    ERRS_N: Float64[NRHS, Flat],
    ERRS_C: Float64[NRHS, Flat],
    RES: Complex128[Flat],
    AYB: Float64[Flat],
    DY: Complex128[Flat],
    Y_TAIL: Complex128[Flat],
    RCOND: Ptr(Float64),
    ITHRESH: Ptr(Int32),
    RTHRESH: Ptr(Float64),
    DZ_UB: Ptr(Float64),
    IGNORE_CWISE: Ptr(Bool),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLA_GERPVGRW")
@external
def zla_gerpvgrw(
    N: Ptr(Int32),
    NCOLS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32)
) -> Float64: ...

@bind("ZLA_HEAMV")
@external
def zla_heamv(
    UPLO: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Float64),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex128[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Float64),
    Y: Float64[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("ZLA_HERCOND_C")
@external
def zla_hercond_c(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    C: Float64[Flat],
    CAPPLY: Ptr(Bool),
    INFO: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_HERCOND_X")
@external
def zla_hercond_x(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    X: Complex128[Flat],
    INFO: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_HERFSX_EXTENDED")
@external
def zla_herfsx_extended(
    PREC_TYPE: Ptr(Int32),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ptr(Bool),
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    Y: Complex128[LDY, Flat],
    LDY: Ptr(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    RES: Complex128[Flat],
    AYB: Float64[Flat],
    DY: Complex128[Flat],
    Y_TAIL: Complex128[Flat],
    RCOND: Ptr(Float64),
    ITHRESH: Ptr(Int32),
    RTHRESH: Ptr(Float64),
    DZ_UB: Ptr(Float64),
    IGNORE_CWISE: Ptr(Bool),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLA_HERPVGRW")
@external
def zla_herpvgrw(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    INFO: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_LIN_BERR")
@external
def zla_lin_berr(
    N: Ptr(Int32),
    NZ: Ptr(Int32),
    NRHS: Ptr(Int32),
    RES: Annotated[Complex128[N, NRHS], ORDER_F],
    AYB: Annotated[Float64[N, NRHS], ORDER_F],
    BERR: Float64[NRHS]
) -> None: ...

@bind("ZLA_PORCOND_C")
@external
def zla_porcond_c(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    C: Float64[Flat],
    CAPPLY: Ptr(Bool),
    INFO: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_PORCOND_X")
@external
def zla_porcond_x(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    X: Complex128[Flat],
    INFO: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_PORFSX_EXTENDED")
@external
def zla_porfsx_extended(
    PREC_TYPE: Ptr(Int32),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    COLEQU: Ptr(Bool),
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    Y: Complex128[LDY, Flat],
    LDY: Ptr(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    RES: Complex128[Flat],
    AYB: Float64[Flat],
    DY: Complex128[Flat],
    Y_TAIL: Complex128[Flat],
    RCOND: Ptr(Float64),
    ITHRESH: Ptr(Int32),
    RTHRESH: Ptr(Float64),
    DZ_UB: Ptr(Float64),
    IGNORE_CWISE: Ptr(Bool),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLA_PORPVGRW")
@external
def zla_porpvgrw(
    UPLO: Ptr(Const(String[1])),
    NCOLS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_SYAMV")
@external
def zla_syamv(
    UPLO: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Float64),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex128[Flat],
    INCX: Ptr(Int32),
    BETA: Ptr(Float64),
    Y: Float64[Flat],
    INCY: Ptr(Int32)
) -> None: ...

@bind("ZLA_SYRCOND_C")
@external
def zla_syrcond_c(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    C: Float64[Flat],
    CAPPLY: Ptr(Bool),
    INFO: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_SYRCOND_X")
@external
def zla_syrcond_x(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    X: Complex128[Flat],
    INFO: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_SYRFSX_EXTENDED")
@external
def zla_syrfsx_extended(
    PREC_TYPE: Ptr(Int32),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    COLEQU: Ptr(Bool),
    C: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    Y: Complex128[LDY, Flat],
    LDY: Ptr(Int32),
    BERR_OUT: Float64[Flat],
    N_NORMS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    RES: Complex128[Flat],
    AYB: Float64[Flat],
    DY: Complex128[Flat],
    Y_TAIL: Complex128[Flat],
    RCOND: Ptr(Float64),
    ITHRESH: Ptr(Int32),
    RTHRESH: Ptr(Float64),
    DZ_UB: Ptr(Float64),
    IGNORE_CWISE: Ptr(Bool),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLA_SYRPVGRW")
@external
def zla_syrpvgrw(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    INFO: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLA_WWADDW")
@external
def zla_wwaddw(
    N: Ptr(Int32),
    X: Complex128[Flat],
    Y: Complex128[Flat],
    W: Complex128[Flat]
) -> None: ...

@bind("ZLABRD")
@external
def zlabrd(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    TAUQ: Complex128[Flat],
    TAUP: Complex128[Flat],
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    Y: Complex128[LDY, Flat],
    LDY: Ptr(Int32)
) -> None: ...

@bind("ZLACGV")
@external
def zlacgv(
    N: Ptr(Int32),
    X: Complex128[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("ZLACN2")
@external
def zlacn2(
    N: Ptr(Int32),
    V: Complex128[Flat],
    X: Complex128[Flat],
    EST: Ptr(Float64),
    KASE: Ptr(Int32),
    ISAVE: Int32[3]
) -> None: ...

@bind("ZLACON")
@external
def zlacon(
    N: Ptr(Int32),
    V: Complex128[N],
    X: Complex128[N],
    EST: Ptr(Float64),
    KASE: Ptr(Int32)
) -> None: ...

@bind("ZLACP2")
@external
def zlacp2(
    UPLO: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("ZLACPY")
@external
def zlacpy(
    UPLO: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("ZLACRM")
@external
def zlacrm(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Float64[LDB, Flat],
    LDB: Ptr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    RWORK: Float64[Flat]
) -> None: ...

@bind("ZLACRT")
@external
def zlacrt(
    N: Ptr(Int32),
    CX: Complex128[Flat],
    INCX: Ptr(Int32),
    CY: Complex128[Flat],
    INCY: Ptr(Int32),
    C: Ptr(Complex128),
    S: Ptr(Complex128)
) -> None: ...

@bind("ZLADIV")
@external
def zladiv(
    X: Ptr(Complex128),
    Y: Ptr(Complex128)
) -> Complex128: ...

@bind("ZLAED0")
@external
def zlaed0(
    QSIZ: Ptr(Int32),
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Int32),
    QSTORE: Complex128[LDQS, Flat],
    LDQS: Ptr(Int32),
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLAED7")
@external
def zlaed7(
    N: Ptr(Int32),
    CUTPNT: Ptr(Int32),
    QSIZ: Ptr(Int32),
    TLVLS: Ptr(Int32),
    CURLVL: Ptr(Int32),
    CURPBM: Ptr(Int32),
    D: Float64[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Int32),
    RHO: Ptr(Float64),
    INDXQ: Int32[Flat],
    QSTORE: Float64[Flat],
    QPTR: Int32[Flat],
    PRMPTR: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float64[2, Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLAED8")
@external
def zlaed8(
    K: Ptr(Int32),
    N: Ptr(Int32),
    QSIZ: Ptr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Int32),
    D: Float64[Flat],
    RHO: Ptr(Float64),
    CUTPNT: Ptr(Int32),
    Z: Float64[Flat],
    DLAMBDA: Float64[Flat],
    Q2: Complex128[LDQ2, Flat],
    LDQ2: Ptr(Int32),
    W: Float64[Flat],
    INDXP: Int32[Flat],
    INDX: Int32[Flat],
    INDXQ: Int32[Flat],
    PERM: Int32[Flat],
    GIVPTR: Ptr(Int32),
    GIVCOL: Int32[2, Flat],
    GIVNUM: Float64[2, Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLAEIN")
@external
def zlaein(
    RIGHTV: Ptr(Bool),
    NOINIT: Ptr(Bool),
    N: Ptr(Int32),
    H: Complex128[LDH, Flat],
    LDH: Ptr(Int32),
    W: Ptr(Complex128),
    V: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    RWORK: Float64[Flat],
    EPS3: Ptr(Float64),
    SMLNUM: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLAESY")
@external
def zlaesy(
    A: Ptr(Complex128),
    B: Ptr(Complex128),
    C: Ptr(Complex128),
    RT1: Ptr(Complex128),
    RT2: Ptr(Complex128),
    EVSCAL: Ptr(Complex128),
    CS1: Ptr(Complex128),
    SN1: Ptr(Complex128)
) -> None: ...

@bind("ZLAEV2")
@external
def zlaev2(
    A: Ptr(Complex128),
    B: Ptr(Complex128),
    C: Ptr(Complex128),
    RT1: Ptr(Float64),
    RT2: Ptr(Float64),
    CS1: Ptr(Float64),
    SN1: Ptr(Complex128)
) -> None: ...

@bind("ZLAG2C")
@external
def zlag2c(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    SA: Complex64[LDSA, Flat],
    LDSA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLAGS2")
@external
def zlags2(
    UPPER: Ptr(Bool),
    A1: Ptr(Float64),
    A2: Ptr(Complex128),
    A3: Ptr(Float64),
    B1: Ptr(Float64),
    B2: Ptr(Complex128),
    B3: Ptr(Float64),
    CSU: Ptr(Float64),
    SNU: Ptr(Complex128),
    CSV: Ptr(Float64),
    SNV: Ptr(Complex128),
    CSQ: Ptr(Float64),
    SNQ: Ptr(Complex128)
) -> None: ...

@bind("ZLAGTM")
@external
def zlagtm(
    TRANS: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    ALPHA: Ptr(Float64),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat],
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    BETA: Ptr(Float64),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("ZLAHEF")
@external
def zlahef(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    KB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    W: Complex128[LDW, Flat],
    LDW: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLAHEF_AA")
@external
def zlahef_aa(
    UPLO: Ptr(Const(String[1])),
    J1: Ptr(Int32),
    M: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    H: Complex128[LDH, Flat],
    LDH: Ptr(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLAHEF_RK")
@external
def zlahef_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    KB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    W: Complex128[LDW, Flat],
    LDW: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLAHEF_ROOK")
@external
def zlahef_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    KB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    W: Complex128[LDW, Flat],
    LDW: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLAHQR")
@external
def zlahqr(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    H: Complex128[LDH, Flat],
    LDH: Ptr(Int32),
    W: Complex128[Flat],
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLAHR2")
@external
def zlahr2(
    N: Ptr(Int32),
    K: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[NB],
    T: Annotated[Complex128[LDT, NB], ORDER_F],
    LDT: Ptr(Int32),
    Y: Annotated[Complex128[LDY, NB], ORDER_F],
    LDY: Ptr(Int32)
) -> None: ...

@bind("ZLAIC1")
@external
def zlaic1(
    JOB: Ptr(Int32),
    J: Ptr(Int32),
    X: Complex128[J],
    SEST: Ptr(Float64),
    W: Complex128[J],
    GAMMA: Ptr(Complex128),
    SESTPR: Ptr(Float64),
    S: Ptr(Complex128),
    C: Ptr(Complex128)
) -> None: ...

@bind("ZLALS0")
@external
def zlals0(
    ICOMPQ: Ptr(Int32),
    NL: Ptr(Int32),
    NR: Ptr(Int32),
    SQRE: Ptr(Int32),
    NRHS: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    BX: Complex128[LDBX, Flat],
    LDBX: Ptr(Int32),
    PERM: Int32[Flat],
    GIVPTR: Ptr(Int32),
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ptr(Int32),
    GIVNUM: Float64[LDGNUM, Flat],
    LDGNUM: Ptr(Int32),
    POLES: Float64[LDGNUM, Flat],
    DIFL: Float64[Flat],
    DIFR: Float64[LDGNUM, Flat],
    Z: Float64[Flat],
    K: Ptr(Int32),
    C: Ptr(Float64),
    S: Ptr(Float64),
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLALSA")
@external
def zlalsa(
    ICOMPQ: Ptr(Int32),
    SMLSIZ: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    BX: Complex128[LDBX, Flat],
    LDBX: Ptr(Int32),
    U: Float64[LDU, Flat],
    LDU: Ptr(Int32),
    VT: Float64[LDU, Flat],
    K: Int32[Flat],
    DIFL: Float64[LDU, Flat],
    DIFR: Float64[LDU, Flat],
    Z: Float64[LDU, Flat],
    POLES: Float64[LDU, Flat],
    GIVPTR: Int32[Flat],
    GIVCOL: Int32[LDGCOL, Flat],
    LDGCOL: Ptr(Int32),
    PERM: Int32[LDGCOL, Flat],
    GIVNUM: Float64[LDU, Flat],
    C: Float64[Flat],
    S: Float64[Flat],
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLALSD")
@external
def zlalsd(
    UPLO: Ptr(Const(String[1])),
    SMLSIZ: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    RCOND: Ptr(Float64),
    RANK: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLAMSWLQ")
@external
def zlamswlq(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLAMTSQR")
@external
def zlamtsqr(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLANGB")
@external
def zlangb(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANGE")
@external
def zlange(
    NORM: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANGT")
@external
def zlangt(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    DL: Complex128[Flat],
    D: Complex128[Flat],
    DU: Complex128[Flat]
) -> Float64: ...

@bind("ZLANHB")
@external
def zlanhb(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANHE")
@external
def zlanhe(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANHF")
@external
def zlanhf(
    NORM: Ptr(Const(String[1])),
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Complex128[Flat], SourceDims("0:*")],
    WORK: Annotated[Float64[Flat], SourceDims("0:*")]
) -> Float64: ...

@bind("ZLANHP")
@external
def zlanhp(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANHS")
@external
def zlanhs(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANHT")
@external
def zlanht(
    NORM: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Complex128[Flat]
) -> Float64: ...

@bind("ZLANSB")
@external
def zlansb(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANSP")
@external
def zlansp(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANSY")
@external
def zlansy(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANTB")
@external
def zlantb(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANTP")
@external
def zlantp(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLANTR")
@external
def zlantr(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    WORK: Float64[Flat]
) -> Float64: ...

@bind("ZLAPLL")
@external
def zlapll(
    N: Ptr(Int32),
    X: Complex128[Flat],
    INCX: Ptr(Int32),
    Y: Complex128[Flat],
    INCY: Ptr(Int32),
    SSMIN: Ptr(Float64)
) -> None: ...

@bind("ZLAPMR")
@external
def zlapmr(
    FORWRD: Ptr(Bool),
    M: Ptr(Int32),
    N: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("ZLAPMT")
@external
def zlapmt(
    FORWRD: Ptr(Bool),
    M: Ptr(Int32),
    N: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    K: Int32[Flat]
) -> None: ...

@bind("ZLAQGB")
@external
def zlaqgb(
    M: Ptr(Int32),
    N: Ptr(Int32),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ptr(Float64),
    COLCND: Ptr(Float64),
    AMAX: Ptr(Float64),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("ZLAQGE")
@external
def zlaqge(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    R: Float64[Flat],
    C: Float64[Flat],
    ROWCND: Ptr(Float64),
    COLCND: Ptr(Float64),
    AMAX: Ptr(Float64),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("ZLAQHB")
@external
def zlaqhb(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    S: Float64[Flat],
    SCOND: Ptr(Float64),
    AMAX: Ptr(Float64),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("ZLAQHE")
@external
def zlaqhe(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float64[Flat],
    SCOND: Ptr(Float64),
    AMAX: Ptr(Float64),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("ZLAQHP")
@external
def zlaqhp(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    S: Float64[Flat],
    SCOND: Ptr(Float64),
    AMAX: Ptr(Float64),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("ZLAQP2")
@external
def zlaqp2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    OFFSET: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    JPVT: Int32[Flat],
    TAU: Complex128[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLAQP2RK")
@external
def zlaqp2rk(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    IOFFSET: Ptr(Int32),
    KMAX: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    RELTOL: Ptr(Float64),
    KP1: Ptr(Int32),
    MAXC2NRM: Ptr(Float64),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    K: Ptr(Int32),
    MAXC2NRMK: Ptr(Float64),
    RELMAXC2NRMK: Ptr(Float64),
    JPIV: Int32[Flat],
    TAU: Complex128[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLAQP3RK")
@external
def zlaqp3rk(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    IOFFSET: Ptr(Int32),
    NB: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    RELTOL: Ptr(Float64),
    KP1: Ptr(Int32),
    MAXC2NRM: Ptr(Float64),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    DONE: Ptr(Bool),
    KB: Ptr(Int32),
    MAXC2NRMK: Ptr(Float64),
    RELMAXC2NRMK: Ptr(Float64),
    JPIV: Int32[Flat],
    TAU: Complex128[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    AUXV: Complex128[Flat],
    F: Complex128[LDF, Flat],
    LDF: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLAQPS")
@external
def zlaqps(
    M: Ptr(Int32),
    N: Ptr(Int32),
    OFFSET: Ptr(Int32),
    NB: Ptr(Int32),
    KB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    JPVT: Int32[Flat],
    TAU: Complex128[Flat],
    VN1: Float64[Flat],
    VN2: Float64[Flat],
    AUXV: Complex128[Flat],
    F: Complex128[LDF, Flat],
    LDF: Ptr(Int32)
) -> None: ...

@bind("ZLAQR0")
@external
def zlaqr0(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    H: Complex128[LDH, Flat],
    LDH: Ptr(Int32),
    W: Complex128[Flat],
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLAQR1")
@external
def zlaqr1(
    N: Ptr(Int32),
    H: Complex128[LDH, Flat],
    LDH: Ptr(Int32),
    S1: Ptr(Complex128),
    S2: Ptr(Complex128),
    V: Complex128[Flat]
) -> None: ...

@bind("ZLAQR2")
@external
def zlaqr2(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    KTOP: Ptr(Int32),
    KBOT: Ptr(Int32),
    NW: Ptr(Int32),
    H: Complex128[LDH, Flat],
    LDH: Ptr(Int32),
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    NS: Ptr(Int32),
    ND: Ptr(Int32),
    SH: Complex128[Flat],
    V: Complex128[LDV, Flat],
    LDV: Ptr(Int32),
    NH: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    NV: Ptr(Int32),
    WV: Complex128[LDWV, Flat],
    LDWV: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32)
) -> None: ...

@bind("ZLAQR3")
@external
def zlaqr3(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    KTOP: Ptr(Int32),
    KBOT: Ptr(Int32),
    NW: Ptr(Int32),
    H: Complex128[LDH, Flat],
    LDH: Ptr(Int32),
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    NS: Ptr(Int32),
    ND: Ptr(Int32),
    SH: Complex128[Flat],
    V: Complex128[LDV, Flat],
    LDV: Ptr(Int32),
    NH: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    NV: Ptr(Int32),
    WV: Complex128[LDWV, Flat],
    LDWV: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32)
) -> None: ...

@bind("ZLAQR4")
@external
def zlaqr4(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    H: Complex128[LDH, Flat],
    LDH: Ptr(Int32),
    W: Complex128[Flat],
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLAQR5")
@external
def zlaqr5(
    WANTT: Ptr(Bool),
    WANTZ: Ptr(Bool),
    KACC22: Ptr(Int32),
    N: Ptr(Int32),
    KTOP: Ptr(Int32),
    KBOT: Ptr(Int32),
    NSHFTS: Ptr(Int32),
    S: Complex128[Flat],
    H: Complex128[LDH, Flat],
    LDH: Ptr(Int32),
    ILOZ: Ptr(Int32),
    IHIZ: Ptr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ptr(Int32),
    U: Complex128[LDU, Flat],
    LDU: Ptr(Int32),
    NV: Ptr(Int32),
    WV: Complex128[LDWV, Flat],
    LDWV: Ptr(Int32),
    NH: Ptr(Int32),
    WH: Complex128[LDWH, Flat],
    LDWH: Ptr(Int32)
) -> None: ...

@bind("ZLAQSB")
@external
def zlaqsb(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    S: Float64[Flat],
    SCOND: Ptr(Float64),
    AMAX: Ptr(Float64),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("ZLAQSP")
@external
def zlaqsp(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    S: Float64[Flat],
    SCOND: Ptr(Float64),
    AMAX: Ptr(Float64),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("ZLAQSY")
@external
def zlaqsy(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float64[Flat],
    SCOND: Ptr(Float64),
    AMAX: Ptr(Float64),
    EQUED: Ptr(Const(String[1]))
) -> None: ...

@bind("ZLAQZ0")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7), Arg(8), Arg(9), Arg(10), Arg(11), Arg(12), Arg(13), Arg(14), Arg(15), Arg(16), Arg(17), Arg(18), Arg(19), Return('INFO', 1)])
def zlaqz0(
    WANTS: Ptr(Const(String[1])),
    WANTQ: Ptr(Const(String[1])),
    WANTZ: Ptr(Const(String[1])),
    N: Ptr(Const(Int32)),
    ILO: Ptr(Const(Int32)),
    IHI: Ptr(Const(Int32)),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Const(Int32)),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Const(Int32)),
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Const(Int32)),
    WORK: Complex128[Flat],
    LWORK: Ptr(Const(Int32)),
    RWORK: Float64[Flat],
    REC: Ptr(Const(Int32))
) -> tuple[Returns["RWORK", Float64[Flat]], Int32]: ...

@bind("ZLAQZ1")
@external
def zlaqz1(
    ILQ: Ptr(Const(Bool)),
    ILZ: Ptr(Const(Bool)),
    K: Ptr(Const(Int32)),
    ISTARTM: Ptr(Const(Int32)),
    ISTOPM: Ptr(Const(Int32)),
    IHI: Ptr(Const(Int32)),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Const(Int32)),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    NQ: Ptr(Const(Int32)),
    QSTART: Ptr(Const(Int32)),
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Const(Int32)),
    NZ: Ptr(Const(Int32)),
    ZSTART: Ptr(Const(Int32)),
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Const(Int32))
) -> None: ...

@bind("ZLAQZ2")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7), Arg(8), Arg(9), Arg(10), Arg(11), Arg(12), Arg(13), Arg(14), Return('NS', 0), Return('ND', 1), Arg(15), Arg(16), Arg(17), Arg(18), Arg(19), Arg(20), Arg(21), Arg(22), Arg(23), Arg(24), Return('INFO', 2)])
def zlaqz2(
    ILSCHUR: Ptr(Const(Bool)),
    ILQ: Ptr(Const(Bool)),
    ILZ: Ptr(Const(Bool)),
    N: Ptr(Const(Int32)),
    ILO: Ptr(Const(Int32)),
    IHI: Ptr(Const(Int32)),
    NW: Ptr(Const(Int32)),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Const(Int32)),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Const(Int32)),
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Const(Int32)),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    QC: Complex128[LDQC, Flat],
    LDQC: Ptr(Const(Int32)),
    ZC: Complex128[LDZC, Flat],
    LDZC: Ptr(Const(Int32)),
    WORK: Complex128[Flat],
    LWORK: Ptr(Const(Int32)),
    RWORK: Float64[Flat],
    REC: Ptr(Const(Int32))
) -> tuple[Int32, Int32, Int32]: ...

@bind("ZLAQZ3")
@external
@native_call([Arg(0), Arg(1), Arg(2), Arg(3), Arg(4), Arg(5), Arg(6), Arg(7), Arg(8), Arg(9), Arg(10), Arg(11), Arg(12), Arg(13), Arg(14), Arg(15), Arg(16), Arg(17), Arg(18), Arg(19), Arg(20), Arg(21), Arg(22), Arg(23), Return('INFO', 0)])
def zlaqz3(
    ILSCHUR: Ptr(Const(Bool)),
    ILQ: Ptr(Const(Bool)),
    ILZ: Ptr(Const(Bool)),
    N: Ptr(Const(Int32)),
    ILO: Ptr(Const(Int32)),
    IHI: Ptr(Const(Int32)),
    NSHIFTS: Ptr(Const(Int32)),
    NBLOCK_DESIRED: Ptr(Const(Int32)),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    A: Complex128[LDA, Flat],
    LDA: Ptr(Const(Int32)),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Const(Int32)),
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Const(Int32)),
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Const(Int32)),
    QC: Complex128[LDQC, Flat],
    LDQC: Ptr(Const(Int32)),
    ZC: Complex128[LDZC, Flat],
    LDZC: Ptr(Const(Int32)),
    WORK: Complex128[Flat],
    LWORK: Ptr(Const(Int32))
) -> Int32: ...

@bind("ZLAR1V")
@external
def zlar1v(
    N: Ptr(Int32),
    B1: Ptr(Int32),
    BN: Ptr(Int32),
    LAMBDA: Ptr(Float64),
    D: Float64[Flat],
    L: Float64[Flat],
    LD: Float64[Flat],
    LLD: Float64[Flat],
    PIVMIN: Ptr(Float64),
    GAPTOL: Ptr(Float64),
    Z: Complex128[Flat],
    WANTNC: Ptr(Bool),
    NEGCNT: Ptr(Int32),
    ZTZ: Ptr(Float64),
    MINGMA: Ptr(Float64),
    R: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    NRMINV: Ptr(Float64),
    RESID: Ptr(Float64),
    RQCORR: Ptr(Float64),
    WORK: Float64[Flat]
) -> None: ...

@bind("ZLAR2V")
@external
def zlar2v(
    N: Ptr(Int32),
    X: Complex128[Flat],
    Y: Complex128[Flat],
    Z: Complex128[Flat],
    INCX: Ptr(Int32),
    C: Float64[Flat],
    S: Complex128[Flat],
    INCC: Ptr(Int32)
) -> None: ...

@bind("ZLARCM")
@external
def zlarcm(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Float64[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    RWORK: Float64[Flat]
) -> None: ...

@bind("ZLARF")
@external
def zlarf(
    SIDE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    V: Complex128[Flat],
    INCV: Ptr(Int32),
    TAU: Ptr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLARF1F")
@external
def zlarf1f(
    SIDE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    V: Complex128[Flat],
    INCV: Ptr(Int32),
    TAU: Ptr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLARF1L")
@external
def zlarf1l(
    SIDE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    V: Complex128[Flat],
    INCV: Ptr(Int32),
    TAU: Ptr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLARFB")
@external
def zlarfb(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIRECT: Ptr(Const(String[1])),
    STOREV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[LDWORK, Flat],
    LDWORK: Ptr(Int32)
) -> None: ...

@bind("ZLARFB_GETT")
@external
def zlarfb_gett(
    IDENT: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex128[LDWORK, Flat],
    LDWORK: Ptr(Int32)
) -> None: ...

@bind("ZLARFG")
@external
def zlarfg(
    N: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    X: Complex128[Flat],
    INCX: Ptr(Int32),
    TAU: Ptr(Complex128)
) -> None: ...

@bind("ZLARFGP")
@external
def zlarfgp(
    N: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    X: Complex128[Flat],
    INCX: Ptr(Int32),
    TAU: Ptr(Complex128)
) -> None: ...

@bind("ZLARFT")
@external
def zlarft(
    DIRECT: Ptr(Const(String[1])),
    STOREV: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ptr(Int32),
    TAU: Complex128[Flat],
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32)
) -> None: ...

@bind("ZLARFX")
@external
def zlarfx(
    SIDE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    V: Complex128[Flat],
    TAU: Ptr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLARFY")
@external
def zlarfy(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    V: Complex128[Flat],
    INCV: Ptr(Int32),
    TAU: Ptr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLARGV")
@external
def zlargv(
    N: Ptr(Int32),
    X: Complex128[Flat],
    INCX: Ptr(Int32),
    Y: Complex128[Flat],
    INCY: Ptr(Int32),
    C: Float64[Flat],
    INCC: Ptr(Int32)
) -> None: ...

@bind("ZLARNV")
@external
def zlarnv(
    IDIST: Ptr(Int32),
    ISEED: Int32[4],
    N: Ptr(Int32),
    X: Complex128[Flat]
) -> None: ...

@bind("ZLARRV")
@external
def zlarrv(
    N: Ptr(Int32),
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    D: Float64[Flat],
    L: Float64[Flat],
    PIVMIN: Ptr(Float64),
    ISPLIT: Int32[Flat],
    M: Ptr(Int32),
    DOL: Ptr(Int32),
    DOU: Ptr(Int32),
    MINRGP: Ptr(Float64),
    RTOL1: Ptr(Float64),
    RTOL2: Ptr(Float64),
    W: Float64[Flat],
    WERR: Float64[Flat],
    WGAP: Float64[Flat],
    IBLOCK: Int32[Flat],
    INDEXW: Int32[Flat],
    GERS: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLARSCL2")
@external
def zlarscl2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    D: Float64[Flat],
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32)
) -> None: ...

@bind("ZLARTG")
@external
def zlartg(
    f: Ptr(Complex128),
    g: Ptr(Complex128),
    c: Ptr(Float64),
    s: Ptr(Complex128),
    r: Ptr(Complex128)
) -> None: ...

@bind("ZLARTV")
@external
def zlartv(
    N: Ptr(Int32),
    X: Complex128[Flat],
    INCX: Ptr(Int32),
    Y: Complex128[Flat],
    INCY: Ptr(Int32),
    C: Float64[Flat],
    S: Complex128[Flat],
    INCC: Ptr(Int32)
) -> None: ...

@bind("ZLARZ")
@external
def zlarz(
    SIDE: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    V: Complex128[Flat],
    INCV: Ptr(Int32),
    TAU: Ptr(Complex128),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLARZB")
@external
def zlarzb(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIRECT: Ptr(Const(String[1])),
    STOREV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[LDWORK, Flat],
    LDWORK: Ptr(Int32)
) -> None: ...

@bind("ZLARZT")
@external
def zlarzt(
    DIRECT: Ptr(Const(String[1])),
    STOREV: Ptr(Const(String[1])),
    N: Ptr(Int32),
    K: Ptr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ptr(Int32),
    TAU: Complex128[Flat],
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32)
) -> None: ...

@bind("ZLASCL")
@external
def zlascl(
    TYPE: Ptr(Const(String[1])),
    KL: Ptr(Int32),
    KU: Ptr(Int32),
    CFROM: Ptr(Float64),
    CTO: Ptr(Float64),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLASCL2")
@external
def zlascl2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    D: Float64[Flat],
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32)
) -> None: ...

@bind("ZLASET")
@external
def zlaset(
    UPLO: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    BETA: Ptr(Complex128),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("ZLASR")
@external
def zlasr(
    SIDE: Ptr(Const(String[1])),
    PIVOT: Ptr(Const(String[1])),
    DIRECT: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    C: Float64[Flat],
    S: Float64[Flat],
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("ZLASSQ")
@external
def zlassq(
    n: Ptr(Int32),
    x: Complex128[Flat],
    incx: Ptr(Int32),
    scale: Ptr(Float64),
    sumsq: Ptr(Float64)
) -> None: ...

@bind("ZLASWLQ")
@external
def zlaswlq(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLASWP")
@external
def zlaswp(
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    K1: Ptr(Int32),
    K2: Ptr(Int32),
    IPIV: Int32[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("ZLASYF")
@external
def zlasyf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    KB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    W: Complex128[LDW, Flat],
    LDW: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLASYF_AA")
@external
def zlasyf_aa(
    UPLO: Ptr(Const(String[1])),
    J1: Ptr(Int32),
    M: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    H: Complex128[LDH, Flat],
    LDH: Ptr(Int32),
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLASYF_RK")
@external
def zlasyf_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    KB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    W: Complex128[LDW, Flat],
    LDW: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLASYF_ROOK")
@external
def zlasyf_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    KB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    W: Complex128[LDW, Flat],
    LDW: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLAT2C")
@external
def zlat2c(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    SA: Complex64[LDSA, Flat],
    LDSA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLATBS")
@external
def zlatbs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    NORMIN: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    X: Complex128[Flat],
    SCALE: Ptr(Float64),
    CNORM: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLATDF")
@external
def zlatdf(
    IJOB: Ptr(Int32),
    N: Ptr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    RHS: Complex128[Flat],
    RDSUM: Ptr(Float64),
    RDSCAL: Ptr(Float64),
    IPIV: Int32[Flat],
    JPIV: Int32[Flat]
) -> None: ...

@bind("ZLATPS")
@external
def zlatps(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    NORMIN: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    X: Complex128[Flat],
    SCALE: Ptr(Float64),
    CNORM: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLATRD")
@external
def zlatrd(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    E: Float64[Flat],
    TAU: Complex128[Flat],
    W: Complex128[LDW, Flat],
    LDW: Ptr(Int32)
) -> None: ...

@bind("ZLATRS")
@external
def zlatrs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    NORMIN: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex128[Flat],
    SCALE: Ptr(Float64),
    CNORM: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLATRS3")
@external
def zlatrs3(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    NORMIN: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    SCALE: Float64[Flat],
    CNORM: Float64[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLATRZ")
@external
def zlatrz(
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat]
) -> None: ...

@bind("ZLATSQR")
@external
def zlatsqr(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLAUNHR_COL_GETRFNP")
@external
def zlaunhr_col_getrfnp(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    D: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLAUNHR_COL_GETRFNP2")
@external
def zlaunhr_col_getrfnp2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    D: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLAUU2")
@external
def zlauu2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZLAUUM")
@external
def zlauum(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPBCON")
@external
def zpbcon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPBEQU")
@external
def zpbequ(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    S: Float64[Flat],
    SCOND: Ptr(Float64),
    AMAX: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPBRFS")
@external
def zpbrfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPBSTF")
@external
def zpbstf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPBSV")
@external
def zpbsv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPBSVX")
@external
def zpbsvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    AFB: Complex128[LDAFB, Flat],
    LDAFB: Ptr(Int32),
    EQUED: Ptr(Const(String[1])),
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPBTF2")
@external
def zpbtf2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPBTRF")
@external
def zpbtrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPBTRS")
@external
def zpbtrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPFTRF")
@external
def zpftrf(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Complex128[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPFTRI")
@external
def zpftri(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Complex128[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPFTRS")
@external
def zpftrs(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Annotated[Complex128[Flat], SourceDims("0:*")],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPOCON")
@external
def zpocon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPOEQU")
@external
def zpoequ(
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float64[Flat],
    SCOND: Ptr(Float64),
    AMAX: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPOEQUB")
@external
def zpoequb(
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float64[Flat],
    SCOND: Ptr(Float64),
    AMAX: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPORFS")
@external
def zporfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPORFSX")
@external
def zporfsx(
    UPLO: Ptr(Const(String[1])),
    EQUED: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPOSV")
@external
def zposv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPOSVX")
@external
def zposvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    EQUED: Ptr(Const(String[1])),
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPOSVXX")
@external
def zposvxx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    EQUED: Ptr(Const(String[1])),
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    RPVGRW: Ptr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPOTF2")
@external
def zpotf2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPOTRF")
@external
def zpotrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPOTRF2")
@external
def zpotrf2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPOTRI")
@external
def zpotri(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPOTRS")
@external
def zpotrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPPCON")
@external
def zppcon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPPEQU")
@external
def zppequ(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    S: Float64[Flat],
    SCOND: Ptr(Float64),
    AMAX: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPPRFS")
@external
def zpprfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex128[Flat],
    AFP: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPPSV")
@external
def zppsv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPPSVX")
@external
def zppsvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex128[Flat],
    AFP: Complex128[Flat],
    EQUED: Ptr(Const(String[1])),
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPPTRF")
@external
def zpptrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPPTRI")
@external
def zpptri(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPPTRS")
@external
def zpptrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPSTF2")
@external
def zpstf2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    PIV: Int32[N],
    RANK: Ptr(Int32),
    TOL: Ptr(Float64),
    WORK: Float64[2 * N],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPSTRF")
@external
def zpstrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    PIV: Int32[N],
    RANK: Ptr(Int32),
    TOL: Ptr(Float64),
    WORK: Float64[2 * N],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPTCON")
@external
def zptcon(
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Complex128[Flat],
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPTEQR")
@external
def zpteqr(
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPTRFS")
@external
def zptrfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float64[Flat],
    E: Complex128[Flat],
    DF: Float64[Flat],
    EF: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPTSV")
@external
def zptsv(
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float64[Flat],
    E: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPTSVX")
@external
def zptsvx(
    FACT: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float64[Flat],
    E: Complex128[Flat],
    DF: Float64[Flat],
    EF: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPTTRF")
@external
def zpttrf(
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPTTRS")
@external
def zpttrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float64[Flat],
    E: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZPTTS2")
@external
def zptts2(
    IUPLO: Ptr(Int32),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    D: Float64[Flat],
    E: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32)
) -> None: ...

@bind("ZROT")
@external
def zrot(
    N: Ptr(Int32),
    CX: Complex128[Flat],
    INCX: Ptr(Int32),
    CY: Complex128[Flat],
    INCY: Ptr(Int32),
    C: Ptr(Float64),
    S: Ptr(Complex128)
) -> None: ...

@bind("ZRSCL")
@external
def zrscl(
    N: Ptr(Int32),
    A: Ptr(Complex128),
    X: Complex128[Flat],
    INCX: Ptr(Int32)
) -> None: ...

@bind("ZSPCON")
@external
def zspcon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSPMV")
@external
def zspmv(
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

@bind("ZSPR")
@external
def zspr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    X: Complex128[Flat],
    INCX: Ptr(Int32),
    AP: Complex128[Flat]
) -> None: ...

@bind("ZSPRFS")
@external
def zsprfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex128[Flat],
    AFP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSPSV")
@external
def zspsv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSPSVX")
@external
def zspsvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex128[Flat],
    AFP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSPTRF")
@external
def zsptrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSPTRI")
@external
def zsptri(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSPTRS")
@external
def zsptrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSTEDC")
@external
def zstedc(
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSTEGR")
@external
def zstegr(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    ABSTOL: Ptr(Float64),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSTEIN")
@external
def zstein(
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    M: Ptr(Int32),
    W: Float64[Flat],
    IBLOCK: Int32[Flat],
    ISPLIT: Int32[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    IWORK: Int32[Flat],
    IFAIL: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSTEMR")
@external
def zstemr(
    JOBZ: Ptr(Const(String[1])),
    RANGE: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    VL: Ptr(Float64),
    VU: Ptr(Float64),
    IL: Ptr(Int32),
    IU: Ptr(Int32),
    M: Ptr(Int32),
    W: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    NZC: Ptr(Int32),
    ISUPPZ: Int32[Flat],
    TRYRAC: Ptr(Bool),
    WORK: Float64[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSTEQR")
@external
def zsteqr(
    COMPZ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    D: Float64[Flat],
    E: Float64[Flat],
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    WORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYCON")
@external
def zsycon(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYCON_3")
@external
def zsycon_3(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYCON_ROOK")
@external
def zsycon_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    ANORM: Ptr(Float64),
    RCOND: Ptr(Float64),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYCONV")
@external
def zsyconv(
    UPLO: Ptr(Const(String[1])),
    WAY: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    E: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYCONVF")
@external
def zsyconvf(
    UPLO: Ptr(Const(String[1])),
    WAY: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYCONVF_ROOK")
@external
def zsyconvf_rook(
    UPLO: Ptr(Const(String[1])),
    WAY: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYEQUB")
@external
def zsyequb(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    S: Float64[Flat],
    SCOND: Ptr(Float64),
    AMAX: Ptr(Float64),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYMV")
@external
def zsymv(
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

@bind("ZSYR")
@external
def zsyr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    X: Complex128[Flat],
    INCX: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32)
) -> None: ...

@bind("ZSYRFS")
@external
def zsyrfs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYRFSX")
@external
def zsyrfsx(
    UPLO: Ptr(Const(String[1])),
    EQUED: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYSV")
@external
def zsysv(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYSV_AA")
@external
def zsysv_aa(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYSV_AA_2STAGE")
@external
def zsysv_aa_2stage(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TB: Complex128[Flat],
    LTB: Ptr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYSV_RK")
@external
def zsysv_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYSV_ROOK")
@external
def zsysv_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYSVX")
@external
def zsysvx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYSVXX")
@external
def zsysvxx(
    FACT: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AF: Complex128[LDAF, Flat],
    LDAF: Ptr(Int32),
    IPIV: Int32[Flat],
    EQUED: Ptr(Const(String[1])),
    S: Float64[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    RCOND: Ptr(Float64),
    RPVGRW: Ptr(Float64),
    BERR: Float64[Flat],
    N_ERR_BNDS: Ptr(Int32),
    ERR_BNDS_NORM: Float64[NRHS, Flat],
    ERR_BNDS_COMP: Float64[NRHS, Flat],
    NPARAMS: Ptr(Int32),
    PARAMS: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYSWAPR")
@external
def zsyswapr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    I1: Ptr(Int32),
    I2: Ptr(Int32)
) -> None: ...

@bind("ZSYTF2")
@external
def zsytf2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYTF2_RK")
@external
def zsytf2_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYTF2_ROOK")
@external
def zsytf2_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYTRF")
@external
def zsytrf(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYTRF_AA")
@external
def zsytrf_aa(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYTRF_AA_2STAGE")
@external
def zsytrf_aa_2stage(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TB: Complex128[Flat],
    LTB: Ptr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYTRF_RK")
@external
def zsytrf_rk(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYTRF_ROOK")
@external
def zsytrf_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYTRI")
@external
def zsytri(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYTRI2")
@external
def zsytri2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYTRI2X")
@external
def zsytri2x(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[N + NB + 1, Flat],
    NB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYTRI_3")
@external
def zsytri_3(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYTRI_3X")
@external
def zsytri_3x(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    WORK: Complex128[N + NB + 1, Flat],
    NB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYTRI_ROOK")
@external
def zsytri_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYTRS")
@external
def zsytrs(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYTRS2")
@external
def zsytrs2(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYTRS_3")
@external
def zsytrs_3(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    E: Complex128[Flat],
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYTRS_AA")
@external
def zsytrs_aa(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYTRS_AA_2STAGE")
@external
def zsytrs_aa_2stage(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TB: Complex128[Flat],
    LTB: Ptr(Int32),
    IPIV: Int32[Flat],
    IPIV2: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZSYTRS_ROOK")
@external
def zsytrs_rook(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    IPIV: Int32[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTBCON")
@external
def ztbcon(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    RCOND: Ptr(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTBRFS")
@external
def ztbrfs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTBTRS")
@external
def ztbtrs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    KD: Ptr(Int32),
    NRHS: Ptr(Int32),
    AB: Complex128[LDAB, Flat],
    LDAB: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTFSM")
@external
def ztfsm(
    TRANSR: Ptr(Const(String[1])),
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ALPHA: Ptr(Complex128),
    A: Annotated[Complex128[Flat], SourceDims("0:*")],
    B: Annotated[Complex128[0:LDB-1, Flat], SourceDims("0:LDB-1", "0:*")],
    LDB: Ptr(Int32)
) -> None: ...

@bind("ZTFTRI")
@external
def ztftri(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Complex128[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTFTTP")
@external
def ztfttp(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ARF: Annotated[Complex128[Flat], SourceDims("0:*")],
    AP: Annotated[Complex128[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTFTTR")
@external
def ztfttr(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    ARF: Annotated[Complex128[Flat], SourceDims("0:*")],
    A: Annotated[Complex128[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTGEVC")
@external
def ztgevc(
    SIDE: Ptr(Const(String[1])),
    HOWMNY: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    S: Complex128[LDS, Flat],
    LDS: Ptr(Int32),
    P: Complex128[LDP, Flat],
    LDP: Ptr(Int32),
    VL: Complex128[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Ptr(Int32),
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTGEX2")
@external
def ztgex2(
    WANTQ: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    J1: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTGEXC")
@external
def ztgexc(
    WANTQ: Ptr(Bool),
    WANTZ: Ptr(Bool),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    IFST: Ptr(Int32),
    ILST: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTGSEN")
@external
def ztgsen(
    IJOB: Ptr(Int32),
    WANTQ: Ptr(Bool),
    WANTZ: Ptr(Bool),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    ALPHA: Complex128[Flat],
    BETA: Complex128[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Int32),
    Z: Complex128[LDZ, Flat],
    LDZ: Ptr(Int32),
    M: Ptr(Int32),
    PL: Ptr(Float64),
    PR: Ptr(Float64),
    DIF: Float64[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    LIWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTGSJA")
@external
def ztgsja(
    JOBU: Ptr(Const(String[1])),
    JOBV: Ptr(Const(String[1])),
    JOBQ: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    TOLA: Ptr(Float64),
    TOLB: Ptr(Float64),
    ALPHA: Float64[Flat],
    BETA: Float64[Flat],
    U: Complex128[LDU, Flat],
    LDU: Ptr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ptr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Int32),
    WORK: Complex128[Flat],
    NCYCLE: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTGSNA")
@external
def ztgsna(
    JOB: Ptr(Const(String[1])),
    HOWMNY: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    VL: Complex128[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Ptr(Int32),
    S: Float64[Flat],
    DIF: Float64[Flat],
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTGSY2")
@external
def ztgsy2(
    TRANS: Ptr(Const(String[1])),
    IJOB: Ptr(Int32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    D: Complex128[LDD, Flat],
    LDD: Ptr(Int32),
    E: Complex128[LDE, Flat],
    LDE: Ptr(Int32),
    F: Complex128[LDF, Flat],
    LDF: Ptr(Int32),
    SCALE: Ptr(Float64),
    RDSUM: Ptr(Float64),
    RDSCAL: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTGSYL")
@external
def ztgsyl(
    TRANS: Ptr(Const(String[1])),
    IJOB: Ptr(Int32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    D: Complex128[LDD, Flat],
    LDD: Ptr(Int32),
    E: Complex128[LDE, Flat],
    LDE: Ptr(Int32),
    F: Complex128[LDF, Flat],
    LDF: Ptr(Int32),
    SCALE: Ptr(Float64),
    DIF: Ptr(Float64),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTPCON")
@external
def ztpcon(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    RCOND: Ptr(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTPLQT")
@external
def ztplqt(
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    MB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTPLQT2")
@external
def ztplqt2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTPMLQT")
@external
def ztpmlqt(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    MB: Ptr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTPMQRT")
@external
def ztpmqrt(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    NB: Ptr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTPQRT")
@external
def ztpqrt(
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTPQRT2")
@external
def ztpqrt2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    L: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTPRFB")
@external
def ztprfb(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIRECT: Ptr(Const(String[1])),
    STOREV: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    V: Complex128[LDV, Flat],
    LDV: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    WORK: Complex128[LDWORK, Flat],
    LDWORK: Ptr(Int32)
) -> None: ...

@bind("ZTPRFS")
@external
def ztprfs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTPTRI")
@external
def ztptri(
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTPTRS")
@external
def ztptrs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    AP: Complex128[Flat],
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTPTTF")
@external
def ztpttf(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Annotated[Complex128[Flat], SourceDims("0:*")],
    ARF: Annotated[Complex128[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTPTTR")
@external
def ztpttr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTRCON")
@external
def ztrcon(
    NORM: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    RCOND: Ptr(Float64),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTREVC")
@external
def ztrevc(
    SIDE: Ptr(Const(String[1])),
    HOWMNY: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    VL: Complex128[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Ptr(Int32),
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTREVC3")
@external
def ztrevc3(
    SIDE: Ptr(Const(String[1])),
    HOWMNY: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    VL: Complex128[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Ptr(Int32),
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTREXC")
@external
def ztrexc(
    COMPQ: Ptr(Const(String[1])),
    N: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Int32),
    IFST: Ptr(Int32),
    ILST: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTRRFS")
@external
def ztrrfs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    X: Complex128[LDX, Flat],
    LDX: Ptr(Int32),
    FERR: Float64[Flat],
    BERR: Float64[Flat],
    WORK: Complex128[Flat],
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTRSEN")
@external
def ztrsen(
    JOB: Ptr(Const(String[1])),
    COMPQ: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Int32),
    W: Complex128[Flat],
    M: Ptr(Int32),
    S: Ptr(Float64),
    SEP: Ptr(Float64),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTRSNA")
@external
def ztrsna(
    JOB: Ptr(Const(String[1])),
    HOWMNY: Ptr(Const(String[1])),
    SELECT: Bool[Flat],
    N: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    VL: Complex128[LDVL, Flat],
    LDVL: Ptr(Int32),
    VR: Complex128[LDVR, Flat],
    LDVR: Ptr(Int32),
    S: Float64[Flat],
    SEP: Float64[Flat],
    MM: Ptr(Int32),
    M: Ptr(Int32),
    WORK: Complex128[LDWORK, Flat],
    LDWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTRSYL")
@external
def ztrsyl(
    TRANA: Ptr(Const(String[1])),
    TRANB: Ptr(Const(String[1])),
    ISGN: Ptr(Int32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    SCALE: Ptr(Float64),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTRSYL3")
@external
def ztrsyl3(
    TRANA: Ptr(Const(String[1])),
    TRANB: Ptr(Const(String[1])),
    ISGN: Ptr(Int32),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    SCALE: Ptr(Float64),
    SWORK: Float64[LDSWORK, Flat],
    LDSWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTRTI2")
@external
def ztrti2(
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTRTRI")
@external
def ztrtri(
    UPLO: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTRTRS")
@external
def ztrtrs(
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    DIAG: Ptr(Const(String[1])),
    N: Ptr(Int32),
    NRHS: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    B: Complex128[LDB, Flat],
    LDB: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTRTTF")
@external
def ztrttf(
    TRANSR: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Annotated[Complex128[0:LDA-1, Flat], SourceDims("0:LDA-1", "0:*")],
    LDA: Ptr(Int32),
    ARF: Annotated[Complex128[Flat], SourceDims("0:*")],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTRTTP")
@external
def ztrttp(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    AP: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZTZRZF")
@external
def ztzrzf(
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNBDB")
@external
def zunbdb(
    TRANS: Ptr(Const(String[1])),
    SIGNS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Complex128[LDX11, Flat],
    LDX11: Ptr(Int32),
    X12: Complex128[LDX12, Flat],
    LDX12: Ptr(Int32),
    X21: Complex128[LDX21, Flat],
    LDX21: Ptr(Int32),
    X22: Complex128[LDX22, Flat],
    LDX22: Ptr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Complex128[Flat],
    TAUP2: Complex128[Flat],
    TAUQ1: Complex128[Flat],
    TAUQ2: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNBDB1")
@external
def zunbdb1(
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Complex128[LDX11, Flat],
    LDX11: Ptr(Int32),
    X21: Complex128[LDX21, Flat],
    LDX21: Ptr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Complex128[Flat],
    TAUP2: Complex128[Flat],
    TAUQ1: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNBDB2")
@external
def zunbdb2(
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Complex128[LDX11, Flat],
    LDX11: Ptr(Int32),
    X21: Complex128[LDX21, Flat],
    LDX21: Ptr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Complex128[Flat],
    TAUP2: Complex128[Flat],
    TAUQ1: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNBDB3")
@external
def zunbdb3(
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Complex128[LDX11, Flat],
    LDX11: Ptr(Int32),
    X21: Complex128[LDX21, Flat],
    LDX21: Ptr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Complex128[Flat],
    TAUP2: Complex128[Flat],
    TAUQ1: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNBDB4")
@external
def zunbdb4(
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Complex128[LDX11, Flat],
    LDX11: Ptr(Int32),
    X21: Complex128[LDX21, Flat],
    LDX21: Ptr(Int32),
    THETA: Float64[Flat],
    PHI: Float64[Flat],
    TAUP1: Complex128[Flat],
    TAUP2: Complex128[Flat],
    TAUQ1: Complex128[Flat],
    PHANTOM: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNBDB5")
@external
def zunbdb5(
    M1: Ptr(Int32),
    M2: Ptr(Int32),
    N: Ptr(Int32),
    X1: Complex128[Flat],
    INCX1: Ptr(Int32),
    X2: Complex128[Flat],
    INCX2: Ptr(Int32),
    Q1: Complex128[LDQ1, Flat],
    LDQ1: Ptr(Int32),
    Q2: Complex128[LDQ2, Flat],
    LDQ2: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNBDB6")
@external
def zunbdb6(
    M1: Ptr(Int32),
    M2: Ptr(Int32),
    N: Ptr(Int32),
    X1: Complex128[Flat],
    INCX1: Ptr(Int32),
    X2: Complex128[Flat],
    INCX2: Ptr(Int32),
    Q1: Complex128[LDQ1, Flat],
    LDQ1: Ptr(Int32),
    Q2: Complex128[LDQ2, Flat],
    LDQ2: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNCSD")
@external
def zuncsd(
    JOBU1: Ptr(Const(String[1])),
    JOBU2: Ptr(Const(String[1])),
    JOBV1T: Ptr(Const(String[1])),
    JOBV2T: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    SIGNS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Complex128[LDX11, Flat],
    LDX11: Ptr(Int32),
    X12: Complex128[LDX12, Flat],
    LDX12: Ptr(Int32),
    X21: Complex128[LDX21, Flat],
    LDX21: Ptr(Int32),
    X22: Complex128[LDX22, Flat],
    LDX22: Ptr(Int32),
    THETA: Float64[Flat],
    U1: Complex128[LDU1, Flat],
    LDU1: Ptr(Int32),
    U2: Complex128[LDU2, Flat],
    LDU2: Ptr(Int32),
    V1T: Complex128[LDV1T, Flat],
    LDV1T: Ptr(Int32),
    V2T: Complex128[LDV2T, Flat],
    LDV2T: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNCSD2BY1")
@external
def zuncsd2by1(
    JOBU1: Ptr(Const(String[1])),
    JOBU2: Ptr(Const(String[1])),
    JOBV1T: Ptr(Const(String[1])),
    M: Ptr(Int32),
    P: Ptr(Int32),
    Q: Ptr(Int32),
    X11: Complex128[LDX11, Flat],
    LDX11: Ptr(Int32),
    X21: Complex128[LDX21, Flat],
    LDX21: Ptr(Int32),
    THETA: Float64[Flat],
    U1: Complex128[LDU1, Flat],
    LDU1: Ptr(Int32),
    U2: Complex128[LDU2, Flat],
    LDU2: Ptr(Int32),
    V1T: Complex128[LDV1T, Flat],
    LDV1T: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    RWORK: Float64[Flat],
    LRWORK: Ptr(Int32),
    IWORK: Int32[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNG2L")
@external
def zung2l(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNG2R")
@external
def zung2r(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNGBR")
@external
def zungbr(
    VECT: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNGHR")
@external
def zunghr(
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNGL2")
@external
def zungl2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNGLQ")
@external
def zunglq(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNGQL")
@external
def zungql(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNGQR")
@external
def zungqr(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNGR2")
@external
def zungr2(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNGRQ")
@external
def zungrq(
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNGTR")
@external
def zungtr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNGTSQR")
@external
def zungtsqr(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNGTSQR_ROW")
@external
def zungtsqr_row(
    M: Ptr(Int32),
    N: Ptr(Int32),
    MB: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNHR_COL")
@external
def zunhr_col(
    M: Ptr(Int32),
    N: Ptr(Int32),
    NB: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    T: Complex128[LDT, Flat],
    LDT: Ptr(Int32),
    D: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNM22")
@external
def zunm22(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    N1: Ptr(Int32),
    N2: Ptr(Int32),
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Int32),
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNM2L")
@external
def zunm2l(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNM2R")
@external
def zunm2r(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNMBR")
@external
def zunmbr(
    VECT: Ptr(Const(String[1])),
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNMHR")
@external
def zunmhr(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    ILO: Ptr(Int32),
    IHI: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNML2")
@external
def zunml2(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNMLQ")
@external
def zunmlq(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNMQL")
@external
def zunmql(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNMQR")
@external
def zunmqr(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNMR2")
@external
def zunmr2(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNMR3")
@external
def zunmr3(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNMRQ")
@external
def zunmrq(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNMRZ")
@external
def zunmrz(
    SIDE: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    K: Ptr(Int32),
    L: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUNMTR")
@external
def zunmtr(
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    A: Complex128[LDA, Flat],
    LDA: Ptr(Int32),
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat],
    LWORK: Ptr(Int32),
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUPGTR")
@external
def zupgtr(
    UPLO: Ptr(Const(String[1])),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    TAU: Complex128[Flat],
    Q: Complex128[LDQ, Flat],
    LDQ: Ptr(Int32),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...

@bind("ZUPMTR")
@external
def zupmtr(
    SIDE: Ptr(Const(String[1])),
    UPLO: Ptr(Const(String[1])),
    TRANS: Ptr(Const(String[1])),
    M: Ptr(Int32),
    N: Ptr(Int32),
    AP: Complex128[Flat],
    TAU: Complex128[Flat],
    C: Complex128[LDC, Flat],
    LDC: Ptr(Int32),
    WORK: Complex128[Flat],
    INFO: Ptr(Int32)
) -> None: ...
